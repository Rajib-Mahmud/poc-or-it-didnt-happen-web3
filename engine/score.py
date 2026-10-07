from __future__ import annotations

from pathlib import Path

VULN_SEVERITIES = {"critical", "high", "medium", "low"}


def _load_yaml(path: Path):
    try:
        import yaml  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("pyyaml is required for scoring: pip install pyyaml") from e
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def score(findings: list[dict], truth_path: str) -> dict:
    """Score audit findings against a benchmark truth.yaml.

    - expected[]            : real vulnerabilities (must_find => counts toward recall)
    - negative_cases[]      : reporting any as a vuln is a false positive
    Matching is by bug `class`/`category` overlap (coarse but transparent).
    """
    truth = _load_yaml(Path(truth_path))
    expected = truth.get("expected", []) or []
    must_find = [e for e in expected if e.get("must_find")]

    reported_vulns = [f for f in findings if str(f.get("severity", "")).lower() in VULN_SEVERITIES]

    def cls(x: str) -> str:
        return (x or "").lower().split("/")[0]

    expected_classes = {cls(e.get("class", "")) for e in expected}

    tp_set, fp = set(), 0
    for f in reported_vulns:
        c = cls(f.get("category", ""))
        if c and c in expected_classes:
            tp_set.add(c)
        else:
            fp += 1

    tp = len(tp_set)
    fn = max(0, len({cls(e.get("class", "")) for e in must_find}) - tp)

    precision = None if (tp + fp) == 0 else round(tp / (tp + fp), 3)
    recall = None if (tp + fn) == 0 else round(tp / (tp + fn), 3)

    return {
        "benchmark": truth.get("name", Path(truth_path).parent.name),
        "tp": tp, "fp": fp, "fn": fn,
        "precision": precision, "recall": recall,
        "reported": len(reported_vulns), "expected": len(expected),
    }
