# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 11:42:16 2023

@author: 357375
"""

import numpy as np
from . import PSD as psd
import editor as edit

editor: edit.Editor = None

def conduct_PSD():
    
    '''Creates PSD plots based on input data.'''

    file_path = editor.parameters.settings['Input/Output Settings']['Input file/folder']

    values = np.loadtxt(file_path, usecols=(0,3), max_rows=2000000, dtype=float)

    PSD_Object = psd.PowerSpectralDensity(list_data_array=values, 
                                          leg_label=editor.parameters.settings['PSD Settings']['Legend Label'], 
                                          clean_pulses_switch=editor.parameters.settings['PSD Settings']['Clean pulses switch'], 
                                          dwell_time=editor.parameters.settings['PSD Settings']['Dwell time'], 
                                          meas_time_range=editor.parameters.settings['PSD Settings']['Meas time range'])
    
    
    PSD_Object.conduct_APSD(show_plot=editor.parameters.settings['General Settings']['Show plots'], 
                            save_fig=editor.parameters.settings['General Settings']['Save figures'],
                            save_dir=editor.parameters.settings['Input/Output Settings']['Save directory'],
                            annotate_font_weight=editor.parameters.settings['PSD Settings']['Annotation Font Weight'],
                            annotate_color=editor.parameters.settings['PSD Settings']['Annotation Color'],
                            annotate_background_color=editor.parameters.settings['PSD Settings']['Annotation Background Color'])


def main(editorIn: edit.Editor, queue: list[str]):
    global editor
    editor = editorIn
    selection = 'blank'
    editor.print('You are running the Power Spectral Density Method.')
    while selection != '' and selection != 'x':
        editor.print('You can utilize any of the following functions:')
        editor.print('m - run the entire program through the main driver')
        '''
        editor.print('p - plot the data')
        editor.print('f - fit the data to a curve')
        '''
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
                if editor.parameters.settings['Input/Output Settings']['Input file/folder'] == 'none':
                    print('ERROR: You currently have no input file or folder defined. '
                          + 'Please make sure to specify one before running any analysis.\n')
                else:
                    editor.print('\nRunning the entire power spectral density analysis...')
                    conduct_PSD()
                    editor.log('Ran the entire RossiAlpha method on file ' 
                                + editor.parameters.settings['Input/Output Settings']['Input file/folder'] 
                                + '.\n')
                '''
            case 'p':
                editor.print('')
                editor.print('Plotting the data...')
            case 'f':
                editor.print('')
                editor.print('Fitting the data...')
                '''
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
