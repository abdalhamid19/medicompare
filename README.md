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
AI_MODEL=minimax-m2.5-free
OPENCODE_API_KEY=your-opencode-key
OPENROUTER_API_KEY=your-openrouter-key
GROQ_API_KEY=your-groq-key
REVIEW_MODEL=big-pickle
AI_REVIEW_THRESHOLD=1.0
```

> بدون مفتاح API، يعمل النظام في وضع الخوارزمية فقط (بدون AI).
> استخدم `--provider` لتحديد مزود API مباشرةً عن متغيرات البيئة.

### التشغيل

```bash
# مطابقة كاملة (خوارزمية + AI + مراجعة)
python run_matcher.py

# مطابقة خوارزمية فقط (بدون AI)
python run_matcher.py --no-ai

# تشغيل AI تحقق فقط
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

# اختبار موديلات OpenCode قبل التشغيل الطويل
python test_opencode_models.py --mode both --timeout 20 --concurrency 4

# تشغيل آمن: preflight تلقائي + حد أقصى لبحث AI
python run_matcher.py --provider opencode --trace --ai-search-limit 200

# اختبار كل مزودي AI المتاحين وترتيبهم للـ rotation
python test_ai_rotation.py --providers auto --mode json --timeout 10 --concurrency 4

# تشغيل بنظام AI rotation بين كل providers الصالحة
python run_matcher.py --provider rotation --trace --ai-search-limit 200

# تشغيل rotation مع موديل مراجعة ثاني من rotation وتوازي 4 طلبات
python run_matcher.py --provider rotation --review-model rotation --concurrency 4

# استخدام مزود AI محدد (--provider)
python run_ai_verify.py --provider opencode --model minimax-m2.5-free
python run_ai_verify.py --provider openrouter --model openai/gpt-4o-mini
python run_ai_verify.py --provider openrouter --model openai/gpt-oss-120b:free

# تحديد مفتاح API مباشرة (--api-key)
python run_ai_verify.py --provider opencode --api-key sk-xxx

# مراجعة AI: نموذج ثاني يراجع قرارات النموذج الأول
python run_matcher.py --provider opencode --model minimax-m2.5-free --review-model big-pickle
python run_ai_verify.py --provider opencode --model minimax-m2.5-free --review-model big-pickle

# مراجعة فقط للقرارات بثقة أقل من 0.9
python run_matcher.py --review-model big-pickle --review-threshold 0.9

# مراجعة كاملة (كل قرارات AI) + تتبع
python run_matcher.py --provider opencode --model minimax-m2.5-free --review-model big-pickle --review-threshold 1.0 --trace --limit 50

# اختبار اتصال API
python test_api.py

# مقارنة نماذج AI (benchmark)
python benchmark_models.py --provider opencode --preset opencode
python benchmark_models.py --provider openrouter --preset openrouter-free
python benchmark_models.py --models big-pickle gpt-5.1 --provider opencode

# اختبارات
python run_tests.py
```

### خيارات سطر الأوامر

#### `run_matcher.py` و `run_ai_verify.py`

| الخيار | الوصف | الافتراضي |
|---|---|---|
| `--limit N` | معالجة أول N دواء فقط | الكل |
| `--log-level` | مستوى السجلات (DEBUG, INFO, WARNING, ERROR) | INFO |
| `--threshold` | حد المطابقة الخوارزمية | 80 |
| `--ai-threshold` | حد إحالة المطابقات للـ AI | 90.0 |
| `--output` | مسار ملف الإخراج | output/matched_drugs_verified.csv |
| `--trace` | تتبع تفصيلي لكل خطوة (CSV+TXT في output/trace/) | معطل |
| `--no-ai` | تخطي AI (مطابقة خوارزمية فقط بدون تحقق أو بحث) | معطل |
| `--provider` | مزود API: `rotation`, `groq`, `opencode`, `openrouter`, `custom` | من .env |
| `--model` | نموذج AI (مثل `big-pickle`, `openai/gpt-4o-mini`) | من .env |
| `--api-key` | مفتاح API (يتجاوز .env) | من .env |
| `--review-model` | موديل مراجعة ثاني، أو `rotation` لاختيار reviewer من attempts الصالحة | من .env |
| `--concurrency N` | عدد طلبات AI المتوازية ويستخدم أيضًا في preflight | 5 |
| `--no-ai-preflight` | تعطيل اختبار صحة موديلات/مفاتيح AI قبل التشغيل | معطل |
| `--ai-timeout` | مهلة اختبار كل model/key في preflight بالثواني | 10 |
| `--ai-search-limit N` | أقصى عدد unmatched يدخل مرحلة AI search | بلا حد |

### تشغيل AI آمن وسريع

عند تشغيل `run_matcher.py` مع AI، يقوم البرنامج تلقائيًا بعمل preflight سريع للمفاتيح والموديلات المتاحة. إذا فشل موديل محدد في نفس وقت التشغيل، لا يعتمد عليه البرنامج حتى لو كان مكتوبًا في `.env`، ويستخدم أول combo صالح من نفس قائمة `AI_MODEL` و`FALLBACK_MODELS` و`REVIEW_MODEL`.

إذا لم يجد preflight أي model/key صالح، يكمل البرنامج تلقائيًا بدون AI بدل أن يتوقف، ويظهر السبب في `trace` عند تفعيل `--trace`.

للتشغيل الطويل، يفضل:

```bash
python test_opencode_models.py --mode both --timeout 20 --concurrency 4
python test_ai_rotation.py --providers auto --mode json --timeout 10 --concurrency 4
python run_matcher.py --provider rotation --trace --ai-search-limit 200
```

مرحلة AI search لا ترسل كل `no_match` إلى النموذج. يتم إرسال الحالات التي لديها مرشحين أقوياء وآمنين فقط، مع الاحتفاظ بقواعد الرفض الخوارزمية مثل اختلاف الشكل أو الجرعة أو route أو imported/local.

في وضع `rotation`، يعتبر `.env` قائمة candidates فقط. البرنامج يختبر
المتاح وقت التشغيل، ثم يرتب attempts حسب التوفر، جودة الموديل، الكوتا،
والسرعة، ويبدأ بأفضل provider/model/key صالح.
يتم تقسيم موديلات كل provider إلى 3 مستويات حسب ترتيب `DEFAULT_MODELS`،
ثم يدور داخل المستوى الأقوى أولاً بنظام round-robin بين كل
`provider/key/model` قبل تكرار نفس التركيبة. إذا انتهت محاولات المستوى
الأقوى بسبب quota أو failures، ينتقل تلقائياً للمستوى التالي داخل نفس التشغيل.

يمكن استخدام `--review-model rotation` مع `--provider rotation` لتشغيل مراجعة
ثانية على قرارات AI باستخدام أفضل attempt آخر متاح قدر الإمكان. إذا لم يوجد
إلا attempt واحد صالح، يستخدمه البرنامج كخيار أخير بدل تعطيل المراجعة بالكامل.

#### `benchmark_models.py`

| الخيار | الوصف | الافتراضي |
|---|---|---|
| `--provider` | مزود API | من .env |
| `--preset` | مجموعة نماذج: `openrouter-free`, `openrouter-paid`, `openrouter-all`, `opencode` | حسب provider |
| `--models` | نماذج محددة للاختبار | حسب preset |
| `--output` | مسار تقرير Markdown | docs/MODEL_BENCHMARK.md |
| `--api-key` | مفتاح API (يتجاوز .env) | من .env |
| `--base-url` | رابط API (يتجاوز provider) | حسب provider |

## 📁 الهيكل

```
medicompare/
├── drug_matcher/          # الحزمة الأساسية
│   ├── config.py          # الإعدادات
│   ├── normalizer.py      # التطبيع
│   ├── indexer.py         # البحث
│   ├── ai_steps.py        # خطوات AI (تحقق + بحث + مراجعة)
│   ├── verifier.py        # AI API client (تحقق + مراجعة)
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
| `verifier.py` | التحقق بـ AI متزامن (max 5 طلبات متوازية) + مراجعة بنموذج ثاني |
| `pipeline.py` | 5 مراحل: مطابقة → تحقق → بحث → مراجعة → تنظيف |

## 📊 العمليات الخمس

```
1️⃣ المطابقة الخوارزمية     Brand Index (O(1)) + Fuzzy (O(n))
2️⃣ التحقق بالـ AI          للنتائج الضعيفة (<90%)
3️⃣ بحث الـ AI               عن مطابقات للأصناف غير المطابقة
4️⃣ مراجعة AI ثاني          يراجع قرارات النموذج الأول (ثقة < عتبة المراجعة)
5️⃣ تنظيف خوارزمي نهائي     تحقق إضافي
```

## 📋 الإخراج

ملف `output/matched_drugs_verified_YYYYMMDD_HHMMSS.csv`:

| العمود | الوصف |
|---|---|
| code | كود الدواء |
| drug_name | اسم الدواء الأصلي |
| matched_product_name_en | الاسم المطابق الإنجليزي |
| matched_product_name_ar | الاسم المطابق العربي |
| match_score | نسبة المطابقة (0-100) |
| verified | الحالة (algo_match, ai_confirmed, ai_confirmed_reviewed, ai_review_rejected, etc) |
| match_method | طريقة المطابقة (brand_index, token_set_ratio, etc) |
| ai_confidence | ثقة النموذج الأول (0.0-1.0) |
| ai_review_confidence | ثقة نموذج المراجعة (0.0-1.0) |

## ⚙️ الإعدادات الافتراضية

```python
fuzzy_threshold = 80              # الحد الأدنى للمطابقة
brand_prefix_min = 4              # طول البادئة للعلامة التجارية
ai_verify_threshold = 90.0        # نسبة الإحالة للـ AI
ai_max_concurrent = 5             # طلبات AI المتوازية
ai_batch_size = 20                # حجم دفعة الـ AI
ai_review_threshold = 1.0         # عتبة مراجعة AI (مراجعة القرارات بثقة < هذا)
```

راجع [ARCHITECTURE.md](docs/ARCHITECTURE.md) لفهم كل خيار بالتفصيل.

## 🎯 الميزات

✅ **فهرس مقلوب**: بحث O(1) عن طريق البادئة  
✅ **Fuzzy Matching**: 3 طرق مختلفة للمقارنة  
✅ **AI Verification**: تحقق متزامن من OpenRouter API  
✅ **AI Review**: نموذج ثاني يراجع قرارات النموذج الأول ذات الثقة المنخفضة  
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
| AI مراجعة واحدة | O(1) | 1-3s |
| AI مراجعة دفعة (20) | O(1) | 3-5s (متوازي) |

## 🤖 مزودي API المدعومين

| المزود | `--provider` | Base URL | النموذج الافتراضي |
|---|---|---|---|
| OpenCode Zen | `opencode` | `opencode.ai/zen/v1` | `big-pickle` |
| Groq | `groq` | `api.groq.com/openai/v1` | `openai/gpt-oss-120b` |
| Rotation | `rotation` | يختار تلقائيًا | أفضل attempt صالح |
| OpenRouter | `openrouter` | `openrouter.ai/api/v1` | `openai/gpt-4o-mini` |
| مخصص | `custom` | من .env | من .env |

### أفضل النماذج المجانية (نتائج Benchmark)

| النموذج | المزود | الدقة | مطابقة | رفض | الوقت |
|---|---|---|---|---|---|
| `big-pickle` 🥇 | OpenCode | **92%** | 83% | 100% | 41s |
| `gpt-oss-20b:free` 🥈 | OpenRouter | **80%** | 92% | 69% | 124s |
| `gpt-oss-120b:free` 🥉 | OpenRouter | **72%** | 92% | 54% | 122s |

> راجع [FREE_BENCHMARK.md](docs/FREE_BENCHMARK.md) و [OPENCODE_BENCHMARK.md](docs/OPENCODE_BENCHMARK.md) للتفاصيل.

## 📝 الملاحظات

- أفضل نموذج مجاني: `big-pickle` من OpenCode (92% دقة)
- معدل النجاح: 63.2% خوارزمي + ~85% مع التحقق
- ~25 تطابق قد تحتاج مراجعة يدوية
- الأسماء العربية: لا يتم التعامل معها في المطابقة

## 🔗 الروابط

- [GitHub Repository](https://github.com/abdalhamid19/medicompare)
- [Issues & Discussions](https://github.com/abdalhamid19/medicompare/issues)
