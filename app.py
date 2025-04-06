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
        # Collect user input
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

        # Render results page
        return render_template(
            'results.html',
            user_data=user_data,
            analysis=analysis,
            meal_plan=meal_plan,
            exercise_plan=exercise_plan,
            supplements=supplements,
            risks=risks
        )

    except ValueError:
        return "Invalid input. Please ensure all fields are correctly filled."
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)