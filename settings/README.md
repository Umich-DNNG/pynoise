# Settings

This folder contains all the relevant settings that are fed into the three analysis methods for Rossi-Alpha, Cohn-Alpha, and Feynman Y. These settings were chosen to make the program more modular and enable the ability to adjust the input parameters in real time. This section will outline each subgroup of settings and the acceptable values for each parameter. There are different categories of settings as follows:  

## Format

Setting options can be stored after runtime in .json files for later use. Because settings files are read through the default JSON reader, the user must ensure that the json is properly formatted and all values are correctly inputted. Please review json formatting or the default.json file to ensure this is done correctly:

```
{
    "Input/Output Settings": {
        "Input file/folder": "none",
        "Time column": 0,
        "Channels column": null,
        "Save directory": "./data",
        "Save figures": false,
        "Save raw data": false,
        "Keep logs": false,
        "Quiet mode": false
    },
    "General Settings": {
        "Number of folders": 10,
        "Verbose iterations": false,
        "Sort data": true,
        "Show plots": false
    },
    "RossiAlpha Settings": {
        "Time difference method": "aa",
        "Digital delay": 750,
        "Reset time": 1000,
        "Combine Calc and Binning": false,
        "Bin width": 9,
        "Error Bar/Band": "band",
        "Fit minimum": 30,
        "Fit maximum": null
    },
    "CohnAlpha Settings": {
        "Dwell time": 2e6,
        "Meas time range": [
            1.5e11,
            1e12
        ],
        "Clean pulses switch": true,
        "Font Size": 12, 
        "Annotation Font Weight": "bold",
        "Annotation Color": "black",
        "Annotation Background Color": "white",
        "nperseg": 4096
    },
    "FeynmanY Settings": {
        "Tau range": [30, 3000],
        "Increment amount": 30,
        "Plot scale": "linear"
    },
    "Semilog Plot Settings": {
        "label": "Frequency Intensity",
        "markeredgecolor": "#162F65",
        "markeredgewidth": 0.2,
        "markerfacecolor": "#B2CBDE"
    },
    "Histogram Visual Settings": {
        "alpha": 1,
        "fill": true,
        "color": "#B2CBDE",
        "edgecolor": "#162F65",
        "linewidth": 0.4
    },
    "Line Fitting Settings": {
        "color": "#162F65",
        "linestyle": "-",
        "linewidth": 1,
        "label": "Fit"
    },
    "Scatter Plot Settings": {
        "color": "#B2CBDE",
        "edgecolor": "#162F65",
        "linewidth": 0.4,
        "marker": "o",
        "s": 20
    }
}

```

 A complete settings file must also follow the following structure:
1. Brackets must enclose the entire settings JSON object.
2. Within this, each setting group *must* be included.
3. Input/Output Settings, General Settings, RossiAlpha Settings, and PSD Settings must contain all of the settings defined in default.json and each setting must be assigned the correct data type.
4. For the remaining sections, any number of matplotlib settings can be included. See the Settings Configurations section for more info.

## Initializing Settings
Upon starting the PyNoise project, the user will be prompted to initialize the program settings. Default settings have been chosen based on rigorous testing to ensure the most commonly optimal parameters. However, a user may desire alternate settings that will be frequently used (for example, different settings for running single file vs. folder analysis). As such, there is also an option to import settings from another .json file. There are two options for importing files:
* o - overwrite the entire settings, not including anything from the default. Ensure this file is compliant with the requirements stated in the Settings Input Format section.
* a - append the settings onto the default. This mode will download default.json settings first, and then from the given file will overwrite, append, and delete settings as necessary. This type of settings file is more flexible and has the following structure:
    1. Brackets must still enclose the entire settings JSON object.
    2. To change a specific setting, create the settings group and the setting within it with the correct data type for its value. If this setting already exists within the default, it will overwrite the default value with the one specified here. If the setting is new, it will create the setting and set the value. To remove a setting, set its value to an empty string (""), regardless of the normal data type. This will indicate to the prgram that this setting should be removed. *NOTE: this means you should never input a blank string for a setting you want to keep. Leave a placeholder value like "none", or "empty".*
    3. Creating and deleting settings should be used for the matplotlib visual settings only.
    4. Empty setting groups can be given - if no settings are within them, there will be no effect.

See single.json for an example of appropriate append file syntax.

## Editing Settings

Settings can be edited live during runtime using a vim in terminal mode, or in the window in GUI mode. Editing in the window is intuitive, but the vim requires a little more explanation.

**Edit/View Current Settings**

This will open up the settings currently in use in the vim. Here you can modify settings directly on a json file. At the end of editing, the settings will be completely overwritten by whatever is currently in this vim. As such, ensure the vim file is in compliance with the formatting outlined in the Settings Input Format section.

See the vim Commands section for more information on how to use the vim.

**Import .json File**

Like when initializing settings, the user can choose to append settings from the file or use the file to completely overwrite the current settings. See the Initializing Settings section for more information.

**Blank .json File**

This method is for appending settings. It will open up a properly formated settings file with each settings group empty. Any settings that should be edited/append/deleted can then be written into the group. After editing, the program will append the vim file onto the current settings accordingly. For more information on append file format/use, see the Initializing Settings section.

See the vim Commands section for more information on how to use the vim.

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

*WARNING*: Try to avoid exiting/quitting the program while in the editing vim. To use vim, temporary files are created that will not be correctly deleted if vim editing is halted incorrectly. Additionally, terminal tab formatting may be affected and functionality may be broken.

## List of Settings

**INPUT/OUTPUT SETTINGS**: This section contains information about the input and output details of the program.
* Input file/folder (*path*): users should input the absolute or relative path to the file/folder that the user wants analyzed. See specific method README files for the exact formatting of these input files. **Please avoid naming folders with periods, as our program differentiates between files and folders by counting periods in the input name.**
* Time column (*int*): Specify which column in your data files (if data is in .txt format) the time differences are recorded in (with the leftmost column corresponding to column 0, and incrementing as your move right).
* Channels column (*int*): Specify which column in your data files (if data is in .txt format) the channels are recorded in (with the leftmost column corresponding to column 0, and incrementing as your move right). If your .txt file does not contain channels, or you do not want to read them in, you will need to specify ```null``` as the channels column to avoid errors.
* Save directory (*path*): Should a user desire to save graphs generated by the program, this absolute or relative path to a folder will be where the graphs are saved.
* Save figures (*boolean*): If true, graphs generated by the program will be saved to the specified directory.
* Save raw data (*boolean*): If true, the raw analysis data will be exported as a .csv file.
* Keep logs (*boolean*): If true, logs will be kept in the (hidden) .logs folder, which keep track of changes made to the settings and types of analyses run. For more information, see the respective README file.
* Quiet mode (*boolean*): If true, enables quiet mode (see the quiet mode section for more information).

**GENERAL PROGRAM SETTINGS**: This section contains general program settings that are applied to all methods of analysis.
* Number of folders (*int*): When analyzing a folder of data, this specifies how many folders within the given directory should be analyzed.
* Verbose iterations (*boolean*): If true and running on folder data, each subfolder will prooduce output instead of just aggregate data.
* Sort data (*boolean*): If true, the time stamps given in the input files will be sorted from least to greatest.
* Show plots (*boolean*): If true, graphs generated by the program will appear on screen when created.

**ROSSIALPHA SETTINGS**: This section has settings specific to Rossi Alpha analysis. Please see the Rossi Alpha README file for more information.

**COHNALPHA SETTINGS**: This section has settings specific to Power Spectral Density analysis. Please see the PSD README file for more information.

**FEYNMANY SETTINGS**: This section has settings specific to Power Spectral Density analysis. Please see the PSD README file for more information.

**SEMILOG PLOT SETTINGS**: These settings correspond to the built-in matplotlib semilogx settings for whenever the program generates a semilog plot for CohnAlpha. See https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.semilogx.html for full documentation of options. All options on the website are supported.

**HISTOGRAM VISUAL SETTINGS**: These settings correspond to the built-in matplotlib histogram settings for whenever the program generates a bar graph. See https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.bar.html for full documentation of options. All options on the website are supported.

**LINE FITTING SETTINGS**: These settings correspond to the built-in matplotlib plot settings for whenever the program generates a line of best fit for data. See https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html for full documentation of options. All options on the website are supported.

**SCATTER PLOT SETTINGS**: These settings correspond to the built-in matplotlib plot settings for whenever the program generates a residual graph for the line of best fit. See https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.scatter.html for full documentation of options. All options on the website are supported. 
