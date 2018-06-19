
import sympy as sp
from numpy import ndarray, asarray
import mpmath

class System():

    @staticmethod
    def ps_conv(x): # conversion from series to parallel and vice versa
        if x == () or x == 0:
            return 0
        return 1/sum(tuple(1/x[i] for i in range(len(x))))
    
    @staticmethod
    def CCE(c):
        return sp.simplify(sp.conjugate(c)/sp.Abs(c)).doit()

    def set(self, sym, val, mode = "Z",*, eval = False):
        # sets a symbol sym in the calling System to a value val 
        # in case of iterable input the symbol is substituted for each one and a list with all solutions returned
        # mode can be Y or Z and selects if values are assigned to Y or Z  
        # if eval == true the output is converted to a python complex
        if type(sym) != sp.Symbol:
            raise TypeError("sym parameter has to be a symbol!")
        t = type(val)
        if mode == "Z":
            param = self.Z
        elif mode == "Y":
            param = self.Y
        else:
            raise ValueError('mode parameter has to be "Y" or "Z"')
        if t == list or t == tuple or t == ndarray:
            out = []
            for i in range(len(val)):
                if eval:
                    out.append(complex(param.subs(sym,val[i])))
                else:
                    out.append(param.subs(sym,val[i]))
            return asarray(out)
        param = param.subs(sym,val)
        if mode == "Z":
            self.Z = param
        elif mode == "Y":
            self.Y = param

            
    def Resonance(self, f = sp.symbols("f"), start = 0.1e-50):
        # calculate resonance frequency of system
        # f is symbol for frequency in system
        # start is the frequency from which the system is evaluated, zero isn't possible
        #Z_im = sp.im(self.Z)
        #Z_im_of_f = sp.lambdify(f, Z_im, "numpy")
        #f_re = mpmath.findroot(Z_im,0)
        return mpmath.findroot(sp.lambdify(f,sp.im(self.Z),"numpy"), start)

    def MinZ(self, f = sp.symbols("f"), start = 0.1e-50):
        # calculate frequency with min Abs(Z) of system
        # derives |Y| with f and finds root
        return mpmath.findroot(
            sp.lambdify(
                f, sp.diff(
                    sp.Abs(self.Y), f
                    ) 
                )
            , start)

    def __init__(self, f, conf = "s", Z = (), R=(), L = (), C = (), Y = (), G = ()):
        # conf sets configuration of elements(in series or parallel) with "s" and "p"
        # the other parameters can be set either to strings that sp.symbols can convert to symbols or tuples of sympy symbols
        params = [Z,R,L,C,Y,G]
        for i in range(len(params)):
            if not isinstance(params[i], (type(sp.symbol), sp.Add, sp.Mul)) and params[i] != ():
                if type(params[i]) == tuple:
                    if isinstance(params[i][0], (type(sp.symbol), sp.Add, sp.Mul)):
                        break
                params[i] = sp.symbols(params[i], seq=True)
                #if type(params[i]) != tuple:
                #    params[i] = (params[i],)
        Z,R,L,C,Y,G = params
        self.R = R
        try:
            self.R += (1/System.ps_conv(G))
        except:
            pass

        self.Rg = sum(R)
        self.L = L
        self.Lg = sum(L)
        self.C = C
        self.Cg = System.ps_conv(C) # TODO abfrage nach conf fehlt
        self.Z = Z
        self.Y = Y
        self.f = f
        self.omega = 2*sp.pi*f
        print("{}\n{}".format(type(self.f),type(self.f)))
        self.config = conf
        if conf == "s":
            self.Z = sp.simplify(sum(self.Z) + 
                                 System.ps_conv(sum(self.Y)) + 
                                 self.Rg +
                                 sp.I*( self.omega*self.Lg 
                                     - self.omega*
                                     self.Cg ))
            self.Y = System.CCE(self.Z)
        else:
            self.Y = sp.simplify(System.ps_conv(sum(self.Z)) + sum(self.Y) + 1/System.ps_conv(self.R) + sp.I* (1/(self.omega*self.Cg) - 1/(self.omega*self.Lg)))
            self.Z = System.CCE(self.Y)
