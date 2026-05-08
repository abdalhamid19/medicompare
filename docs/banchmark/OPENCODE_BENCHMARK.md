# 🏥 OPENCODE Model Benchmark — Drug Name Comparison

**Date**: 2026-05-08 23:03
**Test cases**: 25 (should-match: 12, should-reject: 13)

## 📊 Summary Ranking

| # | Model | Accuracy | Should-Match | Should-Reject | Time (s) |
|---|---|---|---|---|---|
| 🥇 | `big-pickle` | **92%** (23/25) | 83% | 100% | 40.6 |
| 🥈 | `qwen3.5-plus` | **48%** (12/25) | 100% | 0% | 4.7 |
| 🥉 | `minimax-m2.5` | **48%** (12/25) | 100% | 0% | 4.8 |
| 4. | `gpt-5.4-mini` | **48%** (12/25) | 100% | 0% | 4.9 |
| 5. | `claude-sonnet-4-5` | **48%** (12/25) | 100% | 0% | 5.8 |
| 6. | `gemini-3-flash` | **48%** (12/25) | 100% | 0% | 5.8 |
| 7. | `glm-5.1` | **48%** (12/25) | 100% | 0% | 5.8 |
| 8. | `gpt-5.1` | **48%** (12/25) | 100% | 0% | 5.9 |
| 9. | `kimi-k2.5` | **48%** (12/25) | 100% | 0% | 6.0 |

## 🏆 Best Model: `big-pickle`

- **Overall accuracy**: 92%
- **Should-match accuracy**: 83%
- **Should-reject accuracy**: 100%
- **Time**: 40.6s

## 📋 Detailed Results Per Model

### `big-pickle` — 92%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Brand and dosage match; TAB and TABLETS are same form. |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 1.0 | Same brand, strength, quantity, and form (capsules). |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 1.0 | Same brand, dosage, quantity, and form; 'TAB' vs 'TABS' is a |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Same brand, dosage, quantity, and form; 'TAB' and 'TABLETS'  |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 1.0 | Same brand, dosage, and quantity; 'TAB' and 'TABS' are minor |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ❌ reject | ✗ | 0.5 |  |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 1.0 | Same brand, dosage, quantity, and form (TAB vs TABS is just  |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Both have identical brand, dosage, quantity, and form (table |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 1.0 | Same brand, dosage, quantity, and form; 'TAB' vs 'TABS' is a |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 1.0 | Same brand, dosage, quantity, and form. Only pluralization d |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ❌ reject | ✓ | 0.9 | Different brand names: 'GREEN TEA' vs 'GREENTAL'. Also, DRUG |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ❌ reject | ✓ | 0.5 |  |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 0.5 |  |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage mismatch: 500 mg vs 250 mg. |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage differs: 50 mg vs 75 mg |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | different dosage (5 MG vs 2.5 MG) |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage mismatch (10mg vs 20mg) |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage differs: 400 mg vs 600 mg |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Brand names differ: 'PANADOL NIGHT' vs 'PANADOL' |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ❌ reject | ✓ | 0.5 |  |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ❌ reject | ✗ | 0.9 | Brand names differ: FEROGLOBIN B12 vs FEROGLOBIN, indicating |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Different product names (COLD AND FLU vs EXTRA) and quantity |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 1.0 | Same brand, dosage, quantity, and form (capsules). |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Different brand names: CIPRO vs CIPROBAY |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Different form (tablets vs capsules) and different quantity  |

### `qwen3.5-plus` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |

### `minimax-m2.5` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |

### `gpt-5.4-mini` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |

### `claude-sonnet-4-5` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |

### `gemini-3-flash` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |

### `glm-5.1` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |

### `gpt-5.1` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |

### `kimi-k2.5` — 48%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 0.0 | api_error_401 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ✅ match | ✗ | 0.0 | api_error_401 |

## 💡 Recommendations

- **Best paid model**: `big-pickle` (92%)
- **Overall best**: `big-pickle` (92%)

### To use a specific model:

```bash
# Via --provider and --model flags:
python run_ai_verify.py --limit 50 --provider opencode --model big-pickle
python run_ai_verify.py --limit 50 --provider openrouter --model openai/gpt-4o-mini

# Free model:
python run_ai_verify.py --limit 50 --provider openrouter --model openai/gpt-oss-120b:free
```