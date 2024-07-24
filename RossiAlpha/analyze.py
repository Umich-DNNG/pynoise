'''The class for constructing and calculating time 
difference objects for RossiAlpha analysis. Supports 
separated and combined histogram/time difference operations.

Also executes MARBE

Imported as "td" (time difference)
'''


# Necessary imports.
import numpy as np
from . import plots as plt
import Event as evt
import lmxReader as lmx
import os
import json

from tkinter import *               # for the gui--TODO: implement
from tqdm import tqdm               # for the progress bar
import math                         # used in the unmaintained MARBE functions
from . import rossiAlpha as ra      # to import some of the functions used across the entire rossi alpha method

# to allow for importing global files of the same name
import sys
ogPath = sys.path.copy()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)))
import analyze
import hdf5
sys.path = ogPath


# ----------------driving the calculations of the timeDifCalcs class objects----------------


def createTimeDifs(timeDifs:dict, settings:dict, settingsPath: str, curFolder:int = 0):
    
    '''Create Rossi Alpha time differences for files or for a subfolder
    
    Inputs:
    - timeDifs: the calling class's dictionary of time differences 
    - settings: the dictionary holding the runtime settings
    - curFolder: the current folder being analyzed'''
    

    # Clear out the current time difference data and methods.
    timeDifs['Time differences'].clear()
    timeDifs['Time difference method'].clear()
    # If methods is a list, create a time difference for each instance.
    if isinstance(settings['RossiAlpha Settings']['Time difference method'], list):
        for method in settings['RossiAlpha Settings']['Time difference method']:
            timeDifs['Time differences'].append(timeDifCalcs(
                                                            io=settings['Input/Output Settings'],
                                                            reset_time=settings['RossiAlpha Settings']['Reset time'], 
                                                            method=method, 
                                                            digital_delay=settings['RossiAlpha Settings']['Digital delay'],
                                                            folderNum=curFolder,
                                                            sort_data=settings['General Settings']['Sort data']))
            timeDifs['Time difference method'].append(method)
    # Otherwise, just create one with the given method.
    else:
        timeDifs['Time differences'].append(timeDifCalcs(
                                                        io=settings['Input/Output Settings'],
                                                        reset_time=settings['RossiAlpha Settings']['Reset time'], 
                                                        method=settings['RossiAlpha Settings']['Time difference method'], 
                                                        digital_delay=settings['RossiAlpha Settings']['Digital delay'],
                                                        folderNum=curFolder,
                                                        sort_data=settings['General Settings']['Sort data']))
        timeDifs['Time difference method'].append(settings['RossiAlpha Settings']['Time difference method'])
    # For each time difs object, compute the time differences.
    for i in range(0,len(timeDifs['Time differences'])):
        timeDifs['Time differences'][i] = timeDifs['Time differences'][i].calculateTimeDifsFromEvents()
    # save single file time differences if specified
    if settings['Input/Output Settings']['Save time differences'] and curFolder == 0:
        path = ['RossiAlpha', 'time differences']
        key = ['data']
        hdf5.writeHDF5Data(timeDifs['Time differences'], key, path, settings, 'processing_data', settingsPath)


def folderAnalyzer(timeDifs: dict, settings: dict, settingsPath:str, numFolders: int) -> bool:
    '''Create Rossi Alpha time differences for folders

    The indicies will hold each subfolder's data within the index for a given time difference method

    Inputs:
    - timeDifs: the dictionary from the calling function that will contain the time difference data
    - settings: the dictionary that contains all of the runtime settings.
    - numFolders
    - window: the gui window, if in gui mode.

    Outputs:
    - bool: true if analysis was successful, false otherwise
    '''

    original = settings['Input/Output Settings']['Input file/folder']
    numSets = ra.getNumSets(settings)
    
    # hold a list of all the time difference data across all folders
    combinedTimeDifs = [[] for _ in range(numSets)]
    
    print("Calculating time differences...")
    # iterate through all of the folders (1-based indexing)
    for folder in tqdm(range(1, numFolders + 1)):

        # Add the folder number to the input.
        settings['Input/Output Settings']['Input file/folder'] = original + '/' + str(folder)

        # check if the folder exists. if not, abort
        if not os.path.isdir(settings['Input/Output Settings']['Input file/folder']):
            print('ERROR: Folder ', settings['Input/Output Settings']['Input file/folder'], ' does not exist on this path. Please review the RossiAlpha documentation.')
            print('Aborting...\n')
            settings['Input/Output Settings']['Input file/folder'] = original
            return False
        
        # compute the time difs for this subfolder and add to the list
        createTimeDifs(timeDifs, settings, settingsPath, folder)
        for i in range(numSets):
            combinedTimeDifs[i].append(timeDifs['Time differences'][i])
    
    # set the class object to the calculated combined time differences
    timeDifs['Time differences'].clear()
    timeDifs['Time difference method'].clear()
    for i in range(len(combinedTimeDifs)):
        timeDifs['Time differences'].append(combinedTimeDifs[i])
    # append the time difference methods
    for i in range(numSets):
        if isinstance(settings['RossiAlpha Settings']['Time difference method'], list):
            timeDifs['Time difference method'].append(settings['RossiAlpha Settings']['Time difference method'][i])
        else:
            timeDifs['Time difference method'].append(settings['RossiAlpha Settings']['Time difference method'])

    # reset file name to original path
    settings['Input/Output Settings']['Input file/folder'] = original
    
    # save time difference data for folders
    if settings['Input/Output Settings']['Save time differences']:
        path = ['RossiAlpha', 'time differences']
        key = [f'{i}' for i in range(1, numFolders + 1)]
        hdf5.writeHDF5Data(timeDifs['Time differences'][0], key, path, settings, 'processing_data', settingsPath)
    return True


# ------------------------ class for time difference calculations ----------------------------

class timeDifCalcs:
    
    '''The time differences object that stores 
    events and calculates time differences.'''

    def __init__(self, io: dict, reset_time: float = None, method: str = 'aa', digital_delay: int = None, folderNum = 0, sort_data: bool = False):
        
        '''Initializes a time difference object. Autogenerates variables where necessary.
    
        Inputs:
        - events: the list of measurement times for each data point.
        - digital_delay: the amount of digital delay, if 
        applicable. Only required when using the dd method.
        - reset_time: the maximum time difference allowed. If 
        not given, will autogenerate the best reset time.
        - method: the method of calculating time 
        differences (assumes aa).'''
        

        # If a reset time is given, use it.
        if reset_time != None:
            self.reset_time = float(reset_time)
        # TODO: Otherwise, generate one.
        else:
            self.reset_time = 0
        # Store the method of analysis.
        self.method = method
        # When considering digital delay, store given digital delay.
        if self.method == 'dd':
            self.digital_delay = digital_delay
        # Initialize the blank time differences.
        self.timeDifs = None
        self.export = io['Save time differences']
        self.overwrite = io['Overwrite lower reset times']
        self.outputFolder = io['Save directory']
        name = io['Input file/folder']
        # if is a folder analysis, retrieve the name of the folder. 
        # When this function is called on a folder, the input file/folder was changed to the user inputted folder name + "/" + the current folder number
        # TODO: change calling logic to not have to do this?
        if folderNum != 0:
            temp = name[:name.rfind('/')]
            name = temp[temp.rfind('/')+1:]
        # if is a file, retrieve the name of just the file
        else:
            name = name[name.rfind('/')+1:]
        self.outputName = 'output_rossi_time_difs_' + name
        # self.outputName = io['Output name']
        self.folderNum = folderNum
        self.file_name = os.path.abspath(self.outputFolder) + '/' + self.outputName + '/' + (str(self.folderNum) + '/' if self.folderNum != 0 else '') + self.method + '/'
        self.pregenerated = ''
        if os.path.exists(self.file_name):
            for time_dif_data in os.listdir(self.file_name):
                if len(time_dif_data) > 3 and time_dif_data[-3:] == '.td' and time_dif_data[:-3].isnumeric() and int(time_dif_data[:-3]) >= self.reset_time:
                    self.pregenerated = self.file_name + time_dif_data
                    break
        if self.pregenerated == '':
            # Create empty data and time difference lists.
            self.events = []
            # Load the data according to its file type.
            if io['Input file/folder'].endswith(".txt"):
                self.events = evt.createEventsListFromTxtFile(io['Input file/folder'],
                                                    io['Time column'],
                                                    io['Channels column'],
                                                    True,
                                                    io['Quiet mode'],
                                                    self.folderNum != 0)
            elif io['Input file/folder'].endswith(".lmx"):
                self.events =  lmx.readLMXFile(io['Input file/folder'])
            # If folder analysis:
            else:
                # For each file in the specified folder:
                for filename in os.listdir(io['Input file/folder']):
                    if len(filename) >= 14:
                        board = filename[0:8]
                        ntxt = filename[len(filename)-6:]
                        channel = filename[8:len(filename)-6]
                        if board == 'board0ch' and ntxt == '_n.txt' and channel.isnumeric() and int(channel) >= 0:
                            # Change the input file to this file.
                            # Add the data from this file to the events list.
                            self.events.extend(evt.createEventsListFromTxtFile(io['Input file/folder'] + "/" + filename,
                                                                        io['Time column'],
                                                                        int(channel),
                                                                        False,
                                                                        io['Quiet mode'],
                                                                        True))
            # Sort the data if applicable.
            if sort_data:
                self.events.sort(key=lambda Event: Event.time)

    def exportTimeDifs(self):
        if self.pregenerated == '':
            file_check = os.path.abspath(self.outputFolder) + '/'
            if not os.path.exists(file_check):
                os.mkdir(file_check)
            file_check += self.outputName + '/'
            if not os.path.exists(file_check):
                os.mkdir(file_check)
            if self.folderNum != 0:
                file_check += str(self.folderNum) + '/'
                if not os.path.exists(file_check):
                    os.mkdir(file_check)
            file_check += self.method + '/'
            if not os.path.exists(file_check):
                os.mkdir(file_check)
            if self.overwrite:
                for time_dif_data in os.listdir(self.file_name):
                    if len(time_dif_data) > 3 and time_dif_data[-3:] == '.td' and time_dif_data[:-3].isnumeric() and int(time_dif_data[:-3]) <= self.reset_time:
                        os.remove(self.file_name + time_dif_data)
            with open(self.file_name + str(int(self.reset_time)) + '.td','w') as file:
                json.dump({"Time differences":self.timeDifs.tolist()},file,indent=2)

    def calculateTimeDifsFromEvents(self):

        '''Returns and stores the array of time differences used 
        for constructing a histogram based on the stored method.

        Outputs:
        - the calculated time differences.'''
        
        # Construct the empty time differences array, store the total 
        # number of data points, and initialize the indexing variable.
        
        if self.pregenerated != '':
            with open(self.pregenerated,'r') as file:
                self.timeDifs = np.array([item for item in json.load(file)['Time differences'] if item <= self.reset_time])
            return self.timeDifs
        time_diffs = np.array([])
        n = len(self.events)
        i = 0
        prevent = False
        # Iterate through the whole time vector.
        while i < len(self.events):
            # Create an empty channel bank.
            ch_bank = set()
            # Iterate through the rest of the vector
            # starting 1 after the current data point.
            for j in range(i + 1, n):
                # If the current time difference exceeds the 
                # reset time range, break to the next data point.
                if self.events[j].time - self.events[i].time > self.reset_time:
                    break
                # If the method is any and all, continue. Otherwise, assure 
                # that the channels are different between the two data points.
                if((self.method == 'aa') or self.events[j].channel != self.events[i].channel):
                    # If the method is any and all or cross_correlation, continue. Otherwise, 
                    # check that the current data point's channel is not in the bank.
                    if(self.method == 'aa' or 
                       self.method == 'cc' or 
                       self.events[j].channel not in ch_bank):
                        # Add the current time difference to the list.
                        time_diffs = np.append(time_diffs,(self.events[j].time - self.events[i].time))
                    # If digital delay is on:
                    elif(self.method == 'dd'):
                        # Skip to the nearest data point after the
                        # current one with the digital delay added.
                        stamped_time = self.events[i].time
                        while self.events[i].time < stamped_time + self.digital_delay:
                           i += 1
                        prevent = True
                    # Add the current channel to the channel bank if considering channels.
                    if(self.method != "aa"):
                        ch_bank.add(self.events[j].channel)
            # Iterate to the next data point without double counting for digital delay.
            if not prevent:
                i += 1
            else:
                prevent = False
        # Store the time differences array.
        self.timeDifs = time_diffs
        
        # NOTE: the code commented out below saves time differences to a folder with text files
        # as we move to exporting to hdf5, this is no longer needed
        
        # if self.export:
        #     self.exportTimeDifs()

        # Return the time differences array.
        return self.timeDifs
    

    # NOTE: this function is not currently maintained
    def calculateTimeDifsAndBin(self, 
                                input:str,
                                bin_width:int = None, 
                                save_fig:bool = False, 
                                show_plot:bool = True, 
                                save_dir:str= './', 
                                plot_opts:dict = None, 
                                folder:bool = False, 
                                verbose:bool = False):
        
        '''Simultaneously calculates the time differences for 
        the timeDifs object and adds them to a new histogram.
        
        Inputs:
        - bin width: the width of each histogram bin. If 
        not given, will autogenerate a reasonable width.
        TODO: Actually do this.
        - save_fig: whether or not the figures should be saved 
        to the given directory after creation (assumes False).
        - show_plot: whether or not the figures should be 
        shown to the user upon creation (assumes True).
        - save_dir: if save_fig is True, what directory the figures 
        will be saved in (assumes the current working directory).
        - plot_opts: all the matplotlib plot parameters.
        - folder: whether or not this plot is for folder analysis.
        - verbose: whether or not folder analysis should output file results.
        
        Outputs:
        - RossiHistogram object
        - histogram: the list of counts for each histogram bin.
        - bin_centers: the time at the center of each bin.
        - bin_edges: the time on the edge of each bin.
        '''
        
        
        # Store the number of data points, the number of bins, 
        # and initialize the data point index and histogram array.
        n = len(self.events)
        i = 0
        num_bins = int(self.reset_time / bin_width)
        histogram = np.zeros(num_bins)
        prevent = False
        # Iterate through the whole time vector.
        while i < len(self.events):
            # Create an empty channel bank.
            ch_bank = set()
            # Iterate through the rest of the vector
            # starting 1 after the current data point.
            for j in range(i + 1, n):
                # If the current time difference exceeds the 
                # reset time range, break to the next data point.
                if self.events[j].time - self.events[i].time > self.reset_time:
                    break
                # If the method is any and all, continue. Otherwise, assure 
                # that the channels are different between the two data points.
                if((self.method == 'aa') or self.events[j].channel != self.events[i].channel):
                    # If the method is any and all or cross_correlation, continue. Otherwise, 
                    # check that the current data point's channel is not in the bank.
                    if(self.method == 'aa' or self.method == 'cc' or self.events[j].channel not in ch_bank):
                        # Store the current time difference.
                        thisDif = self.events[j].time - self.events[i].time
                        # Calculate the bin index for the current time difference.
                        binIndex = int((thisDif) / bin_width)
                        # If the calculated index is exactly at the end 
                        # of the time range, put it into the last bin.
                        if(binIndex == num_bins):
                            binIndex -= 1
                        # Increase the histogram count in the appropriate bin.
                        histogram[binIndex] += 1    
                    # If digital delay is on:
                    elif(self.method == 'dd'):
                        # Skip to the nearest data point after the
                        # current one with the digital delay added.
                        stamped_time = self.events[i]
                        while self.events[i].time < stamped_time + self.digital_delay:
                           i += 1
                        prevent = True
                    # Add the current channel to the channel bank if considering channels.
                    if(self.method != "aa"):
                        ch_bank.add(self.events[j].channel)
            # Iterate to the next data point.
            if not prevent:
                i += 1
            else:
                prevent = False
        # Normalize the histogram.
        bin_edges = np.linspace(0, self.reset_time, num_bins + 1)
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])
        # Constuct the rossiHistogram object and plot accordingly.
        rossiHistogram = plt.RossiHistogram(bin_width= bin_width, reset_time=self.reset_time)
        rossiHistogram.initFromHist(histogram,bin_centers,bin_edges)
        rossiHistogram.plotFromHist(input,self.method,plot_opts,save_fig,show_plot,save_dir,folder,verbose)
        # Return the rossiHistogram object and related NP arrays.
        return rossiHistogram, histogram, bin_centers, bin_edges



#------------------------ functions for MARBE ----------------------------------------
#------------ NOTE: these are not currently maintained -------------------------------

def computeMARBE(timeDifs: dict, hist: dict, settings: dict, numFolders: int):
    '''
    Executes the trial and error portion of MARBE calculation

    Inputs:
    - timeDifs: dictionary of time difference data
    - hist: dictionary of histogram data
    - settings: dictionary of runtime settings
    - numFolders: int indicating number of folders
    '''
    settings['RossiAlpha Settings']['Bin width'] = math.ceil(settings['RossiAlpha Settings']['Reset time'] / 1000)
    bestBinFound = False
    # hold a list of time difference data for the first time diff method listed
    # (which is the one used for MARBE calculations)
    timeDifsMARBE = timeDifs['Time differences'][0].copy()
    bestAvgUncertainty = -1
    uncertaintyCap = settings['RossiAlpha Settings']['Max avg relative bin err']
    while not bestBinFound:
        RA_hist_array = []
        RA_std_dev = []
        RA_hist_total = []
        uncertainties = []
        for folder in range(1, numFolders+1):
            plt.marbePlot(timeDifsMARBE[folder-1],
                          hist,
                          settings['RossiAlpha Settings']['Bin width'],
                          settings['RossiAlpha Settings']['Reset time'])
            # If this is the first folder, initialize the histogram array.
            if folder == 1:
                for histogram in hist['Histogram']:
                    RA_hist_array.append(histogram.counts)
            # Otherwise, add the counts to the histogram array.
            else:
                for i in range(0, len(hist['Histogram'])):
                    RA_hist_array[i] = np.vstack((RA_hist_array[i], hist['Histogram'][i].counts))

        # Compute the histogram standard deviation and total.
        RA_std_dev.append(np.std(RA_hist_array[0], axis=0, ddof=1))
        RA_hist_total.append(np.sum(RA_hist_array[0], axis=0))
        # Calculate the uncertainties and replace zeroes.
        uncertainties.append(RA_std_dev[0] * numFolders)
        uncertainties[0] = analyze.replace_zeroes(uncertainties[0])
        # Add the time difference centers and uncertainties to the total histogram.
        avg_uncertainty = 0.0
        total_counts_squared = 0
        for j in range(0, len(RA_hist_total[0])):
            avg_uncertainty += uncertainties[0][j] * RA_hist_total[0][j]
            total_counts_squared += RA_hist_total[0][j] * RA_hist_total[0][j]
        avg_uncertainty /= total_counts_squared

        # determine if best bin was found or if we must continue
        if avg_uncertainty < uncertaintyCap:
            bestAvgUncertainty = settings['RossiAlpha Settings']['Bin width']
            if settings['RossiAlpha Settings']['Bin width'] == 1:
                bestBinFound = True
            else:
                settings['RossiAlpha Settings']['Bin width'] -= 1
        else:
            if settings['RossiAlpha Settings']['Bin width'] == bestAvgUncertainty - 1:
                settings['RossiAlpha Settings']['Bin width'] = bestAvgUncertainty
                bestBinFound = True
            else:
                if settings['RossiAlpha Settings']['Reset time'] / (settings['RossiAlpha Settings']['Bin width'] + 1) < 4:
                    bestBinFound = True
                else:
                    settings['RossiAlpha Settings']['Bin width'] += 1 
        
        # clean up histogram memory
        hist['Histogram'].clear()


def prepMARBE(timeDifs: dict, hist: dict, settings: dict, settingsPath: str, numFolders: int, window: Tk = None):
    '''Function to prepare for automatic bin width computation using MARBE when a bin width is not specified for folder analysis
    
    NOTE: Automatic bin width calculation is not properly supported for multiple time difference methods at once; it will
    default to the method listed first in the settings
    
    Inputs:
    - timeDifs
    - hist:
    - settings: dict holding all the runtime settings
    - settingsPath: string indicating path to settings file
    - numFolders: int, holds the number of folders
    - window: the gui window, if applicable
    '''
    # TODO: temp variable, delete when multiple method MARBE is supported; hold original methods
    timeDifMethods = settings['RossiAlpha Settings']['Time difference method']
    original = settings['Input/Output Settings']['Input file/folder']

    print('Generating time differences...')
    successful = folderAnalyzer(timeDifs, settings, settingsPath, numFolders)
    if not successful:
        return False
    # Restore the original folder pathway.
    settings['Input/Output Settings']['Input file/folder'] = original

    if isinstance(settings['RossiAlpha Settings']['Time difference method'], list):
        settings['RossiAlpha Settings']['Time difference method'] = settings['RossiAlpha Settings']['Time difference method'][0]
        print('Automatic bin width calculation is currently only supported for 1 time difference method at a time.', 
                    'Defaulting to', 
                    settings['RossiAlpha Settings']['Time difference method'],
                    'method for the bin width calculation portion.')
    print("Testing different bin widths...")
        
    # compute MARBE
    computeMARBE(timeDifs, hist, settings, numFolders)

    print('Best bin width for your settings is ' + str(settings['RossiAlpha Settings']['Bin width']) + '\n')
    # restore original time diff settings in case of change
    settings['RossiAlpha Settings']['Time difference method'] = timeDifMethods
    return True