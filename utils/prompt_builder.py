def generate_prompt(user_data, prompt_type="analysis"):
    base_info = f"""Patient Info:
- Age: {user_data['age']}
- Sex: {user_data['sex']}
- Height: {user_data['height_cm']} cm
- Weight: {user_data['weight_kg']} kg

Blood Panel Results:
{chr(10).join([f'- {marker}: {value}' for marker, value in user_data['biomarkers'].items()])}
"""

    prompts = {
        "analysis": f"""You are an expert health analyst interpreting blood test results. Provide a clear, structured analysis using this format:

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

{base_info}""",

        "meal_plan": f"""As a nutrition expert, create a personalized 3-day meal plan based on this blood panel:

{base_info}

Consider:
- Foods that could help improve any out-of-range values
- The person's age and weight
- Include specific portions and timing
- Focus on practical, everyday foods
- Include scientific reasoning for key recommendations

Format as a clear, day-by-day plan with meals and snacks.""",

        "exercise_plan": f"""As a fitness expert, create a personalized exercise plan based on this health profile:

{base_info}

Consider:
- Current health markers and any limitations they suggest
- Age-appropriate activities
- Progressive difficulty
- Mix of cardio and strength training
- Recovery recommendations

Provide a weekly plan with specific exercises, durations, and intensities.""",

        "supplement_advice": f"""As a nutrition scientist, recommend evidence-based supplements based on these blood markers:

{base_info}

For each recommendation:
- Explain why it's needed based on the blood values
- Specify dosage and timing
- Note any interactions or contraindications
- Prioritize by importance
- Include both essential nutrients and optional supplements""",

        "risk_assessment": f"""As a preventive health specialist, analyze potential health risks based on:

{base_info}

Provide:
• Current risk factors based on blood values
• Long-term health implications if not addressed
• Early warning signs to watch for
• Preventive measures prioritized by importance
• Timeline for recommended follow-up tests"""
    }

    return prompts.get(prompt_type, prompts["analysis"])


