import logging
from flask import Blueprint, current_app, jsonify, request
from ..extensions import limiter
from ..schemas.models import ResultsRequest, AdviceType
from ..services.analysis_service import analyze_biomarkers
from ..services.ai_service import generate_ai_sections


logger = logging.getLogger(__name__)
api_bp = Blueprint("api", __name__)


@api_bp.post("/results")
@limiter.limit(lambda: current_app.config.get("RATELIMIT_DEFAULT", "20/minute"))
def api_results():
    try:
        payload = request.get_json(silent=True) or {}
        data = ResultsRequest.model_validate(payload)

        analysis = analyze_biomarkers(data)

        ai_sections = {}
        if current_app.config.get("AI_ENABLED", False):
            try:
                ai_sections = generate_ai_sections(data, analysis)
            except Exception as e:
                logger.warning("AI generation failed: %s", e)
                ai_sections = {k: "AI temporarily unavailable" for k in [
                    "overall_analysis", "meal_plan", "exercise_plan", "supplement_advice", "risk_assessment"
                ]}
        else:
            ai_sections = {k: "AI disabled (missing GEMINI_API_KEY)" for k in [
                "overall_analysis", "meal_plan", "exercise_plan", "supplement_advice", "risk_assessment"
            ]}

        return jsonify({
            "biological_age": analysis.biological_age,
            "biomarkers": [m.model_dump() for m in analysis.biomarkers],
            "overall_health_score": analysis.overall_health_score,
            "concerns": analysis.concerns,
            "optimizations": analysis.optimizations,
            "ai": ai_sections,
        })
    except Exception as e:
        logger.exception("Error in /api/results")
        return jsonify({"error": str(e)}), 400


@api_bp.post("/advice/<advice_type>")
@limiter.limit(lambda: current_app.config.get("RATELIMIT_DEFAULT", "20/minute"))
def api_advice(advice_type: str):
    try:
        if not current_app.config.get("AI_ENABLED", False):
            return jsonify({"error": "AI disabled (missing GEMINI_API_KEY)"}), 503

        payload = request.get_json(silent=True) or {}
        data = ResultsRequest.model_validate(payload)

        # Validate advice type
        try:
            atype = AdviceType(advice_type)
        except ValueError:
            return jsonify({"error": f"Unsupported advice type: {advice_type}"}), 400

        analysis = analyze_biomarkers(data)
        sections = generate_ai_sections(data, analysis, types=[atype.value])
        return jsonify({"type": atype.value, "content": sections.get(atype.value, "")})
    except Exception as e:
        logger.exception("Error in /api/advice/%s", advice_type)
        return jsonify({"error": str(e)}), 400

