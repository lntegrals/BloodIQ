from flask import Flask, render_template, request, jsonify
import os
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
from utils.prompt_builder import generate_prompt
from utils.biological_age import calculate_biological_age

# Load environment variables and configure Gemini
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found in .env file")
genai.configure(api_key=api_key)

# Initialize Flask and Gemini model
app = Flask(__name__)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_marker_info(marker):
    """Get reference ranges and descriptions for biomarkers"""
    info = {
        'albumin': {
            'range': '3.4-5.4 g/dL',
            'optimal': (4.3, 5.2),
            'unit': 'g/dL',
            'description': 'Protein made by liver; low levels can indicate malnutrition or liver/kidney disease',
            'thresholds': {'low': 3.4, 'high': 5.4}
        },
        'glucose': {
            'range': '70-99 mg/dL',
            'optimal': (70, 90),
            'unit': 'mg/dL',
            'description': 'Blood sugar level; high levels indicate diabetes risk or metabolic issues',
            'thresholds': {'low': 70, 'high': 99}
        },
        'crp': {
            'range': '0-3.0 mg/L',
            'optimal': (0, 1),
            'unit': 'mg/L',
            'description': 'Inflammation marker; elevated levels indicate systemic inflammation',
            'thresholds': {'low': 0, 'high': 3.0}
        },
        'lymph_pct': {
            'range': '20-40%',
            'optimal': (25, 35),
            'unit': '%',
            'description': 'Percentage of white blood cells that are lymphocytes; immune system indicator',
            'thresholds': {'low': 20, 'high': 40}
        },
        'mcv': {
            'range': '80-100 fL',
            'optimal': (85, 95),
            'unit': 'fL',
            'description': 'Mean Corpuscular Volume; size of red blood cells',
            'thresholds': {'low': 80, 'high': 100}
        },
        'rdw': {
            'range': '11.5-14.5%',
            'optimal': (12.0, 13.5),
            'unit': '%',
            'description': 'Red Cell Distribution Width; variation in red blood cell size',
            'thresholds': {'low': 11.5, 'high': 14.5}
        },
        'alk_phos': {
            'range': '44-147 U/L',
            'optimal': (50, 120),
            'unit': 'U/L',
            'description': 'Alkaline Phosphatase; enzyme related to liver and bone health',
            'thresholds': {'low': 44, 'high': 147}
        },
        'wbc': {
            'range': '4.5-11.0 K/µL',
            'optimal': (5.0, 8.0),
            'unit': 'K/µL',
            'description': 'White Blood Cell count; immune system activity indicator',
            'thresholds': {'low': 4.5, 'high': 11.0}
        },
        'creatinine': {
            'range': '0.6-1.3 mg/dL',
            'optimal': (0.7, 1.2),
            'unit': 'mg/dL',
            'description': 'Kidney function marker; filtered waste product from muscles',
            'thresholds': {'low': 0.6, 'high': 1.3}
        }
    }
    return info.get(marker, {
        'range': 'N/A',
        'optimal': (0, 0),
        'unit': '',
        'description': 'No reference data available',
        'thresholds': {'low': 0, 'high': 999999}
    })

def calculate_biological_age(blood_markers):
    chronological_age = float(blood_markers.get('age', 0))
    age_modifier = 0
    
    if 'glucose' in blood_markers:
        glucose = float(blood_markers['glucose'])
        if glucose > 100:
            age_modifier += (glucose - 100) / 10
        elif glucose < 70:
            age_modifier += (70 - glucose) / 5

    if 'cholesterol' in blood_markers:
        cholesterol = float(blood_markers['cholesterol'])
        if cholesterol > 200:
            age_modifier += (cholesterol - 200) / 20

    if 'blood_pressure' in blood_markers:
        bp = float(blood_markers['blood_pressure'])
        if bp > 120:
            age_modifier += (bp - 120) / 10

    biological_age = chronological_age + age_modifier
    return round(biological_age, 1)

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
        # Collect general info
        age = request.form.get('age')
        sex = request.form.get('sex')
        height = request.form.get('height')
        weight = request.form.get('weight')

        # Prepare all biomarkers
        biomarkers = {
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

        # Calculate biological age (will be included in AI analysis)
        biological_age = calculate_biological_age(biomarkers)

        # Prepare user data with metric units
        user_data = {
            "age": int(age),
            "sex": sex,
            "height_cm": float(height),
            "weight_kg": float(weight),
            "biomarkers": biomarkers,
            "phenotypic_age": biological_age
        }

        # Generate marker insights
        marker_insights = {}
        for marker, value in biomarkers.items():
            if value and marker != 'age':  # Skip age from biomarker analysis
                info = get_marker_info(marker)
                try:
                    value_float = float(value)
                    
                    if value_float < info['thresholds']['low']:
                        status = "Below Normal"
                        status_class = "status-low"
                    elif value_float > info['thresholds']['high']:
                        status = "Above Normal"
                        status_class = "status-high"
                    else:
                        status = "Normal"
                        status_class = "status-normal"

                    marker_insights[marker] = {
                        'value': value_float,
                        'unit': info['unit'],
                        'range': info['range'],
                        'description': info['description'],
                        'status': status,
                        'status_class': status_class,
                        'reference': info  # Include full reference data
                    }
                except (ValueError, TypeError):
                    continue

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

        return render_template(
            'results.html',
            user_data=user_data,
            marker_insights=marker_insights,
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