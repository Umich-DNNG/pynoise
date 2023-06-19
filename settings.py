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
        self.settings = {'Input/Output Settings': {'Input file/folder': '',
                                                    'Data Column': 0,
                                                    'Save directory': '',
                                                    'Keep logs': False},
                         'General Settings': {'Fit range':[0,0],
                                              'Number of folders':0,
                                              'Meas time per folder':0,
                                              'Quiet mode':False,
                                              'Sort data':False,
                                              'Save figures':False,
                                              'Show plots':False
                                              },
                         'RossiAlpha Settings': {
                                                'Time difference method':'',
                                                'Digital delay':0,
                                                'Histogram Generation Settings': {
                                                    'Reset time':0,
                                                    'Bin width':0,
                                                    'Error Bar/Band':''
                                                },
                                                "Fit Region Settings": {
                                                    "Minimum cutoff": 0
                                                }
                         },
                         'PSD Settings' : {'Dwell time':0,
                                           'Meas time range':[0,0],
                                           'Clean pulses switch': False},
                         'Histogram Visual Settings': {},
                         'Line Fitting Settings': {},
                         'Residual Plot Settings': {}
        }
        # The variable that stores the path of the 
        # .json file that was most recently imported.
        self.origin = ''
        # The variable that indicates whether or not the
        # settings have been changed during runtime.
        self.changed = False
    
    def append(self, path):
        
        '''Appends settings from a json file into the settings 
        object. Requires an abolsute path to the file.
        
        Does not change the file of origin.'''

        # Load the new parameters from the json file.
        parameters = json.load(open(path))
        for group in parameters:
            for setting in parameters[group]:
                # If user wants the setting removed and it currently exists, remove it.
                if parameters[group][setting] == '' and self.settings[group].get(setting) != None:
                    self.settings[group].pop(setting)
                # Otherwise, add/modify the specified setting.
                else:
                    self.settings[group][setting] = parameters[group][setting]

    def read(self, path):

        '''Reads in a json file that completely overwrites the 
        exisitng settings. Requiures an absolute path to the file.'''

        # Load the new parameters from the json file.
        self.settings = json.load(open(path))
        # If the JSON file being loaded is a permanent 
        # file, change the settings origin.
        if path != os.path.abspath('current.json'):
            self.origin = path

    def write(self, path):

        '''Write the current settings to a file.
        Requiures an absolute path to the file.'''

        with open(path,'w') as file:
            file.write(json.dumps(self.settings, indent=4))

    def save(self, path):

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