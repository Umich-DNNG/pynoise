import os
from tqdm import tqdm
import h5py
import numpy as np


def writeData(npArrays, keys:list = [], fileName:str = "", fileFormat:str = 'hdf5'):
    '''
    Saves a list of numpy arrays to a file in hdf5 format

    Inputs:
    - npArrays: numpy lists to be saved in the file
    - keys: the keys for each of the data set. Assuming parallel list with npArrays
    - fileName: Name of the hdf5 file
    - fileFormat: type of format to save file into
    (TODO: will make a universal import/export, use fileFormat to choose between csv and hdf5 and such)
    '''

    # TODO: make work with all arguments
    # for now, just try and use hdf5 a little, get a feel for it

    fileName = fileName + '.h5'
    with h5py.File(fileName, 'w') as file:
        for i, (npList, key) in tqdm(enumerate(zip(npArrays, keys))):
            file.create_dataset(key, data=npList)





def readData(fileName:str = ""):
    returnList = []
    fileName = fileName + '.h5'
    with h5py.File(fileName, 'r') as file:
        for i, key in tqdm(enumerate(file.keys())):
            # read in array as numpy array, append to return list
            # [()] means to read the entire array in and changes it from hdf5 dataset to a numpy array
            returnList.append(file[key][()])
    return returnList
