# standard imports
import numpy as np
import math
from lmx.Event import Event
# third party imports
from scipy.optimize import curve_fit


def exp_one(x, a, b, c):
    x = np.array(x, dtype="double")
    return a * np.exp(-b * x) + c


def exp_two(x, a, b, c, d, e):
    x = np.array(x, dtype="double")
    return a * np.exp(-b * x) + c * np.exp(-d * x) + e


class RossiHistogram:
    def __init__(self, reset_time: float, frequency: list):
        """Initialise the Rossi histogram processing functions

               Arguments:
                   reset_time: the window size (in nanoseconds) where events are compared
                   num_bins  : divide the window into N bins (should be greater than detector timing)
                   frequency : the solved Rossi-alpha histogram frequency distribution

               Exceptions:
                   ValueError : Something is wrong with the data (no counts, zero or negative window, etc.)
        """
        self._reset_time = reset_time
        self._num_bins = len(frequency)
        self._freq = frequency
        bins = np.linspace(reset_time / (2 * self._num_bins), reset_time - (reset_time / (2 * self._num_bins)),
                           self._num_bins)
        self._bins = bins.tolist()
        self._sgl_cov = []
        self._sgl_opts = []
        self._dbl_cov = []
        self._dbl_opts = []

    @property
    def reset_time(self):
        return self._reset_time

    @reset_time.setter
    def reset_time(self, reset_time: float):
        if reset_time <= 0:
            raise ValueError("The reset time cannot be zero or negative.")
        self._reset_time = reset_time

    @property
    def num_bins(self):
        return self._num_bins

    @num_bins.setter
    def num_bins(self, num_bins: int):
        if num_bins <= 0:
            raise ValueError("The number of bins cannot be zero or negative.")
        self._num_bins = num_bins

    @property
    def frequency(self):
        return self._freq

    @frequency.setter
    def frequency(self, frequency: list):
        if not frequency:
            raise ValueError("The frequency cannot be an empty list.")
        self._freq = frequency

    @property
    def bins(self):
        return self._bins

    @bins.setter
    def bins(self, bins: list):
        if not bins:
            raise ValueError("The bins cannot be an empty list.")
        self._bins = bins

    @property
    def single_opts(self):
        return self._sgl_opts

    @single_opts.setter
    def single_opts(self, singl_opts):
        if len(singl_opts) != 3:
            raise ValueError("There must be three variable to fit")
        self._sgl_opts = singl_opts

    @property
    def single_covariance(self):
        return self._sgl_cov

    @single_covariance.setter
    def single_covariance(self, singl_cov):
        if len(singl_cov) != 3 & len(singl_cov[0]) != 3:
            raise ValueError("The covariance must be a 3x3 matrix list of lists")
        self._sgl_cov = singl_cov

    @property
    def double_opts(self):
        return self._dbl_opts

    @double_opts.setter
    def double_opts(self, doubl_opts):
        if len(doubl_opts) != 3:
            raise ValueError("There must be three variable to fit")
        self._dbl_opts = doubl_opts

    @property
    def double_covariance(self):
        return self._dbl_cov

    @double_covariance.setter
    def double_covariance(self, doubl_cov):
        if len(doubl_cov) != 5 & len(doubl_cov[0]) != 5:
            raise ValueError("The covariance must be a 5x5 matrix list of lists")
        self._dbl_cov = doubl_cov

    def removeFirstZeros(self):
        i = 0
        while self._freq[i] < 1:
            i = i + 1
        self._freq = self._freq[i:]
        self._bins = self._bins[i:]

    def histShape(self):
        """Frequency reshaped to remove 2n+1 point (where n is the max frequency) and baseline

               Arguments: none

               Exceptions: none

               Returns:
                   shaped_freq: list with baseline subtraction and first 2n+1 points removed
                   shaped_bins: list of bins with first 2n+1 points removed
                   head       : number of points removed from start
                   baseline   : mean of the last 10% of the frequency
        """
        tail = int(len(self._freq) * 0.10)
        head = 2 * self._freq.index(max(self._freq)) + 1  # one specific method I know but allow for others
        baseline = sum(self._freq[-tail:]) / tail
        shaped_freq = [i - baseline for i in self._freq[head:]]
        self._freq = shaped_freq
        self._bins = self._bins[head:]
        return head, baseline

    def calculate1exp(self):
        """Calculates the single exponential fit parameters for A*exp(-Bx) + C

                Arguments : none

                Exceptions: none

                Returns:
                    popt: list of 3 fit parameters
                    pcov: list of lists making the 3*3 covariance matrix
        """
        tail = int(len(self._freq) * 0.10)
        baseline = sum(self._freq[-tail:]) / tail
        p0 = [max(self._freq), 1 / 1000, baseline]
        self._sgl_opts, self._sgl_cov = curve_fit(exp_one, self._bins, self._freq, p0, maxfev=5000, method="lm")
        return self._sgl_opts, self._sgl_cov

    def calculate2exp(self):
        """Calculates the double exponential fit parameters for A*exp(-Bx) + C*exp(-Dx) + E

                Arguments : none

                Exceptions: none

                Returns:
                    popt: list of 5 fit parameters
                    pcov: list of lists making the 5*5 covariance matrix
        """
        tail = int(len(self._freq) * 0.10)
        baseline = sum(self._freq[-tail:]) / tail
        p0 = [max(self._freq), 1 / 1000, max(self._freq), 1 / 1000, baseline]
        self._dbl_opts, self._dbl_cov = curve_fit(exp_two, self._bins, self._freq, p0, maxfev=20000, method="lm")
        return self._dbl_opts, self._dbl_cov

    def calcAlpha(self, exp_type):
        """Calculates the alpha value and associated sigma from fit parameters

                Arguments :
                    type: define whether type = "1exp" or "2exp" for calculation

                Exceptions: none

                Returns:
                    alpha: alpha value
                    sigma: sigma of the alpha value
        """
        alpha = -1.
        sigma = -1.

        if exp_type == "1exp":
            if len(self._sgl_opts) == 0:
                self.calculate1exp()
            alpha = self._sgl_opts[1]
            sigma = np.sqrt(self._sgl_cov[1][1])

        elif exp_type == "2exp":
            if len(self._dbl_opts) == 0:
                self.calculate2exp()
            # Mikwa paper and derivation
            p1, r1, p2, r2 = self._dbl_opts[:-1]
            sig_p1, sig_r1 = np.sqrt(self._dbl_cov[0][0]), np.sqrt(self._dbl_cov[1][1])
            sig_p2, sig_r2 = np.sqrt(self._dbl_cov[2][2]), np.sqrt(self._dbl_cov[3][3])
            sig_p1r1, sig_p1p2, sig_p1r2 = self._dbl_cov[0][1:-1]
            sig_r1p2, sig_r1r2 = self._dbl_cov[1][2:-1]
            sig_p2r2 = self._dbl_cov[2][3]
            r_sub = (r1 - r2) * (r1 * p1 + r2 * p2)
            R_a = (-r2*(r1*p1 + r2*p2) + np.sqrt(r1*r2*(r2*p1 + r1*p2)*(r1*p1 + r2*p2))) /r_sub
            R_b = (-r2*(r1*p1 + r2*p2) - np.sqrt(r1*r2*(r2*p1 + r1*p2)*(r1*p1 + r2*p2))) /r_sub
            R = R_a
            if R_a < 0 or R_a > 1:
                R = R_b
            alpha = r1*(1-R) + r2 * R

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

            sigma = np.sqrt(var_alpha)

        return alpha, sigma

    def FitDistributions(self):
        """
        Calculates distributions from fit parameters for pre-given bins

        Returns:
              exp1_result: Distribution of single exponential
              exp2_result: Distribution of double exponential

        """
        if len(self._sgl_opts) == 0:
            self.calculate1exp()
        if len(self._dbl_opts) == 0:
            self.calculate2exp()

        exp1_result = exp_one(self.bins, *self._sgl_opts)
        exp2_result = exp_two(self.bins, *self._dbl_opts)

        return exp1_result, exp2_result

       # uhrig
    def Uhrig(self):
        # after fitting with single exponential-> A, B, and alpha
        # alpha = 1-k(1-beta)/ l = (1-kp)/l = (beta -react)/mean neut gen
        # A = average counting rate
        # F = average fission rate of the system
        # epsilon = detector efficiency in counts per fission
        # l = neutron lifetime
        # B = bar{eps * }
        # many function
        return self._freq  # not actual
