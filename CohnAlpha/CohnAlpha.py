import numpy as np                     # For processing data
import matplotlib.pyplot as pyplot     # For plotting data summaries
from scipy.optimize import curve_fit   # For fitting the curve
from scipy import signal               # For welch (fourier transform)
from pathlib import Path               # Currently strings for pathnames are not working, attempting to use pathlib/Path
import datastream as ds
import os                              # For saving figures
import math                            # To compare floats and assign correct time units string
#import h5py                            # For saving data in .hdf5 format                       


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
                 settings:dict = {}):

        '''
        Description:
            - Creating a PowerSpectralDensity() object and its variables.

        Inputs:
            - list_data_array (Input script)
            - dwell_time (DESCRIPTION NEEDED)
            - meas_time_range (DESCRIPTION NEEDED)

        Outputs: 
            - PowerSpectralDensity() object
        '''

        # set quiet variable first for print statements
        self.quiet = settings['Input/Output Settings']['Quiet mode']
        self.print("Reading in input file/folder data...")

        # Required Parameters
        # Load the values from the specified file into an NP array.
        self.list_data_array = np.loadtxt(settings['Input/Output Settings']['Input file/folder'], usecols=0, dtype=float)
        self.meas_time_range = settings['CohnAlpha Settings']['Meas time range']
    
        # set measure time range to default value if incorrect input
        if self.meas_time_range == [] or self.meas_time_range is None:
            self.print("Unable to determine Measure Time Range from settings")
            self.print("Setting Measure Time Range to default values of [1.5e11, 1.0e12] in ns")
            self.meas_time_range = [1.5e11, 1.0e12]
        self.fs = 0

        # Annotation Parameters
        self.annotate_font_weight = settings['CohnAlpha Settings']['Annotation Font Weight']
        self.annotate_color = settings['CohnAlpha Settings']['Annotation Color']
        self.annotate_background_color = settings['CohnAlpha Settings']['Annotation Background Color']
        self.annotate_font_size = settings['CohnAlpha Settings']['Font Size']
        
        self.print("Finished reading input file/folder data")

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

        counts_time_hist = np.zeros([2,int(count_bins)])

        index = self.list_data_array[:,0]!=0

        times = self.list_data_array[index, 0]

        N, _ = np.histogram(
                 times,
                 bins=int(count_bins),
                 range=self.meas_time_range
                 )
        counts_time_hist[0,:] = N

        list_data_array = np.loadtxt(caSet['Second Input file'])
        index = list_data_array[:,0]!=0

        N, _ = np.histogram(list_data_array,
                            bins=int(count_bins),
                            range=self.meas_time_range)
        
        counts_time_hist[1,:] = N
        
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

        '''fig1, ax1 = pyplot.subplots()
        ax1.plot(timeline, counts_time_hist, '.', label="TBD")
        ax1.plot(timeline, counts_time_hist2, '.', label="TBD")

        ax1.set_ylabel('Counts')
        ax1.set_xlabel('Time(s)')
        ax1.legend()'''
        
        # Plot counts over time histogram (ensure constant or near constant)
        i=0
        for ch in [0,1]:
            fig1, ax1 = pyplot.subplots()
            ax1.plot(timeline, counts_time_hist[i,:], '.', label="TBD")

            ax1.set_ylabel('Counts')
            ax1.set_xlabel('Time(s)')
            ax1.legend()
            i+=1

        fs = 1/(timeline[3]-timeline[2]) # Get frequency of counts samples

        f, Pxy = signal.csd(
            counts_time_hist[0,:], 
            counts_time_hist[1,:], 
            fs, 
            nperseg=2**10, 
            window='boxcar')
        Pxy = np.abs(Pxy)

        '''f1, Pxx1 = signal.welch(x=counts_time_hist[0,:], 
                            fs=fs, 
                            nperseg=2**12, 
                            window='boxcar')
        
        f2, Pxx2 = signal.welch(x=counts_time_hist[1,:], 
                            fs=fs, 
                            nperseg=2**12, 
                            window='boxcar')'''

        # Apply welch windows and FFT to tapered windows, summation is smoothed FFT

        # f, Pxx = lpsd(counts_time_hist, fs, window='boxcar')
        # # Apply logarithmically spaced power spectral density

        popt, pcov = curve_fit(CAFit, f[1:-2], Pxy[1:-2],
                                        p0=[Pxy[2], 25, 0],
                                        bounds=(0, np.inf),
                                        maxfev=100000
                                        )

        '''popt1, pcov1 = curve_fit(CAFit, f1[1:-2], 
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
                                        )'''
        
        fig2, ax2 = pyplot.subplots()
        ax2.semilogx(f[1:-2], Pxy[1:-2], '.', **sps)
        ax2.semilogx(f[1:-2], CAFit(f[1:-2], *popt), **lfs)
        ymin, ymax = ax2.get_ylim()
        dy = ymax-ymin
        ax2.set_xlim([1, 200])
        ax2.set_xlabel('Frequency(Hz)')
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

        # ax2.set_title(pyplot_title)
        ax2.legend(loc='upper right')

        ax2.grid()

        '''
        # Plotting the auto-power-spectral-density distribution and fit
        figauto1, (axauto1, axauto2) = pyplot.subplots(nrows=2, sharex=True, figsize=(8, 6), gridspec_kw={'height_ratios': [2, 1]})
        figauto2, (axauto3, axauto4) = pyplot.subplots(nrows=2, sharex=True, figsize=(8, 6), gridspec_kw={'height_ratios': [2, 1]})

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
        axauto1.set_xlabel('Frequency(Hz)')
        axauto1.set_ylabel('Intensity (V$^2$/Hz)')

        axauto3.set_xlim([1, 200])
        axauto3.set_xlabel('Frequency(Hz)')
        axauto3.set_ylabel('Intensity (V$^2$/Hz)')

        # Compute residuals
        residuals1 = ((CAFit(f1[1:-2], *popt1) - Pxx1[1:-2]) / Pxx1[1:-2]) * 100
        residuals2 = ((CAFit(f2[1:-2], *popt2) - Pxx2[1:-2]) / Pxx2[1:-2]) * 100

        # Computing residuals and plot in bottom subplot
        axauto2.scatter(f[1:-2], residuals1, **scatter_opt)  # Use f for residuals
        axauto2.axhline(y=0, color='#162F65', linestyle='--')
        axauto2.set_xlabel('Frequency(Hz)')
        axauto2.set_ylabel('Percent difference (%)')

        axauto4.scatter(f[1:-2], residuals2, **scatter_opt)  # Use f for residuals
        axauto4.axhline(y=0, color='#162F65', linestyle='--')
        axauto4.set_xlabel('Frequency(Hz)')
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
            pyplot.show()
        '''
        pyplot.show()

        return f, Pxy, popt, pcov    

    def conductCohnAlpha(self, settings: dict = {}):
        
        '''
        Deprecated Function. Just call fitCohnAlpha() instead


        Creating PSD plot from an array of data inputs.
        Saving and showing the plot can be turned on or off.
        Visual settings can also be adjusted.

        Inputs:
            - self: all the private variables in PowerSpectralDensity() object
            - settings: the current user runtime settings

        Outputs: 
            - f (DESCRIPTION NEEDED)
            - Pxx (DESCRIPTION NEEDED)
            - popt (Optimal values for the parameters)
            - pcov (DESCRIPTION NEEDED)
        '''

        return

        # counts_time_hist = self.plotHistogram(settings)
        # return self.welchApproximationFourierTransformation(settings, counts_time_hist)

    def plotCountsHistogram(self, settings: dict = {}):

        '''
        Creating Counts Histogram from data
        Saving and showing the histogram can be turned on or off in the settings
        Visual Settings can also be adjusted in the settings

        Inputs:
            - self: all the private variables in PowerSpectralDensity() object
            - settings: the current user runtime settings

        Output:
            - count_times_hist: the histogram saved in array format
        '''

        # calculate dwell time
        # change from Hz --> seconds --> nanoseconds
        dwell_time = 1 / (2 * settings['CohnAlpha Settings']['Frequency Maximum'])
        dwell_time = dwell_time * 1e9

        # Making count of bins over time histogram
        count_bins = np.diff(self.meas_time_range) / dwell_time

        # read in histogram data
        # reformat lists to numpy arrays
        counts_time_hist = []
        edges_seconds = []

        # import data from disk
        importResults = ds.importAnalysis(
            data={
                'Time(s)': edges_seconds,
                'Counts': counts_time_hist
            },
            name='ca_hist_s',
            input=settings['Input/Output Settings']['Save directory'])
        
        counts_time_hist = np.array(counts_time_hist, dtype=np.int64)
        edges_seconds = np.array(edges_seconds, dtype=np.float64)

        # If unable to read in data or no data exists
        # generate corresponding histogram
        if not importResults:
            counts_time_hist, edges_ns = np.histogram(a=self.list_data_array,
                                                    bins=int(count_bins),
                                                    range=self.meas_time_range)
            edges_seconds = edges_ns / 1e9
            edges_seconds = edges_seconds[:-1]

        # Plotting
        if settings['General Settings']['Show plots']:
            self.plot(x=edges_seconds,y=counts_time_hist, method='hist', settings=settings)

        # Saving counts histogram raw data
        if settings['Input/Output Settings']['Save raw data']:
            ds.exportAnalysis(
                data={
                    'Time(s)': (edges_seconds.tolist(), 0),
                    'Counts': (counts_time_hist.tolist(), 0)
                },
                singles=[],
                name='ca_hist_s',
                output=settings['Input/Output Settings']['Save directory']
            )

            # output save location
            outputPath = os.path.abspath(settings['Input/Output Settings']['Save directory'])
            self.print('Histogram Data saved at ' + str(outputPath))

        # Creating evenly spaced start and stop endpoint for plotting
        timeline = np.linspace(start=self.meas_time_range[0], 
                            stop=self.meas_time_range[1],
                            num=int(count_bins))/1e9
        
        # Calculating power spectral density distribution from counts over time hist (Get frequency of counts samples)
        # Save into class, for future functions to use
        self.fs = 1 / (timeline[3]-timeline[2])
        return (edges_seconds, counts_time_hist)
    
    def welchApproxFourierTrans(self, settings:dict = {}):

        '''
        Creating Cohn Alpha Scatterplot from data
        Saving and showing the scatterplot can be turned on or off in the settings
        Visual Settings can also be adjusted in the settings

        Inputs:
            - self: all the private variables in PowerSpectralDensity() object
            - count_times_hist: the histogram to be converted to a frequency distribution
            - settings: the current user runtime settings

        Output:
            - welchResultDict: a dict, contains the frequency and the power spectral density
        '''

        
        self.print('\nApplying the Welch Approximation...')

        # Read in existing data if exists
        # re-format lists to numpy arrays
        f = []
        Pxx = []

        importResults = ds.importAnalysis(
                    data={
                        'Frequency(Hz)': f,
                        'Counts^2/Hz': Pxx
                    },
                    name='ca_graph_s',
                    input=settings['Input/Output Settings']['Save directory'])

        f = np.array(f, dtype=np.float64)
        Pxx = np.array(Pxx, dtype=np.float64)

        
        # If existing data does not exist
        # read in histogram information from disk
        if not importResults:
            edges_seconds = []
            counts_time_hist = []

            dwell_time = 1 / (2 * settings['CohnAlpha Settings']['Frequency Maximum'])
            nperseg = 1 / (dwell_time * settings['CohnAlpha Settings']['Frequency Minimum'])

            # check to see if nperseg is a power of 2
            if not checkPowerOfTwo(value=int(nperseg)):
                self.print('WARNING: calculated nperseg is not a power of 2')

            # first attempt to read in file
            # import data from disk
            importResults = ds.importAnalysis(
                data={
                    'Time(s)': edges_seconds,
                    'Counts': counts_time_hist
                },
                name='ca_hist_s',
                input=settings['Input/Output Settings']['Save directory'])

            edges_seconds = np.array(edges_seconds, dtype=np.float64)
            counts_time_hist = np.array(counts_time_hist, dtype=np.int64)

            # if no existing data found for the histogram
            # Apply welch approximation of the fourier transform, converting counts over time to a frequency distribution
            if not importResults:
                edges_seconds, counts_time_hist = self.plotCountsHistogram(settings=settings)
            f, Pxx = signal.welch(x=counts_time_hist,
                                fs=self.fs,
                                nperseg=int(nperseg), 
                                window='boxcar')

        if settings['General Settings']['Show plots']:
            self.plot(x=f, y=Pxx, method='scatter', settings=settings)
        
        # Saving scatter plot data (optional)
        if settings['Input/Output Settings']['Save raw data']:
            ds.exportAnalysis(
                data={
                    'Frequency(Hz)': (f.tolist(), 0),
                    'Counts^2/Hz': (Pxx.tolist(), 0)
                },
                singles=[],
                name='ca_graph_s',
                output=settings['Input/Output Settings']['Save directory']
            )
            outputPath = os.path.abspath(settings['Input/Output Settings']['Save directory'])
            self.print('Scatterplot Data saved at ' + str(outputPath))

        return (f, Pxx)
        

    def fitCohnAlpha(self, settings:dict = {}):

        '''
        Fits Power Spectral Density onto provided scatterplot
        Saving and showing the graph can be turned on or off in the settings
        Visual Settings can also be adjusted in the settings

        Inputs:
            - self: all the private variables in PowerSpectralDensity() object
            - settings: the current user runtime settings
            - welchResultDict: the dict that contains the result of Welch's Approximation

        Output:
            - dict: contains the fitted curve
        '''

        self.print('\nFitting Power Spectral Density Curve...')
        
        # initialize lists
        # read in files
        f = []
        Pxx = []
        residuals = []
        singlesPopt = []

        importResults = ds.importAnalysis(
            data={
                'Frequency(Hz)': f,
                'Counts^2/Hz': Pxx,
                'Residuals': residuals
            },
            singles=singlesPopt,
            name='ca_graph_s',
            input=settings['Input/Output Settings']['Save directory'])

        popt = []

        # modify singles' list of tuples
        # change to list of only the values, leaving behind column header information
        # grab value from each tuple
        # only do it if import worked properly
        if importResults:
            while singlesPopt != []:
                popt.append(singlesPopt.pop(0)[1])          
            # assign uncertainty and alpha values
            # grab from end of list
            # i.e. [x, y, z, alpha, uncertainty] --> [x, y, z, alpha] --> [x, y, z]
            uncertainty = np.float64(popt.pop(len(popt) - 1))
            alpha = np.float64(popt.pop(len(popt) - 1))

        # convert lists to proper numpy array
        f = np.array(f, dtype=np.float64)
        Pxx = np.array(Pxx, dtype=np.float64)
        residuals = np.array(residuals, dtype=np.float64)
        popt = np.array(popt,dtype=np.float64)

        # if no existing data is found
        # re-generate scatterplot data, fitting data
        # Ignore start & end points that are incorrect due to welch endpoint assumptions
        # Fitting distribution with expected equation
        if not importResults:
            f, Pxx = self.welchApproxFourierTrans(settings=settings)
            popt, pcov = curve_fit(CAFit,
                                f[1:-2],
                                Pxx[1:-2],
                                p0=[Pxx[2], 25, 0.001],
                                bounds=(0, np.inf),
                                maxfev=100000)
            
            alpha = np.around(popt[1]*2*np.pi, decimals=2)
            uncertainty = np.around(pcov[1,1]*2*np.pi, decimals=2)
            residuals = ((CAFit(f[1:-2], *popt) - Pxx[1:-2]) / Pxx[1:-2]) * 100

        # Display Alpha and Uncertainty values, store within Welch Approx
        self.print('alpha = ' + str(alpha) + ', uncertainty = '+ 
                    str(uncertainty))
        
        
        kwDict = {
            'optimal a': popt[0],
            'optimal alpha': popt[1],
            'optimal c': popt[2],
            'alpha': alpha,
            'uncertainty': uncertainty
        }

        # TODO: place plotting function here
        self.plot(x=f, y=Pxx, residuals=residuals, method='fit', settings=settings, **kwDict)

        return
        # also construct kwargs here
        # return 'TODO COME BACK TO HERE'
        # TODO: another TODO so I can see this easier

        


        
        # Plotting the auto-power-spectral-density distribution and fit
        fig, ax = pyplot.subplots(nrows=2, sharex=True, figsize=(8, 6), gridspec_kw={'height_ratios': [2, 1]})


        # Creating a plot with semilogarithmic (log-scale) x-axis 
        ax[0].semilogx(f[1:-2], Pxx[1:-2], '.', **settings['Semilog Plot Settings'])
        ax[0].semilogx(f[1:-2], CAFit(f[1:-2], *popt), **settings['Line Fitting Settings'])


        # Setting minimum and maximum for y
        ymin, ymax = ax[0].get_ylim()
        dy = ymax-ymin


        # Constructing alpha string
        alph_str = (r'$\alpha$ = (' +
            '{:.2e}'.format(alpha) + '$\pm$ ' + 
            '{:.2e}'.format(uncertainty) + ') 1/s')


        # Annotating the plots
        ax[0].annotate(alph_str, 
                     xy=(1.5, ymin+0.1*dy), 
                     xytext=(1.5, ymin+0.1*dy),
                     fontsize=self.annotate_font_size, 
                     fontweight=self.annotate_font_weight,
                     color=self.annotate_color, 
                     backgroundcolor=self.annotate_background_color)


        # Creating title and legend
        ax[0].set_title('Cohn Alpha Graph')
        ax[0].legend(loc='upper right')


        # Creating axis titles
        ax[0].set_xlim([1, 200])
        ax[0].set_xlabel('Frequency(Hz)')
        ax[0].set_ylabel('Counts$^2$/Hz')


        # Use f for residuals
        ax[1].scatter(f[1:-2], residuals, **settings['Scatter Plot Settings'])
        ax[1].axhline(y=0, color='#162F65', linestyle='--')
        ax[1].set_xlabel('Frequency(Hz)')
        ax[1].set_ylabel('Percent difference (%)')
        
        # Saving figure (optional)
        if settings['Input/Output Settings']['Save figures']:
            fig.tight_layout()
            frequencyString = f"{settings['CohnAlpha Settings']['Frequency Minimum']}_{settings['CohnAlpha Settings']['Frequency Maximum']}_s"
            save_filename = os.path.join(settings['Input/Output Settings']['Save directory'], 'fittedCohnAlpha_' + frequencyString + '.png')
            fig.savefig(save_filename, dpi=300, bbox_inches='tight')


        # Showing plot (optional)
        if settings['General Settings']['Show plots']:
            pyplot.show()
        
        pyplot.close()

        if settings['Input/Output Settings']['Save raw data']:
            ds.exportAnalysis(
                data={
                    'Frequency(Hz)': (f.tolist(), 0),
                    'Counts^2/Hz': (Pxx.tolist(), 0),
                    'Residuals': (residuals.tolist(), 0)
                },
                singles=[('optimal a', popt[0]),
                         ('optimal alpha', popt[1]),
                         ('optimal c', popt[2]),
                         ('alpha', alpha),
                         ('uncertainty', uncertainty)],
                name='ca_graph_s',
                output=settings['Input/Output Settings']['Save directory']
            )
            # outputPath = os.path.abspath(settings['Input/Output Settings']['Save directory'])
            # self.print('Fitted Curve Data saved at ' + str(outputPath))

        # Outputting the PSD distribution and fit
        return {'popt': popt,
                'alpha': alpha,
                'uncertainty': uncertainty}


    def print(self, message):
        if self.quiet:
            return
        print(message)
        
    def plot(self, x, y, residuals = None, method:str = '', settings:dict = {}, **kwargs):

        '''
        Cohn Alpha Plotting Function
        x, y should both be numpy arrays to plot the x,y values
        residuals, popt, and pcov are only used for fitting, otherwise set to None
        method should have 3 possible values, either: 'hist', 'scatter', or 'fit'
        settings are user's current runtime settings

        '''
        # TODO: use kwargs to construct popt and grab alpha and uncertainty values
        # useful links:
        # passing kwargs to function: https://stackoverflow.com/questions/1496346/passing-a-list-of-kwargs
        # how to use kwargs within function: https://stackoverflow.com/questions/1098549/proper-way-to-use-kwargs-in-python

        # grab axis titles and graph name from map
        # return tuple order:
        # x-axis label, y-axis label, graph title, residual's y-axis label
        # if not using residuals, then residual's y-axis label is set to None
        map = {
            'hist': ('Time(s)', 'Counts', 'Cohn-Alpha Counts Histogram', None),
            'scatter': ('Frequency(Hz)', 'Counts^2/Hz', 'Cohn-Alpha Scatter Plot', None),
            'fit': ('Frequency(Hz)', 'Counts^2/Hz', 'Cohn-Alpha Graph', 'Percent difference (%)')
        }
        
        xLabel, yLabel, graphTitle, y2Label = map[method]

        # initialize variables for hist and scatterplot settings
        nRows = 1
        shareX = False
        gridSpecDict = {}

        # update variables for fitting if fitting is chosen
        if method == 'fit':
            nRows = 2
            shareX = True
            gridSpecDict['height_ratios']= [2, 1]


        # initialize plot
        fig, ax = pyplot.subplots(nrows=nRows,sharex=shareX, gridspec_kw=gridSpecDict)

        # fit creates a numpy array, modify data structure to be a numpy array
        if method != 'fit':
            ax = np.array([ax, ax])

        # set axis labelx
        ax[0].set_xlabel(xLabel)
        ax[0].set_ylabel(yLabel)
        ax[0].set_title(graphTitle)

        # if histogram, plot histogram values
        if method == 'hist':
            ax[0].scatter(x=x,
                    y=y,
                    **settings['Scatter Plot Settings'])

        # if scatterplot or fitting, then:
        # change scaling of x-axis to log scaling via semilogx()
        # plot points onto graph
        # update limit of x-axis
        else:
            ax[0].semilogx(x[1:-2], y[1:-2], '.', **settings['Semilog Plot Settings'])
            ax[0].set_xlim([1, 200])
            
            # if fitting, then do addition changes:
            # plot the fitted curve
            # plot the residuals
            # calculate and ddisplay alpha and uncertainty values
            # construct alpha string
            if method == 'fit':
                popt = []
                popt.append(kwargs['optimal a'])
                popt.append(kwargs['optimal alpha'])
                popt.append(kwargs['optimal c'])
                ax[0].semilogx(x[1:-2], CAFit(y[1:-2], *popt), **settings['Line Fitting Settings'])                
                ax[0].legend(loc='upper right')
                ax[1].scatter(x[1:-2], residuals, **settings['Scatter Plot Settings'])
                ax[1].axhline(y=0, color='#162F65', linestyle='--')
                ax[1].set_xlabel(xLabel)
                ax[1].set_ylabel(y2Label)

                # NOTE: should be able to pass in alpha and uncertainty through **kwargs
                # don't need below code
                # alpha = np.around(popt[1]*2*np.pi, decimals=2)
                # uncertainty = np.around(pcov[1,1]*2*np.pi, decimals=2)
                alpha = kwargs['alpha']
                uncertainty = kwargs['uncertainty']
                self.print('alpha = ' + str(alpha) + ', uncertainty = ' + 
                    str(uncertainty))
                
                ymin, ymax = ax[0].get_ylim()
                dy = ymax - ymin
                alph_str = (r'$\alpha$ = (' +
                            '{:.2e}'.format(alpha) + '$\pm$ ' +
                            '{:.2e}'.format(uncertainty) + ') 1/s')
                ax[0].annotate(alph_str,
                               xy=(1.5, ymin+0.1*dy),
                               xytext=(1.5, ymin+0.1*dy),
                               fontsize=self.annotate_font_size,
                               fontweight=self.annotate_font_weight,
                               color=self.annotate_color,
                               backgroundcolor=self.annotate_background_color)

        # reduce padding in the figure
        fig.tight_layout()

        # Saving figure
        # file name: CA_[method]_[freq min]_[freq_max]_[time units].png
        # TODO: start to use settings and time units setting, currently hard coding in seconds
        # NOTE: if saving figure and showing plot: must first save plot, otherwise matplotlib saves a blank plot
        if settings['Input/Output Settings']['Save figures']:
            absPath = os.path.abspath(settings['Input/Output Settings']['Save directory'])
            frequencyString = f"{settings['CohnAlpha Settings']['Frequency Minimum']}_{settings['CohnAlpha Settings']['Frequency Maximum']}_s"
            save_img_filename = os.path.join(absPath, 'CA_' + method + '_' + frequencyString + '.png')
            pyplot.savefig(save_img_filename, dpi=300, bbox_inches='tight')
            self.print('Image saved at ' + save_img_filename)

        # plot and show graph
        # close graph after showing graph
        self.print("Plotting...")
        pyplot.show()
        pyplot.close()

# ---------------------------------------------------------------------------------------------------   

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