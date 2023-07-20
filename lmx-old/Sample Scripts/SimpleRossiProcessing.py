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

# SIMPLE ROSSI PROCESSING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
rossi_calculator = RossiHistogramCalculator(event_list=events_list)  # default type I binning
# In terms of nanoseconds and the binning is linear
raw_histogram = rossi_calculator.calculate(reset_time=10000., number_bins=50)
shaped_histogram = shapeHistogram(raw_histogram, cutFirstZeros=True, cutFirstValues=True,
                                                 extraCut=1, shiftBaseline=True)[0]
analyze_rossi_histogram = RossiHistogramAnalysis(shaped_histogram)
analyze_rossi_histogram.plotHistogram(fits=True, residuals=True, gaussianBins=40)
print(analyze_rossi_histogram)  # prints the alpha values with associated error

# VIEW FIGURES AND SAVE DATA ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
plt.show()  # will display all figure that were created previously

# must also download the smores package

writeRossiToJSON(analyze_rossi_histogram.histogram, "rossi_test_a", indent=1)  # writes to human readable JSON file
rossi_histograms_JSON = loadRossiFromJSON("rossi_test_a.json")  # loads list of RossiHistogram types

pickleRossi(analyze_rossi_histogram.histogram, "rossi_test_b")  # writes to numpy binary file
rossi_histograms_pickle = unpickleRossi("rossi_test_b.npy")  # loads list of RossiHistogram types

