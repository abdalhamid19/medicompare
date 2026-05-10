# أفضل ممارسات كتابة الكود — MediCompare

> دليل مرجعي للحفاظ على كود نظيف، سريع، موفّر للرام، وقابل للتوسع

---

## 1. حدود الأحجام

| العنصر | الحد الأقصى | السبب |
|---|---|---|
| **سطر واحد** | 100 حرف | قابلية القراءة بدون scroll أفقي |
| **دالة (function)** | 30 سطر | دالة واحدة = مسؤولية واحدة |
| **كلاس (class)** | 300 سطر | كلاس كبير = مسؤوليات كثيرة |
| **ملف (file)** | 150 سطر | ملف طويل = صعوبة التنقل والمراجعة |
| **`__slots__`** | مطلوب دائماً | توفير ~40% رام لكل كائن |

### تجاوز الحدود

- **سطر > 100 حرف**: اكسر الأسطر الطويلة باستخدام `()` أو `\`
```python
# ❌ سيء
result = await verifier.find_better_match(drug_name, candidates, threshold=cfg.ai_verify_threshold, max_retries=3)

# ✅ جيد
result = await verifier.find_better_match(
    drug_name, candidates,
    threshold=cfg.ai_verify_threshold,
    max_retries=3,
)
```

- **دالة > 30 سطر**: استخرج أجزاء مستقلة كدوال فرعية
```python
# ❌ سيء: دالة طويلة تفعل كل شيء
async def _apply_review_results(verifier, results, index, all_results, cfg, trace):
    # 80 سطر من المنطق المتداخل...

# ✅ جيد: قسم إلى دوال صغيرة
async def _apply_review_results(verifier, results, index, all_results, cfg, trace):
    for rr in all_results:
        await _apply_one_review(verifier, results, index, rr, cfg, trace)

async def _apply_one_review(verifier, results, index, rr, cfg, trace):
    if rr.get("api_failed"):
        _apply_api_failed_review(results, rr)
    elif rr.get("is_correct"):
        _apply_agreed_review(results, rr)
    else:
        await _apply_disagreed_review(verifier, results, index, rr, cfg, trace)
```

- **ملف > 150 سطر**: قسم إلى وحدة جديدة (module)

---

## 2. هيكل المشروع

```
medicompare/
├── drug_matcher/           # الحزمة الأساسية
│   ├── __init__.py
│   ├── config.py           # إعدادات + ثوابت (< 150 سطر)
│   ├── normalizer.py       # تطبيع الأسماء + parsing (< 200 سطر)
│   ├── indexer.py          # فهرس البحث + fuzzy (< 200 سطر)
│   ├── pipeline.py         # تنسيق المراحل (< 350 سطر)
│   ├── ai_steps.py         # خطوات AI (verify/search/review) (< 400 سطر)
│   ├── verifier.py         # عميل API + fallback (< 400 سطر)
│   ├── trace_log.py        # تسجيل التتبع (< 500 سطر — استثناء)
│   └── utils.py            # دوال مساعدة مشتركة
├── run_matcher.py          # CLI: pipeline كامل
├── run_ai_verify.py        # CLI: تحقق AI فقط
├── tests/                  # اختبارات
│   ├── test_normalizer.py
│   ├── test_indexer.py
│   └── test_pipeline.py
├── docs/                   # توثيق
├── output/                 # نتائج
│   └── trace/              # ملفات تتبع
└── .env                    # مفاتيح API
```

### قواعد التقسيم

- **كل ملف = مسؤولية واحدة** (Single Responsibility)
- **لا استيراد دائري** (circular import) — استخدم حقن التبعيات بدلاً من ذلك
- **الثوابت في أعلى الملف** أو في `config.py`
- **الدوال الخاصة تبدأ بـ `_`** — لا تُصدّر عبر `__all__`

---

## 3. أداء البرنامج (Speed)

### 3.1 عمليات I/O

| القاعدة | التطبيق |
|---|---|
| **قراءة مرة واحدة** | اقرأ CSV كاملاً ثم اعمل في الذاكرة |
| **كتابة مرة واحدة** | اجمع النتائج في list ثم اكتب دفعة واحدة |
| **API: تجميع (batching)** | أرسل 20 طلب دفعة واحدة بدل 20 طلب متتالي |
| **API: تزامن (concurrency)** | استخدم `asyncio.Semaphore` لتحديد التزامن |
| **API: إعادة محاولة ذكية** | `429` → انتظر `Retry-After`، `401/403` → تخطّى فوراً |

```python
# ✅ جيد: batch + semaphore
async with asyncio.Semaphore(5):
    tasks = [verify_one(a, b) for a, b, _ in batch]
    results = await asyncio.gather(*tasks, return_exceptions=True)
```

### 3.2 حسابات

| القاعدة | التطبيق |
|---|---|
| **تجنب الحلقات على DataFrame** | استخدم vectorized operations (`pd.to_numeric`, `.isin()`) |
| **خزّن النتائج المعاد حسابها** | `_failed_combos` cache يمنع إعادة محاولة (key, model) فاشل |
| **فهرس البحث مرة واحدة** | `DrugIndex` يُبنى مرة عند التحميل، لا في كل استعلام |
| **`frozenset` للبحث السريع** | `FORM_WORDS`, `FORM_PREFIXES` — بحث O(1) بدل O(n) |

### 3.3 نصوص و Regex

| القاعدة | التطبيق |
|---|---|
| **Compile regex مرة واحدة** | `_DOSAGE_RE = re.compile(...)` في أعلى الملف |
| **تجنب `re.sub` متكرر** | مرر الاسم مرة واحدة عبر `normalize()` |
| **استخدم `str.split()` بدل regex** عندما ممكن | أسرع 5-10x |

---

## 4. استهلاك الرام (Memory)

### 4.1 DataFrames

| القاعدة | التطبيق |
|---|---|
| **حدد الأعمدة عند القراءة** | `usecols=[0, 1]` بدل قراءة كل الأعمدة |
| **نوع البيانات `str`** | `dtype=str` يمنع pandas من استنتاج أنواع ضخمة |
| **امسح البيانات المؤقتة** | `del unmatched; gc.collect()` بعد الانتهاء |
| **لا تنسخ بدون سبب** | استخدم `.copy()` فقط عند التعديل الفعلي |

```python
# ❌ سيء: نسخة كاملة بدون سبب
matched = results[results["matched_product_name_en"] != ""]

# ✅ جيد: نسخة فقط عند الحاجة للتعديل
to_verify = results[condition].copy()  # نعدل هذا الـ subset
```

### 4.2 الكائنات (Objects)

| القاعدة | التطبيق |
|---|---|
| **`__slots__` دائماً** | يمنع `__dict__` ويوفر ~40% رام لكل كائن |
| **`@dataclass(slots=True)`** | نفس الفائدة مع بناء أنظف |
| **تجنب القوائم الكبيرة في الكائنات** | `_fallback_log: list[str]` — امسحها بعد القراءة |
| **استخدم `tuple` بدل `list`** للثوابت | `api_keys: tuple[str, ...]` — أسرع وأخف |

### 4.3 جلسات HTTP

| القاعدة | التطبيق |
|---|---|
| **جلسة واحدة لكل pipeline** | `aiohttp.ClientSession` تُنشأ مرة وتُغلق مرة |
| **استخدم `async with`** | يضمن إغلاق الجلسة حتى مع الأخطاء |
| **لا تفتح جلسة لكل طلب** | كل جلسة = connection pool + رام |

---

## 5. قابلية التوسع (Scalability)

### 5.1 الإعدادات

| القاعدة | التطبيق |
|---|---|
| **كل حد قابل للتعديل** | `MatchingConfig`, `APIConfig` — لا أرقام سحرية |
| **CLI يُجاوز الإعدادات** | `--threshold`, `--model`, `--start`, `--end` |
| **`.env` للبيانات الحساسة** | مفاتيح API، لا في الكود أبداً |
| **ثوابت في `config.py`** | `PROVIDERS` dict — إضافة مزود = سطر واحد |

### 5.2 البنية

| القاعدة | التطبيق |
|---|---|
| **فصل المراحل** | `run_matching()` → `run_ai_verification()` → `run_ai_search()` → `run_ai_review()` |
| **كل مرحلة مستقلة** | يمكن تشغيل أي مرحلة منفصلة |
| **حقن التبعيات** | `AIVerifier(cfg=api_cfg)` — لا globals |
| **واجهة موحدة** | `_call_api()` مركزية — إضافة مزود جديد = تعديل مكان واحد |

### 5.3 إضافة مزود API جديد

```python
# في config.py — سطر واحد فقط:
PROVIDERS["newprovider"] = {
    "base_url": "https://api.newprovider.com/v1",
    "env_key": "NEWPROVIDER_API_KEY",
    "env_keys": ["NEWPROVIDER_API_KEY"],
    "default_model": "model-name",
}
```

### 5.4 إضافة نموذج احتياطي جديد

```bash
# في .env — سطر واحد فقط:
FALLBACK_MODELS=nemotron-3-super-free,hy3-preview-free,trinity-large-preview-free,new-model-free
```

---

## 6. جودة الكود

### 6.1 التسمية

| النوع | الصيغة | مثال |
|---|---|---|
| دالة/متغير | `snake_case` | `run_ai_verification` |
| كلاس | `PascalCase` | `MatchPipeline` |
| ثابت | `UPPER_SNAKE` | `FORM_WORDS` |
| خاص (private) | `_leading_underscore` | `_call_api` |
| متغير مؤقت | `اسم واضح قصير` | `vr` للنتيجة، `rr` للمراجعة |

### 6.2 التعليقات

- **لا تعليق يكرر الكود**: `# increment counter` قبل `counter += 1` ❌
- **علّق القرارات**: `# Cache auth errors to skip in future` ✅
- **علّق الـ WHY لا الـ WHAT**: `# Using frozenset for O(1) lookup` ✅
- **Docstring لكل دالة عامة**: سطر واحد يكفي

### 6.3 الأخطاء

| القاعدة | التطبيق |
|---|---|
| **لا `bare except`** | `except Exception as e` مع تسجيل الخطأ |
| **سجّل دائماً** | `logger.warning()` للأخطاء المتوقعة، `logger.error()` للحرجة |
| **فشل سريع (fail fast)** | `if not api_key: return early` بدل تداخل عميق |
| **`return_exceptions=True`** في `gather` | لا تدع خطأ واحد يكسر الباقة كاملة |

---

## 7. اختبارات

| القاعدة | التطبيق |
|---|---|
| **اختبر الدوال الصغيرة أولاً** | `parse_drug`, `components_match`, `normalize` |
| **اختبر الحالات الحدية** | أسماء فارغة، أرقام فقط، أسماء طويلة جداً |
| **`subTest` للحالات المتعددة** | `with self.subTest(raw=raw):` |
| **لا تحذف اختبار أبداً** | فقط أضف أو عدّل |

---

## 8. ملخص سريع — قائمة مراجعة

- [ ] سطر < 100 حرف؟
- [ ] دالة < 30 سطر؟
- [ ] ملف < 150 سطر؟
- [ ] `__slots__` على كل كلاس؟
- [ ] regex مُصرّح (compiled) في أعلى الملف؟
- [ ] لا أرقام سحرية — كل شيء في config؟
- [ ] `async with` للجلسات والموارد؟
- [ ] `return_exceptions=True` في `gather`؟
- [ ] تسجيل أخطاء API مع `logger.warning`؟
- [ ] لا نسخ DataFrame بدون سبب؟
- [ ] فحص مكونات الأدوية يعمل بشكل صحيح؟
- [ ] اختبارات تمر؟
