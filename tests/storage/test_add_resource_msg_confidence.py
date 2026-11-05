# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: AGPL-3.0
"""Unit tests for confidence on the add-resource queue message."""

from openviking.storage.queuefs.add_resource_msg import AddResourceMsg

_BASE = {
    "task_id": "task-1",
    "path": "/tmp/source",
    "root_uri": "viking://resources/sample",
    "account_id": "default",
    "user_id": "default",
    "role": "root",
}


def test_add_resource_msg_round_trip_confidence():
    """Given a confidence value, the message survives a dict round trip."""
    msg = AddResourceMsg(confidence=0.4, **_BASE)

    assert msg.to_dict()["confidence"] == 0.4
    assert AddResourceMsg.from_dict(msg.to_dict()).confidence == 0.4


def test_add_resource_msg_legacy_payload_defaults_to_none():
    """An older queued payload without the key restores as None, not an error."""
    payload = dict(AddResourceMsg(confidence=0.4, **_BASE).to_dict())
    payload.pop("confidence")

    assert AddResourceMsg.from_dict(payload).confidence is None


def test_add_resource_msg_rejects_non_numeric_confidence():
    """A malformed queued value degrades to None instead of raising."""
    payload = AddResourceMsg(confidence=0.4, **_BASE).to_dict()
    payload["confidence"] = "abc"

    assert AddResourceMsg.from_dict(payload).confidence is None

    payload["confidence"] = True
    assert AddResourceMsg.from_dict(payload).confidence is None
