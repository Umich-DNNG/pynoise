# RossiAlpha

This section of the PyNoise suite is for Rossi Alpha Algorithm analysis. This draws inspiration from faust lmx on gitlab.lanl.gov. This suite is designed specifically for pulse time-of-detection chains from organic scintillator arrays. If you are unfamiliar with the Rossi Alpha method, please familiarize yourself before using this package and reading the README file. Some resources on the Rossi Alpha method can be found below:


* [Rossi-Alpha Method](https://www.osti.gov/biblio/6188965)
* [Prompt Neutron Periods (Inverse Alpha)](https://doi.org/10.13182/NSE57-A25409)
* [Validation of Two-Region Rossi-Alpha](https://doi.org/10.1016/j.nima.2020.164535)

### Requirements

You will need the following inputs for the analysis:
* A single file or folder of data that will be analyzed.
* A settings configuration file (Please review SETTINGS.md for the list of relevant settings for RossiAlpha analysis.).

### I/O FILE INFO

Our program takes files in the following format:
* Each detection is separated by a newline.
* Each piece of information is separated by white-space.

A sample is shown below, where the first column specifies the channel the detection was recorded on, the second column is the time of detection, and the remaining columns contain data not relevant to our analysis:

<img width="250" alt="Screen Shot 2024-04-10 at 1 27 47 PM" src="https://github.com/Umich-DNNG/pynoise/assets/112817120/a62c3f9f-c198-4c24-b495-57cbe7938886">


The columns for channel and time data can be in any order, but must be specified in the Input/Output Settings. There can also be no channel data, in which case this setting is `null`. The columns should follow zero-based numbering.

For folder analysis, the individual file setup is the same. In the folder the user gives in the Input/Output Settings, the program searches for numbered folders from 1 up through the number specified by the "Number of folders" setting. The "Number of folders" setting may also be `null`, in which case the analysis will utilize all folders sequentially numbered 1, 2, 3, and so on until it reaches a gap. In each of these folders, the program searches for files of the name "board0ch{channel#}_n.txt", where {channel#} is an integer representing which channel the file contains data for. For this reason, these files do not need to contain channel data themselves. An example setup is shown below, where the files with a green check mark are those that our program uses:

<img width="621" alt="Screen Shot 2024-04-10 at 1 38 37 PM" src="https://github.com/Umich-DNNG/pynoise/assets/112817120/d01a938b-42a5-4459-a609-d4d3f4ad9041">

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