# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 11:42:16 2023

@author: 357375
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import signal
from PowerSpectralDensity import PSD as psd

editor = None

def main(editorIn):
    global editor
    editor = editorIn
    selection = 'blank'
    print('You are running the Power Spectral Density Method.')
    while selection != '':
        print('You can utilize any of the following functions:')
        print('m - run the entire program through the main driver')
        print('p - plot the data')
        print('f - fit the data to a curve')
        print('s - view or edit the program settings')
        print('Leave the command blank to end the program.')
        selection = input('Enter a command: ')
        match selection:
            case 'm':
                print()
                print('Running the entire power spectral density analysis...')

                file_path = "/Users/vincentweng/Documents/PyNoise/PowerSpectralDensity/sample_data/stilbene_2in_CROCUS_20cm_offset_east.txt"
                values = np.loadtxt(file_path, usecols=(0,3), max_rows=2000000, dtype=float)

                PSD_Object = psd.PowerSpectralDensity(list_data_array=values, 
                                                      leg_label="TEST", 
                                                      clean_pulses_switch=1, 
                                                      dwell_time=2e6, 
                                                      meas_time_range=[150e9,1e12])
                
                save_dir= "/Users/vincentweng/Documents/PyNoise/PowerSpectralDensity/output"
                
                PSD_Object.conduct_APSD(show_plot=False, save_fig=False, save_dir=save_dir) # PSD Analysis
                
            case 'p':
                print()
                print('Plotting the data...')
            case 'f':
                print()
                print('Fitting the data...')
            # View and/or edit program settings.
            case 's':
                print()
                editor.driver()
            # End the program.
            case '':
                print('Returning to main menu...\n')
            # Catchall for invalid commands.
            case _:
                print('Unrecognized command. Please review the list of appriopriate inputs.\n')
    return editor


# Tells the program what function to start if this is the main program being run (TO BE DELETED)
if __name__ == "__main__":
    main()
                