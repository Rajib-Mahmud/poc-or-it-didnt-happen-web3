# Protocol Math — and where it breaks

Formulas alone don't find bugs. Each entry carries the attacker-relevant context:

> **Formula** → assumptions → invariant → manipulable variables → boundary cases → rounding → historical exploits → how to test.

---

## AMM constant product
**`x * y = k`** (reserves x, y)
- *Assumptions:* reserves reflect real balances; no mid-swap reentry; fee applied correctly.
- *Invariant:* `k` never decreases except by fees (see INV-A-1).
- *Manipulable:* reserves via large swap or direct token donation + `sync`/`skim`; price = `y/x` is instantaneous and cheap to move.
- *Boundary:* tiny reserves (pool just created), single-sided liquidity, tokens with transfer fees / rebasing.
- *Rounding:* output rounded down; repeated tiny swaps leak dust.
- *Historical:* spot-price-as-oracle manipulations (countless); read-only reentrancy on `getReserves`.
- *Test:* fork, move price with a flash loan, read what a dependent protocol computes.

## Lending — collateral & health
**`LTV = debt / collateralValue`**, **`healthFactor = collateralValue * liquidationThreshold / debt`**
- *Assumptions:* `collateralValue` from a sound oracle; debt includes accrued interest; prices same decimals.
- *Invariant:* action allowed only if `healthFactor ≥ 1` after it (INV-L-1); debt accrued first (INV-L-2).
- *Manipulable:* `collateralValue` (oracle!), the *order* of operations (withdraw before health check), interest not accrued.
- *Boundary:* exactly `hf == 1`; dust debt rounding to 0; collateral with 6 decimals vs 18-decimal math.
- *Rounding:* round debt UP, collateral DOWN (favor protocol).
- *Historical:* oracle-manipulation liquidations; self-liquidation profit; borrow using spot-priced thin collateral.
- *Test:* push price to the liquidation edge; try to withdraw collateral while leaving hidden debt.

## Utilization & interest
**`U = borrowed / supplied`** → feeds a rate curve.
- *Assumptions:* `supplied` and `borrowed` can't be transiently distorted.
- *Manipulable:* flash-deposit to spike/suppress U and move rates; `supplied == 0` division.
- *Boundary:* `U = 0`, `U = 1` (100% utilized → withdrawals blocked), kink point.
- *Test:* flash-loan around a rate-sensitive action.

## Vault share price (ERC-4626)
**`sharePrice = totalAssets / totalSupply`**, **`shares = assets * totalSupply / totalAssets`**
- *Assumptions:* `totalAssets` only changes through accounted flows.
- *Invariant:* INV-V-1 (no inflation), INV-V-2 (rounding favors vault).
- *Manipulable:* `totalAssets` via **direct donation** (ERC-20 transfer in) before first deposit → `totalSupply` tiny → victim shares round to 0.
- *Boundary:* `totalSupply == 0` (first depositor), 1 wei deposits, high-decimal assets.
- *Rounding:* `deposit` rounds shares DOWN, `withdraw` rounds assets DOWN.
- *Historical:* first-depositor / inflation attack. *Mitigations:* virtual offset (OZ), dead shares, min initial deposit.
- *Test:* as attacker, deposit 1 wei → donate large amount → victim deposits → attacker redeems > deposited.

## Liquidation incentive
**`seized = repaid * (1 + bonus) / collateralPrice`**
- *Manipulable:* `collateralPrice` (oracle), `bonus` config, rounding of `seized`.
- *Boundary:* bonus so high it creates bad debt; seize > available collateral.
- *Test:* liquidate at a manipulated price; check protocol left with bad debt.

---
*Adding one: write the formula, then for each variable ask "can an attacker move this within one transaction, and does the code read it at the wrong moment?"*
