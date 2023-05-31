'''The file that contains the Settings class for storing and modifying the program settings.'''

import os

# Set the current working directory for assigning absolute paths.
os.chdir(os.path.dirname(os.path.realpath(__file__)))

class Settings:

    def __init__(self,
                 
                # Initial Input/Ouput Settings.
                ioSettings={
                                'Input type':0,
                                'Input file/folder':'',
                                'Save directory':'',
                                'Keep logs':False
                            },

                # Initial General Settings.
                genSettings={  
                                'Fit range':[0,0],
                                'Plot scale':'',
                                'Time difference method':'',
                                'Digital delay':0,
                                'Number of folders':0,
                                'Meas time per folder':0,
                                'Sort data?':False,
                                'Save figures?':False,
                                'Show plots?':False,
                            },

                # Inital Histogram Visual Settings.
                visSettings={},

                # Inital Histogram Generation Settings.
                histSettings={
                                'Reset time':0,
                                'Bin width':0,
                                'Minimum cutoff':0
                            },

                # Inital Line Fitting Settings.
                fitSettings={},

                # Inital Residual Plot Settings.
                resSettings={}
                ):

        '''The initializer for a Settings object. The object is initialized 
        with blank/empty values, but can be overwritten if desired. However, 
        it is recommended to instead us the read() or set() functions.'''
        
        # Create a dictionary that stores each group of settings,
        # and set each one to the respective input dictionary.
        self.settings = {'Input/Output Settings': ioSettings,
                         'General Settings': genSettings,
                         'Histogram Visual Settings': visSettings,
                         'Histogram Generation Settings': histSettings,
                         'Line Fitting Settings': fitSettings,
                         'Residual Plot Settings': resSettings
        }
        # The variable that indicates whether or not the
        # settings have been changed during runtime.
        self.changed = False

    def isFloat(self, input):

        '''Checks whether or not the input string can be converted to a float.'''

        try:
            float(input)
            return True
        except ValueError:
            return False

    def updated(self):

        '''Returns whether or not the settings have been updated in the current runtime.'''

        return self.changed

    def update(self):

        '''Indicate that the settings have been updated/altered.'''

        self.changed = True

    def set(self, group, setting, value):

        '''Set the value of a specific setting.
        
        Assumes the group exists and that the value is a valid data
        type (no error checking). The setting can be a new setting
        not previously in the dictionary that will be added on.'''

        self.settings[group][setting] = value
    
    def get(self, group, setting):

        '''Get the value of a specific setting.
        
        Assumes the group exists (no error checking). If the
        setting does not exist, the function will return None.'''

        return self.settings[group].get(setting)
    
    def getGroup(self, group):

        '''Get the value of a setting group.
        
        Assumes the group exists (no error checking).'''

        return self.settings[group]
    
    def remove(self, group, setting):

        '''Removes a specific setting. This function should only 
        be used for plot settings, which can be variable.

        Assumes the group is a valid plot setting group and 
        the setting is an exisitng setting (no error checking).'''

        self.settings[group].pop(setting)

    def readPlot(self, group, f):

        '''Reads the settings for a plot (Histogram Visual, Line
        Fitting, Residual Plot) in from a .set file. Requires a
        file object and which type of plot this is for.
        
        Assumes the group and file object are correct (no error checking).'''

        # Clear all settings currently in the group.
        self.settings[group] = {}
        # Get the first setting for the plot.
        line = f.readline().replace('\n','')
        # Continue looping while the input isn't a dashed line.
        while line[0] != '#':
            # Find the : and store the setting name and value accordingly.
            split = line.find(':')
            setting = line[:split]
            value = line[split+2:]
            # If value is boolean, store as bool.
            if value == 'True':
                self.set(group,setting,True)
            elif value == 'False':
                self.set(group,setting,False)
            # If value is numeric, store as integer.
            elif value.isnumeric():
                self.set(group,setting,int(value))
            # If value is a float, store as float.
            elif self.isFloat(value):
                self.set(group,setting,float(value))
            # Otherwise, store as a string.
            else:
                self.set(group,setting,value)
            # Read the next setting.
            line = f.readline().replace('\n','')

    def read(self, path):

        '''The function that reads in settings from a given .set file. 
        The file must be given as an absolute path.
        
        The function assumes that the file path and that all formatting
        and values in the settings file are valid (no error checking).'''

        # Create a file object by opening the given file (read-only).
        f = open(path, "r")
        line = ''
        # Loop through any initial comments/dashed lines,
        # then read through the first header.
        while line != 'Input/Output Settings':
            line = f.readline().replace('\n','')
        f.readline()
        # Read input type and store it.
        line = f.readline().replace('\n','')
        self.set('Input/Output Settings','Input type',int(line[12]))
        # If input type not specified, assume file is not given, and issue a warning to 
        # the user. Then read over the input file/foler line since no input is assumed.
        if line[12] == '0':
            print('WARNING: with the current imported settings, the input file'
                      + '/folder is not specified. You must add it manually.')
            f.readline()
        # Otherwise, read input as given.
        else:
            line = f.readline().replace('\n','')
            file = line[19:]
            # Store the input file/folder.
            self.set('Input/Output Settings','Input file/folder',os.path.abspath(file))
        # Read the save directory and store it.
        line = f.readline().replace('\n','')
        file = line[16:]
        self.set('Input/Output Settings','Save directory',os.path.abspath(file))
        # Read keep logs choice and store it.
        line = f.readline().replace('\n','')
        if line[11] == 'T':
            self.set('Input/Output Settings','Keep logs',True)
        else:
            self.set('Input/Output Settings','Keep logs',False)
        # Read past header and dashed lines.
        f.readline()
        f.readline()
        f.readline()
        # Read the fit range and isolate the two nubmers.
        line = f.readline().replace('\n','')
        line = line[12:len(line)-1]
        # Split the fit range string at the comma to 
        # store the beginning and end of the fit ranges.
        begin = float(line[:line.find(',')])
        end = float(line[line.find(',')+1:])
        # Store the fit range.
        self.set('General Settings','Fit range',[begin,end])
        # Read the plot scale and store it.
        line = f.readline().replace('\n','')
        self.set('General Settings','Plot scale',line[12:])
        # Read the time difference method and store it.
        line = f.readline().replace('\n','')
        self.set('General Settings','Time difference method',line[24:])
        # Read the digital delay and store it.
        line = f.readline().replace('\n','')
        self.set('General Settings','Digital delay',int(line[15:]))
        # Read the number of folders and store it.
        line = f.readline().replace('\n','')
        self.set('General Settings','Number of folders',int(line[19:]))
        # Read the meas time per folder and store it.
        line = f.readline().replace('\n','')
        self.set('General Settings','Meas time per folder',int(line[22:]))
        # Read the sort data choice and store it.
        line = f.readline().replace('\n','')
        if line[12] == 'T':
            self.set('General Settings','Sort data?',True)
        else:
            self.set('General Settings','Sort data?',False)
        # Read the save figures choice and store it.
        line = f.readline().replace('\n','')
        if line[15] == 'T':
            self.set('General Settings','Save figures?',True)
        else:
            self.set('General Settings','Save figures?',False)
        # Read the show plots choice and store it.
        line = f.readline().replace('\n','')
        if line[13] == 'T':
            self.set('General Settings','Show plots?',True)
        else:
            self.set('General Settings','Show plots?',False)
        # Read past header and dashed lines.
        f.readline()
        f.readline()
        f.readline()
        # Read the Histogram Visual Settings.
        self.readPlot('Histogram Visual Settings',f)
        # Read past header and dashed lines.
        f.readline()
        f.readline()
        # Read the reset time and store it.
        line = f.readline().replace('\n','')
        self.set('Histogram Generation Settings','Reset time',float(line[12:]))
        # Read the bin width and store it.
        line = f.readline().replace('\n','')
        self.set('Histogram Generation Settings','Bin width',int(line[11:]))
        # Read the minimum cutoff and store it.
        line = f.readline().replace('\n','')
        self.set('Histogram Generation Settings','Minimum cutoff',int(line[16:]))
        # Read past header and dashed lines.
        f.readline()
        f.readline()
        f.readline()
        # Read the Line Fitting Settings.
        self.readPlot('Line Fitting Settings',f)
        # Read past header and dashed lines.
        f.readline()
        f.readline()
        # Read the Residual Plot Settings.
        self.readPlot('Residual Plot Settings',f)
        # Since settings are all from file, any previous changes
        # will have been overwritten, so mark settings as unchanged.
        self.changed = False

    def write(self, path, default):

        '''The function that writes the current settings to a given 
        .set file. The file must be given as an absolute path.

        The function takes a boolean, default, which marks whether 
        or not the settings being written are the default.
        
        The function assumes that the file path is valid (no error checking).'''

        # Create a file object by opening the given file (write enabled).
        f = open(path,'w')
        # Create a generic comment header and dashed line.
        if default:
            f.write('# The default settings for running the PyNoise project.\n')
        else:
            f.write('# Custom user generated settings.\n')
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
                f.write(str(self.get(group, setting)))
                f.write('\n')
            # At the end of the group, write a dashed line.
            f.write('#----------------------------------------------'
                    + '------------------------------------------\n')

    def print_section(self, group):

        '''Prints all the settings within a specific setting group.
        
        Assumes the given group is valid (no error checking).'''

        # print group name.
        print(group)
        # If no settings exist in the group, mention it.
        if len(self.settings[group]) == 0:
            print ('No specified settings.')
        # Otherwise, for each setting in the group, write
        # its name and value separated by a dash.
        else:
            for setting in self.settings[group]:
                print(setting,'-',self.get(group,setting))

    def print_all(self):

        '''Print all of the current settings.'''

        print('\nHere are the current settings for the program:')
        print()
        # Print Input/Output Settings.
        self.print_section('Input/Output Settings')
        print()
        # Print General Settings.
        self.print_section('General Settings')
        print()
        # Print Histogram Visual Settings.
        self.print_section('Histogram Visual Settings')
        print()
        # Print Histogram Generation Settings.
        self.print_section('Histogram Generation Settings')
        print()
        # Print Line Fitting Settings.
        self.print_section('Line Fitting Settings')
        print()
        # Print Residual Plot Settings.
        self.print_section('Residual Plot Settings')