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
* fit range   
* plot scale   
* time difference method   
* digital delay   
* number of folders   
* meas time per folder 
* sort data?  
Users can edit this .txt file to change the settings that they wish to use.
INSERT DESCRIPTION OF DIFFERENT SETTINGS. 


