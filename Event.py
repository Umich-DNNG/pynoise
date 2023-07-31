'''The file that defines and stores Event objects.'''



# Necessary imports.
from tqdm import tqdm



class Event:

    '''The class for each radiation measurement. Stores the time 
    of measurement and channel that it was recorded by (if given).'''


    def __init__(self, time, channel = None):

        '''Initializes the measurement time and channel for an Event.
        
        Inputs:
        - time: the time (in nanoseconds) that the measurement was taken.
        - channel: the channel the measurement was taken 
        on. If not given, assumes no channel data.'''


        # Store the time and channel data accordingly.
        self.time = time
        self.channel = channel



def createEventsListFromTxtFile(path:str,
                                timeCol:int = 0,
                                channelCol:int = None,
                                quiet:bool = False,
                                folder:bool = False):
    
    '''Creates an event list from a text file.
    
    Inputs:
    - path: a string that indicates the absolute path of the input file.
    - timeCol: a integer indicating which column in the 
    file holds the time data. If not given, assumes column 0.
    - channelCol: an integer indicating which column in the file 
    holds the channel data. If not given, assumes no channel column.
    - quiet: a boolean indicating whether or not print statements should 
    be silenced. If not given, assumes False (uses print statements).
    - folder: a boolean indicating whether or not this file is for 
    folder analysis. If not given, assumes False (single file).
    
    Outputs:
    - events: the list containing one Event 
    object for each row in the text file.'''


    # Initialize the list.
    events = []
    # If not in quiet nor folder mode, print 
    # that data loading is in progress.
    if not quiet and not folder:
        print('Loading data...')
    # Open the given file in read mode.
    with open(path, 'r') as file:
        # If not in folder mode, make a progress bar.
        if not folder:
            file = tqdm(file)
        # For each line in the file:
        for line in file:
            # Get rid of trailing and leading 
            # whitespace and split the columns up.
            columns = line.strip().split()
            # Save the time data from the appropriate column.
            time = columns[timeCol]
            # If there is no channel column, set the channel to None.
            if channelCol is None:
                channel = None
            # Otherwise, save the channel data from the appropriate column.
            else:
                channel = columns[channelCol]
            # Store the time and channel data in an 
            # event object and add it to the events list.
            event = Event(float(time), int(channel))
            events.append(event)
    # Return the events list.
    return events
