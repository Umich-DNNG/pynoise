# Settings

This folder contains all the relevant settings that are fed into the three analysis methods for Rossi-Alpha, Cohn-Alpha, and Feynman Y. These settings were chosen to make the program more modular ang enable the ability to adjust the input parameters in real time.

## Input/Output Settings

These settings are applicable to all three methods.

- "Input file/folder": "none" is the setting that specifies the input file that will be fed into pipeline
- "Time column": 0 is the setting... TODO
- "Channels column": null is the setting... TODO
- "Save directory": "./data" is the setting that specifies the directory in which all of the plot will be saved into
- "Save figures": false is the setting that controls whether plots should be saved
- "Save raw data": false is the setting that controls whether raw output are outputted 
- "Keep logs": false is the setting that controls whether a log should be outputted 
- "Quiet mode": false is the setting that controls whether you want to silence all the text output for each step

## General Settings

These settings are applicable to all three methods.

- "Fit range": [0.0, 1000.0] represents the range of fittig
- "Number of folders": 10 represents the number of folders that you want to conduct the analysis on (only for multi-folder analysis)
- "Verbose iterations": false represents... TODO
- "Sort data": true represents whether the input data should be sorted
- "Show plots": false represents whether plots should be shown


## RossiAlpha Settings

These settings are ONLY applicable to the Rossi-Alpha method.

- "Time difference method": "any_and_all" represents the time difference method performed on the data input
- "Digital delay": 750 represents... TODO
- "Combine Calc and Binning": false represents whether calculating the binning and the creating the histogram should be combined
- "Reset time": 1000 represents... TODO
- "Bin width": 9 represents the width of the histogram bins
- "Error Bar/Band": "band" represents the type of measuring the error
- "Minimum cutoff": 30 represents when the line fitting should start


## CohnAlpha Settings

These settings are ONLY applicable to the CohnAlpha method.

- "Dwell time": 2e6 represents... TODO
- "Meas time range": [1.5e11, 1e12] represents... TODO
- "Clean pulses switch": true represents... TODO
- "Annotation Font Weight": "bold" represents the weight of the annotation font
- "Annotation Color": "black" represents the color of the annotation font
- "Annotation Background Color": "white" represents the background color of the annotation font


## FeynmanY Settings

These settings are ONLY applicable to the FeynmanY method.

- "Tau range": [30, 3000] represents the range of tau values
- "Increment amount": 30 represents the increment interval in the tau range
- "Plot scale": "log" represents the type of scale 


## Semilog Plot Settings"

These settings are ONLY applicable to the semilog in CohnAlpha method.

- "label": "Frequency Intensity" represents the legend label of the data points
- "markeredgecolor": "#162F65" represents edge color of the data points
- "markeredgewidth": 0.2 represents width of the data points
- "markerfacecolor": "#B2CBDE" represents the face color of the data points


## Histogram Visual Settings

These settings are ONLY applicable to the visual in Rossi-Alpha method.

- "alpha": 1 represents the alpha value
- "fill": true represents whether to fill the histogram bins visually
- "color": "#B2CBDE" represents the color of the histogram
- "edgecolor": "#162F65" represents the edge color of the histogram
- "linewidth": 0.4 represents... TODO


## Line Fitting Settings

These settings are ONLY applicable to the line fitting in Rossi-Alpha method.

- "color": "#162F65" represents the color of the fitted line
- "linestyle": "-" represents the style of the fitted line
- "linewidth": 1 represents the width of the fitted line
- "label": "Fit" represents the legend label of the fitted line

## Scatter Plot Settings

These settings are utilized in the residual plots in all three methods.

- "color": "#B2CBDE" represents the color of the residual data points
- "edgecolor": "#162F65" represents the edge color of the residual data points
- "linewidth": 0.4 represents the line width of the residual data points
- "marker": "o", represents the style of residual data points
- "s": 20 represents the size of the residual data points