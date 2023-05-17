import numpy as np  # For processing data

"""
Rossi_alpha_settings = dict([('reset time', 2e3), ('bin width', 2),
                             ('minimum cutoff', 25), ('fit range', [0, 2e3]),
                             ('plot scale', 'linear'), 
                             ('time difference method', 
                              'any-and-all'), ('digital delay', 750),
                             ('number of folders', 61),
                             ('meas time per folder', 60)])
"""

class timeDifCalcs:
    
    def __init__(self, list_data, general_settings, generating_hist_settings):
        self.time_vector = list_data
        self.list_data = list_data
        self.reset_time = float(generating_hist_settings["reset time"])
        self.timeDifs = None
        self.method = general_settings["time difference method"]
        self.digital_delay = general_settings["digital delay"]
    
    def calculate_time_differences(self):
        #time_vector = self.list_data

        #reset_time = float(Rossi_alpha_settings["reset time"])

        if self.method == "any_and_all":
            self.time_diffs = self.any_and_all_time_differences()
        elif (self.method["time difference method"] == "any-and-all cross-correlations"
        ):
            channels = self.list_data[:, 0]
            self.time_vector = list_datatime_diffs = self.any_and_all_cross_correlation_time_differences(channels)

        elif (self.method == "any-and-all cross-correlations no-repeat"):
            channels = self.list_data[:, 0]
            self.time_vector = list_datatime_diffs = self.any_and_all_cross_correlation_no_repeat_time_differences(channels)

        elif (self.method == "any-and-all cross-correlations no-repeat digital-delay"):
            channels = self.list_data[:, 0]
            self.time_vector = list_datatime_diffs = self.any_and_all_cross_correlation_no_repeat_digital_delay_time_differences(channels)
            
        else:
            print()
            print(self.method)
            print("This time difference method requested is either mistyped or")
            print("has not been programmed. The current available options are:")
            print()
            print("any_and_all")
            print("any-and-all cross-correlations")
            print("any-and-all cross-correlations no-repeat")
            print("any-and-all cross-correlations no-repeat digital-delay")
            print()

        return self.time_diffs


    def any_and_all_time_differences(self):
        time_diffs = np.array([])
        n = len(self.time_vector)
        for i in range(n):
            for j in range(i + 1, n):
                if self.time_vector[j] - self.time_vector[i] > self.reset_time:
                    break
                time_diffs = np.append(time_diffs,(self.time_vector[j] - self.time_vector[i]))

        return time_diffs


    def any_and_all_cross_correlation_time_differences(self, channels):
        time_diffs = np.array([])
        n = len(self.time_vector)
        for i in range(n):
            for j in range(i + 1, n):
                if channels[j] != channels[i]:
                    if self.time_vector[j] - self.time_vector[i] > self.reset_time:
                        break
                    time_diffs.append(self.time_vector[j] - self.time_vector[i])
        return time_diffs


    def any_and_all_cross_correlation_no_repeat_time_differences(self, channels):
        time_diffs = np.array([])
        for i in range(len(self.time_vector)):
            ch_bank = []
            for j in range(i + 1, len(self.time_vector)):
                if channels[j] - channels[i] != 0:
                    if self.time_vector[j] - self.time_vector[i] > self.reset_time:
                        break
                    elif sum(ch_bank - channels[j] == 0) == 0:
                        time_diffs.append(self.time_vector[j] - self.time_vector[i])
                    ch_bank.append(channels[j])
        return time_diffs


    def any_and_all_cross_correlation_no_repeat_digital_delay_time_differences(self, channels):
        time_diffs = np.array([])
        i = 0
        while i < len(self.time_vector):
            ch_bank = []
            for j in range(i + 1, len(self.time_vector)):
                if channels[j] - channels[i] != 0:
                    if self.time_vector[j] - self.time_vector[i] > self.reset_time:
                        break
                    elif sum(ch_bank - channels[j] == 0) == 0:
                        time_diffs.append(self.time_vector[j] - self.time_vector[i])
                    else:
                        stamped_time = self.time_vector[i]
                        while self.time_vector[i] < stamped_time + self.digital_delay:
                            i = i + 1
                    ch_bank.append(channels[j])
            i = i + 1
        return time_diffs
