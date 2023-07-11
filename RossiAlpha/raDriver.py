'''The command line driver for running Rossi Alpha analysis.'''

import editor as edit
import analyze as alz

# The editor class that contains the settings and settings editor.
editor: edit.Editor = None
analyzer = alz.Analyzer()

def main(editorIn: edit.Editor, queue: list[str] = []):
    global editor
    editor = editorIn
    selection = 'blank'
    while selection != '' and selection != 'x':
        editor.print('What analysis would you like to perform?')
        editor.print('m - run the entire program through the main driver')
        editor.print('t - calculate time differences')
        editor.print('p - create plots of the time difference data')
        editor.print('f - fit the data to an exponential curve')
        editor.print('s - view or edit the program settings')
        editor.print('Leave the command blank or enter x to return to the main menu.')
        if len(queue) != 0:
            selection = queue[0]
            queue.pop(0)
            if selection == '':
                editor.print('Running automated return command...')
            else:
                editor.print('Running automated command ' + selection + '...')
        else:
            selection = input('Enter a command: ')
        match selection:
            # Run the whole analysis process.
            case 'm':
                if editor.parameters.settings['Input/Output Settings']['Input file/folder'] == 'none':
                    print('ERROR: You currently have no input file or folder defined. '
                          + 'Please make sure to specify one before running any analysis.\n')
                else:
                    name = editor.parameters.settings['Input/Output Settings']['Input file/folder']
                    name = name[name.rfind('/')+1:]
                    if name.count('.') > 0:
                        if editor.parameters.settings['RossiAlpha Settings']['Time difference method'] != 'any_and_all' and editor.parameters.settings['Input/Output Settings']['Channels column'] is None:
                            print('ERROR: When using methods other than any_and_all, you must specify a column.\n')
                        else:
                            editor.print('Running the entire RossiAlpha method...')
                            analyzer.raAll(True, editor.parameters.settings)
                            editor.log('Ran the entire RossiAlpha method on file ' 
                                + editor.parameters.settings['Input/Output Settings']['Input file/folder'] 
                                + '.\n')
                    else:
                        editor.print('Running the entire RossiAlpha method...')
                        analyzer.raAll(False, editor.parameters.settings)
                        editor.log('Ran the entire RossiAlpha method on folder ' 
                            + editor.parameters.settings['Input/Output Settings']['Input file/folder'] 
                            + '.\n')
            # Calculate time differences for the given input.
            case 't':
                if editor.parameters.settings['Input/Output Settings']['Input file/folder'] == 'none':
                    print('ERROR: You currently have no input file or folder defined. '
                          + 'Please make sure to specify one before running any analysis.\n')
                else:
                    # If time differences are already stored, notify user.
                    if analyzer.time_difs is not None:
                        editor.print('WARNING: There are already stored time differences '
                            + 'in this runtime. Do you want to overwrite them?')
                        if len(queue) != 0:
                            choice = queue[0]
                            queue.pop(0)
                            if choice == '':
                                editor.print('Running automated return command...')
                            else:
                                editor.print('Running automated command ' + choice + '...')
                        else:
                            choice = input('Enter y to continue and anything else to abort: ')
                        # Confirm user wants to overwrite time differences.
                        if choice == 'y':
                            editor.log('Currently stored time differences overwritten.\n')
                        # Catchall for user canceling overwrite.
                        else:
                            editor.print('Cancelling overwrite...\n')
                            selection = 'blank'
                    # If user hasn't canceled, create the time differences.
                    if selection != 'blank':
                        editor.print('Creating new time differences...')
                        analyzer.createTimeDifs(editor.parameters.settings['Input/Output Settings'],
                                                editor.parameters.settings['General Settings']['Sort data'],
                                                editor.parameters.settings['RossiAlpha Settings']['Reset time'],
                                                editor.parameters.settings['RossiAlpha Settings']['Time difference method'],
                                                editor.parameters.settings['RossiAlpha Settings']['Digital delay'])
                        editor.log('New time differences created.\n')
            # Plot the time difference data.
            # TODO: Have some method of detection for when the input has changed.
            case 'p':
                if editor.parameters.settings['Input/Output Settings']['Input file/folder'] == 'none':
                    print('ERROR: You currently have no input file or folder defined. '
                          + 'Please make sure to specify one before running any analysis.\n')
                else:
                    # If plot is already stored, notify user.
                    if analyzer.histogram is not None:
                        editor.print('WARNING: There is an already stored histogram '
                            + 'in this runtime. Do you want to overwrite it?')
                        if len(queue) != 0:
                            choice = queue[0]
                            queue.pop(0)
                            if choice == '':
                                editor.print('Running automated return command...')
                            else:
                                editor.print('Running automated command ' + choice + '...')
                        else:
                            choice = input('Enter y to continue and anything else to abort: ')
                        # Confirm user wants to overwrite the plot.
                        if choice == 'y':
                            editor.log('Currently stored time histogram overwritten.\n')
                        # Catchall for user canceling overwrite.
                        else:
                            editor.print('Cancelling overwrite...\n')
                            selection = 'blank'
                    # If user hasn't canceled, create the histogram.
                    if selection != 'blank':
                        editor.print('Creating new histogram...')
                        analyzer.plotSplit(editor.parameters.settings)
                        editor.log('New histogram created.\n')
            # Create a line of best fit and show the residuals.
            case 'f':
                if editor.parameters.settings['Input/Output Settings']['Input file/folder'] == 'none':
                    print('ERROR: You currently have no input file or folder defined. '
                          + 'Please make sure to specify one before running any analysis.\n')
                else:
                    # If plot is already stored, notify user.
                    if analyzer.best_fit is not None:
                        editor.print('WARNING: There is an already stored best fit line '
                            + 'in this runtime. Do you want to overwrite it?')
                        if len(queue) != 0:
                            choice = queue[0]
                            queue.pop(0)
                            if choice == '':
                                editor.print('Running automated return command...')
                            else:
                                editor.print('Running automated command ' + choice + '...')
                        else:
                            choice = input('Enter y to continue and anything else to abort: ')
                        # Confirm user wants to overwrite the plot.
                        if choice == 'y':
                            editor.log('Currently stored best fit line overwritten.\n')
                        # Catchall for user canceling overwrite.
                        else:
                            editor.print('Cancelling overwrite...\n')
                            selection = 'blank'
                    # If user hasn't canceled, create the line of best fit.
                    if selection != 'blank':
                        # If there aren't any current time 
                        # differences/histogram plots, make them.
                        if analyzer.histogram is None or (not (analyzer.method == editor.parameters.settings['RossiAlpha Settings']['Time difference method'] 
                                                          and analyzer.input == editor.parameters.settings['Input/Output Settings']['Input file/folder'])):
                            editor.print('Creating new histogram...')
                            analyzer.plotSplit(editor.parameters.settings)
                            editor.log('New histogram created.\n')
                        editor.print('Creating new best fit and residual...')
                        analyzer.createBestFit(editor.parameters.settings['RossiAlpha Settings']['Minimum cutoff'],
                                               editor.parameters.settings['RossiAlpha Settings']['Time difference method'],
                                               editor.parameters.settings['General Settings'],
                                               editor.parameters.settings['Input/Output Settings']['Save directory'],
                                               editor.parameters.settings['Line Fitting Settings'],
                                               editor.parameters.settings['Residual Plot Settings'],
                                               editor.parameters.settings['Histogram Visual Settings'])
                        editor.log('New best fit and residual created.\n')
            # View and/or edit program settings.
            case 's':
                editor.print('')
                queue = editor.driver(queue)
            # End the program.
            case '':
                editor.print('Returning to main menu...\n')
            case 'x':
                editor.print('Returning to main menu...\n')
            # Catchall for invalid commands.
            case _:
                print('ERROR: Unrecognized command ' + selection 
                        + '. Please review the list of appriopriate inputs.\n')
    return editor, queue