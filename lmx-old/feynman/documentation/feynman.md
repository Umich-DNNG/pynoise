# The Feynman processing package
The ```lmx.feynman``` package aims to provide an easy to use 
interface to process an existing time dependent data, create 
feynman histograms from scratch, analyze feynman histogram 
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

The top level component is the ```SequentialBinning.py``` file that can initialise ```SequentialBinning```
with an existing input file or be initialised with its individual components.

### Using Sequential Binning

To use sequential binning:
```python
from lmx.feynman.SequentialBinning import SequentialBinning

Callable = SequentialBinning()
timeList  = listOfEventTypes  # A list of data of Event Class types
gateWidth = 10.0              # Size of Feynman gatewidth in nanoseconds
frequency = Callable(events=timeList, gatewidth=gateWidth) 
```

```SequentialBinning``` given a list of ```Event``` types and a gatewidth returns
the frequency of multiplets.

## Calculator

The ```FeynmanHistogramCalculator``` is the class that combines the ```SequentialBinning```
and a list of ```Event``` types from a user given file to create a Feynman histogram.

### Using the Feynman Calculator

To use the feynman calculator:

```python
from lmx.feynman.FeynmanHistogramCalculator import FeynmanHistogramCalculator 

feynman_calculator = FeynmanHistogramCalculator(events_list, binning=binning, time_cutoff=None)
single_feynman_histogram = feynman_calculator.calculate(gatewidth=1.0)
```


```FeynmanHistogramCalculator``` given a list of ```Event``` initiates the class with
a default of ```binning``` as ```SequentialBinning```, but other forms of binning may
be used as a callable. There is a default of no ```time_cutoff```. A ```FeynmanHistogram``` class will be initialized if:


```python
single_feynman_histogram = feynman_calculator.calculate(gatewidth=1.0)
``` 

## Histogram

The ```FeynmanHistogram``` is the class initialized in three ways. It can initialized from 
```FeynmanHistogramCalculator``` or directly initialized given a ```gatewidth``` and 
```frequency```.

### Initializing a Feynman histogram

To initialize a ```FeynmanHistogram``` class we have:

* ```gatewidth``` : the gate width (often referred to as tau, has to be given in nanoseconds)
* ```frequency``` : the count frequency (unnormalised) for all gates (the sum of this list is the total number N of gates)

```python
from lmx.feynman.FeynmanHistogram import FeynmanHistogram

feynman_histogram = FeynmanHistogram(gatewidth=10.0, frequency=frequency)
```

### Features of Feynman histogram

Once a ```FeynmanHistogram``` has been initialized, various details of the histogram can
be extracted.

The reduced factorial moment can be calculated until the fourth moment as: 
```python
first_reduced_factorial_moment = single_feynman_histogram.reduced_factorial_moment(1)
fourth_reduced_factorial_moment = single_feynman_histogram.reduced_factorial_moment(4)
```
\
The mean, variance, and variance to mean can be calculated as:
```python
single_feynman_mean = single_feynman_histogram.mean
single_feynman_variance = single_feynman_histogram.variance
single_variance_to_mean = single_feynman_histogram.variance_to_mean
```
\
The Y1, Y2, and the associated error on each are calculated for each gate as:
```python
Y1, dY1 = single_feynman_histogram.Y1
Y2, dY2 = single_feynman_histogram.Y2
```
\
The R1 and R2 values can be calculated, given a ```decay_constant``` in nanoseconds as:
```python
r1 = single_feynman_histogram.R1(decay_constant=decay_constant)
r2 = single_feynman_histogram.R2(decay_constant=decay_constant)
```
\
The plot for the histogram comparing frequency to multiplets for the gatewidth is:
```python
single_feynman_figure, single_feynman_axis = single_feynman_histogram.plotHistogram(poisson=True, show=True)
```
For the ```plotHistogram```, an overlay of a ```poisson``` distribution defaults to ```True``` 
and ```show``` defaults to ```True```. The function returns a figure and axis variables that 
can be edited externally once the plot is produced.

## Analysis

The ```FeynmanYAnalysis``` component compares the Y's of several ```FeynmanHistogram``` of 
different ```gatewidth```.

### Initializing Feynman Y analysis

A ```FeynmanYAnalysis``` class object can be initialized as empty, without histograms, as:
```python
from lmx.feynman.FeynmanYAnalysis import *

feynman_analysis = FeynmanYAnalysis()
```
from which, the ```FeynmanYAnalysis``` object can be filled with histograms as:
```python
feynman_analysis.makeHistograms(FeynmanHistogramCalculator(events_list),
                                minimum=1, maximum=50000, spacing=5)
```
\
```makeHistograms``` must be given a calculator as previously described, and a ```minimum``` 
and ```maximum``` gatewidth in nanoseconds. The gatewidth is logarithmically spaced with
```spacing``` amount of points between ```minimum``` and ```maximum```.

\
Otherwise, ```FeynmanYAnalysis```is initialized with a list of histograms as:
```python
feynman_analysis = FeynmanYAnalysis(histograms=ListofFeynmanHistograms)
```

### Features of Feynman Y analysis

Once a ```FeynmanYAnalysis``` has been initialized, various details of the histograms
can be extracted along the gatewidths for each histogram.

The ```gatewidth```, ```Y1```, and ```Y2``` distributions can be called as:
```python
gates_widths = feynman_analysis.gatewidths()  # Extract the log spaced gate widths
Y1_distribution = feynman_analysis.Y1Distributions()
Y2_distribution = feynman_analysis.Y2Distributions()
```

\
The ```fitDistributions``` is best used as an internal function, but can be called if desired 
to obtain the distributions from logarithmic fits of the Y2.
```python
log1_distribution = feynman_analysis.fit1LogDistribution()
log2_distribution = feynman_analysis.fit2LogDistribution()
```

\
The residuals of fits are shown in a plot as:
```python
residual_figure, residual_axis = feynman_analysis.plotResiduals(gaussianBins=100, show=True)
```

\
Creates residual plots comparing residual vs gatewidths and histogram of residuals.
The amount of bins for the histogram can be specified with ```gaussianBins```. Defaults to ```True``` 
for ```show```. The function returns a figure and axis variables that can be edited 
externally once the plot is produced.

\
The plot for the histogram comparing Y2 to gatewidth is:
```python
histogram_figure, histogram_axis = feynman_analysis.plotY2(fits=True, residuals=True, gaussianBins=40, show=True)
```
The ```plotY2``` defaults to ```True```  for ```fits```, ```residuals``` and 
```show```. The ```gaussianBins``` can be specified like in ```plotResiduals```.
The function returns a figure and axis variables that can be edited externally once the plot is produced.

## Save/Load

Once the histogram(s) are created, they can be saved to ```.JSON``` or ```.npy```
files that preserve the ```FeynmanHistogram``` structure for easy reloading. 

This section is where ```marshmallow``` and ```smores``` modules are necessary 
for proper functionality.

### JSON 

JSON files are human readable files that will contain the variables associated with
the histogram. Import module as:
```python
from lmx.feynman.json import *
```

\
To save one or several ```FeynmanHistogram```: 
```python
writeFeynmanToJSON(data=feynman_analysis.histograms, file="feynman_test_a", indent=1)
```
```data``` can be extracted from an ```FeynmanYAnalysis``` object as shown above
or can be specified to any other variable containing ```FeynmanHistogram``` objects.
```file``` is a user specified name, and the ```indent``` is for readability
of the JSON file.

\
To load from a ```.JSON``` file:
```python
feynman_histograms_JSON = loadFeynmanFromJSON(file="feynman_test_a.json") 
```
Loads directly to a list or single instance of ```FeynmanHistogram``` objects.


### Pickle

The [pickle](https://github.com/python/cpython/blob/3.9/Lib/pickle.py) module must
be installed for this method to work. The package allows for the histogram to be
preserved as it is save to a binary ```.npy``` file. Import module as:
```python
from lmx.feynman.pickle import *
```

\
To save one or several ```FeynmanHistogram```: 
```python
pickleFeynman(data=feynman_analysis.histograms[1], file="feynman_test_b")
```
```data``` can be extracted from an ```FeynmanYAnalysis``` object as shown above
or can be specified to any other variable containing ```FeynmanHistogram``` objects.
```file``` is a user specified name.

\
To load from a ```.npy``` file:
```python
feynman_histograms_pickle = unpickleFeynman(file="feynman_test_b.npy") 
```
Loads directly to a list or single instance of ```FeynmanHistogram``` objects.