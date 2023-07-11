from RossiAlpha import analyzeAll as mn
from RossiAlpha import fitting as fit
from RossiAlpha import plots as plt
from RossiAlpha import timeDifs as dif
import Event as evt
import lmxReader as lmx
from CohnAlpha import CohnAlpha as ca
import numpy as np

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
        
    def raAll(self, single: bool, settings: dict):
        if single:
            self.time_difs, self.histogram, self.best_fit = mn.analyzeAllType1(settings)
            self.input = settings['Input/Output Settings']['Input file/folder']
            self.method = settings['RossiAlpha Settings']['Time difference method']
        else:
            mn.analyzeAllType2(settings)

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
            
    def createBestFit(self, cutoff: int, method: str, gen: dict, output: str, line: dict, res: dict, hist: dict):
        self.best_fit = fit.RossiHistogramFit(self.histogram.counts, self.histogram.bin_centers, cutoff, method, gen['Fit range'])
        self.best_fit.fit_and_residual(gen['Save figures'], output, gen['Show plots'], line, res, hist)