import sqlite3

conn = sqlite3.connect("data/processed/rocketprop.db")
cursor = conn.cursor()

# --- Query: average Isp for LOX/RP-1 ---
cursor.execute("""
SELECT AVG(s.Isp_s)
FROM simulations s
JOIN propellants p ON s.propellant_id = p.propellant_id
WHERE p.oxidizer = 'LOX' AND p.fuel = 'RP-1'
""")

result = cursor.fetchone()
print(f"Average Isp for LOX/RP-1: {result[0]:.1f} s")

cursor.execute("""
SELECT p.oxidizer, p.fuel, AVG(s.Isp_s) as avg_isp, COUNT(*) as n_sims
FROM simulations s
JOIN propellants p ON s.propellant_id = p.propellant_id
GROUP BY p.propellant_id
ORDER BY avg_isp DESC
""")

for row in cursor.fetchall():
    print(f"{row[0]}/{row[1]}: avg Isp = {row[2]:.1f} s  (n={row[3]})")
cursor.execute("""
SELECT p.oxidizer, p.fuel, s.of_ratio, s.Isp_s
FROM simulations s
JOIN propellants p ON s.propellant_id = p.propellant_id
WHERE p.oxidizer = 'LOX' AND p.fuel = 'RP-1'
ORDER BY s.Isp_s DESC
LIMIT 1
""")

row = cursor.fetchone()
print(f"\nBest LOX/RP-1 config: O/F={row[2]:.2f}, Isp={row[3]:.1f} s")
cursor.execute("""
SELECT COUNT(*)
FROM simulations s
JOIN propellants p ON s.propellant_id = p.propellant_id
WHERE s.Isp_s > 350 AND s.Tc_R < 7000
""")

count = cursor.fetchone()[0]
print(f"\nConfigs with Isp > 350s AND Tc < 7000R: {count}")
conn.close()