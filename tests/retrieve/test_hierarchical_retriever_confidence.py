# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: AGPL-3.0
"""Unit tests for the confidence-aware ranking score."""

import pytest

from openviking.retrieve.hierarchical_retriever import (
    CONFIDENCE_PENALTY_LAMBDA,
    HierarchicalRetriever,
)


def _retriever() -> HierarchicalRetriever:
    retriever = HierarchicalRetriever.__new__(HierarchicalRetriever)
    retriever.hotness_alpha = 0.0
    return retriever


def _candidate(uri, raw_score, confidence):
    return {
        "uri": uri,
        "_final_score": raw_score,
        "confidence": confidence,
        "level": 2,
        "context_type": "resource",
    }


async def _convert(items):
    return await _retriever()._convert_to_matched_contexts(
        [_candidate(*item) for item in items], None, apply_hotness=False
    )


def test_penalty_lambda_is_twenty_percent():
    assert CONFIDENCE_PENALTY_LAMBDA == 0.2


@pytest.mark.asyncio
async def test_convert_identity_when_confidence_one():
    """An unannotated record keeps the exact pre-change score."""
    matches = await _convert([("a", 0.8, 1.0)])

    assert matches[0].score == 0.8
    assert matches[0].raw_score == 0.8
    assert matches[0].confidence == 1.0


@pytest.mark.asyncio
async def test_convert_cross_band_does_not_overtake():
    """A strong match discounted to half still outranks a weak, trusted one."""
    matches = await _convert([("Y", 0.46, 1.0), ("X", 0.90, 0.5)])

    assert [m.uri for m in matches] == ["X", "Y"]
    assert matches[0].score == pytest.approx(0.81)
    assert matches[1].score == pytest.approx(0.46)


@pytest.mark.asyncio
async def test_convert_within_band_overtakes():
    """Within the discount band, the trusted record moves ahead."""
    matches = await _convert([("P", 0.50, 0.5), ("Q", 0.46, 1.0)])

    assert [m.uri for m in matches] == ["Q", "P"]


@pytest.mark.asyncio
async def test_convert_tight_boundary_inside_lambda_swaps():
    """A 19% unweighted gap sits inside the 20% band and swaps."""
    matches = await _convert([("A", 0.50, 0.0), ("B", 0.405, 1.0)])

    assert [m.uri for m in matches] == ["B", "A"]


@pytest.mark.asyncio
async def test_convert_tight_boundary_outside_lambda_keeps_order():
    """A 21% unweighted gap sits outside the band and cannot swap."""
    matches = await _convert([("A", 0.50, 0.0), ("B", 0.395, 1.0)])

    assert [m.uri for m in matches] == ["A", "B"]


@pytest.mark.asyncio
@pytest.mark.parametrize("confidence", [0.0, 0.3, 0.5, 1.0])
async def test_convert_discount_is_bounded(confidence):
    """The weighted score never leaves [raw * 0.8, raw]."""
    matches = await _convert([("a", 0.8, confidence)])
    match = matches[0]

    assert match.raw_score * 0.8 - 1e-9 <= match.score <= match.raw_score + 1e-9
    assert match.score == pytest.approx(
        match.raw_score * (1 - CONFIDENCE_PENALTY_LAMBDA * (1 - match.confidence)),
        abs=1e-9,
    )


@pytest.mark.asyncio
async def test_convert_clamps_out_of_range_stored_value():
    """A stored value above 1.0 must not turn the discount into a boost."""
    matches = await _convert([("a", 0.8, 1.5)])

    assert matches[0].confidence == 1.0
    assert matches[0].score == matches[0].raw_score


@pytest.mark.asyncio
async def test_convert_defaults_when_confidence_missing():
    """Records indexed before the field existed behave as unannotated."""
    matches = await _retriever()._convert_to_matched_contexts(
        [{"uri": "a", "_final_score": 0.5, "level": 2, "context_type": "resource"}],
        None,
        apply_hotness=False,
    )

    assert matches[0].confidence == 1.0
    assert matches[0].score == 0.5


@pytest.mark.asyncio
async def test_convert_tie_break_prefers_higher_raw_score():
    """Equal weighted scores order by the unweighted score, deterministically.

    ``0.5 * 0.8`` and the literal ``0.4`` are the same double, so this pair
    produces a genuine tie that only the secondary key can resolve.
    """
    matches = await _convert([("low_raw", 0.4, 1.0), ("high_raw", 0.5, 0.0)])

    assert matches[0].score == matches[1].score
    assert [m.uri for m in matches] == ["high_raw", "low_raw"]
    assert matches[0].raw_score > matches[1].raw_score


@pytest.mark.asyncio
async def test_threshold_operand_is_unweighted_score():
    """Gating happens on the unweighted score, so the discount cannot drop a hit.

    The threshold is applied by the surrounding pipeline on ``_final_score``
    before conversion; this pins the resulting behaviour: a discounted record
    below the weighted threshold is still returned.
    """
    candidates = [
        candidate
        for candidate in [_candidate("A", 0.42, 0.0), _candidate("B", 0.21, 1.0)]
        if candidate["_final_score"] >= 0.35
    ]

    matches = await _retriever()._convert_to_matched_contexts(candidates, None, apply_hotness=False)

    assert [m.uri for m in matches] == ["A"]
    assert matches[0].score == pytest.approx(0.336)
    assert matches[0].score < 0.35
