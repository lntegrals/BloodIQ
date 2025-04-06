from flask import Flask, render_template, request
import os
import numpy as np
from dotenv import load_dotenv
from utils.prompt_builder import generate_prompt
import google.generativeai as genai

# Load Gemini API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    try:
        # Collect general info
        age = request.form.get('age')
        sex = request.form.get('sex')
        height = request.form.get('height')
        weight = request.form.get('weight')

        # Collect all biomarkers (used by Gemini to calculate)
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
            "wbc": request.form.get('wbc'),
            "hdl": request.form.get('hdl'),
            "ldl": request.form.get('ldl'),
            "alt": request.form.get('alt'),
            "ast": request.form.get('ast')
        }

        # Prepare user data for rendering and prompt building
        user_data = {
            "age": int(age),
            "sex": sex,
            "height_cm": float(height),
            "weight_kg": float(weight),
            "biomarkers": {k: float(v) for k, v in phenotypic_inputs.items() if v}
        }

        # Generate prompt for Gemini
        prompt = generate_prompt(user_data)

        # Call Gemini to interpret and calculate phenotypic age
        model = genai.GenerativeModel("models/gemini-1.5-pro")
        response = model.generate_content(prompt)
        feedback = response.text

        return render_template('results.html', user_data=user_data, feedback=feedback)

    except ValueError:
        return "Invalid input. Please make sure all fields are filled correctly."
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)
