import numpy as np

def calculate_biological_age(biomarkers):
    """
    Calculates biological age based on blood work markers and their optimal ranges
    """
    try:
        age = float(biomarkers['age'])
        albumin = float(biomarkers['albumin'])
        creatinine = float(biomarkers['creatinine'])
        glucose = float(biomarkers['glucose'])
        crp = float(biomarkers['crp'])
        lymph_pct = float(biomarkers['lymph_pct'])
        mcv = float(biomarkers['mcv'])
        rdw = float(biomarkers['rdw'])
        alk_phos = float(biomarkers['alk_phos'])
        wbc = float(biomarkers['wbc'])

        # Define optimal ranges and calculate deviations
        deviations = [
            (albumin, 4.3, 5.2),      # weight: 2.0
            (glucose, 70, 90),        # weight: 1.5
            (crp, 0, 1),             # weight: 1.5
            (lymph_pct, 20, 40),     # weight: 1.0
            (mcv, 80, 96),           # weight: 1.0
            (rdw, 11.5, 14.5),       # weight: 1.0
            (wbc, 4.5, 10),          # weight: 1.0
            (alk_phos, 44, 147),     # weight: 0.5
            (creatinine, 0.6, 1.2)   # weight: 0.5
        ]

        weights = [2.0, 1.5, 1.5, 1.0, 1.0, 1.0, 1.0, 0.5, 0.5]
        total_deviation = 0
        total_weight = sum(weights)

        for (value, min_val, max_val), weight in zip(deviations, weights):
            optimal = (min_val + max_val) / 2
            deviation = abs(value - optimal) / optimal
            total_deviation += deviation * weight

        # Calculate biological age adjustment
        avg_deviation = total_deviation / total_weight
        age_adjustment = avg_deviation * 10  # Scale factor for age impact
        
        biological_age = age + (age_adjustment if avg_deviation > 0.1 else -age_adjustment)
        biological_age = max(0, min(biological_age, 120))

        return round(biological_age, 1)

    except (ValueError, TypeError) as e:
        print(f"Error calculating biological age: {str(e)}")
        return None