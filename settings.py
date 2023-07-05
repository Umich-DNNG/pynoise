'''The file that contains the Settings class for 
importing, uploading, and storing the program settings.'''

# For working with paths.
import os
import json

# Set the current working directory for assigning absolute paths.
os.chdir(os.path.dirname(os.path.realpath(__file__)))

class Settings:

    def __init__(self):

        '''The initializer for a Settings object. The object is initialized 
        with blank/empty values.'''
        
        # Create a dictionary that stores each group of settings,
        # and set each one to the respective input dictionary.
        self.settings = {'Input/Output Settings': {'Input file/folder': 'none',
                                                    'Time Column': 0,
                                                    'Channels Column':None,
                                                    'Save directory': './',
                                                    'Keep logs': False},
                         'General Settings': {'Fit range':[0.0,1000.0],
                                              'Number of folders':10,
                                              'Quiet mode':False,
                                              'Sort data':True,
                                              'Save figures':False,
                                              'Show plots':False
                                              },
                         'RossiAlpha Settings': {
                                                'Time difference method':'any_and_all',
                                                'Digital delay':750,
                                                'Combine Calc and Binning': False,
                                                'Histogram Generation Settings': {
                                                    'Reset time':1000,
                                                    'Bin width':9,
                                                    'Error Bar/Band':'band'
                                                },
                                                "Fit Region Settings": {
                                                    "Minimum cutoff": 30
                                                }
                         },
                         'PSD Settings' : {'Dwell time':2.0e6,
                                           'Meas time range':[1.5e11,1.0e12],
                                           'Clean pulses switch': True},
                         'Histogram Visual Settings': {'alpha': 1,
                                                        'fill': True,
                                                        'color': '#B2CBDE',
                                                        'edgecolor': '#162F65',
                                                        'linewidth': 0.4
                         },
                         'Line Fitting Settings': {'color': '#162F65',
                                                    'markeredgecolor': 'blue',
                                                    'markerfacecolor': 'black',
                                                    'linestyle': '-',
                                                    'linewidth': 1  
                         },
                         'Residual Plot Settings': {'color': '#B2CBDE',
                                                    'edgecolor': '#162F65',
                                                    'linewidth': 0.4,
                                                    'marker': 'o',
                                                    's': 20
                         }
        }
        # The variable that stores the path of the 
        # .json file that was most recently imported.
        self.origin = 'None'
        # The variable that stores the path of the 
        # .json file that was most recently appended.
        self.appended = 'None'
    
    def compare(self):

        '''Compare the current settings to the most recently 
        imported + appended version to see if they have changed.'''

        # Create a baseline settings object and the list of changes.
        baseline = Settings()
        list = []
        # Read in previous settings and append 
        # most recently appended settings, if any.
        baseline.read(self.origin)
        if self.appended != 'None':
            baseline.append(self.appended)
        # For each setting in the current settings, if it's different 
        # compared to the baseline or new, store the difference.
        for group in self.settings:
            for setting in self.settings[group]:
                if baseline.settings[group].get(setting) != self.settings[group][setting]:
                    list.append(setting + ' in ' + group + ': ' 
                                + str(baseline.settings[group].get(setting)) 
                                + ' -> ' + str(self.settings[group][setting]))
        # For each setting in the baseline, if it does not 
        # exist in the current settings, store the removal.
        for group in baseline.settings:
            for setting in baseline.settings[group]:
                if self.settings[group].get(setting) == None and baseline.settings[group].get(setting) != self.settings[group][setting]:
                    list.append(setting + ' in ' + group + ' removed')
        # Return the list of changes for printing.
        return list

    def append(self, path: str):
        
        '''Appends settings from a json file into the settings 
        object. Requires an abolsute path to the settings file.
        
        Does not change the file of origin.'''

        # Load the new parameters from the json file.
        parameters = json.load(open(path))
        # For each of the settings listed:
        for group in parameters:
            for setting in parameters[group]:
                # If user wants the setting removed and it currently exists, 
                # remove it. If the setting doesn't exist, do nothing.
                if parameters[group][setting] == '':
                    if self.settings[group].get(setting) != None:
                        self.settings[group].pop(setting)
                # Otherwise, add/modify the specified setting.
                else:
                    self.settings[group][setting] = parameters[group][setting]
        # If the append is from a permanent file, mark that 
        # file as the most recently file appended from.
        if path != os.path.abspath('append.json'):
            self.appended = path

    def read(self, path: str):

        '''Reads in a json file that completely overwrites the 
        exisitng settings. Requiures an absolute path to the file.'''

        # Load the new parameters from the json file.
        self.settings = json.load(open(path))
        # If the JSON file being loaded is a permanent file, change the 
        # settings origin and clear the most recently appended variable.
        if path != os.path.abspath('current.json'):
            self.origin = path
            self.appended = 'None'

    def write(self, path: str):

        '''Write the current settings to a file.
        Requiures an absolute path to the file.'''

        with open(path,'w') as file:
            file.write(json.dumps(self.settings, indent=4))

    def save(self, path: str):

        '''Save the current settings to a file, listing 
        only those that overwrite the default.'''

        # Create and load a default settings object.
        default = Settings()
        default.read(os.path.abspath('default.json'))
        # The dictionary to be outputted.
        output = {}
        for group in self.settings:
            for setting in self.settings[group]:
                # For each setting in the current settings, if 
                # it is different/new from the default, store it.
                if default.settings[group].get(setting) != self.settings[group][setting]:
                    # If group doesn't currently exist, make it.
                    if output.get(group) == None:
                        output[group] = {}
                    # Set setting to specified value.
                    output[group][setting] = self.settings[group][setting]
        for group in default.settings:
            for setting in default.settings[group]:
                # If there is a setting in the default that is not 
                # in the current settings, mark it as deleted.
                if self.settings[group].get(setting) == None:
                    # If group doesn't currently exist, make it.
                    if output.get(group) == None:
                        output[group] = {}
                    output[group][setting] = ""
        # Open file and store settings in JSON format.
        with open(path,'w') as file:
            file.write(json.dumps(output, indent=4))