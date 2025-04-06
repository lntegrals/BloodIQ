# app.py
from flask import Flask, render_template, request
import os
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai
from utils.prompt_builder import generate_prompt

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

# --- Phenotypic Age Formula (Stable + Validated) ---
def calculate_phenotypic_age(data):
    try:
        albumin = float(data["albumin"])
        creatinine = float(data["creatinine"])
        glucose = float(data["glucose"])
        crp_raw = float(data["crp"])
        crp = np.log(crp_raw if crp_raw > 0 else 0.01)  # avoid log(0)
        lymph_pct = float(data["lymph_pct"])
        mcv = float(data["mcv"])
        rdw = float(data["rdw"])
        alk_phos = float(data["alk_phos"])
        wbc = float(data["wbc"])
        age = float(data["age"])

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

        exp_xb = np.exp(xb)
        M = 1 - np.exp(-1.51714 * exp_xb / 0.0076927)

        # Validate M to avoid log(0) or negative input
        if M >= 1.0:
            M = 0.999999
        elif M <= 0.0:
            M = 0.000001

        phenotypic_age = 141.50 + (np.log(-0.00553 * np.log(1 - M))) / 0.09165

        return round(phenotypic_age, 2)

    except Exception as e:
        print("[ERROR] Phenotypic age calculation failed:", e)
        return None

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    # Collect general inputs
    age = request.form.get('age')
    sex = request.form.get('sex')
    height = request.form.get('height')
    weight = request.form.get('weight')

    # Biomarkers for Gemini
    biomarkers = {
        "Glucose": request.form.get('glucose'),
        "HDL": request.form.get('hdl'),
        "LDL": request.form.get('ldl'),
        "CRP": request.form.get('crp'),
        "ALT": request.form.get('alt'),
        "AST": request.form.get('ast')
    }

    try:
        user_data = {
            "age": int(age),
            "sex": sex,
            "height_cm": float(height),
            "weight_kg": float(weight),
            "biomarkers": {k: float(v) for k, v in biomarkers.items() if v}
        }

        # Inputs needed for phenotypic age
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

    except ValueError:
        return "Invalid input. Please ensure all fields are numbers."

    # Prompt for Gemini
    prompt = generate_prompt(user_data)

    # Gemini response
    try:
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
        response = model.generate_content(prompt)
        feedback = response.text
    except Exception as e:
        feedback = f"Something went wrong with Gemini: {e}"

    return render_template(
        'results.html',
        user_data=user_data,
        feedback=feedback,
        phenotypic_age=phenotypic_age
    )

if __name__ == '__main__':
    app.run(debug=True)
