'''The file that runs code related to the GUI implementation.'''

import os
import numpy as np
from tkinter import *
import gui
import settings as set
from RossiAlpha import analyzeAll as mn
from RossiAlpha import fitting as fit
from RossiAlpha import plots as plt
from RossiAlpha import timeDifs as dif
from PowerSpectralDensity import PSD

# Where the time difference data us stored.
time_difs = None
time_difs_file = None
time_difs_method = None
# Where the histogram plot data is stored.
histogram = None
hist_file = None
hist_method = None
# Where the best fit curve data is stored.
best_fit = None

def warningFunction(popup: Tk, to):

    '''The function that is called when the user chooses to ignore a warning.
    
    Requires:
    - popup: the warning window that will be deleted.
    - to: the main function that will be called.
    '''

    # Destroy the warning window and run the desired function.
    popup.destroy()
    to()

def shutdown(window: Tk, parameters: set.Settings, file: str):

    '''Save settings to the specified file at the end of runtime.
    
    Requires:
    - window: the main window that will be closed down.
    - file: the absolute path of the file being saved to.
    - parameters: the settings object holding the current settings.
    
    If no file is given, the function assumes the 
    file is in the global response variable.'''

    # If the file already exists, warns the user of the overwrite.
    if os.path.isfile(file):
        gui.warning(lambda: shutdown(window, parameters, file))
        # Return so the window isn't deleted.
        return
     # Otherwise, save to the new file.
    else:
        if file == os.path.abspath('default.json'):
            parameters.write(file)
        else:
            parameters.save(file)
    # Close the program.
    window.destroy()

def createTimeDifs(parameters: set.Settings):

    '''Copy and pasted function from raDriver for creating time differences.

    Requires:
    - parameters: the settings object holding the current settings.
    
    See the original for more info.'''

    global time_difs, time_difs_file, time_difs_method
    name = parameters.settings['Input/Output Settings']['Input file/folder']
    name = name[name.rfind('/')+1:]
    if name.count('.') > 0:
        if parameters.settings['Input/Output Settings'].get('Data Column') is not None:
            data = np.loadtxt(parameters.settings['Input/Output Settings']['Input file/folder'],delimiter=" ", usecols=(parameters.settings['Input/Output Settings']['Data Column']))
        else:
            data = np.loadtxt(parameters.settings['Input/Output Settings']['Input file/folder'])

        if parameters.settings['General Settings']['Sort data']:
            data = np.sort(data)
        time_difs = dif.timeDifCalcs(data, 
            parameters.settings['RossiAlpha Settings']['Reset time'], 
            parameters.settings['RossiAlpha Settings']['Time difference method'])
        time_difs = time_difs.calculate_time_differences()
        time_difs_file = parameters.settings['Input/Output Settings']['Input file/folder']
        time_difs_method = parameters.settings['RossiAlpha Settings']['Time difference method']

def createPlot(parameters: set.Settings):

    '''Copy and pasted function from raDriver for creating the histogram.

    Requires:
    - parameters: the settings object holding the current settings.
    
    See the original for more info.'''

    global time_difs, histogram, hist_file, hist_method
    histogram = plt.RossiHistogram(parameters.settings['RossiAlpha Settings']['Reset time'],
                              parameters.settings['RossiAlpha Settings']['Bin width'],
                              parameters.settings['Histogram Visual Settings'],
                              parameters.settings['Input/Output Settings']['Save directory'])
    histogram.plot(time_difs,
              save_fig=parameters.settings['General Settings']['Save figures'],
              show_plot=parameters.settings['General Settings']['Show plots'])
    hist_file = parameters.settings['Input/Output Settings']['Input file/folder']
    hist_method = parameters.settings['RossiAlpha Settings']['Time difference method']

def calculateTimeDifsAndPlot(parameters: set.Settings):

    '''Copy and pasted function from raDriver for creating the 
    time differences and histogram plot in parallel.

    Requires:
    - parameters: the settings object holding the current settings.
    
    See the original for more info.'''

    global histogram, time_difs, hist_file, hist_method
    time_difs = None
    if parameters.settings['Input/Output Settings'].get('Data Column') is not None:
        data = np.loadtxt(parameters.settings['Input/Output Settings']['Input file/folder'],delimiter=" ", usecols=(parameters.settings['Input/Output Settings']['Data Column']))
    else:
        data = np.loadtxt(parameters.settings['Input/Output Settings']['Input file/folder'])

    if parameters.settings['General Settings']['Sort data']:
        data = np.sort(data)

    thisTimeDifCalc = dif.timeDifCalcs(data, parameters.settings['RossiAlpha Settings']['Reset time'], parameters.settings['RossiAlpha Settings']['Time difference method'])

    histogram, counts, bin_centers, bin_edges = thisTimeDifCalc.calculateTimeDifsAndBin(parameters.settings['RossiAlpha Settings']['Bin width'], parameters.settings['General Settings']['Save figures'], parameters.settings['General Settings']['Show plots'], parameters.settings['Input/Output Settings']['Save directory'], parameters.settings['Histogram Visual Settings'])
    hist_file = parameters.settings['Input/Output Settings']['Input file/folder']
    hist_method = parameters.settings['RossiAlpha Settings']['Time difference method']

def plotSplit(parameters: set.Settings):

    '''The split for plotting the histogram to determine 
    whether it is generated in series or parallel with 
    creating the time differences.
    
    Requires:
    - parameters: the settings object holding the current settings.'''

    global time_difs, time_difs_method, time_difs_file
    # If no time difs have been made or the input file/
    # method of time difference calculation has changed.
    if time_difs is None or (not 
                             (time_difs_method == parameters.settings['RossiAlpha Settings']['Time difference method'] 
                          and time_difs_file == parameters.settings['Input/Output Settings']['Input file/folder'])):
        # Combine time difference calculation and plot generation if applicable.
        if (parameters.settings['RossiAlpha Settings']['Combine Calc and Binning']):
            calculateTimeDifsAndPlot(parameters)
        # Otherwise, do them separately.
        else:
            createTimeDifs(parameters)
            createPlot(parameters)
    # Otherwise, just create the plot.
    else:
        createPlot(parameters)

def createBestFit(parameters: set.Settings):

    '''Copy and pasted function from raDriver for creating a line of best fit.
    
    Requires:
    - parameters: the settings object holding the current settings.

    See the original for more info.'''

    global time_difs, histogram, best_fit
    counts = histogram.counts
    bin_centers = histogram.bin_centers

    best_fit = fit.RossiHistogramFit(counts, bin_centers, parameters.settings)
        
    best_fit.fit_and_residual(save_every_fig=parameters.settings['General Settings']['Save figures'], 
                              show_plot=parameters.settings['General Settings']['Show plots'])

def raAll(single: bool, parameters: set.Settings):

    '''Run all of the Rossi Alpha analyis.
    
    Reqires:
    - single: a boolean that marks whether the input is a single file or folder.
    - parameters: the settings object holding the current settings.'''

    global time_difs, histogram, best_fit
    # Run and save accordingly based on the input type.
    if single:
        time_difs, histogram, best_fit = mn.analyzeAllType1(parameters.settings)
    else:
        mn.analyzeAllType2(parameters.settings)

def raSplit(mode: str, parameters: set.Settings):

    '''The main driver for the Rossi Alpha analysis. 
    Checks for user error and saved data overwriting.
    
    Requires:
    - mode: a string of the analysis that is desired. It should 
    exactly match the name of the function to be called.
    - parameters: the settings object holding the current settings.'''

    global time_difs, histogram, best_fit

    # If no input defined, throw error.
    if parameters.settings['Input/Output Settings']['Input file/folder'] == 'none':
        gui.error('You currently have no input file or folder defined.\n\n'
            + 'Please make sure to specify one before running any analysis.\n')
    # If user does have an input.
    else:
        # Get name of actual file/folder without entire path.
        name = parameters.settings['Input/Output Settings']['Input file/folder']
        name = name[name.rfind('/')+1:]
        # If name has a . in it, assume a single file.
        if name.count('.') > 0:
            # If time difference method is not any and all, throw an error.
            if parameters.settings['RossiAlpha Settings']['Time difference method'] != 'any_and_all':
                gui.error('To analyze a single file, you must use '
                    + 'the any_and_all time difference method only.\n')
            # Otherwise, split on the analysis type.
            else:
                match mode:
                    # Run all analysis; no checks needed.
                    case 'raAll':
                        raAll(True, parameters)
                    # Create time differences.
                    case 'createTimeDifs':
                        # If time differences already exist, warn user.
                        if time_difs is not None:
                            gui.warning(lambda: createTimeDifs(parameters),
                                    'There are already stored time differences '
                                    + 'in this runtime. Do you want to overwrite them?')
                        # Otherwise, create with no warning.
                        else:
                            createTimeDifs(parameters)
                    # Create a histogram plot.
                    case 'plotSplit':
                        # If histogram already exists, warn user.
                        if histogram is not None:
                            gui.warning(lambda: plotSplit(parameters),
                                    'There is an already stored histogram '
                                    + 'in this runtime. Do you want to overwrite it?')
                        # Otherwise, create with no warning.
                        else:
                            plotSplit(parameters)
                    # Create a best fit + residual.
                    case 'createBestFit':
                        # If best fit already exists, warn user.
                        if best_fit is not None:
                            gui.warning(lambda: createBestFit(parameters),
                                    'There is an already stored best fit line '
                                    + 'in this runtime. Do you want to overwrite it?')
                        # Otherwise, create with no warning.
                        else:
                            createBestFit(parameters)
        # Otherwise, assume folder data.
        else:
            # If modular analysis is attempted, throw and error.
            if mode != 'raAll':
                gui.error('You can only run full folder analysis.\n\n'
                      + 'These modular options are for single files.')
            # Otherwise, run the full analysis.
            else:
                raAll(False, parameters)

def conduct_PSD(parameters: set.Settings):

    '''Copy and pasted function from psdDriver for 
    running Power Spectral Density analysis.

    Requires:
    - parameters: the settings object holding the current settings.
    
    See the original for more info.'''

    file_path = parameters.settings['Input/Output Settings']['Input file/folder']

    values = np.loadtxt(file_path, usecols=(0,3), max_rows=2000000, dtype=float)

    PSD_Object = PSD.PowerSpectralDensity(list_data_array=values, 
                                        leg_label="TEST", 
                                        clean_pulses_switch=parameters.settings['PSD Settings']['Clean pulses switch'], 
                                        dwell_time=parameters.settings['PSD Settings']['Dwell time'], 
                                        meas_time_range=parameters.settings['PSD Settings']['Meas time range'])
    
    PSD_Object.conduct_APSD(show_plot=parameters.settings['General Settings']['Show plots'], 
                            save_fig=parameters.settings['General Settings']['Save figures'],
                            save_dir=parameters.settings['Input/Output Settings']['Save directory'])

def format(value):

    '''Converts a variable to a properly formatted string. 
    This is needed for floats in scientific notation.
    
    Requires:
    - value: the variable that is to be converted into a string.'''

    # If variable is a list.
    if isinstance(value, list):
        response ='['
        # For each entry, properly convert it to a string and 
        # add it to the list string with a separating ', '.
        for entry in value:
            response += format(entry) + ', '
        # Remove the extra ', ' and close the list.
        response = response[0:len(response)-2] + ']'
        # Return completed list.
        return response
    # If variable is a float and is of an excessively large or 
    # small magnitude, display it in scientific notation.
    elif isinstance(value, float) and (value > 1000 or value < -1000 or (value < 0.01 and value > -0.01 and value != 0)):
        return f'{value:g}'
    # Otherwise, just return a string cast of the variable.
    else:
        return str(value)

def saveType(value: str):

    '''Converts the output of a tkinter string variable to 
    its proper value for storage. WARNING: this implementation 
    does not support nested lists or any dictionaries.
    
    Requires:
    - value: the string to be converted to a value.'''

    # If variable is a list:
    if value[0] == '[':
        # Get rid of brackets and make empty list variable.
        value = value[1:len(value)-1]
        response = []
        # Loop while there are still entries in the list string.
        while value.find(', ') != -1:
            # Add the proper type of the next variable.
            response.append(saveType(value[0:value.find(', ')]))
            # Remove the appended variable from the list string.
            value=value[value.find(', ')+2:]
        # Append the final value.
        response.append(saveType(value))
        # Return the completed list.
        return response
    # If string represents a boolean, return accordingly.
    elif value == 'True':
        return True
    elif value == 'False':
        return False
    # If string is numeric, cast it to an integer.
    elif value.isnumeric():
        return int(value)
    # Try casting the response to a float.
    try:
        response = float(value)
        # If it works, return the float.
        return response
    # Otherwise, assume a string type and return it.
    except ValueError:
        return value
    
def edit(inputs: dict, parameters: set.Settings, prev):

    '''Save the inputs from the editor menu to the settings.
    
    Requires:
    - inputs: a dictionary of tkinter string variables. 
    Should have groups that match the current settings.
    - parameters: the settings object holding the current settings.
    - prev: the GUI function for the menu 
    to return to after the settings menu.'''

    # For each group and setting in the inputs, convert the 
    # string to the correct time and save it accordingly.
    for group in inputs:
        for setting in inputs[group]:
            parameters.settings[group][setting] = saveType(inputs[group][setting].get())
    # Return to the settings menu.
    gui.setMenu(prev)

def download(parameters: set.Settings, file: str, append: bool, prev):

    '''Download the file given in the global response variable.
    
    Requires:
    - parameters: the settings object holding the current settings.
    - file: the absolute path of the file being saved to.
    - append: a boolean that represents whether this download is 
    meant for appending or overwriting the entire settings.
    - prev: the menu to return to after downloading.'''

    # If file exists.
    if os.path.isfile(file):
        # If in append mode.
        if append:
            # If settings have not been initialized, read in the defualt.
            if parameters.origin == 'None':
                parameters.read(os.path.abspath('default.json'))
            # Append the file to the current settings.
            parameters.append(file)
        # If in overwrite mode, read in the settings.
        else:
            parameters.read(file)
        # Return to the previous menu.
        prev()
    # If not, throw an error.
    else:
        gui.error(file + ' is not a correct path or references an invalid settings '
              + 'file.\n\nMake sure that your settings file is named correctly, '
              + 'the correct absolute/relative path to it is given, and '
              + 'you did not include the .json extenstion in your input.')