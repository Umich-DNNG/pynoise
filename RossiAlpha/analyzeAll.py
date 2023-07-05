# %%
import sys
# # Define location of Git synchoronized Python functions
# # Add python functions folder to path
# sys.path.extend([python_scripts_path])
# from Data_structure import DataLoader # For building data file load structure
import numpy as np  # For processing data
from scipy.optimize import curve_fit
import seaborn as sns
from RossiAlpha import analyzingFolders
from .timeDifs import timeDifCalcs
from .plots import RossiHistogram
from .fitting import RossiHistogramFit
import matplotlib.pyplot as plt
from lmxReader import *
from Event import Event
from Event import createEventsListFromTxtFile
# sns.set(rc={"figure.dpi": 350, "savefig.dpi": 350})
# sns.set_style("ticks")
# sns.set_context("talk", font_scale=0.8)

def analyzeAllType1(settings: dict):
    #current_path = os.path.realpath(__file__)
    #theseSettings = readInput.readInput()
  
    
    filePath = settings['Input/Output Settings']['Input file/folder']

    if filePath.endswith(".txt"):
        listData = createEventsListFromTxtFile(filePath,settings['Input/Output Settings']['Time Column'], settings['Input/Output Settings']['Channels Column'])
    # sorting timestamps to be fed into calculate_time_differences()
    elif filePath.endswith(".lmx"):
        print("this is an lmx file. we are currently in testing stages for analyzing this file type.")
        listData = readLMXFile(filePath)

    
    
    if settings['General Settings']["Sort data"]:
        listData.sort(key=lambda Event: Event.time)

    # applying time differences function
    thisTimeDifCalc = timeDifCalcs(listDataSorted, settings['RossiAlpha Settings']["Reset time"],  settings['RossiAlpha Settings']["Time difference method"])

    if(not settings['RossiAlpha Settings']['Combine Calc and Binning']):
        time_diffs = thisTimeDifCalc.calculateTimeDifsFromEvents()

        # creating RossiHistogram() object with specified settings
        thisPlot = RossiHistogram(time_diffs,settings['RossiAlpha Settings']['Histogram Generation Settings']['Bin width'],settings['RossiAlpha Settings']['Histogram Generation Settings']['Reset time'])

        counts, bin_centers, bin_edges = thisPlot.plot(save_fig=settings['General Settings']['Save figures'], show_plot=settings['General Settings']['Show plots'], save_dir = settings['Input/Output Settings']['Save directory'], plot_opts = settings['Histogram Visual Settings'])


        
    #combined calculating time differences and binning them
    else:
        thisPlot, counts, bin_centers, bin_edges = thisTimeDifCalc.calculateTimeDifsAndBin(settings['RossiAlpha Settings']['Bin width'], settings['General Settings']['Save figures'], settings['General Settings']['Show plots'], settings['Input/Output Settings']['Save directory'], settings['Histogram Visual Settings'])
        time_diffs = None

    

    # creating Fit() object with specified settings
    thisFit = RossiHistogramFit(counts, bin_centers, settings['RossiAlpha Settings']['Fit Region Settings']['Minimum cutoff'], settings['RossiAlpha Settings']['Time difference method'], settings['General Settings']['Fit range'])
        
        # Fitting curve to the histogram and plotting the residuals
    thisFit.fit_and_residual(settings['General Settings']['Save figures'], settings['Input/Output Settings']['Save directory'], settings['General Settings']['Show plots'],settings['Line Fitting Settings'], settings['Residual Plot Settings'],settings['Histogram Visual Settings']  )
    plt.close('all')
    return time_diffs, thisPlot, thisFit
        


def analyzeAllType2(settings: dict):
    RA_hist_total = analyzingFolders.compile_sample_stdev_RA_dist(settings)
    from .fitting import Fit_With_Weighting
    thisWeightedFit = Fit_With_Weighting(RA_hist_total,settings['RossiAlpha Settings']['Minimum cutoff'], 
                                        settings['General Settings'],settings['Input/Output Settings']['Save directory'], settings['Line Fitting Settings'], 
                                        settings['Residual Plot Settings'])
    thisWeightedFit.fit_RA_hist_weighting()
    thisWeightedFit.plot_RA_and_fit(save_fig=settings['General Settings']['Save figures'], 
                                    show_plot=settings['General Settings']['Show plots'], errorBars = settings['RossiAlpha Settings']['Error Bar/Band'])
    plt.close('all')