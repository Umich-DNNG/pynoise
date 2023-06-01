'''The main file that should be run each time the user wants to use this Python Suite.'''

import main as mn
import fitting as fit
import plots as plt
import timeDifs as dif
import analyzingFolders as fol
import editor as edit
import os
import numpy as np
import matplotlib.pyplot as mpl
mpl.ioff()

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

# The editor class that contains the settings and settings editor.
editor = edit.Editor()

# Where the time differences are stored.
time_difs = None

# Where the histogram plot is stored.
histogram = None

# Where the best fit curve is stored.
best_fit = None

# Set the current working directory for assigning absolute paths.
os.chdir(os.path.dirname(os.path.realpath(__file__)))

def createTimeDifs():

    '''Create time differences based on the input data.
    
    Will overwrite the current time differences, if they exist.'''

    global time_difs
    print('Creating time differences...')
    # For signle file analysis.
    if editor.parameters.get('Input/Output Settings','Input type') == 1:
        # Load data from 
        data = np.loadtxt(editor.parameters.get('Input/Output Settings','Input file/folder'))
        if editor.parameters.get('General Settings','Sort data?'):
            data = np.sort(data)
        time_difs = dif.timeDifCalcs(data, 
            editor.parameters.get('Histogram Generation Settings','Reset time'), 
            editor.parameters.get('General Settings','Time difference method'))
        time_difs = time_difs.calculate_time_differences()
        editor.log('Calculated time differences for file ' 
            + editor.parameters.get('Input/Output Settings','Input file/folder') + '.\n')
    # For folder analysis.
    elif editor.parameters.get('Input/Output Settings','Input type') == 2:
        print('TODO: Add functionality to create time differences for folders.')
    # Catchall for nonexistent input.
    else:
        print('ERROR: No input file/folder defined. Please edit the settings.')

def createPlot():

    '''Creates a histogram based on the time difference data.
    
    Will overwrite the current histogram, if one exists.

    Assumes that the time difference data is valid.'''

    global time_difs, histogram
    print('Building plot...')
    histogram = plt.RossiHistogram(editor.parameters.get('Histogram Generation Settings','Reset time'),
                              editor.parameters.get('Histogram Generation Settings','Bin width'),
                              editor.parameters.getGroup('Histogram Visual Settings'),
                              editor.parameters.get('Input/Output Settings','Save directory'))
    histogram.plot(time_difs,
              save_fig=editor.parameters.get('General Settings','Save figures?'),
              show_plot=editor.parameters.get('General Settings','Show plots?'))
    editor.log('Created a histogram plot using the current settings and time difference data.\n')

def createBestFit():

    '''Creates a line of best fit + residuals based on the created histogram.
    
    Will overwrite the current line of best fit, if one exists.

    Assumes that the histogram is valid.'''

    global time_difs, histogram, best_fit
    print('Building line of best fit...')
    counts, bin_centers, bin_edges = histogram.plot(time_difs, save_fig=False, show_plot=False)
    best_fit = fit.RossiHistogramFit(counts, bin_centers, editor.parameters.settings)
        
        # Fitting curve to the histogram and plotting the residuals
    best_fit.fit_and_residual(save_every_fig=editor.parameters.get('General Settings','Save figures?'), 
                              show_plot=editor.parameters.get('General Settings','Show plots?'))
    editor.log('Created line of best fit with residuals for the current histogram.\n')

def main():

    '''The main driver that runs the whole program.'''

    global time_difs, histogram, best_fit
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
                editor.parameters.read(path)
                editor.changeLog()
                editor.log('Settings from default.set succesfully imported.\n')
            # Import custom settings.
            case 'i':
                print()
                editor.importSettings(True)
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
                if editor.parameters.get('Input/Output Settings','Input type') == 1:
                    if editor.parameters.get('General Settings','Time difference method') != 'any_and_all':
                        print('ERROR: To analyze a single file, you must use '
                              + 'the any_and_all time difference method only.\n')
                    else:
                        print('Running the entire RossiAlpha method...')
                        time_difs, histogram, best_fit = mn.analyzeAllType1(editor.parameters.settings)
                        editor.log('Ran the entire RossiAlpha method on file ' 
                            + editor.parameters.get('Input/Output Settings','Input file/folder') 
                            + '.\n')
                elif editor.parameters.get('Input/Output Settings','Input type') == 2:
                    print('Running the entire RossiAlpha method...')
                    mn.analyzeAllType2(editor.parameters.settings)
                    editor.log('Ran the entire RossiAlpha method on folder ' 
                        + editor.parameters.get('Input/Output Settings','Input file/folder') 
                        + '.\n')
                    print('TODO: Implement modularity for folder analysis.')
                else:
                    print('ERROR: No input file/folder defined. Please edit the settings.')
            # Calculate time differences for the given input.
            # TODO: Have some method of detection for when the input has changed.
            case 't':
                # If time differences are already stored, notify user.
                if time_difs is not None:
                    print('WARNING: There are already stored time differences '
                          + 'in this runtime. Do you want to overwrite them?')
                    choice = input('Enter y to continue and anything else to abort: ')
                    # Confirm user wants to overwrite time differences.
                    if choice == 'y':
                        editor.log('Currently stored time differences overwritten.\n')
                    # Catchall for user canceling overwrite.
                    else:
                        print('Cancelling overwrite...\n')
                        selection = 'blank'
                # If user hasn't canceled, create the time differences.
                if selection != 'blank':
                    createTimeDifs()
            # Plot the time difference data.
            # TODO: Have some method of detection for when the input has changed.
            case 'p':
                # If plot is already stored, notify user.
                if histogram is not None:
                    print('WARNING: There is an already stored histogram '
                          + 'in this runtime. Do you want to overwrite it?')
                    choice = input('Enter y to continue and anything else to abort: ')
                    # Confirm user wants to overwrite the plot.
                    if choice == 'y':
                        editor.log('Currently stored time histogram overwritten.\n')
                    # Catchall for user canceling overwrite.
                    else:
                        print('Cancelling overwrite...\n')
                        selection = 'blank'
                # If user hasn't canceled, create the histogram.
                if selection != 'blank':
                    # If there aren't any current time differences, make them.
                    if time_difs is None:
                        createTimeDifs()
                    createPlot()
            # Create a line of best fit and show the residuals.
            case 'f':
                # If plot is already stored, notify user.
                if best_fit is not None:
                    print('WARNING: There is an already stored best fit line '
                          + 'in this runtime. Do you want to overwrite it?')
                    choice = input('Enter y to continue and anything else to abort: ')
                    # Confirm user wants to overwrite the plot.
                    if choice == 'y':
                        editor.log('Currently stored best fit line overwritten.\n')
                    # Catchall for user canceling overwrite.
                    else:
                        print('Cancelling overwrite...\n')
                        selection = 'blank'
                # If user hasn't canceled, create the line of best fit.
                if selection != 'blank':
                    # If there aren't any current time 
                    # differences/histogram plots, make them.
                    if histogram is None:
                        if time_difs is None:
                            createTimeDifs()
                        createPlot()
                    createBestFit()
            # View and/or edit program settings.
            case 's':
                print()
                editor.driver()
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
    if editor.parameters.updated():
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
                        editor.parameters.write(path, True)
                        editor.log('Default settings overwritten.\n')
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
                                    editor.parameters.write(path, False)
                                    editor.log('Settings in ' + file + ' overwritten.\n')
                                # Catchall for user canceling overwrite.
                                else:
                                    print()
                                    path = 'blank'
                            # Otherwise, save with no confirmation needed.
                            else:
                                print('Saving current settings to new file ' + file + '...')
                                editor.parameters.write(path, False)
                                editor.log('Settings saved to file ' + file + '.\n')
                        else:
                            print()
                            selection = ''
                # User wants to discard changes.
                case 'a':
                    print('WARNING: all your current changes will be lost. Are you sure you want to do this?')
                    choice = input('Enter y to continue and anything else to abort: ')
                    # Confirm user choice.
                    if choice == 'y':
                        editor.log('Discarded the current settings.\n')
                    # Catchall for user canceling.
                    else:
                        print()
                        selection = ''
                # Catchall for invalid commands.
                case _:
                    print('You must choose what to do with your changes.\n')
    # Close the log file if one is open.
    if editor.history is not None:
        editor.history.close()
    # Shutdown message.
    print('Thank you for using the DNNG/PyNoise project.')

# Tells the program what function to start if this is the main program being run.
if __name__ == "__main__":
    main()