import os
from tqdm import tqdm
import h5py # 3.11.0
import numpy as np


def writeHDF5Data(npArrays, keys, path: list, settings: dict, fileName:str = "pynoise", settingsName: str = './settings/default.json'):
    '''
    Saves a list of numpy arrays to a file in hdf5 format.

    Inputs:
    - npArrays: numpy lists to be saved in the file
    - keys: the keys for each of the data set. Assuming parallel list with npArrays
    - path: list containing the path to where the npArray will be stored. Ex: [RossiAlpha, histogram] or [input file/folder, rossialpha, td method, reset time]
    - settings: dict of runtime settings
    - fileName: string name of the hdf5 file. 'pynoise' has a specific starting format before following user format, while all others just follow user format
    - settingsName: string of the path to settings file--not required if fileName is not pynoise
    '''

    # numFolders + reset time + td method
    fileName = fileName + '.h5'
    filePath = os.path.join(settings['Input/Output Settings']['Save directory'], fileName)
    with h5py.File(filePath, 'a') as file:
        group = file
        # if is pynoise.h5, find the matching settings, or create a new iteration
        if fileName == 'pynoise.h5':
            settingsName = settingsName[settingsName.rfind('/')+1:]
            group = findMatchingSettings(file.require_group(settingsName), settings)
        
        # find the base
        dest = travelDownHDF5Write(group, path)
        
        # if it was None, meaning the data exists already, exit without writing
        if dest is None:
            return
        
        # write data to destination
        for _, (npList, key) in tqdm(enumerate(zip(npArrays, keys))):
            dest.create_dataset(key, data=npList)


def readHDF5Data(path: list, settings: dict, fileName:str = 'pynoise', settingsName: str = './settings/default.json'):
    '''
    Reads the data at the path destination of an hdf5 file.

    Inputs:
    - path: list containing the path to the data destinataion
    - settings: dictionary containing runtimee settings
    - fileName: string name of the h5 file to read from. 'pynoise' has a specific format to search, all other files follow user paths
    - settingsName: string path to settings file--not required if fileName is not pynoise

    Outputs:
    data: a dictionary of the data at the destination
    '''
    fileName = fileName + '.h5'
    filePath = os.path.join(settings['Input/Output Settings']['Save directory'], fileName)
    
    with h5py.File(filePath, 'r') as file:
        group = file
        
        # if pynoise, find correct settings
        if fileName == 'pynoise.h5':
            settingsName = settingsName[settingsName.rfind('/')+1:]
            group = findMatchingSettings(file.require_group(settingsName), settings)
        
        # travel to destination
        dest = travelDownHDF5Read(group, path)

        # if destination could not be found, the data does not exist. Exit without reading data
        if dest is None:
            return None
        
        data = {}
        for key in dest.keys():
            data[key] = dest[key][()]
        return data


# -----------------------------helper functions for hdf5---------------------------------------------

def travelDownHDF5Write(group, layers):
    '''
    Helper function to travel recursively down the HDF5 file portion "group" on the path specified by layers
    Used for writing data to an HDF5 file, which requires creating groups along the way if it does not exists

    Inputs:
    - group: HDF5 object portion. The file or a subgroup of the file
    - layers: list holding the layers to be traveled. Index 0 is the next layer to be created/traveled to

    Outputs: 
    the new group for information to be stored OR None, which indicates the information already exists in the file
    '''
    if (len(layers)) > 1:
        return travelDownHDF5Write(group.require_group(layers[0]), layers[1:])
    # if we are on the last layer
    else:
        # if the last layer exists already, do not create a group, 
        # as the existance means the data is already written to the file
        if layers[0] in group:
            return None
        else:
            return group.create_group(layers[0])


def travelDownHDF5Read(group, layers):
    '''
    Helper function to travel recursively down the HDF5 file portion "group" on the path specified by layers
    Used for reading data from an HDF5 file, which should NOT create any groups whatsoever

    Inputs:
    - group: HDF5 object portion. The file or a subgroup of the file
    - layers: list holding the layers to be traveled. Index 0 is the next layer to be created/traveled to

    Outputs: 
    the ending group to read information from OR None if it does not exist
    '''
    # if layer exists, continue down the path OR return the end group
    if layers[0] in group:
        if (len(layers)) > 1:
            return travelDownHDF5Read(group[layers[0]], layers[1:])
        else: 
            return group[layers[0]]
    
    else:
        return None


def findMatchingSettings(group, settings):
    '''
    Helper function to determine which iteration number has settings that match. If none match, create a new iteration and add the settings

    Inputs:
    - group: the h5 group to analyze
    - settings: dictionary containing runtime settings
    '''
    i = 1
    paramStr = 'iteration' + str(i)

    # keep looping as long as 'iteration[x]' exists for this settings group
    while paramStr in group:
        tempGroup = group[paramStr]
        if 'settings' in tempGroup:
            settingsGroup = tempGroup['settings']
            found = compareSettings(settings, settingsGroup)
            if found:
                return tempGroup
        i = i + 1
        paramStr = 'iteration' + str(i)
    
    # if matching settings were not found, create a new iteration group and write the settings to it
    group = group.create_group(paramStr)
    settingsGroup = group.create_group('settings')
    for key, value in settings.items():                    
        # do not store visual plot settings
        if (key == 'Semilog Plot Settings' or key == 'Histogram Visual Settings' 
            or key == 'Line Fitting Settings' or key == 'Scatter Plot Settings'):
            continue
        # any slashes must be sanitized
        key = key.replace('/', '-')
        valueGroup = settingsGroup.create_group(key)
        for subkey, subvalue in value.items():
            # any slashes must be sanitized
            subkey = subkey.replace('/', '-')
            # skip over any "null" settings values
            if subvalue is not None:
                continue
            valueGroup.create_dataset(subkey, data=subvalue)
        
    return group


def compareSettings(settings, group):
    '''
    Helper function to compare the current runtime settings and the settings in the current group of the hdf5 file

    Inputs:
    - settings: dictionary holding current runtime settings
    - group: group holding the settings in the hdf5 file

    Outputs:
    - a boolean indicating whether the settings match or not
    '''
    for key, value in settings.items():                    
        # do not confirm visual plot settings
        if (key == 'Semilog Plot Settings' or key == 'Histogram Visual Settings' 
            or key == 'Line Fitting Settings' or key == 'Scatter Plot Settings'):
            continue
        
        data = {}

        # get the subgroup matching the key
        currSettings = settings[key]
        # any slashes must be sanitized
        key = key.replace('/', '-')
        valueGroup = group[key]
        
        # read in settings
        for h5Key in valueGroup.keys():
            data[h5Key] = valueGroup[h5Key][()]

        for subkey, subvalue in value.items():
            # any slashes must be sanitized
            sanitizedKey = subkey.replace('/', '-')
            # if settings value is None (ie null), ensure it does not exist in hdf5 data
            if subvalue is None:
                if sanitizedKey in valueGroup:
                    return False
            else:
                # at this point, all values in the runtime settings are NOT null, so
                # ensure setting exists in the hdf5 file before starting comparisons
                if sanitizedKey not in data:
                    return False
                
                # convert the read-in setting to a string if it was a bytes object
                if isinstance(data[sanitizedKey], bytes):
                    data[sanitizedKey] = data[sanitizedKey].decode('utf-8')

                # for list/array comparisons
                if isinstance(data[sanitizedKey], np.ndarray) or isinstance(currSettings[subkey], list):
                    # compare lists
                    if isinstance(data[sanitizedKey], np.ndarray) and isinstance(currSettings[subkey], list):
                        if not all(a == b for a, b in zip(data[sanitizedKey], currSettings[subkey])):
                            return False
                    # if they are not both lists
                    else: 
                        return False

                elif data[sanitizedKey] != currSettings[subkey]:
                    return False
    return True

