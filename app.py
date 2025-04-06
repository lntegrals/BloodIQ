from flask import Flask, render_template, request
import os
import numpy as np
from dotenv import load_dotenv
from utils.prompt_builder import generate_prompt  # Optional if you're using Gemini later

# Load environment variables (e.g., Gemini API key)
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_advice', methods=['POST'])
def get_advice():
    advice_type = request.form.get('type')
    user_data = request.form.get('user_data')
    
    prompt = generate_prompt(user_data, advice_type)
    try:
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
        response = model.generate_content(prompt)
        return jsonify({'advice': response.text})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/results', methods=['POST'])
def results():
    try:
        # Collect general info
        age = request.form.get('age')
        sex = request.form.get('sex')
        height = request.form.get('height')
        weight = request.form.get('weight')

        # Biomarkers for phenotypic age calculation
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

        # Calculate phenotypic age
        phenotypic_age = calculate_phenotypic_age(phenotypic_inputs)

        if phenotypic_age is None:
            return "An error occurred while calculating your phenotypic age."

        # Prepare user data for display
        user_data = {
            "age": int(age),
            "sex": sex,
            "height_cm": float(height),
            "weight_kg": float(weight),
            "phenotypic_age": phenotypic_age,
            "biomarkers": phenotypic_inputs  # Include biomarkers in user data
        }

        # Render results page
        return render_template('results.html', user_data=user_data)

    except ValueError:
        return "Invalid input. Please ensure all fields are correctly filled."

    # Generate Gemini prompt
    prompt = generate_prompt(user_data)

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
