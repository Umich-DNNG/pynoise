'''The object used for analyzing data.'''

import os
import numpy as np
import matplotlib.pyplot as pyplot
import Event as evt
import lmxReader as lmx
from RossiAlpha import fitting as fit
from RossiAlpha import plots as plt
from RossiAlpha import timeDifs as dif
from CohnAlpha import CohnAlpha as ca
from FeynmanY import feynman as fey
from tkinter import ttk
from tkinter import *

class Analyzer:

    def __init__(self):

        '''The initializer for the Analyzer object.'''

        # Initialize the variables used to determine whether 
        # or not RossiAlpha elements have to be recreated.
        self.time_difs: dif.timeDifCalcs = None
        self.histogram: plt.RossiHistogram = None
        self.best_fit: fit.RossiHistogramFit = None
        self.input: str = None
        self.method: str = None

    def runFeynmanY(self, io: dict, fy: dict, show: bool, save: bool, hvs: dict, window: Tk = None):
        
        '''Run FeynmanY analysis for varying tau values.
        Plots each tau value and estimates alpha.
        
        Requires:
        - io: the Input/Output Settings dictionary.
        - fy: the FeynmanY Settings dictionary.
        - show: whether or not to show plots.
        - save: whether or not to save plots.
        - hvs: the Histogram Visual Settings dictionary.'''
        
        yValues = []
        y2Values = []
        tValues = []
        tValues.extend(range(fy['Tau range'][0], fy['Tau range'][1]+1, fy['Increment amount']))
        # Load in the data and sort it.
        data = evt.createEventsListFromTxtFile(io['Input file/folder'], io['Time column'], io['Channels column'])
        data.sort(key=lambda Event: Event.time)
        # Adjust each measurement by making
        # the earliest measurement time 0.
        min = data[0].time
        for entry in data:
            entry.time -= min
        # DEBUG LINE
        print('Tau\tY\tY2')
        if window is not None:
            window.children['progress']['value'] += 1
            wait = BooleanVar()
            # After 1 ms, set the dummy variable to True.
            window.after(1, wait.set, True)
            # Wait for the dummy variable to be set, then continue.
            window.wait_variable(wait)
        # For each tau:
        for tau in tValues:
            # Convert the data into bin frequency counts.
            counts = fey.randomCounts(data, tau)
            # Compute the variance to mean for this 
            # tau value and add it to the list.
            y, y2 = fey.computeVarToMean(counts, tau)
            yValues.append(y)
            y2Values.append(y2)
            # DEBUG LINE
            print(str(tau) + '\t' + str(y) + '\t' + str(y2))   
            if window is not None:
                window.children['progress']['value'] += 1
                wait = BooleanVar()
                # After 1 ms, set the dummy variable to True.
                window.after(1, wait.set, True)
                # Wait for the dummy variable to be set, then continue.
                window.wait_variable(wait)
        fey.plot(tValues,yValues, save, show, io['Save directory'])
        fey.plot(tValues,y2Values, save, show, io['Save directory'])

    def conductCohnAlpha(self, input: str, output: str, show: bool, save: bool, caGen: dict, caVis: dict):

        '''Runs Cohn Alpha analysis.
        
        Requires:
        - input: the file path.
        - output: the save directory.
        - show: whether or not to show plots.
        - save: whether or not to save plots.
        - caGen: the CohnAlpha Settings dictionary.
        - caVis: the CohnAlpha Visual Settings dictionary.'''

        # Load the values from the specified file into an NP array.
        values = np.loadtxt(input, usecols=(0,3), max_rows=2000000, dtype=float)
        # Create a Cohn Alpha object with the given settings.
        CA_Object = ca.CohnAlpha(values,
                                 caGen['Clean pulses switch'], 
                                 caGen['Dwell time'],
                                 caGen['Meas time range'])
        # Conduct Cohn Alpha analysis with the given settings.
        CA_Object.conductCohnAlpha(show,
                                   save,
                                   output,
                                   caVis['Legend Label'],
                                   caVis['Annotation Font Weight'],
                                   caVis['Annotation Color'],
                                   caVis['Annotation Background Color'])

    def createTimeDifs(self, io: dict, sort: bool, reset: float, method: str, delay: int):
        
        '''Create Rossi Alpha time differences.
        
        Requires:
        - io: the Input/Output Settings dictionary.
        - sort: whether or not to sort the data.
        - reset: the reset time.
        - method: the time difference method.
        - delay: the digital delay.'''
        
        # Load the data according to its file type.
        if io['Input file/folder'].endswith(".txt"):
            data = evt.createEventsListFromTxtFile(io['Input file/folder'], io['Time column'], io['Channels column'])
        elif io['Input file/folder'].endswith(".lmx"):
            data = lmx.readLMXFile(io['Input file/folder'])
        # If file type isn't valid, throw an error.
        else:
            return ValueError
        # Sort the data if applicable.
        if sort:
            data.sort(key=lambda Event: Event.time)
        # Create the time difference object and calculate 
        # the time differences with the given settings.
        self.time_difs = dif.timeDifCalcs(data, reset, method, delay)
        self.time_difs = self.time_difs.calculateTimeDifsFromEvents()
        # Save the input and method of analysis.
        self.input = io['Input file/folder']
        self.method = method

    def createPlot(self, width: int, reset: float, save: bool, show: bool, output: str, vis: dict):
        
        '''Create a Rossi Alpha histogram. Assumes 
        that time differences are already calculated.
        
        Requires:
        - width: the bin width.
        - reset: the reset time.
        - save: whether or not to save plots.
        - show: whether or not to show plots.
        - output: the save directory.
        - vis: the Histogram Visual Settings dictionary.'''
        
        # Create a RossiHistogram object and plot the data with the given settings.
        self.histogram = plt.RossiHistogram(self.time_difs, width, reset)
        self.histogram.plot(save, show, output, vis)

    def calculateTimeDifsAndPlot(self, io: dict, gen: dict, raGen: dict, raVis: dict):

        '''Simultaneously calculate the time 
        differences and construct a Rossi Histogram.
        
        Requires:
        - io: the Input/Output Settings dictionary.
        - gen: the General Settings dictionary.
        - raGen: the RossiAlpha Settings dictionary.
        - raVis: the Histogram Visual Settings dictionary.'''

        # Reset the time differences.
        self.time_difs = None
        # Load the data according to its file type.
        if io['Input file/folder'].endswith(".txt"):
            data = evt.createEventsListFromTxtFile(io['Input file/folder'], io['Time column'], io['Channels column'])
        elif io['Input file/folder'].endswith(".lmx"):
            data =  lmx.readLMXFile(io['Input file/folder'])
        # If file type isn't valid, throw an error.
        else:
            return ValueError
        # Sort the data if applicable.
        if gen['Sort data']:
            data.sort(key=lambda Event: Event.time)
        # Construct a time differences object with the given settings.
        thisTimeDifCalc = dif.timeDifCalcs(data, raGen['Reset time'], raGen['Time difference method'], raGen['Digital delay'])
        # Simulatenously calculate the time differences and bin them.
        self.histogram, counts, bin_centers, bin_edges = thisTimeDifCalc.calculateTimeDifsAndBin(raGen['Bin width'],
                                                                                                 gen['Save figures'],
                                                                                                 gen['Show plots'],
                                                                                                 io['Save directory'],
                                                                                                 raVis)
        # Save the input and method of analysis.
        self.input = io['Input file/folder']
        self.method = raGen['Time difference method']

    def plotSplit(self, settings: dict):

        '''Determines what combination of time difference 
        calculation and Rossi Histogram constructing to do.
        
        Requires:
        - settings: the current runtime settings.'''

        # If time differences have not yet been calculated or the 
        # current method/input file do not match those previously used:
        if self.time_difs is None or (not (self.method == settings['RossiAlpha Settings']['Time difference method']
                                      and self.input == settings['Input/Output Settings']['Input file/folder'])):
            # If applicable, combine the time difference calculation and binning.
            if (settings['RossiAlpha Settings']['Combine Calc and Binning']):
                self.calculateTimeDifsAndPlot(settings['Input/Output Settings'],
                                              settings['General Settings'],
                                              settings['RossiAlpha Settings'],
                                              settings['Histogram Visual Settings'])
            # Otherwise, create the time differences and histogram separately.
            else:
                self.createTimeDifs(settings['Input/Output Settings'],
                                    settings['General Settings']['Sort data'],
                                    settings['RossiAlpha Settings']['Reset time'],
                                    settings['RossiAlpha Settings']['Time difference method'],
                                    settings['RossiAlpha Settings']['Digital delay'])
                self.createPlot(settings['RossiAlpha Settings']['Bin width'],
                                settings['RossiAlpha Settings']['Reset time'],
                                settings['General Settings']['Save figures'],
                                settings['General Settings']['Show plots'],
                                settings['Input/Output Settings']['Save directory'],
                                settings['Histogram Visual Settings'])
        # Otherwise, just create a Rossi Histogram plot. 
        else:
            self.createPlot(settings['RossiAlpha Settings']['Bin width'],
                            settings['RossiAlpha Settings']['Reset time'],
                            settings['General Settings']['Save figures'],
                            settings['General Settings']['Show plots'],
                            settings['Input/Output Settings']['Save directory'],
                            settings['Histogram Visual Settings'])
            
    def createBestFit(self, cutoff: int, method: str, gen: dict, output: str, line: dict, res: dict, hist: dict, index = None):
        
        '''Create a Rossi Histogram line of best fit and residual plot.
        
        Requires:
        - cutoff: the minimum cutoff.
        - method: the time difference method.
        - gen: the General Settings dictionary.
        - output: the save directory.
        - line: the Line Fitting Settings dictionary.
        - res: the Residual Plot Settings dictionary.
        - hist: the Histogram Visual Settings dictionary.
        
        Optional:
        - index: the folder index, if applicable.'''
        
        # Construct a RossiHistogramFit object and plot it with the given settings.
        self.best_fit = fit.RossiHistogramFit(self.histogram.counts,
                                              self.histogram.bin_centers,
                                              cutoff,
                                              method,
                                              gen['Fit range'])
        self.best_fit.fit_and_residual(gen['Save figures'],
                                       output,
                                       gen['Show plots'],
                                       line,
                                       res,
                                       hist,
                                       index)

    def fullFile(self, settings: dict):

        '''Run full Rossi Alpha analysis on a single file.
        
        Requires:
        - settings: the current runtime settings.'''

        # Run the plot split.
        self.plotSplit(settings)
        # Create a best fit for the data.
        self.createBestFit(settings['RossiAlpha Settings']['Minimum cutoff'],
                           settings['RossiAlpha Settings']['Time difference method'],
                           settings['General Settings'],
                           settings['Input/Output Settings']['Save directory'],
                           settings['Line Fitting Settings'],
                           settings['Residual Plot Settings'],
                           settings['Histogram Visual Settings'])
        # Close all currently open plots.
        pyplot.close()

    def replace_zeroes(self, lst: list):

        '''Replace all zeroes in a list with 
        the average of the non-zero elements.
        
        Requires:
        - lst: the list to be edited.'''

        # Create a list of all the non-zero elements and compute their average.
        non_zero_elements = [x for x in lst if x != 0]
        average = sum(non_zero_elements) / len(non_zero_elements)
        # For each zero in the list, replace it with the average.
        for i in range(len(lst)):
            if lst[i] == 0:
                lst[i] = average
        # Return the edited list.
        return lst

    def fullFolder(self, settings: dict):

        '''Conduct RossiAlpha analysis on a folder of files.
        
        Requires:
        - settings: the dictionary that contains all of the runtime settings.'''

        # Store the original folder pathway.
        original = settings['Input/Output Settings']['Input file/folder']
        # Loop for the number of folders specified.
        for folder in range(1, settings['General Settings']['Number of folders'] + 1):
            # For each file in the specified folder:
            for filename in os.listdir(original + "/" + str(folder)):
                # If this is the desired file:
                if filename.endswith("n_allch.txt"):
                    # Change the input file to this file.
                    settings['Input/Output Settings']['Input file/folder'] = original + "/" + str(folder) + "/" + filename
                    # Conduct the plot split.
                    self.plotSplit(settings)
                    # If this is the first folder, initialize the histogram array.
                    if folder == 1:
                        RA_hist_array = self.histogram.counts
                    # Otherwise, add the counts to the histogram array.
                    else:
                        RA_hist_array = np.vstack((RA_hist_array, self.histogram.counts))
                    # Create a best fit graph.
                    self.createBestFit(settings['RossiAlpha Settings']['Minimum cutoff'],
                                       settings['RossiAlpha Settings']['Time difference method'],
                                       settings['General Settings'],
                                       settings['Input/Output Settings']['Save directory'],
                                       settings['Line Fitting Settings'],
                                       settings['Residual Plot Settings'],
                                       settings['Histogram Visual Settings'],
                                       folder)
                    pyplot.close()
                    # Break to the next folder.
                    break
        # Restore the original folder pathway.
        settings['Input/Output Settings']['Input file/folder'] = original
        # Compute the histogram standard deviation and total.
        RA_std_dev = np.std(RA_hist_array, axis=0, ddof=1)
        RA_hist_total = np.sum(RA_hist_array, axis=0)
        # Calculate the time difference centers.
        time_diff_centers = self.histogram.bin_edges[1:] - np.diff(self.histogram.bin_edges[:2]) / 2
        # Calculate the uncertainties and replace zeroes.
        uncertainties = RA_std_dev * settings['General Settings']['Number of folders']
        uncertainties = self.replace_zeroes(uncertainties)
        # Add the time difference centers and uncertainties to the total histogram.
        RA_hist_total = np.vstack((RA_hist_total, time_diff_centers, uncertainties))
        # Create a fit object for the total histogram.
        thisWeightedFit = fit.Fit_With_Weighting(RA_hist_total,
                                                 settings['RossiAlpha Settings']['Minimum cutoff'],
                                                 settings['General Settings'],
                                                 settings['Input/Output Settings']['Save directory'],
                                                 settings['Line Fitting Settings'], 
                                                 settings['Residual Plot Settings'])
        # Fit the total histogram with weighting.
        thisWeightedFit.fit_RA_hist_weighting()
        # Plot the total histogram fit.
        thisWeightedFit.plot_RA_and_fit(settings['General Settings']['Save figures'], 
                                        settings['General Settings']['Show plots'],
                                        settings['RossiAlpha Settings']['Error Bar/Band'])
        # Close all open plots.
        pyplot.close()