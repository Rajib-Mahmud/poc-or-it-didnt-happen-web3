from __future__ import annotations

from abc import ABC, abstractmethod

from .config import Config


class LLMProvider(ABC):
    """Model-agnostic LLM interface. Adapters implement `complete`; the rest of the
    engine never imports a vendor SDK directly."""
    name = "base"

    @abstractmethod
    def complete(self, system: str, user: str, max_tokens: int = 8000) -> str: ...


class DryRunProvider(LLMProvider):
    """Offline stub: proves the pipeline runs end-to-end with no API key.
    Deliberately returns NO findings — no real model means no real audit (honesty > theater)."""
    name = "dry"

    def complete(self, system: str, user: str, max_tokens: int = 8000) -> str:
        return (
            "## AUDIT (dry-run stub — no model was called)\n"
            "W3SEC_PROVIDER=dry, so this proves the pipeline executes end-to-end without a key.\n"
            "Set W3SEC_PROVIDER=anthropic|deepseek|openai and the matching API key for a real audit.\n"
            "FINDINGS_JSON: []\n"
        )


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, api_key: str, model: str):
        self.api_key, self.model = api_key, model

    def complete(self, system: str, user: str, max_tokens: int = 8000) -> str:
        from anthropic import Anthropic  # lazy import: only needed when actually used
        client = Anthropic(api_key=self.api_key)
        msg = client.messages.create(
            model=self.model, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(getattr(b, "text", "") for b in msg.content)


class OpenAICompatibleProvider(LLMProvider):
    """Covers OpenAI (Codex) and DeepSeek — both speak the OpenAI chat API; DeepSeek
    just needs a different base_url."""

    def __init__(self, api_key: str, model: str, base_url: str | None = None, name: str = "openai"):
        self.api_key, self.model, self.base_url, self.name = api_key, model, base_url, name

    def complete(self, system: str, user: str, max_tokens: int = 8000) -> str:
        from openai import OpenAI  # lazy import
        client = OpenAI(api_key=self.api_key, base_url=self.base_url) if self.base_url else OpenAI(api_key=self.api_key)
        resp = client.chat.completions.create(
            model=self.model, max_tokens=max_tokens,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        )
        return resp.choices[0].message.content or ""


def _need(value: str, what: str) -> None:
    if not value:
        raise RuntimeError(
            f"{what} is required for this provider. Set it in the environment. "
            f"(Use W3SEC_PROVIDER=dry to run the pipeline offline with no key.)"
        )


def get_provider(cfg: Config) -> LLMProvider:
    p = cfg.provider.lower()
    if p == "dry":
        return DryRunProvider()
    if p == "anthropic":
        _need(cfg.anthropic_key, "ANTHROPIC_API_KEY"); _need(cfg.model, "W3SEC_MODEL")
        return AnthropicProvider(cfg.anthropic_key, cfg.model)
    if p == "deepseek":
        _need(cfg.deepseek_key, "DEEPSEEK_API_KEY"); _need(cfg.model, "W3SEC_MODEL")
        return OpenAICompatibleProvider(cfg.deepseek_key, cfg.model, base_url="https://api.deepseek.com", name="deepseek")
    if p in ("openai", "codex"):
        _need(cfg.openai_key, "OPENAI_API_KEY"); _need(cfg.model, "W3SEC_MODEL")
        return OpenAICompatibleProvider(cfg.openai_key, cfg.model, name="openai")
    raise ValueError(f"Unknown W3SEC_PROVIDER={cfg.provider!r}. One of: {', '.join(PROVIDERS)}")


from .config import PROVIDERS  # noqa: E402  (kept at end to avoid clutter in the error message above)
