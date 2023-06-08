from . import main as mn
from . import fitting as fit
from . import plots as plt
from . import timeDifs as dif
from . import analyzingFolders as fol
import matplotlib.pyplot as mpl
import numpy as np
mpl.ioff()

# Where the time differences are stored.
time_difs = None
time_difs_file = None
time_difs_method = None
# Where the histogram plot is stored.
histogram = None
hist_file = None
hist_method = None
# Where the best fit curve is stored.
best_fit = None

# The editor class that contains the settings and settings editor.
editor = None

def createTimeDifs():

    '''Create time differences based on the input data.
    
    Will overwrite the current time differences, if they exist.'''

    global time_difs, time_difs_file, time_difs_method, editor
    print('Creating time differences...')
    name = editor.parameters.settings['Input/Output Settings']['Input file/folder']
    name = name[name.rfind('/')+1:]
    # For signle file analysis.
    if name.count('.') > 0:
        # Load data from 
        if editor.parameters.settings['Input/Output Settings'].get('Data Column') is not None:
            data = np.loadtxt(editor.parameters.settings['Input/Output Settings']['Input file/folder'],delimiter=" ", usecols=(editor.parameters.settings['Input/Output Settings']['Data Column']))
        else:
            data = np.loadtxt(editor.parameters.settings['Input/Output Settings']['Input file/folder'])

        if editor.parameters.settings['General Settings']['Sort data']:
            data = np.sort(data)
        time_difs = dif.timeDifCalcs(data, 
            editor.parameters.settings['RossiAlpha Settings']['Histogram Generation Settings']['Reset time'], 
            editor.parameters.settings['RossiAlpha Settings']['Time difference method'])
        time_difs = time_difs.calculate_time_differences()
        editor.log('Calculated time differences for file ' 
            + editor.parameters.settings['Input/Output Settings']['Input file/folder'] + '.\n')
        time_difs_file = editor.parameters.settings['Input/Output Settings']['Input file/folder']
        time_difs_method = editor.parameters.settings['RossiAlpha Settings']['Time difference method']
    # For folder analysis.
    else:
        print('TODO: Add functionality to create time differences for folders.')

def createPlot():

    '''Creates a histogram based on the time difference data.
    
    Will overwrite the current histogram, if one exists.

    Assumes that the time difference data is valid.'''

    global time_difs, histogram, hist_file, hist_method, editor
    print('Building plot...')
    histogram = plt.RossiHistogram(editor.parameters.settings['RossiAlpha Settings']['Histogram Generation Settings']['Reset time'],
                              editor.parameters.settings['RossiAlpha Settings']['Histogram Generation Settings']['Bin width'],
                              editor.parameters.settings['Histogram Visual Settings'],
                              editor.parameters.settings['Input/Output Settings']['Save directory'])
    histogram.plot(time_difs,
              save_fig=editor.parameters.settings['General Settings']['Save figures'],
              show_plot=editor.parameters.settings['General Settings']['Show plots'])
    editor.log('Created a histogram plot using the current settings and time difference data.\n')

def createBestFit():

    '''Creates a line of best fit + residuals based on the created histogram.
    
    Will overwrite the current line of best fit, if one exists.

    Assumes that the histogram is valid.'''

    global time_difs, histogram, best_fit, editor
    print('Building line of best fit...')
    counts, bin_centers, bin_edges = histogram.plot(time_difs, save_fig=False, show_plot=False)
    best_fit = fit.RossiHistogramFit(counts, bin_centers, editor.parameters.settings)
        
        # Fitting curve to the histogram and plotting the residuals
    best_fit.fit_and_residual(save_every_fig=editor.parameters.settings['General Settings']['Save figures'], 
                              show_plot=editor.parameters.settings['General Settings']['Show plots'])
    editor.log('Created line of best fit with residuals for the current histogram.\n')

def main(editorIn):
    global editor
    editor = editorIn
    selection = 'blank'
    while selection != '':
        print('What analysis would you like to perform?')
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
                name = editor.parameters.settings['Input/Output Settings']['Input file/folder']
                name = name[name.rfind('/')+1:]
                if name.count('.') > 0:
                    if editor.parameters.settings['RossiAlpha Settings']['Time difference method'] != 'any_and_all':
                        print('ERROR: To analyze a single file, you must use '
                              + 'the any_and_all time difference method only.\n')
                    else:
                        print('Running the entire RossiAlpha method...')
                        time_difs, histogram, best_fit = mn.analyzeAllType1(editor.parameters.settings)
                        editor.log('Ran the entire RossiAlpha method on file ' 
                            + editor.parameters.settings['Input/Output Settings']['Input file/folder'] 
                            + '.\n')
                else:
                    print('Running the entire RossiAlpha method...')
                    mn.analyzeAllType2(editor.parameters.settings)
                    editor.log('Ran the entire RossiAlpha method on folder ' 
                        + editor.parameters.settings['Input/Output Settings']['Input file/folder'] 
                        + '.\n')
                    print('TODO: Implement modularity for folder analysis.')
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
                    # If there aren't any current time differences or the time differences aren't current, make them.
                    if time_difs is None or (not (time_difs_method == editor.parameters.settings['RossiAlpha Settings']['Time difference method'] and time_difs_file == editor.parameters.settings['Input/Output Settings']['Input file/folder'])):
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
                    if histogram is None or (not (hist_method == editor.parameters.settings['RossiAlpha Settings']['Time difference method'] and hist_file == editor.parameters.settings['Input/Output Settings']['Input file/folder'])):
                        if time_difs is None or (not (time_difs_method ==editor.parameters.settings['RossiAlpha Settings']['Time difference method'] and time_difs_file == editor.parameters.settings['Input/Output Settings']['Input file/folder'])):
                            createTimeDifs()
                        createPlot()
                    createBestFit()
            # View and/or edit program settings.
            case 's':
                print()
                editor.driver()
            # End the program.
            case '':
                print('Returning to main menu...\n')
            # Catchall for invalid commands.
            case _:
                print('Unrecognized command. Please review the list of appriopriate inputs.\n')
    return editor