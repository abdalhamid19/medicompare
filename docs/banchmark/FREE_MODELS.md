# 🆓 Free Models on OpenRouter

All models with **$0.00** prompt and completion pricing (as of 2026-05-08).

## Recommended for Drug Matching

These are the most capable free models for structured JSON output:

| Model | Context | Notes |
|---|---|---|
| `openai/gpt-oss-120b:free` | 131K | Best free model (76% in benchmark) |
| `nvidia/nemotron-3-super-120b-a12b:free` | 262K | Large model, decent reasoning |
| `qwen/qwen3-next-80b-a3b-instruct:free` | 262K | Good instruction following |
| `meta-llama/llama-3.3-70b-instruct:free` | 65K | Popular, but 48% accuracy |
| `minimax/minimax-m2.5:free` | 196K | Chinese-origin, decent |
| `z-ai/glm-4.5-air:free` | 131K | Chinese-origin, lightweight |

## All Free Models

| Model | Context | Provider |
|---|---|---|
| `baidu/cobuddy:free` | 131K | Baidu |
| `baidu/qianfan-ocr-fast:free` | 65K | Baidu (OCR) |
| `cognitivecomputations/dolphin-mistral-24b-venice-edition:free` | 32K | Venice (uncensored) |
| `google/gemma-4-26b-a4b-it:free` | 262K | Google |
| `google/gemma-4-31b-it:free` | 262K | Google |
| `google/lyria-3-clip-preview` | 1M | Google (multimodal) |
| `google/lyria-3-pro-preview` | 1M | Google (multimodal) |
| `inclusionai/ring-2.6-1t:free` | 262K | InclusionAI |
| `liquid/lfm-2.5-1.2b-instruct:free` | 32K | LiquidAI (small) |
| `liquid/lfm-2.5-1.2b-thinking:free` | 32K | LiquidAI (thinking) |
| `meta-llama/llama-3.2-3b-instruct:free` | 131K | Meta (small) |
| `meta-llama/llama-3.3-70b-instruct:free` | 65K | Meta |
| `minimax/minimax-m2.5:free` | 196K | MiniMax |
| `nousresearch/hermes-3-llama-3.1-405b:free` | 131K | NousResearch |
| `nvidia/nemotron-3-nano-30b-a3b:free` | 256K | NVIDIA |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | 256K | NVIDIA (reasoning) |
| `nvidia/nemotron-3-super-120b-a12b:free` | 262K | NVIDIA |
| `nvidia/nemotron-nano-12b-v2-vl:free` | 128K | NVIDIA (vision) |
| `nvidia/nemotron-nano-9b-v2:free` | 128K | NVIDIA (small) |
| `openai/gpt-oss-120b:free` | 131K | OpenAI |
| `openai/gpt-oss-20b:free` | 131K | OpenAI (smaller) |
| `openrouter/free` | 200K | Router (picks best free) |
| `openrouter/owl-alpha` | 1M | OpenRouter |
| `poolside/laguna-m.1:free` | 131K | Poolside |
| `poolside/laguna-xs.2:free` | 131K | Poolside (small) |
| `qwen/qwen3-coder:free` | 262K | Qwen (code-focused) |
| `qwen/qwen3-next-80b-a3b-instruct:free` | 262K | Qwen |
| `tencent/hy3-preview:free` | 262K | Tencent |
| `z-ai/glm-4.5-air:free` | 131K | Z.ai |

## Usage

```bash
# Test a free model
python run_ai_verify.py --limit 20 --provider openrouter --model openai/gpt-oss-120b:free

# Benchmark all free models
python benchmark_models.py --provider openrouter
```
