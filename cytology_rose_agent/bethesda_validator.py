"""
Bethesda System Category Validation Agent for Cytology ROSE Agent.
Cross-reference assigned Bethesda category against reported cytomorphologic features.
"""
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class BethesdaValidation:
    """Bethesda category validation result."""
    assigned_category: str
    suggested_category: str
    confidence: float
    discordance_flags: List[str]


class BethesdaCategoryValidator:
    """Validate Bethesda category assignments against cytomorphologic features."""

    BETHELSDA_CATEGORIES = {
        "I": "Nondiagnostic/Unsatisfactory",
        "II": "Benign",
        "III": "Atypia of Undetermined Significance",
        "IV": "Follicular Neoplasm",
        "V": "Suspicious for Malignancy",
        "VI": "Malignant",
    }

    def validate_bethesda_category(self, category: str, findings: dict) -> dict:
        """Validate Bethesda category (I-VI) against cytomorphologic features."""
        flags = []
        suggested = category
        confidence = 1.0

        cellularity = findings.get("cellularity", "adequate")
        nuclear_features = findings.get("nuclear_features", "benign")
        architectural_pattern = findings.get("architectural_pattern", "monolayered")
        colloid_present = findings.get("colloid_present", True)

        if category == "I" and cellularity == "adequate":
            flags.append("Cellularity adequate but category I (nondiagnostic) assigned")
            suggested = "II"
            confidence = 0.7
        elif category == "II" and nuclear_features == "atypical":
            flags.append("Nuclear atypia present but category II (benign) assigned")
            suggested = "III"
            confidence = 0.6
        elif category == "II" and not colloid_present:
            flags.append("Absent colloid with benign diagnosis; consider atypia")
            confidence = 0.8
        elif category == "IV" and nuclear_features == "benign":
            flags.append("Category IV (follicular neoplasm) without nuclear atypia")
            confidence = 0.5
        elif category == "VI" and nuclear_features != "malignant":
            flags.append("Category VI (malignant) without malignant nuclear features")
            confidence = 0.5
        elif category == "V" and architectural_pattern == "monolayered":
            flags.append("Category V with monolayered pattern; verify suspicious features")
            confidence = 0.6

        return {
            "assigned_category": category,
            "category_name": self.BETHELSDA_CATEGORIES.get(category, "Unknown"),
            "suggested_category": suggested,
            "confidence": confidence,
            "discordance_flags": flags,
            "needs_review": len(flags) > 0,
        }

    def get_risk_of_malignancy(self, category: str) -> dict:
        """Return expected risk of malignancy per Bethesda category."""
        rom = {
            "I": {"rom_pct": "1-4", "note": "Repeat FNA recommended"},
            "II": {"rom_pct": "0-3", "note": "Benign; clinical follow-up"},
            "III": {"rom_pct": "6-18", "note": "Consider repeat FNA or molecular testing"},
            "IV": {"rom_pct": "10-40", "note": "Surgical lobectomy recommended"},
            "V": {"rom_pct": "45-75", "note": "Surgical excision recommended"},
            "VI": {"rom_pct": "97-99", "note": "Malignant; treatment planning"},
        }
        return rom.get(category, {"rom_pct": "Unknown", "note": "Invalid category"})
