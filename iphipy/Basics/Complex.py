import numpy as np

@np.vectorize
def CCE(c): #complex conjugated extension - equal to 1/c
    if c.imag == 0 and c.real == 0:
        return 0
    elif c.imag == 0:
        return 1/c.real
    elif c.real == 0:
        return -1j/c.imag
    else:
        return (c.real - 1j*c.imag)/(c.real**2 + c.imag**2)