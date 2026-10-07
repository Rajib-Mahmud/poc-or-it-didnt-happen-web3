# Security Memory — schema

Two record types. Both are **Web3-only**. Quality over quantity: every record is deeply normalized, retrievable by tag, and usable by the reasoning pipeline (not dumped into context).

## 1. `research_pattern` — reusable *thinking*, not just a writeup
The killer asset: how a researcher *reasoned*, abstracted so the model can re-apply it to new targets.
```yaml
research_pattern:
  id: P<n>
  bug_class: <taxonomy path, e.g. accounting/share-inflation>
  observation: "what caught the eye in the code"
  suspicious_property: "why it's worth a second look"
  why_trusted: "the assumption the code makes that may be false"
  trace_strategy: "how to follow it through the system"
  hypothesis: "the attack to try"
  validation: "how to PROVE or DISPROVE it (ideally a runnable PoC idea)"
  impact: "what is lost if true (funds theft / permanent lock)"
  generalization: "the abstract primitive this is an instance of"
  detection_questions: ["concrete yes/no questions to ask any target"]
  historical_cases: [<exploit_case id or public reference>]
  applies_to: [<target tags: vault, lending, amm, bridge, ...>]
```

## 2. `exploit_case` — a normalized real incident
```yaml
exploit_case:
  id: E<n>
  name: "<protocol / incident>"
  date: <YYYY-MM>
  chain: <ethereum|bsc|...>
  protocol_type: [<tags>]
  root_cause: "<one line>"
  attack_path: ["step", "step", ...]
  prerequisites: "<attacker capability / funding / timing>"
  impact: "<loss amount / effect>"
  poc_ref: "<path or url to PoC>"
  fix_ref: "<commit / diff / url>"
  generalized_pattern: P<n>        # links to the research_pattern it teaches
  source: "DeFiHackLabs | Code4rena | GHSA/OSV | ..."
  license: "<MIT | ...>"
```

## How they're used
- `INDEX.md` maps **target type → relevant pattern/case ids** (retrieval).
- The `/audit` pipeline pulls only the matching records as few-shot grounding + "historical analogue" reasoning.
- Validated new findings → promoted into a new `exploit_case` (+ regression benchmark). Rejected hypotheses → stored with the reason so retrieval can downrank them (self-learning).

## Scale path
Seed = a handful of curated `research_pattern`s (see `patterns.md`). Thousands of `exploit_case`s come from `INGESTION.md` (automated, licensed sources) — never hand-faked.
