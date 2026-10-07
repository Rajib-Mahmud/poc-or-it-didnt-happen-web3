from __future__ import annotations

import re
from pathlib import Path

# Target-type inference: map code keywords -> tags. Deliberately simple and transparent;
# an embedding backend can replace/augment this later (see ROADMAP M-retrieval).
_TAG_RULES: list[tuple[str, str]] = [
    (r"erc4626|previewredeem|previewdeposit|totalassets|shares", "vault"),
    (r"erc4626|previewredeem|previewdeposit", "erc4626"),
    (r"\bvault\b", "vault"),
    (r"borrow|collateral|liquidat|healthfactor|ltv", "lending"),
    (r"swap|reserve|getreserves|amountout|x\s*\*\s*y", "amm"),
    (r"oracle|latestanswer|latestrounddata|getprice|twap", "oracle"),
    (r"bridge|crosschain|chainid|trustedremote|relayer|lzreceive", "bridge"),
    (r"vrf|randomwords|raffle|sweepstake|wave|winner", "randomness"),
    (r"propos|vote|quorum|timelock|delegat", "governance"),
    (r"permit|eip712|ecrecover|nonce|signature", "signature"),
    (r"delegatecall|upgradeto|initializ|proxy|implementation", "proxy"),
    (r"stake|reward|payout|apy|referral|commission", "staking"),
]

# Fallback patterns to always consider for any fund-holding contract.
_ALWAYS = ["P1", "P4"]  # reentrancy, access-control/init


def infer_tags(code: str) -> list[str]:
    low = code.lower()
    tags: list[str] = []
    for pat, tag in _TAG_RULES:
        if re.search(pat, low) and tag not in tags:
            tags.append(tag)
    return tags


def _patterns_path(repo_root: str) -> Path:
    return Path(repo_root) / "memory" / "patterns.md"


def _parse_patterns(text: str) -> list[dict]:
    """Light parser for memory/patterns.md entries (id + bug_class + applies_to)."""
    out = []
    # Each entry starts at "- id: P<n>"
    blocks = re.split(r"\n\s*- id:\s*", text)
    for b in blocks[1:]:
        pid = b.splitlines()[0].strip()
        bug = _field(b, "bug_class")
        applies = _list_field(b, "applies_to")
        out.append({"id": pid, "bug_class": bug, "applies_to": applies, "raw": "- id: " + b.strip()})
    return out


def _field(block: str, key: str) -> str:
    m = re.search(rf"{key}:\s*(.+)", block)
    return m.group(1).strip().strip('"') if m else ""


def _list_field(block: str, key: str) -> list[str]:
    m = re.search(rf"{key}:\s*\[(.*?)\]", block)
    if not m:
        return []
    return [x.strip().strip('"') for x in m.group(1).split(",") if x.strip()]


def _idnum(pid: str) -> int:
    m = re.search(r"\d+", pid)
    return int(m.group()) if m else 9999


def retrieve(tags: list[str], repo_root: str, limit: int = 8) -> list[dict]:
    """Return the memory patterns relevant to the given target tags (retrieval, not dump)."""
    pth = _patterns_path(repo_root)
    if not pth.exists():
        return []
    patterns = _parse_patterns(pth.read_text(encoding="utf-8"))
    wanted = set(tags)
    scored = []
    for p in patterns:
        score = len(wanted.intersection(p["applies_to"]))
        if p["id"] in _ALWAYS:
            score += 1
        if score > 0:
            scored.append((score, p))
    scored.sort(key=lambda x: (-x[0], _idnum(x[1]["id"])))
    return [p for _, p in scored[:limit]]
