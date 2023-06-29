'''The file that runs code related to the GUI implementation.'''

import os
import io
import time
import numpy as np
from tkinter import *
from tkinter import ttk
import gui
import settings as set
from RossiAlpha import analyzeAll as mn
from RossiAlpha import fitting as fit
from RossiAlpha import plots as plt
from RossiAlpha import timeDifs as dif
from PowerSpectralDensity import PSD

#--------------------Global Variables--------------------#

# Where the time difference data us stored.
time_difs: dif.timeDifCalcs = None
time_difs_file: str = None
time_difs_method: str = None
# Where the histogram plot data is stored.
histogram: plt.RossiHistogram = None
hist_file: str = None
hist_method: str = None
# Where the best fit curve data is stored.
best_fit: fit.RossiHistogramFit = None

# The file that will have logs written to it.
logfile: io.TextIOWrapper = None

#--------------------GUI Functions--------------------#

def create_logfile():

    '''Create a log file for logging user interactions.'''

    global logfile
    # Ensure a log file does not already exist.
    if logfile is None:
        # Get local time.
        curTime = time.localtime()
        # Create log file name with relative path and timestamp.
        logName = ('./logs/' + str(curTime.tm_year) 
                    + '-' + str(curTime.tm_mon) 
                    + '-' + str(curTime.tm_mday) 
                    + '@' + str(curTime.tm_hour)
                    + (':0' if curTime.tm_min < 10 else ':') + str(curTime.tm_min)
                    + (':0' if curTime.tm_sec < 10 else ':') + str(curTime.tm_sec)
                    + '.log')
        # Open the logfile.
        logfile = open(os.path.abspath(logName),'w')
        # Write an introductory message at the top.
        logfile.write('# A logfile for the runtime started at the named '
                    + 'timestamp.\n# If keep logs is set to false at the end '
                    + 'of runtime, this file will automatically be deleted.\n')
        # Flush the file so it can be read immediately.
        logfile.flush()

def log(message: str,
        xor=None,
        window: Tk=None,
        menu=None):

    '''Log a message to the current window and the logfile.
    
    Requires:
    - message: the string that will be displayed.

    Optional:    
    - xor: a boolean that determines where this message should be displayed:
        - True: show only in the given label.
        - False: show only in the logfile.
        - not provided: show in both.
    - label: the label within which the notification will be put. 
    This is required when xor is True or not provided.
    - menu: if returning to a previous menu, this is that menu 
    function. If not defined, will assume staying on the same menu.'''

    global logfile
    if menu != None:
        error = menu()
    else:
        error = False
    if not error:
        if not isinstance(message,str):
            message = message()
        # When applicable, log the message to the logfile.
        if xor == None or not xor:
            # Create a timestamp for the confirmation message.
            curTime = time.localtime()
            log_message = (str(curTime.tm_year) 
            + '-' + str(curTime.tm_mon) 
            + '-' + str(curTime.tm_mday) 
            + ' @ ' + str(curTime.tm_hour) 
            + (':0' if curTime.tm_min < 10 else ':') + str(curTime.tm_min) 
            + (':0' if curTime.tm_sec < 10 else ':') + str(curTime.tm_sec) 
            + ' - ' + message.replace('\n',' ') + '\n')
            # Write the confirmation + timestamp to the file and flush 
            # immediately so user can see log updates in real time.
            logfile.write(log_message)
            logfile.flush()
        # When applicable, set the label in the window to have the correct message.
        if xor == None or xor:
            if window.children.get('log') == None:
                ttk.Separator(window,
                              orient='horizontal',
                              ).grid(column=0,row=window.grid_size()[1], sticky='ew')
                ttk.Label(window,
                        name='log',
                        text=message,
                        ).grid(column=0,row=window.grid_size()[1])
            else:
                window.children['log'].config(text=message)

def warningFunction(popup: Tk,
                    to):

    '''The function that is called when the user chooses to ignore a warning.
    
    Requires:
    - popup: the warning window that will be deleted.
    - to: the main function that will be called.
    '''

    # Destroy the warning window and run the desired function.
    popup.destroy()
    to()

def format(value):

    '''Converts a variable to a properly formatted string. 
    This is needed for floats/ints in scientific notation.
    
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
    # If variable is a float/int and is of an excessively large or 
    # small magnitude, display it in scientific notation.
    elif ((isinstance(value, float) or isinstance(value, int)) 
          and (value > 1000 
               or value < -1000 
               or (value < 0.01 and value > -0.01 and value != 0))):
        return f'{value:g}'
    # Otherwise, just return a string cast of the variable.
    else:
        return str(value)

def add(prev, group: str, blanks: dict):
    blanks[group] += 1
    gui.editor_menu(prev, blanks)

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

def changes(parameters: set.Settings):

    '''Compare recently edited settings to the 
    previous version and log any changes.
    
    Requires:
    - parameters: the settings object holding the current settings.
    
    Returns:
    - count: the number of changes made.'''

    # Create a baseline settings object for comparison.
    baseline = set.Settings()
    count = 0
    # Read in previous settings and delete temp file.
    baseline.read(os.path.abspath('./settings/comp.json'))
    os.remove(os.path.abspath('./settings/comp.json'))
    # For every setting in the current settings, compare its
    # value to the source value and log if it is new or changed.
    for group in parameters.settings:
        for setting in parameters.settings[group]:
            if (baseline.settings[group].get(setting) 
                != parameters.settings[group][setting]):
                log(setting + ' in ' + group + ': ' 
                    + format(baseline.settings[group].get(setting)) + ' -> '
                    + format(parameters.settings[group][setting]) + '.\n',
                    xor=False)
                count += 1
    # For each setting in the baseline, if it does not 
    # exist in the current settings, log the removal.
    for group in baseline.settings:
        for setting in baseline.settings[group]:
            if parameters.settings[group].get(setting) == None:
                log(setting + ' in ' + group + ' removed.\n', xor=False)
                count += 1
    return count

def edit(window: Tk,
         inputs: dict,
         newSet: dict,
         newVal: dict,
         parameters: set.Settings,
         prev):

    '''Save the inputs from the editor menu to the settings.
    
    Requires:
    - inputs: a dictionary of tkinter string variables. 
    Should have groups that match the current settings.
    - parameters: the settings object holding the current settings.
    - prev: the GUI function for the menu 
    to return to after the settings menu.'''

    for group in newSet:
        for i in range(0, len(newSet[group])):
            if newSet[group][i].get() != '' and newVal[group][i].get() != '':
                inputs[group][newSet[group][i].get()] = newVal[group][i]


    parameters.write(os.path.abspath('./settings/comp.json'))
    # For each group and setting in the inputs, convert the 
    # string to the correct time and save it accordingly.
    for group in inputs:
        for setting in inputs[group]:
            if inputs[group][setting].get() == '':
                if parameters.settings[group].get(setting) != None:
                    parameters.settings[group].pop(setting)
            else:
                parameters.settings[group][setting] = saveType(inputs[group][setting].get())
    # Compare the modified settings to the previous and save the number of changes.
    total = changes(parameters)
    # If there were changes made, notify the user.
    if total > 0:
        log('Succesfully made ' + str(total) + ' changes to the '
            + 'settings\n(see logfile for more information).',
            True,
            window,
            lambda: gui.setMenu(prev))
    else:
        gui.setMenu(prev)

def download(parameters: set.Settings,
             file: str,
             append: bool,
             prev):

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
                parameters.read(os.path.abspath('./settings/default.json'))
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
        return True

def export(window: Tk,
           parameters: set.Settings,
           file: str,
           warn: bool):

    '''Save settings to the specified file at the end of runtime.
    
    Requires:
    - window: the main window that will be closed down.
    - parameters: the settings object holding the current settings.
    - file: the absolute path of the file being saved to.
    - warn: a boolean that determines whether or not 
    the program should warn the user of the overwrite.
    
    If no file is given, the function assumes the 
    file is in the global response variable.'''

    # If the file already exists, warns the user of the overwrite.
    if warn and os.path.isfile(file):
        gui.warning(lambda: export(window, parameters, file, False))
        # Return so the shutdown doesn't happen twice.
        return
     # Otherwise, save to the new file.
    else:
        if file == os.path.abspath('./settings/default.json'):
            parameters.write(file)
            message = 'Default settings successfully overwritten.'
        else:
            parameters.save(file)
            message = 'Settings successfully saved to file:\n' + file + '.'
    shutdown(window, parameters, message)

def shutdown(window: Tk,
             parameters: set.Settings,
             message: str = None):

    '''Close the program & logfile and delete the logfile is applicable.
    
    Requires:
    - window: the main window that will be closed down.
    - parameters: the settings object holding the current settings.'''

    global logfile
    window.destroy()
    gui.byeMenu(message)
    # Close the logfile.
    logfile.close()
    # If user doesn't want logs, delete the logfile.
    if not parameters.settings['Input/Output Settings']['Keep logs']:
        os.remove(logfile.name)
    else:
        logfile = open(logfile.name,'r')
        lines = logfile.readlines()
        logfile.close()
        logfile = open(logfile.name,'w')
        logfile.write(lines[0])
        for line in lines[2:]:
            logfile.write(line)
        logfile.close()


#--------------------RossiAlpha Functions--------------------#

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

def raAll(single: bool,
          parameters: set.Settings):

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

def raSplit(window: Tk,
            mode: str,
            parameters: set.Settings):

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
        return True
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
                return True
            # Otherwise, split on the analysis type.
            else:
                match mode:
                    # Run all analysis; no checks needed.
                    case 'raAll':
                        raAll(True, parameters)
                        log(message='Successfully ran all analysis on file:\n'
                            +parameters.settings['Input/Output Settings']['Input file/folder'],
                            window=window)
                    # Create time differences.
                    case 'createTimeDifs':
                        # If time differences already exist, warn user.
                        if time_difs is not None:
                            gui.warning(lambda: log(message='Successfully recalculated time differences for file:\n'
                                                +parameters.settings['Input/Output Settings']['Input file/folder'],
                                                window=window,
                                                menu=lambda:createTimeDifs(parameters)),
                                    'There are already stored time differences '
                                    + 'in this runtime. Do you want to overwrite them?')
                        # Otherwise, create with no warning.
                        else:
                            createTimeDifs(parameters)
                            log(message='Successfully calculated time differences for file:\n'
                                +parameters.settings['Input/Output Settings']['Input file/folder'],
                                window=window)
                    # Create a histogram plot.
                    case 'plotSplit':
                        # If histogram already exists, warn user.
                        if histogram is not None:
                            gui.warning(lambda: log(message='Successfully recreated a histogram for file:\n'
                                                +parameters.settings['Input/Output Settings']['Input file/folder'],
                                                window=window,
                                                menu=lambda:plotSplit(parameters)),
                                    'There is an already stored histogram '
                                    + 'in this runtime. Do you want to overwrite it?')
                        # Otherwise, create with no warning.
                        else:
                            plotSplit(parameters)
                            log(message='Successfully created a histogram for file:\n'
                                +parameters.settings['Input/Output Settings']['Input file/folder'],
                                window=window)
                    # Create a best fit + residual.
                    case 'createBestFit':
                        # If best fit already exists, warn user.
                        if best_fit is not None:
                            gui.warning(lambda: log(message='Successfully recreated a best fit for file:\n'
                                                +parameters.settings['Input/Output Settings']['Input file/folder'],
                                                window=window,
                                                menu=lambda:createBestFit(parameters)),
                                    'There is an already stored best fit line '
                                    + 'in this runtime. Do you want to overwrite it?')
                        # Otherwise, create with no warning.
                        else:
                            plotSplit(parameters)
                            createBestFit(parameters)
                            log(message='Successfully created a best fit for file:\n'
                                +parameters.settings['Input/Output Settings']['Input file/folder'],
                                window=window)
        # Otherwise, assume folder data.
        else:
            # If modular analysis is attempted, throw and error.
            if mode != 'raAll':
                gui.error('You can only run full folder analysis.\n\n'
                      + 'These modular options are for single files.')
                return True
            # Otherwise, run the full analysis.
            else:
                raAll(False, parameters)
                log(message='Successfully ran all analysis with folder:\n'
                            +parameters.settings['Input/Output Settings']['Input file/folder'],
                            window=window)

#--------------------PowerSpectralDensity Functions--------------------#

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