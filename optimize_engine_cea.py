from rocketcea.cea_obj import CEA_Obj
from scipy.optimize import minimize
import numpy as np

def make_objective(ox, fuel, pamb_fixed):
    cea = CEA_Obj(oxName=ox, fuelName=fuel)

    def objective(x):
        of_ratio, pc, eps = x
        try:
            isp = cea.estimate_Ambient_Isp(Pc=pc, MR=of_ratio, eps=eps, Pamb=pamb_fixed)[0]
            return -isp
        except Exception:
            return 1e6  # penalize invalid/failed configurations heavily
    return objective

propellant_bounds = {
    ("LOX", "RP-1"): {"of_range": (2.0, 3.8), "pc_range": (300, 3000), "eps_range": (5, 100)},
    ("LOX", "LH2"):  {"of_range": (4.0, 7.0), "pc_range": (300, 3000), "eps_range": (5, 100)},
    ("N2O4", "MMH"): {"of_range": (1.5, 2.5), "pc_range": (300, 3000), "eps_range": (5, 100)},
}

print("--- Optimal configuration per propellant, using real CEA (vacuum, Pamb=0) ---")
for (ox, fuel), bounds in propellant_bounds.items():
    obj_fn = make_objective(ox, fuel, pamb_fixed=1e-6)

    of_range = bounds["of_range"]
    pc_range = bounds["pc_range"]
    eps_range = bounds["eps_range"]

    x0 = [np.mean(of_range), np.mean(pc_range), np.mean(eps_range)]

    result = minimize(
        obj_fn,
        x0,
        bounds=[of_range, pc_range, eps_range],
        method="Nelder-Mead"
    )

    best_of, best_pc, best_eps = result.x
    best_isp = -result.fun

    print(f"\n{ox}/{fuel}:")
    print(f"  Optimal O/F:  {best_of:.2f}")
    print(f"  Optimal Pc:   {best_pc:.0f} psia")
    print(f"  Optimal eps:  {best_eps:.1f}")
    print(f"  True CEA Isp: {best_isp:.1f} s")
# --- Constrained optimization: maximize Isp subject to Tc <= 3400 K ---
print("\n\n--- Constrained: maximize Isp subject to Tc <= 3400 K (6120 R) ---")

TC_LIMIT_R = 6120  # 3400 K converted to Rankine

def make_constrained_objective(ox, fuel, pamb_fixed, tc_limit):
    cea = CEA_Obj(oxName=ox, fuelName=fuel)

    def objective(x):
        of_ratio, pc, eps = x
        try:
            isp = cea.estimate_Ambient_Isp(Pc=pc, MR=of_ratio, eps=eps, Pamb=pamb_fixed)[0]
            tc = cea.get_Tcomb(Pc=pc, MR=of_ratio)
            if tc > tc_limit:
                return 1e6 + (tc - tc_limit)  # penalize violations proportionally
            return -isp
        except Exception:
            return 1e6
    return objective

for (ox, fuel), bounds in propellant_bounds.items():
    obj_fn = make_constrained_objective(ox, fuel, pamb_fixed=1e-6, tc_limit=TC_LIMIT_R)

    of_range = bounds["of_range"]
    pc_range = bounds["pc_range"]
    eps_range = bounds["eps_range"]

    # Try multiple starting points instead of just the midpoint
    starting_points = [
        [of_range[0], pc_range[0], eps_range[0]],   # low corner
        [of_range[1], pc_range[0], eps_range[1]],   # mixed corner
        [np.mean(of_range), np.mean(pc_range), np.mean(eps_range)],  # midpoint
        [of_range[0], pc_range[1], eps_range[0]],   # another mixed corner
    ]

    best_result = None
    for x0 in starting_points:
        result = minimize(obj_fn, x0, bounds=[of_range, pc_range, eps_range], method="Nelder-Mead")
        if best_result is None or result.fun < best_result.fun:
            best_result = result

    best_of, best_pc, best_eps = best_result.x
    feasible = best_result.fun < 1e6
    best_isp = -best_result.fun if feasible else None

    cea_check = CEA_Obj(oxName=ox, fuelName=fuel)
    actual_tc = cea_check.get_Tcomb(Pc=best_pc, MR=best_of)

    print(f"\n{ox}/{fuel}:")
    print(f"  Optimal O/F: {best_of:.2f}, Pc: {best_pc:.0f} psia, eps: {best_eps:.1f}")
    print(f"  Isp: {best_isp:.1f} s" if feasible else "  No feasible solution found")
    print(f"  Resulting Tc: {actual_tc:.0f} R ({actual_tc*5/9:.0f} K)  [limit: {TC_LIMIT_R} R / 3400 K]")