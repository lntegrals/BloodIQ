def generate_prompt(user_data):
    prompt = f"""
You are a health assistant analyzing blood panel data.

Patient Info:
- Age: {user_data['age']}
- Sex: {user_data['sex']}
- Height: {user_data['height_cm']} cm
- Weight: {user_data['weight_kg']} kg

Blood Panel Results:
"""
    for marker, value in user_data['biomarkers'].items():
        prompt += f"- {marker}: {value}\n"

    prompt += """
Please analyze the results in a friendly, medically-informed way. 
Comment on possible health concerns or strengths, explain what some values mean, 
and recommend simple lifestyle or diet changes based on the user's age and metrics.
Be helpful, but never offer a diagnosis. This is just for educational feedback.
"""

    return prompt


