import sympy as sp
import numpy as np
import mpmath

"""Provides classes for dealing with electrical circuits
Todo:
    Resonance frequency calculation
    Evaluation with values (should be possible atm but only via sympy)
"""

def _ee_symbol(name):
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
        self.symbol = _ee_symbol(name)
        self.value = value
        self._impedance = None
        self._admittance = None
        self._symbolic_impedance = None
        self._symbolic_admittance = None

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
        self.frequency = frequency if isinstance(frequency, sp.Symbol) else _ee_symbol(frequency)

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
        if self.mode =="series":
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

    def __init__(self, name, components, mode = "series",):
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