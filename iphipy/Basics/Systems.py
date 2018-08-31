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
    DC-equivalent voltage calculation of voltage: solve U² = 1/T * integral from 0 to T of u² for u²
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
        #t = threading.Thread(target = self._nyquist, name = "nyquist plot {} {}".format(mode, self.name), args = (range, frequency, mode))
        #t.start()
        #return t
        p = Process(target = self._nyquist, name = "nyquist plot {} {}".format(mode, self.name), args = (range_, frequency, mode))
        p.start()
        return p

class VoltageSource():
    def __init__(self, name, mode, voltage, reference = 0 ):
        """Represents a general voltage source
        Args:
            mode (str): Type of voltage, can be "DC", "AC sine", "AC tri", "AC rect"
            voltage (float): Peak voltage
            offset (float): DC offset of the voltage
            reference (float): reference voltage, usually ground but there for convenience
        """
        self.name = name
        self.mode = mode
        self.reference = reference
        self.voltage = voltage+reference
    
class DCSource(VoltageSource):
    """DC Source for various waveforms
    Args:
        mode (str): Type of voltage, can be "DC", "AC sine", "AC tri", "AC rect" - For an DCSource it ideally is DC
        name (str): Name of the source
        peakvoltage (float): [V] Peak value of the voltage
        reference (float): [V] Reference for voltage. Basically a DC-Offset
    """
    def __init__(self, name, voltage, reference, mode = "DC"):
        super().__init__(self, mode, voltage, reference)

    
    def _plot(self, range_):
        """Plot the voltage for the Source
        
        Args:
            range_ (range object or nparray): Range for the time
        """
        range_ = _checkrange(range_)

        lambda_func = lambda x: self.voltage
        lambda_func_vec = np.vectorize(lambda_func)
        voltage = lambda_func_vec(range_)

        plt.plot(range_, voltage)
        plt.ylabel(r"$u_{}/V$".format(self.name))
        plt.xlabel(r"$t_{}/s$".format(self.name))
        plt.gcf().canvas.set_window_title("{}".format(self.name))
        plt.show()

    def plot(self, range_):
        """Plot the voltage for the Source
        Args:
            range_ (range object or nparray): Range for the time
        Returns:
            multiprocessing.Process: Process of the plot
        """
        p = Process(target = self._plot, name = "voltage plot {}".format(self.name), args = (range_,))
        p.start()
        return p

class ACSource(VoltageSource):
    """AC Source for various waveforms
    Args:
        mode (str): Type of voltage, can be "DC", "AC sine", "AC tri", "AC rect" - For an ACSource it ideally is AC*
        name (str): Name of the source
        peakvoltage (float): [V] Peak value of the voltage
        reference (float): [V] Reference for voltage. Basically a DC-Offset
        frequency (float): [Hz] Frequency of the AC. If you have T use 1/T
        time (sp.core.symbol.Symbol): [s] Symbol of the timestep
        symbolic_peakvoltage (sp.core.symbol.Symbol): [V] Symbol for peak value of the voltage
        symbolic_reference (sp.core.symbol.Symbol): Symbol for reference for voltage.
        symbolic_frequency (sp.core.symbol.Symbol): Symbol for Frequency of the AC.
        phase (string): Phaseshift as string with unit in form "value"+"unit". see _str_to_rad() for units
    Attributes:
        phase (float): [rad] Phaseshift
        voltage (sp.core.symbol.Symbol): Equation of the wave
        symbolic_voltage (sp.core.symbol.Symbol): Symbolic Equation of the wave
    """
    @staticmethod
    def _sinewave(peak, frequency, time, phase, reference):
        """Returns function of a sinewave
        Args:
            peak (numeric or sp.core.symbol.Symbol): [V] peak voltage of the wave
            frequency (numeric or sp.core.symbol.Symbol): [Hz] frequency of the wave
            time (sp.core.symbol.Symbol): [s] the time interval over which to calculate values
            phase (numeric or sp.core.symbol.Symbol): [rad] phaseshift angle
            reference (numeric or sp.core.symbol.Symbol): [V] Reference Voltage / DC Offset
        Returns:
            sp.core.symbol.Symbol: Function of a sinewave with the given values
        """
        return peak*sp.sin( 2*np.pi*frequency*time+phase )+reference
    @staticmethod
    def _triwave(peak, frequency, time, phase, reference):
        """Returns function of a triangular wave
        Args:
            peak (numeric or sp.core.symbol.Symbol): [V] peak voltage of the wave
            frequency (numeric or sp.core.symbol.Symbol): [Hz] frequency of the wave
            time (sp.core.symbol.Symbol): [s] Symbol of the time interval over which to calculate values
            phase (numeric or sp.core.symbol.Symbol): [rad] phaseshift angle
            reference (numeric or sp.core.symbol.Symbol): [V] Reference Voltage / DC Offset
         Returns:
            sp.core.symbol.Symbol: Function of a triangular wave with the given values
        """
        """Alternative function
        steps = [i/(4*frequency) for i in np.linspace(1, 4, 4)]
        slope = 4*peak*frequency # delta u/ delta t = peak / (1/(4*frequency))
        
        @np.vectorize
        def tri(x): # building triwave with lines
            xv = x+phase*steps[3]/(2*np.pi)
            if xv > steps[3]:
                xv -= xv//steps[3]*steps[3]
            if  0 <= xv and xv <= steps[0]:
                return (np.vectorize(lambda x: slope*(x)+reference))(xv)
            elif steps[0] < xv and xv <= steps[2]:
                return (np.vectorize(lambda x: -slope*(x-1/(2*frequency))+reference))(xv)
            elif steps[2] < xv and xv <= steps[3]:
                return (np.vectorize(lambda x: slope*(x-1/(frequency))+reference))(xv)
        """
        T = 1/frequency
        def tri2(time): # triwave formula
            time = time - T/4-phase*T/(2*np.pi)
            abs_ = sp.Max((1-((2*frequency*time)%2)), -1)
            return 2*peak*sp.Abs(abs_)-peak+reference
        return tri2(time)
    @staticmethod
    def _rectwave(peak, frequency, time, phase, reference):
        """Returns function of a rectangular wave
        Args:
            peak (numeric or sp.core.symbol.Symbol): [V] peak voltage of the wave
            frequency (numeric or sp.core.symbol.Symbol): [Hz] frequency of the wave
            time (sp.core.symbol.Symbol): [s] Symbol of the time interval over which to calculate values
            phase (numeric or sp.core.symbol.Symbol): [rad] phaseshift angle
            reference (numeric or sp.core.symbol.Symbol): [V] Reference Voltage / DC Offset
         Returns:
            sp.core.symbol.Symbol: Function of a square wave with the given values
        """
        T = 1/frequency
        exp = sp.floor(2*(time-phase)/T)
        return peak * sp.Pow(-1, exp) + reference

    @staticmethod
    def _check_sublist(lst1, lst2):
        """Check if a list contains one element from another list
        Args:
            lst1 (iterable): List to search in
            lst2 (iterable): List with values
        Examples:
            >>> a = ["a", "A"]
            >>> b = ["b", "B"]
            >>> c = "Ac2"
            >>> ACSource._check_sublist(c, a)
            True
            >>> ACSource._check_sublist(c, b)
            False
        """
        if [ True for i in lst1 if i in lst2 ]: # empty lists are evaluated as False, nonempty ones as True
            return True
        else:
            return False
    @staticmethod
    def _str_to_rad(string):
        """converts a string in the form of "value"+"unit" to an rad value
        "rad" as value is optional
        """
        if isinstance(string, int):
            return string
        deg = ["deg", "°"]
        rad = ["rad", ]
        if ACSource._check_sublist(string, rad):
            for exp in rad: # remove the unit from the string
                string = string.replace(exp, "")
            string = int(string)
        elif ACSource._check_sublist(string, deg):
            for exp in deg: # remove the unit from the string
                string = string.replace(exp, "")
            string = int(string)
            string *= (np.pi)/(180) # 2*pi[rad] over 360[deg]
        else:
            try:
                string = int(string)
            except ValueError:
                raise ValueError("String doesn't have a valid unit or is no number")
        return string
    
    def __init__(self, name, peakvoltage, reference, frequency, time, mode = "AC sine",\
        symbolic_peakvoltage = None, symbolic_reference = None, symbolic_frequency = None, \
        phase = "0"):
        super().__init__(name, mode, peakvoltage, reference)
        self.frequency = frequency
        self.time = time
        self.phase = self._str_to_rad(phase)
        self.period = 1/frequency
        self.peakvoltage = peakvoltage
        
        if None in (symbolic_peakvoltage, symbolic_reference, symbolic_frequency):
            self._symbolic = False
        else:
            self._symbolic = True
            self.symbolic_peakvoltage = symbolic_peakvoltage
            self.symbolic_reference = symbolic_reference
            self.symbolic_frequency = symbolic_frequency
            if self.mode == "AC sine":
                self.symbolic_voltage = self._sinewave(symbolic_peakvoltage, symbolic_frequency, time, self.phase, symbolic_reference)
            elif self.mode == "AC tri":
                self.symbolic_voltage = self._triwave(symbolic_peakvoltage, symbolic_frequency, time, self.phase, symbolic_reference)
            elif self.mode == "AC rect":
                self.symbolic_voltage = self._rectwave(symbolic_peakvoltage, symbolic_frequency, time, self.phase, symbolic_reference)
            else:
                raise ValueError("Selected mode doesn't exist")
        if self.mode == "AC sine":
            self.voltage = self._sinewave(peakvoltage, frequency, time, self.phase, reference)
        elif self.mode == "AC tri":
            self.voltage = self._triwave(peakvoltage, frequency, time, self.phase, reference)
        elif self.mode == "AC rect":
            self.voltage = self._rectwave(peakvoltage, frequency, time, self.phase, reference)
        else: 
            raise ValueError("Selected mode doesn't exist")

    def _plot(self, range_, time):
        """Plot the voltage for the Source
        
        Args:
            range_ (range object or nparray): Range for the time
            time (sp.core.symbol.Symbol): Symbol of the time of the system
        """
        range_ = _checkrange(range_)

        lambda_func = sp.lambdify(time, self.voltage)
        lambda_func_vec = np.vectorize(lambda_func)
        voltage = lambda_func_vec(range_)

        plt.plot(range_, voltage)
        plt.ylabel(r"$u_{0}/V$".format(self.name))
        plt.xlabel(r"$t_{0}/s$".format(self.name))
        plt.gcf().canvas.set_window_title("{}".format(self.name))
        plt.show()

    def plot(self, range_, time):
        """Plot the voltage for the Source
        Args:
            range_ (range object or nparray): Range for the time
            time (sp.core.symbol.Symbol): Symbol of the time of the system
        Returns:
            multiprocessing.Process: Process of the plot
        """
        p = Process(target = self._plot, name = "voltage plot {}".format(self.name), args = (range_, time))
        p.start()
        return p