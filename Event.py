from tqdm import tqdm

class Event:
    def __init__(self, time, channel = None):
        self.time = time
        self.channel = channel

    def getTime(self):
        return self.time
    
    def getChannel(self):
        return self.channel



def createEventsListFromTxtFile(filePath,timeCol,channelCol,quiet=False):
    events = []
    if not quiet:
        print('Loading data...')
    with open(filePath, 'r') as file:
        for line in tqdm(file):
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
