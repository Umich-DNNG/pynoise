import os
import h5py # 3.11.0
import numpy as np
from itertools import zip_longest
from collections import defaultdict
from pathlib import Path

def writeHDF5Data(npArrays, keys, path: list, settings: dict, fileName:str = "pynoise", settingsName: str = './settings/default.json'):
    '''
    Saves a list of numpy arrays to a file in hdf5 format.

    Inputs:
    - npArrays: numpy lists to be saved in the file
    - keys: the keys for each of the data set. Assuming parallel list with npArrays
    - path: list containing the path to where the npArray will be stored. Ex: [RossiAlpha, histogram] or [input file/folder, rossialpha, td method, reset time]
    - settings: dict of runtime settings
    - fileName: string name of the hdf5 file. 'pynoise' and 'processing_data' have a specific starting format before following user format, while all others just follow user format
    - settingsName: string of the path to settings file--not required if fileName is not pynoise or processing_data
    '''
    fileName = fileName + '.h5'
    filePath = os.path.join(settings['Input/Output Settings']['Save directory'], fileName)
    with h5py.File(filePath, 'a') as file:
        group = file
        # if is pynoise.h5, find the matching settings, or create a new iteration
        if fileName == 'pynoise.h5' or fileName == 'processing_data.h5':
            settingsName = settingsName[settingsName.rfind('/')+1:]
            group = findMatchingSettings(file.require_group(settingsName), settings)
        
        # find the base
        dest = travelDownHDF5Write(group, path)
        
        # if it was None, meaning the data exists already, exit without writing
        if dest is None:
            return
        
        # write data to destination
        for _, (npList, key) in enumerate(zip(npArrays, keys)):
            dest.create_dataset(key, data=npList)


def readHDF5Data(path: list, settings: dict, fileName:str = 'pynoise', settingsName: str = './settings/default.json'):
    '''
    Reads the data at the path destination of an hdf5 file.

    Inputs:
    - path: list containing the path to the data destinataion
    - settings: dictionary containing runtimee settings
    - fileName: string name of the h5 file to read from. 'pynoise' and 'processing_data' have a specific format to search, all other files follow user paths
    - settingsName: string path to settings file--not required if fileName is not pynoise or processing_data

    Outputs:
    data: a dictionary of the data at the destination
    '''
    fileName = fileName + '.h5'
    filePath = os.path.join(settings['Input/Output Settings']['Save directory'], fileName)
    try:
        with h5py.File(filePath, 'r') as file:
            group = file
            
            # if pynoise or processing_data, find correct settings
            if fileName == 'pynoise.h5' or fileName == 'processing_data.h5':
                settingsName = settingsName[settingsName.rfind('/')+1:]
                # if the settingsName does not exist, data does not exist
                if settingsName not in file:
                    return None
                group = findMatchingSettings(file[settingsName], settings, True)
                # if iteration could not be found, data does not exist
                if group is None:
                    return None
            
            # travel to destination
            dest = travelDownHDF5Read(group, path)
    
            # if destination could not be found, the data does not exist. Exit without reading data
            if dest is None:
                return None
            
            data = {}
            for key in dest.keys():
                data[key] = dest[key][()]
            return data
    except FileNotFoundError:
        return None

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


def findMatchingSettings(group, settings: dict, read: bool=False):
    '''
    Helper function to determine which iteration number has settings that match. If none match, create a new iteration and add the settings

    Inputs:
    - group: the h5 group to analyze
    - settings: dictionary containing runtime settings
    - read: bool indicating if this is being called for reading only

    Outputs:
    - the group to write settings to, or None if we are reading and the group wasn't found
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
    
    # if we reach here, settings were not found.
    # leave for reading only instances
    if read:
        return None

    # create a new iteration group and write the settings to it
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
            if subvalue is None:
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




def exportFissionChamberData(settings: dict = {}):

    # remove duplicate iterations (e.g. same input file/nperseg/dwell time, but a true/false setting was changed creating a new iteration)
    removeDuplicates(settings=settings)
    filePath = os.path.join(settings['Input/Output Settings']['Save directory'], 'pynoise.h5')
    apsd_keys = []
    cpsd_keys = []

    # collect APSD output
    with h5py.File(filePath, 'r') as file:
        for key in file.keys():
            if 'fission_chamber_setting' in key:
                apsd_keys.append(key)
    
    apsd_output = extractAPSD(settings=settings, apsd_keys=apsd_keys)

    
    # collect CPSD output
    with h5py.File(filePath, 'r') as file:
        for key in file.keys():
            if 'cpsd_' in key:
                cpsd_keys.append(key)
    
    cpsd_output = extractCPSD(settings=settings, cpsd_keys=cpsd_keys)


    # write output to file
    with open('fission_chamber_tabular.csv', 'w+') as file:
        # write headers
        file.write('APSD,,,,,,,,,,,,, CPSD\n')
        file.write('Wattage,C1,, C2,, C3,, C4,, , , , , Wattage, C1/C2,, C1/C3,, C1/C4,, C2/C3,, C2/C4,, C3/C4\n')
        
        # parse output
        # take alpha + uncertainty value from output tuple, connect to wattage
        # use 2d list since multiple runs per wattage is possible
        for (apsd_wattage, apsd_vals), (cpsd_wattage, cpsd_vals) in zip(apsd_output.items(), cpsd_output.items()):
            apsd_output_list = []
            apsd_write_list = []
            for i in range(4):
                apsd_output_list.append([])
            for val in apsd_vals:
                # val == ('C#', ',', 'alpha_val', ',', 'uncertainty_val')
                indice, filler, alpha, filler, uncertainty = val
                indice = int(val[0][-1:]) - 1     
                apsd_output_list[indice].append(alpha + ',' + uncertainty + ',')
            
            # while data still in apsd_output_list
            while not apsd_output_list.count([]) == len(apsd_output_list):
                apsd_file_write_string = ""
                for chamber in apsd_output_list:
                    apsd_file_write_string += chamber[0]
                    chamber.pop(0)
                apsd_write_list.append(apsd_file_write_string)
            
            cpsd_output_list = []
            cpsd_write_list = []
            for i in range(6):
                cpsd_output_list.append([])
            for val in cpsd_vals:
                # val == ('C#/C#', ',', 'alpha_val', ',', 'uncertainty_val')
                chambers, filler, alpha, filler, uncertainty = val

                # create indice by adding the two chamber numbers together
                # since C1 + C4 and C2 + C3 lead to same value, increase C2 + C3 by 1
                indice = int(chambers[1]) + int(chambers[4]) - 3
                if 'C1' not in chambers:
                    indice += 1
                cpsd_output_list[indice].append(alpha + ',' + uncertainty + ',')

            # while data still in cpsd_output_list
            while not cpsd_output_list.count([]) == len(cpsd_output_list):
                cpsd_file_write_string = ""
                for chamber in cpsd_output_list:
                    cpsd_file_write_string += chamber[0]
                    chamber.pop(0)
                cpsd_write_list.append(cpsd_file_write_string)
            
            # write parsed output to file
            for apsd_write, cpsd_write in zip_longest(apsd_write_list, cpsd_write_list,fillvalue=',,,,,,,,'):
                file.write(apsd_wattage + ',' + apsd_write + ',,,,' + cpsd_wattage + ',' + cpsd_write + '\n')
    

def extractAPSD(settings: dict = {}, apsd_keys:list = []):
    filePath = os.path.join(settings['Input/Output Settings']['Save directory'], 'pynoise.h5')
    output = defaultdict(list)

    # open file, go thru each iteration
    with h5py.File(filePath, 'r') as file:
        for key in apsd_keys:
            iterations = file[key]
            for iteration_num in iterations:

                # get chamber number
                file_name = iterations[iteration_num]["settings"]["Input-Output Settings"]["Input file-folder"][()]
                if isinstance(file_name, np.ndarray):
                    file_name = file_name[0]
                file_name = file_name.decode('utf-8')
                split_file_name = file_name.split('/')
                chamber_num = split_file_name[3][:2]

                # find wattage from input file name
                wattage_index = split_file_name[3].find('W')

                end_index = wattage_index

                while end_index > 0:
                    if split_file_name[3][end_index] == '-': break
                    end_index = end_index - 1
                
                start_index = end_index

                run_num = Path(file_name).stem
                run_num = run_num[(len(run_num) - 1)]
                wattage_str = split_file_name[3][start_index + 1 : wattage_index + 1] + '_' + run_num

                # get alpha + uncertainty
                try:
                    alpha_uncertainty = iterations[iteration_num]["CohnAlpha"]["Fit"]["alpha_uncertainty"][()]
                except KeyError:
                    continue

                # store output
                line = (str(chamber_num),',', str(alpha_uncertainty[0]), ',', str(alpha_uncertainty[1]))
                output[wattage_str].append(line)
            
            # sort output
            for key in output:
                output[key].sort()
    return output


def extractCPSD(settings: dict = {}, cpsd_keys:list = []):
    filePath = os.path.join(settings['Input/Output Settings']['Save directory'], 'pynoise.h5')
    output = defaultdict(list)

    # open file, go thru iterations
    with h5py.File(filePath, 'r') as file:
        for key in cpsd_keys:
            iterations = file[key]
            for iteration_num in iterations:
                # get chamber number
                chamber_string = ""
                split_file_name = ""
                file_name_list = iterations[iteration_num]["settings"]["Input-Output Settings"]["Input file-folder"][()]
                if not isinstance(file_name_list, np.ndarray):
                    file_name_list = [file_name_list]
                for item in file_name_list:
                    file_name = item.decode('utf-8')
                    split_file_name = file_name.split('/')
                    chamber_num = split_file_name[3][:2]
                    chamber_string += (chamber_num + '/')
                chamber_string = chamber_string[:-1]

                # find wattage from input file name
                wattage_index = split_file_name[3].find('W')
                end_index = wattage_index
                while end_index > 0:
                    if split_file_name[3][end_index] == '-': break
                    end_index = end_index - 1
                start_index = end_index

                run_num = Path(file_name).stem
                run_num = run_num[(len(run_num) - 1)]
                wattage_str = split_file_name[3][start_index + 1 : wattage_index + 1] + '_' + run_num

                # get alpha + uncertainty
                alpha_uncertainty = iterations[iteration_num]["CohnAlpha"]["Fit"]["alpha_uncertainty"][()]
                
                # store output
                line = (str(chamber_string),',', str(alpha_uncertainty[0]), ',', str(alpha_uncertainty[1]))
                output[wattage_str].append(line)

        # sort output
        for key in output:
            output[key].sort()

    return output


def removeDuplicates(settings:dict = {}):

    filePath = os.path.join(settings['Input/Output Settings']['Save directory'], 'pynoise.h5')

    with h5py.File(filePath, 'a') as file:
        # go through all settings + iterations, ignore default.json
        for key in file.keys():
            if 'default.json' not in key:
                iterations = file[key]
                to_delete = []
                dupe_check = {}
                for iteration_num in iterations:

                    # grab file name from iteration
                    # if stored within a list, then combine all file names into one string
                    combined_file_names = ""
                    file_name_list = iterations[iteration_num]["settings"]["Input-Output Settings"]["Input file-folder"][()]

                    if isinstance(file_name_list, np.ndarray):
                        for file_name in file_name_list:
                            combined_file_names += file_name.decode('utf-8')
                    else:
                        combined_file_names += file_name_list.decode('utf-8')
                    
                    # try to get iteration nperseg; if not provided, set value to 0
                    try:
                        iteration_nperseg = iterations[iteration_num]["settings"]["CohnAlpha Settings"]["nperseg"][()]
                    except KeyError:
                        iteration_nperseg = 0
                    # try to get iteration dwell time; if not provided, set value to 0
                    try:
                        iteration_dwell_time = iterations[iteration_num]["settings"]["CohnAlpha Settings"]["Dwell Time"][()]
                    except KeyError:
                        iteration_dwell_time = 0
                    
                    # combine file name(s), dwell time, nperseg into tuple
                    # use tuple to check if already inserted
                    # if not inserted, insert into dict. If already inserted, then add to to_delete list
                    data_tuple = (combined_file_names, iteration_nperseg, iteration_dwell_time)
                    if data_tuple in dupe_check:
                        to_delete.append(iteration_num)
                        continue
                    dupe_check[data_tuple] = True
                
                # delete iterations within to_delete list
                while len(to_delete) != 0:
                    del iterations[to_delete[0]]
                    to_delete.pop(0)