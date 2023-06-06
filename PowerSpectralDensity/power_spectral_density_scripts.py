import numpy as np                     # For processing data
import matplotlib.pyplot as plt        # For plotting data summaries
from scipy.optimize import curve_fit   # For fitting the curve
from scipy import signal               # For welch (fourier transform)



# ------------ Specifying Setting Options (TO CHANGE LATER) -----------------------------------------
PowSpecDens_settings = {'dwell time': 2e6, 'meas time range': [150e9,1e12]}
# ---------------------------------------------------------------------------------------------------




# ------------ Power Spectral Density Fitting Function ----------------------------------------------
def APSD(f, A, alpha, c):
    return A / (1+(f**2/alpha**2)) + c
# ---------------------------------------------------------------------------------------------------




# ------------ Power Spectral Density Fitting Function ----------------------------------------------
def conduct_APSD(list_data_array, PowSpecDens_settings, leg_label,plt_title, clean_pulses_switch):
    
    # Making count of bins over time histogram
    count_bins = np.diff(PowSpecDens_settings['meas time range']) / PowSpecDens_settings['dwell time']
        
    # Only considering rows where last column value == 1 (Optional)
    if clean_pulses_switch == 1:
        indices = (list_data_array[:,-1] == 1)
    
    # Taking first column values ONLY
    times = list_data_array[indices, 0]
    
    # Generating corresponding histogram
    counts_time_hist, _ = np.histogram(a=times, 
                                       bins=int(count_bins), 
                                       range=PowSpecDens_settings['meas time range'])
    
    # Creating evenly spaced start and stop endpoint for plotting
    timeline = np.linspace(start=PowSpecDens_settings['meas time range'][0], 
                           stop=PowSpecDens_settings['meas time range'][1],
                           num=int(count_bins))/1e9
    
    # Plotting counts over time histogram (ensure constant or near constant)
    fig1, ax1 = plt.subplots()
    ax1.plot(timeline, counts_time_hist, '.', label=leg_label)
    
    # Setting axis titles and legend
    ax1.set_ylabel('Counts')
    ax1.set_xlabel('Time(s)')
    ax1.legend()
    
    # Calculating power spectral density distribution from counts over time hist (Get frequency of counts samples)
    fs = 1 / (timeline[3]-timeline[2])
    
    # Apply welch approximation of the fourier transform, convertig counts over time to a frequency distribution
    f, Pxx = signal.welch(x=counts_time_hist, 
                          fs=fs, 
                          nperseg=2**12, 
                          window='boxcar')
    
    # Fitting distribution with expected equation (Ignore start & end points that are incorrect due to welch endpoint assumptions)
    popt, pcov = curve_fit(APSD, 
                           f[1:-2], 
                           Pxx[1:-2],
                           p0=[Pxx[2], 25, 0.001],
                           bounds=(0, np.inf),
                           maxfev=100000)
    
    # Plotting the auto-power-spectral-density distribution and fit
    fig2, ax2 = plt.subplots()

    # Creating a plot with semilogarithmic (log-scale) x-axis 
    ax2.semilogx(f[1:-2], Pxx[1:-2], '.', label=leg_label)
    ax2.semilogx(f[1:-2], APSD(f[1:-2], *popt), '--', label='fit')
    
    # Setting minimum and maximum for y
    ymin, ymax = ax2.get_ylim()
    dy = ymax-ymin

    # Creating axis titles
    ax2.set_xlim([1, 200])
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('PSD (V$^2$/Hz)')

    # Constructing alpha string
    alph_str = (r'$\alpha$ = (' +
                str(np.around(popt[1]*2*np.pi, decimals=2)) + '$\pm$ '+ 
                str(np.around(pcov[1,1]*2*np.pi, decimals=2)) + ') 1/s')
    
    # Annotating the plots
    ax2.annotate(alph_str, 
                 xy=(1.5, ymin+0.1*dy), 
                 xytext=(1.5, ymin+0.1*dy),
                 fontsize=16, 
                 fontweight='bold',
                 color='black', 
                 backgroundcolor='white')
    
    # Creating title and legend
    ax2.set_title(plt_title)
    ax2.legend(loc='upper right')
    
    plt.show()
    
    # Outputting the PSD distribution and fit
    return f, Pxx, popt, pcov
# ---------------------------------------------------------------------------------------------------