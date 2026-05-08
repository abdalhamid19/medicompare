# MediCompare - Drug Matching & Verification Pipeline

نظام متكامل لمطابقة أسماء الأدوية من المخزون مع منتجات التوريد، مع التحقق بالـ AI.

## 📊 النتائج الحالية

| المؤشر | النسبة |
|---|---|
| إجمالي الأدوية | 6,295 |
| مطابق بنجاح | 3,981 (63.2%) |
| غير مطابق | 2,314 (36.8%) |

## 🚀 البدء السريع

### المتطلبات

```bash
pip install pandas numpy rapidfuzz aiohttp requests
```

**متغيرات البيئة** (ملف `.env`):
```
AGENT_ROUTER_API_KEY=your-key
AGENT_ROUTER_BASE_URL=https://openrouter.ai/api/v1
AGENT_ROUTER_MODEL=glm-5.1
```

### التشغيل

```bash
# مطابقة خوارزمية فقط
python run_matcher.py
# → output/matched_drugs.csv

# مطابقة + تحقق AI
python run_ai_verify.py
# → output/matched_drugs_verified.csv

# اختبارات
python run_tests.py
```

## 📁 الهيكل

```
medicompare/
├── drug_matcher/          # الحزمة الأساسية
│   ├── config.py          # الإعدادات
│   ├── normalizer.py      # التطبيع
│   ├── indexer.py         # البحث
│   ├── verifier.py        # AI verification
│   └── pipeline.py        # التنسيق
├── input/                 # البيانات المدخلة
├── output/                # النتائج
├── tests/                 # الاختبارات
└── docs/                  # التوثيق التفصيلي
```

## 📚 التوثيق

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** — شرح العمارة والمكونات
- **[ALGORITHMS.md](docs/ALGORITHMS.md)** — الخوارزميات مع أمثلة عملية
- **[PROJECT_RULES.md](docs/PROJECT_RULES.md)** — القواعس والمعايير

## 🔧 المكونات الأساسية

| الملف | الوصف |
|---|---|
| `config.py` | إعدادات centralized |
| `normalizer.py` | تطبيع واستخراج المكونات |
| `indexer.py` | فهرس مقلوب + Fuzzy matching |
| `verifier.py` | التحقق بـ AI متزامن |
| `pipeline.py` | 4 مراحل: مطابقة، تحقق، بحث، تنظيف |

## 📊 العمليات الأربع

```
1️⃣ المطابقة الخوارزمية (Brand Index + Fuzzy)
2️⃣ التحقق بالـ AI للنتائج الضعيفة (<90%)
3️⃣ بحث الـ AI عن مطابقات للأصناف غير المطابقة
4️⃣ تنظيف خوارزمي نهائي
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

## 🎯 الميزات

✅ **فهرس مقلوب**: بحث O(1) بدل O(n)  
✅ **Fuzzy Matching**: 3 طرق مختلفة للمقارنة  
✅ **AI Verification**: تحقق متزامن بـ Semaphore  
✅ **Batch Processing**: معالجة 20 تطابق معاً  
✅ **Post Cleanup**: تنظيف خوارزمي نهائي  

## 🧪 الاختبارات

```bash
python run_tests.py
pytest
```

## 📈 الأداء

| العملية | التعقيد | الوقت |
|---|---|---|
| تطبيع واحد | O(n) | <1ms |
| بحث بالعلامة | O(1) | <0.1ms |
| fuzzy search | O(n) | 50-200ms |
| AI واحد | O(1) | 1-3s |
| AI دفعة (20) | O(1) | 3-5s (متوازي) |

## 🐛 معالجة الأخطاء

- API errors → إعادة محاولة تلقائية
- Timeouts → timeout معروّف (30s)
- Invalid JSON → معالجة خاصة

## 📝 الملاحظات

1. النموذج: `glm-5.1` من OpenRouter
2. ~25 تطابق قد تحتاج مراجعة يدوية
3. أسماء عربية: لا يتم التعامل معها في المطابقة

## 🔗 الروابط

- [GitHub](https://github.com/abdalhamid19/medicompare)
- [Issues](https://github.com/abdalhamid19/medicompare/issues)

