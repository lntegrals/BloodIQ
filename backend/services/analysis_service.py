from __future__ import annotations
from typing import Dict, List
from ..schemas.models import ResultsRequest, BiomarkerResult, AnalysisResult
from ..utils.reference_data import BIOMARKER_REFERENCE
from ..utils.biological_age import calculate_biological_age


def analyze_biomarkers(data: ResultsRequest) -> AnalysisResult:
    biomarkers: List[BiomarkerResult] = []
    total_score = 0
    count = 0
    concerns: List[str] = []
    optimizations: List[str] = []

    # Ensure age is available to biological age calc
    bio_input = {**data.biomarkers}
    bio_input["age"] = float(data.age)

    for name, value in data.biomarkers.items():
        if name not in BIOMARKER_REFERENCE:
            continue
        ref = BIOMARKER_REFERENCE[name]
        min_range, max_range = ref["range"]
        min_opt, max_opt = ref["optimal"]

        if value < min_range:
            status = "Low"
            status_class = "status-low"
            score = 50
            concerns.append(f"{name} below normal range")
        elif value > max_range:
            status = "High"
            status_class = "status-high"
            score = 50
            concerns.append(f"{name} above normal range")
        else:
            status = "Normal"
            status_class = "status-normal"
            # Encourage optimization if not in optimal window
            if not (min_opt <= value <= max_opt):
                optimizations.append(f"{name} could be optimized")
            score = 80 if not (min_opt <= value <= max_opt) else 100

        biomarkers.append(
            BiomarkerResult(
                name=name,
                value=value,
                unit=ref["unit"],
                range=f"{min_range}-{max_range} {ref['unit']}",
                description=ref["description"],
                status=status,
                status_class=status_class,
            )
        )
        total_score += score
        count += 1

    biological_age = calculate_biological_age(bio_input)
    overall_health_score = round(total_score / max(1, count))

    return AnalysisResult(
        biological_age=biological_age,
        biomarkers=biomarkers,
        overall_health_score=overall_health_score,
        concerns=concerns,
        optimizations=optimizations,
    )

