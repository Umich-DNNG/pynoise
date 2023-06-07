# RossiAlpha

A repository for a Python suite for the Rossi Alpha Algorithm analysis. This draws inspiration from faust lmx on gitlab.lanl.gov. This suite is designed specifically for pulse time-of-detection chains from organic scintillator arrays.

## How to Use


### Requirements

To run the PyNoise project, the following programs must be downloaded:
* driver.py
* editor.py
* settings.py
* main.py
* analyzingFolders.py
* timeDifs.py
* plots.py
* fitting.py

Additionally, you will need the following:
* A single file or folder of data that will be analyzed.
* A settings configuration file (see the settings section for more information).

### Settings Configurations

The RossiAlpha program can be run with a variety of options that change the visual output and type of analysis being run. This section will outline each subgroup of settings and the acceptable values for each parameter. The format of the file you want to analyze should be a txt file with a list of time stamps of neutron detection times, separated by new lines.
There are different categories of settings as follows:  

**I/O FILE INFO** : this group contains information about the input and output details of the program.
* Input type: there are two options for inputs - 
    * option 1 corresponds to a single file with a list of neutron detection times seperated by newlines 
    * option 2 corresponds to a folder that has folders within it and files within that folder. the first column of the file is the channel of the detection and the second column is the time of the detection
* input file/folder: users should input the path to the file or folder that the user wants analyzed
* save directory: users can input a path to where they want produced plots to save

 
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
* sort data? : select True if the data file you provide is unsorted, False otherwise  

**HISTOGRAM VISUAL SETTINGS:** these settings correspond to the histogram settings see https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html for full documentation of options TODO: change code to get boolean values

**HISTOGRAM GENERATION SETTINGS**  
* reset time :   
* bin width : the width of the histogram bins  
* minimum cutoff :  

**LINE FITTING SETTINGS** : visual settings for the fit line see https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html for full documentation of options    

### Settings Input Format
Default or custom settings can be imported into the program and can be changed during runtime. For the program to read in the settings correctly, the file extension must be .set and must have the following formatting:
1. The file can begin with any number of comments (lines that start with #)
2. Each settings group must have a header of the correct name and must have its contents surrounded by a comment line on either side (dashed lines are commonly used but the comment line can contain anything)
3. Input/Output, General, and Histogram Generation Settings must always have the same settings.
4. Other settings groups can have a variable number of parameters.
5. Settings can come in any order within a group.

See the default.set format for examples.


### Driver
```driver.py``` provides the user with an interactive command line driver program, which when ran can either use the default settings file (```default.set```) or users can import a different settings file. Follow initial instructions to choose .set file.   
**Using Driver**   
The main menu has 5 main options:
* m - run the entire program through the [main driver](#main)
* t - calculate [time differences](#time-difference-calculator)
* p - create [plots](#rossihistogram) of the time difference data
* f - [fit](#fitting) the data to an exponential curve
* s - view or edit the program [settings](#settings-configurations)
* Leave the command blank to end the program.


### Editor
Settings can be edited live during runtime using a vim. This operation is handled by ```editor.py```.

**Editor Options**

There are a few choices when using the settings editor:
* c - edit/view the current runtime settings.
* i - overwrite current settings with an imported .set file.
* n - create a blank settings file.

**vim Commands**

When editing settings, a vim editor will open in the command tab. There are a couple of essential commands that should be known to be able to effectively modify the settings.

When in view mode:
* $ - Go to the end of the current line
* 0 - Go to the beginning of the current line
* Shift + arrow key: Go mutiple spaces in the direction of the arrow

To enter/exit editing mode:
* s or a - enter editing mode
* ctrl + C: exit editing mode:

To close the vim:
* :wq or :exit

*WARNING*: Try to avoid exiting/quitting the program while in the editing vim. To use vim, temporary files are created that will not be correctly deleted if vim editing is halted incorrectly. Additionally, the entire terminal tab formatting may be affected.

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
