# Cohn Alpha Method

This section of the PyNoise suite is for Cohn Alpha (aka Power Spectral Density) Algorithm analysis. If you are unfamiliar with the Power Spectral Density method, please familiarize yourself before using this package and reading the README file.


### **Requirements**
Required python libraries (can be automated with requirements.txt from the main README.md):  
* NumPy   
* Matplotlib   
* Scipy

Additionally, you will need the following:
* A single file of data that will be analyzed.
* A settings configuration file (see the settings section for more information).


### **I/O FILE INFO**

The format of the file you want to analyze should be a .txt file with a list of inputs separated by new lines. A sample snippet of an input file is shown below.

<img width="243" alt="Screenshot 2024-04-17 at 1 59 33 PM" src="https://github.com/Umich-DNNG/pynoise/assets/90876107/530ffa80-0cdb-4a53-97c5-521d40cd7132">


Furthermore, sample data inputs can be found with this link: [Google Drive - Sample Data](https://drive.google.com/drive/folders/1jEswA6AqeNLgGJW6iXs1Ti7XEXad9D0w)


### **Settings**
The CohnAlpha program can be run with a variety of options that change the visual output and type of analysis being run. In the settings file, this is listed as the CohnAlpha Settings. 

"Input/Output Settings": 
* "Input file/folder" (*str): Input data pathway.

"General Settings":
* "Show plots": Boolean setting controlling whether you want to show plots.

"CohnAlpha Settings":
* "Dwell time": This is the timing gate to record counts and the fluctuation between "dwells" are used to derive the distribution.
* "Meas time range": The measurement time range set by two float values in a list that denotes start and end.
* "Plot Counts Histogram": Boolean setting controlling whether you want to plot the Cohn Alpha counts histogram.
* The rest of the settings are the visual settings that can be adjusted.

"Scatter Plot Settings"
* These are the visual settings that can be adjusted.

A .json snippet example is shown below. You can reference the matplotlib website to check out available setting options here: [Maplotlib Website](https://matplotlib.org/stable/api/pyplot_summary.html)

```python
"Input/Output Settings": {
        "Input file/folder": INSERT INPUT PATHWAY HERE,
        "Time column": 0,
        "Channels column": null,
        "Save directory": "./data",
        "Save figures": false,
        "Save raw data": false,
        "Keep logs": false,
        "Quiet mode": false
    },

"General Settings": {
    "Number of folders": null,
    "Verbose iterations": false,
    "Sort data": true,
    "Show plots": true
},

"CohnAlpha Settings": {
        "Dwell time": 2000000.0,
        "Meas time range": [
            150000000000.0,
            1000000000000.0
        ],
        "Plot Counts Histogram": true,
        "Font Size": 12,
        "Annotation Font Weight": "bold",
        "Annotation Color": "black",
        "Annotation Background Color": "white",
        "nperseg": 4096

"Scatter Plot Settings": {
        "color": "#B2CBDE",
        "edgecolor": "#162F65",
        "linewidth": 0.4,
        "marker": "o",
        "s": 20
    }
},
```


### **CohnAlpha.py**
CohnAlpha.py will have the following functions:
* CAFit(): Represents the Cohn Alpha fitting function
* class CohnAlpha: __init__(): Constructs a Cohn Alpha object
* class CohnAlpha: conductCohnAlpha(): Performs the analysis

### **Driver**
```CohnAlphaDriver.py``` is used to run all analysis pertaining to the Cohn Alpha method, and is called from the main driver. **Trying to call psdDriver independently will not work**. 
There are 2 options for this method:  
* m - run the entire program through the [main driver](#main)
* s - view or edit the program [settings](#settings-configurations)
* Leave the command blank to end the program.

### **How To Run CohnAlpha Method**
* Open the terminal and navigate to where the PyNoise repository is located.
* Enter "python3 main.py" and you will see the following menu:
```
Welcome to the DNNG/PyNoise project.
With this software we are taking radiation data from fission reactions (recorded by organic scintillators) and analyzing it using various methods and tools.
Use this Python suite to analyze a single file or multiple across numerous folders.

Would you like to use the default settings or import another .json file?
d - use default settings
i - import custom settings
Select settings choice:
```
* You can either use default settings or import your own custom settings.
* After specifying your settings, you will see the following menu:
```
Initializing program with default settings...
Settings from default.json succesfully imported.

Settings initialized. You can now begin using the program.

----------------------------------------------------------

You can utitilze any of the following functions:
r - run Rossi Alpha analysis
c - run Cohn Alpha Analysis
f - run Feynman Y Analysis
s - view or edit the program settings
Leave the command blank or enter x to end the program.
Enter a command:
```
* To run the Cohn Alpha Analysis, enter "c" as the command.
* Upon specifying the CohnAlpha analysis, you will reach this menu:
```
What analysis would you like to perform?
m - run the entire program through the main driver
t - calculate time differences
p - create plots of the time difference data
f - fit the data to an exponential curve
s - view or edit the program settings
Leave the command blank or enter x to return to the main menu.
```
* Enter "m" to run the entire CohnAlpha method and get your outputs.

### **Output**
- A figure where the top half represents the Cohn Alpha distribution and bottom half represents the corresponding residuals
- A figure that represents the Cohn Alpha Counts Histogram plot
CohnAlpha/documentation/README.md

<img width="500" alt="Screenshot 2024-04-17 at 1 56 48 PM" src="https://github.com/Umich-DNNG/pynoise/assets/90876107/82f29960-4a8b-490a-b247-e09f645d5570">
<img width="500" alt="Screenshot 2024-04-17 at 1 56 52 PM" src="https://github.com/Umich-DNNG/pynoise/assets/90876107/652f8bba-06d7-44a3-a478-88a7d2754a41">




