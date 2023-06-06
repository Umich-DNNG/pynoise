import numpy as np                     # For processing data
import matplotlib.pyplot as plt        # For plotting data summaries
from scipy.optimize import curve_fit   # For fitting the curve
from scipy import signal               # For welch (fourier transform)
import os                              # For saving figures


# ------------ Power Spectral Density Fitting Function ----------------------------------------------
def APSD(f, A, alpha, c):
    return A / (1+(f**2/alpha**2)) + c
# ---------------------------------------------------------------------------------------------------

class PowerSpectralDensity:
    def __init__(self, list_data_array, leg_label, clean_pulses_switch, dwell_time, meas_time_range):

        '''
        Description:
            - Creating a PowerSpectralDensity() object and its variables.

        Inputs:
            - list_data_array (Input script)
            - leg_label (label setting for legend)
            - clean_pulses_switch (whether to include rows where last column==1)
            - dwell_time (DESCRIPTION NEEDED)
            - meas_time_range (DESCRIPTION NEEDED)

        Outputs: 
            - PowerSpectralDensity() object
        '''

        # Required Parameters
        self.list_data_array = list_data_array
        self.leg_label = leg_label
        self.clean_pulses_switch = clean_pulses_switch
        self.dwell_time = dwell_time
        self.meas_time_range = meas_time_range


    def conduct_APSD(self, show_plot, save_fig, save_dir):

        '''
        Creating PSD plot from an array of data inputs.
        Saving and showing the plot can be turned on or off.

        Inputs:
            - self (all the private variables in PowerSpectralDensity() object)

        Outputs: 
            - f (DESCRIPTION NEEDED)
            - Pxx (DESCRIPTION NEEDED)
            - popt (Optimal values for the parameters)
            - pcov (DESCRIPTION NEEDED)
        '''
        
        # Making count of bins over time histogram
        count_bins = np.diff(self.meas_time_range) / self.dwell_time
            
        # Only considering rows where last column value == 1 (Optional)
        if self.clean_pulses_switch == 1:
            indices = (self.list_data_array[:,-1] == 1)
        
        # Taking first column values ONLY
        times = self.list_data_array[indices, 0]
        
        # Generating corresponding histogram
        counts_time_hist, _ = np.histogram(a=times, 
                                        bins=int(count_bins), 
                                        range=self.meas_time_range)
        
        # Creating evenly spaced start and stop endpoint for plotting
        timeline = np.linspace(start=self.meas_time_range[0], 
                            stop=self.meas_time_range[1],
                            num=int(count_bins))/1e9
        
        # Plotting counts over time histogram (ensure constant or near constant)
        fig1, ax1 = plt.subplots()
        ax1.plot(timeline, counts_time_hist, '.', label=self.leg_label)
        
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
        ax2.semilogx(f[1:-2], Pxx[1:-2], '.', label=self.leg_label)
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
        ax2.set_title('Power Spectral Density Graph')
        ax2.legend(loc='upper right')
        

        # Saving figure (optional)
        if save_fig:

            fig1.tight_layout()
            save_filename = os.path.join(save_dir, 'PSD1')
            fig1.savefig(save_filename, dpi=300, bbox_inches='tight')

            fig2.tight_layout()
            save_filename = os.path.join(save_dir, 'PSD2')
            fig2.savefig(save_filename, dpi=300, bbox_inches='tight')


        # Showing plot (optional)
        if show_plot:
            print("entered")
            plt.show()
        
        # Outputting the PSD distribution and fit
        return f, Pxx, popt, pcov
    # ---------------------------------------------------------------------------------------------------