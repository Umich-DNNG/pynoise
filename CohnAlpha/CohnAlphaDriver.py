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
        selection = helperAutoFunc(queue=queue)

        # if running analysis and not changing settings, then ensure that the input file path is valid
        # if input file path is not valid then lock user here unless changing settings or going back
        if (selection != 's' and selection != 'x' and selection != '' 
            and not os.path.isfile(editor.parameters.settings['Input/Output Settings']['Input file/folder'])
            and not os.path.isdir(editor.parameters.settings['Input/Output Settings']['Input file/folder'])):
                    editor.print('ERROR: You currently have no input file/folder defined or the input file/folder cannot be found. '
                          + 'Please ensure input path is correct before running any analysis.\n')
                    continue
        
        overwrite = False
        match selection:
            # Run entire Cohn-Alpha method
            case 'm':
                    editor.print('\nRunning the entire Cohn Alpha analysis...')
                    analyzer.fitPSDCurve(editor.parameters.settings, overwrite=True)
                    editor.log('Ran the entire Cohn Alpha on file ' 
                                + editor.parameters.settings['Input/Output Settings']['Input file/folder'] 
                                + '\n')
            # Plot Counts Histogram
            case 'p':
                # If data exists, ask if user willing to overwrite
                # if overwriting, run function
                # Otherwise, do nothing
                if analyzer.CohnAlpha['Histogram'] != []:
                    overwrite = overwriteHelperFunction(queue=queue, key='Histogram')

                if analyzer.plotCohnAlphaHist(settings=editor.parameters.settings, overwrite=overwrite):
                    editor.log('Generated Cohn Alpha Histogram on file '
                            + editor.parameters.settings['Input/Output Settings']['Input file/folder'] 
                            + '.\n')
            # Apply Welch Approximation of Fourier Transformation
            case 'w':
                # If data exists, ask if user willing to overwrite
                # if overwriting, run function
                # Otherwise, do nothing
                if analyzer.CohnAlpha['Welch Result'] != []:
                    overwrite = overwriteHelperFunction(queue=queue, key='Welch Result')

                if analyzer.applyWelchApprox(settings=editor.parameters.settings, overwrite=overwrite):
                    editor.log('Calculated frequency and power spectral density values on '
                            + editor.parameters.settings['Input/Output Settings']['Input file/folder'] 
                            + '.\n')
            # Fit Power Spectral Density Curve
            case 'f':
                # If data exists, ask if user willing to overwrite
                # if overwriting or no data exists, run function
                # Otherwise, do nothing
                if analyzer.CohnAlpha['PSD Fit Curve'] != []:
                    overwrite = overwriteHelperFunction(queue=queue, key='PSD Fit Curve')

                if analyzer.fitPSDCurve(settings=editor.parameters.settings, overwrite=overwrite):
                    editor.log('Fitted Power Spectral Density Curve on '
                            + editor.parameters.settings['Input/Output Settings']['Input file/folder'] 
                            + '.\n')
                    
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


def helperAutoFunc(queue):
    # If there's currently something in the command queue, 
    # take that as the input and remove it from the queue.
    if len(queue) != 0:
            selection = queue[0]
            queue.pop(0)
            editor.print('Running automated command ' + selection + '...')
    else:
        selection = input('Enter a command: ')

    return selection
            


def overwriteHelperFunction(queue, key:str = ""):

    if 'Histogram' == key:
        displayString = ' There is an already stored histogram '
    elif 'Welch Result' == key:
        displayString = 'There are already stored frequency and power spectral density values '
    elif 'PSD Fit Curve' == key:
        displayString = 'There is an already stored best fit curve '

    if analyzer.CohnAlpha[key] != []:
        editor.print('WARNING: '
            + displayString
            + 'in this runtime. Do you want to overwrite?')
        editor.print('Enter y to continue and anything else to abort')
        
    selection = helperAutoFunc(queue=queue)
    if selection == 'y':
        editor.log('Currently stored data erased.')
        return True
    else:
        editor.print('Cancelling overwrite...')
        return False
    

# TODO: currently showing an image does not work. Need to fix or decide on another idea
# Currently Ssows the plot, but within another plot

# def displayImage():
    # return

    # If generated histogram is found, ask users if willing to overwrite
    # Otherwise generate Histogram and save Histogram in analyzer.CohnAlpha dict
    # if analyzer.CohnAlpha['Histogram'] != []:
    #     # Ask user if willing to overwrite histogram that exists in memory
    #     editor.print('WARNING: There is an already stored histogram '
    #         + 'in this runtime. Do you want to erase it?')
    #     editor.print('If not erasing, the program will simply display the histogram in memory')

    #     auto = input('Enter y to continue and anything else to display: ')
    #     if auto == 'y':
    #         editor.log('Currently stored time histogram erased.')
    #         overwrite = True
    #     else:
    #         editor.print('Cancelling overwrite...')
    #         editor.print('Displaying Histogram')
    #         overwrite = False
    # helperAutoFunc(queue=queue, editor=editor, overwrite=overwrite)