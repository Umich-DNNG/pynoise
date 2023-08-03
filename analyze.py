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



class Analyzer:

    '''The class that runs analysis. Can be used 
    in either terminal or gui implementation.'''


    def __init__(self):

        '''The initializer for the Analyzer object.'''


        # Initialize the variables used to determine whether 
        # or not certain elements have to be recreated.
        self.RATimeDifs = {'Time differences': None,
                           'Input file/folder': None,
                           'Number of folders': None,
                           'Sort data': None,
                           'Time difference method': None,
                           'Digital delay': None,
                           'Reset time': None}
        self.RAHist = {'Histogram': None,
                       'Bin width': None}
        self.RABestFit = {'Best fit': None,
                          'Fit range': None}
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
               method: str, 
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


        # Get the current time for file naming.
        curTime = time.localtime()
        # Name the file appropriately with the method name and current time.
        fileName = (output + '/' + method +
                    ('(0' if curTime.tm_mon < 10 else '(') + str(curTime.tm_mon) +
                    ('-0' if curTime.tm_mday < 10 else '-') + str(curTime.tm_mday) +
                    ('-0' if curTime.tm_year%100 < 10 else '-') + str(curTime.tm_year%100) +
                    ('@0' if curTime.tm_hour < 10 else '@') + str(curTime.tm_hour) +
                    (':0' if curTime.tm_min < 10 else ':') + str(curTime.tm_min) +
                    (':0' if curTime.tm_sec < 10 else ':') + str(curTime.tm_sec) +
                    ').csv')
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


        # Load the values from the specified file into an NP array.
        values = np.loadtxt(input, usecols=(0,3), max_rows=2000000, dtype=float)
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
        

        # Load the data according to its file type.
        # TODO: Add folder modular support.
        # Create an empty data list.
        data = []
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
        # Create the time difference object and calculate 
        # the time differences with the given settings.
        self.RATimeDifs['Time differences'] = dif.timeDifCalcs(data, reset, method, delay)
        self.RATimeDifs['Time differences'] = self.RATimeDifs['Time differences'].calculateTimeDifsFromEvents()
        # Save the current relevant settings.
        self.RATimeDifs['Input file/folder'] = io['Input file/folder']
        self.RATimeDifs['Sort data'] = sort
        self.RATimeDifs['Number of folders'] = folder
        self.RATimeDifs['Time difference method'] = method
        self.RATimeDifs['Digital delay'] = delay
        self.RATimeDifs['Reset time'] = reset
        


    def createPlot(self,
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
        

        # Create a RossiHistogram object and plot the data with the given settings.
        self.RAHist['Histogram'] = plt.RossiHistogram(self.RATimeDifs['Time differences'], width, reset)
        self.RAHist['Histogram'].plot(save, show, output, vis, folder, verbose)
        self.RAHist['Bin width'] = width



    def calculateTimeDifsAndPlot(self,
                                 io:dict,
                                 gen:dict,
                                 raGen:dict,
                                 raVis:dict,
                                 folder:bool = False):

        '''Simultaneously calculate the time 
        differences and construct a Rossi Histogram.
        
        Inputs:
        - io: the Input/Output Settings dictionary.
        - gen: the General Settings dictionary.
        - raGen: the RossiAlpha Settings dictionary.
        - raVis: the Histogram Visual Settings dictionary.
        - folder: whether or not this is for folder analysis.'''


        # Reset the time differences.
        self.RATimeDifs['Time differences'] = None
        # Create an empty data list.
        data = []
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
        # Construct a time differences object with the given settings.
        thisTimeDifCalc = dif.timeDifCalcs(data, raGen['Reset time'], raGen['Time difference method'], raGen['Digital delay'])
        # Simulatenously calculate the time differences and bin them.
        self.RAHist['Histogram'], counts, bin_centers, bin_edges = thisTimeDifCalc.calculateTimeDifsAndBin(raGen['Bin width'],
                                                                                                 io['Save figures'],
                                                                                                 gen['Show plots'],
                                                                                                 io['Save directory'],
                                                                                                 raVis,
                                                                                                 folder,
                                                                                                 gen['Verbose iterations'])
        # Save the input and method of analysis.
        self.RATimeDifs['Input file/folder'] = io['Input file/folder']
        self.RATimeDifs['Time difference method'] = raGen['Time difference method']



    def plotSplit(self, settings: dict, folder: bool = False):

        '''Determines what combination of time difference 
        calculation and Rossi Histogram constructing to do.
        
        Inputs:
        - settings: the current runtime settings.
        - folder: whether or not this is for folder analysis.'''


        # Create a dictionary of the current relevant settings.
        check = {'Input file/folder': settings['Input/Output Settings']['Input file/folder'],
                'Sort data': settings['General Settings']['Sort data'],
                'Time difference method': settings['RossiAlpha Settings']['Time difference method'],
                'Digital delay': settings['RossiAlpha Settings']['Digital delay'],
                'Reset time': settings['RossiAlpha Settings']['Reset time']}
        # Get the name of the input.
        name = settings['Input/Output Settings']['Input file/folder']
        name = name[name.rfind('/')+1:]
        # If in folder mode, add the number of folders setting.
        if name.count('.') == 0:
            check['Number of folders'] = settings['General Settings']['Number of folders']
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
                self.createPlot(settings['RossiAlpha Settings']['Bin width'],
                                settings['RossiAlpha Settings']['Reset time'],
                                settings['Input/Output Settings']['Save figures'],
                                settings['General Settings']['Show plots'],
                                settings['Input/Output Settings']['Save directory'],
                                settings['Histogram Visual Settings'],
                                folder,
                                settings['General Settings']['Verbose iterations'])
        # Otherwise, just create a Rossi Histogram plot. 
        else:
            self.createPlot(settings['RossiAlpha Settings']['Bin width'],
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
                      index:int = None):
        
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
        - index: the folder index, if applicable.'''
        
        if ra['Fit range'][1] == 'Reset time':
            ra['Fit range'][1] = ra['Reset time']
            auto = True
        else:
            auto = False
        # Construct a RossiHistogramFit object and plot it with the given settings.
        self.RABestFit['Best fit'] = fit.RossiHistogramFit(self.RAHist['Histogram'].counts,
                                              self.RAHist['Histogram'].bin_centers,
                                              ra['Time difference method'],
                                              ra['Fit range'])
        self.RABestFit['Best fit'].fit_and_residual(save,
                                       output,
                                       show,
                                       line,
                                       res,
                                       hist,
                                       index,
                                       verbose)
        if auto:
            ra['Fit range'][1] = 'Reset time'



    def fitSplit(self, settings:dict, folder:bool = False):

        '''Determines what combination of time difference 
        calculation and Rossi Histogram constructing to do.
        
        Inputs:
        - settings: the current runtime settings.
        - folder: whether or not this is for folder analysis.'''


        # Create a dictionary of the current relevant settings.
        check = {'Input file/folder': settings['Input/Output Settings']['Input file/folder'],
                'Sort data': settings['General Settings']['Sort data'],
                'Time difference method': settings['RossiAlpha Settings']['Time difference method'],
                'Digital delay': settings['RossiAlpha Settings']['Digital delay'],
                'Reset time': settings['RossiAlpha Settings']['Reset time'],
                'Bin width': settings['RossiAlpha Settings']['Bin width']}
        # If in folder mode, add the number of folders setting.
        if folder:
            check['Number of folders'] = settings['General Settings']['Number of folders']
            index = int(settings['Input/Output Settings']['Input file/folder'][settings['Input/Output Settings']['Input file/folder'].rfind('/')+1:])
        else:
            index = None
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
                           index)



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
            resStart = 0
            # Continue increasing the residual/prediction starting index 
            # while the minimum cutoff is greater than the current bin center.
            while settings['RossiAlpha Settings']['Fit range'][0] > self.RAHist['Histogram'].bin_centers[resStart]:
                resStart += 1
            # Construct the beginning and ending bin edges lists.
            for i in range(len(self.RAHist['Histogram'].bin_edges)-1):
                begin.append(self.RAHist['Histogram'].bin_edges[i])
                end.append(self.RAHist['Histogram'].bin_edges[i+1])
            # Export the beginning and ends of bins, measured counts, 
            # predicted counts, residual, fit parameters, and file name.
            self.export({'Bin beginning': (begin,0),
                        'Bin ending': (end,0),
                        'Measured Count': (self.RAHist['Histogram'].counts,0),
                        'Predicted Count': (self.RABestFit['Best fit'].pred,resStart),
                        'Residual': (self.RABestFit['Best fit'].residuals,resStart)},
                        [('A', self.RABestFit['Best fit'].a),
                        ('B', self.RABestFit['Best fit'].b),
                        ('Alpha', self.RABestFit['Best fit'].alpha),
                        ('Input file', settings['Input/Output Settings']['Input file/folder'])],
                        'RAFile',
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


        # Store the original folder pathway.
        original = settings['Input/Output Settings']['Input file/folder']
        # Loop for the number of folders specified.
        for folder in tqdm(range(1, settings['General Settings']['Number of folders'] + 1)):
            # Add the folder number to the input.
            settings['Input/Output Settings']['Input file/folder'] = original + '/' + str(folder)
            # Conduct full analysis.
            self.fitSplit(settings, True)
            # If this is the first folder, initialize the histogram array.
            if folder == 1:
                RA_hist_array = self.RAHist['Histogram'].counts
            # Otherwise, add the counts to the histogram array.
            else:
                RA_hist_array = np.vstack((RA_hist_array, self.RAHist['Histogram'].counts))
            # Close all open plots.
            pyplot.close()
            # If exporting raw data for individual folders:
            if settings['Input/Output Settings']['Save raw data'] == True and settings['General Settings']['Verbose iterations'] == True:
                # Initialize variables.
                begin = []
                end = []
                resStart = 0
                # Continue increasing the residual/prediction starting index 
                # while the minimum cutoff is greater than the current bin center.
                while settings['RossiAlpha Settings']['Fit range'][0] > self.RAHist['Histogram'].bin_centers[resStart]:
                    resStart += 1
                # Construct the beginning and ending bin edges lists.
                for i in range(len(self.RAHist['Histogram'].bin_edges)-1):
                    begin.append(self.RAHist['Histogram'].bin_edges[i])
                    end.append(self.RAHist['Histogram'].bin_edges[i+1])
                # Export the beginning and ends of bins, measured counts, 
                # predicted counts, residual, fit parameters, and file name.
                self.export({'Bin beginning': (begin,0),
                            'Bin ending': (end,0),
                            'Measured Count': (self.RAHist['Histogram'].counts,0),
                            'Predicted Count': (self.RABestFit['Best fit'].pred,resStart),
                            'Residual': (self.RABestFit['Best fit'].residuals,resStart)},
                            [('A', self.RABestFit['Best fit'].a),
                            ('B', self.RABestFit['Best fit'].b),
                            ('Alpha', self.RABestFit['Best fit'].alpha),
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
        # Compute the histogram standard deviation and total.
        RA_std_dev = np.std(RA_hist_array, axis=0, ddof=1)
        RA_hist_total = np.sum(RA_hist_array, axis=0)
        # Calculate the time difference centers.
        time_diff_centers = self.RAHist['Histogram'].bin_edges[1:] - np.diff(self.RAHist['Histogram'].bin_edges[:2]) / 2
        # Calculate the uncertainties and replace zeroes.
        uncertainties = RA_std_dev * settings['General Settings']['Number of folders']
        uncertainties = self.replace_zeroes(uncertainties)
        # Add the time difference centers and uncertainties to the total histogram.
        RA_hist_total = np.vstack((RA_hist_total, time_diff_centers, uncertainties))
        if settings['RossiAlpha Settings']['Fit range'][1] == 'Reset time':
            settings['RossiAlpha Settings']['Fit range'][1] = settings['RossiAlpha Settings']['Reset time']
            auto = True
        else:
            auto = False
        # Create a fit object for the total histogram.
        thisWeightedFit = fit.Fit_With_Weighting(RA_hist_total,
                                                 settings['RossiAlpha Settings']['Fit range'],
                                                 settings['Input/Output Settings']['Save directory'],
                                                 settings['Line Fitting Settings'], 
                                                 settings['Scatter Plot Settings'])
        # Fit the total histogram with weighting.
        thisWeightedFit.fit_RA_hist_weighting()
        # Plot the total histogram fit.
        thisWeightedFit.plot_RA_and_fit(settings['Input/Output Settings']['Save figures'], 
                                        settings['General Settings']['Show plots'],
                                        settings['RossiAlpha Settings']['Error Bar/Band'])
        if auto:
            settings['RossiAlpha Settings']['Fit range'][1] = 'Reset time'
        # Close all open plots.
        pyplot.close()
        # If saving raw data:
        if settings['Input/Output Settings']['Save raw data'] == True:
            begin = []
            end = []
            predStart = 0
            # Find the starting index of the prediction data.
            while settings['RossiAlpha Settings']['Fit range'][0] > time_diff_centers[predStart]:
                predStart += 1
            # Fill out the beginning and ending of each bin.
            # TODO: May be able to delete this.
            for i in range(len(self.RAHist['Histogram'].bin_edges)-1):
                begin.append(self.RAHist['Histogram'].bin_edges[i])
                end.append(self.RAHist['Histogram'].bin_edges[i+1])
            # If using verbose mode, mark this as the final file.
            if settings['General Settings']['Verbose iterations'] == True:
                filename = 'RAFolderFull'
            # Otherwise, keep the shortened name.
            else:
                filename = 'RAFolder'
            # Export the time differences, weighted counts, 
            # uncertainties, predicted counts, number of folders, 
            # folder name, and fit parameters to a .csv.
            self.export({'Time difference': (time_diff_centers,0),
                         'Weighted Count': (thisWeightedFit.hist,0),
                         'Uncertainty': (uncertainties,0),
                         'Predicted Count': (thisWeightedFit.pred,predStart)},
                        [('A', thisWeightedFit.a),
                         ('B', thisWeightedFit.b),
                         ('Alpha', thisWeightedFit.alpha),
                         ('Input folder', settings['Input/Output Settings']['Input file/folder']),
                         ('Number of folders', settings['General Settings']['Number of folders'])],
                        filename,
                        settings['Input/Output Settings']['Save directory'])