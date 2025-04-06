from flask import Flask, render_template, request, jsonify
import os
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
from utils.prompt_builder import generate_prompt
from utils.phenotypic_age import calculate_phenotypic_age

# Load environment variables and configure Gemini
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found in .env file")
genai.configure(api_key=api_key)

# Initialize Flask and Gemini model
app = Flask(__name__)
model = genai.GenerativeModel('models/gemini-2.0-flash-lite')

def get_marker_info(marker):
    """Get reference ranges and descriptions for biomarkers"""
    info = {
        "Glucose": {
            "range": "70-99 mg/dL",
            "description": "Blood sugar level - key indicator of metabolic health",
            "thresholds": {"low": 70, "high": 99}
        },
        "HDL": {
            "range": "40-60 mg/dL",
            "description": "Good cholesterol - helps protect heart health",
            "thresholds": {"low": 40, "high": 60}
        },
        "LDL": {
            "range": "<100 mg/dL",
            "description": "Bad cholesterol - lower is generally better",
            "thresholds": {"low": 0, "high": 100}
        },
        "CRP": {
            "range": "<3.0 mg/L",
            "description": "Inflammation marker - indicates systemic inflammation",
            "thresholds": {"low": 0, "high": 3.0}
        },
        "ALT": {
            "range": "7-56 U/L",
            "description": "Liver enzyme - elevated in liver stress",
            "thresholds": {"low": 7, "high": 56}
        },
        "AST": {
            "range": "10-40 U/L",
            "description": "Liver enzyme - indicates liver health",
            "thresholds": {"low": 10, "high": 40}
        },
        "Albumin": {
            "range": "3.4-5.4 g/dL",
            "description": "Important protein for blood volume",
            "thresholds": {"low": 3.4, "high": 5.4}
        },
        "Creatinine": {
            "range": "0.7-1.3 mg/dL",
            "description": "Kidney function marker",
            "thresholds": {"low": 0.7, "high": 1.3}
        },
        "Lymphocyte %": {
            "range": "20-40%",
            "description": "White blood cells - immune health",
            "thresholds": {"low": 20, "high": 40}
        },
        "MCV": {
            "range": "80-100 fL",
            "description": "Red blood cell size",
            "thresholds": {"low": 80, "high": 100}
        },
        "RDW": {
            "range": "11.5-14.5%",
            "description": "Red cell size variation",
            "thresholds": {"low": 11.5, "high": 14.5}
        },
        "Alkaline Phosphatase": {
            "range": "44-147 U/L",
            "description": "Liver & bone enzyme",
            "thresholds": {"low": 44, "high": 147}
        },
        "WBC": {
            "range": "4.5-11.0 ×10⁹/L",
            "description": "Overall immune strength",
            "thresholds": {"low": 4.5, "high": 11.0}
        }
    }
    return info.get(marker, {
        "range": "N/A",
        "description": "No reference data available",
        "thresholds": {"low": 0, "high": 999999}
    })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_advice', methods=['POST'])
def get_advice():
    try:
        advice_type = request.form.get('type')
        user_data = request.form.get('user_data')

        if not advice_type or not user_data:
            return jsonify({'error': 'Missing required fields: type or user_data'}), 400

        prompt = generate_prompt(user_data, advice_type)
        response = model.generate_content(prompt)
        return jsonify({'advice': response.text})
    except Exception as e:
        return jsonify({'error': f"Failed to generate advice: {str(e)}"}), 500

@app.route('/results', methods=['POST'])
def results():
    try:
        # Collect general info
        age = request.form.get('age')
        sex = request.form.get('sex')
        height = request.form.get('height')
        weight = request.form.get('weight')

        # Prepare all biomarkers
        biomarkers = {
            "age": age,
            "albumin": request.form.get('albumin'),
            "creatinine": request.form.get('creatinine'),
            "glucose": request.form.get('glucose'),
            "crp": request.form.get('crp'),
            "lymph_pct": request.form.get('lymph_pct'),
            "mcv": request.form.get('mcv'),
            "rdw": request.form.get('rdw'),
            "alk_phos": request.form.get('alk_phos'),
            "wbc": request.form.get('wbc')
        }

        # Calculate phenotypic age (will be included in AI analysis)
        phenotypic_age = calculate_phenotypic_age(biomarkers)

        # Prepare user data
        user_data = {
            "age": int(age),
            "sex": sex,
            "height_cm": float(height),
            "weight_kg": float(weight),
            "biomarkers": biomarkers,
            "phenotypic_age": phenotypic_age  # Add to user_data for AI analysis
        }

        # Generate marker insights
        marker_insights = {}
        for marker, value in biomarkers.items():
            if value:
                marker_insights[marker] = get_marker_info(marker)
                value_float = float(value)
                
                if value_float < marker_insights[marker]["thresholds"]["low"]:
                    status = "Below Normal"
                    status_class = "status-low"
                elif value_float > marker_insights[marker]["thresholds"]["high"]:
                    status = "Above Normal"
                    status_class = "status-high"
                else:
                    status = "Normal"
                    status_class = "status-normal"

                marker_insights[marker].update({
                    "status": status,
                    "status_class": status_class
                })
            else:
                marker_insights[marker] = {
                    "range": "N/A",
                    "description": "Invalid value",
                    "status": "Unknown",
                    "status_class": ""
                }

        # Generate AI insights
        try:
            analysis = model.generate_content(generate_prompt(user_data, "analysis")).text
            meal_plan = model.generate_content(generate_prompt(user_data, "meal_plan")).text
            exercise_plan = model.generate_content(generate_prompt(user_data, "exercise_plan")).text
            supplements = model.generate_content(generate_prompt(user_data, "supplement_advice")).text
            risks = model.generate_content(generate_prompt(user_data, "risk_assessment")).text
        except Exception as e:
            print(f"❌ Gemini API error: {str(e)}")
            analysis = meal_plan = exercise_plan = supplements = risks = "AI insights temporarily unavailable"

        return render_template(
            'results.html',
            user_data=user_data,
            marker_insights=marker_insights,
            analysis=analysis,
            meal_plan=meal_plan,
            exercise_plan=exercise_plan,
            supplements=supplements,
            risks=risks
        )

    except Exception as e:
        print(f"❌ Error in results route: {str(e)}")
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)