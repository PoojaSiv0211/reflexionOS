"""
ReflexionOS — FastAPI backend
"""
from __future__ import annotations
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from models import RunRequest, RunResult
from engine import ReasoningEngine
import store
import report as report_gen
from providers.mock_provider import MockProvider
from providers.bedrock_provider import BedrockNovaProvider

# ─── Provider selection ───────────────────────────────────────────────────────

def _build_provider():
    mode = os.getenv("REFLEXION_PROVIDER", "mock").lower()
    if mode == "bedrock":
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        return BedrockNovaProvider(region=region)
    return MockProvider()


PROVIDER = _build_provider()
ENGINE = ReasoningEngine(PROVIDER)

# ─── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(title="ReflexionOS", version="1.0.0")

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
def serve_frontend():
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"status": "ReflexionOS backend running. Frontend not found."}


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "provider": PROVIDER.name,
        "version": "1.0.0",
    }


@app.post("/api/run")
def run_analysis(req: RunRequest) -> RunResult:
    seed = 42 if req.deterministic else None

    try:
        attacker, defender, referee = ENGINE.run(req, seed=seed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    result = RunResult(
        run_id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        provider=PROVIDER.name,
        seed=seed,
        document_type=req.document_type,
        risk_lens=req.risk_lens,
        attacker=attacker,
        defender=defender,
        referee=referee,
    )
    store.save(result)
    return result


@app.get("/api/replay/{run_id}")
def replay(run_id: str) -> RunResult:
    result = store.load(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Run {run_id!r} not found.")
    return result


@app.get("/api/runs")
def list_runs():
    return store.list_runs()


@app.get("/api/report/{run_id}")
def get_report(run_id: str):
    result = store.load(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Run {run_id!r} not found.")

    pdf_bytes = report_gen.generate_pdf(result)
    media_type = "application/pdf"
    filename = f"reflexionos-{run_id[:8]}.pdf"

    return Response(
        content=pdf_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
