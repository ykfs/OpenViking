#!/usr/bin/env python3
"""Generate the hand-run test fixtures for the resource-confidence change.

Creates the source directories, the manifest, and the fixed-score pair data that
the manual integration / performance / regression cases in ``tasks.md`` refer to.

Usage::

    python spec/resource-confidence/test-fixtures/generate_fixtures.py [--out DIR]

The generated tree is idempotent: re-running overwrites the fixtures with the
same content.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Pairs with fixed unweighted scores, used to prove the discount band. Each pair
# records the two records and the order they must come back in.
FIXED_SCORE_PAIRS = [
    {
        "id": "user-sample-1",
        "case": "TC-09",
        "why": "A 0.90 match discounted to half must still outrank a 0.46 match.",
        "records": [
            {"uri": "viking://resources/pairs/X", "raw_score": 0.90, "confidence": 0.5},
            {"uri": "viking://resources/pairs/Y", "raw_score": 0.46, "confidence": 1.0},
        ],
        "expected_order": ["X", "Y"],
        "expected_weighted": {"X": 0.81, "Y": 0.46},
    },
    {
        "id": "user-sample-2",
        "case": "TC-10",
        "why": "Within the discount band the trusted record moves ahead.",
        "records": [
            {"uri": "viking://resources/pairs/P", "raw_score": 0.50, "confidence": 0.5},
            {"uri": "viking://resources/pairs/Q", "raw_score": 0.46, "confidence": 1.0},
        ],
        "expected_order": ["Q", "P"],
        "expected_weighted": {"P": 0.45, "Q": 0.46},
    },
    {
        "id": "boundary-inside",
        "case": "TC-11",
        "why": "A 19% unweighted gap is inside the 20% band, so the order swaps.",
        "records": [
            {"uri": "viking://resources/pairs/A1", "raw_score": 0.50, "confidence": 0.0},
            {"uri": "viking://resources/pairs/B1", "raw_score": 0.405, "confidence": 1.0},
        ],
        "expected_order": ["B1", "A1"],
        "expected_weighted": {"A1": 0.40, "B1": 0.405},
    },
    {
        "id": "boundary-outside",
        "case": "TC-12",
        "why": "A 21% unweighted gap is outside the band, so the order holds.",
        "records": [
            {"uri": "viking://resources/pairs/A2", "raw_score": 0.50, "confidence": 0.0},
            {"uri": "viking://resources/pairs/B2", "raw_score": 0.395, "confidence": 1.0},
        ],
        "expected_order": ["A2", "B2"],
        "expected_weighted": {"A2": 0.40, "B2": 0.395},
    },
    {
        "id": "threshold-split",
        "case": "TC-13",
        "why": "Gating uses the unweighted score; A survives, B does not.",
        "score_threshold": 0.35,
        "records": [
            {"uri": "viking://resources/pairs/A3", "raw_score": 0.42, "confidence": 0.0},
            {"uri": "viking://resources/pairs/B3", "raw_score": 0.21, "confidence": 1.0},
        ],
        "expected_order": ["A3"],
        "expected_weighted": {"A3": 0.336},
    },
]

# Values written straight into the collection, bypassing write-side validation.
DIRTY_RECORDS = [
    {
        "uri": "viking://resources/dirty/over-range",
        "confidence": 1.5,
        "why": "TC-35: the read side must clamp this to 1.0, never boost the score.",
    }
]

MINIMAL_MANIFEST = {
    "version": 1,
    "resources": [
        {"path": "conf-high", "to": "viking://resources/conf-high"},
    ],
}


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def generate(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)

    # Source folders. conf-high and conf-low are deliberately close in wording so
    # that they land in the same score band and the confidence discount decides.
    for name, body_topic in (("conf-high", "release checklist"), ("conf-low", "release checklist")):
        for index in range(1, 4):
            _write_text(
                out / name / f"doc-{index}.md",
                f"# {body_topic} {index}\n\n"
                f"The {body_topic} covers rollout steps, rollback steps and owners.\n",
            )

    # Two five-file folders for the granularity case (TC-41).
    for name in ("granularity-a", "granularity-b"):
        for index in range(1, 6):
            _write_text(
                out / name / f"note-{index}.md",
                f"# {name} note {index}\n\nBody for granularity fixture {index}.\n",
            )

    # A read-back comparison set that must score exactly like the imported one.
    _write_text(
        out / "conf-high-group" / "doc-1.md",
        "# release checklist 1\n\nThe release checklist covers rollout steps, rollback steps and owners.\n",
    )

    (out / "manifest-min.json").write_text(
        json.dumps(MINIMAL_MANIFEST, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (out / "fixed-score-pairs.json").write_text(
        json.dumps(FIXED_SCORE_PAIRS, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (out / "dirty-records.json").write_text(
        json.dumps(DIRTY_RECORDS, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"fixtures written to {out}")
    for item in sorted(out.rglob("*")):
        if item.is_file():
            print(f"  {item.relative_to(out)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "data")
    args = parser.parse_args()
    generate(args.out.resolve())


if __name__ == "__main__":
    main()
