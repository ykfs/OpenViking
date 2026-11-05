# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: AGPL-3.0
"""Unit tests for confidence in the portable (backup/migration) field sets.

The three sets are independent: export projection, the import recompute write
allow-list, and the namespace migration projection. Missing any one silently
drops confidence on that path.
"""

from openviking.storage.ovpack.index import (
    EXPORT_VECTOR_FIELDS,
    PORTABLE_VECTOR_SCALAR_FIELDS,
    portable_scalars,
)
from openviking.storage.vector_migration import VECTOR_MIGRATION_OUTPUT_FIELDS
from openviking.utils.embedding_utils import _PORTABLE_SCALAR_FIELDS


def test_ovpack_export_fields_include_confidence():
    assert "confidence" in PORTABLE_VECTOR_SCALAR_FIELDS


def test_ovpack_export_fields_derived_list_includes_confidence():
    """EXPORT_VECTOR_FIELDS is derived from the portable scalars, so it follows."""
    assert "confidence" in EXPORT_VECTOR_FIELDS


def test_portable_scalar_fields_include_confidence():
    """The import recompute allow-list is a separate set from the export one."""
    assert "confidence" in _PORTABLE_SCALAR_FIELDS


def test_vector_migration_output_fields_include_confidence():
    assert "confidence" in VECTOR_MIGRATION_OUTPUT_FIELDS


def test_portable_scalars_copies_confidence_from_record():
    """End to end: an exported record carries the annotation into the package."""
    scalars = portable_scalars(
        {"uri": "viking://resources/a", "level": 2, "confidence": 0.4, "abstract": "x"}
    )

    assert scalars["confidence"] == 0.4
    assert "uri" not in scalars
