# app.py
from flask import Flask, render_template, request
import os
from dotenv import load_dotenv  # <-- make sure to install python-dotenv
import google.generativeai as genai
from utils.prompt_builder import generate_prompt

# Load .env file to access GEMINI_API_KEY
load_dotenv()

# Configure Gemini with your API key from the environment
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

# Home route — shows input form
@app.route('/')
def index():
    return render_template('index.html')

# Results route — handles form submission and Gemini response
@app.route('/results', methods=['POST'])
def results():
    # Collect form inputs
    age = request.form.get('age')
    sex = request.form.get('sex')
    height = request.form.get('height')
    weight = request.form.get('weight')

    # Extract biomarker data
    biomarkers = {
        "Glucose": request.form.get('glucose'),
        "HDL": request.form.get('hdl'),
        "LDL": request.form.get('ldl'),
        "CRP": request.form.get('crp'),
        "ALT": request.form.get('alt'),
        "AST": request.form.get('ast')
    }

    # Convert everything to correct types (float or int where needed)
    try:
        user_data = {
            "age": int(age),
            "sex": sex,
            "height_cm": float(height),
            "weight_kg": float(weight),
            "biomarkers": {k: float(v) for k, v in biomarkers.items() if v}
        }
    except ValueError:
        return "Invalid input. Please ensure all fields are numbers."

    # Build prompt for Gemini
    prompt = generate_prompt(user_data)

    # Use Gemini to generate feedback
    try:
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
        response = model.generate_content(prompt)
        feedback = response.text
    except Exception as e:
        feedback = f"Something went wrong with Gemini: {e}"

    return render_template('results.html', user_data=user_data, feedback=feedback)

if __name__ == '__main__':
    app.run(debug=True)

