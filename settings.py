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
    
    def read(self, path):
        
        self.settings = json.load(open(path))
        if path != os.path.abspath('current.json'):
            self.origin = path

    def write(self, path):

        with open(path,'w') as file:
            file.write(json.dumps(self.settings, indent=4))