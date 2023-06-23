'''The file that creates and runs all program GUI elements.'''

from tkinter import *
from tkinter import ttk
import tkinter as tk
import settings as set
import os
import numpy as np
from PowerSpectralDensity import PSD
from RossiAlpha import analyzeAll as mn
from RossiAlpha import fitting as fit
from RossiAlpha import plots as plt
from RossiAlpha import timeDifs as dif

# The main window that is used for the program.
window = None
# The settings used during runtime
parameters = None
# The response variable used for entry boxes.
response = None

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

def prompt(prev, to, message='Enter your choice:', title='User Prompt'):

    '''Create a prompt window to get a text input from the user.
    
    Requires:
    - prev: the function to return to if the user cancels the input.
    - to: the function that is called when the user confirms their input.
    
    Optional:
    - message: the message that the user sees above the entry box.
    - title: the title of the window'''

    global window, response
    response = tk.StringVar()
    # Clear the window of all previous entries, labels, and buttons.
    for item in window.winfo_children():
        item.destroy()
    # Properly name the window.
    window.title(title)
    # The label with the appropriate prompt message.
    ttk.Label(window,
              name='prompt',
              text=message
              ).grid(column=0,row=0)
    # The text box where the user can type their response.
    ttk.Entry(window,
              name='response',
              textvariable=response,
              ).grid(column=0,row=1)
    # The confirmation button.
    ttk.Button(window,
              name='continue',
              text='Continue',
              command=to
              ).grid(column=0,row=2)
    # The cancel button.
    ttk.Button(window,
              name='cancel',
              text='Cancel',
              command=prev
              ).grid(column=0,row=3)
    
def error(message='Something went wrong. Please contact the developers.',
          title='ERROR!'):
    '''Create an error popup for when the user encounters an error.
    
    Parameters:
    - message: the error message that the user will see.
    - title: the title of the window.
    
    If no parameters are given, a default error popup is shown. '''

    # Create a new popup and title it accordingly.
    popup=Tk()
    popup.title(title)
    # The label with the appropriate error message.
    ttk.Label(popup,
            name='message',
            text=message
            ).grid(column=0,row=0)
    # The button to confirm the user has seen the error.
    ttk.Button(popup,
               name='return',
               text='OK',
               command=popup.destroy
               ).grid(column=0,row=1)
    # Open the popup.
    popup.mainloop()

def warningFunction(popup, to):

    '''The function that is called when the user chooses to ignore a warning.
    
    Requires:
    - popup: the warning window that will be deleted.
    - to: the main function that will be called.
    '''

    # Destroy the warning window and run the desired function.
    popup.destroy()
    to()


def warning(to,
            message='This action will delete data. Are you sure you want to do this?',
            title='WARNING!'):

    '''Display a warning popup when the user is at risk of deleting/overwriting data.
    
    Requires:
    - to: the function to be called should the user choose to ignore the warning.
    
    Optional:
    - message: the warning the user will receive.
    - title: the title of the popup.'''

    # Create a new popup and title it accordingly.
    popup=Tk()
    popup.title(title)
    # The label with the appropriate warning message.
    ttk.Label(popup,
            name='message',
            text=message
            ).grid(column=0,row=0)
    # The yes button.
    ttk.Button(popup,
               name='yes',
               text='Yes',
               command=lambda: warningFunction(popup, to)
               ).grid(column=0,row=1)
    # The no button.
    ttk.Button(popup,
               name='no',
               text='No',
               command=popup.destroy
               ).grid(column=0,row=2)
    # Open the popup.
    popup.mainloop()

def shutdown(file=''):

    '''Save settings to the specified file at the end of runtime.
    
    Parameters:
    - file: the absolute path of the file being saved to.
    
    If no file is given, the function assumes the 
    file is in the global response variable.'''

    global window, response
    # If no file given.
    if file == '':
        # Get the file from the response variable and convert it to a path.
        file = os.path.abspath(response.get() + '.json')
        # If the file already exists, warns the user of the overwrite.
        if os.path.isfile(file):
            warning(lambda: shutdown(file))
            # Return so the window isn't deleted.
            return
        # Otherwise, save to the new file.
        else:
            parameters.save(file)
    # If a file is given.
    else:
        # If saving to the default, write the settings completely.
        if file == os.path.abspath('default.json'):
            parameters.write(file)
        # Otherwise, save a shortened version.
        else:
            parameters.save(file)
    # Close the program.
    window.destroy()

def shutdown_menu():

    '''Load the shutdown menu GUI if need be.'''

    global window, parameters
    # Compare the current settings to the most recently 
    # imported + appended and store the changes.
    list = parameters.compare()
    # If there were changes from the baseline.
    if len(list) != 0:
        # Clear the window of all previous entries, labels, and buttons.
        for item in window.winfo_children():
            item.destroy()
        # Properly name the window.
        window.title('Unsaved Changes')
        # Notify the user of unsaved changes and note their
        # most recently imported and appended settings.
        ttk.Label(window,
                name='message',
                text='You have made unsaved changes to the settings:\n\n'
                + 'Base settings: ' + parameters.origin + '\n\nMost recently '
                + 'appended settings: ' + parameters.appended + '\n'
                ).grid(column=0,row=0)
        # Keep track of the total listed changes.
        total = 0
        # For up to 5 entries in the list.
        while total != 5 and total < len(list):
            # List the entry.
            ttk.Label(window,
                name='entry' + str(total),
                text=list[total]
                ).grid(column=0,row=total+1)
            # Increase the count.
            total += 1
        # If there were more than 5 entries,
        # note how many more there are.
        if len(list) > 5:
            ttk.Label(window,
                name='extra',
                text='\n...plus ' + str(len(list)-5) + ' more change(s).'
                ).grid(column=0,row=6)
            total += 1
        # Ask the user what they want to do.
        ttk.Label(window,
                name='prompt',
                text='\nWhat would you like to do with your changes?'
                ).grid(column=0,row=total+1)
        # Button for saving current settings to the default.
        ttk.Button(window,
                name='default',
                text='Save as default',
                command=lambda: warning(lambda: shutdown(os.path.abspath('default.json')))
                ).grid(column=0,row=total+2)
        # Button for saving current settings to another file.
        ttk.Button(window,
                name='new',
                text='Save to other file',
                command=lambda: prompt(shutdown_menu,
                                       lambda: shutdown(),
                                       'Enter a name for the new settings '
                                        + '(not including the .json file extension).',
                                        'Export Settings',)
                ).grid(column=0,row=total+3)
        # Button for discarding the current settings.
        ttk.Button(window,
                name='discard',
                text='Discard changes',
                command=lambda: warning(window.destroy,
                                        'All your current changes will be lost. '
                                        + 'Are you sure you want to do this?')
                ).grid(column=0,row=total+4)
    # If no changes, program can just end here.
    else:
        window.destroy()

def createTimeDifs():

    '''Copy and pasted function from raDriver for creating time differences.
    
    See the original for more info.'''

    global time_difs, time_difs_file, time_difs_method, parameters
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

def createPlot():

    '''Copy and pasted function from raDriver for creating the histogram.
    
    See the original for more info.'''

    global time_difs, histogram, hist_file, hist_method, parameters
    histogram = plt.RossiHistogram(parameters.settings['RossiAlpha Settings']['Reset time'],
                              parameters.settings['RossiAlpha Settings']['Bin width'],
                              parameters.settings['Histogram Visual Settings'],
                              parameters.settings['Input/Output Settings']['Save directory'])
    histogram.plot(time_difs,
              save_fig=parameters.settings['General Settings']['Save figures'],
              show_plot=parameters.settings['General Settings']['Show plots'])
    hist_file = parameters.settings['Input/Output Settings']['Input file/folder']
    hist_method = parameters.settings['RossiAlpha Settings']['Time difference method']

def calculateTimeDifsAndPlot():

    '''Copy and pasted function from raDriver for creating the 
    time differences and histogram plot in parallel.
    
    See the original for more info.'''

    global histogram, time_difs, hist_file, hist_method, parameters
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

def plotSplit():

    '''The split for plotting the histogram to determine 
    whether it is generated in series or parallel with 
    creating the time differences.'''

    global parameters
    # If no time difs have been made or the input file/
    # method of time difference calculation has changed.
    if time_difs is None or (not 
                             (time_difs_method == parameters.settings['RossiAlpha Settings']['Time difference method'] 
                          and time_difs_file == parameters.settings['Input/Output Settings']['Input file/folder'])):
        # Combine time difference calculation and plot generation if applicable.
        if (parameters.settings['RossiAlpha Settings']['Combine Calc and Binning']):
            calculateTimeDifsAndPlot()
        # Otherwise, do them separately.
        else:
            createTimeDifs()
            createPlot()
    # Otherwise, just create the plot.
    else:
        createPlot()

def createBestFit():

    '''Copy and pasted function from raDriver for creating a line of best fit.
    
    See the original for more info.'''

    global time_difs, histogram, best_fit, parameters
    counts = histogram.counts
    bin_centers = histogram.bin_centers

    best_fit = fit.RossiHistogramFit(counts, bin_centers, parameters.settings)
        
    best_fit.fit_and_residual(save_every_fig=parameters.settings['General Settings']['Save figures'], 
                              show_plot=parameters.settings['General Settings']['Show plots'])

def raAll(single: bool):

    '''Run all of the Rossi Alpha analyis.
    
    Reqires:
    - single: a boolean that marks whether the input is a single file or folder.'''

    global time_difs, histogram, best_fit
    # Run and save accordingly based on the input type.
    if single:
        time_difs, histogram, best_fit = mn.analyzeAllType1(parameters.settings)
    else:
        mn.analyzeAllType2(parameters.settings)

def raSplit(mode: str):

    '''The main driver for the Rossi Alpha analysis. 
    Checks for user error and saved data overwriting.
    
    Requires:
    - mode: a string of the analysis that is desired. It should 
    exactly match the name of the function to be called.'''

    global time_difs, histogram, best_fit

    # If no input defined, throw error.
    if parameters.settings['Input/Output Settings']['Input file/folder'] == 'none':
        error('You currently have no input file or folder defined.\n\n'
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
                error('To analyze a single file, you must use '
                    + 'the any_and_all time difference method only.\n')
            # Otherwise, split on the analysis type.
            else:
                match mode:
                    # Run all analysis; no checks needed.
                    case 'raAll':
                        raAll(True)
                    # Create time differences.
                    case 'createTimeDifs':
                        # If time differences already exist, warn user.
                        if time_difs is not None:
                            warning(createTimeDifs,
                                    'There are already stored time differences '
                                    + 'in this runtime. Do you want to overwrite them?')
                        # Otherwise, create with no warning.
                        else:
                            createTimeDifs()
                    # Create a histogram plot.
                    case 'plotSplit':
                        # If histogram already exists, warn user.
                        if histogram is not None:
                            warning(plotSplit,
                                    'There is an already stored histogram '
                                    + 'in this runtime. Do you want to overwrite it?')
                        # Otherwise, create with no warning.
                        else:
                            plotSplit()
                    # Create a best fit + residual.
                    case 'createBestFit':
                        # If best fit already exists, warn user.
                        if best_fit is not None:
                            warning(createBestFit,
                                    'There is an already stored best fit line '
                                    + 'in this runtime. Do you want to overwrite it?')
                        # Otherwise, create with no warning.
                        else:
                            createBestFit()
        # Otherwise, assume folder data.
        else:
            # If modular analysis is attempted, throw and error.
            if mode != 'raAll':
                error('You can only run full folder analysis.\n\n'
                      + 'These modular options are for single files.')
            # Otherwise, run the full analysis.
            else:
                raAll(False)

def conduct_PSD():

    '''Copy and pasted function from psdDriver for 
    running Power Spectral Density analysis.
    
    See the original for more info.'''

    global parameters

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

def setMenu(prev):

    '''The GUI for the settings menu.
    
    Requires:
    - prev: the GUI function for the previous menu.'''

    global window
    # Clear the window of all previous entries, labels, and buttons.
    for item in window.winfo_children():
        item.destroy()
    # Properly name the window.
    window.title('Settings Editor & Viewer')
    # Lable to prompt the user.
    ttk.Label(window,
              name='prompt',
              text='What settings do you want to edit/view?',
              ).grid(column=0,row=0)
    # Button to edit/view current settings.
    ttk.Button(window,
              name='current',
              text='Current Settings',
              command=lambda: editor_menu(prev)
              ).grid(column=0,row=1)
    # Button to import settings files.
    ttk.Button(window,
              name='import',
              text='Import settings file',
              command=lambda: download_menu(lambda: setMenu(prev), lambda: setMenu(prev))
              ).grid(column=0,row=2)
    # Button to return to the previous menu.
    ttk.Button(window,
              name='return',
              text='Return to previous menu',
              command=prev
              ).grid(column=0,row=3)

def edit(inputs, prev):

    '''Save the inputs from the editor menu to the settings.
    
    Requires:
    - inputs: a dictionary of tkinter string variables. 
    Should have groups that match the current settings.
    - prev: the GUI function for the menu 
    to return to after the settings menu.'''

    global parameters
    # For each group and setting in the inputs, convert the 
    # string to the correct time and save it accordingly.
    for group in inputs:
        for setting in inputs[group]:
            parameters.settings[group][setting] = saveType(inputs[group][setting].get())
    # Return to the settings menu.
    setMenu(prev)

def editor_menu(prev):

    '''The GUI for the editor menu.
    
    Requires:
    - prev: the GUI function for the menu 
    to return to after the settings menu.'''

    global window, parameters
    groupNum=0
    curTop=0
    curMax = 0
    # Initialize inputs dictionary (assume settings groups are constant).
    inputs={'Input/Output Settings': {},
            'General Settings': {},
            'RossiAlpha Settings': {},
            'PSD Settings': {},
            'Histogram Visual Settings': {},
            'Line Fitting Settings': {},
            'Residual Plot Settings': {},}
    # Clear the window of all previous entries, labels, and buttons.
    for item in window.winfo_children():
        item.destroy()
    # Properly name the window.
    window.title('View/Edit Current Settings')
    # For each group in the settings.
    for group in parameters.settings:
        # If the start of a new row, add the previous current maximum 
        # to the current top and reset the current maximum variable. 
        if (groupNum*3) % 9 == 0:
            curTop += curMax
            curMax = 0
        # The label for the settings group.
        ttk.Label(window,
                  name=group[0:group.find(' Settings')].lower(),
                  text=group[0:group.find(' Settings')] + ':'
                  ).grid(column=(groupNum*3) % 9,row=curTop)
        # Reset the settings number (1-indexed)
        setNum=1
        # For each setting in the group.
        for setting in parameters.settings[group]:
            # Create a string variable linked to 
            # this setting in the inputs dictionary.
            inputs[group][setting]=tk.StringVar()
            # The label for the setting name.
            ttk.Label(window,
                  name=(group + ' ' + setting).lower(),
                  text=setting + ':'
                  ).grid(column=(groupNum*3+1) % 9,row=curTop+setNum)
            # The entry box for inputting/viewing the setting value.
            tk.Entry(window,
                  name=(group + ' ' + setting + ' value').lower(),
                  textvariable=inputs[group][setting]
                  ).grid(column=(groupNum*3+2) % 9,row=curTop+setNum)
            # Insert into the entry box the current value of the setting.
            window.children[(group + ' ' + setting + ' value').lower()].insert(0,format(parameters.settings[group][setting]))
            # Increase the setting number.
            setNum += 1
        # If the total settings in this group were the max 
        # in this row, set the current max to this value.
        if setNum > curMax:
            curMax = setNum
        # Increase the group number.
        groupNum += 1
    # Add the previous current maximum to 
    # the current top for button formatting.
    curTop += curMax
    # Button for saving changes.
    ttk.Button(window,
                name='save',
                text='Save changes',
                command=lambda: edit(inputs, prev)
                ).grid(column=0 % 9,row=curTop)
    # Button for canceling changes.
    ttk.Button(window,
                  name='cancel',
                  text='Cancel changes',
                  command=lambda: setMenu(prev)
                  ).grid(column=0 % 9,row=curTop+1)

def raMenu():

    '''The GUI for the Rossi Alpha menu.'''

    global window
    # Clear the window of all previous entries, labels, and buttons.
    for item in window.winfo_children():
        item.destroy()
    # Properly name the window.
    window.title('Rossi Alpha Analysis')
    # Prompt the user.
    ttk.Label(window,
              name='prompt',
              text='What would you like to do?'
              ).grid(column=0,row=0)
    # Button for running all analysis.
    ttk.Button(window,
              name='all',
              text='Run entire analysis',
              command=lambda: raSplit('raAll')
              ).grid(column=0,row=1)
    # Button for calculating time differences.
    ttk.Button(window,
              name='time_dif',
              text='Calculate time differences',
              command=lambda: raSplit('createTimeDifs')
              ).grid(column=0,row=2)
    # Button for creating a histogram.
    ttk.Button(window,
              name='histogram',
              text='Create histogram',
              command=lambda: raSplit('plotSplit')
              ).grid(column=0,row=3)
    # Button for creating a line fit + residual.
    ttk.Button(window,
              name='fit',
              text='Fit data',
              command=lambda: raSplit('createBestFit')
              ).grid(column=0,row=4)
    # Button to view the program settings.
    ttk.Button(window,
              name='settings',
              text='Program settings',
              command=lambda: setMenu(raMenu)
              ).grid(column=0,row=5)
    # Button to return to the main menu.
    ttk.Button(window,
              name='return',
              text='Return to main menu',
              command=main
              ).grid(column=0,row=6)

def psdMenu():

    '''The GUI for the Power Spectral Density menu.'''

    global window
    # Clear the window of all previous entries, labels, and buttons.
    for item in window.winfo_children():
        item.destroy()
    # Properly name the window.
    window.title('Power Spectral Density Analysis')
    # Prompt the user.
    ttk.Label(window,
              name='prompt',
              text='What would you like to do?'
              ).grid(column=0,row=0)
    # Button to run analysis.
    ttk.Button(window,
              name='run',
              text='Run analysis',
              command=conduct_PSD
              ).grid(column=0,row=1)
    # Button to view the program settings.
    ttk.Button(window,
              name='settings',
              text='Program settings',
              command=lambda: setMenu(psdMenu)
              ).grid(column=0,row=2)
    # Button to return to the main menu.
    ttk.Button(window,
              name='return',
              text='Return to main menu',
              command=main
              ).grid(column=0,row=3)

def default():

    '''Import the default settings 
    at the beginning of runtime.'''

    global parameters
    # Create the absolute path for the 
    # default settings and read them in.
    path = os.path.abspath('default.json')
    parameters.read(path)
    # Run the main menu.
    main()

def download(append: bool, prev):

    '''Download the file given in the global response variable.
    
    Requires:
    - append: a boolean that represents whether this download is 
    meant for appending or overwriting the entire settings.
    - prev: the menu to return to after downloading.'''

    global window, response, parameters
    # Get the response, add the .json extension, 
    # and convert it to an absolute path.
    file = os.path.abspath(response.get() + '.json')
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
        error(file + ' is not a correct path or references an invalid settings '
              + 'file.\n\nMake sure that your settings file is named correctly, '
              + 'the correct absolute/relative path to it is given, and '
              + 'you did not include the .json extenstion in your input.')

def download_menu(prev, to):

    '''The GUI for the settings download menu.'''

    global window
    # Clear the window of all previous entries, labels, and buttons.
    for item in window.winfo_children():
        item.destroy()
    # Properly name the window.
    window.title('Download Settings')
    # Notify the user of the different import options.
    ttk.Label(window,
              name='choice',
              text='You have two import options:'
              ).grid(column=0,row=0)
    # Button for overwriting the entire settings.
    ttk.Button(window,
               name='overwrite',
               text='Overwrite entire settings',
               command=lambda: prompt(lambda: download_menu(prev, to),
                                      lambda: download(False, to),
                                      'Enter a settings file (no .json extension):',
                                      'Overwrite Settings')
               ).grid(column=0,row=1)
    # Button for appending settings to the current settings.
    ttk.Button(window,
               name='append',
               text='Append settings',
               command=lambda: prompt(lambda: download_menu(prev, to),
                                      lambda: download(True, to),
                                      'Enter a settings file (no .json extension):',
                                      'Append Settings to Default')
               ).grid(column=0,row=2)
    # Button for canceling settings import.
    ttk.Button(window,
               name='cancel',
               text='Cancel',
               command=prev
               ).grid(column=0,row=3)

def main():

    '''The GUI for the main menu.'''

    global window
    # Clear the window of all previous entries, labels, and buttons.
    for item in window.winfo_children():
        item.destroy()
    # Properly name the window.
    window.title('Main Menu')
    # Prompt the user.
    ttk.Label(window,
              name='choice',
              text='You can utilize any of the following functions:'
              ).grid(column=0,row=0)
    # Button to run Rossi Alpha analysis. 
    ttk.Button(window,
               name='rossi_alpha',
               text='Run Rossi Alpha analysis',
               command=raMenu
               ).grid(column=0,row=1)
    # Button to run Power Spectral Density analysis. 
    ttk.Button(window,
               name='power_spectral_density',
               text='Run Power Spectral Density analysis',
               command=psdMenu
               ).grid(column=0,row=2)
    # Button to edit the program settings.
    ttk.Button(window,
               name='settings',
               text='Edit the program settings',
               command=lambda: setMenu(main)
               ).grid(column=0,row=3)
    # Button to exit the program.
    ttk.Button(window,
               name='quit',
               text='Quit the program',
               command=lambda: warning(shutdown_menu,
                                       'Are you sure you want to quit the program?',
                                       'Shutdown Confirmation')
               ).grid(column=0,row=4)

def startup():

    '''The GUI for the startup menu.'''

    global window, parameters
    # If window is not yet defined, create it and grid it.
    if window == None:
        window = Tk()
        window.grid()
    # Otherwise, clear the window of all 
    # previous entries, labels, and buttons.
    else:
        for item in window.winfo_children():
            item.destroy()
    # Properly name the window.
    window.title('Welcome!')
    # If settings are not yet defined, construct an empty settings object.
    if parameters == None:
        parameters = set.Settings()
    # Welcome information for the user.
    ttk.Label(window,
            name='welcome',
            text='Welcome to the DNNG/PyNoise project.\n\nWith '
            + 'this software we are taking radiation data from '
            + 'fission reactions \n(recorded by organic scintillators) '
            + 'and analyzing it using various methods and tools.\n\n'
            + 'Use this Python suite to analyze a single file or '
            + 'multiple across numerous folders.\n'
            ).grid(column=0, row=0)
    # Prompt the user.
    ttk.Label(window,
            name='choice',
            text='Would you like to use the default '
            + 'settings or import another .json file?'
            ).grid(column=0, row=1)
    # Button for importing the default settings.
    ttk.Button(window,
               name='default',
               text="Default",
               command=default
               ).grid(column=0, row=2)
    # Button for importing other settings.
    ttk.Button(window,
               name='import',
               text="Import Settings",
               command=lambda:download_menu(startup, main)
               ).grid(column=0, row=3)
    # Run the window.
    window.mainloop()