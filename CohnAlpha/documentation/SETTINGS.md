# Cohna Alpha Settings
The CohnAlpha program can be run with a variety of options that change the visual output and type of analysis being run. Here are the breakdown of the subsettings related to the CohnAlpha analysis:

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
