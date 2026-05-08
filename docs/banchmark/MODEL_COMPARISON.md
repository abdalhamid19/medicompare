# 🏥 Model Comparison: big-pickle vs Top Free Models

**Date**: 2026-05-08  
**Test cases**: 25 (should-match: 14, should-reject: 11)

## 📊 Summary

| # | Model | Provider | Accuracy | Should-Match | Should-Reject | API Failed | Time (s) |
|---|---|---|---|---|---|---|---|
| 🥇 | `openai/gpt-oss-120b:free` | OpenRouter | **88%** (22/25) | 86% | 91% | 0 | 109.0 |
| 🥈 | `big-pickle` | OpenCode | **84%** (21/25) | 71% | 100% | 0 | 37.3 |
| 🥉 | `openai/gpt-oss-20b:free` | OpenRouter | **72%** (18/25) | 79% | 64% | 0 | 44.7 |
| ❌ | `z-ai/glm-4.5-air:free` | OpenRouter | **N/A** (0/0) | — | — | ⚠️ 25/25 | 4.6 |

## 🔍 تحليل مفصل

### `openai/gpt-oss-120b:free` 🥇 — 88%

- **أفضل توازن** بين المطابقة والرفض
- يرفض 91% من المطابقات الخاطئة
- يطابق 86% من المطابقات الصحيحة
- بطيء (109s) لكن الأكثر دقة

### `big-pickle` 🥈 — 84%

- **أقوى رفض**: 100% من المطابقات الخاطئة مرفوضة بشكل صحيح
- مطابقة جيدة (71%) — يرفض بعض الحالات الصعبة (TAB vs TABLETS)
- أسرع من gpt-oss-120b (37s vs 109s)
- لا يوجد API failures

### `openai/gpt-oss-20b:free` 🥉 — 72%

- أداء أقل من gpt-oss-120b في كل شيء
- رفض ضعيف (64%) — يقبل مطابقات خاطئة
- أسرع (45s)

### `z-ai/glm-4.5-air:free` ❌ — لا يعمل

- **كل الطلبات ترجع 429 (Rate Limit)**
- النموذج لا يعمل فعلياً — كل النتائج السابقة كانت `api_error_429`
- الـ 56% السابقة كانت وهمية لأن benchmark كان يعدّ API errors كـ مطابقات صحيحة
- **غير صالح للاستخدام**

## ⚖️ المقارنة حسب الفئة

### مطابقة صحيحة (Should-Match) — 14 حالة

| Model | صح | خطأ | الدقة |
|---|---|---|---|
| openai/gpt-oss-120b:free | 12 | 2 | 86% |
| openai/gpt-oss-20b:free | 11 | 3 | 79% |
| big-pickle | 10 | 4 | 71% |

### رفض صحيح (Should-Reject) — 11 حالة

| Model | صح | خطأ | الدقة |
|---|---|---|---|
| big-pickle | 11 | 0 | **100%** |
| openai/gpt-oss-120b:free | 10 | 1 | 91% |
| openai/gpt-oss-20b:free | 7 | 4 | 64% |

## 💡 التوصية

| الاستخدام | النموذج الموصى |
|---|---|
| **أفضل دقة شاملة** | `openai/gpt-oss-120b:free` (88%) |
| **أقصى أمان (رفض 100%)** | `big-pickle` (84%) |
| **أسرع + دقة معقولة** | `big-pickle` (37s, 84%) |
| **لا يوصى به** | `glm-4.5-air:free` (لا يعمل) |

## 🚀 الاستخدام

```bash
# أفضل دقة شاملة
python run_ai_verify.py --limit 50 --provider openrouter --model openai/gpt-oss-120b:free

# أقصى أمان + سرعة
python run_ai_verify.py --limit 50 --provider opencode --model big-pickle
```

## ⚠️ ملاحظة عن glm-4.5-air:free

النتائج السابقة (56%) كانت **وهمية**. النموذج يرجع `429 Rate Limit` لكل طلب،
لكن الـ benchmark القديم كان يعدّ `is_correct=True` من API errors كـ مطابقة صحيحة.
تم إصلاح الـ benchmark الآن لاستبعاد حالات `api_failed`.
