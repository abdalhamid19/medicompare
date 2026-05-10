"""AI-powered match verification using Agent Router API."""
import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Any

import aiohttp

from .config import APIConfig

logger = logging.getLogger("medicompare")

DEFAULT_SYSTEM_PROMPT = """You are a pharmaceutical product matching expert. Your job is to verify if two drug names refer to the EXACT SAME product.

STRICT Rules - if ANY of these fail, the match is WRONG:
1. BRAND NAME must be identical (e.g. "PANADOL" = "PANADOL", but "PANADOL" ≠ "PANADOL EXTRA", "VIGOTON PLUS" ≠ "VIGOTON")
2. DOSAGE numbers must match exactly (e.g. 0.8% ≠ 0.4%, 25mg = 25mg, 10mg ≠ 20mg)
   EXCEPTION: If Drug A (inventory) does NOT specify a dosage/strength but Drug B does (e.g. "ACHTENON 30 TABS" vs "ACHTENON 2 MG 30 TABS"), this is NOT a mismatch — inventory names are often abbreviated and omit the dosage. Only reject if BOTH specify a dosage AND they differ.
3. QUANTITY must match (e.g. 30 tabs = 30 tabs, 20 tabs ≠ 30 tabs).
   EXCEPTION: If Drug A (inventory) does NOT specify a quantity but Drug B does (e.g. "ACRETIN 0.05% CREAM" vs "ACRETIN 0.05% CREAM 30 GM"), this is NOT a mismatch — inventory names are often abbreviated and omit quantity/weight/volume. Only reject if BOTH specify a quantity AND they differ.
4. VOLUME must match (e.g. 120ml = 120ml, 60ml ≠ 120ml). Same exception as quantity: missing volume in inventory name is NOT a mismatch.
5. Different FORM is WRONG (e.g. CREAM ≠ GEL, SYRUP ≠ TABLETS, OINTMENT ≠ CREAM, FOAMING SOLUTION ≠ SACHETS)
6. Different BRAND is WRONG (e.g. GLUCOPHAGE ≠ GLUCOLIGHT, "TOTAL COD LIVER OIL" ≠ "TOTAL")
7. "PLUS" or "EXTRA" in one name but not the other is a MISMATCH (e.g. "VIGOTON PLUS" ≠ "VIGOTON")

OK differences (minor formatting only):
- "F.C.TAB" vs "TAB", "SACHETS" vs "SACHET", spaces, dots, hyphens
- Additional descriptive words that don't change the product (e.g. manufacturer name, "I.M./I.V." route)
- "EFF. GRAN. SACHETS" vs "SACHETS" (same form, different description)
- "PICS" vs "PIECES" vs "SOFT CHEWS PIECES" (same form, different wording)
- "CAPS" vs "CAPSULES", "TABS" vs "TABLETS", "TAB" vs "TABS."

CRITICAL: You MUST include a "confidence" field in your JSON response. This is REQUIRED, not optional.
- confidence = 1.0 if you are absolutely certain (all fields match perfectly)
- confidence = 0.8-0.9 if you are fairly sure but there is minor ambiguity
- confidence = 0.5-0.7 if you are unsure or it is a borderline case
- confidence = 0.0-0.4 if you are very uncertain
NEVER return confidence = 0.0 unless you are completely uncertain.

Respond in JSON only (ALL three fields are MANDATORY):
{"is_correct": true/false, "reason": "brief explanation", "confidence": 0.0-1.0}
"""


def _load_system_prompt() -> str:
    """Load the editable AI prompt, falling back to the built-in prompt."""
    prompt_path = Path(__file__).resolve().parent.parent / "prompt_for_ai.md"
    try:
        text = prompt_path.read_text(encoding="utf-8").strip()
    except OSError:
        return DEFAULT_SYSTEM_PROMPT
    return text or DEFAULT_SYSTEM_PROMPT


SYSTEM_PROMPT = _load_system_prompt()

VERIFY_PROMPT = """Verify this drug match:

DRUG A (from inventory): {drug_a}
DRUG B (from tawreed): {drug_b}{drug_b_ar_line}

Is this the SAME product? The Arabic name can help confirm the match if the English name is ambiguous. You MUST respond with JSON containing ALL three fields: is_correct, reason, and confidence (0.0-1.0)."""


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


def _normalize_verify_item(item: tuple) -> tuple[str, str, str, int]:
    """Support old 3-field and current 4-field verify batch items."""
    if len(item) == 3:
        drug_a, drug_b, row_idx = item
        return drug_a, drug_b, "", row_idx
    drug_a, drug_b, drug_b_ar, row_idx = item
    return drug_a, drug_b, drug_b_ar, row_idx


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
                                    # Model didn't return valid JSON
                                    is_correct = _infer_is_correct(content)
                                    return {
                                        "is_correct": is_correct,
                                        "reason": content[:200],
                                        "confidence": 0.5,
                                    }
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

    async def verify_one(self, drug_a: str, drug_b: str, drug_b_ar: str = "") -> dict[str, Any]:
        """Verify a single match. Returns {is_correct, reason, confidence}."""
        if not self._cfg.api_key:
            return {"is_correct": True, "reason": "no_api_key", "confidence": 0.5}

        ar_line = f"\nDRUG B Arabic: {drug_b_ar}" if drug_b_ar else ""
        prompt = VERIFY_PROMPT.format(drug_a=drug_a, drug_b=drug_b, drug_b_ar_line=ar_line)
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
        tasks = [self.verify_one(a, b, ar) for a, b, ar, _ in normalized]
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
    ) -> dict[str, Any]:
        """Ask a second model to review the first AI's decision.
        If api_failed=True, the first AI never made a real decision — ask for fresh verification.
        Returns {is_correct, reason, confidence}."""
        review_model = self._cfg.review_model
        if not review_model or (not self._cfg.api_keys and not self._cfg.api_key):
            return {"is_correct": True, "reason": "no_review_model", "confidence": first_confidence}

        ar_line = f"\nDRUG B Arabic: {drug_b_ar}" if drug_b_ar else ""
        if api_failed:
            prompt = f"""The first AI model was UNAVAILABLE (API failure) and could NOT verify this drug match.
No first-AI decision was made — the algorithmic match was kept by default.

Please verify this match from scratch as the FIRST and ONLY AI reviewer:

DRUG A (from inventory): {drug_a}
DRUG B (from tawreed): {drug_b}{ar_line}

Is this the SAME product? Apply the strict pharmaceutical matching rules.
Respond in JSON only:
{{"is_correct": true/false, "reason": "brief explanation", "confidence": 0.0-1.0}}""".format(drug_a=drug_a, drug_b=drug_b, ar_line=ar_line)
        else:
            prompt = f"""Review this AI decision about a drug match:

DRUG A (from inventory): {drug_a}
DRUG B (from tawreed): {drug_b}{ar_line}

First AI decided: {"CORRECT match" if first_decision == "ai_confirmed" else "INCORRECT match"}
First AI confidence: {first_confidence}
First AI reason: {first_reason}

Do you AGREE with the first AI? Apply the same strict pharmaceutical matching rules.
Respond in JSON only:
{{"agree": true/false, "reason": "brief explanation", "confidence": 0.0-1.0}}"""

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
        self, items: list[tuple[str, str, str, str, float, str, int, bool]]
    ) -> list[dict[str, Any]]:
        """Review a batch of first-AI decisions. Each item is (drug_a, drug_b, drug_b_ar, first_decision, first_confidence, first_reason, row_index, api_failed)."""
        tasks = [
            self.review_one(a, b, d, c, r, api_failed=f, drug_b_ar=ar)
            for a, b, ar, d, c, r, _, f in items
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        out = []
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                out.append({"is_correct": True, "reason": f"review_exception:{r}", "confidence": items[i][4], "row_idx": items[i][6]})
            else:
                r["row_idx"] = items[i][6]
                out.append(r)
        return out

    async def find_better_match(
        self, drug_name: str, candidates: list[tuple[dict, float, int]]
    ) -> dict[str, Any] | None:
        """Ask AI to pick the best match from candidates."""
        if not candidates or (not self._cfg.api_keys and not self._cfg.api_key):
            return None

        candidates_text = "\n".join(
            f"{i+1}. {c[0]['product_name_en']} / {c[0].get('product_name_ar', '')} (score={c[1]:.1f})"
            for i, c in enumerate(candidates[:5])
        )
        prompt = f"""Given this drug from inventory: "{drug_name}"

Which of these candidates is the CORRECT match? Consider brand name, dosage, quantity, and form.

Candidates:
{candidates_text}

Respond in JSON: {{"best_index": 1-{min(len(candidates),5)}, "reason": "brief explanation", "confidence": 0.0-1.0}}
If NONE are correct, set best_index to 0."""

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
