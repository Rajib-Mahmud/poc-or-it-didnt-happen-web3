# CLAUDE.md — Web3 Security Thinking Framework

This project is a **thinking framework** (not an automation) that amplifies security-research reasoning on
**Web3 / EVM smart-contract** code. It runs inside the coding agent — here, Claude Code.

## When asked to audit / review Web3 code (or on `/audit <scope>`)
0. **If a `scope.md` is present, read it first** — it defines in-scope assets, severity bar, PoC requirement, known issues, and rules of engagement; obey it (test/report only what it allows).
1. Follow **`FRAMEWORK.md`** (the method) and the `audit` skill in `.claude/skills/audit/SKILL.md`.
2. Knowledge base: `knowledge/taxonomy.md`, `knowledge/invariants.md`, `knowledge/formulas.md`.
3. Retrieve relevant patterns for the target type via `memory/INDEX.md` → `memory/patterns.md`.
4. Full stage spec: `PIPELINE.md`.

## Principles
- Investigation generation, not answer generation: generate hypotheses from **every angle/corner**, then prove or kill each.
- Precision is the moat: rule out mitigations; every High/Critical needs a **runnable PoC** or it's downgraded; non-exploitable → Informational.
- **Web3 only** (web2/API/browser out of scope). No "100%." Authorized targets only.

## Repo map
- `FRAMEWORK.md` — the framework (start here) · `PIPELINE.md` — stage spec
- `knowledge/` — taxonomy · invariants · formulas · `memory/` — reusable research patterns + retrieval
- `benchmarks/` — the eval "ruler" (blind-run scores in `benchmarks/RESULTS.md`)
- `engine/`, `ingest/` — **optional** dev tooling (benchmark harness + corpus ingester), not the framework
