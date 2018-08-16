
import numpy as np

def cutoff_frequency_RC(R,C): 
    """Cut-off Frequency for RC High- and Lowpass filters (1st order)
    
    """
    return 1/(2*np.pi*R*C)

def cutoff_frequency_RL(R,L):
    """Cut-off Frequency for RL High- and Lowpass filters (1st order)

    """
    return R/(2*np.pi*L)

def cutoff_frequency_CL(L,C):
    """Cut-off Frequency for CL High- and Lowpass filters (2nd order)

    """
    return 1/(2*np.pi*np.sqrt(L*C))

def attenuation_U(U2, U1 = 775e-3):
    """Attenuation of Voltage, if U1 isn't specified absolute level is used
    
    """
    return 20*np.log10(U2/U1)

def attenuation_P(P2, P1 = 1e-3):
    """Attenuation of Power, if P1 isn't specified absolute level is used
    
    """
    return 10*np.log10(P2/P1)

def attenuation_I(I2, I1 = 1.29e-3):
    """Attenuation of Current, if I1 isn't specified absolute level is used
    
    """
    return 20*np.log10(I2/I1)
