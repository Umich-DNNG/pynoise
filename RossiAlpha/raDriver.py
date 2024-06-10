'''The command line driver for running Rossi Alpha analysis.'''



# Necessary imports.
import editor as edit
import analyze as alz
import os



# The global object.
analyzer = alz.Analyzer()



def main(editor: edit.Editor, queue: list[str] = []):

    '''The function that runs when the Rossi Alpha driver is called.
    
    Inputs:
    - editor: the current settings editor from the main driver.
    - queue: the list of prefilled commands. 
    If not given, assumes an empty queue.
        
    Outputs:
    - the altered settings/settings editor.
    - the remaining queue after runtime.'''

    # Initalize user response variable.
    selection = 'blank'
    # Keep looping until user returns to the previous menu.
    while selection != '' and selection != 'x':
        # Display options.
        editor.print('What analysis would you like to perform?')
        editor.print('m - run the entire program through the main driver')
        editor.print('t - calculate time differences')
        editor.print('p - create plots of the time difference data')
        editor.print('f - fit the data to an exponential curve')
        editor.print('s - view or edit the program settings')
        editor.print('Leave the command blank or enter x to return to the main menu.')
        # If there's currently something in the command queue, 
        # take that as the input and remove it from the queue.
        if len(queue) != 0:
            selection = queue[0]
            queue.pop(0)
            # Tell user automated command is being run.
            if selection == '' or selection == 'x':
                editor.print('Running automated return command...')
            else:
                editor.print('Running automated command ' + selection + '...')
        # Otherwise, prompt the user.
        else:
            selection = input('Enter a command: ')
        if selection == 'm' or selection == 't' or selection == 'p' or selection == 'f':
            # Get the file name for later use.
            name = editor.parameters.settings['Input/Output Settings']['Input file/folder']
            name = name[name.rfind('/')+1:]
            # Ensure there is a valid input file/
            # folder, and if not throw an error.
            if (not os.path.isfile(editor.parameters.settings['Input/Output Settings']['Input file/folder'])
            and not os.path.isdir(editor.parameters.settings['Input/Output Settings']['Input file/folder'])):
                print('ERROR: You currently have no input file or '
                      + 'folder defined or the specified input file/'
                      + 'directory does not exist. Please make sure '
                      + 'to adjust this before running any analysis.\n')
                selection = 'blank'
                continue
            # Ensure the user is using a valid time difference method.
            if (editor.parameters.settings['RossiAlpha Settings']['Time difference method'] != 'aa' 
                and editor.parameters.settings['RossiAlpha Settings']['Time difference method'] != ['aa']
                and editor.parameters.settings['Input/Output Settings']['Channels column'] == None
                and name.count('.') > 0):
                print('ERROR: When using methods other than any and all for a file analysis, you must specify a channels column.\n')
                selection = 'blank'
                continue
            # if is a folder and number of folders is specified, it must be more than one folder
            if (name.count('.') == 0 and editor.parameters.settings["General Settings"]["Number of folders"] != None 
                and editor.parameters.settings["General Settings"]["Number of folders"] <= 1):
                print('ERROR: Running RossiAlpha method on a folder of folders requires either more' 
                    + ' than one folder specified or \"null\" for the setting.\n')
                selection = 'blank'
                continue
            # For full analysis:
            elif selection == 'm':
                # If input is a file and the bin width is not specified:
                if name.count('.') > 0 and editor.parameters.settings['RossiAlpha Settings']['Bin width'] == None:
                    print('ERROR: Using RossiAlpha on a file to generate plots of the time difference data and/or'
                        + ' fit the data to an exponetial curve requires the bin width to be specified.\n')
                    selection = 'blank'
                    continue
                # Display progress.
                editor.print('Running the entire RossiAlpha method...')
                # If input is file:
                if name.count('.') > 0:
                    # Run full analysis on the file.
                    analyzer.fullFile(editor.parameters.settings)
                    # Display success.
                    editor.log('Ran the entire RossiAlpha method on file ' 
                        + editor.parameters.settings['Input/Output Settings']['Input file/folder'] 
                        + '.\n')
                # If input is a folder:
                else:
                    # Run full analysis on the folder.
                    successful = analyzer.fullFolder(editor.parameters.settings)
                    # Display success if successful.
                    if successful:
                        editor.log('Ran the entire RossiAlpha method on folder ' 
                            + editor.parameters.settings['Input/Output Settings']['Input file/folder'] 
                            + '.\n')
                    else:
                        selection = 'blank'
                        continue
            # For time difference calculation:
            elif selection == 't':
                # If time differences already exist.
                if analyzer.RATimeDifs['Time differences'] is not None:
                    # Create a dictionary of the current relevant settings.
                    check = {'Input file/folder': editor.parameters.settings['Input/Output Settings']['Input file/folder'],
                            'Sort data': editor.parameters.settings['General Settings']['Sort data'],
                            'Time difference method': editor.parameters.settings['RossiAlpha Settings']['Time difference method'],
                            'Digital delay': editor.parameters.settings['RossiAlpha Settings']['Digital delay'],
                            'Reset time': editor.parameters.settings['RossiAlpha Settings']['Reset time']}
                    # If in folder mode, add the number of folders setting.
                    if name.count('.') == 0:
                        check['Number of folders'] = editor.parameters.settings['General Settings']['Number of folders']
                    # If time differences are still valid:
                    if analyzer.isValid('RATimeDifs', check):
                        # Notify user that calculation is being canceled.
                        editor.print('Time differences have already been '
                                     + 'generated with these settings.\nTime '
                                     + 'difference calculation aborted.\n')
                        # Reset the user input variable.
                        selection = 'blank'
                    # Time differences are not valid anymore.
                    else:
                        # Warn user of overwrite.
                        editor.print('WARNING: There are already stored time differences '
                            + 'in this runtime. Do you want to overwrite them?')
                        # If there's currently something in the command queue, 
                        # take that as the input and remove it from the queue.
                        if len(queue) != 0:
                            choice = queue[0]
                            queue.pop(0)
                            # Tell user automated command is being run.
                            if choice != 'y':
                                editor.print('Running automated return command...')
                            else:
                                editor.print('Running automated command y...')
                        # Otherwise, prompt the user.
                        else:
                            choice = input('Enter y to continue and anything else to abort: ')
                        # Display confirmation for overwriting.
                        if choice == 'y':
                            editor.log('Currently stored time differences overwritten.\n')
                        # Display confirmation for cancel.
                        else:
                            editor.print('Cancelling overwrite...\n')
                            selection = 'blank'
                # If calculation hasn't been canceled:
                if selection != 'blank':
                    # Display progress.
                    editor.print('Creating new time differences...')
                    # Create the time differences.
                    analyzer.createTimeDifs(editor.parameters.settings['Input/Output Settings'],
                                            editor.parameters.settings['General Settings']['Sort data'],
                                            editor.parameters.settings['RossiAlpha Settings']['Reset time'],
                                            editor.parameters.settings['RossiAlpha Settings']['Time difference method'],
                                            editor.parameters.settings['RossiAlpha Settings']['Digital delay'],
                                            editor.parameters.settings['Input/Output Settings']['Quiet mode'],
                                            name.count('.') == 0)
                    # Display success.
                    editor.log('New time differences created.\n')
            # If input is a file and the bin width is not specified:
            if name.count('.') > 0 and editor.parameters.settings['RossiAlpha Settings']['Bin width'] == None:
                print('ERROR: Using RossiAlpha on a file to generate plots of the time difference data and/or'
                    + ' fit the data to an exponetial curve requires the bin width to be specified.\n')
                selection = 'blank'
                continue
            # Make a histogram of the time differences.
            elif selection == 'p':
                # If plot is already stored:
                if analyzer.RAHist['Histogram'] is not None:
                    # Warn user of overwrite.
                    editor.print('WARNING: There is an already stored histogram '
                        + 'in this runtime. Do you want to overwrite it?')
                    # If there's currently something in the command queue, 
                    # take that as the input and remove it from the queue.
                    if len(queue) != 0:
                        choice = queue[0]
                        queue.pop(0)
                        # Tell user automated command is being run.
                        if choice != 'y':
                            editor.print('Running automated return command...')
                        else:
                            editor.print('Running automated command y...')
                    # Otherwise, prompt the user.
                    else:
                        choice = input('Enter y to continue and anything else to abort: ')
                    # Display confirmation for overwriting.
                    if choice == 'y':
                        editor.log('Currently stored time histogram overwritten.\n')
                    # Display confirmation for cancel.
                    else:
                        editor.print('Cancelling overwrite...\n')
                        selection = 'blank'
                # If generation hasn't been canceled:
                if selection != 'blank':
                    # Display progress.
                    editor.print('Creating new histogram...')
                    # Plot the histogram.
                    analyzer.plotSplit(editor.parameters.settings)
                    # Display success.
                    editor.log('New histogram created.\n')
            # Create a line of best fit for the histogram:
            else:
                # If line is already stored:
                if analyzer.RABestFit['Best fit'] is not None:
                    # Warn user of overwrite.
                    editor.print('WARNING: There is an already stored best fit line '
                        + 'in this runtime. Do you want to overwrite it?')
                    # If there's currently something in the command queue, 
                    # take that as the input and remove it from the queue.
                    if len(queue) != 0:
                        choice = queue[0]
                        queue.pop(0)
                        # Tell user automated command is being run.
                        if choice != 'y':
                            editor.print('Running automated return command...')
                        else:
                            editor.print('Running automated command y...')
                    # Otherwise, prompt the user.
                    else:
                        choice = input('Enter y to continue and anything else to abort: ')
                    # Display confirmation for overwriting.
                    if choice == 'y':
                        editor.log('Currently stored best fit line overwritten.\n')
                    # Display confirmation for cancel.
                    else:
                        editor.print('Cancelling overwrite...\n')
                        selection = 'blank'
                # If fitting hasn't been canceled:
                if selection != 'blank':
                    # Display progress.
                    editor.print('Creating new best fit and residual...')
                    # Split on the best fit.
                    analyzer.fitSplit(editor.parameters.settings, name.count('.') == 0)
                    # Display success.
                    editor.log('New best fit and residual created.\n')
        # View and/or edit program settings.
        elif selection == 's':
            editor.print('')
            queue = editor.driver(queue)
        # Return to the main menu.
        elif selection == '' or selection == 'x':
            editor.print('Returning to main menu...\n')
        # Catchall for invalid commands.
        else:
            print('ERROR: Unrecognized command ' + selection
                  + '. Please review the list of appriopriate inputs.\n')          
    return editor, queue