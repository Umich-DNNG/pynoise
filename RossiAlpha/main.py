# %%
import sys
# # Define location of Git synchoronized Python functions
# # Add python functions folder to path
# sys.path.extend([python_scripts_path])
# from Data_structure import DataLoader # For building data file load structure
import numpy as np  # For processing data
from scipy.optimize import curve_fit
import seaborn as sns
import analyzingFolders
from timeDifs import timeDifCalcs
from plots import RossiHistogram
from fitting import RossiHistogramFit
# sns.set(rc={"figure.dpi": 350, "savefig.dpi": 350})
# sns.set_style("ticks")
# sns.set_context("talk", font_scale=0.8)

def analyzeAllType1(settings):
    #current_path = os.path.realpath(__file__)
    #theseSettings = readInput.readInput()

    
    filePath = settings['Input/Output Settings']['Input file/folder']
    listData = np.loadtxt(filePath)
    # sorting timestamps to be fed into calculate_time_differences()
    if settings['General Settings']["Sort data?"]:
        listDataSorted = np.sort(listData)
    
    # applying time differences function
    thisTimeDifCalc = timeDifCalcs(listDataSorted, settings['Histogram Generation Settings']["Reset time"],  settings['General Settings']["Time difference method"])
    time_diffs = thisTimeDifCalc.calculate_time_differences()

    # creating RossiHistogram() object with specified settings
    thisPlot = RossiHistogram(settings['Histogram Generation Settings']['Reset time'], settings['Histogram Generation Settings']['Bin width'], settings['Histogram Visual Settings'], settings['Input/Output Settings']['Save directory'])

    counts, bin_centers, bin_edges = thisPlot.plot(time_diffs, save_fig=settings['General Settings']['Save figures?'], show_plot=settings['General Settings']['Show plots?'])
    # creating Fit() object with specified settings
    thisFit = RossiHistogramFit(counts, bin_centers, settings)
        
        # Fitting curve to the histogram and plotting the residuals
    thisFit.fit_and_residual(save_every_fig=settings['General Settings']['Save figures?'], 
                                 show_plot=settings['General Settings']['Show plots?'])
    return time_diffs, thisPlot, thisFit
        


def analyzeAllType2(settings):
    RA_hist_total = analyzingFolders.compile_sample_stdev_RA_dist(settings)
    from fitting import Fit_With_Weighting
    thisWeightedFit = Fit_With_Weighting(RA_hist_total,settings['Histogram Generation Settings']['Minimum cutoff'], 
                                        settings['General Settings'],settings['Input/Output Settings']['Save directory'], settings['Line Fitting Settings'], 
                                        settings['Residual Plot Settings'])
    thisWeightedFit.fit_RA_hist_weighting()
    thisWeightedFit.plot_RA_and_fit(save_fig=settings['General Settings']['Save figures?'], 
                                    show_plot=False)

#
#if __name__ == "__main__":
#    main()
# %%