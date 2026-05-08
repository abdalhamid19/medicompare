# 🏥 OPENROUTER Model Benchmark — Drug Name Comparison

**Date**: 2026-05-08 23:01
**Test cases**: 25 (should-match: 12, should-reject: 13)

## 📊 Summary Ranking

| # | Model | Accuracy | Should-Match | Should-Reject | Time (s) |
|---|---|---|---|---|---|
| 🥇 | `openai/gpt-oss-20b:free` | **80%** (20/25) | 92% | 69% | 123.5 |
| 🥈 | `openai/gpt-oss-120b:free` | **72%** (18/25) | 92% | 54% | 121.6 |
| 🥉 | `inclusionai/ring-2.6-1t:free` | **48%** (12/25) | 100% | 0% | 3.8 |
| 4. | `google/gemma-4-31b-it:free` | **48%** (12/25) | 100% | 0% | 3.9 |
| 5. | `nvidia/nemotron-nano-9b-v2:free` | **48%** (12/25) | 100% | 0% | 4.0 |
| 6. | `google/gemma-4-26b-a4b-it:free` | **48%** (12/25) | 100% | 0% | 4.1 |
| 7. | `nvidia/nemotron-3-nano-30b-a3b:free` | **48%** (12/25) | 100% | 0% | 4.3 |
| 8. | `liquid/lfm-2.5-1.2b-instruct:free` | **48%** (12/25) | 100% | 0% | 4.3 |
| 9. | `nvidia/nemotron-3-super-120b-a12b:free` | **48%** (12/25) | 100% | 0% | 4.4 |
| 10. | `poolside/laguna-m.1:free` | **48%** (12/25) | 100% | 0% | 4.5 |
| 11. | `baidu/cobuddy:free` | **48%** (12/25) | 100% | 0% | 4.6 |
| 12. | `qwen/qwen3-next-80b-a3b-instruct:free` | **48%** (12/25) | 100% | 0% | 4.8 |
| 13. | `z-ai/glm-4.5-air:free` | **48%** (12/25) | 100% | 0% | 4.8 |
| 14. | `poolside/laguna-xs.2:free` | **48%** (12/25) | 100% | 0% | 4.8 |
| 15. | `qwen/qwen3-coder:free` | **48%** (12/25) | 100% | 0% | 4.9 |
| 16. | `meta-llama/llama-3.2-3b-instruct:free` | **48%** (12/25) | 100% | 0% | 5.0 |
| 17. | `nousresearch/hermes-3-llama-3.1-405b:free` | **48%** (12/25) | 100% | 0% | 5.1 |
| 18. | `meta-llama/llama-3.3-70b-instruct:free` | **48%** (12/25) | 100% | 0% | 6.3 |
| 19. | `tencent/hy3-preview:free` | **48%** (12/25) | 100% | 0% | 7.0 |
| 20. | `openrouter/free` | **48%** (12/25) | 100% | 0% | 14.7 |
| 21. | `minimax/minimax-m2.5:free` | **48%** (12/25) | 100% | 0% | 22.4 |

## 🏆 Best Model: `openai/gpt-oss-20b:free`

- **Overall accuracy**: 80%
- **Should-match accuracy**: 92%
- **Should-reject accuracy**: 69%
- **Time**: 123.5s

## 📋 Detailed Results Per Model

### `openai/gpt-oss-20b:free` — 80%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage, quantity, and form are identical; only the wo |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | exception:TimeoutError |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage, quantity, and form are identical; only plural |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage, quantity, and form are identical (TAB/TABLETS |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage, quantity, and form are identical; only plural |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ❌ reject | ✗ | 1.0 | Brand names differ (ACETYLCISTEINE vs ACETYLCISTEIN). |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | exception:KeyError |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | exception:KeyError |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage, quantity, and form are identical; only a mino |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage, quantity, and form are identical (minor plura |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Brand names differ (GREEN TEA vs GREENTAL) and dosage/quanti |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | exception:TimeoutError |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Brand name and dosage differ (PANADOL vs PANADOL EXTRA, 20 T |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage differs (500 mg vs 250 mg) |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage differs (50 mg vs 75 mg) |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.5 | {"is_correct": false, " |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.5 | {"is_correct": |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.5 | {"is_correct": false, "{"reason":"Dos

 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Brand names differ: 'PANADOL NIGHT' vs 'PANADOL' (extra word |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ❌ reject | ✓ | 1.0 | Brand names differ (ACETYLCISTEINE vs ACETYLCISTEIN), which  |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | exception:TimeoutError |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Brand names differ (PANADOL vs PANADOL EXTRA) and quantity i |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 1.0 | Same brand, dosage, quantity, and form (capsules). |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Brand names differ (CIPRO vs CIPROBAY) |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Different quantity (10 vs 6) and different form (TAB vs CAP) |

### `openai/gpt-oss-120b:free` — 72%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage, quantity and form all match (PANADOL 20 table |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage, and quantity all match; only minor plural for |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | exception:TimeoutError |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage, quantity and form all match (minor plural var |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 1.0 | Brand name essentially identical, dosage 200 mg matches, qua |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage, quantity and form match (TAB/TABS considered  |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage, quantity, and form match (TAB vs TABLETS are  |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | exception:TimeoutError |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.5 | {"is_correct": true, "reason": "Brand, dosage,{quantity,  }  |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Brand names differ (GREEN TEA vs GREENTAL) and form/dosage n |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 1.0 | Brand identical, quantity both 30 pieces, form both chewable |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Brand names differ (PANADOL vs PANADOL EXTRA) and quantity d |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.5 | {
  "is_correct": false,
  "

 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:TimeoutError |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage differs (400 mg vs 600 mg) |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Brand matches but Drug A includes 'NIGHT' variant, which cha |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.5 | {"is_correct\": true, \"reason\": \"Dosage, quantity, and fo |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ❌ reject | ✗ | 0.9 | Drug A includes 'B12' indicating a specific formulation, whi |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Brand names differ (PANADOL vs PANADOL EXTRA) and quantity d |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 1.0 | Identical generic name, dosage, quantity and form (capsules) |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Brand names differ (CIPRO vs CIPROBAY); brand must be identi |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Different quantity (10 tablets vs 6 capsules) and different  |

### `inclusionai/ring-2.6-1t:free` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |

### `google/gemma-4-31b-it:free` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |

### `nvidia/nemotron-nano-9b-v2:free` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |

### `google/gemma-4-26b-a4b-it:free` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |

### `nvidia/nemotron-3-nano-30b-a3b:free` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |

### `liquid/lfm-2.5-1.2b-instruct:free` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |

### `nvidia/nemotron-3-super-120b-a12b:free` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |

### `poolside/laguna-m.1:free` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |

### `baidu/cobuddy:free` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |

### `qwen/qwen3-next-80b-a3b-instruct:free` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |

### `z-ai/glm-4.5-air:free` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |

### `poolside/laguna-xs.2:free` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |

### `qwen/qwen3-coder:free` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |

### `meta-llama/llama-3.2-3b-instruct:free` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |

### `nousresearch/hermes-3-llama-3.1-405b:free` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |

### `meta-llama/llama-3.3-70b-instruct:free` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |

### `tencent/hy3-preview:free` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_400 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_400 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_400 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_400 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_400 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_400 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_400 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_400 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_400 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_400 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_400 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_400 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_400 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_400 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_400 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_400 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_400 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_400 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_400 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_400 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_400 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_400 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_400 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_400 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_400 |

### `openrouter/free` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_429 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_429 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |

### `minimax/minimax-m2.5:free` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |

## 💡 Recommendations

- **Best free model**: `openai/gpt-oss-20b:free` (80%)
- **Best paid model**: `openrouter/free` (48%)
- **Overall best**: `openai/gpt-oss-20b:free` (80%)

### To use a specific model:

```bash
# Via --provider and --model flags:
python run_ai_verify.py --limit 50 --provider opencode --model big-pickle
python run_ai_verify.py --limit 50 --provider openrouter --model openai/gpt-4o-mini

# Free model:
python run_ai_verify.py --limit 50 --provider openrouter --model openai/gpt-oss-120b:free
```