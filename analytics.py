import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("data/processed/rocketprop.db")

# Pull everything into one big DataFrame, joined and ready for analysis
df = pd.read_sql_query("""
SELECT p.oxidizer, p.fuel, s.of_ratio, s.Pc_psia, s.eps, s.Pamb_psia,
       s.Isp_s, s.Tc_R, s.MW, s.gamma
FROM simulations s
JOIN propellants p ON s.propellant_id = p.propellant_id
""", conn)

conn.close()

print(df.shape)
print(df.head())

# --- Correlation matrix (numeric columns only) ---
numeric_cols = ["of_ratio", "Pc_psia", "eps", "Pamb_psia", "Isp_s", "Tc_R", "MW", "gamma"]
corr = df[numeric_cols].corr()

print("\nCorrelation with Isp_s:")
print(corr["Isp_s"].sort_values(ascending=False))
print("\n--- Correlation with Isp_s, BY PROPELLANT ---")
for (ox, fuel), group in df.groupby(["oxidizer", "fuel"]):
    corr_group = group[numeric_cols].corr()["Isp_s"].sort_values(ascending=False)
    print(f"\n{ox}/{fuel}:")
    print(corr_group)
fig, ax = plt.subplots(figsize=(8, 6))

for (ox, fuel), group in df.groupby(["oxidizer", "fuel"]):
    ax.scatter(group["Pamb_psia"], group["Isp_s"], alpha=0.3, s=8, label=f"{ox}/{fuel}")

ax.set_xlabel("Ambient Pressure (psia)")
ax.set_ylabel("Isp (s)")
ax.set_title("Isp vs Ambient Pressure, by Propellant")
ax.legend()
plt.savefig("data/processed/isp_vs_pamb.png", dpi=150)
plt.show()