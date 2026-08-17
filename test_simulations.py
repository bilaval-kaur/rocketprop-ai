from rocketcea.cea_obj import CEA_Obj
from scipy.stats import qmc
import pandas as pd

# --- Propellant definitions with realistic O/F bounds ---
propellants = [
    {"ox": "LOX", "fuel": "RP-1", "of_min": 2.0, "of_max": 3.8},
    {"ox": "LOX", "fuel": "LH2",  "of_min": 4.0, "of_max": 7.0},
    {"ox": "N2O4", "fuel": "MMH", "of_min": 1.5, "of_max": 2.5},
]

# --- Shared ranges for the other continuous parameters ---
PC_MIN, PC_MAX = 300, 3000     # chamber pressure, psia
EPS_MIN, EPS_MAX = 5, 100      # expansion ratio
PAMB_MIN, PAMB_MAX = 0.0, 14.7 # ambient pressure, psia (vacuum to sea level)

SAMPLES_PER_PROPELLANT = 33    # ~100 total across 3 propellants

results = []  # will hold one dict per successful simulation

for prop in propellants:
    cea = CEA_Obj(oxName=prop["ox"], fuelName=prop["fuel"])

    # LHS sampler for 4 dimensions: O/F, Pc, eps, Pamb
    sampler = qmc.LatinHypercube(d=4, seed=42)
    unit_samples = sampler.random(n=SAMPLES_PER_PROPELLANT)  # values in [0,1)

    # Scale each column from [0,1) to its real parameter range
    lower_bounds = [prop["of_min"], PC_MIN, EPS_MIN, PAMB_MIN]
    upper_bounds = [prop["of_max"], PC_MAX, EPS_MAX, PAMB_MAX]
    scaled_samples = qmc.scale(unit_samples, lower_bounds, upper_bounds)

    for row in scaled_samples:
        of_ratio, pc, eps, pamb = row

        try:
            isp = cea.estimate_Ambient_Isp(Pc=pc, MR=of_ratio, eps=eps, Pamb=pamb)[0]
            tc = cea.get_Tcomb(Pc=pc, MR=of_ratio)
            mw, gamma = cea.get_Chamber_MolWt_gamma(Pc=pc, MR=of_ratio, eps=eps)

            results.append({
                "oxidizer": prop["ox"],
                "fuel": prop["fuel"],
                "of_ratio": of_ratio,
                "Pc_psia": pc,
                "eps": eps,
                "Pamb_psia": pamb,
                "Isp_s": isp,
                "Tc_R": tc,
                "MW": mw,
                "gamma": gamma,
            })
        except Exception as e:
            print(f"FAILED: {prop['ox']}/{prop['fuel']} OF={of_ratio:.2f} Pc={pc:.0f} eps={eps:.1f} Pamb={pamb:.1f} -> {e}")

df = pd.DataFrame(results)
df.to_csv("test_simulations.csv", index=False)

print(f"\nCompleted {len(df)} successful simulations out of {SAMPLES_PER_PROPELLANT * len(propellants)} attempted.")
print(df.head())
from rocketcea.cea_obj import CEA_Obj
from scipy.stats import qmc
import pandas as pd
import time

propellants = [
    {"ox": "LOX", "fuel": "RP-1", "of_min": 2.0, "of_max": 3.8},
    {"ox": "LOX", "fuel": "LH2",  "of_min": 4.0, "of_max": 7.0},
    {"ox": "N2O4", "fuel": "MMH", "of_min": 1.5, "of_max": 2.5},
]

PC_MIN, PC_MAX = 300, 3000
EPS_MIN, EPS_MAX = 5, 100
PAMB_MIN, PAMB_MAX = 0.0, 14.7

SAMPLES_PER_PROPELLANT = 33

results = []
start_time = time.time()

for prop in propellants:
    cea = CEA_Obj(oxName=prop["ox"], fuelName=prop["fuel"])

    sampler = qmc.LatinHypercube(d=4, seed=42)
    unit_samples = sampler.random(n=SAMPLES_PER_PROPELLANT)

    lower_bounds = [prop["of_min"], PC_MIN, EPS_MIN, PAMB_MIN]
    upper_bounds = [prop["of_max"], PC_MAX, EPS_MAX, PAMB_MAX]
    scaled_samples = qmc.scale(unit_samples, lower_bounds, upper_bounds)

    for row in scaled_samples:
        of_ratio, pc, eps, pamb = row
        try:
            isp = cea.estimate_Ambient_Isp(Pc=pc, MR=of_ratio, eps=eps, Pamb=pamb)[0]
            tc = cea.get_Tcomb(Pc=pc, MR=of_ratio)
            mw, gamma = cea.get_Chamber_MolWt_gamma(Pc=pc, MR=of_ratio, eps=eps)

            results.append({
                "oxidizer": prop["ox"], "fuel": prop["fuel"],
                "of_ratio": of_ratio, "Pc_psia": pc, "eps": eps, "Pamb_psia": pamb,
                "Isp_s": isp, "Tc_R": tc, "MW": mw, "gamma": gamma,
            })
        except Exception as e:
            print(f"FAILED: {prop['ox']}/{prop['fuel']} -> {e}")

elapsed = time.time() - start_time
df = pd.DataFrame(results)
df.to_csv("test_simulations.csv", index=False)

n_total = len(df)
print(f"\nCompleted {n_total} simulations in {elapsed:.2f} seconds")
print(f"Average time per simulation: {elapsed/n_total*1000:.1f} ms")
print(f"Estimated time for 5,000 simulations: {elapsed/n_total*5000/60:.1f} minutes")
print(f"Estimated time for 10,000 simulations: {elapsed/n_total*10000/60:.1f} minutes")