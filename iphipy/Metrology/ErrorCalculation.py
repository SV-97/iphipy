
import numpy as np

def AbsoluteDeviation(true, measured): # Absolute Error - measured is measured value and true the true value
    return measured-true

def RelativeDeviation(true, F): # Relative Error - F is absolute deviation and true the true value
    return F/true

def RelativeDeviationPerc(true, F): # Relative Error in % - see RelativeDeviation()
    return abs*100/true