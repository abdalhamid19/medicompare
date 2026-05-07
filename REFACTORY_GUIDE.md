# دليل إعادة الهيكلة — MediCompare2

هذا الدليل يهدف إلى رفع سرعة المطابقة، تقليل استهلاك الذاكرة، وتحسين قابلية التوسع بدون التضحية بدقة المطابقة الدوائية.

## ملخص فهم المشروع

المشروع يطابق ملف الأدوية الداخلي `all_non_cosmotics_drug_all.csv` مع كتالوج توريد `tawreed_products.csv` ثم ينتج `matched_drugs_verified.csv`.

المسار الحالي يتكون من:

1. `drug_matcher/normalizer.py`: تنظيف الاسم واستخراج المكونات مثل العلامة التجارية، الجرعة، الكمية، الحجم، الوزن، والشكل.
2. `drug_matcher/indexer.py`: بناء فهرس لمنتجات توريد وتنفيذ brand lookup و fuzzy matching.
3. `drug_matcher/pipeline.py`: تحميل البيانات، تشغيل المطابقة، تشغيل التحقق بالـ AI، تنظيف النتائج، وحفظها.
4. `drug_matcher/verifier.py`: عميل غير متزامن للتحقق بالذكاء الاصطناعي.
5. `drug_matcher/config.py`: مصدر الإعدادات الموحد.

الأحجام الحالية تقريباً:

- الأدوية: 6,295 صف.
- منتجات توريد: 14,802 صف.
- الناتج الحالي: 3,981 مطابق و 2,314 غير مطابق حسب الخطة المرفقة.

## أهداف الأداء

يجب أن تكون أي إعادة هيكلة قابلة للقياس. لا يتم قبول تعديل في المطابقة إلا بعد قياس:

- عدد المطابقات.
- عدد غير المطابقات.
- توزيع درجات المطابقة.
- عدد الرفض بسبب brand/dosage/qty/volume/weight/modifier.
- زمن تنفيذ `run_matching()`.
- Peak RAM عند معالجة كامل الملفات.
- عينة مراجعة بشرية تقيس false positives و false negatives.

الهدف العملي الأول:

- خفض زمن المطابقة الخوارزمية إلى أقل من 30 ثانية على البيانات الحالية.
- عدم زيادة الذاكرة أكثر من حجم البيانات الأساسية × 2 تقريباً.
- تقليل false positives قبل محاولة زيادة عدد المطابقات.

## المشاكل الحالية المؤثرة على السرعة والذاكرة

1. `pipeline.run_matching()` يستخدم `iterrows()` وهو أبطأ من `itertuples()`.
2. `DrugIndex` يخزن السجلات كـ dict لكل صف، وهذا مريح لكنه يستهلك ذاكرة أكثر من namedtuple/dataclass slots أو أعمدة منفصلة.
3. `components_match()` يتم استدعاؤها بكثرة داخل candidate filtering، لذلك أي منطق ثقيل داخلها يضرب الأداء مباشرة.
4. fuzzy search على كامل القائمة مكلف، خصوصاً عند تكراره لعدة scorers.
5. الوصول إلى خصائص خاصة مثل `_parsed_cache` و `_records` من `pipeline.py` يجعل التوسع أصعب.
6. لا توجد طبقة تقييم benchmark ثابتة تقارن الأداء والدقة قبل وبعد التعديل.

## خطة إعادة الهيكلة المقترحة

### المرحلة 1 — تثبيت السلوك والاختبارات

تمت إضافة اختبارات standard-library `unittest` تغطي:

- التطبيع واستخراج المكونات.
- مطابقة المكونات ورفض المطابقات الخطرة.
- `DrugIndex.best_match()` و `fuzzy_match()`.
- تشغيل pipeline مصغر بدون AI.
- سلوك AI verifier عند عدم وجود API key.

التشغيل:

- `python run_tests.py`
- أو `python -m unittest discover -s tests -p "test_*.py"`

يجب تشغيل هذه الاختبارات قبل وبعد أي تعديل.

### المرحلة 2 — تسريع الحلقة الرئيسية

استبدل `iterrows()` بـ `itertuples(index=False)` في `run_matching()` لأن `itertuples()` أسرع ويقلل إنشاء كائنات pandas.

القاعدة:

- لا تستخدم `iterrows()` داخل hot path.
- لا تنشئ dict كبير لكل صف داخل loop إلا عند كتابة النتيجة النهائية.

### المرحلة 3 — فصل candidate generation عن verification

أنشئ واجهة واضحة داخل `DrugIndex` بدلاً من وصول `pipeline` إلى الخصائص الخاصة:

- `get_candidates(parsed, limit)`
- `get_record(idx)`
- `get_parsed(idx)`
- `score_candidate(query_norm, idx, scorer)`

الفائدة:

- منع تكرار منطق candidate selection.
- تسهيل إضافة Arabic matching أو active ingredient matching.
- تقليل مخاطر كسر الأداء عند تعديل داخلي.

### المرحلة 4 — تحسين بنية التخزين داخل الفهرس

بدلاً من تخزين كامل `dict` لكل record في `_records`، يمكن تخزين أعمدة منفصلة:

- `product_name_en: list[str]`
- `product_name_ar: list[str]`
- `store_product_id: list[str]`
- `norms: list[str]`
- `parsed_cache: list[DrugComponents]` بدل dict.

الفائدة:

- تقليل ذاكرة الـ Python dict.
- تسريع الوصول بالـ index.
- جعل `parsed_cache[idx]` أسرع وأبسط.

### المرحلة 5 — Blocking قبل fuzzy search

لا يجب تشغيل fuzzy على كل 14,802 منتج إلا كـ fallback محدود. استخدم blocking كالتالي:

1. brand prefix block.
2. normalized first token block.
3. dosage block عند وجود جرعة.
4. quantity block عند وجود كمية.
5. form block عند وجود form قوي.

بعد ذلك طبق fuzzy فقط على candidate pool صغير.

الهدف:

- candidate pool أقل من 200 منتج في معظم الحالات.
- fallback full fuzzy فقط عند فشل كل blocks، وبحد أعلى للحالات.

### المرحلة 6 — Scoring موحد بدل thresholds متناثرة

أنشئ دالة scoring موحدة ترجع:

- `brand_score`
- `dosage_score`
- `qty_score`
- `form_score`
- `name_score`
- `final_score`
- `reject_reason`

قواعد مقترحة:

- اختلاف الجرعة إذا كانت موجودة في الطرفين = رفض مباشر.
- اختلاف الكمية إذا كانت موجودة في الطرفين = رفض مباشر.
- اختلاف modifiers مثل PLUS/EXTRA/NIGHT/FORTE = رفض مباشر.
- brand mismatch قوي = رفض مباشر.
- fuzzy threshold منخفض لا يستخدم إلا بعد مرور قواعد المكونات.

### المرحلة 7 — تقليل تكلفة AI

الـ AI يجب أن يكون verifier وليس matcher أساسي.

قواعد استخدامه:

1. لا ترسل أي حالة يرفضها `components_match()`.
2. لا ترسل حالات score >= 95 ومع مكونات متطابقة.
3. أرسل فقط منطقة الشك: score بين 70 و 94 أو حالات candidates متعددة متقاربة.
4. أضف cache لقرارات AI باستخدام hash من `(drug_name, candidate_name, model)`.
5. استخدم retries قليلة عند JSON invalid، ثم fallback لنموذج آخر.

### المرحلة 8 — تقليل الذاكرة عند قراءة CSV

استخدم `usecols` و `dtype=str` عند قراءة الملفات:

- منع pandas من تخمين أنواع لا نحتاجها.
- منع تحويل IDs إلى أرقام وفقدان leading zeros.
- تقليل الذاكرة.

قواعد:

- كل أسماء الأدوية و IDs تقرأ كنصوص.
- لا تحمل أعمدة غير مستخدمة.
- عند كبر الملفات جداً، استخدم chunking لملف drugs فقط مع فهرس tawreed ثابت في الذاكرة.

### المرحلة 9 — Benchmark دائم

أضف لاحقاً ملف benchmark مستقل يقيس:

- build index time.
- matching time.
- matches count.
- unmatched count.
- precision على gold sample.
- false positives by reason.

يجب حفظ النتائج في ملف مثل `benchmarks/YYYY-MM-DD.json` لمقارنة التغييرات.

## أولويات التنفيذ العملية

1. تثبيت الاختبارات والتشغيل المستمر.
2. `itertuples()` في pipeline.
3. typed/list-based storage داخل `DrugIndex`.
4. candidate blocking قبل fuzzy full scan.
5. scoring موحد و reject reasons واضحة.
6. AI cache + model fallback.
7. Arabic matching و active ingredient بعد وجود benchmark ذهبي.

## تحذيرات مهمة

- تخفيض `fuzzy_threshold` إلى 65 بدون blocking صارم سيزيد false positives.
- active ingredient matching قد يطابق generic بمنتج branded غير مكافئ تجارياً؛ لا تستخدمه إلا بعد جرعة/شكل/كمية قوية ومع قاموس موثوق.
- مطابقة عربية بدون normalization عربي ستضيف ضوضاء.
- الوصول لـ 100% غير ممكن إذا كان المنتج غير موجود في ملف توريد. الهدف الصحيح هو أعلى recall ممكن على الأصناف الموجودة مع precision عالية جداً.
