# MediCompare - Drug Matching & Verification Pipeline

نظام متكامل لمطابقة أسماء الأدوية من المخزون مع منتجات التوريد، مع التحقق بالـ AI.

## 📊 النتائج الحالية

| المؤشر | النسبة |
|---|---|
| إجمالي الأدوية | 6,295 |
| مطابق بنجاح | 3,981 (63.2%) |
| غير مطابق | 2,314 (36.8%) |

## 🚀 البدء السريع

### إعداد البيئة

```bash
# إنشاء بيئة افتراضية
python3 -m venv .venv
source .venv/bin/activate       # Linux/Mac
# .venv\Scripts\activate        # Windows

# تثبيت المتطلبات
pip install -r requirements.txt
```

**متغيرات البيئة** (ملف `.env` في جذر المشروع):
```
AGENT_ROUTER_API_KEY=your-key
AGENT_ROUTER_BASE_URL=https://openrouter.ai/api/v1
AGENT_ROUTER_MODEL=glm-5.1
```

> بدون مفتاح API، يعمل النظام في وضع الخوارزمية فقط (بدون AI).

### التشغيل

```bash
# مطابقة كاملة (خوارزمية + AI)
python run_matcher.py

# مطابقة خوارزمية فقط (بدون AI)
python run_ai_verify.py

# تحديد عدد الأدوية (--limit)
python run_matcher.py --limit 50
python run_ai_verify.py --limit 100

# مستوى التفصيل في السجلات (--log-level)
python run_matcher.py --log-level DEBUG
python run_ai_verify.py --log-level WARNING

# تغيير حد المطابقة (--threshold) وحد التحقق بالـ AI (--ai-threshold)
python run_matcher.py --threshold 85 --ai-threshold 95

# تحديد ملف الإخراج (--output)
python run_matcher.py --output output/my_results.csv

# تشغيل تجريبي سريع
python run_matcher.py --limit 10 --log-level DEBUG

# تتبع تفصيلي لكل خطوة خوارزمية (--trace)
python run_matcher.py --limit 50 --trace

# اختبارات
python run_tests.py
```

### خيارات سطر الأوامر

| الخيار | الوصف | الافتراضي |
|---|---|---|
| `--limit N` | معالجة أول N دواء فقط | الكل |
| `--log-level` | مستوى السجلات (DEBUG, INFO, WARNING, ERROR) | INFO |
| `--threshold` | حد المطابقة الخوارزمية | 80 |
| `--ai-threshold` | حد إحالة المطابقات للـ AI | 90.0 |
| `--output` | مسار ملف الإخراج | output/matched_drugs_verified.csv |
| `--trace` | تتبع تفصيلي لكل خطوة (CSV+TXT في output/trace/) | معطل |
| `--no-ai` | تخطي AI (مطابقة خوارزمية فقط بدون تحقق أو بحث) | معطل |

## 📁 الهيكل

```
medicompare/
├── drug_matcher/          # الحزمة الأساسية
│   ├── config.py          # الإعدادات
│   ├── normalizer.py      # التطبيع
│   ├── indexer.py         # البحث
│   ├── ai_steps.py        # خطوات AI (تحقق + بحث)
│   ├── verifier.py        # AI API client
│   └── pipeline.py        # التنسيق
├── input/                 # البيانات المدخلة
├── output/                # النتائج
├── tests/                 # الاختبارات
├── docs/                  # التوثيق التفصيلي
└── requirements.txt       # المتطلبات
```

## 📚 التوثيق

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** — شرح العمارة والمكونات
- **[ALGORITHMS.md](docs/ALGORITHMS.md)** — الخوارزميات مع أمثلة عملية
- **[PROJECT_RULES.md](docs/PROJECT_RULES.md)** — القواعد والمعايير
- **[MATCHING_STRATEGY_REVIEW.md](docs/MATCHING_STRATEGY_REVIEW.md)** — مراجعة الاستراتيجيات

## 🔧 المكونات الأساسية

| الملف | الوصف |
|---|---|
| `config.py` | إعدادات centralized (fuzzy_threshold, brand_prefix_min, etc) |
| `normalizer.py` | تطبيع واستخراج مكونات الدواء (brand, dosage, form, etc) |
| `indexer.py` | فهرس مقلوب (Brand Index O(1)) + Fuzzy matching (O(n)) |
| `trace_log.py` | تتبع تفصيلي لخطوات الخوارزمية (CSV+TXT) |
| `verifier.py` | التحقق بـ AI متزامن (max 5 طلبات متوازية) |
| `pipeline.py` | 4 مراحل: مطابقة → تحقق → بحث → تنظيف |

## 📊 العمليات الأربع

```
1️⃣ المطابقة الخوارزمية     Brand Index (O(1)) + Fuzzy (O(n))
2️⃣ التحقق بالـ AI          للنتائج الضعيفة (<90%)
3️⃣ بحث الـ AI               عن مطابقات للأصناف غير المطابقة
4️⃣ تنظيف خوارزمي نهائي     تحقق إضافي
```

## 📋 الإخراج

ملف `output/matched_drugs_verified.csv`:

| العمود | الوصف |
|---|---|
| code | كود الدواء |
| drug_name | اسم الدواء الأصلي |
| matched_product_name_en | الاسم المطابق الإنجليزي |
| matched_product_name_ar | الاسم المطابق العربي |
| match_score | نسبة المطابقة (0-100) |
| verified | الحالة (algo_match, ai_confirmed, etc) |
| match_method | طريقة المطابقة (brand_index, token_set_ratio, etc) |

## ⚙️ الإعدادات الافتراضية

```python
fuzzy_threshold = 80              # الحد الأدنى للمطابقة
brand_prefix_min = 4              # طول البادئة للعلامة التجارية
ai_verify_threshold = 90.0        # نسبة الإحالة للـ AI
ai_max_concurrent = 5             # طلبات AI المتوازية
ai_batch_size = 20                # حجم دفعة الـ AI
```

راجع [ARCHITECTURE.md](docs/ARCHITECTURE.md) لفهم كل خيار بالتفصيل.

## 🎯 الميزات

✅ **فهرس مقلوب**: بحث O(1) عن طريق البادئة  
✅ **Fuzzy Matching**: 3 طرق مختلفة للمقارنة  
✅ **AI Verification**: تحقق متزامن من OpenRouter API  
✅ **Batch Processing**: معالجة 20 تطابق معاً  
✅ **Post Cleanup**: تنظيف خوارزمي نهائي للنتائج  

## 🧪 الاختبارات

```bash
python run_tests.py
pytest
pytest -v                    # verbose
pytest tests/test_indexer.py  # اختبار واحد
```

## 📈 الأداء

| العملية | التعقيد | الوقت |
|---|---|---|
| تطبيع واحد | O(n) | <1ms |
| بحث بالعلامة | O(1) | <0.1ms |
| fuzzy search | O(n) | 50-200ms |
| AI واحد | O(1) | 1-3s |
| AI دفعة (20) | O(1) | 3-5s (متوازي) |

## 📝 الملاحظات

- النموذج: `glm-5.1` من OpenRouter
- معدل النجاح: 63.2% خوارزمي + ~85% مع التحقق
- ~25 تطابق قد تحتاج مراجعة يدوية
- الأسماء العربية: لا يتم التعامل معها في المطابقة

## 🔗 الروابط

- [GitHub Repository](https://github.com/abdalhamid19/medicompare)
- [Issues & Discussions](https://github.com/abdalhamid19/medicompare/issues)

