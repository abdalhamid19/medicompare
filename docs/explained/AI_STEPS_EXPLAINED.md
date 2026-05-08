# شرح تفصيلي لخطوات AI في MediCompare

## نظرة عامة

الـ AI يمر بمرحلتين مستقلتين بعد انتهاء المطابقة الخوارزمية:

| المرحلة | الاسم | الهدف |
|---|---|---|
| Phase 2 | AI Verification | التحقق من صحة المطابقات الضعيفة |
| Phase 3 | AI Search | البحث عن مطابقات للأصناف غير المطابقة |

كل مرحلة لها **شروط دخول** محددة — لا يُرسل كل شيء للـ AI.

---

## Phase 2: AI Verification (التحقق)

### شرط الدخول

الدواء يدخل هذه المرحلة **فقط** إذا تحققت **كل** الشروط التالية:

1. **تمت مطابقته خوارزمياً** — أي `matched_product_name_en` ليس فارغاً
2. **نسبة المطابقة أقل من حد التحقق** — أي `match_score < ai_verify_threshold` (الافتراضي: 90.0)

بمعنى آخر: الخوارزمية قالت "هذا تطابق" لكن بنسبة ضعيفة (80-89)، فالـ AI يتأكد هل هو صحيح أم لا.

### ماذا يحدث داخل الـ AI

لكل دواء يدخل التحقق:

1. يُرسل للـ AI السؤال: **"هل هذا التطابق صحيح؟"**
2. الـ AI يجيب بأحد ثلاثة:

| إجابة AI | المعنى | ماذا يحدث |
|---|---|---|
| `is_correct = True` | التطابق صحيح | `verified = ai_confirmed` |
| `is_correct = False` + بديل أفضل | التطابق خاطئ لكن وجد بديل | `verified = ai_corrected` — يُستبدل بالبديل |
| `is_correct = False` + لا بديل | التطابق خاطئ ولا يوجد بديل | `verified = ai_rejected` — يُلغى التطابق |

### مثال حقيقي 1: تطابق ضعيف تم تأكيده

```
الدواء: FEROGLOBIN B12 30 CAP
الخوارزمية طابقته مع: FEROGLOBIN 30 CAPS
النسبة: 85.0 (أقل من 90 → يدخل AI)

AI: "هل FEROGLOBIN 30 CAPS تطابق صحيح لـ FEROGLOBIN B12 30 CAP؟"
AI: "نعم، هذا صحيح — نفس البراند ونفس الشكل"

النتيجة: verified = ai_confirmed
```

### مثال حقيقي 2: تطابق ضعيف تم رفضه

```
الدواء: ***GREEN TEA
الخوارزمية طابقته مع: GREENTAL 30 CAP
النسبة: 82.4 (أقل من 90 → يدخل AI)

AI: "هل GREENTAL 30 CAP تطابق صحيح لـ GREEN TEA؟"
AI: "لا — GREENTAL دواء مختلف (جينتال) وليس شاي أخضر"

يبحث عن بديل بـ fuzzy_match:
  - ORGANIC NATION MATCHA GREEN TEA 60 CAP → score=100
  - لكن components_match يرفضه (different_brand)

لا يوجد بديل صالح → verified = ai_rejected
التطابق يُلغى تماماً
```

### مثال حقيقي 3: تطابق خاطئ تم تصحيحه

```
الدواء: PANADOL EXTRA 24 TAB
الخوارزمية طابقته مع: PANADOL 20 TAB
النسبة: 85.0 (أقل من 90 → يدخل AI)

AI: "هل PANADOL 20 TAB تطابق صحيح لـ PANADOL EXTRA 24 TAB؟"
AI: "لا — هذا PANADOL عادي وليس EXTRA"

يبحث عن بديل:
  - PANADOL EXTRA 24 TAB → score=95, components_match=ok

AI يؤكد البديل → verified = ai_corrected
التطابق يُستبدل: PANADOL 20 TAB → PANADOL EXTRA 24 TAB
```

### من لا يدخل Phase 2

| الحالة | السبب |
|---|---|
| `score ≥ 90` | التطابق قوي بما يكفي — لا حاجة للتحقق |
| `no_match` (غير مطابق) | لا يوجد تطابق ليُتحقق منه |
| بدون API key | يتخطى بالكامل |

---

## Phase 3: AI Search (البحث)

### شرط الدخول

الدواء يدخل هذه المرحلة **فقط** إذا تحققت **كل** الشروط التالية:

1. **لم يُطابق أبداً** — أي `matched_product_name_en` فارغ أو NaN
2. **الاسم المعياري ليس قصيراً جداً** — أي `len(norm) ≥ 3`
3. **يتوفر API key**

هذه هي الأصناف التي فشلت الخوارزمية في مطابقتها بالكامل.

### ماذا يحدث داخل الـ AI

لكل دواء غير مطابق:

1. **جمع مرشحين** من مصدرين:
   - **Fuzzy search**: باستخدام 3 scorers (token_set_ratio, token_sort_ratio) مع `score ≥ 70` + `components_match = ok`
   - **Brand lookup**: المنتجات التي تتشارك نفس بادئة البراند مع `score ≥ 65`

2. **إزالة التكرار** — إذا ظهر نفس المنتج من مصدرين مختلفين

3. **إرسال المرشحين للـ AI**: "أي من هذه المنتجات هو الأنسب؟"

4. **قرار الـ AI**:
   - `confidence ≥ 0.7` + وجد تطابق → `verified = ai_found`
   - أقل من 0.7 أو لم يجد → يبقى غير مطابق

### مثال حقيقي 4: صنف غير مطابق وجد الـ AI له تطابق

```
الدواء: +***IMP ANAFRANIL 25MG 30 TAB
الخوارزمية: no_match

الاسم المعياري: ANAFRANIL 25 MG 30 TAB
البراند: ANAFRANIL

جمع المرشحين:
  [fuzzy/token_set_ratio]  ANAFRONIL 25 MG 30 TAB  score=95.5
  [fuzzy/token_sort_ratio] ANAFRONIL 25 MG 30 TAB  score=95.5
  لكن components_check: different_brand (ANAFRANIL ≠ ANAFRONIL)

ملاحظة: المرشح فشل في components_match → لا يُرسل للـ AI
النتيجة: يبقى no_match
```

> هذا مثال مهم يوضح لماذا ANAFRANIL لم يُطابق — الخوارزمية وجدت ANAFRONIL
> لكن `components_match` رفضته لأن البراند مختلف (ANAFRANIL ≠ ANAFRONIL).
> حتى الـ AI لا يراه كمرشح صالح.

### مثال حقيقي 5: صنف كانت الخوارزمية ستجد تطابق لو خُفض الحد

```
الدواء: +***IMP OSTEOCARE ORIGINAL 30 TAB
الاسم المعياري: OSTEOCARE ORIGINAL 30 TAB
البراند: OSTEOCAREORIGINAL

جمع المرشحين:
  [fuzzy/token_set_ratio]  OSTEOCARE 30 TABS  score=82.8
  [fuzzy/partial_token_sort_ratio] OSTEOCARE 30 TABS  score=90.3
  لكن components_check: different_brand
    (OSTEOCAREORIGINAL ≠ OSTEOCARE — بادئة مختلفة)

المرشحون فشلوا في components_match → لا يُرسلون للـ AI
النتيجة: يبقى no_match
```

### مثال حقيقي 6: صنف وجد الـ AI تطابقه (سيناريو ناجح)

```
الدواء: +***imp PANADOL EXTRA 24 TAB IMP
الاسم المعياري: PANADOL EXTRA 24 TAB
البراند: PANADOLEXTRA

جمع المرشحين:
  [brand_lookup] PANADOL EXTRA 24 TAB  score=95.0  components_match=ok
  [fuzzy/token_set_ratio] PANADOL EXTRA 24 TAB  score=98.0

يُرسل المرشحون للـ AI:
  AI: "PANADOL EXTRA 24 TAB هو التطابق الأنسب"
  confidence = 0.95 ≥ 0.7

النتيجة: verified = ai_found, match_method = ai_search
```

### من لا يدخل Phase 3

| الحالة | السبب |
|---|---|
| لديه تطابق (من Phase 1 أو 2) | لا يحتاج بحث |
| `len(norm) < 3` | اسم قصير جداً لا يمكن البحث به |
| بدون API key | يتخطى بالكامل |

---

## مخطط تدفق كامل

```
الدواء المدخل
    │
    ▼
┌─────────────────────┐
│  Phase 1: خوارزمية   │
│  brand_index + fuzzy │
└─────────┬───────────┘
          │
    ┌─────┴──────┐
    │            │
  مطابق      غير مطابق
  score=X     no_match
    │            │
    ▼            ▼
┌──────────┐  ┌──────────────┐
│score≥90? │  │ Phase 3:     │
│          │  │ AI Search    │
└────┬─────┘  │ (غير المطابق)│
  نعم│ لا      └──────┬───────┘
    │  │              │
    │  ▼              ▼
    │ ┌────────────┐ ┌──────────┐
    │ │Phase 2:    │ │مرشحين    │
    │ │AI Verify   │ │+AI قرار  │
    │ │(الضعيف)    │ └────┬─────┘
    │ └──────┬─────┘      │
    │        │            │
    │   ┌────┴───┐   ┌────┴───┐
    │   confirmed│   found   not
    │   corrected│   ai_found found
    │   rejected │
    │        │    │
    ▼        ▼    ▼
┌──────────────────────┐
│  Phase 4: تنظيف نهائي │
│  component + brand    │
└──────────────────────┘
          │
          ▼
      النتائج النهائية
```

---

## الأرقام الافتراضية

| الإعداد | القيمة | المعنى |
|---|---|---|
| `fuzzy_threshold` | 80 | أقل نسبة للمطابقة الخوارزمية |
| `ai_verify_threshold` | 90.0 | الأصناف تحت هذا الحد تُرسل للتحقق |
| `ai_batch_size` | 20 | عدد الأصناف في كل دفعة AI |
| `ai_max_concurrent` | 5 | أقصى عدد طلبات AI متوازية |
| `confidence` (search) | 0.7 | أقل ثقة لقبول نتيجة AI Search |
| `fuzzy_score` (search candidates) | 70 | أقل نسبة لاعتبار مرشح في البحث |
| `brand_score` (search candidates) | 65 | أقل نسبة لمرشح brand في البحث |

---

## كيف تقرأ ملف الـ Trace لفهم الأخطاء

عند تشغيل `--log`، ملف الـ TXT يوضح بالضبط فين حدث الرفض:

```
DRUG: [55748] OSTEOCARE SYRUP 200ML
  norm=OSTEOCARE SYRUP 200 ML  brand=OSTEOCARE
  [brand_lookup] idx=1692  score=66.7     ← وجد مرشح لكن score ضعيف
  [fuzzy/token_set_ratio] score=81.8      ← وجد مرشح
  [component_check] ok=no  reason=different_brand  ← ← هنا السبب!
  >> FINAL: match=NONE
```

السطر `[component_check] ok=no reason=different_brand` يخبرك أن البراند مختلف
(OSTEOCARE في الدواء ≠ OSTEOMOHA في المرشح)، لذلك رُفض التطابق.

هذا يسمح لك بتحديد:
- **هل المشكلة في threshold؟** — مرشح جيد رُفض بسبب الحد
- **هل المشكلة في components_match؟** — مرشح عالي النسبة لكن براند مختلف
- **هل المشكلة في عدم وجود مرشح أصلاً؟** — لا توجد نتائج fuzzy فوق 80
