from rocketcea.cea_obj import CEA_Obj

cea = CEA_Obj(oxName="LOX", fuelName="RP-1")

Pc = 1000
MR = 2.3
eps = 16.0

isp, cstar, tc = cea.get_IvacCstrTc(Pc=Pc, MR=MR, eps=eps)

print(f"Isp   = {isp:.1f} s")
print(f"C*    = {cstar:.1f} ft/s")
print(f"Tc    = {tc:.1f} R")
from rocketcea.cea_obj import CEA_Obj

cea = CEA_Obj(oxName="LOX", fuelName="RP-1")

Pc = 1000
MR = 2.3
eps = 16.0

isp, cstar, tc = cea.get_IvacCstrTc(Pc=Pc, MR=MR, eps=eps)
mw, gamma = cea.get_Chamber_MolWt_gamma(Pc=Pc, MR=MR, eps=eps)

print(f"Isp   = {isp:.1f} s")
print(f"C*    = {cstar:.1f} ft/s")
print(f"Tc    = {tc:.1f} R")
print(f"MW    = {mw:.2f} g/mol")
print(f"gamma = {gamma:.3f}")