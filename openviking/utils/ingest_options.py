# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: AGPL-3.0
"""Options carried with content as it enters downstream processing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional

from openviking.utils.tags import normalize_search_tags


@dataclass(frozen=True)
class IngestOptions:
    """Small, serializable options shared across processing stages.

    This is not limited to resource imports. It may be used by any producer
    that submits content into summarization, semantic indexing, or vector
    writing pipelines. Do not put request identity, locks, telemetry collectors,
    or large source payloads here.
    """

    search_tags: Optional[list[str]] = None
    search_tag_mode: str = "replace"
    # Human-assigned confidence for the content being ingested. ``None`` means
    # "this call carries no confidence", so a partial update leaves any existing
    # value untouched. Callers that own the value (the add-resource request path)
    # always pass it explicitly, including the 1.0 default, so re-importing a
    # resource resets it. Rewrite and re-index paths leave it unset.
    confidence: Optional[float] = None

    @classmethod
    def from_search_tags(
        cls,
        tags: Iterable[str] | None,
        *,
        mode: str = "replace",
    ) -> "IngestOptions":
        if tags is None:
            return cls()
        return cls(
            search_tags=normalize_search_tags(tags, discard_invalid=True),
            search_tag_mode=mode,
        )

    @classmethod
    def from_value(cls, value: "IngestOptions | Mapping[str, Any] | None") -> "IngestOptions":
        if value is None:
            return cls()
        if isinstance(value, IngestOptions):
            return value
        return cls(
            search_tags=(
                list(value.get("search_tags") or [])
                if value.get("search_tags") is not None
                else None
            ),
            search_tag_mode=str(value.get("search_tag_mode", "replace")),
            confidence=value.get("confidence"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "search_tags": list(self.search_tags) if self.search_tags is not None else None,
            "search_tag_mode": self.search_tag_mode,
            "confidence": self.confidence,
        }
