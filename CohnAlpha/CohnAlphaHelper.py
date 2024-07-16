import math                            # To compare floats and assign correct time units string
from pathlib import Path               # Path manipulation

# Helper Functions
def convertTimeUnitsToStr(units):
    # femtoseconds
    if (math.isclose(a=units, b=1e-15, abs_tol=1e-15)):
        return 'fs'
    # picoseconds
    if (math.isclose(a=units, b=1e-12, abs_tol=1e-12)):
        return 'ps'    
    # nano seconds
    if (math.isclose(a=units, b=1e-9, abs_tol=1e-9)):
        return 'ns'
    # microseconds
    if (math.isclose(a=units, b=1e-6, abs_tol=1e-6)):
        return 'us'
    # milliseconds
    if (math.isclose(a=units, b=1e-3, abs_tol=1e-3)):
        return 'ms'
    # seconds
    if (math.isclose(a=units, b=1, abs_tol=1)):
        return 's'



def checkPowerOfTwo(value):
    '''Function to check if value is a power of 2 or not
    Returns True if a power of 2, otherwise returns False
    Note: make value an integer, otherwise cannot properly calculate
    
    Input:
    - value (int): the value to be checked'''

    while (value > 1):
        value = value / 2

    if value == 1:
        return True
    if value < 1:
        return False