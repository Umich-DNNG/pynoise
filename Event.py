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
                                channel:int = None,
                                isColumn:bool = True,
                                quiet:bool = False,
                                folder:bool = False):
    
    '''Creates an event list from a text file.
    
    Inputs:
    - path: a string that indicates the absolute path of the input file.
    - timeCol: a integer indicating which column in the 
    file holds the time data. If not given, assumes column 0.
    - channel: an integer indicating which column in the file 
    holds the channel data or what the channel for all data 
    points should be. If not given, assumes no channel column.
    - isColumn: a boolean that determines whether channel is a column 
    or channel value. If not given, assumes True (channel is a column).
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
            timeIn = columns[timeCol]
            if isColumn:
                # If there is no channel column, set the channel to None.
                if channel is None:
                    # Store the time data in an event object.
                    event = Event(float(timeIn))
                # Otherwise, save the channel data from the appropriate column.
                else:
                    channelIn = columns[channel]
                    # Store the time and channel data in an event object.
                    event = Event(float(timeIn), int(channelIn))
            else:
                event = Event(float(timeIn), channel)
            # Add the current Event to the events list.  
            events.append(event)
    file.close()
    # Return the events list.
    return events
