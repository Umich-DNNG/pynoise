import numpy as np
import pickle
from lmx.factory import *
from operator import itemgetter
from lmx.Event import Event


def ReadToEvents(file, time_list=0, detector_list=None):
    def fileFormatter(data_arr):
        if len(data_arr) < len(data_arr[0]):
            data_arr.T

        sorted(data_arr, key=itemgetter(time_list))
        data_arr.T
        if not detector_list:
            return ToEvents(data_arr[time_list])
        else:
            return ToEvents(data_arr[time_list], data_arr[detector_list])

    if file.endswith(".npy"):
        np_data = np.load(file)
        return fileFormatter(np_data)
    else:
        data_file = open(file, "r")
        data = np.array(data_file.read().splitlines())
        data_file.close()
        return fileFormatter(data)

def toEvents(times: list, detectors: list = None):
    """ Takes a list of times (and optionally a list of detectors) to create Event objects

        Arguments:
            times: values for the time component of the Events
            detectors: values for the detector component of the Events
                       (specifying detectors is an optional feature)

        Returns:
            A list of Event class objects
    """
    events = []
    if not detectors:
        [events.append(Event(1, row)) for row in times]

    else:
        if len(detectors) != len(times):
            raise RuntimeError("Detector list not the same length as time list")
        for i in range(len(times)):
            events.append(Event(int(detectors[i]), float(times[i])))

    return events


def formatForToEvents(data: np.ndarray, times_index: int = 0, detectors_index: int = None):
    """ Takes data read from a file and format for use in toEvents function

    Arguments:
        data: Values obtained from reading a file
        times_index: Position of times list column/row
        detectors_index: Position of detectors list column/row

    Returns:
            A list of Event class objects using toEvents

    """
    if data.ndim == 1:
        return toEvents(data)

    elif data.shape[0] > data.shape[1]:
        data = data.T

    if not detectors_index:
        return toEvents(data[times_index])

    else:
        return toEvents(data[times_index], data[detectors_index])


def eventsFromLMX(file):
    """ Reads and processes an LMX file to create a list of Event types

    Arguments:
        file: An LMX file with appropriate data

    Returns:
            A list of Event class objects using toEvents
    """
    return readLMXFile(file).events


def eventsFromNumpy(file, times_index=0, detectors_index=None):
    """ Reads and processes a Numpy file to create a list of Event types

    Arguments:
        file: A Numpy file with appropriate data
        times_index: Position of the times list column/row
        detectors_index: Position of the detectors list column/row

    Returns:
            A list of Event class objects using toEvents
    """
    data = np.load(file)
    return formatForToEvents(data, times_index, detectors_index)


def eventsFromTxt(file, times_index=0, detectors_index=None):
    """ Reads and processes a text file to create a list of Event types

    Arguments:
        file: A text file with appropriate data
        times_index: Position of the times list column/row
        detectors_index: Position of the detectors list column/row

    Returns:
            A list of Event class objects using toEvents
    """
    data_file = open(file, "r")
    data = np.array(data_file.read().splitlines()).astype(float)
    data_file.close()
    return formatForToEvents(data, times_index, detectors_index)


def eventsFromPickle(file):
    """ Loads list of Event types from Pickle

    Arguments:
        file: A numpy file with pickled object

    Returns:
            A list of Event class objects
    """
    if file.endswith(".npy") is False:
        file = file + ".npy"

    with open(file, "rb") as in_file:
        return pickle.load(in_file)


def saveToPickle(file, events):
    """Save Event data through python pickling

        Arguments:
            file: name of file to be saved to
            events: list of Event types
    """
    if file.endswith(".npy") is False:
        file = file + ".npy"

    with open(file, "wb") as out_file:
        pickle.dump(events, out_file)


def saveToText(file, events):
    """Save Event data to txt file

        Arguments:
            file: name of file to be saved to
            events: list of Event types
    """
    if file.endswith(".txt") is False:
        file = file + ".txt"

    with open(file, 'w') as f:
        f.write('\n'.join('{} {}'.format(event.detector, event.time) for event in events))
