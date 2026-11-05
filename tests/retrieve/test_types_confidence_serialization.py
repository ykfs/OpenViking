# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: AGPL-3.0
"""Unit tests for confidence in the retrieval result contract."""

from openviking_cli.retrieve.types import ContextType, FindResult, MatchedContext


def _result() -> FindResult:
    return FindResult(memories=[], resources=[], skills=[])


def test_context_to_dict_includes_raw_score_and_confidence():
    """The list response exposes both new keys alongside the weighted score."""
    ctx = MatchedContext(
        uri="viking://resources/a",
        context_type=ContextType.RESOURCE,
        score=0.21,
        raw_score=0.42,
        confidence=0.5,
    )

    data = _result()._context_to_dict(ctx)

    assert data["score"] == 0.21
    assert data["raw_score"] == 0.42
    assert data["confidence"] == 0.5


def test_query_result_to_dict_provenance_includes_both():
    """The provenance branch carries the same two keys, not just the list branch."""
    from types import SimpleNamespace

    from openviking_cli.retrieve.types import QueryResult, TypedQuery

    ctx = MatchedContext(
        uri="viking://resources/a",
        context_type=ContextType.RESOURCE,
        score=0.21,
        raw_score=0.42,
        confidence=0.5,
        match_reason="semantic",
    )
    query = TypedQuery(query="q", context_type=ContextType.RESOURCE, intent="", priority=1)
    qr = QueryResult(
        query=query,
        matched_contexts=[ctx],
        searched_directories=[],
        thinking_trace=SimpleNamespace(to_dict=lambda: {}),
    )

    data = _result()._query_result_to_dict(qr)

    match = data["matched_contexts"][0]
    assert match["raw_score"] == 0.42
    assert match["confidence"] == 0.5


def test_from_dict_reads_both_fields():
    """A response carrying the fields is parsed back into the model."""
    parsed = FindResult.from_dict(
        {"resources": [{"uri": "u", "score": 0.21, "raw_score": 0.42, "confidence": 0.5}]}
    )

    ctx = parsed.resources[0]
    assert ctx.raw_score == 0.42
    assert ctx.confidence == 0.5


def test_from_dict_legacy_payload_defaults():
    """A response from an older server parses without raising."""
    parsed = FindResult.from_dict({"resources": [{"uri": "u", "score": 0.5}]})

    ctx = parsed.resources[0]
    assert ctx.score == 0.5
    assert ctx.raw_score == 0.0
    assert ctx.confidence == 1.0
