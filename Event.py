class Event:
    def __init__(self, time, channel = None):
        self.time = time
        self.channel = channel

    def getTime(self):
        return self.time
    
    def getChannel(self):
        return self.channel



def createEventsListFromTxtFile(filePath,timeCol,channelCol):
    events = []
    with open(filePath, 'r') as file:
        for line in file:
            columns = line.strip().split()
            channel = columns[channelCol]
            time = columns[timeCol]
            event = Event(float(time), int(channel))
            events.append(event)
    return events
