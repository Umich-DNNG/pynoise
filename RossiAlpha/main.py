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
#import fitting
sns.set(rc={"figure.dpi": 350, "savefig.dpi": 350})
sns.set_style("ticks")
sns.set_context("talk", font_scale=0.8)



def main():
    # extracting settings and timestamps
    # settings = getSettings()
    # options = getOptions()
    current_path = os.path.realpath(__file__)
    import readInput
    from readInput import Settings
    theseSettings = readInput.readInput()
    import analyzingFolders

    if (theseSettings.io_file_info['file type'] == 1):
        file_path = os.path.join(os.path.dirname(current_path), theseSettings.io_file_info["input file"])
        list_data_n = np.loadtxt(file_path)
        
        # sorting timestamps to be fed into calculate_time_differences()
        if theseSettings.general_program_settings["sort data?"] == "yes":
            list_data_n = np.sort(list_data_n)
        # applying time differences function
        
        from timeDifs import timeDifCalcs
        thisTimeDifCalc = timeDifCalcs(list_data_n, theseSettings.generating_histogram_settings["reset time"], theseSettings.general_program_settings["time difference method"])
        time_diffs = thisTimeDifCalc.calculate_time_differences()


        # plotting the histogram plot
        from plots import RossiHistogram
        
        thisPlot = RossiHistogram(theseSettings.generating_histogram_settings, theseSettings.histogram_visual_settings, show_plot=True)

        counts, bin_centers, bin_edges = thisPlot.plot(time_diffs)

        # fitting curve to the histogramp plot
        from fitting import Fit
        thisFit = Fit(counts, bin_centers, theseSettings.generating_histogram_settings, 
                      theseSettings.line_fitting_settings, theseSettings.general_program_settings,
                      theseSettings.residual_plot_settings, theseSettings.histogram_visual_settings)
        
        thisFit.fit_and_residual()
        
    else:
        RA_hist_total = analyzingFolders.compile_sample_stdev_RA_dist(theseSettings)
        from fitting import Fit_With_Weighting
        thisWeightedFit = Fit_With_Weighting(RA_hist_total,theseSettings.generating_histogram_settings, 
                                             theseSettings.general_program_settings, theseSettings.line_fitting_settings, 
                                             theseSettings.residual_plot_settings)
        thisWeightedFit.fit_RA_hist_weighting()
        thisWeightedFit.plot_RA_and_fit()


if __name__ == "__main__":
    main()
# %%