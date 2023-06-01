# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 11:42:16 2023

@author: 357375
"""

import numpy as np                    # For processing data
import matplotlib.pyplot as plt       # For plotting data summaries
from scipy.optimize import curve_fit
from scipy import signal

PowSpecDens_settings = {'dwell time': 2e6, 'meas time range': [150e9,1e12]}

def APSD(f, A, alpha, c):
    return A / (1+(f**2/alpha**2)) + c

def conduct_APSD(list_data_array,PowSpecDens_settings,leg_label,plt_title,
                 clean_pulses_switch):
    
    # Make counts over time historgram
    count_bins = (
        np.diff(PowSpecDens_settings['meas time range'])/
        PowSpecDens_settings['dwell time']
                  )\
        
    if clean_pulses_switch == 1:
        index = (list_data_array[:,-1]==1)
    
    times = list_data_array[index,0]
    
    counts_time_hist, _ = np.histogram(
        times, 
        bins=int(count_bins), 
        range=PowSpecDens_settings['meas time range']
        )
    
    timeline = np.linspace(PowSpecDens_settings['meas time range'][0], 
                PowSpecDens_settings['meas time range'][1], # Get measurement time in seconds
                int(count_bins))/1e9
    
    # Plot counts over time histogram (ensure constant or near constant)
    fig1, ax1 = plt.subplots()
    ax1.plot(timeline, counts_time_hist, '.', label=leg_label)
    
    ax1.set_ylabel('Counts')
    ax1.set_xlabel('Time (s)')
    ax1.legend()
    
    # Calculate power spectral density distribution from counts over time hist
    fs = 1/(timeline[3]-timeline[2]) # Get frequency of counts samples
    
    # Apply welch approximation of the fourier transform
    # This converts counts over time to a frequency distribution
    f, Pxx = signal.welch(
        counts_time_hist, fs, nperseg=2**12, window='boxcar')
    
    # Fit the distribution with the expected equation
    # Ignore some start and end points that are incorrect due to welch endpoint 
    # assumptions.
    popt, pcov = curve_fit(APSD, f[1:-2], Pxx[1:-2],
                                     p0=[Pxx[2], 25, 0.001],
                                     bounds=(0, np.inf),
                                     maxfev=100000
                                     )
    
    # Plot the auto-power-spectral-density distribution and fit
    fig2, ax2 = plt.subplots()
    ax2.semilogx(f[1:-2], Pxx[1:-2], '.', label=leg_label)
    ax2.semilogx(f[1:-2], APSD(f[1:-2], *popt), '--', label='fit')
    ymin, ymax = ax2.get_ylim()
    dy = ymax-ymin
    ax2.set_xlim([1, 200])
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('PSD (V$^2$/Hz)')
    alph_str = (r'$\alpha$ = (' +
              str(np.around(popt[1]*2*np.pi, decimals=2))+
              '$\pm$ '+ 
              str(np.around(pcov[1,1]*2*np.pi, decimals=2))
              +') 1/s')
    ax2.annotate(alph_str, xy=(1.5, ymin+0.1*dy), xytext=(1.5, ymin+0.1*dy),
                fontsize=16, fontweight='bold',
                color='black', backgroundcolor='white')
    # ax2.text(1.5, ymin+0.1*dy, alph_str)
    
    ax2.set_title(plt_title)
    ax2.legend(loc='upper right')
    
    plt.show()
    
    # Output the PSD distribution and fit
    return f, Pxx, popt, pcov