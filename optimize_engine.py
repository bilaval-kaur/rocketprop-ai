import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from scipy.optimize import minimize

conn = sqlite3.connect("data/processed/rocketprop.db")
df = pd.read_sql_query("""
SELECT p.oxidizer, p.fuel, s.of_ratio, s.Pc_psia, s.eps, s.Pamb_psia, s.Isp_s
FROM simulations s
JOIN propellants p ON s.propellant_id = p.propellant_id
""", conn)
conn.close()

df_encoded = pd.get_dummies(df, columns=["oxidizer", "fuel"])
X = df_encoded.drop(columns=["Isp_s"])
y = df_encoded["Isp_s"]

# Train on the FULL dataset now (not train/test split) since we're deploying this
# model for actual use, not evaluating its accuracy anymore
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

feature_columns = X.columns.tolist()
print("Feature columns:", feature_columns)
def make_objective(oxidizer, fuel, pamb_fixed):
    """
    Returns an objective function for a specific propellant and fixed ambient pressure.
    The returned function takes [of_ratio, Pc_psia, eps] and returns -predicted_Isp.
    """
    def objective(x):
        of_ratio, pc, eps = x
        row = {
            "of_ratio": of_ratio,
            "Pc_psia": pc,
            "eps": eps,
            "Pamb_psia": pamb_fixed,
            "oxidizer_LOX": 1 if oxidizer == "LOX" else 0,
            "oxidizer_N2O4": 1 if oxidizer == "N2O4" else 0,
            "fuel_LH2": 1 if fuel == "LH2" else 0,
            "fuel_MMH": 1 if fuel == "MMH" else 0,
            "fuel_RP-1": 1 if fuel == "RP-1" else 0,
        }
        X_row = pd.DataFrame([row])[feature_columns]
        predicted_isp = model.predict(X_row)[0]
        return -predicted_isp  # negative because we minimize, but want to maximize Isp
    return objective

# --- Define search bounds per propellant (matching our original dataset ranges) ---
propellant_bounds = {
    ("LOX", "RP-1"): {"of_range": (2.0, 3.8), "pc_range": (300, 3000), "eps_range": (5, 100)},
    ("LOX", "LH2"):  {"of_range": (4.0, 7.0), "pc_range": (300, 3000), "eps_range": (5, 100)},
    ("N2O4", "MMH"): {"of_range": (1.5, 2.5), "pc_range": (300, 3000), "eps_range": (5, 100)},
}

# --- Optimize each propellant separately, at vacuum (Pamb=0) ---
print("\n--- Optimal configuration per propellant (vacuum, Pamb=0) ---")
for (ox, fuel), bounds in propellant_bounds.items():
    obj_fn = make_objective(ox, fuel, pamb_fixed=0.0)

    of_range = bounds["of_range"]
    pc_range = bounds["pc_range"]
    eps_range = bounds["eps_range"]

    # Starting guess: midpoint of each range
    x0 = [np.mean(of_range), np.mean(pc_range), np.mean(eps_range)]

    result = minimize(
        obj_fn,
        x0,
        bounds=[of_range, pc_range, eps_range],
        method="L-BFGS-B"
    )

    best_of, best_pc, best_eps = result.x
    best_isp = -result.fun

    print(f"\n{ox}/{fuel}:")
    print(f"  Optimal O/F:  {best_of:.2f}")
    print(f"  Optimal Pc:   {best_pc:.0f} psia")
    print(f"  Optimal eps:  {best_eps:.1f}")
    print(f"  Predicted Isp: {best_isp:.1f} s")