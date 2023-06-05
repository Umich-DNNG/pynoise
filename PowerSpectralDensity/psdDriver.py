# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 11:42:16 2023

@author: 357375
"""

import numpy as np                    # For processing data
import matplotlib.pyplot as plt       # For plotting data summaries
from scipy.optimize import curve_fit
from scipy import signal

def main():
    selection = 'blank'
    print('You are running the Power Spectral Density Method.')
    while selection != '':
        print('You can utilize any of the following functions:')
        print('m - run the entire program through the main driver')
        print('p - plot the data')
        print('f - fit the data to a curve')
        print('Leave the command blank to end the program.')
        selection = input('Enter a command: ')
        match selection:
            case 'm':
                print()
                print('Running the entire power spectral density analysis...')
            case 'p':
                print()
                print('Plotting the data...')
            case 'f':
                print()
                print('Fitting the data...')
                