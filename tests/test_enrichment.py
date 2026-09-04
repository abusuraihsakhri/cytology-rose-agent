"""
Automated Pytest for cytology-rose-agent Enrichment Modules.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from enrichment import (
    OverviewEngine,
    Enrichment1BethesdaSystemCategoryValidationAgent,
    ImplementationEngine,
    Enrichment2NeedlePassTrackingWithAdequacyPredictionEngine,
    Enrichment3CrushArtifactQuantificationAgent,
    Enrichment4CellBlockAdequacyAssessmentEngine,
    CytologyroseagentEnrichmentSuite,
    enrichment_suite,
)

def test_enrichment_suite_execution():
    suite = CytologyroseagentEnrichmentSuite()
    res = suite.execute_all(primary_val=0.5, secondary_val=0.2)
    assert len(res) >= 1
    for k, v in res.items():
        assert v.status in ["OPTIMAL", "WARNING", "CRITICAL_ALERT"]
        assert isinstance(v.recommendations, list)

def test_enrichment_threshold_escalation():
    suite = CytologyroseagentEnrichmentSuite()
    res = suite.execute_all(primary_val=10.0, secondary_val=5.0)
    for k, v in res.items():
        assert v.status in ["WARNING", "CRITICAL_ALERT"]
        assert len(v.alerts) > 0

def test_enrichment_suite_unique_keys():
    """Verify all enrichment suite results have unique keys (no overwrites)."""
    suite = CytologyroseagentEnrichmentSuite()
    res = suite.execute_all(primary_val=0.5, secondary_val=0.2)
    # Should have 8 unique results (no duplicate keys overwriting each other)
    assert len(res) == 8
    expected_keys = {
        "OverviewEngine",
        "Enrichment1BethesdaSystemCategoryValidationAgent",
        "ImplementationEngine_needle",
        "Enrichment2NeedlePassTrackingWithAdequacyPredictionEngine",
        "ImplementationEngine_crush",
        "Enrichment3CrushArtifactQuantificationAgent",
        "ImplementationEngine_cellblock",
        "Enrichment4CellBlockAdequacyAssessmentEngine",
    }
    assert set(res.keys()) == expected_keys
