# Smart-Contract Vulnerability Taxonomy

The checklist `/audit` walks against target code. Each class has a one-line "look for" cue. This is a *reference*, not a scoring sheet — the goal is to generate hypotheses, then reject the ones that don't survive the adversarial self-check.

## Access / Authorization
- **Access control** — missing/incorrect `onlyOwner`/role checks on state-changing functions.
- **Initialization** — unprotected `initialize()`, re-initialization, uninitialized proxies.
- **Privilege escalation** — a low-priv path that reaches a high-priv effect.
- **Role confusion** — one role assumed where another is checked.
- **Ownership** — transfer/renounce flaws, two-step vs one-step.
- **Upgrade authorization** — who can upgrade, and is that gate real.

## DeFi (protocol logic)
- **AMM** — k-invariant breaks, fee/reserve desync, swap rounding.
- **Lending / borrowing** — bad-debt creation, interest accrual errors, collateral mispricing.
- **Liquidation** — self-liquidation, grief, liquidation at wrong price, no incentive.
- **Staking / farming** — reward accounting, deposit/withdraw ordering, inflation.
- **Vault (ERC-4626)** — share inflation, donation, first-depositor, rounding direction.
- **Derivatives / stablecoin** — peg assumptions, funding, settlement.

## Oracles
- **Manipulation** — spot-price reads, low-liquidity pools, single-source.
- **Stale price** — missing freshness/heartbeat checks.
- **Decimal mismatch** — feed decimals ≠ token decimals.
- **Fallback** — insecure fallback path when primary fails.
- **TWAP vs spot** — window too short, or spot used where TWAP needed.

## Accounting / Math
- **Share inflation / donation** — direct transfer skews `assets/shares`.
- **Rounding / precision** — rounding in attacker's favor, accumulated dust.
- **Unit / decimal mismatch** — mixing 1e18 and token-native units.
- **Debt / fee accounting** — fees double-counted, debt not updated atomically.

## Execution / Control flow
- **Reentrancy** — cross-function, cross-contract, read-only reentrancy.
- **Callback** — ERC-777/ERC-1155/hooks giving attacker control mid-operation.
- **Delegatecall** — context/storage confusion, untrusted target.
- **Arbitrary call** — user-controlled target/calldata.
- **Flash loans** — atomic capital enabling any of the above.

## Signatures / Auth messages
- **Replay** — missing nonce, cross-chain replay (no chainId), cross-contract.
- **Nonce** — reuse, predictable, not incremented.
- **Domain separation** — EIP-712 domain wrong/missing.
- **Permit / meta-tx** — signature malleability, front-running permit, relayer trust.

## Cross-chain / Bridge
- **Message authentication** — forged/unauthenticated messages.
- **Replay** — same message accepted twice; missing per-chain nonce.
- **Chain ID** — not bound into the message.
- **Trusted remote** — misconfigured/unverified source address.
- **Relayer** — trust in relayer for ordering/delivery/finality.

## Governance
- **Voting** — snapshot vs live balance, double-count.
- **Flash-loan governance** — borrow votes atomically.
- **Delegation** — delegate then transfer, double-voting.
- **Quorum / timelock** — bypass, or no delay on critical changes.

## Upgradeability
- **Proxy** — function clash, storage collision.
- **Implementation** — self-destruct / left uninitialized.
- **Storage collision** — layout changes across versions.
- **Initializer** — missing `_disableInitializers`, re-init.
- **UUPS / beacon / diamond** — upgrade gate, facet selector clashes.

## Token integration
- **Unchecked return** — raw transfer/approve (no SafeERC20); no-return (USDT-style) tokens.
- **Fee-on-transfer / rebasing** — credited amount ≠ measured balance delta.
- **Callback hooks** — ERC-777 / ERC-721 / 1155 receiver hooks enabling reentrancy.
- **Approval race / permit** — approve front-run, infinite approval, permit griefing.
- **Decimals** — mixing token-native decimals with protocol math.

## Denial of Service / griefing
- **Unbounded loop** — iteration over user-growable arrays exceeds the gas limit.
- **Push-payment block** — one reverting/blacklisting recipient bricks a shared flow.
- **Griefable state** — anyone can wedge a wave/queue/epoch into a stuck state.
- **Revert-in-batch** — one external call reverting rolls back everyone.

## MEV / ordering
- **Missing slippage / deadline** — sandwichable swaps / mints / redeems.
- **Front-running** — commit-sensitive actions without commit-reveal.
- **JIT / back-run** — liquidity or liquidation timing games.

## Randomness / time
- **Weak RNG** — block.timestamp / blockhash / prevrandao used as randomness.
- **VRF misuse** — predictable request, revert-on-unfavorable, no request/fulfill separation.
- **Timestamp dependence** — critical logic gated on manipulable block.timestamp.

## L2 / rollup-specific
- **Sequencer uptime** — oracle/liquidation without an L2 sequencer-uptime check.
- **Address aliasing** — L1→L2 `msg.sender` aliasing assumptions.
- **Gas/fee model** — L1 data-fee or gas-price assumptions that differ on L2.

---
*When extending this file, keep each entry to one actionable line. Depth lives in `invariants.md` and `formulas.md`.*
