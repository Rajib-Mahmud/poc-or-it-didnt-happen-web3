"""Web3 Security Intelligence Engine — model-agnostic audit core.

The portable "intelligence": providers (Claude/DeepSeek/Codex), retrieval over the
Security Memory, a multi-model committee, the audit pipeline, a Foundry PoC harness,
and a benchmark scorer. Runs offline in dry mode; full power needs an API key
(and `forge` for PoC execution).
"""
__all__ = ["config", "providers", "retrieval", "prompt", "committee", "pipeline", "poc", "score"]
