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
        self.settings = {'Input/Output Settings': {},
                         'General Settings': {},
                         'RossiAlpha Settings': {},
                         'CohnAlpha Settings' : {},
                         'Semilog Plot Settings': {},
                         'FeynmanY Settings' : {},
                         'Histogram Visual Settings': {},
                         'Line Fitting Settings': {},
                         'Scatter Plot Settings': {}
        }
        # The variable that stores the path of the 
        # .json file that was most recently imported.
        self.origin = 'None'
        # The variable that stores the path of the 
        # .json file that was most recently appended.
        self.appended = 'None'
        self.hvs_drop = ['select setting...','alpha','angle','animated','antialiased','bounds','capsize','capstyle','clip_on','clip_path','color','ecolor','edgecolor','error_kw','facecolor','fill','grid','hatch','height','in_layout','joinstyle','label','linestyle','linewidth','log','mouseover','picker','rasterized','sketch_params','snap','tick_label','url','visible','width','xerr','yerr','zorder','Cancel']
        self.lfs_drop = ['select setting...','alpha','angle','animated','antialiased','clip_on','clip_path','color','dash_capstyle','dash_joinstyle','dashes','drawstyle','fillstyle','gapcolor','grid','in_layout','label','linestyle','linewidth','marker','markeredgecolor','markeredgewidth','markerfacecolor','markerfacecoloralt','markersize','markevery','mouseover','path_effects','picker','pickradius','rasterized','scalex','scaley','sketch_params','snap','solid_capstyle','solid_joinstyle','transform','url','visible','zorder','Cancel']
        self.rps_drop = ['select setting...','alpha','antialiased','color','capstyle','cmap','edgecolor','facecolor','hatch','joinstyle','linestyle','linewidth','marker','norm','offset_transform','offsets','pickradius','plotnonfinite','s','urls','vmin','vmax','zorder','Cancel']
    
    def sort_drops(self):
        self.hvs_drop.remove('Cancel')
        self.hvs_drop.remove('select setting...')
        self.hvs_drop.sort()
        self.hvs_drop.append('Cancel')
        self.hvs_drop.insert(0,'select setting...')
        self.lfs_drop.remove('Cancel')
        self.lfs_drop.remove('select setting...')
        self.lfs_drop.sort()
        self.lfs_drop.append('Cancel')
        self.lfs_drop.insert(0,'select setting...')
        self.rps_drop.remove('Cancel')
        self.rps_drop.remove('select setting...')
        self.rps_drop.sort()
        self.rps_drop.append('Cancel')
        self.rps_drop.insert(0,'select setting...')

    def format(self, value):

        '''Converts a variable to a properly formatted string. 
        This is needed for floats/ints in scientific notation.
        
        Requires:
        - value: the variable that is to be converted into a string.'''

        # If variable is a list.
        if isinstance(value, list):
            response ='['
            # For each entry, properly convert it to a string and 
            # add it to the list string with a separating ', '.
            for entry in value:
                response += self.format(entry) + ', '
            # Remove the extra ', ' and close the list.
            response = response[0:len(response)-2] + ']'
            # Return completed list.
            return response
        # If variable is a float/int and is of an excessively large or 
        # small magnitude, display it in scientific notation.
        elif ((isinstance(value, float) or isinstance(value, int)) 
            and (value > 1000 
                or value < -1000 
                or (value < 0.01 and value > -0.01 and value != 0))):
            return f'{value:g}'
        # Otherwise, just return a string cast of the variable.
        else:
            return str(value)

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
                                + self.format(baseline.settings[group].get(setting)) 
                                + ' -> ' + self.format(self.settings[group][setting]))
        # For each setting in the baseline, if it does not 
        # exist in the current settings, store the removal.
        for group in baseline.settings:
            for setting in baseline.settings[group]:
                if self.settings[group].get(setting) == None and baseline.settings[group].get(setting) != self.settings[group].get(setting):
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
                        match group:
                            case 'Histogram Visual Settings':
                                self.hvs_drop.append(setting)
                            case 'Line Fitting Settings':
                                self.lfs_drop.append(setting)
                            case 'Scatter Plot Settings':
                                self.rps_drop.append(setting)
                # Otherwise, add/modify the specified setting.
                else:
                    if self.settings[group].get(setting) == None:
                        match group:
                            case 'Histogram Visual Settings':
                                self.hvs_drop.remove(setting)
                            case 'Line Fitting Settings':
                                self.lfs_drop.remove(setting)
                            case 'Scatter Plot Settings':
                                self.rps_drop.remove(setting)
                    self.settings[group][setting] = parameters[group][setting]
        self.sort_drops()
        # If the append is from a permanent file, mark that 
        # file as the most recently file appended from.
        if path != os.path.abspath('append.json'):
            self.appended = path

    def read(self, path: str):

        '''Reads in a json file that completely overwrites the 
        exisitng settings. Requiures an absolute path to the file.'''

        for setting in self.settings['Histogram Visual Settings']:
            self.hvs_drop.append(setting)
        for setting in self.settings['Line Fitting Settings']:
            self.lfs_drop.append(setting)
        for setting in self.settings['Scatter Plot Settings']:
            self.rps_drop.append(setting)
        # Load the new parameters from the json file.
        self.settings = json.load(open(path))
        for setting in self.settings['Histogram Visual Settings']:
            self.hvs_drop.remove(setting)
        for setting in self.settings['Line Fitting Settings']:
            self.lfs_drop.remove(setting)
        for setting in self.settings['Scatter Plot Settings']:
            self.rps_drop.remove(setting)
        self.sort_drops()
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
        default.read(os.path.abspath('./settings/default.json'))
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