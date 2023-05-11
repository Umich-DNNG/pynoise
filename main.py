# %%
import sys

# # Define location of Git synchoronized Python functions
# # Add python functions folder to path
# sys.path.extend([python_scripts_path])

# from Data_structure import DataLoader # For building data file load structure

import numpy as np  # For processing data
import os  # For scanning directories
import matplotlib.pyplot as plt  # For plotting data summaries
from matplotlib.colors import LogNorm  # For adjusting colorbar scale

# from scipy.signal import find_peaks
from scipy.optimize import curve_fit
import copy
import seaborn as sns

sns.set(rc={"figure.dpi": 350, "savefig.dpi": 350})
sns.set_style("ticks")
sns.set_context("talk", font_scale=0.8)


# get the settings for the user to use
def getSettings():
    current_path = os.path.realpath(__file__)
    file_path = os.path.join(os.path.dirname(current_path), "Rossi_alpha_settings.txt")
    Rossi_alpha_settings = {}
    with open(file_path, "r") as file:
        for line in file:
            settingName = line.split(":")[0].strip()
            setting = line.split(":")[1].strip()
            if settingName == "fit range":
                setting = [float(s) for s in setting[1:-1].split(",")]
            Rossi_alpha_settings[settingName] = setting

    Rossi_alpha_settings["reset time"] = float(Rossi_alpha_settings["reset time"])
    Rossi_alpha_settings["bin width"] = int(Rossi_alpha_settings["bin width"])
    Rossi_alpha_settings["minimum cutoff"] = int(Rossi_alpha_settings["minimum cutoff"])
    Rossi_alpha_settings["digital delay"] = int(Rossi_alpha_settings["digital delay"])
    Rossi_alpha_settings["meas time per folder"] = int(
        Rossi_alpha_settings["meas time per folder"]
    )
    return Rossi_alpha_settings


def getOptions():
    current_path = os.path.realpath(__file__)
    file_path = os.path.join(os.path.dirname(current_path), "plotOptions.txt")
    plotOpts = {}
    with open(file_path, "r") as file:
        for line in file:
            settingName = line.split(":")[0].strip()
            setting = line.split(":")[1].strip()
            if setting.isdigit():
                setting = float(setting)
            plotOpts[settingName] = setting
    return plotOpts


def main():
    # extracting settings and timestamps
    # settings = getSettings()
    # options = getOptions()
    current_path = os.path.realpath(__file__)
    import readInput

    (
        io_file_info,
        general_program_settings,
        histogram_settings,
        line_fitting_settings,
        residual_plot_settings,
    ) = readInput.readInput()
    file_path = os.path.join(os.path.dirname(current_path), io_file_info["input file"])
    list_data_n = np.loadtxt(file_path)

    # sorting timestamps to be fed into calculate_time_differences()
    if general_program_settings["sort data?"] == "yes":
        list_data_n = np.sort(list_data_n)

    # applying time differences function
    import timeDifs

    time_diffs = timeDifs.calculate_time_differences(
        list_data_n, general_program_settings
    )

    # plotting the histogram plot
    from plots import Plot

    reset_time = general_program_settings["reset time"]
    bin_width = general_program_settings["bin width"]
    thisPlot = Plot(general_program_settings, histogram_settings)

    # counts, bin_centers = plots.plot(time_diffs, reset_time, bin_width, "Time Differences", "Count", "Histogram", options)
    counts, bin_centers = thisPlot.plot(time_diffs)

    # fitting curve to the histogramp plot
    import fitting

    line_y = fitting.fit(
        counts,
        bin_centers,
        "Time Differences",
        "Count",
        "Histogram w/ Fitted Line",
        line_fitting_settings,
    )

    fitting.residual_plot(counts, bin_centers, line_y, "Time Differences", "Residuals")


if __name__ == "__main__":
    main()
# %%
