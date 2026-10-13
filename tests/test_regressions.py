"""Regression tests for audit integrity, CSV processing, and API exposure."""
import csv

from agents.base import AuditTrail
from cli import main


def test_audit_signatures_detect_modified_metadata():
    audit = AuditTrail(secret_key="test-only-strong-key")
    audit.log("worker", "system", "created", {"task_id": "T-1"})
    audit.log("worker", "system", "checked", {"task_id": "T-2"})
    assert audit.verify_integrity()

    audit.logs[-1]["event_type"] = "forged"
    assert not audit.verify_integrity()
    audit.logs[-1]["event_type"] = "checked"
    assert audit.verify_integrity()

    audit.logs[-1]["current_hash"] = "0" * 64
    assert not audit.verify_integrity()


def test_audit_snapshots_cannot_modify_live_ledger():
    audit = AuditTrail(secret_key="test-only-strong-key")
    audit.log("worker", "system", "created", {"task_id": "T-1"})
    snapshot = audit.get_trail()
    snapshot[0]["event_type"] = "forged"
    snapshot.clear()
    assert audit.verify_integrity()
    assert len(audit.get_trail()) == 1


def test_batch_parses_false_strings_and_legacy_headers(tmp_path):
    source = tmp_path / "legacy.csv"
    output = tmp_path / "result.csv"
    source.write_text(
        "case_id,patient_synthetic_id,metric_primary,metric_secondary,is_stat,status_flag\n"
        "C-1,SYNTH-01,12,4,False,NORMAL\n"
        "C-2,SYNTH-02,28,13,True,DISCORDANT\n",
        encoding="utf-8",
    )
    assert main(["batch", "-i", str(source), "-o", str(output)]) == 0
    with output.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert rows[0]["overall_urgency"] == "ROUTINE"
    assert rows[1]["overall_urgency"] == "CRITICAL_STAT_PANIC"


def test_batch_rejects_invalid_boolean_without_writing_file(tmp_path):
    source = tmp_path / "broken.csv"
    output = tmp_path / "out.csv"
    source.write_text(
        "task_id,target_identifier,primary_metric,is_critical_flag\n"
        "T-1,SPECIMEN-1,10,sometimes\n",
        encoding="utf-8",
    )
    assert main(["batch", "-i", str(source), "-o", str(output)]) == 1
    assert not output.exists()


def test_api_restricts_sensitive_endpoints(monkeypatch):
    from fastapi.testclient import TestClient
    from agents.api import app

    monkeypatch.setenv("CYTOLOGY_API_KEY", "test-only-api-key")
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    assert client.get("/metrics").status_code == 401
    assert client.get("/api/audit/logs").status_code == 401
    assert client.post("/api/chat", json={"query": "status"}).status_code == 401

    headers = {"x-api-key": "test-only-api-key"}
    assert client.get("/metrics", headers=headers).status_code == 200
    payload = {
        "task_id": "T-1", "target_identifier": "SPECIMEN-1",
        "primary_metric": 10, "attributes": {"contact": "someone@example.com"},
    }
    assert client.post("/api/audit", json=payload, headers=headers).status_code == 422

    for invalid in (-1, "NaN", "Infinity"):
        response = client.post(
            "/api/audit",
            json={"task_id": "T-2", "target_identifier": "DEMO-02", "primary_metric": invalid},
            headers=headers,
        )
        assert response.status_code == 422
