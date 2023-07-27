from tqdm import tqdm

class Event:
    def __init__(self, time, channel = None):
        self.time = time
        self.channel = channel

    def getTime(self):
        return self.time
    
    def getChannel(self):
        return self.channel



def createEventsListFromTxtFile(filePath,timeCol=0,channelCol=None,quiet=False,folder=False):
    events = []
    if not quiet and not folder:
        print('Loading data...')
    with open(filePath, 'r') as file:
        if not folder:
            file = tqdm(file)
        for line in file:
            columns = line.strip().split()
            time = columns[timeCol]
            if channelCol is None:
                channel = None
                event = Event(float(time))
            else:
                channel = columns[channelCol]
                event = Event(float(time), int(channel))
            events.append(event)
    return events
