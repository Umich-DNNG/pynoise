import math                            # To compare floats and assign correct time units string
from pathlib import Path               # Path manipulation

# Helper Functions
def convertTimeUnitsToStr(units):

    units_map = {
        1: '',
        1e-3: 'm',
        1e-6: 'u',
        1e-9: 'n',
        1e-12: 'p',
        1e-15: 'f'
    }

    return units_map[units]

def convertTimeUnitsToStrInverse(units):
    units_map = {
        1: '',
        1e-3: 'k',
        1e-6: 'M',
        1e-9: 'G',
        1e-12: 'T',
        1e-15: 'P'
    }

    return units_map[units]



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
    

def constructHDF5Path(settings:dict = {}):
    h5_path = Path(settings['Input/Output Settings']['Input file/folder']).stem
    h5_path += '_' + str(settings['CohnAlpha Settings']['Frequency Minimum'])
    h5_path += '_' + str(settings['CohnAlpha Settings']['Frequency Maximum'])
    return h5_path
