from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class AdviceType(str, Enum):
    overall_analysis = "overall_analysis"
    meal_plan = "meal_plan"
    exercise_plan = "exercise_plan"
    supplement_advice = "supplement_advice"
    risk_assessment = "risk_assessment"


class BiomarkerInput(BaseModel):
    name: str
    value: float

    @field_validator("name")
    @classmethod
    def lower_name(cls, v: str) -> str:
        return v.strip().lower()


class ResultsRequest(BaseModel):
    age: int = Field(ge=0, le=120)
    sex: str = Field(pattern=r"^(?i)(male|female)$")
    height_cm: float = Field(gt=0, le=300)
    weight_kg: float = Field(gt=0, le=500)
    biomarkers: Dict[str, float]

    @field_validator("biomarkers")
    @classmethod
    def validate_biomarkers(cls, v: Dict[str, float]) -> Dict[str, float]:
        cleaned = {}
        for k, val in v.items():
            if val is None:
                continue
            try:
                cleaned[k.strip().lower()] = float(val)
            except Exception:
                continue
        if "age" not in cleaned:
            cleaned["age"] = 0.0
        return cleaned


class BiomarkerResult(BaseModel):
    name: str
    value: float
    unit: str
    range: str
    description: str
    status: str  # Low / Normal / High
    status_class: str


class AnalysisResult(BaseModel):
    biological_age: float
    biomarkers: List[BiomarkerResult]
    overall_health_score: int
    concerns: List[str]
    optimizations: List[str]

