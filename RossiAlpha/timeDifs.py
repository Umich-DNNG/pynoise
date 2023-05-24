import numpy as np  # For processing data


class timeDifCalcs:
    
    def __init__(self, time_data, reset_time, method, digital_delay = None, channels = None):
        self.time_vector = time_data 
        self.reset_time = float(reset_time)
        self.method = method
        self.digital_delay = digital_delay
        self.channels = channels
        self.timeDifs = None
    
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

        self.time_diffs = time_diffs
        
        return self.time_diffs