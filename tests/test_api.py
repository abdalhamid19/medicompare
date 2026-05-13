"""Quick API connectivity test for OpenRouter."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys

from drug_matcher.config import APIConfig, load_env, setup_logging
from drug_matcher.verifier import AIVerifier, SYSTEM_PROMPT, VERIFY_PROMPT


MODELS = [
    "openai/gpt-4o-mini",
    "z-ai/glm-5.1",
    "deepseek/deepseek-chat-v3.1",
    "meta-llama/llama-3.3-70b-instruct",
]


async def run_one_api_test(cfg: APIConfig) -> dict:
    """Test a single API call."""
    async with AIVerifier(cfg) as v:
        result = await v.verify_one(
            "PANADOL 20 TAB",
            "PANADOL 20 TABLETS",
        )
        return result


def main():
    parser = argparse.ArgumentParser(description="Test OpenRouter API connectivity")
    parser.add_argument("--model", default=None, help="Model to test (default: test all)")
    parser.add_argument("--key", default=None, help="API key (overrides .env)")
    args = parser.parse_args()

    load_env()
    setup_logging("WARNING")

    models = [args.model] if args.model else MODELS

    for model in models:
        key = args.key or APIConfig().api_key
        if not key:
            print(f"❌ {model}: No API key found")
            continue

        cfg = APIConfig(
            api_key=key,
            model=model,
            max_tokens=256,
            temperature=0.1,
        )
        print(f"Testing {model} ...", end=" ", flush=True)
        try:
            result = asyncio.run(run_one_api_test(cfg))
            reason = result.get("reason", "")
            conf = result.get("confidence", 0)
            correct = result.get("is_correct", False)

            if "no_api_key" in reason:
                print(f"❌ No API key")
            elif "api_error" in reason:
                print(f"❌ API error: {reason}")
            elif "exception" in reason:
                print(f"❌ Exception: {reason}")
            else:
                print(f"✅ correct={correct} confidence={conf} reason='{reason}'")
        except Exception as e:
            print(f"❌ Error: {e}")

    print("\nDone.")


if __name__ == "__main__":
    main()
