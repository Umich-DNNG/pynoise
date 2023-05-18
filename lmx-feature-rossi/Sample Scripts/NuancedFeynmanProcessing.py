# sample script for processing files with feynman scripts

# standard imports
import matplotlib.pyplot as plt
import glob
import sys

sys.path.append(r"C:\Users\352798\python")  # specify path to modules if not in system
# local imports
from lmx.ToEvents import *  # For interpreting various file types
from lmx.feynman.FeynmanHistogramCalculator import *  # Import feynman scripts
from lmx.feynman.FeynmanYAnalysis import *
from lmx.feynman.SequentialBinning import *
from lmx.feynman.json import *
from lmx.feynman.pickle import *

# load from a lmx file
files = glob.glob("files*.lmx")
events_list = []
[events_list.extend(eventsFromLMX(f)) for f in files]

# NUANCED FEYNMAN PROCESSING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
binning = SequentialBinning()
feynman_calculator = FeynmanHistogramCalculator(events_list, binning=binning, time_cutoff=1000)

# example of creating a single feynman histogram for a single gate width
single_feynman_histogram = feynman_calculator.calculate(gatewidth=1.0)
first_reduced_factorial_moment = single_feynman_histogram.reduced_factorial_moment(1)
fourth_reduced_factorial_moment = single_feynman_histogram.reduced_factorial_moment(4)

single_feynman_mean = single_feynman_histogram.mean
single_feynman_variance = single_feynman_histogram.variance
single_variance_to_mean = single_feynman_histogram.variance_to_mean

Y1, dY1 = single_feynman_histogram.Y1
Y2, dY2 = single_feynman_histogram.Y2

decay_constant = 1.0  # Arbitrary value of 1.0 but should represent the assembly decay constant in nanoseconds
r1 = single_feynman_histogram.R1(decay_constant=decay_constant)
r2 = single_feynman_histogram.R2(decay_constant=decay_constant)

single_feynman_figure, single_feynman_axis = single_feynman_histogram.plotHistogram(poisson=True, show=True)

# example of analyzing multiple histograms of multiple gatewidths
feynman_analysis = FeynmanYAnalysis()
feynman_analysis.makeHistograms(FeynmanHistogramCalculator(events_list),
                                minimum=1, maximum=2e6, spacing=15)
gates_widths = feynman_analysis.gatewidths()  # Extract the log spaced gate widths
Y1_distribution = feynman_analysis.Y1Distribution()
Y2_distribution = feynman_analysis.Y2Distribution()

# fitDistributions is best used as an internal function, but can be called if desired
# to obtain the distributions from fits
log1_distribution = feynman_analysis.fit1LogDistribution()
log2_distribution = feynman_analysis.fit2LogDistribution()
# Viewing of residuals
residual_figure, residual_axis = feynman_analysis.plotResiduals(gaussianBins=100, show=True)

# Viewing of histogram with fits
histogram_figure, histogram_axis, a, b = feynman_analysis.plotY2(fits=True, residuals=False, gaussianBins=40, show=True)

# VIEW FIGURES AND SAVE DATA~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
plt.show()

# must also download the smores package

writeFeynmanToJSON(data=feynman_analysis.histograms, file="feynman_test_a", indent=1)  # writes to human readable JSON file
feynman_histograms_JSON = loadFeynmanFromJSON(file="feynman_test_a.json")  # loads list of FeynmanHistogram types

# example in saving a single histogram
pickleFeynman(data=feynman_analysis.histograms[1], file="feynman_test_b")  # writes to numpy binary file
feynman_histograms_pickle = unpickleFeynman(file="feynman_test_b.npy")  # loads list of FeynmanHistogram types
