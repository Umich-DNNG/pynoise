import numpy as np  # For processing data
from . import plots as plt

class timeDifCalcs:
    
    def __init__(self, time_data: list[float], reset_time: float = None, method: str = 'any_and_all', digital_delay: int = None, channels = None):
        
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
        - method: the method of calculating time differences (assumes any_and_all).'''
        
        # Store the raw time measurements.
        self.time_vector = time_data 
        # If a reset time is given, use it.
        if reset_time != None:
            self.reset_time = float(reset_time)
        # Otherwise, generate one.
        else:
            self.reset_time = max(time_data) - min(time_data)
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
        # If using channels, make a variable for it.
        if self.method != "any_and_all":
            self.channels = channels
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
                # If the method is any and all, there are no additional conditions, but if any other method, check that the channels are diff
                if((self.method == 'any_and_all') or self.channels[j] != self.channels[i]):
                    # if the method checks for repeats, check that it is not in the channels bank, otherwise we can add the time_diff
                    if(self.method == 'any_and_all' or self.method == 'any_and_all cross_correlations' or self.channels[j] not in ch_bank):
                        time_diffs = np.append(time_diffs,(self.time_vector[j] - self.time_vector[i]))
                    # If digital delay is on:
                    elif(self.method == 'any_and_all cross_correlations no_repeat digital_delay'):
                        # Skip to the nearest data point after the
                        # current one with the digital delay added.
                        stamped_time = self.time_vector[i]
                        while self.time_vector[i] < stamped_time + self.digital_delay:
                           i = i + 1
                    # Add the current channel to the channel bank if considering channels.
                    if(self.method != "any_and_all"):
                        ch_bank.add(self.channels[j])
            i = i + 1

        # Store the time differences array.
        self.timeDifs = time_diffs
        # Return the time differences array.
        return self.timeDifs
    

    def calculateTimeDifsAndBin(self, bin_width: int = None, save_fig: bool = False, show_plot: bool = True, save_dir:str= './', plot_opts: dict = None):
        '''can be called on a timeDifCalcs object and simultaneously calculates the time differences
        and adds them to a histogram.
        
        inputs:
        - bin width
        -save_fig
        -show_plot
        -save_dir
        -plot_opts
        
        outputs:
        RossiHistogram object'''
        
        #time_diffs = np.array([])
        n = len(self.time_vector)
        i = 0
        num_bins = int(self.reset_time / bin_width)
        histogram = np.zeros(num_bins)
        # iterate from 0 through the whole time vector
        while i < len(self.time_vector):
            ch_bank = set()
            # iterate through the rest of the vector starting 1 after i
            for j in range(i + 1, n):
                # if we get outside the reset_time range, break to the next iteratiion of i
                if self.time_vector[j] - self.time_vector[i] > self.reset_time:
                    break
                # if the method is any and all, there are no additional conditions, but if any other method, check that the channels are diff
                if((self.method == 'any_and_all') or self.channels[j] != self.channels[i]):
                    # if the method checks for repeats, check that it is not in the channels bank, otherwise we can add the time_diff
                    if(self.method == 'any_and_all' or self.method == 'any_and_all cross_correlations' or self.channels[j] not in ch_bank):
                        thisDif = self.time_vector[j] - self.time_vector[i]
                        #time_diffs = np.append(time_diffs,(thisDif))

                        binIndex = int((thisDif) / bin_width)
                        if(binIndex == num_bins):
                            binIndex -= 1
                        histogram[binIndex] += 1       
                    elif(self.method == 'any_and_all cross_correlations no_repeat digital_delay'):
                        # add the digital delay if digital delay is on
                        stamped_time = self.time_vector[i]
                        while self.time_vector[i] < stamped_time + self.digital_delay:
                           i = i + 1
                    # add the current channel to the channels set if considering channels
                    if(self.method != "any_and_all"):
                        ch_bank.add(self.channels[j])
            i = i + 1

        #Normalize the histogram
        bin_edges = np.linspace(0, self.reset_time, num_bins + 1)
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])
         # Saving plot (optional)
        rossiHistogram = plt.RossiHistogram(bin_width= bin_width, reset_time=self.reset_time)
        rossiHistogram.initFromHist(histogram,bin_centers,bin_edges)
        rossiHistogram.plotFromHist(plot_opts,save_fig,show_plot,save_dir)
        
        return rossiHistogram, histogram, bin_centers, bin_edges