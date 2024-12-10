# Cohn Alpha Method
This section of the PyNoise suite is for Cohn Alpha (aka Power Spectral Density) Algorithm analysis. If you are unfamiliar with the Cohn Alpha method, please familiarize yourself before using this package and reading the README file. Some resources on the Rossi Alpha method can be found below:

* **[Enter Resource Links Here]**


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

### **CohnAlpha.py**
CohnAlpha.py will have the following functions:
* CAFit(): Represents the Cohn Alpha fitting function
* class CohnAlpha: __init__(): Constructs a Cohn Alpha object
* class CohnAlpha: plotCountsHistogram(): Plots the counts histogram.
* class CohnAlpha: welchApproxFourierTrans(): applies the Welch Approximation to a histogram and generates a scatterplot
* class CohnAlpha: fitPSDCurve(): fits the Power Spectral Density curve to the scatterplot as well as generates residuals

### **Driver**
```CohnAlphaDriver.py``` is used to run all analysis pertaining to the Cohn Alpha method, and is called from the main driver. **Trying to call psdDriver independently will not work**. 
There are 5 options for this method:  
* m - run the entire program through the [main driver](#main)
* p - plot the [histogram](#histogram) of the provided time data
* w - perform the Welch Approximation of the Fourier Transformation
* a - perform APSD
* c - perform CPSD
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

Once input file/folder has been defined, the all methods can be used. Otherwise, with no input file/folder defined, only exiting the program and changing the settings are allowed.

Any methods requiring additional data will automatically attempt to load in required data or generate the required data. For example, Welch's Approximation will automatically generate the histogram if no histogram information can be found.

All methods attempt to first load in raw graph data, saved through the "Save raw data" setting. In order to load in the raw graph data, the program's runtime settings must match the graph data's settings, located within the filename. The data should be named as follows: ca_[hist or graph]_[input file/folder]_[dwell time]_[measure time range start]-[measure time range end]_[nperseg value].csv. In addition, the file must be located within the directory under "Save directory" listed in the settings.

For example, with an input file named "stilbene_2in_CROCUS_20cm_offset_east.txt", and using the default CohnAlpha settings, the program would generate a file with histogram data with the name: ca_hist_2000000.0_150000000000.0-1000000000000.0_4096.csv

An example of the default settings for the Cohn Alpha method can be found in the default.json, or in the [CohnAlpha SETTINGS.md file](https://github.com/Umich-DNNG/pynoise/blob/master/CohnAlpha/documentation/SETTINGS.md)

### **Output**
- A figure where the top half represents the Cohn Alpha distribution and bottom half represents the corresponding residuals
- A figure that represents the Cohn Alpha Counts Histogram plot

<img width="500" alt="Screenshot 2024-04-17 at 1 56 48 PM" src="https://github.com/Umich-DNNG/pynoise/assets/90876107/82f29960-4a8b-490a-b247-e09f645d5570">
<img width="500" alt="Screenshot 2024-04-17 at 1 56 52 PM" src="https://github.com/Umich-DNNG/pynoise/assets/90876107/652f8bba-06d7-44a3-a478-88a7d2754a41">
