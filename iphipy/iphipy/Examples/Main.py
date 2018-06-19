# i phi py
# examples below

import iphipy as ec
import iphipy.Basics.Basics as bs
from iphipy.Basics.Complex import CCE
from iphipy.Metrology.ErrorCalculation import AbsoluteDeviation, RelativeDeviation
import iphipy.Basics.Systems as sys
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
sp.init_printing()

F = sp.symbols("f", real=True)
Z1 = sys.System(F, conf = "s", R = "R1,R2", L = "L1,L2", C = "C1")
R1,R2 = Z1.R
L1,L2 = Z1.L
C1, = Z1.C

Z2 = sys.System(F, conf = "p", R = "R3,R4", C = "C2")
R3,R4 = Z2.R
C2, = Z2.C

Z1_formula = Z1.Z
Y1_formula = Z1.Y
Z2_formula = Z2.Z
Y2_formula = Z2.Y

Z1.set(R1,150)
Z1.set(R2,100)
Z1.set(L1,10e-3)
Z1.set(L2,300e-3)
Z1.set(C1,10e-6)
Z2.set(R3, 200)
Z2.set(R4, 150)
Z2.set(C2, 500e-6)

Z3 = sys.System(F, conf = "s", Z=(Z1.Z, Z2.Z))
Z3_formula = Z3.Z
Y3_formula = Z3.Y

#print(Z1.Z.free_symbols)
print("Z = {}".format(Z3.Z))
f = np.linspace(0,100e3,50e3)

F = sp.symbols("f", real=True)
Z3_of_f = sp.lambdify(F, Z3.Z, "numpy")
Z3_eval = Z3_of_f(f)
f_res = Z3.Resonance(F)
print("Resonance frequency of Z3 is {}".format(f_res))
# print(Z1.MinZ()) not working right now
plt.plot(Z3_eval.real, Z3_eval.imag)
plt.show()
