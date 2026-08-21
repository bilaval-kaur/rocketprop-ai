import sqlite3
import pandas as pd

# --- Step 1: Connect to (and create) the database file ---
conn = sqlite3.connect("data/processed/rocketprop.db")
cursor = conn.cursor()

# --- Step 2: Create the propellants table ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS propellants (
    propellant_id INTEGER PRIMARY KEY,
    oxidizer TEXT NOT NULL,
    fuel TEXT NOT NULL
)
""")

# --- Step 3: Create the simulations table ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS simulations (
    sim_id INTEGER PRIMARY KEY AUTOINCREMENT,
    propellant_id INTEGER NOT NULL,
    of_ratio REAL,
    Pc_psia REAL,
    eps REAL,
    Pamb_psia REAL,
    Isp_s REAL,
    Tc_R REAL,
    MW REAL,
    gamma REAL,
    FOREIGN KEY (propellant_id) REFERENCES propellants(propellant_id)
)
""")

# --- Step 4: Insert the 3 known propellant pairs ---
propellant_pairs = [
    (1, "LOX", "RP-1"),
    (2, "LOX", "LH2"),
    (3, "N2O4", "MMH"),
]

cursor.executemany(
    "INSERT OR IGNORE INTO propellants (propellant_id, oxidizer, fuel) VALUES (?, ?, ?)",
    propellant_pairs
)

# --- Step 5: Load the CSV and map oxidizer/fuel to propellant_id ---
df = pd.read_csv("data/raw/simulations_v1.csv")

propellant_lookup = {
    ("LOX", "RP-1"): 1,
    ("LOX", "LH2"): 2,
    ("N2O4", "MMH"): 3,
}

df["propellant_id"] = df.apply(
    lambda row: propellant_lookup[(row["oxidizer"], row["fuel"])], axis=1
)

# --- Step 6: Insert all simulation rows ---
sim_columns = ["propellant_id", "of_ratio", "Pc_psia", "eps", "Pamb_psia",
               "Isp_s", "Tc_R", "MW", "gamma"]

cursor.executemany(
    f"""INSERT INTO simulations ({', '.join(sim_columns)})
        VALUES ({', '.join(['?'] * len(sim_columns))})""",
    df[sim_columns].values.tolist()
)

# --- Step 7: Commit and close ---
conn.commit()

cursor.execute("SELECT COUNT(*) FROM propellants")
print(f"Propellants table: {cursor.fetchone()[0]} rows")

cursor.execute("SELECT COUNT(*) FROM simulations")
print(f"Simulations table: {cursor.fetchone()[0]} rows")

conn.close()
print("Database built successfully at data/processed/rocketprop.db")