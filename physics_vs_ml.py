import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

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

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)
y_pred = rf_model.predict(X_test)

# Build a results dataframe combining predictions with the original (non-encoded) test rows
results = df.loc[X_test.index].copy()
results["Isp_actual"] = y_test.values
results["Isp_predicted"] = y_pred
results["residual"] = results["Isp_predicted"] - results["Isp_actual"]
results["abs_error"] = results["residual"].abs()

print(results[["oxidizer", "fuel", "of_ratio", "Pc_psia", "eps", "Pamb_psia",
               "Isp_actual", "Isp_predicted", "residual"]].head())

print(f"\nMax absolute error: {results['abs_error'].max():.2f} s")
print(f"95th percentile absolute error: {results['abs_error'].quantile(0.95):.2f} s")
# --- Find and inspect the worst predictions ---
worst = results.sort_values("abs_error", ascending=False).head(10)
print("\n--- 10 Worst Predictions ---")
print(worst[["oxidizer", "fuel", "of_ratio", "Pc_psia", "eps", "Pamb_psia",
             "Isp_actual", "Isp_predicted", "residual"]])

# --- Check: does error correlate with any input feature? ---
print("\n--- Correlation of absolute error with input features ---")
feature_cols = ["of_ratio", "Pc_psia", "eps", "Pamb_psia"]
for col in feature_cols:
    corr_val = results[col].corr(results["abs_error"])
    print(f"{col}: {corr_val:.3f}")

# --- Check: does error differ by propellant? ---
print("\n--- Mean absolute error by propellant ---")
print(results.groupby(["oxidizer", "fuel"])["abs_error"].mean())
fig, ax = plt.subplots(figsize=(10, 6))
for (ox, fuel), group in results.groupby(["oxidizer", "fuel"]):
    ax.scatter(group["of_ratio"], group["abs_error"], alpha=0.4, s=15, label=f"{ox}/{fuel}")
ax.set_xlabel("O/F ratio")
ax.set_ylabel("Absolute Error (s)")
ax.set_title("Prediction Error vs O/F Ratio, by Propellant")
ax.legend()
plt.savefig("data/processed/ml_error_vs_of.png", dpi=150)
plt.show()