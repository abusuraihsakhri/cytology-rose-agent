"""
FastAPI REST API Server for Cytology Rose Agent.
"""
import math
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Depends
from api_security import require_api_access
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")



app = FastAPI(
    title="Cytology Rose Agent API",
    description="Enterprise Distributed Component Platform (Digital Pathology & Histology Systems)",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "cytology-rose-agent", "domain": "Digital Pathology & Histology Systems", "standard": "CAP Cancer Protocols / DICOM WSI PS3.16", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics", dependencies=[Depends(require_api_access)])
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit", dependencies=[Depends(require_api_access)])
def api_audit(payload: SystemTaskPayload):
    if not all(math.isfinite(value) and value >= 0 for value in
               (payload.primary_metric, payload.secondary_metric)):
        raise HTTPException(status_code=422, detail="Metrics must be finite and non-negative")
    try:
        dossier = supervisor.process_task(payload)
        return dossier.to_dict()
    except SecurityException as exc:
        raise HTTPException(status_code=422, detail="Input rejected by identifier guard") from exc


@app.post("/api/chat", dependencies=[Depends(require_api_access)])
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        if isinstance(e, SecurityException):
            raise HTTPException(status_code=422, detail="Input rejected by identifier guard") from e
        raise


@app.get("/api/audit/logs", dependencies=[Depends(require_api_access)])
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
