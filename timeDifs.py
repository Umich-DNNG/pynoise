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


def calculate_time_differences(list_data, Rossi_alpha_settings):
    time_vector = list_data

    reset_time = float(Rossi_alpha_settings["reset time"])

    if Rossi_alpha_settings["time difference method"] == "any_and_all":
        time_diffs = any_and_all_time_differences(time_vector, reset_time)
    elif (
        Rossi_alpha_settings["time difference method"]
        == "any-and-all cross-correlations"
    ):
        channels = list_data[:, 0]
        time_diffs = any_and_all_cross_correlation_time_differences(
            time_vector, channels, reset_time
        )

    elif (
        Rossi_alpha_settings["time difference method"]
        == "any-and-all cross-correlations no-repeat"
    ):
        channels = list_data[:, 0]
        time_diffs = any_and_all_cross_correlation_no_repeat_time_differences(
            time_vector, channels, reset_time
        )

    elif (
        Rossi_alpha_settings["time difference method"]
        == "any-and-all cross-correlations no-repeat digital-delay"
    ):
        channels = list_data[:, 0]
        time_diffs = (
            any_and_all_cross_correlation_no_repeat_digital_delay_time_differences(
                time_vector, channels, reset_time
            )
        )
    else:
        print()
        print(Rossi_alpha_settings["time difference method"])
        print("This time difference method requested is either mistyped or")
        print("has not been programmed. The current available options are:")
        print()
        print("any-and-all")
        print("any-and-all cross-correlations")
        print("any-and-all cross-correlations no-repeat")
        print("any-and-all cross-correlations no-repeat digital-delay")
        print()

    return time_diffs


def any_and_all_time_differences(time_vector, reset_time):
    time_diffs = np.array([])
    n = len(time_vector)
    for i in range(n):
        for j in range(i + 1, n):
            if time_vector[j] - time_vector[i] > reset_time:
                break
            time_diffs = np.append(time_diffs,(time_vector[j] - time_vector[i]))

    return time_diffs


def any_and_all_cross_correlation_time_differences(time_vector, channels, reset_time):
    time_diffs = np.array([])
    n = len(time_vector)
    for i in range(n):
        for j in range(i + 1, n):
            if channels[j] != channels[i]:
                if time_vector[j] - time_vector[i] > reset_time:
                    break
                time_diffs.append(time_vector[j] - time_vector[i])
    return time_diffs


def any_and_all_cross_correlation_no_repeat_time_differences(
    time_vector, channels, reset_time
):
    time_diffs = np.array([])
    for i in range(len(time_vector)):
        ch_bank = []
        for j in range(i + 1, len(time_vector)):
            if channels[j] - channels[i] != 0:
                if time_vector[j] - time_vector[i] > reset_time:
                    break
                elif sum(ch_bank - channels[j] == 0) == 0:
                    time_diffs.append(time_vector[j] - time_vector[i])
                ch_bank.append(channels[j])
    return time_diffs


def any_and_all_cross_correlation_no_repeat_digital_delay_time_differences(
    time_vector, channels, reset_time, Rossi_alpha_settings
):
    digital_delay = Rossi_alpha_settings["digital delay"]
    time_diffs = np.array([])
    i = 0
    while i < len(time_vector):
        ch_bank = []
        for j in range(i + 1, len(time_vector)):
            if channels[j] - channels[i] != 0:
                if time_vector[j] - time_vector[i] > reset_time:
                    break
                elif sum(ch_bank - channels[j] == 0) == 0:
                    time_diffs.append(time_vector[j] - time_vector[i])
                else:
                    stamped_time = time_vector[i]
                    while time_vector[i] < stamped_time + digital_delay:
                        i = i + 1
                ch_bank.append(channels[j])
        i = i + 1
    return time_diffs
