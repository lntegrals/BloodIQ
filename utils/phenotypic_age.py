import numpy as np

def calculate_phenotypic_age(data):
    """Calculate phenotypic age from biomarker data."""
    try:
        # Unit conversions
        albumin = float(data["albumin"]) * 10            # g/dL → g/L
        creatinine = float(data["creatinine"]) * 88.4    # mg/dL → µmol/L
        glucose = float(data["glucose"]) / 18            # mg/dL → mmol/L
        crp_val = float(data["crp"]) / 10                # mg/L → mg/dL
        crp = np.log(crp_val if crp_val > 0 else 0.01)   # log safe

        # Other biomarkers
        lymph_pct = float(data["lymph_pct"])
        mcv = float(data["mcv"])
        rdw = float(data["rdw"])
        alk_phos = float(data["alk_phos"])
        wbc = float(data["wbc"]) * 1000                  # ×10⁹/L → cells/μL
        age = float(data["age"])

        # Calculate XB (Levine's formula)
        xb = (
            -19.907
            - 0.0336 * albumin
            + 0.0095 * creatinine
            + 0.1953 * glucose
            + 0.0954 * crp
            - 0.0120 * lymph_pct
            + 0.0268 * mcv
            + 0.3306 * rdw
            + 0.00188 * alk_phos
            + 0.0554 * wbc
            + 0.0804 * age
        )

        # Process through transformations
        xb = np.clip(xb, -30, 30)
        exp_xb = np.exp(xb)
        M = 1 - np.exp(-1.51714 * exp_xb / 0.0076927)
        M = np.clip(M, 1e-5, 1 - 1e-5)

        # Calculate final age
        phenotypic_age = 141.50 + (np.log(-0.00553 * np.log(1 - M))) / 0.09165
        phenotypic_age = max(0, min(phenotypic_age, 120))  # Clamp to valid range

        print(f"[DEBUG] XB = {xb:.2f}, M = {M:.6f}, PhenoAge = {phenotypic_age:.2f}")
        return round(phenotypic_age, 2)

    except Exception as e:
        print("[ERROR] Phenotypic Age calculation failed:", e)
        return None
