# Web3 Security Thinking Framework

**A thinking framework, not an automation.** Loaded into any coding agent — **Claude Code, Codex, opencode, or DeepSeek** — it amplifies how the agent *reasons* about Web3 / smart-contract security: generate hypotheses from every angle and corner, then prove or kill each one. Precision-first — optimized to **reject non-bugs**, not just find them.

> Start here: **[FRAMEWORK.md](FRAMEWORK.md)** · plan: [ROADMAP.md](ROADMAP.md) · stage spec: [PIPELINE.md](PIPELINE.md)

## Use it in your agent (host-agnostic)
- **Claude Code** — `CLAUDE.md` + the `/audit` skill auto-load the framework, knowledge, and memory.
- **Codex / opencode** (any backend model, incl. **DeepSeek**) — `AGENTS.md` points the agent to it.
- **Any chat (DeepSeek, …)** — paste `FRAMEWORK.md` as the system prompt, then the target code. No keys, no install.

*(`engine/` + `ingest/` are optional dev tooling — a benchmark harness and corpus ingester — not part of the framework.)*

## Current status
- **M0 (foundations + eval ruler): done** — knowledge files, benchmark, `/audit` skill.
- **M0.5 (blind validation): done** — 3 targets, Precision/Recall 100%, 0 FP on a clean control (`benchmarks/RESULTS.md`).
- **System skeleton: in place** — Web3-only engine spec (`PIPELINE.md`), Security Memory (`memory/`) with a curated seed + a real ingestion path to thousands.
- **Engine: runnable (code-complete)** — `python -m engine.cli selftest` passes offline (dry). Real audits need a provider API key; PoC execution needs `forge`; thousands of cases need `ingest --run`.
- **Still ahead:** scaled corpus (ingestion), embeddings retrieval, multi-model committee, automated PoC execution, broad benchmark. These are real, not done — see `ROADMAP.md`.

## Structure
```
.
├── ROADMAP.md                         # milestone plan (+ v2 vision/architecture addendum)
├── PIPELINE.md                        # model-agnostic engine spec (the portable "intelligence")
├── README.md
├── .claude/skills/audit/SKILL.md      # Claude Code adapter — Web3-only /audit skill
├── knowledge/                         # static reference (hand-written, cheap, high-value)
│   ├── taxonomy.md                    # bug-class taxonomy
│   ├── invariants.md                  # protocol invariant library
│   └── formulas.md                    # protocol math + where it breaks
├── memory/                            # Security Memory (retrieval corpus)
│   ├── SCHEMA.md                      # research_pattern + exploit_case schemas
│   ├── patterns.md                    # curated seed of reusable reasoning patterns
│   ├── INDEX.md                       # target type → relevant patterns (retrieval)
│   └── INGESTION.md                   # honest path to scale to thousands (DeFiHackLabs, …)
├── engine/                            # runnable model-agnostic core: providers (Claude/
│                                      #   DeepSeek/Codex), retrieval, committee, pipeline,
│                                      #   PoC harness, scorer, CLI  (python -m engine.cli)
├── ingest/                            # DeFiHackLabs ingester (scale corpus to thousands)
└── benchmarks/                        # the "ruler": targets + ground truth + results
    ├── README.md
    ├── TEMPLATE.truth.yaml
    ├── RESULTS.md                     # blind-run leaderboard
    └── examples/                      # erc4626-first-depositor · safe-vault · subtle-rounding
```

**Engine vs adapter:** `PIPELINE.md` + `knowledge/` + `memory/` + `benchmarks/` are the model-neutral *engine*; the Claude Code skill is one *adapter* (DeepSeek / Codex runners planned). Web3 / EVM smart contracts only.

## Principles (non-negotiable)
1. **Precision > recall.** A finding you can't defend is worse than a miss.
2. **Prove it or reject it.** Every candidate runs an adversarial self-check; Highs/Criticals need an exploit path (and later a Foundry PoC).
3. **Quality corpus over volume.** 300–800 deeply-normalized cases beat 100k shallow ones.
4. **The model is not a blank slate.** Knowledge files + (later) retrieval add grounding, recency, and false-positive calibration — not basic bug knowledge.

## Using `/audit` (target state)
`/audit <path>` → recon → architecture map → invariant extraction → attack-surface mapping → hypothesis generation → adversarial self-check → structured report.

**M0 reality:** reasoning-only. Measure it against `benchmarks/` and record the baseline that every later change must beat.
