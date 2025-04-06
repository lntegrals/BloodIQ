from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
import google.generativeai as genai
import numpy as np
from utils.prompt_builder import generate_prompt

print("🔥 Flask app started from THIS app.py!")  # Confirm you're using the right app

# Load Gemini API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

# --- TEMP TEST: Phenotypic Age Calculator (fake result) ---
def calculate_phenotypic_age(data):
    print("🔥 This function was called correctly!")
    return 42.42  # FORCE FIX VALUE to test if it's being used

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    # Collect general user inputs
    age = request.form.get('age')
    sex = request.form.get('sex')
    height = request.form.get('height')
    weight = request.form.get('weight')

    # Biomarkers for Gemini prompt
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

        phenotypic_inputs = {
            "age": float(age),
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

        # 🔍 Confirm it's working
        print("[DEBUG] phenotypic_age =", phenotypic_age)
        print("[DEBUG] user_data =", user_data)

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
