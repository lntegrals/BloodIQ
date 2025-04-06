# app.py
from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
import google.generativeai as genai
import numpy as np
from utils.prompt_builder import generate_prompt

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

def calculate_phenotypic_age(data):
    try:
        # Raw inputs
        albumin_g_dL = float(data["albumin"])
        creatinine_mg_dL = float(data["creatinine"])
        glucose_mg_dL = float(data["glucose"])
        crp_mg_L = float(data["crp"])
        lymph_pct = float(data["lymph_pct"])
        mcv = float(data["mcv"])
        rdw = float(data["rdw"])
        alk_phos = float(data["alk_phos"])
        wbc_x10_9_per_L = float(data["wbc"])
        age = float(data["age"])

        # Convert units
        albumin = albumin_g_dL * 10                  # g/L
        creatinine = creatinine_mg_dL * 88.4         # µmol/L
        glucose = glucose_mg_dL / 18                 # mmol/L
        crp_val = crp_mg_L / 10                      # mg/dL
        if crp_val <= 0:
            raise ValueError("CRP must be > 0")
        crp = np.log(crp_val)
        wbc = wbc_x10_9_per_L * 1000                 # 1000 cells/uL

        # XB calculation
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

        exp_part = np.exp(xb)
        M = 1 - np.exp(-1.51714 * exp_part / 0.0076927)
        M = np.clip(M, 1e-5, 1 - 1e-5)

        phenotypic_age = 141.50 + (np.log(-0.00553 * np.log(1 - M))) / 0.09165
        return round(phenotypic_age, 2)

    except Exception as e:
        print("Phenotypic Age Calculation Error:", e)
        return "Calculation error"
    
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

    # Extract biomarkers for Gemini
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

        # Additional data for phenotypic age
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

    # Gemini Prompt
    prompt = generate_prompt(user_data)

    # Gemini API call
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
