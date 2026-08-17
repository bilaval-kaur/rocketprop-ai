from rocketcea.cea_obj import CEA_Obj
from scipy.stats import qmc
import pandas as pd
import time

# --- Propellant definitions with realistic O/F bounds ---
propellants = [
    {"ox": "LOX", "fuel": "RP-1", "of_min": 2.0, "of_max": 3.8, "seed": 101},
    {"ox": "LOX", "fuel": "LH2",  "of_min": 4.0, "of_max": 7.0, "seed": 202},
    {"ox": "N2O4", "fuel": "MMH", "of_min": 1.5, "of_max": 2.5, "seed": 303},
]

# --- Shared ranges for the other continuous parameters ---
PC_MIN, PC_MAX = 300, 3000       # chamber pressure, psia
EPS_MIN, EPS_MAX = 5, 100        # expansion ratio
PAMB_MIN, PAMB_MAX = 0.0, 14.7   # ambient pressure, psia (vacuum to sea level)

SAMPLES_PER_PROPELLANT = 3334    # ~10,000 total across 3 propellants

results = []
start_time = time.time()

for prop in propellants:
    cea = CEA_Obj(oxName=prop["ox"], fuelName=prop["fuel"])

    # Each propellant gets its own LHS seed for independent, non-correlated coverage
    sampler = qmc.LatinHypercube(d=4, seed=prop["seed"])
    unit_samples = sampler.random(n=SAMPLES_PER_PROPELLANT)

    lower_bounds = [prop["of_min"], PC_MIN, EPS_MIN, PAMB_MIN]
    upper_bounds = [prop["of_max"], PC_MAX, EPS_MAX, PAMB_MAX]
    scaled_samples = qmc.scale(unit_samples, lower_bounds, upper_bounds)

    n_success = 0
    n_failed = 0

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
            n_success += 1
        except Exception as e:
            n_failed += 1

    print(f"{prop['ox']}/{prop['fuel']}: {n_success} succeeded, {n_failed} failed")

elapsed = time.time() - start_time
df = pd.DataFrame(results)

output_path = "data/raw/simulations_v1.csv"
df.to_csv(output_path, index=False)

print(f"\nTotal: {len(df)} simulations completed in {elapsed:.2f} seconds")
print(f"Saved to {output_path}")
print(df.describe())