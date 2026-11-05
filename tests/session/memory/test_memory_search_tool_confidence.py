# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: AGPL-3.0
"""Unit tests for confidence on the in-process memory search tool."""

from openviking.session.memory.tools import optimize_search_result


def _payload(*items):
    return {"memories": list(items)}


def test_optimize_search_result_keeps_raw_score_and_confidence():
    """The tool previously kept only uri/score; both new fields must survive."""
    result = optimize_search_result(
        _payload(
            {
                "uri": "viking://user/memories/a",
                "score": 0.21,
                "raw_score": 0.42,
                "confidence": 0.5,
                "abstract": "x",
            }
        ),
        5,
    )

    assert set(result[0]) == {"uri", "score", "raw_score", "confidence"}
    assert result[0]["raw_score"] == 0.42
    assert result[0]["confidence"] == 0.5


def test_optimize_search_result_defaults_when_fields_missing():
    """An older payload must not raise a KeyError."""
    result = optimize_search_result(_payload({"uri": "viking://user/memories/a", "score": 0.5}), 5)

    assert result[0]["raw_score"] == 0.0
    assert result[0]["confidence"] == 1.0


def test_optimize_search_result_preserves_order():
    """The tool must not reorder what the server ranked."""
    result = optimize_search_result(
        _payload(
            {"uri": "viking://user/memories/a", "score": 0.9},
            {"uri": "viking://user/memories/b", "score": 0.5},
            {"uri": "viking://user/memories/c", "score": 0.1},
        ),
        5,
    )

    assert [item["uri"] for item in result] == [
        "viking://user/memories/a",
        "viking://user/memories/b",
        "viking://user/memories/c",
    ]
