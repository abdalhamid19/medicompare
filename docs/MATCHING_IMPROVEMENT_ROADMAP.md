# خطة متعددة المراحل لتقوية خوارزمية المطابقة

## النطاق والقواعد

هذه الخطة مبنية على مراجعة الملفات التالية:

- `drug_matcher/normalizer.py`
- `drug_matcher/indexer.py`
- `drug_matcher/pipeline.py`
- `drug_matcher/ai_steps.py`
- `drug_matcher/config.py`
- `docs/coding_best_practices.md`
- `docs/MATCHING_STRATEGY_REVIEW.md`

تم إنشاء `prompt_for_ai.md` وربطه بطبقة التحقق بالذكاء الاصطناعي، مع اختبارات
تثبت وجود قواعد الرفض الأساسية.

الهدف ليس زيادة عدد المطابقات فقط، بل رفع الدقة وتقليل الأخطاء. أي منتج غير
موجود فعلاً في كتالوج توريد يجب أن يصنف بوضوح، ولا يضغط النظام نفسه لقبول
مطابقة ضعيفة.

## تحليل الأخطاء المرسلة

الأمثلة تكشف أن الخوارزمية الحالية تفشل في حالات متكررة:

- اختلاف كلمات الشكل التجاري: `LIQUID SPRAY` مقابل `SPRAY`.
- أخطاء إملائية بسيطة: `esomeprprazole` مقابل `ESOMEPRAZOLE`.
- كلمات وصفية زائدة أو ناقصة: `INFINITY AKREN FACIAL CLEANSER` مقابل
  `AKREN CLEANSER FACIAL WASH`.
- اختلافات تنسيق الجرعة: `16 / 12.5` مقابل `16\12.5`.
- النكهات كخصائص حاسمة: `BANANA`, `ORANGE`, `PINEAPPLE`, `STRAWBERRY`.
- أسماء مختصرة شائعة: `ALGESAL CREAM 40 GM` مقابل
  `ALGESAL SURACTIVE 40 GM CREAM`.
- ترتيب الكلمات واختلافات المفردات: `ALKALINE WASH POWDER 12 SACHETS`.

هذه الأخطاء تحتاج تحسينات في التطبيع، استخراج المكونات، توليد المرشحين، scoring،
والتحقق النهائي.

## المرحلة 0: تثبيت خط أساس قابل للقياس

1. إنشاء ملف golden set صغير من الحالات المرسلة وحالات مشابهة.
2. تصنيف كل حالة إلى:
   - `MATCH`
   - `NO_MATCH`
   - `NOT_AVAILABLE`
   - `NEEDS_REVIEW`
3. إضافة اختبارات regression تغطي الحالات الإيجابية والسلبية.
4. تشغيل:
   - `python run_tests.py`
   - عينة تشغيل من `run_matcher.py` بدون AI.
5. حفظ تقرير baseline يحتوي:
   - precision
   - recall
   - false positives
   - false negatives
   - أسباب الرفض الأكثر تكراراً

معيار النجاح: وجود baseline ثابت يمنع أي تحسين من كسر حالات كانت صحيحة.

## المرحلة 1: تقوية التطبيع Normalization

1. توحيد الفواصل بين الجرعات المركبة:
   - `16 / 12.5`
   - `16\12.5`
   - `16-12.5`
2. توحيد أسماء الوحدات والأحجام:
   - `GM`, `G`
   - `ML`
   - `CAPS`, `CAPSULES`
   - `TAB`, `TABS`, `TABLETS`
3. إضافة قاموس مرادفات للأشكال:
   - `FACIAL WASH` = `CLEANSER`
   - `LIQUID SPRAY` = `SPRAY`
   - `ALKALINE WASH POWDER` = `WASH POWDER`
4. فصل النكهات كخاصية مستقلة بدلاً من تركها داخل النص العام.
5. إضافة اختبارات مباشرة لـ `normalize()` و `parse_drug()`.

معيار النجاح: الحالات ذات اختلاف التنسيق لا تفشل بسبب شكل كتابة الرقم أو الوحدة.

## المرحلة 2: استخراج مكونات المنتج بدقة أعلى

1. توسيع `DrugComponents` تدريجياً ليشمل:
   - `flavor`
   - `route_or_area`
   - `pack_count`
   - `variant_words`
2. اعتبار النكهة خاصية حاسمة عند وجودها في الطرفين.
3. اعتبار الحجم والوزن والكمية قواعد رفض صارمة عند وجودها في الطرفين.
4. فصل كلمات العلامة التجارية عن كلمات الفئة مثل:
   - `FACIAL`
   - `WASH`
   - `CLEANSER`
   - `SYRUP`
   - `CREAM`
5. إضافة tests للأمثلة:
   - `ALEXOLYTE 360ML BANANA FLAVOR`
   - `ALEXOLYTE (ORS) SYRUP 360 ML BANANA`
   - `ALBUSTIX 16\12.5 MG 30 TAB`

معيار النجاح: parser ينتج مكونات قابلة للمقارنة بدلاً من الاعتماد على fuzzy score
واحد.

## المرحلة 3: تحسين توليد المرشحين Candidate Generation

1. بناء فهارس إضافية بجانب brand index:
   - normalized exact key
   - brand + volume
   - brand + quantity
   - brand + dosage tuple
   - brand + flavor
2. استخدام fallback للبحث عندما تكون العلامة ناقصة في مصدر ما.
3. إدخال alias index للأسماء المختصرة:
   - `AKREN` داخل `INFINITY AKREN`
   - `ALGESAL` داخل `ALGESAL SURACTIVE`
4. تقليل الاعتماد على full fuzzy search إلا بعد فشل الفهارس الأسرع.
5. تسجيل مصدر كل مرشح في trace لتسهيل تحليل الأخطاء.

معيار النجاح: المرشح الصحيح يظهر ضمن top candidates قبل تدخل AI.

## المرحلة 4: Scoring متعدد العوامل

1. استبدال score الواحد بتركيبة درجات:
   - brand score
   - token score
   - dosage score
   - form score
   - pack score
   - flavor score
2. تطبيق penalties واضحة عند فقدان خصائص مهمة.
3. إضافة score tiers:
   - قبول مباشر عند score عال مع مكونات متطابقة.
   - AI أو review عند المنطقة الرمادية.
   - رفض مباشر عند اختلاف جرعة أو نكهة أو حجم مؤكد.
4. إخراج `reject_reason` و `decision_reason` في النتائج.
5. إبقاء thresholds داخل `MatchingConfig`.

معيار النجاح: لا يتم قبول match لأن fuzzy مرتفع بينما الجرعة أو النكهة مختلفة.

## المرحلة 5: قواعد رفض صارمة قبل AI

1. رفض اختلافات الجرعة المركبة.
2. رفض اختلاف النكهة عند وجودها في الطرفين.
3. رفض اختلاف الحجم أو الوزن أو عدد الأقراص.
4. رفض اختلاف modifiers المهمة مثل:
   - `D`
   - `PLUS`
   - `FORTE`
   - `EXTRA`
   - `SURACTIVE`
5. عدم إرسال الحالات المرفوضة بوضوح إلى AI إلا كمراجعة عينة.

معيار النجاح: تقليل false positives قبل أي تكلفة API.

## المرحلة 6: تحسين طبقة AI

1. إنشاء أو تحديد ملف `prompt_for_ai.md`.
2. جعل prompt يطلب JSON صارماً فقط.
3. إدخال أمثلة سلبية من الحالات الفعلية.
4. منع AI من قبول مطابقة عند اختلاف:
   - dosage
   - volume
   - flavor
   - pack quantity
5. استخدام candidate list محدودة مع أسباب خوارزمية لكل مرشح.
6. إضافة cache لقرارات AI حسب `query + candidate`.
7. تقييم أي نموذج على golden set قبل اعتماده.

معيار النجاح: AI لا يؤكد المطابقات الخاطئة، ويعمل كحكم للحالات الرمادية فقط.

## المرحلة 7: Arabic Matching بعد تثبيت الإنجليزي

1. إضافة Arabic normalization:
   - إزالة التشكيل.
   - توحيد `أ`, `إ`, `آ` إلى `ا`.
   - توحيد `ى` و`ي`.
   - التعامل الحذر مع `ة` و`ه`.
2. استخراج الجرعات والأحجام من العربي عند وجودها.
3. استخدام العربي كإشارة مساعدة، وليس كقرار منفرد في البداية.
4. إضافة اختبارات عربية من البيانات الحقيقية.

معيار النجاح: العربي يحسن recall بدون رفع false positives.

## المرحلة 8: Workflow للمراجعة اليدوية والتعلم

1. إخراج CSV للحالات الرمادية فقط.
2. إضافة أعمدة مراجعة:
   - `manual_decision`
   - `manual_reason`
   - `correct_store_product_id`
3. تحويل قرارات المراجعة إلى اختبارات regression.
4. تحديث alias dictionaries بناءً على المراجعة.
5. قياس التحسن بعد كل دفعة.

معيار النجاح: كل خطأ مكتشف يتحول إلى اختبار أو قاعدة، ولا يتكرر بصمت.

## المرحلة 9: القياس والتشغيل بعد كل خطوة

بعد كل مرحلة تنفيذية يجب تشغيل:

```bash
python run_tests.py
python run_matcher.py --no-ai --limit 200 --trace
```

وعند تعديل AI:

```bash
python run_ai_verify.py
```

بعد نجاح الاختبارات يجب حفظ التغيير في Git:

```bash
git status --short
git add <files-changed-by-this-step>
git commit -m "Describe matching improvement step"
git push origin main
```

يجب عدم إضافة ملفات بيانات ضخمة أو مخرجات عشوائية إلا إذا كانت مقصودة.

## ترتيب التنفيذ المقترح

1. baseline + tests للحالات المرسلة.
2. normalization للجرعات المركبة والمرادفات.
3. parser للنكهات والأشكال والكميات.
4. فهارس candidate generation إضافية.
5. scoring متعدد العوامل.
6. reject rules صارمة.
7. AI prompt وgolden benchmark.
8. Arabic matching.
9. manual review loop.

## مؤشرات النجاح النهائية

- انخفاض false positives إلى الحد الأدنى.
- ارتفاع recall للحالات الموجودة فعلاً في كتالوج توريد.
- كل `no_match` له سبب واضح.
- كل قرار AI قابل للتتبع.
- الاختبارات تغطي كل خطأ تم اكتشافه.
- تشغيل كامل pipeline لا يكسر حدود الأداء والذاكرة الموضحة في
  `docs/coding_best_practices.md`.

## حالة التنفيذ

تم تنفيذ الخطة الأساسية عبر مراحل قابلة للاختبار:

- المرحلة 0: أضيفت regression tests للحالات المكتشفة.
- المرحلة 1: تم تحسين التطبيع للجرعات المركبة، النكهات، الأشكال، ومرادفات
  النصوص التجارية.
- المرحلة 2: تم توسيع `DrugComponents` بخصائص مثل `flavor` و`imported`.
- المرحلة 3: تم إضافة `component_index` لفهارس تعتمد على العلامة مع الحجم،
  الكمية، الجرعة، والنكهة.
- المرحلة 4: تم إدخال scoring إضافي محدود للمكونات داخل `component_index`.
- المرحلة 5: تم تثبيت قواعد رفض للجرعة، الحجم، النكهة، الكمية، `B12/D3`،
  وفرق المستورد/المحلي.
- المرحلة 6: تم إنشاء `prompt_for_ai.md` وربطه بالكود. تقييم النماذج وAI cache
  مؤجلان حتى توفر API credentials وعينة ذهبية أكبر.
- المرحلة 7: تم إضافة `normalize_arabic()` كإشارة مساعدة آمنة مع اختبارات.
- المرحلة 8: تم إضافة CSV للمراجعة اليدوية يحتوي `manual_decision`,
  `manual_reason`, و`correct_store_product_id`.
- المرحلة 9: تم تشغيل `python run_tests.py` و
  `python run_matcher.py --no-ai --limit 200 --trace` بعد المراحل التنفيذية.
