from flask import Flask, render_template, request, jsonify
import os
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai
from utils.prompt_builder import generate_prompt

# Load environment variables and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

# --- ✅ Phenotypic Age Formula (with unit conversion) ---
def calculate_phenotypic_age(data):
    try:
        albumin = float(data["albumin"]) * 10            # g/dL → g/L
        creatinine = float(data["creatinine"]) * 88.4    # mg/dL → µmol/L
        glucose = float(data["glucose"]) / 18            # mg/dL → mmol/L
        crp_val = float(data["crp"]) / 10                # mg/L → mg/dL
        crp = np.log(crp_val if crp_val > 0 else 0.01)   # log safe

        lymph_pct = float(data["lymph_pct"])
        mcv = float(data["mcv"])
        rdw = float(data["rdw"])
        alk_phos = float(data["alk_phos"])
        wbc = float(data["wbc"]) * 1000                  # ×10⁹/L → cells/μL
        age = float(data["age"])

        # --- XB Calculation ---
        xb = (
            -19.907
            - 0.0336 * albumin
            + 0.0095 * creatinine
            + 0.1953 * glucose
            + 0.0954 * crp
            - 0.0120 * lymph_pct
            + 0.0268 * mcv
            + 0.3306 * rdw
            + 0.00188 * alk_phos
            + 0.0554 * wbc
            + 0.0804 * age
        )

        xb = np.clip(xb, -30, 30)
        exp_xb = np.exp(xb)
        M = 1 - np.exp(-1.51714 * exp_xb / 0.0076927)
        M = np.clip(M, 1e-5, 1 - 1e-5)

        phenotypic_age = 141.50 + (np.log(-0.00553 * np.log(1 - M))) / 0.09165
        phenotypic_age = max(0, min(phenotypic_age, 120))  # Clamp to valid range

        print(f"[DEBUG] XB = {xb:.2f}, M = {M:.6f}, PhenoAge = {phenotypic_age:.2f}")
        return round(phenotypic_age, 2)

    except Exception as e:
        print("[ERROR] Phenotypic Age calculation failed:", e)
        return None

# --- Marker Insights ---
def get_marker_insight(marker, value):
    insights = {
        "Glucose": {
            "range": "70-99 mg/dL",
            "description": "Glucose is your blood sugar level. It's crucial for energy but high levels can indicate diabetes risk.",
            "thresholds": {"low": 70, "high": 99}
        },
        "HDL": {
            "range": "40-60 mg/dL",
            "description": "HDL is 'good' cholesterol that helps remove other forms of cholesterol from your bloodstream.",
            "thresholds": {"low": 40, "high": 60}
        },
        "LDL": {
            "range": "<100 mg/dL",
            "description": "LDL is 'bad' cholesterol that can build up in your arteries. Lower is generally better.",
            "thresholds": {"low": 0, "high": 100}
        },
        "CRP": {
            "range": "<3.0 mg/L",
            "description": "CRP indicates inflammation. Elevated levels might suggest infection or chronic inflammation.",
            "thresholds": {"low": 0, "high": 3.0}
        },
        "ALT": {
            "range": "7-56 U/L",
            "description": "ALT is a liver enzyme. Elevated levels can indicate liver stress or damage.",
            "thresholds": {"low": 7, "high": 56}
        },
        "AST": {
            "range": "10-40 U/L",
            "description": "AST is another liver enzyme. High levels might indicate liver or muscle damage.",
            "thresholds": {"low": 10, "high": 40}
        }
    }

    if marker not in insights:
        return {"range": "N/A", "description": "No detailed information available.", "status": "Unknown", "status_class": ""}

    info = insights[marker]
    value = float(value)
    
    if value < info["thresholds"]["low"]:
        status = "Below Normal"
        status_class = "status-low"
    elif value > info["thresholds"]["high"]:
        status = "Above Normal"
        status_class = "status-high"
    else:
        status = "Normal"
        status_class = "status-normal"

    return {
        "range": info["range"],
        "description": info["description"],
        "status": status,
        "status_class": status_class
    }

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_advice', methods=['POST'])
def get_advice():
    advice_type = request.form.get('type')
    user_data = request.form.get('user_data')
    
    prompt = generate_prompt(user_data, advice_type)
    try:
        model = genai.GenerativeModel('models/gemini-2.0-flash-lite')  # Updated model name
        response = model.generate_content(prompt)
        return jsonify({'advice': response.text})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/results', methods=['POST'])
def results():
    try:
        # Collect user input
        age = request.form.get('age')
        sex = request.form.get('sex')
        height = request.form.get('height')
        weight = request.form.get('weight')

        # All biomarkers for display
        biomarkers = {
            "Glucose": request.form.get('glucose'),
            "HDL": request.form.get('hdl'),
            "LDL": request.form.get('ldl'),
            "CRP": request.form.get('crp'),
            "ALT": request.form.get('alt'),
            "AST": request.form.get('ast'),
            "Albumin": request.form.get('albumin'),
            "Creatinine": request.form.get('creatinine'),
            "Lymphocyte %": request.form.get('lymph_pct'),
            "MCV": request.form.get('mcv'),
            "RDW": request.form.get('rdw'),
            "Alkaline Phosphatase": request.form.get('alk_phos'),
            "WBC": request.form.get('wbc')
        }

        # Calculate phenotypic age
        phenotypic_inputs = {
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

        phenotypic_age = calculate_phenotypic_age(phenotypic_inputs)

        # Generate marker insights
        marker_insights = {}
        for marker, value in biomarkers.items():
            if value:  # Only generate insights for provided values
                marker_insights[marker] = get_marker_insight(marker, value)

        # Prepare user data
        user_data = {
            "age": int(age),
            "sex": sex,
            "height_cm": float(height),
            "weight_kg": float(weight),
            "biomarkers": {k: float(v) for k, v in biomarkers.items() if v}
        }

        # Generate all AI insights first
        try:
            model = genai.GenerativeModel('models/gemini-2.0-flash-lite')  # Updated model name
            
            # Generate different types of insights
            analysis = model.generate_content(generate_prompt(user_data, "analysis")).text
            meal_plan = model.generate_content(generate_prompt(user_data, "meal_plan")).text
            exercise_plan = model.generate_content(generate_prompt(user_data, "exercise_plan")).text
            supplements = model.generate_content(generate_prompt(user_data, "supplement_advice")).text
            risks = model.generate_content(generate_prompt(user_data, "risk_assessment")).text
            
            print("✅ Successfully generated Gemini insights")
        except Exception as e:
            print(f"❌ Gemini API error: {str(e)}")
            analysis = meal_plan = exercise_plan = supplements = risks = "AI insights temporarily unavailable"

        # Return all data to template
        return render_template(
            'results.html',
            user_data=user_data,
            phenotypic_age=phenotypic_age,
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
