# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: AGPL-3.0
"""Unit tests for confidence at the resource-service request boundary.

The three neighbouring entry points have distinct responsibilities, and mixing
them up silently resets human annotations on scheduled refreshes:

* ``add_resource`` resolves the default and is the only place that does so.
* ``_submit_resource_ingestion`` forwards whatever it is given, unchanged.
* ``refresh_resource`` never carries a confidence at all.
"""

import inspect

import pytest

from openviking.service.resource_service import (
    _ADD_RESOURCE_ARGS_RESERVED_FIELDS,
    ResourceService,
)
from openviking_cli.exceptions import InvalidArgumentError


def _service() -> ResourceService:
    return ResourceService.__new__(ResourceService)


def test_reserved_fields_reject_confidence_in_args():
    """The core parameter must not be smuggled through generic parser args."""
    assert "confidence" in _ADD_RESOURCE_ARGS_RESERVED_FIELDS


def test_gate_returns_empty_when_nothing_supplied():
    """Without tags or confidence the gate keeps its original behaviour."""
    assert (
        _service()._add_resource_ingest_options(tags=None, tag_mode="replace", confidence=None)
        == {}
    )


def test_gate_builds_ingest_options_without_tags():
    """A confidence-only import must still produce ingest options."""
    result = _service()._add_resource_ingest_options(tags=None, tag_mode="replace", confidence=0.4)

    assert result["ingest_options"].confidence == 0.4
    assert result["ingest_options"].search_tags is None


def test_submit_and_refresh_signatures_are_asymmetrical():
    """Refresh must not carry confidence, or it would reset an annotation."""
    submit = inspect.signature(ResourceService._submit_resource_ingestion)
    refresh = inspect.signature(ResourceService.refresh_resource)
    add = inspect.signature(ResourceService.add_resource)

    assert "confidence" in add.parameters
    assert "confidence" in submit.parameters
    assert "confidence" not in refresh.parameters


@pytest.mark.asyncio
async def test_add_resource_normalizes_and_forwards_confidence(monkeypatch):
    """Given a value, the resolved float reaches the ingestion pipeline."""
    service = _service()
    captured = {}

    async def _fake_submit(**kwargs):
        captured.update(kwargs)
        return {"status": "ok"}

    monkeypatch.setattr(service, "_submit_resource_ingestion", _fake_submit)

    await service.add_resource(path="/tmp/x", ctx=object(), confidence=0.6)

    assert captured["confidence"] == 0.6


@pytest.mark.asyncio
async def test_add_resource_defaults_confidence_to_one(monkeypatch):
    """An omitted value is resolved to 1.0 before it leaves the request path."""
    service = _service()
    captured = {}

    async def _fake_submit(**kwargs):
        captured.update(kwargs)
        return {"status": "ok"}

    monkeypatch.setattr(service, "_submit_resource_ingestion", _fake_submit)

    await service.add_resource(path="/tmp/x", ctx=object())

    assert captured["confidence"] == 1.0


@pytest.mark.asyncio
async def test_add_resource_rejects_out_of_range_without_submitting(monkeypatch):
    """An out-of-range value fails before anything is enqueued."""
    service = _service()
    calls = []

    async def _fake_submit(**kwargs):
        calls.append(kwargs)
        return {"status": "ok"}

    monkeypatch.setattr(service, "_submit_resource_ingestion", _fake_submit)

    with pytest.raises(InvalidArgumentError, match="confidence"):
        await service.add_resource(path="/tmp/x", ctx=object(), confidence=1.2)

    assert calls == []
