# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: AGPL-3.0
"""Unit tests for the confidence helpers."""

import pytest

from openviking.utils.confidence import (
    CONFIDENCE_FIELD,
    DEFAULT_CONFIDENCE,
    coerce_confidence_for_read,
    confidence_factor,
    normalize_confidence_for_write,
)
from openviking_cli.exceptions import InvalidArgumentError


def test_normalize_confidence_for_write_none():
    """Given no value supplied, the default is returned instead of an error."""
    assert normalize_confidence_for_write(None) == 1.0
    assert DEFAULT_CONFIDENCE == 1.0
    assert CONFIDENCE_FIELD == "confidence"


@pytest.mark.parametrize("value", [0.0, 0.5, 1.0, 0.37])
def test_normalize_confidence_for_write_valid_bounds(value):
    """Given an in-range value, it is returned unchanged."""
    assert normalize_confidence_for_write(value) == value


@pytest.mark.parametrize("value", [-0.1, 1.1, 2.0, -1])
def test_normalize_confidence_for_write_out_of_range(value):
    """Given an out-of-range value, the write side rejects it by name."""
    with pytest.raises(InvalidArgumentError, match="confidence"):
        normalize_confidence_for_write(value)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_normalize_confidence_for_write_non_finite(value):
    """Given a non-finite value, the write side rejects it."""
    with pytest.raises(InvalidArgumentError, match="confidence"):
        normalize_confidence_for_write(value)


def test_normalize_confidence_for_write_non_numeric():
    """Given a non-numeric value, the write side rejects it."""
    with pytest.raises(InvalidArgumentError, match="confidence"):
        normalize_confidence_for_write("high")


@pytest.mark.parametrize(
    ("stored", "expected"),
    [(1.5, 1.0), (-0.5, 0.0), (2.0, 1.0), (0.4, 0.4), (0.0, 0.0), (1.0, 1.0)],
)
def test_coerce_confidence_for_read_clamps_out_of_range(stored, expected):
    """Given stored values, the read side clamps them into [0, 1]."""
    assert coerce_confidence_for_read(stored) == expected


@pytest.mark.parametrize("value", [None, "abc", float("nan"), float("inf")])
def test_coerce_confidence_for_read_missing_or_invalid(value):
    """Given unusable stored values, the read side falls back without raising."""
    assert coerce_confidence_for_read(value) == 1.0


@pytest.mark.parametrize(
    ("confidence", "expected"),
    [(1.0, 1.0), (0.5, 0.9), (0.0, 0.8)],
)
def test_confidence_factor_endpoints(confidence, expected):
    """Given lambda 0.2, the factor spans 1.0 down to 0.8."""
    assert confidence_factor(confidence, 0.2) == pytest.approx(expected)


@pytest.mark.parametrize("penalty_lambda", [0.0, 0.2, 1.0])
def test_confidence_factor_identity_at_one(penalty_lambda):
    """An unannotated record keeps a factor of exactly 1.0 for any lambda."""
    assert confidence_factor(1.0, penalty_lambda) == 1.0
