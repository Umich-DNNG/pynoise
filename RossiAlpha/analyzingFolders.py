import os  # For scanning directories
import numpy as np
from timeDifs import timeDifCalcs
from plots import RossiHistogram
import fitting
import matplotlib.pyplot as plt  # For plotting data summaries

# --------------------------------------------------------------------------------
def replace_zeroes(lst):
    non_zero_elements = [x for x in lst if x != 0]
    average = sum(non_zero_elements) / len(non_zero_elements)

    for i in range(len(lst)):
        if lst[i] == 0:
            lst[i] = average

    return lst

def compile_sample_stdev_RA_dist(settings):
    '''goes through folders in the specified folder path and finds the appropriate file to analyze
    calculates the time difference and constructs a histogram and fitting for each file
    compiles all of these folders finds the standard deviation and uncertainties
    
    arguements: Settings object
    
    outputs: RA_Hist_Total which contains three things:
    RA_Hist_Total[0] is the summed histogram from all of the folders 
    RA_Hist_Total[1] is the bin centers for the histogram
    RA_Hist_Total[2] is the uncertainties'''

    data_folder = settings.io_file_info["input folder"]
    num_folders = int(settings.general_program_settings['number of folders'])
    i = 0
    for fol_num in range(1, num_folders + 1):
        for filename in os.listdir(data_folder + "/" + str(fol_num)):
            if filename.endswith("n_allch.txt"):
                path_to_data = data_folder + "/" + str(fol_num) + "/" + filename
                list_data_n = np.loadtxt(path_to_data, delimiter=" ")
                # list_data_n = np.genfromtxt(path_to_data, delimiter=' ')
                list_data = list_data_n[:, 1]
                channels = list_data_n[:,0]
                if settings.general_program_settings["sort data?"] == "yes":
                    list_data = np.sort(list_data)
                from timeDifs import timeDifCalcs

                thisData = timeDifCalcs(list_data, settings.generating_histogram_settings["reset time"], settings.general_program_settings["time difference method"], settings.general_program_settings["digital delay"], channels)
                
                if i == 0:
                    time_diffs = thisData.calculate_time_differences()

                    thisPlot = RossiHistogram(settings.generating_histogram_settings,
                                    settings.histogram_visual_settings, False)
                    
                    counts, bin_centers, bin_edges = thisPlot.plot(time_diffs)
                    RA_hist_array = counts

                    from fitting import Fit
                    thisFit = Fit(counts,bin_centers,settings.generating_histogram_settings,settings.line_fitting_settings, 
                                  settings.general_program_settings, settings.residual_plot_settings, settings.histogram_visual_settings)
                    popt = thisFit.fit_and_residual
                    popt_array = popt

                else:
                    time_diffs = thisData.calculate_time_differences()

                    thisPlot = RossiHistogram(settings.generating_histogram_settings,
                                    settings.histogram_visual_settings, False)
                    
                    counts, bin_centers, bin_edges = thisPlot.plot(time_diffs)

                    thisFit = Fit(counts,bin_centers,settings.generating_histogram_settings,settings.line_fitting_settings, 
                                  settings.general_program_settings, settings.residual_plot_settings, settings.histogram_visual_settings)

                    popt = thisFit.fit_and_residual()
                    RA_hist_array = np.vstack((RA_hist_array, counts))
                    # popt_array = np.vstack((popt_array, popt))

                i = i + 1
                break


    RA_std_dev = np.std(RA_hist_array, axis=0, ddof=1)
    RA_hist_total = np.sum(RA_hist_array, axis=0)

    time_diff_centers = bin_edges[1:] - np.diff(bin_edges[:2]) / 2
    uncertainties = RA_std_dev * num_folders
    uncertainties = replace_zeroes(uncertainties)
    RA_hist_total = np.vstack((RA_hist_total, time_diff_centers,uncertainties))
     
    return RA_hist_total
