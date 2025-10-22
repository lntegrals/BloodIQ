from __future__ import annotations


def calculate_biological_age(biomarkers: dict) -> float:
    """Estimate biological age based on weighted deviations from optimal ranges.

    The formula computes a normalized deviation for each marker relative to the
    midpoint of its optimal range, weights it by marker importance, and scales
    to an age adjustment. Modest deviations reduce age if below threshold, larger
    deviations increase age.
    """
    age = float(biomarkers.get("age", 0.0))

    # Expected fields with (optimal_min, optimal_max, weight)
    spec = {
        "albumin": ((4.3, 5.2), 2.0),
        "glucose": ((70, 90), 1.5),
        "crp": ((0.0, 1.0), 1.5),
        "lymph_pct": ((25, 35), 1.0),
        "mcv": ((85, 95), 1.0),
        "rdw": ((12.0, 13.5), 1.0),
        "wbc": ((5.0, 8.0), 1.0),
        "alk_phos": ((50, 120), 0.5),
        "creatinine": ((0.7, 1.2), 0.5),
    }

    total = 0.0
    weights = 0.0
    for key, ((opt_min, opt_max), w) in spec.items():
        try:
            val = float(biomarkers[key])
        except Exception:
            continue
        midpoint = (opt_min + opt_max) / 2.0
        dev = abs(val - midpoint) / midpoint
        total += dev * w
        weights += w

    if weights == 0:
        return round(age, 1)

    avg_dev = total / weights
    # Scale factor determines how much deviation impacts age
    scale = 10.0
    adj = avg_dev * scale

    # If close to optimal (< 0.1), treat as rejuvenating (slightly lower age)
    adjusted = age + (adj if avg_dev > 0.1 else -adj)
    adjusted = max(0.0, min(120.0, adjusted))
    return round(adjusted, 1)

