# sample script for processing files with rossi-alpha scripts

# standard imports
import matplotlib.pyplot as plt
import numpy as np
import glob
import sys

sys.path.append(r"C:\Users\352798\python")  # specify path to modules if not in system
# local imports
from lmx.ToEvents import *  # For interpreting various file types
from lmx.rossi.RossiHistogramCalculator import *  # Import Rossi-alpha scripts
from lmx.rossi.RossiBinning import *
from lmx.rossi.RossiHistogramAnalysis import *
from lmx.rossi.ShapeRossiHistogram import *
from lmx.rossi.json import *
from lmx.rossi.pickle import *

# load from a txt file
files = glob.glob("files*.txt")
events_list = []
[events_list.extend(eventsFromLMX(f)) for f in files]

# NUANCED ROSSI PROCESSING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
binning = RossiBinningTypeI()  # Type I,II, III and TimeIntervalAnalysis binning methods included in RossiBinning
rossi_calculator = RossiHistogramCalculator(event_list=events_list, binning=binnin, time_cutoff=1000)

raw_histogram = rossi_calculator.calculate(reset_time=10000., number_bins=50)
# Figure and axis can optionally be returned for editing
figure, axis = raw_histogram.plotHistogram(show=True)  # Defaults to show=True


def sample_equation(x, a):
    """Callable equation used to demonstrate ability to overlay a user specified regression

        Arguments:
            x: Bins of time
            a: Fitting Parameter

        Returns: Linear distribution plus offset for equation
    """
    return [a + pt for pt in x]


sample_parameter_list = [10.]  # must be in list form
# Histogram can be overlayed with a user specified equation as long as specified as a callable and
# a list of parameters
raw_histogram.plotHistogram(show=True, equation=sample_equation, parameters=sample_parameter_list)

# Shaping is an optional step that will also specify the values associated with shaping effects
shaped_histogram, firstZeros, firstValues, baseline = shapeHistogram(raw_histogram, cutFirstZeros=True,
                                                        cutFirstValues=True, extraCut=1, shiftBaseline=True)

analyze_rossi_histogram = RossiHistogramAnalysis(shaped_histogram)

# Call for the alpha values with associated sigma for a specified exponential
one_exp_alpha, one_exp_sigma = analyze_rossi_histogram.calculateAlpha(1)
two_exp_alpha, two_exp_sigma = analyze_rossi_histogram.calculateAlpha(2)

# fitDistributions is best used as an internal function, but can be called if desired
# to obtain the distributions from fits
exp1_result = analyze_rossi_histogram.fit1ExpDistribution()
exp2_result = analyze_rossi_histogram.fit2ExpDistribution()

# Viewing of residuals
residual_figure, residual_axis = analyze_rossi_histogram.plotResiduals(gaussianBins=100, show=True)

# Viewing of histogram with fits
analyze_rossi_histogram.plotHistogram(fits=True, residuals=True, gaussianBins=40, show=True)
print(analyze_rossi_histogram)  # prints the alpha values with associated error

# VIEW FIGURES AND SAVE DATA ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
plt.show()  # will display all figure that were created previously

# must also download the smores package

writeRossiToJSON(analyze_rossi_histogram.histogram, "rossi_test_a", indent=1)  # writes to human readable JSON file
rossi_histograms_JSON = loadRossiFromJSON("rossi_test_a.json")  # loads list of RossiHistogram types

pickleRossi(analyze_rossi_histogram.histogram, "rossi_test_b")  # writes to numpy binary file
rossi_histograms_pickle = unpickleRossi("rossi_test_b.npy")  # loads list of RossiHistogram types
