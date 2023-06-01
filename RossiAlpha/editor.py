'''The program that interacts with the settings object.'''

import settings as set
import os
import time
from subprocess import call

class Editor:

    def __init__(self):
        self.parameters = set.Settings()
        self.history = None
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

    def log(self, output):

        '''Prints the output statement to the command line 
        and saves it to the log if logs are enabled.
        
        The output statement must be a string.'''

        # Print the confirmation statement to the 
        # console regardless of log preferences.
        print(output)
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
        if self.parameters.get('Input/Output Settings','Keep logs') and self.history is None:
            # Get local time.
            curTime = time.localtime()
            # Create log file name with relative path and timestamp.
            logName = ('../.logs/' + str(curTime.tm_year) 
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
        elif not self.parameters.get('Input/Output Settings','Keep logs') and self.history is not None:
            # Close file.
            self.history.close()
            # Delete file.
            os.remove(self.history.name)
            # Reset history variable.
            self.history = None

    def driver(self):

        '''The driver that opens the settings vim for editing.'''

        EDITOR = os.environ.get('EDITOR', 'vim')
        choice = 'blank'
        file = ''
        while choice != '' and choice != 'c' and choice != 'o' and choice != 'n':
            print('What settings do you want to edit/view?')
            print('c - current settings')
            print('o - other .set file')
            print('n - new settings')
            print('Leave the command blank to cancel editing/viewing.')
            choice = input('Enter command: ')
            match choice:
                case 'c':
                    print('Opening current settings...')
                    file = 'current.set'
                    self.parameters.write(os.path.abspath(file),
                                          'The current settings during runtime.\n'
                                          + 'This file is temporary and will be '
                                          + 'deleted after editing is done.\n')
                case 'o':
                    while not os.path.isfile(os.path.abspath(file)):
                        file = input('Enter a settings file (no .set extension): ')
                        file = file + '.set'
                        if os.path.isfile(os.path.abspath(file)):
                            print('Opening ' + file + '...')
                        else:
                            print('ERROR: ' + file + ' does not exist in this directory. '
                                  + 'Make sure that your settings file is named '
                                  + 'correctly and in the same folder as this program.\n')
                case 'n':
                    print('Opening new settings...')
                    file = 'new.set'
                    blank = set.Settings()
                    blank.write(os.path.abspath(file),
                                'A new settings file.\n'
                                + 'This file is temporary and will be '
                                + 'deleted after editing is done.\n')
                case '':
                    print('Returning to previous menu...')
                case _:
                    print('Unrecognized command. Please review the list of appriopriate inputs.\n')

        with open(os.path.abspath(file),'a') as settings:
            call([EDITOR, settings.name])
        self.parameters.read(os.path.abspath(file))
        self.changeLog()
        if file == 'new.set' or file == 'current.set':
            os.remove(os.path.abspath(file))