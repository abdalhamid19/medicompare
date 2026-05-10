"""AI-powered match verification using Agent Router API."""
import asyncio
import json
import logging
import re
from typing import Any

import aiohttp

from .config import APIConfig
from .normalizer import parse_drug
from .pricing import format_price, price_context, price_delta_text
from .prompts import (
    FRESH_REVIEW_PROMPT,
    REVIEW_PROMPT,
    SEARCH_PROMPT,
    SYSTEM_PROMPT,
    VERIFY_PROMPT,
    render_prompt,
)

logger = logging.getLogger("medicompare")

def _extract_json(text: str) -> dict | None:
    """Extract JSON from model response, handling markdown code blocks and truncation."""
    # Try direct parse
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        pass
    # Try extracting from ```json ... ``` block
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except (json.JSONDecodeError, ValueError):
            pass
    # Try finding first { ... } in text
    m = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except (json.JSONDecodeError, ValueError):
            pass
    # Handle truncated JSON: find opening { and try to close it
    start = text.find("{")
    if start >= 0:
        fragment = text[start:]
        # Try adding closing braces
        for suffix in ["}", "\"}", "\"\n}"]:
            try:
                return json.loads(fragment + suffix)
            except (json.JSONDecodeError, ValueError):
                continue
        # Last resort: extract key-value pairs with regex
        is_correct_m = re.search(r'"is_correct"\s*:\s*(true|false)', fragment, re.IGNORECASE)
        reason_m = re.search(r'"reason"\s*:\s*"([^"]*)"', fragment)
        confidence_m = re.search(r'"confidence"\s*:\s*([\d.]+)', fragment)
        if is_correct_m:
            return {
                "is_correct": is_correct_m.group(1).lower() == "true",
                "reason": reason_m.group(1) if reason_m else "",
                "confidence": float(confidence_m.group(1)) if confidence_m else 0.5,
            }
    return None


def _infer_is_correct(text: str) -> bool:
    """Infer match correctness from text when JSON parsing fails."""
    lower = text.lower()
    # Strong reject signals
    for word in ["different brand", "not the same", "mismatch", "incorrect",
                 "wrong match", "different product", "different dosage",
                 "different form", "different quantity"]:
        if word in lower:
            return False
    # Strong accept signals
    for word in ["same product", "correct match", "identical", "is_correct",
                 "matching", "same brand", "same dosage"]:
        if word in lower:
            return True
    # Default: reject (safer for drug matching)
    return False


def _fallback_from_unparseable_response(text: str, model: str) -> dict[str, Any]:
    is_correct = _infer_is_correct(text)
    confidence = 0.55 if is_correct else 0.4
    return {
        "is_correct": is_correct,
        "agree": is_correct,
        "reason": f"invalid_json:{text[:180]}",
        "confidence": confidence,
        "model_used": model,
        "parse_failed": True,
    }


def _route_from_norm(norm: str) -> str:
    words = set(norm.split())
    routes = set(words & {"IM", "IV", "SC"})
    if {"I", "M"} <= words:
        routes.add("IM")
    if {"I", "V"} <= words:
        routes.add("IV")
    if {"S", "C"} <= words:
        routes.add("SC")
    return "/".join(sorted(routes)) or "-"


def _component_context(name: str) -> str:
    c = parse_drug(name)
    return (
        f"normalized='{c.normalized}', brand='{c.brand}', "
        f"dosage={c.dosage_nums or '-'}, qty='{c.qty or '-'}', "
        f"volume='{c.volume or '-'}', weight='{c.weight or '-'}', "
        f"form='{c.form or '-'}', flavor='{c.flavor or '-'}', "
        f"route='{_route_from_norm(c.normalized)}', "
        f"imported={'yes' if c.imported else 'no'}"
    )


def _format_candidate(
    position: int, candidate: tuple[dict, float, int],
    inventory_price=None,
) -> str:
    rec, score, _ = candidate
    candidate_price = rec.get("price")
    price_text = (
        f", candidate_price={format_price(candidate_price)}, "
        f"price_delta={price_delta_text(inventory_price, candidate_price)}"
    )
    return (
        f"{position}. {rec['product_name_en']} / "
        f"{rec.get('product_name_ar', '')} "
        f"(score={score:.1f}{price_text})\n"
        f"   parsed: {_component_context(rec['product_name_en'])}"
    )


def _normalize_verify_item(
    item: tuple,
) -> tuple[str, str, str, int, str, str, object, object]:
    """Support old verify items plus optional score/method context."""
    if len(item) == 3:
        drug_a, drug_b, row_idx = item
        return drug_a, drug_b, "", row_idx, "", "", None, None
    if len(item) == 4:
        drug_a, drug_b, drug_b_ar, row_idx = item
        return drug_a, drug_b, drug_b_ar, row_idx, "", "", None, None
    if len(item) == 6:
        drug_a, drug_b, drug_b_ar, row_idx, score, method = item
        return drug_a, drug_b, drug_b_ar, row_idx, score, method, None, None
    drug_a, drug_b, drug_b_ar, row_idx = item[:4]
    score, method = item[4], item[5]
    inventory_price, candidate_price = item[6], item[7]
    return (
        drug_a, drug_b, drug_b_ar, row_idx, score, method,
        inventory_price, candidate_price,
    )


def _normalize_review_item(item: tuple) -> tuple:
    """Support review items with optional inventory/candidate prices."""
    if len(item) == 8:
        return (*item, None, None)
    return item


class AIVerifier:
    """Async AI verification client with rate limiting, batching, and key/model fallback."""

    __slots__ = ("_cfg", "_session", "_semaphore", "_fallback_log", "_failed_combos")

    def __init__(self, cfg: APIConfig | None = None, max_concurrent: int = 5):
        self._cfg = cfg or APIConfig()
        self._session: aiohttp.ClientSession | None = None
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._fallback_log: list[str] = []
        self._failed_combos: set[tuple[str, str]] = set()

    def get_fallback_log(self) -> str:
        """Return and clear the API failure log for trace reporting."""
        if not self._fallback_log:
            return ""
        log = "; ".join(self._fallback_log)
        self._fallback_log.clear()
        return log

    def _build_attempt_plan(self, model: str) -> list[tuple[str, str]]:
        """Build ordered list of (api_key, model) to try, skipping previously failed combos.
        Order: primary key + primary model → other keys + primary model → fallback models + all keys."""
        keys = self._cfg.api_keys if self._cfg.api_keys else (self._cfg.api_key,)
        models = [model] + list(self._cfg.fallback_models)
        plan = []
        # Phase 1: try primary model with all keys
        for key in keys:
            combo = (key[-6:], models[0])
            if combo not in self._failed_combos:
                plan.append((key, models[0]))
        # Phase 2: try each fallback model with all keys
        for mdl in models[1:]:
            for key in keys:
                combo = (key[-6:], mdl)
                if combo not in self._failed_combos:
                    plan.append((key, mdl))
        return plan

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            headers={
                "Content-Type": "application/json",
                "HTTP-Referer": "https://medicompare.local",
                "X-Title": "MediCompare Drug Matcher",
            },
            timeout=aiohttp.ClientTimeout(total=30),
        )
        return self

    async def __aexit__(self, *args):
        if self._session:
            await self._session.close()

    async def _call_api(self, payload: dict, max_retries: int = 2) -> dict[str, Any] | None:
        """Make an API call with key+model fallback.
        Tries each (key, model) combination from the attempt plan.
        Returns parsed result dict or None if all attempts fail."""
        if not self._cfg.api_key:
            return None
        close_session = False
        if self._session is None:
            self._session = aiohttp.ClientSession(
                headers={
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://medicompare.local",
                    "X-Title": "MediCompare Drug Matcher",
                },
                timeout=aiohttp.ClientTimeout(total=30),
            )
            close_session = True
        model = payload.get("model", self._cfg.model)
        plan = self._build_attempt_plan(model)

        try:
            for key, mdl in plan:
                payload["model"] = mdl
                headers = dict(self._session.headers)
                headers["Authorization"] = f"Bearer {key}"

                for attempt in range(max_retries + 1):
                    async with self._semaphore:
                        try:
                            async with self._session.post(
                                f"{self._cfg.base_url}/chat/completions",
                                json=payload,
                                headers=headers,
                            ) as resp:
                                if resp.status == 429 and attempt < max_retries:
                                    retry_after = int(
                                        resp.headers.get("Retry-After", "10"),
                                    )
                                    await asyncio.sleep(retry_after + attempt * 2)
                                    continue
                                if resp.status != 200:
                                    text = await resp.text()
                                    log_msg = (
                                        f"API error {resp.status} "
                                        f"with model={mdl} key=...{key[-6:]}"
                                    )
                                    self._fallback_log.append(log_msg)
                                    logger.warning(f"  ⚠ {log_msg}, trying next...")
                                    # Cache auth errors (401/403) to skip in future
                                    if resp.status in (401, 403):
                                        self._failed_combos.add((key[-6:], mdl))
                                    break  # try next (key, model) combo
                                data = await resp.json()
                                content = data["choices"][0]["message"]["content"]
                                result = _extract_json(content)
                                if result is None:
                                    logger.warning(
                                        "  ⚠ invalid JSON from model=%s",
                                        mdl,
                                    )
                                    return _fallback_from_unparseable_response(
                                        content, mdl,
                                    )
                                confidence = float(result.get("confidence", 0.0))
                                if confidence == 0.0:
                                    is_correct = bool(result.get("is_correct", False))
                                    confidence = 0.7 if is_correct else 0.6
                                return {
                                    "is_correct": bool(result.get("is_correct", False)),
                                    "agree": bool(result.get("agree", True)),
                                    "reason": str(result.get("reason", "")),
                                    "confidence": confidence,
                                    "model_used": mdl,
                                    "_raw": result,
                                }
                        except Exception as e:
                            if attempt < max_retries:
                                await asyncio.sleep(2 + attempt * 2)
                                continue
                            log_msg = (
                                f"Exception {type(e).__name__} "
                                f"with model={mdl} key=...{key[-6:]}"
                            )
                            self._fallback_log.append(log_msg)
                            logger.warning(f"  ⚠ {log_msg}, trying next...")
                            break  # try next combo
            return None  # all combos exhausted
        finally:
            if close_session and self._session:
                await self._session.close()
                self._session = None

    async def verify_one(
        self, drug_a: str, drug_b: str, drug_b_ar: str = "",
        algo_score="", algo_method="", inventory_price=None,
        candidate_price=None,
    ) -> dict[str, Any]:
        """Verify a single match. Returns {is_correct, reason, confidence}."""
        if not self._cfg.api_key:
            return {"is_correct": True, "reason": "no_api_key", "confidence": 0.5}

        ar_line = f"\nDRUG B Arabic: {drug_b_ar}" if drug_b_ar else ""
        algorithm_context = (
            f"score={algo_score or '-'}, method={algo_method or '-'}"
        )
        prompt = render_prompt(
            VERIFY_PROMPT,
            drug_a=drug_a,
            drug_b=drug_b,
            drug_b_ar_line=ar_line,
            drug_a_context=_component_context(drug_a),
            drug_b_context=_component_context(drug_b),
            algorithm_context=algorithm_context,
            price_context=price_context(inventory_price, candidate_price),
        )
        payload = {
            "model": self._cfg.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": self._cfg.max_tokens,
            "temperature": self._cfg.temperature,
            "response_format": {"type": "json_object"},
        }

        result = await self._call_api(payload)
        if result is None:
            return {"is_correct": True, "reason": "all_api_failed", "confidence": 0.0, "api_failed": True}
        # Remove 'agree' key if present (not used in verify)
        result.pop("agree", None)
        return result

    async def verify_batch(self, matches: list[tuple]) -> list[dict[str, Any]]:
        """Verify a batch of matches. Each item is (drug_a, drug_b, drug_b_ar, row_index)."""
        normalized = [_normalize_verify_item(item) for item in matches]
        tasks = [
            self.verify_one(a, b, ar, score, method, inv_price, cand_price)
            for (
                a, b, ar, _, score, method, inv_price, cand_price
            ) in normalized
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        out = []
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                out.append({
                    "is_correct": True,
                    "reason": f"exception:{r}",
                    "confidence": 0.0,
                    "row_idx": normalized[i][3],
                })
            else:
                r["row_idx"] = normalized[i][3]
                out.append(r)
        return out

    async def review_one(
        self, drug_a: str, drug_b: str,
        first_decision: str, first_confidence: float, first_reason: str,
        api_failed: bool = False, drug_b_ar: str = "",
        inventory_price=None, candidate_price=None,
    ) -> dict[str, Any]:
        """Ask a second model to review the first AI's decision.
        If api_failed=True, the first AI never made a real decision — ask for fresh verification.
        Returns {is_correct, reason, confidence}."""
        review_model = self._cfg.review_model
        if not review_model or (not self._cfg.api_keys and not self._cfg.api_key):
            return {"is_correct": True, "reason": "no_review_model", "confidence": first_confidence}

        ar_line = f"\nDRUG B Arabic: {drug_b_ar}" if drug_b_ar else ""
        if api_failed:
            prompt = render_prompt(
                FRESH_REVIEW_PROMPT,
                drug_a=drug_a,
                drug_b=drug_b,
                drug_b_ar_line=ar_line,
                drug_a_context=_component_context(drug_a),
                drug_b_context=_component_context(drug_b),
                price_context=price_context(inventory_price, candidate_price),
            )
        else:
            decision_text = (
                "CORRECT match"
                if first_decision == "ai_confirmed"
                else "INCORRECT match"
            )
            prompt = render_prompt(
                REVIEW_PROMPT,
                drug_a=drug_a,
                drug_b=drug_b,
                drug_b_ar_line=ar_line,
                drug_a_context=_component_context(drug_a),
                drug_b_context=_component_context(drug_b),
                price_context=price_context(inventory_price, candidate_price),
                first_decision_text=decision_text,
                first_confidence=first_confidence,
                first_reason=first_reason,
            )

        payload = {
            "model": review_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": self._cfg.max_tokens,
            "temperature": self._cfg.temperature,
            "response_format": {"type": "json_object"},
        }

        result = await self._call_api(payload)
        if result is None:
            return {"is_correct": True, "reason": "review_all_api_failed", "confidence": first_confidence}

        if result.get("parse_failed"):
            return {
                "is_correct": not api_failed,
                "reason": str(result.get("reason", "invalid_json")),
                "confidence": min(float(result.get("confidence", 0.0)), 0.5),
                "parse_failed": True,
            }

        if api_failed:
            # Fresh verification: result is direct is_correct
            return {
                "is_correct": bool(result.get("is_correct", True)),
                "reason": str(result.get("reason", "")),
                "confidence": float(result.get("confidence", first_confidence)),
            }
        agree = bool(result.get("agree", True))
        return {
            "is_correct": agree if first_decision == "ai_confirmed" else not agree,
            "reason": str(result.get("reason", "")),
            "confidence": float(result.get("confidence", first_confidence)),
        }

    async def review_batch(
        self, items: list[tuple]
    ) -> list[dict[str, Any]]:
        """Review a batch of first-AI decisions."""
        normalized = [_normalize_review_item(item) for item in items]
        tasks = [
            self.review_one(
                a, b, d, c, r, api_failed=f, drug_b_ar=ar,
                inventory_price=inv_price, candidate_price=cand_price,
            )
            for (
                a, b, ar, d, c, r, _, f, inv_price, cand_price
            ) in normalized
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        out = []
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                out.append({
                    "is_correct": True,
                    "reason": f"review_exception:{r}",
                    "confidence": normalized[i][4],
                    "row_idx": normalized[i][6],
                })
            else:
                r["row_idx"] = normalized[i][6]
                out.append(r)
        return out

    async def find_better_match(
        self, drug_name: str, candidates: list[tuple[dict, float, int]],
        inventory_price=None,
    ) -> dict[str, Any] | None:
        """Ask AI to pick the best match from candidates."""
        if not candidates or (not self._cfg.api_keys and not self._cfg.api_key):
            return None

        candidates_text = "\n".join(
            _format_candidate(i + 1, c, inventory_price)
            for i, c in enumerate(candidates[:5])
        )
        prompt = render_prompt(
            SEARCH_PROMPT,
            drug_name=drug_name,
            inventory_context=_component_context(drug_name),
            inventory_price=format_price(inventory_price),
            candidates_text=candidates_text,
            max_index=min(len(candidates), 5),
        )

        payload = {
            "model": self._cfg.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": self._cfg.max_tokens,
            "temperature": self._cfg.temperature,
            "response_format": {"type": "json_object"},
        }

        result = await self._call_api(payload)
        if result is None:
            return None
        raw = result.get("_raw", {})
        best_idx = int(raw.get("best_index", 0))
        if best_idx > 0 and best_idx <= len(candidates):
            return {
                "record": candidates[best_idx - 1][0],
                "score": candidates[best_idx - 1][1],
                "reason": result.get("reason", ""),
                "confidence": float(result.get("confidence", 0.0)),
            }
        return {"record": None, "score": 0.0, "reason": result.get("reason", "none"), "confidence": float(result.get("confidence", 0.0))}
