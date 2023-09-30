# FeynmanY Method

This section of the PyNoise suite is for FeynmanY Algorithm analysis. If you are unfamiliar with the FeynmanY method, please familiarize yourself before using this package and reading the README file.



### Requirements

Besides those mentioned in the main README file, the following programs must be downloaded to run Power Spectral Density analysis:
* Event.py
* feynman.py
* fyDriver.py

Required python libraries (can be automated with requirements.txt from the main README.md):  
* NumPy   
* Matplotlib   
* Scipy

Additionally, you will need the following:
* A single file of data that will be analyzed.
* A settings configuration file (see the settings section for more information).



### I/O FILE INFO

The format of the file you want to analyze should be a .txt file with a list of inputs separated by new lines.



### Settings Configurations

The FeynmanY program can be run with a variety of options that change the visual output and type of analysis being run. In the settings file, this is listed as the FeynmanY Settings. The settings are as follows: 

* Tau range (*list*): The start and end of the tau values that you want to derive from.
* Increment (*int*): The tau increment as you go through tau range.
* Plot scale (*str*): The scale of the plot.

### Driver
```fyDriver.py``` is used to run all analysis pertaining to the FeynmanY method, and is called from the main driver. **Trying to call fyDriver independently will not work**. 
There are 2 options for this method:  
* m - run the entire program through the [main driver](#main)
* s - view or edit the program [settings](#settings-configurations)
* Leave the command blank to end the program.


### Editor
The editor class for modifying settings is also accessible from the CohnAlphaDriver. See the main README file for more information on its proper use.


### CohnAlpha.py

feynman.py will have the following functions:
* class FeynmanY: __init__()
* randomCounts()
* FeynmanY_histogram()
* computeMoments()
* computeYY2()
* plot()
* fitting()


The class FeynmanY: __init__() function will initialize a FeynmanY object
Inputs:
* tau_range: = [30, 3000]
* increment_amount: int = 30
* plots_scale: str = "log"

The class FeynmanY: randomCounts() will convert a list of Events into random trigger gate frequencies
Inputs:
* triggers: list[evt.Event]
* tau: int
* meas_time: float = -1

The class FeynmanY: FeynmanY_histogram() creates a histogram from a numpy array of random trigger probabilities
Inputs:
* probabilities
* show_plot: bool = False
* save_fig: bool = False
* save_dir: str = './'
* hvs: dict = None

The class FeynmanY: computeMoments() creates the two moments from probabilities
Inputs:
* probabilities: list
* tau: int


The class FeynmanY: computeYY2() computes the Y and Y2 values
Inputs:
* tau: int

The class FeynmanY: plot() plots the Y and Y2 distribution
Inputs:
* taus
* ys
* save_fig: bool = False
* show_plot: bool = False
* save_dir: str = './'


The class FeynmanY: fitting() plots the line of best fit and the corresponding residuals
Inputs:
* x_data
* y_data
* gamma_guess
* alpha_guess
* save_fig: bool = False
* show_plot: bool = False
* save_dir: str = './'
* fit_opt: dict = {}
* scatter_opt: dict = {}
* type: str = 'Y'


Output:
- A figure where the top half represents the FeynmanY distribution and bottom half represents the corresponding residuals

Running through all FeynmanY analyses will produce an image that is similar to the following: 

<img src="./FeynmanY_fitting.png" width="400" >
<img src="./FeynmanY2_fitting.png" width="400" >