# RossiAlpha

This section of the PyNoise suite is for Rossi Alpha Algorithm analysis. This draws inspiration from faust lmx on gitlab.lanl.gov. This suite is designed specifically for pulse time-of-detection chains from organic scintillator arrays. If you are unfamiliar with the Rossi Alpha method, please familiarize yourself before using this package and reading the README file. Some resources on the Rossi Alpha method can be found below:


* [Rossi-Alpha Method](https://www.osti.gov/biblio/6188965)
* [Prompt Neutron Periods (Inverse Alpha)](https://doi.org/10.13182/NSE57-A25409)
* [Validation of Two-Region Rossi-Alpha](https://doi.org/10.1016/j.nima.2020.164535)

### Requirements

You will need the following inputs for the analysis:
* A single file or folder of data that will be analyzed.
* A settings configuration file (see the settings section for more information).

### I/O FILE INFO

The format of the file you want to analyze should be a .txt file with a list of time stamps of neutron detection times, separated by new lines. For folder analysis, the given folder should contain numbered folders that each contain data for analysis. A snippet of the sample data is shown below.

<img src="./sample_data.png" width="400" >

### How To Run RossiAlpha
* Create a .json file with the appropriate settings (default.json contains all the default settings)
* Input the pathway of your input data directory into the "Input file/folder" setting under "Input/Output Settings" in the .json file that you created (as shown in the .json snippet below)
```python
"Input/Output Settings": {
        "Input file/folder": INSERT PATHWAY HERE,
        "Time column": 0,
        "Channels column": null,
        "Save directory": "./data",
        "Save figures": false,
        "Save raw data": false,
        "Keep logs": false,
        "Quiet mode": false
    },
```
* Open your terminal and navigate to the PyNoise directory
* Type "python3 main.py" and hit enter (you should be prompted with a welcome message as shown below)
```
Welcome to the DNNG/PyNoise project.
With this software we are taking radiation data from fission reactions (recorded by organic scintillators) and analyzing it using various methods and tools.
Use this Python suite to analyze a single file or multiple across numerous folders.

Would you like to use the default settings or import another .json file?
d - use default settings
i - import custom settings
Select settings choice:
```
* Type "d" if you want to use the default settings or type "i" if you want to import the .json that created earlier
* If you are using the default settings, type "r" to run the RossiAlpha analysis (example shown below)
```
Would you like to use the default settings or import another .json file?
d - use default settings
i - import custom settings
Select settings choice: d

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
Enter a command: r
```
* If you are using the .json file from earlier, type "o" to run the RossiAlpha analysis (example shown below)
```
Would you like to use the default settings or import another .json file?
d - use default settings
i - import custom settings
Select settings choice: i

You have two import options:
o - overwrite entire settings
a - append settings to default
Enter a command (or leave blank to cancel): o
Overwrite mode selected.
Enter a settings file (no .json extension): [ENTER YOUR JSON FILE NAME WITHOUT THE ".json" HERE]
```
* The results should either pop up on the screen, saved to a folder, or both.

### Settings Configurations

The RossiAlpha program can be run with a variety of options that change the visual output and type of analysis being run. In the settings file, this is listed as the RossiAlpha Settings. The settings are as follows: 
* Reset time (float): the maximum time difference to consider during analysis, in the units given by the "Input time units" setting.
* Time difference method (*string or list*): This refers to the way you want the time differences generated. the options are:  
    * "aa" (representing any and all): Considers all time differences within the reset time.
    * "cc" (representing cross correlations): Considers all time differences except those from the same detector/channel.
    * "dd" (representing digital delay): Follows cross correlation analysis and considers a digital delay for each detector between each detection time.
    * You can only run methods involving cross correlation ("cc" and "dd") when you have specified a time column in the Input/Output Settings.
    * These options can be given alone or can be given as a list. For example, if you wanted to run all three types of analysis, you would put ["aa", "cc", "dd"] in the settings file.
* Digital delay (*int*): The amount of digital delay, if applicable (see above).
* Combine Calc and Binning (*bool*): if true, will build the histogram as the time differences are calculated.
* Bin width (float): the width of each histogram bin, in the units given by the "Input time units" setting.
    * When doing folder analysis, the bin width can be set to null. In this case, the program will automate the bin width to be as small as possible while ensuring the maximum average relative bin error is no higher than the following setting.
    * \sum_{i=1}^{100}i
* Max avg relative bin err (float): the maximum average relative bin error, as described above. This is given as a fraction; for example, if you wanted your maximum average relative bin error to be 10%, you would enter 0.10.


### Running the RossiAlpha Method from the Main Driver
<figure class="video_container">
 <video controls="true" allowfullscreen="true" style = "width: 500px;">
 <source src="./RossiAlphaDemo.mp4" type="video/mp4" >
 </video>
</figure>

### Driver
```raDriver.py``` is used to run all analysis pertaining to the Rossi Alpha method, and is called from the main driver. **Trying to call raDriver independently will not work**. The driver has been designed modularly, so that analysis at any stage can be done without having to run through the entire process. There are 5 main options:
* m - run the entire program through the [main driver](#main)
* t - calculate [time differences](#time-difference-calculator)
* p - create [plots](#rossihistogram) of the time difference data
* f - [fit](#fitting) the data to an exponential curve
* s - view or edit the program [settings](#settings-configurations)
* Leave the command blank to end the program.
