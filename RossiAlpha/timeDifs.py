'''The class for constructing and calculating time difference objects for RossiAlpha 
analysis. Supports separated and combined histogram/time difference operations.'''

import numpy as np
from . import plots as plt
from Event import Event

class timeDifCalcs:
    
    def __init__(self, events, reset_time: float = None, method: str = 'any_and_all', digital_delay: int = None):
        
        '''Initializes a time difference object. Autogenerates variables where necessary.
    
        Requires:
        - time_data: the list of measurement times for each data point.
        - channels: the list of channels for each data point. The 
        indeces for each data point should match between time_data 
        and channels. ONLY required when method is not any_and_all.
        - digital_delay: the amount of digital delay. OtNLY 
        required when performing analysis with digital_delay.
        
        Optional:
        - reset_time: the maximum time difference allowed. If 
        not given, will autogenerate the best reset time.
        TODO: Actually do this.
        - method: the method of calculating time differences (assumes any_and_all).'''
        
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
        # For considering digital delay.
        if self.method == 'any_and_all cross_correlations no_repeat digital_delay':
            # If no digital delay is given, generate one.
            if digital_delay == None:
                #TODO: create a generated default for the data. The line below is a stand-in.
                self.digital_delay = digital_delay
            # Otherwise, use the given value.
            else:
                self.digital_delay = digital_delay
        
        # Initialize the blank time differences.
        self.timeDifs = None

    def calculate_time_differences(self):

        '''Returns and stores the array of time differences used 
        for constructing a histogram based on the stored method.

        Returns:
        - self.timeDifs
        '''

        # Construct the empty time differences array.
        time_diffs = np.array([])
        n = len(self.time_vector)
        i = 0
        # Iterate through the whole time vector.
        while i < len(self.time_vector):
            # Create an empty channel bank.
            ch_bank = set()
            # Iterate through the rest of the vector
            # starting 1 after the current data point.
            for j in range(i + 1, n):
                # If the current time difference exceeds the 
                # reset time range, break to the next data point.
                if self.time_vector[j] - self.time_vector[i] > self.reset_time:
                    break
                # If the method is any and all, continue. Otherwise, assure 
                # that the channels are different between the two data points.
                if((self.method == 'any_and_all') or self.channels[j] != self.channels[i]):
                    # If the method is any and all or cross_correlation, continue. Otherwise, 
                    # check that the current data point's channel is not in the bank.
                    if(self.method == 'any_and_all' or self.method == 'any_and_all cross_correlations' or self.channels[j] not in ch_bank):
                        # Add the current time difference to the list.
                        time_diffs = np.append(time_diffs,(self.time_vector[j] - self.time_vector[i]))
                    # If digital delay is on:
                    # TODO: why is it elif???
                    elif(self.method == 'any_and_all cross_correlations no_repeat digital_delay'):
                        # Skip to the nearest data point after the
                        # current one with the digital delay added.
                        stamped_time = self.time_vector[i]
                        while self.time_vector[i] < stamped_time + self.digital_delay:
                           i += 1
                    # Add the current channel to the channel bank if considering channels.
                    if(self.method != "any_and_all"):
                        ch_bank.add(self.channels[j])
            # Iterate to the next data point.
            # TODO: Should we still do this when using digital delay?
            i += 1
        # Store the time differences array.
        self.timeDifs = time_diffs
        # Return the time differences array.
        return self.timeDifs



    def calculateTimeDifsFromEvents(self):
        '''Returns and stores the array of time differences used 
        for constructing a histogram based on the stored method.

        Returns:
        - self.timeDifs
        '''

        time_diffs = np.array([])
        n = len(self.events)
        i = 0
        # iterate from 0 through the whole time vector
        while i < len(self.events):
            ch_bank = set()
            # iterate through the rest of the vector starting 1 after i

            for j in range(i + 1, n):

                # if we get outside the reset_time range, break to the next iteratiion of i
                if self.events[j].time - self.events[i].time > self.reset_time:
                    break
                # if the method is any and all, there are no additional conditions, but if any other method, check that the channels are diff
                if((self.method == 'any_and_all') or self.events[j].channel != self.events[i].channel):
                    # if the method checks for repeats, check that it is not in the channels bank, otherwise we can add the time_diff
                    if(self.method == 'any_and_all' or self.method == 'any_and_all cross_correlations' or self.events[j].channel not in ch_bank):
                        time_diffs = np.append(time_diffs,(self.events[j].time - self.events[i].time))
                    elif(self.method == 'any_and_all cross_correlations no_repeat digital_delay'):
                        # add the digital delay if digital delay is on
                        stamped_time = self.events[i].time
                        while self.events[i].time < stamped_time + self.digital_delay:
                           i = i + 1
                    # add the current channel to the channels set if considering channels
                    if(self.method != "any_and_all"):
                        ch_bank.add(self.events[j].channel)
            i = i + 1

        self.timeDifs = time_diffs
        return self.timeDifs
    
    def calculateTimeDifsAndBin(self, bin_width: int = None, save_fig: bool = False, show_plot: bool = True, save_dir:str= './', plot_opts: dict = None):
        
        '''Simultaneously calculates the time differences for 
        the timeDifs object and adds them to a new histogram.
        
        Optional:
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
        
        Returns:
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
                    # TODO: why is it elif???
                    elif(self.method == 'any_and_all cross_correlations no_repeat digital_delay'):
                        # Skip to the nearest data point after the
                        # current one with the digital delay added.
                        stamped_time = self.time_vector[i]
                        while self.events[i].time < stamped_time + self.digital_delay:
                           i += 1
                    # Add the current channel to the channel bank if considering channels.
                    if(self.method != "any_and_all"):
                        ch_bank.add(self.events[j].channel)
            # Iterate to the next data point.
            # TODO: Should we still do this when using digital delay?
            i += 1
        # Normalize the histogram.
        bin_edges = np.linspace(0, self.reset_time, num_bins + 1)
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])
        # Constuct the rossiHistogram object and plot accordingly.
        rossiHistogram = plt.RossiHistogram(bin_width= bin_width, reset_time=self.reset_time)
        rossiHistogram.initFromHist(histogram,bin_centers,bin_edges)
        rossiHistogram.plotFromHist(plot_opts,save_fig,show_plot,save_dir)
        # Return the rossiHistogram object and related NP arrays.
        return rossiHistogram, histogram, bin_centers, bin_edges