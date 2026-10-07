# Benchmarks — the eval ruler

You cannot improve what you cannot measure. This folder is the **ground truth** `/audit` is scored against. Build it *before* tuning anything (M0), and keep a held-out slice you never tune on.

## How it works
Each benchmark is a folder with the target contract(s) and a `truth.yaml` describing the **real** vulnerabilities present (and the things that look buggy but aren't). After running `/audit` on the target, score the output:

- **True positive (TP):** a reported finding that matches a `findings[]` entry.
- **False negative (FN):** a `must_find: true` entry the audit missed. (hurts **recall**)
- **False positive (FP):** a reported finding not in `findings[]` and not excused by `known_non_issues[]`. (hurts **precision** — the metric that matters most)

`precision = TP / (TP + FP)` · `recall = TP / (TP + FN)`

**Primary gate (ROADMAP §7):** precision ≥ ~70% before trusting output. Secondary: recall of known Highs/Criticals.

## Sources (licensing first — see ROADMAP §5)
- **Damn Vulnerable DeFi** — teaching challenges, clean known bugs. Good for the first entries.
- **DeFiHackLabs** (MIT) — real incidents with Foundry PoCs; normalize into `truth.yaml`.
- **Custom** — minimized repros you write.

Log each source + license in `SOURCES.md` (create at repo root when you ingest the first external target).

## Adding a benchmark
1. `mkdir benchmarks/<name>/` and add the contract(s).
2. Copy `TEMPLATE.truth.yaml` → `benchmarks/<name>/truth.yaml` and fill it.
3. Run `/audit benchmarks/<name>/` and score by hand (M0). An automated scorer comes later.

See `examples/erc4626-first-depositor/truth.yaml` for a worked example.
