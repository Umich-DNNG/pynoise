from CohnAlpha import CohnAlphaHelper as helper
import numpy as np                     # For processing data
import matplotlib.pyplot as pyplot     # For plotting data summaries
from scipy.optimize import curve_fit   # For fitting the curve
from scipy import signal               # For welch (fourier transform)
import os                              # For saving figures
import hdf5
from pathlib import Path

import time
import sys
import bisect

import CohnAlpha.WelchAndCSD as testing


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

        # Required Parameters

        # Load the values from the specified file into an NP array.
        self.meas_time_range = settings['CohnAlpha Settings']['Meas time range']
    
        # set measure time range to default value if incorrect input
        if self.meas_time_range == [] or self.meas_time_range is None:
            self.print("Unable to determine Measure Time Range from settings")
            self.print("Setting Measure Time Range to default values of [1.5e11, 1.0e12] in ns")
            self.meas_time_range = [1.5e11, 1.0e12]

        # Annotation Parameters
        self.annotate_font_weight = settings['CohnAlpha Settings']['Annotation Font Weight']
        self.annotate_color = settings['CohnAlpha Settings']['Annotation Color']
        self.annotate_background_color = settings['CohnAlpha Settings']['Annotation Background Color']
        self.annotate_font_size = settings['CohnAlpha Settings']['Font Size']


    def memControl(self, settings: dict = {}, settingsPath:str = './settings/default.json'):

        '''
        loads a txt file by portions for memory control
        '''

        dwell_time = 1 / (2 * settings['CohnAlpha Settings']['Frequency Maximum'])
        dwell_time_ns = dwell_time * 1e9
        # nperseg = num bins for each segment
        nperseg = int(1 / (dwell_time * settings['CohnAlpha Settings']['Frequency Minimum']))
        # amount of s in a segment
        segmentLength = nperseg * dwell_time
        # amount of time (in input units) in a segment
        # segmentLength = segmentLength / settings['General Settings']['Input time units']
        segmentLength = segmentLength * 1e6
        numSegments = 0
        
        fftSum = []

        self.print("Reading in input file/folder data...")

# hertz for frequency, (1/s). ns for meas time range

        with open(settings['Input/Output Settings']['Input file/folder']) as file:
            # determine measurement time range, in input units
            rangeStart = settings['CohnAlpha Settings']['Meas time range'][0] * 1e-9 * 1e6
            # rangeStart = settings['CohnAlpha Settings']['Meas time range'][0] * 1e-9 / settings['General Settings']['Input time units']
            # rangeEnd = settings['CohnAlpha Settings']['Meas time range'][1] * 1e-9 / settings['General Settings']['Input time units']
            rangeEnd = settings['CohnAlpha Settings']['Meas time range'][1] * 1e-9 *1e6

            # find start of time stamps to analyze
            readIn = float(file.readline())
            while readIn < rangeStart:
                readIn = float(file.readline())

            # initialize segment bounds
            segment = []
            segmentStart = rangeStart
            segmentEnd = segmentStart + segmentLength
            rollover = [readIn]
            chunk = []

            while True:
                chunk = rollover
                rollover = []
                temp = file.readlines(nperseg)
                temp = [float(line) for line in temp]
                # if no more data to read, break the loop
                if not temp: 
                    break
                chunk += temp


                # if we have read to or past the segment end, parse out current segment and compute
                if chunk[-1] >= segmentEnd:
                    segmentRange = np.array([segmentStart, segmentEnd])
                    index = bisect.bisect(chunk, segmentEnd)
                    rollover = chunk[index:]
                    segment += chunk[:index]
                    if segment == []:
                        continue
                        
                    numSegments += 1
                    fft = self.memcontrolCompute(settings, segment, nperseg, segmentRange)
                    if fftSum == []:
                        fftSum = fft
                    else:
                        fftSum += fft

                    print("fft:")
                    print(fftSum)
                    # update segment bounds for next segment
                    segmentStart = (segmentStart + segmentEnd) / 2 # hardcoded 50% overlap
                    segmentEnd = segmentStart + segmentLength
                    # update starting segment from overlap
                    index = bisect.bisect(segment, segmentStart)
                    segment = segment[index:]
                    # if settings['General Settings']['Show plots']:
                    # self.plot_ca(x=fft, y=edges, method='scatter', settings=settings)
                
                # if we have read past the meas time range, parse out portion within the range and exit
                elif chunk[-1] >= rangeEnd:
                    segmentRange = np.array([segmentStart, segmentEnd])
                    index = bisect.bisect(chunk, rangeEnd)
                    segment += chunk[:index]
                    if segment == []:
                        continue

                    numSegments += 1
                    fft, edges = self.memcontrolCompute(settings, segment, nperseg, segmentRange)
                    if fftSum == []:
                        fftSum = fft
                    else:
                        fftSum += fft
                    break
                # otherwise, continue reading TODO: clean up logic
                else:
                    segment += chunk
                    continue

                '''# Split the chunk into lines
                lines = chunk.splitlines()

                # convert string lines to floats, then to ns
                segmentData = np.array([float(line) for line in lines]) * 1e3

                # clear out data after use?
                segmentData = None
                if histogram is None:
                    histogram = counts
                    edges_seconds = edges_ns / 1e9
                    edges_seconds = edges_seconds[:-1]
                else:
                    histogram += counts'''
        print(f"fftSum {fftSum}")
        fftMean = fftSum / numSegments
        print(fftMean)
        # # Plotting
        # if settings['General Settings']['Show plots']:
        #     self.plot_ca(x=edges_seconds,y=histogram, method='hist', settings=settings)

        '''  # Creating evenly spaced start and stop endpoint for plotting
        # Calculating power spectral density distribution from counts over time hist (Get frequency of counts samples)
        timeline = np.linspace(start=self.meas_time_range[0], 
                            stop=self.meas_time_range[1],
                            num=int(count_bins))/1e9
        self.fs = 1 / (timeline[3]-timeline[2])'''
        
    
    def memcontrolCompute(self, settings, segment, nperseg, segmentRange):
        # convert segment from us into s
        array = np.array(segment)
        array = array / 1e6
        segmentRange = np.array(segmentRange)
        segmentRange /= 1e6

        # compute hist of segment
        hist, edges_input = np.histogram(a=array,
                                        bins=nperseg,
                                        range=segmentRange)
        edges_seconds = edges_input #* settings['General Settings']['Input time units']
        edges_seconds = edges_seconds[:-1]

        # self.plot_ca(x=edges_seconds,y=hist, method='hist', settings=settings)
        
        # win = signal.get_window('boxcar', nperseg)
        # segmentsX = hist * win

        # fft
        # TODO: inverse seconds
        fft = np.fft.rfft(np.array(hist), axis=0)
        squaredModulus = np.abs(fft) ** 2
        return squaredModulus

    def fitCohnAlpha(self, settings: dict = {}, settingsPath:str = './settings/default.json', showSubPlots:bool = False):

        '''
        Fits Power Spectral Density onto provided scatterplot
        Saving and showing the graph can be turned on or off in the settings
        Visual Settings can also be adjusted in the settings

        Inputs:
            - self: all the private variables in PowerSpectralDensity() object
            - settings: the current user runtime settings
            - showSubPlots: if higher-order function (e.g. fitCohnAlpha) would like to display plots
                Mainly done for quicker debugging

            
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
        importResults = hdf5.readHDF5Data(path=['CohnAlpha', 'Fit'],
                                        settings=settings,
                                        settingsName=settingsPath,
                                        fileName='pynoise')
        
        # If existing data does not exist and showSubPlots is false
        # import data from disk
        if importResults is not None:
            data = importResults['graphData']
            f = data[:, 0]
            Pxx = data[:, 1]
            residuals = importResults['residuals']
            popt = importResults['popt']
            alpha = importResults['alpha_uncertainty'][0]
            uncertainty = importResults['alpha_uncertainty'][1]

        # otherwise re-calculate data and re-plot histogram + scatterplot
        # Fitting distribution with expected equation
        else:
            showSubPlots = False
            f, Pxx = self.welchApproxFourierTrans(settings=settings, settingsPath=settingsPath, showSubPlots=True)
            # Ignore start & end points that are incorrect due to welch endpoint assumptions
            popt, pcov = curve_fit(CAFit,
                                f[1:-2],
                                Pxx[1:-2],
                                p0=[Pxx[2], 25, 0.001],
                                bounds=(0, np.inf),
                                maxfev=100000)
            
            alpha = np.around(popt[1]*2*np.pi, decimals=2)
            uncertainty = np.around(pcov[1,1]*2*np.pi, decimals=2)
            residuals = ((CAFit(f[1:-2], *popt) - Pxx[1:-2]) / Pxx[1:-2]) * 100
        
        # separate if block to prevent plotting scatter plot twice
        if showSubPlots:
            self.welchApproxFourierTrans(settings=settings, settingsPath=settingsPath, showSubPlots=True)

        # plots the graph
        # will call fit() as well to fit the curve
        # plot() will return the dict containing popt, alpha, uncertainty
        if settings['General Settings']['Show plots']:
            kwDict = {'popt': popt,
                      'alpha': alpha,
                      'uncertainty': uncertainty}
            self.plot_ca(x=f, y=Pxx, residuals=residuals, method='fit', settings=settings, **kwDict)

        # Saving raw data
        if settings['Input/Output Settings']['Save outputs']:
            data = np.array([f, Pxx]).T
            alpha_uncertainty = np.array([alpha, uncertainty])
            hdf5.writeHDF5Data(npArrays=[data, residuals, popt, alpha_uncertainty],
                               keys=['graphData', 'residuals', 'popt', 'alpha_uncertainty'],
                               path=['CohnAlpha', 'Fit'],
                               settings=settings,
                               settingsName=settingsPath,
                               fileName='pynoise')

        return popt, alpha, uncertainty


    def print(self, message):

        '''
        Self-defined print function
        Will print if quiet mode is set to false, otherwise prints nothing
        '''

        if self.quiet:
            return
        print(message)


    def plot_ca(self, x, y, residuals = None, method:str = '', settings:dict = {}, **kwargs):

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

        # small data manipulation, makes code cleaner
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
        # change scaling of x-axis to log scaling + plot points
        # update limit of x-axis
        else:
            # if is_mem:
            #     ax[0].semilogx(x[2:-2], y[2:-2], label="APSD (scaled)")
            # else:
            ax[0].semilogx(x[1:-2], y[1:-2], '.', **settings['Semilog Plot Settings'])
            ax[0].set_xlim([1, 200])


            # if fitting, then call fit() and fit curve
            # use kwargs to pass popt, alpha, uncertainty
            if method == 'fit':
                self.fit_ca(x=x,
                            y=y,
                            residuals=residuals,
                            ax=ax,
                            popt=kwargs['popt'],
                            alpha=kwargs['alpha'],
                            uncertainty=kwargs['uncertainty'],
                            settings=settings)


        # Saving figure
        # file name: CA_[method]_[freq min]_[freq_max]_[time units].png
        # TODO: start to use settings and time units setting, currently hard coding in seconds
        # NOTE: if saving figure and showing plot: must first save plot, otherwise matplotlib saves a blank plot
        if settings['Input/Output Settings']['Save figures']:
            # reduce padding in the figure
            fig.tight_layout()
            absPath = os.path.abspath(settings['Input/Output Settings']['Save directory'])
            inputFileName = Path(settings['Input/Output Settings']['Input file/folder']).stem
            save_img_filename = os.path.join(absPath, 'CA_' + method + '_' + inputFileName + '.png')
            pyplot.savefig(save_img_filename, dpi=300, bbox_inches='tight')
            self.print('Image saved at ' + save_img_filename)

        # plot and show graph
        # close graph after showing graph
        self.print("Plotting...")
        pyplot.show()
        pyplot.close()



    def fit_ca(self, x, y, residuals, ax, popt = None, alpha = None, uncertainty = None, settings:dict = {}):

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

        # Display Alpha and Uncertainty values, store within Welch Approx
        self.print('alpha = ' + str(alpha) + ', uncertainty = '+ 
                    str(uncertainty))
        
        
        ax[0].semilogx(x[1:-2], CAFit(x[1:-2], *popt), **settings['Line Fitting Settings'])                
        ax[0].legend(loc='upper right')
        
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

        # plot residuals
        # label axis
        ax[1].scatter(x[1:-2], residuals, **settings['Scatter Plot Settings'])
        ax[1].axhline(y=0, color='#162F65', linestyle='--')
        ax[1].set_xlabel('Frequency(Hz)')
        ax[1].set_ylabel('Percent difference (%)')



    # TODO: a different method of Cohn-Alpha
    # Need to use sub-functions to also work with this alternate method
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

#TODO: swap
        f, Pxy = testing.CPSD(
        # f, Pxy = signal.csd(
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
        pyplot.show()

        return f, Pxy, popt, pcov
# ---------------------------------------------------------------------------------------------------

    def create_time_domain_signal(self,
                                  timestamps, 
                                  nperseg, 
                                  segment_start,
                                  sampling_rate):
        """
        Converts a list of timestamps to a time-domain signal.

        Parameters:
        - timestamps (list of floats): List of timestamp data in microseconds.
        - sampling_rate (float): Sampling rate in Hz (samples per second).

        Returns:
        - signal (np.array): Time-domain signal of bin counts per sampling 
        interval.
        """
        
        signal = np.zeros(nperseg)
        
        timestamps = np.array(timestamps) - segment_start
        for ts in timestamps:
            index = int(np.floor((ts/1e6) * sampling_rate))
            if index < nperseg:
                signal[index] += 1  # Increment count in the corresponding time bin

        return signal


    def process_file_with_windowing(self, settings, window_type='boxcar'):
        """
        Processes timestamp data in segments, applies windowing before FFT, and computes APSD for each segment.

        Parameters:
        - settings
        - window_type (str): Windowing type for FFT (default is 'boxcar').

        Returns:
        - freqs (np.array): Frequencies corresponding to the APSD.
        - apsd_sum (np.array): Cumulative APSD for all segments.
        """

        overlap_fraction = 50e-2 # Fractional overlap of adjacent segments
        dwell_time = 1 / (2 * settings['CohnAlpha Settings']['Frequency Maximum']) # in seconds
        nperseg = int(1 / (dwell_time * settings['CohnAlpha Settings']['Frequency Minimum']))
        sampling_rate = (dwell_time)**(-1)   # Sampling rate in Hz
        segment_length = dwell_time * nperseg   # Length of each segment in seconds
        segment_length *= 1e6 # convert to microseconds
        start_time = settings['CohnAlpha Settings']['Meas time range'][0] / 1e9 # seconds

        segment = []
        segment_start = start_time*1e6  # Start time of the current segment in microseconds
        segment_end = segment_start + segment_length 

        # apsd_sum = None
        fft_sum = None
        freqs = np.fft.rfftfreq(nperseg, d=1/sampling_rate)
        num_segments = 0
        
        self.print("Reading in input file/folder data...")

        with open(settings['Input/Output Settings']['Input file/folder'], 'r') as file:
            for line in file:
                timestamp = float(line.strip())
                
                # Collect timestamps for the current segment
                if segment_start <= timestamp < segment_end:
                    segment.append(timestamp)
                elif timestamp >= segment_end:
                    # Process the current segment if it has data
                    if segment:
                        # Convert timestamps to a time-domain signal
                        time_domain_signal = \
                            self.create_time_domain_signal(segment, 
                                                    nperseg,
                                                    segment_start,
                                                    sampling_rate)
                        
                        # Apply windowing
                        window = signal.get_window(window_type, 
                                                        len(time_domain_signal))
                        windowed_signal = time_domain_signal * window
                        
                        # Compute APSD using Welch's method
                        # f, apsd = signal.welch(windowed_signal, 
                        #                             fs=sampling_rate, 
                        #                             nperseg=nperseg)
                        squared_modulus = np.fft.rfft(time_domain_signal)
                        squared_modulus = np.abs(squared_modulus) ** 2
                        
                        # Accumulate APSD and frequencies
                        # if apsd_sum is None:
                        if fft_sum is None:
                            num_segments += 1
                            # apsd_sum = apsd
                            # freqs = f
                            fft_sum = squared_modulus
                        else:
                            num_segments += 1
                            fft_sum += squared_modulus
                            # apsd_sum += apsd
                    
                    # Reset for the next segment with overlap
                    overlap = int(segment_length *
                            overlap_fraction)  # Calculate overlap in microseconds
                    segment_start = segment_end - overlap
                    segment_end = segment_start + segment_length
                    segment = [timestamp for timestamp in segment if timestamp >= segment_start]
                    segment.append(timestamp)

        # apsd_sum = np.abs(apsd_sum)
        window = signal.get_window(window_type, nperseg)
        scaled_apsd = (fft_sum / num_segments) / (np.sum(window**2) * sampling_rate)

        self.plot_ca(freqs, scaled_apsd, method='scatter', settings=settings)
        popt, pcov = curve_fit(CAFit,
                                freqs[1:-2],
                                scaled_apsd[1:-2],
                                p0=[scaled_apsd[2], 25, 0.001],
                                bounds=(0, np.inf),
                                maxfev=100000)
        alpha = np.around(popt[1]*2*np.pi, decimals=2)
        uncertainty = np.around(pcov[1,1]*2*np.pi, decimals=2)
        residuals = ((CAFit(freqs[1:-2], *popt) - scaled_apsd[1:-2]) / scaled_apsd[1:-2]) * 100
        kwDict = {'popt': popt,
                    'alpha': alpha,
                    'uncertainty': uncertainty}
        self.plot_ca(x=freqs, y=scaled_apsd, residuals=residuals, method='fit', settings=settings, **kwDict)
        













    def loadSegments(self, settings):
        '''
        loads a txt file by portions for memory control
        '''
        
        histogram = None
        edgesSeconds = None

        dwell_time = 1 / (2 * settings['CohnAlpha Settings']['Frequency Maximum'])
        dwell_time_ns = dwell_time * 1e9

        # Annotation Parameters
        self.annotate_font_weight = settings['CohnAlpha Settings']['Annotation Font Weight']
        self.annotate_color = settings['CohnAlpha Settings']['Annotation Color']
        self.annotate_background_color = settings['CohnAlpha Settings']['Annotation Background Color']
        self.annotate_font_size = settings['CohnAlpha Settings']['Font Size']

        # lines = look at final time stamp + total num of lines -> load % of lines associated with a segment
        # segment = nperseg * dwell time 
        count_bins = np.diff(self.meas_time_range) / dwell_time_ns
        with open(settings['Input/Output Settings']['Input file/folder']) as file:
            while True:
                # TODO: change? make a setting?
                numBytes = 1000
                lines = file.readline(numBytes)
                if not lines:
                    break
                segmentData = np.array([float(line.strip()) for line in lines if line.strip()])
                counts, edges_ns = np.histogram(segmentData, bins=int(count_bins), range=[0, self.reset_time])
                if histogram is None:
                    histogram = counts
                    edges_seconds = edges_ns / 1e9
                    edges_seconds = edges_seconds[:-1]
                else:
                    histogram += counts
        return edges_seconds, histogram