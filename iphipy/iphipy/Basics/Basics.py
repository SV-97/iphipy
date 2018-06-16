
import numpy as np

##################
# equivalent component
# parallel

def Lp(L): #total inductance in parallel
    return (np.product(L))/(np.sum(L))

def Cp(C): #total capacitance in parallel
    return np.sum(C)

def Rp(R): #total resistance in parallel
    return (np.product(R))/np.sum(R)

def Gp(G): #total conductance in parallel
    return np.sum(G)

# series

def Ls(L): #total inductance in series
    return np.sum(L)

def Cs(C): #total capacitance in series
    return (np.product(C))/(np.sum(C))

def Rs(R): #total resistance in series
    return np.sum(R)

def Gs(G): #total conductance in series
    return (np.product(G))/np.sum(G)


##################
# frequency based calculations
@np.vectorize
def Omega(f): #circular frequency
    return 2*np.pi*f

def Frequencyband(stop,start=0,n=500000,*,f = (), O = 1e-50): 
    """
Frequency band with n values from start to stop
0 is automatically removed to avoid div by zero errors
If you explicitly want 0 in the band you can keep it in by setting O to that value, if you simply want it out you can do so by assigning an empty string to O. 
If you set another value to O it's added to the frequency band and it's sorted afterwards.
    """
    f = np.linspace(start,stop,n)
    if f[0] == 0 and O != 0: #remove 0 from frequencies to prevent division by zero errors
        f = f[1:]
        if type(O) != str():
            np.append(f,O)
            np.sort(f)
    if LC != (-1,):
        for i in range(len(LC)):
            if LC[i] != ():
                fr = Resonance(LC[i][0],LC[i][1])
                np.append(f,fr)
                np.sort(f) #not ideal since frequencyband is sorted every iteration
                fr_pos.append(np.where(f==fr))
                #fr_pos.append(f.index(fr))
            else:
                fr_pos.append(-1)
    else:
        fr_pos.append(-1)
    return (f,fr_pos)

@np.vectorize
def Resonance(L,C): #resonance frequency and omega of a basic parallel or series resonance circuit
    omega_r = 1/(np.sqrt(L*C))
    f_r = omega_r/(2*pi)
    return (f_r, omega_r)
