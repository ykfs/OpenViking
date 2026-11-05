# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: AGPL-3.0
"""Unit tests for confidence on skill search results."""

from openviking.server.routers.skills import _skill_summary_from_hit

_HIT_URI = "viking://user/default/skills/demo/.abstract.md"


def test_skill_summary_includes_raw_score_and_confidence():
    summary = _skill_summary_from_hit(
        {
            "uri": _HIT_URI,
            "score": 0.5,
            "raw_score": 0.6,
            "confidence": 0.8,
            "abstract": "abstract",
            "match_reason": "semantic",
            "level": 0,
        }
    )

    assert summary["raw_score"] == 0.6
    assert summary["confidence"] == 0.8


def test_skill_summary_defaults_when_stored_fields_missing():
    """Skill records written before the field existed rank as unannotated."""
    summary = _skill_summary_from_hit(
        {"uri": _HIT_URI, "score": 0.5, "abstract": "a", "match_reason": "m", "level": 0}
    )

    assert summary["raw_score"] == 0.0
    assert summary["confidence"] == 1.0
    assert summary["score"] == 0.5
    assert summary["match_reason"] == "m"
    assert summary["level"] == 0
    assert summary["abstract"] == "a"


def test_skill_summaries_preserve_hit_order():
    """Summaries are built per hit and iterated in the server's order."""
    hits = [
        {"uri": "viking://user/default/skills/a/.abstract.md", "score": 0.9},
        {"uri": "viking://user/default/skills/b/.abstract.md", "score": 0.5},
        {"uri": "viking://user/default/skills/c/.abstract.md", "score": 0.1},
    ]

    summaries = [_skill_summary_from_hit(hit) for hit in hits]

    assert [item["score"] for item in summaries] == [0.9, 0.5, 0.1]
