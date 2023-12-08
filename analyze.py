'''The object used for analyzing data.'''



# Necessary imports.
import os
import numpy as np
import matplotlib.pyplot as pyplot
import Event as evt
import time
import lmxReader as lmx
from RossiAlpha import fitting as fit
from RossiAlpha import plots as plt
from RossiAlpha import timeDifs as dif
from CohnAlpha import CohnAlpha as ca
from FeynmanY import feynman as fey
from tkinter import *
from tqdm import tqdm
import psutil
import sys
from scipy import signal               # For welch (fourier transform)





class Analyzer:

    '''The class that runs analysis. Can be used 
    in either terminal or gui implementation.'''


    def __init__(self):

        '''The initializer for the Analyzer object.'''


        # Initialize the variables used to determine whether 
        # or not certain elements have to be recreated.
        self.RATimeDifs = {'Time differences': [],
                           'Input file/folder': None,
                           'Number of folders': None,
                           'Sort data': None,
                           'Time difference method': [],
                           'Digital delay': None,
                           'Reset time': None}
        self.RAHist = {'Histogram': [],
                       'Bin width': None}
        self.RABestFit = {'Best fit': [],
                          'Fit minimum': [],
                          'Fit maximum': []}
        self.CohnAlpha = {}
        self.FeynmanY = {}



    def isValid(self, method:str, parameters:dict):
        match method:
            case 'RABestFit':
                if (not self.isValid('RAHist',parameters)):
                    return False
            case 'RAHist':
                if (not self.isValid('RATimeDifs',parameters)):
                    return False
        for setting in parameters:
            if parameters[setting] != self.RATimeDifs[setting]:
                return False
            return True
        

    def export(self, 
               data: dict[str:tuple], 
               singles: list[tuple], 
               name: str, 
               output: str = './data'):

        '''Export data from analysis to a csv file. The file 
        will be stored in the data folder and will be named 
        based on the give analysis method and current time.
        
        Inputs:
        - dict: a dictionary that contains all the 
        list data to be outputted to the csv file. 
        Each key will be the name of the column, and 
        the value stored will be a tuple. The first 
        value is the list of data, and the second is 
        the row to start displaying the list at.
        - single: a list of single values to display on the top row. 
        Each list value will contain a tuple, whose first entry is 
        the name of the value and whose second entry is the value.
        - method: the name of the method of analysis.
        - output: the output directory. If not given, defaults to ./data.'''


        # Name the file appropriately with the method name and current time.
        fileName = (output + '/raw_data_' + name + '.csv')
        # Open the new file.
        file = open(os.path.abspath(fileName),'w')
        # Initialize variables.
        labels = ''
        line = ''
        max = 0
        # For each dataset:
        for key in data:
            # If this is the longest dataset, store its length.
            if len(data[key][0]) + data[key][1] > max:
                max = len(data[key][0]) + data[key][1]
            # Add the dataset name to the labels string.
            labels += key + ','
            # If the dataset is starting at first 
            # row, add the first value to the row.
            if data[key][1] == 0:
                line += str(data[key][0][0]) + ','
            # Otherwise, leave an empty space.
            else:
                line += ','
        # For each single datapoint:
        for item in singles:
            # Add the data name to the labels string.
            labels += str(item[0]) + ','
            # Add the data value to the first row.
            line += str(item[1]) + ','
        # Write the columns row and first data row 
        # to the file (excluding tailing commas).
        file.write(labels[:-1] + '\n' + line[:-1] + '\n')
        # For each possible dataset index:
        for i in range(1,max):
            # Reset the line string.
            line = ''
            # For each dataset:
            for key in data:
                # If the desired beginning row for the dataset has 
                # been reached and there's still data left to print, 
                # add the proper data value to the current row.
                if i >= data[key][1] and i-data[key][1] < len(data[key][0]):
                    line += str(data[key][0][i-data[key][1]]) + ','
                # Otherwise, leave an empty space.
                else:
                    line += ','
            # Write the whole row to the file (excluding tailing comma).
            file.write(line[:-1]+'\n')
        # Flush the output to the file and close it.
        file.flush()
        file.close()



    def runFeynmanY(self, 
                    io: dict, 
                    fy: dict, 
                    show: bool, 
                    save: bool, 
                    quiet: bool, 
                    verbose: bool = False, 
                    hvs: dict = {}, 
                    lfs: dict = {},
                    sps: dict = {}, 
                    window: Tk = None):
        
        '''Run FeynmanY analysis for varying tau values.
        Plots each tau value and estimates alpha.
        
        Inputs:
        - io: the Input/Output Settings dictionary.
        - fy: the FeynmanY Settings dictionary.
        - show: whether or not to show plots.
        - save: whether or not to save plots.
        - quiet: whether or not to silence print statements.
        - verbose: whether or not the analysis should 
        consider each tau value for exporting.
        - hvs: the Histogram Visual Settings.
        - lfs: the Line Fitting Settings.
        - sps: the Scatter Plot Settings.
        - window: the window object, if being run in GUI mode.'''
        

        # Initialize variables.
        yValues = []
        y2Values = []
        tValues = []
        # Fill the tau list with the desired tau values.
        tValues.extend(range(fy['Tau range'][0], fy['Tau range'][1]+1, fy['Increment amount']))
        # Create a FeynmanY object.
        FeynmanYObject = fey.FeynmanY(fy['Tau range'], fy['Increment amount'], fy['Plot scale'])
        # Load in the data and sort it.
        data = evt.createEventsListFromTxtFile(io['Input file/folder'],
                                               io['Time column'],
                                               io['Channels column'],
                                               True,
                                               quiet,
                                               False)
        data.sort(key=lambda Event: Event.time)
        # Initialize variables for counting
        # the total real measurement time.
        meas_time = 0
        begin = data[0].time
        end = data[0].time
        # Iterate through the data.
        for entry in data:
            # If we have reached a jump:
            if entry.time - end > 1e13:
                # Add the previous measurement 
                # time range to the total.
                meas_time += end - begin
                # Reset the beginning time
                begin = entry.time
            # Move the ending time up.
            end = entry.time
        # Add the remaining time range.
        meas_time += end - begin
        # For GUI mode.
        if window is not None:
            # Increment the progress bar.
            window.children['progress']['value'] += 1
            wait = BooleanVar()
            # After 1 ms, set the dummy variable to True.
            window.after(1, wait.set, True)
            # Wait for the dummy variable to be set, then continue.
            window.wait_variable(wait)
        # If not in quiet mode, display progress.
        if not quiet:
            print('Running each tau value...')
        # For each tau value:
        for tau in tqdm(tValues):
            # Convert the data into bin frequency counts.
            counts = FeynmanYObject.randomCounts(data, tau, meas_time)
            # Compute the variance to mean for this 
            # tau value and add it to the list.
            FeynmanYObject.computeMoments(counts, tau)
            y, y2 = FeynmanYObject.computeYY2(tau)
            yValues.append(y)
            y2Values.append(y2)
            # If in verbose mode:
            if verbose:
                # Save the raw data if desired..
                if io['Save raw data']:
                    self.export({'Count': (range(0,len(counts)), 0),
                                 'Frequency': (counts,0)},
                                 [('Tau',tau)],
                                 'FY' + str(tau),
                                 io['Save directory'])
                # Call the histogram plotter if desired.
                if show or save:
                    FeynmanYObject.FeynmanY_histogram(counts,
                                                    fy['Plot scale'],
                                                    show,
                                                    save,
                                                    io['Save directory'],
                                                    hvs)
            # For GUI mode.
            if window is not None:
                # Increment the progress bar.
                window.children['progress']['value'] += 1
                wait = BooleanVar()
                # After 1 ms, set the dummy variable to True.
                window.after(1, wait.set, True)
                # Wait for the dummy variable to be set, then continue.
                window.wait_variable(wait)
        # Plot and fit both Y and Y2 values against tau.
        FeynmanYObject.plot(tValues, yValues, save, show, io['Save directory'])
        FeynmanYObject.plot(tValues, y2Values, save, show, io['Save directory'])
        FeynmanYObject.fitting(tValues, 
                               yValues, 
                               gamma_guess=yValues[-1], 
                               alpha_guess=-0.01, 
                               save_fig=save, 
                               show_plot=show, 
                               save_dir=io['Save directory'],
                               fit_opt=lfs,
                               scatter_opt=sps,
                               type='Y')
        FeynmanYObject.fitting(tValues, 
                               y2Values, 
                               gamma_guess=yValues[-1], 
                               alpha_guess=-0.01, 
                               save_fig=save, 
                               show_plot=show, 
                               save_dir=io['Save directory'],
                               fit_opt=lfs,
                               scatter_opt=sps,
                               type='Y2')
        # If saving raw dta:
        if io['Save raw data']:
            # Create a proper file name.
            if verbose:
                filename = 'FYFull'
            else:
                filename = 'FY'
            # Export the data.
            self.export({'Tau':(tValues,0),
                         'Experimental Y':(yValues,0),
                         'Experimental Y2':(y2Values,0),
                         'Predicted Y2': (FeynmanYObject.pred,0)},
                        [('Gamma',FeynmanYObject.gamma),
                         ('Alpha',FeynmanYObject.alpha),
                         ('Input file', io['Input file/folder'])],
                        filename,
                        io['Save directory'])

    def find_large_relative_changes(self, values, threshold_percent):
        datasize = 25000
        change_indices = []
        
        for i in range(1, len(values)):
            print ("values[i]", values[i])
            print ("values[i-1]", values[i-1])
            change_percentage = abs(values[i] - values[i-1])
            # change_percentage = change_percentage / values[i - 1] * 100
            print("change percent type", type(change_percentage))
            print("length change percentage", len(change_percentage))
            print("threshold percent type", type(threshold_percent))
            if change_percentage > threshold_percent:
                change_indices.append(i)
        chunks = []
        start_idx = 0
        
        for end_idx in change_indices:
            chunk = values[start_idx:end_idx]
            chunks.append(chunk)
            start_idx = end_idx
        
        # Add the last chunk (from the last change index to the end of the data)
        if start_idx < len(values):
            last_chunk = values[start_idx:]
            chunks.append(last_chunk)
        # Further split chunks into smaller ones
        smaller_chunks = []
        for chunk in chunks:
            if len(chunk) <= datasize:
                smaller_chunks.append(chunk)
            else:
                num_subchunks = len(chunk) // datasize
                remaining_data = chunk
                for _ in range(num_subchunks):
                    subchunk = remaining_data[:datasize]
                    smaller_chunks.append(subchunk)
                    remaining_data = remaining_data[datasize:]
                if remaining_data.size > 0:
                    smaller_chunks.append(remaining_data)
                smaller_chunks = smaller_chunks
        return chunks, smaller_chunks
    
    def process_chunk(self, chunk_index, chunk_data, dwell_time_ms, nperseg_m):
        # Create the histogram
        bin_width_ps = dwell_time_ms * 1e9  # Convert ms to ps
        # Define explicit bin edges
        bin_edges = np.arange(min(chunk_data), max(chunk_data) + bin_width_ps,
                            bin_width_ps)
        hist, _ = np.histogram(chunk_data, bins=bin_edges)

        fs = round(1 / (dwell_time_ms / int(1000)))  # Frequency converting ns to s
        f, Pxx = signal.welch(hist, fs, nperseg=nperseg_m, window='boxcar')
        result = {
            'chunk_index': chunk_index,
            'f': f,
            'Pxx': Pxx,
        }
        return result

    def conductCohnAlpha(self,
                         input:str,
                         output:str,
                         show:bool,
                         save:bool,
                         caSet:dict,
                         sps:dict,
                         lfs:dict,
                         scatter_plot_settings:dict):

        '''Runs Cohn Alpha analysis.
        
        Inputs:
        - input: the file path.
        - output: the save directory.
        - show: whether or not to show plots.
        - save: whether or not to save plots.
        - caSet: the CohnAlpha Settings.
        - sps: the Semilog Plot Settings.
        - lfs: the Line Fitting Settings.'''

        # measure memory available on device
        available_memory_gb = psutil.virtual_memory().available / 1073741824
        print(f"Available Memory: {available_memory_gb:.2f} GB")

        # Load the values from the specified file into an NP array.
        values = np.loadtxt(input, usecols=(0,3), dtype=float)

        # set parameters based on memory
        # if (available_memory_gb < ):


        dwell_time_ms = caSet['Dwell time']
        nperseg_m = caSet['nperseg']
        threshold_percent = 0.2
        chunks, schunks = self.find_large_relative_changes(values, threshold_percent)

        # process chunks and get results
        for chunk_index, chunk_data in enumerate(chunks):
            result = self.process_chunk(chunk_index, chunk_data, dwell_time_ms, nperseg_m)


        # -------- TODO: Using "clean_pulses_switch" here directly --------

        # Only considering rows where last column value == 1 (Optional)
        if caSet['Clean pulses switch'] == 1:
            values = np.loadtxt(input, usecols=(0,3), dtype=float)
            values = values[values[:, 1] == 1]
            values = values[:, 0]
        else:
            values = np.loadtxt(input, usecols=0, dtype=float)

        # -----------------------------------------------------------------

        # Create a Cohn Alpha object with the given settings.
        CA_Object = ca.CohnAlpha(values,
                                 caSet['Clean pulses switch'], 
                                 caSet['Dwell time'],
                                 caSet['Meas time range'])
        # Conduct Cohn Alpha analysis with the given settings.
        CA_Object.conductCohnAlpha(show, save, output, caSet, sps, lfs, scatter_plot_settings)



    def createTimeDifs(self,
                       io:dict,
                       sort:bool,
                       reset:float,
                       method:str,
                       delay:int,
                       quiet:bool,
                       folder:int = 0):
        
        '''Create Rossi Alpha time differences.
        
        Inputs:
        - io: the Input/Output Settings dictionary.
        - sort: whether or not to sort the data.
        - reset: the reset time.
        - method: the time difference method.
        - delay: the digital delay.
        - quiet: whether or not to output print statements.
        - folder: the number of folders (0 if single file).'''
        

        # Clear out the current time difference data and methods.
        self.RATimeDifs['Time differences'].clear()
        self.RATimeDifs['Time difference method'].clear()
        # Create an empty data list.
        data = []
        # Load the data according to its file type.
        if io['Input file/folder'].endswith(".txt"):
            data = evt.createEventsListFromTxtFile(io['Input file/folder'],
                                                   io['Time column'],
                                                   io['Channels column'],
                                                   True,
                                                   quiet,
                                                   True if folder != 0 else False)
        elif io['Input file/folder'].endswith(".lmx"):
            data = lmx.readLMXFile(io['Input file/folder'])
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
                        data.extend(evt.createEventsListFromTxtFile(io['Input file/folder'] + "/" + filename,
                                                                    io['Time column'],
                                                                    int(channel),
                                                                    False,
                                                                    io['Quiet mode'],
                                                                    True))
        # Sort the data if applicable.
        if sort:
            data.sort(key=lambda Event: Event.time)
        # If methods is a list, create a time difference for each instance.
        if isinstance(method, list):
            for type in method:
                self.RATimeDifs['Time differences'].append(dif.timeDifCalcs(data, reset, type, delay))
                self.RATimeDifs['Time difference method'].append(type)
        # Otherwise, just create one with the given method.
        else:
            self.RATimeDifs['Time differences'].append(dif.timeDifCalcs(data, reset, method, delay))
            self.RATimeDifs['Time difference method'].append(method)
        # For each time difs object, create the time differences.
        for i in range(0,len(self.RATimeDifs['Time differences'])):
            self.RATimeDifs['Time differences'][i] = self.RATimeDifs['Time differences'][i].calculateTimeDifsFromEvents()
        # Save the current relevant settings.
        self.RATimeDifs['Input file/folder'] = io['Input file/folder']
        self.RATimeDifs['Sort data'] = sort
        self.RATimeDifs['Number of folders'] = folder
        self.RATimeDifs['Digital delay'] = delay
        self.RATimeDifs['Reset time'] = reset
        


    def createPlot(self,
                   input:str,
                   width:int,
                   reset:float,
                   save:bool,
                   show:bool,
                   output:str,
                   vis:dict,
                   folder:bool = False,
                   verbose:bool = False):
        
        '''Create a Rossi Alpha histogram. Assumes 
        that time differences are already calculated.
        
        Inputs:
        - width: the bin width.
        - reset: the reset time.
        - save: whether or not to save plots.
        - show: whether or not to show plots.
        - output: the save directory.
        - vis: the Histogram Visual Settings dictionary.
        - folder: whether or not this is for folder analysis.
        - verbose: whether or not individual files should be outputted.'''
        

        # Clear out the current histogram data.
        self.RAHist['Histogram'].clear()
        # Create a RossiHistogram object for each time difference.
        for time_dif in self.RATimeDifs['Time differences']:
            self.RAHist['Histogram'].append(plt.RossiHistogram(time_dif, width, reset))
        # Plot each histogram.
        for i in range (0, len(self.RAHist['Histogram'])):
            self.RAHist['Histogram'][i].plot(input, self.RATimeDifs['Time difference method'][i], save, show, output, vis, folder, verbose)
        # Store the current setting.
        self.RAHist['Bin width'] = width



    def calculateTimeDifsAndPlot(self,
                                 io:dict,
                                 gen:dict,
                                 ra:dict,
                                 hist:dict,
                                 folder:bool = False):

        '''Simultaneously calculate the time 
        differences and construct a Rossi Histogram.
        
        Inputs:
        - io: the Input/Output Settings dictionary.
        - gen: the General Settings dictionary.
        - ra: the RossiAlpha Settings dictionary.
        - hist: the Histogram Visual Settings dictionary.
        - folder: whether or not this is for folder analysis.'''


        # Clear out all of the current data.
        self.RATimeDifs['Time differences'].clear()
        self.RATimeDifs['Time difference method'].clear()
        self.RAHist['Histogram'].clear()
        # Create empty data and time difference lists.
        data = []
        timeDifCalcs = []
        # Load the data according to its file type.
        if io['Input file/folder'].endswith(".txt"):
            data = evt.createEventsListFromTxtFile(io['Input file/folder'],
                                                   io['Time column'],
                                                   io['Channels column'],
                                                   True,
                                                   io['Quiet mode'],
                                                   folder)
        elif io['Input file/folder'].endswith(".lmx"):
            data =  lmx.readLMXFile(io['Input file/folder'])
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
                        data.extend(evt.createEventsListFromTxtFile(io['Input file/folder'] + "/" + filename,
                                                                    io['Time column'],
                                                                    int(channel),
                                                                    False,
                                                                    io['Quiet mode'],
                                                                    True))
        # Sort the data if applicable.
        if gen['Sort data']:
            data.sort(key=lambda Event: Event.time)
        # If methods is a list, create a time difference for each instance.
        if isinstance(ra['Time difference method'], list):
            for type in ra['Time difference method']:
                self.RATimeDifs['Time differences'].append(dif.timeDifCalcs(data, ra['Reset time'], type, ra['Digital delay']))
                self.RATimeDifs['Time difference method'].append(type)
        # Otherwise, just create one with the given method.
        else:
            self.RATimeDifs['Time differences'].append(dif.timeDifCalcs(data, ra['Reset time'], ra['Time difference method'], ra['Digital delay']))
            self.RATimeDifs['Time difference method'].append(ra['Time difference method'])
        # Simulatenously calculate the time differences and bin them.
        for i in range (0, len(timeDifCalcs)):
            input = io['Input file/folder']
            if folder:
                input = input[input[:input.rfind('/')].rfind('/')+1:].replace('/','-')
            else:
                input = input[input.rfind('/')+1:]
            currentHist, counts, bin_centers, bin_edges = timeDifCalcs[i].calculateTimeDifsAndBin(input,
                                                                                                  ra['Bin width'],
                                                                                                  io['Save figures'],
                                                                                                  gen['Show plots'],
                                                                                                  io['Save directory'],
                                                                                                  hist,
                                                                                                  folder,
                                                                                                  gen['Verbose iterations'])
            self.RAHist['Histogram'].append(currentHist)
        # Save the current settings.
        self.RATimeDifs['Input file/folder'] = io['Input file/folder']
        self.RATimeDifs['Sort data'] = gen['Sort data']
        self.RATimeDifs['Number of folders'] = folder
        self.RATimeDifs['Digital delay'] = ra['Digital delay']
        self.RATimeDifs['Reset time'] = ra['Reset time']
        self.RAHist['Bin width'] = ra['Bin width']



    def plotSplit(self, settings: dict, folder: bool = False):

        '''Determines what combination of time difference 
        calculation and Rossi Histogram constructing to do.
        
        Inputs:
        - settings: the current runtime settings.
        - folder: whether or not this is for folder analysis.'''


        # Create a dictionary of the current relevant settings.
        check = {'Input file/folder': settings['Input/Output Settings']['Input file/folder'],
                'Sort data': settings['General Settings']['Sort data'],
                'Time difference method': (settings['RossiAlpha Settings']['Time difference method'] if isinstance(settings['RossiAlpha Settings']['Time difference method'], list) else [settings['RossiAlpha Settings']['Time difference method']]),
                'Digital delay': settings['RossiAlpha Settings']['Digital delay'],
                'Reset time': settings['RossiAlpha Settings']['Reset time']}
        # Get the name of the input.
        name = settings['Input/Output Settings']['Input file/folder']
        if folder:
            name = name[name[:name.rfind('/')].rfind('/')+1:].replace('/','-')
            check['Number of folders'] = settings['General Settings']['Number of folders']
        else:
            name = name[name.rfind('/')+1:]   
        # If time differences have not yet been calculated or the 
        # current settings do not match those previously used:
        if self.RATimeDifs['Time differences'] is None or not self.isValid('RATimeDifs', check):
            # If applicable, combine the time difference calculation and binning.
            if (settings['RossiAlpha Settings']['Combine Calc and Binning']):
                self.calculateTimeDifsAndPlot(settings['Input/Output Settings'],
                                              settings['General Settings'],
                                              settings['RossiAlpha Settings'],
                                              settings['Histogram Visual Settings'],
                                              folder)
            # Otherwise, create the time differences and histogram separately.
            else:
                self.createTimeDifs(settings['Input/Output Settings'],
                                    settings['General Settings']['Sort data'],
                                    settings['RossiAlpha Settings']['Reset time'],
                                    settings['RossiAlpha Settings']['Time difference method'],
                                    settings['RossiAlpha Settings']['Digital delay'],
                                    settings['Input/Output Settings']['Quiet mode'],
                                    settings['General Settings']['Number of folders'] if folder else 0)
                self.createPlot(name,
                                settings['RossiAlpha Settings']['Bin width'],
                                settings['RossiAlpha Settings']['Reset time'],
                                settings['Input/Output Settings']['Save figures'],
                                settings['General Settings']['Show plots'],
                                settings['Input/Output Settings']['Save directory'],
                                settings['Histogram Visual Settings'],
                                folder,
                                settings['General Settings']['Verbose iterations'])
        # Otherwise, just create a Rossi Histogram plot. 
        else:
            self.createPlot(name,
                            settings['RossiAlpha Settings']['Bin width'],
                            settings['RossiAlpha Settings']['Reset time'],
                            settings['Input/Output Settings']['Save figures'],
                            settings['General Settings']['Show plots'],
                            settings['Input/Output Settings']['Save directory'],
                            settings['Histogram Visual Settings'],
                            folder,
                            settings['General Settings']['Verbose iterations'])
            

            
    def createBestFit(self,
                      save:bool,
                      output:str,
                      show:bool,
                      verbose:bool,
                      ra:dict,
                      line:dict,
                      res:dict,
                      hist:dict,
                      folder:bool = False):
        
        '''Create a Rossi Histogram line of best fit and residual plot.
        
        Inputs:
        - save: whether or not to save figures.
        - output: the save directory.
        - show: whether or not to show plots.
        - verbose: whether or not individual file
        results should be exported.
        - ra: the Rossi Alpha settings dictionary.
        - line: the Line Fitting Settings dictionary.
        - res: the Scatter Plot Settings dictionary.
        - hist: the Histogram Visual Settings dictionary.
        - folder: whether or not this is for folder analysis.'''
        
        self.RABestFit['Best fit'].clear()
        self.RABestFit['Fit minimum'].clear()
        self.RABestFit['Fit maximum'].clear()
        if isinstance(ra['Fit maximum'],list):
            for i in range(0,len(ra['Fit maximum'])):
                if ra['Fit maximum'][i] == None:
                    self.RABestFit['Fit maximum'].append(ra['Reset time'])
                else:
                    self.RABestFit['Fit maximum'].append(ra['Fit maximum'][i])
        else:
            if ra['Fit maximum'] == None:
                self.RABestFit['Fit maximum'].append(ra['Reset time'])
            else:
                self.RABestFit['Fit maximum'].append(ra['Fit maximum'])
        if isinstance(ra['Fit minimum'],list):
            for i in range(0,len(ra['Fit minimum'])):
                self.RABestFit['Fit minimum'].append(ra['Fit minimum'][i])
        else:
            self.RABestFit['Fit minimum'].append(ra['Fit minimum'])
        for i in range(0, len(self.RAHist['Histogram'])):
            for j in range(0, len(self.RABestFit['Fit minimum'])):
                # Construct a RossiHistogramFit object and plot it with the given settings.
                self.RABestFit['Best fit'].append(fit.RossiHistogramFit(self.RAHist['Histogram'][i].counts,
                                                    self.RAHist['Histogram'][i].bin_centers,
                                                    self.RATimeDifs['Time difference method'][i],
                                                    self.RABestFit['Fit minimum'][j],
                                                    self.RABestFit['Fit maximum'][j]))
                input =  self.RATimeDifs['Input file/folder']
                if folder:
                    input = input[input[:input.rfind('/')].rfind('/')+1:].replace('/','-')
                else:
                    input = input[input.rfind('/')+1:]
                self.RABestFit['Best fit'][i*len(self.RABestFit['Fit minimum'])+j].fit_and_residual(save,
                                                            output,
                                                            show,
                                                            line,
                                                            res,
                                                            hist,
                                                            input,
                                                            self.RATimeDifs['Time difference method'][i],
                                                            folder,
                                                            verbose)
                pyplot.close()



    def fitSplit(self, settings:dict, folder:bool = False):

        '''Determines what combination of time difference 
        calculation and Rossi Histogram constructing to do.
        
        Inputs:
        - settings: the current runtime settings.
        - folder: whether or not this is for folder analysis.'''


        # Create a dictionary of the current relevant settings.
        check = {'Input file/folder': settings['Input/Output Settings']['Input file/folder'],
                'Sort data': settings['General Settings']['Sort data'],
                'Time difference method': (settings['RossiAlpha Settings']['Time difference method'] if isinstance(settings['RossiAlpha Settings']['Time difference method'], list) else [settings['RossiAlpha Settings']['Time difference method']]),
                'Digital delay': settings['RossiAlpha Settings']['Digital delay'],
                'Reset time': settings['RossiAlpha Settings']['Reset time'],
                'Bin width': settings['RossiAlpha Settings']['Bin width']}
        # If histogram has not yet been generated or the 
        # current settings do not match those previously used, rerun the plot split
        if self.RAHist['Histogram'] is None or not self.isValid('RAHist', check):
            self.plotSplit(settings, folder)
        # Create a best fit.
        self.createBestFit(settings['Input/Output Settings']['Save figures'],
                           settings['Input/Output Settings']['Save directory'],
                           settings['General Settings']['Show plots'],
                           settings['General Settings']['Verbose iterations'],
                           settings['RossiAlpha Settings'],
                           settings['Line Fitting Settings'],
                           settings['Scatter Plot Settings'],
                           settings['Histogram Visual Settings'],
                           folder)



    def fullFile(self, settings: dict):

        '''Run full Rossi Alpha analysis on a single file.
        
        Inputs:
        - settings: the current runtime settings.'''


        # Run all analysis.
        self.fitSplit(settings)
        # Close all currently open plots.
        pyplot.close()
        # If exporting raw data:
        if settings['Input/Output Settings']['Save raw data'] == True:
            # Initialize variables.
            begin = []
            end = []
            # Construct the beginning and ending bin edges lists.
            for i in range(len(self.RAHist['Histogram'][0].bin_edges)-1):
                begin.append(self.RAHist['Histogram'][0].bin_edges[i])
                end.append(self.RAHist['Histogram'][0].bin_edges[i+1])
            numRanges = len(self.RABestFit['Fit minimum'])
            for i in range(0,len(self.RABestFit['Best fit'])):
                name = settings['Input/Output Settings']['Input file/folder']
                name = name[name.rfind('/')+1:]
                name += ('_' + str(self.RATimeDifs['Time difference method'][int(i/numRanges)])
                       + '_' + str(self.RABestFit['Fit minimum'][i % numRanges])
                       + '-' + str(self.RABestFit['Fit maximum'][i % numRanges]))
                # Export the beginning and ends of bins, measured counts, 
                # Fit counts, residual, fit parameters, and file name.
                self.export({'Bin beginning': (begin,0),
                             'Bin ending': (end,0),
                             'Measured Count': (self.RAHist['Histogram'][int(i/numRanges)].counts,0),
                             'Fit count': (self.RABestFit['Best fit'][i].pred,self.RABestFit['Best fit'][i].fit_index[0][0]),
                             'Percent error': (self.RABestFit['Best fit'][i].residuals,self.RABestFit['Best fit'][i].fit_index[0][0])},
                            [('A', self.RABestFit['Best fit'][i].a),
                             ('A uncertainty', self.RABestFit['Best fit'][i].perr[0]),
                             ('Alpha', self.RABestFit['Best fit'][i].alpha),
                             ('Alpha uncertainty', self.RABestFit['Best fit'][i].perr[1]),
                             ('B', self.RABestFit['Best fit'][i].b),
                             ('Fit minimum',self.RABestFit['Fit minimum'][i % numRanges]),
                             ('Fit maximum',self.RABestFit['Fit maximum'][i % numRanges]),
                             ('Time difference method',self.RATimeDifs['Time difference method'][int(i/numRanges)]),
                             ('Bin width',self.RAHist['Histogram'][int(i/numRanges)].bin_width),
                             ('Input file', settings['Input/Output Settings']['Input file/folder'])],
                            name,
                            settings['Input/Output Settings']['Save directory'])



    def replace_zeroes(self, lst: list):

        '''Replace all zeroes in a list with 
        the average of the non-zero elements.
        
        Inputs:
        - lst: the list to be edited.
        
        Outputs:
        - the edited list.'''
        

        # Create a list of all the non-zero elements and compute their average.
        non_zero_elements = [x for x in lst if x != 0]
        if len(non_zero_elements) != 0:
            average = sum(non_zero_elements) / len(non_zero_elements)
            # For each zero in the list, replace it with the average.
            for i in range(len(lst)):
                if lst[i] == 0:
                    lst[i] = average
            # Return the edited list.
        return lst



    def fullFolder(self, settings: dict, window: Tk = None):

        '''Conduct RossiAlpha analysis on a folder of files.
        
        Inputs:
        - settings: the dictionary that contains all of the runtime settings.
        - window: the gui window, if in gui mode.'''

        RA_hist_array = []
        RA_std_dev = []
        RA_hist_total = []
        time_diff_centers = []
        uncertainties = []
        # Store the original folder pathway.
        original = settings['Input/Output Settings']['Input file/folder']
        # Loop for the number of folders specified.
        for folder in tqdm(range(1, settings['General Settings']['Number of folders'] + 1)):
            # Add the folder number to the input.
            settings['Input/Output Settings']['Input file/folder'] = original + '/' + str(folder)
            # Conduct full analysis.
            if settings['General Settings']['Verbose iterations']:
                self.fitSplit(settings, True)
            else:
                self.plotSplit(settings, True)
            # If this is the first folder, initialize the histogram array.
            if folder == 1:
                for histogram in self.RAHist['Histogram']:
                    RA_hist_array.append(histogram.counts)
            # Otherwise, add the counts to the histogram array.
            else:
                for i in range(0, len(self.RAHist['Histogram'])):
                    RA_hist_array[i] = np.vstack((RA_hist_array[i], self.RAHist['Histogram'][i].counts))
            # Close all open plots.
            pyplot.close()
            # If exporting raw data for individual folders:
            if settings['Input/Output Settings']['Save raw data'] == True and settings['General Settings']['Verbose iterations'] == True:
                # Initialize variables.
                begin = []
                end = []
                # Construct the beginning and ending bin edges lists.
                for i in range(len(self.RAHist['Histogram'][0].bin_edges)-1):
                    begin.append(self.RAHist['Histogram'][0].bin_edges[i])
                    end.append(self.RAHist['Histogram'][0].bin_edges[i+1])
                numRanges = len(self.RABestFit['Fit minimum'])
                for i in range(0,len(self.RABestFit['Best fit'])):
                    name = settings['Input/Output Settings']['Input file/folder']
                    name = name[name[:name.rfind('/')].rfind('/')+1:].replace('/','-')
                    name += ('_' + str(self.RATimeDifs['Time difference method'][int(i/numRanges)])
                        + '_' + str(self.RABestFit['Fit minimum'][i % numRanges])
                        + '-' + str(self.RABestFit['Fit maxmimum'][i % numRanges]))
                    # Export the beginning and ends of bins, measured counts, 
                    # Fit counts, residual, fit parameters, and file name.
                    self.export({'Bin beginning': (begin,0),
                                'Bin ending': (end,0),
                                'Measured Count': (self.RAHist['Histogram'][int(i/numRanges)].counts,0),
                                'Fit count': (self.RABestFit['Best fit'][i].pred,self.RABestFit['Best fit'][i].fit_index[0][0]),
                                'Percent error': (self.RABestFit['Best fit'][i].residuals,self.RABestFit['Best fit'][i].fit_index[0][0])},
                                [('A', self.RABestFit['Best fit'][i].a),
                                ('A uncertainty', self.RABestFit['Best fit'][i].perr[0]),
                                ('Alpha', self.RABestFit['Best fit'][i].alpha),
                                ('Alpha uncertainty', self.RABestFit['Best fit'][i].perr[1]),
                                ('B', self.RABestFit['Best fit'][i].b),
                                ('Fit minimum',self.RABestFit['Fit minimum'][i % numRanges]),
                                ('Fit maximum',self.RABestFit['Fit maximum'][i % numRanges]),
                                ('Time difference method',self.RATimeDifs['Time difference method'][int(i/numRanges)]),
                                ('Bin width',self.RAHist['Histogram'][int(i/numRanges)].bin_width),
                                ('Input file', settings['Input/Output Settings']['Input file/folder'])],
                                'RAFolder' + str(folder),
                                settings['Input/Output Settings']['Save directory'])
            # If in gui mode:
            if window != None:
                # Incremement the progress bar.
                window.children['progress']['value'] += 10
                wait = BooleanVar()
                # After 1 ms, set the dummy variable to True.
                window.after(1, wait.set, True)
                # Wait for the dummy variable to be set, then continue.
                window.wait_variable(wait)
        # Restore the original folder pathway.
        settings['Input/Output Settings']['Input file/folder'] = original
        auto = []
        if isinstance(settings['RossiAlpha Settings']['Fit maximum'], list):
            for i in range(0,len(settings['RossiAlpha Settings']['Fit maximum'])):
                if settings['RossiAlpha Settings']['Fit maximum'][i] == None:
                    settings['RossiAlpha Settings']['Fit maximum'][i] = settings['RossiAlpha Settings']['Reset time']
                    auto.append(True)
                else:
                    auto.append(False)
        else:
            if settings['RossiAlpha Settings']['Fit maximum'] == None:
                settings['RossiAlpha Settings']['Fit maximum'] = [settings['RossiAlpha Settings']['Reset time']]
                auto = True
            else:
                settings['RossiAlpha Settings']['Fit maximum'] = [settings['RossiAlpha Settings']['Fit maximum']]
                auto = False
        if not isinstance(settings['RossiAlpha Settings']['Fit minimum'], list):
            settings['RossiAlpha Settings']['Fit minimum'] = [settings['RossiAlpha Settings']['Fit minimum']]
            min_single = True
        else:
            min_single = False
        for i in range(0, len(RA_hist_array)):
            # Compute the histogram standard deviation and total.
            RA_std_dev.append(np.std(RA_hist_array[i], axis=0, ddof=1))
            RA_hist_total.append(np.sum(RA_hist_array[i], axis=0))
            # Calculate the time difference centers.
            time_diff_centers.append(self.RAHist['Histogram'][i].bin_edges[1:] - np.diff(self.RAHist['Histogram'][i].bin_edges[:2]) / 2)
            # Calculate the uncertainties and replace zeroes.
            uncertainties.append(RA_std_dev[i] * settings['General Settings']['Number of folders'])
            uncertainties[i] = self.replace_zeroes(uncertainties[i])
            # Add the time difference centers and uncertainties to the total histogram.
            RA_hist_total[i] = np.vstack((RA_hist_total[i], time_diff_centers[i], uncertainties[i]))
            for j in range(0, len(settings['RossiAlpha Settings']['Fit minimum'])):
                # Create a fit object for the total histogram.
                thisWeightedFit = fit.Fit_With_Weighting(RA_hist_total[i],
                                                        settings['RossiAlpha Settings']['Fit minimum'][j],
                                                        settings['RossiAlpha Settings']['Fit maximum'][j],
                                                        settings['Input/Output Settings']['Save directory'],
                                                        settings['Line Fitting Settings'], 
                                                        settings['Scatter Plot Settings'])
                # Fit the total histogram with weighting.
                thisWeightedFit.fit_RA_hist_weighting()
                # Plot the total histogram fit.
                thisWeightedFit.plot_RA_and_fit(settings['Input/Output Settings']['Save figures'], 
                                                settings['General Settings']['Show plots'],
                                                settings['RossiAlpha Settings']['Error Bar/Band'],
                                                settings['Input/Output Settings']['Input file/folder'][settings['Input/Output Settings']['Input file/folder'].rfind('/')+1:],
                                                self.RATimeDifs['Time difference method'][i])
                # If saving raw data:
                if settings['Input/Output Settings']['Save raw data'] == True:
                    begin = []
                    end = []
                    # Fill out the beginning and ending of each bin.
                    halfWidth = settings['RossiAlpha Settings']['Bin width']/2
                    for k in range(len(thisWeightedFit.bin_centers)):
                        begin.append(thisWeightedFit.bin_centers[k]-halfWidth)
                        end.append(thisWeightedFit.bin_centers[k]+halfWidth)
                    name = settings['Input/Output Settings']['Input file/folder']
                    name = name[name.rfind('/')+1:]
                    name += ('_' + str(self.RATimeDifs['Time difference method'][i % len(self.RATimeDifs['Time difference method'])] )
                        + '_' + str(settings['RossiAlpha Settings']['Fit minimum'][j])
                        + '-' + str(settings['RossiAlpha Settings']['Fit maximum'][j]))
                    # Export the time differences, Total counts, 
                    # uncertainties, Fit counts, number of folders, 
                    # folder name, and fit parameters to a .csv.
                    self.export({'Bin beginning': (begin,0),
                                 'Bin ending': (end,0),
                                 'Total count': (thisWeightedFit.hist,0),
                                 'Uncertainty': (thisWeightedFit.uncertainties,0),
                                 'Fit count': (thisWeightedFit.pred, thisWeightedFit.fit_index[0][0]),
                                 'Percent Error': (thisWeightedFit.residuals, thisWeightedFit.fit_index[0][0])},
                                [('A', thisWeightedFit.a),
                                 ('A uncertainty', thisWeightedFit.perr[0]),
                                ('Alpha', thisWeightedFit.alpha),
                                ('Alpha uncertainty', thisWeightedFit.perr[1]),
                                ('B', thisWeightedFit.b),
                                ('Fit minimum',settings['RossiAlpha Settings']['Fit minimum'][j]),
                                ('Fit maximum',settings['RossiAlpha Settings']['Fit maximum'][j]),
                                ('Time difference method',self.RATimeDifs['Time difference method'][i % len(self.RATimeDifs['Time difference method'])]),
                                ('Bin width',settings['RossiAlpha Settings']['Bin width']),
                                ('Input file', settings['Input/Output Settings']['Input file/folder'])],
                                name,
                                settings['Input/Output Settings']['Save directory'])
        if isinstance(auto, bool):
            if auto:
                settings['RossiAlpha Settings']['Fit maximum'] = None
            else:
                settings['RossiAlpha Settings']['Fit maximum'] = settings['RossiAlpha Settings']['Fit maximum'][0]
        else:
            for i in range(0,len(auto)):
                if auto[i]:
                    settings['RossiAlpha Settings']['Fit maximum'][i] = None
        if min_single:
            settings['RossiAlpha Settings']['Fit minimum'] = settings['RossiAlpha Settings']['Fit minimum'][0]
        # Close all open plots.
        pyplot.close()

    def cohnAlphaFullFolder(self,
                         input:str,
                         output:str,
                         show:bool,
                         save:bool,
                         caSet:dict,
                         sps:dict,
                         lfs:dict,
                         scatter_plot_settings:dict,):


        for file in os.listdir(input):
            inputFile = input + '/' + file
            self.conductCohnAlpha(inputFile, output, show, save, caSet, sps, lfs, scatter_plot_settings)

