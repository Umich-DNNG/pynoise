'''The program that interacts with the settings object.'''



# Necessary imports.
import settings as set
import os
import time
from subprocess import call



class Editor:

    '''The class that runs terminal mode 
    settings editing, log keeping, and printing.'''


    def __init__(self):

        '''The initializer for the Editor class.'''


        # Create a blank settings object, blank log path, and 
        # gets the working directory for making absolute paths.
        self.parameters = set.Settings()
        self.history = None
        os.chdir(os.path.dirname(os.path.realpath(__file__)))



    def print(self, message: str):

        '''Prints a string if quiet mode is off. Otherwise, does nothng.
        
        Inputs:
        - message: the string message to print.'''


        # If not in quiet mode, print the message.
        if not self.parameters.settings['Input/Output Settings']['Quiet mode']:
            print(message)



    def log(self, output: str):

        '''Prints the output statement to the command line 
        and saves it to the log if logs are enabled.
        
        Inputs:
        - output: the string statement to be logged.'''


        # Print the confirmation statement to the 
        # console if the user is not in quiet mode.
        self.print(output)
        # If log file exists, record this confirmation.
        if self.history is not None:
            # Create a timestamp for the confirmation message.
            curTime = time.localtime()
            output = (str(curTime.tm_year) 
            + '-' + str(curTime.tm_mon) 
            + '-' + str(curTime.tm_mday) 
            + ' @ ' + str(curTime.tm_hour) 
            + (':0' if curTime.tm_min < 10 else ':') + str(curTime.tm_min) 
            + (':0' if curTime.tm_sec < 10 else ':') + str(curTime.tm_sec) 
            + ' - ' + output)
            # Write the confirmation + timestamp to the file and flush 
            # immediately so user can see log updates in real time.
            self.history.write(output)
            self.history.flush()



    def changeLog(self):

        '''Change the current use of the log file.
        
        If setting changed:
        * True -> False - close log file and delete it.
        * False -> True - create/open new log file named with current timestamp.
        * True -> True - does nothing (prevents recreation of log file).
        * False -> False - does nothing (prevents closing/deletion of nonexistent file).'''


        # If user wants to keep logs and one is not already open.
        if self.parameters.settings['Input/Output Settings']['Keep logs'] and self.history is None:
            # Get local time.
            curTime = time.localtime()
            # Create log file name with relative path and timestamp.
            logName = ('./logs/' + str(curTime.tm_year) 
                        + '-' + str(curTime.tm_mon) 
                        + '-' + str(curTime.tm_mday) 
                        + '@' + str(curTime.tm_hour) 
                        + (':0' if curTime.tm_min < 10 else ':') + str(curTime.tm_min) 
                        + (':0' if curTime.tm_sec < 10 else ':') + str(curTime.tm_sec) 
                        + '.log')
            # Convert relative path into absolute path.
            logName = os.path.abspath(logName)
            # Create and open a log file with writing priveleges.
            self.history = open(logName,'w')
        # If user does not want logs and one is currently open.
        elif not self.parameters.settings['Input/Output Settings']['Keep logs'] and self.history is not None:
            # Close file.
            self.history.close()
            # Delete file.
            os.remove(self.history.name)
            # Reset history variable.
            self.history = None



    def edit(self, file: str):

        '''The function that allows the user to edit settings 
        in a vim and save them to runtime afterwards.
        
        Inputs:
        - file: the string of the absolute path of the .json file being 
        opened. The only files that should be edited in the vim are 
        current and new settings (current.json and append.json respectively).'''


        # Create an editor using the os environ function.
        EDITOR = os.environ.get('EDITOR', 'vim')
        # Open the file in append mode.
        with open(file,'a') as settings:
            # If appending settings, prefill the file.
            if file == os.path.abspath('settings/append.json'):
                settings.write('{\n\t"Input/Output Settings": {\n\t\t\n\t},\n')
                settings.write('\t"General Settings": {\n\t\t\n\t},\n')
                settings.write('\t"RossiAlpha Settings": {\n\t\t\n\t},\n')
                settings.write('\t"CohnAlpha Settings": {\n\t\t\n\t},\n')
                settings.write('\t"Semilog Plot Settings": {\n\t\t\n\t},\n')
                settings.write('\t"FeynmanY Settings": {\n\t\t\n\t},\n')
                settings.write('\t"Histogram Visual Settings": {\n\t\t\n\t},\n')
                settings.write('\t"Line Fitting Settings": {\n\t\t\n\t},\n')
                settings.write('\t"Scatter Plot Settings": {\n\t\t\n\t}\n}')
                settings.flush()
            # Call the editor.
            call([EDITOR, settings.name])
        settings.close()
        # Create a temp file to compare the 
        # edited settings to the previous ones.
        self.parameters.write(os.path.abspath('settings/comp.json'))
        # If in append mode, append the settings.
        if file == os.path.abspath('settings/append.json'):
            self.parameters.append(file)
        # If in overwrite mode, overwrite the entire settings.
        else:
            self.parameters.read(file)
        # Change the log state.
        self.changeLog()
        # Notify the user the settings editing is complete.
        self.print('Settings viewer/editor closed.\n')
        # Check to see if the settings have changed from the latest import.
        changes = self.parameters.compare(True)
        # If there are changes, log each one.
        for message in changes:
            self.log(message)
        # Delete the temporary file.
        os.remove(file)



    def driver(self, queue:list[str] = []):

        '''The driver that manages the settings vim for editing/viewing.
        
        Inputs:
        - queue: the list of prefilled commands. 
        If not given, assumes an empty queue.
        
        Outputs:
        - the remaining queue after runtime.'''


        # Initialize the user input variables.
        choice = 'blank'
        file = ''
        # Keep looping until user is done editing/viewing.
        while choice != '' and choice != 'x':
            # Display options.
            self.print('What settings do you want to edit/view?')
            self.print('c - current settings')
            self.print('i - import a .json file')
            self.print('a - append settings')
            self.print('Leave the command blank or enter x to cancel editing/viewing.')
            # If there's currently something in the command queue, 
            # take that as the input and remove it from the queue.
            if len(queue) != 0:
                choice = queue[0]
                queue.pop(0)
                # Tell user automated command is being run.
                if choice == '' or choice == 'x':
                    self.print('Running automated return command...')
                else:
                    self.print('Running automated command ' + choice + '...')
            # Otherwise, prompt the user.
            else:
                choice = input('Enter command: ')
            match choice:
                # User wants to view/edit current settings.
                case 'c':
                    # Display progress.
                    self.print('Opening current settings...')
                    # Create temporary current.json file to edit.
                    file = 'settings/current.json'
                    # Write current settings to temp file.
                    self.parameters.write(os.path.abspath(file))
                    # Open the settings editor.
                    self.edit(os.path.abspath(file))
                # User wants to import settings from a file.
                case 'i':
                    # Initialize the user input variables.
                    file = 'blank'
                    opt = 'blank'
                    # Keep looping until valid command or user cancels.
                    while opt != '' and opt != 'o' and opt != 'a':
                        # Display options.
                        self.print('You have two input options:')
                        self.print('o - overwrite the entire settings')
                        self.print('a - append settings')
                        # If there's currently something in the command queue, 
                        # take that as the input and remove it from the queue.
                        if len(queue) != 0:
                            opt = queue[0]
                            queue.pop(0)
                            # Tell user automated command is being run.
                            if opt == '' or opt == 'x':
                                self.print('Running automated return command...')
                            else:
                                self.print('Running automated command ' + opt + '...')
                        # Otherwise, prompt the user.
                        else:
                            opt = input('Enter a command (or leave blank to cancel): ')   
                        match opt:
                            # User chooses overwrite mode.
                            case 'o':
                                self.print('Overwrite mode selected.')
                            # User chooses append mode.
                            case 'a':
                                self.print('Append mode selected.')
                            # User cancels file import.
                            case '':
                                self.print('Canceling import...\n')
                            # Catchall for invalid commands.
                            case _:
                                print('ERROR: Unrecognized command ' + opt 
                                        + '. Please review the list of appriopriate inputs.\n')
                    # Keep prompting the user until they 
                    # give an existing file or they cancel.
                    while opt != '' and not os.path.isfile(os.path.abspath(file)) and file != '.json':
                        # If there's currently something in the command queue, 
                        # take that as the input and remove it from the queue.
                        if len(queue) != 0:
                            file = queue[0]
                            queue.pop(0)
                            # Tell user automated command is being run.
                            if file == '':
                                self.print('Running automated return command...')
                            else:
                                self.print('Using automated file ' + file + '...')
                        # Otherwise, prompt the user.
                        else:
                            file = input('Enter a settings file (no .json '
                                     + 'extension) or leave blank to cancel: ')
                        # Add .json extension.
                        file = file + '.json'
                        # If file exists.
                        if os.path.isfile(os.path.abspath(file)):
                            # Display progress.
                            self.print('Importing ' + file + '...')
                            # Overwrite all settings.
                            if opt == 'o':
                                self.parameters.read(os.path.abspath(file))
                                self.changeLog()
                                self.log('Imported settings from ' + file + '.\n')
                            # Append settings in file.
                            else:
                                self.parameters.append(os.path.abspath(file))
                                self.changeLog()
                                self.log('Appended settings from ' + file + '.\n')
                        # User cancels import.
                        elif file == '.json':
                            self.print('Canceling import...\n')
                        # Catchall for invalid files.
                        else:
                            print('ERROR: ' + file + ' does not exist in the given directory. '
                              + 'Make sure that your settings file is named correctly, '
                              + 'the correct absolute/relative path to it is given, and '
                              + 'you did not include the .json extenstion in your input.\n')
                # User wants to create entirely new settings.
                case 'a':
                    self.print('Opening empty settings...')
                    # Create temporary new.json file to edit.
                    file = 'settings/append.json'
                    # Open the settings editor.
                    self.edit(os.path.abspath(file))
                # User is ready to return to the main menu.
                case '':
                    self.print('Returning to previous menu...\n')
                case 'x':
                    self.print('Returning to previous menu...\n')
                # Catchall for invalid commands.
                case _:
                    print('ERROR: Unrecognized command ' + choice 
                        + '. Please review the list of appriopriate inputs.\n')
        # Return the remaining queue.
        return queue