import os
import numpy as np
from .timeDifs import timeDifCalcs
from .plots import RossiHistogram
from .fitting import RossiHistogramFit
from Event import Event
from Event import createEventsListFromTxtFile
# --------------------------------------------------------------------------------
def replace_zeroes(lst: list):
    non_zero_elements = [x for x in lst if x != 0]
    average = sum(non_zero_elements) / len(non_zero_elements)

    for i in range(len(lst)):
        if lst[i] == 0:
            lst[i] = average

    return lst

def compile_sample_stdev_RA_dist(settings: dict):
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
  
                events = createEventsListFromTxtFile(path_to_data,settings['Input/Output Settings']['Time Column'], settings['Input/Output Settings']['Channels Column'])

                if settings['General Settings']['Sort data'] == True:
                    events.sort(key=lambda Event: Event.time)

                thisData = timeDifCalcs(events,settings['RossiAlpha Settings']['Histogram Generation Settings']['Reset time'], 
                                        settings['RossiAlpha Settings']['Time difference method'], 
                                        settings['RossiAlpha Settings']['Digital delay'])
                if(settings['RossiAlpha Settings']['Combine Calc and Binning']):
                    thisPlot, counts, bin_centers, bin_edges   = thisData.calculateTimeDifsAndBin( settings['RossiAlpha Settings']['Histogram Generation Settings']['Bin width'], False, False, settings['Input/Output Settings']['Save directory'], settings['Histogram Visual Settings'])

                else:
                    time_diffs = thisData.calculateTimeDifsFromEvents()

                    thisPlot = RossiHistogram(time_diffs,settings['RossiAlpha Settings']['Histogram Generation Settings']['Bin width'],settings['RossiAlpha Settings']['Histogram Generation Settings']['Reset time'])



                    counts, bin_centers, bin_edges = thisPlot.plot(save_fig=settings['General Settings']['Save figures'], show_plot=settings['General Settings']['Show plots'], save_dir = settings['Input/Output Settings']['Save directory'], plot_opts = settings['Histogram Visual Settings'])



                if i == 1:
                    RA_hist_array = counts
                else:
                    RA_hist_array = np.vstack((RA_hist_array, counts))
                save_dir = data_folder + "/" + str(fol_num)
                thisFit = RossiHistogramFit(counts, bin_centers, settings['RossiAlpha Settings']['Fit Region Settings']['Minimum cutoff'], settings['RossiAlpha Settings']['Time difference method'], settings['General Settings']['Fit range'])




                thisFit.fit_and_residual(settings['General Settings']['Save figures'], save_dir, settings['General Settings']['Show plots'],settings['Line Fitting Settings'], settings['Residual Plot Settings'],settings['Histogram Visual Settings'], folder_index=i)

                i = i + 1
                break

    RA_std_dev = np.std(RA_hist_array, axis=0, ddof=1)
    RA_hist_total = np.sum(RA_hist_array, axis=0)

    time_diff_centers = bin_edges[1:] - np.diff(bin_edges[:2]) / 2
    uncertainties = RA_std_dev * num_folders
    uncertainties = replace_zeroes(uncertainties)
    RA_hist_total = np.vstack((RA_hist_total, time_diff_centers,uncertainties))
     
    return RA_hist_total
