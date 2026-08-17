from rocketcea.cea_obj import CEA_Obj
import matplotlib.pyplot as plt

cea = CEA_Obj(oxName="LOX", fuelName="RP-1")

Pc = 1000    # chamber pressure, psia (fixed for this sweep)
eps = 16.0   # expansion ratio (fixed for this sweep)

# O/F ratios to sweep across, from fuel-rich to oxidizer-rich
of_ratios = [1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0]

isp_values = []   # empty list, will hold one Isp result per O/F ratio

for mr in of_ratios:
    isp = cea.get_Isp(Pc=Pc, MR=mr, eps=eps)
    isp_values.append(isp)
    print(f"O/F = {mr:.1f}  ->  Isp = {isp:.1f} s")

# Plot the results
plt.plot(of_ratios, isp_values, marker="o")
plt.xlabel("O/F ratio (mixture ratio)")
plt.ylabel("Isp (s)")
plt.title("LOX/RP-1: Specific Impulse vs O/F Ratio")
plt.grid(True)
plt.savefig("isp_vs_of.png")
plt.show()