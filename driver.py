'''The main file that should be run each time the user wants to use this Python Suite.'''



# Necessary imports.
import editor as edit
from RossiAlpha import raDriver as ra
from CohnAlpha import CohnAlphaDriver as ca
from FeynmanY import fyDriver as fy
import os
import sys



# Declare the global editor class that contains the 
# settings and settings editor and Set the current 
# working directory for assigning absolute paths.
editor = edit.Editor()
os.chdir(os.path.dirname(os.path.realpath(__file__)))



def main():

    '''The main driver that runs the whole program.'''


    # Use the global editor variable.
    global editor
    # Initialize the user response variable.
    selection = 'blank'
    # Command queue.
    queue = []
    # Try to find the -c command line argument.
    try:
        # If found, store the index of it.
        start = sys.argv.index('-c')
    # If not, try to find the --commands command line argument.
    except ValueError:
        try:
            # If found, store the index of it.
            start = sys.argv.index('--commands')
        # If not, store the index as -1.
        except ValueError:
            start = -1
    # Try to find the -q command line argument.
    try:
        sys.argv.index('-q')
        # If found, set quiet mode to true.
        editor.parameters.settings['Input/Output Settings']['Quiet mode'] = True
    # If not, try to find the --quiet command line argument.
    except ValueError:
        try:
            sys.argv.index('--quiet')
            # If found, set quiet mode to true.
            editor.parameters.settings['Input/Output Settings']['Quiet mode'] = True
        # If not, set quiet mode to false.
        except ValueError:
            editor.parameters.settings['Input/Output Settings']['Quiet mode'] = False
    # If there are program commands, loop through them.
    if start != -1:
        # Skip over --commands/-c.
        start += 1
        # Keep looping until reaching the end of the commands 
        # or reaching another command line argument.
        while start < len(sys.argv) and sys.argv[start].find('-') == -1:
            # If a file is given.
            if sys.argv[start].count('.') > 0:
                # Open the file and read the entire file.
                file = open(os.path.abspath(sys.argv[start]))
                commands = file.read()
                file.close()
                # Keep looping until there are no more newlines.
                while commands.find('\n') != -1:
                    # Isolate the next entry, remove it from the 
                    # list of commands, and add it to the queue.
                    entry = commands[0:commands.find('\n')]
                    commands = commands[commands.find('\n')+1:]
                    queue.append(entry)
                # Append the final command.
                queue.append(commands)
            # Otherwise, assume a raw command is 
            # given and add it to the queue.
            else:
                queue.append(sys.argv[start])
            # Continue to next command.
            start = start + 1
    # Welcome statement.
    editor.print('Welcome to the DNNG/PyNoise project.') 
    editor.print('With this software we are taking radiation data from '
                 + 'fission reactions (recorded by organic scintillators) '
                 + 'and analyzing it using various methods and tools.')
    editor.print('Use this Python suite to analyze a single '
                 + 'file or multiple across numerous folders.\n')
    # Continue looping until the user has selected an import option.
    while selection != 'd' and selection != 'i':
        # Display options.
        editor.print('Would you like to use the default settings or import another .json file?')
        editor.print('d - use default settings')
        editor.print('i - import custom settings')
        # If there's currently something in the command queue, 
        # take that as the input and remove it from the queue.
        if len(queue) != 0:
            selection = queue[0]
            queue.pop(0)
            # Tell user automated command is being run.
            editor.print('Running automated command ' + selection + '...')
        # Otherwise, prompt the user.
        else:
            selection = input('Select settings choice: ')
        match selection:
            # Import the default settings.
            case 'd':
                # Display progress.
                editor.print('\nInitializing program with default settings...')
                # Create absolute path for the default settings file and read it in.
                path = os.path.abspath('./settings/default.json')
                editor.parameters.read(path)
                editor.changeLog()
                # Display confirmation.
                editor.log('Settings from default.json succesfully imported.\n')
            # Import custom settings.
            case 'i':
                # Initialize the user response variables.
                file = ''
                choice = 'blank'
                opt = 'blank'
                # Keep looping until valid command or user cancels.
                while opt != '' and opt != 'x' and opt != 'o' and opt != 'a':
                    # Display options.
                    editor.print('\nYou have two import options:')
                    editor.print('a - append settings to default')
                    editor.print('o - overwrite entire settings')
                    # If there's currently something in the command queue, 
                    # take that as the input and remove it from the queue.
                    if len(queue) != 0:
                        opt = queue[0]
                        queue.pop(0)
                        # Tell user automated command is being run.
                        if opt == '' or opt == 'x':
                            editor.print('Running automated return command...')
                        else:
                            editor.print('Running automated command ' + opt + '...')
                    # Otherwise, prompt the user.
                    else:
                        opt = input('Enter a command (or leave blank to cancel): ')
                    match opt:
                        # User chooses overwrite mode.
                        case 'o':
                            editor.print('Overwrite mode selected.')
                        # User chooses append mode.
                        case 'a':
                            editor.print('Append mode selected.')
                        # User cancels file import.
                        case '':
                            editor.print('Canceling import...\n')
                            selection = ''
                        case 'x':
                            editor.print('Canceling import...\n')
                            selection = ''
                        # Catchall for invalid commands.
                        case _:
                            print('ERROR: Unrecognized command ' + opt 
                                  + '. Please review the list of appriopriate inputs.\n')
                # Keep looping until valid file or user cancels.
                while (opt != '' 
                       and not os.path.isfile(os.path.abspath(file)) 
                       and file != '.json'):
                    # If there's currently something in the command queue, 
                    # take that as the input and remove it from the queue.
                    if len(queue) != 0:
                        file = queue[0]
                        queue.pop(0)
                        # Tell user automated command is being run.
                        if file == '':
                            editor.print('Running automated return command...')
                        else:
                            editor.print('Using automated file ' + file + '.json...')
                    # Otherwise, prompt the user.
                    else:
                        file = input('Enter a settings file (no .json extension): ')
                    # Change directory to settings
                    # Add .json extension.
                    file = './settings/' + file
                    file = file + '.json'
                    file = os.path.abspath(file)
                    # If file exists.
                    if os.path.isfile(file):
                        # Display progress.
                        editor.print('Importing settings from ' + file + '...')
                        # Append settings.
                        if opt == 'a':
                            # Read default settings first to append over.
                            editor.parameters.read(os.path.abspath('./settings/default.json'))
                            # Append changed/removed settings.
                            editor.parameters.append(os.path.abspath(file))
                            editor.changeLog()
                            # Display confirmation.
                            editor.log('Settings from ' + file + ' succesfully'
                                       + ' appended to the default.\n')
                        # Overwrite all settings.
                        else:
                            editor.parameters.read(os.path.abspath(file))
                            editor.changeLog()
                            # Display confirmation.
                            editor.log('Settings from ' + file + ' succesfully imported.\n')
                    # User cancels import.
                    elif file == '.json':
                        editor.print('Canceling import...\n')
                        selection = ''
                    # Catchall for invalid files.
                    else:
                        print('ERROR: ' + file + ' does not exist in the given directory. '
                              + 'Make sure that your settings file is named correctly, '
                              + 'the correct absolute/relative path to it is given, and '
                              + 'you did not include the .json extenstion in your input.\n')
            # Catchall for invalid commands.
            case _:
                print('ERROR: You must choose what settings to import.\n')
    # Display confirmation.
    editor.print('Settings initialized. You can now begin using the program.\n')
    editor.print('----------------------------------------------------------\n')

    # update user's text editor preference
    editor.text_editor = editor.parameters.settings['General Settings']['Text editor']
    
    # Continue running the program until the user is done.
    while selection != '' and selection != 'x':
        # Display options.
        editor.print('You can utitilze any of the following functions:')
        editor.print('r - run Rossi Alpha analysis')
        editor.print('c - run Cohn Alpha Analysis')
        editor.print('f - run Feynman Y Analysis')
        editor.print('s - view or edit the program settings')
        editor.print('Leave the command blank or enter x to end the program.')
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
        match selection:
            # Run RossiAlpha analysis.
            case 'r':
                editor.print('')
                editor, queue = ra.main(editor, queue)
            # Run CohnAlpha analysis.
            case 'c':
                editor.print('')
                editor, queue = ca.main(editor, queue)
            # Run Feynman Y analysis.
            case 'f':
                editor.print('')
                editor, queue = fy.main(editor, queue)
            # View and/or edit program settings.
            case 's':
                editor.print('')
                queue = editor.driver(queue)
            # End the program.
            case '':
                editor.print('\nAre you sure you want to quit the program?')
                # If there's currently something in the command queue, 
                # take that as the input and remove it from the queue.
                if len(queue) != 0:
                    choice = queue[0]
                    queue.pop(0)
                    # Tell user automated command is being run.
                    if choice != 'q':
                        editor.print('Running automated return command...')
                    else:
                        editor.print('Running automated command q...')
                # Otherwise, prompt the user.
                else:
                    choice = input('Enter q to quit and anything else to abort: ')
                # Confirm quit command.
                if choice == 'q':
                    editor.print('Ending program...\n')
                # Catchall for user canceling shutdown.
                else:
                    editor.print('Quit aborted.\n')
                    selection = 'blank'
            case 'x':
                editor.print('\nAre you sure you want to quit the program?')
                # If there's currently something in the command queue, 
                # take that as the input and remove it from the queue.
                if len(queue) != 0:
                    choice = queue[0]
                    queue.pop(0)
                    # Tell user automated command is being run.
                    if choice != 'q':
                        editor.print('Running automated return command...')
                    else:
                        editor.print('Running automated command q...')
                # Otherwise, prompt the user.
                else:
                    choice = input('Enter q to quit and anything else to abort: ')
                # Confirm quit command.
                if choice == 'q':
                    editor.print('Ending program...\n')
                # Catchall for user canceling shutdown.
                else:
                    editor.print('Quit aborted.\n')
                    selection = 'blank'
            # Catchall for invalid commands.
            case _:
                print('ERROR: Unrecognized command ' + selection 
                    + '. Please review the list of appriopriate inputs.\n')
    # Check for changes in the settings.
    list = editor.parameters.compare()
    # If there are changes:
    if len(list) != 0:
        # Initialize user response variable.
        selection = ''
        # Continue looping until the user has decided what to do with their changes.
        while selection != 'd' and selection != 'n' and selection != 'a':
            # Display options and changes.
            editor.print('You have made unsaved changes to the '
              + 'settings:\n')
            editor.print('Base settings: ' + editor.parameters.origin)
            editor.print('Most recently appended settings: ' + (editor.parameters.appended if editor.parameters.appended != None else 'None') + '\n')
            for change in list:
                editor.print(change)
            editor.print('\nDo you want to save your changes?')
            editor.print('d - save current settings as the default')
            editor.print('n - save current settings as a new settings file')
            editor.print('a - abandon current settings')
            # If there's currently something in the command queue, 
            # take that as the input and remove it from the queue.
            if len(queue) != 0:
                selection = queue[0]
                queue.pop(0)
                # Tell user automated command is being run.
                editor.print('Running automated command ' + selection + '...')
            # Otherwise, prompt the user.
            else:
                selection = input('Select an option: ')
            match selection:
                # User wants to overwrite the defualt settings.
                case 'd':
                    editor.print('This will overwrite the current default settings. Are you sure you want to do this?')
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
                    # Confirm user wants to overwrite.
                    if choice == 'y':
                        # Create an absolute path for the default settings
                        # file and write the current settings into it.
                        path = os.path.abspath('./settings/default.json')
                        editor.print('Overwriting default settings...')
                        editor.parameters.write(path)
                        editor.log('Default settings overwritten.\n')
                    # Catchall for user canceling overwrite.
                    else:
                        editor.print('')
                        selection = ''
                # User wants to save settings in a new file.
                case 'n':
                    # Initialize user response variables.
                    path = 'blank'
                    file = 'blank'
                    # Loop until user cancels or the user has created a new settings
                    # file/canceled the overwriting of an existing one.
                    while file != '' and not os.path.isfile(path):
                        editor.print('Enter a name for the new settings (not including the .json file extension).')
                        # If there's currently something in the command queue, 
                        # take that as the input and remove it from the queue.
                        if len(queue) != 0:
                            file = queue[0]
                            queue.pop(0)
                            # Tell user automated command is being run.
                            if file == '':
                                editor.print('Running automated return command...')
                            else:
                                editor.print('Using automated file ' + file + '...')
                        # Otherwise, prompt the user.
                        else:
                            file  = input('Name of file (or blank to cancel): ')
                        # If user doesn't cancel:
                        if file != '':
                            # Create absolute path for user given file.
                            file = file + '.json'
                            path = os.path.abspath(file)
                            # If settings file already exists, check that user 
                            # wants to overwrite settings currently in the file.
                            if os.path.isfile(path):
                                editor.print('WARNING: settings file ' + file + ' already exists.'
                                    + ' Do you want to overwrite the previous stored settings?')
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
                                # If user confirms, overwrite the settings.
                                if choice == 'y':
                                    editor.print('Overwriting ' + file + '...')
                                    editor.parameters.save(path)
                                    editor.log('Settings in ' + file + ' overwritten.\n')
                                # Catchall for user canceling overwrite.
                                else:
                                    editor.print('')
                                    path = 'blank'
                            # Otherwise, save with no confirmation needed.
                            else:
                                editor.print('Saving current settings to new file ' + file + '...')
                                editor.parameters.save(path)
                                editor.log('Settings saved to file ' + file + '.\n')
                        # Otherwise, return to the previous choice.
                        else:
                            editor.print('')
                            selection = ''
                # User wants to discard changes.
                case 'a':
                    editor.print('WARNING: all your current changes will be lost. Are you sure you want to do this?')
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
                    # Confirm user choice.
                    if choice == 'y':
                        editor.log('Discarded the current settings.\n')
                    # Catchall for user canceling.
                    else:
                        editor.print('')
                        selection = ''
                # Catchall for invalid commands.
                case _:
                    print('ERROR: You must choose what to do with your changes.\n')
    # Close the log file if one is open.
    if editor.history is not None:
        editor.history.close()
    # Shutdown message.
    editor.print('Thank you for using the DNNG/PyNoise project.')