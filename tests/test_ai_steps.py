"""Tests for AI verification and search steps."""
from __future__ import annotations

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd

from drug_matcher.ai_steps import (
    run_ai_verification,
    run_ai_search,
    _select_for_verification,
    _select_for_review,
    _build_verify_items,
    _get_unmatched,
    _search_candidates,
    _eligible_search_candidates,
    _search_acceptance_threshold,
    _dedupe_candidates,
    _apply_correction,
    _apply_search_result,
    _clear_match,
    _batch_review,
    _apply_review_results,
)
from drug_matcher.config import MatchingConfig, APIConfig
from drug_matcher.indexer import DrugIndex
from drug_matcher.normalizer import parse_drug
from drug_matcher.trace_log import MatchTraceLog


def _make_results(rows):
    """Build a results DataFrame from list of dicts."""
    cols = [
        "code", "drug_name", "matched_product_name_en",
        "matched_product_name_ar", "matched_store_product_id",
        "match_score", "verified", "match_method",
        "_drug_price", "_matched_price",
    ]
    return pd.DataFrame(rows, columns=cols)


def _make_index():
    """Build a small DrugIndex for testing."""
    tawreed = pd.DataFrame([
        {
            "product_name_ar": "اوجمنتين",
            "product_name_en": "AUGMENTIN 625 MG 10 TAB",
            "store_product_id": "T-1",
        },
        {
            "product_name_ar": "بانادول اكسترا",
            "product_name_en": "PANADOL EXTRA 24 TAB",
            "store_product_id": "T-2",
        },
        {
            "product_name_ar": "بانادول",
            "product_name_en": "PANADOL 20 TAB",
            "store_product_id": "T-3",
        },
        {
            "product_name_ar": "فيرجلوبين",
            "product_name_en": "FEROGLOBIN 30 CAPS",
            "store_product_id": "T-4",
        },
    ])
    return DrugIndex(tawreed, MatchingConfig())


class TestSelectForVerification(unittest.TestCase):
    def test_selects_only_matched_below_threshold(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "AUGMENTIN 625 MG 10 TAB",
                "matched_product_name_en": "AUGMENTIN 625 MG 10 TAB",
                "matched_product_name_ar": "اوجمنتين",
                "matched_store_product_id": "T-1",
                "match_score": 100.0, "verified": "algo_match",
                "match_method": "brand_index",
            },
            {
                "code": "D2", "drug_name": "FEROGLOBIN B12 30 CAP",
                "matched_product_name_en": "FEROGLOBIN 30 CAPS",
                "matched_product_name_ar": "فيرجلوبين",
                "matched_store_product_id": "T-4",
                "match_score": 85.0, "verified": "algo_match",
                "match_method": "brand_index",
            },
        ])
        cfg = MatchingConfig(ai_verify_threshold=90.0)
        selected = _select_for_verification(results, cfg)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected.iloc[0]["code"], "D2")

    def test_skips_unmatched(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "UNKNOWN",
                "matched_product_name_en": "",
                "matched_product_name_ar": "",
                "matched_store_product_id": "",
                "match_score": "", "verified": "",
                "match_method": "no_match",
            },
        ])
        cfg = MatchingConfig(ai_verify_threshold=90.0)
        selected = _select_for_verification(results, cfg)
        self.assertEqual(len(selected), 0)

    def test_skips_high_scores(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "AUGMENTIN",
                "matched_product_name_en": "AUGMENTIN 625 MG 10 TAB",
                "matched_product_name_ar": "اوجمنتين",
                "matched_store_product_id": "T-1",
                "match_score": 95.0, "verified": "algo_match",
                "match_method": "brand_index",
            },
        ])
        cfg = MatchingConfig(ai_verify_threshold=90.0)
        selected = _select_for_verification(results, cfg)
        self.assertEqual(len(selected), 0)

    def test_fuzzy_policy_selects_fuzzy_matches_above_threshold(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "PANADOL",
                "matched_product_name_en": "PANADOL 20 TAB",
                "matched_product_name_ar": "بانادول",
                "matched_store_product_id": "T-3",
                "match_score": 96.0, "verified": "algo_match",
                "match_method": "token_set_ratio",
            },
        ])
        cfg = MatchingConfig(ai_verify_threshold=90.0, ai_verify_policy="fuzzy")

        selected = _select_for_verification(results, cfg)

        self.assertEqual(len(selected), 1)

    def test_all_non_exact_policy_skips_only_exact_component_matches(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "PANADOL",
                "matched_product_name_en": "PANADOL 20 TAB",
                "matched_product_name_ar": "بانادول",
                "matched_store_product_id": "T-3",
                "match_score": 100.0, "verified": "algo_match",
                "match_method": "component_index",
            },
            {
                "code": "D2", "drug_name": "AUGMENTIN",
                "matched_product_name_en": "AUGMENTIN 625 MG 10 TAB",
                "matched_product_name_ar": "اوجمنتين",
                "matched_store_product_id": "T-1",
                "match_score": 100.0, "verified": "algo_match",
                "match_method": "brand_index",
            },
        ])
        cfg = MatchingConfig(ai_verify_policy="all-non-exact")

        selected = _select_for_verification(results, cfg)

        self.assertEqual(list(selected["code"]), ["D2"])

    def test_verify_limit_caps_selected_rows(self):
        results = _make_results([
            {
                "code": f"D{i}", "drug_name": "PANADOL",
                "matched_product_name_en": "PANADOL 20 TAB",
                "matched_product_name_ar": "بانادول",
                "matched_store_product_id": "T-3",
                "match_score": 80.0, "verified": "algo_match",
                "match_method": "brand_index",
            }
            for i in range(3)
        ])
        cfg = MatchingConfig(ai_verify_limit=2)

        selected = _select_for_verification(results, cfg)

        self.assertEqual(len(selected), 2)


class TestBuildVerifyItems(unittest.TestCase):
    def test_builds_items_with_idx(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "PANADOL EXTRA",
                "matched_product_name_en": "PANADOL EXTRA 24 TAB",
                "matched_product_name_ar": "بانادول اكسترا",
                "matched_store_product_id": "T-2",
                "match_score": 85.0, "verified": "algo_match",
                "match_method": "brand_index",
            },
        ])
        items = _build_verify_items(results)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0][0], "PANADOL EXTRA")
        self.assertEqual(items[0][1], "PANADOL EXTRA 24 TAB")
        self.assertEqual(items[0][2], "بانادول اكسترا")
        self.assertEqual(items[0][3], 0)
        self.assertEqual(items[0][4], 85.0)
        self.assertEqual(items[0][5], "brand_index")

    def test_builds_items_with_price_context(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "PANADOL EXTRA",
                "matched_product_name_en": "PANADOL EXTRA 24 TAB",
                "matched_product_name_ar": "بانادول اكسترا",
                "matched_store_product_id": "T-2",
                "match_score": 85.0, "verified": "algo_match",
                "match_method": "brand_index",
                "_drug_price": "34",
                "_matched_price": 34.0,
            },
        ])

        items = _build_verify_items(results)

        self.assertEqual(items[0][6], "34")
        self.assertEqual(items[0][7], 34.0)


class TestGetUnmatched(unittest.TestCase):
    def test_returns_empty_matched(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "AUGMENTIN",
                "matched_product_name_en": "AUGMENTIN 625 MG 10 TAB",
                "matched_product_name_ar": "اوجمنتين",
                "matched_store_product_id": "T-1",
                "match_score": 95.0, "verified": "algo_match",
                "match_method": "brand_index",
            },
            {
                "code": "D2", "drug_name": "UNKNOWN",
                "matched_product_name_en": "",
                "matched_product_name_ar": "",
                "matched_store_product_id": "",
                "match_score": "", "verified": "",
                "match_method": "no_match",
            },
        ])
        unmatched = _get_unmatched(results)
        self.assertEqual(len(unmatched), 1)
        self.assertEqual(unmatched.iloc[0]["code"], "D2")


class TestApplyCorrection(unittest.TestCase):
    def test_applies_ai_correction(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "PANADOL EXTRA",
                "matched_product_name_en": "PANADOL 20 TAB",
                "matched_product_name_ar": "بانادول",
                "matched_store_product_id": "T-3",
                "match_score": 85.0, "verified": "algo_match",
                "match_method": "brand_index",
            },
        ])
        ai_result = {
            "record": {
                "product_name_en": "PANADOL EXTRA 24 TAB",
                "product_name_ar": "بانادول اكسترا",
                "store_product_id": "T-2",
            },
            "score": 95.0,
        }
        _apply_correction(results, 0, ai_result)
        self.assertEqual(
            results.at[0, "matched_product_name_en"],
            "PANADOL EXTRA 24 TAB",
        )
        self.assertEqual(results.at[0, "verified"], "ai_corrected")
        self.assertEqual(results.at[0, "match_method"], "ai_verified")


class TestClearMatch(unittest.TestCase):
    def test_clears_match_fields(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "PANADOL",
                "matched_product_name_en": "PANADOL 20 TAB",
                "matched_product_name_ar": "بانادول",
                "matched_store_product_id": "T-3",
                "match_score": 85.0, "verified": "algo_match",
                "match_method": "brand_index",
            },
        ])
        _clear_match(results, 0)
        self.assertEqual(results.at[0, "matched_product_name_en"], "")
        self.assertEqual(results.at[0, "matched_store_product_id"], "")
        self.assertEqual(results.at[0, "match_score"], "")


class TestApplySearchResult(unittest.TestCase):
    def test_applies_search_result(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "UNKNOWN",
                "matched_product_name_en": "",
                "matched_product_name_ar": "",
                "matched_store_product_id": "",
                "match_score": "", "verified": "",
                "match_method": "no_match",
            },
        ])
        ai_result = {
            "record": {
                "product_name_en": "PANADOL EXTRA 24 TAB",
                "product_name_ar": "بانادول اكسترا",
                "store_product_id": "T-2",
            },
            "score": 88.0,
            "confidence": 0.9,
        }
        _apply_search_result(results, 0, ai_result)
        self.assertEqual(
            results.at[0, "matched_product_name_en"],
            "PANADOL EXTRA 24 TAB",
        )
        self.assertEqual(results.at[0, "verified"], "ai_found")
        self.assertEqual(results.at[0, "match_method"], "ai_search")


class TestDedupeCandidates(unittest.TestCase):
    def test_removes_duplicate_ids(self):
        candidates = [
            ({"store_product_id": "T-1", "product_name_en": "A"}, 90.0, 0),
            ({"store_product_id": "T-1", "product_name_en": "A"}, 85.0, 0),
            ({"store_product_id": "T-2", "product_name_en": "B"}, 80.0, 1),
        ]
        deduped = _dedupe_candidates(candidates)
        self.assertEqual(len(deduped), 2)
        self.assertEqual(deduped[0][0]["store_product_id"], "T-1")
        self.assertEqual(deduped[1][0]["store_product_id"], "T-2")


class TestRunAiVerificationNoKey(unittest.TestCase):
    def test_skips_without_api_key(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "PANADOL",
                "matched_product_name_en": "PANADOL 20 TAB",
                "matched_product_name_ar": "بانادول",
                "matched_store_product_id": "T-3",
                "match_score": 85.0, "verified": "algo_match",
                "match_method": "brand_index",
            },
        ])
        index = _make_index()
        cfg = MatchingConfig()
        api_cfg = APIConfig(api_key="")
        out = asyncio.run(
            run_ai_verification(results, index, cfg, api_cfg)
        )
        # unchanged
        self.assertEqual(
            out.at[0, "matched_product_name_en"], "PANADOL 20 TAB",
        )


class TestRunAiSearchNoKey(unittest.TestCase):
    def test_skips_without_api_key(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "UNKNOWN",
                "matched_product_name_en": "",
                "matched_product_name_ar": "",
                "matched_store_product_id": "",
                "match_score": "", "verified": "",
                "match_method": "no_match",
            },
        ])
        index = _make_index()
        cfg = MatchingConfig()
        api_cfg = APIConfig(api_key="")
        out = asyncio.run(
            run_ai_search(results, index, cfg, api_cfg)
        )
        self.assertEqual(out.at[0, "matched_product_name_en"], "")


class TestRunAiVerificationWithMock(unittest.TestCase):
    """Test AI verify with mocked AIVerifier."""

    def test_confirmed_match(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "FEROGLOBIN B12 30 CAP",
                "matched_product_name_en": "FEROGLOBIN 30 CAPS",
                "matched_product_name_ar": "فيرجلوبين",
                "matched_store_product_id": "T-4",
                "match_score": 85.0, "verified": "algo_match",
                "match_method": "brand_index",
            },
        ])
        index = _make_index()
        cfg = MatchingConfig()
        api_cfg = APIConfig(api_key="test-key")

        mock_verifier = AsyncMock()
        mock_verifier.__aenter__ = AsyncMock(return_value=mock_verifier)
        mock_verifier.__aexit__ = AsyncMock(return_value=None)
        mock_verifier.verify_batch = AsyncMock(return_value=[
            {
                "is_correct": True,
                "reason": "same product",
                "confidence": 0.95,
                "row_idx": 0,
            },
        ])
        mock_verifier.find_better_match = AsyncMock(return_value=None)

        with patch("drug_matcher.ai_steps.AIVerifier", return_value=mock_verifier):
            out = asyncio.run(
                run_ai_verification(results, index, cfg, api_cfg)
            )
        self.assertEqual(out.at[0, "verified"], "ai_confirmed")
        self.assertEqual(out.at[0, "match_method"], "ai_verified")

    def test_rejected_match_no_better(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "PANADOL NIGHT 20 TAB",
                "matched_product_name_en": "STOPADOL NIGHT 30 TAB",
                "matched_product_name_ar": "ستوبادول",
                "matched_store_product_id": "T-5",
                "match_score": 80.0, "verified": "algo_match",
                "match_method": "fuzzy",
            },
        ])
        index = _make_index()
        cfg = MatchingConfig()
        api_cfg = APIConfig(api_key="test-key")

        mock_verifier = AsyncMock()
        mock_verifier.__aenter__ = AsyncMock(return_value=mock_verifier)
        mock_verifier.__aexit__ = AsyncMock(return_value=None)
        mock_verifier.verify_batch = AsyncMock(return_value=[
            {
                "is_correct": False,
                "reason": "different brand",
                "confidence": 0.9,
                "row_idx": 0,
            },
        ])
        mock_verifier.find_better_match = AsyncMock(return_value=None)

        with patch("drug_matcher.ai_steps.AIVerifier", return_value=mock_verifier):
            out = asyncio.run(
                run_ai_verification(results, index, cfg, api_cfg)
            )
        self.assertEqual(out.at[0, "verified"], "ai_rejected")
        self.assertEqual(out.at[0, "matched_product_name_en"], "")

    def test_corrected_match(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "PANADOL EXTRA 24 TAB",
                "matched_product_name_en": "PANADOL 20 TAB",
                "matched_product_name_ar": "بانادول",
                "matched_store_product_id": "T-3",
                "match_score": 82.0, "verified": "algo_match",
                "match_method": "fuzzy",
            },
        ])
        index = _make_index()
        cfg = MatchingConfig()
        api_cfg = APIConfig(api_key="test-key")

        mock_verifier = AsyncMock()
        mock_verifier.__aenter__ = AsyncMock(return_value=mock_verifier)
        mock_verifier.__aexit__ = AsyncMock(return_value=None)
        mock_verifier.verify_batch = AsyncMock(return_value=[
            {
                "is_correct": False,
                "reason": "wrong product",
                "confidence": 0.9,
                "row_idx": 0,
            },
        ])
        mock_verifier.find_better_match = AsyncMock(return_value={
            "record": {
                "product_name_en": "PANADOL EXTRA 24 TAB",
                "product_name_ar": "بانادول اكسترا",
                "store_product_id": "T-2",
            },
            "score": 95.0,
            "confidence": 0.95,
        })

        with patch("drug_matcher.ai_steps.AIVerifier", return_value=mock_verifier):
            out = asyncio.run(
                run_ai_verification(results, index, cfg, api_cfg)
            )
        self.assertEqual(out.at[0, "verified"], "ai_corrected")
        self.assertEqual(
            out.at[0, "matched_product_name_en"],
            "PANADOL EXTRA 24 TAB",
        )


class TestRunAiSearchWithMock(unittest.TestCase):
    """Test AI search with mocked AIVerifier."""

    def test_finds_match(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "PANADOL EXTRA 24 TAB",
                "matched_product_name_en": "",
                "matched_product_name_ar": "",
                "matched_store_product_id": "",
                "match_score": "", "verified": "",
                "match_method": "no_match",
            },
        ])
        index = _make_index()
        cfg = MatchingConfig(fuzzy_threshold=70)
        api_cfg = APIConfig(api_key="test-key")

        mock_verifier = AsyncMock()
        mock_verifier.__aenter__ = AsyncMock(return_value=mock_verifier)
        mock_verifier.__aexit__ = AsyncMock(return_value=None)
        mock_verifier.find_better_match = AsyncMock(return_value={
            "record": {
                "product_name_en": "PANADOL EXTRA 24 TAB",
                "product_name_ar": "بانادول اكسترا",
                "store_product_id": "T-2",
            },
            "score": 95.0,
            "confidence": 0.9,
        })

        with patch("drug_matcher.ai_steps.AIVerifier", return_value=mock_verifier):
            out = asyncio.run(
                run_ai_search(results, index, cfg, api_cfg)
            )
        self.assertEqual(out.at[0, "verified"], "ai_found")
        self.assertEqual(
            out.at[0, "matched_product_name_en"],
            "PANADOL EXTRA 24 TAB",
        )

    def test_search_exception_does_not_stop_batch(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "PANADOL EXTRA 24 TAB",
                "matched_product_name_en": "",
                "matched_product_name_ar": "",
                "matched_store_product_id": "",
                "match_score": "", "verified": "",
                "match_method": "no_match",
            },
            {
                "code": "D2", "drug_name": "PANADOL EXTRA 24 TAB",
                "matched_product_name_en": "",
                "matched_product_name_ar": "",
                "matched_store_product_id": "",
                "match_score": "", "verified": "",
                "match_method": "no_match",
            },
        ])
        index = _make_index()
        cfg = MatchingConfig(fuzzy_threshold=70)
        api_cfg = APIConfig(api_key="test-key")
        trace = MatchTraceLog(enabled=True)

        mock_verifier = AsyncMock()
        mock_verifier.__aenter__ = AsyncMock(return_value=mock_verifier)
        mock_verifier.__aexit__ = AsyncMock(return_value=None)
        mock_verifier.find_better_match = AsyncMock(side_effect=[
            ValueError("bad best_index"),
            {
                "record": {
                    "product_name_en": "PANADOL EXTRA 24 TAB",
                    "product_name_ar": "بانادول اكسترا",
                    "store_product_id": "T-2",
                },
                "score": 95.0,
                "confidence": 0.9,
            },
        ])
        mock_verifier.get_fallback_log = MagicMock(return_value="")

        with patch("drug_matcher.ai_steps.AIVerifier", return_value=mock_verifier):
            out = asyncio.run(
                run_ai_search(results, index, cfg, api_cfg, trace)
            )

        self.assertEqual(out.at[0, "matched_product_name_en"], "")
        self.assertEqual(out.at[1, "verified"], "ai_found")
        self.assertTrue(any(
            row.get("error_code") == "ai_search_exception"
            for row in trace._rows
        ))

    def test_passes_inventory_price_to_ai_search(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "PANADOL EXTRA 24 TAB",
                "matched_product_name_en": "",
                "matched_product_name_ar": "",
                "matched_store_product_id": "",
                "match_score": "", "verified": "",
                "match_method": "no_match",
                "_drug_price": "40",
            },
        ])
        index = _make_index()
        cfg = MatchingConfig(fuzzy_threshold=70)
        api_cfg = APIConfig(api_key="test-key")

        mock_verifier = AsyncMock()
        mock_verifier.__aenter__ = AsyncMock(return_value=mock_verifier)
        mock_verifier.__aexit__ = AsyncMock(return_value=None)
        mock_verifier.find_better_match = AsyncMock(return_value=None)
        mock_verifier.get_fallback_log = MagicMock(return_value="")

        with patch("drug_matcher.ai_steps.AIVerifier", return_value=mock_verifier):
            asyncio.run(run_ai_search(results, index, cfg, api_cfg))

        call = mock_verifier.find_better_match.call_args
        self.assertEqual(call.kwargs["inventory_price"], "40")

    def test_no_candidates_skips_ai(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "ZZZZZ UNKNOWN",
                "matched_product_name_en": "",
                "matched_product_name_ar": "",
                "matched_store_product_id": "",
                "match_score": "", "verified": "",
                "match_method": "no_match",
            },
        ])
        index = _make_index()
        cfg = MatchingConfig(fuzzy_threshold=80)
        api_cfg = APIConfig(api_key="test-key")

        mock_verifier = AsyncMock()
        mock_verifier.__aenter__ = AsyncMock(return_value=mock_verifier)
        mock_verifier.__aexit__ = AsyncMock(return_value=None)

        with patch("drug_matcher.ai_steps.AIVerifier", return_value=mock_verifier):
            out = asyncio.run(
                run_ai_search(results, index, cfg, api_cfg)
            )
        # no candidates -> find_better_match never called
        mock_verifier.find_better_match.assert_not_called()
        self.assertEqual(out.at[0, "matched_product_name_en"], "")

    def test_low_confidence_rejected(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "PANADOL EXTRA 24 TAB",
                "matched_product_name_en": "",
                "matched_product_name_ar": "",
                "matched_store_product_id": "",
                "match_score": "", "verified": "",
                "match_method": "no_match",
            },
        ])
        index = _make_index()
        cfg = MatchingConfig(fuzzy_threshold=70)
        api_cfg = APIConfig(api_key="test-key")

        mock_verifier = AsyncMock()
        mock_verifier.__aenter__ = AsyncMock(return_value=mock_verifier)
        mock_verifier.__aexit__ = AsyncMock(return_value=None)
        mock_verifier.find_better_match = AsyncMock(return_value={
            "record": {
                "product_name_en": "PANADOL EXTRA 24 TAB",
                "product_name_ar": "بانادول اكسترا",
                "store_product_id": "T-2",
            },
            "score": 85.0,
            "confidence": 0.5,  # below 0.7 threshold
        })

        with patch("drug_matcher.ai_steps.AIVerifier", return_value=mock_verifier):
            out = asyncio.run(
                run_ai_search(results, index, cfg, api_cfg)
            )
        # low confidence -> not accepted
        self.assertEqual(out.at[0, "matched_product_name_en"], "")

    def test_borderline_confidence_below_search_gate_rejected(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "PANADOL EXTRA 24 TAB",
                "matched_product_name_en": "",
                "matched_product_name_ar": "",
                "matched_store_product_id": "",
                "match_score": "", "verified": "",
                "match_method": "no_match",
            },
        ])
        index = _make_index()
        cfg = MatchingConfig(fuzzy_threshold=70)
        api_cfg = APIConfig(api_key="test-key")

        mock_verifier = AsyncMock()
        mock_verifier.__aenter__ = AsyncMock(return_value=mock_verifier)
        mock_verifier.__aexit__ = AsyncMock(return_value=None)
        mock_verifier.find_better_match = AsyncMock(return_value={
            "record": {
                "product_name_en": "PANADOL EXTRA 24 TAB",
                "product_name_ar": "بانادول اكسترا",
                "store_product_id": "T-2",
            },
            "score": 85.0,
            "confidence": 0.72,
        })

        with patch("drug_matcher.ai_steps.AIVerifier", return_value=mock_verifier):
            out = asyncio.run(
                run_ai_search(results, index, cfg, api_cfg)
            )
        self.assertEqual(out.at[0, "matched_product_name_en"], "")

    def test_lower_search_accept_confidence_accepts_borderline_result(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "PANADOL EXTRA 24 TAB",
                "matched_product_name_en": "",
                "matched_product_name_ar": "",
                "matched_store_product_id": "",
                "match_score": "", "verified": "",
                "match_method": "no_match",
            },
        ])
        index = _make_index()
        cfg = MatchingConfig(
            fuzzy_threshold=70,
            ai_search_accept_confidence=0.7,
        )
        api_cfg = APIConfig(api_key="test-key")

        mock_verifier = AsyncMock()
        mock_verifier.__aenter__ = AsyncMock(return_value=mock_verifier)
        mock_verifier.__aexit__ = AsyncMock(return_value=None)
        mock_verifier.find_better_match = AsyncMock(return_value={
            "record": {
                "product_name_en": "PANADOL EXTRA 24 TAB",
                "product_name_ar": "بانادول اكسترا",
                "store_product_id": "T-2",
            },
            "score": 85.0,
            "confidence": 0.72,
        })

        with patch("drug_matcher.ai_steps.AIVerifier", return_value=mock_verifier):
            out = asyncio.run(
                run_ai_search(results, index, cfg, api_cfg)
            )

        self.assertEqual(out.at[0, "verified"], "ai_found")

    def test_ai_search_limit_skips_extra_rows(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "PANADOL EXTRA 24 TAB",
                "matched_product_name_en": "",
                "matched_product_name_ar": "",
                "matched_store_product_id": "",
                "match_score": "", "verified": "",
                "match_method": "no_match",
            },
            {
                "code": "D2", "drug_name": "FEROGLOBIN 30 CAPS",
                "matched_product_name_en": "",
                "matched_product_name_ar": "",
                "matched_store_product_id": "",
                "match_score": "", "verified": "",
                "match_method": "no_match",
            },
        ])
        index = _make_index()
        cfg = MatchingConfig(fuzzy_threshold=70, ai_search_limit=1)
        api_cfg = APIConfig(api_key="test-key")
        trace = MatchTraceLog(enabled=True)

        mock_verifier = AsyncMock()
        mock_verifier.__aenter__ = AsyncMock(return_value=mock_verifier)
        mock_verifier.__aexit__ = AsyncMock(return_value=None)
        mock_verifier.find_better_match = AsyncMock(return_value=None)
        mock_verifier.get_fallback_log = MagicMock(return_value="")

        with patch("drug_matcher.ai_steps.AIVerifier", return_value=mock_verifier):
            asyncio.run(run_ai_search(results, index, cfg, api_cfg, trace))

        self.assertEqual(mock_verifier.find_better_match.call_count, 1)
        skipped = [
            row for row in trace._rows
            if row["step"] == "ai_search_not_eligible"
        ]
        self.assertEqual(len(skipped), 1)
        self.assertIn("ai_search_limit=1", skipped[0]["selection_reason"])


class TestAiSearchEligibility(unittest.TestCase):
    def test_rejects_low_score_candidates_before_ai(self):
        index = _make_index()
        parsed = index.get_parsed(0)
        candidates = [(index.get_record(0), 79.9, 0)]

        eligible = _eligible_search_candidates(
            parsed, candidates, index, MatchingConfig(),
        )

        self.assertEqual(eligible, [])

    def test_lower_candidate_threshold_keeps_more_candidates(self):
        index = _make_index()
        parsed = index.get_parsed(0)
        candidates = [(index.get_record(0), 75.0, 0)]
        cfg = MatchingConfig(ai_search_min_candidate_score=75.0)

        eligible = _eligible_search_candidates(parsed, candidates, index, cfg)

        self.assertEqual(len(eligible), 1)

    def test_keeps_high_score_safe_candidates(self):
        index = _make_index()
        parsed = index.get_parsed(2)
        candidates = [(index.get_record(2), 95.0, 2)]

        eligible = _eligible_search_candidates(
            parsed, candidates, index, MatchingConfig(),
        )

        self.assertEqual(len(eligible), 1)

    def test_review_policy_keeps_reviewable_import_mismatch(self):
        tawreed = pd.DataFrame([
            {
                "product_name_ar": "بانادول اكسترا",
                "product_name_en": "PANADOL EXTRA 24 TAB",
                "store_product_id": "T-1",
            },
        ])
        index = DrugIndex(tawreed, MatchingConfig())
        parsed = index.get_parsed(0)
        inventory = parse_drug("PANADOL EXTRA 24 TAB IMP")
        candidates = [(index.get_record(0), 95.0, 0, "different_import_status")]

        eligible = _eligible_search_candidates(
            inventory, candidates, index, MatchingConfig(),
        )

        self.assertEqual(len(eligible), 1)

    def test_review_candidate_acceptance_requires_higher_confidence(self):
        tawreed = pd.DataFrame([
            {
                "product_name_ar": "ادماليز",
                "product_name_en": "AMYLASE SYRUP 90 ML",
                "store_product_id": "T-1",
            },
        ])
        index = DrugIndex(tawreed, MatchingConfig())
        parsed = parse_drug("ADMLASE SYRUP 120 ML")
        candidates = [(index.get_record(0), 82.0, 0, "different_brand")]
        ai_result = {"record": index.get_record(0), "best_index": 1}

        threshold, reason = _search_acceptance_threshold(
            ai_result, candidates, parsed, index, MatchingConfig(),
        )

        self.assertEqual(reason, "different_brand")
        self.assertEqual(threshold, 0.85)

    def test_review_selects_component_mismatch_ai_found(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "ADMLASE SYRUP 120 ML",
                "matched_product_name_en": "AMYLASE SYRUP 90 ML",
                "matched_product_name_ar": "اميليز",
                "matched_store_product_id": "T-1",
                "match_score": 87.0, "verified": "ai_found",
                "match_method": "ai_search",
            },
        ])
        results["_ai_component_reason"] = "different_brand"
        results["ai_confidence"] = 0.99

        selected = _select_for_review(results, MatchingConfig(ai_review_threshold=0.95))

        self.assertEqual(len(selected), 1)

    def test_search_candidate_limit_expands_candidates(self):
        index = _make_index()
        parsed = index.get_parsed(2)
        cfg = MatchingConfig(ai_search_candidate_limit=10)

        candidates = _search_candidates(
            parsed, "PANADOL EXTRA 24 TAB", index, cfg,
        )

        self.assertGreaterEqual(len(candidates), 2)


class TestApplyReviewResults(unittest.TestCase):
    def test_low_confidence_review_disagreement_keeps_first_decision(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "PANADOL EXTRA 24 TAB",
                "matched_product_name_en": "",
                "matched_product_name_ar": "",
                "matched_store_product_id": "",
                "match_score": "", "verified": "ai_rejected",
                "match_method": "ai_verified",
            },
        ])
        index = _make_index()
        verifier = MagicMock()
        verifier._cfg.review_model = "review"
        verifier.get_fallback_log.return_value = ""

        overridden = asyncio.run(
            _apply_review_results(
                verifier, results, index,
                [{
                    "row_idx": 0,
                    "is_correct": False,
                    "confidence": 0.6,
                    "reason": "uncertain disagreement",
                    "api_failed": False,
                }],
                MatchingConfig(),
                trace=None,
            )
        )

        self.assertEqual(overridden, 0)
        self.assertEqual(results.at[0, "verified"], "ai_rejected")
        self.assertEqual(results.at[0, "ai_review_confidence"], 0.6)

    def test_fresh_review_low_confidence_confirm_rejects_conservatively(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "PANADOL EXTRA 24 TAB",
                "matched_product_name_en": "PANADOL EXTRA 24 TAB",
                "matched_product_name_ar": "بانادول اكسترا",
                "matched_store_product_id": "T-2",
                "match_score": 85.0, "verified": "ai_confirmed",
                "match_method": "ai_verified",
            },
        ])
        index = _make_index()
        verifier = MagicMock()
        verifier._cfg.review_model = "review"
        verifier.get_fallback_log.return_value = ""

        overridden = asyncio.run(
            _apply_review_results(
                verifier, results, index,
                [{
                    "row_idx": 0,
                    "is_correct": True,
                    "confidence": 0.6,
                    "reason": "low confidence",
                    "api_failed": True,
                }],
                MatchingConfig(),
                trace=None,
            )
        )

        self.assertEqual(overridden, 1)
        self.assertEqual(results.at[0, "verified"], "ai_review_rejected")
        self.assertEqual(results.at[0, "matched_product_name_en"], "")


class TestBatchReview(unittest.TestCase):
    def test_propagates_api_failed_flag_not_row_index(self):
        verifier = AsyncMock()
        verifier.review_batch = AsyncMock(return_value=[
            {"is_correct": True, "row_idx": 10},
            {"is_correct": False, "row_idx": 11},
        ])
        items = [
            ("A", "B", "", "ai_rejected", 0.5, "", 10, False, "10", "11"),
            ("C", "D", "", "ai_confirmed", 0.0, "", 11, True, "20", "20"),
        ]

        out = asyncio.run(_batch_review(verifier, items, MatchingConfig()))

        self.assertEqual(out[0]["api_failed"], False)
        self.assertEqual(out[1]["api_failed"], True)


class TestAiStepsWithTrace(unittest.TestCase):
    """Test that AI steps log to trace correctly."""

    def test_verify_skip_logs_trace(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "PANADOL",
                "matched_product_name_en": "PANADOL 20 TAB",
                "matched_product_name_ar": "بانادول",
                "matched_store_product_id": "T-3",
                "match_score": 85.0, "verified": "algo_match",
                "match_method": "brand_index",
            },
        ])
        index = _make_index()
        cfg = MatchingConfig()
        api_cfg = APIConfig(api_key="")
        trace = MatchTraceLog(enabled=True)

        asyncio.run(
            run_ai_verification(results, index, cfg, api_cfg, trace)
        )
        # Should have ai_skip rows
        skip_rows = [r for r in trace._rows if r["step"] == "ai_skip"]
        self.assertTrue(len(skip_rows) > 0)
        self.assertEqual(skip_rows[0]["ai_phase"], "verify")
        self.assertEqual(skip_rows[0]["ai_result"], "skipped")

    def test_search_skip_logs_trace(self):
        results = _make_results([
            {
                "code": "D1", "drug_name": "UNKNOWN",
                "matched_product_name_en": "",
                "matched_product_name_ar": "",
                "matched_store_product_id": "",
                "match_score": "", "verified": "",
                "match_method": "no_match",
            },
        ])
        index = _make_index()
        cfg = MatchingConfig()
        api_cfg = APIConfig(api_key="")
        trace = MatchTraceLog(enabled=True)

        asyncio.run(
            run_ai_search(results, index, cfg, api_cfg, trace)
        )
        skip_rows = [r for r in trace._rows if r["step"] == "ai_skip"]
        self.assertTrue(len(skip_rows) > 0)
        self.assertEqual(skip_rows[0]["ai_phase"], "search")


if __name__ == "__main__":
    unittest.main()
