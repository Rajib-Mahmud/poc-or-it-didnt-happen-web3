# Security Memory — retrieval index

The `/audit` pipeline identifies the target type, then pulls **only** the matching patterns/cases (context quality > quantity). This is the hand-maintained index for the seed; when the corpus scales (`INGESTION.md`), this is replaced by an embedding + tag index.

## Target type → relevant patterns
| Target type / tags | Pull patterns |
|---|---|
| ERC-4626 / vault / staking | P3 (inflation), P7 (rounding), P1 (reentrancy), P2 (oracle if priced) |
| Lending / borrowing / CDP | P2 (oracle), P7 (rounding/accounting), P1 (reentrancy), P4 (access) |
| AMM / DEX | P2 (price/manipulation), P1 (read-only reentrancy), P7 (rounding) |
| Bridge / cross-chain / messaging | P8 (message auth), P5 (replay), P4 (access) |
| Governance / DAO | P6 (flash-loan voting), P5 (replay), P4 (access) |
| Token / ERC-20/721/1155 | P4 (access/init), P1 (hooks/reentrancy), P5 (permit replay) |
| Proxy / upgradeable | P4 (init/upgrade-auth), P1 (delegatecall) |
| Raffle / lottery / randomness (e.g. Chainlink VRF) | P2 (manipulable input), P4 (access), P1 (callback) |
| Any contract holding funds | P1, P4 always; others by shape |

## Tags vocabulary
`vault, erc4626, lending, cdp, amm, bridge, cross-chain, governance, dao, token, token-integration, permit, proxy, upgradeable, staking, farming, derivatives, perps, stablecoin, oracle, randomness, raffle, gaming, nft, treasury, payout, mev, dos, l2, multicall, account-abstraction`

## Additional patterns (P9–P20) — by trigger
| When the target has… | Pull |
|---|---|
| balance / supply / price-gated logic | P9 (flash-loan amplification) |
| external token integrations | P10 (fee-on-transfer/rebasing) · P12 (unchecked return) · P13 (approval/permit) |
| receiver hooks (ERC-777/721/1155), safeMint | P11 (callback reentrancy) |
| lending / CDP liquidation | P14 (liquidation grief / self / bad-debt) |
| staking / farming rewards | P15 (reward accounting) |
| shared flows, loops, push payments | P16 (DoS / griefing) |
| swaps / mint / redeem | P17 (slippage / MEV) |
| proxy / upgradeable / initializer | P18 (init/upgrade) · P20 (delegatecall target) |
| randomness / raffle | P19 (predictable randomness) |
| low-level `.call` / `.delegatecall` with user input | P20 (arbitrary call) |

## Rule
If the target shape isn't listed, map it to the nearest shape by **what state is trusted and what moves funds**, then pull those patterns. Never load the whole file.
