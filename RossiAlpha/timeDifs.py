import numpy as np  # For processing data
import matplotlib.pyplot as plt
from . import plots as plt
from Event import Event

class timeDifCalcs:
    
    def __init__(self, events, reset_time: float = None, method: str = 'any_and_all', digital_delay: int = None):
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
        



    def calculateTimeDifsFromEvents(self):
         # reset_time = float(Rossi_alpha_settings["reset time"])
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
    

    def calculate_time_differences(self):
        '''can be called on a timeDifCalcs object and returns the array of time differences used for constructing a histogram based on the appropriate method
        
        inputs:
        -None

        outputs:
        -time differences array
        '''

        # time_vector = self.list_data

        # reset_time = float(Rossi_alpha_settings["reset time"])
        time_diffs = np.array([])
        n = len(self.time_vector)
        i = 0
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
                        time_diffs = np.append(time_diffs,(self.time_vector[j] - self.time_vector[i]))
                    elif(self.method == 'any_and_all cross_correlations no_repeat digital_delay'):
                        # add the digital delay if digital delay is on
                        stamped_time = self.time_vector[i]
                        while self.time_vector[i] < stamped_time + self.digital_delay:
                           i = i + 1
                    # add the current channel to the channels set if considering channels
                    if(self.method != "any_and_all"):
                        ch_bank.add(self.channels[j])
            i = i + 1

        self.timeDifs = time_diffs
        return self.timeDifs
    

    def calculateTimeDifsAndBin(self, bin_width, save_fig: bool, show_plot: bool, save_dir: str, options: dict):
        '''can be called on a timeDifCalcs object and simultaneously calculates the time differences
        and adds them to a histogram.
        
        inputs:
        - bin width
        -save_fig
        -show_plot
        -save_dir
        -options
        
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
        rossiHistogram.plotFromHist(options,save_fig,show_plot,save_dir)
        
        return rossiHistogram, histogram, bin_centers, bin_edges