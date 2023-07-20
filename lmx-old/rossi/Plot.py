from lmx.rossi.RossiHistogram import RossiHistogram

import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams['backend'] = "Qt5Agg"


def Residuals(hist: RossiHistogram, res_bins=100):
    """

    Args:
        hist: RossiHistogram class object
        res_bins: The amount of bins desired for histogram of residuals

    Returns:
          figure: Variable containing figure with subplots
          axis  : Variable used to control aspects of figure and subplots

    """
    figure, axis = plt.subplots(1, 2)

    exp1_result, exp2_result = hist.FitDistributions()

    residual1 = [row[0] - row[1] for row in zip(hist.frequency, exp1_result)]
    residual2 = [row[0] - row[1] for row in zip(hist.frequency, exp2_result)]

    axis[0].scatter(hist.bins, residual1, label="1exp")
    axis[0].scatter(hist.bins, residual2, label="2exp")
    axis[0].set(xlabel='Time Difference [ns]', ylabel='Residual')
    axis[0].legend()

    axis[1].hist(residual1, res_bins, label="1exp")
    axis[1].hist(residual2, res_bins, label="2exp")
    axis[1].set(xlabel='Residual', ylabel='Counts')
    axis[1].legend()

    return figure, axis

    # make its own function


def Plot(hist: RossiHistogram, fits=False, residuals=False, res_bins=50):
    """
    Creates plot of Rossi-alpha distribution
    User can specify if they want fits overlaying and if residual figure appear
    Args:
        hist: RossiHistogram class object
        fits: User defines if they want the fits overlaying the raw calculation, does 1exp and 2exp
        residuals: User defines if they want to see figure of residuals
        res_bins: The amount of bins desired for histogram of residuals

    Returns:
          rossi_fig: Variable containing figure
          rossi_ax : Variable used to control aspects of figure
    """
    rossi_fig, rossi_ax = plt.subplots()
    rossi_ax.plot(hist.bins, hist.frequency, label="Raw Calculation")
    rossi_ax.set(xlabel='Time [ns]', ylabel='Counts')

    if fits:
        fit1, fit2 = hist.FitDistributions()
        rossi_ax.plot(hist.bins, fit1, label="1exp")
        rossi_ax.plot(hist.bins, fit2, label="2exp")
    if residuals:
        res_fig, res_ax = Residuals(hist, res_bins)
        res_fig.show()

    rossi_ax.legend()
    rossi_fig.show()
    return rossi_fig, rossi_ax
