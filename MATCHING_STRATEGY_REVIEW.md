# مراجعة خطة الوصول لأعلى Matching — MediCompare2

هذه مراجعة للخطة الموجودة في `PLAN.md` مع ترتيب عملي أفضل للوصول إلى أعلى نسبة مطابقة صحيحة، وليس فقط أعلى رقم مطابقات.

## الخلاصة التنفيذية

الخطة الأصلية جيدة في الاتجاه العام، خصوصاً مراحل تنظيف `IMP`، تحسين parsing، والتحقق الخوارزمي قبل AI. لكن يجب تعديل نقطتين أساسيتين:

1. لا تستهدف 100% كمطابقات فعلية؛ لأن جزءاً من المنتجات غير موجود في كتالوج توريد. الهدف الواقعي هو أعلى recall على المنتجات الموجودة مع precision عالية جداً.
2. لا تخفض `fuzzy_threshold` إلى 65 كخطوة عامة قبل بناء blocking و scoring صارم؛ هذا قد يرفع false positives بسرعة.

أفضل ترتيب هو:

1. تنظيف وتطبيع أقوى.
2. Component extraction أدق.
3. Reject rules صارمة قبل أي AI.
4. Candidate blocking لتقليل البحث.
5. Threshold adaptive وليس ثابتاً.
6. AI فقط للحالات الرمادية مع نموذج أقوى أو fallback.
7. Active ingredient و Arabic matching بعد وجود benchmark ذهبي.
8. Manual review لإغلاق الباقي وتغذية قواعد الاستثناءات.

## تقييم مراحل الخطة الأصلية

### المرحلة 1 — تنظيف IMP

ممتازة وذات خطر منخفض. تم تطبيق تحسين في `normalize()` لإزالة بادئات مثل `+***IMP` وفصلها بشكل صحيح.

الأثر المتوقع منطقي: +30 إلى +50 مطابق جديد.

### المرحلة 2 — فصل الأرقام عن الحروف

ممتازة وذات أثر عالي. تم تطبيق فصل مثل:

- `PANADOL20MG` إلى `PANADOL 20 MG`
- `30TAB` إلى `30 TAB`
- `21-CAP` إلى `21 CAP`

كما تم إصلاح parsing للجرعات المئوية مثل `0.8%`.

### المرحلة 3 — تخفيض threshold

الفكرة صحيحة لكن التنفيذ المقترح خطر إذا كان عاماً.

البديل الأفضل:

- لا تجعل `fuzzy_threshold=65` عالمياً في كل الاستراتيجيات.
- استخدم threshold منخفض فقط إذا كانت المكونات القوية متطابقة:
  - brand مقبول.
  - dosage متطابق أو غير موجود في أحد الطرفين.
  - qty متطابقة أو غير موجودة في أحد الطرفين.
  - modifiers متطابقة.
- استخدم reject reasons قبل score.

قاعدة مقترحة:

- score >= 95 + components ok = قبول مباشر.
- score 80 إلى 94 + components ok = قبول أو AI verification حسب الخطورة.
- score 65 إلى 79 + components ok + candidate pool صغير = قبول مشروط أو AI.
- score < 65 = لا تقبل إلا باستثناء معروف أو مراجعة يدوية.

### المرحلة 4 — Active ingredient matching

مفيدة لكن يجب تأخيرها حتى لا تزيد false positives.

الشروط قبل تفعيلها:

1. قاموس active ingredients موثوق.
2. منع مطابقة generic مع brand مختلف إذا كان الشكل أو الجرعة أو الكمية غير مؤكدة.
3. إضافة tests لحالات إيجابية وسلبية.
4. إضافة وسم method منفصل مثل `active_ingredient_verified`.

لا تستخدمها كبحث حر في النص فقط؛ الأفضل بناء فهرس active ingredient من catalog بعد normalizing.

### المرحلة 5 — تحسين AI Verifier

صحيح أن النموذج الحالي إذا كان يؤكد كل شيء فهو غير مناسب لهذه المهمة. لكن التغيير وحده لا يكفي؛ يجب تقوية البروتوكول:

1. pre-check خوارزمي قبل AI.
2. prompt يحتوي أمثلة سلبية قوية.
3. JSON schema صارم.
4. retry عند JSON invalid.
5. model fallback عند سلوك غير موثوق.
6. cache للقرارات.

تم تعديل الإعدادات بحيث لا توجد مفاتيح API hardcoded، ويمكن تغيير النموذج عبر `AGENT_ROUTER_MODEL`.

نماذج مقترحة بالترتيب:

1. `glm-5.1` كافتراضي مطلوب حالياً للمشروع.
2. `anthropic/claude-3.5-sonnet` للحالات الصعبة إذا كانت التكلفة مقبولة.
3. `google/gemini-2.0-flash-001` كبديل سريع واقتصادي.
4. `google/gemini-2.5-flash-preview` إذا كان متاحاً ومستقراً في مزودك.
5. نموذج ثانٍ fallback عند تكرار تأكيد خاطئ أو JSON غير صالح.

قاعدة تغيير النموذج:

- أنشئ عينة ذهبية من 200 حالة تشمل positives و negatives.
- شغل كل نموذج عليها.
- اختر النموذج حسب أعلى precision أولاً، ثم recall، ثم التكلفة.
- إذا كان النموذج يؤكد أكثر من 95% من الحالات المختلطة، اعتبره غير صالح كـ verifier.

### المرحلة 6 — Arabic matching

مفيدة إذا كانت الأسماء العربية في الطرفين نظيفة. لكنها تحتاج Arabic normalization:

- إزالة التشكيل.
- توحيد أ/إ/آ إلى ا.
- توحيد ة/ه عند الحاجة بحذر.
- توحيد ي/ى.
- إزالة كلمات عامة مثل أقراص، كبسولات، شراب بعد استخراج الشكل.

لا تبدأ بها قبل تحسين الإنجليزي لأن الإنجليزي يحتوي الجرعة والكمية غالباً بشكل أوضح.

### المرحلة 7 — Manual review والتعلم

ضرورية للوصول لأعلى نتيجة واقعية. يجب ألا تكون آخر خطوة فقط؛ بل تبدأ مبكراً بعينة صغيرة لتقييم precision.

المخرجات المطلوبة من المراجعة:

- `APPROVED_MATCH`
- `REJECTED_MATCH`
- `NOT_AVAILABLE`
- `INVALID_DATA`
- `NEEDS_CATALOG_UPDATE`

هذه التصنيفات ستوضح هل المشكلة في الخوارزمية أم في نقص الكتالوج.

## الخطة المحسنة المقترحة

### Sprint 1 — الثبات والأمان

- تثبيت الاختبارات الحالية وتشغيل `python run_tests.py`.
- تدوير أي API key كان موجوداً في الكود سابقاً.
- استخدام environment variables فقط للـ AI.
- توحيد إحصاءات matched/unmatched مع NaN والفراغ.

### Sprint 2 — parsing و reject rules

- توسيع `FORM_WORDS` و `FORM_PREFIXES` بناءً على غير المطابقين.
- إضافة critical modifiers تدريجياً.
- توحيد dosage units مثل `I U` و `IU`.
- إضافة reject reason في output لاحقاً.

### Sprint 3 — performance/indexing

- تحويل `run_matching()` إلى `itertuples()`.
- جعل `_parsed_cache` list بدلاً من dict.
- إضافة candidate blocking by dosage/qty/form.
- تقليل full fuzzy search.

### Sprint 4 — adaptive matching

- اعتماد score tiers بدلاً من threshold واحد.
- قبول عالي الثقة مباشرة.
- إرسال zone الرمادية للـ AI فقط.
- تسجيل سبب القرار لكل match.

### Sprint 5 — AI verification مضبوط

- بناء gold sample.
- اختبار النماذج المقترحة.
- اعتماد النموذج الأفضل أو fallback متعدد.
- إضافة AI cache.

### Sprint 6 — توسيع recall

- active ingredient matching مع قاموس موثوق.
- Arabic matching بعد Arabic normalization.
- manual review UI أو CSV workflow.

## أعلى Matching متوقع

حسب الخطة الأصلية، هناك تقريباً 912 صنف علامتها غير موجودة في توريد و 9 بيانات ضوضاء، وبالتالي لا يمكن مطابقتها خوارزمياً بشكل صحيح. لذلك الحد النظري العملي ليس 100% من كامل ملف الأدوية، بل تقريباً 87% إلى 88% إذا تم تصنيف غير الموجودين بوضوح.

الأهم من الرقم النهائي:

- Precision للمطابقات المقبولة يجب أن تكون عالية جداً.
- غير الموجود يجب تصنيفه `NOT_AVAILABLE` وليس اعتباره فشل Matching.
- الناتج النهائي يجب أن يميز بين matched و not available و invalid و needs review.

## القرار بخصوص نموذج AI

إذا كان النموذج الحالي يؤكد النتائج الخاطئة، غيّره. لكن لا تجعل تغيير النموذج هو الحل الوحيد.

أفضل بروتوكول:

1. ابدأ بـ `glm-5.1` كافتراضي للمشروع.
2. اختبر `anthropic/claude-3.5-sonnet` على العينة الذهبية للحالات الصعبة.
3. استخدم `AGENT_ROUTER_MODEL` للتبديل بدون تعديل الكود.
4. لا تعتمد أي نموذج إلا إذا رفض الأمثلة السلبية بوضوح.
5. عند تضارب النماذج، لا تقبل match تلقائياً؛ أرسله إلى manual review.

## توصية نهائية

أفضل طريق لأعلى matching هو أن تعتبر العملية تصنيفاً متعدد المراحل:

1. exact/normalized match.
2. component-safe fuzzy match.
3. low-score strict match.
4. AI verified uncertain match.
5. active ingredient / Arabic fallback.
6. manual classification.

بهذا تصل لأعلى matching صحيح مع تقليل RAM والتكلفة وخطر المطابقات الخاطئة.
