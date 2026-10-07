from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

POC_TEMPLATE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// Auto-scaffolded PoC for: {title}
// Finding: {category} @ {location}
// Fill in setUp() + the exploit, then: forge test -vvv
import "forge-std/Test.sol";

contract PoC_{slug} is Test {{
    function setUp() public {{
        // TODO: deploy target + dependencies (or fork): vm.createSelectFork(RPC)
    }}

    function test_exploit() public {{
        // TODO: reproduce the attack path:
        // {attack}
        // Assert the broken invariant / attacker profit, e.g.:
        // assertGt(token.balanceOf(attacker), startBalance, "no profit => not exploitable");
        emit log("PoC not yet implemented");
    }}
}}
"""


def foundry_available() -> bool:
    return shutil.which("forge") is not None


def scaffold_poc(finding: dict, out_dir: str) -> str:
    slug = "".join(c if c.isalnum() else "_" for c in finding.get("title", "finding"))[:40] or "finding"
    code = POC_TEMPLATE.format(
        title=finding.get("title", ""), category=finding.get("category", ""),
        location=finding.get("location", ""), attack=finding.get("attack", ""), slug=slug,
    )
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"PoC_{slug}.t.sol"
    path.write_text(code, encoding="utf-8")
    return str(path)


def run_poc(project_dir: str) -> dict:
    """Run `forge test` if forge is installed; otherwise report the dependency (honest)."""
    if not foundry_available():
        return {"ran": False, "reason": "forge not installed — run `foundryup` to enable PoC execution",
                "passed": None, "output": ""}
    try:
        res = subprocess.run(["forge", "test", "-vv"], cwd=project_dir,
                             capture_output=True, text=True, timeout=600)
        return {"ran": True, "passed": res.returncode == 0, "output": res.stdout + res.stderr}
    except Exception as e:  # noqa: BLE001
        return {"ran": True, "passed": None, "reason": str(e), "output": ""}
