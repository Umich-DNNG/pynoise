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
        self.settings = {'Input/Output Settings': {'Input type':0,
                                                   'Input file/folder':'',
                                                   'Save directory':'',
                                                   'Keep logs':False},
                         'General Settings': {'Fit range':[0,0],
                                              'Plot scale':'',
                                              'Digital delay':0,
                                              'Number of folders':0,
                                              'Meas time per folder':0,
                                              'Sort data':False,
                                              'Save figures':False,
                                              'Show plots':False
                                              },
                         'RossiAlpha Settings': {
                                                'Time difference method':'',
                         },
                         'PSD Settings' : {'Dwell time':0,
                                           'Meas time range':[0,0],
                                           'Clean pulses switch': False},
                         'Histogram Generation Settings': {'Reset time':0,
                                                           'Bin width':0,
                                                           'Minimum cutoff':0},
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
        
        Does not change the file of origin. Cannot delete exisiting settings.'''

        parameters = json.load(open(path))
        for group in parameters:
            for setting in parameters[group]:
                if parameters[group][setting] == '' and self.settings[group].get(setting) != None:
                    self.settings[group].pop(setting)
                else:
                    self.settings[group][setting] = parameters[group][setting]

    def read(self, path):

        '''Reads in a json file that completely overwrites the 
        exisitng settings. Requiures an absolute path to the file.'''

        self.settings = json.load(open(path))
        if path != os.path.abspath('current.json'):
            self.origin = path

    def write(self, path):

        '''Write the current settings to a file.'''

        with open(path,'w') as file:
            file.write(json.dumps(self.settings, indent=4))

    def save(self, path):

        '''Save the current settings to a file, listing 
        only those that overwrite the default.'''

        default = Settings()
        default.read(os.path.abspath('default.json'))
        output = {}
        for group in self.settings:
            for setting in self.settings[group]:
                if default.settings[group].get(setting) != self.settings[group][setting]:
                    if output.get(group) == None:
                        output[group] = {}
                    output[group][setting] = self.settings[group][setting]
        for group in default.settings:
            for setting in default.settings[group]:
                if self.settings[group].get(setting) == None:
                    if output.get(group) == None:
                        output[group] = {}
                    output[group][setting] = ""
        with open(path,'w') as file:
            file.write(json.dumps(output, indent=4))