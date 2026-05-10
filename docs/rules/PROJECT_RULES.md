# قواعد المشروع — MediCompare2

هذه القواعد ملزمة لأي تعديل لاحق لضمان أن المشروع منظم، سريع، آمن، وقابل للتوسع.

## 1. قواعد عامة

1. لا يتم تعديل منطق المطابقة بدون اختبار يغطي الحالة.
2. لا يتم قبول زيادة عدد المطابقات إذا زادت false positives في العينة الذهبية.
3. أي قرار matching يجب أن يكون قابلاً للتفسير بسبب واضح مثل `ok`, `different_brand`, `different_dosage`, `different_quantity`.
4. لا تستخدم AI كبديل عن قواعد دوائية واضحة؛ AI يستخدم للتحقق من الحالات الرمادية فقط.
5. أي API key يجب أن يأتي من environment variables أو `.env` غير مرفوع للمستودع.

## 2. هيكل الملفات المعتمد

الهيكل الحالي المقبول:

- `drug_matcher/config.py`: الإعدادات فقط.
- `drug_matcher/normalizer.py`: normalization و component parsing و component verification فقط.
- `drug_matcher/indexer.py`: بناء الفهارس واستخراج candidates والتسجيل fuzzy.
- `drug_matcher/pipeline.py`: orchestration فقط، بدون تفاصيل داخلية عن index storage.
- `drug_matcher/verifier.py`: AI verification فقط.
- `tests/`: اختبارات شاملة لا تعتمد على API خارجي.
- `run_tests.py`: تشغيل الاختبارات بدون pytest.

أي إضافة كبيرة يجب أن توضع في ملف مستقل:

- `drug_matcher/scoring.py` عند بناء scoring موحد.
- `drug_matcher/arabic.py` عند إضافة Arabic normalization/matching.
- `drug_matcher/active_ingredients.py` عند إضافة قاموس المواد الفعالة.
- `drug_matcher/benchmark.py` عند إضافة قياسات أداء.

## 3. قواعد الكود

1. استخدم type hints في كل الدوال العامة.
2. استخدم `dataclass(slots=True)` أو tuples في الكائنات المتكررة بكثرة.
3. تجنب `dict` داخل hot path إذا كان يمكن استخدام list أو tuple.
4. تجنب `iterrows()` في الحلقات الكبيرة؛ استخدم `itertuples()`.
5. لا تصل إلى خصائص تبدأ بـ `_` من خارج الكلاس إلا داخل اختبار مخصص ومع سبب واضح.
6. أي regex جديد يجب أن يكون له test باسم حالة واقعية.
7. لا تضف dependency جديدة إلا إذا كانت تقلل تعقيداً أو تحسن أداءً بوضوح.
8. لا تطبع أسرار أو API response كامل قد يحتوي بيانات حساسة.

## 4. قواعد البيانات

1. اقرأ CSV دائماً بـ `encoding="utf-8-sig"`.
2. IDs والأسماء تقرأ كنصوص `str`.
3. لا تعدل ملفات المصدر الأصلية أثناء التشغيل.
4. كل output يجب أن يحتوي الأعمدة الأساسية:
   - `code`
   - `drug_name`
   - `matched_product_name_en`
   - `matched_product_name_ar`
   - `matched_store_product_id`
   - `match_score`
   - `verified`
   - `match_method`
5. غير المطابق يجب أن يكون واضحاً: match fields فارغة أو NaN بطريقة موحدة، و `match_method` يوضح السبب.

## 5. قواعد المطابقة الدوائية

رفض مباشر عند:

1. اختلاف العلامة التجارية بشكل واضح.
2. اختلاف الجرعة إذا كانت موجودة في الطرفين.
3. اختلاف الكمية إذا كانت موجودة في الطرفين.
4. اختلاف الحجم إذا كان موجوداً في الطرفين.
5. اختلاف الوزن إذا كان موجوداً في الطرفين.
6. وجود modifier مهم في طرف دون الآخر مثل `PLUS`, `EXTRA`, `FORTE`, `NIGHT`, `COLD`, `SINUS`.

قبول محتمل عند:

1. اختلاف تنسيق فقط: مسافات، نقاط، شرطات.
2. `TAB` و `TABS` و `TABLETS` لنفس الكمية.
3. `F.C. TAB` مقابل `TAB` عند تطابق الجرعة والكمية والعلامة.
4. اختلاف manufacturer descriptor دون تغيير المنتج.

## 6. قواعد AI

1. استخدم مفاتيح المزود من البيئة فقط، ولا تضع أي API key داخل الكود.
2. استخدم `AI_MODEL` لتغيير النموذج بدون تعديل الكود.
3. النموذج الافتراضي يجب أن يكون قابلاً للتغيير من config.
4. إذا أعاد النموذج JSON غير صالح، نفذ retry محدود ثم fallback.
5. إذا كان النموذج يؤكد كل شيء، يعتبر غير موثوق ويجب تغييره أو تعطيله لهذه المرحلة.
6. لا ترسل إلى AI أي حالة ترفضها القواعد الخوارزمية.
7. احفظ قرارات AI في cache لاحقاً لتقليل التكلفة والتذبذب.

## 7. قواعد الاختبارات

يجب الحفاظ على هذه الطبقات:

1. Unit tests لـ `normalize()` و `parse_drug()`.
2. Unit tests لـ `components_match()` لحالات القبول والرفض.
3. Tests لـ `DrugIndex` باستخدام catalog صغير مصطنع.
4. Tests لـ `MatchPipeline` باستخدام CSV مؤقت.
5. Tests لـ `AIVerifier` بدون API key لضمان عدم وجود network dependency.

تشغيل الاختبارات:

- `python run_tests.py`

أي bug جديد يجب أن يبدأ باختبار فاشل ثم إصلاح.

## 8. قواعد الأداء

1. قبل أي refactor في `indexer.py` أو `normalizer.py`، سجل زمن baseline.
2. لا تجعل `components_match()` يقوم بعمل ثقيل غير ضروري.
3. نفذ blocking قبل full fuzzy search.
4. أي fallback full scan يجب أن يكون محدوداً ومقاساً.
5. حافظ على cache للمكونات parsed؛ لا تعيد parse للكتالوج داخل كل query.
6. استهدف candidate pools صغيرة قبل fuzzy.

## 9. قواعد الأمان

1. ممنوع hardcode لأي API key.
2. لا تحفظ `.env` في Git.
3. لا ترفع ملفات output تحتوي بيانات حساسة إذا كانت البيئة إنتاجية.
4. عند ظهور مفتاح API داخل الكود، يجب تدويره فوراً من مزود الخدمة ثم حذفه من المشروع.

## 10. تعريف النجاح

التعديل ناجح فقط إذا حقق:

1. الاختبارات كلها تمر.
2. لا يوجد انخفاض واضح في precision.
3. يوجد تحسن موثق في recall أو السرعة أو الذاكرة.
4. التغيير مفهوم ومعزول ويمكن الرجوع عنه.
