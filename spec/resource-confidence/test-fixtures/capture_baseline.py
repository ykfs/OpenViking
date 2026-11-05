#!/usr/bin/env python3
"""Capture the pre-change ranking baseline used by the zero-regression case.

``TC-31`` proves that records without an annotation keep exactly the score and
order they had before this change. That comparison needs a baseline captured
from the **unmodified** revision, so this script materialises a git worktree at
a pre-change revision, runs the same queries there and in the working tree, and
diffs the two result sets.

Run it before the change lands (or pass ``--baseline-rev`` to any revision that
still predates it)::

    python spec/resource-confidence/test-fixtures/capture_baseline.py \
        --repo /path/to/OpenViking \
        --queries queries.json \
        --baseline-rev HEAD

Each recorded result is written as ``{"query": ..., "items": [{"uri", "score"}]}``
and the diff is reported per query. A non-zero difference means a regression.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = r"""
import asyncio, json, sys
sys.path.insert(0, ".")
from openviking.retrieve.hierarchical_retriever import HierarchicalRetriever

async def main(queries_path, out_path):
    queries = json.loads(open(queries_path, encoding="utf-8").read())
    retriever = HierarchicalRetriever.from_config() if hasattr(HierarchicalRetriever, "from_config") else None
    if retriever is None:
        raise SystemExit(
            "HierarchicalRetriever has no from_config(); wire this script to the "
            "project's retrieval entry point (see spec design C10) before use."
        )
    recorded = []
    for query in queries:
        result = await retriever.retrieve(query=query, limit=20)
        recorded.append(
            {
                "query": query,
                "items": [
                    {"uri": m.uri, "score": m.raw_score} for m in result.matched_contexts
                ],
            }
        )
    open(out_path, "w", encoding="utf-8").write(json.dumps(recorded, indent=2))

asyncio.run(main(sys.argv[1], sys.argv[2]))
"""


def _run_capture(repo: Path, queries: Path, out: Path) -> None:
    script = repo / "_capture_baseline_tmp.py"
    script.write_text(SCRIPT, encoding="utf-8")
    try:
        subprocess.run(
            [sys.executable, str(script), str(queries), str(out)],
            cwd=repo,
            check=True,
        )
    finally:
        script.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--queries", type=Path, required=True)
    parser.add_argument("--baseline-rev", default="HEAD")
    parser.add_argument("--out", type=Path, default=Path("baseline-before.json"))
    parser.add_argument("--after", type=Path, default=Path("baseline-after.json"))
    args = parser.parse_args()

    repo = args.repo.resolve()
    worktree = Path(tempfile.mkdtemp(prefix="ov-baseline-"))
    subprocess.run(
        ["git", "worktree", "add", "--detach", str(worktree), args.baseline_rev],
        cwd=repo,
        check=True,
    )
    try:
        _run_capture(worktree, args.queries.resolve(), args.out.resolve())
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(worktree)], cwd=repo)

    _run_capture(repo, args.queries.resolve(), args.after.resolve())

    before = json.loads(args.out.read_text(encoding="utf-8"))
    after = json.loads(args.after.read_text(encoding="utf-8"))
    failures = []
    for left, right in zip(before, after):
        if left != right:
            failures.append((left["query"], left["items"], right["items"]))

    if not failures:
        print(f"OK: {len(before)} queries match the pre-change baseline exactly.")
        return
    for query, expected, actual in failures:
        print(f"MISMATCH for {query!r}")
        print(f"  before: {expected}")
        print(f"  after : {actual}")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
