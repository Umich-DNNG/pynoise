from CohnAlpha import CohnAlphaHelper as helper
import numpy as np                     # For processing data
import matplotlib.pyplot as pyplot     # For plotting data summaries
from scipy.optimize import curve_fit   # For fitting the curve
from scipy import signal               # For welch (fourier transform)
from pathlib import Path               # path manipulation
import datastream as ds                # for importing/exporting analysis
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
        return edges_seconds, counts_time_hist
    
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
            if not helper.checkPowerOfTwo(value=int(nperseg)):
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

        --------------------------------------------------------------------------------
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

        # TODO: need to change quite a few things
        # plotting() function finished, need to create separate fitting function instead
        # use plot to place the initial data points, then use fit to place the fitted curve
        # call curve_fit and everything inside the fit function
        # self.plot(x=f, y=Pxx, method='fit', settings=settings)


        
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
        
    def plot(self, x, y, method:str = '', settings:dict = {}):

        '''
        Cohn Alpha Plotting Function
        x, y should both be numpy arrays to plot the x,y values
        method should have 3 possible values, either: 'hist', 'scatter', or 'fit'
        settings are user's current runtime settings

        '''

        # grab axis titles and graph name from map
        # return tuple order: x-axis label, y-axis label, graph title
        map = {
            'hist': ('Time(s)', 'Counts', 'Cohn-Alpha Counts Histogram'),
            'scatter': ('Frequency(Hz)', 'Counts^2/Hz', 'Cohn-Alpha Scatter Plot'),
            'fit': ('Frequency(Hz)', 'Counts^2/Hz', 'Cohn-Alpha Graph')
        }
        
        xLabel, yLabel, graphTitle = map[method]

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

        # small data manipulation to make code organization easier
        # if nrows > 1 (used above in pyplot.subplots() when method == 'fit'), ax becomes list
        # if nrows == 1 (used above in pyplot.subplots() when method != 'fit'), ax becomes a single variable
        # turn single variable into list for code consistency
        if method != 'fit':
            ax = np.array([ax, ax])

        # set axis labels
        ax[0].set_xlabel(xLabel)
        ax[0].set_ylabel(yLabel)
        ax[0].set_title(graphTitle)

        # if histogram, plot histogram values
        if method == 'hist':
            ax[0].scatter(x=x,
                    y=y,
                    **settings['Scatter Plot Settings'])

        # if scatterplot or fitting, then:
        # change scaling of x-axis to log scaling
        # plot points onto graph
        # update limit of x-axis
        else:
            ax[0].semilogx(x[1:-2], y[1:-2], '.', **settings['Semilog Plot Settings'])
            ax[0].set_xlim([1, 200])
            
            # if fitting, then return
            # points have already been plotted, need to fit a curve
            # fit() will fit the curve and show plot
            if method == 'fit':
                return (fig, ax)


        # Saving figure
        # file name: CA_[method]_[freq min]_[freq_max]_[time units].png
        # TODO: start to use settings and time units setting, currently hard coding in seconds
        # NOTE: if saving figure and showing plot: must first save plot, otherwise matplotlib saves a blank plot
        if settings['Input/Output Settings']['Save figures']:
            # reduce padding in the figure
            fig.tight_layout()
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

        # return tuple to be consistent with method == 'fit'
        return None, None

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

            '''
            Fitting Function; assumes plot() has been called with method='fit' 
            Fits scatterplot with Power Spectral Density Curve

            Inputs:
                self: (TODO: ADD DESCRIPTION)
                fig: the figure returned by pyplot.subplots()
                ax: the axes returned by pyplot.subplots()
                fitEquation: the equation that will be used by curve_fit() to fit the graph
                kwargs: (TODO: ADD DESCRIPTION)
            '''
            'Percent difference (%)'
            popt = []
            popt.append(kwargs['optimal a'])
            popt.append(kwargs['optimal alpha'])
            popt.append(kwargs['optimal c'])
            popt = np.array(popt,dtype=np.float64)
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

# ---------------------------------------------------------------------------------------------------