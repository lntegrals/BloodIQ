from flask import Flask, render_template, request, jsonify
import os
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
from utils.prompt_builder import generate_prompt
from utils.phenotypic_age import calculate_phenotypic_age  # Add this import

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
    advice_type = request.form.get('type')
    user_data = request.form.get('user_data')
    
    prompt = generate_prompt(user_data, advice_type)
    try:
        response = model.generate_content(prompt)
        return jsonify({'advice': response.text})
    except Exception as e:
        return jsonify({'error': str(e)})

def get_marker_insight(marker, value):
    insights = {
        "Glucose": {
            "range": "70-99 mg/dL",
            "description": "Glucose is your blood sugar level. It's crucial for energy but high levels can indicate diabetes risk.",
            "thresholds": {"low": 70, "high": 99}
        },
        # Add other markers here
    }

    if marker not in insights:
        return {"range": "N/A", "description": "No detailed information available.", "status": "Unknown", "status_class": ""}

    try:
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
    except (ValueError, TypeError):
        return {"range": "N/A", "description": "Invalid value provided.", "status": "Unknown", "status_class": ""}

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

        # Prepare marker insights
        marker_insights = {}
        for marker, value in user_data["biomarkers"].items():
            marker_insights[marker] = get_marker_insight(marker, str(value))

        # Generate all AI insights first
        try:
            # Use existing model instance
            analysis = model.generate_content(generate_prompt(user_data, "analysis")).text
            meal_plan = model.generate_content(generate_prompt(user_data, "meal_plan")).text
            exercise_plan = model.generate_content(generate_prompt(user_data, "exercise_plan")).text
            supplements = model.generate_content(generate_prompt(user_data, "supplement_advice")).text
            risks = model.generate_content(generate_prompt(user_data, "risk_assessment")).text
            
            print("✅ Successfully generated Gemini insights")
        except Exception as e:
            print(f"❌ Gemini API error: {str(e)}")
            analysis = meal_plan = exercise_plan = supplements = risks = "AI insights temporarily unavailable"

        # Render results page
        return render_template(
            'results.html',
            user_data=user_data,
            marker_insights=marker_insights,  # Pass marker insights to template
            phenotypic_age=phenotypic_age,
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
