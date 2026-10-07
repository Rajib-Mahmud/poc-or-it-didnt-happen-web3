# Baseline result — erc4626-first-depositor

- **Date:** 2026-10-07
- **Auditor:** `/audit` skill (Opus 4.8), M0 reasoning-only (no retrieval, no automated PoC)
- **Target:** `Vault.sol` (only)
- **Execution:** forge NOT installed → PoC hand-traced, not run
- ⚠️ **Bias caveat:** the target, the ground truth, and the skill were all authored in the same session. This validates that the **pipeline runs end-to-end and adjudicates correctly**, not detection power on unseen code. Treat as a plumbing test, not proof of capability.

## Findings (survived the precision gate)

### F1 — First-depositor / donation share inflation
- **Severity:** High · **Confidence:** 100/100
- **Class:** accounting/share-inflation · **Broken invariant:** INV-V-1
- **Affected:** `Vault.sol: deposit` + `previewDeposit` + `totalAssets`
- **Root cause:** `totalAssets()` = live token balance, no virtual shares / dead shares / minimum initial deposit, and `deposit` permits a 0-share mint (no `require(shares > 0)`).
- **Attacker prerequisites:** be the first depositor (`totalSupply == 0`); able to `transfer` the asset directly to the vault; a victim deposits afterward.
- **Attack path:**
  1. Attacker `deposit(1)` → `totalSupply = 1`, `totalAssets = 1`.
  2. Attacker `asset.transfer(vault, 100e18)` (donation) → `totalAssets = 100e18 + 1`, supply still 1.
  3. Victim `deposit(100e18)` → `shares = 100e18 * 1 / (100e18+1) = 0`; victim gets 0 shares.
  4. Attacker `redeem(1)` → `1 * (200e18+1) / 1 = 200e18+1`; drains the pool.
- **Impact:** attacker net profit ≈ victim's full deposit (100e18); victim left with nothing.
- **Why existing controls fail:** no virtual-offset accounting, no dead shares, no min deposit, no min-shares-out slippage guard.
- **PoC:** `Exploit.t.sol` (`test_inflation_steals_victim_deposit`). Hand-trace confirms attacker outlay `1 + 100e18`, redemption `200e18 + 1`, net `+100e18`.
- **Fix:** OZ-style virtual shares/assets offset, or mint dead shares on first deposit, or enforce a minimum initial deposit; add a `minSharesOut` parameter to `deposit`.

## Rejected candidates (precision gate working — NOT false positives)
| Candidate | Why rejected |
|---|---|
| Reentrancy in `deposit` (transferFrom before effects) | Asset assumed standard ERC-20 (no callback); not exploitable. At most **informational** ("document token assumption"). |
| Reentrancy in `redeem` | CEI respected — effects before the external transfer. Safe. |
| Rounding "loss" in previewDeposit/Redeem | Rounds **down**, favoring the vault. Intended and safe (INV-V-2 holds). |
| `setFeeRecipient` centralization | Properly `onlyOwner`; `feeRecipient` is unused. At most **informational**. |
| `deposit(0)` → 0 shares | Harmless. |

## Score
| Metric | Value |
|---|---|
| True positives (TP) | 1 |
| False positives (FP) | 0 |
| False negatives (FN) | 0 |
| **Precision** | **100%** |
| **Recall** | **100%** |

## M0 verdict: **PASS** (with caveats)
- precision ≥ 0.70 ✓ · inflation detected at High ✓ · PoC path coherent ✓ · no hallucinated High/Critical ✓

## Weaknesses this run surfaced (feed into M1)
1. **Report format has no "Informational / QA" bucket.** Legit non-vuln notes (ERC-777 token assumption, centralization) are forced into either "finding" (FP risk) or "rejected" (signal lost). → add an Info section to `SKILL.md`, kept out of the precision metric.
2. **Benchmark is too easy & author-biased.** One obvious bug, written by the grader. Need: (a) a **clean negative-control** vault where the correct output is ZERO findings (the sharpest FP test), and (b) a **real DeFiHackLabs target** nobody here wrote.
3. **No independent run.** The trustworthy baseline is a fresh-context audit that does not see this file.
