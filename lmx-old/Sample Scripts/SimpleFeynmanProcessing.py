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

# SIMPLE FEYNMAN PROCESSING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
feynman_analysis = FeynmanYAnalysis()
# In terms of nanoseconds and the spacing is logarithmic
feynman_analysis.makeHistograms(FeynmanHistogramCalculator(events_list),
                                minimum=1., maximum=2e6, spacing=15)
feynman_analysis.Y2Distribution()
feynman_analysis.plotY2(fits=True, residuals=False)

# VIEW FIGURES AND SAVE DATA~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
plt.show()

# must also download the smores package

writeFeynmanToJSON(feynman_analysis.histograms, "feynman_test_a", indent=1)  # writes to human readable JSON file
feynman_histograms_JSON = loadFeynmanFromJSON("feynman_test_a.json")  # loads list of FeynmanHistogram types

# example in saving a single histogram
pickleFeynman(feynman_analysis.histograms[1], "feynman_test_b")  # writes to numpy binary file
feynman_histograms_pickle = unpickleFeynman("feynman_test_b.npy")  # loads list of FeynmanHistogram types
