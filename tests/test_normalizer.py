from __future__ import annotations

import unittest

from drug_matcher.normalizer import (
    components_match, normalize, normalize_arabic, parse_drug,
)


class NormalizerTests(unittest.TestCase):
    def test_normalize_handles_noise_compact_tokens_and_decimals(self) -> None:
        cases = [
            ("+***IMP PANADOL20MG 30TAB", "PANADOL 20 MG 30 TAB"),
            ("+***imp PANADOL NIGHT 20 TAB", "PANADOL NIGHT 20 TAB"),
            ("INDERAL 10MG 50TAB", "INDERAL 10 MG 50 TAB"),
            ("OMEPRAZOLE 21-CAP", "OMEPRAZOLE 21 CAP"),
            ("GYNOCONAZOLE 0.8% CREAM", "GYNOCONAZOLE 0.8% CREAM"),
            ("VITAMIN D 1.000IU", "VITAMIN D 1000 IU"),
            ("FEROGLOBIN B12 30 CAP", "FEROGLOBIN B12 30 CAP"),
            ("CALCIUM D3 30 TAB", "CALCIUM D3 30 TAB"),
            ("PANADOL EXTRA 24 TAB IMP", "PANADOL EXTRA 24 TAB IMP"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(normalize(raw), expected)

    def test_normalize_arabic_unifies_common_letters(self) -> None:
        cases = [
            ("إيزوميبرازول ٤٠ مجم", "ايزوميبرازول ٤٠ مجم"),
            ("كبسولة", "كبسوله"),
            ("على", "علي"),
            ("أقراص", "اقراص"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(normalize_arabic(raw), expected)

    def test_parse_drug_extracts_core_components(self) -> None:
        comp = parse_drug("+***IMP AUGMENTIN625MG 10TABS")

        self.assertEqual(comp.brand, "AUGMENTIN")
        self.assertEqual(comp.dosage_nums, ("625",))
        self.assertEqual(comp.dosage_units, ("MG",))
        self.assertEqual(comp.qty, "10")
        self.assertTrue(comp.imported)
        self.assertEqual(comp.normalized, "AUGMENTIN 625 MG 10 TABS")

    def test_parse_drug_detects_compact_import_prefix(self) -> None:
        comp = parse_drug("+***IMPGlUCOSAMINE CHONDROTN MSM 120CAP")

        self.assertTrue(comp.imported)

    def test_parse_drug_separates_packaging_weight_from_dosage(self) -> None:
        comp = parse_drug("PRODUCT 500 MG 30 TAB 20 GM")

        self.assertEqual(comp.dosage_nums, ("500",))
        self.assertEqual(comp.dosage_units, ("MG",))
        self.assertEqual(comp.qty, "30")
        self.assertEqual(comp.weight, "20")

    def test_components_match_rejects_unsafe_matches(self) -> None:
        cases = [
            ("VIGOTON PLUS 20 TABS", "VIGOTON 30 TABS", "different_modifier"),
            ("GYNOCONAZOLE 0.8%", "GYNOCONAZOL 0.4%", "different_dosage"),
            ("CLOZAPINE 100 MG 30 TABS", "CLOZAPEX 100 MG 50 TAB", "different_brand"),
            ("TOTAL COD LIVER OIL 120 ML SYP", "TOTAL SYRUP 120 ML", "different_brand"),
            ("FEROGLOBIN B12 30 CAP", "FEROGLOBIN 30 CAPS", "different_modifier"),
            ("CALCIUM D3 30 TAB", "CALCIUM 30 TAB", "different_modifier"),
            ("PANADOL EXTRA 24 TAB IMP", "PANADOL EXTRA 24 F.C. TAB", "different_import_status"),
        ]
        for left, right, reason in cases:
            with self.subTest(left=left, right=right):
                is_ok, actual_reason = components_match(parse_drug(left), parse_drug(right))
                self.assertFalse(is_ok)
                self.assertEqual(actual_reason, reason)

    def test_components_match_accepts_equivalent_formatting(self) -> None:
        cases = [
            ("AUGMENTIN 625MG 10 TABS", "AUGMENTIN 625 MG 10 F.C. TAB."),
            ("INDERAL 10 MG 50TAB", "INDERAL 10 MG 50 TABS"),
            ("PANADOL NIGHT 20 TAB", "PANADOL NIGHT 20 TABLETS"),
            ("PANADOL EXTRA 24 TAB IMP", "PANADOL EXTRA 24 F.C. TAB IMP"),
        ]
        for left, right in cases:
            with self.subTest(left=left, right=right):
                is_ok, reason = components_match(parse_drug(left), parse_drug(right))
                self.assertTrue(is_ok)
                self.assertEqual(reason, "ok")


if __name__ == "__main__":
    unittest.main()
