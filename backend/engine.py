"""
ReflexionOS — Three-agent adversarial reasoning engine
"""
from __future__ import annotations
import json
from typing import Any

from providers.base import BaseProvider
from models import (
    AttackerOutput,
    DefenderOutput,
    RefereeOutput,
    RunRequest,
)


# ─── Prompt builders ──────────────────────────────────────────────────────────

def _attacker_prompts(req: RunRequest) -> tuple[str, str]:
    system = (
        "You are the ATTACKER agent in ReflexionOS, an adversarial document "
        "stress-testing platform. Your role is to think like a hostile lawyer, "
        "security auditor, or adversarial counterparty. You must find every "
        "exploitable weakness in the document. Be ruthless, specific, and precise. "
        "Every issue MUST cite exact evidence from the document text."
    )
    schema = {
        "issues": [
            {
                "id": "ATK-NNN",
                "title": "string",
                "severity": "critical|high|medium|low|info",
                "category": "string",
                "description": "string",
                "evidence": "exact quote or location from document",
                "recommendation": "string",
            }
        ],
        "summary": "string",
        "total_risk_score": "number 0-100",
    }
    user = (
        f"Document Type: {req.document_type}\n"
        f"Risk Lens: {req.risk_lens}\n"
        f"Maximum Issues to Return: {req.max_issues}\n\n"
        f"DOCUMENT:\n{req.document}\n\n"
        f"Return JSON matching this schema exactly:\n{json.dumps(schema, indent=2)}"
    )
    return system, user


def _defender_prompts(req: RunRequest, attacker: AttackerOutput) -> tuple[str, str]:
    issues_json = json.dumps(
        [i.model_dump() for i in attacker.issues], indent=2
    )
    system = (
        "You are the DEFENDER agent in ReflexionOS. Your role is to respond "
        "constructively to every attacker finding. Provide improved wording, "
        "suggested replacement clauses, risk mitigations, and compliance notes. "
        "Be practical and implementation-focused. Base improvements on industry "
        "standards (GDPR, CCPA, ISO 27001, ICC model contracts, WIPO guidelines)."
    )
    schema = {
        "findings": [
            {
                "issue_id": "ATK-NNN",
                "improved_wording": "string",
                "suggested_clause": "string",
                "risk_mitigation": "string",
                "compliance_note": "string",
            }
        ],
        "overall_recommendation": "string",
    }
    user = (
        f"Document Type: {req.document_type}\n"
        f"Risk Lens: {req.risk_lens}\n\n"
        f"ORIGINAL DOCUMENT:\n{req.document}\n\n"
        f"ATTACKER FINDINGS:\n{issues_json}\n\n"
        f"Return JSON matching this schema exactly:\n{json.dumps(schema, indent=2)}"
    )
    return system, user


def _referee_prompts(
    req: RunRequest, attacker: AttackerOutput, defender: DefenderOutput
) -> tuple[str, str]:
    issues_json = json.dumps(
        [i.model_dump() for i in attacker.issues], indent=2
    )
    defender_json = json.dumps(defender.model_dump(), indent=2)
    system = (
        "You are the REFEREE agent in ReflexionOS. Your role is to objectively "
        "evaluate every attacker finding. Score each issue on Evidence Strength, "
        "Impact, and Exploitability (each 0-100). Provide an Overall Score and a "
        "Verdict (accept/reject/borderline) with a clear rationale. Be objective "
        "and consistent. Consider both the attacker's evidence and the defender's "
        "proposed mitigations when forming your verdict."
    )
    schema = {
        "scores": [
            {
                "issue_id": "ATK-NNN",
                "evidence_strength": "number 0-100",
                "impact": "number 0-100",
                "exploitability": "number 0-100",
                "overall_score": "number 0-100",
                "verdict": "accept|reject|borderline",
                "rationale": "string",
            }
        ],
        "final_verdict": "string",
        "document_risk_rating": "critical|high|medium|low",
    }
    user = (
        f"Document Type: {req.document_type}\n"
        f"Risk Lens: {req.risk_lens}\n\n"
        f"ATTACKER FINDINGS:\n{issues_json}\n\n"
        f"DEFENDER RESPONSES:\n{defender_json}\n\n"
        f"Return JSON matching this schema exactly:\n{json.dumps(schema, indent=2)}"
    )
    return system, user


# ─── Engine ───────────────────────────────────────────────────────────────────

class ReasoningEngine:
    """Orchestrates the three-agent adversarial reasoning pipeline."""

    def __init__(self, provider: BaseProvider) -> None:
        self._provider = provider

    def run(
        self,
        req: RunRequest,
        seed: int | None = None,
    ) -> tuple[AttackerOutput, DefenderOutput, RefereeOutput]:
        temperature = 0.0 if req.deterministic else 0.7

        # ── Pass 1: Attacker ─────────────────────────────────────────────────
        a_sys, a_user = _attacker_prompts(req)
        a_raw = self._provider.generate_json(a_sys, a_user, temperature, seed)
        attacker = AttackerOutput.model_validate(a_raw)

        # ── Pass 2: Defender ─────────────────────────────────────────────────
        d_sys, d_user = _defender_prompts(req, attacker)
        d_raw = self._provider.generate_json(d_sys, d_user, temperature, seed)
        defender = DefenderOutput.model_validate(d_raw)

        # ── Pass 3: Referee ──────────────────────────────────────────────────
        r_sys, r_user = _referee_prompts(req, attacker, defender)
        r_raw = self._provider.generate_json(r_sys, r_user, temperature, seed)
        referee = RefereeOutput.model_validate(r_raw)

        return attacker, defender, referee
