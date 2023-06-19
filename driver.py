'''The main file that should be run each time the user wants to use this Python Suite.'''

import editor as edit
from RossiAlpha import raDriver as ra
from PowerSpectralDensity import psdDriver as psd
import os
import sys

# The editor class that contains the settings and settings editor.
editor = edit.Editor()

# Set the current working directory for assigning absolute paths.
os.chdir(os.path.dirname(os.path.realpath(__file__)))

def main():

    '''The main driver that runs the whole program.'''

    global editor
    selection = 'blank'
    queue = []
    while len(sys.argv) > 1:
        if sys.argv[1].count('.') > 0:
            file = open(os.path.abspath(sys.argv[1]))
            commands = file.read()
            while commands.find('\n') != -1:
                entry = commands[0:commands.find('\n')]
                commands = commands[commands.find('\n')+1:]
                queue.append(entry)
            queue.append(commands)
        else:
            queue.append(sys.argv[1])
        sys.argv.pop(1)
    print('Welcome to the DNNG/PyNoise project. With this software we are '
          + 'taking radiation data from fission reactions (recorded by organic '
          + 'scintillators) and applying a line of best fit to the decay rate. '
          + 'Use this Python suite to analyze a single file or multiple across '
          + 'numerous folders.\n')
    # Continue looping until the user has selected an import option.
    while selection != 'd' and selection != 'i':
        print('Would you like to use the default settings or import another .json file?')
        print('d - use default settings')
        print('i - import custom settings')
        if len(queue) != 0:
            selection = queue[0]
            queue.pop(0)
        else:
            selection = input('Select settings choice: ')
        match selection:
            # Import the default settings.
            case 'd':
                print()
                print('Initializing program with default settings...')
                # Create absolute path for the default settings file and read it in.
                path = os.path.abspath('default.json')
                editor.parameters.read(path)
                editor.changeLog()
                editor.log('Settings from default.json succesfully imported.\n')
            # Import custom settings.
            case 'i':
                file = ''
                choice = 'blank'
                opt = 'blank'
                while opt != '' and opt != 'o' and opt != 'a':
                    print('\nYou have two import options:')
                    print('o - overwrite entire settings')
                    print('a - append settings to default')
                    if len(queue) != 0:
                        opt = queue[0]
                        queue.pop(0)
                    else:
                        opt = input('Enter a command (or leave blank to cancel): ')
                    match opt:
                        case 'o':
                            print('Overwrite mode selected.')
                        case 'a':
                            print('Append mode selected.')
                        case '':
                            print('Canceling import...\n')
                            selection = ''
                        case _:
                            print('Unrecognized command. Please review the list of appriopriate inputs.')
                while opt != '' and not os.path.isfile(os.path.abspath(file)) and file != '.json':
                    if len(queue) != 0:
                        file = queue[0]
                        queue.pop(0)
                    else:
                        file = input('Enter a settings file (no .json extension): ')
                    file = file + '.json'
                    if os.path.isfile(os.path.abspath(file)):
                        print('Importing settings from ' + file + '...')
                        if opt == 'a':
                            editor.parameters.read(os.path.abspath('default.json'))
                            editor.parameters.append(os.path.abspath(file))
                            editor.changeLog()
                            editor.log('Settings from ' + file + ' succesfully'
                                       + ' appended to the default.\n')
                        else:
                            editor.parameters.read(os.path.abspath(file))
                            editor.changeLog()
                            editor.log('Settings from ' + file + ' succesfully imported.\n')
                    elif file == '.json':
                        print('Canceling import...\n')
                        selection = ''
                    else:
                        print('ERROR: ' + file + ' does not exist in the given directory. '
                              + 'Make sure that your settings file is named correctly, '
                              + 'the correct absolute/relative path to it is given, and '
                              + 'you did not include the .json extenstion in your input.\n')
            # Catchall for invalid commands.
            case _:
                print('You must choose what settings to import.\n')
    print('Settings initialized. You can now begin using the program.\n')
    print('----------------------------------------------------------\n')
    # Continue running the program until the user is done.
    while selection != '':
        print('You can utitilze any of the following functions:')
        print('r - run Rossi Alpha analysis')
        print('p - run Power Spectral Density Analysis')
        print('s - view or edit the program settings')
        print('Leave the command blank or enter x to end the program.')
        if len(queue) != 0:
            selection = queue[0]
            queue.pop(0)
        else:
            selection = input('Enter a command: ')
        match selection:
            # Run RossiAlpha analysis.
            case 'r':
                print()
                editor, queue = ra.main(editor, queue)
            case 'p':
                print()
                editor, queue = psd.main(editor, queue)
            # View and/or edit program settings.
            case 's':
                print()
                queue = editor.driver(queue)
            # End the program.
            case '':
                print('\nAre you sure you want to quit the program?')
                if len(queue) != 0:
                    choice = queue[0]
                    queue.pop(0)
                else:
                    choice = input('Enter q to quit and anything else to abort: ')
                # Confirm quit command.
                if choice == 'q':
                    print('Ending program...\n')
                # Catchall for user canceling shutdown.
                else:
                    print('Quit aborted.\n')
                    selection = 'blank'
            case 'x':
                print('\nAre you sure you want to quit the program?')
                if len(queue) != 0:
                    choice = queue[0]
                    queue.pop(0)
                else:
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
    if editor.parameters.changed:
        selection = ''
        # Continue looping until the user has decided what to do with their changes.
        while selection != 'd' and selection != 'n' and selection != 'a':
            print('It appears you have made unsaved changes to the '
              + 'settings. Do you want to save your changes?')
            print('d - save current settings as the default')
            print('n - save current settings as a new settings file')
            print('a - abandon current settings')
            if len(queue) != 0:
                selection = queue[0]
                queue.pop(0)
            else:
                selection = input('Select an option: ')
            match selection:
                # User wants to overwrite the defualt settings.
                case 'd':
                    print('This will overwrite the current default settings. Are you sure you want to do this?')
                    if len(queue) != 0:
                        choice = queue[0]
                        queue.pop(0)
                    else:
                        choice = input('Enter y to continue and anything else to abort: ')
                    # Confirm user wants to overwrite.
                    if choice == 'y':
                        # Create an absolute path for the default settings
                        # file and write the current settings into it.
                        path = os.path.abspath('default.json')
                        print('Overwriting default settings...')
                        editor.parameters.write(path)
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
                        print('Enter a name for the new settings (not including the .json file extension).')
                        if len(queue) != 0:
                            file = queue[0]
                            queue.pop(0)
                        else:
                            file  = input('Name of file (or blank to cancel): ')
                        if file != '':
                            # Create absolute path for user given file.
                            file = file + '.json'
                            path = os.path.abspath(file)
                            # If settings file already exists, check that user 
                            # wants to overwrite settings currently in the file.
                            if os.path.isfile(path):
                                print('WARNING: settings file ' + file + ' already exists.'
                                    + ' Do you want to overwrite the previous stored settings?')
                                if len(queue) != 0:
                                    choice = queue[0]
                                    queue.pop(0)
                                else:
                                    choice = input('Enter y to continue and anything else to abort: ')
                                # If user confirms, overwrite the settings.
                                if choice == 'y':
                                    print('Overwriting ' + file + '...')
                                    editor.parameters.save(path)
                                    editor.log('Settings in ' + file + ' overwritten.\n')
                                # Catchall for user canceling overwrite.
                                else:
                                    print()
                                    path = 'blank'
                            # Otherwise, save with no confirmation needed.
                            else:
                                print('Saving current settings to new file ' + file + '...')
                                editor.parameters.save(path)
                                editor.log('Settings saved to file ' + file + '.\n')
                        else:
                            print()
                            selection = ''
                # User wants to discard changes.
                case 'a':
                    print('WARNING: all your current changes will be lost. Are you sure you want to do this?')
                    if len(queue) != 0:
                        choice = queue[0]
                        queue.pop(0)
                    else:
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