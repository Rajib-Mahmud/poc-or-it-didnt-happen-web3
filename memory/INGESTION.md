# Security Memory — ingestion (how we reach "thousands", honestly)

The corpus is **not** hand-written to thousands (that produces low-quality noise and kills precision). Instead, licensed sources are ingested, normalized into `exploit_case` records, and their reusable reasoning distilled into `research_pattern`s. "Thousands" = running this pipeline, not typing.

## Sources (licensing first — see ROADMAP §5)
| Source | What | License | Priority |
|---|---|---|---|
| **DeFiHackLabs** | hundreds of real incidents with Foundry PoCs + root causes | MIT (verify) | **first** |
| **Code4rena / Sherlock reports** | thousands of findings incl. invalid/duplicate (FP calibration) | public per-repo (check) | second |
| **GHSA / OSV** | structured advisories + patches | open | second |
| **Rekt / incident writeups** | narrative root causes | varies — link, don't copy | enrichment |

Record each source + license + ingest date in a repo-root `SOURCES.md` at first ingest.

## Pipeline
```
raw source (PoC / report / advisory)
      ↓  extract
exploit_case  (root cause, attack path, prerequisites, impact, poc_ref, fix_ref, source, license)
      ↓  distill (cluster by root cause)
research_pattern  (observation → … → generalization + detection_questions)   [dedup against existing]
      ↓  index
embedding + tag index  (replaces the hand INDEX.md at scale)
      ↓
retrieval at audit time (target type → top-k relevant records)
```

## Distillation rule (quality gate)
- Many incidents → **one** `research_pattern` when they share a root cause (dedup; don't store 50 near-duplicates).
- Keep the invalid/duplicate findings from Code4rena/Sherlock specifically as **false-positive calibration** (what *looks* like a bug but was rejected, and why).

## Stub (to implement)
`scripts/ingest_defihacklabs.py` (planned):
1. clone/pull DeFiHackLabs (MIT); iterate PoC test files.
2. parse title/root-cause/links → `exploit_case` YAML under `memory/cases/`.
3. cluster by root cause → draft/extend `research_pattern`s (human-reviewed before promotion).
4. rebuild the tag/embedding index.

Status: **not yet run.** Seed corpus (`patterns.md`) is live; this is the path to scale.
