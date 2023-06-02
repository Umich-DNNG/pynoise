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

editor = edit.Editor()

time_difs = None
time_difs_file = None
time_difs_method = None
histogram = None
hist_file = None
hist_method = None
best_fit = None

os.chdir(os.path.dirname(os.path.realpath(__file__)))

def createTimeDifs():

    '''Create time differences based on the input data.
    
    Will overwrite the current time differences, if they exist.'''

    global time_difs, time_difs_file, time_difs_method
    print('Creating time differences...')
    if editor.parameters.settings['Input/Output Settings']['Input type'] == 1:
        data = np.loadtxt(editor.parameters.settings['Input/Output Settings']['Input file/folder'])
        if editor.parameters.settings['General Settings']['Sort data?']:
            data = np.sort(data)
        time_difs = dif.timeDifCalcs(data, 
            editor.parameters.settings['Histogram Generation Settings']['Reset time'], 
            editor.parameters.settings['General Settings']['Time difference method'])
        time_difs = time_difs.calculate_time_differences()
        editor.log('Calculated time differences for file ' 
            + editor.parameters.settings['Input/Output Settings']['Input file/folder'] + '.\n')
        time_difs_file = editor.parameters.settings['Input/Output Settings']['Input file/folder']
        time_difs_method = editor.parameters.settings['General Settings']['Time difference method']
    elif editor.parameters.settings['Input/Output Settings']['Input type'] == 2:
        print('TODO: Add functionality to create time differences for folders.')
    else:
        print('ERROR: No input file/folder defined. Please edit the settings.')

def createPlot():

    '''Creates a histogram based on the time difference data.
    
    Will overwrite the current histogram, if one exists.

    Assumes that the time difference data is valid.'''

    global time_difs, histogram, hist_file, hist_method
    print('Building plot...')
    histogram = plt.RossiHistogram(editor.parameters.settings['Histogram Generation Settings']['Reset time'],
                              editor.parameters.settings['Histogram Generation Settings']['Bin width'],
                              editor.parameters.settings['Histogram Visual Settings'],
                              editor.parameters.settings['Input/Output Settings']['Save directory'])
    histogram.plot(time_difs,
              save_fig=editor.parameters.settings['General Settings']['Save figures?'],
              show_plot=editor.parameters.settings['General Settings']['Show plots?'])
    editor.log('Created a histogram plot using the current settings and time difference data.\n')

def createBestFit():

    '''Creates a line of best fit + residuals based on the created histogram.
    
    Will overwrite the current line of best fit, if one exists.

    Assumes that the histogram is valid.'''

    global time_difs, histogram, best_fit
    print('Building line of best fit...')
    counts, bin_centers, bin_edges = histogram.plot(time_difs, save_fig=False, show_plot=False)
    best_fit = fit.RossiHistogramFit(counts, bin_centers, editor.parameters.settings)
        
    best_fit.fit_and_residual(save_every_fig=editor.parameters.settings['General Settings']['Save figures?'], 
                              show_plot=editor.parameters.settings['General Settings']['Show plots?'])
    editor.log('Created line of best fit with residuals for the current histogram.\n')

def main():

    '''The main driver that runs the whole program.'''

    global time_difs, histogram, best_fit, time_difs_file,time_difs_method
    selection = 'blank'
    print('Welcome to the DNNG/PyNoise project. With this software we are '
          + 'taking radiation data from fission reactions (recorded by organic '
          + 'scintillators) and applying a line of best fit to the decay rate. '
          + 'Use this Python suite to analyze a single file or multiple across '
          + 'numerous folders.\n')
    while selection != 'd' and selection != 'i':
        print('Would you like to use the default settings or import another .set file?')
        print('d - use default settings')
        print('i - import custom settings')
        selection = input('Select settings choice: ')
        match selection:
            case 'd':
                print()
                print('Initializing program with default settings...')
                path = os.path.abspath('default.set')
                editor.parameters.read(path)
                editor.changeLog()
                if editor.parameters.settings['Input/Output Settings']['Input type'] == 0:
                    print('WARNING: with the current settings, the input file'
                        + '/folder is not specified. You must add it manually.')
                editor.log('Settings from default.set succesfully imported.\n')
            case 'i':
                file = ''
                while not os.path.isfile(os.path.abspath(file)):
                    file = input('Enter a settings file (no .set extension): ')
                    file = file + '.set'
                    if os.path.isfile(os.path.abspath(file)):
                        print('Initializing the program with ' + file + '...')
                        editor.parameters.read(os.path.abspath(file))
                        editor.changeLog()
                        if editor.parameters.settings['Input/Output Settings']['Input type'] == 0:
                            print('WARNING: with the current settings, the input file'
                                + '/folder is not specified. You must add it manually.')
                        editor.log('Settings from ' + file + ' succesfully imported.\n')
                    else:
                        print('ERROR: ' + file + ' does not exist in this directory. '
                              + 'Make sure that your settings file is named '
                              + 'correctly and in the same folder as this program.\n')
            case _:
                print('You must choose what settings to import.\n')
    print('Settings initialized. You can now begin using the program.\n')
    print('----------------------------------------------------------\n')
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
            case 'm':
                if editor.parameters.settings['Input/Output Settings']['Input type'] == 1:
                    if editor.parameters.settings['General Settings']['Time difference method'] != 'any_and_all':
                        print('ERROR: To analyze a single file, you must use '
                              + 'the any_and_all time difference method only.\n')
                    else:
                        print('Running the entire RossiAlpha method...')
                        time_difs, histogram, best_fit = mn.analyzeAllType1(editor.parameters.settings)
                        editor.log('Ran the entire RossiAlpha method on file ' 
                            + editor.parameters.settings['Input/Output Settings']['Input file/folder'] 
                            + '.\n')
                elif editor.parameters.settings['Input/Output Settings']['Input type'] == 2:
                    print('Running the entire RossiAlpha method...')
                    mn.analyzeAllType2(editor.parameters.settings)
                    editor.log('Ran the entire RossiAlpha method on folder ' 
                        + editor.parameters.settings['Input/Output Settings']['Input file/folder'] 
                        + '.\n')
                    print('TODO: Implement modularity for folder analysis.')
                else:
                    print('ERROR: No input file/folder defined. Please edit the settings.\n')
            case 't':
                if time_difs is not None:
                    print('WARNING: There are already stored time differences '
                          + 'in this runtime. Do you want to overwrite them?')
                    choice = input('Enter y to continue and anything else to abort: ')
                    if choice == 'y':
                        editor.log('Currently stored time differences overwritten.\n')
                    else:
                        print('Cancelling overwrite...\n')
                        selection = 'blank'
                if selection != 'blank':
                    createTimeDifs()
            case 'p':
                if histogram is not None:
                    print('WARNING: There is an already stored histogram '
                          + 'in this runtime. Do you want to overwrite it?')
                    choice = input('Enter y to continue and anything else to abort: ')
                    if choice == 'y':
                        editor.log('Currently stored time histogram overwritten.\n')
                    else:
                        print('Cancelling overwrite...\n')
                        selection = 'blank'
                if selection != 'blank':
                    if time_difs is None or (not (time_difs_method == editor.parameters.settings['General Settings']['Time difference method'] and time_difs_file == editor.parameters.settings['Input/Output Settings']['Input file/folder'])):
                        createTimeDifs()
                    createPlot()
            case 'f':
                if best_fit is not None:
                    print('WARNING: There is an already stored best fit line '
                          + 'in this runtime. Do you want to overwrite it?')
                    choice = input('Enter y to continue and anything else to abort: ')
                    if choice == 'y':
                        editor.log('Currently stored best fit line overwritten.\n')
                    else:
                        print('Cancelling overwrite...\n')
                        selection = 'blank'
                if selection != 'blank':
                    if histogram is None or (not (hist_method == editor.parameters.settings['General Settings']['Time difference method'] and hist_file == editor.parameters.settings['Input/Output Settings']['Input file/folder'])):
                        if time_difs is None or (not (time_difs_method ==editor.parameters.settings['General Settings']['Time difference method'] and time_difs_file == editor.parameters.settings['Input/Output Settings']['Input file/folder'])):
                            createTimeDifs()
                        createPlot()
                    createBestFit()
            case 's':
                print()
                editor.driver()
            case '':
                print('\nAre you sure you want to quit the program?')
                choice = input('Enter q to quit and anything else to abort: ')
                if choice == 'q':
                    print('Ending program...\n')
                else:
                    print('Quit aborted.\n')
                    selection = 'blank'
            case _:
                print('Unrecognized command. Please review the list of appriopriate inputs.\n')
    if editor.parameters.changed:
        selection = ''
        while selection != 'd' and selection != 'n' and selection != 'a':
            print('It appears you have made unsaved changes to the '
              + 'settings. Do you want to save your changes?')
            print('d - save current settings as the default')
            print('n - save current settings as a new settings file')
            print('a - abandon current settings')
            selection = input('Select an option: ')
            match selection:
                case 'd':
                    print('This will overwrite the current default settings. Are you sure you want to do this?')
                    choice = input('Enter y to continue and anything else to abort: ')
                    if choice == 'y':
                        path = os.path.abspath('default.set')
                        print('Overwriting default settings...')
                        editor.parameters.write(path, 'The default settings for running the PyNoise project.\n')
                        editor.log('Default settings overwritten.\n')
                    else:
                        print()
                        selection = ''
                case 'n':
                    path = 'blank'
                    file = 'blank'
                    while file != '' and not os.path.isfile(path):
                        print('Enter a name for the new settings (not including the .set file extension).')
                        file  = input('Name of file (or blank to cancel): ')
                        if file != '':
                            file = file + '.set'
                            path = os.path.abspath(file)
                            if os.path.isfile(path):
                                print('WARNING: settings file ' + file + ' already exists.'
                                    + ' Do you want to overwrite the previous stored settings?')
                                choice = input('Enter y to continue and anything else to abort: ')
                                if choice == 'y':
                                    print('Overwriting ' + file + '...')
                                    editor.parameters.write(path, 'Custom user generated settings.\n')
                                    editor.log('Settings in ' + file + ' overwritten.\n')
                                else:
                                    print()
                                    path = 'blank'
                            else:
                                print('Saving current settings to new file ' + file + '...')
                                editor.parameters.write(path, 'Custom user generated settings.\n')
                                editor.log('Settings saved to file ' + file + '.\n')
                        else:
                            print()
                            selection = ''
                case 'a':
                    print('WARNING: all your current changes will be lost. Are you sure you want to do this?')
                    choice = input('Enter y to continue and anything else to abort: ')
                    if choice == 'y':
                        editor.log('Discarded the current settings.\n')
                    else:
                        print()
                        selection = ''
                case _:
                    print('You must choose what to do with your changes.\n')
    if editor.history is not None:
        editor.history.close()
    print('Thank you for using the DNNG/PyNoise project.')

if __name__ == "__main__":
    main()