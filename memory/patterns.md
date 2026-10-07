# Security Memory — research patterns (curated seed)

Web3-only. Each is *reasoning*, abstracted from public, canonical exploit classes, in the `research_pattern` schema (`SCHEMA.md`). This is a **seed** — the automated ingester (`INGESTION.md`) scales the corpus to thousands.

---

```yaml
- id: P1
  bug_class: execution/reentrancy
  observation: "external call (token transfer, callback, or arbitrary .call) inside a state-changing flow"
  suspicious_property: "state is read/used before it is finalized"
  why_trusted: "code assumes control returns only after state settles"
  trace_strategy: "list every external call; check checks-effects-interactions order; check if any view this contract exposes is read by others mid-call"
  hypothesis: "attacker re-enters before effects, or an external consumer reads stale state (read-only reentrancy)"
  validation: "fork test that re-enters during the external call and asserts a broken invariant"
  impact: "fund drain / inconsistent accounting"
  generalization: "untrusted control transfer in the middle of a non-atomic state update"
  detection_questions:
    - "Is there an external call before state is updated?"
    - "Can the called token/recipient execute code (ERC-777/hooks/callbacks)?"
    - "Does another contract read a value that changes across this call?"
  applies_to: [vault, lending, amm, staking, any-external-call]

- id: P2
  bug_class: oracle/price-manipulation
  observation: "a price/amount is read from a source an attacker can move within one tx"
  suspicious_property: "spot value consumed at the wrong moment"
  why_trusted: "code treats the price as ground truth"
  trace_strategy: "find every price read; classify spot vs TWAP; check freshness/decimals; enumerate downstream consumers (borrow, liquidation, mint, share price)"
  hypothesis: "attacker moves the source (flash-funded) then triggers the consumer at the manipulated value"
  validation: "fork test: move price, call consumer, show mispriced mint/borrow/liquidation"
  impact: "under-collateralized borrow / unfair liquidation / theft"
  generalization: "attacker-controlled input consumed as trusted valuation"
  detection_questions:
    - "Is the price spot and cheap to move?"
    - "Is there a staleness/heartbeat and decimal check?"
    - "How many consumers trust this one source?"
  applies_to: [lending, amm, vault, derivatives, stablecoin]

- id: P3
  bug_class: accounting/share-inflation
  observation: "shares = assets * supply / totalAssets, where totalAssets = live balance"
  suspicious_property: "totalAssets movable by a direct transfer; no virtual offset / dead shares / min deposit"
  why_trusted: "code assumes balance only changes through accounted flows"
  trace_strategy: "check first-deposit path; can shares round to 0; is a donation reflected in totalAssets"
  hypothesis: "attacker deposits first, donates to inflate, victim's deposit rounds to 0 shares"
  validation: "fork test: 1-wei deposit + donation + victim deposit → victim 0 shares → attacker redeems pool"
  impact: "theft of subsequent depositors' funds"
  generalization: "price/ratio state mutable outside accounted flows before it stabilizes"
  detection_questions:
    - "Is there a virtual shares/assets offset, dead shares, or minimum initial deposit?"
    - "Are 0-share deposits rejected?"
    - "Does rounding favor the vault?"
  applies_to: [vault, erc4626, staking]

- id: P4
  bug_class: access-control/initialization
  observation: "a state-changing function sets trusted config / roles / upgrade target"
  suspicious_property: "missing or wrong gate, or an unprotected initializer"
  why_trusted: "code assumes only the intended role can reach it"
  trace_strategy: "enumerate every external state-changing fn; confirm each gate; look for indirect paths (delegatecall, callback) that bypass it; check initializer is one-shot"
  hypothesis: "unprivileged caller (or re-initialization) rewrites trusted state"
  validation: "unit test calling the function from a non-owner account succeeds"
  impact: "takeover / rewrite of oracle/fees/upgrade → total compromise"
  generalization: "trusted state reachable by an untrusted actor"
  detection_questions:
    - "Does every sensitive fn have the correct modifier?"
    - "Is initialize() protected and non-repeatable?"
    - "Can an indirect path bypass the gate?"
  applies_to: [proxy, upgradeable, any-admin, token]
  note: "for bug-bounty scope: 'rogue privileged user' is usually OUT of scope — target the UNPRIVILEGED reach or privilege-escalation path, not 'admin can rug'."

- id: P5
  bug_class: signatures/replay
  observation: "an authorized message/permit is verified and executed"
  suspicious_property: "no nonce, or missing chainId / verifyingContract in the domain"
  why_trusted: "code assumes a signature is used once, here"
  trace_strategy: "check nonce increment+check; inspect EIP-712 domain; check cross-chain / cross-contract reuse"
  hypothesis: "replay the same signature (same chain twice, or across chains/contracts)"
  validation: "unit test submitting the signature twice both succeed"
  impact: "double execution / drained approvals"
  generalization: "authorization token valid in more contexts than intended"
  detection_questions:
    - "Is a nonce incremented and checked?"
    - "Are chainId and verifyingContract bound into the signed data?"
  applies_to: [permit, meta-tx, bridge, governance]

- id: P6
  bug_class: governance/flash-loan
  observation: "voting power = token balance at call time"
  suspicious_property: "power is borrowable within one tx"
  why_trusted: "code assumes voters are long-term holders"
  trace_strategy: "check if proposal/vote uses live balance vs a past snapshot; check timelock"
  hypothesis: "flash-borrow tokens, vote/execute, repay in one tx"
  validation: "fork test: flash-loan, pass a malicious proposal"
  impact: "hostile governance action / treasury drain"
  generalization: "transient, borrowable control over a trusted decision"
  detection_questions:
    - "Is voting power snapshotted before the proposal?"
    - "Is there a timelock between decision and effect?"
  applies_to: [governance, dao]

- id: P7
  bug_class: accounting/rounding
  observation: "division in a value-returning path"
  suspicious_property: "rounding direction favors the user, or an off-by-one"
  why_trusted: "code assumes rounding is negligible"
  trace_strategy: "check each mulDiv's rounding direction on deposit vs withdraw; ceil vs floor"
  hypothesis: "repeatedly exploit the favorable rounding to extract value / break sum(out) <= in"
  validation: "unit test showing redeemed > fair / invariant drift"
  impact: "value leak (often Low/Med unless amplifiable); accounting drift"
  generalization: "rounding must always favor the protocol, never the user"
  detection_questions:
    - "Does withdraw/redeem round down (vault-favoring)?"
    - "Is any ceil division used in the user's favor?"
  applies_to: [vault, lending, amm, staking]

- id: P8
  bug_class: cross-chain/message-authentication
  observation: "an inbound cross-chain message triggers a privileged effect (mint/release)"
  suspicious_property: "source/authenticity not fully verified, or replayable"
  why_trusted: "code assumes the message came from the real remote via the real relayer"
  trace_strategy: "check how source chain/address is verified; per-message nonce; trusted-remote config"
  hypothesis: "forge or replay a message to mint/release without a real deposit"
  validation: "test delivering a crafted/duplicated message that releases funds"
  impact: "unbacked mint / double release — bridge drain"
  generalization: "trusted effect gated on an insufficiently-authenticated external message"
  detection_questions:
    - "Is the source chainId + remote address verified?"
    - "Is each message consumable only once?"
  applies_to: [bridge, cross-chain, messaging]

- id: P9
  bug_class: execution/flash-loan-amplification
  observation: "a check or effect depends on a balance/supply/price the caller can hold transiently"
  suspicious_property: "'must own X' / 'TVL > Y' / spot price satisfied within one tx"
  why_trusted: "code assumes capital = long-term commitment"
  trace_strategy: "list every balance/supply/price-gated branch; ask if it survives borrowed capital repaid same tx"
  hypothesis: "flash-borrow to satisfy the gate, extract, repay atomically"
  validation: "fork test wrapping the action in a flash loan"
  impact: "governance capture, oracle move, threshold bypass, reward inflation"
  generalization: "transient capital treated as durable state"
  detection_questions:
    - "Does any critical decision read a same-tx-movable quantity?"
    - "Is there a snapshot / time lock between funding and effect?"
  applies_to: [lending, amm, governance, vault, staking]

- id: P10
  bug_class: accounting/fee-on-transfer-rebasing
  observation: "deposit/transfer accounting uses the `amount` argument, not the actual balance delta"
  suspicious_property: "`balanceBefore/After` not measured around transferFrom"
  why_trusted: "code assumes tokens move 1:1 and balances are static"
  trace_strategy: "find every transferFrom/transfer; check if credited amount = measured delta; check rebasing"
  hypothesis: "fee-on-transfer token credits more than received → protocol under-collateralized; rebasing desyncs internal accounting"
  validation: "fork test with a fee-on-transfer / rebasing token"
  impact: "insolvency / theft of the shortfall"
  generalization: "internal accounting diverges from real token balances"
  detection_questions:
    - "Is the credited amount the measured balance delta?"
    - "Are non-standard (fee/rebasing) tokens in scope?"
  applies_to: [vault, lending, amm, staking, token-integration]

- id: P11
  bug_class: execution/callback-reentrancy
  observation: "a token/NFT transfer with a receiver hook (ERC777 tokensReceived, ERC721/1155 onReceived) mid-operation"
  suspicious_property: "attacker-controlled code runs before state settles"
  why_trusted: "code treats a 'transfer' as inert"
  trace_strategy: "find safeMint/safeTransfer/ERC777 flows; check CEI; check cross-function state read during the hook"
  hypothesis: "reenter via the receiver hook before balances/flags update"
  validation: "malicious receiver contract in a fork test"
  impact: "double-mint, drain, inconsistent state"
  generalization: "untrusted callback inside a non-atomic update (a reentrancy with no `.call`)"
  detection_questions:
    - "Does a transfer here invoke a receiver hook?"
    - "Is state finalized before that transfer?"
  applies_to: [vault, nft, token-integration, staking]

- id: P12
  bug_class: token-integration/unchecked-return
  observation: "ERC-20 transfer/approve return value ignored, or assumes a bool is returned"
  suspicious_property: "non-standard tokens (USDT-style no-return) or silently-failing transfers"
  why_trusted: "code assumes a failed transfer reverts"
  trace_strategy: "grep raw transfer/transferFrom/approve not wrapped in SafeERC20; check return handling"
  hypothesis: "a transfer that returns false (not revert) is treated as success → credited without funds"
  validation: "token that returns false; assert accounting credited anyway"
  impact: "theft / phantom balances"
  generalization: "trusting an external call's success without checking it"
  detection_questions:
    - "Is SafeERC20 used, or are returns checked?"
    - "Are no-return tokens (USDT) in scope?"
  applies_to: [token-integration, vault, lending, amm]

- id: P13
  bug_class: signatures/approval-permit
  observation: "approve/permit used for pulling funds; infinite or re-set approvals"
  suspicious_property: "approval race (front-run approve change) or permit front-run griefing"
  why_trusted: "code assumes allowance reflects current intent"
  trace_strategy: "check approve patterns (set-to-0 first?), permit usage, who can call permit-consuming fn"
  hypothesis: "front-run a permit/approve to grief or double-spend the allowance window"
  validation: "order two txs (approve N->M) and show double pull"
  impact: "unexpected spend / griefed txs"
  generalization: "a two-step allowance whose steps can be reordered by an attacker"
  detection_questions:
    - "Is permit consumption front-runnable for griefing?"
    - "Is the classic approve-race mitigated (increase/decrease)?"
  applies_to: [token-integration, amm, permit]

- id: P14
  bug_class: lending/liquidation
  observation: "liquidation path: eligibility, seizure amount, incentive, and who may call"
  suspicious_property: "self-liquidation profit, grief (block liquidation), or seize > collateral"
  why_trusted: "code assumes liquidations keep the system solvent"
  trace_strategy: "trace health check -> seize math -> incentive; check rounding, price source, partial liq"
  hypothesis: "manipulate price or craft a position so liquidation is profitable to the borrower, blocked, or creates bad debt"
  validation: "fork test pushing a position to the liquidation edge"
  impact: "bad debt / protocol insolvency / stuck collateral"
  generalization: "a solvency backstop that can be turned against the protocol"
  detection_questions:
    - "Can the borrower profit from liquidating themselves?"
    - "Can liquidation be reverted/griefed to trap bad debt?"
  applies_to: [lending, derivatives, cdp]

- id: P15
  bug_class: accounting/reward-staking
  observation: "reward math: rewardPerToken / accRewardPerShare / lastUpdate, claimed vs pending"
  suspicious_property: "index not updated before balance change; deposit-then-claim; double claim"
  why_trusted: "code assumes the accumulator is always synced before stake/unstake/claim"
  trace_strategy: "check every stake/unstake/claim updates the accumulator FIRST; check first-depositor / zero-supply div"
  hypothesis: "deposit right before a reward tick, or claim twice via a stale index, to over-earn"
  validation: "unit test: stake, trigger reward, claim > fair share"
  impact: "reward pool drain (other stakers' funds)"
  generalization: "an accumulator read before it is updated"
  detection_questions:
    - "Is the reward index updated before every balance mutation?"
    - "What happens at totalSupply == 0?"
  applies_to: [staking, farming, vault]

- id: P16
  bug_class: dos/griefing
  observation: "an unbounded loop over users/entries, or a push-payment to an address that can revert"
  suspicious_property: "one participant can block the whole flow, or arrays grow without bound"
  why_trusted: "code assumes lists stay small and recipients accept funds"
  trace_strategy: "find loops over dynamic arrays; find push transfers to arbitrary recipients inside shared flows"
  hypothesis: "add many entries (gas DoS) or supply a reverting/blacklisting recipient to brick a shared function"
  validation: "fork test: a reverting recipient blocks others' withdrawals / finalize"
  impact: "permanent lock / denial of a critical function"
  generalization: "shared liveness coupled to one untrusted participant or unbounded work"
  detection_questions:
    - "Can one user make a shared function always revert?"
    - "Is there a pull-payment fallback? Are loops bounded?"
  applies_to: [vault, staking, governance, raffle, payout]

- id: P17
  bug_class: amm/slippage-mev
  observation: "a swap/mint/redeem with no minOut / deadline, or priced at spot"
  suspicious_property: "user value depends on pool state at execution time"
  why_trusted: "code assumes the mempool is fair"
  trace_strategy: "check for minAmountOut, deadline, and whether price is spot vs protected"
  hypothesis: "sandwich the victim tx (front-run to move price, back-run to profit)"
  validation: "fork test ordering attacker txs around the victim"
  impact: "value extraction from users each tx"
  generalization: "unprotected execution against attacker-orderable state"
  detection_questions:
    - "Is there a minOut and deadline?"
    - "Is the execution price manipulable in the same block?"
  applies_to: [amm, vault, lending]

- id: P18
  bug_class: upgradeability/initialization
  observation: "an upgradeable/proxied contract with an initializer instead of a constructor"
  suspicious_property: "initializer unprotected, re-callable, or implementation left uninitialized/self-destructible"
  why_trusted: "code assumes init runs once, by the deployer, atomically"
  trace_strategy: "check initializer modifier, _disableInitializers in impl, front-run window on deploy"
  hypothesis: "front-run or re-call initialize() to seize ownership; brick/selfdestruct an uninitialized implementation"
  validation: "call initialize() from an attacker after deploy"
  impact: "full takeover / permanently bricked proxy"
  generalization: "one-time trusted setup that is reachable more than once or by the wrong actor"
  detection_questions:
    - "Is initialize() protected and non-repeatable?"
    - "Are implementation contracts disabled from init?"
  applies_to: [proxy, upgradeable]

- id: P19
  bug_class: randomness/predictability
  observation: "outcome depends on block.timestamp, blockhash, prevrandao, or on-chain pseudo-randomness"
  suspicious_property: "a winner/price/selection derivable or influenceable by a miner/validator or same-tx actor"
  why_trusted: "code assumes on-chain values are unpredictable"
  trace_strategy: "find randomness sources; check if a secure VRF with proper request/fulfill separation is used"
  hypothesis: "predict or bias the random value, or revert-until-favorable, to win"
  validation: "compute the outcome in a contract before entering"
  impact: "rigged raffles / unfair selection / fund theft"
  generalization: "trusting a predictable value as unpredictable"
  detection_questions:
    - "Is randomness from a secure oracle (VRF), not block values?"
    - "Can the consumer revert on an unfavorable result?"
  applies_to: [raffle, randomness, nft, gaming]

- id: P20
  bug_class: execution/arbitrary-call
  observation: "a user-influenced target address and/or calldata passed to .call/.delegatecall"
  suspicious_property: "the contract can be made to call arbitrary code, or delegatecall untrusted logic"
  why_trusted: "code assumes the target/selector is a known, safe integration"
  trace_strategy: "trace every low-level call; who controls target, value, calldata; is delegatecall target trusted"
  hypothesis: "point the call at the token/treasury to move funds, or delegatecall to hijack storage"
  validation: "craft calldata that makes the contract transfer its own funds/approvals"
  impact: "full drain / takeover"
  generalization: "attacker-chosen callee executed with the contract's authority"
  detection_questions:
    - "Is the call target/selector attacker-influenced?"
    - "Does the contract hold funds/approvals the call could spend?"
  applies_to: [proxy, vault, bridge, multicall, account-abstraction]
```
