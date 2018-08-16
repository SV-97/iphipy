
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

import Basics.Basics as base
import Basics.Complex as cmplx
import Basics.Convert as conv
import Basics.Filters as fltr
import Basics.Systems as sys
import Metrology
import threading

sp.init_printing()
"""Package Doc
ToDo:
Multiprocess Evaluation of Systems to speed up the currently exorbitantly long calculation times or implementing calculations in C
Renaming all modules to snake case

"""
"""Uncomment on release
if __name__ == "__main__":
    raise ImportWarning("This is a module and should not to be executed")
"""

def system_test():
    print("")
    print(" -- -"*20)
    print("Examples")
    print(" -- -"*20)
    sp.init_printing()
    f = sys._ee_symbol("f") # define your frequency
    R1 = sys.Resistor("R1", 100) # define your components
    R2 = sys.Resistor("R2", 100)
    L1 = sys.Inductance("L1", 10e-3, f)
    C1 = sys.Capacitor("C1", 20e-6, f)
    C2 = sys.Capacitor("C2", 10e-3, f)
    Z1 = sys.System("Z1", (R1, L1, C1, R2)) # define your circuit
    Z2 = sys.System("Z2", (C2, Z1), "parallel")  
    p1 = Z2.nyquist(range(0, int(20e3)), f, mode = "impedance") # plot everything
    p2 = Z2.nyquist(range(0, int(20e3)), f, mode = "admittance")
    p1.join()
    p2.join()
    print("Symbolic expressions are:") # get all your equations
    print("Z1 = {}".format(Z1.symbolic_impedance))
    print("Z2 = {}".format(Z2.symbolic_impedance))
    print("Y1 = {}".format(Z1.symbolic_admittance))
    print("Y2 = {}".format(Z2.symbolic_admittance))
    print("Partially evaluated expressions are:")
    print("Z1 = {}".format(Z1.impedance))
    print("Z2 = {}".format(Z2.impedance))
    print("Y1 = {}".format(Z1.admittance))
    print("Y2 = {}".format(Z2.admittance))
    print("f_resonance = {}Hz".format(Z2.resonance(f))) # do some fancy maths and get your resonance frequency ( or not if your system doesn't have one )
    print(Z1) # Or get all information on the system by just printing it
    print(Z2)
system_test()