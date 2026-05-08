# الخوارزميات والأمثلة - Algorithms & Examples

## 1. استراتيجيات البحث

### الاستراتيجية 1: Brand Index (السريعة - O(1))

**المبدأ:**
استخدام فهرس مسبق لتخزين العلامات التجارية بدلاً من البحث الخطي.

**البناء:**
```python
brand_index = {
    "PAN": [0, 2, 5],         # فهرس الصفوف التي تبدأ بـ PAN
    "PANA": [0, 2],
    "PANAD": [0],
    "PANADOL": [0],
    "PAR": [1, 3],
    "PARA": [1],
    "PARACE": [1],
    # ... وهكذا
}
```

**الخوارزمية:**
```
1. استخرج العلامة التجارية من الدواء المدخل
   مثال: "PANADOL 500 MG" → "PANADOL"

2. ابحث في الفهرس من أطول بادئة لأقصرها
   ["PANADOL", "PANADO", "PANAD", "PANA", "PAN"]

3. لكل بادئة: احصل على قائمة المنتجات الممكنة

4. صفّي القائمة بـ components_match()
   - تحقق من الجرعة
   - تحقق من الكمية
   - تحقق من الحجم

5. اختر أفضل نتيجة بـ token_sort_ratio()

6. إذا النسبة >= fuzzy_threshold (80%) → قبول
   وإلا → رفض والذهاب للاستراتيجية 2
```

**مثال عملي:**

```
Input:  PANADOL 500 MG 30 TABLET

Step 1: النطبيع
├─ تحويل لأحرف كبيرة: PANADOL 500 MG 30 TABLET
├─ إزالة النقاط والمسافات الزائدة
└─ النتيجة: PANADOL 500 MG 30 TAB

Step 2: استخراج المكونات
├─ brand: "PANADOL"
├─ dosage: 500 MG
├─ qty: 30
└─ form: TAB

Step 3: البحث بالفهرس
├─ جرب PANADOL ← وجدنا: [0, 25, 67]
├─ تحقق من components_match:
│  ├─ index 0: PANADOL 500 MG 20 TAB ✅ (عادي)
│  ├─ index 25: PANADOL 500 MG 30 TAB ✅ (مطابق تماماً!)
│  └─ index 67: PANADOL EXTRA 500 MG 30 TAB ✗ (مختلف)
│
├─ النتائج الصالحة: [0, 25]

Step 4: اختيار الأفضل
├─ قارن: "PANADOL 500 MG 30 TAB"
│  ├─ مع: "PANADOL 500 MG 20 TAB" → score = 89%
│  └─ مع: "PANADOL 500 MG 30 TAB" → score = 100% ✅

Step 5: التحقق
├─ score = 100% >= 80% → قبول!

Output: {
  "record": {"en": "PANADOL 500 MG 30 TAB", "ar": "..."},
  "score": 100,
  "method": "brand_index"
}
```

---

### الاستراتيجية 2: Fuzzy Matching (الدقيقة - O(n))

**المبدأ:**
إذا فشل البحث بالعلامة التجارية، ابحث شاملاً في كل الأسماء.

**الـ 3 Scorers:**

#### 1️⃣ token_set_ratio
يقسم النص لكلمات ويقارن المجموعات

```python
# لا يهم الترتيب!
token_set_ratio("PANADOL 30 TAB 500 MG", "PANADOL 500 MG 30 TAB")
# → 100%

# كلمات مشتركة: {PANADOL, 30, TAB, 500, MG}
# الفرق: ترتيب فقط
```

#### 2️⃣ token_sort_ratio
يرتب الكلمات قبل المقارنة

```python
# الترتيب يعتبر!
s1 = "PANADOL 30 500 MG TAB"
s2 = "PANADOL 500 MG 30 TAB"

# بعد الترتيب:
sorted_s1 = "30 500 PANADOL MG TAB"
sorted_s2 = "30 500 PANADOL MG TAB"  → 100% تطابق
```

#### 3️⃣ partial_token_sort_ratio
يبحث عن أطول قطعة متطابقة

```python
# كلمات إضافية → تجاهل!
partial_token_sort_ratio(
    "PANADOL PLUS 500 MG 30 TAB",
    "PANADOL 500 MG 30 TAB"
)
# يجد: "PANADOL 500 MG 30 TAB" → 100%
# يتجاهل: "PLUS"
```

**الخوارزمية الكاملة:**

```
FOR each scorer in [token_set_ratio, token_sort_ratio, partial_token_sort_ratio]:
   1. استخدم scorer للمقارنة مع كل المنتجات
   2. احصل على أفضل نتيجة
   3. تحقق من components_match()
   4. إذا صحيح: احفظ النتيجة
   5. اختر أفضل النتائج الثلاث
END
```

**مثال عملي:**

```
Input: "ASPIRIN PLUS 325 MG 20 TABLET"

Step 1: البحث بـ token_set_ratio
├─ النتيجة الأولى: "ASPIRIN 325 MG 20 TAB" → 98%
│  └─ components_match ✅
│
├─ النتيجة الثانية: "ASPIRIN 500 MG 20 TAB" → 85%
│  └─ components_match ✗ (جرعة مختلفة)
│
└─ النتيجة الثالثة: "ASPIRIN COMPLEX 325 MG" → 80%
   └─ components_match ✗ (كمية مختلفة)

Step 2: البحث بـ token_sort_ratio
├─ النتيجة: "ASPIRIN 325 MG 20 TAB" → 96%

Step 3: البحث بـ partial_token_sort_ratio
├─ النتيجة: "ASPIRIN 325 MG 20 TAB" → 99%

Step 4: اختيار الأفضل
├─ أفضل scorer: partial_token_sort_ratio
├─ أفضل نتيجة: 99%
└─ المنتج: "ASPIRIN 325 MG 20 TAB"

Output: {
  "record": {"en": "ASPIRIN 325 MG 20 TAB", ...},
  "score": 99,
  "method": "partial_token_sort_ratio"
}
```

---

## 2. التحقق بالـ AI

### الـ System Prompt الصارم

```
أنت متخصص في التحقق من تطابق أسماء الأدوية. 
القواعس التالية صارمة - لا استثناءات:

1. ❌ العلامة التجارية مختلفة = عدم تطابق
   مثال: PANADOL ≠ PANADOL EXTRA

2. ❌ أرقام الجرعة مختلفة = عدم تطابق
   مثال: 500 MG ≠ 400 MG

3. ❌ الكمية مختلفة = عدم تطابق
   مثال: 20 TAB ≠ 30 TAB
   (إذا واحد معروف والآخر غير معروف → اقبل فقط إذا كانت الأسماء متطابقة جداً)

4. ❌ الحجم مختلف = عدم تطابق
   مثال: 120 ML ≠ 100 ML

5. ❌ الشكل مختلف = عدم تطابق
   مثال: CREAM ≠ GEL

6. ❌ PLUS/EXTRA/NIGHT/COLD في واحد دون الآخر = عدم تطابق
   مثال: PANADOL PLUS ≠ PANADOL

أرجع JSON: {"is_correct": bool, "reason": str, "confidence": 0.0-1.0}
```

### أمثلة التحقق

```
Example 1:
Drug A: PANADOL 500 MG 30 TABLET
Drug B: PANADOL 500 MG 30 TAB
Result: ✅ CORRECT (confidence: 0.99)

Example 2:
Drug A: PANADOL PLUS 500 MG 30 TAB
Drug B: PANADOL 500 MG 30 TAB
Result: ❌ INCORRECT (confidence: 0.95)
Reason: "PLUS" في الأول دون الثاني

Example 3:
Drug A: ASPIRIN 325 MG 20 TABLET
Drug B: ASPIRIN 325 MG 40 TABLET
Result: ❌ INCORRECT (confidence: 0.98)
Reason: الكمية مختلفة (20 vs 40)

Example 4:
Drug A: CREAM 1% 50G
Drug B: LOTION 1% 50G
Result: ❌ INCORRECT (confidence: 0.97)
Reason: الشكل مختلف (CREAM vs LOTION)
```

---

## 3. المرحلة 4: التنظيف الخوارزمي النهائي

### المنطق

```python
FOR each matched_result:
   1. أعد تحليل الدواء الأصلي
   2. أعد تحليل المنتج المطابق
   
   3. تحقق من:
      ✓ العلامة التجارية (أول 4 أحرف على الأقل)
      ✓ الجرعة (يجب أن تكون متطابقة تماماً)
      ✓ الكمية (إذا كان في الاثنين → يجب تطابق)
      ✓ الحجم (إذا كان في الاثنين → يجب تطابق)
      ✓ الوزن (إذا كان في الاثنين → يجب تطابق)
   
   4. إذا فشل أي تحقق:
      ❌ احذف التطابق
   
   5. وإلا:
      ✅ احفظ التطابق
```

### مثال

```
Matched Result:
├─ drug_input: "PANADOL EXTRA 500 MG 30 TABLET"
├─ product_matched: "PANADOL 500 MG 30 TAB"

Step 1: أعد التحليل
├─ drug: brand="PANADOL EXTRA", dosage=500, unit=MG, qty=30
├─ prod: brand="PANADOL", dosage=500, unit=MG, qty=30

Step 2: التحقق
├─ Brand Check: "PANAD" vs "PANAD" ✓ (أول 4 أحرف متطابقة)
├─ But: "EXTRA" في الدواء دون المنتج ✗

Step 3: الإجراء
└─ ❌ احذف هذا التطابق (خطأ!)

Result: REJECTED
```

---

## 4. حالات الاختبار الشاملة

### حالة 1: تطابق مثالي
```
Input:  PANADOL 500 MG 30 TABLET
Output: 100% match ✅
Method: brand_index
```

### حالة 2: ترتيب مختلف
```
Input:  30 TABLET PANADOL 500 MG
Output: 95% match ✅
Method: token_set_ratio
```

### حالة 3: كلمة إضافية
```
Input:  PANADOL PLUS 500 MG 30 TABLET
Output: AI rejects ✅
Reason: PLUS في الدواء دون المنتج
```

### حالة 4: جرعة مختلفة
```
Input:  ASPIRIN 250 MG (في المخزن 325 MG)
Output: No match ✅
Reason: جرعة مختلفة
```

### حالة 5: اسم غير موجود
```
Input:  UNKNOWN DRUG 123
Output: No match ✅
Method: fuzzy score < 80%
```

