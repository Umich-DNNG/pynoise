# standard imports
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from enum import Enum

from lmx.rossi.RossiHistogram import RossiHistogram

np.seterr(over="ignore", invalid="ignore")


class FitType(Enum):
    OneExponential = 1
    TwoExponential = 2


def exp_one(x, a, b, c):
    """Callable equation for a single exponential rossi fit
       a * np.exp(-b * x) + c

        Arguments:
            x: Bins of time
            a: Fitting Parameter
            b: Fitting Parameter (representative of the decay constant)
            c: Fitting Parameter (representative of the baseline value)

        Returns: Distribution for equation for the given parameters
    """
    return a * np.exp(-b * x) + c


def exp_two(x, a, b, c, d, e):
    """Callable equation for a double exponential rossi fit
       a * np.exp(-b * x) + c * np.exp(-d * x) + e

        Arguments:
            x: Bins of time
            a: Fitting Parameter
            b: Fitting Parameter
            c: Fitting Parameter
            d: Fitting Parameter
            e: Fitting Parameter

        Returns: Distribution for equation for the given parameters
    """
    return a * np.exp(-b * x) + c * np.exp(-d * x) + e


class RossiHistogramAnalysis:
    def __init__(self, histogram: RossiHistogram = None):
        """ Initializes the RossiHistogramAnalysis Class

            Arguments:
                histogram: Takes a single RossiHistograms;
                           Defaults to initializing with no histogram
        """
        if not None:
            if isinstance(histogram, RossiHistogram):
                self._histogram = histogram
            else:
                raise ValueError("A RossiHistogram type must be provided")
        else:
            self._histogram = histogram

        self._1expfit_covariance = []
        self._1expfit_parameters = []
        self._2expfit_covariance = []
        self._2expfit_parameters = []
        self._alpha = -1
        self._sigma = -1

    @property
    def histogram(self):
        """Retrieves RossiHistogram type

            Returns: A RossiHistogram type
        """
        return self._histogram

    @histogram.setter
    def histogram(self, histogram: RossiHistogram):
        """Sets a RossiHistogram

            Arguments:
                histogram: A single RossiHistogram type
        """
        if not histogram or not isinstance(histogram, RossiHistogram):
            raise ValueError('The histogram cannot be undefined or empty')
        self._histogram = histogram

    @property
    def singleFitParameters(self):
        """Retrieves parameters from a 1 exponential fit

            Returns: A list of 3 parameters
        """
        return self._1expfit_parameters

    @singleFitParameters.setter
    def singleFitParameters(self, single_parameters):
        """Sets parameters for a 1 exponential fit

            Arguments:
                single_parameters: A list of 3 fit parameters
        """
        if len(single_parameters) != 3:
            raise ValueError("There must be three variable to fit")
        self._1expfit_parameters = single_parameters

    @property
    def singleFitCovariance(self):
        """Retrieves covariance for a 1 exponential fit

            Returns: A matrix of 3 parameters
        """
        return self._1expfit_covariance

    @singleFitCovariance.setter
    def singleFitCovariance(self, single_covariance):
        """Sets covariance for a 1 exponential fit

            Arguments:
                single_covariance: A matrix of 3x3 parameters
        """
        if len(single_covariance) != 3 & len(single_covariance[0]) != 3:
            raise ValueError("The covariance must be a 3x3 matrix list of lists")
        self._1expfit_covariance = single_covariance

    @property
    def doubleFitParameters(self):
        """Retrieves parameters from a 2 exponential fit

            Returns: A list of 5 parameters
        """
        return self._2expfit_parameters

    @doubleFitParameters.setter
    def doubleFitParameters(self, double_parameters):
        """Sets parameters for a 2 exponential fit

            Arguments:
                double_parameters: A list of 5 fit parameters
        """
        if len(double_parameters) != 5:
            raise ValueError("There must be three variable to fit")
        self._2expfit_parameters = double_parameters

    @property
    def doubleFitCovariance(self):
        """Retrieves covariance for a 2 exponential fit

            Returns: A matrix of 5 parameters
        """
        return self._2expfit_covariance

    @doubleFitCovariance.setter
    def doubleFitCovariance(self, double_covariance):
        """Sets covariance for a 2 exponential fit

            Arguments:
                double_covariance: A matrix of 2x2 parameters
        """
        if len(double_covariance) != 5 & len(double_covariance[0]) != 5:
            raise ValueError("The covariance must be a 5x5 matrix list of lists")
        self._2expfit_covariance = double_covariance

    @property
    def alpha(self):
        """Retrieves the prompt neutron decay constant alpha

            Returns: alpha in 1/nanoseconds
        """
        return self._alpha

    @alpha.setter
    def alpha(self, set_alpha: float):
        """Sets the prompt neutron decay constant alpha

            Arguments:
                set_alpha: alpha given in 1/nanoseconds
        """
        if not set_alpha:
            raise ValueError('The alpha cannot be undefined or empty')
        self._alpha = set_alpha

    @property
    def sigma(self):
        """Retrieves sigma value for the prompt neutron decay constant alpha

            Returns: sigma value of alpha
        """
        return self._sigma

    @sigma.setter
    def sigma(self, set_sigma: float):
        """Sets sigma value for the prompt neutron decay constant alpha

            Arguments:
                set_sigma: sigma value of alpha
        """
        if not set_sigma:
            raise ValueError('The sigma cannot be undefined or empty')
        self._sigma = set_sigma

    def __repr__(self):
        alpha1, error1 = self.calculateAlpha(exponentialType=FitType.OneExponential)
        alpha2, error2 = self.calculateAlpha(exponentialType=FitType.TwoExponential)
        s1 = "One exponential gives %s ns with a %s%% error" % (
            round((1 / alpha1), 3), round((100 * error1 / alpha1), 3))
        s2 = "Two exponential gives %s ns with a %s%% error" % (
            round((1 / alpha2), 3), round((100 * error2 / alpha2), 3))
        return s1 + "\n" + s2

    def makeHistogram(self, calculator: callable, reset_times, number_bins):
        """Calculates RossiHistograms for combinations of reset time and number of bins

            Arguments:
                calculator: The RossiHistogramCalculator class which has taken in events
                reset_times: The window size (in nanoseconds) where events are compared
                number_bins: Divide the window into N bins (should be greater than detector timing)

            Returns:
                RossiHistogramAnalysis now has a RossiHistogram for the specified conditions
        """
        self.histogram = calculator.calculate(reset_times, number_bins)

    def fit1Exp(self, guess=None):
        """Calculates the single exponential fit parameters and covariance matrix for
           A*exp(-Bx) + C and stores it in the RossiHistogram type object

            Arguments :
                guess: Optional list of initial guess for fit parameters A, B, C

            Stored as:
                fitParameters: list of 3 fit parameters
                fitCovariance: list of lists making the 3*3 covariance matrix
        """

        if not guess:
            tail = int(self.histogram.number_bins * 0.10)
            baseline = max(self.histogram.frequency)/2#sum(self.histogram.frequency[-tail:]) / tail
            alpha0 = 1 / ((self.histogram.bins[1] - self.histogram.bins[0]) *self.histogram.number_bins)
            guess = [max(self.histogram.frequency) , alpha0, baseline]
        else:
            if len(guess) != 3:
                print("Initial values must be a list of three values")

        try:
            self.singleFitParameters, self.singleFitCovariance = curve_fit(exp_one, self.histogram.bins,
                                                                           self.histogram.frequency,
                                                                           p0=guess, maxfev=40000, method="lm")
            # for i in range(10):
            #     sigma = np.array(self.histogram.frequency) - exp_one(np.array(self.histogram.bins), *self.singleFitParameters)
            #     self.singleFitParameters, self.singleFitCovariance = curve_fit(exp_one, self.histogram.bins,
            #                                                                    self.histogram.frequency,
            #                                                                    p0=self.singleFitParameters, absolute_sigma=False,
            #                                                                    maxfev=40000, method="lm")
            return self.singleFitParameters, self.singleFitCovariance
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            print("More appropriate guess values may be needed")

    def fit2Exp(self, guess=None):
        """Calculates the double exponential fit parameters and covariance matrix for
           A*exp(-Bx) + C*exp(-Dx) + E and stores it in the RossiHistogram type object

            Arguments :
                guess: Optional list of initial guess for fit parameters A, B, C, D, E

            Stored as:
                fitParameters: list of 5 fit parameters
                fitCovariance: list of lists making the 5*5 covariance matrix
        """

        if not guess:
            tail = int(self.histogram.number_bins * 0.10)
            baseline = sum(self.histogram.frequency[-tail:]) / tail
            alpha0 = 1 / ((self.histogram.bins[1] - self.histogram.bins[0]) * self.histogram.number_bins)
            guess = [max(self.histogram.frequency) * 2, alpha0, max(self.histogram.frequency) * 2, alpha0, baseline]
        else:
            if len(guess) != 5:
                print("Initial values must be a list of five values")
        try:
            self.doubleFitParameters, self.doubleFitCovariance = curve_fit(exp_two, self.histogram.bins,
                                                                           self.histogram.frequency, p0=guess,
                                                                           maxfev=40000, method="lm")

            return self.doubleFitParameters, self.doubleFitCovariance
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            print("More appropriate guess values may be needed")

    def calculateAlpha(self, exponentialType: FitType):
        """Calculates the alpha value and associated sigma from fit parameters

            Arguments :
                exponentialType: define whether type = "1exp" or "2exp" for calculation

            Returns:
                alpha: alpha value
                sigma: sigma of the alpha value
        """
        if FitType(exponentialType) == FitType.OneExponential:
            try:
                self.fit1Exp()
                self.alpha = self.singleFitParameters[1]
                self.sigma = np.sqrt(self.singleFitCovariance[1][1])
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print(e)
                print("Poor 1-exp fit prevents the alpha calculation from occurring \n")

        elif FitType(exponentialType) == FitType.TwoExponential:
            self.fit2Exp()
            try:
                # Mikwa paper and derivation
                p1, r1, p2, r2 = self.doubleFitParameters[:-1]
                sig_p1, sig_r1 = np.sqrt(self.doubleFitCovariance[0][0]), np.sqrt(self.doubleFitCovariance[1][1])
                sig_p2, sig_r2 = np.sqrt(self.doubleFitCovariance[2][2]), np.sqrt(self.doubleFitCovariance[3][3])
                sig_p1r1, sig_p1p2, sig_p1r2 = self.doubleFitCovariance[0][1:-1]
                sig_r1p2, sig_r1r2 = self.doubleFitCovariance[1][2:-1]
                sig_p2r2 = self.doubleFitCovariance[2][3]
                r_sub = (r1 - r2) * (r1 * p1 + r2 * p2)
                R_a = (-r2 * (r1 * p1 + r2 * p2) + np.sqrt(r1 * r2 * (r2 * p1 + r1 * p2) * (r1 * p1 + r2 * p2))) / r_sub
                R_b = (-r2 * (r1 * p1 + r2 * p2) - np.sqrt(r1 * r2 * (r2 * p1 + r1 * p2) * (r1 * p1 + r2 * p2))) / r_sub
                R = R_a
                if R_a < 0 or R_a > 1:
                    R = R_b
                self.alpha = r1 * (1 - R) + r2 * R

                delta = 2 * np.sqrt(r1 * r2 * (p2 * r1 + p1 * r2) * (p1 * r1 + p2 * r2) ** 3)
                par_r1 = 1 + p2 * r2 * (2 * p2 * r1 * r2 + p1 * (np.square(r1) + np.square(r2))) / delta
                par_r2 = 1 + p1 * r1 * (2 * p1 * r1 * r2 + p2 * (np.square(r1) + np.square(r2))) / delta
                par_p1 = p2 * r1 * r2 * (np.square(r2) - np.square(r1)) / delta
                par_p2 = p1 * r1 * r2 * (np.square(r1) - np.square(r2)) / delta
                var_alpha = np.square(par_r1) * np.square(sig_r1) + np.square(par_r2) * np.square(sig_r2) \
                            + np.square(par_p1) * np.square(sig_p1) + np.square(par_p2) * np.square(sig_p2) \
                            + 2 * par_r1 * par_r2 * sig_r1r2 + 2 * par_r1 * par_p1 * sig_p1r1 + 2 * par_r1 * par_p2 * sig_r1p2 \
                            + 2 * par_r2 * par_p1 * sig_p1r2 + 2 * par_r2 * par_p2 * sig_p2r2 \
                            + 2 * par_p1 * par_p2 * sig_p1p2

                self.sigma = np.sqrt(var_alpha)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print(e)
                print("Poor 2-exp fit prevents the alpha calculation from occurring \n")

        return self.alpha, self.sigma

    def fit1ExpDistribution(self):
        """Calculates 1 exponential distribution from fit parameters for pre-given bins

            Returns:
                  exp1_result: Distribution of single exponential
        """
        try:
            self.fit1Exp()
            exp1_result = exp_one(np.array(self.histogram.bins), *self.singleFitParameters)
            return exp1_result
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            print("Poor 1-exp fit prevents the distribution calculation from occurring \n")

    def fit2ExpDistribution(self):
        """Calculates 2 exponential distribution from fit parameters for pre-given bins

            Returns:
                  exp2_result: Distribution of single exponential
        """
        try:
            self.fit2Exp()
            exp2_result = exp_two(np.array(self.histogram.bins), *self.doubleFitParameters)
            return exp2_result
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            print("Poor 2-exp fit prevents the distribution calculation from occurring \n")

    def plotResiduals(self, gaussianBins: int = 100, show=True):
        """Creates residual plots comparing residuals vs bins and histogram of residuals

            Arguments:
                show: Defaults to displaying the figure
                gaussianBins: The amount of bins desired for histogram of residuals

            Returns:
                  figure: Variable containing figure with subplots
                  axis  : Variable used to control aspects of figure and subplots

        """
        figure, axis = plt.subplots(2, 1)
        try:
            exp1_result = self.fit1ExpDistribution()
            residual1 = [row[0] - row[1] for row in zip(self.histogram.frequency, exp1_result)]
            axis[0].plot(self.histogram.bins, residual1, markerfacecolor="None", color='k', marker="o",
                         linestyle='None', label="1exp")
            hist1, bin1 = np.histogram(residual1, gaussianBins)
            axis[1].plot((bin1[1:] + bin1[:-1]) / 2, hist1, color='k', drawstyle='steps-mid', label="1exp")

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            print("Poor 1-exp fit prevents inclusion in the plot \n")

        try:
            exp2_result = self.fit2ExpDistribution()
            residual2 = [row[0] - row[1] for row in zip(self.histogram.frequency, exp2_result)]
            axis[0].plot(self.histogram.bins, residual2, color='r', marker="x", linestyle='None', label="2exp")
            hist2, bin2 = np.histogram(residual2, gaussianBins)
            axis[1].plot((bin2[1:] + bin2[:-1]) / 2, hist2, color='r', drawstyle='steps-mid', label="2exp")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            print("Poor 2-exp fit prevents fit prevents inclusion in the plot \n")

        axis[0].set_xlabel('Time Difference [ns]', fontsize=16)
        axis[0].set_ylabel('Residual', fontsize=16)
        axis[0].legend()

        axis[1].set_xlabel('Residual', fontsize=16)
        axis[1].set_ylabel('Counts', fontsize=16)
        axis[1].legend()

        figure.tight_layout()

        if show:
            figure.show()

        return figure, axis

    def plotHistogram(self, fits=False, residuals=False, gaussianBins=50, show=True):
        """Creates a plot of the Rossi-alpha distribution
           User can specify if they want fits overlaying and if the residual figure appears

            Arguments:
                fits: User defines if they want the fits overlaying the raw calculation, does 1exp and 2exp
                residuals: User defines if they want to see figure of residuals
                gaussianBins: The amount of bins desired for histogram of residuals
                show: Defaults to displaying all figures

            Returns:
                  figure: Variable containing Rossi figure
                  axis : Variable used to control aspects of Rossi figure
                  if residuals is True: figure and axis for residuals
        """
        figure, axis = self.histogram.plotHistogram(show=False)

        if fits:
            try:
                fit1 = self.fit1ExpDistribution()
                self.calculateAlpha(exponentialType=FitType.OneExponential)
                label_exp1 = "1exp " + str(round(1 / self.alpha * 1e-6, 2)) + " ± " + str(
                    round(self.sigma * 1e-6 / (self.alpha * self.alpha), 2)) + " ms"
                axis.plot(self.histogram.bins, fit1, label=label_exp1, color='k', linestyle="--", linewidth=2)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print(e)
                print("Poor 1-exp fit prevents the calculation from occurring \n")

            try:
                fit2 = self.fit2ExpDistribution()
                self.calculateAlpha(exponentialType=FitType.TwoExponential)
                label_exp2 = "2exp " + str(round(1 / self.alpha * 1e-6, 2)) + " ± " + str(
                    round(self.sigma * 1e-6 / (self.alpha * self.alpha), 2)) + " ms"
                axis.plot(self.histogram.bins, fit2, label=label_exp2, color='r', linestyle=":", linewidth=2)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print(e)
                print("Poor 2-exp fit prevents the calculation from occurring \n")

        axis.legend()
        figure.tight_layout()
        if show:
            figure.show()

        return figure, axis, self.plotResiduals(gaussianBins, show=show) if residuals else figure, axis, None, None
