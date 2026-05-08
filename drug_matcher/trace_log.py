"""Detailed algorithm trace logger - CSV + TXT output."""
import csv
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("medicompare")

_TRACE_CSV_COLS = [
    "drug_code", "drug_name", "norm", "brand",
    "step", "candidate_name", "candidate_id",
    "candidate_brand", "candidate_norm",
    "score", "scorer", "threshold",
    "component_ok", "component_reason",
    "ai_phase", "ai_result",
    "selection_reason",
    "final_match", "final_score", "final_method",
]


class MatchTraceLog:
    """Records every algorithmic + AI step for debugging."""

    __slots__ = ("_rows", "_dir", "_enabled")

    def __init__(self, log_dir: str | None = None, enabled: bool = True):
        self._enabled = enabled
        self._rows: list[dict] = []
        self._dir = Path(log_dir) if log_dir else Path("output/trace")
        if enabled:
            self._dir.mkdir(parents=True, exist_ok=True)

    @property
    def enabled(self) -> bool:
        return self._enabled

    def _base(self, code, name, norm, brand):
        return {
            "drug_code": code, "drug_name": name,
            "norm": norm, "brand": brand,
            "step": "", "candidate_name": "",
            "candidate_id": "", "candidate_brand": "",
            "candidate_norm": "", "score": "",
            "scorer": "", "threshold": "",
            "component_ok": "", "component_reason": "",
            "ai_phase": "", "ai_result": "",
            "selection_reason": "",
            "final_match": "", "final_score": "",
            "final_method": "",
        }

    # --- Phase 1: algorithmic steps ---

    def log_normalization(self, code, name, norm, brand, dosage, form):
        if not self._enabled:
            return
        row = self._base(code, name, norm, brand)
        row["step"] = "normalize"
        row["selection_reason"] = f"dosage={dosage} form={form}"
        self._rows.append(row)

    def log_brand_lookup(self, code, name, norm, brand, hits, index):
        if not self._enabled:
            return
        if not hits:
            row = self._base(code, name, norm, brand)
            row["step"] = "brand_lookup"
            row["selection_reason"] = (
                f"brand={brand} len={len(brand)} (need >=3)"
            )
            row["ai_result"] = "no_hits"
            self._rows.append(row)
            return
        for idx, score in hits:
            rec = index.get_record(idx)
            parsed = index.get_parsed(idx)
            row = self._base(code, name, norm, brand)
            row["step"] = "brand_lookup"
            row["candidate_name"] = rec["product_name_en"]
            row["candidate_id"] = str(idx)
            row["candidate_brand"] = parsed.brand
            row["candidate_norm"] = parsed.normalized
            row["score"] = round(score, 1)
            row["scorer"] = "token_sort_ratio"
            row["selection_reason"] = (
                f"brand_prefix_match score={round(score, 1)}"
            )
            self._rows.append(row)

    def log_fuzzy_step(
        self, code, name, norm, brand,
        scorer_name, result, threshold, index,
    ):
        if not self._enabled:
            return
        row = self._base(code, name, norm, brand)
        row["step"] = "fuzzy"
        row["scorer"] = scorer_name
        row["threshold"] = threshold
        if result:
            match_name, score, idx = result
            rec = index.get_record(idx)
            parsed = index.get_parsed(idx)
            row["candidate_name"] = match_name
            row["candidate_id"] = str(idx)
            row["candidate_brand"] = parsed.brand
            row["candidate_norm"] = parsed.normalized
            row["score"] = round(score, 1)
            row["selection_reason"] = (
                f"score={round(score, 1)} >= threshold={threshold}"
            )
        else:
            row["selection_reason"] = (
                f"no candidate above threshold={threshold}"
            )
        self._rows.append(row)

    def log_component_check(
        self, code, name, norm, brand,
        cidx, ok, reason, index,
    ):
        if not self._enabled:
            return
        rec = index.get_record(cidx)
        parsed = index.get_parsed(cidx)
        row = self._base(code, name, norm, brand)
        row["step"] = "component_check"
        row["candidate_name"] = rec["product_name_en"]
        row["candidate_id"] = str(cidx)
        row["candidate_brand"] = parsed.brand
        row["candidate_norm"] = parsed.normalized
        row["component_ok"] = "yes" if ok else "no"
        row["component_reason"] = reason
        row["selection_reason"] = (
            f"components_match={'ok' if ok else 'FAIL'}"
            f" reason={reason}"
        )
        self._rows.append(row)

    def log_final(
        self, code, name, norm, brand,
        match, score, method, ai_eligible, ai_reason,
    ):
        if not self._enabled:
            return
        row = self._base(code, name, norm, brand)
        row["step"] = "final"
        row["final_match"] = match or "NONE"
        row["final_score"] = round(score, 1) if score else ""
        row["final_method"] = method
        row["ai_phase"] = (
            "verify" if ai_eligible == "verify"
            else "search" if ai_eligible == "search"
            else "none"
        )
        row["ai_result"] = ai_eligible
        row["selection_reason"] = ai_reason
        self._rows.append(row)

    # --- Phase 2 & 3: AI steps ---

    def log_ai_verify_sent(
        self, code, name, norm, brand, score, threshold,
    ):
        if not self._enabled:
            return
        row = self._base(code, name, norm, brand)
        row["step"] = "ai_verify_sent"
        row["ai_phase"] = "verify"
        row["score"] = round(score, 1)
        row["threshold"] = threshold
        row["selection_reason"] = (
            f"algo_score={round(score, 1)} "
            f"< ai_threshold={threshold}"
            f" -> sent to AI verification"
        )
        self._rows.append(row)

    def log_ai_verify_result(
        self, code, name, norm, brand,
        is_correct, ai_action, detail,
    ):
        if not self._enabled:
            return
        row = self._base(code, name, norm, brand)
        row["step"] = "ai_verify_result"
        row["ai_phase"] = "verify"
        row["ai_result"] = ai_action
        row["selection_reason"] = (
            f"AI_says={'correct' if is_correct else 'incorrect'}"
            f" action={ai_action} detail={detail}"
        )
        self._rows.append(row)

    def log_ai_search_sent(
        self, code, name, norm, brand, n_candidates,
    ):
        if not self._enabled:
            return
        row = self._base(code, name, norm, brand)
        row["step"] = "ai_search_sent"
        row["ai_phase"] = "search"
        row["selection_reason"] = (
            f"no_match + {n_candidates} candidates"
            f" -> sent to AI search"
        )
        self._rows.append(row)

    def log_ai_search_result(
        self, code, name, norm, brand,
        found, match_name, confidence,
    ):
        if not self._enabled:
            return
        row = self._base(code, name, norm, brand)
        row["step"] = "ai_search_result"
        row["ai_phase"] = "search"
        row["ai_result"] = "ai_found" if found else "not_found"
        row["candidate_name"] = match_name or ""
        row["score"] = round(confidence, 2) if confidence else ""
        row["selection_reason"] = (
            f"AI_confidence="
            f"{round(confidence, 2) if confidence else 'N/A'}"
            f" >= 0.7 -> {'accepted' if found else 'rejected'}"
        )
        self._rows.append(row)

    def log_ai_skip(self, code, name, norm, brand, phase, reason):
        if not self._enabled:
            return
        row = self._base(code, name, norm, brand)
        row["step"] = "ai_skip"
        row["ai_phase"] = phase
        row["ai_result"] = "skipped"
        row["selection_reason"] = reason
        self._rows.append(row)

    # --- output ---

    def save(self, prefix: str = "trace") -> tuple[str, str]:
        if not self._enabled or not self._rows:
            return "", ""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = self._dir / f"{prefix}_{ts}.csv"
        txt_path = self._dir / f"{prefix}_{ts}.txt"
        self._save_csv(csv_path)
        self._save_txt(txt_path)
        logger.info(f"Trace saved: {csv_path} + {txt_path}")
        return str(csv_path), str(txt_path)

    def _save_csv(self, path: Path):
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=_TRACE_CSV_COLS)
            writer.writeheader()
            writer.writerows(self._rows)

    def _save_txt(self, path: Path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("MediCompare Algorithm Trace Log\n")
            f.write(f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}\n")
            f.write(f"Total steps: {len(self._rows)}\n")
            f.write("=" * 80 + "\n\n")
            current_drug = None
            for row in self._rows:
                key = (row["drug_code"], row["drug_name"])
                if key != current_drug:
                    current_drug = key
                    f.write("-" * 60 + "\n")
                    f.write(
                        f"DRUG: [{row['drug_code']}] "
                        f"{row['drug_name']}\n",
                    )
                    f.write(
                        f"  norm={row['norm']}  "
                        f"brand={row['brand']}\n",
                    )
                self._write_step(f, row)
            f.write("=" * 80 + "\n")

    def _write_step(self, f, row):
        step = row["step"]
        if step == "normalize":
            f.write(f"  [normalize] {row['selection_reason']}\n")
        elif step == "brand_lookup":
            if row["ai_result"] == "no_hits":
                f.write(
                    f"  [brand_lookup] no hits  "
                    f"({row['selection_reason']})\n",
                )
            else:
                f.write(
                    f"  [brand_lookup] "
                    f"{row['candidate_name']}"
                    f"  brand={row['candidate_brand']}"
                    f"  score={row['score']}\n",
                )
        elif step == "fuzzy":
            if "no candidate" in row.get("selection_reason", ""):
                f.write(
                    f"  [fuzzy/{row['scorer']}] "
                    f"no hit above threshold={row['threshold']}\n",
                )
            else:
                f.write(
                    f"  [fuzzy/{row['scorer']}] "
                    f"{row['candidate_name']}"
                    f"  brand={row['candidate_brand']}"
                    f"  score={row['score']}"
                    f"  (threshold={row['threshold']})\n",
                )
        elif step == "component_check":
            f.write(
                f"  [component_check] "
                f"{row['candidate_name']}"
                f"  brand={row['candidate_brand']}"
                f"  ok={row['component_ok']}"
                f"  reason={row['component_reason']}\n",
            )
        elif step == "final":
            ai = row["ai_phase"]
            ai_txt = f"  AI={ai}" if ai != "none" else ""
            f.write(
                f"  >> FINAL: match={row['final_match']}"
                f"  score={row['final_score']}"
                f"  method={row['final_method']}"
                f"{ai_txt}\n",
            )
            f.write(f"     reason: {row['selection_reason']}\n\n")
        elif step == "ai_verify_sent":
            f.write(
                f"  [AI VERIFY] sent  "
                f"score={row['score']} < threshold={row['threshold']}\n",
            )
        elif step == "ai_verify_result":
            f.write(
                f"  [AI VERIFY] result={row['ai_result']}  "
                f"{row['selection_reason']}\n",
            )
        elif step == "ai_search_sent":
            f.write(
                f"  [AI SEARCH] sent  "
                f"{row['selection_reason']}\n",
            )
        elif step == "ai_search_result":
            if row["ai_result"] == "ai_found":
                f.write(
                    f"  [AI SEARCH] FOUND: "
                    f"{row['candidate_name']}"
                    f"  confidence={row['score']}\n",
                )
            else:
                f.write(
                    f"  [AI SEARCH] not found  "
                    f"{row['selection_reason']}\n",
                )
        elif step == "ai_skip":
            f.write(
                f"  [AI {row['ai_phase'].upper()}] "
                f"SKIPPED: {row['selection_reason']}\n",
            )
