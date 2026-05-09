# OpenCode Free Models — Rate Limits & Usage Report

> **تاريخ التقرير**: مايو 2026  
> **المصدر**: [opencode.ai/docs/zen](https://opencode.ai/docs/zen/) + [opencode.ai/zen/v1/models](https://opencode.ai/zen/v1/models)

---

## النماذج المجانية المتاحة حالياً

جميع النماذج التالية متاحة بسعر **$0 لكل 1M توكن** على منصة OpenCode Zen لفترة محدودة:

| # | اسم النموذج | الحالة | ملاحظات |
|---|---|---|---|
| 1 | **MiniMax M2.5 Free** (`minimax-m2.5-free`) | ✅ متاح | فترة تجريبية — البيانات قد تُستخدم لتحسين النموذج |
| 2 | **Big Pickle** (`big-pickle`) | ✅ متاح | نموذج "stealth" — فترة تجريبية |
| 3 | **Nemotron 3 Super Free** (`nemotron-3-super-free`) | ✅ متاح | فترة تجريبية |
| 4 | **Hy3 Preview Free** (`hy3-preview-free`) | ✅ متاح | فترة تجريبية |
| 5 | **Trinity Large Preview Free** (`trinity-large-preview-free`) | ✅ متاح | فترة تجريبية (جديد) |

> ⚠️ **ملاحظة**: نموذج `ling-2.6-flash-free` لم يعد يظهر في قائمة النماذج الحالية — يبدو أنه استُبدل بـ `trinity-large-preview-free`.

---

## حدود الاستخدام (Rate Limits)

OpenCode Zen **ليس لديه حدود ثابتة** للنماذج المجانية بالمعنى التقليدي. بدلاً من ذلك:

| المعيار | القيمة |
|---|---|
| **السعر** | $0 لكل 1M توكن (input + output + cached) |
| **Rate Limit التقريبي** | ~1 RPS (طلب واحد في الثانية) |
| **نوع الحد** | ديناميكي — يعتمد على الحمل الكلي على المنصة |
| **429 Too Many Requests** | يظهر عند الضغط على الخادم |

### سلوك Rate Limit الفعلي

- **لا يوجد حد يومي ثابت** — النماذج المجانية تعمل بـ pay-as-you-go بسعر $0
- **الحدود ديناميكية**: تعتمد على الاستخدام الكلي لجميع المستخدمين، وليس حسابك فقط
- **أوقات الذروة**: قد تحصل على 429 بشكل عشوائي عندما يكون الضغط عالياً
- **النماذج الأقل شعبية** (مثل Nemotron, Hy3) عادة أقل عرضة للـ 429

---

## مقارنة مع OpenCode Go (المدفوع)

| المعيار | Free (Zen) | Go ($5→$10/شهر) |
|---|---|---|
| **السعر** | $0 | $5 الشهر الأول، ثم $10 |
| **Rate Limit** | ~1 RPS ديناميكي | أعلى بكثير |
| **النماذج** | 5 نماذج مجانية | 12+ نموذج مدفوع |
| **حد 5 ساعات** | غير متاح | $12 استخدام |
| **حد أسبوعي** | غير متاح | $30 استخدام |
| **حد شهري** | غير متاح | $60 استخدام |
| **الاستقرار** | متقلب | أكثر استقراراً |

### تقدير عدد الطلبات لخطة Go (للمقارنة)

| النموذج | تقدير الطلبات / $60 شهرياً |
|---|---|
| Big Pickle + Free models | ~200 |
| GLM-5.1 | ~1,150 |
| Kimi K2.6 | ~1,290 |
| MiMo-V2.5-Pro | ~3,300 |
| Qwen3.6 Plus | ~3,400 |
| MiniMax M2.7 | ~3,450 |
| DeepSeek V4 Pro | ~10,200 |
| DeepSeek V4 Flash | ~أعلى بكثير |

---

## إعدادات MediCompare الحالية

### الترتيب الاحتياطي (Fallback Order)

عند فشل النموذج الأساسي، يتم تجربة التركيبات بالترتيب التالي:

```
المرحلة 1: النموذج الأساسي مع كل المفاتيح
  key1 (abdalhamid0006) + minimax-m2.5-free
  key2 (abdalhamid.mahrous) + minimax-m2.5-free

المرحلة 2: النماذج الاحتياطية مع كل المفاتيح
  key1 + nemotron-3-super-free
  key2 + nemotron-3-super-free
  key1 + hy3-preview-free
  key2 + hy3-preview-free
  key1 + trinity-large-preview-free
  key2 + trinity-large-preview-free
```

### تحسينات الأداء المطبقة

- **_failed_combos cache**: تركيبات (key, model) التي فشلت بـ 401/403 تُتخطى مباشرة في الطلبات التالية
- **API failure review**: عناصر فشل API تُرسل لنموذج المراجعة مع prompt مختلف (تحقق من الصفر)
- **Review threshold**: 0.8 — فقط القرارات بثقة < 0.8 تُرسل للمراجعة

---

## توصيات

1. **أضف `trinity-large-preview-free`** لقائمة FALLBACK_MODELS في `.env` (نموذج مجاني جديد)
2. **غيّر النموذج الأساسي** من `minimax-m2.5-free` إلى نموذج أكثر استقراراً إذا استمرت أخطاء 401
3. **فكر في اشتراك Go** ($10/شهر) للحصول على حدود أعلى واستقرار أفضل
4. **وزّع الطلبات** عبر النماذج المجانية المتعددة لتقليل الضغط على نموذج واحد

---

## روابط مفيدة

- [OpenCode Zen Docs](https://opencode.ai/docs/zen/)
- [OpenCode Go Docs](https://opencode.ai/docs/go/)
- [قائمة النماذج الحالية (API)](https://opencode.ai/zen/v1/models)
- [OpenCode Console](https://opencode.ai/auth)
