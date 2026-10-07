# Engine pipeline (model-agnostic spec)

The intelligence lives here — in files + a protocol — **not** in any one model. Claude Code / Codex / DeepSeek are interchangeable **adapters** that drive this same pipeline. This is what makes the extension portable and what the benchmark compares backends against.

## Inputs
- A Web3 / EVM smart-contract scope (path or files). Non-Web3 → out of scope, stop.
- **`scope.md`** — the program brief the user provides (in/out-of-scope assets, severity bar, PoC requirement, known issues, rules of engagement). Read it first; it is the source of truth and the acceptance bar for the whole pipeline.

## Stages → artifacts
| # | Stage | Artifact |
|---|---|---|
| 1 | Recon | contracts, deps, roles, upgradeability, external calls, assets, trust boundaries |
| 2 | Architecture map | protocol type, money flow, privileged actors, crown-jewel assets |
| 3 | Retrieve | relevant `knowledge/*` + `memory/` patterns for THIS target type (not a dump) |
| 4 | Invariant extraction | invariants that must hold + who can modify them |
| 5 | Attack-surface + multi-angle hypotheses | candidates from economic / state / cross-contract / trust / composition / historical / assumption angles |
| 6 | Adversarial gate | for each candidate, try to kill it (intended? reachable? mitigated? economic? duplicate?) |
| 7 | PoC | runnable proof for survivors (Foundry/Hardhat) — **prove or drop** |
| 8 | Deep-drive | expand confirmed findings across consumers / compositions |
| 9 | Dedup + score | collapse same-root-cause; confidence; drop known issues |
| 10 | Report | per acceptance criteria: finding + broken invariant + attack path + **runnable PoC** + fix + "why not FP/duplicate" |

## Acceptance criteria (default; overridable per program)
A finding ships only if: broken invariant named · concrete attack path · **runnable PoC** · deduped against known issues · fix suggested. No PoC → not submitted. (Mirrors real bug-bounty rules, e.g. Critical + unprivileged + runnable PoC.)

## Adapters
| Adapter | Status | Role |
|---|---|---|
| **Claude Code skill** (`.claude/skills/audit/SKILL.md`) | ✅ built | drives stages 1–10 in-session |
| DeepSeek API runner | ⏳ planned | same pipeline, self-hostable / low-cost |
| Codex adapter | ⏳ planned | same pipeline |
| Multi-model committee | ⏳ planned (M6) | researcher / verifier / skeptic / judge across models |

## Why model-agnostic matters
- **Benchmark = objective backend chooser**: run the same blind suite with each adapter → compare precision/recall → route to the best (or ensemble).
- **No vendor lock-in / self-hostable** (DeepSeek) → viable for solo bug-bounty hunters, not just enterprises.
