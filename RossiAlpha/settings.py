'''The file that contains the Settings class for storing and modifying the program settings.'''

import os

# Set the current working directory for assigning absolute paths.
os.chdir(os.path.dirname(os.path.realpath(__file__)))

class Settings:

    def __init__(self):

        '''The initializer for a Settings object. The object is initialized 
        with blank/empty values.'''
        
        # Create a dictionary that stores each group of settings,
        # and set each one to the respective input dictionary.
        self.settings = {'Input/Output Settings': {'Input type':0,
                                                   'Input file/folder':'',
                                                   'Save directory':'',
                                                   'Keep logs':False},
                         'General Settings': {'Fit range':[0,0],
                                              'Plot scale':'',
                                              'Time difference method':'',
                                              'Digital delay':0,
                                              'Number of folders':0,
                                              'Meas time per folder':0,
                                              'Sort data?':False,
                                              'Save figures?':False,
                                              'Show plots?':False
                                              },
                         'Histogram Generation Settings': {'Reset time':0,
                                                           'Bin width':0,
                                                           'Minimum cutoff':0},
                         'Histogram Visual Settings': {},
                         'Line Fitting Settings': {},
                         'Residual Plot Settings': {}
        }
        # The variable that indicates whether or not the
        # settings have been changed during runtime.
        self.origin = ''
        changed = False

    def isFloat(self, input):

        '''Checks whether or not the input string can be converted to a float.'''

        try:
            float(input)
            return True
        except ValueError:
            return False

    def parseType(self, input):

        '''Converts a string into the detected variable type.
        
        Accepted types:
        * int
        * bool
        * float
        * string
        * list (no nested loops)'''

        if input == '' or input is None:
            return ''
        elif input[0] == '[':
            response = []
            input = input[1:len(input)-1]
            while input.count(',') > 0:
                while input[0] == ' ':
                    input = input[1:]
                response.append(self.parseType(input[0:input.find(',')]))
                input = input[input.find(',')+1:]
            response.append(self.parseType(input))
            return response
        elif input == 'True':
            return True
        elif input == 'False':
            return False
        # If value is numeric, store as integer.
        elif input.isnumeric():
            return int(input)
        # If value is a float, store as float.
        elif self.isFloat(input):
            return float(input)
        # Otherwise, store as a string.
        else:
            return input

    def readGroup(self, group, f):

        '''Reads the settings for a plot (Histogram Visual, Line
        Fitting, Residual Plot) in from a .set file. Requires a
        file object and which type of plot this is for.
        
        Assumes the group and file object are correct (no error checking).'''

        # Clear all settings currently in the group.
        self.settings[group] = {}
        # Get the first setting for the plot.
        f.readline()
        line = f.readline().replace('\n','')
        # Continue looping while the input isn't a dashed line.
        while line[0] != '#':
            # Find the : and store the setting name and value accordingly.
            split = line.find(':')
            setting = line[:split]
            value = line[split+2:]
            # If value is boolean, store as bool.
            self.settings[group][setting] = self.parseType(value)
            # Read the next setting.
            line = f.readline().replace('\n','')

    def read(self, path):

        '''The function that reads in settings from a given .set file. 
        The file must be given as an absolute path.
        
        The function assumes that the file path and that all formatting
        and values in the settings file are valid (no error checking).'''
        if path != os.path.abspath('current.set'):
            self.origin = path
        # Create a file object by opening the given file (read-only).
        f = open(path, "r")
        line = f.readline().replace('\n','')
        # Loop through any initial comments/dashed lines,
        # then read through the first header.
        while line[0] == '#':
            line = f.readline().replace('\n','')
        while line != '':
            group = line
            self.readGroup(group, f)
            line = f.readline().replace('\n','')
        if self.settings['Input/Output Settings']['Input file/folder'] != '':
            self.settings['Input/Output Settings']['Input file/folder'] = os.path.abspath(self.settings['Input/Output Settings']['Input file/folder'])
        self.settings['Input/Output Settings']['Save directory'] = os.path.abspath(self.settings['Input/Output Settings']['Save directory'])

    def write(self, path, message):

        '''The function that writes the current settings to a given 
        .set file. The file must be given as an absolute path.

        The function takes a string, message, which is written 
        to the top of the settings file: 
        * Each newline characterin the string will start a new comment line. 
        * The write function will autogenerate comment tags (#).
        * The message ALWAYS ends in a newline character.
        
        The function assumes that the file path is valid (no error checking).'''

        # Create a file object by opening the given file (write enabled).
        f = open(path,'w')
        # Create a generic comment header and dashed line.
        while message.count('\n') > 0:
            f.write('# ' + message[:message.find('\n')+1])
            message = message[message.find('\n')+1:]
        f.write('#----------------------------------------------'
                + '------------------------------------------\n')
        # For each settings group, do the following:
        for group in self.settings:
            # Display the group name followed by a dashed line.
            f.write(group + '\n')
            f.write('#----------------------------------------------'
                    + '------------------------------------------\n')
            # For each setting in the group, do the following:
            for setting in self.settings[group]:
                # Write the name and value of the setting separated by a colon and space.
                f.write(setting + ': ')
                f.write(str(self.settings[group][setting]))
                f.write('\n')
            # At the end of the group, write a dashed line.
            f.write('#----------------------------------------------'
                    + '------------------------------------------\n')