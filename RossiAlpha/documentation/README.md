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

Our program takes files in the following format:
* Each detection is separated by a newline.
* Each piece of information is separated by white-space.

A sample is shown belowm, where the first column specifies the channel the detection was recorded on, the second column is the time of detection, and the remaining columns contain data not relevant to our analysis:

<img width="250" alt="Screen Shot 2024-04-10 at 1 27 47 PM" src="https://github.com/Umich-DNNG/pynoise/assets/112817120/a62c3f9f-c198-4c24-b495-57cbe7938886">


The columns for channel and time data can be in any order, but must be specified in the Input/Output Settings. There can also be no channel data, in which case this setting is null.

For folder analysis, the individual file setup is the same. In the folder the user gives in the Input/Output Settings, the program searches for numbered folders up through the number specified by the "Number of folders" setting. In each of these folders, the program searches for files of the name "board0ch{channel#}_n.txt", where {channel#} is an integer representing which channel the file contains data for. For this reason, these files do not need to contain channel data themsevles. An example setup is shown below, where the files with a green check mark are those that our program uses:

<img width="621" alt="Screen Shot 2024-04-10 at 1 38 37 PM" src="https://github.com/Umich-DNNG/pynoise/assets/112817120/d01a938b-42a5-4459-a609-d4d3f4ad9041">


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
    * The average relative bin error is calculated as the sum of counts(i) * error(i) for all n bins divided by the sum of counts(i)^2 for all n bins (where counts(i) is the number of time differences in the ith bin, and error is the error for the ith bin).
* Max avg relative bin err (*float*): the maximum average relative bin error, as described above. This is given as a fraction; for example, if you wanted your maximum average relative bin error to be 10%, you would enter 0.10.
* Error Bar/Band (*"bar" or "band"*): whether the error should be represented as a bar or a band on the histogram.
* Fit minimum (*float*): the time difference at which to start fitting an exponential curve to the histogram, in the units given by the "Input time units" setting.
* Fit maximum (*float*): the time difference at which to stop fitting an exponential curve to the histogram, in the units given by the "Input time units" setting.
    * If set to null, will fit all the way up to the reset time.

```math
SE = \left(\frac{\Sigma_{i=1}^n c_i\cdot e_i}{\Sigma_{i=1}^n c_i^2}\right)
```


### How To Run RossiAlpha Analysis
Our program allows for modular analysis, allowing you to run each portion of the analysis independently. For example, this allows you to generate time differences once, then play around with plot settings to get a graph that fits your visual requirements. Navigate to the RossiAlpha menu by running the command specified in the main README and following the instructions given by the program. Upon specifying RossiAlpha analysis, you will reach this menu:

```
What analysis would you like to perform?
m - run the entire program through the main driver
t - calculate time differences
p - create plots of the time difference data
f - fit the data to an exponential curve
s - view or edit the program settings
Leave the command blank or enter x to return to the main menu.
```

You can then select which analysis you need. If you request a plot but there are no current time differences, the program will automatically generate them for you.
