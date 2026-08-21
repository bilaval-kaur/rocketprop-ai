import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split

conn = sqlite3.connect("data/processed/rocketprop.db")
df = pd.read_sql_query("""
SELECT p.oxidizer, p.fuel, s.of_ratio, s.Pc_psia, s.eps, s.Pamb_psia, s.Isp_s
FROM simulations s
JOIN propellants p ON s.propellant_id = p.propellant_id
""", conn)
conn.close()

# One-hot encode the categorical propellant columns
df_encoded = pd.get_dummies(df, columns=["oxidizer", "fuel"])

print(df_encoded.head())
print(df_encoded.columns.tolist())

# Separate features (X) from target (y)
X = df_encoded.drop(columns=["Isp_s"])
y = df_encoded["Isp_s"]

# Split into train/test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\nTraining set size: {len(X_train)}")
print(f"Test set size: {len(X_test)}")
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"\n--- Linear Regression Performance ---")
print(f"MAE:  {mae:.2f} s")
print(f"RMSE: {rmse:.2f} s")
print(f"R²:   {r2:.4f}")
from sklearn.ensemble import RandomForestRegressor

rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

y_pred_rf = rf_model.predict(X_test)

mae_rf = mean_absolute_error(y_test, y_pred_rf)
rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
r2_rf = r2_score(y_test, y_pred_rf)

print(f"\n--- Random Forest Performance ---")
print(f"MAE:  {mae_rf:.2f} s")
print(f"RMSE: {rmse_rf:.2f} s")
print(f"R²:   {r2_rf:.4f}")
from sklearn.ensemble import GradientBoostingRegressor

gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
gb_model.fit(X_train, y_train)

y_pred_gb = gb_model.predict(X_test)

mae_gb = mean_absolute_error(y_test, y_pred_gb)
rmse_gb = np.sqrt(mean_squared_error(y_test, y_pred_gb))
r2_gb = r2_score(y_test, y_pred_gb)

print(f"\n--- Gradient Boosting Performance ---")
print(f"MAE:  {mae_gb:.2f} s")
print(f"RMSE: {rmse_gb:.2f} s")
print(f"R²:   {r2_gb:.4f}")
from sklearn.model_selection import cross_val_score

cv_scores = cross_val_score(rf_model, X, y, cv=5, scoring="r2")
print(f"\n--- Random Forest 5-Fold Cross-Validation ---")
print(f"R² scores per fold: {cv_scores}")
print(f"Mean R²: {cv_scores.mean():.4f}  (+/- {cv_scores.std():.4f})")