import numpy as np

# Reference data with detailed descriptions and ranges
BIOMARKER_REFERENCE = {
    'albumin': {
        'range': (3.4, 5.4),
        'optimal': (4.3, 5.2),
        'unit': 'g/dL',
        'description': 'Protein made by liver; low levels can indicate malnutrition or liver/kidney disease'
    },
    'glucose': {
        'range': (70, 100),
        'optimal': (70, 90),
        'unit': 'mg/dL',
        'description': 'Blood sugar level; high levels indicate diabetes risk or metabolic issues'
    },
    'crp': {
        'range': (0, 3),
        'optimal': (0, 1),
        'unit': 'mg/L',
        'description': 'Inflammation marker; elevated levels indicate systemic inflammation'
    },
    'lymph_pct': {
        'range': (20, 40),
        'optimal': (25, 35),
        'unit': '%',
        'description': 'Percentage of white blood cells that are lymphocytes; immune system indicator'
    },
    'mcv': {
        'range': (80, 100),
        'optimal': (85, 95),
        'unit': 'fL',
        'description': 'Mean Corpuscular Volume; size of red blood cells, can indicate anemia type'
    },
    'rdw': {
        'range': (11.5, 14.5),
        'optimal': (12.0, 13.5),
        'unit': '%',
        'description': 'Red Cell Distribution Width; variation in red blood cell size'
    },
    'alk_phos': {
        'range': (44, 147),
        'optimal': (50, 120),
        'unit': 'U/L',
        'description': 'Alkaline Phosphatase; enzyme related to liver and bone health'
    },
    'creatinine': {
        'range': (0.6, 1.3),
        'optimal': (0.7, 1.2),
        'unit': 'mg/dL',
        'description': 'Kidney function marker; filtered waste product from muscles'
    },
    'wbc': {
        'range': (4.5, 11.0),
        'optimal': (5.0, 8.0),
        'unit': 'K/µL',
        'description': 'White Blood Cell count; immune system activity indicator'
    }
}

def analyze_health(biomarkers):
    """
    Comprehensive health analysis including biological age and marker evaluations
    """
    analysis = {
        'biological_age': calculate_biological_age(biomarkers),
        'marker_analysis': {},
        'overall_health_score': 0,
        'concerns': [],
        'optimizations': []
    }
    
    total_score = 0
    for marker, value in biomarkers.items():
        if marker in BIOMARKER_REFERENCE:
            ref = BIOMARKER_REFERENCE[marker]
            try:
                value = float(value)
                min_range, max_range = ref['range']
                min_opt, max_opt = ref['optimal']
                
                status = 'optimal' if min_opt <= value <= max_opt else \
                         'normal' if min_range <= value <= max_range else 'outside_range'
                
                score = 100 if status == 'optimal' else \
                        80 if status == 'normal' else 50
                
                analysis['marker_analysis'][marker] = {
                    'value': value,
                    'status': status,
                    'score': score,
                    'reference': ref
                }
                
                total_score += score
                
                if status == 'outside_range':
                    analysis['concerns'].append(f"{marker} is outside normal range")
                elif status == 'normal' and not min_opt <= value <= max_opt:
                    analysis['optimizations'].append(f"{marker} could be optimized")
                    
            except (ValueError, TypeError):
                continue
    
    analysis['overall_health_score'] = round(total_score / len(analysis['marker_analysis']))
    return analysis

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