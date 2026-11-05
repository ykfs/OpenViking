# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: AGPL-3.0
"""Unit tests for confidence through the context assembly chain."""

import pytest

from openviking.retrieve.context_assembler.budget import _make_entry
from openviking.retrieve.context_assembler.gather import Candidate, gather_candidates
from openviking.retrieve.context_assembler.models import AssembledEntry
from openviking.retrieve.context_assembler.render import render_entry
from openviking.server.identity import RequestContext, Role
from openviking_cli.retrieve.types import ContextType, MatchedContext
from openviking_cli.session.user_id import UserIdentifier


class _FakeSearch:
    def __init__(self, result):
        self.result = result

    async def find(self, **_kwargs):
        return self.result


class _FakeService:
    def __init__(self, result):
        self.search = _FakeSearch(result)


def _request_ctx() -> RequestContext:
    return RequestContext(user=UserIdentifier("default", "default"), role=Role.ROOT)


async def _gather(*items):
    service = _FakeService({"memories": [], "resources": list(items), "skills": []})
    candidates, _stats = await gather_candidates(
        service=service,
        ctx=_request_ctx(),
        queries=["q"],
        quotas={"resources": 5},
        limit=5,
        score_threshold=None,
    )
    return candidates


def _candidate(**overrides) -> Candidate:
    values = {
        "uri": "viking://resources/a",
        "base_uri": "viking://resources/a",
        "category": "resource",
        "score": 0.21,
        "ranked_score": 0.21,
        "level": 2,
        "abstract": "abstract",
        "origin": "self",
        "is_directory": False,
        "read_ctx": None,
        "confidence": 0.5,
        "raw_score": 0.42,
    }
    values.update(overrides)
    return Candidate(**values)


def test_make_entry_carries_raw_score_and_confidence():
    """The only channel into the rendered memory tag must transfer both values."""
    entry = _make_entry(_candidate(), "summary", "BODY")

    assert entry.raw_score == 0.42
    assert entry.confidence == 0.5
    assert entry.score == 0.21


def test_make_entry_defaults_when_candidate_lacks_fields():
    """A candidate built without the new fields still produces an entry."""
    entry = _make_entry(_candidate(confidence=1.0, raw_score=0.0), "summary", "BODY")

    assert entry.raw_score == 0.0
    assert entry.confidence == 1.0


def test_assembled_entry_serializes_both_fields():
    """The context-mode entries list exposes both keys."""
    data = _make_entry(_candidate(), "summary", "BODY").to_dict()

    assert data["raw_score"] == 0.42
    assert data["confidence"] == 0.5


def test_assembled_entry_legacy_defaults_are_stable():
    """An entry constructed the old way still serializes a complete contract."""
    data = AssembledEntry(uri="u", category="c", score=0.5, detail="summary").to_dict()

    assert data["raw_score"] == 0.0
    assert data["confidence"] == 1.0


def test_render_entry_adds_attributes_without_touching_body():
    """Credentials-free metadata goes into attributes, never into the body text."""
    out = render_entry(
        AssembledEntry(
            uri="u",
            category="resource",
            score=0.21,
            detail="summary",
            text="BODY",
            raw_score=0.42,
            confidence=0.5,
        )
    )

    assert 'raw_score="0.42"' in out
    assert 'confidence="0.50"' in out
    assert "BODY" in out
    assert out.count("confidence") == 1


def test_render_entry_defaults_when_unset():
    """An entry without the fields still renders valid attributes."""
    out = render_entry(AssembledEntry(uri="u", category="c", score=0.5, detail="summary"))

    assert 'confidence="1.00"' in out
    assert 'raw_score="0.00"' in out


@pytest.mark.asyncio
async def test_gather_transfers_confidence_from_matched_context():
    """Gathering must not drop the two fields on the way to the assembler."""
    item = MatchedContext(
        uri="viking://resources/a",
        context_type=ContextType.RESOURCE,
        score=0.21,
        raw_score=0.42,
        confidence=0.4,
        abstract="abstract",
    )

    candidates = await _gather(item)

    assert len(candidates) == 1
    assert candidates[0].confidence == 0.4
    assert candidates[0].raw_score == 0.42


@pytest.mark.asyncio
async def test_gather_defaults_when_fields_missing():
    """A hit from an older index falls back to unannotated values.

    ``MatchedContext.raw_score`` defaults to 0.0 and the attribute is always
    present, so gathering preserves that default rather than substituting the
    weighted score. Only a payload that omits the key entirely falls back to
    the reported score.
    """
    item = MatchedContext(
        uri="viking://resources/a",
        context_type=ContextType.RESOURCE,
        score=0.5,
        abstract="abstract",
    )

    candidates = await _gather(item)

    assert len(candidates) == 1
    assert candidates[0].confidence == 1.0
    assert candidates[0].raw_score == 0.0
