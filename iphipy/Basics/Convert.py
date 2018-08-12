import numpy as np

@np.vectorize
def R_to_G(R): #resistance to conductance
    return 1/R
    
@np.vectorize
def G_to_R(G): #conductance to resistance
    return 1/G

@np.vectorize
def X_to_B(X): #reactance to susceptance
    return R_to_G(X)
    
@np.vectorize
def B_to_X(B): #susceptance to reactance
    return G_to_R(B)
