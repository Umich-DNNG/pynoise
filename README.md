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
The files that you will need in order to use the Rossi-Alpha program are fitting.py, plots.py, timeDifs.py, Rossi_alpha_settings.txt, and a file that you want to analyze. The format of the file you want to analyze should be a txt file with a list of time stamps of neutron detection times, separated by new lines. The format of the Rossi_alpha_settings.txt should be a list of settings:
* reset time   
* bin width   
* minimum cutoff   
* fit range : format the range as follows [min,max] with min and max being ints  
* plot scale   
* time difference method : 'any_and_all'  
* digital delay   
* number of folders   
* meas time per folder 
* sort data? : select yes if the data file you provide is unsorted, no otherwise
* color : 'b', 'g', 'r', 'c', 'm', 'y', 'k', 'w'
* linestyle : '-', '--', '-.', ':', or ' '
* linewidth : float value, sets the line width in points.
* marker : see https://matplotlib.org/stable/api/markers_api.html#module-matplotlib.markers for complete list of options
* alpha : must be within the 0-1 range, inclusive.
Users can edit this .txt file to change the settings that they wish to use.
INSERT DESCRIPTION OF DIFFERENT SETTINGS. 
color, linestyle,linewidth, and alpha are all settings for the graph. 



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