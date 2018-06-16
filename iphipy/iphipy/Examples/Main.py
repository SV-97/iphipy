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

F = sp.symbols("f")
Z1 = sys.System(F, conf = "r", R = "R1,R2", L = "L1,L2", C = "C1")
R1,R2 = Z1.R
L1,L2 = Z1.L
C1, = Z1.C

#print(Z1.Z)
#print(Z1.Y)
#print(Z1.Z.free_symbols)

Z1_formula = Z1.Z
Y1_formula = Z1.Y

Z1.set(R1,150)
Z1.set(R2,100)
Z1.set(L1,10e-3)
Z1.set(L2,300e-3)
Z1.set(C1,10e-6)
print(Z1.Z.free_symbols)
print("Z = {}".format(Z1.Z))
f = np.linspace(0,100e3,50e3)
#print
#Y1_eval = (Z1.set(F,f,"Y", eval = True))

F = sp.symbols("f")
Z1_of_f = sp.lambdify(F, Z1.Z, "numpy")
Z1_eval = Z1_of_f(f)
f_res = Z1.Resonance(F)
print(f_res)
print(Z1.MinZ())
plt.plot(Z1_eval.real, Z1_eval.imag)
plt.show()
