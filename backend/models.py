"""
ReflexionOS — Data models
"""
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime


# ─── Issue schema ────────────────────────────────────────────────────────────

class Issue(BaseModel):
    id: str
    title: str
    severity: Literal["critical", "high", "medium", "low", "info"]
    category: str
    description: str
    evidence: str
    recommendation: str


class AttackerOutput(BaseModel):
    issues: list[Issue]
    summary: str
    total_risk_score: float = Field(ge=0, le=100)


# ─── Defender schema ─────────────────────────────────────────────────────────

class DefenderFinding(BaseModel):
    issue_id: str
    improved_wording: str
    suggested_clause: str
    risk_mitigation: str
    compliance_note: str


class DefenderOutput(BaseModel):
    findings: list[DefenderFinding]
    overall_recommendation: str


# ─── Referee schema ──────────────────────────────────────────────────────────

class RefereeScore(BaseModel):
    issue_id: str
    evidence_strength: float = Field(ge=0, le=100)
    impact: float = Field(ge=0, le=100)
    exploitability: float = Field(ge=0, le=100)
    overall_score: float = Field(ge=0, le=100)
    verdict: Literal["accept", "reject", "borderline"]
    rationale: str


class RefereeOutput(BaseModel):
    scores: list[RefereeScore]
    final_verdict: str
    document_risk_rating: Literal["critical", "high", "medium", "low"]


# ─── Run schema ───────────────────────────────────────────────────────────────

class RunRequest(BaseModel):
    document: str
    document_type: str = "contract"
    risk_lens: str = "legal"
    deterministic: bool = True
    max_issues: int = Field(default=10, ge=1, le=20)


class RunResult(BaseModel):
    run_id: str
    timestamp: str
    provider: str
    seed: Optional[int]
    document_type: str
    risk_lens: str
    attacker: AttackerOutput
    defender: DefenderOutput
    referee: RefereeOutput
