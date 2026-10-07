# Protocol Invariant Library

Each invariant follows the same shape so `/audit` can reason mechanically:

> **Invariant** → why it must hold → which functions can modify it → who can call those → impact if violated → historical example.

This is a **starter set**. Grow it as real audits/benchmarks reveal new ones.

---

## Access control
**INV-AC-1 — Privileged state changes are gated.**
- *Why:* trusted state (roles, oracle config, fees, upgrade target) drives value-bearing logic.
- *Modified by:* every `setX`, `grantRole`, `setOracle`, `upgradeTo`.
- *Callable by:* only the intended admin/role — verify the modifier is actually present AND correct.
- *If violated:* attacker rewrites trusted state → total compromise.
- *Check:* enumerate every state-changing external fn; confirm each has the right gate; look for indirect paths (delegatecall, callbacks) that bypass it.

## ERC-4626 vault
**INV-V-1 — Share price cannot be manipulated to steal deposits.**
- *Why:* `shares = assets * totalSupply / totalAssets`; if `totalAssets` can be inflated by a donation before the first real deposit, a late depositor's shares round to 0.
- *Modified by:* `deposit`, `mint`, `withdraw`, and *any* path that changes `totalAssets` (incl. direct token transfer / `donation`).
- *Callable by:* anyone (deposit) + anyone (donation via ERC-20 transfer).
- *If violated:* first-depositor / donation attack steals subsequent deposits.
- *Historical:* classic ERC-4626 inflation; mitigations = virtual shares/assets offset, dead shares, minimum initial deposit.

**INV-V-2 — Rounding always favors the vault, never the user.**
- *Why:* consistent rounding direction prevents value extraction via repeated ops.
- *Modified by:* `convertToShares`/`convertToAssets` and callers.
- *If violated:* dust extraction compounding to real loss.

## Lending
**INV-L-1 — A position can only be opened/kept if healthy; unhealthy positions are liquidatable.**
- *Why:* solvency of the protocol.
- *Modified by:* `borrow`, `withdraw`, `liquidate`, price updates.
- *If violated:* bad debt; protocol insolvency.
- *Check:* can health be computed with a manipulable (spot) price? can you withdraw collateral before the health check?

**INV-L-2 — Interest/debt is updated atomically before any health-dependent action.**
- *If violated:* stale debt lets you borrow/withdraw more than allowed.

## AMM
**INV-A-1 — The pool invariant (e.g. `x*y ≥ k`) never decreases except by fees owed.**
- *Modified by:* `swap`, `mint`, `burn`, `skim`, `sync`.
- *If violated:* drain via mispriced swap / reserve desync.
- *Check:* reserves updated from balances vs from internal accounting; donation/`skim` interplay; read-only reentrancy on price.

## Oracle
**INV-O-1 — Consumed prices are fresh, multi-block, and manipulation-resistant.**
- *Why:* every value calc downstream trusts it.
- *Modified by:* oracle config setters (see INV-AC-1) + the feed itself.
- *If violated:* price manipulation → liquidations / mints at wrong value.
- *Check:* spot vs TWAP; staleness/heartbeat; decimals; single-source; fallback path.

## Signatures / cross-chain
**INV-S-1 — Each authorized message executes at most once, on the intended chain/contract.**
- *Why:* prevents replay.
- *Modified by:* the verify/execute path.
- *If violated:* replay → double execution, drained funds.
- *Check:* nonce incremented & checked; chainId + verifyingContract in the EIP-712 domain; per-source nonce for bridges.

## Staking / rewards
**INV-R-1 — The reward accumulator is updated before any balance change.**
- *Why:* rewards must reflect stake-weighted time; a stale index over/under-pays.
- *Modified by:* `stake`, `unstake`, `claim`, `notifyReward`.
- *If violated:* deposit-then-claim / double-claim drains the reward pool (other stakers' funds).
- *Check:* every balance mutation calls the update first; `totalSupply == 0` division handled.

## Accounting conservation
**INV-C-1 — A user can never withdraw more than they contributed plus what they legitimately earned.**
- *Why:* `sum(out) ≤ sum(in) + earned` keeps the system solvent.
- *Modified by:* `deposit`, `withdraw`, `claim`, rounding, fee logic.
- *If violated:* value leak / insolvency.
- *Check:* rounding favors the protocol; rewards/fees are funded; no path double-counts.

## Token integration
**INV-T-1 — Internal accounting equals the measured token balance delta.**
- *Why:* fee-on-transfer / rebasing tokens break the 1:1 assumption.
- *Modified by:* any deposit/withdraw that credits from an `amount` argument.
- *If violated:* protocol under-collateralized → theft of the shortfall.
- *Check:* credited = `balanceAfter - balanceBefore`; non-standard tokens' in/out-of-scope stated.

## Liveness
**INV-L-3 — No single participant can permanently block a shared function.**
- *Why:* one user must not be able to brick withdrawals/finalize for everyone.
- *Modified by:* loops over users, push payments, batch external calls.
- *If violated:* permanent lock / DoS (a Critical class in many bounties).
- *Check:* pull-payment fallback; bounded loops; a reverting recipient can't wedge the flow.

---
*Pattern for adding one: state it as something that must ALWAYS be true, then ask "which function could make it false, and who can call that function?"*
