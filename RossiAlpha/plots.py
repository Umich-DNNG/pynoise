import numpy as np
import matplotlib.pyplot as plt
import os

import tkinter as Tk
from . import rossiAlpha as ra
from tqdm import tqdm

# to allow for importing global files
import sys
ogPath = sys.path.copy()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)))
import analyze as globalAnalyze                      # to import functions used across all methods
import hdf5
sys.path = ogPath

plt.ioff()



def createPlot(timeDifs: dict,
                hist: dict,
                settings: dict,
                settingsPath: str):
    
    '''Create a Rossi Alpha histogram. Assumes 
    that time differences are already calculated.
    
    Inputs:
    - timeDifs: the dictionary containing time difference data; from the calling class
    - hist: the dictionary containing histogram data; from the calling class
    - settings: dictionary holding the runtime settings
    - settingsPath: string path to the settings file'''
    

    # Clear out the current histogram data.
    hist['Histogram'].clear()
    # Create a RossiHistogram object for each time difference.
    for time_dif in timeDifs['Time differences']:
        hist['Histogram'].append(RossiHistogram(time_dif, 
                                                settings['RossiAlpha Settings']['Bin width'], 
                                                settings['RossiAlpha Settings']['Reset time']))
    name = settings['Input/Output Settings']['Input file/folder']
    name = name[name.rfind('/')+1:]

    print('Creating histograms...')
    # Plot each histogram.
    for i in range(0, len(hist['Histogram'])):
        hist['Histogram'][i].plot(name, 
                                    timeDifs['Time difference method'][i], 
                                    settings['Input/Output Settings']['Save figures'], 
                                    settings['General Settings']['Show plots'], 
                                    settings['Input/Output Settings']['Save directory'], 
                                    settings['Histogram Visual Settings'],
                                    False,
                                    settings['General Settings']['Verbose iterations'])
        # save to hdf5
        if settings['Input/Output Settings']['Save outputs']:
            data = []
            data.append(np.array([hist['Histogram'][i].bin_centers, hist['Histogram'][i].counts]).T)
            data = np.array(data)
            hdf5.writeHDF5Data(data,
                               ['values'],
                               ['RossiAlpha', 'distribution'],
                               settings,
                               'pynoise',
                               settingsPath)
    # Store the current setting.
    hist['Bin width'] = settings['RossiAlpha Settings']['Bin width']


def folderHistogram(timeDifs: dict, hist: dict, numFolders: int, settings: dict, settingsPath:str, window: Tk = None):
    '''Create a histogram for a folder input.

    Inputs: 
    - numFolders: int, number of folders to be analyzed.
    - settings: the dictionary containing all the runtime settings
    - settingsPath: string path to the settings file
    - window: the gui window, if in gui mode

    Outputs:
    - bool: true if successful, false otherwise
    '''
    # Get the name of the input.
    name = settings['Input/Output Settings']['Input file/folder']
    name = name[name[:name.rfind('/')].rfind('/')+1:]

    hist['Histogram'].clear()
    hist['Bin width'] = settings['RossiAlpha Settings']['Bin width']
    # compile subfolder data together, including exporting if in verbose mode
    combined = subfolderPlots(timeDifs, hist, settings, settingsPath, numFolders)
    
    # create histogram(s) of entire folder
    print('Creating histograms of the entire folder...')
    hist['Histogram'].clear()
    numBins = int(settings['RossiAlpha Settings']['Reset time'] / settings['RossiAlpha Settings']['Bin width'])
    binEdges = np.linspace(0, settings['RossiAlpha Settings']['Reset time'], numBins + 1)
    binCenters = np.linspace((settings['RossiAlpha Settings']['Bin width'] / 2),
                             (settings['RossiAlpha Settings']['Reset time'] - (settings['RossiAlpha Settings']['Bin width'] / 2)),
                             numBins)
    for i, counts in enumerate(combined):
        method = timeDifs['Time difference method'][i]
        hist['Histogram'].append(RossiHistogram(bin_width=settings['RossiAlpha Settings']['Bin width'], reset_time=settings['RossiAlpha Settings']['Reset time']))
        hist['Histogram'][-1].initFromHist(counts, binCenters, binEdges)
        hist['Histogram'][-1].plotFromHist(name,
                                            method,
                                            settings['Histogram Visual Settings'],
                                            settings['Input/Output Settings']['Save figures'], 
                                            settings['General Settings']['Show plots'], 
                                            settings['Input/Output Settings']['Save directory'], 
                                            False, 
                                            settings['General Settings']['Verbose iterations'])
        if settings['Input/Output Settings']['Save outputs']:
            # ---------- NOTE: code below exports outputs in csv format ------------
            # ----------------- commented out as we move to hdf5 -------------------
            # begin, end = ra.computeBinEdges(hist)
            # fileName = 'rossi_hist_' + name + '_' + method + '_' + str(hist['Histogram'][-1].bin_width) + '_' + str(settings['RossiAlpha Settings']['Reset time'])
            # globalAnalyze.export({'Bin beginning': (begin,0),
            #                     'Bin ending': (end,0),
            #                     'Measured Count': (hist['Histogram'][-1].counts,0)
            #                     },
            #                     [('Time difference method',method),
            #                     ('Number of folders', numFolders),
            #                     ('Input file', name)],
            #                     fileName,
            #                     settings['Input/Output Settings']['Save directory'])

            # export to hdf5
            data = []
            data.append(np.array([hist['Histogram'][-1].bin_centers, hist['Histogram'][-1].counts, hist['Uncertainty'][i]]).T)
            data = np.array(data)
            hdf5.writeHDF5Data(data, 
                               ['values'], 
                               ['RossiAlpha', 'distribution', 'total'], 
                               settings, 
                               'pynoise', 
                               settingsPath)
        plt.close()


# --------------------------------- helper functions for creating histograms -----------------------------------------


def calcUncertainty(hist: dict, total: list, numFolders: int):
    '''
    Helper for a folder, calculates the uncertainty given the separate folder histogram data.
    Also combines the data

    Inputs:
    - hist: dictionary holding histogram data from the class object. Will have uncertainty added to the object
    - total: list containing the histogram data to be used for uncertainty calculations
    - numFolders: int indicating the number of folders

    Outputs:
    - combinedData, the list holding the histogram data of all the subfolders combined 
    '''
    stdDev = []
    combinedData = []

    hist['Uncertainty'].clear()

    for i in range(0, len(total)):
        # Compute the histogram standard deviation and total.
        stdDev.append(np.std(total[i], axis=0, ddof=1))
        combinedData.append(np.sum(total[i], axis=0))

        # Calculate the uncertainties and replace zeroes.
        hist['Uncertainty'].append(stdDev[i] * numFolders)
        hist['Uncertainty'][i] = globalAnalyze.replace_zeroes(hist['Uncertainty'][i])
    return combinedData


def subfolderPlots(timeDifs: dict, hist: dict, settings: dict, settingsPath:str, numFolders: int):
    '''
    For a folder, computes the data for a subfolder and uncertainty data.

    Inputs:
    - timeDifs: dictionary holding the time difference data
    - hist: dictionary holding histogram data
    - settings: dictionary holding runtime settings
    - settingsPath: string path to the settings file
    - numFolders: int indicating the number of folders
    '''
    numHistograms = ra.getNumSets(settings)

    totalHist = []

    name = settings['Input/Output Settings']['Input file/folder']
    name = name[name[:name.rfind('/')].rfind('/')+1:].replace('/','-')

    print('Compiling subfolder data...')
    for folder in tqdm(range(numFolders)):
        hist['Histogram'].clear()
        for i in range(numHistograms):
            method = timeDifs['Time difference method'][i]
            hist['Histogram'].append(RossiHistogram(timeDifs['Time differences'][i][folder],
                                                    settings['RossiAlpha Settings']['Bin width'],
                                                    settings['RossiAlpha Settings']['Reset time']))
            
            # plot with the actual settings, which can show/save the subplot
            if settings['General Settings']['Verbose iterations']:
                hist['Histogram'][-1].plot((name + "-" + str(folder + 1)),
                                            method,
                                            settings['Input/Output Settings']['Save figures'], 
                                            settings['General Settings']['Show plots'], 
                                            settings['Input/Output Settings']['Save directory'], 
                                            settings['Histogram Visual Settings'], 
                                            True, 
                                            settings['General Settings']['Verbose iterations'])
                # ---------- NOTE: code below exports outputs in csv format ------------
                # if settings['Input/Output Settings']['Save outputs']:
                    # begin, end = ra.computeBinEdges(hist) 
                    # fileName = 'rossi_hist_' + name + '-' + str(folder + 1) + '_' + method + '_' + str(hist['Histogram'][folder].bin_width) + '_' + str(settings['RossiAlpha Settings']['Reset time'])
                    # globalAnalyze.export({'Bin beginning': (begin,0),
                    #                     'Bin ending': (end,0),
                    #                     'Measured Count': (hist['Histogram'][0].counts,0)},
                    #                     [('Time difference method',method),
                    #                     ('Input file', (name + '/' + str(folder + 1)))],
                    #                     fileName,
                    #                     settings['Input/Output Settings']['Save directory'])
                hist['Subplots'].append(hist['Histogram'][-1])
            
            # if verbose iterations is not on, then "plot" to be able to retrieve the counts for the uncertainty calculations
            # however, nothing will be saved or shown
            else:
                hist['Histogram'][-1].plot('Does not matter',
                                            method,
                                            False, 
                                            False, 
                                            settings['Input/Output Settings']['Save directory'], 
                                            settings['Histogram Visual Settings'], 
                                            True, 
                                            False)
            plt.close()
        
        if folder == 0:
            for histogram in hist['Histogram']:
                totalHist.append(histogram.counts)
        else:
            for j in range(len(hist['Histogram'])):
                totalHist[j] = np.vstack((totalHist[j], hist['Histogram'][j].counts))

    # save subplots
    if settings['Input/Output Settings']['Save outputs'] and settings['General Settings']['Verbose iterations']:
        data = []
        for subplot in (hist['Subplots']):
            array = np.array([subplot.bin_centers, subplot.counts]).T
            data.append(array)
        data = np.array(data)
        hdf5.writeHDF5Data(data, 
                           [f'{i}' for i in range(1, numFolders + 1)],
                           ['RossiAlpha', 'distribution', 'subfolders'],
                           settings,
                           'pynoise',
                           settingsPath)
    # calculate uncertainty and return the combined histogram data
    return calcUncertainty(hist, totalHist, numFolders)


# NOTE: function not maintained
def marbePlot(timeDifs: list,
              hist: dict,
              width:int,
              reset:float,):
        
        '''Create a Rossi Alpha histogram for MARBE analysis
        
        Inputs:
        - timeDifs: list of time difs used
        - hist: dictionary holding histogram data
        - width: bin width to be tested
        - reset: reset time used'''
        

        # Clear out the current histogram data.
        hist['Histogram'].clear()
        # Create a RossiHistogram object for time difference.
        hist['Histogram'].append(RossiHistogram(timeDifs[0], width, reset))
        # Plot each histogram.
        hist['Histogram'][-1].plot("Doesn't matter", show_plot=False)
        # Store the current setting.
        hist['Bin width'] = width


# ------------------------------------------ class for rossi alpha histograms ----------------------------------------


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
            save_filename = os.path.join(self.save_dir, 'histogram_' + input + '_' + str(self.reset_time) + '_' + method + '.png')
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
            save_filename = os.path.join(self.save_dir, 'histogram_' + input + '_' + str(self.reset_time) + '_' + method + '.png')
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
