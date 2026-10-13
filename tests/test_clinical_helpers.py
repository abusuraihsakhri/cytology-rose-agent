"""Regression checks for non-diagnostic ROSE helpers and legacy API security."""
import pytest

from cytology_rose_agent.needle_tracker import NeedlePassTracker
from cytology_rose_agent.crush_analyzer import CrushArtifactAnalyzer


def test_needle_tracker_respects_minimum_pass_count():
    tracker = NeedlePassTracker()
    tracker.track_pass("DEMO-01", {"cellularity_score": 9})
    first = tracker.predict_adequacy("DEMO-01", "thyroid")
    assert first["adequate"] is False
    assert first["passes_needed"] >= 1

    tracker.track_pass("DEMO-01", {"cellularity_score": 9})
    assert tracker.predict_adequacy("DEMO-01", "thyroid")["adequate"] is True


@pytest.mark.parametrize("score", [float("nan"), float("inf"), -1])
def test_needle_tracker_rejects_invalid_scores(score):
    tracker = NeedlePassTracker()
    with pytest.raises(ValueError):
        tracker.track_pass("DEMO-01", {"cellularity_score": score})


@pytest.mark.parametrize("data", [
    {"total_cells": 0, "crushed_cells": 0},
    {"total_cells": 10, "crushed_cells": 11},
    {"total_cells": 10, "crushed_cells": -1},
    {"total_cells": float("inf"), "crushed_cells": 1},
])
def test_crush_analyzer_rejects_invalid_denominators(data):
    with pytest.raises(ValueError):
        CrushArtifactAnalyzer().quantify_crush_artifact(data)


def test_crush_analyzer_boundary_consistent_with_smear_qc():
    analyzer = CrushArtifactAnalyzer()
    result = analyzer.quantify_crush_artifact({"total_cells": 10, "crushed_cells": 2})
    assert result["crush_pct"] == 20
    assert result["severity"] == "Severe"
    assert "Severe crush artifact" in analyzer.assess_smear_quality(result)["issues"]


@pytest.mark.parametrize("factory", [
    "cyto_rose",
    "cytology_rose_agent.server",
])
def test_legacy_api_endpoints_require_key(monkeypatch, factory):
    from importlib import import_module
    from fastapi.testclient import TestClient

    monkeypatch.setenv("CYTOLOGY_API_KEY", "unit-test-key")
    app = import_module(factory).create_app()
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    assert client.post("/api/chat", json={"query": "status"}).status_code == 401
    assert client.post(
        "/api/chat",
        headers={"x-api-key": "unit-test-key"},
        json={"query": "status"},
    ).status_code == 200
