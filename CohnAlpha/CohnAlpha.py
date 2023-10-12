import numpy as np                     # For processing data
import matplotlib.pyplot as plt        # For plotting data summaries
from scipy.optimize import curve_fit   # For fitting the curve
from scipy import signal               # For welch (fourier transform)
import os                              # For saving figures


# ------------ Power Spectral Density Fitting Function ----------------------------------------------
def CAFit(f, A, alpha, c):
    '''
    Description:
        - Arbitrary fitting function used for line fitting in conductCohnAlpha()
    '''
    return A / (1+(f**2/alpha**2)) + c
# ---------------------------------------------------------------------------------------------------

class CohnAlpha:
    def __init__(self, 
                 list_data_array,
                 list_data_array2, 
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
        self.list_data_array2 = list_data_array2
        self.clean_pulses_switch = clean_pulses_switch
        self.dwell_time = dwell_time
        self.meas_time_range = meas_time_range

    def conduct_CPSD(self,
                    show_plot: bool = True,
                    save_fig: bool = True,
                    save_dir: str = './',
                    caSet: dict = {},
                    sps: dict = {},
                    lfs: dict = {},
                    scatter_opt: dict = {}):
        
        # Annotation Parameters
        self.annotate_font_weight = caSet['Annotation Font Weight']
        self.annotate_color = caSet['Annotation Color']
        self.annotate_background_color = caSet['Annotation Background Color']

        # Making count of bins over time histogram
        count_bins = np.diff(self.meas_time_range) / self.dwell_time

        if self.clean_pulses_switch == 1:
            indices = (self.list_data_array[:,-1]==1)
            indices2 = (self.list_data_array2[:,-1]==1)

        times = self.list_data_array[indices, 0]
        times2 = self.list_data_array2[indices2, 0]

        counts_time_hist, _ = np.histogram(
                    times,
                    bins=int(count_bins),
                    range=self.meas_time_range
                    )
        
        counts_time_hist2, _ = np.histogram(
                    times2,
                    bins=int(count_bins),
                    range=self.meas_time_range
                    )
        
        # counts_time_hist = np.zeros([2,int(count_bins)])
        ''' if np.size(channels) == 2:
            i=0
            for ch in channels:
                
                if self.clean_pulses_switch == 1:
                    indices = (self.list_data_array[:,-1]==1)

                times = self.list_data_array[indices, 0]

                N, _ = np.histogram(
                    times,
                    bins=int(count_bins),
                    range=self.meas_time_range
                    )
                counts_time_hist[i,:] = N
                i+=1
        else:
            print("Must specify two and only two channels to cross-correlate.")
        '''

        timeline = np.linspace(start=self.meas_time_range[0], 
                            stop=self.meas_time_range[1],
                            num=int(count_bins))/1e9

        fig1, ax1 = plt.subplots()
        ax1.plot(timeline, counts_time_hist, '.', label="TBD")
        ax1.plot(timeline, counts_time_hist2, '.', label="TBD")

        ax1.set_ylabel('Counts')
        ax1.set_xlabel('Time (s)')
        ax1.legend()
        
        # Plot counts over time histogram (ensure constant or near constant)
        '''
        i=0
        for ch in channels:
            fig1, ax1 = plt.subplots()
            ax1.plot(timeline, counts_time_hist[i,:], '.', label="TBD")

            ax1.set_ylabel('Counts')
            ax1.set_xlabel('Time (s)')
            ax1.legend()
            i+=1
        '''

        fs = 1/(timeline[3]-timeline[2]) # Get frequency of counts samples

        f, Pxy = signal.csd(
            counts_time_hist, 
            counts_time_hist2, 
            fs, 
            nperseg=2**9, 
            window='boxcar')
        Pxy = np.abs(Pxy)

        f1, Pxx1 = signal.welch(x=counts_time_hist, 
                            fs=fs, 
                            nperseg=2**12, 
                            window='boxcar')
        
        f2, Pxx2 = signal.welch(x=counts_time_hist2, 
                            fs=fs, 
                            nperseg=2**12, 
                            window='boxcar')

        # Apply welch windows and FFT to tapered windows, summation is smoothed FFT

        # f, Pxx = lpsd(counts_time_hist, fs, window='boxcar')
        # # Apply logarithmically spaced power spectral density

        popt, pcov = curve_fit(CAFit, f[1:-2], Pxy[1:-2],
                                        p0=[Pxy[2], 25, 0],
                                        bounds=(0, np.inf),
                                        maxfev=100000
                                        )

        popt1, pcov1 = curve_fit(CAFit, f1[1:-2], 
                                        Pxx1[1:-2],
                                        p0=[Pxx1[2], 25, 0.001],
                                        bounds=(0, np.inf),
                                        maxfev=100000
                                        )
        
        popt2, pcov2 = curve_fit(CAFit, f2[1:-2], 
                                        Pxx2[1:-2],
                                        p0=[Pxx2[2], 25, 0.001],
                                        bounds=(0, np.inf),
                                        maxfev=100000
                                        )
        
        fig2, ax2 = plt.subplots()
        ax2.semilogx(f[1:-2], Pxy[1:-2], '.', **sps)
        ax2.semilogx(f[1:-2], CAFit(f[1:-2], *popt), **lfs)
        ymin, ymax = ax2.get_ylim()
        dy = ymax-ymin
        ax2.set_xlim([1, 200])
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('PSD (V$^2$/Hz)')
        # ax2.set_yscale('log')
        alph_str = (r'$\alpha$ = (' +
                str(np.around(popt[1]*2*np.pi, decimals=2))+
                '$\pm$ '+
                str(np.around(np.sqrt(pcov[1,1])*2*np.pi, decimals=2))
                +') 1/s')
        ax2.annotate(alph_str, xy=(1.5, ymin+0.1*dy), xytext=(1.5, ymin+0.1*dy),
                    fontsize=16, fontweight='bold',
                    color='black', backgroundcolor='white')
        # ax2.text(1.5, ymin+0.1*dy, alph_str)

        # ax2.set_title(plt_title)
        ax2.legend(loc='upper right')

        '''
        # Plotting the auto-power-spectral-density distribution and fit
        figauto1, (axauto1, axauto2) = plt.subplots(nrows=2, sharex=True, figsize=(8, 6), gridspec_kw={'height_ratios': [2, 1]})
        figauto2, (axauto3, axauto4) = plt.subplots(nrows=2, sharex=True, figsize=(8, 6), gridspec_kw={'height_ratios': [2, 1]})

        # Creating a plot with semilogarithmic (log-scale) x-axis 
        axauto1.semilogx(f1[1:-2], Pxx1[1:-2], '.', **sps)
        axauto1.semilogx(f1[1:-2], CAFit(f[1:-2], *popt1), **lfs)

        axauto3.semilogx(f2[1:-2], Pxx2[1:-2], '.', **sps)
        axauto3.semilogx(f2[1:-2], CAFit(f[1:-2], *popt2), **lfs)

        # Setting minimum and maximum for y
        ymin, ymax = ax1.get_ylim()
        dy = ymax-ymin

        # Constructing alpha string
        alph_str1 = (r'$\alpha$ = (' +
                    str(np.around(popt1[1]*2*np.pi, decimals=2)) + '$\pm$ '+ 
                    str(np.around(pcov1[1,1]*2*np.pi, decimals=2)) + ') 1/s')
        alph_str2 = (r'$\alpha$ = (' +
                    str(np.around(popt2[1]*2*np.pi, decimals=2)) + '$\pm$ '+ 
                    str(np.around(pcov2[1,1]*2*np.pi, decimals=2)) + ') 1/s')
        
         # Annotating the plots
        axauto1.annotate(alph_str1, 
                    xy=(1.5, ymin+0.1*dy), 
                    xytext=(1.5, ymin+0.1*dy),
                    fontsize=16, 
                    fontweight=self.annotate_font_weight,
                    color=self.annotate_color, 
                    backgroundcolor=self.annotate_background_color)
        axauto3.annotate(alph_str2, 
                    xy=(1.5, ymin+0.1*dy), 
                    xytext=(1.5, ymin+0.1*dy),
                    fontsize=16, 
                    fontweight=self.annotate_font_weight,
                    color=self.annotate_color, 
                    backgroundcolor=self.annotate_background_color)
        
        # Creating title and legend
        axauto1.set_title('Cohn Alpha Graph')
        axauto1.legend(loc='upper right')

        axauto3.set_title('Cohn Alpha Graph')
        axauto3.legend(loc='upper right')

        # Creating axis titles
        axauto1.set_xlim([1, 200])
        axauto1.set_xlabel('Frequency (Hz)')
        axauto1.set_ylabel('Intensity (V$^2$/Hz)')

        axauto3.set_xlim([1, 200])
        axauto3.set_xlabel('Frequency (Hz)')
        axauto3.set_ylabel('Intensity (V$^2$/Hz)')

        # Compute residuals
        residuals1 = ((CAFit(f1[1:-2], *popt1) - Pxx1[1:-2]) / Pxx1[1:-2]) * 100
        residuals2 = ((CAFit(f2[1:-2], *popt2) - Pxx2[1:-2]) / Pxx2[1:-2]) * 100

        # Computing residuals and plot in bottom subplot
        axauto2.scatter(f[1:-2], residuals1, **scatter_opt)  # Use f for residuals
        axauto2.axhline(y=0, color='#162F65', linestyle='--')
        axauto2.set_xlabel('Frequency (Hz)')
        axauto2.set_ylabel('Percent difference (%)')

        axauto4.scatter(f[1:-2], residuals2, **scatter_opt)  # Use f for residuals
        axauto4.axhline(y=0, color='#162F65', linestyle='--')
        axauto4.set_xlabel('Frequency (Hz)')
        axauto4.set_ylabel('Percent difference (%)')
        
        # Saving figures (optional)
        if save_fig:
            fig1.tight_layout()
            save_filename = os.path.join(save_dir, 'CohnAlpha')
            fig1.savefig(save_filename, dpi=300, bbox_inches='tight')

            fig2.tight_layout()
            save_filename = os.path.join(save_dir, 'CohnAlpha')
            fig2.savefig(save_filename, dpi=300, bbox_inches='tight')

            figauto1.tight_layout()
            save_filename = os.path.join(save_dir, 'CohnAlpha')
            figauto1.savefig(save_filename, dpi=300, bbox_inches='tight')

            figauto2.tight_layout()
            save_filename = os.path.join(save_dir, 'CohnAlpha')
            figauto2.savefig(save_filename, dpi=300, bbox_inches='tight')

        # Showing plots (optional)
        if show_plot:
            plt.show()
        '''
        plt.show()

        return f, Pxy, popt, pcov    


    def conductCohnAlpha(self, 
                         show_plot: bool = True, 
                         save_fig: bool = True, 
                         save_dir: str = './', 
                         caSet: dict = {},
                         sps: dict = {},
                         lfs: dict = {},
                         scatter_opt: dict = {}):
        
        '''
        Creating PSD plot from an array of data inputs.
        Saving and showing the plot can be turned on or off.
        Visual settings can also be adjusted.

        Inputs:
            - self (all the private variables in PowerSpectralDensity() object)
            - show_plot (whether to show plot) default is True
            - save_fig (whether to save figure) default is True
            - save_dir (figure save directory) default if root folder

        Outputs: 
            - f (DESCRIPTION NEEDED)
            - Pxx (DESCRIPTION NEEDED)
            - popt (Optimal values for the parameters)
            - pcov (DESCRIPTION NEEDED)
        '''

        # Annotation Parameters
        self.annotate_font_weight = caSet['Annotation Font Weight']
        self.annotate_color = caSet['Annotation Color']
        self.annotate_background_color = caSet['Annotation Background Color']
        
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
        
        # Calculating power spectral density distribution from counts over time hist (Get frequency of counts samples)
        fs = 1 / (timeline[3]-timeline[2])
        
        # Apply welch approximation of the fourier transform, convertig counts over time to a frequency distribution
        f, Pxx = signal.welch(x=counts_time_hist, 
                            fs=fs, 
                            nperseg=caSet['nperseg'], 
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
        fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True, figsize=(8, 6), gridspec_kw={'height_ratios': [2, 1]})

        # Creating a plot with semilogarithmic (log-scale) x-axis 
        ax1.semilogx(f[1:-2], Pxx[1:-2], '.', **sps)
        ax1.semilogx(f[1:-2], CAFit(f[1:-2], *popt), **lfs)
        
        # Setting minimum and maximum for y
        ymin, ymax = ax1.get_ylim()
        dy = ymax-ymin

        # Constructing alpha string
        alph_str = (r'$\alpha$ = (' +
            '{:.2e}'.format(np.around(popt[1]*2*np.pi, decimals=2)) + '$\pm$ ' + 
            '{:.2e}'.format(np.around(pcov[1,1]*2*np.pi, decimals=2)) + ') 1/s')
        
        # Annotating the plots
        ax1.annotate(alph_str, 
                     xy=(1.5, ymin+0.1*dy), 
                     xytext=(1.5, ymin+0.1*dy),
                     fontsize=caSet['Font Size'], 
                     fontweight=self.annotate_font_weight,
                     color=self.annotate_color, 
                     backgroundcolor=self.annotate_background_color)
        
        # Creating title and legend
        ax1.set_title('Cohn Alpha Graph')
        ax1.legend(loc='upper right')

         # Creating axis titles
        ax1.set_xlim([1, 200])
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('Intensity (V$^2$/Hz)')

        # Compute residuals
        # residuals = Pxx[1:-2] - CAFit(f[1:-2], *popt)
        residuals = ((CAFit(f[1:-2], *popt) - Pxx[1:-2]) / Pxx[1:-2]) * 100

        # Computing residuals and plot in bottom subplot
        # residuals_norm = residuals / np.max(np.abs(residuals))

        ax2.scatter(f[1:-2], residuals, **scatter_opt)  # Use f for residuals
        ax2.axhline(y=0, color='#162F65', linestyle='--')
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Percent difference (%)')
        
        # Saving figure (optional)
        if save_fig:
            fig.tight_layout()
            save_filename = os.path.join(save_dir, 'CohnAlpha')
            fig.savefig(save_filename, dpi=300, bbox_inches='tight')


        # Showing plot (optional)
        if show_plot:
            plt.show()
        
        # Outputting the PSD distribution and fit
        return f, Pxx, popt, pcov
    # ---------------------------------------------------------------------------------------------------   