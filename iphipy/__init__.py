
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
    f = sys.ee_symbol("f") # define your frequency
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
# system_test()
def voltage_source_test():
    t, u_p, grnd, f = sys.ee_symbol("t,u_p,grnd,f")
    source1 = sys.ACSource("S1", 0.5, 0, 33, t, "AC rect")
    source2 = sys.ACSource("S2", 3, -1, 1, t, "AC sine", u_p, grnd, f)
    p1 = source1.plot(range(-10,11), t) # use plotting function
    p2 = source2.plot(range(-10,11), t)

    v1 = source1.voltage # get voltage equation
    v2 = source2.voltage
    v3 = v1+v2 # add voltages
    f_v1 = np.vectorize(sp.lambdify(t, v1)) # make lambda function from equation and vectorize it
    f_v2 = np.vectorize(sp.lambdify(t, v2))
    f_v3 = np.vectorize(sp.lambdify(t, v3))
    f_v3_sym = np.vectorize(sp.lambdify((t, u_p), source2.symbolic_voltage.subs(f, 10).subs(grnd, 0)))

    x = np.linspace(0, 5,50e3)
    y1 = f_v1(x) # calculate values
    y2 = f_v2(x)
    y3 = f_v3(x)

    plt.subplot(2,1,1) # or do it yourself
    plt.plot(x, y1, alpha=0.2)
    plt.plot(x, y2, alpha=0.5)
    plt.subplot(2,1,2)
    plt.plot(x, y3)

    y4 = [] # voltage that changes amplitude time domain
    u_p = 0.1
    for i in x:
        if i<= 2.5:
            u_p = u_p + np.exp(i) if u_p < 400 else (u_p + np.exp(i))/u_p # comment if out for nice plot
        else:
            u_p = u_p - np.log(i-2.5)
        y4.append(f_v3_sym(i, u_p))
    y4 = np.asarray(y4)
    plt.figure()
    plt.plot(x,y4)

    plt.show()
    p1.join()
    p2.join()
# voltage_source_test()
def dc_test():
    source1 = sys.DCSource("S1", 5, 0 )
    p1 = source1.plot(range(-10,11)) # use plotting function
    p1.join()
# dc_test()
def circuit_test():
    # Define all Sources you want
    t = sys.ee_symbol("t")
    source1 = sys.ACSource("source1", 10, 0, 1, t, mode = "AC sine")
    source2 = sys.ACSource("source2", 2, 0, 10, t, mode = "AC sine")
    grnd = sys.Ground()
    source3 = source1 + source2 # equal to sys.MixedSource(source1, source2)
    print(source3.peakvoltage)
    p1 = source3.plot(np.linspace(0,1/source3.frequency,100e3), t) #show voltage plot
    
    # Define your System
    f = sys.ee_symbol("f") # define your frequency
    R1 = sys.Resistor("R1", 100) # define your components
    R2 = sys.Resistor("R2", 100)
    R3 = sys.Resistor("R3", 1e3)
    L1 = sys.Inductance("L1", 10e-3, f)
    C1 = sys.Capacitor("C1", 20e-6, f)
    Z1 = sys.System("Z1", (R1, L1, C1, R2)) # define your systems
    Z2 = sys.System("Z2", (R3, Z1), "parallel")  

    # Define your Circuit
    crct = sys.Circuit(source3, Z2, grnd)
    print(crct.current)
    p2 = crct.plot(np.linspace(0,1/source3.frequency,100e3), t, complex_ = True)
    p1.join()
    p2.join()
circuit_test()
print("end")