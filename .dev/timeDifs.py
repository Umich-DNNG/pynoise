import numpy as np


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

        time_diffs = np.array([])
        n = len(self.time_vector)
        i = 0
        while i < len(self.time_vector):
            ch_bank = set()
            for j in range(i + 1, n):
                if self.time_vector[j] - self.time_vector[i] > self.reset_time:
                    break
                if((self.method == 'any_and_all') or self.channels[j] != self.channels[i]):
                    if(self.method == 'any_and_all' or self.method == 'any_and_all cross_correlations' or self.channels[j] not in ch_bank):
                        time_diffs = np.append(time_diffs,(self.time_vector[j] - self.time_vector[i]))
                    elif(self.method == 'any_and_all cross_correlations no_repeat digital_delay'):
                        stamped_time = self.time_vector[i]
                        while self.time_vector[i] < stamped_time + self.digital_delay:
                           i = i + 1
                    if(self.method != "any_and_all"):
                        ch_bank.add(self.channels[j])
            i = i + 1

        self.time_diffs = time_diffs
        
        return self.time_diffs