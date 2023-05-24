# PyNoise

A repository for a Python suite of neutron noise analysis algorithms. This draws inspiration from faust lmx on gitlab.lanl.gov. This suite is designed specifically for pulse time-of-detection chains from organic scintillator arrays.

## Rossi-Alpha Method


### How to Use
The files that you will need in order to use the Rossi-Alpha program are fitting.py, plots.py, timeDifs.py, main.py, analyzingFolders.py, readInput,py, settings.txt, and either a file that you want to analyze or a path to folder to analyze(specify in settings). The format of the file you want to analyze should be a txt file with a list of time stamps of neutron detection times, separated by new lines. The format of the settings.txt should be a list of settings:  
There are different categories of settings as follows:  
**I/O FILE INFO** : this contains information about the input files and output files that you will be using
* input file: the name of the file being analyzed (if file type is 1)
* output file: 
* input folder: the path to the folder being analyzed (if file type is 2)   
* file type: the type of file being analyzed
    * file type 1 corresponds to a file that is a list of detection times with nothing else
    * file type 2 corresponds to a folder that has folders within it and files within that folder  
 
**GENERAL PROGRAM SETTINGS** : this contains general program settings     
* fit range : format the range as follows [min,max] with min and max being ints  
* plot scale :  
* time difference method : this refers to the way you want the type differences analyzed. the options are:  
    * any_and_all :  considers all time differences within the reset time
    * any_and_all cross_correlations :  considers all time differences except those from the same detector
    * any_and_all cross_correlations no_repeat :  considers all time differences except those from the same channel and doesn't consider more than one detection from each detector within the same reset period
    * any_and_all cross_correlations no_repeat digital_delay :  considers all time differences except those from the same channel and doesn't consider more than one detection from each detector within the same reset period and adds a digital delay when considering detections from the same detector within the same reset period
* digital delay : specify if using the digital delay time difference method
* number of folders : when using file type 2, this is the number of folders you want analyzed  
* meas time per folder :  
* sort data? : select yes if the data file you provide is unsorted, no otherwise  

**HISTOGRAM VISUAL SETTINGS:** these settings correspond to the histogram settings see https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html for full documentation of options TODO: change code to get boolean values

**GENERATING HISTOGRAM SETTINGS**  
* reset time :   
* bin width : the width of the histogram bins  
* minimum cutoff :  

**LINE FITTING SETTINGS** : visual settings for the fit line see https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html for full documentation of options    

Users can edit this .txt file to change the settings that they wish to use.

### Main
```main.py``` contains a driver program, which when ran, will take the settings.txt file and run the sepcified analysis and produce the plots as specified in the settings. Users can run this file without knowing how any of the code works as long as they can correctly edit settings.txt.   

### Time Difference Calculator
```timeDifs.py``` contains a class, ```TimeDifsCalcs``` that can be initialized with the time data (a list of sorted detection times), the reset time, the method that we will be using, the digital delay, and the corresponding channels to the time data (if not using any_and_all method).

**Using Time Difference Calculator**
```python
from RossiAlpha.timeDifs import * #imports all classes from file
thisTimeDifCalc = timeDifCalcs(list_data, 2e3, any_and_all) #constructs an object called thisTimeDifCalc with a reset time of 2000 and method = any_and_all
time_diffs = thisTimeDifCalc.calculate_time_differences() #saves the array of time diffs as time_diffs
```

### RossiHistogram
In the plots.py file, there is a class called ```RossiHistogram``` which is a class that bins the data. Currently, there is one function under ```RossiHistogram``` called ```plot(self, time_diffs, save_every_fig, show_plot)```, in which the input parameter time_diffs is an array of time differences generated from the ```timeDifCalcs``` class.

**Using RossiHistogram**
```python
from RossiAlpha.plots import * #imports all classes from file
thisPlot = RossiHistogram(reset_time = 2e3, bin_width = 2, histogram_visual_settings, save_dir = '/path/to/save/plot.png') #construct a RossiHistogram object specifying the reset time, bin width, visual settings, and (optional) path to where you want plot to save
counts, bin_centers, bin_edges = thisPlot.plot(time_diffs, save_fig="yes", show_plot="no") #constructs the histogram with the time differences and saves it to the save_dir
#Returns the counts,bin_centers, and bin_edges for later use
```


### Fitting
In the fitting.py file, there are two classes. One is called "Fit" and the other one is called "Fit_With_Weighting". Currently, the difference between the two classes is that "Fit_With_Weighting" deals with parsing through folders of files, as well as creating uncertainty plots. The the class "Fit", there are two functions called "fit()" and "fit_and_residual()", the former is used to fit an exponential decay curve onto the histogram and the latter produces a residual plot on top of the curve fitting.

A Fit() object can be created first with the parameters below: 

* counts (array)
* bin_centers (array)
* generating_hist_settings (dict)
* fitting_opts (dict)
* general_settings (dict)
* residual_opts (dict)
* showPlot (boolean)

From there, the Fit.fit() function will fit an exponential decay curve onto the histogram (given in the form of counts and bin_centers). As discussed above, the Fit.fit_and_residual() function will do the same thing as Fit.fit(), execept that it will plot the relative residuals onto a plot right below the curve fitting plot. Thus, the images produced will have two plots that correspond to a line fitted for a histogram and a residua plot describing how well the line is fitting at each Time Difference (ns) unit. 



A Fit_With_Weighting() object can be created with the parameters below:

* RA_hist_totals (array)
* generating_hist_settings (dict)
* general_settings (dict)

In the class "Fit_With_Weighting", there are two functions: "fit_RA_hist_weighting()" and "plot_RA_and_fit()", where the former calculates the histogram weights and outputs x_fit and y_fit. Those two outputs are then fed into the latter function for plotting.
