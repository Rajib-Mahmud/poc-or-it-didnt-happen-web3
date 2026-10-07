from __future__ import annotations

import json
import re
from pathlib import Path

from .config import Config
from .committee import Committee
from .prompt import build_audit_prompt
from .providers import get_provider
from .retrieval import infer_tags, retrieve


def parse_findings(raw: str) -> list[dict]:
    """Extract the JSON array after the FINDINGS_JSON: marker. Returns [] on any problem
    (never fabricates)."""
    m = re.search(r"FINDINGS_JSON:\s*(\[.*)", raw, re.DOTALL)
    if not m:
        return []
    blob = m.group(1).strip()
    # Trim to the matching end bracket of the first array.
    depth, end = 0, None
    for i, ch in enumerate(blob):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        return []
    try:
        data = json.loads(blob[:end])
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def run_audit(target_path: str, cfg: Config | None = None, acceptance: str = "") -> dict:
    cfg = cfg or Config()
    code = Path(target_path).read_text(encoding="utf-8")
    name = Path(target_path).name

    tags = infer_tags(code)
    retrieved = retrieve(tags, cfg.repo_root)
    system, user = build_audit_prompt(cfg.repo_root, name, code, retrieved, acceptance)

    provider = get_provider(cfg)
    if cfg.committee:
        raw = Committee(provider).audit(system, user, cfg.max_tokens)
        mode = f"committee({provider.name})"
    else:
        raw = provider.complete(system, user, cfg.max_tokens)
        mode = provider.name

    return {
        "target": str(target_path),
        "tags": tags,
        "patterns": [p["id"] for p in retrieved],
        "provider": mode,
        "findings": parse_findings(raw),
        "raw": raw,
    }
