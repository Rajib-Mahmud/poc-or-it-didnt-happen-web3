# Web3 Security Intelligence Engine — Realistic Roadmap

> A pressure-tested rewrite of the original 17-phase plan.
> The vision is kept; the **sequencing, scope, and success criteria** are changed so value ships early and the project doesn't die in a data-engineering swamp.

---

## TL;DR — the three changes that matter

1. **An extension does not train a model.** A Claude Code skill is *prompt + retrieval (RAG) + orchestration + tooling (Foundry)*. The corpus feeds retrieval and few-shot examples, **not weights**. There is no fine-tuning step. This collapses most of "Phase 1–9 as training data" into "a retrieval index + a prompt library."

2. **Precision is the product, not recall.** Any strong LLM will emit 50 "findings," most of them wrong. A professional audit tool is defined by its ability to **reject non-bugs** and **prove the real ones with executable PoCs**. So adversarial validation + Foundry PoC (original Phases 12–13) are the *core*, and they move **early**, not late.

3. **Build vertical slices, not horizontal layers.** Ship a working `/audit` in weeks, deepen iteratively. Do **not** build the full corpus / knowledge graph / multi-agent mesh before producing a single audit.

### Milestone map

| Milestone | Time | Outcome (exit criteria) | Replaces phases |
|---|---|---|---|
| **M0 — Foundations + eval ruler** | Week 1 | A benchmark of known-vulnerable contracts with ground-truth findings; hand-written taxonomy; skeleton `/audit` that runs on 1 contract | 0, 5, (13 start) |
| **M1 — Vertical slice** | Weeks 2–3 | `/audit <scope>` → recon → architecture → invariants → attack-surface hypotheses → structured report (no PoC yet), measured on the benchmark | 11-lite, 16-lite, 17, 5, 6, 7 |
| **M2 — Precision layer** ⭐ | Weeks 4–6 | Adversarial false-positive agent + **Foundry PoC generation** + confidence scoring. FP rate drops measurably | 12, 13, 14 |
| **M3 — Grounding corpus v1** | Weeks 7–9 | DeFiHackLabs normalized + flat vector retrieval by target type; "historical analogues" in reports | 1, 8, 10-lite, 9-part |
| **M4 — Calibration corpus** | Weeks 10–12 | Curated *invalid / duplicate / known-issue* findings used to tune the FP agent + dedup clustering | 2, 4, 15 |
| **M5 — Scale + orchestration** | Quarter 2 | Multi-agent pipeline (only if the monolith breaks), GitHub patch intel, knowledge graph (only if flat retrieval is insufficient), corpus scale-up | 3, 7, 9-full, 11-full |

---

## 1. Pressure test — what's right, what changes, what to cut

### ✅ Keep as-is (these are genuinely good)
- **Core principle:** *knowledge → hypotheses; target code + execution evidence → real vulnerabilities.* This is exactly right and should be the project's north star.
- **Report format (Phase 17).** Keep every field. "Why this is not informative," "why this is not a duplicate," broken-invariant, before/after state — this is what makes a finding *defensible*. This is a differentiator.
- **"Quality over quantity" data rule.** 300–800 *deeply normalized* cases beat 100k shallow ones. Lean into this even harder than the original plan.
- **"Teach rejection, not just detection"** (keep invalid/duplicate findings). This is the single best insight in the plan — but it belongs in M4 as **calibration data for the FP agent**, operationalized, not as generic corpus.
- **Researcher-reasoning normalization (Phase 4).** Valuable — but as **few-shot reasoning exemplars** injected at inference, not as a training set.

### 🔀 Resequence (same ideas, different order)
| Original | Problem | New home |
|---|---|---|
| Eval/benchmark at **Phase 13** | You cannot improve what you cannot measure. Every change is a guess until there's a ruler. | **M0** — first thing built |
| Validation + PoC at **Phases 12–13** (late) | This *is* the product. Everything upstream generates noise; this is what turns noise into signal. | **M2** — the core milestone |
| Corpus/knowledge at **Phases 1–9** (first) | Months of data work before any working audit → high abandonment risk. | **M3–M4** — *after* a working, measured tool |
| Multi-agent mesh at **Phase 11** (start) | Premature. Orchestration overhead with no proven single-agent baseline. | **M5** — only when a monolithic skill hits real limits |

### ✂️ Cut or defer (YAGNI until proven necessary)
- **Knowledge graph (Phase 9) as a first-class system.** Start with flat vector search + metadata filters (target type, bug class, protocol). A graph is a lot of engineering for marginal early benefit. Add only if retrieval quality demonstrably stalls.
- **100k-document ambitions.** Explicitly out of scope. The plan already says this; the roadmap enforces it.
- **Custom embeddings / fine-tuning.** Out. Use an off-the-shelf embedding API.
- **Large-scale scraping of Solodit / Immunefi.** Defer until licensing is cleared (see §5). Start **MIT-licensed sources only**.
- **Separate Architecture/Economic/Security agents early.** Fold into one well-prompted analysis pass first; split later if context or quality demands it.

---

## 2. The reframings, explained (the "why")

**The model is not a blank slate.** Reentrancy, oracle manipulation, ERC-4626 share inflation, first-depositor, bridge replay, delegatecall storage collisions — a strong base model already knows these patterns. So the corpus's *marginal* value is narrow and specific:
- **Grounding / evidence** — cite a real incident so the model isn't hallucinating a mechanism.
- **Recency** — exploits after the model's training cutoff.
- **Target-specific retrieval** — pull the 10 most relevant historical cases for *this* contract.
- **Calibration** — real examples of findings that were judged *invalid / duplicate / known*, to suppress false positives.

Scope the corpus to those four things. Do **not** try to "teach the model all of Web3." That work is mostly already done; you'd be paying to re-derive what the base model has.

**Why precision dominates.** On a real audit scope, an eager LLM produces dozens of plausible-sounding findings. If 80% are false positives, the tool is worse than useless — it wastes the human's scarcest resource (review attention) and destroys trust. The entire engineering budget should bend toward: *prove it with a PoC, or disprove it, or downgrade it.* Execution (Foundry fork tests) is the only reliable arbiter.

**Honest expectation setting.** The realistic near-term product is **a strong assistant that generates well-grounded, PoC-backed hypotheses for a human auditor** — not an autonomous auditor that replaces Code4rena wardens. LLMs are strongest on *pattern* bugs and weakest on *novel economic/logic* bugs, which is exactly where the money is. Plan for human-in-the-loop; aim to make the human 3–5× faster, not to remove them.

---

## 3. Milestones in detail

### M0 — Foundations + the eval ruler (Week 1)
**Goal:** a way to measure quality before building quality.
- Repo skeleton + stack decision (see §4).
- **Benchmark v0:** 8–12 known-vulnerable contracts with ground-truth finding sets. Sources: Damn Vulnerable DeFi (teaching set) + a handful of DeFiHackLabs PoCs (real incidents). Store ground truth as YAML (`benchmarks/<name>/truth.yaml`).
- **Taxonomy + invariant + formula libraries (Phases 5, 6, 7)** — hand-written as plain markdown/JSON knowledge files in-repo. These are cheap, high-value, and need no scraping. (The original plan over-sizes these as major phases; they're a day or two of writing each.)
- Skeleton `/audit` skill that ingests one contract and emits *something* structured.
- **Exit:** you can run `/audit` on a benchmark contract and score its output against `truth.yaml` by hand.

### M1 — Vertical slice: `/audit` end to end (Weeks 2–3)
**Goal:** a working audit with no corpus and no PoC — pure reasoning + static knowledge files.
- Pipeline: **recon → architecture map → invariant extraction → attack-surface mapping → hypothesis generation → structured report** (report = Phase 17 format).
- Powered by the base model + the M0 knowledge files. No retrieval yet.
- **Exit:** on the benchmark, the report catches the "obvious" known criticals/highs. Record precision/recall as the baseline all later work must beat.

### M2 — Precision layer ⭐ (Weeks 4–6) — the core milestone
**Goal:** turn noisy hypotheses into defensible, PoC-backed findings.
- **Adversarial false-positive agent (Phase 12):** for each candidate, actively try to kill it — intended behavior? access-controlled? reachable? already mitigated? economic assumption holds? If it survives, it's a finding.
- **Foundry PoC generation (Phase 13):** for surviving High/Critical candidates, scaffold a fork/unit test that *proves* the exploit (before/after state, profit, invariant violation). Execution is ground truth.
- **Confidence scoring (Phase 14):** exploitability / reachability / invariant / impact / PoC / FP-check.
- **Exit:** measurable FP-rate drop vs. M1; every High/Critical ships with a passing Foundry PoC or is auto-downgraded.

### M3 — Grounding corpus v1 (Weeks 7–9)
**Goal:** add historical grounding — now that there's a tool worth grounding.
- Ingest **DeFiHackLabs** (MIT): normalize each incident into `{root_cause, attack_path, primitive, poc_ref, fix, generalized_pattern}` (Phases 1, 8).
- **Flat retrieval (Phase 10-lite):** embed cases; retrieve by target type (ERC-4626 → vault/inflation/donation cases; bridge → replay/nonce/chain-id cases). SQLite + a vector extension or LanceDB — keep it light.
- Inject retrieved cases as few-shot context + populate the report's "Historical Analogues" field.
- **Exit:** retrieval measurably improves recall or report quality vs. M2 on the benchmark. If it doesn't, that's a real finding — don't scale a corpus that isn't helping.

### M4 — Calibration corpus (Weeks 10–12)
**Goal:** operationalize the plan's best idea — learning to reject.
- Curate Code4rena / Sherlock findings **including invalid / duplicate / known-issue** (licensing permitting — see §5). Use them specifically as **calibration exemplars for the FP agent** and dedup.
- **Dedup / root-cause clustering (Phase 15):** collapse N symptoms with one root cause into one finding.
- Researcher-reasoning exemplars (Phase 4) injected as few-shot "how an auditor thinks."
- **Exit:** FP agent cites real "why this was judged invalid/duplicate" analogues; dedup collapses symptom clusters on the benchmark.

### M5 — Scale + orchestration (Quarter 2)
**Goal:** scale only what's proven to matter.
- **Multi-agent pipeline (Phase 11 full):** split into Architecture / Economic / Security / Research / Exploit / Report agents **only if** the monolith hits context or quality ceilings.
- **GitHub patch intelligence (Phases 3, 7):** vuln-version → fix → patch-diff → regression-test as a retrieval source (*what changed → why → which invariant → how the fix prevents recurrence*).
- **Knowledge graph (Phase 9):** only if flat retrieval + metadata filters prove insufficient.
- Corpus scale-up per the plan's own "quality first, then scale" rule.

---

## 4. Recommended stack
- **Delivery:** a Claude Code skill — `.claude/skills/audit/SKILL.md` + helper scripts. This *is* the "extension."
- **Execution / PoC:** Foundry (`forge`, `anvil` fork tests). Non-negotiable; it's the ground-truth engine.
- **Ingestion + retrieval:** Python. Embeddings via API. Vector store: SQLite + `sqlite-vec`, or LanceDB — local, no heavy infra.
- **Knowledge files:** markdown / JSON in-repo (taxonomy, invariants, formulas, attack primitives). Human-readable, diffable, reviewable.
- **Benchmark:** Damn Vulnerable DeFi + curated DeFiHackLabs PoCs, ground truth in YAML.

---

## 5. Legal / licensing (do this before ingesting anything)
- **DeFiHackLabs** — MIT (verify the current LICENSE before ingesting). ✅ Safe starting corpus; already has Foundry PoCs + root causes.
- **Code4rena reports** — public on GitHub; check the specific repo's license and attribution terms per report.
- **GitHub Security Advisories / OSV** — openly licensed, structured, machine-readable. ✅ Great for patch intel.
- **Solodit / Immunefi** — review ToS before scraping; prefer their public write-ups and link rather than wholesale copy. ⚠️ Defer.
- **Rule:** start MIT/public-licensed only. Keep a `SOURCES.md` logging each source's license and date of ingestion.

---

## 6. Risks & honest expectations
- **False positives are the hard problem.** Budget most effort here (M2/M4), not on finding more candidates.
- **Economic/logic bugs are where LLMs are weakest** — and where the value is. Expect pattern bugs to come easily and novel logic bugs to need human partnership.
- **Context limits:** a whole protocol won't fit in context. Chunking + retrieval + (eventually) orchestration is why M5 exists.
- **Benchmark overfitting:** keep a held-out set you never tune against.
- **Reproducibility:** audits must be repeatable. Log prompts, retrieved context, model version, and PoC output for every finding.
- **Retrieval may underperform expectations** on classic bugs the base model already knows. That's fine — M3's exit criterion is designed to catch it early so you don't scale a corpus that doesn't pay off.

---

## 7. Success metrics
- **Primary — precision on benchmark:** fraction of reported findings that are real. Target a floor (e.g. ≥70%) before trusting output.
- **Secondary — recall of known Highs/Criticals.**
- **PoC coverage:** every High/Critical ships with a passing Foundry PoC or is downgraded.
- **Human speedup:** time-to-first-defensible-report per scope.

---

## 8. Immediate next step
Scaffold **M0**: repo skeleton + the taxonomy/invariant/formula knowledge files + the benchmark harness (`benchmarks/` with ground-truth YAML) + a skeleton `SKILL.md`. That gives you the ruler and the slice to iterate against in week one.

---

## Addendum v2 — refined vision, non-goals & model-agnostic architecture
*(adopted after the M0 blind run; supersedes earlier wording where they differ)*

### What this is (one line)
A **Web3-only, model-agnostic security-research layer** that boosts an agent's investigation depth, hypothesis generation, and critical reasoning — running on top of Claude Code / Codex / DeepSeek.

### The moat = trust, not volume
Every finding ships with a working PoC, an explicit "why this is not a false positive / duplicate," and an explicit "what I could not verify." Competitors emit low-precision noise; this emits defensible, proven findings.

### Non-goal: "100% bug detection"
Not achievable — undecidable in general; most serious bugs live in economic/business *intent*, not syntax; even audited code gets exploited. It is also actively harmful to chase: forcing 100% manufactures false positives, the exact failure we engineer against. **Replace the 100% goal with measurable precision/recall on a growing benchmark.** Target: very high precision (≥90%), strong Critical/High recall, every High/Critical PoC-backed.

### Scope
Web3 / EVM smart contracts only. Specialization is what buys depth.

### Architecture: portable engine + thin adapters
- **Engine (model-neutral — just files + a protocol):** knowledge base · Security Memory (retrieval corpus) · pipeline spec · PoC/validation harness · benchmark.
- **Host adapters (thin):** Claude Code skill (built) · DeepSeek / Codex runners (later).
- The **benchmark** doubles as the objective way to compare backends and to prove we beat other tools.

### Adopted design principles
- **Security Memory = retrieval, not context-dump.** Curated thousands, each deeply normalized; pull only what's relevant to the target (quality > quantity).
- **Exploits → reusable research patterns** (observation → why-trusted → trace → hypothesis → validation → generalization), not just writeups.
- **GitHub = code memory:** vuln → fix → diff → regression test; reverse-engineer detection rules from many fixes.
- **Multi-model = committee of roles** (researcher / verifier / skeptic / judge), not fallback.
- **Depth modes:** normal → deep → deep-drive (a confirmed finding triggers attack-surface expansion across consumers / compositions).
- **Self-learning:** store rejected hypotheses + reason → downrank them in retrieval; promote validated findings → add as regression benchmark. Knowledge grows in *quality*, not only size.

### Reconciled milestones (honest status)
| # | Milestone | Status |
|---|---|---|
| M0 | Benchmark infrastructure (the ruler) | ✅ done |
| M0.5 | Blind 3-target validation | ✅ done — P/R 100%, but narrow (2 bug classes); see `benchmarks/RESULTS.md` |
| **M1** | **Broaden benchmark: untested categories + ≥1 real DeFiHackLabs case; re-run blind** | ◀ next |
| M2 | Security Memory v1 (retrieval; DeFiHackLabs normalized) — scoped by M1 failures | |
| M3 | Research-pattern corpus | |
| M4 | GitHub code memory → detection rules | |
| M5 | Invariant / formula graph (living, not static) | |
| M6 | Multi-model committee | |
| M7 | PoC / Foundry / fuzz execution (wire in as soon as Foundry is available — high priority) | |
| M8 | 100–500 benchmark suite (categories × difficulty) | |
| M9 | Model-agnostic adapters + continuous regression | |

The self-learning loop runs continuously from M2 onward.
