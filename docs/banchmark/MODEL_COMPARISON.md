# 🏥 Model Comparison: big-pickle vs Top Free Models

**Date**: 2026-05-08  
**Test cases**: 25 (should-match: 14, should-reject: 11)

## 📊 Summary

| # | Model | Provider | Accuracy | Should-Match | Should-Reject | Time (s) |
|---|---|---|---|---|---|---|
| 🥇 | `openai/gpt-oss-20b:free` | OpenRouter | **88%** (22/25) | 86% | 91% | 92.2 |
| 🥈 | `openai/gpt-oss-120b:free` | OpenRouter | **68%** (17/25) | 86% | 45% | 149.4 |
| 🥉 | `big-pickle` | OpenCode | **64%** (16/25) | 36% | 100% | 43.5 |
| 4. | `z-ai/glm-4.5-air:free` | OpenRouter | **56%** (14/25) | 100% | 0% | 4.6 |

## 🔍 تحليل مفصل

### `openai/gpt-oss-20b:free` 🥇 — 88%

- **أفضل توازن** بين المطابقة والرفض
- يرفض 91% من المطابقات الخاطئة (أعلى بعد big-pickle)
- يطابق 86% من المطابقات الصحيحة
- بطيء نسبياً (92s) لكن دقيق

### `openai/gpt-oss-120b:free` 🥈 — 68%

- مطابقة جيدة (86%) لكن رفض ضعيف (45%)
- يعطي is_correct=True لحالات يجب رفضها (مثل CONCOR 5MG vs 2.5MG)
- الأبطأ (149s)

### `big-pickle` 🥉 — 64%

- **أقوى رفض**: 100% من المطابقات الخاطئة مرفوضة بشكل صحيح
- **مشكلة**: يرفض بعض المطابقات الصحيحة (36% فقط مطابقة)
- السبب: `_infer_is_correct` fallback يُرجع `False` كـ default عند فشل JSON
- أسرع من gpt-oss (43s vs 92-149s)

### `z-ai/glm-4.5-air:free` — 56%

- يقبل كل شيء (100% مطابقة، 0% رفض)
- سريع جداً (4.6s) لكن غير مفيد
- لا يميز بين المطابقات الصحيحة والخاطئة

## ⚖️ المقارنة حسب الفئة

### مطابقة صحيحة (Should-Match) — 14 حالة

| Model | صح | خطأ | الدقة |
|---|---|---|---|
| z-ai/glm-4.5-air:free | 14 | 0 | 100% |
| openai/gpt-oss-20b:free | 12 | 2 | 86% |
| openai/gpt-oss-120b:free | 12 | 2 | 86% |
| big-pickle | 5 | 9 | 36% |

### رفض صحيح (Should-Reject) — 11 حالة

| Model | صح | خطأ | الدقة |
|---|---|---|---|
| big-pickle | 11 | 0 | **100%** |
| openai/gpt-oss-20b:free | 10 | 1 | 91% |
| openai/gpt-oss-120b:free | 5 | 6 | 45% |
| z-ai/glm-4.5-air:free | 0 | 11 | 0% |

## 💡 التوصية

| الاستخدام | النموذج الموصى |
|---|---|
| **أفضل توازن (مطابقة + رفض)** | `openai/gpt-oss-20b:free` |
| **أقصى رفض (منع الأخطاء)** | `big-pickle` |
| **سرعة فقط** | `z-ai/glm-4.5-air:free` (غير موصى به) |
| **لا يوصى به** | `openai/gpt-oss-120b:free` (بطيء + رفض ضعيف) |

> **ملاحظة**: big-pickle يعاني من مشكلة `_infer_is_correct` fallback الذي يرفض كـ default
> عند فشل تحليل JSON. هذا يفسر انخفاض نسبة المطابقة (36%). لو تم إصلاح هذه المشكلة،
> قد يصل إلى 80%+ مع الحفاظ على 100% رفض.

## 🚀 الاستخدام

```bash
# الأفضل توازناً
python run_ai_verify.py --limit 50 --provider openrouter --model openai/gpt-oss-20b:free

# أقصى دقة في الرفض
python run_ai_verify.py --limit 50 --provider opencode --model big-pickle
```
