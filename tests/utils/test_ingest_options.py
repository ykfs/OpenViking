# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: AGPL-3.0
"""Unit tests for confidence propagation through ingest options."""

from openviking.utils.embedding_utils import _apply_ingest_options
from openviking.utils.ingest_options import IngestOptions


class _FakeEmbeddingMsg:
    def __init__(self):
        self.context_data = {}


def test_ingest_options_carries_confidence():
    """Given a confidence value, a dict round trip preserves it."""
    options = IngestOptions(confidence=0.4)

    assert IngestOptions.from_value(options.to_dict()).confidence == 0.4


def test_ingest_options_confidence_defaults_to_none():
    """Given tags only, confidence stays unset so updates keep the stored value."""
    options = IngestOptions.from_search_tags(["alpha"])

    assert options.confidence is None
    assert IngestOptions().confidence is None


def test_apply_ingest_options_writes_confidence_only():
    """Given confidence without tags, it reaches the context payload."""
    msg = _FakeEmbeddingMsg()

    _apply_ingest_options(msg, IngestOptions(confidence=0.6))

    assert msg.context_data == {"confidence": 0.6}


def test_apply_ingest_options_skips_write_when_confidence_none():
    """Given no confidence, the payload omits the key so a partial update keeps it."""
    msg = _FakeEmbeddingMsg()

    _apply_ingest_options(msg, IngestOptions())

    assert "confidence" not in msg.context_data
    assert msg.context_data == {}


def test_apply_ingest_options_writes_both_when_tags_and_confidence():
    """Given tags and confidence, both reach the context payload."""
    msg = _FakeEmbeddingMsg()

    _apply_ingest_options(msg, IngestOptions(search_tags=["alpha"], confidence=0.4))

    assert msg.context_data["confidence"] == 0.4
    assert msg.context_data["search_tags"] == ["alpha"]
    assert msg.context_data["_upsert_options"] == {"search_tag_mode": "replace"}


def test_apply_ingest_options_clamps_stored_out_of_range_value():
    """A value that bypassed write validation is clamped before it is written."""
    msg = _FakeEmbeddingMsg()

    _apply_ingest_options(msg, IngestOptions(confidence=1.5))

    assert msg.context_data["confidence"] == 1.0
