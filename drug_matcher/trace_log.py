"""Detailed algorithm trace logger - CSV + TXT output."""
import csv
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("medicompare")

_TRACE_CSV_COLS = [
    "drug_code", "drug_name", "norm", "brand",
    "step", "candidate_name", "candidate_id",
    "score", "scorer", "component_ok",
    "result", "final_match", "final_score", "final_method",
]


class MatchTraceLog:
    """Records every algorithmic step for debugging."""

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

    # --- recording ---

    def log_normalization(self, code, name, norm, brand):
        """Log the normalization step."""
        if not self._enabled:
            return
        self._rows.append({
            "drug_code": code, "drug_name": name,
            "norm": norm, "brand": brand,
            "step": "normalize", "candidate_name": "",
            "candidate_id": "", "score": "", "scorer": "",
            "component_ok": "", "result": "",
            "final_match": "", "final_score": "",
            "final_method": "",
        })

    def log_brand_lookup(self, code, name, norm, brand, hits):
        """Log brand index lookup results."""
        if not self._enabled:
            return
        for idx, score in hits:
            self._rows.append({
                "drug_code": code, "drug_name": name,
                "norm": norm, "brand": brand,
                "step": "brand_lookup",
                "candidate_name": f"idx:{idx}",
                "candidate_id": str(idx),
                "score": round(score, 1), "scorer": "token_sort_ratio",
                "component_ok": "yes", "result": "candidate",
                "final_match": "", "final_score": "",
                "final_method": "",
            })
        if not hits:
            self._rows.append({
                "drug_code": code, "drug_name": name,
                "norm": norm, "brand": brand,
                "step": "brand_lookup",
                "candidate_name": "", "candidate_id": "",
                "score": "", "scorer": "",
                "component_ok": "", "result": "no_hits",
                "final_match": "", "final_score": "",
                "final_method": "",
            })

    def log_fuzzy_step(self, code, name, norm, brand, scorer_name, result):
        """Log one fuzzy scorer attempt."""
        if not self._enabled:
            return
        if result:
            match_name, score, idx = result
            self._rows.append({
                "drug_code": code, "drug_name": name,
                "norm": norm, "brand": brand,
                "step": "fuzzy",
                "candidate_name": match_name,
                "candidate_id": str(idx),
                "score": round(score, 1),
                "scorer": scorer_name,
                "component_ok": "", "result": "candidate",
                "final_match": "", "final_score": "",
                "final_method": "",
            })
        else:
            self._rows.append({
                "drug_code": code, "drug_name": name,
                "norm": norm, "brand": brand,
                "step": "fuzzy",
                "candidate_name": "", "candidate_id": "",
                "score": "", "scorer": scorer_name,
                "component_ok": "", "result": "no_hit",
                "final_match": "", "final_score": "",
                "final_method": "",
            })

    def log_component_check(self, code, name, norm, brand, cidx, ok, reason):
        """Log component match check."""
        if not self._enabled:
            return
        self._rows.append({
            "drug_code": code, "drug_name": name,
            "norm": norm, "brand": brand,
            "step": "component_check",
            "candidate_name": f"idx:{cidx}",
            "candidate_id": str(cidx),
            "score": "", "scorer": "",
            "component_ok": "yes" if ok else "no",
            "result": reason,
            "final_match": "", "final_score": "",
            "final_method": "",
        })

    def log_final(self, code, name, norm, brand, match, score, method):
        """Log the final match decision."""
        if not self._enabled:
            return
        self._rows.append({
            "drug_code": code, "drug_name": name,
            "norm": norm, "brand": brand,
            "step": "final",
            "candidate_name": match or "",
            "candidate_id": "", "score": "",
            "scorer": "", "component_ok": "",
            "result": "",
            "final_match": match or "NONE",
            "final_score": round(score, 1) if score else "",
            "final_method": method,
        })

    # --- output ---

    def save(self, prefix: str = "trace") -> tuple[str, str]:
        """Save trace to CSV and TXT. Returns (csv_path, txt_path)."""
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
                step = row["step"]
                if step == "normalize":
                    continue  # already shown above
                elif step == "brand_lookup":
                    if row["result"] == "no_hits":
                        f.write("  [brand_lookup] no hits\n")
                    else:
                        f.write(
                            f"  [brand_lookup] idx={row['candidate_id']}"
                            f"  score={row['score']}\n",
                        )
                elif step == "fuzzy":
                    if row["result"] == "no_hit":
                        f.write(
                            f"  [fuzzy/{row['scorer']}] "
                            f"no hit above threshold\n",
                        )
                    else:
                        f.write(
                            f"  [fuzzy/{row['scorer']}] "
                            f"candidate={row['candidate_name']}"
                            f"  score={row['score']}\n",
                        )
                elif step == "component_check":
                    f.write(
                        f"  [component_check] idx={row['candidate_id']}"
                        f"  ok={row['component_ok']}"
                        f"  reason={row['result']}\n",
                    )
                elif step == "final":
                    f.write(
                        f"  >> FINAL: match={row['final_match']}"
                        f"  score={row['final_score']}"
                        f"  method={row['final_method']}\n\n",
                    )
