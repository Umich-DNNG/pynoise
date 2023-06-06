import os
import numpy as np
from .timeDifs import timeDifCalcs
from .plots import RossiHistogram
from .fitting import RossiHistogramFit

# --------------------------------------------------------------------------------
def replace_zeroes(lst):
    non_zero_elements = [x for x in lst if x != 0]
    average = sum(non_zero_elements) / len(non_zero_elements)

    for i in range(len(lst)):
        if lst[i] == 0:
            lst[i] = average

    return lst

def compile_sample_stdev_RA_dist(settings):
    '''
    Goes through folders in the specified folder path and finds the appropriate file to analyze
    calculates the time difference and constructs a histogram and fitting for each file
    compiles all of these folders finds the standard deviation and uncertainties
    
    Arguments: Settings object
    
    Outputs: RA_Hist_Total which contains three things:
    RA_Hist_Total[0] is the summed histogram from all of the folders 
    RA_Hist_Total[1] is the bin centers for the histogram
    RA_Hist_Total[2] is the uncertainties
    '''

    data_folder = settings['Input/Output Settings']['Input file/folder']
    num_folders = int(settings['General Settings']['Number of folders'])
    i = 1
    for fol_num in range(1, num_folders + 1):
        for filename in os.listdir(data_folder + "/" + str(fol_num)):
            if filename.endswith("n_allch.txt"):
                path_to_data = data_folder + "/" + str(fol_num) + "/" + filename
                list_data_n = np.loadtxt(path_to_data, delimiter=" ")

                if settings['General Settings']['Sort data'] == True:
                    list_data = list_data_n[:, 1]
                    sorted_indices = np.argsort(list_data)
                    list_data_n = list_data_n[sorted_indices]

                list_data = list_data_n[:, 1]
                channels = list_data_n[:,0]

                thisData = timeDifCalcs(list_data, 
                                        settings['Histogram Generation Settings']['Reset time'], 
                                        settings['RossiAlpha Settings']['Time difference method'], 
                                        settings['General Settings']['Digital delay'], 
                                        channels)
                
                time_diffs = thisData.calculate_time_differences()

                thisPlot = RossiHistogram(settings['Histogram Generation Settings']['Reset time'],
                                          settings['Histogram Generation Settings']['Bin width'],
                                          settings['Histogram Visual Settings'], 
                                          settings['Input/Output Settings']['Save directory'])

                counts, bin_centers, bin_edges = thisPlot.plot(time_diffs, 
                                                               save_fig=False, 
                                                               show_plot=False)

                if i == 1:
                    RA_hist_array = counts
                else:
                    RA_hist_array = np.vstack((RA_hist_array, counts))

                thisFit = RossiHistogramFit(counts,
                                            bin_centers,settings)

                thisFit.fit_and_residual(save_every_fig=settings['General Settings']['Save figures'], 
                                         show_plot=settings['General Settings']['Show plots'], 
                                         folder_index=i)

                i = i + 1
                break

    RA_std_dev = np.std(RA_hist_array, axis=0, ddof=1)
    RA_hist_total = np.sum(RA_hist_array, axis=0)

    time_diff_centers = bin_edges[1:] - np.diff(bin_edges[:2]) / 2
    uncertainties = RA_std_dev * num_folders
    uncertainties = replace_zeroes(uncertainties)
    RA_hist_total = np.vstack((RA_hist_total, time_diff_centers,uncertainties))
     
    return RA_hist_total
