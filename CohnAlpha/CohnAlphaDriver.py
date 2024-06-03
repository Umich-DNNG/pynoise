# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 11:42:16 2023

@author: 357375
"""


import editor as edit
import analyze as alz
import os


editor: edit.Editor = None
analyzer = alz.Analyzer()


def main(editorIn: edit.Editor, queue: list[str]):
    global editor
    editor = editorIn
    selection = 'blank'
    editor.print('You are running the Cohn Alpha Method.')
    while selection != '' and selection != 'x':
        # print commands
        # check automated queue, run any automated commands if exists
        # else ask for user selection
        editor.print('You can utilize any of the following functions:')
        editor.print('m - run the entire program through the main driver')
        editor.print('p - plot histogram of provided time data')
        editor.print('w - perform welch approximation of the fourier transform')
        editor.print('f - fit and plot power spectral density curve')
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

        CA_Object = None
        overwrite = True

        # if running analysis and not changing settings, then ensure that the input file path is valid
        # if not valid then lock user here unless changing settings
        if (selection != 's' and not os.path.isfile(editor.parameters.settings['Input/Output Settings']['Input file/folder'])
            and not os.path.isdir(editor.parameters.settings['Input/Output Settings']['Input file/folder'])):
                    editor.print('ERROR: You currently have no input file or folder defined. '
                          + 'Please make sure to specify one before running any analysis.\n')
                    continue
        
        match selection:
            # Run entire Cohn-Alpha method
            case 'm':
                    editor.print('\nRunning the entire Cohn Alpha analysis...')
                    analyzer.conductCohnAlpha(editor.parameters.settings)
                    editor.log('Ran the entire Cohn Alpha on file ' 
                                + editor.parameters.settings['Input/Output Settings']['Input file/folder'] 
                                + '.\n')
            # Plot Counts Histogram
            case 'p':
                # If generated histogram is found, ask users if willing to overwrite
                # Otherwise generate Histogram and save Histogram in analyzer.CohnAlpha dict
                if analyzer.CohnAlpha['Histogram'] != []:
                    # Ask user if willing to overwrite histogram that exists in memory
                    editor.print('WARNING: There is an already stored histogram '
                        + 'in this runtime. Do you want to erase it?')
                    editor.print('If not erasing, the program will simply display the histogram in memory')

                    auto = input('Enter y to continue and anything else to display: ')
                    if auto == 'y':
                        editor.log('Currently stored time histogram erased.')
                        overwrite = True
                    else:
                        editor.print('Cancelling overwrite...')
                        editor.print('Displaying Histogram')
                        overwrite = False
                if selection == 'p':
                    editor.print('\nPlotting the Cohn Alpha Histogram...')
                    analyzer.plotCohnAlphaHist(settings=editor.parameters.settings, overwrite=overwrite)
                    editor.log('Generated Cohn Alpha Histogram on file '
                            + editor.parameters.settings['Input/Output Settings']['Input file/folder'] 
                            + '.\n')
            # Apply Welch Approximation of Fourier Transformation
            # If no histogram in memory, will generate ahead of time
            case 'w':
                    editor.print('Applying the Welch Approximation...')
                    analyzer.applyWelchApprox(settings=editor.parameters.settings)

                    editor.log('Calculated alpha and uncertainty value on '
                            + editor.parameters.settings['Input/Output Settings']['Input file/folder'] 
                            + '.\n')
            case 'f':
                    editor.print('Fitting Power Spectral Density Curve...')
                    analyzer.fitPSDCurve(settings=editor.parameters.settings)
                    editor.log('')
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


def helperAutoFunc(queue, editor, selection):
    # If there's currently something in the command queue, 
    # take that as the input and remove it from the queue.
    if len(queue) != 0:
        auto = queue[0]
        queue.pop(0)
        if auto != 'y':
            editor.print('Running automated return command...')
        else:
            editor.print('Running automated command y...')

    # Otherwise, prompt the user.
    # Display confirmation for overwriting and for cancel
    else:
        auto = input('Enter y to continue and anything else to abort: ')
    if auto == 'y':
        editor.log('Currently stored time histogram erased.')
        selection = 'p'
    else:
        editor.print('Cancelling overwrite...')
        selection = 'blank'