"""Benchmark OpenRouter models for drug name comparison accuracy."""
from __future__ import annotations

import argparse
import asyncio
import json
import time
from pathlib import Path

from drug_matcher.config import APIConfig, load_env, setup_logging
from drug_matcher.verifier import AIVerifier


# Test cases: (drug_name, candidate, expected_is_correct, expected_reason_keyword)
BENCHMARK_CASES = [
    # --- Should be CORRECT (same drug, minor differences) ---
    ("PANADOL 20 TAB", "PANADOL 20 TABLETS", True, "same"),
    ("AMOXIL 500 MG 10 CAP", "AMOXIL 500 MG 10 CAPSULES", True, "same"),
    ("ABILIFY 10 MG 10 TAB", "ABILIFY 10 MG 10 TABS.", True, "same"),
    ("VOLTAREN 50 MG 20 TAB", "VOLTAREN 50 MG 20 TABLETS", True, "same"),
    ("CONCOR 5 MG 30 TAB", "CONCOR 5 MG 30 TABS", True, "same"),
    ("ACETYLCISTEINE 200 MG 10 SACHETS", "ACETYLCISTEIN 200 MG 10 SACHET", True, "same"),
    ("COVERAM 5/5 MG 30 TAB", "COVERAM 5/5 MG 30 TABS", True, "same"),
    ("GLUCOPHAGE 500 MG 30 TAB", "GLUCOPHAGE 500 MG 30 TABLETS", True, "same"),
    ("LIPITOR 10 MG 30 TAB", "LIPITOR 10 MG 30 TABS.", True, "same"),
    ("AUGMENTIN 625 MG 14 TAB", "AUGMENTIN 625 MG 14 TABS", True, "same"),

    # --- Should be INCORRECT (different drug) ---
    ("GREEN TEA", "GREENTAL 30 CAP", False, "different"),
    ("CALCIMA 30 PICS", "CALCIMA 30 SOFT CHEWS PIECES", False, "different"),
    ("PANADOL 20 TAB", "PANADOL EXTRA 24 TAB", False, "different"),
    ("AMOXIL 500 MG 10 CAP", "AMOXIL 250 MG 10 CAP", False, "different"),
    ("VOLTAREN 50 MG 20 TAB", "VOLTAREN 75 MG 20 TAB", False, "different"),
    ("CONCOR 5 MG 30 TAB", "CONCOR 2.5 MG 30 TAB", False, "different"),
    ("LIPITOR 10 MG 30 TAB", "LIPITOR 20 MG 30 TAB", False, "different"),
    ("IBUPROFEN 400 MG 20 TAB", "IBUPROFEN 600 MG 20 TAB", False, "different"),
    ("PANADOL NIGHT 20 TAB", "PANADOL 20 TAB", False, "different"),
    ("ACETYLCISTEINE 600 MG 10 SACHETS", "ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS", False, "different"),

    # --- Tricky / edge cases ---
    ("FEROGLOBIN B12 30 CAP", "FEROGLOBIN 30 CAPS", True, "same"),
    ("PANADOL COLD AND FLU TAB", "PANADOL EXTRA 24 TAB", False, "different"),
    ("OMEPRAZOLE 20 MG 14 CAP", "OMEPRAZOLE 20 MG 14 CAPS", True, "same"),
    ("CIPRO 500 MG 10 TAB", "CIPROBAY 500 MG 10 TAB", False, "different"),
    ("IMODIUM 2 MG 10 TAB", "IMODIUM 2 MG 6 CAP", False, "different"),
]

MODELS = [
    "openai/gpt-4o-mini",
    "deepseek/deepseek-chat-v3.1",
    "z-ai/glm-5.1",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-4-31b-it:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "minimax/minimax-m2.5:free",
    "z-ai/glm-4.5-air:free",
    "openai/gpt-oss-120b:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "amazon/nova-micro-v1",
    "mistralai/mistral-nemo",
]


async def benchmark_model(model: str, api_key: str, base_url: str) -> dict:
    """Run benchmark for a single model."""
    cfg = APIConfig(
        api_key=api_key,
        base_url=base_url,
        model=model,
        max_tokens=256,
        temperature=0.1,
    )

    results = []
    correct_count = 0
    total = len(BENCHMARK_CASES)
    start = time.time()

    async with AIVerifier(cfg, max_concurrent=3) as verifier:
        # Run in small batches to avoid rate limits
        batch_size = 5
        for i in range(0, total, batch_size):
            batch = BENCHMARK_CASES[i:i + batch_size]
            tasks = []
            for drug_name, candidate, expected, _ in batch:
                tasks.append(verifier.verify_one(drug_name, candidate))
            try:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                batch_results = [e] * len(batch)

            for (drug_name, candidate, expected, keyword), result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    results.append({
                        "drug": drug_name, "candidate": candidate,
                        "expected": expected, "got": None,
                        "is_correct_match": False, "confidence": 0,
                        "reason": f"exception: {result}", "match": False,
                    })
                    continue

                got = result.get("is_correct", False)
                confidence = result.get("confidence", 0)
                reason = result.get("reason", "")
                match = (got == expected)
                if match:
                    correct_count += 1

                results.append({
                    "drug": drug_name, "candidate": candidate,
                    "expected": expected, "got": got,
                    "is_correct_match": match, "confidence": confidence,
                    "reason": reason, "match": match,
                })

            # Small delay between batches
            await asyncio.sleep(0.5)

    elapsed = time.time() - start
    accuracy = correct_count / total if total > 0 else 0

    # Breakdown by category
    correct_cases = [r for r in results if r["expected"] is True]
    incorrect_cases = [r for r in results if r["expected"] is False]
    correct_acc = sum(1 for r in correct_cases if r["match"]) / len(correct_cases) if correct_cases else 0
    incorrect_acc = sum(1 for r in incorrect_cases if r["match"]) / len(incorrect_cases) if incorrect_cases else 0

    return {
        "model": model,
        "accuracy": accuracy,
        "correct_count": correct_count,
        "total": total,
        "correct_cases_accuracy": correct_acc,
        "incorrect_cases_accuracy": incorrect_acc,
        "elapsed": round(elapsed, 1),
        "results": results,
    }


def generate_report(all_results: list[dict], output_path: str):
    """Generate markdown report."""
    lines = []
    lines.append("# 🏥 OpenRouter Model Benchmark — Drug Name Comparison\n")
    lines.append(f"**Date**: {time.strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Test cases**: {len(BENCHMARK_CASES)} (should-match: {sum(1 for _,_,e,_ in BENCHMARK_CASES if e)}, should-reject: {sum(1 for _,_,e,_ in BENCHMARK_CASES if not e)})")
    lines.append("")

    # Sort by accuracy
    all_results.sort(key=lambda r: (-r["accuracy"], r["elapsed"]))

    # Summary table
    lines.append("## 📊 Summary Ranking\n")
    lines.append("| # | Model | Accuracy | Should-Match | Should-Reject | Time (s) |")
    lines.append("|---|---|---|---|---|---|")
    for i, r in enumerate(all_results, 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        lines.append(
            f"| {emoji} | `{r['model']}` | "
            f"**{r['accuracy']:.0%}** ({r['correct_count']}/{r['total']}) | "
            f"{r['correct_cases_accuracy']:.0%} | "
            f"{r['incorrect_cases_accuracy']:.0%} | "
            f"{r['elapsed']} |"
        )
    lines.append("")

    # Best model
    best = all_results[0]
    lines.append(f"## 🏆 Best Model: `{best['model']}`\n")
    lines.append(f"- **Overall accuracy**: {best['accuracy']:.0%}")
    lines.append(f"- **Should-match accuracy**: {best['correct_cases_accuracy']:.0%}")
    lines.append(f"- **Should-reject accuracy**: {best['incorrect_cases_accuracy']:.0%}")
    lines.append(f"- **Time**: {best['elapsed']}s")
    lines.append("")

    # Detailed per-model results
    lines.append("## 📋 Detailed Results Per Model\n")
    for r in all_results:
        lines.append(f"### `{r['model']}` — {r['accuracy']:.0%}\n")
        lines.append("| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |")
        lines.append("|---|---|---|---|---|---|---|")
        for case in r["results"]:
            expected_str = "✅ match" if case["expected"] else "❌ reject"
            got_str = "✅ match" if case["got"] else "❌ reject"
            mark = "✓" if case["match"] else "✗"
            conf = f"{case['confidence']:.1f}" if isinstance(case["confidence"], (int, float)) else case["confidence"]
            reason = case["reason"][:60]
            lines.append(
                f"| {case['drug']} | {case['candidate']} | "
                f"{expected_str} | {got_str} | {mark} | "
                f"{conf} | {reason} |"
            )
        lines.append("")

    # Recommendations
    lines.append("## 💡 Recommendations\n")
    free_models = [r for r in all_results if ":free" in r["model"] or r["accuracy"] > 0]
    paid_models = [r for r in all_results if ":free" not in r["model"]]

    if free_models:
        best_free = max(free_models, key=lambda r: r["accuracy"])
        lines.append(f"- **Best free model**: `{best_free['model']}` ({best_free['accuracy']:.0%})")
    if paid_models:
        best_paid = max(paid_models, key=lambda r: r["accuracy"])
        lines.append(f"- **Best paid model**: `{best_paid['model']}` ({best_paid['accuracy']:.0%})")
    lines.append(f"- **Overall best**: `{best['model']}` ({best['accuracy']:.0%})")
    lines.append("")
    lines.append("### To use a specific model:\n")
    lines.append("```bash")
    lines.append("# Set in .env file:")
    lines.append("echo 'AGENT_ROUTER_MODEL=openai/gpt-4o-mini' >> .env")
    lines.append("")
    lines.append("# Or via environment variable:")
    lines.append("AGENT_ROUTER_MODEL=deepseek/deepseek-chat-v3.1 python run_ai_verify.py --limit 50")
    lines.append("```")

    Path(output_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport saved to: {output_path}")


async def main():
    parser = argparse.ArgumentParser(description="Benchmark OpenRouter models for drug comparison")
    parser.add_argument("--models", nargs="+", default=None, help="Models to test (default: all)")
    parser.add_argument("--output", default="docs/MODEL_BENCHMARK.md", help="Output report path")
    parser.add_argument("--key", default=None, help="API key (overrides .env)")
    parser.add_argument("--base-url", default=None, help="Base URL (overrides .env)")
    args = parser.parse_args()

    load_env()
    setup_logging("WARNING")

    api_key = args.key or APIConfig().api_key
    base_url = args.base_url or APIConfig().base_url

    if not api_key:
        print("❌ No API key found. Set AGENT_ROUTER_API_KEY in .env or use --key")
        return

    models = args.models or MODELS

    print(f"🧪 Benchmarking {len(models)} models with {len(BENCHMARK_CASES)} test cases each\n")

    all_results = []
    for model in models:
        print(f"Testing {model} ...", end=" ", flush=True)
        try:
            result = await benchmark_model(model, api_key, base_url)
            acc = result["accuracy"]
            print(f"✅ {acc:.0%} ({result['correct_count']}/{result['total']}) in {result['elapsed']}s")
            all_results.append(result)
        except Exception as e:
            print(f"❌ Error: {e}")
            all_results.append({
                "model": model, "accuracy": 0, "correct_count": 0,
                "total": len(BENCHMARK_CASES),
                "correct_cases_accuracy": 0,
                "incorrect_cases_accuracy": 0,
                "elapsed": 0, "results": [],
            })

    generate_report(all_results, args.output)


if __name__ == "__main__":
    asyncio.run(main())
