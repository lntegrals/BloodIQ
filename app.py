def calculate_phenotypic_age(data):
    try:
        # Unit conversions
        albumin = float(data["albumin"]) * 10           # g/L
        creatinine = float(data["creatinine"]) * 88.4   # µmol/L
        glucose = float(data["glucose"]) / 18           # mmol/L
        crp_raw = float(data["crp"]) / 10               # mg/dL
        crp = np.log(crp_raw if crp_raw > 0 else 0.01)
        lymph_pct = float(data["lymph_pct"])
        mcv = float(data["mcv"])
        rdw = float(data["rdw"])
        alk_phos = float(data["alk_phos"])
        wbc = float(data["wbc"]) * 1000                 # cells/µL
        age = float(data["age"])

        # XB calculation
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

        xb = np.clip(xb, -30, 30)
        M = 1 - np.exp(-1.51714 * np.exp(xb) / 0.0076927)
        M = np.clip(M, 1e-5, 1 - 1e-5)

        phenotypic_age = 141.50 + (np.log(-0.00553 * np.log(1 - M))) / 0.09165

        # Debug output
        print(f"[DEBUG] xb = {xb:.2f}, M = {M:.6f}, Age = {phenotypic_age:.2f}")
        return round(phenotypic_age, 2)

    except Exception as e:
        print("[ERROR] Phenotypic Age calculation failed:", e)
        return None
