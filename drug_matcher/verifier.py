"""AI-powered match verification using Agent Router API."""
import asyncio
import json
import re
from typing import Any

import aiohttp

from .config import APIConfig

SYSTEM_PROMPT = """You are a pharmaceutical product matching expert. Your job is to verify if two drug names refer to the EXACT SAME product.

STRICT Rules - if ANY of these fail, the match is WRONG:
1. BRAND NAME must be identical (e.g. "PANADOL" = "PANADOL", but "PANADOL" ≠ "PANADOL EXTRA", "VIGOTON PLUS" ≠ "VIGOTON")
2. DOSAGE numbers must match exactly (e.g. 0.8% ≠ 0.4%, 25mg = 25mg, 10mg ≠ 20mg)
3. QUANTITY must match (e.g. 30 tabs = 30 tabs, 20 tabs ≠ 30 tabs). If one has NO quantity and the other has a specific quantity, that is a MISMATCH.
4. VOLUME must match (e.g. 120ml = 120ml, 60ml ≠ 120ml)
5. Different FORM is WRONG (e.g. CREAM ≠ GEL, SYRUP ≠ TABLETS, OINTMENT ≠ CREAM, FOAMING SOLUTION ≠ SACHETS)
6. Different BRAND is WRONG (e.g. GLUCOPHAGE ≠ GLUCOLIGHT, "TOTAL COD LIVER OIL" ≠ "TOTAL")
7. "PLUS" or "EXTRA" in one name but not the other is a MISMATCH (e.g. "VIGOTON PLUS" ≠ "VIGOTON")

OK differences (minor formatting only):
- "F.C.TAB" vs "TAB", "SACHETS" vs "SACHET", spaces, dots, hyphens
- Additional descriptive words that don't change the product (e.g. manufacturer name, "I.M./I.V." route)
- "EFF. GRAN. SACHETS" vs "SACHETS" (same form, different description)
- "PICS" vs "PIECES" vs "SOFT CHEWS PIECES" (same form, different wording)
- "CAPS" vs "CAPSULES", "TABS" vs "TABLETS", "TAB" vs "TABS."

Respond in JSON only:
{"is_correct": true/false, "reason": "brief explanation", "confidence": 0.0-1.0}
"""

VERIFY_PROMPT = """Verify this drug match:

DRUG A (from inventory): {drug_a}
DRUG B (from tawreed): {drug_b}

Is this the SAME product? Respond in JSON only."""


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


class AIVerifier:
    """Async AI verification client with rate limiting and batching."""

    __slots__ = ("_cfg", "_session", "_semaphore")

    def __init__(self, cfg: APIConfig | None = None, max_concurrent: int = 5):
        self._cfg = cfg or APIConfig()
        self._session: aiohttp.ClientSession | None = None
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self._cfg.api_key}",
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

    async def verify_one(self, drug_a: str, drug_b: str) -> dict[str, Any]:
        """Verify a single match. Returns {is_correct, reason, confidence}."""
        if not self._cfg.api_key:
            return {"is_correct": True, "reason": "no_api_key", "confidence": 0.5}

        prompt = VERIFY_PROMPT.format(drug_a=drug_a, drug_b=drug_b)
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

        max_retries = 3
        for attempt in range(max_retries + 1):
            async with self._semaphore:
                try:
                    async with self._session.post(
                        f"{self._cfg.base_url}/chat/completions",
                        json=payload,
                    ) as resp:
                        if resp.status == 429 and attempt < max_retries:
                            # Rate limited — wait and retry
                            retry_after = int(resp.headers.get("Retry-After", "10"))
                            await asyncio.sleep(retry_after + attempt * 2)
                            continue
                        if resp.status != 200:
                            text = await resp.text()
                            return {"is_correct": True, "reason": f"api_error_{resp.status}", "confidence": 0.0, "api_failed": True}
                        data = await resp.json()
                        content = data["choices"][0]["message"]["content"]
                        # Parse JSON response (with fallback for non-JSON)
                        result = _extract_json(content)
                        if result is None:
                            # Model didn't return valid JSON, infer from text
                            is_correct = _infer_is_correct(content)
                            return {
                                "is_correct": is_correct,
                                "reason": content[:200],
                                "confidence": 0.5,
                            }
                        return {
                            "is_correct": bool(result.get("is_correct", False)),
                            "reason": str(result.get("reason", "")),
                            "confidence": float(result.get("confidence", 0.0)),
                        }
                except Exception as e:
                    if attempt < max_retries:
                        await asyncio.sleep(2 + attempt * 2)
                        continue
                    return {"is_correct": True, "reason": f"exception:{type(e).__name__}", "confidence": 0.0}
        return {"is_correct": True, "reason": "max_retries_exceeded", "confidence": 0.0, "api_failed": True}

    async def verify_batch(self, matches: list[tuple[str, str, int]]) -> list[dict[str, Any]]:
        """Verify a batch of matches. Each item is (drug_a, drug_b, row_index)."""
        tasks = [self.verify_one(a, b) for a, b, _ in matches]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        out = []
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                out.append({"is_correct": True, "reason": f"exception:{r}", "confidence": 0.0, "row_idx": matches[i][2]})
            else:
                r["row_idx"] = matches[i][2]
                out.append(r)
        return out

    async def find_better_match(
        self, drug_name: str, candidates: list[tuple[dict, float, int]]
    ) -> dict[str, Any] | None:
        """Ask AI to pick the best match from candidates."""
        if not candidates or not self._cfg.api_key:
            return None

        candidates_text = "\n".join(
            f"{i+1}. {c[0]['product_name_en']} (score={c[1]:.1f})"
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

        max_retries = 3
        for attempt in range(max_retries + 1):
            async with self._semaphore:
                try:
                    async with self._session.post(
                        f"{self._cfg.base_url}/chat/completions",
                        json=payload,
                    ) as resp:
                        if resp.status == 429 and attempt < max_retries:
                            retry_after = int(resp.headers.get("Retry-After", "10"))
                            await asyncio.sleep(retry_after + attempt * 2)
                            continue
                        if resp.status != 200:
                            return None
                        data = await resp.json()
                        content = data["choices"][0]["message"]["content"]
                        result = _extract_json(content)
                        if result is None:
                            return None
                        best_idx = int(result.get("best_index", 0))
                        if best_idx > 0 and best_idx <= len(candidates):
                            return {
                                "record": candidates[best_idx - 1][0],
                                "score": candidates[best_idx - 1][1],
                                "reason": result.get("reason", ""),
                                "confidence": float(result.get("confidence", 0.0)),
                            }
                        return {"record": None, "score": 0.0, "reason": result.get("reason", "none"), "confidence": float(result.get("confidence", 0.0))}
                except Exception:
                    if attempt < max_retries:
                        await asyncio.sleep(2 + attempt * 2)
                        continue
                    return None
        return None
