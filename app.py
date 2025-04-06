from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
import google.generativeai as genai
from utils.prompt_builder import generate_prompt

# Load Gemini API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    try:
        # --- Collect General Info ---
        age = request.form.get('age')
        sex = request.form.get('sex')
        height = request.form.get('height')
        weight = request.form.get('weight')

        # --- Collect Biomarker Inputs ---
        biomarker_fields = [
            "albumin", "creatinine", "glucose", "crp", "lymph_pct",
            "mcv", "rdw", "alk_phos", "wbc",
            "hdl", "ldl", "alt", "ast"
        ]

        biomarkers = {}
        for field in biomarker_fields:
            value = request.form.get(field)
            if value:
                biomarkers[field] = float(value)

        # --- Build user data for prompt and rendering ---
        user_data = {
            "age": int(age),
            "sex": sex,
            "height_cm": float(height),
            "weight_kg": float(weight),
            "biomarkers": biomarkers
        }

        # --- Generate Gemini Prompt ---
        prompt = generate_prompt(user_data)

        # --- Gemini API Call ---
        model = genai.GenerativeModel("models/gemini-1.5-pro")
        response = model.generate_content(prompt)
        feedback = response.text

        return render_template(
            'results.html',
            user_data=user_data,
            feedback=feedback
        )

    except ValueError:
        return "Invalid input. Please make sure all fields are filled correctly."
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)
