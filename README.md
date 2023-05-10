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

