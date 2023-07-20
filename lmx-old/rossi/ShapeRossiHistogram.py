import copy
import statistics

from lmx.rossi.RossiHistogram import RossiHistogram


def cutFirstZerosTool(histogram: RossiHistogram):
    """Edits a RossiHistogram type's bins and frequency to eliminate the first bins where the frequency is zero

        Arguments:
            histogram: RossiHistogram type object to be edited

        Returns:
            zeros: The amount of leading zeros removed from the histogram
            adjusted_bins = List of bins with cut applied
            adjusted_frequency: List of frequencies with cut applied

    """
    zeros = 0
    while histogram.frequency[zeros] < 1:
        zeros = zeros + 1
    histogram.frequency = histogram.frequency[zeros:]
    histogram.bins = histogram.bins[zeros:]
    return zeros


def cutFirstValuesTool(histogram: RossiHistogram, extraCut: int = 0):
    """Edits a RossiHistogram type to eliminate the first 2n+1 (with option to shift an extraCut quantity)

        Arguments:
            histogram: RossiHistogram type object to be edited
            extraCut: Positive/Negative value to adjust the index of the cut

        Returns:
            firstValues: The amount of values removed from the histogram (2n+1+extraCut)
    """
    firstValues = 2 * (histogram.frequency.index(max(histogram.frequency)) + 1) + int(extraCut) + 1
    histogram.frequency = histogram.frequency[firstValues:]
    histogram.bins = histogram.bins[firstValues:]
    return firstValues


def shiftBaselineTool(histogram: RossiHistogram, custom_baseline: float = None):
    """ Edits a RossiHistogram type's frequencies so the tail values approach zero

        Arguments:
            histogram: RossiHistogram type object to be edited
            custom_baseline: Supply the program with a custom baseline to shift to

        Returns:
            baseline   : mean of the last 10% of the frequency
    """
    tail = int(len(histogram.frequency) * 0.10)
    baseline = sum(histogram.frequency[-tail:]) / tail
    if custom_baseline is not None:
        baseline = baseline - custom_baseline
        histogram.frequency = [i - baseline for i in histogram.frequency]
        return baseline
    else:
        histogram.frequency = [i - baseline for i in histogram.frequency]
        return baseline


def shapeHistogram(histogram: RossiHistogram, cutFirstZeros=True, cutFirstValues=True, extraCut: int = 0,
                   shiftBaseline=True):
    """Edits a Histogram to remove first values of zero, remove 2n + 1 + extraCut points
       (where n is the index of the max frequency and extraCut is any additional adjustment)
       and the baseline is shifted to center around 0

        Arguments:
             histogram: RossiHistogram to be shaped
             cutFirstZeros: Defaults to removing empty bins at early bin times
             cutFirstValues: Defaults to removing 2n+1 points at the beginning of the histogram
             extraCut: Positive/Negative value to adjust the amount of point removed from 2n+1
             shiftBaseline: Defaults to shifting Rossi-alpha down to a tail approaching zero


        Returns:
            shapedHistogram: A new RossiHistogram object that is shaped for analysis
            firstZeros : number of 0 value points at the start of the histogram
            firstValues: number of points removed from start (2n + 1 + headShiftAdjustment)
            baseline   : mean of the last 10% of the frequency
    """
    firstZeros = None
    firstValues = None
    baseline = None
    shapedHistogram = copy.deepcopy(histogram)
    if cutFirstZeros:
        firstZeros = cutFirstZerosTool(shapedHistogram)
    if cutFirstValues:
        firstValues = cutFirstValuesTool(shapedHistogram, extraCut)
    if shiftBaseline:
        baseline = shiftBaselineTool(shapedHistogram)

    return shapedHistogram, firstZeros, firstValues, baseline
