from __future__ import annotations
import json
import logging
from typing import Dict, Iterable, List, Optional
import bleach
import google.generativeai as genai
from flask import current_app
from ..schemas.models import ResultsRequest


logger = logging.getLogger(__name__)


ALLOWED_HTML_TAGS = [
    "p", "ul", "ol", "li", "strong", "em", "code", "pre", "h1", "h2", "h3", "h4", "h5", "h6", "a", "table", "thead", "tbody", "tr", "th", "td", "blockquote", "hr"
]
ALLOWED_HTML_ATTRS = {"a": ["href", "target", "rel"]}


SECTION_KEYS = [
    "overall_analysis",
    "meal_plan",
    "exercise_plan",
    "supplement_advice",
    "risk_assessment",
]


def _ensure_configured() -> None:
    if not current_app.config.get("AI_ENABLED"):
        raise RuntimeError("AI is not enabled (missing GEMINI_API_KEY)")
    api_key = current_app.config.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)


def _build_payload(user: ResultsRequest, analysis) -> Dict:
    return {
        "age": user.age,
        "sex": user.sex,
        "height_cm": user.height_cm,
        "weight_kg": user.weight_kg,
        "biological_age": analysis.biological_age,
        "overall_health_score": analysis.overall_health_score,
        "biomarkers": {bm.name: bm.value for bm in analysis.biomarkers},
    }


def _prompt_for_section(section: str, payload: Dict) -> str:
    header = {
        "overall_analysis": "Provide a clear summary of key findings and implications.",
        "meal_plan": "Create a 3-day meal plan with portions and simple foods.",
        "exercise_plan": "Provide a weekly plan mixing cardio and strength with intensities.",
        "supplement_advice": "Recommend evidence-based supplements with dosages and cautions.",
        "risk_assessment": "Analyze current risk factors, long-term implications, and follow-ups.",
    }[section]

    return (
        "You are an expert preventive health coach generating structured markdown for a patient.\n"
        "Always answer in plain, accessible language.\n\n"
        f"Section: {section}\n"
        f"Instruction: {header}\n\n"
        "Respond strictly as a JSON object with this schema: {\n"
        "  \"section\": string, \n"
        "  \"markdown\": string  // valid GitHub-flavored markdown\n"
        "}\n\n"
        f"Patient payload (JSON):\n{json.dumps(payload)}\n"
        "Ensure facts and ranges align with the input payload."
    )


def _sanitize_markdown(md: str) -> str:
    # Allow markdown but clean any embedded HTML
    return bleach.clean(md, tags=ALLOWED_HTML_TAGS, attributes=ALLOWED_HTML_ATTRS, strip=True)


def _call_gemini(prompt: str) -> Dict[str, str]:
    model_name = "models/gemini-1.5-pro"
    model = genai.GenerativeModel(model_name=model_name)
    resp = model.generate_content(prompt)
    text = resp.text or "{}"
    try:
        obj = json.loads(text)
    except Exception:
        # Try to recover JSON enclosed in code fences
        try:
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end >= start:
                obj = json.loads(text[start : end + 1])
            else:
                obj = {"section": "unknown", "markdown": text}
        except Exception:
            obj = {"section": "unknown", "markdown": text}
    return obj


def generate_ai_sections(user: ResultsRequest, analysis, types: Optional[Iterable[str]] = None) -> Dict[str, str]:
    _ensure_configured()

    payload = _build_payload(user, analysis)
    requested = list(types) if types else SECTION_KEYS
    out: Dict[str, str] = {}

    for section in requested:
        prompt = _prompt_for_section(section, payload)
        result = _call_gemini(prompt)
        md = result.get("markdown", "")
        out[section] = _sanitize_markdown(md)

    return out

