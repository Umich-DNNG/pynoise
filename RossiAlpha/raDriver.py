'''The command line driver for running Rossi Alpha analysis.'''



# Necessary imports.
import editor as edit
import analyze as alz
import os



# The global object.
analyzer = alz.Analyzer()

from . import rossiAlpha as ra
ra = ra.RossiAlpha()


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

            # Ensure there is a valid input file/folder
            if (not os.path.isfile(editor.parameters.settings['Input/Output Settings']['Input file/folder'])
            and not os.path.isdir(editor.parameters.settings['Input/Output Settings']['Input file/folder'])):
                print('ERROR: You currently have no input file or '
                      + 'folder defined or the specified input file/'
                      + 'directory does not exist. Please make sure '
                      + 'to adjust this before running any analysis.\n')
                selection = 'blank'
                continue

            # if no save directory is specified, use the input folder or the file's parent folder
            if editor.parameters.settings['Input/Output Settings']['Save directory'] is None:
                # if input is a folder, set save directory to it
                if name.count('.') == 0:
                    editor.parameters.settings['Input/Output Settings']['Save directory'] = editor.parameters.settings['Input/Output Settings']['Input file/folder']
                # else, set the save directory to the input's parent folder
                else:
                    editor.parameters.settings['Input/Output Settings']['Save directory'] = (editor.parameters.settings['Input/Output Settings']['Input file/folder']
                                                                                             [:editor.parameters.settings['Input/Output Settings']['Input file/folder'].rfind('/')])
            
            # Perform various error checks
            
            # Ensure the user is ONLY using 'aa' time difference method for a file if no channel column is specified
            if (editor.parameters.settings['RossiAlpha Settings']['Time difference method'] != 'aa' 
                and editor.parameters.settings['RossiAlpha Settings']['Time difference method'] != ['aa']
                and editor.parameters.settings['Input/Output Settings']['Channels column'] == None
                and name.count('.') > 0):
                print('ERROR: When using methods other than any and all for a file analysis, you must specify a channels column.\n')
                selection = 'blank'
                continue
            # if is a folder and the number of folders is specified, it must be more than one folder
            if (name.count('.') == 0 and editor.parameters.settings["General Settings"]["Number of folders"] != None 
                and editor.parameters.settings["General Settings"]["Number of folders"] <= 1):
                print('ERROR: Running RossiAlpha method on a folder of folders requires either more' 
                    + ' than one folder specified or \"null\" for the setting.\n')
                selection = 'blank'
                continue
            # If input is a file and the bin width is not specified for anything other than computing time differences
            if (name.count('.') > 0 and editor.parameters.settings['RossiAlpha Settings']['Bin width'] == None
                and (selection == 'm' or selection == 'f' or selection == 'p')):
                print('ERROR: Using RossiAlpha on a file to generate plots of the time difference data and/or'
                    + ' fit the data to an exponetial curve requires the bin width to be specified.\n')
                selection = 'blank'
                continue

            # For full analysis:
            if selection == 'm':
                # Error check: if input is a file and the bin width is not specified
                if name.count('.') > 0 and editor.parameters.settings['RossiAlpha Settings']['Bin width'] == None:
                    print('ERROR: Using RossiAlpha on a file to generate plots of the time difference data and/or'
                        + ' fit the data to an exponetial curve requires the bin width to be specified.\n')
                    selection = 'blank'
                    continue

                editor.print('Running the entire RossiAlpha method...')
                # Split on the best fit. TODO: create a function to specialize for full analysis
                successful = ra.driveFit(editor.parameters.settings, (name.count('.') == 0))
                if successful:
                    if (name.count('.') == 0):
                        editor.log('Ran the entire RossiAlpha method on folder ' 
                            + editor.parameters.settings['Input/Output Settings']['Input file/folder'] 
                            + '.\n')
                    else:
                        editor.log('Ran the entire RossiAlpha method on file ' 
                            + editor.parameters.settings['Input/Output Settings']['Input file/folder'] 
                            + '.\n')
                        
            # For time difference calculation:
            elif selection == 't':
                editor.print('Creating new time differences...')
                successful = ra.driveTimeDifs(editor.parameters.settings, (name.count('.') == 0))
                if successful:
                    editor.log('New time differences created.\n')

            # Make a histogram of the time differences.
            elif selection == 'p':
                editor.print('Creating new histogram...')
                successful = ra.drivePlots(editor.parameters.settings, (name.count('.') == 0))
                if successful: 
                    editor.log('New histogram created.\n')

            # Create a line of best fit for the histogram:
            else:
                # Error check: if input is a file and the bin width is not specified
                if name.count('.') > 0 and editor.parameters.settings['RossiAlpha Settings']['Bin width'] == None:
                    print('ERROR: Using RossiAlpha on a file to generate plots of the time difference data and/or'
                        + ' fit the data to an exponetial curve requires the bin width to be specified.\n')
                    selection = 'blank'
                    continue

                editor.print('Creating new best fit and residual...')
                successful = ra.driveFit(editor.parameters.settings, (name.count('.') == 0))
                if successful:
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