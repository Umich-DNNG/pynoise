'''The main file that should be run each time the user wants to use this Python Suite.'''

import settings as set
import main as mn
import fitting as fit
import plots as plt
import timeDifs as dif
import analyzingFolders as fol
import os
import time

'''Function Table of Contents:
isFloat: 40
fileType: 50
plotLink: 61
log: 73
changeLog: 101
inputBool: 138
inputNum: 173
changePath: 210
ioSet: 265
genSet: 339
histSet: 484
plotSet: 516
settingsEditor: 607
printSelector: 660
settingsDriver: 719
importSettings: 747
main: 785'''

# The settings object to be referenced.
parameters = set.Settings()

# The empty log file.
history = None

# Set the current working directory for assigning absolute paths.
os.chdir(os.path.dirname(os.path.realpath(__file__)))

def isFloat(input):

    '''Checks whether or not the input string can be converted to a float.'''

    try:
        float(input)
        return True
    except ValueError:
        return False

def fileType(input):

    '''Converts input type digit to text for user interactions (print statements).
    
    Assumes input is only either 1 or 2.'''

    if input == 1:
        return 'Single file'
    else:
        return 'Folder'

def plotLink(plot):

    '''Returns the right link based on the plot type.
    
    Requires the settings group for the plot (Histogram 
    Visual, Line Fitting, or Residual Plot)'''

    if plot == 'Histogram Visual Settings':
        return 'https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.bar.html'
    else:
        return 'https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html'

def log(output):

    '''Prints the output statement to the command line 
    and saves it to the log if logs are enabled.
    
    The output statement must be a string.'''

    # Ensure any reference to history is to the global variable.
    global history
    # Print the confirmation statement to the 
    # console regardless of log preferences.
    print(output)
    # If log file exists, record this confirmation.
    if history is not None:
        # Create a timestamp for the confirmation message.
        curTime = time.localtime()
        output = (str(curTime.tm_year) 
          + '-' + str(curTime.tm_mon) 
          + '-' + str(curTime.tm_mday) 
          + ' @ ' + str(curTime.tm_hour) 
          + (':0' if curTime.tm_min < 10 else ':') + str(curTime.tm_min) 
          + (':0' if curTime.tm_sec < 10 else ':') + str(curTime.tm_sec) 
          + ' - ' + output)
        # Write the confirmation + timestamp to the file and flush 
        # immediately so user can see log updates in real time.
        history.write(output)
        history.flush()

def changeLog():

    '''Change the current use of the log file.
    
    If setting changed:
    * True -> False - close log file and delete it.
    * False -> True - create/open new log file named with current timestamp.
    * True -> True - does nothing (prevents recreation of log file).
    * False -> False - does nothing (prevents closing/deletion of nonexistent file).'''

    # Ensure any reference to history is to the global variable.
    global history
    # If user wants to keep logs and one is not already open.
    if parameters.get('Input/Output Settings','Keep logs') and history is None:
        # Get local time.
        curTime = time.localtime()
        # Create log file name with relative path and timestamp.
        logName = ('../.logs/' + str(curTime.tm_year) 
                    + '-' + str(curTime.tm_mon) 
                    + '-' + str(curTime.tm_mday) 
                    + '@' + str(curTime.tm_hour) 
                    + (':0' if curTime.tm_min < 10 else ':') + str(curTime.tm_min) 
                    + (':0' if curTime.tm_sec < 10 else ':') + str(curTime.tm_sec) 
                    + '.log')
        # Convert relative path into absolute path.
        logName = os.path.abspath(logName)
        # Create and open a log file with writing priveleges.
        history = open(logName,'w')
    # If user does not want logs and one is currently open.
    elif not parameters.get('Input/Output Settings','Keep logs') and history is not None:
        # Close file.
        history.close()
        # Delete file.
        os.remove(history.name)
        # Reset history variable.
        history = None

def inputBool(group, setting):

    '''Update a setting to be a boolean (stored as True/False).
    
    Send the function the setting group and the specific setting to be edited.
    
    Assumes the inputs are correct (no input error detection).'''

    selection = 'blank'
    print()
    # Keep looping until the user selects yes or no, or cancels.
    while selection != '' and selection != 't' and selection != 'f':
        selection = input('Enter t/f (or leave blank to cancel): ')
        match selection:
            # Update settings to True.
            case 't':
                parameters.set(group,setting,True)
                parameters.update()
                if setting == 'Keep logs':
                    changeLog()
                log(setting + ' updated to True.\n')
            # Update settings to False.
            case 'f':
                parameters.set(group,setting,False)
                parameters.update()
                if setting == 'Keep logs':
                    changeLog()
                log(setting + ' updated to False.\n')
            # Cancel changes.
            case '':
                print('Canceling changes...\n')
            # Catchall for invalid inputs.
            case _:
                print('This is a true/false question (t/f).\n')

def inputNum(group, setting, type):

    '''Update a setting to be an integer or float.
    
    Send the function the setting group and the specific 
    setting to be edited, and one of the two type options:

    "n integer" - integer

    " float" - float

    The whitespace and n at the beginning of the types is for formatting/printing.
    
    Assumes the inputs are correct (no input error detection).'''

    selection = 'blank'
    print()
    # Keep looping until the user input is valid, or cancels.
    while not (type[0] == 'n' and selection.isnumeric()) and not (type[0] == ' ' and isFloat(selection)) and selection != '':
        selection = input('Enter a' + type + ' (or leave blank to cancel): ')
        # Update setting when input is valid int.
        if type[0] == 'n' and selection.isnumeric():
            parameters.set(group,setting,int(selection))
            parameters.update()
            log(setting + ' updated to ' + selection + '.\n')
        # Update setting when input is valid float.
        elif type[0] == ' ' and isFloat(selection):
            parameters.set(group,setting,float(selection))
            parameters.update()
            log(setting + ' updated to ' + selection + '.\n')
        # Cancel changes.
        elif selection == '':
            print('Canceling changes...\n')
        # Catchall for invalid inputs.
        else:
            print('Please enter a' + type + '.\n')

def changePath(setting):

    '''Change a settings parameter that requires an absolute 
    or relative path (input file/folder and save directory).
    
    Requires a setting parameter (either 'Input file/folder' or 'Save directory') 
    to indicate specific print statements and where to save the user input.'''

    file = 'blank'
    name = ''
    # Continue looping until user input is valid or cancels changes.
    while file != '' and file[0] != '/' and file[0] != '.':
        file = input('Enter an absolute or relative path (or leave blank to cancel): ')
        # Cancel changes.
        if file == '':
            print('Returning to previous menu...\n')
        # When user enters valid input.
        elif file[0] == '/' or file [0] == '.':
            # For input file/folders.
            if setting[0] == 'I':
                name = file[file.rfind('/')+1:]
                # If input name has a . in it, assume it's a file.
                if name.count('.') > 0:
                    parameters.set('Input/Output Settings','Input type',1)
                    # Issue warning if user input for file does not exist.
                    if not os.path.isfile(file):
                        print('WARNING: The inputted file does not currently '
                            + 'exist. Ensure it does before running further analysis.')
                # Otherwise, assume a folder.
                else:
                    parameters.set('Input/Output Settings','Input type',2)
                    # Issue warning if user input for folder does not exist.
                    if not os.path.isdir(file):
                        print('WARNING: The inputted folder does not currently '
                            + 'exist. Ensure it does before running further analysis.')
            else:
                # Issue warning if user input for save directory does not exist.
                    if not os.path.isdir(file):
                        print('WARNING: The inputted directory does not currently '
                            + 'exist. Ensure it does before running further analysis.')
            # Update input.
            file = os.path.abspath(file)
            parameters.set('Input/Output Settings',setting,file)
            parameters.update()
            log(setting + ' changed to ' + parameters.get('Input/Output Settings',setting) + '.\n')
            # Notify user of automatically assigned 
            # input type for input file/folders.
            if setting[0] == 'I':
                log(fileType(parameters.get('Input/Output Settings','Input type'))
                    + ' input type autogenerated. If this type is wrong, '
                    + 'you can manually change it in the settings.\n')
        # Catchall for invalid inputs.
        else:
            print('Your input must be a relative or absolute path (begins with / or ./).\n')

def ioSet():

    '''The settings editor for Input/Output Settings.'''

    choice = 'blank'
    # Continue editing until the user is done.
    while choice != '':
        print('What setting would you like to edit?')
        print('t - input type')
        print('i - input file/folder')
        print('s - save directory')
        print('k - keep logs')
        print('v - view current Input/Output Settings')
        print('Leave the command blank if you wish to return to the previous menu.')
        choice = input('Enter setting: ')
        match choice:
            # User wants to change the input file/folder.
            case 'i':
                print()
                changePath('Input file/folder')
            # Change the save directory.
            case 's':
                print()
                changePath('Save directory')
            # Manual override for input type in case automatic assignment is wrong.
            # If this function is used, there is a bug in input type assignment.
            # Talk with the coders and explain the bug so it can be fixed.
            case 't':
                print()
                value = 'blank'
                # Explain valid inputs and use case to user.
                print('The input type can be 1 (single file) or 2 (folder). '
                      + 'Please note that this value is automatically assigned '
                      + 'when entering the input file/folder and should only '
                      + 'manually be changed if the autogenerated value is wrong.')
                # Keep looping until the user input is valid, or cancels.
                while value != '1' and value != '2' and value != '':
                    value = input('Select an input type (or leave blank to cancel): ')
                    # Update input type accordingly.
                    if value == '1' or value == '2':
                        parameters.set('Input/Output Settings','Input type',int(value))
                        log(str(fileType(parameters.get('Input/Output Settings','Input type'))) + ' (' + value + ') set as the input type.\n')
                        parameters.update()
                    # Cancel changes.
                    elif value == '':
                        print('Canceling changes...\n')
                    # Catchall for invalid commands.
                    else:
                        print('You must enter 1 or 2 for the file type.')
            # Change the keep logs option.
            case 'k':
                prev = parameters.get('Input/Output Settings','Keep logs')
                if prev:
                    print('WARNING: You currently have keep logs set to True. '
                          + 'If you change this to false, your current history '
                          + 'for this session will be deleted and cannot be restored.')
                inputBool('Input/Output Settings','Keep logs')
                if prev != parameters.get('Input/Output Settings','Keep logs'):
                    if parameters.get('Input/Output Settings','Keep logs'):
                        log('Created a log file for the current session and started recording changes.\n')
                    else:
                        print('Deleted current log file.\n')
            # Print current Input/Output Settings.
            case 'v':
                print()
                parameters.print_section('Input/Output Settings')
                print()
            # End editing.
            case '':
                print('Returning to previous menu...\n')
            # Catchall for invalid commands.
            case _:
                print('Unrecognized command. Please review the list of appriopriate inputs.\n')

def genSet():

    '''The settings editor for General Settings.'''

    choice = 'blank'
    # Continue editing until the user is done.
    while choice != '':
        print('What setting would you like to edit?')
        print('r - fit range')
        print('p - plot scale')
        print('t - time difference method')
        print('d - digital delay')
        print('n - number of folders')
        print('m - meas time per folder')
        print('o - sort data?')
        print('f - save fig?')
        print('w - show plot?')
        print('v - view current General Settings')
        print('Leave the command blank if you wish to return to the previous menu.')
        choice = input('Enter setting: ')
        match choice:
            # Update the fit range.
            case 'r':
                begin = 0
                end = 0
                selection = 'blank'
                # Keep looping until the user input is valid, or cancels.
                while not isFloat(selection) and selection != '':
                    print('Enter a float value to start the fitting range at.')
                    selection = input ('Value (or blank to cancel the edit): ')
                    # Save new beginning to fit range.
                    if isFloat(selection):
                        begin = float(selection)
                    # Catchall for invalid inputs.
                    elif selection != '':
                        print('You must enter a float value.\n')
                # If user hasn't canceled changes, continue to next section.
                if selection != '':
                    selection = 'blank'
                    # Keep looping until the user input is valid, or cancels.
                    while not isFloat(selection) and selection != '':
                        print('Enter a float value to end the fitting range at.')
                        selection = input ('Value (or blank to cancel the edit): ')
                        # Save new ending to fit range.
                        if isFloat(selection):
                            end = float(selection)
                        # Catchall for invalid inputs.
                        elif selection != '':
                            print('You must enter a float value.\n')
                    # Apply changes if user hasn't canceled.
                    if selection != '':
                        parameters.set('General Settings','Fit range',[begin,end])
                        log('Fit range updated to ' + str(parameters.get('General Settings','Fit range')) + '.\n')
                    # Cancel changes.
                    else:
                        print('Canceling changes...\n')
                # Cancel changes.
                else:
                    print('Canceling changes...\n')
            # Update the plot scale.
            case 'p':
                selection = input('Enter a new plot scale (or leave blank to cancel): ')
                # Apply changes if user hasn't canceled.
                if selection != '':
                    parameters.set('General Settings','Plot scale',selection)
                    parameters.update()
                    log('Updated the plot scale to ' + selection + '.\n')
                # Cancel changes.
                else:
                    print('Canceling changes...\n')
            # Update the time difference method.
            case 't':
                print()
                selection = 'blank'
                # Keep looping until the user input is valid, or cancels.
                while (selection != '' and selection != 'a' and selection != 'c'
                                       and selection != 'n' and selection != 'd'):
                    print('There are 4 time difference method options:')
                    print('a - any and all')
                    print('c - any and all + cross correlations')
                    print('n - all above options + no repeat')
                    print('d - all above options + digital delay')
                    selection = input('Choose an option, or leave blank to cancel the edit: ')
                    match selection:
                        # Apply and and all.
                        case 'a':
                            parameters.set('General Settings','Time difference method','any_and_all')
                            parameters.update()
                            log('Updated the time difference method to any and all.\n')
                         # Apply cross correlations.
                        case 'c':
                            parameters.set('General Settings','Time difference method','any_and_all cross_correlations')
                            parameters.update()
                            log('Updated the time difference method to any and all + cross correlations.\n')
                         # Apply no repeat.
                        case 'n':
                            parameters.set('General Settings','Time difference method','any_and_all cross_correlations no_repeat')
                            parameters.update()
                            log('Updated the time difference method to any and all + cross correlations + no repeat.\n')
                         # Apply digital delay.
                        case 'd':
                            parameters.set('General Settings','Time difference method','any_and_all cross_correlations no_repeat digital_delay')
                            parameters.update()
                            log('Updated the time difference method to any and all + cross correlations + no repeat + digital delay.\n')
                        # Cancel changes.
                        case '':
                            print('Canceling changes...\n')
                        # Catchall for invalid inputs.
                        case _:
                            print('Unrecognized command. Please review the list of appriopriate inputs.\n')
            # Update the digital delay.
            case 'd':
                inputNum('General Settings','Digital delay','n integer')
            # Update the number of folders.
            case 'n':
                # If settings indicate one file is to be analyzed, warn user of conflict.
                if parameters.get('Input/Output Settings','Input Type') == 1:
                    print('WARNING: You current settings indicate you are only analyzing 1 '
                          + 'file. This setting is intended for analyzing multiple folders. '
                          + 'If you plan to do so, please update your settings.')
                inputNum('General Settings','Number of folders','n integer')
            # Update the meas time per folder.
            case 'm':
                inputNum('General Settings','Meas time per folder','n integer')
            # Update the sort data choice.
            case 'o':
                inputBool('General Settings','Sort data?')
            # Update the save figures choice.
            case 'f':
                inputBool('General Settings','Save figures?')
            # Update the show plots choice.
            case 'w':
                inputBool('General Settings','Show plots?')
            # Print current General Settings.
            case 'v':
                print()
                parameters.print_section('General Settings')
                print()
            # End editing.
            case '':
                print('Returning to previous menu...\n')
            # Catchall for invalid commands.
            case _:
                print('Unrecognized command. Please review the list of appriopriate inputs.\n')

def histSet():
    choice = 'blank'
    while choice != '':
        print('What setting would you like to edit?')
        print('r - reset time')
        print('b - bin width')
        print('m - minimum cutoff')
        print('v - view current Histogram Generation Settings')
        print('Leave the command blank if you wish to return to the previous menu.')
        choice = input('Enter setting: ')
        match choice:
            # Update the reset time.
            case 'r':
                inputNum('Histogram Generation Settings','Reset time',' float')
            # Update the bin width.
            case 'b':
                inputNum('Histogram Generation Settings','Bin width','n integer')
            # Update the minimum cutoff.
            case 'm':
                inputNum('Histogram Generation Settings','Minimum cutoff','n integer')
            # Print current Histogram Generation Settings.
            case 'v':
                print()
                parameters.print_section('Histogram Generation Settings')
                print()
            # End editing.
            case '':
                print('Returning to previous menu...\n')
            # Catchall for invalid commands.
            case _:
                print('Unrecognized command. Please review the list of appriopriate inputs.\n')

def plotSet(plot):

    '''The general settings editor for plot settings 
    (histogram visual, line fitting, and residual plot).
    
    Send the function the setting group to be edited.
    
    Assumes the inputs are correct (no input error detection).
    
    Since there are countless plot variables, no user error detection 
    is supplied to insure plot paramters/values are correct.'''

    choice = 'blank'
    print('You are editing settings for a plot. There are many '
          + 'settings for plots - the full list for', plot, 
          'can be found at:\n', plotLink(plot),'\nAs such, '
          + 'you can add and remove settings as you wish.\n')
    # Continue editing until the user is done.
    while choice != '':
        print('Choose a following action:')
        print('c - change new or exisitng ' + plot)
        print('d - delete exisiting ' + plot)
        print('v - view the current ' + plot)
        print('Leave the command blank if you wish to return to the previous menu.')
        choice = input('Enter command: ')
        match choice:
            # Change exisitng setting.
            case 'c':
                print()
                setting = input('Input the parameter name that you want added/modified (or leave blank to cancel): ')
                # Any non-empty input is accepted (no error checking).
                if setting != '':
                    # If setting did not previously exist, tell user.
                    if parameters.get(plot, setting) == None:
                        log('Created parameter ' + setting + ' in ' + plot + '.\n')
                    value = input('Input the value of the parameter (or leave blank to cancel): ')
                    # Any non-empty input is accepted (no error checking).
                    if value != '':
                        # If value is boolean, store as bool.
                        if value == 'True':
                            parameters.set(plot,setting,True)
                        elif value == 'False':
                            parameters.set(plot,setting,False)
                        # If value is numeric, store as integer.
                        elif value.isnumeric():
                            parameters.set(plot,setting,int(value))
                        # If value is a float, store as float.
                        elif isFloat(value):
                            parameters.set(plot,setting,float(value))
                        # Otherwise, store as a string.
                        else:
                            parameters.set(plot,setting,value)
                        # Mark the settings as updated.
                        parameters.update()
                        log('Set paramter ' + setting + ' in ' + plot + ' to ' + value +  '.\n')
                    # User cancels parameter addition:
                    else:
                        print('Cancelling changes...\n')
                # User cancels parameter addition:
                else:
                    print('Cancelling changes...\n')
            # Delete existing setting.
            case 'd':
                print()
                remove = ' '
                while remove != '':
                    remove = input('Input the parameter name that you want removed (or leave blank to cancel): ')
                    # User cancels the removal.
                    if remove == '':
                        print('Cancelling changes...\n')
                    # Error catch for trying to delete a setting that does no exist.
                    elif parameters.get(plot, remove) == None:
                        print('Parameter ' + remove + ' is not currently in the settings.\n')
                    # Remove the parameter from the dictionary.
                    else:
                        parameters.remove(plot, remove)
                        parameters.update()
                        log('Removed parameter ' + remove + ' from ' + plot + '.\n')
                        remove = ''
            # View current settings for the plot.
            case 'v':
                print()
                parameters.print_section(plot)
                print()
            # End editing.
            case '':
                print('Returning to previous menu...\n')
            # Catchall for invalid commands.
            case _:
                print('Unrecognized command. Please review the list of appriopriate inputs.\n')

def settingsEditor():

    '''The main driver function for editing settings.'''

    selection = 'blank'
    # Continue editing until the user is done.
    while selection != '':
        print('What setting group would you like to edit?')
        print('i - input/output settings')
        print('g - general settings')
        print('v - histogram visual settings')
        print('h - histogram generation settings')
        print('l - line fitting settings')
        print('r - residual plot settings')
        print('d - download settings config from file')
        print('Leave the command blank if you wish to return to the previous menu.')
        selection = input('Enter edit command: ')
        match selection:
            # Call the Input/Output Settings editor.
            case 'i':
                print()
                ioSet()
            # Call the General Settings editor.
            case 'g':
                print()
                genSet()
            # Call the plot settings editor under Histogram Visual Settings.
            case 'v':
                print()
                plotSet('Histogram Visual Settings')
            # Call the Histogram Generation Settings editor.
            case 'h':
                print()
                histSet()
            # Call the plot settings editor under Line Fitting Settings.
            case 'l':
                print()
                plotSet('Line Fitting Settings')
            # Call the plot settings editor under Residual Plot Settings.
            case 'r':
                print()
                plotSet('Residual Plot Settings')
            # Import settings from a file.
            case 'd':
                print()
                importSettings(False)
            # End editing.
            case '':
                print('Returning to previous menu...\n')
            # Catchall for invalid commands.
            case _:
                print('Unrecognized command. Please review the list of appriopriate inputs.\n')

def printSelector():

    '''The main driver function for displaying settings.'''

    selection = 'blank'
    # Continue looping until the user is done.
    while selection != '':
        print('What settings would you like to view?')
        print('i - input/output settings')
        print('g - general settings')
        print('v - histogram visual settings')
        print('h - histogram generation settings')
        print('l - line fitting settings')
        print('r - residual plot settings')
        print('a - view all settings')
        print('Leave the command blank if you wish to return to the previous menu.')
        selection = input('Enter print command: ')
        match selection:
            # Print Input/Output Settings.
            case 'i':
                print()
                parameters.print_section('Input/Output Settings')
                print()
            # Print General Settings.
            case 'g':
                print()
                parameters.print_section('General Settings')
                print()
            # Print Histogram Visual Settings.
            case 'v':
                print()
                parameters.print_section('Histogram Visual Settings')
                print()
            # Print Histogram Generation Settings.
            case 'h':
                print()
                parameters.print_section('Histogram Generation Settings')
                print()
            # Print Line Fitting Settings.
            case 'l':
                print()
                parameters.print_section('Line Fitting Settings')
                print()
            # Print Residual Plot Settings.
            case 'r':
                print()
                parameters.print_section('Residual Plot Settings')
                print()
            # Print all settings.
            case 'a':
                parameters.print_all()
                print()
            # End editing.
            case '':
                print('Returning to previous menu...\n')
            # Catchall for invalid commands.
            case _:
                print('Unrecognized command. Please review the list of appriopriate inputs.\n')

def settingsDriver():

    '''The home menu for viewing and editing settings.'''

    selection = 'blank'
    # Continue looping until the user is done.
    while (selection != ''):
        print('What would you like to do with the program settings?')
        print('v - view the current settings')
        print('e - edit the settings')
        print('Leave the command blank if you wish to return to the previous menu.')
        selection = input('Enter menu command: ')
        match selection:
            # Run the settings viewer driver.
            case 'v':
                print()
                printSelector()
            # Run the settings editor driver.
            case 'e':
                print()
                settingsEditor()
            # End editing.
            case '':
                print('Returning to previous menu...\n')
            # Catchall for invalid commands.
            case _:
                print('Unrecognized command. Please review the list of appriopriate inputs.\n')

def importSettings(init):

    '''The function that imports settings from .set files.

    Requires an init input, which is a boolean that indicates 
    whether or not this import is to initialize the settings.'''

    path = 'blank'
    file = 'blank'
    # Continue looping until the user input is a valid file or the
    # input is empty and this call is not for initialization.
    while not os.path.isfile(path) and (init or file != ''):
        print('Enter the name of the settings file (not including '
            + 'the .set file extension) you want imported.')
        # If initializing, user must select a file and cannot cancel.
        if init:
            file = input('Name of file: ')
        # Otherwise, user can cancel the change.
        else:
            file = input('Name of file (or blank to cancel): ')
        # If user wants to cancel and not initializing, do so.
        if file == '' and not init:
            print('Returning to previous menu...\n')
        # For all other user inputs, assume it is the exact file name.
        else:
            # Create an absolute path to the file name.
            file = file + '.set'
            path = os.path.abspath(file)
            # If file exists, import the settings.
            if os.path.isfile(path):
                print('Importing settings from ' + file + '...')
                parameters.read(path)
                changeLog()
                log('Settings from ' + file + ' succesfully imported.\n')
            # Catchall for nonexistent files.
            else:
                print('It appears the file you selected does not exist. Please try again.\n')
    
def main():

    '''The main driver that runs the whole program.'''

    selection = 'blank'
    print('Welcome to the DNNG/PyNoise project. With this software we are '
          + 'taking radiation data from fission reactions (recorded by organic '
          + 'scintillators) and applying a line of best fit to the decay rate. '
          + 'Use this Python suite to analyze a single file or multiple across '
          + 'numerous folders.\n')
    # Continue looping until the user has selected an import option.
    while selection != 'd' and selection != 'i':
        print('Would you like to use the default settings or import another .set file?')
        print('d - use default settings')
        print('i - import custom settings')
        selection = input('Select settings choice: ')
        match selection:
            # Import the default settings.
            case 'd':
                print()
                print('Initializing program with default settings...')
                # Create absolute path for the default settings file and read it in.
                path = os.path.abspath('default.set')
                parameters.read(path)
                changeLog()
                log('Settings from default.set succesfully imported.\n')
            # Import custom settings.
            case 'i':
                print()
                importSettings(True)
            # Catchall for invalid commands.
            case _:
                print('You must choose what settings to import.\n')
    print('Settings initialized. You can now begin using the program.\n')
    print('----------------------------------------------------------\n')
    # Continue running the program until the user is done.
    while selection != '':
        print('You can utitilze any of the following functions:')
        print('m - run the entire program through the main driver')
        print('t - calculate time differences')
        print('p - create plots of the time difference data')
        print('f - fit the data to an exponential curve')
        print('s - view or edit the program settings')
        print('Leave the command blank to end the program.')
        selection = input('Enter a command: ')
        match selection:
            # Run the whole analysis process.
            case 'm':
                if parameters.get('Input/Output Settings','Input type') == 1:
                    mn.analyzeAllType1(parameters.settings)
                elif parameters.get('Input/Output Settings','Input type') == 2:
                    mn.analyzeAllType2(parameters.settings)
                else:
                    print('ERROR: No input file/folder defined. Please edit the settings.')
                print('TODO: Add user interactions here, print statements, options, etc.\n')
            # Utilize the timeDifs.py program.
            case 't':
                print('TODO: Run timeDifs.py accordingly\n')
            # Utilize the plots.py program.
            case 'p':
                print('TODO: Run plots.py accordingly\n')
            # Utilize the fitting.py program.
            case 'f':
                print('TODO: Run fitting.py accordingly\n')
            # View and/or edit program settings.
            case 's':
                print()
                settingsDriver()
            # End the program.
            case '':
                print('\nAre you sure you want to quit the program?')
                choice = input('Enter q to quit and anything else to abort: ')
                # Confirm quit command.
                if choice == 'q':
                    print('Ending program...\n')
                # Catchall for user canceling shutdown.
                else:
                    print('Quit aborted.\n')
                    selection = 'blank'
            # Catchall for invalid commands.
            case _:
                print('Unrecognized command. Please review the list of appriopriate inputs.\n')
    # If the settings have been changed at any point during runtime, notify user.
    if parameters.updated():
        selection = ''
        # Continue looping until the user has decided what to do with their changes.
        while selection != 'd' and selection != 'n' and selection != 'a':
            print('It appears you have made changes to the default '
              + 'settings. Do you want to save your changes?')
            print('d - save current settings as the default')
            print('n - save current settings as a new settings file')
            print('a - abandon current settings')
            selection = input('Select an option: ')
            match selection:
                # User wants to overwrite the defualt settings.
                case 'd':
                    print('This will overwrite the current default settings. Are you sure you want to do this?')
                    choice = input('Enter y to continue and anything else to abort: ')
                    # Confirm user wants to overwrite.
                    if choice == 'y':
                        # Create an absolute path for the default settings
                        # file and write the current settings into it.
                        path = os.path.abspath('default.set')
                        print('Overwriting default settings...')
                        parameters.write(path, True)
                        log('Default settings overwritten.\n')
                    # Catchall for user canceling overwrite.
                    else:
                        print()
                        selection = ''
                # User wants to save settings in a new file.
                case 'n':
                    path = 'blank'
                    file = 'blank'
                    # Loop until user cancels or the user has created a new settings
                    # file/canceled the overwriting of an existing one.
                    while file != '' and not os.path.isfile(path):
                        print('Enter a name for the new settings (not including the .set file extension).')
                        file  = input('Name of file (or blank to cancel): ')
                        if file != '':
                            # Create absolute path for user given file.
                            file = file + '.set'
                            path = os.path.abspath(file)
                            # If settings file already exists, check that user 
                            # wants to overwrite settings currently in the file.
                            if os.path.isfile(path):
                                print('WARNING: settings file ' + file + ' already exists.'
                                    + ' Do you want to overwrite the previous stored settings?')
                                choice = input('Enter y to continue and anything else to abort: ')
                                # If user confirms, overwrite the settings.
                                if choice == 'y':
                                    print('Overwriting ' + file + '...')
                                    parameters.write(path, False)
                                    log('Settings in ' + file + ' overwritten.\n')
                                # Catchall for user canceling overwrite.
                                else:
                                    print()
                                    path = 'blank'
                            # Otherwise, save with no confirmation needed.
                            else:
                                print('Saving current settings to new file ' + file + '...')
                                parameters.write(path, False)
                                log('Settings saved to file ' + file + '.\n')
                        else:
                            print()
                            selection = ''
                # User wants to discard changes.
                case 'a':
                    print('WARNING: all your current changes will be lost. Are you sure you want to do this?')
                    choice = input('Enter y to continue and anything else to abort: ')
                    # Confirm user choice.
                    if choice == 'y':
                        log('Discarded the current settings.\n')
                    # Catchall for user canceling.
                    else:
                        print()
                        selection = ''
                # Catchall for invalid commands.
                case _:
                    print('You must choose what to do with your changes.\n')
    global history
    if history is not None:
        history.close()
    # Shutdown message.
    print('Thank you for using the DNNG/PyNoise project.')

# Tells the program what function to start if this is the main program being run.
if __name__ == "__main__":
    main()