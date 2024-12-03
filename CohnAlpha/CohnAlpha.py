from CohnAlpha import CohnAlphaHelper as helper
import numpy as np                     # For processing data
import matplotlib.pyplot as pyplot     # For plotting data summaries
from scipy.optimize import curve_fit   # For fitting the curve
from scipy import signal               # For welch (fourier transform)
import hdf5
from pathlib import Path               # For path manipulation (replaces os)


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
        input_list = settings['Input/Output Settings']['Input file/folder']
        if isinstance(input_list, list):
            if len(input_list) > 2:
                print('ERROR: the suite can only read in 1 or 2 files. Please ensure there are at most 2 files in input file/folder')
                exit(1)
            if len(input_list) > 1 and Path(input_list[0]).suffix != Path(input_list[1]).suffix:
                print('ERROR: different file formats provided. Please check input file/folder and ensure they are the same file format')
                exit(1)
            for item in input_list:
                self.input_file_ext = Path(item).suffix
        
        else:
            self.input_file_ext = Path(input_list).suffix




        self.meas_time_range = np.array(settings['CohnAlpha Settings']['Meas time range'])

        # set measure time range to default value if incorrect input
        if self.meas_time_range == [] or self.meas_time_range is None:
            print("ERROR: Unable to determine Measure Time Range from settings. Please ensure that Measure Time Range setting is correct.")
            exit(1)


        # normalize measure time range to be in output time units
        self.time_factor = settings['General Settings']['Input time units'] / settings['General Settings']['Output time units']
        self.meas_time_range *= self.time_factor

        # calculate and normalize dwell time; change from Hz --> seconds --> output time units
        # if not provided in setting, use except block to set values
        try:
            self.dwell_time = settings['CohnAlpha Settings']['Dwell Time']
            self.nperseg = settings['CohnAlpha Settings']['nperseg']
        except KeyError:
            self.print('Dwell Time and nperseg value not provided')
            self.print('Using frequency minimum and maximum values instead')
            self.dwell_time = 1 / (2 * settings['CohnAlpha Settings']['Frequency Maximum'])
            self.nperseg = 1 / (self.dwell_time * settings['CohnAlpha Settings']['Frequency Minimum'])
            self.dwell_time = self.dwell_time / settings['General Settings']['Input time units']


        # Either multiple by time factor or multiply by output time units since calculated dwell time is in seconds
        self.dwell_time = self.dwell_time * self.time_factor

        # Annotation Parameters
        self.annotate_font_weight = settings['CohnAlpha Settings']['Annotation Font Weight']
        self.annotate_color = settings['CohnAlpha Settings']['Annotation Color']
        self.annotate_background_color = settings['CohnAlpha Settings']['Annotation Background Color']
        self.annotate_font_size = settings['CohnAlpha Settings']['Font Size']


    
    def readInInputFile(self, input):

        if self.input_file_ext == '.hist':
            list_data_array = np.loadtxt(input, delimiter=',',skiprows=5)
        else:
            list_data_array = np.loadtxt(input, usecols=0, dtype=float)

        return list_data_array


    def plotCountsHistogram(self, input_file:str = None, settings: dict = {}, settingsPath:str = './settings/default.json'):

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

        # new count_bins value: 4250000
        # dwell_time value: 0.002
        # Making count of bins over time histogram

        # import data
        # generate corresponding histogram if importing fails
        importResults = hdf5.readHDF5Data(path=['CohnAlpha', 'Histogram'],
                                          settings=settings,
                                          settingsName=settingsPath,
                                          fileName='processing_data')
    
        importResults = None
        plot_method = None

        list_data_array = self.readInInputFile(input=input_file)
        list_data_array *= self.time_factor

        if importResults is not None:
            data = importResults['data']
            edges_seconds, hist = data[:,0], data[:,1]

        elif self.input_file_ext == '.hist':
            # normalize list_data_array to be in output time units
            self.print('Current Mode data provided, using dwell time from input file')
            edges_output, hist = list_data_array[:,0], list_data_array[:,1]
            self.dwell_time = edges_output[1] - edges_output[0]

        else:
            count_bins = np.diff(self.meas_time_range) / self.dwell_time
            hist, edges_output = np.histogram(a=list_data_array,
                                            bins=int(count_bins),
                                            range=self.meas_time_range)
            edges_output = edges_output[:-1]
        
        if self.input_file_ext == '.hist':
            plot_method = 'current_mode'
        else:
            plot_method = 'hist'

        # Plotting
        if settings['General Settings']['Show plots'] or settings['Input/Output Settings']['Save figures']:
            self.plot_ca(x=edges_output,y=hist, input_file=input_file, method=plot_method, settings=settings)

        # Saving raw data
        if settings['Input/Output Settings']['Save outputs']:
            data = np.array([edges_output, hist]).T
            hdf5.writeHDF5Data(npArrays=[data],
                               keys=['data'],
                               path=['CohnAlpha', 'Histogram'],
                               settings=settings,
                               settingsName=settingsPath,
                               fileName='processing_data')

        # Calculating power spectral density distribution from counts over time hist (Get frequency of counts samples)
        # Normalize dwell time and convert back into seconds to calculate sampling frequency in Hz
        # Current mode uses its own dwell time, no need to calculate
        if self.input_file_ext == '.hist':
            self.fs = 1 / self.dwell_time
        else:
            temp_dwell_time = self.dwell_time * settings['General Settings']['Output time units']
            self.fs = 1 / temp_dwell_time

        return edges_output, hist

    def welchApproxFourierTrans(self, input_file:str = None, settings: dict = {}, settingsPath:str = './settings/default.json',):

        '''
        Creating Cohn Alpha Scatterplot from data
        Saving and showing the scatterplot can be turned on or off in the settings
        Visual Settings can also be adjusted in the settings

        Inputs:
            - self: all the private variables in PowerSpectralDensity() object
            - settings: the current user runtime settings

        Output:
            - welchResultDict: a dict, contains the frequency and the power spectral density
        '''

        # Read in existing data if exists
        # file == pynoise.h5, path = CohnAlpha/Scatter
        importResults = hdf5.readHDF5Data(path=['CohnAlpha', 'apsd'],
                                          settings=settings,
                                          settingsName=settingsPath,
                                          fileName='pynoise')
        
        # If existing data does not exist
        # import data from disk
        if importResults is not None:
            data = importResults['graphData']
            f = data[:, 0]
            Pxx = data[:, 1]

        # otherwise re-calculate data and re-plot histogram
        if importResults is None or settings['General Settings']['Show plots']:
            # check to see if nperseg is a power of 2
            if not helper.checkPowerOfTwo(value=int(self.nperseg)):
                self.print('WARNING: calculated nperseg: ' + str(int(self.nperseg)) + ' is not a power of 2')
            
            # initialize counts histogram list
            # generate frequency and power spectral densities
            edges_output, hist = self.plotCountsHistogram(input_file=input_file, settings=settings, settingsPath=settingsPath)
            f, Pxx = signal.welch(x=hist,
                                  fs=self.fs,
                                  nperseg=int(self.nperseg), 
                                  window='boxcar')


        # Plotting
        if settings['General Settings']['Show plots'] or settings['Input/Output Settings']['Save figures']:
            self.plot_ca(x=f, y=Pxx, input_file=input_file, method='scatter', settings=settings)

        # Saving raw data
        if settings['Input/Output Settings']['Save outputs']:
            data = np.array([f, Pxx]).T
            hdf5.writeHDF5Data(npArrays=[data],
                               keys=['graphData'],
                               path=['CohnAlpha', 'Scatter'],
                               settings=settings,
                               settingsName=settingsPath,
                               fileName='pynoise')

        return (f, Pxx)
        

    def conductAPSD(self, input_file:str = None, settings: dict = {}, settingsPath:str = './settings/default.json'):

        '''
        Fits Power Spectral Density onto provided scatterplot
        Saving and showing the graph can be turned on or off in the settings
        Visual Settings can also be adjusted in the settings

        Inputs:
            - self: all the private variables in PowerSpectralDensity() object
            - settings: the current user runtime settings

            
        Output:
            - dict: contains the fitted curve, in addition to alpha and uncertainty values
            - popt: key == 'popt', will contain the popt list returned from curve_fit()
            - alpha: key == 'alpha', will contain printed alpha value
            - uncertainty: key == 'uncertainty', will contain printed uncertainty value

----------------------------------------------------------------------------------------
        Old docstring:
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

        # read in files
        importResults = hdf5.readHDF5Data(path=['CohnAlpha', 'apsd'],
                                        settings=settings,
                                        settingsName=settingsPath,
                                        fileName='pynoise')
        
        # If existing data does not exist
        # import data from disk
        if importResults is not None:
            data = importResults['graphData']
            f = data[:, 0]
            Pxx = data[:, 1]

        # otherwise re-calculate data and re-plot histogram + scatterplot
        # Fitting distribution with expected equation
        if importResults is None or settings['General Settings']['Show plots']:
            f, Pxx = self.welchApproxFourierTrans(settings=settings, input_file=input_file, settingsPath=settingsPath)


        # plots the graph
        # will call fit() as well to fit the curve
        # plot() will return the dict containing popt, alpha, uncertainty
        popt, pcov, alpha, uncertainty, residuals = self.plot_ca(x=f, y=Pxx, input_file=input_file, method='apsd', settings=settings)

        # Saving raw data
        if settings['Input/Output Settings']['Save outputs']:
            data = np.array([f, Pxx]).T
            alpha_uncertainty = np.array([alpha, uncertainty])
            hdf5.writeHDF5Data(npArrays=[data, residuals, popt, alpha_uncertainty],
                               keys=['graphData', 'residuals', 'popt', 'alpha_uncertainty'],
                               path=['CohnAlpha', 'apsd'],
                               settings=settings,
                               settingsName=settingsPath,
                               fileName='pynoise')
            hdf5.exportFissionChamberData(settings=settings)

        return popt, alpha, uncertainty


    def conductCPSD(self,
                     input_list:list = [],
                     settings:dict = {},
                     show_plot: bool = True,
                     save_fig: bool = True,
                     save_dir: str = './',
                     caSet: dict = {},
                     sps: dict = {},
                     lfs: dict = {},
                     scatter_opt: dict = {},
                     settingsPath:str = './settings/default.json'):
        
        
        # Annotation Parameters
        self.annotate_font_weight = settings['CohnAlpha Settings']['Annotation Font Weight']
        self.annotate_color = settings['CohnAlpha Settings']['Annotation Color']
        self.annotate_background_color = settings['CohnAlpha Settings']['Annotation Background Color']

        input_list = settings['Input/Output Settings']['Input file/folder']
        graph_title = str(Path(input_list[0]).stem) + '_' + str(Path(input_list[1]).stem)
            
        edges_seconds, hist1 = self.plotCountsHistogram(settings=settings, input_file=input_list[0])
        edges_seconds, hist2 = self.plotCountsHistogram(settings=settings, input_file=input_list[1])

        counts_time_hist = np.array([hist1, hist2]).T

        f, Pxy = signal.csd(
            counts_time_hist[:, 0], 
            counts_time_hist[:, 1], 
            self.fs,
            nperseg=settings['CohnAlpha Settings']['nperseg'], 
            window='boxcar')
        
        
        
        
        Pxy = np.abs(Pxy)
        
        alpha = np.around(popt[1]*2*np.pi, decimals=2)
        uncertainty = np.around(np.sqrt(pcov[1,1])*2*np.pi, decimals=2)
        
        # if settings['General Settings']['Show plots'] or settings['Input/Output Settings']['Save figures']:
        popt, pcov, alpha, uncertainty, residuals = self.plot_ca(x=f, y=Pxy, input_file=graph_title, method='cpsd', settings=settings, **kwDict)

        # Saving raw data
        if settings['Input/Output Settings']['Save outputs']:
            data = np.array([f, Pxy]).T
            alpha_uncertainty = np.array([alpha, uncertainty])
            hdf5.writeHDF5Data(npArrays=[data, popt, alpha_uncertainty],
                               keys=['graphData', 'popt', 'alpha_uncertainty'],
                               path=['CohnAlpha', 'CPSD'],
                               settings=settings,
                               settingsName=settingsPath,
                               fileName='pynoise')
            hdf5.exportFissionChamberData(settings=settings)

        # Making count of bins over time histogram
        # count_bins = np.diff(self.meas_time_range) / self.dwell_time

        # counts_time_hist = np.zeros([2,int(count_bins)])

        # index = self.list_data_array[:,0]!=0

        # times = self.list_data_array[index, 0]

        # N, _ = np.histogram(
        #             times,
        #             bins=int(count_bins),
        #             range=self.meas_time_range
        #             )
        # counts_time_hist[0,:] = N

        # list_data_array = np.loadtxt(caSet['Second Input file'])
        # index = list_data_array[:,0]!=0

        # N, _ = np.histogram(list_data_array,
        #                     bins=int(count_bins),
        #                     range=self.meas_time_range)
        
        # counts_time_hist[1,:] = N
        
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

        # timeline = np.linspace(start=self.meas_time_range[0], 
        #                     stop=self.meas_time_range[1],
        #                     num=int(count_bins))/1e9

        '''fig1, ax1 = pyplot.subplots()
        ax1.plot(timeline, counts_time_hist, '.', label="TBD")
        ax1.plot(timeline, counts_time_hist2, '.', label="TBD")

        ax1.set_ylabel('Counts')
        ax1.set_xlabel('Time(s)')
        ax1.legend()'''
        
        # Plot counts over time histogram (ensure constant or near constant)
        # i=0
        # for ch in [0,1]:
        #     fig1, ax1 = pyplot.subplots()
        #     # ax1.plot(timeline, counts_time_hist[i,:], '.', label="TBD")
        #     ax1.plot(edges_seconds, counts_time_hist[:, i], '.', label="TBD")

        #     ax1.set_ylabel('Counts')
        #     ax1.set_xlabel('Time(s)')
        #     ax1.legend()
        #     i+=1

        # fs = 1/(timeline[3]-timeline[2]) # Get frequency of counts samples

        # f, Pxy = signal.csd(
        #     counts_time_hist[0,:], 
        #     counts_time_hist[1,:], 
        #     fs, 
        #     nperseg=settings['CohnAlpha Settings']['nperseg'], 
        #     window='boxcar')

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
        
        # fig2, ax2 = pyplot.subplots()
        # ax2.semilogx(f[1:-2], Pxy[1:-2], '.', **sps)
        # ax2.semilogx(f[1:-2], CAFit(f[1:-2], *popt), **lfs)
        # ymin, ymax = ax2.get_ylim()
        # dy = ymax-ymin
        # ax2.set_xlim([1, 200])
        # ax2.set_xlabel('Frequency(Hz)')
        # ax2.set_ylabel('PSD (V$^2$/Hz)')
        # # ax2.set_yscale('log')
        # alph_str = (r'$\alpha$ = (' +
        #         str(np.around(popt[1]*2*np.pi, decimals=2))+
        #         '$\pm$ '+
        #         str(np.around(np.sqrt(pcov[1,1])*2*np.pi, decimals=2))
        #         +') 1/s')
        # ax2.annotate(alph_str, xy=(1.5, ymin+0.1*dy), xytext=(1.5, ymin+0.1*dy),
        #             fontsize=16, fontweight='bold',
        #             color='black', backgroundcolor='white')
        # # ax2.text(1.5, ymin+0.1*dy, alph_str)


            

        # ax2.grid()



        # fig2.tight_layout()

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



        return f, Pxy, popt, pcov
# ---------------------------------------------------------------------------------------------------

    def print(self, message):

        '''
        Self-defined print function
        Will print if quiet mode is set to false, otherwise prints nothing
        '''
        if self.quiet:
            return
        print(message)


    def plot_ca(self, x, y, input_file:str = "", method:str = '', settings:dict = {}):

        '''
        Cohn Alpha Plotting Function
        x, y should both be numpy arrays to plot the x,y values
        method should have 4 possible values, either: 'hist', 'scatter', 'apsd', or 'cpsd'
        settings are user's current runtime settings

        '''

        # grab axis titles and graph name from map
        # return tuple order: x-axis label, y-axis label, graph title
        # map = {
        #     'hist': ('Time(s)', 'Signal(V)', 'Cohn-Alpha Counts Histogram'),
        #     'scatter': ('Frequency(Hz)', 'Counts^2/Hz', 'Cohn-Alpha Scatter Plot'),
        #     'fit': ('Frequency(Hz)', 'Counts^2/Hz', 'Cohn-Alpha Graph')
        # }
        
        self.print("Plotting...")
        output_units_str = helper.convertTimeUnitsToStr(settings['General Settings']['Output time units'])
        output_units_freq_str = helper.convertTimeUnitsToStrInverse(settings['General Settings']['Output time units'])
        frequency_units_str = output_units_freq_str + 'Hz'

        map = {
            'hist': (f"Time({output_units_str}s)", 'Counts'),
            'current_mode': ('Time(s)', 'Signal(V)'),
            'scatter': (f"Frequency({frequency_units_str})", f"Counts$^2$/{frequency_units_str}"),
            'apsd': (f"Frequency({frequency_units_str})", f"Counts$^2$/{frequency_units_str}"),
            'cpsd': (f"Frequency({frequency_units_str})", f"PSD (V$^2$/{frequency_units_str})")
        }

        xLabel, yLabel = map[method]

        # initialize variables for hist and scatterplot settings
        nRows = 1
        shareX = False
        gridSpecDict = {}

        # update variables for fitting if fitting is chosen
        if method == 'apsd':
            nRows = 2
            shareX = True
            gridSpecDict['height_ratios']= [2, 1]

        # initialize plot
        fig, ax = pyplot.subplots(nrows=nRows,sharex=shareX, gridspec_kw=gridSpecDict)

        # small data manipulation, makes code cleaner
        if method != 'apsd':
            ax = np.array([ax, ax])

        # set axis labels
        ax[0].set_xlabel(xLabel)
        ax[0].set_ylabel(yLabel)

        ax[0].set_title(input_file)

        # if histogram, plot histogram values
        if method == 'hist' or method == 'current_mode':
            ax[0].scatter(x=x,
                    y=y,
                    **settings['Scatter Plot Settings'])

        # if scatterplot or fitting, then:
        # change scaling of x-axis to log scaling + plot points
        # update limit of x-axis

        # update units of x for non-histogram graphs (change from Hz --> output units)
        else:
            x = x * settings['General Settings']['Output time units']
            ax[0].semilogx(x[1:-2], y[1:-2], '.', **settings['Semilog Plot Settings'])
            # ax[0].set_xlim([1, 300])


            # if fitting, then call fit() and fit curve
            # use kwargs to pass popt, alpha, uncertainty
            if method == 'apsd' or method == 'cpsd':
                popt, pcov, alpha, uncertainty, residuals = self.fit_ca(x=x,
                                                                        y=y,
                                                                        ax=ax,
                                                                        settings=settings)


        # Saving figure
        # file name: CA_[method]_[input_file name].png
        # NOTE: few concerns
        # if saving figure and showing plot: must first save plot, otherwise matplotlib saves a blank plot
        if settings['Input/Output Settings']['Save figures']:
            # reduce padding in the figure
            fig.tight_layout()
            absPath = Path(settings['Input/Output Settings']['Save directory']).resolve()
            output_units_str = helper.convertTimeUnitsToStr(settings['General Settings']['Output time units']) + 's'
            save_img_filename = absPath / ('CA_' + method + '_' + Path(input_file).stem + '_' + output_units_str + '.png')
            pyplot.savefig(save_img_filename, dpi=300, bbox_inches='tight')
            self.print('Image saved at ' + str(save_img_filename))


        # plot and show graph
        # close graph after showing graph
        if settings['General Settings']['Show plots']:
            pyplot.show()
        
        pyplot.close()

        try:
            return popt, pcov, alpha, uncertainty, residuals
        except Exception as e:
            return None


    def fit_ca(self, x, y, ax, settings:dict = {}):

        '''
        Fitting Function, plots fitted curve
        assumes plot() has been called with method='fit' 
        Fits scatterplot with Power Spectral Density Curve

        Inputs:
            self: (TODO: ADD DESCRIPTION)
            fig: the figure returned by pyplot.subplots()
            ax: the axes returned by pyplot.subplots()
            fitEquation: the equation that will be used by curve_fit() to fit the graph
            kwargs: (TODO: ADD DESCRIPTION)
        '''

        p0 = [y[2], np.mean(x), np.mean(y[-10:-2])]

        # Ignore start & end points that are incorrect due to welch endpoint assumptions
        if self.input_file_ext == '.hist':

            # Due to reactor issues, some frequencies are not accurately calculated; filter out frequencies
            index = ((x < 45) | ((x > 56) & (x < 148)) | ((x > 152) & (x < 248)) | ((x > 252) & (x < 300)))
            x = x[index]
            y = y[index]           
            popt, pcov = curve_fit(CAFit,
                            x[2:-1],
                            y[2:-1],
                            p0=p0,
                            maxfev=1000000)
            residuals = None

        else:
            popt, pcov = curve_fit(CAFit,
                                x[1:-2],
                                y[1:-2],
                                p0=p0,
                                bounds=(0, np.inf),
                                maxfev=100000)
            alpha = np.around(popt[1]*2*np.pi / settings['General Settings']['Output time units'], decimals=2)
            uncertainty = np.around(pcov[1,1]*2*np.pi / settings['General Settings']['Output time units'], decimals=2)
            residuals = ((CAFit(x[1:-2], *popt) - y[1:-2]) / y[1:-2]) * 100

        # Display Alpha and Uncertainty values, store within Welch Approx
        self.print('alpha = ' + str(alpha) + ', uncertainty = '+ 
                    str(uncertainty))
        
        ax[0].semilogx(x[1:-2], CAFit(x[1:-2], *popt), **settings['Line Fitting Settings'])                
        ax[0].legend(loc='upper right')
        
        ymin, ymax = ax[0].get_ylim()
        dy = ymax - ymin

        time_units = helper.convertTimeUnitsToStr(settings['General Settings']['Output time units'])
        alph_str = (r'$\alpha$ = (' +
                    '{:.2e}'.format(alpha) + '$\pm$ ' +
                    '{:.2e}'.format(uncertainty) + ') ')
        
        alph_str += f"1/{time_units}s"
        
        ax[0].annotate(alph_str,
                        xy=(1.5 * settings['General Settings']['Output time units'], ymin+0.1 * dy),
                        xytext=(1.5 * settings['General Settings']['Output time units'], ymin+0.1 * dy),
                        fontsize=self.annotate_font_size,
                        fontweight=self.annotate_font_weight,
                        color=self.annotate_color,
                        backgroundcolor=self.annotate_background_color)

        if residuals is None:
            return popt, pcov, alpha, uncertainty, residuals

        output_units_str = helper.convertTimeUnitsToStrInverse(settings['General Settings']['Output time units'])
        frequency_units_str = output_units_str + 'Hz'

        # plot residuals
        # label axis
        ax[1].scatter(x[1:-2], residuals, **settings['Scatter Plot Settings'])
        ax[1].axhline(y=0, color='#162F65', linestyle='--')
        ax[1].set_xlabel(f"Frequency({frequency_units_str})")
        ax[1].set_ylabel('Percent difference (%)')
        return popt, pcov, alpha, uncertainty, residuals


