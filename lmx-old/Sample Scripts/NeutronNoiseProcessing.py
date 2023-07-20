# sample script for simple processing of files with feynman and rossi-alpha scripts

# standard imports
import matplotlib.pyplot as plt
import glob
import sys

sys.path.append(r"C:\Users\352798\python")  # specify path to modules if not in system
# local imports
from lmx.ToEvents import *  # For interpreting various file types
from lmx.rossi.RossiHistogramCalculator import *  # Import Rossi-alpha scripts
from lmx.rossi.RossiHistogramAnalysis import *
from lmx.rossi.ShapeRossiHistogram import *
from lmx.feynman.FeynmanHistogramCalculator import *  # Import feynman scripts
from lmx.feynman.FeynmanYAnalysis import *

# load from a numpy file
files = glob.glob("combined_all_Data_02_rf3_40_cf_rr_config_5_waves_PSD_CH*_time_and_ch.npy")
events_list = []
[events_list.extend(eventsFromNumpy(f)) for f in files]

# FEYNMAN PROCESSING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
feynman_analysis = FeynmanYAnalysis()
# In terms of nanoseconds and the spacing is logarithmic
feynman_analysis.makeHistograms(FeynmanHistogramCalculator(events_list),
                                minimum=1, maximum=50000, spacing=5)
feynman_analysis.Y2Distribution()
feynman_analysis.plotY2(fits=True, residuals=True)

# ROSSI-ALPHA PROCESSING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
rossi_calculator = RossiHistogramCalculator(events_list)
# In terms of nanoseconds and the binning is linear
raw_histogram = rossi_calculator.calculate(reset_time=6000., number_bins=1500)
shaped_histogram = shapeHistogram(raw_histogram, cutFirstZeros=True, cutFirstValues=True,
                                                 extraCut=1, shiftBaseline=True)[0]
analyze_rossi_histogram = RossiHistogramAnalysis(shaped_histogram)
analyze_rossi_histogram.plotHistogram(fits=True, residuals=True, gaussianBins=40)
print(analyze_rossi_histogram)  # prints the alpha values with associated error

# VIEW FIGURES AND SAVE DATA~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
plt.show()

# To save results RossiSave and FeynmanSave give options to save variables as calculated
# must also download the smores package

writeRossiToJSON(analyze_rossi_histogram.histogram, "rossi_test_a", indent=1)  # writes to human readable JSON file
rossi_histograms_JSON = loadRossiFromJSON("rossi_test_a.json")  # loads list of RossiHistogram types

pickleRossi(analyze_rossi_histogram.histogram, "rossi_test_b")  # writes to numpy binary file
rossi_histograms_pickle = unpickleRossi("rossi_test_b.npy")  # loads list of RossiHistogram types

writeFeynmanToJSON(feynman_analysis.histograms, "feynman_test_a", indent=1)  # writes to human readable JSON file
feynman_histograms_JSON = loadFeynmanFromJSON("feynman_test_a.json")  # loads list of FeynmanHistogram types

# example in saving a single histogram
pickleFeynman(feynman_analysis.histograms[0], "feynman_test_b")  # writes to numpy binary file
feynman_histograms_pickle = unpickleFeynman("feynman_test_b.npy")  # loads list of FeynmanHistogram types
