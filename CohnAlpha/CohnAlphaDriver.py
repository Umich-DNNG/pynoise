# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 11:42:16 2023

@author: 357375
"""

import editor as edit
import analyze as alz

editor: edit.Editor = None
analyzer = alz.Analyzer()

def main(editorIn: edit.Editor, queue: list[str]):
    global editor
    editor = editorIn
    selection = 'blank'
    editor.print('You are running the Cohn Alpha Method.')
    while selection != '' and selection != 'x':
        editor.print('You can utilize any of the following functions:')
        editor.print('m - run the entire program through the main driver')
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
            case 'm':
                # Get the file name for later use.
                name = editor.parameters.settings['Input/Output Settings']['Input file/folder']
                name = name[name.rfind('/')+1:]
                # if input is file:
                if name.count('.') > 0:
                    if editor.parameters.settings['Input/Output Settings']['Input file/folder'] == 'none':
                        print('ERROR: You currently have no input file or folder defined. '
                            + 'Please make sure to specify one before running any analysis.\n')
                    else:
                        editor.print('\nRunning the entire Cohn Alpha analysis...')
                        analyzer.conductCohnAlpha(editor.parameters.settings['Input/Output Settings']['Input file/folder'],
                                                editor.parameters.settings['Input/Output Settings']['Save directory'],
                                                editor.parameters.settings['General Settings']['Show plots'],
                                                editor.parameters.settings['Input/Output Settings']['Save figures'],
                                                editor.parameters.settings['CohnAlpha Settings'],
                                                editor.parameters.settings['Semilog Plot Settings'],
                                                editor.parameters.settings['Line Fitting Settings'],
                                                editor.parameters.settings['Scatter Plot Settings'])
                        editor.log('Ran the entire Cohn Alpha on file ' 
                                    + editor.parameters.settings['Input/Output Settings']['Input file/folder'] 
                                    + '.\n')
                # if input is a folder:
                else:
                    if editor.parameters.settings['Input/Output Settings']['Input file/folder'] == 'none':
                        print('ERROR: You currently have no input file or folder defined. '
                            + 'Please make sure to specify one before running any analysis.\n')
                    else:
                        editor.print('\nRunning the entire Cohn Alpha analysis with folder...')
                        # TODO: error, Analyzer.cohnAlphaFullFolder takes 2 positional arguments but 9 were given
                        analyzer.cohnAlphaFullFolder(editor.parameters.settings['Input/Output Settings']['Input file/folder'],
                                                editor.parameters.settings['Input/Output Settings']['Save directory'],
                                                editor.parameters.settings['General Settings']['Show plots'],
                                                editor.parameters.settings['Input/Output Settings']['Save figures'],
                                                editor.parameters.settings['CohnAlpha Settings'],
                                                editor.parameters.settings['Semilog Plot Settings'],
                                                editor.parameters.settings['Line Fitting Settings'],
                                                editor.parameters.settings['Scatter Plot Settings'],
                                                editor.parameters.settings)
                        editor.log('Ran the entire Cohn Alpha with folder ' 
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