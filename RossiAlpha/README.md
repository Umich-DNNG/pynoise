# RossiAlpha

This section of the PyNoise suite is for Rossi Alpha Algorithm analysis. This draws inspiration from faust lmx on gitlab.lanl.gov. This suite is designed specifically for pulse time-of-detection chains from organic scintillator arrays. If you are unfamiliar with the Rossi Alpha method, please familiarize yourself before using this package and reading the README file.

## How to Use

### I/O FILE INFO

The format of the file you want to analyze should be a .txt file with a list of time stamps of neutron detection times, separated by new lines. For folder analysis, the given folder should contain numbered folders that each contain data for analysis.

### Settings Configurations

The RossiAlpha program can be run with a variety of options that change the visual output and type of analysis being run. In the settings file, this is listed as the RossiAlpha Settings. The settings are as follows: 
* Time difference method (*string*): This refers to the way you want the time differences generated. the options are:  
    * any_and_all: Considers all time differences within the reset time.
    * any_and_all cross_correlations: Considers all time differences except those from the same detector.
    * any_and_all cross_correlations no_repeat: Considers all time differences except those from the same channel and doesn't consider more than one detection from each detector within the same reset period.
    * any_and_all cross_correlations no_repeat digital_delay: Considers all time differences except those from the same channel and doesn't consider more than one detection from each detector within the same reset period and adds a digital delay when considering detections from the same detector within the same reset period.
    * **NOTE: the last three options are only valid for folder analysis. For single file analysis, any_and_all must be chosen.**
* digital delay (*int*): The amount of digital delay, if applicable (see above).
* **Histogram Generation Settings**: Settings specific to generating RossiAlpha histograms:
    * Reset time (*int*): **TODO**: Find out what this is.
    * Bin width (*int*): The width of the histogram bins.
    * Error bar/band (*string*): For folder analysis, the type of visual used to show residuals of the overall line of best fit. Valid values are bar, band, and none.
* **Fit Region Settings**: Settings specific to applying the line of best fit to Rossi Alpha histograms:
    * Minimum cutoff (*int*): The value at which to start applying the line fitting algorithm.

### Driver
```raDriver.py``` is used to run all analysis pertaining to the Rossi Alpha method, and is called from the main driver. **Trying to call raDriver independently will not work**. The driver has been designed modularly, so that analysis at any stage can be done without having to run through the entire process. There are 5 main options:
* m - run the entire program through the [main driver](#main)
* t - calculate [time differences](#time-difference-calculator)
* p - create [plots](#rossihistogram) of the time difference data
* f - [fit](#fitting) the data to an exponential curve
* s - view or edit the program [settings](#settings-configurations)
* Leave the command blank to end the program.

### Editor
The editor class for modifying settings is also accessible from the raDriver. See the main README file for more information on its proper use.

### Main
```main.py``` contains two functions, one for file type 1 and one for file type 2. ```analyzeAllType1(settings)``` calculates the time differences of a type 1 file, constructs a histogram, and fits a curve to the histogram, and constructs a residuals plot. It uses the settings dictionary to do these functions.   
```analyzeAllType2(settings)``` calculates the time differences for the file within each folder, constructs a histogram, fits a curve to each histogram, then constructs a scatterplot of all of the combined data and fits a curve to it

### Time Difference Calculator
```timeDifs.py``` contains a class, ```TimeDifsCalcs``` that can be initialized with the time data (a list of sorted detection times), the reset time, the method that we will be using, the digital delay, and the corresponding channels to the time data (if not using any_and_all method).

**Using Time Difference Calculator**
```python
from RossiAlpha.timeDifs import * #imports all classes from file
thisTimeDifCalc = timeDifCalcs(list_data, 2e3, any_and_all) #constructs an object called thisTimeDifCalc with a reset time of 2000 and method = any_and_all
time_diffs = thisTimeDifCalc.calculate_time_differences() #saves the array of time diffs as time_diffs
```

### RossiHistogram
In the plots.py file, there is a class called ```RossiHistogram``` which is a class that bins the data. There is one function under ```RossiHistogram``` called ```plot(self, time_diffs, save_every_fig, show_plot)```, in which the input parameter time_diffs is an array of time differences generated from the ```timeDifCalcs``` class.

**Using RossiHistogram**
```python
from RossiAlpha.plots import * #imports all classes from file
thisPlot = RossiHistogram(reset_time = 2e3, bin_width = 2, histogram_visual_settings, save_dir = '/path/to/save/plot.png') #construct a RossiHistogram object specifying the reset time, bin width, visual settings, and (optional) path to where you want plot to save
counts, bin_centers, bin_edges = thisPlot.plot(time_diffs, save_fig="yes", show_plot="no") #constructs the histogram with the time differences and saves it to the save_dir
#Returns the counts,bin_centers, and bin_edges for later use
```


### Fitting
In the fitting.py file, there are two classes. One is called ```RossiHistogramFit``` and the other one is called ```Fit_With_Weighting```. The difference between the two classes is that "Fit_With_Weighting" deals with input type 1, as well as creating uncertainty plots. In ```RossiHistogramFit``` there are two functions called "fit()" and "fit_and_residual()", the former is used to fit an exponential decay curve onto the histogram and the latter produces a residual plot on top of the curve fitting.

fit_and_residual() function will do the same thing as Fit.fit(), execept that it will plot the relative residuals onto a plot right below the curve fitting plot. Thus, the images produced will have two plots that correspond to a line fitted for a histogram and a residua plot describing how well the line is fitting at each Time Difference (ns) unit. 

**Using Fitting**


```python
thisFit = RossiHistogramFit(counts, bin_centers, settings) #construct the fit object
# Fitting curve to the histogram and plotting the residuals
#saves the plot with a fit on top and residuals on bottonm but does not show it
thisFit.fit_and_residual(save_every_fig=True, show_plot=False)
```
```python
RA_hist_total = analyzingFolders.compile_sample_stdev_RA_dist(settings)
from fitting import Fit_With_Weighting
thisWeightedFit = Fit_With_Weighting(RA_hist_total,min_cutoff = , general_settings,saveDir, fitting_opts, residual_opts)
#creates the fit to the data 
thisWeightedFit.fit_RA_hist_weighting()
#plots the histogram
thisWeightedFit.plot_RA_and_fit(save_fig= False, show_plot="No")

```
