import numpy as np
import sys
import matplotlib.pyplot as plt

sys.path.append(r"C:\Users\352798\python")
# local imports
from lmx.ToEvents import ToEvents
from lmx.rossi.RossiBinning import *
from lmx.rossi.RossiHistogramCalculator import RossiHistogramCalculator
from lmx.rossi.RossiHistogram import RossiHistogram


def OptimizeBinWidth(histCalc, window, maxBinWidth=5, minBinWidth=0.05, points=50):
    """

    Args:
        histCalc: RossiHistogram class object
        window: a static value for the rossi alpha window
        maxBinWidth: Maximum Bin Width to be tested (Default 5 ns)
        minBinWidth: Minimum Bin Width ot be tested (Default 0.05 ns)
        points: amount of point to test between min and max bin width

    Returns:
        A plot showing the calculated inverse alpha and % relative error on the
        same plot comparing both against BinWidth
    """
    alpha1 = []
    error1 = []
    alpha2 = []
    error2 = []

    rng = np.linspace(minBinWidth, maxBinWidth, points)

    for bin_width in rng:
        bins = int(window / bin_width)
        hist = histCalc.calculate(window, bins)
        hist.removeFirstZeros()
        hist.histShape()
        a1, e1 = hist.calcAlpha(exp_type="1exp")
        a2, e2 = hist.calcAlpha(exp_type="2exp")
        alpha1.append(1 / a1)
        error1.append(100 * e1 / a1)
        alpha2.append(1 / a2)
        error2.append(100 * e2 / a2)

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot(rng, error2, 'g-', label="% relative error")
    ax2.plot(rng, alpha2, 'b-', label="inverse alpha [ns]")
    ax1.set_xlabel("Bin Width [ns]")
    ax1.set_ylabel("% Relative Error", color="green")
    ax2.set_ylabel("Inverse Alpha [ns]", color="blue")
    fig.legend()
    fig.show()


def OptimizeCutoff(histCalc, BinWidth, minCutoff, maxCutoff, points=50):

    """

    Args:
        histCalc: RossiHistogram class object
        BinWidth: a static value for the rossi alpha Bin Width Size
        maxCutoff: Maximum Cutoff to be tested
        minCutoff: Minimum Cutoff to be tested
        points: amount of point to test between min and max Cutoff

    Returns:
        A plot showing the calculated inverse alpha and % relative error on the
        same plot comparing both against Cutoff
    """
    alpha1 = []
    error1 = []
    alpha2 = []
    error2 = []

    rng = np.linspace(minCutoff, maxCutoff, points)

    for cut in rng:
        hist = histCalc.calculate(maxCutoff, int(cut / BinWidth))
        hist.removeFirstZeros()
        hist.histShape()

        a1, e1 = hist.calcAlpha(exp_type="1exp")
        a2, e2 = hist.calcAlpha(exp_type="2exp")
        alpha1.append(1 / a1)
        error1.append(100 * e1 / a1)
        alpha2.append(1 / a2)
        error2.append(100 * e2 / a2)

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot(rng, error2, 'g-', label="% relative error")
    ax2.plot(rng, alpha2, 'b-', label="inverse alpha [ns]")
    ax1.set_xlabel("Bin Width [ns]")
    ax1.set_ylabel("% Relative Error", color="green")
    ax2.set_ylabel("Inverse Alpha [ns]", color="blue")
    fig.legend()
    fig.show()
