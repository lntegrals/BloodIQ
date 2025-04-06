from flask import Flask, render_template, request
import os
import numpy as np
from dotenv import load_dotenv
from utils.prompt_builder import generate_prompt  # Optional if you're using Gemini later

# Load environment variables (e.g., Gemini API key)
load_dotenv()

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

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    try:
        # --- General Info ---
        age = request.form.get('age')
        sex = request.form.get('sex')
        height = request.form.get('height')
        weight = request.form.get('weight')

        # --- Biomarkers for Phenotypic Age ---
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

        # --- Calculate Phenotypic Age ---
        phenotypic_age = calculate_phenotypic_age(phenotypic_inputs)
        if phenotypic_age is None:
            return "An error occurred during calculation."

        # --- Package User Data for Results Page ---
        user_data = {
            "age": int(age),
            "sex": sex,
            "height_cm": float(height),
            "weight_kg": float(weight),
            "phenotypic_age": phenotypic_age,
            "biomarkers": {k: float(v) for k, v in phenotypic_inputs.items()}
        }

        return render_template('results.html', user_data=user_data)

    except ValueError:
        return "Invalid input: please make sure all fields are filled with numbers."
    except Exception as e:
        return f"Unexpected error: {e}"

if __name__ == '__main__':
    app.run(debug=True)
