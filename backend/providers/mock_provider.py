"""
ReflexionOS — Mock Provider
Returns pre-baked structured responses for demo / CI use.
"""
from __future__ import annotations
from typing import Any
from .base import BaseProvider


_MOCK_ATTACKER = {
    "issues": [
        {
            "id": "ATK-001",
            "title": "Unlimited Liability Exposure",
            "severity": "critical",
            "category": "Liability",
            "description": "Section 7.2 contains no liability cap. This exposes the signing party to uncapped damages far exceeding the contract value.",
            "evidence": "\"Party A shall be liable for any and all damages arising from...\" (Section 7.2)",
            "recommendation": "Insert a mutual liability cap tied to fees paid in the preceding 12 months. Standard enterprise cap is 12× monthly fees.",
        },
        {
            "id": "ATK-002",
            "title": "Vague Data Retention Language",
            "severity": "high",
            "category": "Data Privacy",
            "description": "Section 12 references data retention without specifying a maximum retention period, violating GDPR Article 5(1)(e).",
            "evidence": "\"Data will be retained for a reasonable period...\" (Section 12)",
            "recommendation": "Define explicit retention schedules: e.g., 90 days post-termination, then secure deletion with written confirmation.",
        },
        {
            "id": "ATK-003",
            "title": "Overly Broad IP Assignment",
            "severity": "high",
            "category": "Intellectual Property",
            "description": "Section 9 assigns all work product to the counterparty without carve-outs for pre-existing IP or background technology.",
            "evidence": "\"All inventions, discoveries, and work product...shall be the exclusive property of...\" (Section 9)",
            "recommendation": "Add a Schedule A listing pre-existing IP. Limit assignment to foreground IP created solely for this engagement.",
        },
        {
            "id": "ATK-004",
            "title": "Unilateral Termination with No Notice",
            "severity": "medium",
            "category": "Contract Risk",
            "description": "Section 15 permits the counterparty to terminate for convenience with zero days' notice, creating operational risk.",
            "evidence": "\"Either party may terminate this Agreement at any time without cause...\" (Section 15)",
            "recommendation": "Require minimum 30-day written notice for termination for convenience to allow transition planning.",
        },
        {
            "id": "ATK-005",
            "title": "Missing Governing Law Clause",
            "severity": "medium",
            "category": "Jurisdiction",
            "description": "No governing law or jurisdiction is specified. Disputes would require expensive conflict-of-laws analysis.",
            "evidence": "No governing law clause found in document.",
            "recommendation": "Add a clear governing law clause specifying jurisdiction, venue, and waiver of jury trial if appropriate.",
        },
    ],
    "summary": "The document contains 5 material weaknesses across liability, data privacy, IP ownership, contract risk, and jurisdiction. The unlimited liability exposure is the highest-priority item requiring immediate correction.",
    "total_risk_score": 72.5,
}

_MOCK_DEFENDER = {
    "findings": [
        {
            "issue_id": "ATK-001",
            "improved_wording": "Each party's aggregate liability under this Agreement shall not exceed the total fees paid by Customer in the twelve (12) months preceding the event giving rise to liability.",
            "suggested_clause": "Mutual Liability Cap: Notwithstanding any other provision, neither party's total liability shall exceed 12× the monthly average fees paid hereunder.",
            "risk_mitigation": "A mutual cap protects both parties. Tie exceptions only to gross negligence, fraud, and IP indemnity.",
            "compliance_note": "Consistent with ICC Model Contract guidelines and standard SaaS enterprise agreements.",
        },
        {
            "issue_id": "ATK-002",
            "improved_wording": "Personal data shall be retained for no longer than ninety (90) days following contract termination, after which it shall be securely deleted and a written deletion certificate provided within 14 days.",
            "suggested_clause": "Data Retention Schedule: All personal data processed under this Agreement shall be deleted within 90 days of termination.",
            "risk_mitigation": "Explicit schedules eliminate GDPR Article 5(1)(e) violations and provide audit trails.",
            "compliance_note": "Aligns with GDPR, CCPA, and ISO 27001 Annex A.8.3 controls.",
        },
        {
            "issue_id": "ATK-003",
            "improved_wording": "Only Foreground IP (IP created specifically and solely under this Agreement) shall be assigned. Pre-existing IP, as listed in Schedule A, remains the exclusive property of the originating party.",
            "suggested_clause": "Add Schedule A: Background IP Registry listing all pre-existing tools, libraries, and frameworks.",
            "risk_mitigation": "A Schedule A registry and foreground/background IP split is industry standard practice.",
            "compliance_note": "Consistent with WIPO recommended IP clauses for service agreements.",
        },
        {
            "issue_id": "ATK-004",
            "improved_wording": "Either party may terminate this Agreement for convenience upon thirty (30) days' prior written notice to the other party.",
            "suggested_clause": "Termination for Convenience: Either party may terminate with 30 days written notice. During notice period, work shall continue at current rates.",
            "risk_mitigation": "Provides transition runway and protects both parties from operational disruption.",
            "compliance_note": "30-day notice is the commercial standard for enterprise SaaS and service agreements.",
        },
        {
            "issue_id": "ATK-005",
            "improved_wording": "This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to conflict of laws principles.",
            "suggested_clause": "Governing Law: This Agreement is governed by Delaware law. Exclusive jurisdiction: Court of Chancery, New Castle County.",
            "risk_mitigation": "Choosing a predictable, well-developed jurisdiction reduces dispute resolution costs significantly.",
            "compliance_note": "Delaware is universally accepted for US enterprise contracts due to its mature commercial law framework.",
        },
    ],
    "overall_recommendation": "The document requires 5 targeted revisions before execution. Priority order: (1) liability cap, (2) governing law, (3) IP schedule, (4) data retention, (5) termination notice. Estimated revision time with competent counsel: 2–4 hours.",
}

_MOCK_REFEREE = {
    "scores": [
        {
            "issue_id": "ATK-001",
            "evidence_strength": 95.0,
            "impact": 98.0,
            "exploitability": 90.0,
            "overall_score": 94.3,
            "verdict": "accept",
            "rationale": "Unlimited liability is directly evidenced in Section 7.2. Legal risk is material and well-documented. Defender's proposed cap is industry-standard.",
        },
        {
            "issue_id": "ATK-002",
            "evidence_strength": 88.0,
            "impact": 82.0,
            "exploitability": 75.0,
            "overall_score": 81.7,
            "verdict": "accept",
            "rationale": "Vague retention language clearly conflicts with GDPR Article 5(1)(e). Evidence is direct. Defender's 90-day schedule is a reasonable and enforceable fix.",
        },
        {
            "issue_id": "ATK-003",
            "evidence_strength": 92.0,
            "impact": 88.0,
            "exploitability": 80.0,
            "overall_score": 86.7,
            "verdict": "accept",
            "rationale": "IP assignment clause is unambiguously broad. The lack of a Schedule A for pre-existing IP is a standard oversight with serious long-term consequences.",
        },
        {
            "issue_id": "ATK-004",
            "evidence_strength": 85.0,
            "impact": 70.0,
            "exploitability": 65.0,
            "overall_score": 73.3,
            "verdict": "accept",
            "rationale": "Zero-notice termination is clearly stated. Impact is operational rather than legal, but still material for any ongoing service engagement.",
        },
        {
            "issue_id": "ATK-005",
            "evidence_strength": 75.0,
            "impact": 65.0,
            "exploitability": 55.0,
            "overall_score": 65.0,
            "verdict": "borderline",
            "rationale": "Omission of governing law is real but not always deliberate. Courts can imply governing law from context. Adding a clause is best practice, but the risk is lower than other findings.",
        },
    ],
    "final_verdict": "Document is HIGH RISK. Four findings are fully accepted with strong evidence. One is borderline. Immediate revision is recommended before execution.",
    "document_risk_rating": "high",
}


class MockProvider(BaseProvider):
    """Returns deterministic mock data. No network calls."""

    @property
    def name(self) -> str:
        return "mock"

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        seed: int | None = None,
    ) -> dict[str, Any]:
        # Route by role keyword in system_prompt (check most specific first)
        sp = system_prompt.lower()
        if "referee" in sp:
            return _MOCK_REFEREE
        elif "defender" in sp:
            return _MOCK_DEFENDER
        elif "attacker" in sp:
            return _MOCK_ATTACKER
        return {}
