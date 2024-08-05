'''
A subdriver for the Rossi Alpha method

Holds the data collected to pass into functions to perform the actions specified by the user
Does NOT perform any calculations, just determines the combination of calls and stores the data
'''


# Necessary imports.
from . import fitting as fit
from . import plots as plt
from . import analyze as td
from tkinter import *

# to allow for importing global files of the same name
import os
import sys
ogPath = sys.path.copy()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)))
import analyze as globalAnalyze
import hdf5

sys.path = ogPath


# --------- class determining the combination of calls to make for rossi alpha

class RossiAlpha:
    '''
    Class holding the data computed to be passed into further analyses
    '''
    def __init__(self):
        '''
        Initialize the object for the class functions to be utilized in raDriver.py
        The class holds the dictionaries of computed rossi-alpha data
        '''
        self.timeDifs = {'Time differences': [],
                        'Time difference method': []}
        self.hist = {'Histogram': [],
                     'Uncertainty': [],
                     'Bin width': None,
                     'Subplots': []} # holds subfolder histograms, only saved if verbose iterations is on
        self.fit = {'Best fit': [],
                    'Fit minimum': [],
                    'Fit maximum': []}

    def driveTimeDifs(self, settings: dict, settingsPath: str, isFolder: bool = False):
        
        '''Determine the function combinations needed to compute Rossi Alpha time differences
        for the specific current settings
        
        Inputs:
        - settings: dictionary of runtime settings
        - settingsPath: path to the settings file
        - isFolder: whether this is a folder analysis or not

        Outputs:
        - a bool indicating whether the computation was successful
        '''       
        if isFolder:
            numFolders = settings['General Settings']['Number of folders']
            # calculate number of folders if was not specified
            if numFolders is None:
                successful, numFolders = globalAnalyze.calcNumFolders(settings['Input/Output Settings']['Input file/folder'])
                if not successful: return False
            success = td.folderAnalyzer(self.timeDifs, settings, settingsPath, numFolders) 
        else:
            success = True
            td.createTimeDifs(self.timeDifs, settings, settingsPath)
        return success


    def drivePlots(self, settings: dict, settingsPath: str, isFolder: bool = False):

        '''Determine the function combinations needed to compute Rossi Alpha histograms
        for the specific current settings and situation
        
        Inputs:
        - settings: dictionary containing the current runtime settings.
        - isFolder: bool indicating whether this is a folder or a file'''
        
        # execute for "Combine Calc and Binning". NOTE that these functions are not currently maintained
        if (settings['RossiAlpha Settings']['Combine Calc and Binning']):
            if numFolders == 0:
                self.calculateTimeDifsAndPlot(settings['Input/Output Settings'],
                                                settings['General Settings'],
                                                settings['RossiAlpha Settings'],
                                                settings['Histogram Visual Settings'],
                                                0)
            else:
                for folder in range(1, numFolders + 1):
                    self.calculateTimeDifsAndPlot(settings['Input/Output Settings'],
                                                    settings['General Settings'],
                                                    settings['RossiAlpha Settings'],
                                                    settings['Histogram Visual Settings'],
                                                    folder)
                
        if isFolder:
            numFolders = settings['General Settings']['Number of folders']
            # calculate number of folders if was not specified
            if numFolders is None:
                successful, numFolders = globalAnalyze.calcNumFolders(settings['Input/Output Settings']['Input file/folder'])
                if not successful: return False
            successful = plt.folderHistogram(self.timeDifs, self.hist, numFolders, settings, settingsPath)
            if not successful: return False
        
        else:
            plt.createPlot(self.timeDifs, self.hist, settings, settingsPath)
        
        
    def driveFit(self, settings: dict, settingsPath: str, isFolder: bool = False):
        '''
        Determine the function combinations needed to compute Rossi Alpha fit graphs
        for the specific current settings and situation
        
        Inputs:
        - settings: dictionary containing the current runtime settings.
        - isFolder: bool indicating whether this is a folder or a file
        '''

        if isFolder:
            numFolders = settings['General Settings']['Number of folders']
            # calculate number of folders if was not specified
            if numFolders is None:
                successful, numFolders = globalAnalyze.calcNumFolders(settings['Input/Output Settings']['Input file/folder'])
                if not successful: return False
            plt.folderHistogram(self.timeDifs, self.hist, numFolders, settings, settingsPath)
            fit.folderFit(self.fit, self.hist, settings, settingsPath, numFolders)
        else:
            plt.createPlot(self.timeDifs, self.hist, settings, settingsPath)
            fit.createBestFit(self.fit, self.hist, settings, settingsPath)
        pass

# --------------------------- helper functions for the class -------------------------------
    
    # NOTE: this function is not currently maintained
    def calculateTimeDifsAndPlot(self,
                                 io:dict,
                                 gen:dict,
                                 ra:dict,
                                 hist:dict,
                                 folder:int = 0):

        '''Simultaneously calculate the time 
        differences and construct a Rossi Histogram.

        
        Inputs:
        - io: the Input/Output Settings dictionary.
        - gen: the General Settings dictionary.
        - ra: the RossiAlpha Settings dictionary.
        - hist: the Histogram Visual Settings dictionary.
        - folder: whether or not this is for folder analysis (0 means no folder).'''


        # Clear out all of the current data.
        self.timeDifs['Time differences'].clear()
        self.timeDifs['Time difference method'].clear()
        self.hist['Histogram'].clear()
        timeDifCalcs = []
        # If methods is a list, create a time difference for each instance.
        if isinstance(ra['Time difference method'], list):
            for type in ra['Time difference method']:
                self.timeDifs['Time differences'].append(td.timeDifCalcs(
                    io=io,
                    reset_time=ra['Reset time'], 
                    method=type, 
                    digital_delay=ra['Digital delay'],
                    folderNum=folder,
                    sort_data=gen['Sort data']))
                self.timeDifs['Time difference method'].append(type)
        # Otherwise, just create one with the given method.
        else:
            self.timeDifs['Time differences'].append(td.timeDifCalcs(
                io=io,
                reset_time=ra['Reset time'], 
                method=type, 
                digital_delay=ra['Digital delay'],
                folderNum=folder,
                sort_data=gen['Sort data']))
            self.timeDifs['Time difference method'].append(ra['Time difference method'])
        # Simulatenously calculate the time differences and bin them.
        for i in range (0, len(timeDifCalcs)):
            input = io['Input file/folder']
            if folder != 0:
                input = input[input[:input.rfind('/')].rfind('/')+1:].replace('/','-')
            else:
                input = input[input.rfind('/')+1:]
            currentHist, counts, bin_centers, bin_edges = timeDifCalcs[i].calculateTimeDifsAndBin(input,
                                                                                                  ra['Bin width'],
                                                                                                  io['Save figures'],
                                                                                                  gen['Show plots'],
                                                                                                  io['Save directory'],
                                                                                                  hist,
                                                                                                  folder!=0,
                                                                                                  gen['Verbose iterations'])
            self.hist['Histogram'].append(currentHist)
        # Save the current settings.
        self.timeDifs['Input file/folder'] = io['Input file/folder']
        self.timeDifs['Sort data'] = gen['Sort data']
        self.timeDifs['Number of folders'] = folder
        self.timeDifs['Digital delay'] = ra['Digital delay']
        self.timeDifs['Reset time'] = ra['Reset time']
        self.hist['Bin width'] = ra['Bin width']


# ------------- helper functions used across analyze, plots, and fitting


def getNumSets(settings: dict):
    '''
    Returns the number of time diff sets/histograms to make. 
    This is equivalent to the number of time difference methods listed

    Inputs:
    - settings: dictionary containing the runtime settings

    Outputs:
    - number of time difference sets/histograms
    '''
    if isinstance(settings['RossiAlpha Settings']['Time difference method'], list):
        return len(settings['RossiAlpha Settings']['Time difference method'])
    else:
        return 1


def computeBinEdges(hist: dict):
    '''
    Computes the bin edges for anytime outputs are saved to csv

    Inputs:
    - hist: the dictionary of the histogram used to determine the bin edges

    Outputs:
    - begin, end: the lists containing the bin beginnings and edges, respectively
    '''
    # Initialize variables.
    begin = []
    end = []
    # Construct the beginning and ending bin edges lists.
    for k in range(len(hist['Histogram'][-1].bin_edges)-1):
        begin.append(hist['Histogram'][-1].bin_edges[k])
        end.append(hist['Histogram'][-1].bin_edges[k+1])
    return begin, end
