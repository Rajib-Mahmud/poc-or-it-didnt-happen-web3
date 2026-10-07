from __future__ import annotations

from pathlib import Path

SKILL_REL = ".claude/skills/audit/SKILL.md"
KNOWLEDGE = ["knowledge/taxonomy.md", "knowledge/invariants.md", "knowledge/formulas.md"]

OUTPUT_CONTRACT = """
After your analysis, output findings as a single JSON array on a line starting with
`FINDINGS_JSON:` (empty array `[]` if none — reporting nothing on safe code is correct).
Each finding object: {"title","severity"(critical|high|medium|low|info),"category",
"location","root_cause","attack","confidence"(0-100)}.
"""


def _read(repo_root: str, rel: str) -> str:
    p = Path(repo_root) / rel
    return p.read_text(encoding="utf-8") if p.exists() else ""


def build_audit_prompt(
    repo_root: str,
    target_name: str,
    target_code: str,
    retrieved: list[dict],
    acceptance: str = "",
) -> tuple[str, str]:
    """system = the audit methodology (SKILL.md). user = references + retrieved memory + target."""
    system = _read(repo_root, SKILL_REL) or "You are a senior Web3 smart-contract security auditor."

    refs = "\n\n".join(f"# {rel}\n{_read(repo_root, rel)}" for rel in KNOWLEDGE)
    mem = "\n\n".join(p["raw"] for p in retrieved) or "(no specific patterns matched)"

    user_parts = [
        "## Reference knowledge\n" + refs,
        "## Retrieved Security-Memory patterns (relevant to this target)\n" + mem,
    ]
    if acceptance:
        user_parts.append("## Program acceptance criteria (a finding ships ONLY if it meets these)\n" + acceptance)
    user_parts.append(f"## TARGET: {target_name}\n```solidity\n{target_code}\n```")
    user_parts.append(OUTPUT_CONTRACT)
    return system, "\n\n".join(user_parts)
