# v000: 12/17/2022: unmodified from bitbucket
# v001: 12/17/2022: added ability to save plots
# v002: 12/17/2022: added ability to save residuals


# standard imports
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter
from typing import List
from tqdm import tqdm

# local imports
from lmx.feynman.FeynmanHistogram import FeynmanHistogram

np.seterr(over="ignore", invalid="ignore")


def log_one(tau, a, b):
    """Callable equation for a single log feynman fit
       a * (1 - (1 - np.exp(-b * tau)) / (b * tau))

        Arguments:
            tau: Gatewidths
            a: Fitting Parameter (representative of plateau value)
            b: Fitting Parameter (representative of lambda value)

    Returns: Distribution for equation for the given parameters
    """
    return a * (1 - ((1 - np.exp(-b * tau)) / (b * tau)))


def log_two(tau, a, b, c, d):
    """Callable equation for a single log feynman fit
       a * (1 - ((1 - np.exp(-b * tau)) / (b * tau))) + c * (1 - ((1 - np.exp(-d * tau)) / (d * tau)))

    Arguments:
        tau: Gatewidths
        a: Fitting Parameter (representative of first plateau value)
        b: Fitting Parameter (representative of lambda 1 value)
        c: Fitting Parameter (representative of second plateau value)
        d: Fitting Parameter (representative of lambda 2 value)

    Returns: Distribution for equation for the given parameters
    """
    return a * (1 - ((1 - np.exp(-b * tau)) / (b * tau))) + c * (1 - ((1 - np.exp(-d * tau)) / (d * tau)))


class FeynmanYAnalysis:
    def __init__(self, histograms: List[FeynmanHistogram] = None):
        """Initializes the FeynmanYAnalysis Class

            Arguments:
                histograms: Takes a list of FeynmanHistograms;
                            Defaults to initializing with no histograms
        """
        self._taus = []
        if histograms is not None:
            if not histograms or not isinstance(histograms, list):
                raise ValueError("A list of FeynmanHistogramTypes must be provided")
            else:
                if not isinstance(histograms[0], FeynmanHistogram):
                    raise ValueError("A list of FeynmanHistogramTypes must be provided")
        self._histograms = histograms
        self.Y1s = []
        self.D1s = []
        self.Y2s = []
        self.D2s = []

        self._1logfit_covariance = []
        self._1logfit_parameters = []
        self._2logfit_covariance = []
        self._2logfit_parameters = []

    @property
    def histograms(self):
        """Retrieves list of FeynmanHistogram types 
            
            Returns: A list of FeynmanHistogram types 
        """
        return self._histograms

    @histograms.setter
    def histograms(self, histograms: List[FeynmanHistogram]):
        """Sets a list FeynmanHistogram types
        
            Arguments:
                histograms: List of FeynmanHistogram types
        """
        if histograms is None or not histograms or not isinstance(histograms, list):
            raise ValueError("A list of FeynmanHistogramTypes must be provided")
        else:
            if not isinstance(histograms[0], FeynmanHistogram):
                raise ValueError("A list of FeynmanHistogramTypes must be provided")
        self._histograms = histograms
        self._taus = [hist.gatewidth for hist in histograms]

    @property
    def singleFitParameters(self):
        """Retrieves parameters from a 1 log fit
        
            Returns: A list of 2 parameters
        """
        return self._1logfit_parameters

    @singleFitParameters.setter
    def singleFitParameters(self, single_parameters):
        """Sets parameters for a 1 log fit
        
            Arguments:
                single_parameters: A list of 2 fit parameters 
        """
        if len(single_parameters) != 2:
            raise ValueError("There must be two variables to fit")
        self._1logfit_parameters = single_parameters

    @property
    def singleFitCovariance(self):
        """Retrieves covariance for a 1 log fit
        
            Returns: A matrix of 2 parameters
        """
        return self._1logfit_covariance

    @singleFitCovariance.setter
    def singleFitCovariance(self, single_covariance):
        """Sets covariance for a 1 log fit
        
            Arguments:
                single_covariance: A matrix of 2x2 parameters
        """
        if len(single_covariance) != 2 & len(single_covariance[0]) != 2:
            raise ValueError("The covariance must be a 2x2 matrix list of lists")
        self._1logfit_covariance = single_covariance

    @property
    def doubleFitParameters(self):
        """Retrieves parameters from a 2 log fit
        
            Returns: A list of 4 parameters
        """
        return self._2logfit_parameters

    @doubleFitParameters.setter
    def doubleFitParameters(self, double_parameters):
        """Sets parameters for a 2 log fit
        
            Arguments:
                double_parameters: A list of 4 fit parameters 
        """
        if len(double_parameters) != 4:
            raise ValueError("There must be four variables to fit")
        self._2logfit_parameters = double_parameters

    @property
    def doubleFitCovariance(self):
        """Retrieves covariance for a 2 log fit
        
            Returns: A matrix of 4 parameters
        """
        return self._2logfit_covariance

    @doubleFitCovariance.setter
    def doubleFitCovariance(self, double_covariance):
        """Sets covariance for a 2 log fit
        
            Arguments:
                double_covariance: A matrix of 4x4 parameters
        """
        if len(double_covariance) != 4 & len(double_covariance[0]) != 4:
            raise ValueError("The covariance must be a 4x4 matrix list of lists")
        self._2logfit_covariance = double_covariance

    def makeHistograms(self, calculator: callable, gates_list: list = None, minimum=10, maximum=2e6,
                       spacing=10, disableSubProgBar=True):
        """Creates several FeynmanHistograms for a range of log spaced gate widths

            Arguments:
                gates_list: List of gatewidths in nanoseconds
                calculator: The FeynmanHistogramCalculator class which has taken in the events
                minimum: minimum gatewidth in nanoseconds
                maximum: maximum gatewidth in nanoseconds
                spacing: The amount of points is log spaced between min_ and max_
                disableSubProgBar: Defaults to disabling the progress bar of each histogram

            Stored as:
                self.histograms:list of FeynmanHistograms for the specified range
        """

        if gates_list is None:
            self.histograms = [calculator.calculate(tau)
                               for tau in tqdm(np.logspace(np.log10(minimum), np.log10(maximum), spacing))]
        else:
            self.histograms = [calculator.calculate(tau) for tau in tqdm(gates_list)]

    def gatewidths(self):
        """Extracts the gatewidths from all FeynmanHistograms

            Returns: List of gatewidths in nanoseconds
        """
        return self._taus

    def Y1Distribution(self):
        """Extracts the Y1 and its uncertainty as a function of gate width

            Returns: List of Y1's in nanoseconds
        """
        holdY1 = [hist.Y1 for hist in self.histograms]
        self.Y1s, self.D1s = zip(*holdY1)
        return self.Y1s, self.D1s

    def Y2Distribution(self):
        """Extracts the Y2's from all FeynmanHistograms

            Returns: List of Y2's in nanoseconds
        """
        holdY2 = [hist.Y2 for hist in self.histograms]
        self.Y2s, self.D2s = zip(*holdY2)
        return self.Y2s, self.D2s

    def fit1Log(self, guess=None):
        """Calculates the curve fit for a single log Feynman fit
            
            Arguments:
                guess: Optional list of initial guess for fit parameters A, B
                        
            Returns:
                singleFitParameters: list of 2 fit parameters
                singleFitCovariance: list of lists making the 2*2 covariance matrix
        """
        if not guess:
            self.Y2Distribution()
            dY2s = savgol_filter(np.gradient(self.Y2s, self.gatewidths()), 2 * (len(self.gatewidths()) // 2) - 1, 3)
            dY2s_max = np.argmax(dY2s)
            guess = [self.Y2s[np.argmin(dY2s[dY2s_max:])], dY2s[dY2s_max]]
        else:
            if len(guess) != 2:
                print("Initial values must be a list of two values")

        try:
            self.singleFitParameters, self.singleFitCovariance = curve_fit(log_one, self.gatewidths(), self.Y2s,
                                                                           guess, method="lm")
            return self.singleFitParameters, self.singleFitCovariance
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            print("More appropriate guess values may be needed")

    def fit2Log(self, guess=None):
        """Calculates the curve fit for a double log Feynman fit
            
            Arguments:
                guess: Optional list of initial guess for fit parameters A, B
            
            Returns:
                doubleFitParameters: list of 4 fit parameters
                singleFitCovariance: list of lists making the 4x4 covariance matrix
        """
        if not guess:
            self.Y2Distribution()
            dY2s = savgol_filter(np.gradient(self.Y2s, self.gatewidths()), 2 * (len(self.gatewidths()) // 2) - 1, 3)
            dY2s_max = np.argmax(dY2s)
            guess = [self.Y2s[np.argmin(dY2s[dY2s_max:])], dY2s[dY2s_max] / 2,
                     self.Y2s[np.argmin(dY2s[dY2s_max:])], dY2s[dY2s_max] / 2]
        else:
            if len(guess) != 4:
                print("Initial values must be a list of four values")

        try:
            self.doubleFitParameters, self.doubleFitCovariance = curve_fit(log_two, self.gatewidths(), self.Y2s,
                                                                           guess, method="lm")
            return self.doubleFitParameters, self.doubleFitCovariance
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            print("More appropriate guess values may be needed")

    def fit1LogDistribution(self):
        """Calculates 1 log distribution from fit parameters for pre-given bins

            Returns:
                log1_result: Distribution of single exponential
        """
        try:
            self.fit1Log()
            log1_result = log_one(np.array(self._taus), *self.singleFitParameters)
            return log1_result
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            print("Poor 1-log fit prevents the distribution calculation from occurring \n")

    def fit2LogDistribution(self):
        """Calculates 2 log distribution from fit parameters for pre-given bins

            Returns:
                log2_result: Distribution of double exponential
        """
        try:
            self.fit2Log()
            log2_result = log_two(np.array(self._taus), *self.doubleFitParameters)
            return log2_result
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            print("Poor 2-log fit prevents the distribution calculation from occurring \n")

    def plotResiduals(self, gaussianBins: int = 100, show=True, save=False):
        """Creates residual plots comparing residual vs gatewidths and histogram of residuals

            Arguments:
                show: Defaults to displaying the figure
                gaussianBins: The amount of bins desired for histogram of residuals
    
            Returns:
                  figure: Variable containing figure with subplots
                  axis  : Variable used to control aspects of figure and subplots
        """
        figure, axis = plt.subplots(2, 1)
        try:
            log1_result = self.fit1LogDistribution()
            residual1 = [row[0] - row[1] for row in zip(self.Y2s, log1_result)]
            axis[0].plot(self.gatewidths(), residual1, markerfacecolor="None", color='k', marker="o", linestyle='None',
                         label="log1")
            hist1, bin1 = np.histogram(residual1, gaussianBins)
            axis[1].plot((bin1[1:] + bin1[:-1]) / 2, hist1, color='k', drawstyle='steps-mid', label="log1")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            print("Poor 1-log fit prevents inclusion in the plot \n")

        try:
            log2_result = self.fit2LogDistribution()
            residual2 = [row[0] - row[1] for row in zip(self.Y2s, log2_result)]
            axis[0].plot(self.gatewidths(), residual2, color='r', marker="x", linestyle='None', label="log2")
            hist2, bin2 = np.histogram(residual2, gaussianBins)
            axis[1].plot((bin2[1:] + bin2[:-1]) / 2, hist2, color='r', drawstyle='steps-mid', label="log2")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            print("Poor 2-log fit prevents fit prevents inclusion in the plot \n")

        axis[0].set_xlabel('Gate Width [ns]', fontsize=16)
        axis[0].set_ylabel('Residual', fontsize=16)
        axis[0].legend()
        axis[0].set_xscale("log")

        axis[1].set_xlabel('Residual', fontsize=16)
        axis[1].set_ylabel('Counts', fontsize=16)
        axis[1].legend()

        figure.tight_layout()

        if show:
            figure.show()
        
        if save != False and type(save) == str:
            plt.savefig(save+'.png',dpi=500,bbox_inches='tight',pad_inches=0.1)
            plt.savefig(save+'.pdf',dpi=500,bbox_inches='tight',pad_inches=0.1)
        
        return figure, axis

    def plotY2(self, fits=False, residuals=False, gaussianBins=50, show=True, save=False):
        """Creates a plot of the Y2 distribution
           User can specify if they want fits overlaying and if the residual figure appears

            Arguments:
                fits: User defines if they want the fits overlaying the raw calculation, does 1log and 2log
                residuals: User defines if they want to see figure of residuals
                gaussianBins: The amount of bins desired for histogram of residuals
                show: Defaults to displaying all figures
                
            Returns:
                  figure: Variable containing Rossi figure
                  axis : Variable used to control aspects of Rossi figure
                  if residuals is True: figure and axis for residuals
        """
        figure, axis = plt.subplots()
        axis.plot(self.gatewidths(), self.Y2Distribution()[0], color='#00aaffff', label="Raw Calculation",
                  drawstyle='steps-mid', linewidth=2)
        axis.set_xlabel('Gate Width [ns]', fontsize=16)
        axis.set_ylabel('Counts', fontsize=16)
        axis.set_yscale("log")
        axis.set_xscale("log")
        if fits:
            try:
                fit1 = self.fit1LogDistribution()
                axis.plot(self.gatewidths(), fit1, label="log1", color='k', linestyle="--", linewidth=2)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print(e)
                print("Poor 1-log fit prevents the calculation from occurring \n")

            try:
                fit2 = self.fit2LogDistribution()
                axis.plot(self.gatewidths(), fit2, label="log2", color='r', linestyle=":", linewidth=2)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print(e)
                print("Poor 2-log fit prevents the calculation from occurring \n")

        axis.legend()
        figure.tight_layout()
        if show:
            figure.show()
        
        if save != False and type(save) == str:
            plt.savefig(save+'.png',dpi=500,bbox_inches='tight',pad_inches=0.1)
            plt.savefig(save+'.pdf',dpi=500,bbox_inches='tight',pad_inches=0.1)

        figure.clear()
        
        return (figure, axis, self.plotResiduals(gaussianBins, show=show)) if residuals else (figure, axis, None, None)
