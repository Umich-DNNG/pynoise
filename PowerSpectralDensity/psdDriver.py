# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 11:42:16 2023

@author: 357375
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import signal
import power_spectral_density_scripts as psd

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

                file_path = "/Users/vincentweng/Documents/PyNoise/PowerSpectralDensity/sample_data/stilbene_2in_CROCUS_20cm_offset_east.txt"
                values = np.loadtxt(file_path, usecols=(0,3), max_rows=2000000, dtype=float)

                PowSpecDens_settings = {'dwell time': 2e6, 'meas time range': [150e9,1e12]}
                
                psd.conduct_APSD(list_data_array=values, 
                                 PowSpecDens_settings=PowSpecDens_settings, 
                                 leg_label="TEST", 
                                 plt_title = "Power Spectral Density Graph", 
                                 clean_pulses_switch=1)
            case 'p':
                print()
                print('Plotting the data...')
            case 'f':
                print()
                print('Fitting the data...')


# Tells the program what function to start if this is the main program being run (TO BE DELETED)
if __name__ == "__main__":
    main()
                