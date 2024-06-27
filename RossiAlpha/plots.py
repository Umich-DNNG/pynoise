import numpy as np
import matplotlib.pyplot as plt
import os

import math
import tkinter as Tk
from . import analyze as td
from . import rossiAlpha as ra
import tqdm

# to allow for importing global files
import sys
ogPath = sys.path.copy()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)))
import analyze as globalAnalyze                      # to import functions used across all methods
sys.path = ogPath

plt.ioff()





def createPlot(timeDifs: dict,
                hist: dict,
                settings: dict,
                input:str,
                folder:bool = False):
    
    '''Create a Rossi Alpha histogram. Assumes 
    that time differences are already calculated.
    
    Inputs:
    - timeDifs: time difference being passed in from the storing calling class
    - hist: the dictionary containing histogram data; from the calling class
    - settings: dictionary holding the runtime settings
    - input: the name of the file
    - folder: whether or not this is for folder analysis.'''
    

    # Clear out the current histogram data.
    hist['Histogram'].clear()
    # Create a RossiHistogram object for each time difference.
    for time_dif in timeDifs['Time differences']:
        hist['Histogram'].append(RossiHistogram(time_dif, 
                                                settings['RossiAlpha Settings']['Bin width'], 
                                                settings['RossiAlpha Settings']['Reset time']))
    # Plot each histogram.
    for i in range(0, len(hist['Histogram'])):
        hist['Histogram'][i].plot(input, 
                                    timeDifs['Time difference method'][i], 
                                    settings['Input/Output Settings']['Save figures'], 
                                    settings['General Settings']['Show plots'], 
                                    settings['Input/Output Settings']['Save directory'], 
                                    settings['Histogram Visual Settings'],
                                    folder,
                                    settings['General Settings']['Verbose iterations'])
    # Store the current setting.
    hist['Bin width'] = settings['RossiAlpha Settings']['Bin width']


def calcUncertainty(hist: dict, total: list, numFolders: int):
    '''
    For a folder, calculates the uncertainty given the combined histogram data

    Inputs:
    - hist: dictionary holding histogram data from the class object. Will have uncertainty added to the object
    - total: list containing the histogram data to be used for uncertainty calculations
    - numFolders: int indicating the number of folders
    '''
    stdDev = []
    combinedData = []
    centers = []
    for i in range(0, len(total[-1])):
        # Compute the histogram standard deviation and total.
        stdDev.append(np.std(total[-1][i], axis=0, ddof=1))
        combinedData.append(np.sum(total[-1][i], axis=0))
        # Calculate the time difference centers.
        centers.append(hist['Histogram'][i].bin_edges[1:] - np.diff(hist['Histogram'][i].bin_edges[:2]) / 2)
        # Calculate the uncertainties and replace zeroes.
        hist['Uncertainty'].append(stdDev[i] * numFolders)
        hist['Uncertainty'][i] = globalAnalyze.replace_zeroes(hist['Uncertainty'][i])
        # Add the time difference centers and uncertainties to the total histogram.
        combinedData[i] = np.vstack((combinedData[i], centers[i], hist['Uncertainty'][i]))
    print(hist['Uncertainty'])
    return combinedData


def subfolderPlots(timeDifs: dict, hist: dict, settings: dict, numFolders: int):
    '''
    For a folder, computes the data for a subfolder and uncertainty data.

    Inputs:
    - timeDifs: dictionary holding the time difference data
    - hist: dictionary holding histogram data
    - settings: dictionary holding runtime settings
    - numFolders: int indicating the number of folders

    
    '''
    numHistograms = ra.getNumSets(settings)

    totalHist = []

    name = settings['Input/Output Settings']['Input file/folder']
    name = name[name[:name.rfind('/')].rfind('/')+1:].replace('/','-')
    for i in range(numHistograms):
        if isinstance(settings['RossiAlpha Settings']['Time difference method'], list):
            method = settings['RossiAlpha Settings']['Time difference method'][i]
        else:
            method = settings['RossiAlpha Settings']['Time difference method']
        # complete computations for each folder
        for folder in range(numFolders):
            hist['Histogram'].append(RossiHistogram(timeDifs['Time differences'][i][folder], 
                                                                settings['RossiAlpha Settings']['Bin width'], 
                                                                settings['RossiAlpha Settings']['Reset time']))

            if settings['General Settings']['Verbose iterations']:
                hist['Histogram'][0].plot((name + "-" + str(folder + 1)),
                                            method,
                                            settings['Input/Output Settings']['Save figures'], 
                                            settings['General Settings']['Show plots'], 
                                            settings['Input/Output Settings']['Save directory'], 
                                            settings['Histogram Visual Settings'], 
                                            True, 
                                            settings['General Settings']['Verbose iterations'])
                # export outputs in csv format
                if settings['Input/Output Settings']['Save outputs']:
                    begin, end = ra.computeBinEdges(hist) 
                    fileName = 'rossi_hist_' + name + '-' + str(folder + 1) + '_' + method + '_' + str(hist['Histogram'][folder].bin_width) + '_' + str(settings['RossiAlpha Settings']['Reset time'])
                    globalAnalyze.export({'Bin beginning': (begin,0),
                                        'Bin ending': (end,0),
                                        'Measured Count': (hist['Histogram'][0].counts,0)},
                                        [('Time difference method',method),
                                        ('Input file', (name + '/' + str(j + 1)))],
                                        fileName,
                                        settings['Input/Output Settings']['Save directory'])
            # if verbose iterations is not on, then "plot" to be able to retrieve the counts for the uncertainty calculations
            else:
                hist['Histogram'][0].plot((name + "-" + str(folder + 1)),
                                            method,
                                            False, 
                                            False, 
                                            settings['Input/Output Settings']['Save directory'], 
                                            settings['Histogram Visual Settings'], 
                                            True, 
                                            False)
            plt.close()
            # Create the  this is the first folder, initialize the histogram array.
            if folder == 1:
                for histogram in hist['Histogram']:
                    totalHist.append(histogram.counts)
            # Otherwise, add the counts to the histogram array.
            else:
                for j in range(0, len(hist['Histogram'])):
                    totalHist[j] = np.vstack((totalHist[j], hist['Histogram'][j].counts))
            hist['Histogram'].clear()
    totalHist = calcUncertainty(hist, totalHist, numFolders)
    return totalHist


def folderHistogram(timeDifs: dict, hist: dict, numFolders: int, settings: dict, window: Tk = None):
    '''Create a histogram for a folder input.

    Inputs: 
    - numFolders: int, number of folders to be analyzed.
    - settings: the dictionary containing all the runtime settings
    - window: the gui window, if in gui mode

    Outputs:
    - bool: true if successful, false otherwise
    '''
    numHistograms = ra.getNumSets(settings)
    
    ogWidth = settings['RossiAlpha Settings']['Bin width']

    # Get the name of the input.
    original = settings['Input/Output Settings']['Input file/folder']
    name = settings['Input/Output Settings']['Input file/folder']
    name = name[name[:name.rfind('/')].rfind('/')+1:].replace('/','-')
    

    # Restore the original folder pathway.
    settings['Input/Output Settings']['Input file/folder'] = original

    hist['Histogram'].clear()
    hist['Bin width'] = settings['RossiAlpha Settings']['Bin width']
    # compile subfolder data, including exporting if in verbose mode
    combined = subfolderPlots(timeDifs, hist, settings, numFolders)
    
    for i in range(0, len(combined)):
        hist['Histogram'].append(RossiHistogram(combined[i],
                                                settings['RossiAlpha Settings']['Bin width'],
                                                settings['RossiAlpha Settings']['Reset time']))
    # todo

    plt.close()
    # restore original bin width if it was changed--redundant if it was not
    settings['RossiAlpha Settings']['Bin width'] = ogWidth
    return True



class RossiHistogram:
    def __init__(self, time_diffs = None, bin_width: int = None, reset_time: int = None):

        '''
        Description:
            - Creating a Plot() object and its variables.

        Inputs:
            - time_diffs: If Histogram is being constructed from time_differences that still need to be binned, this arg should be provided
            - bin_width: If time_diffs still need to be binned, this arg should be provided
            - reset_time: If time_diffs still need to be binned, this arg should be provided

        Outputs: 
            - Plot() object
        '''
        #Data Variables
        self.time_diffs = time_diffs
        self.reset_time = reset_time
        self.bin_width = bin_width
        # Plotting options
        self.options = None
        self.save_dir = None
        
        # Required parameters
        self.reset_time = reset_time
        self.bin_width = bin_width
        self.x_axis = "Time Differences"
        self.y_axis = "Count"
        self.title = "Histogram Using "
        
        # Parameters set once plot(time_diffs) is called
        self.counts, self.bin_edges, self.bin_centers = None, None, None

    def plot(self, input: str, method: str = 'aa', save_fig: bool = False, show_plot: bool = True, save_dir:str= './',plot_opts: dict = None, folder: bool = False, verbose: bool = False, **kwargs ):
        

        '''
        Creating histogram from an array of time differences and plotting it.
        Saving and showing the plot can be turned on or off.

        Inputs:
            - self (all the private variables in Plot() object)
            - save_fig : True/False to save figure
            - show_plot : True/False to show plot in plot editor
            - save_dir : If save_fig = True, the save_dir must be provided. Default saves in current working directory
            - plot_opts: dictionary of histogram visual settings. 
            -**kwargs: If plot_opts is not inputed, you can input individual plot settings that you want to be applied to the plot 

        Outputs: 
            - counts (The set of values of the histogram as a list)
            - bin_centers (adjusted bin centers for visual plotting)
            - bin_edges (The edges of the bins are mentioned as a parameter)
        '''

        if plot_opts is None:
            plot_opts = {}
        plot_opts.update(kwargs)

        #TODO: Set defaults for the plot_opts if this dict is empty here.
        self.options = plot_opts
        self.save_dir = save_dir

        if (self.reset_time == None) :
            self.reset_time = np.max(self.time_diffs)

        # Calculating the number of bins
        num_bins = int(self.reset_time / self.bin_width)

        # Generating histogram
        counts, bin_edges = np.histogram(self.time_diffs, bins=num_bins, range=[0, self.reset_time])

        # Adjusting the bin centers
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])

        # Saving plot (optional)
        if save_fig and (not folder or verbose):

            # Plotting
            plt.figure()
            plt.bar(bin_centers, counts, width=0.8 * (bin_centers[1] - bin_centers[0]), **self.options)

            plt.xlabel(self.x_axis)
            plt.ylabel(self.y_axis)
            plt.title(self.title + method)

            plt.tight_layout()
            save_filename = os.path.join(self.save_dir, 'histogram_' + input + '_' + method + '.png')
            plt.savefig(save_filename, dpi=300, bbox_inches='tight')
        
        # Showing plot (optional)
        if show_plot and (not folder or verbose):

            # Plotting
            if not save_fig:
                plt.figure()
            plt.bar(bin_centers, counts, width=0.8 * (bin_centers[1] - bin_centers[0]), **self.options)

            plt.xlabel(self.x_axis)
            plt.ylabel(self.y_axis)
            plt.title(self.title + method)
            
            plt.show()

        #Set the counts, bin_centers, and bin_edges of the object
        self.counts = counts
        self.bin_centers = bin_centers
        self.bin_edges = bin_edges

        return counts, bin_centers, bin_edges
    
    #This function is to initialize the RossiHistogram if we used the combined time_diffs and hist function
    def initFromHist(self, counts, bin_centers, bin_edges):
        '''Description: Used to initialize the plot object if the data has already been processed/binned.
        
        Inputs: 
            - counts: array of histogram counts
            - bin_centers: bin centers of histogram
            - bin_edges: bin_edges of histogram
            
        Outputs:
        Nothing, but plotFromHist can now be called.'''

        self.counts = counts
        self.bin_centers = bin_centers
        self.bin_edges = bin_edges
        self.title = 'Histogram Using '

    # NOTE: this function is not currently maintained
    def plotFromHist(self, input: str, method: str = 'aa', plot_opts: dict = None, save_fig: bool = False, show_plot: bool = True, save_dir:str= None, folder: bool = False, verbose: bool = False):
        '''Description: Used to plot the histogram when the time differences were calculated simulatenously while being binned. 
        
        Inputs: 
            - plot_opts: dictionary of visual settings to be applied
            - save_fig: True/False to save the figure
            - show_plot: True/False to show figure in plot editor
            - save_dir: Must be provided if save_fig is on.
            
        Outputs:
        Shows a plot/saves a figure if turned on.'''
        
        self.options = plot_opts
        self.save_dir = save_dir
        self.show_plot = show_plot

        
        if save_fig and (not folder or verbose):

            # Plotting
            plt.figure()
            plt.bar(self.bin_centers, self.counts, width=0.8 * (self.bin_centers[1] - self.bin_centers[0]), **self.options)

            plt.xlabel(self.x_axis)
            plt.ylabel(self.y_axis)
            plt.title(self.title + method)

            plt.tight_layout()
            save_filename = os.path.join(self.save_dir, 'histogram_' + input + '_' + method + '.png')
            plt.savefig(save_filename, dpi=300, bbox_inches='tight')
        
        # Showing plot (optional)
        if show_plot and (not folder or verbose):

            # Plotting
            if not save_fig:
                plt.figure()
            plt.bar(self.bin_centers, self.counts, width=0.8 * (self.bin_centers[1] - self.bin_centers[0]), **self.options)

            plt.xlabel(self.x_axis)
            plt.ylabel(self.y_axis)
            plt.title(self.title + method)
            
            plt.show()

        
#--------------------------------------
