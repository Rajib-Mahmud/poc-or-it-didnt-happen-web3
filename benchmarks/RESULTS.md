# Benchmark leaderboard

The "ruler." Scores here come from a **blind run** — an auditor that sees only the target
`Vault.sol` + `knowledge/` + the `audit` skill, with **neutral target names** and **no** `truth.yaml` /
`RESULTS.md` / `*.t.sol`. Inline self-audits (author grading their own work) are excluded as biased.

---

## Blind run 1 — 2026-10-07
- **Auditor:** `general-purpose` subagent (Opus 4.8), fresh context, workspace `scratchpad/blind`, neutral names `target-a/b/c`, no answer files present.
- **Mapping (revealed post-run):** `target-a` = subtle-rounding · `target-b` = erc4626-first-depositor · `target-c` = safe-vault.

| Real target | Expected | Auditor reported | TP | FP | FN | Verdict |
|---|---|---|---|---|---|---|
| erc4626-first-depositor | 1 High: inflation | 1 **Critical**: inflation | 1 | 0 | 0 | ✅ caught (Critical vs key High — both defensible) |
| subtle-rounding | 1 Low/Med: redeem rounds up; **not** inflation | 1 **Low**: redeem rounds up; inflation explicitly ruled out | 1 | 0 | 0 | ✅ caught **+ decoy resisted** |
| safe-vault | **0** vulns | **0** vulns; mitigations confirmed sound | 0 | 0 | 0 | ✅ **no false positive** |

**Aggregate:** TP=2 · FP=0 · FN=0 → **Precision 100% · Recall 100%**
- 0 false positives on the negative control ✅
- 0 hallucinated High/Critical ✅
- mitigated-inflation decoy resisted 2/2 ✅

### Category-wise
| Category | Detected | FP | Coverage |
|---|---|---|---|
| accounting/share-inflation | 1/1 | 0 | tested |
| accounting/rounding | 1/1 | 0 | tested |
| negative control (clean code) | — | 0 | tested |
| decoy resistance (mitigated inflation) | 2/2 ignored | — | tested |
| access-control, oracle, reentrancy, signature, cross-chain, governance, upgradeability | — | — | **UNTESTED** |

## M0 verdict: **PASS (blind)** — and meaningful, unlike the inline run.
All gates met: precision ≥0.70, Highs/Criticals found, decoy resisted, 0 FP on clean code, no hallucinated H/C.

## Honest caveats (why this is NOT "solved")
1. **Small N, self-authored, accounting-heavy.** Blind removes the big bias (answer-key visibility), but the targets are still my constructions and skew to ERC-4626 vaults.
2. **Only 2 real bug categories exercised.** 100% says nothing about oracle / access-control / reentrancy / signatures / cross-chain — all UNTESTED. A high aggregate here hides *coverage*, not a weak category.
3. **Same model family audits + grades.** Not independent of model.
4. **The auditor out-calibrated the key** on subtle-rounding: it argued LOW (excess is dust-bounded ~1 wei/call, gas ≫ 1 wei, no profitable drain) — sound reasoning. The key's severity/impact was slightly generous and has been corrected to LOW.

## Next (M1 rigor = breadth, not knowledge)
Don't expand the corpus yet. First **broaden the benchmark into untested categories + real (non-self-authored) DeFiHackLabs code**, re-run blind, and let the errors that appear there drive the M1 knowledge/reasoning upgrades.

## Run log
- 2026-10-07 — blind run 1. Precision 100% / Recall 100% on 3 targets (original skill).
- 2026-10-07 — blind run 2 (**upgraded** skill: Web3-only + `memory/` retrieval + attack-angles; re-randomized target names x/y/z). Same result: safe-vault→0, subtle-rounding→Low rounding (inflation ruled out), first-depositor→High inflation. **Precision 100% / Recall 100%, no regression**; auditor explicitly applied memory patterns P1/P2/P3/P7.
