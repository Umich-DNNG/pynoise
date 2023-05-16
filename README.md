# PyNoise

A repository for a Python suite of neutron noise analysis algorithms. This draws inspiration from faust lmx on gitlab.lanl.gov. This suite is designed specifically for pulse time-of-detection chains from organic scintillator arrays.

## Rossi-Alpha Method

### Setup
You will need to install python and then install numpy.   
To begin, you must create a local repo. To do this, initialize the local repo by typing the following command into your terminal:   
```$ git init```   
This will create a .git subdirectory which will contain files for the repo.   
To check the status of the repo at any point, type:    
```$ git status```   
To clone the project onto your machine locally, type   
```$ git clone https://gitlab.eecs.umich.edu/umich-dnng/pynoise.git```

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
    * any_and_all :  
    * any_and_all cross_correlations :  
    * any_and_all cross_correlations no_repeat :  
    * any_and_all cross_correlations no_repeat digital_delay :  
* digital delay   
* number of folders : when using file type 2, this is the number of folders you want analyzed  
* meas time per folder :  
* sort data? : select yes if the data file you provide is unsorted, no otherwise  
**HISTOGRAM VISUAL SETTINGS:** these settings correspond to the histogram settings see https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html for full documentation of options TODO: change code to get boolean values
* color : 'b', 'g', 'r', 'c', 'm', 'y', 'k', 'w'
* linestyle : '-', '--', '-.', ':', or ' '
* linewidth : float value, sets the line width in points.
* marker : see https://matplotlib.org/stable/api/markers_api.html#module-matplotlib.markers for complete list of options
* alpha : must be within the 0-1 range, inclusive.  
**GENERATING HISTOGRAM SETTINGS**  
* reset time :   
* bin width : the width of the histogram bins  
* minimum cutoff :  
**LINE FITTING SETTINGS** : visual settings for the fit line see https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html for full documentation of options   
* color : 'b', 'g', 'r', 'c', 'm', 'y', 'k', 'w'   
* linestyle : '-', '--', '-.', ':', or ' '   
* linewidth : float value, sets the line width in points.   
* marker : see https://matplotlib.org/stable/api/markers_api.html#module-matplotlib.markers for complete list of options   

Users can edit this .txt file to change the settings that they wish to use.




### Plotting
In the plots.py file, there is a class called "Plot" which is umbrella class that encompasses all the important plotting functions. Currently, there is one function under "Plot" called "plot(self, time_diffs)", in which the input parameter time_diffs is an array of time differences generated from the "timeDifCalcs" class.

Firstly, a Plot() object must be created first with the parameters below: 

* reset_time (numeric)
* bin_width (numeric)
* show_plot (boolean)
* options (dict)
* x_axis (string)
* y_axis (string)
* title (string)

From there, the Plot.plot() function will construct the corresponding histogram. The option show_plot can be set to whether you want to show the plot and save the plot or not. Finally, it will also return: counts, bin_centers, and big edges. These outputs will be used in various fitting functions in the next section.