"""
Crush Artifact Quantification Agent for Cytology ROSE Agent.
Detect and quantify crush artifact in FNA smears.
"""
from dataclasses import dataclass
import math
from typing import Dict, Optional


@dataclass
class CrushArtifactResult:
    """Crush artifact analysis result."""
    crush_pct: float
    severity: str
    affected_clusters: int
    recommendation: str
    specimen_quality: str


class CrushArtifactAnalyzer:
    """Quantify crush artifacts in FNA smear specimens."""

    def quantify_crush_artifact(self, image_metrics: dict) -> dict:
        """Quantify crush artifact percentage from image analysis metrics."""
        crushed_cells = image_metrics.get("crushed_cells", 0)
        total_cells = image_metrics.get("total_cells", 0)
        for name, count in (("crushed_cells", crushed_cells), ("total_cells", total_cells)):
            if isinstance(count, bool) or not isinstance(count, (int, float)):
                raise ValueError(f"{name} must be a non-negative count")
            if not math.isfinite(count) or count < 0 or int(count) != count:
                raise ValueError(f"{name} must be a finite non-negative integer")
        if total_cells == 0 or crushed_cells > total_cells:
            raise ValueError("total_cells must be positive and at least crushed_cells")
        crush_pct = crushed_cells / total_cells * 100

        if crush_pct < 5:
            severity = "Mild"
            recommendation = "Acceptable for evaluation"
            quality = "Adequate"
        elif crush_pct < 20:
            severity = "Moderate"
            recommendation = "Request additional passes with gentler technique"
            quality = "Suboptimal"
        else:
            severity = "Severe"
            recommendation = "Specimen suboptimal; consider repeat FNA with 25G needle"
            quality = "Inadequate"

        return {
            "crush_pct": round(crush_pct, 1),
            "severity": severity,
            "affected_clusters": crushed_cells,
            "total_cells": total_cells,
            "recommendation": recommendation,
            "specimen_quality": quality,
        }

    def assess_smear_quality(self, smear_data: dict) -> dict:
        """Comprehensive smear quality assessment."""
        issues = []

        if smear_data.get("crush_pct", 0) >= 20:
            issues.append("Severe crush artifact")
        if smear_data.get("air_drying_artifact", False):
            issues.append("Air-drying artifact present")
        if smear_data.get("blood_obscuration_pct", 0) > 30:
            issues.append("Excessive blood obscuration")
        if smear_data.get("thickness_score", 0) > 3:
            issues.append("Smear too thick")

        quality_score = max(0, 100 - len(issues) * 25)

        return {
            "quality_score": quality_score,
            "issues": issues,
            "overall_grade": "A" if quality_score >= 90 else "B" if quality_score >= 70 else "C" if quality_score >= 50 else "D",
            "adequate_for_diagnosis": quality_score >= 50,
        }
