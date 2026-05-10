# 🏥 OpenRouter Model Benchmark — Drug Name Comparison

**Date**: 2026-05-08 19:21
**Test cases**: 25 (should-match: 12, should-reject: 13)

## 📊 Summary Ranking

| # | Model | Accuracy | Should-Match | Should-Reject | Time (s) |
|---|---|---|---|---|---|
| 🥇 | `amazon/nova-micro-v1` | **88%** (22/25) | 92% | 85% | 9.2 |
| 🥈 | `mistralai/mistral-nemo` | **84%** (21/25) | 100% | 69% | 15.3 |
| 🥉 | `openai/gpt-4o-mini` | **84%** (21/25) | 67% | 100% | 17.0 |
| 4. | `openai/gpt-oss-120b:free` | **76%** (19/25) | 92% | 62% | 61.7 |
| 5. | `z-ai/glm-5.1` | **72%** (18/25) | 100% | 46% | 93.1 |
| 6. | `deepseek/deepseek-chat-v3.1` | **68%** (17/25) | 92% | 46% | 64.4 |
| 7. | `z-ai/glm-4.5-air:free` | **48%** (12/25) | 100% | 0% | 4.4 |
| 8. | `qwen/qwen3-next-80b-a3b-instruct:free` | **48%** (12/25) | 100% | 0% | 4.8 |
| 9. | `meta-llama/llama-3.3-70b-instruct:free` | **48%** (12/25) | 100% | 0% | 4.9 |
| 10. | `nousresearch/hermes-3-llama-3.1-405b:free` | **48%** (12/25) | 100% | 0% | 5.0 |
| 11. | `google/gemma-4-31b-it:free` | **48%** (12/25) | 100% | 0% | 5.2 |
| 12. | `nvidia/nemotron-3-super-120b-a12b:free` | **48%** (12/25) | 100% | 0% | 7.1 |
| 13. | `minimax/minimax-m2.5:free` | **48%** (12/25) | 100% | 0% | 14.2 |

## 🏆 Best Model: `amazon/nova-micro-v1`

- **Overall accuracy**: 88%
- **Should-match accuracy**: 92%
- **Should-reject accuracy**: 85%
- **Time**: 9.2s

## 📋 Detailed Results Per Model

### `amazon/nova-micro-v1` — 88%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Both drugs have identical brand name, dosage, and quantity.  |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 1.0 | Both drugs have identical brand name, dosage, and quantity,  |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 1.0 | Both drugs have the same brand name, dosage, and quantity, d |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Both drugs have identical brand name, dosage, quantity, and  |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 1.0 | Both drugs have identical brand name, dosage, quantity, and  |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 1.0 | Despite minor spelling differences, the brand name, dosage,  |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 1.0 | Both drugs have identical brand name, dosage, quantity, and  |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Both drugs have identical brand name, dosage, and quantity,  |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 1.0 | Both drugs have identical brand name, dosage, quantity, and  |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 1.0 | Both drugs have identical brand name, dosage, quantity, and  |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ❌ reject | ✓ | 0.9 | Different brand names: 'GREEN TEA' ≠ 'GREENTAL' and differen |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ❌ reject | ✓ | 0.9 | Different form: 'PICS' ≠ 'SOFT CHEWS PIECES' |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 0.9 | BRAND NAME and DOSAGE do not match. 'PANADOL' ≠ 'PANADOL EXT |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ❌ reject | ✓ | 0.9 | The dosage numbers do not match (500 mg ≠ 250 mg). |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 0.9 | The dosage numbers do not match (50 mg ≠ 75 mg). |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ❌ reject | ✓ | 0.9 | The dosage numbers do not match (5 mg ≠ 2.5 mg). |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ❌ reject | ✓ | 0.9 | The dosage numbers do not match (10 mg ≠ 20 mg). |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 0.9 | DRUG A and DRUG B have different dosages (400 mg vs 600 mg). |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.9 | Both drugs have the same brand name, dosage, and quantity, a |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.9 | Both drugs have the same brand name, dosage, quantity, and f |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ❌ reject | ✗ | 0.9 | The BRAND NAME 'FEROGLOBIN B12' is different from 'FEROGLOBI |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 0.9 | BRAND NAME mismatch: 'PANADOL COLD AND FLU' ≠ 'PANADOL EXTRA |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 1.0 | Both drugs have identical brand name, dosage, and quantity,  |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ❌ reject | ✓ | 0.9 | Different brand names: 'CIPRO' ≠ 'CIPROBAY' |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ❌ reject | ✓ | 0.9 | The quantity of the product differs: 10 tabs vs 6 caps. |

### `mistralai/mistral-nemo` — 84%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Both have the same brand name, dosage, quantity, and form. |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 1.0 | Both have the same brand name (AMOXIL), dosage (500 MG), qua |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 1.0 | Both have the same brand name (Abilify), dosage (10mg), quan |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Both have the same brand name, dosage, quantity, and form (t |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 1.0 | Both have the same brand name (CONCOR), dosage (5 MG), quant |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 1.0 | Both have the same brand name, dosage, quantity, and form. |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 1.0 | Both have the same brand name, dosage, quantity, and form (t |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Both have the same brand name, dosage, quantity, and form (t |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 1.0 | Both have the same brand name (LIPITOR), dosage (10mg), quan |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 1.0 | Both have the same brand name (Augmentin), dosage (625mg), q |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Different brand names |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 1.0 | Both have the same brand name, dosage (30), form (PICS/PIECE |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Different quantity and 'EXTRA' in Drug B |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage numbers do not match (500mg ≠ 250mg) |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage numbers do not match (50mg ≠ 75mg) |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage numbers do not match (5mg ≠ 2.5mg) |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage numbers do not match (10mg ≠ 20mg) |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage numbers do not match (400mg ≠ 600mg) |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 1.0 | Both have the same brand name (PANADOL), dosage (20 TAB), an |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 1.0 | Both have the same active ingredient, dosage, quantity, and  |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 1.0 | Both have the same brand name 'FEROGLOBIN', dosage (30 CAPS) |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Brand name mismatch (PANADOL vs PANADOL EXTRA) |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 1.0 | Both have the same brand name (OMEPRAZOLE), dosage (20 MG),  |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 1.0 | Both have the same brand name (Cipro/Ciprobay), dosage (500m |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Different form (CAP vs TAB) |

### `openai/gpt-4o-mini` — 84%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Brand name, dosage, and quantity match; 'TAB' and 'TABLETS'  |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 1.0 | Brand name, dosage, quantity, and form match exactly. |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 1.0 | Brand name, dosage, quantity, and form match exactly. |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Brand name, dosage, quantity, and form match exactly. |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 1.0 | Brand name, dosage, quantity, and form match exactly despite |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ❌ reject | ✗ | 0.9 | Different quantity form (SACHETS vs SACHET) |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 1.0 | Brand name, dosage, quantity, and form match exactly. |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ❌ reject | ✗ | 0.9 | Different form: 'TAB' vs 'TABLETS' |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ❌ reject | ✗ | 0.9 | Different quantity wording (TAB vs TABS) |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 1.0 | Brand name, dosage, quantity, and form match exactly. |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Different brand names and dosage forms |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ❌ reject | ✓ | 1.0 | Different quantity and form (PICS vs SOFT CHEWS PIECES) |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | BRAND NAME and QUANTITY do not match |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Different dosage (500 mg ≠ 250 mg) |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Different dosage (50 mg ≠ 75 mg) |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Different dosage (5 mg ≠ 2.5 mg) |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Different dosage (10 mg ≠ 20 mg) |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Different dosage: 400 MG ≠ 600 MG |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Different brand names (PANADOL NIGHT vs PANADOL) |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ❌ reject | ✓ | 1.0 | Different form: 'SACHETS' vs 'EFF. INSTANT GRAN. SACHETS' |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ❌ reject | ✗ | 0.9 | BRAND NAME differs (B12 vs no B12), FORM differs (CAP vs CAP |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Different brand names and 'EXTRA' in one name but not the ot |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 1.0 | Brand names, dosage, quantity, and form match exactly despit |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Different brand names (CIPRO vs CIPROBAY) |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Different quantity (10 TAB vs 6 CAP) |

### `openai/gpt-oss-120b:free` — 76%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | exception:JSONDecodeError |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage, quantity and form match (CAP = CAPSULES). |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | exception:JSONDecodeError |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | exception:KeyError |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage, quantity and form match; minor plural differe |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage, quantity and form match (TAB vs TABLETS consi |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage, and quantity match; only minor plural formatt |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Brand names differ (GREEN TEA vs GREENTAL) and dosage/quanti |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | exception:KeyError |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Brand names differ (PANADOL vs PANADOL EXTRA) and quantity d |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage differs (500 mg vs 250 mg) despite same brand and qua |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage differs (10 mg vs 20 mg) despite same brand and quant |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage differs (400 mg vs 600 mg) |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Drug A includes 'NIGHT' indicating a different formulation,  |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 1.0 | Dosage, quantity, and form match; extra description does not |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Different product names: 'COLD AND FLU' vs 'EXTRA' indicate  |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ❌ reject | ✗ | 0.0 |  |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:KeyError |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Quantity and form differ (10 tablets vs 6 capsules) |

### `z-ai/glm-5.1` — 72%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 1.0 | Same brand (AMOXIL), same dosage (500 MG), same quantity (10 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 1.0 | Brand (ABILIFY), dosage (10 MG), and quantity (10) all match |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | exception:JSONDecodeError |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Different brand names: 'GREEN TEA' is not the same as 'GREEN |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage mismatch: 50mg ≠ 75mg |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage mismatch: 5 MG vs 2.5 MG |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage mismatch: 400 MG vs 600 MG |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | PANADOL NIGHT is a different product from PANADOL - 'NIGHT'  |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Different products: PANADOL COLD AND FLU ≠ PANADOL EXTRA - t |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |

### `deepseek/deepseek-chat-v3.1` — 68%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Brand name (PANADOL), dosage (20), and form (TAB/TABLETS) ar |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | exception:JSONDecodeError |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | exception:JSONDecodeError |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | exception:JSONDecodeError |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 1.0 | Identical brand, dosage, quantity and form (TAB vs TABS is m |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | exception:JSONDecodeError |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | exception:JSONDecodeError |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 1.0 | Brand name, dosage (10 MG), quantity (30), and form (TAB/TAB |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 1.0 | TAB and TABS are minor formatting differences referring to t |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ❌ reject | ✓ | 0.0 | Brand names are different ('GREEN TEA' vs 'GREENTAL'), dosag |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ❌ reject | ✓ | 0.9 | Different quantity/form: '30 PICS' vs '30 SOFT CHEWS PIECES' |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Brand name mismatch: 'PANADOL' vs 'PANADOL EXTRA' - 'EXTRA'  |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage mismatch: 500 MG vs 250 MG |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage mismatch: 50 MG vs 75 MG |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:JSONDecodeError |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage mismatch: 400 MG vs 600 MG |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:JSONDecodeError |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.9 | Brand name (ACETYLCISTEINE/ACETYLCISTEIN) is a minor spellin |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ❌ reject | ✗ | 0.9 | Brand name mismatch: 'FEROGLOBIN B12' vs 'FEROGLOBIN'. 'B12' |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:JSONDecodeError |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | exception:JSONDecodeError |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:JSONDecodeError |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | exception:JSONDecodeError |

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

- **Best free model**: `amazon/nova-micro-v1` (88%)
- **Best paid model**: `amazon/nova-micro-v1` (88%)
- **Overall best**: `amazon/nova-micro-v1` (88%)

### To use a specific model:

```bash
# Set in .env file:
echo 'AI_MODEL=openai/gpt-4o-mini' >> .env

# Or via environment variable:
AI_MODEL=deepseek/deepseek-chat-v3.1 python run_ai_verify.py --limit 50
```
