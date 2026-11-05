# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: AGPL-3.0
"""Unit tests pinning the retrieval output field projections."""

from openviking.storage.viking_vector_index_backend import (
    FETCH_BY_URI_OUTPUT_FIELDS,
    LOOKUP_OUTPUT_FIELDS,
    RETRIEVAL_OUTPUT_FIELDS,
)


def test_retrieval_output_fields_include_confidence():
    """Candidate projections must carry confidence or scoring cannot read it."""
    assert "confidence" in RETRIEVAL_OUTPUT_FIELDS


def test_fetch_by_uri_output_fields_include_confidence():
    """Read-back projections must carry confidence so tags updates keep it."""
    assert "confidence" in FETCH_BY_URI_OUTPUT_FIELDS


def test_lookup_output_fields_unchanged():
    """Lookup stays a narrow projection; confidence is not needed there."""
    assert "confidence" not in LOOKUP_OUTPUT_FIELDS
