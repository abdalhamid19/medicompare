#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def _read_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str).fillna("")


def _matched(df: pd.DataFrame) -> pd.Series:
    return df["matched_product_name_en"].fillna("") != ""


def _keyed(df: pd.DataFrame) -> pd.DataFrame:
    return df.set_index("code", drop=False)


def _summary(label: str, df: pd.DataFrame) -> list[str]:
    matched = _matched(df)
    lines = [
        f"{label}: rows={len(df)} matched={int(matched.sum())} unmatched={int((~matched).sum())}",
    ]
    if "match_method" in df.columns:
        lines.append(f"{label} methods:")
        lines.extend(
            f"  {method or '<blank>'}: {count}"
            for method, count in df["match_method"].value_counts().head(15).items()
        )
    if "verified" in df.columns:
        lines.append(f"{label} verified:")
        lines.extend(
            f"  {status or '<blank>'}: {count}"
            for status, count in df["verified"].value_counts().head(15).items()
        )
    return lines


def _trace_summary(label: str, path: str | None) -> list[str]:
    if not path:
        return []
    trace_path = Path(path)
    if not trace_path.exists():
        return [f"{label} trace: missing {trace_path}"]
    trace = _read_csv(path)
    lines = [f"{label} trace rows={len(trace)}"]
    for col in ("phase", "decision", "error_code", "component_reason"):
        if col in trace.columns:
            lines.append(f"{label} trace {col}:")
            lines.extend(
                f"  {value or '<blank>'}: {count}"
                for value, count in trace[col].value_counts().head(12).items()
            )
    return lines


def compare(before: pd.DataFrame, after: pd.DataFrame) -> list[str]:
    b = _keyed(before)
    a = _keyed(after)
    shared = b.index.intersection(a.index)
    b = b.loc[shared]
    a = a.loc[shared]
    before_matched = _matched(b)
    after_matched = _matched(a)
    newly_matched = a[(~before_matched) & after_matched]
    newly_unmatched = a[before_matched & (~after_matched)]
    id_changed = a[
        before_matched
        & after_matched
        & (b["matched_store_product_id"].astype(str) != a["matched_store_product_id"].astype(str))
    ]
    lines = [
        "Delta:",
        f"  shared_rows={len(shared)}",
        f"  newly_matched={len(newly_matched)}",
        f"  newly_unmatched={len(newly_unmatched)}",
        f"  changed_store_product_id={len(id_changed)}",
    ]
    for title, rows in (
        ("Newly matched sample", newly_matched),
        ("Newly unmatched sample", newly_unmatched),
        ("Changed ID sample", id_changed),
    ):
        lines.append(f"{title}:")
        if rows.empty:
            lines.append("  <none>")
            continue
        for _, row in rows.head(20).iterrows():
            lines.append(
                "  "
                f"{row.get('code', '')}: {row.get('drug_name', '')} -> "
                f"{row.get('matched_product_name_en', '')} "
                f"({row.get('match_method', '')}, {row.get('verified', '')})"
            )
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--before-trace")
    parser.add_argument("--after-trace")
    args = parser.parse_args()

    before = _read_csv(args.before)
    after = _read_csv(args.after)
    lines: list[str] = []
    lines.extend(_summary("before", before))
    lines.extend(_summary("after", after))
    lines.extend(compare(before, after))
    lines.extend(_trace_summary("before", args.before_trace))
    lines.extend(_trace_summary("after", args.after_trace))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
