import numpy as np                     # For processing data
import matplotlib.pyplot as plt        # For plotting data summaries
from scipy.optimize import curve_fit   # For fitting the curve
from scipy import signal               # For welch (fourier transform)
import os                              # For saving figures


# ------------ Power Spectral Density Fitting Function ----------------------------------------------
def CAFit(f, A, alpha, c):
    return A / (1+(f**2/alpha**2)) + c
# ---------------------------------------------------------------------------------------------------

class CohnAlpha:
    def __init__(self, 
                 list_data_array, 
                 clean_pulses_switch: bool = True, 
                 dwell_time: float = 2.0e6, 
                 meas_time_range: list[float] = [1.5e11, 1.0e12]):

        '''
        Description:
            - Creating a PowerSpectralDensity() object and its variables.

        Inputs:
            - list_data_array (Input script)
            - clean_pulses_switch (whether to include rows where last column==1)
            - dwell_time (DESCRIPTION NEEDED)
            - meas_time_range (DESCRIPTION NEEDED)

        Outputs: 
            - PowerSpectralDensity() object
        '''

        # Required Parameters
        self.list_data_array = list_data_array
        self.clean_pulses_switch = clean_pulses_switch
        self.dwell_time = dwell_time
        self.meas_time_range = meas_time_range


    def conductCohnAlpha(self, 
                     show_plot: bool = True, 
                     save_fig: bool = True, 
                     save_dir: str = './', 
                     leg_label: str = "frequency intensity",
                     annotate_font_weight: str = "bold", 
                     annotate_color: str = "black", 
                     annotate_background_color: str = "white"):
        
        '''
        Creating PSD plot from an array of data inputs.
        Saving and showing the plot can be turned on or off.
        Visual settings can also be adjusted.

        Inputs:
            - self (all the private variables in PowerSpectralDensity() object)
            - show_plot (whether to show plot) default is True
            - save_fig (whether to save figure) default is True
            - save_dir (figure save directory) default if root folder
            - leg_label (label for the legend)
            - annotate_font_weight (annotation font weight) default is bold
            - annotate_color (color of the annotation) default is black
            - annotate_background_color (color of the annotation background) default is white

        Outputs: 
            - f (DESCRIPTION NEEDED)
            - Pxx (DESCRIPTION NEEDED)
            - popt (Optimal values for the parameters)
            - pcov (DESCRIPTION NEEDED)
        '''

        # Annotation Parameters
        self.leg_label = leg_label
        self.annotate_font_weight = annotate_font_weight
        self.annotate_color = annotate_color
        self.annotate_background_color = annotate_background_color
        
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
        popt, pcov = curve_fit(CAFit, 
                            f[1:-2], 
                            Pxx[1:-2],
                            p0=[Pxx[2], 25, 0.001],
                            bounds=(0, np.inf),
                            maxfev=100000)
        
        print('alpha = ' + str(np.around(popt[1]*2*np.pi, decimals=2)) + ', uncertainty = '+ 
                    str(np.around(pcov[1,1]*2*np.pi, decimals=2)))
        
        # Plotting the auto-power-spectral-density distribution and fit
        fig2, ax2 = plt.subplots()

        # Creating a plot with semilogarithmic (log-scale) x-axis 
        ax2.semilogx(f[1:-2], Pxx[1:-2], '.', label=self.leg_label)
        ax2.semilogx(f[1:-2], CAFit(f[1:-2], *popt), '--', label='fit')
        
        # Setting minimum and maximum for y
        ymin, ymax = ax2.get_ylim()
        dy = ymax-ymin

        # Creating axis titles
        ax2.set_xlim([1, 200])
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('CohnAlpha (V$^2$/Hz)')

        # Constructing alpha string
        alph_str = (r'$\alpha$ = (' +
                    str(np.around(popt[1]*2*np.pi, decimals=2)) + '$\pm$ '+ 
                    str(np.around(pcov[1,1]*2*np.pi, decimals=2)) + ') 1/s')
        
        # Annotating the plots
        ax2.annotate(alph_str, 
                    xy=(1.5, ymin+0.1*dy), 
                    xytext=(1.5, ymin+0.1*dy),
                    fontsize=16, 
                    fontweight=self.annotate_font_weight,
                    color=self.annotate_color, 
                    backgroundcolor=self.annotate_background_color)
        
        # Creating title and legend
        ax2.set_title('Cohn Alpha Graph')
        ax2.legend(loc='upper right')
        

        # Saving figure (optional)
        if save_fig:

            fig1.tight_layout()
            save_filename = os.path.join(save_dir, 'CohnAlpha1')
            fig1.savefig(save_filename, dpi=300, bbox_inches='tight')

            fig2.tight_layout()
            save_filename = os.path.join(save_dir, 'CohnAlpha2')
            fig2.savefig(save_filename, dpi=300, bbox_inches='tight')


        # Showing plot (optional)
        if show_plot:
            plt.show()
        
        # Outputting the PSD distribution and fit
        return f, Pxx, popt, pcov
    # ---------------------------------------------------------------------------------------------------