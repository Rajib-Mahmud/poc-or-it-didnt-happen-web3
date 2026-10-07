from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import Config
from .pipeline import run_audit
from .poc import foundry_available, scaffold_poc
from .score import score


def _benchmarks(root: str):
    base = Path(root) / "benchmarks" / "examples"
    return sorted(p for p in base.glob("*") if (p / "truth.yaml").exists()) if base.exists() else []


def _target_of(bench_dir: Path) -> Path | None:
    for name in ("Vault.sol",):
        if (bench_dir / name).exists():
            return bench_dir / name
    sols = [p for p in bench_dir.glob("*.sol") if not p.name.endswith(".t.sol") and p.name != "MockERC20.sol"]
    return sols[0] if sols else None


def _find_scope(target: str, repo_root: str, explicit: str | None) -> str:
    """scope.md defines the engagement (in-scope assets, severity bar, PoC rule, known issues).
    Use --scope if given, else auto-detect next to the target or at the repo root."""
    if explicit:
        return Path(explicit).read_text(encoding="utf-8")
    for cand in (Path(target).parent / "scope.md", Path(target).parent / "SCOPE.md",
                 Path(repo_root) / "scope.md", Path(repo_root) / "SCOPE.md"):
        if cand.exists():
            return cand.read_text(encoding="utf-8")
    return ""


def cmd_info(cfg: Config, _args) -> int:
    print(cfg.summary())
    print(f"forge installed: {foundry_available()}")
    print(f"benchmarks: {[p.name for p in _benchmarks(cfg.repo_root)]}")
    return 0


def cmd_audit(cfg: Config, args) -> int:
    scope = _find_scope(args.target, cfg.repo_root, args.scope)
    result = run_audit(args.target, cfg, scope)
    print(json.dumps({k: v for k, v in result.items() if k != "raw"}, indent=2))
    if args.show_raw:
        print("\n--- RAW ---\n" + result["raw"])
    if args.scaffold_poc:
        for f in result["findings"]:
            if str(f.get("severity", "")).lower() in ("critical", "high"):
                print("PoC scaffold:", scaffold_poc(f, str(Path(args.target).parent / "poc")))
    return 0


def cmd_score(cfg: Config, args) -> int:
    bench = Path(args.benchmark)
    truth = bench / "truth.yaml"
    target = _target_of(bench)
    if not truth.exists() or target is None:
        print(f"error: {bench} needs truth.yaml and a target .sol", file=sys.stderr)
        return 2
    result = run_audit(str(target), cfg)
    sc = score(result["findings"], str(truth))
    print(json.dumps(sc, indent=2))
    return 0


def cmd_selftest(cfg: Config, _args) -> int:
    """Prove the whole pipeline runs end-to-end on every benchmark (dry by default)."""
    benches = _benchmarks(cfg.repo_root)
    if not benches:
        print("no benchmarks found", file=sys.stderr)
        return 2
    print(f"[selftest] {cfg.summary()}")
    rows = []
    for b in benches:
        target = _target_of(b)
        if not target:
            continue
        res = run_audit(str(target), cfg)
        sc = score(res["findings"], str(b / "truth.yaml"))
        rows.append((b.name, res["tags"], res["patterns"], sc))
        print(f"  {b.name:28} tags={res['tags']} patterns={res['patterns']} "
              f"-> findings={len(res['findings'])} precision={sc['precision']} recall={sc['recall']}")
    print(f"[selftest] OK - pipeline executed on {len(rows)} targets "
          f"({'dry run: findings=0 is expected' if cfg.provider == 'dry' else cfg.provider})")
    return 0


def cmd_ingest(cfg: Config, args) -> int:
    from ingest.ingest_defihacklabs import ingest
    return ingest(cfg.repo_root, run=args.run)


def main(argv=None) -> int:
    cfg = Config()
    ap = argparse.ArgumentParser(prog="engine", description="Web3 Security Intelligence Engine")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("info").set_defaults(func=cmd_info)
    sub.add_parser("selftest").set_defaults(func=cmd_selftest)

    pa = sub.add_parser("audit"); pa.add_argument("target")
    pa.add_argument("--scope", help="path to scope.md (else auto-detected next to target / repo root)")
    pa.add_argument("--show-raw", action="store_true")
    pa.add_argument("--scaffold-poc", action="store_true"); pa.set_defaults(func=cmd_audit)

    ps = sub.add_parser("score"); ps.add_argument("benchmark"); ps.set_defaults(func=cmd_score)

    pi = sub.add_parser("ingest"); pi.add_argument("--run", action="store_true"); pi.set_defaults(func=cmd_ingest)

    args = ap.parse_args(argv)
    return args.func(cfg, args)


if __name__ == "__main__":
    raise SystemExit(main())
