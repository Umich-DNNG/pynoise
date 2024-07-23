### Settings Configurations

The RossiAlpha program can be run with a variety of options that change the visual output and type of analysis being run. In the settings file, this is listed as the RossiAlpha Settings. The settings are as follows: 
* `Reset time` (*float*): the maximum time difference to consider during analysis, in the units given by the "Input time units" setting.
* `Time difference method` (*string*): This refers to the way you want the time differences generated. the options are:  
    * "aa" (representing any and all): Considers all time differences within the reset time.
    * "cc" (representing cross correlations): Considers all time differences except those from the same detector/channel.
    * "dd" (representing digital delay): Follows cross correlation analysis and considers a digital delay for each detector between each detection time.
    * You can only run methods involving cross correlation ("cc" and "dd") when you have specified a time column in the Input/Output Settings.
* `Digital delay` (*int*): The amount of digital delay, if applicable (see above).
* `Bin width` (*float*): the width of each histogram bin, in the units given by the "Input time units" setting.
    * File analysis does not calculate a bin width. You must supply one.
    * When doing folder analysis, the bin width can be set to null. In this case, the program will automate the bin width to be as small as possible while ensuring the Maximum Average Relative Bin Error (MARBE) is no higher than the following setting.
        * Note: MARBE is not fully implemented to compute a different bin width for each analysis, if a list is given. It will default to the first time difference method in the list.
    * The MARBE is calculated as follows:
$`
MARBE = \frac{\Sigma_{i=1}^n c_i\cdot e_i}{\Sigma_{i=1}^n c_i^2}
`$, where $`c_i`$ is the number of counts for the $`i^{th}`$ at this time bin, and $`e_i`$ is the error for the $`i^{th}`$ bin.
* `Max avg relative bin err` (*float*): the MARBE, as described above. For example, if you wanted your maximum average relative bin error to be 10%, you would enter 0.10.
* `Error Bar/Band` (*"bar" or "band"*): whether the error should be represented as a bar or a band on the histogram.
* `Fit minimum` (*float* or *list*): the time difference at which to start fitting an exponential curve to the histogram, in the units given by the "Input time units" setting.
    * NOTE: if this is set as a list, the length of it must be the same as the length of fit maximum
    * If set to a list, each index will correspond to one other to create multiple ranges. 
* `Fit maximum` (*float* or *list*): the time difference at which to stop fitting an exponential curve to the histogram, in the units given by the "Input time units" setting.
    * If set to null, will fit all the way up to the reset time.
    * NOTE: if this is set as a list, the length of it must be the same as the length of fit minimum

### Sample settings
```
"RossiAlpha Settings": {
        "Reset time": 500,
        "Time difference method": "aa",
        "Digital delay": 750,
        "Bin width": 3,
        "Max avg relative bin err": 0.10,
        "Error Bar/Band": "band",
        "Fit minimum": 30,
        "Fit maximum": null
    },
```