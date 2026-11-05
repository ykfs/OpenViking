# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: AGPL-3.0
"""Human-assigned resource confidence: validation, coercion and discounting.

Confidence is a writer-supplied scalar in the closed range ``[0.0, 1.0]``. It is
stored alongside a context record and, at retrieval time, used to discount the
record's ranking score so that lower-confidence material ranks lower.

Two independent defences live here:

* ``normalize_confidence_for_write`` rejects bad values at the request boundary,
  so newly written data is always clean.
* ``coerce_confidence_for_read`` repairs values read back from storage, which
  never passed through the write-side check (legacy records, ovpack restores,
  out-of-band vector writes). A stored value above 1.0 would otherwise produce a
  factor above 1.0 and boost the score instead of discounting it.
"""

from __future__ import annotations

import math
from typing import Any

from openviking_cli.exceptions import InvalidArgumentError

CONFIDENCE_FIELD = "confidence"
DEFAULT_CONFIDENCE = 1.0
MIN_CONFIDENCE = 0.0
MAX_CONFIDENCE = 1.0


def normalize_confidence_for_write(value: Any) -> float:
    """Validate a caller-supplied confidence value.

    ``None`` means "not supplied" and resolves to ``DEFAULT_CONFIDENCE``.
    Out-of-range, non-numeric and non-finite values are rejected rather than
    silently clamped, so a typo cannot turn into a silent ranking change.
    """
    if value is None:
        return DEFAULT_CONFIDENCE
    try:
        confidence = float(value)
    except (TypeError, ValueError) as exc:
        raise InvalidArgumentError(f"{CONFIDENCE_FIELD} must be a number, got {value!r}") from exc
    if not math.isfinite(confidence):
        raise InvalidArgumentError(f"{CONFIDENCE_FIELD} must be a finite number")
    if confidence < MIN_CONFIDENCE or confidence > MAX_CONFIDENCE:
        raise InvalidArgumentError(
            f"{CONFIDENCE_FIELD} must be within "
            f"[{MIN_CONFIDENCE}, {MAX_CONFIDENCE}], got {confidence}"
        )
    return confidence


def coerce_confidence_for_read(value: Any) -> float:
    """Coerce a stored confidence value into the legal range.

    Never raises: one bad record must not fail an entire retrieval. Missing,
    unparsable and non-finite values fall back to ``DEFAULT_CONFIDENCE``;
    out-of-range values are clamped.
    """
    if value is None:
        return DEFAULT_CONFIDENCE
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return DEFAULT_CONFIDENCE
    if not math.isfinite(confidence):
        return DEFAULT_CONFIDENCE
    return min(MAX_CONFIDENCE, max(MIN_CONFIDENCE, confidence))


def confidence_factor(confidence: float, penalty_lambda: float) -> float:
    """Bounded discount factor for a confidence value.

    ``factor = 1 - penalty_lambda * (1 - confidence)``, so the factor stays in
    ``[1 - penalty_lambda, 1]``. A confidence of exactly ``1.0`` yields exactly
    ``1.0``, which keeps unannotated records bit-identical to their pre-change
    scores.
    """
    return 1.0 - penalty_lambda * (1.0 - confidence)
