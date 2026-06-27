"""
ReflexionOS — PDF report generator
Uses only the standard library + fpdf2 (pure Python).
"""
from __future__ import annotations
from models import RunResult

try:
    from fpdf import FPDF  # type: ignore
    _FPDF_AVAILABLE = True
except ImportError:
    _FPDF_AVAILABLE = False


SEVERITY_COLORS = {
    "critical": (220, 38, 38),
    "high": (234, 88, 12),
    "medium": (202, 138, 4),
    "low": (22, 163, 74),
    "info": (59, 130, 246),
}

VERDICT_COLORS = {
    "accept": (220, 38, 38),
    "borderline": (202, 138, 4),
    "reject": (22, 163, 74),
}


def _s(text: str) -> str:
    """Sanitize text to latin-1 safe characters."""
    return (
        str(text)
        .replace("\u2014", "--")
        .replace("\u2013", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2022", "*")
        .replace("\u00d7", "x")
        .encode("latin-1", errors="replace")
        .decode("latin-1")
    )


def _make_pdf_with_fpdf(result: RunResult) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Header
    pdf.set_fill_color(10, 10, 20)
    pdf.rect(0, 0, 210, 30, "F")
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, "ReflexionOS", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, "Adversarial Document Stress Test Report", ln=True, align="C")
    pdf.ln(8)

    # Metadata
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Run Metadata", ln=True)
    pdf.set_font("Helvetica", "", 9)
    meta = [
        ("Run ID", result.run_id),
        ("Timestamp", result.timestamp),
        ("Provider", result.provider),
        ("Document Type", result.document_type),
        ("Risk Lens", result.risk_lens),
        ("Issue Count", str(len(result.attacker.issues))),
        ("Risk Rating", result.referee.document_risk_rating.upper()),
        ("Total Risk Score", f"{result.attacker.total_risk_score:.1f} / 100"),
    ]
    for k, v in meta:
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(45, 6, _s(k) + ":")
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 6, _s(v), ln=True)
    pdf.ln(4)

    # Executive Summary
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Executive Summary", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5, _s(result.attacker.summary))
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(0, 5, _s(result.referee.final_verdict))
    pdf.ln(4)

    # Issues
    issue_map = {i.id: i for i in result.attacker.issues}
    defender_map = {f.issue_id: f for f in result.defender.findings}
    referee_map = {s.issue_id: s for s in result.referee.scores}

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, f"Findings ({len(result.attacker.issues)})", ln=True)

    for issue in result.attacker.issues:
        sev_color = SEVERITY_COLORS.get(issue.severity, (100, 100, 100))
        ref = referee_map.get(issue.id)
        defender = defender_map.get(issue.id)

        # Issue header bar
        pdf.set_fill_color(*sev_color)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        label = f"  {issue.id}  [{issue.severity.upper()}]  {issue.title}"
        pdf.cell(0, 8, _s(label), ln=True, fill=True)

        pdf.set_text_color(30, 30, 30)

        pdf.set_font("Helvetica", "B", 8.5)
        pdf.cell(0, 5, "Description:", ln=True)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.multi_cell(0, 4.5, _s(issue.description))

        pdf.set_font("Helvetica", "B", 8.5)
        pdf.cell(0, 5, "Evidence:", ln=True)
        pdf.set_font("Helvetica", "I", 8.5)
        pdf.multi_cell(0, 4.5, _s(issue.evidence))

        pdf.set_font("Helvetica", "B", 8.5)
        pdf.cell(0, 5, "Attacker Recommendation:", ln=True)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.multi_cell(0, 4.5, _s(issue.recommendation))

        if defender:
            pdf.set_font("Helvetica", "B", 8.5)
            pdf.cell(0, 5, "Defender -- Suggested Clause:", ln=True)
            pdf.set_font("Helvetica", "", 8.5)
            pdf.multi_cell(0, 4.5, _s(defender.suggested_clause))
            pdf.set_font("Helvetica", "B", 8.5)
            pdf.cell(0, 5, "Compliance Note:", ln=True)
            pdf.set_font("Helvetica", "", 8.5)
            pdf.multi_cell(0, 4.5, _s(defender.compliance_note))

        if ref:
            pdf.set_font("Helvetica", "B", 8.5)
            score_line = (
                f"Referee Score: {ref.overall_score:.1f}/100  |  "
                f"Evidence: {ref.evidence_strength:.0f}  |  "
                f"Impact: {ref.impact:.0f}  |  "
                f"Exploitability: {ref.exploitability:.0f}  |  "
                f"Verdict: {ref.verdict.upper()}"
            )
            pdf.set_fill_color(245, 245, 245)
            pdf.cell(0, 6, _s(score_line), ln=True, fill=True)
            pdf.set_font("Helvetica", "I", 8.5)
            pdf.multi_cell(0, 4.5, _s(ref.rationale))

        pdf.ln(3)

    # Footer
    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(
        0, 6,
        _s(f"Generated by ReflexionOS  |  Run {result.run_id}  |  {result.timestamp}"),
        align="C",
    )

    return bytes(pdf.output())


def _make_pdf_fallback(result: RunResult) -> bytes:
    lines = [
        "ReflexionOS -- Adversarial Document Stress Test Report",
        "=" * 60,
        f"Run ID: {result.run_id}",
        f"Timestamp: {result.timestamp}",
        f"Provider: {result.provider}",
        f"Risk Rating: {result.referee.document_risk_rating.upper()}",
        f"Total Risk Score: {result.attacker.total_risk_score:.1f}/100",
        "",
        "SUMMARY",
        result.attacker.summary,
        "",
        "FINAL VERDICT",
        result.referee.final_verdict,
        "",
    ]
    for issue in result.attacker.issues:
        lines += [
            f"--- {issue.id}: {issue.title} [{issue.severity.upper()}] ---",
            f"Category: {issue.category}",
            f"Description: {issue.description}",
            f"Evidence: {issue.evidence}",
            f"Recommendation: {issue.recommendation}",
            "",
        ]
    return "\n".join(lines).encode("utf-8")


def generate_pdf(result: RunResult) -> bytes:
    """Generate a PDF report. Falls back to plain text if fpdf2 missing."""
    if _FPDF_AVAILABLE:
        return _make_pdf_with_fpdf(result)
    return _make_pdf_fallback(result)
