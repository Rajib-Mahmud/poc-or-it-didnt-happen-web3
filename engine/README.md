# Engine — runnable, model-agnostic audit core

The portable "intelligence" from `PIPELINE.md`, as actual code. Same engine under any host
(Claude Code / Codex / DeepSeek); the model is chosen by environment variables.

## Quick start
```bash
pip install -r engine/requirements.txt          # just pyyaml for the offline core
python -m engine.cli info                        # show config + what's available
python -m engine.cli selftest                    # prove the pipeline runs on every benchmark (dry)
```

## Real audits (needs a key)
```bash
# Anthropic / Claude
export W3SEC_PROVIDER=anthropic W3SEC_MODEL=<model-id> ANTHROPIC_API_KEY=sk-...
# DeepSeek (OpenAI-compatible)
export W3SEC_PROVIDER=deepseek  W3SEC_MODEL=deepseek-reasoner DEEPSEEK_API_KEY=sk-...
# OpenAI / Codex
export W3SEC_PROVIDER=openai    W3SEC_MODEL=<model-id> OPENAI_API_KEY=sk-...

pip install anthropic   # or: pip install openai   (only the one you use)
python -m engine.cli audit path/to/Contract.sol --show-raw
python -m engine.cli audit path/to/Contract.sol --scaffold-poc
export W3SEC_COMMITTEE=1   # researcher -> skeptic -> judge
python -m engine.cli score benchmarks/examples/subtle-rounding
```

## Scale the corpus to thousands
```bash
python -m engine.cli ingest           # dry: show plan
python -m engine.cli ingest --run     # shallow-clone DeFiHackLabs (MIT) + write case stubs
```

## What runs offline vs what needs you
| Capability | Status |
|---|---|
| pipeline, retrieval, committee wiring, scorer, CLI, PoC scaffolder | ✅ runs now (dry) |
| real audit quality | needs a provider **API key** |
| PoC **execution** | needs `foundryup` (install `forge`) |
| thousands of cases | needs `ingest --run` (git + network) |
| embedding retrieval | future (tag-based today) |

Honest by design: the dry provider returns **no** findings — no model means no real audit.
