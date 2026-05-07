# MediCompare2 - Drug Matching & Verification Pipeline

## نظرة عامة

نظام متكامل لمطابقة أسماء الأدوية من ملف المخزون (`all_non_cosmotics_drug_all.csv`) مع أسماء المنتجات في ملف التوريد (`tawreed_products.csv`)، مع التحقق من صحة التطابقات باستخدام الذكاء الاصطناعي.

---

## النتائج الحالية

| المؤشر | القيمة |
|---|---|
| إجمالي الأدوية | 6,295 |
| مطابق بنجاح | 3,981 (63.2%) |
| غير مطابق | 2,314 (36.8%) |
| تطابق 100% | 906 |
| تطابق 95-99% | 388 |
| تطابق 90-94% | 710 |
| تطابق 80-89% | 1,977 |

---

## هيكل المشروع

```
medicompare2/
├── all_non_cosmotics_drug_all.csv    # بيانات الأدوية (code, drug_name)
├── tawreed_products.csv              # بيانات التوريد (product_name_ar, product_name_en, store_product_id)
├── matched_drugs_verified.csv        # النتيجة النهائية
├── run_matcher.py                    # نقطة دخول - مطابقة خوارزمية فقط
├── run_ai_verify.py                  # نقطة دخول - المطابقة + التحقق بالـ AI
└── drug_matcher/                     # الحزمة الأساسية
    ├── __init__.py                   # تعريف الحزمة
    ├── config.py                     # الإعدادات المركزية
    ├── normalizer.py                 # تطبيع وتحليل أسماء الأدوية
    ├── indexer.py                    # فهرس مقلوب + مطابقة fuzzy
    ├── verifier.py                   # تحقق AI عبر OpenRouter API
    └── pipeline.py                   # منسق الـ pipeline الكامل
```

---

## الملفات بالتفصيل

### 1. `drug_matcher/config.py` - الإعدادات

مصدر الحقيقة الوحيد لكل إعدادات النظام. يستخدم `dataclass` ثابت (frozen) لمنع التعديل العشوائي.

**MatchingConfig** - إعدادات المطابقة:
- `fuzzy_threshold: int = 80` — الحد الأدنى لنسبة المطابقة fuzzy
- `brand_prefix_min: int = 4` — أقل طول بادئة للعلامة التجارية
- `brand_prefix_ratio: float = 0.75` — نسبة بادئة العلامة التجارية
- `ai_verify_threshold: float = 90.0` — التطابقات أقل من هذا تُرسل للـ AI للتحقق
- `ai_batch_size: int = 20` — حجم دفعة الـ AI
- `ai_max_concurrent: int = 5` — أقصى عدد طلبات AI متوازية
- `top_k_candidates: int = 10` — عدد المرشحين من fuzzy search

**APIConfig** - إعدادات الـ API:
- `api_key: str` — مفتاح OpenRouter API
- `base_url: str = "https://openrouter.ai/api/v1"` — رابط الـ API
- `model: str = "~google/gemini-flash-latest"` — نموذج AI (أرخص وأسرع)
- `max_tokens: int = 1024` — أقصى tokens للاستجابة
- `temperature: float = 0.1` — حرارة الـ model (منخفضة = نتائج ثابتة)

**Paths** - مسارات الملفات:
- `drugs_csv` — ملف الأدوية
- `tawreed_csv` — ملف التوريد
- `output_csv` — ملف النتائج
- `env_file` — ملف البيئة

---

### 2. `drug_matcher/normalizer.py` - التطبيع والتحليل

الوحدة المسؤولة عن تنظيف وتحليل أسماء الأدوية إلى مكوناتها الأساسية.

#### الثوابت

**FORM_WORDS** — كلمات الشكل الدوائي (تُستخدم لاستخراج الشكل):
- `TABLET`, `TAB`, `TABS`, `CAP`, `CAPS`, `CAPSULE`, `CAPSULES`
- `SACHET`, `SACHETS`, `AMP`, `AMPS`, `VIAL`, `VIALS`
- `SUPP`, `DROPS`, `PEN`, `CARTRIDGE`, `GUMMIES`, `PACKETS`
- `F.C.TAB`, `E.C.TAB`, `EXT.REL.TAB`, `CHEW.TAB`, `S.G.CAPS`, `FILM`, `LOZENGES`

**FORM_PREFIXES** — بادئات الشكل الدوائي (تُستخدم لاكتشاف النوع):
- `CREAM`, `GEL`, `OINTMENT`, `SYRUP`, `SUSP`, `SPRAY`
- `POWDER`, `LOTION`, `SOAP`, `SHAMPOO`, `OIL`, `SERUM`
- `INJECTION`, `INFUSION`, `SOLUTION`, `INHALER`
- `TOPICAL`, `ORAL`, `EYE`, `NASAL`, `EAR`
- `MASSAGE`, `CLEANSER`, `WASH`, `DOUCHE`

**NOISE_WORDS** — كلمات ضوضاء تُزال:
- `IMP`, `IMPORTED`, `BLUE`, `RED`, `WHITE`

#### الدوال

**`normalize(name: str) -> str`**

تنظيف اسم الدواء:
1. تحويل لأحرف كبيرة
2. إزالة بادئات الضوضاء (`+***`, `*.`)
3. إزالة كلمة `IMP`
4. معالجة التدوين العشري الأوروبي: `1.000 IU` ← `1000 IU` (قبل إزالة النقاط)
5. إزالة النقاط مع الحفاظ على الأعداد العشرية (`0.5`, `2.5` تبقى كما هي)
6. توحيد المسافات

**`parse_drug(name: str) -> DrugComponents`**

تحليل اسم الدواء إلى مكوناته:

| المكون | الوصف | مثال |
|---|---|---|
| `brand` | العلامة التجارية (كلمات أبجدية قبل أول رقم) | `PANADOL`, `COVERSYLPLUS` |
| `dosage_nums` | أرقام الجرعة | `('500',)`, `('5', '1.25')` |
| `dosage_units` | وحدات الجرعة | `('MG',)`, `('MG', 'MG')` |
| `qty` | الكمية (عدد أقراص/كبسولات) | `'30'`, `'14'` |
| `volume` | الحجم (مل) | `'120'`, `'500'` |
| `weight` | الوزن (جم) - مفصول عن الجرعة | `'30'`, `'15'` |
| `form` | الشكل الدوائي | `CREAM`, `SYRUP` |
| `normalized` | الاسم بعد التطبيع | `PANADOL 500 MG 30 TAB` |

ملاحظات مهمة:
- **الجرعة (MG, MCG, IU, %)** مفصولة عن **الوزن (GM, G)** — الوزن يمثل حجم العبوة وليس الجرعة
- **التدوين الأوروبي** يُعالج: `4.000 I.U.` ← `4000 IU`
- **الكمية** تستخرج من الرقم قبل كلمات الشكل (TAB, TABS, CAP, CAPS, etc.)

**`components_match(d, m, brand_prefix_min=4) -> tuple[bool, str]`**

التحقق من أن مكونين يمثلان نفس المنتج. تُرجع `(is_match, reason)`.

التحققات بالترتيب:
1. **العلامة التجارية** — بادئة مشتركة بطول `brand_prefix_min` على الأقل، أو واحدة تحتوي الأخرى
2. **الجرعة** — كل أرقام الجرعة يجب أن تتطابق
3. **الكمية** — إذا كلاهما محدد، يجب أن يتطابق
4. **الحجم** — إذا كلاهما محدد، يجب أن يتطابق
5. **الوزن** — إذا كلاهما محدد، يجب أن يتطابق

أسباب الرفض: `different_brand`, `different_dosage`, `different_quantity`, `different_volume`, `different_weight`

---

### 3. `drug_matcher/indexer.py` - الفهرسة والمطابقة

#### `DrugIndex` — فهرس مقلوب + مطابقة fuzzy

**البناء (`__init__`)**:
1. قراءة بيانات التوريد وتطبيع أسماء المنتجات
2. بناء **فهرس مقلوب** (`brand_index`): بادئة العلامة التجارية ← قائمة أرقام الصفوف
   - لكل منتج، يتم استخراج العلامة التجارية وإضافة بادئات بطول 3-7 أحرف
   - مثال: `PANADOL` ← `PAN`, `PANA`, `PANAD`, `PANADO`, `PANADOL`
3. **ذاكرة تخزين مؤقت** (`parsed_cache`): تحليل مسبق لكل منتج لتسريع المقارنة

**`lookup_by_brand(drug_components) -> list[tuple[dict, int]]`**

بحث سريع O(1) باستخدام الفهرس المقلوب:
1. استخراج بادئة العلامة التجارية من الـ drug
2. البحث في الفهرس من أطول بادئة لأقصرها
3. تصفية النتائج بـ `components_match`
4. إرجاع قائمة `(record, index)` للمرشحين الصالحين

**`fuzzy_match(query, top_k) -> list[tuple[dict, float, int]]`**

مطابقة fuzzy باستخدام `rapidfuzz`:
- يستخدم `token_set_ratio` كـ scorer أساسي
- يُرجع أعلى `top_k` نتائج فوق `fuzzy_threshold`

**`best_match(drug_name) -> tuple[dict|None, float, str]`**

إيجاد أفضل تطابق باستراتيجيتين:

**الاستراتيجية 1: Brand Index** (الأسرع - O(1)):
- بحث بالعلامة التجارية
- اختيار أفضل نتيجة بـ `token_sort_ratio`
- رفض إذا كانت النسبة أقل من `fuzzy_threshold`

**الاستراتيجية 2: Fuzzy Matching** (أبطأ - O(n)):
- تجربة 3 scorers: `token_set_ratio`, `token_sort_ratio`, `partial_token_sort_ratio`
- تصفية كل نتيجة بـ `components_match`
- اختيار أعلى نسبة

---

### 4. `drug_matcher/verifier.py` - التحقق بالذكاء الاصطناعي

#### `AIVerifier` — عميل AI غير متزامن مع تحديد المعدل

**البناء**:
- `max_concurrent: int = 5` — عدد الطلبات المتوازية (Semaphore)
- جلسة `aiohttp` تُدار كـ async context manager

**الـ Prompt**:

System prompt يحدد قواعد صارمة:
1. العلامة التجارية يجب أن تكون مطابقة (`PANADOL` ≠ `PANADOL EXTRA`)
2. أرقام الجرعة يجب أن تتطابق بالضبط (`0.8%` ≠ `0.4%`)
3. الكمية يجب أن تتطابق (إذا واحد محدد والآخر لا = عدم تطابق)
4. الحجم يجب أن يتطابق
5. شكل مختلف = خطأ (`CREAM` ≠ `GEL`)
6. علامة تجارية مختلفة = خطأ
7. `PLUS` أو `EXTRA` في واحد دون الآخر = عدم تطابق

**`verify_one(drug_a, drug_b) -> dict`**

التحقق من تطابق واحد:
- إرسال طلب لـ OpenRouter API
- استجابة JSON: `{"is_correct": bool, "reason": str, "confidence": float}`
- معالجة الأخطاء (API error, timeout, JSON parse)

**`verify_batch(matches) -> list[dict]`**

التحقق من دفعة تطابقات بشكل متوازي:
- كل عنصر: `(drug_a, drug_b, row_index)`
- يستخدم `asyncio.gather` مع التحكم بـ Semaphore

**`find_better_match(drug_name, candidates) -> dict|None`**

يطلب من الـ AI اختيار أفضل تطابق من قائمة مرشحين:
- يعرض حتى 5 مرشحين مع نسبهم
- يستجيب بـ `{"best_index": 0-5, "reason": str, "confidence": float}`
- `best_index = 0` يعني لا يوجد تطابق صحيح

---

### 5. `drug_matcher/pipeline.py` - منسق الـ Pipeline

#### `MatchPipeline` — الـ pipeline الكامل بأربع مراحل

**المرحلة 0: تحميل البيانات (`load_data`)**
- قراءة ملف الأدوية (code, drug_name)
- قراءة ملف التوريد وبناء `DrugIndex`
- طباعة إحصائيات التحميل

**المرحلة 1: المطابقة الخوارزمية (`run_matching`)**

لكل دواء في الملف:
1. استدعاء `DrugIndex.best_match(drug_name)`
2. إذا وُجد تطابق: حفظ البيانات مع `verified = "algo_match"`
3. إذا لم يُوجد: حفظ كـ `no_match`

النتائج تُحفظ في DataFrame بالأعمدة:
- `code` — كود الدواء
- `drug_name` — اسم الدواء الأصلي
- `matched_product_name_en` — الاسم الإنجليزي المطابق
- `matched_product_name_ar` — الاسم العربي المطابق
- `matched_store_product_id` — رقم المنتج في المخزن
- `match_score` — نسبة المطابقة
- `verified` — حالة التحقق
- `match_method` — طريقة المطابقة

**المرحلة 2: التحقق بالـ AI (`run_ai_verification`)**

لكل تطابق بنسبة أقل من `ai_verify_threshold` (90%):
1. إرسال للتحقق عبر `AIVerifier.verify_batch`
2. إذا **صحيح**: `verified = "ai_confirmed"`
3. إذا **خاطئ**:
   - البحث عن بديل أفضل عبر fuzzy + `components_match`
   - إذا وُجد بديل: `verified = "ai_corrected"` مع البيانات الجديدة
   - إذا لم يُوجد: `verified = "ai_rejected"` وحذف التطابق

**المرحلة 3: البحث بالـ AI عن مطابقات جديدة (`run_ai_search_unmatched`)**

لكل صنف غير مطابق:
1. بحث fuzzy بنسبة أقل (≥70) + بحث بالعلامة التجارية (≥65)
2. تصفية المرشحين بـ `components_match`
3. إزالة التكرارات
4. طلب الـ AI لاختيار الأفضل
5. إذا ثقة AI ≥ 0.7: `verified = "ai_found"`, `match_method = "ai_search"`

**المرحلة 4: التنظيف الخوارزمي (`run_post_cleanup`)**

فحص نهائي لكل التطابقات:
1. إعادة تحليل اسم الدواء واسم المنتج المطابق
2. التحقق بـ `components_match` (جرعة، كمية، حجم، وزن)
3. فحص إضافي لبادئة العلامة التجارية (أول 4 أحرف)
4. حذف أي تطابق خاطئ

---

### 6. نقاط الدخول

**`run_matcher.py`** — مطابقة خوارزمية فقط (بدون AI):
```python
pipeline = MatchPipeline(cfg=match_cfg, api_cfg=api_cfg)
result = asyncio.run(pipeline.run_full())
```

**`run_ai_verify.py`** — المطابقة الكاملة مع AI:
```python
pipeline = MatchPipeline(cfg=cfg, api_cfg=api_cfg)
pipeline.load_data()
pipeline.run_matching()                    # المرحلة 1
await pipeline.run_ai_verification()       # المرحلة 2
await pipeline.run_ai_search_unmatched()   # المرحلة 3
pipeline.run_post_cleanup()                # المرحلة 4
pipeline.save()
pipeline.print_stats()
```

---

## كيفية التشغيل

### المتطلبات
```bash
pip install pandas numpy rapidfuzz aiohttp
```

### تشغيل المطابقة فقط (بدون AI)
```bash
python run_matcher.py
```

### تشغيل المطابقة + التحقق بالـ AI
```bash
python run_ai_verify.py
```

### أو من كود Python
```python
import asyncio
from drug_matcher.config import MatchingConfig, APIConfig
from drug_matcher.pipeline import MatchPipeline

cfg = MatchingConfig(fuzzy_threshold=80, ai_verify_threshold=90.0)
api_cfg = APIConfig(api_key="your-openrouter-key")

pipeline = MatchPipeline(cfg=cfg, api_cfg=api_cfg)
result = asyncio.run(pipeline.run_full())
```

---

## ملف الإخراج `matched_drugs_verified.csv`

| العمود | الوصف |
|---|---|
| `code` | كود الصنف في المخزون |
| `drug_name` | اسم الدواء الأصلي |
| `matched_product_name_en` | الاسم الإنجليزي المطابق من التوريد |
| `matched_product_name_ar` | الاسم العربي المطابق من التوريد |
| `matched_store_product_id` | رقم المنتج في مخزن التوريد |
| `match_score` | نسبة المطابقة (80-100) |
| `verified` | حالة التحقق (انظر الجدول أدناه) |
| `match_method` | طريقة المطابقة (انظر الجدول أدناه) |

**قيم `verified`**:
| القيمة | المعنى |
|---|---|
| `algo_match` | مطابقة خوارزمية بنسبة ≥ 90% |
| `ai_confirmed` | أكدها الـ AI |
| `ai_corrected` | صححها الـ AI لتطابق أفضل |
| `ai_rejected` | رفضها الـ AI |
| `ai_found` | وجدها الـ AI للأصناف غير المطابقة |
| فارغ | غير مطابق |

**قيم `match_method`**:
| القيمة | المعنى |
|---|---|
| `brand_index` | مطابق عبر فهرس العلامة التجارية |
| `token_set_ratio` | مطابق عبر fuzzy token_set_ratio |
| `token_sort_ratio` | مطابق عبر fuzzy token_sort_ratio |
| `partial_token_sort_ratio` | مطابق عبر fuzzy partial |
| `ai_verified` | تم التحقق/التعديل بالـ AI |
| `ai_search` | وجده الـ AI للأصناف غير المطابقة |
| `no_match` | لم يُعثر على تطابق |

---

## التحسينات والمعالجات التي تمت

### مشكلة 1: الـ brand_index يُمرّر تطابقات خاطئة
- **السبب**: مطابقة بادئة العلامة التجارية فقط بدون فحص fuzzy score
- **الحل**: إضافة حد أدنى `fuzzy_threshold` لنتائج brand_index في `indexer.py:84`

### مشكلة 2: GM/G يُعتبر جرعة
- **السبب**: الـ regex للجرعة كان يلتقط `GM` و `G` كوحدة جرعة
- **الحل**: فصل الوزن (`GM/G`) عن الجرعة (`MG/MCG/IU/%`) في `normalizer.py`، مع إضافة حقل `weight` لـ `DrugComponents`

### مشكلة 3: التدوين العشري الأوروبي
- **السبب**: `4.000 I.U.` يُقرأ كـ `4.0` بدل `4000`
- **الحل**: معالجة النقاط الأوروبية قبل إزالة النقاط في `normalize()`

### مشكلة 4: النقاط العشرية تُزال
- **السبب**: `0.5 MG` يتحول لـ `0 5 MG` بعد إزالة النقاط
- **الحل**: إزالة النقاط فقط إذا لم تكن بين أرقام (regex lookahead/lookbehind)

### مشكلة 5: TABS/CAPS/GUMMIES غير ملتقطة
- **السبب**: regex الكمية لا يشمل صيغ الجمع
- **الحل**: إضافة `TABS`, `CAPS`, `AMPS`, `GUMMIES` لـ `_QTY_RE`

### مشكلة 6: GUM يُعتبر شكل دوائي
- **السبب**: `GUM` في FORM_WORDS، لكنه يُستخدم كاسم منتج (GUM-C)
- **الحل**: إزالة `GUM` من FORM_WORDS

### مشكلة 7: AI يؤكد تطابقات خاطئة
- **السبب**: نموذج gemini-flash متساهل جداً في التحقق
- **الحل**: تحسين الـ prompt بقواعد أكثر صرامة + إضافة مرحلة `run_post_cleanup` للتحقق الخوارزمي بعد الـ AI

### مشكلة 8: AttributeError في ai_max_concurrent
- **السبب**: محاولة الوصول لـ `ai_max_concurrent` من `APIConfig` بدل `MatchingConfig`
- **الحل**: تمرير `max_concurrent` كمعامل مباشر لـ `AIVerifier.__init__`

---

## الأداء والقابلية للتوسع

### الأداء
- **الفهرس المقلوب**: بحث O(1) بالعلامة التجارية بدل O(n) fuzzy scan
- **ذاكرة التخزين المؤقت**: تحليل مسبق لكل منتجات التوريد
- **الـ AI غير المتزامن**: مع `asyncio.Semaphore` للتحكم بالتزامن
- **المعالجة بالدفعات**: الـ AI يعالج 20 تطابق في كل دفعة

### القابلية للتوسع
- **إعدادات مركزية**: كل threshold وقابل للتعديل من `config.py`
- **وحدات مستقلة**: كل وحدة مسؤولة عن مهمة واحدة
- **إضافة scorers جديدة**: سهل في `indexer.py`
- **إضافة نماذج AI**: تغيير `model` في `APIConfig`
- **إضافة مراحل pipeline**: إضافة methods لـ `MatchPipeline`

---

## الملاحظات المعروفة

1. **نموذج AI متساهل**: gemini-flash يؤكد تطابقات خاطئة (كمية/جرعة مختلفة) — يُعالج بـ `run_post_cleanup`
2. **المرحلة 3 (بحث AI)**: لم تجد مطابقات جديدة حتى الآن — معظم الأصناف غير المطابقة ببساطة غير موجودة في التوريد
3. **أسماء الأدوية غير الإنجليزية**: لا يتم التعامل مع الأسماء العربية في المطابقة
4. **التحقق اليدوي**: ~25 تطابق مشبوه قد يحتاج مراجعة يدوية (كميات مختلفة أو علامات تجارية مشابهة جداً)
