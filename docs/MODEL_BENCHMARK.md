# 🏥 OPENCODE Model Benchmark — Drug Name Comparison

**Date**: 2026-05-09 10:57
**Test cases**: 25 (should-match: 14, should-reject: 11)

## 📊 Summary Ranking

| # | Model | Accuracy | Should-Match | Should-Reject | API Failed | Time (s) |
|---|---|---|---|---|---|---|
| 🥇 | `nemotron-3-super-free` | **88%** (22/25) | 79% | 100% | 0 | 167.5 |
| 🥈 | `minimax-m2.5-free` | **88%** (22/25) | 93% | 82% | 0 | 339.3 |
| 🥉 | `big-pickle` | **80%** (20/25) | 64% | 100% | 0 | 85.2 |
| 4. | `trinity-large-preview-free` | **0%** (0/0) | 0% | 0% | ⚠️ 25/25 | 22.9 |
| 5. | `hy3-preview-free` | **0%** (0/0) | 0% | 0% | ⚠️ 25/25 | 23.9 |

## 🏆 Best Model: `nemotron-3-super-free`

- **Overall accuracy**: 88%
- **Should-match accuracy**: 79%
- **Should-reject accuracy**: 100%
- **Time**: 167.5s

## 📋 Detailed Results Per Model

### `nemotron-3-super-free` — 88%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Brand identical, quantity 20 matches, form TAB/TABLETS consi |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 1.0 | Brand name, dosage, and quantity match; CAP vs CAPSULES is a |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 1.0 | Brand ABILIFY matches, dosage 10 MG matches, quantity 10 tab |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage, quantity, and form match; 'TAB' vs 'TABLETS'  |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage, and quantity match; 'TABS' vs 'TAB' is accept |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ❌ reject | ✗ | 0.9 | Brand name mismatch: ACETYLCISTEINE vs ACETYLCISTEIN (differ |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage (5/5 MG), and quantity (30) match exactly; 'TA |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Brand name, dosage, and quantity match exactly; form (tablet |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage, quantity, and form match; TABS vs TAB is acce |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | Brand, dosage, quantity match; 'TAB' vs 'TABS' is acceptable |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ✅ match | ✅ match | ✓ | 1.0 | Brand name identical (CALCIMA), dosage absent in both, quant |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ✅ match | ❌ reject | ✗ | 0.9 | Generic name mismatch: ACETYLCISTEINE vs ACETYLCISTEIN (diff |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ❌ reject | ✓ | 0.0 | Brand names differ |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 0.0 | Brand name differs (PANADOL vs PANADOL EXTRA) |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage mismatch: 500 mg vs 250 mg |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage mismatch: 50 MG vs 75 MG |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ❌ reject | ✓ | 0.0 | Dosage mismatch: 5 mg vs  |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage mismatch: 10 mg vs 20 mg |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 0.0 |  |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Brand name differs: 'PANADOL NIGHT' vs 'PANADOL' (extra 'NIG |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ❌ reject | ✗ | 0.0 | Brand name mismatch: |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Brand name differs: 'PANADOL COLD AND FLU' vs 'PANADOL EXTRA |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 1.0 | ... |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Brand names differ: CIPRO vs CIPROBAY |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ❌ reject | ✓ | 0.0 | Quantity differs (10 vs 6) |

### `minimax-m2.5-free` — 88%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | BRAND NAME (PANADOL) and QUANTITY (20) match exactly. 'TAB'  |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 0.0 | Brand (AMOXIL), dosage (500 MG), quantity (10), and form (ca |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 0.0 | Brand name (ABILIFY), dosage (10 MG), and quantity (10) all  |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 0.0 | BRAND (VOLTAREN), DOSAGE (50 MG), QUANTITY (20), and FORM ar |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | Both products are CONCOR 5 MG with quantity 30 tablets. The  |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 0.0 | Brand name 'COVERAM' matches, dosage ' |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Brand name (GLUCOPHAGE), dosage (500 MG), quantity (30), and |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 0.0 | Brand name LIPITOR matches, dosage 10 MG matches, quantity 3 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 0.0 | Brand (AUGMENTIN), dosage (625 MG), quantity (14), and form  |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ✅ match | ✅ match | ✓ | 0.0 | exception:TypeError |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Different brand names: 'PANADOL' vs 'PANADOL EXTRA' (the wor |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage mismatch: 500 MG vs 250 MG - these are different stre |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 0.0 | Dosage mismatch: VOLTAREN 50 MG vs VOLTAR |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage mismatch: CONCOR 5 MG vs CONCOR 2.5 MG. Different str |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage mismatch: DRUG A is 10 MG while DRUG B is 20 MG. Thes |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage mismatch: 400 MG vs 600 MG |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ✅ match | ✗ | 0.0 | exception:TypeError |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ❌ reject | ✗ | 0.0 | Brand name mismatch: 'FEROGLOBIN B12' vs 'FEROGLOBIN'. The ' |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 0.5 |  |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ✅ match | ✓ | 1.0 | Both products have identical drug name (OMEPRAZOLE), dosage  |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ❌ reject | ✓ | 0.0 | Different brand names: CIPRO |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Multiple mismatches: QUANTITY differs (10 tabs vs 6 caps) an |

### `big-pickle` — 80%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ❌ reject | ✗ | 0.5 |  |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ✅ match | ✓ | 1.0 | Same brand, dosage, quantity, and form with minor abbreviati |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ✅ match | ✓ | 1.0 | Both specify ABILIFY 10 MG with quantity 10, and 'TAB' vs 'T |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Both have identical brand name, dosage, quantity; 'TAB' is a |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ✅ match | ✓ | 1.0 | Brand name, dosage, quantity, and form match; 'TAB' and 'TAB |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ❌ reject | ✗ | 0.5 |  |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage, quantity, and form match; 'TAB' vs 'TABS' is  |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ✅ match | ✓ | 1.0 | Brand, dosage, and quantity match; TAB and TABLETS are equiv |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ✅ match | ✓ | 1.0 | Same brand, dosage, quantity, and form (tablets). 'TAB' vs ' |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ✅ match | ✓ | 1.0 | Same brand (AUGMENTIN), dosage (625 MG), quantity (14), and  |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ✅ match | ✅ match | ✓ | 1.0 | Both have brand CALCIMA and quantity 30; 'PICS' and 'SOFT CH |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ✅ match | ❌ reject | ✗ | 0.5 |  |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Brand names differ: 'GREEN TEA' vs 'GREENTAL', and DRUG A la |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Brand names differ (PANADOL vs PANADOL EXTRA) and quantity d |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage mismatch: 500 MG vs 250 MG. |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage strength differs: 50 mg vs 75 mg. |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage mismatch: 5 mg vs 2.5 mg |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage mismatch: 10 mg vs 20 mg. |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Dosage differs: 400 mg vs 600 mg |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ❌ reject | ✓ | 0.0 | PANADOL NIGHT is a |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ❌ reject | ✗ | 0.9 | Brand names differ: 'FEROGLOBIN B12' vs 'FEROGLOBIN', indica |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Different formulations: 'COLD AND FLU' vs 'EXTRA', and quant |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ❌ reject | ✗ | 0.5 |  |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ❌ reject | ✓ | 1.0 | Different brand names: CIPRO vs CIPROBAY |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ❌ reject | ✓ | 1.0 | Different form (tablets vs capsules) and different quantity  |

### `trinity-large-preview-free` — 0%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_400 |

### `hy3-preview-free` — 0%

| Drug | Candidate | Expected | Got | ✓ | Confidence | Reason |
|---|---|---|---|---|---|---|
| PANADOL 20 TAB | PANADOL 20 TABLETS | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| AMOXIL 500 MG 10 CAP | AMOXIL 500 MG 10 CAPSULES | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| ABILIFY 10 MG 10 TAB | ABILIFY 10 MG 10 TABS. | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 50 MG 20 TABLETS | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| CONCOR 5 MG 30 TAB | CONCOR 5 MG 30 TABS | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| ACETYLCISTEINE 200 MG 10 SACHETS | ACETYLCISTEIN 200 MG 10 SACHET | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| COVERAM 5/5 MG 30 TAB | COVERAM 5/5 MG 30 TABS | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| GLUCOPHAGE 500 MG 30 TAB | GLUCOPHAGE 500 MG 30 TABLETS | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| LIPITOR 10 MG 30 TAB | LIPITOR 10 MG 30 TABS. | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| AUGMENTIN 625 MG 14 TAB | AUGMENTIN 625 MG 14 TABS | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| CALCIMA 30 PICS | CALCIMA 30 SOFT CHEWS PIECES | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| ACETYLCISTEINE 600 MG 10 SACHETS | ACETYLCISTEIN 600 MG 10 EFF. INSTANT GRAN. SACHETS | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| GREEN TEA | GREENTAL 30 CAP | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| PANADOL 20 TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| AMOXIL 500 MG 10 CAP | AMOXIL 250 MG 10 CAP | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| VOLTAREN 50 MG 20 TAB | VOLTAREN 75 MG 20 TAB | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| CONCOR 5 MG 30 TAB | CONCOR 2.5 MG 30 TAB | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| LIPITOR 10 MG 30 TAB | LIPITOR 20 MG 30 TAB | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| IBUPROFEN 400 MG 20 TAB | IBUPROFEN 600 MG 20 TAB | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| PANADOL NIGHT 20 TAB | PANADOL 20 TAB | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| FEROGLOBIN B12 30 CAP | FEROGLOBIN 30 CAPS | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| PANADOL COLD AND FLU TAB | PANADOL EXTRA 24 TAB | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| OMEPRAZOLE 20 MG 14 CAP | OMEPRAZOLE 20 MG 14 CAPS | ✅ match | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| CIPRO 500 MG 10 TAB | CIPROBAY 500 MG 10 TAB | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |
| IMODIUM 2 MG 10 TAB | IMODIUM 2 MG 6 CAP | ❌ reject | ❌ reject | ✗ | 0.0 | ⚠️ api_error_401 |

## 💡 Recommendations

- **Best paid model**: `nemotron-3-super-free` (88%)
- **Overall best**: `nemotron-3-super-free` (88%)

### To use a specific model:

```bash
# Via --provider and --model flags:
python run_ai_verify.py --limit 50 --provider opencode --model big-pickle
python run_ai_verify.py --limit 50 --provider openrouter --model openai/gpt-4o-mini

# Free model:
python run_ai_verify.py --limit 50 --provider openrouter --model openai/gpt-oss-120b:free
```