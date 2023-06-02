import sys
import numpy as np 
from scipy.optimize import curve_fit
import seaborn as sns
import analyzingFolders
from timeDifs import timeDifCalcs
from plots import RossiHistogram
from fitting import RossiHistogramFit
import matplotlib.pyplot as plt

def analyzeAllType1(settings):
    
    filePath = settings['Input/Output Settings']['Input file/folder']
    listData = np.loadtxt(filePath)
    if settings['General Settings']["Sort data?"]:
        listDataSorted = np.sort(listData)
    
    thisTimeDifCalc = timeDifCalcs(listDataSorted, settings['Histogram Generation Settings']["Reset time"],  settings['General Settings']["Time difference method"])
    time_diffs = thisTimeDifCalc.calculate_time_differences()

    thisPlot = RossiHistogram(settings['Histogram Generation Settings']['Reset time'], settings['Histogram Generation Settings']['Bin width'], settings['Histogram Visual Settings'], settings['Input/Output Settings']['Save directory'])

    counts, bin_centers, bin_edges = thisPlot.plot(time_diffs, save_fig=settings['General Settings']['Save figures?'], show_plot=settings['General Settings']['Show plots?'])
    thisFit = RossiHistogramFit(counts, bin_centers, settings)
        
    thisFit.fit_and_residual(save_every_fig=settings['General Settings']['Save figures?'], 
                                 show_plot=settings['General Settings']['Show plots?'])
    plt.close('all')
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
    plt.close('all')