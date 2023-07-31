'''The file that contains the Settings class for 
importing, exporting, and storing the program settings.'''



# Necessary imports.
import os
import json



# Set the current working directory for assigning absolute paths.
os.chdir(os.path.dirname(os.path.realpath(__file__)))



def format(value):

    '''Converts a variable to a properly formatted string 
    (needed for floats/ints in scientific notation). 
    Supports ints, floats, and lists/nested lists of these 
    basic variables. All others are casted to strings.
        
    Inputs:
    - value: the variable that is to be converted into a string.
        
    Outputs:
    - the string equivalent of value.'''


    # If the variable is a list:
    if isinstance(value, list):
        response ='['
        # For each entry, properly convert it to a string and 
        # add it to the list string with a separating ', '.
        for entry in value:
            response += format(entry) + ', '
        # Remove the extra ', ' and close the list.
        response = response[:len(response)-2] + ']'
        # Return the completed list.
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



class Settings:

    '''The class that contains the settings dictionary along 
    with helper functions for importing/exporting settings.'''


    def __init__(self, gui:bool = False):

        '''Initializes an empty Settings object.
        
        Inputs:
        - gui: a boolean stating whether or not these 
        settings will be used for gui purposes. If not 
        given, assumes False (terminal implementation).'''


        # Create a dictionary that stores each group 
        # of settings, initialized to be empty.
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
        self.origin = None
        # The variable that stores the path of the 
        # .json file that was most recently appended.
        self.appended = None
        # Store the gui boolean.
        self.gui_mode = gui
        # If in gui mode, create the dropdown menu 
        # options for matplotlib settings groups.
        if self.gui_mode:
            self.hvs_drop = ['select setting...','alpha','angle','animated','antialiased','bounds','capsize','capstyle','clip_on','clip_path','color','ecolor','edgecolor','error_kw','facecolor','fill','grid','hatch','height','in_layout','joinstyle','label','linestyle','linewidth','log','mouseover','picker','rasterized','sketch_params','snap','tick_label','url','visible','width','xerr','yerr','zorder','Cancel']
            self.lfs_drop = ['select setting...','alpha','angle','animated','antialiased','clip_on','clip_path','color','dash_capstyle','dash_joinstyle','dashes','drawstyle','fillstyle','gapcolor','grid','in_layout','label','linestyle','linewidth','marker','markeredgecolor','markeredgewidth','markerfacecolor','markerfacecoloralt','markersize','markevery','mouseover','path_effects','picker','pickradius','rasterized','scalex','scaley','sketch_params','snap','solid_capstyle','solid_joinstyle','transform','url','visible','zorder','Cancel']
            self.sps_drop = ['select setting...','alpha','antialiased','color','capstyle','cmap','edgecolor','facecolor','hatch','joinstyle','linestyle','linewidth','marker','norm','offset_transform','offsets','pickradius','plotnonfinite','s','urls','vmin','vmax','zorder','Cancel']
            self.sls_drop = ['select setting...','alpha','angle','animated','antialiased','clip_on','clip_path','color','dash_capstyle','dash_joinstyle','dashes','drawstyle','fillstyle','gapcolor','grid','in_layout','label','linestyle','linewidth','marker','markeredgecolor','markeredgewidth','markerfacecolor','markerfacecoloralt','markersize','markevery','mouseover','path_effects','picker','pickradius','rasterized','scalex','scaley','sketch_params','snap','solid_capstyle','solid_joinstyle','transform','url','visible','zorder','Cancel']
    


    def sort_drops(self):
        
        '''Sorts the dropdown menus.'''


        # Remove the settings that shouldn't be sorted.
        self.hvs_drop.remove('Cancel')
        self.hvs_drop.remove('select setting...')
        # Sort the remaining settings.
        self.hvs_drop.sort()
        # Add the unsorted settings to their intended spot.
        self.hvs_drop.append('Cancel')
        self.hvs_drop.insert(0,'select setting...')
        # Do this for all the settings groups.
        self.lfs_drop.remove('Cancel')
        self.lfs_drop.remove('select setting...')
        self.lfs_drop.sort()
        self.lfs_drop.append('Cancel')
        self.lfs_drop.insert(0,'select setting...')
        self.sps_drop.remove('Cancel')
        self.sps_drop.remove('select setting...')
        self.sps_drop.sort()
        self.sps_drop.append('Cancel')
        self.sps_drop.insert(0,'select setting...')
        self.sls_drop.remove('Cancel')
        self.sls_drop.remove('select setting...')
        self.sls_drop.sort()
        self.sls_drop.append('Cancel')
        self.sls_drop.insert(0,'select setting...')



    def compare(self, current:bool = False):

        '''Compare the current settings to the most recently 
        imported + appended version to see if they have changed.
        
        Inputs:
        - current: a boolean stating what settings should be 
        imported into the baseline (current or origin + appended). If 
        current is True, there MUST be a comp.json file in the 
        settings folder. If not given, assumes False (origin + appended).'''


        # Create the baseline settings object and the list of changes.
        baseline = Settings()
        list = []
        # If comparing current settings:
        if current:
            # Read in from the temporary comparison file.
            baseline.read(os.path.abspath('settings/comp.json'))
            # Close the temporary comparison file.
            os.remove(os.path.abspath('settings/comp.json'))
        # If comparing to baseline:
        else:
            # Read in previous settings and append the
            # most recently appended settings, if any.
            baseline.read(self.origin)
            if self.appended != None:
                baseline.append(self.appended)
        # For each setting in the current settings:
        for group in self.settings:
            for setting in self.settings[group]:
                # If it's different or new, store the difference.
                if baseline.settings[group].get(setting) != self.settings[group][setting]:
                    list.append(setting + ' in ' + group + ': ' 
                                + format(baseline.settings[group].get(setting)) 
                                + ' -> ' + format(self.settings[group][setting]))
        # For each setting in the baseline:
        for group in baseline.settings:
            for setting in baseline.settings[group]:
                # If it does not exist in the current settings, store the removal.
                if (self.settings[group].get(setting) == None 
                    and baseline.settings[group].get(setting) != None):
                    list.append(setting + ' in ' + group + ' removed')
        # Return the list of changes for printing.
        return list



    def append(self, path: str):
        
        '''Appends settings from a json file into the settings 
        object.
        
        Inputs:
        - path: a string indicating the absolute 
        path to the .json file to be appended.'''


        # Load the new parameters from the json file.
        parameters = json.load(open(path))
        # For each of the settings listed:
        for group in parameters:
            for setting in parameters[group]:
                # If user wants the setting removed:
                if parameters[group][setting] == '':
                    # Ensure the setting currently exists.
                    if self.settings[group].get(setting) != None:
                        # Remove the setting.
                        self.settings[group].pop(setting)
                        # If in gui mode, add the removed setting 
                        # back to the appropriate dropdown menu.
                        if self.gui_mode:
                            match group:
                                case 'Histogram Visual Settings':
                                    self.hvs_drop.append(setting)
                                case 'Line Fitting Settings':
                                    self.lfs_drop.append(setting)
                                case 'Scatter Plot Settings':
                                    self.sps_drop.append(setting)
                                case 'Semilog Plot Settings':
                                    self.sls_drop.append(setting)
                # Otherwise, add/modify the specified setting.
                else:
                    # If in gui mode and setting didn't exist 
                    # before, remove it from the dropdown menu.
                    if self.gui_mode and self.settings[group].get(setting) == None:
                        match group:
                            case 'Histogram Visual Settings':
                                self.hvs_drop.remove(setting)
                            case 'Line Fitting Settings':
                                self.lfs_drop.remove(setting)
                            case 'Scatter Plot Settings':
                                self.sps_drop.remove(setting)
                            case 'Semilog Plot Settings':
                                self.sls_drop.remove(setting)
                    # Set the setting to its new value.
                    self.settings[group][setting] = parameters[group][setting]
        # Resort the dropdown menus if in gui mode.
        if self.gui_mode:
            self.sort_drops()
        # If the append is from a permanent file, mark that 
        # file as the most recently file appended from.
        if path != os.path.abspath('append.json'):
            self.appended = path



    def read(self, path: str):

        '''Reads in a json file that completely 
        overwrites the exisitng settings.
        
        Inputs:
        - path: a string indicating the absolute 
        path to the .json file to be read.'''


        # Add all the current settings back to 
        # the dropdown menus if in gui mode.
        if self.gui_mode:
            for setting in self.settings['Histogram Visual Settings']:
                self.hvs_drop.append(setting)
            for setting in self.settings['Line Fitting Settings']:
                self.lfs_drop.append(setting)
            for setting in self.settings['Scatter Plot Settings']:
                self.sps_drop.append(setting)
            for setting in self.settings['Semilog Plot Settings']:
                self.sls_drop.append(setting)
        # Load the new parameters from the json file.
        self.settings = json.load(open(path))
        # If in gui mode:
        if self.gui_mode:
            # Remove all the used settings from the dropdown menus.
            for setting in self.settings['Histogram Visual Settings']:
                self.hvs_drop.remove(setting)
            for setting in self.settings['Line Fitting Settings']:
                self.lfs_drop.remove(setting)
            for setting in self.settings['Scatter Plot Settings']:
                self.sps_drop.remove(setting)
            for setting in self.settings['Semilog Plot Settings']:
                self.sls_drop.remove(setting)
            # Sort the dropdown menus.
            self.sort_drops()
        # If the JSON file being loaded is a permanent file, change the 
        # settings origin and clear the most recently appended variable.
        if path != os.path.abspath('current.json'):
            self.origin = path
            self.appended = None



    def write(self, path: str):

        '''Write the entire current settings to a file.
        
        Inputs:
        - path: a string indicating the absolute 
        path to the .json file to be written to.'''


        # Open the file in write mode and use the json 
        # dumps function to export the current settings.
        with open(path,'w') as file:
            file.write(json.dumps(self.settings, indent=4))



    def save(self, path: str):

        '''Save the current settings to a file, listing 
        only those that overwrite the default.
        
        Inputs:
        - path: a string indicating the absolute 
        path to the .json file to be written to.'''


        # Create and load a default settings object.
        default = Settings()
        default.read(os.path.abspath('settings/default.json'))
        # The dictionary to be outputted.
        output = {}
        # For each current setting:
        for group in self.settings:
            for setting in self.settings[group]:
                # If it is different/new from the default:
                if default.settings[group].get(setting) != self.settings[group][setting]:
                    # If group doesn't currently exist, make it.
                    if output.get(group) == None:
                        output[group] = {}
                    # Store the altered setting.
                    output[group][setting] = self.settings[group][setting]
        # For each default setting:
        for group in default.settings:
            for setting in default.settings[group]:
                # If it is not in the current settings:
                if self.settings[group].get(setting) == None:
                    # If group doesn't currently exist, make it.
                    if output.get(group) == None:
                        output[group] = {}
                    # Store an empty string to mark it as deleted.
                    output[group][setting] = ''
        # Open the file in write mode and use the json 
        # dumps function to export the current settings.
        with open(path,'w') as file:
            file.write(json.dumps(output, indent=4))