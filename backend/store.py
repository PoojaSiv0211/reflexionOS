"""
ReflexionOS — JSONL trace store
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Optional

from models import RunResult

TRACES_DIR = Path(__file__).parent / "traces"
TRACES_DIR.mkdir(exist_ok=True)


def save(result: RunResult) -> None:
    """Append a run result to the JSONL store."""
    path = TRACES_DIR / f"{result.run_id}.jsonl"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(result.model_dump_json() + "\n")


def load(run_id: str) -> Optional[RunResult]:
    """Load a run result by ID. Returns None if not found."""
    path = TRACES_DIR / f"{run_id}.jsonl"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as fh:
        line = fh.readline().strip()
        if not line:
            return None
        data = json.loads(line)
        return RunResult.model_validate(data)


def list_runs(limit: int = 50) -> list[dict]:
    """Return metadata for recent runs, newest first."""
    files = sorted(TRACES_DIR.glob("*.jsonl"), key=os.path.getmtime, reverse=True)
    results = []
    for f in files[:limit]:
        try:
            with open(f, encoding="utf-8") as fh:
                data = json.loads(fh.readline())
            results.append({
                "run_id": data["run_id"],
                "timestamp": data["timestamp"],
                "provider": data["provider"],
                "document_type": data["document_type"],
                "risk_lens": data["risk_lens"],
                "risk_rating": data["referee"]["document_risk_rating"],
                "issue_count": len(data["attacker"]["issues"]),
            })
        except Exception:
            continue
    return results
