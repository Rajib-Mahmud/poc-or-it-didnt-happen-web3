"""Scale the Security Memory to thousands of real cases from DeFiHackLabs (MIT).

This is the honest path to "thousands": clone the licensed source, discover incident PoCs,
and write one `exploit_case` stub per incident under memory/cases/. Deeper per-case
normalization (root cause, attack path, generalized_pattern link) is the reviewed follow-up.

Usage:
    python -m engine.cli ingest           # dry: explain + show plan, clone nothing
    python -m engine.cli ingest --run     # actually shallow-clone and index (needs git + network)
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = "https://github.com/SunWeb3Sec/DeFiHackLabs"
LICENSE = "MIT (verify the current LICENSE before relying on it)"


def ingest(repo_root: str, run: bool = False) -> int:
    cache = Path(repo_root) / ".cache" / "DeFiHackLabs"
    cases_dir = Path(repo_root) / "memory" / "cases"

    if not run:
        print("DeFiHackLabs ingestion plan (dry - nothing cloned):")
        print(f"  source : {REPO}")
        print(f"  license: {LICENSE}")
        print(f"  would shallow-clone to: {cache}")
        print(f"  would write exploit_case stubs to: {cases_dir}")
        print("  then: cluster by root cause -> research_patterns (human-reviewed before promotion)")
        print("Run with --run to execute (requires git + network).")
        return 0

    cache.parent.mkdir(parents=True, exist_ok=True)
    if not cache.exists():
        print(f"shallow-cloning {REPO} ...")
        r = subprocess.run(["git", "clone", "--depth", "1", REPO, str(cache)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("clone failed:\n" + r.stderr)
            return 1

    # Discover incident PoC test files (DeFiHackLabs keeps them under src/test/**/*.sol).
    sols = list((cache / "src").rglob("*.sol")) if (cache / "src").exists() else list(cache.rglob("*_exp.sol"))
    cases_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    index_lines = ["# Security Memory — ingested cases (DeFiHackLabs)\n",
                   f"source: {REPO}\nlicense: {LICENSE}\n"]
    for sol in sols:
        name = re.sub(r"[_\-]?exp$", "", sol.stem)
        slug = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower()
        if not slug:
            continue
        stub = (cases_dir / f"{slug}.yaml")
        if not stub.exists():
            stub.write_text(
                f"exploit_case:\n  id: E-{slug}\n  name: \"{name}\"\n  source: DeFiHackLabs\n"
                f"  license: MIT\n  poc_ref: \"{sol.relative_to(cache).as_posix()}\"\n"
                f"  root_cause: \"TODO: normalize\"\n  generalized_pattern: \"TODO: link to P*\"\n",
                encoding="utf-8",
            )
            written += 1
        index_lines.append(f"- E-{slug}: {sol.relative_to(cache).as_posix()}")

    (cases_dir / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"discovered {len(sols)} PoC files; wrote {written} new case stubs to {cases_dir}")
    print("next: normalize root_cause + link generalized_pattern (reviewed), then rebuild retrieval index")
    return 0
