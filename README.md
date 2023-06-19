# PyNoise Project

Welcome to the PyNoise Project! The goal of this Python suite is to process and analyze radiation data recorded from fission reactions. Our supported methods of analysis currently include Rossi Alpha and Power Spectral Density. For more information about these methods, please see the README files in their respective subdirectories.

## How to Use



### Requirements

To run the PyNoise project, the following programs ust be downloaded:
* driver.py
* editor.py
* settings.py
* raDriver.py
* psdDriver.py

### Python Packages & Virtal Environment.

Ensure that Python and ```pip``` are installed on your system. You can check this by running the following commands in the terminal:
```python
python --version
pip --version
```

Create a virtual environment (optional): It is recommended to isolate the programs' dependencies from other Python installations. In 
the terminal, navigate to the PyNoise directory and run the following command to create a virtual environment:
```python
python -m venv myenv
```

Activate the virtual environment (optional). Run the following command for the different operating systems:

For MacOS/Linux:
```python
source myenv/bin/activate
```

For Windows:
```python
myenv\Scipts\activate
```

With the virtual environment activated (or without one), navigate to the PyNoise directory and run the following command to install the 
project dependencies:
```python
pip install -r requirements.txt
```


Additionally, you will need the following:
* A single file or folder of data that will be analyzed.
* A settings configuration file (see the settings section for more information).

### Settings Configurations

The PyNoise program can be run with a variety of options that change the visual output and type of analysis being run. This section will outline each subgroup of settings and the acceptable values for each parameter. There are different categories of settings as follows:  

**I/O FILE INFO**: This section contains information about the input and output details of the program.
* Input file/folder (*path*): users should input the absolute or relative path to the file/folder that the user wants analyzed. See specific method README files for the exact formatting of these input files. **Please avoid naming folders with periods, as our program differentiates between files and folders by counting periods in the input name.**
* Data column (*int*): **TODO**: Write explanation for this.
* Save directory (*path*): Should a user desire to save graphs generated by the program, this absolute or relative path to a folder will be where the graphs are saved.
* Keep logs (*boolean*): If true, logs will be kept in the (hidden) .logs folder, which keep track of changes made to the settings and types of analyses run. For more information, see the respective README file.

**GENERAL PROGRAM SETTINGS**: This section contains general program settings that are applied to all methods of analysis.
* Fit range (*list of ints*): The beginning and end points of where the data will be fit.
* Number of folders (*int*): When analyzing a folder of data, this specifies how many folders within the given directory should be analyzed.
* Meas time per folder (*int*): **TODO**: what is this for?
* Quiet mode (*boolean*): If true, enables quiet mode (see the quiet mode section for more information).
* Sort data (*boolean*): If true, the time stamps given in the input files will be sorted from least to greatest.
* Save figures (*boolean*): If true, graphs generated by the program will be saved to the specified directory.
* Show plots (*boolean*): If true, graphs generated by the program will appear on screen when created.

**ROSSIALPHA SETTINGS**: This section has settings specific to Rossi Alpha analysis. Please see the Rossi Alpha README file for more information.

**PSD SETTINGS**: This section has settings specific to Power Spectral Density analysis. Please see the PSD README file for more information.

**HISTOGRAM VISUAL SETTINGS**: These settings correspond to the built-in matplotlib histogram settings for whenever the program generates a bar graph. See https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.bar.html for full documentation of options. All options on the website are supported.

**LINE FITTING SETTINGS**: These settings correspond to the built-in matplotlib plot settings for whenever the program generates a line of best fit for data. See https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html for full documentation of options. All options on the website are supported.

**RESIDUAL PLOT SETTINGS**: These settings correspond to the built-in matplotlib plot settings for whenever the program generates a residual graph for the line of best fit. See https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.scatter.html for full documentation of options. All options on the website are supported. 

### Settings Input Format
Setting options can be stored after runtime in .json files for later use. Because settings files are read through the default JSON reader, the user must ensure that the json is properly formatted and all values are correctly inputted. Please review json formatting or the default.json file to ensure this is done correctly. A complete settings file must also follow the following structure:
1. Brackets must enclose the entire settings JSON object.
2. Within this, each setting group *must* be included.
3. Input/Output Settings, General Settings, RossiAlpha Settings, and PSD Settings must contain all of the settings defined in default.json and each setting must be assigned the correct data type.
4. For the remaining sections, any number of matplotlib settings can be included. See the Settings Configurations section for more info.
5. Setting groups and settings can be listed in any order, but the order given in defualt.json is recommended.

**Initializing Settings**
Upon starting the PyNoise project, the user will be prompted to initialize the program settings. Default settings have been chosen based on rigorous testing to ensure the most commonly optimal parameters. However, a user may desire alternate settings that will be frequently used (for example, different settings for running single file vs. folder analysis). As such, there is also an option to import settings from another .json file. There are two options for importing files:
* o - overwrite the entire settings, not including anything from the default. Ensure this file is compliant with the requirements stated in the Settings Input Format section.
* a - append the settings onto the default. This mode will download default.json settings first, and then from the given file will overwrite, append, and delete settings as necessary. This type of settings file is more flexible and has the following structure:
    1. Brackets must still enclose the entire settings JSON object.
    2. To change a specific setting, create the settings group and the setting within it with the correct data type for its value. If this setting already exists within the default, it will overwrite the default value with the one specified here. If the setting is new, it will create the setting and set the value. To remove a setting, set its value to an empty string (""), regardless of the normal data type. This will indicate to the prgram that this setting should be removed. *NOTE: this means you should never input a blank string for a setting you want to keep. Leave a placeholder value like "none", or "empty".*
    3. Creating and deleting settings should be used for the matplotlib visual settings only.
    4. Empty setting groups can be given - if no settings are within them, there will be no effect.

See single.json for an example of appropriate append file syntax.

### Driver

After deciding what settings to include, the program will begin and you can select what command to do next:
* r - run Rossi Alpha Analysis
* p - run Power Spectral Density Analysis
* s - view or edit the program settings

See the respective README files and sections for more information on each command.

### Editor
Settings can be edited live during runtime using a vim. This operation is handled by ```editor.py```. There are a few choices when using the settings editor:
* c - edit/view the current runtime settings.
* i - overwrite/append current settings with an imported .json file.
* n - create a blank .json file to append new settings.

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

### Automating Commands

When the user wants to run the same thing multiple times, it may become tedious to manually enter each command. For this reason command inputs can be automated in two different ways. This section will walk through the example of opening the program, importing settings from auto.json, and closing the program. Commands for this would normally be:
* i - import custom settings
* a - append settings to default
* auto - the name of the settings file
* (blank) - exit the program
* q - confirm the quit
With both options, the commands need to be preceded by ```--command``` *or* ```-c```. The lets the the program know where to start reading command line arguments as program commands.

**Formatting**

Commands can be handed to the program through command line arguments when calling the program. There are two acceptable ways to pass commands:

1. Send raw commands as command line arguments. In this mode, the command line arguments can directly be the commands that would be entered during runtime. For the example, the formatting would be as follows:

```python3.10 driver.py --commands i a auto x q```

Alternatively:

```python3.10 driver.py -c i a auto x q```

Note that instead of an empty input for exiting the program, there is an x instead. This is because it is not possible to have empty command line arguments. As such, x is also a valid command for returning from submenus (Rossi Alpha, Power Spectral Density, and Settings Editor) as well as exiting the program. However, be aware that it is not acceptable to use an x command in any other circumstance. If a blank command is needed, use the following option to pass commands.

2. Send a file as a command line argument. In this mode, the file you are sending (can be given as an absolute or relative path) will contain a command on each line. As long as the file has as extension (.txt, for example), any file name is valid. In this example, the file will be called ```input.txt``` and will be formatted as follows:

```input.txt```:

i

a

auto

(blank)

q


Then, to run the program with these commands (in this case assuming input.txt is in the same folder as driver.py), the command line call would be:

```python3.10 driver.py --commands input.txt```

Alternatively:

```python3.10 driver.py -c input.txt```

Both of these examples would result in the same code execution. However, note it is possible to have a blank command in the file format (the (blank) text is just a placeholder - see the input.txt file included in this package for a literal example). For this reason, there should be no extra newlines at the end of the file unless the last desired command is a blank command.

**Flexibility and Restrictions**

The automated command input is quite flexibile - it can take in any number of command line arguments, and the user can mix and match raw commands and file names as needed. Furthermore, the commands given to the program do not need to end the program. If the program runs out of given commands, it will prompt the user to enter commands as usual.

Besides the necessity of the x command with raw commands, note there is another restriction on automated commands in that they cannot control vim editing. If an automated command chooses to edit the current settings or append new ones, it will be up to the user to manually do so. However, once the vim editor is closed the automated commands will continue running as normal.

### Quiet Mode

When enabled, quiet mode will silence all program outputs to the command line excluding error messages and input prompts. This mode is intended for automated commands, when the listing of options is unnecessary and may flood the command line tab with undesired output. ***It is not recommended*** to use this mode when manually running the program. When using quiet mode, ***it is recommended*** to keep logs enabled so that any important changes/analysis can be recorded for later reference.

Quiet mode can also be passed in as a command line argument as ```--quiet``` *or* ```-q```. This is because there are some inital messages that are printed before settings are initialized and are therefore unaffected by the later imported settings. Similarly, note that default settings have quiet mode turned off, so even if the program is run with ```--quiet```, using default settings will almost immediately turn this off. 

The --quiet and --commands argument are independent and can be listed in any order. However, please ensure that they only occur once at most, and that all program commands follow -c/--commands and come before -q/--quiet (if the quiet mode option is given after).

To run an example, enter the following command:

```python3.10 driver.py -c input.txt -q```

Alternatively:

```python3.10 driver.py -q -c input.txt```

### Using pyNoise as a Python Package

To download this program as a package, navigate into the pyNoise folder on your machine, and run the following command: 
```python setup.py sdist```
This should create a subfolder called "dist" within your pyNoise folder. Within the dist folder, there should be a file ending in .tar.gz. Install the package by running the following command with the correct path to this .tar.gz file:
```pip install ./dist/pyNoise-1.0.0.tar.gz```
You should now be able to use pyNoise as a python package. 