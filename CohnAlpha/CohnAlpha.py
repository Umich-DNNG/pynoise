import numpy as np                     # For processing data
import matplotlib.pyplot as pyplot     # For plotting data summaries
from scipy.optimize import curve_fit   # For fitting the curve
from scipy import signal               # For welch (fourier transform)
from pathlib import Path               # Currently strings for pathnames are not working, attempting to use pathlib/Path
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
                 list_data_array,
                 dwell_time: float = 2.0e6, 
                 meas_time_range: list[float] = [1.5e11, 1.0e12]):

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

        # Required Parameters
        self.list_data_array = list_data_array
        self.meas_time_range = meas_time_range
        self.dwell_time = dwell_time
        self.fs = 0

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
        ax1.set_xlabel('Time (s)')
        ax1.legend()'''
        
        # Plot counts over time histogram (ensure constant or near constant)
        i=0
        for ch in [0,1]:
            fig1, ax1 = pyplot.subplots()
            ax1.plot(timeline, counts_time_hist[i,:], '.', label="TBD")

            ax1.set_ylabel('Counts')
            ax1.set_xlabel('Time (s)')
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
            pyplot.show()
        '''
        pyplot.show()

        return f, Pxy, popt, pcov    


    def conductCohnAlpha(self, settings: dict = {}):
        
        '''
        Deprecated Function. Just call FitPSDCurve() instead


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
        # Annotation Parameters
        self.annotate_font_weight = settings['CohnAlpha Settings']['Annotation Font Weight']
        self.annotate_color = settings['CohnAlpha Settings']['Annotation Color']
        self.annotate_background_color = settings['CohnAlpha Settings']['Annotation Background Color']
        self.annotate_font_size = settings['CohnAlpha Settings']['Font Size']
        
        # Making count of bins over time histogram
        count_bins = np.diff(self.meas_time_range) / self.dwell_time
        
        # TODO: need to ensure that:
        # input file, dwell time, measure time range, and nperseg are the same
        # grab information from filename, compare with current settings
        # if different, then generate, else continue
        # NOTE: dwell_time and measure time range are FLOATS. Need to use math.isclose()


        # if settings are different:
        #   re-generate

        # read in histogram data
        counts_time_hist = []
        edges_seconds = []
        readInFile(settings=settings, x=edges_seconds, y=counts_time_hist, residuals=None, method='Histogram')

        # If unable to read in data/no data exists
        # Generating corresponding histogram
        if counts_time_hist == [] or edges_seconds == []:
            counts_time_hist, edges = np.histogram(a=self.list_data_array, 
                                                   bins=int(count_bins), 
                                                   range=self.meas_time_range)
            edges_seconds = edges / 1e9
            edges_seconds = edges_seconds[:-1]
        else:
            counts_time_hist = np.array(counts_time_hist, dtype=np.int64)
            edges_seconds = np.array(edges_seconds, dtype=np.float64)

        # Plotting counts histogram
        if settings['General Settings']['Show plots']:
            print("Plotting Histogram...")
            pyplot.scatter(edges_seconds, counts_time_hist, **settings['Scatter Plot Settings'])
            pyplot.xlabel('Time (s)')
            pyplot.ylabel('Counts')
            pyplot.title('Cohn-Alpha Counts Histogram')
            pyplot.show()
            
            # Saving counts histogram
            if settings['Input/Output Settings']['Save figures']:
                pyplot.tight_layout()
                absPath = os.path.abspath(settings['Input/Output Settings']['Save directory'])
                save_img_filename = os.path.join(absPath, 'CACountsHist' + str(self.dwell_time) + '.png')
                pyplot.savefig(save_img_filename, dpi=300, bbox_inches='tight')
                # print('Histogram Image saved at ' + save_img_filename)

            pyplot.close()
        # Saving counts histogram raw data
        if settings['Input/Output Settings']['Save raw data']:
            outputPath = exportRawData(x=edges_seconds, 
                                       y=counts_time_hist, 
                                       residuals=None, 
                                       settings=settings, 
                                       method='Histogram')
            # print('Histogram Data saved at ' + str(outputPath))

        # Creating evenly spaced start and stop endpoint for plotting
        timeline = np.linspace(start=self.meas_time_range[0], 
                            stop=self.meas_time_range[1],
                            num=int(count_bins))/1e9
        
        # Calculating power spectral density distribution from counts over time hist (Get frequency of counts samples)
        self.fs = 1 / (timeline[3]-timeline[2])
        return counts_time_hist
    
    def welchApproxFourierTrans(self, counts_time_hist, settings:dict = {}):

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

        # Read in existing data if exists
        f = []
        Pxx = []

        readInFile(settings=settings,
                   x=f, 
                   y=Pxx, 
                   residuals=None,
                   method='Welch Result')

        
        # If existing data does not exist
        # Apply welch approximation of the fourier transform, converting counts over time to a frequency distribution
        if f == [] or Pxx == []:
            f, Pxx = signal.welch(x=counts_time_hist,
                                fs=self.fs, 
                                nperseg=settings['CohnAlpha Settings']['nperseg'], 
                                window='boxcar')
        # convert lists to numpy arrays
        else:
            f = np.array(f, dtype=np.float64)
            Pxx = np.array(Pxx, dtype=np.float64)
            

        welchResultDict = {'f': f,
                           'Pxx': Pxx}

        # Plotting the auto-power-spectral-density distribution and fit
        fig, ax = pyplot.subplots(figsize=(8, 6))

        # Creating a plot with semilogarithmic (log-scale) x-axis 
        ax.semilogx(f[1:-2], Pxx[1:-2], '.', **settings['Semilog Plot Settings'])

        # Creating title and legend
        ax.set_title('Cohn Alpha Scatter Plot')

        # Creating axis titles
        ax.set_xlim([1, 200])
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Counts$^2$/Hz')

        # Saving figure (optional)
        if settings['Input/Output Settings']['Save figures']:
            fig.tight_layout()
            save_filename = os.path.join(settings['Input/Output Settings']['Save directory'], 'CAScatterPlot' + str(self.dwell_time) + '.png')
            fig.savefig(save_filename, dpi=300, bbox_inches='tight')
            # print('Scatterplot Image saved at ' + save_filename)


        # Showing plot (optional)
        if settings['General Settings']['Show plots']:
            pyplot.show()
        
        pyplot.close()
        
        # Saving scatter plot data (optional)
        if settings['Input/Output Settings']['Save raw data']:
            outputPath = exportRawData(x=f, 
                                       y=Pxx, 
                                       residuals=None, 
                                       settings=settings, 
                                       method='Welch Result')
            # print('Scatterplot Data saved at ' + str(outputPath))

        # Return values needed to be saved for the fitting
        return welchResultDict
        

    def fitPSDCurve(self, settings:dict = {}, welchResultDict:dict = {}):

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

        f = welchResultDict['f']
        Pxx = welchResultDict['Pxx']

        # Ignore start & end points that are incorrect due to welch endpoint assumptions        
        f = f[1:-2]
        Pxx = Pxx[1:-2]

        # Fitting distribution with expected equation
        popt, pcov = curve_fit(CAFit, 
                            f, 
                            Pxx,
                            p0=[Pxx[2], 25, 0.001],
                            bounds=(0, np.inf),
                            maxfev=100000)

        # save Alpha and Uncertainty values
        alpha = np.around(popt[1]*2*np.pi, decimals=2)
        uncertainty = np.around(pcov[1,1]*2*np.pi, decimals=2)
    
        # Display Alpha and Uncertainty values, store within Welch Approx
        print('alpha = ' + str(alpha) + ', uncertainty = '+ 
                    str(uncertainty))

        
        # Plotting the auto-power-spectral-density distribution and fit
        fig, (ax1, ax2) = pyplot.subplots(nrows=2, sharex=True, figsize=(8, 6), gridspec_kw={'height_ratios': [2, 1]})


        # Creating a plot with semilogarithmic (log-scale) x-axis 
        ax1.semilogx(f, Pxx, '.', **settings['Semilog Plot Settings'])
        ax1.semilogx(f, CAFit(f, *popt), **settings['Line Fitting Settings'])


        
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
                     fontsize=self.annotate_font_size, 
                     fontweight=self.annotate_font_weight,
                     color=self.annotate_color, 
                     backgroundcolor=self.annotate_background_color)
        
        # Creating title and legend
        ax1.set_title('Cohn Alpha Graph')
        ax1.legend(loc='upper right')

        # Creating axis titles
        ax1.set_xlim([1, 200])
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('Counts$^2$/Hz')

        # Compute residuals
        residuals = ((CAFit(f, *popt) - Pxx) / Pxx) * 100


        ax2.scatter(f, residuals, **settings['Scatter Plot Settings'])  # Use f for residuals
        ax2.axhline(y=0, color='#162F65', linestyle='--')
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Percent difference (%)')
        
        # Saving figure (optional)
        if settings['Input/Output Settings']['Save figures']:
            fig.tight_layout()
            save_filename = os.path.join(settings['Input/Output Settings']['Save directory'], 'CohnAlpha' + str(self.dwell_time) + '.png')
            fig.savefig(save_filename, dpi=300, bbox_inches='tight')


        # Showing plot (optional)
        if settings['General Settings']['Show plots']:
            pyplot.show()
        
        pyplot.close()

        # saving graph data (optional)
        # TODO: fix
        # Placeholder for now, need to actually export the data
        if settings['Input/Output Settings']['Save raw data']:
            outputPath = exportRawData(x=f,
                                       y=Pxx,
                                       residuals=residuals,
                                       alpha=alpha,
                                       uncertainty=uncertainty,
                                       settings=settings,
                                       method='PSD Fit Curve')
            # print('Fitted Curve Data saved at ' + str(outputPath))
        
        # Outputting the PSD distribution and fit
        return {'popt': popt,
                'pcov': pcov,
                'alpha': alpha,
                'uncertainty': uncertainty}

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
    
def readInFile(settings, x, y, residuals:None, method:str = ""):

    # using a dict instead of match-case statements
    map = {
        'Histogram': 'hist',
        'Welch Result': 'scatter',
        'PSD Fit Curve': 'fit'
    }

    # grab input file name
    inputFileName = os.path.abspath(settings['Input/Output Settings']['Input file/folder'])
    inputFileName = Path(inputFileName).stem

    # construct fileName
    # fileName structure:
    # ca_[graph_type]_[dwell_time]_[measure time range]_[nperseg].csv
    fileName = "ca"
    fileName = fileName + "_" + map[method]
    fileName = fileName + "_" + str(settings['CohnAlpha Settings']['Dwell time'])

    timeRangeStart = str(settings['CohnAlpha Settings']['Meas time range'][0])
    timeRangeEnd = str(settings['CohnAlpha Settings']['Meas time range'][1])
    fileName = fileName + "_" + timeRangeStart + "-" + timeRangeEnd
    fileName = fileName + "_" + str(settings['CohnAlpha Settings']['nperseg']) + ".csv"

    inputPath = os.path.abspath(settings['Input/Output Settings']['Save directory'])
    inputPath = Path(inputPath)
    inputPath = inputPath / fileName

    # open file
    # skip header, store in case needed
    # read in data
    try:
        with open(inputPath, 'r') as file:
            headerLine = next(file)
            if method != 'PSD Fit Curve':
                # read in file
                for line in file:
                    splitLines = line.split(',')
                    x.append(splitLines[0])
                    y.append(splitLines[1])

                print ("Existing Data found at " + str(inputPath))
                return
            else:
                # read in first line separately to grab alpha and uncertainty values
                firstLine = next(file)
                firstLine = firstLine.split(',')
                x.append(splitLines[0])
                y.append(splitLines[1])
                residuals.append(splitLines[2])
                alpha = splitLines[3]
                uncertainty = splitLines[4]
                # read in the rest of the file
                for line in file:
                    splitLines = line.split(',')
                    x.append(splitLines[0])
                    y.append(splitLines[1])
                    residuals.append(splitLines[2])
                print ("Existing Data found at " + str(inputPath))
                return (alpha, uncertainty)


            
    # If graph data unable to be found
    # Then return false and generate the data
    except FileNotFoundError:
        # TODO: print current settings as well
        print("Existing Data with current settings could not be found")
        print("Data must be stored within the save directory listed in the settings.")
        print("Generating Data...")
        return
    

def exportRawData(x, y, residuals=None, alpha=None, uncertainty=None, settings:dict={}, method:str=""):

    # fileName format:
    # ca_[graph_type]_[input file/folder]_[dwell_time]_[measure_time_range]_[nperseg].csv

    # using dict instead of match-case statements
    map = {
        'Histogram': 'hist',
        'Welch Result': 'scatter',
        'PSD Fit Curve': 'fit'
    }
    # grab input file's name
    inputFileName = os.path.abspath(settings['Input/Output Settings']['Input file/folder'])
    inputFileName = Path(inputFileName).stem

    # construct fileName
    fileName = "ca"
    fileName = fileName + "_" + map[method]
    fileName = fileName + "_" + str(settings['CohnAlpha Settings']['Dwell time'])

    timeRangeStart = str(settings['CohnAlpha Settings']['Meas time range'][0])
    timeRangeEnd = str(settings['CohnAlpha Settings']['Meas time range'][1])
    fileName = fileName + "_" + timeRangeStart + "-" + timeRangeEnd
    fileName = fileName + "_" + str(settings['CohnAlpha Settings']['nperseg']) + ".csv"

    # construct output directory
    outputPath = os.path.abspath(settings['Input/Output Settings']['Save directory'])
    outputPath = Path(outputPath)
    outputPath = outputPath / fileName

    # open file
    # write header
    # then write data
    with open(outputPath, "w+") as file:
        if method == 'Histogram':
            # convert time units to string
            timeUnits = settings['General Settings']['Output time units']
            timeUnits = convertTimeUnitsToStr(timeUnits)
            file.write("%s,%s\n" % ("counts", "time(" + timeUnits + ')'))
            for x, y in zip(x, y):
                file.write("%s,%s\n" % (x, y))

        elif method == 'Welch Result':
            file.write("%s,%s\n" % ('Frequency(Hz)', 'Counts^2/Hz'))
            for x, y in zip(x, y):
                file.write("%s,%s\n" % (x, y))

        elif method == 'PSD Fit Curve':
            file.write("%s,%s,%s,%s,%s\n" % ('Frequency(Hz)', 'Counts^2/Hz', 'Percent Difference', 'Alpha', 'Uncertainty'))
            file.write("%s,%s,%s,%s,%s\n" % (x[0], y[0], residuals[0], alpha, uncertainty))
            for x, y, residuals, in zip(x[1:], y[1:], residuals[1:]):
                file.write("%s,%s,%s\n" % (x, y, residuals))

    return outputPath