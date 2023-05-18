# The Rossi processing package
The ```lmx.rossi``` package aims to provide an easy to use 
interface to process an existing time dependent data, create 
rossi histograms from scratch, analyze rossi histogram 
distributions, and/or modify an existing histogram. 

The process is split up into five components: 
* [Binning](#Binning) 
* [Calculator](#Calculator)
* [Histogram](#Histogram)
* [Analysis](#Analysis)
* [Save/Load](#Save/Load)

This is a complete description of the components. Not all components
need to be invoked in a script, and all components can be called
individually given proper user inputs.
 
## Binning

The top level component is the ```RossiBinning.py``` file that can initialize
```RossiBinningTypeI```, ```RossiBinningTypeII```, ```RossiBinningTypeIII```, and ```TimeIntervalAnalysis``` classes
as methods for binning time data. 
* ```RossiBinningTypeI```: Window shifts and takes time difference for every event in list
* ```RossiBinningTypeII```: Window shifts and takes time difference for every event after previous window
* ```RossiBinningTypeIII```: Time differences between even and odd events in a list
* ```TimeIntervalAnalysis```: Time differences between one event and its previous event

### Using Rossi Binning

To use rossi binning:
```python
from lmx.rossi.RossiBinning import * # imports all possible classes

Callable = RossiBinningTypeI()
timeList  = listOfEventTypes  # A list of data of Event Class types
reset_time = 10.0             # Size of Rossi reset time window in nanoseconds
bins = 100                    # Number of bins to  split up the reset time window
frequency = Callable(events=timeList, reset_time=gateWidth) 
```

Any binning method, given a list of ```Event``` types, ```reset_time```, and a number of ```bins```, 
returns the frequency of time differences. Note, ```RossiBinningTypeI``` is the default for further 
analysis.

## Calculator

The ```RossiHistogramCalculator``` is the class that combines the ```binning```
and a list of ```Event``` types from a user given file to create a Rossi histogram.

### Using the Rossi Calculator

To use the rossi calculator:
```python
from lmx.rossi.RossiHistogramCalculator import RossiHistogramCalculator 

rossi_calculator = RossiHistogramCalculator(events_list, binning=binning, time_cutoff=None)
single_rossi_histogram = rossi_calculator.calculate(reset_time=1.0, number_bins=100)
```

\
```RossiHistogramCalculator``` given a list of ```Event``` initiates the class with
a default of ```binning``` as ```RossiBinningTypeI```, but other forms of binning may
be used as a callable. There is a default of no ```time_cutoff```. A ```RossiHistogram``` class will be initialized if:

```python
single_rossi_histogram = rossi_calculator.calculate(reset_time=1.0, number_bins=100)
``` 

## Histogram

The ```RossiHistogram``` is the class initialized in three ways. It can initialized from 
```RossiHistogramCalculator``` or directly initialized given a ```reset_time``` and ```frequency```.

### Initializing a Rossi histogram

To initialize a ```RossiHistogram``` class we have:

* ```reset_time``` : the window size (in nanoseconds) where events are compared
* ```frequency``` : the solved Rossi-alpha histogram frequency distribution

```python
from lmx.rossi.RossiHistogram import RossiHistogram

rossi_histogram = RossiHistogram(reset_time=10.0, frequency=frequency)
```

### Features of Rossi histogram

Once a ```RossiHistogram``` has been initialized, details of the histogram can be visualized.

\
The plot for Rossi-alpha distribution as frequency vs bins (in nanoseconds):
```python
single_rossi_figure, single_rossi_axis = single_rossi_histogram.plotHistogram(show=True, equation=None, parameters=None)
```
For the ```plotHistogram```, an overlay of a user specified ```equation``` and ```parameters``` 
defaults to ```None```. ```show``` defaults to ```True```. The function returns a figure and axis variables that 
can be edited externally once the plot is produced.

#### Overlaying an equation 

If the user has the desire to employ an initial guess of a fit and would like to compare,
the ```plotHistogram``` function can employed as:
```python
def sample_equation(x, a):
    """Callable equation used to demonstrate ability to overlay a user specified regression

        Arguments:
            x: Bins of time
            a: Fitting Parameter

        Returns: Linear distribution plus offset for equation
    """
    return [a + pt for pt in x]


sample_parameter_list = [10.]  # must be in list form
raw_histogram.plotHistogram(show=True, equation=sample_equation, parameters=sample_parameter_list)
```


## Analysis

The ```RossiHistogramAnalysis``` component analyzes a single ```RossiHistogram``` object.

### Shaping a Rossi Histogram

If desired, the raw histogram can be shaped with the import of:
```python
from lmx.rossi.ShapeRossiHistogram import *
```

\
From which we have the tools:
* ```cutFirstZerosTool```: Edits a RossiHistogram type's bins and frequency to eliminate the first bins where the frequency is zero
* ```cutFirstValuesTool```: Edits a RossiHistogram type to eliminate the first 2n+1 (with option to shift an ```extraCut``` quantity)
* ```shiftBaselineTool```: Edits a RossiHistogram type's frequencies so the tail values approach zero
* ```shapeHistogram```:  Combines the other tools for a single shaping command

\
The histogram can be edited, with the edits returned to the user as:
```python
firstZeros = cutFirstZerosTool(histogram)
firstValues = cutFirstValuesTool(histogram, extraCut = 1)
baseline = shiftBaselineTool(histogram)

shaped_histogram, firstZeros, firstValues, baseline = shapeHistogram(raw_histogram, cutFirstZeros=True,
                                                        cutFirstValues=True, extraCut=1, shiftBaseline=True)
```

\
A shaped histogram allows for easier analysis of the Rossi-alpha distribution.


### Initializing Rossi Histogram analysis

A ```RossiHistogramAnalysis``` class object can be initialized as empty, without histograms, as:
```python
from lmx.rossi.RossiHistogramAnalysis import *

analyze_rossi_histogram = RossiHistogramAnalysis()
```

\
from which, the ```RossiHistogramAnalysis``` object can be filled with a histogram as:
```python
analyze_rossi_histogram.RossiHistogramAnalysis(histogram=shaped_histogram)
```

\
or if initialized as empty:
```python
analyze_rossi_histogram = RossiHistogramAnalysis()
analyze_rossi_histogram.histogram = histogram
```

### Features of Rossi Histogram analysis

Once a ```RossiHistogramAnalysis``` has been initialized, various details of the histograms
can be extracted along the ```reset_time``` for each histogram.

\
The alpha values with associated sigma for a specified exponential can be called as:
```python
one_exp_alpha, one_exp_sigma = analyze_rossi_histogram.calculateAlpha(1)
two_exp_alpha, two_exp_sigma = analyze_rossi_histogram.calculateAlpha(2)
```

\
Only ```OneExponetial``` and ```TwoExponetial``` fits are supported as of this version.

\
The ```fitDistributions``` is best used as an internal function, but can be called if desired 
to obtain the distributions from exponential fits of the Rossi-alpha distribution.
```python
exp1_result = analyze_rossi_histogram.fit1ExpDistribution()
exp2_result = analyze_rossi_histogram.fit2ExpDistribution()
```

\
The residuals of fits are shown in a plot as:
```python
residual_figure, residual_axis = analyze_rossi_histogram.plotResiduals(gaussianBins=100, show=True)
```

\
Creates residual plots comparing residual vs reset_times and histogram of residuals.
The amount of bins for the histogram can be specified with ```gaussianBins```. Defaults to ```True``` 
for ```show```. The function returns a figure and axis variables that can be edited 
externally once the plot is produced.

\
The plot for the histogram comparing frequency to bins (in nanoseconds) is:
```python
histogram_figure, histogram_axis = analyze_rossi_histogram.plotHistogram(fits=True, residuals=True, gaussianBins=40, show=True)
```
For the ```plotHistogram``` defaults to ```True```  for ```fits```, ```residuals``` and 
```show```. The ```gaussianBins``` can be specified like in ```plotResiduals```.
The function returns a figure and axis variables that can be edited externally once the plot is produced.

The alpha values and associated error are the representation for the ```RossiHistogramAnalysis``` 
object, and will print out when employed as:
```python
print(analyze_rossi_histogram)
```

## Save/Load

Once the histogram(s) are created, they can be saved to ```.JSON``` or ```.npy```
files that preserve the ```RossiHistogram``` structure for easy reloading. 

This section is where ```marshmallow``` and ```smores``` modules are necessary 
for proper functionality.

### JSON 

JSON files are human readable files that will contain the variables associated with
the histogram. Import module as:
```python
from lmx.rossi.json import *
```

\
To save one or several ```RossiHistogram```: 
```python
writeRossiToJSON(data=rossi_analysis.histograms, file="rossi_test_a", indent=1)
```
```data``` can be extracted from an ```RossiHistogramAnalysis``` object as shown above
or can be specified to any other variable containing ```RossiHistogram``` objects.
```file``` is a user specified name, and the ```indent``` is for readability
of the JSON file.

\
To load from a ```.JSON``` file:
```python
rossi_histograms_JSON = loadRossiFromJSON(file="rossi_test_a.json") 
```
Loads directly to a list or single instance of ```RossiHistogram``` objects.

### Pickle

The [pickle](https://github.com/python/cpython/blob/3.9/Lib/pickle.py) module must
be installed for this method to work. The package allows for the histogram to be
preserved as it is save to a binary ```.npy``` file. Import module as:
```python
from lmx.rossi.pickle import *
```

\
To save one or several ```RossiHistogram```: 
```python
pickleRossi(data=rossi_analysis.histograms[1], file="rossi_test_b")
```
```data``` can be extracted from an ```RossiHistogramAnalysis``` object as shown above
or can be specified to any other variable containing ```RossiHistogram``` objects.
```file``` is a user specified name.

\
To load from a ```.npy``` file:
```python
rossi_histograms_pickle = unpickleRossi(file="rossi_test_b.npy") 
```
Loads directly to a list or single instance of ```RossiHistogram``` objects.