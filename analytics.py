import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

conn = sqlite3.connect("data/processed/rocketprop.db")

df = pd.read_sql_query("""
SELECT p.oxidizer, p.fuel, s.of_ratio, s.Pc_psia, s.eps, s.Pamb_psia,
       s.Isp_s, s.Tc_R, s.MW, s.gamma
FROM simulations s
JOIN propellants p ON s.propellant_id = p.propellant_id
""", conn)

conn.close()

print(df.shape)
print(df.head())

numeric_cols = ["of_ratio", "Pc_psia", "eps", "Pamb_psia", "Isp_s", "Tc_R", "MW", "gamma"]
corr = df[numeric_cols].corr()

print("\nCorrelation with Isp_s:")
print(corr["Isp_s"].sort_values(ascending=False))

print("\n--- Correlation with Isp_s, BY PROPELLANT ---")
for (ox, fuel), group in df.groupby(["oxidizer", "fuel"]):
    corr_group = group[numeric_cols].corr()["Isp_s"].sort_values(ascending=False)
    print(f"\n{ox}/{fuel}:")
    print(corr_group)

# --- Plot 1: Isp vs Ambient Pressure ---
fig, ax = plt.subplots(figsize=(8, 6))
for (ox, fuel), group in df.groupby(["oxidizer", "fuel"]):
    ax.scatter(group["Pamb_psia"], group["Isp_s"], alpha=0.3, s=8, label=f"{ox}/{fuel}")
ax.set_xlabel("Ambient Pressure (psia)")
ax.set_ylabel("Isp (s)")
ax.set_title("Isp vs Ambient Pressure, by Propellant")
ax.legend()
plt.savefig("data/processed/isp_vs_pamb.png", dpi=150)
plt.show()

# --- Plot 2: Isp vs O/F ratio, per propellant ---
fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
for ax, ((ox, fuel), group) in zip(axes, df.groupby(["oxidizer", "fuel"])):
    ax.scatter(group["of_ratio"], group["Isp_s"], alpha=0.2, s=6, color="steelblue")
    ax.set_xlabel("O/F ratio")
    ax.set_title(f"{ox}/{fuel}")
axes[0].set_ylabel("Isp (s)")
plt.suptitle("Isp vs O/F Ratio, by Propellant (full dataset)")
plt.tight_layout()
plt.savefig("data/processed/isp_vs_of_full.png", dpi=150)
plt.show()

# --- Plot 3: Correlation heatmap ---
fig, ax = plt.subplots(figsize=(7, 6))
im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
ax.set_xticks(range(len(numeric_cols)))
ax.set_yticks(range(len(numeric_cols)))
ax.set_xticklabels(numeric_cols, rotation=45, ha="right")
ax.set_yticklabels(numeric_cols)
for i in range(len(numeric_cols)):
    for j in range(len(numeric_cols)):
        ax.text(j, i, f"{corr.iloc[i,j]:.2f}", ha="center", va="center", fontsize=8)
plt.colorbar(im)
plt.title("Correlation Matrix (full dataset, all propellants combined)")
plt.tight_layout()
plt.savefig("data/processed/correlation_heatmap.png", dpi=150)
plt.show()