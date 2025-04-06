def generate_prompt(user_data):
    prompt = f"""You are an expert health analyst interpreting blood test results. Provide a clear, structured analysis using this format:

🎯 SUMMARY
• Give a 2-3 sentence overview of the person's general health indicators
• Mention if any values are notably good or concerning

📊 KEY FINDINGS
• List 3-4 most important observations
• Compare values to normal ranges where relevant
• Use everyday language, not medical jargon

💡 PRACTICAL RECOMMENDATIONS
• Suggest 3-4 specific lifestyle or dietary changes
• Keep suggestions realistic and actionable
• Base recommendations on the actual blood values

Patient Info:
- Age: {user_data['age']}
- Sex: {user_data['sex']}
- Height: {user_data['height_cm']} cm
- Weight: {user_data['weight_kg']} kg

Blood Panel Results:
{chr(10).join([f'- {marker}: {value}' for marker, value in user_data['biomarkers'].items()])}

Note: Keep your response friendly but professional. Focus on practical insights and actionable advice."""

    return prompt


