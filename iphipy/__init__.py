
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
import timeit.time

import Basics.Basics as base
import Basics.Complex as cmplx
import Basics.Convert as conv
import Basics.Filters as fltr
import Basics.Systems as sys
import Metrology


"""Package Doc
ToDo:
WIP Multiprocess Evaluation of Systems to speed up the currently exorbitantly long calculation times

if __name__ == "__main__":
    raise ImportWarning("This is a module and should not to be executed")
"""
def function_():
    print("")
    print("---"*20)
    print("Examples")
    print("---"*20)
    sp.init_printing()
    try:
        f = sys._ee_symbol("f")
        C1 = sys.Capacitor("C1", 100e-6, f)
        R1 = sys.Resistor("R1", 100)
        Z1 = sys.System("Z1", (C1,R1))
        print(R1.symbolic_impedance)
        print(C1.symbolic_impedance)
        print(Z1.symbolic_impedance)    
        f = np.linspace(0,20e3,5e3)
        frequency_band = f[1:]
        Z1_nyquist = []
        i = 0
        print(Z1.admittance)
        for f in frequency_band:
            print(i)
            i += 1
            a = complex(Z1._admittance.subs(C1.frequency, f))
            Z1_nyquist.append(a)
        Z1_nyquist = np.asarray(Z1_nyquist)
        plt.plot(Z1_nyquist.real, Z1_nyquist.imag)
    except DeprecationWarning as err:
        print(err.__str__)

    print("END")

def calculate():
    for i in range(start, stop):
        

def multiprocess(function_, number_of_processes, total_range):
    """
    Args:
        function_ (function): Function that is to be multiprocessed
        numer_of_processes (int): Number of processes to spawn
        total_range (iterable of numeric): min and max value to pass to function_
    """
    processes = [Process(target = calculate, args = (total_range/number_of_processes)) for i in range(number_of_processes)]
    
    step_size = (total_range[-1]-total_range[0])/number_of_processes
    for i in range(number_of_processes):
        
        
        processes.append(Process(target = calculate, args = ()))

    for process in processes:
        process.start()
    
    for process in processes:
        process.join()
t0 = time.time()
function_()
t1 = time.time()
plt.show()
print(t1-t0)
