'''The class for constructing and calculating time 
difference objects for RossiAlpha analysis. Supports 
separated and combined histogram/time difference operations.'''



# Necessary imports.
import numpy as np
from . import plots as plt
from Event import Event



class timeDifCalcs:
    
    '''The tiem differences object that stores 
    events and calculates time differences.'''

    def __init__(self, events: list[Event], reset_time: float = None, method: str = 'any_and_all', digital_delay: int = None):
        
        '''Initializes a time difference object. Autogenerates variables where necessary.
    
        Inputs:
        - events: the list of measurement times for each data point.
        - digital_delay: the amount of digital delay, if 
        applicable. Only required when using the any_and_all 
        cross_correlations no_repeat digital_delay method.
        - reset_time: the maximum time difference allowed. If 
        not given, will autogenerate the best reset time.
        - method: the method of calculating time 
        differences (assumes any_and_all).'''
        

        # Store events as a list.
        self.events = events
        # If a reset time is given, use it.
        if reset_time != None:
            self.reset_time = float(reset_time)
        # Otherwise, generate one.
        else:
            self.reset_time = events[-1].time - events[0].time
        # Store the method of analysis.
        self.method = method
        # When considering digital delay, store given digital delay.
        if self.method == 'any_and_all cross_correlations no_repeat digital_delay':
            self.digital_delay = digital_delay
        # Initialize the blank time differences.
        self.timeDifs = None



    def calculateTimeDifsFromEvents(self):

        '''Returns and stores the array of time differences used 
        for constructing a histogram based on the stored method.

        Outputs:
        - the calculated time differences.'''


        # Construct the empty time differences array, store the total 
        # number of data points, and initialize the indexing variable.
        time_diffs = np.array([])
        n = len(self.events)
        i = 0
        # Iterate through the whole time vector.
        while i < len(self.events):
            # Create an empty channel bank.
            ch_bank = set()
            # Iterate through the rest of the vector
            # starting 1 after the current data point.
            for j in range(i + 1, n):
                # If the current time difference exceeds the 
                # reset time range, break to the next data point.
                if self.events[j].time - self.events[i].time > self.reset_time:
                    break
                # If the method is any and all, continue. Otherwise, assure 
                # that the channels are different between the two data points.
                if((self.method == 'any_and_all') or self.events[j].channel != self.events[i].channel):
                    # If the method is any and all or cross_correlation, continue. Otherwise, 
                    # check that the current data point's channel is not in the bank.
                    if(self.method == 'any_and_all' or 
                       self.method == 'any_and_all cross_correlations' or 
                       self.events[j].channel not in ch_bank):
                        # Add the current time difference to the list.
                        time_diffs = np.append(time_diffs,(self.events[j].time - self.events[i].time))
                    # If digital delay is on:
                    elif(self.method == 'any_and_all cross_correlations no_repeat digital_delay'):
                        # Skip to the nearest data point after the
                        # current one with the digital delay added.
                        stamped_time = self.events[i].time
                        while self.events[i].time < stamped_time + self.digital_delay:
                           i += 1
                    # Add the current channel to the channel bank if considering channels.
                    if(self.method != "any_and_all"):
                        ch_bank.add(self.events[j].channel)
            # Iterate to the next data point without double counting for digital delay.
            if self.method != 'any_and_all cross_correlations no_repeat digital_delay':
                i += 1
        # Store the time differences array.
        self.timeDifs = time_diffs
        # Return the time differences array.
        return self.timeDifs
    


    def calculateTimeDifsAndBin(self, 
                                bin_width:int = None, 
                                save_fig:bool = False, 
                                show_plot:bool = True, 
                                save_dir:str= './', 
                                plot_opts:dict = None, 
                                folder:bool = False, 
                                verbose:bool = False):
        
        '''Simultaneously calculates the time differences for 
        the timeDifs object and adds them to a new histogram.
        
        Inputs:
        - bin width: the width of each histogram bin. If 
        not given, will autogenerate a reasonable width.
        TODO: Actually do this.
        - save_fig: whether or not the figures should be saved 
        to the given directory after creation (assumes False).
        - show_plot: whether or not the figures should be 
        shown to the user upon creation (assumes True).
        - save_dir: if save_fig is True, what directory the figures 
        will be saved in (assumes the current working directory).
        - plot_opts: all the matplotlib plot parameters.
        - folder: whether or not this plot is for folder analysis.
        - verbose: whether or not folder analysis should output file results.
        
        Outputs:
        - RossiHistogram object
        - histogram: the list of counts for each histogram bin.
        - bin_centers: the time at the center of each bin.
        - bin_edges: the time on the edge of each bin.
        '''
        
        
        # Store the number of data points, the number of bins, 
        # and initialize the data point index and histogram array.
        n = len(self.events)
        i = 0
        num_bins = int(self.reset_time / bin_width)
        histogram = np.zeros(num_bins)
        # Iterate through the whole time vector.
        while i < len(self.events):
            # Create an empty channel bank.
            ch_bank = set()
            # Iterate through the rest of the vector
            # starting 1 after the current data point.
            for j in range(i + 1, n):
                # If the current time difference exceeds the 
                # reset time range, break to the next data point.
                if self.events[j].time - self.events[i].time > self.reset_time:
                    break
                # If the method is any and all, continue. Otherwise, assure 
                # that the channels are different between the two data points.
                if((self.method == 'any_and_all') or self.events[j].channel != self.events[i].channel):
                    # If the method is any and all or cross_correlation, continue. Otherwise, 
                    # check that the current data point's channel is not in the bank.
                    if(self.method == 'any_and_all' or self.method == 'any_and_all cross_correlations' or self.events[j].channel not in ch_bank):
                        # Store the current time difference.
                        thisDif = self.events[j].time - self.events[i].time
                        # Calculate the bin index for the current time difference.
                        binIndex = int((thisDif) / bin_width)
                        # If the calculated index is exactly at the end 
                        # of the time range, put it into the last bin.
                        if(binIndex == num_bins):
                            binIndex -= 1
                        # Increase the histogram count in the appropriate bin.
                        histogram[binIndex] += 1    
                    # If digital delay is on:
                    elif(self.method == 'any_and_all cross_correlations no_repeat digital_delay'):
                        # Skip to the nearest data point after the
                        # current one with the digital delay added.
                        stamped_time = self.events[i]
                        while self.events[i].time < stamped_time + self.digital_delay:
                           i += 1
                    # Add the current channel to the channel bank if considering channels.
                    if(self.method != "any_and_all"):
                        ch_bank.add(self.events[j].channel)
            # Iterate to the next data point.
            if self.method != 'any_and_all cross_correlations no_repeat digital_delay':
                i += 1
        # Normalize the histogram.
        bin_edges = np.linspace(0, self.reset_time, num_bins + 1)
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])
        # Constuct the rossiHistogram object and plot accordingly.
        rossiHistogram = plt.RossiHistogram(bin_width= bin_width, reset_time=self.reset_time)
        rossiHistogram.initFromHist(histogram,bin_centers,bin_edges)
        rossiHistogram.plotFromHist(plot_opts,save_fig,show_plot,save_dir,folder,verbose)
        # Return the rossiHistogram object and related NP arrays.
        return rossiHistogram, histogram, bin_centers, bin_edges