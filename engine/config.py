from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

PROVIDERS = ("dry", "anthropic", "deepseek", "openai", "codex")


def _repo_root_default() -> str:
    # Walk up from CWD looking for the repo marker (ROADMAP.md); fall back to CWD.
    p = Path(os.getenv("W3SEC_REPO_ROOT", os.getcwd())).resolve()
    for cand in [p, *p.parents]:
        if (cand / "ROADMAP.md").exists() and (cand / "knowledge").exists():
            return str(cand)
    return str(p)


@dataclass
class Config:
    """Engine configuration, driven entirely by environment variables so the same
    code runs under any host (Claude Code / Codex / DeepSeek) with zero code change."""
    provider: str = field(default_factory=lambda: os.getenv("W3SEC_PROVIDER", "dry").lower())
    model: str = field(default_factory=lambda: os.getenv("W3SEC_MODEL", ""))
    committee: bool = field(default_factory=lambda: os.getenv("W3SEC_COMMITTEE", "0") == "1")
    max_tokens: int = field(default_factory=lambda: int(os.getenv("W3SEC_MAX_TOKENS", "8000")))

    anthropic_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    openai_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    deepseek_key: str = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", ""))

    repo_root: str = field(default_factory=_repo_root_default)

    def summary(self) -> str:
        keys = []
        if self.anthropic_key: keys.append("anthropic")
        if self.openai_key: keys.append("openai")
        if self.deepseek_key: keys.append("deepseek")
        return (f"provider={self.provider} model={self.model or '(unset)'} "
                f"committee={self.committee} keys={keys or 'none'} root={self.repo_root}")
