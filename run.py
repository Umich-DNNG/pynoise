'''The file that runs code related to the GUI implementation.'''



# Necessary imports.
import os
import io
import time
from tkinter import *
from tkinter import ttk
import gui
import settings as set
import analyze as alz



# Global variables for the analysis object 
# and file that will have logs written to it.
analyzer = alz.Analyzer()
logfile: io.TextIOWrapper = None



def create_logfile():

    '''Create a log file for logging user interactions.'''


    # Use the global logfile variable.
    global logfile
    # Ensure a log file does not already exist.
    if logfile is None:
        # Get local time.
        curTime = time.localtime()
        # Create log file name with relative path and timestamp.
        logName = ('logs/' + str(curTime.tm_year) 
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



def log(message, xor=None, window: Tk=None, menu=None):

    '''Log a message to the current window and the logfile.
    
    Inputs:
    - message: the string or string-returning function that will be displayed.  
    - xor: a boolean that determines where this message should be displayed:
        - True: show only in the given label.
        - False: show only in the logfile.
        - not provided: show in both.
    - label: the label within which the notification will be put. 
    This is required when xor is True or not provided.
    - menu: if returning to a previous menu, this is that menu 
    function. If not defined, will assume staying on the same menu.'''


    # Use the global logfile variable.
    global logfile
    # If there is a menu to be run, call it.
    if menu != None:
        error = menu()
    # Otherwise, mark no error by default.
    else:
        error = False
    # If there is no error:
    if not error:
        # If message is a function, call it and save the output.
        if not isinstance(message, str):
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
            # If there is not already a log element on the screen, create one.
            if window.children.get('log') == None:
                ttk.Separator(window,
                              orient='horizontal',
                              ).pack(side=TOP,fill=X,padx=10)
                ttk.Label(window,
                        name='log',
                        text=message,
                        ).pack(side=TOP,padx=10,pady=10)
            # Otherwise, just replace the text in the log element.
            else:
                window.children['log'].config(text=message)



def warningFunction(popup: Tk,
                    to):

    '''The function that is called when the user chooses to ignore a warning.
    
    Inputs:
    - popup: the warning window that will be deleted.
    - to: the main function that will be called.'''


    # Destroy the warning window and run the desired function.
    popup.destroy()
    to()



def saveType(value: str):

    '''Converts the output of a tkinter string variable to its 
    proper value for storage. This supports None, ints, floats, 
    booleans, strings, and non-nested lists of these variable types.
    
    Inputs:
    - value: the string to be converted.
    
    Outputs:
    - the value stored as its correct type.'''


    # If variable is None, store it as such.
    if value == 'None':
        return None
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



def edit(window: Tk,
         inputs: dict,
         newSet: dict,
         newVal: dict,
         parameters: set.Settings,
         prev):

    '''Save the inputs from the editor menu to the settings.
    
    Inputs:
    - window: the window that will display the number of changes.
    - inputs: a dictionary of tkinter string variables. 
    Should have groups that match the current settings.
    - newSet: the new settings that have been added.
    - newVal: the values of the new settings.
    - parameters: the settings object holding the current settings.
    - prev: the GUI function for the menu 
    to return to after the settings menu.'''


    # For every new proposed setting:
    for group in newSet:
        for key in newSet[group]:
            # If the setting isn't the placeholder 'Cancel' 
            # or 'Select setting...', and the value isn't 
            # blank, add the setting and value to the inputs.
            if newSet[group][key].get() != 'Cancel' and newSet[group][key].get() != 'select setting...' and newVal[group][key].get() != '':
                inputs[group][newSet[group][key].get()] = newVal[group][key]
    # Write the current parameters to a temp file for comparison.
    parameters.write(os.path.abspath('settings/comp.json'))
    # For each setting change:
    for group in inputs:
        for setting in inputs[group]:
            # If the setting is being deleted:
            if inputs[group][setting].get() == '':
                # Confirm the setting currently exists.
                if parameters.settings[group].get(setting) != None:
                    # Pop the setting from the group.
                    parameters.settings[group].pop(setting)
                    # Add the setting back to the appropriate dropdown menu.
                    match group:
                        case 'Histogram Visual Settings':
                            parameters.hvs_drop.append(setting)
                        case 'Line Fitting Settings':
                            parameters.lfs_drop.append(setting)
                        case 'Scatter Plot Settings':
                            parameters.sps_drop.append(setting)
                        case 'Semilog Plot Settings':
                            parameters.sls_drop.append(setting)
            # Otherwise:
            else:
                # If this is a new setting, remove it 
                # from the appropriate dropdown menu.
                if parameters.settings[group].get(setting) == None:
                    match group:
                        case 'Histogram Visual Settings':
                            parameters.hvs_drop.remove(setting)
                        case 'Line Fitting Settings':
                            parameters.lfs_drop.remove(setting)
                        case 'Scatter Plot Settings':
                            parameters.sps_drop.remove(setting)
                        case 'Semilog Plot Settings':
                            parameters.sls_drop.remove(setting)
                # Store the correct value.
                parameters.settings[group][setting] = saveType(inputs[group][setting].get())
    # Sort the dropdown menus.
    parameters.sort_drops()
    # Compare the modified settings to the 
    # previous and save the change messages.
    changes = parameters.compare(True)
    # Log each change message to the logfile.
    for message in changes:
        log(message=message, xor=False)
    # If there were changes made, notify the user.
    if len(changes) > 0:
        log('Succesfully made ' + str(len(changes)) + ' changes to the '
            + 'settings\n(see logfile for more information).',
            True,
            window,
            lambda: gui.setMenu(prev))
    # Otherwise, just return to the settings menu.
    else:
        gui.setMenu(prev)



def download(parameters: set.Settings, file: str, append: bool, prev):

    '''Download settings from the file given.
    
    Inputs:
    - parameters: the settings object holding the current settings.
    - file: the absolute path of the file being downloaded from.
    - append: a boolean that represents whether this download is 
    meant for appending or overwriting the entire settings.
    - prev: the menu to return to after downloading.'''
    

    # If file exists:
    if os.path.isfile(file):
        # If in append mode:
        if append:
            # If settings have not been initialized, read in the defualt.
            if parameters.origin == None:
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



def export(window: Tk, parameters: set.Settings, file: str, warn: bool):

    '''Save settings to the specified file at the end of runtime.
    
    Requires:
    - window: the main window that will be closed down.
    - parameters: the settings object holding the current settings.
    - file: the absolute path of the file being saved to.
    - warn: a boolean that determines whether or not 
    the program should warn the user of the overwrite.'''



    # If the file already exists, warns the user of the overwrite.
    if warn and os.path.isfile(file):
        gui.warning(lambda: export(window, parameters, file, False))
        # Return so the shutdown doesn't happen twice.
        return
     # Otherwise, save to the new file.
    else:
        # If saving as default, do a complete 
        # overwrite and write an appropriate message.
        if file == os.path.abspath('./settings/default.json'):
            parameters.write(file)
            message = 'Default settings successfully overwritten.'
        # Otherwise, save based on the default 
        # and write an appropriate message.
        else:
            parameters.save(file)
            message = 'Settings successfully saved to file:\n' + file + '.'
    # Shut down the program.
    shutdown(window, parameters, message)



def shutdown(window: Tk, parameters: set.Settings, message: str = None):

    '''Close the program & logfile and delete the logfile is applicable.
    
    Inputs:
    - window: the main window that will be closed down.
    - parameters: the settings object holding the current settings.
    - message: the message to display in the final window, if any.'''

    # Use the global logfile variable.
    global logfile
    # Close the main window.
    window.destroy()
    # Run the goodbye menu.
    gui.byeMenu(message)
    # Close the logfile.
    logfile.close()
    # If user doesn't want logs, delete the logfile.
    if not parameters.settings['Input/Output Settings']['Keep logs']:
        os.remove(logfile.name)
    # Otherwise:
    else:
        # Open the logfile in read mode, read 
        # all of the lines, and close it again.
        logfile = open(logfile.name,'r')
        lines = logfile.readlines()
        logfile.close()
        # Open the logfile and write everything 
        # except the disclaimer to the file.
        logfile = open(logfile.name,'w')
        logfile.write(lines[0])
        for line in lines[2:]:
            logfile.write(line)
        logfile.close()



def raSplit(window: Tk, mode: str, parameters: set.Settings):

    '''The main driver for the Rossi Alpha analysis. 
    Checks for user error and saved data overwriting.
    
    Inputs:
    - window: the main window of the gui.
    - mode: a string of the analysis that is desired. It should 
    exactly match the name of the function to be called.
    - parameters: the settings object holding the current settings.'''


    # Ensure there is a valid input file/ folder, and if not throw an error.
    if (not os.path.isfile(parameters.settings['Input/Output Settings']['Input file/folder'])
    and not os.path.isdir(parameters.settings['Input/Output Settings']['Input file/folder'])):
        gui.error('ERROR: You currently have no input file or '
                  + 'folder defined or the specified input file/'
                  + 'directory does not exist.\n\nPlease make sure '
                  + 'to adjust this before running any analysis.\n')
        return True
     # Get name of actual file/folder for later use.
    name = parameters.settings['Input/Output Settings']['Input file/folder']
    name = name[name.rfind('/')+1:]
    # If time difference method is not any and all 
    # and channel column is None, throw an error.
    if (parameters.settings['RossiAlpha Settings']['Time difference method'] != 'aa' 
    and parameters.settings['RossiAlpha Settings']['Time difference method'] != ['aa']
    and parameters.settings['Input/Output Settings']['Channels column'] == None
    and name.count('.') > 0):
        gui.error('To analyze a file/folder with more than any and all, '
                  + 'you must define a channels column.\n')
        return True
    # If name has a . in it, assume a single file.
    if name.count('.') > 0:
        # Split on the analysis type.
        match mode:
            # Run all analysis:
            case 'raAll':
                # Run full file and log the completion.
                analyzer.fullFile(parameters.settings)
                log(message='Successfully ran all analysis on file:\n'
                    +parameters.settings['Input/Output Settings']['Input file/folder'],
                    window=window)
            # Create time differences:
            case 'createTimeDifs':
                # If time differences already exist, warn user.
                if analyzer.RATimeDifs['Time differences'] is not None:
                    # Create a dictionary of the current relevant settings.
                    check = {'Input file/folder': parameters.settings['Input/Output Settings']['Input file/folder'],
                            'Sort data': parameters.settings['General Settings']['Sort data'],
                            'Time difference method': parameters.settings['RossiAlpha Settings']['Time difference method'],
                            'Digital delay': parameters.settings['RossiAlpha Settings']['Digital delay'],
                            'Reset time': parameters.settings['RossiAlpha Settings']['Reset time']}
                    # If in folder mode, add the number of folders setting.
                    if name.count('.') == 0:
                        check['Number of folders'] = parameters.settings['General Settings']['Number of folders']
                    # If time differences are still valid:
                    if analyzer.isValid('RATimeDifs', check):
                        # Notify user that calculation is being canceled.
                        gui.error('Time differences have already been '
                                 + 'generated with these settings.\nTime '
                                 + 'difference calculation has been aborted.\n',
                                 'Recalculation Paused')
                    # If time differences are not valid 
                    # anymore, warn user of overwrite.
                    else:
                        gui.warning(lambda: log(message='Successfully recalculated time differences for file:\n'
                                            +parameters.settings['Input/Output Settings']['Input file/folder'],
                                            window=window,
                                            menu=lambda:analyzer.createTimeDifs(parameters.settings['Input/Output Settings'],
                                                                                parameters.settings['General Settings']['Sort data'],
                                                                                parameters.settings['RossiAlpha Settings']['Reset time'],
                                                                                parameters.settings['RossiAlpha Settings']['Time difference method'],
                                                                                parameters.settings['RossiAlpha Settings']['Digital delay'],
                                                                                parameters.settings['Input/Output Settings']['Quiet mode'],
                                                                                False)),
                                'There are already stored time differences '
                                + 'in this runtime. Do you want to overwrite them?')
                # Otherwise, create with no warning.
                else:
                    analyzer.createTimeDifs(parameters.settings['Input/Output Settings'],
                                            parameters.settings['General Settings']['Sort data'],
                                            parameters.settings['RossiAlpha Settings']['Reset time'],
                                            parameters.settings['RossiAlpha Settings']['Time difference method'],
                                            parameters.settings['RossiAlpha Settings']['Digital delay'],
                                            parameters.settings['Input/Output Settings']['Quiet mode'],
                                            False)
                    log(message='Successfully calculated time differences for file:\n'
                        +parameters.settings['Input/Output Settings']['Input file/folder'],
                        window=window)
            # Create a histogram plot.
            case 'plotSplit':
                # If histogram already exists, warn user.
                if analyzer.RAHist['Histogram'] is not None:
                    gui.warning(lambda: log(message='Successfully recreated a histogram for file:\n'
                                        +parameters.settings['Input/Output Settings']['Input file/folder'],
                                        window=window,
                                        menu=lambda:analyzer.plotSplit(parameters.settings)),
                                'There is an already stored histogram '
                                + 'in this runtime. Do you want to overwrite it?')
                # Otherwise, create with no warning.
                else:
                    analyzer.plotSplit(parameters.settings)
                    log(message='Successfully created a histogram for file:\n'
                        +parameters.settings['Input/Output Settings']['Input file/folder'],
                        window=window)
            # Create a best fit + residual.
            case 'createBestFit':
                # If best fit already exists, warn user.
                if analyzer.RABestFit['Best fit'] is not None:
                    gui.warning(lambda: log(message='Successfully recreated a best fit for file:\n'
                                        +parameters.settings['Input/Output Settings']['Input file/folder'],
                                        window=window,
                                        menu=lambda:analyzer.fitSplit(parameters.settings,
                                                                      name.count('.') == 0)),
                            'There is an already stored best fit line '
                            + 'in this runtime. Do you want to overwrite it?')
                # Otherwise, create with no warning.
                else:
                    analyzer.fitSplit(parameters.settings, name.count('.') == 0)
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
        # Otherwise:
        else:
            # Show the progress menu for folders.
            gui.folderProgress()
            # Run full folder analysis.
            analyzer.fullFolder(parameters.settings, window)
            # Return to the Rossi Alpha menu and log the success.
            gui.raMenu()
            log(message='Successfully ran all analysis with folder:\n'
                        +parameters.settings['Input/Output Settings']['Input file/folder'],
                        window=window)



def caSplit(window: Tk, parameters: set.Settings):

    '''The main driver for Cohn Alpha analysis.
    
    Inputs:
    - window: the main window of the gui.
    - parameters: the settings object holding the current settings.'''

    name = parameters.settings['Input/Output Settings']['Input file/folder']
    name = name[name.rfind('/')+1:]

    # if name has a . in it, assume a single file.
    if name.count('.') > 0:
        # Conduct Cohn Alpha analysis and log the success.
        analyzer.conductCohnAlpha(parameters.settings['Input/Output Settings']['Input file/folder'],
                                parameters.settings['Input/Output Settings']['Save directory'],
                                parameters.settings['General Settings']['Show plots'],
                                parameters.settings['Input/Output Settings']['Save figures'],
                                parameters.settings['CohnAlpha Settings'],
                                parameters.settings['Semilog Plot Settings'],
                                parameters.settings['Line Fitting Settings'])
        log(message='Successfully ran Cohn Alpha analysis on file:\n'
            +parameters.settings['Input/Output Settings']['Input file/folder'],
            window=window)
    # Otherwise, assume folder data.
    else:
        analyzer.CohnAlphaFullFolder(parameters.settings, window)
        log(message='Successfully ran Cohn Alpha analysis with folder:\n'
            +parameters.settings['Input/Output Settings']['Input file/folder'],
            window=window)




def fySplit(window: Tk, parameters: set.Settings):

    '''The main driver for FeynmanY analysis.
    
    Inputs:
    - window: the main window of the gui.
    - parameters: the settings object holding the current settings.'''


    # Conduct FeynmanY analysis and log the success.
    analyzer.runFeynmanY(parameters.settings['Input/Output Settings'],
                         parameters.settings['FeynmanY Settings'],
                         parameters.settings['General Settings']['Show plots'],
                         parameters.settings['Input/Output Settings']['Save figures'],
                         parameters.settings['Input/Output Settings']['Quiet mode'],
                         parameters.settings['General Settings']['Verbose iterations'],
                         parameters.settings['Histogram Visual Settings'],
                         parameters.settings['Line Fitting Settings'],
                         parameters.settings['Scatter Plot Settings'],
                         window)
    gui.feynmanYMenu()
    log(message='Successfully ran Feynman Y analysis on file:\n'
        +parameters.settings['Input/Output Settings']['Input file/folder'],
        window=window)