import mpmath
from multiprocessing import Process
import threading
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

"""Provides classes for dealing with electrical circuits
ToDo:
implementing __slots__() for all classes(no inheritance!)
finding out why DC plotting process name is messed up
"""

def _checkrange(range_):
        if len(range_)<=500:
            range_ = np.linspace(range_[0],range_[-1], 50e3)
        range_ = np.asarray(range_)
        return range_

def ee_symbol(name):
    """generate a sympy symbol with settings fitting for electrical engineering applications
    """
    return sp.symbols(name, real = True, nonzero = True)

class Component():
    """General Electrical Component
    Attributes:
        impedance (numeric): Impedance of the Component
        admittance (numeric): Admittance of the Component
        symbolic_impedance (sp.core.symbol.Symbol): Impedance of the Component as symbolic expression
        symbolic_admittance (sp.core.symbol.Symbol): Admittance of the Component as symbolic expression
    """

    def get_impedance(self): # could eventually be implemented as a method since only read is needed
        return self._impedance
    def get_admittance(self):
        return self._admittance
    def get_symbolic_impedance(self):
        return self._symbolic_impedance
    def get_symbolic_admittance(self):
        return self._symbolic_admittance
    
    _doc = "Read-Only Property"
    impedance = property(get_impedance, None, None, _doc)
    admittance = property(get_admittance, None, None, _doc)
    symbolic_impedance = property(get_symbolic_impedance, None, None, _doc)
    symbolic_admittance = property(get_symbolic_admittance, None, None, _doc)
    del _doc

    def __init__(self, name, value):
        self.name = name
        self.symbol = ee_symbol(name)
        self.value = value
        self._impedance = None
        self._admittance = None
        self._symbolic_impedance = None
        self._symbolic_admittance = None

    def __str__(self):
        return "{class_} {name} = {value}".format(class_ = self.__class__.__name__, name = self.name, value = self.value)

class Resistor(Component):
    """Resistive load
    
    """
    def get_impedance(self):
        self._impedance = self.value
        return self._impedance
    def get_admittance(self):
        self._admittance = 1/self.value
        return self._admittance
    def get_symbolic_impedance(self):
        self._symbolic_impedance = self.symbol
        return self._symbolic_impedance
    def get_symbolic_admittance(self):
        self._symbolic_admittance = 1/self.symbol
        return self._symbolic_admittance

    _doc = "Read-Only Property"
    impedance = property(get_impedance, None, None, _doc)
    admittance = property(get_admittance, None, None, _doc)
    symbolic_impedance = property(get_symbolic_impedance, None, None, _doc)
    symbolic_admittance = property(get_symbolic_admittance, None, None, _doc)
    del _doc

    def __init__(self, name, value):
        super().__init__(name, value)

class FrequencyDependentComponent(Component):
    """General frequency dependant resistor
    Attributes:
        frequency (sp.core.symbol.Symbol): Symbol of the frequency of the system
    """
    def __init__(self, name, value, frequency):
        """
        Args:
            frequency (str or sp.core.symbol.Symbol): Frequency that's to be used in expressions of the Component
        """
        super().__init__(name, value)
        self.frequency = frequency if isinstance(frequency, sp.Symbol) else ee_symbol(frequency)

class Capacitor(FrequencyDependentComponent):
    """Capacitive Load
    Attributes:
        impedance (numeric): Impedance of the Component - Can be Complex
        admittance (numeric): Admittance of the Component - Can be Complex
        symbolic_impedance (sp.core.symbol.Symbol): Impedance of the Component as symbolic expression - Can be Complex
        symbolic_admittance (sp.core.symbol.Symbol): Admittance of the Component as symbolic expression - Can be Complex
    """
    def get_impedance(self):
        self._impedance = -1*sp.I/(2*np.pi*self.frequency*self.value)
        return self._impedance
    def get_admittance(self):
        self._admittance = 1*sp.I*2*np.pi*self.frequency*self.value
        return self._admittance
    def get_symbolic_impedance(self):
        self._symbolic_impedance = -1*sp.I/(2*sp.pi*self.frequency*self.symbol)
        return self._symbolic_impedance
    def get_symbolic_admittance(self):
        self._symbolic_admittance = 1*sp.I*2*sp.pi*self.frequency*self.symbol
        return self._symbolic_admittance

    _doc = "Read-Only Property"
    impedance = property(get_impedance, None, None, _doc)
    admittance = property(get_admittance, None, None, _doc)
    symbolic_impedance = property(get_symbolic_impedance, None, None, _doc)
    symbolic_admittance = property(get_symbolic_admittance, None, None, _doc)
    del _doc

    def __init__(self, name, value, frequency):
        super().__init__(name, value, frequency)

class Inductance(FrequencyDependentComponent):
    """Inductive Load
     Attributes:
        impedance (numeric): Impedance of the Component - Can be Complex
        admittance (numeric): Admittance of the Component - Can be Complex
        symbolic_impedance (sp.core.symbol.Symbol): Impedance of the Component as symbolic expression - Can be Complex
        symbolic_admittance (sp.core.symbol.Symbol): Admittance of the Component as symbolic expression - Can be Complex
    """
    def get_impedance(self):
        self._impedance = 1*sp.I*2*np.pi*self.frequency*self.value
        return self._impedance
    def get_admittance(self):
        self._admittance = -1*sp.I/(2*np.pi*self.frequency*self.value)
        return self._admittance
    def get_symbolic_impedance(self):
        self._symbolic_impedance = 1*sp.I*2*sp.pi*self.frequency*self.symbol
        return self._symbolic_impedance
    def get_symbolic_admittance(self):
        self._symbolic_admittance = -1*sp.I/(2*sp.pi*self.frequency*self.symbol)
        return self._symbolic_admittance

    _doc = "Read-Only Property"
    impedance = property(get_impedance, None, None, _doc)
    admittance = property(get_admittance, None, None, _doc)
    symbolic_impedance = property(get_symbolic_impedance, None, None, _doc)
    symbolic_admittance = property(get_symbolic_admittance, None, None, _doc)
    del _doc

    def __init__(self, name, value, frequency):
        super().__init__(name, value, frequency)

class System(Component):
    """Represents parallel or series circuitry of electrical components and subsystems

    """
    def _modecheck(self):
        """Check if current mode is a valid configuration/circuit
            Prevents stuff like mode = "wrongmode"
        """
        if self.mode not in ("series", "parallel"):
            raise ValueError("Selected mode doesn't exist")

    def _refresh(self, property_):
        """Refresh a property
        In case the components changed since instantiation a correct value is assured
        Args:
            property_ (string): Name of the property that's to be updated
        Returns:
            The internal property
        """
        self._modecheck()
        internal_property = "_"+property_
        sum_ = sum(getattr(cmp, property_) for cmp in self.components)
        if self.mode == "series":
            if property_ in ("impedance", "symbolic_impedance"):
                setattr(self, internal_property, sum_)
            else:
                setattr(self, internal_property, 1/sum_)
        else:
            if property_ in ("impedance", "symbolic_impedance"):
                setattr(self, internal_property, 1/sum_)
            else:
                setattr(self, internal_property, sum_)
        return getattr(self, internal_property)

    def get_impedance(self):
        return self._refresh("impedance")
    def get_admittance(self):
        return self._refresh("admittance")
    def get_symbolic_impedance(self):
        return self._refresh("symbolic_impedance")
    def get_symbolic_admittance(self):
        return self._refresh("symbolic_admittance")
    
    _doc = "Read-Only Property"
    impedance = property(get_impedance, None, None, _doc)
    admittance = property(get_admittance, None, None, _doc)
    symbolic_impedance = property(get_symbolic_impedance, None, None, _doc)
    symbolic_admittance = property(get_symbolic_admittance, None, None, _doc)
    del _doc

    def __init__(self, name, components, mode = "series", ):
        """
        Args:
            name (str): Name of the symbol for the system
            components(tuple of :Component:): All the components in the circuit, including subsystems.
            mode (str): Either 'series' or 'parallel'. Calculations are done based upon current mode.
        """
        super().__init__(name, None)
        del self.value # Systems don't have a value
        self.mode = mode
        self.components = components

    def __str__(self):
        return """System {name} with Components {cmp}
        Configuration = {mode}
        Equations are:
        Impedance: {imp}
        Admittance: {admt}
        """.format(name = self.name, cmp = list(map(lambda s: str(s), self.components)), imp = self.symbolic_impedance, admt = self.symbolic_admittance, mode = self.mode)

    def resonance(self, frequency):
        """Get resonance frequency of system
        Args:
            f (sp.core.symbol.Symbol): Symbol of the frequency of the system
        Returns:
            complex: resonance frequency
        """
        abs_ = sp.Abs(self.impedance)
        derivative = sp.diff(abs_, frequency)
        return mpmath.findroot(sp.lambdify(frequency, derivative), 1)

    def _nyquist(self, range_, frequency, mode):
        """Plot a nyquist plot for the System
        Args:
            range_ (range object or nparray): Range for the frequency/frequencyband
            frequency (sp.core.symbol.Symbol): Symbol of the frequency of the system
            mode (str): decides if impedance or admittance is plotted
        Returns:
            multiprocessing.Process: Process of the plot
        """
        range_ = _checkrange(range_)

        if range_[0] == 0:
            range_ = range_[1:]
        elif range_[0] < 0:
            return None
        frequencyband = range_
        if mode == "impedance":
            lambda_func = sp.lambdify(frequency, self.impedance)
        elif mode == "admittance":
            lambda_func = sp.lambdify(frequency, self.admittance)
        else:
            raise ValueError("Selected mode doesn't exist")
        lambda_func = np.vectorize(lambda_func)
        nyquist = lambda_func(frequencyband)

        plt.plot(nyquist.real, nyquist.imag)
        plt.ylabel(r"Im[{}]/$\Omega$".format(self.name) if mode == "impedance" else r"Im[{}]/$S$".format(self.name))
        plt.xlabel(r"Re[{}]/$\Omega$".format(self.name) if mode == "impedance" else r"Re[{}]/$S$".format(self.name))
        plt.gcf().canvas.set_window_title("{} {}".format(mode, self.name))
        plt.show()

    def nyquist(self, range_, frequency, mode = "impedance"):
        """Plot a nyquist plot for the System in a new process
        Args:
            range_ (range object or nparray): Range for the frequency/frequencyband
            frequency (sp.core.symbol.Symbol): Symbol of the frequency of the system
            mode (str): decides if impedance or admittance is plotted
        Returns:
            multiprocessing.Process: Process of the plot
        """
        #t = threading.Thread(target=self._nyquist, name = "nyquist plot {} {}".format(mode, self.name), args = (range, frequency, mode))
        #t.start()
        #return t
        p = Process(target=self._nyquist, name = "nyquist plot {} {}".format(mode, self.name), args = (range_, frequency, mode))
        p.start()
        return p