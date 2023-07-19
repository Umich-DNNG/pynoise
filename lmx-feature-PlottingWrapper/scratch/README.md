# This is a script used for analyzing and plotting subcritical neutron noise data files
The outputs are images and/or csv files.

This script utilizes a modified version of FAUST/lmx.

To run, simply type "python PlotWrapper.py".
The user should only have to interact with PlotWrapper.py.
The user should only modify lines between "# begin user specifications" and "# end currently-supported user specifications".

A separate file, 'script_batch.py' can be used to make multiple PlotWrapper.py files with different filepaths.
This is run independently and should be run via "python script_batch.py".
Similarly, the user should only modify lines between "# begin user specifications" and "# end user specifications"

'script_modify.py' is somewhat similar to 'script_batch.py', but is used to modify a PlotWrapper.py file using user-defined lists.
This is run independently and should be run via "python script_modify.py".
As above, the user should only modify lines between "# begin user specifications" and "# end user specifications"

'default_params.py' is another script that can be run separately. It will first backup PlotWrapper.py, then will override the user-specifications in PlotWrapper.py with those in 'default_params.py'. This is mostly used for modifying to defaults right before pushing an update.

## Needed modules
The following python modules are needed: marshmallow, matplotlib, glob, sys, csv, numpy, os, time, scipy, copy, itertools, shutil.
From the command prompt (assuming you have python), "pip list" will show you currently installed modules. 
To install modules, run python command prompt as administrator, then "pip install X --proxy http://proxyout.lanl.gov:8080"

In addition, this uses a modified version of FAUST/lmx to read, analyze, and interact with .lmx files.
The user must have this modified version of FAUST/lmx (the currently supported version will not work).

## Installation notes
On first use, there might be a failure due to smores/marshmallow.
There should be a smores folder located in the FAUST directory.

In addition, there may be a conflict if an instance of smores is installed already (via pip or conda).
The user may have to uninstall smores via pip or conda prior to proceeding?

## Paths

Note that two paths need to be setup by the user (use of "compare_combine_Y2_rate_results_and_Feynman_sum" may require additional paths).
The first is the path in which the FAUST directory is located.
This is the line "sys.path.append()".

The second is the location of the input files.
This is the line "filepath = ".

Regarding output paths:
1. If "output_nested_subdirectories" is set to False, then the output files (images and/or csv files) will all be placed in the same directory as the input file(s). This is not recommended.
2. If "output_nested_subdirectories" is set to True, then the output files will be located in a subdirectory, nested inside the directory of the input file(s). This is recommended (and you can just put a name such as "save_path = 'output'").

## Supported file types

Three types of input files are supported (specified by the 'input_type = ' line):
1. input_type = '.lmx': these are list-mode data files in .lmx file format.
2. input_type = '.xml': these are .xml files that contain binned Feynman histograms. This has only been tested with .xml files output by Momentum v0.45.10b.
3. input_type = '.csv': these are .csv files created from previous executions of the PlotWrapper.py script. Either .csv files from individual files or sum_Feynman_histograms is allowed. Using .csv files fromcombine_Y2_rate_results is currently not supported. 

The script will analyze and plot every file of the specified type that is located in the specified directory. If there are no files with the extension listed for "input_type", then the script will exit and display a message.

Two output image formats are produced for each plot: one file is .png and the other is .pdf.

## Analysis options

There are 7 main analysis types currently supported by this script. These can be turned on/off using True/False statements. If all 7 analysis types are set to False, then essentially there is nothing for the script to do. It simply exits and displays a message to reflect this. 
More than one calculation type can be set to True.
Note that depending on the input file sizes, the analysis type(s) chosen, and the number of gate-widths, it may take a very long time to run the script.

There are also three calculation types related to a Feynman analysis:
1. If calculation_type is set '' (or anything other than #2 and #3 below), then any Feynman results include moments and rates only.
2. If calculation_type is set to 'Cf', then the results of #1 above are calculated, but in addition, a detector efficiency is calculated using a known Cf252 spontaneous fission emission (set via "Cf252_Fs") and spontaneous fission emission uncertainty (set via "Cf252_dFs").
3. If calculation_type is set to 'Multiplicity', then the singles and doubles are used to solve for leakage multiplication and spontaneous fission rate. Note that perform_Y2_single_fit and/or perform_Y2_double_fit must be set to True, as fitting Y2 is required for the analysis. This will utilize nuclear data parameters (listed under 'Nuclear data specifications').

### plot_histograms
This is used to plot Feynman histograms. If set to True, then it will output an image of a Feynman histogram for each gate-width for each file. In addition, if more than one input file is present, then there will also be an image that overlays all of the files on the same plot (one file per gate-width). 
There are two additional options associated with plotting histograms:
1. histogram_match_axis: If this is set to True, then two sets of Feynman histograms are output. For the second set of outputs, the x and y axis will be the same for all gate-widths of the same input file. This is useful if using the images to make a movie showing how the histograms evolve as the gate-width changes (contact Jesson for more info on this).
2. histogram_normalize: If this is set to False (the default), then the y-axis of the Feynman histograms is the frequency (i.e. the number of gates that n neutron events occurred, often referred to as Cn). If this is set to True, then the y-axis of the Feynman histograms is the probability (i.e. Cn/sum(Cn), often referred to as pn).

### plot_individual_files
This is used to plot Feynman histogram parameters versus gate-width for individual files. This will output moments, reduced factorial moments, and rates (Y1, Y2, R1, and potentially R2 depending on the other user options). A different image file is output for each parameter.

### plot_all_files_vs_gw
This is used to overlay all files on the same plot. Here the x-axis is the gate-width and the series is each file. The y-axis will include moments, reduced factorial moments, and rates (Y1, Y2, R1, and potentially R2 depending on the other user options); a different image file is output for each parameter. It is not recommended to do this if there are more than about 10 files.

### plot_all_files_vs_con
In these plots, the x-axis is the configuration. The y-axis will include moments, reduced factorial moments, and rates (Y1, Y2, R1, and potentially R2 depending on the other user options); a different image file is output for each parameter. A different image file is output for each gate-width.

### plot_channels
These are plots of the number of counts in each channel. 'channel_display' can be set to 'MC15_1' (for one MC-15), 'MC15_2' (for two MC-15s), or 'Other' (which will just all non-zero channels). There are two additional options related to this called "use_title" and "title_prefix". If "use_title" is set to True, then the plots will have a title (which includes "title_prefix", followed by the "detector number").

### perform_Rossi
This will plot Rossi-alpha analysis results.

### read_header
If this is set to True, then the script will read in the .lmx file header and print information from it. Note that if the input type is set to '.xml' or '.csv', there is no header to read. 

## Fitting
For Y2, there are two fitting options: perform_Y2_single_fit and perform_Y2_double_fit. The user can set either/both of these to True in order to perform fitting of Y2 results. This will be used for additional parameters (R2, etc.).
Random sampling of Y2 can be performed using: Y2_fit_randomized_data. If this is set to True, then the user must specifiy Y2_fit_randomized_data_number_points and Y2_fit_randomized_data_number_fits. Y2_fit_randomized_data_number_points is the number of points used in the fit (default is 'automatic'). Y2_fit_randomized_data_number_fits is the number of times to perform a fit.

For Rossi-alpha, there is only one fitting option: perform_Rossi_fits. If this is set to True, then both a single and double exponential fit will be performed on the Rossi-alpha data.

## Important user options

The most important user options are those related to paths, see the section "Paths" above.

Other important user options include:
1. combine_Y2_rate_results: If this is set to True, then Y2 rate results will be combined. Here combined means that the average (over all files) is reported, as is the standard deviation and an uncertainty. The uncertainty is a sum of squares of the uncertainty reported for each file. This should only be performed if all measurements are identical (i.e. repeat measurements).
2. sum_Feynman_histograms: If this is set to True, then the histograms for each file are summed. This should only be performed if all measurements are identical (i.e. repeat measurements).
3. compare_combine_Y2_rate_results_and_Feynman_sum: Useful for validation of combine and sum histograms. If set to True, this will read in 'Combined_rates.csv' and 'Histogram_Sum_Rates.csv' files (from the paths provided) and output overlay plots. If combine_Y2_rate_results and sum_Feynman_histograms are set to True, then user paths are not required.
4. file_descriptions: This is a tuple that contains a string that the user would like to use for each file in legends. One example would be ('Configuration 1', 'Configuration 2'). The user must understand the order that the script will read the input files (which generally matches sorted filenames alphabetically). If the user wishes not to have any info specified, then this can be left empty "file_descriptions = ()".
5. gatewidth_list: This is a list containing all of the user-selected gatewidth in nano-sec. Several examples are commented out. 
Note that if the input type is set to '.xml', then the gate-widths use depend on the parameter xml_user_gatewidths. If xml_user_gatewidths is set to True, then the user-specific gatewidth_list is used, but ONLY gate-widths in the .xml file are used. If then the user-specific gatewidth_list is set to False, then the user-specific gatewidth_list is ignored and the gate-widths within the .xml file are used.
If the input type is set to '.csv', the user gate-widths are never used (and the gate-widths in the .csv files are used instead).
6. The Rossi options 'Rossi_reset_time' and 'Rossi_bin_num' are the parameters used for Rossi-alpha binning. 
7. output_csv: If this is set to True, then a .csv file with the relevant parameters are output, depending on the calculation type(s) used.
8. combine_statistical_plots: if this is set to True, then additional statistical plots will be generated. 
10. backup_script: If this is set to True, then a copy of the PlotWrapper.py script will be pasted in the output directory. It is recommended to always set this to True.
11. exit_on_FIFO: If This is set to True, and the .lmx file header has FIFO losses (FIFO > 0), then the script will exit. If this is set to False and FIFO losses are present, then a warning will still appead. Note that FIFO losses can only be checked for .lmx files.
12. perform_bkg_subtract_rates: If this is set to True, background subtraction will be performed. 'bkg_subtract_fname' is the filename of the BKG file. Note that the BKG file needs to be in the same 'filepath'.

## Minor user options
There are several minor user options, including:
1. marker_size: The marker size used in plots
2. yaxis_log: Used to specify if the user would like to put the y-axis on a log scale in plots or not. May not work for all supported plot types.
3. plot_titles: Used to specify if the user would like to have the filename in the title of the plot. May not work for all supported plot types.
4. des_on_vs_config: if this is set to True, 'file_descriptions' (instead of an arbitrary file number) will be used on the x-axis of 'plot_all_files_vs_con' plots.


## Notes
1. There appears to be a minor bug associated with the creation of Feynman histograms for lmx files. It only seems to exist for high-count rate systems with short count times.

## Potential workflows

### Comparing different configurations
This workflow is used to overlay plots from different configurations.
1. Setup "PlotWrapper.py" with the following:
	a. "filepath" of the data location
	b. desired "input_type"
	c. Optional: add in file descriptions ("file_descriptions")
	d. set the analysis types as desired
	e. choose the desired gate-widths ("gatewidth_list") if using .lmx file "input_type".
	f. set the desired Rossi options (if "perform_Rossi" is set to True)
	g. all other options can likely be set to default values
2. Run using "python PlotWrapper.py"

### Benchmark analysis 
This workflow assumes that each directory has very similar files (i.e. multiple files on the exact same configuration)
This results in statistical checks to ensure validation of methods and checks for data quality.
1. If .xml input_type is desired, run the .lmx files in Momentum using batch mode. Ensure that appropriate gate-widths are used (the default will work for most systems).
2. For each configuration (see "script_batch.py" and/or 'script_modify.py' to help make input files) you should run "PlotWrapper.py". The "calculation_type" should be set appropriately (see notes above). Recommend setting "plot_all_files_vs_gw", "plot_all_files_vs_con", "combine_Y2_rate_results", "combine_statistical_plots", "sum_Feynman_histograms", and "compare_combine_Y2_rate_results_and_Feynman_sum" to True. It may be desirable to set "perform_Y2_single_fit", "perform_Y2_double_fit", "perform_Rossi" and/or "perform_Rossi_fits" to True as well.
3. If it is desired to plot results of "sum_Feynman_histograms" for different configurations together, then those have to be copied manually to a single location and run using the workflow described above (Comparing different configurations).

### Analysis of split files
This workflow is used to compare split files to measured files.
This results in statistical checks to ensure validation of methods and checks for data quality.
1. Create split files using "split_LMX_files_v3.py". The use of that script is outside the scope of this document, but info can be found here: \\slip.lanl.gov\robba\NEN2_resources\ListModeData\LMXprocessing_scripts
2. Run both the split .lmx files and the original .lmx files in Momentum using batch mode. Ensure that appropriate gate-widths are used (the default will work for most systems).
3. For each configuration (see "script_batch.py" if you would like to run multiple configurations simultaneously) you should run "PlotWrapper.py" for the split files. The "calculation_type" should be set appropriately (see notes above). Recommend setting "plot_all_files_vs_gw", "plot_all_files_vs_con", "combine_Y2_rate_results", and "combine_statistical_plots" to True. It may be desirable to set "perform_Y2_single_fit" and/or "perform_Y2_double_fit" to true as well.

## Outstanding/known issues:
1. If you get the error "UnicodeDecodeError: 'charmap' codec can't decode byte 0x8d in position 3157: character maps to <undefined>" related to "[events_list.extend(ReadToEvents(current_file))]" OR
   If you get "NameError: name 'eventsFromLMX' is not defined" related to "[events_list.extend(eventsFromLMX(current_file))]", this is likely related to merge issues.
   'eventsFromLMX' is in the 'feature/rossi' branch of the 'ToEvents.py' file, but it is not in the main branch. So it is likely that you need to get this from the 'feature/rossi' branch.
2. Similar to #1, "AttributeError: 'FeynmanHistogram' object has no attribute 'plotHistogram'" is likely related to the fact that FeynmanHistogram.py is different on the 'feature/rossi' and master branches. Likely a copy from the 'old/modified' folder is needed (this is really bad...).
3. Again, similar to #1, "NameError: name 'readLMXFile_old' is not defined" is likely related to an old instance of 'factory.py'.
