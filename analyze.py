from RossiAlpha import fitting as fit
from RossiAlpha import plots as plt
from RossiAlpha import timeDifs as dif
import Event as evt
import lmxReader as lmx
from CohnAlpha import CohnAlpha as ca
import numpy as np
import matplotlib.pyplot as pyplot
import os

class Analyzer:

    def __init__(self):
        self.time_difs: dif.timeDifCalcs = None
        self.histogram: plt.RossiHistogram = None
        self.best_fit: fit.RossiHistogramFit = None
        self.input: str = None
        self.method: str = None

    def conductCohnAlpha(self, input: str, output: str, show: bool, save: bool, caGen: dict, caVis: dict):
        values = np.loadtxt(input, usecols=(0,3), max_rows=2000000, dtype=float)
        CA_Object = ca.CohnAlpha(values,
                                 caGen['Clean pulses switch'], 
                                 caGen['Dwell time'],
                                 caGen['Meas time range'])
        CA_Object.conductCohnAlpha(show,
                                   save,
                                   output,
                                   caVis['Legend Label'],
                                   caVis['Annotation Font Weight'],
                                   caVis['Annotation Color'],
                                   caVis['Annotation Background Color'])

    def createTimeDifs(self, io: dict, sort: bool, reset: float, method: str, delay: int):
        if io['Input file/folder'].endswith(".txt"):
            data = evt.createEventsListFromTxtFile(io['Input file/folder'], io['Time column'], io['Channels column'])
        elif io['Input file/folder'].endswith(".lmx"):
            data = lmx.readLMXFile(io['Input file/folder'])
        else:
            return ValueError
        if sort:
            data.sort(key=lambda Event: Event.time)
        self.time_difs = dif.timeDifCalcs(data, reset, method, delay)
        self.time_difs = self.time_difs.calculateTimeDifsFromEvents()
        self.input = io['Input file/folder']
        self.method = method

    def createPlot(self, width: int, reset: float, save: bool, show: bool, output: str, vis: dict):
        self.histogram = plt.RossiHistogram(self.time_difs, width, reset)
        self.histogram.plot(save, show, output, vis)

    def calculateTimeDifsAndPlot(self, io: dict, gen: dict, raGen: dict, raVis: dict):
        self.time_difs = None
        if io['Input file/folder'].endswith(".txt"):
            data = evt.createEventsListFromTxtFile(io['Input file/folder'], io['Time column'], io['Channels column'])
        elif io['Input file/folder'].endswith(".lmx"):
            data =  lmx.readLMXFile(io['Input file/folder'])
        else:
            return ValueError
        if gen['Sort data']:
            data.sort(key=lambda Event: Event.time)
        thisTimeDifCalc = dif.timeDifCalcs(data, 
                                           raGen['Reset time'], 
                                           raGen['Time difference method'],
                                           raGen['Digital delay'])
        self.histogram, counts, bin_centers, bin_edges = thisTimeDifCalc.calculateTimeDifsAndBin(raGen['Bin width'],
                                                                                                 gen['Save figures'],
                                                                                                 gen['Show plots'],
                                                                                                 io['Save directory'],
                                                                                                 raVis)
        self.input = io['Input file/folder']
        self.method = raGen['Time difference method']

    def plotSplit(self, settings: dict):
        if self.time_difs is None or (not (self.method == settings['RossiAlpha Settings']['Time difference method']
                                      and self.input == settings['Input/Output Settings']['Input file/folder'])):
            if (settings['RossiAlpha Settings']['Combine Calc and Binning']):
                self.calculateTimeDifsAndPlot(settings['Input/Output Settings'],
                                              settings['General Settings'],
                                              settings['RossiAlpha Settings'],
                                              settings['Histogram Visual Settings'])
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
        else:
            self.createPlot(settings['RossiAlpha Settings']['Bin width'],
                            settings['RossiAlpha Settings']['Reset time'],
                            settings['General Settings']['Save figures'],
                            settings['General Settings']['Show plots'],
                            settings['Input/Output Settings']['Save directory'],
                            settings['Histogram Visual Settings'])
            
    def createBestFit(self, cutoff: int, method: str, gen: dict, output: str, line: dict, res: dict, hist: dict, index = None):
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
        self.plotSplit(settings)
        self.createBestFit(settings['RossiAlpha Settings']['Minimum cutoff'],
                           settings['RossiAlpha Settings']['Time difference method'],
                           settings['General Settings'],
                           settings['Input/Output Settings']['Save directory'],
                           settings['Line Fitting Settings'],
                           settings['Residual Plot Settings'],
                           settings['Histogram Visual Settings'])
        pyplot.close()

    def replace_zeroes(self, lst: list):
        non_zero_elements = [x for x in lst if x != 0]
        average = sum(non_zero_elements) / len(non_zero_elements)
        for i in range(len(lst)):
            if lst[i] == 0:
                lst[i] = average
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
        pyplot.close()