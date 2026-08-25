"""
Needle Pass Tracking with Adequacy Prediction for Cytology ROSE Agent.
Track FNA needle passes in real-time and predict specimen adequacy.
"""
import datetime
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class NeedlePassRecord:
    """Record of a single FNA needle pass."""
    case_id: str
    pass_number: int
    cellularity_score: float
    needle_gauge: int
    technique: str
    timestamp: str


class NeedlePassTracker:
    """Track FNA needle passes and predict specimen adequacy."""

    ORGAN_THRESHOLDS = {
        "thyroid": {"min_cellularity": 6.0, "min_passes": 2, "max_passes": 6},
        "breast": {"min_cellularity": 8.0, "min_passes": 3, "max_passes": 8},
        "lymph_node": {"min_cellularity": 4.0, "min_passes": 2, "max_passes": 5},
        "pancreas": {"min_cellularity": 6.0, "min_passes": 3, "max_passes": 6},
        "salivary": {"min_cellularity": 5.0, "min_passes": 2, "max_passes": 6},
        "lung": {"min_cellularity": 6.0, "min_passes": 2, "max_passes": 5},
    }

    def __init__(self):
        self.pass_history: Dict[str, List[NeedlePassRecord]] = {}

    def track_pass(self, case_id: str, pass_data: dict) -> NeedlePassRecord:
        passes = self.pass_history.get(case_id, [])
        record = NeedlePassRecord(
            case_id=case_id,
            pass_number=len(passes) + 1,
            cellularity_score=pass_data.get("cellularity_score", 0),
            needle_gauge=pass_data.get("needle_gauge", 25),
            technique=pass_data.get("technique", "standard"),
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )
        self.pass_history.setdefault(case_id, []).append(record)
        return record

    def predict_adequacy(self, case_id: str, target_organ: str = "thyroid") -> dict:
        passes = self.pass_history.get(case_id, [])
        if not passes:
            return {"adequate": False, "passes_needed": 1, "recommendation": "Begin FNA passes"}

        current_cellularity = sum(p.cellularity_score for p in passes) / len(passes)
        total_passes = len(passes)
        thresholds = self.ORGAN_THRESHOLDS.get(target_organ, self.ORGAN_THRESHOLDS["thyroid"])

        if current_cellularity >= thresholds["min_cellularity"]:
            return {
                "adequate": True,
                "passes_completed": total_passes,
                "current_cellularity": round(current_cellularity, 1),
                "recommendation": "Specimen adequate for evaluation",
            }

        remaining = max(0, int((thresholds["min_cellularity"] - current_cellularity) / 2))
        if total_passes >= thresholds["max_passes"]:
            return {
                "adequate": False,
                "passes_completed": total_passes,
                "current_cellularity": round(current_cellularity, 1),
                "recommendation": f"Maximum passes reached ({total_passes}); evaluate current specimen",
                "at_max_passes": True,
            }

        return {
            "adequate": False,
            "passes_completed": total_passes,
            "passes_needed": remaining,
            "current_cellularity": round(current_cellularity, 1),
            "threshold": thresholds["min_cellularity"],
            "recommendation": f"Request {remaining} additional passes",
        }

    def get_pass_summary(self, case_id: str) -> dict:
        passes = self.pass_history.get(case_id, [])
        if not passes:
            return {"total_passes": 0}

        cellularity_scores = [p.cellularity_score for p in passes]
        return {
            "total_passes": len(passes),
            "mean_cellularity": round(sum(cellularity_scores) / len(cellularity_scores), 1),
            "max_cellularity": round(max(cellularity_scores), 1),
            "cellularity_trend": "Improving" if len(passes) > 1 and cellularity_scores[-1] > cellularity_scores[0] else "Stable",
        }
