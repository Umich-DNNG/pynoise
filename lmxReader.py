import sys
import re
import numpy
from tqdm import tqdm
import math
from Event import Event



#--------------------------------------------------------
def readData(file, ticklength, counts):

    def readPair(lmxfile):

        # numberstring = lmxfile.read(4)
        # tickstring = lmxfile.read(4)

        # if numberstring:
        try:
            number = int.from_bytes(lmxfile.read(4),
                                    byteorder=sys.byteorder,
                                    signed=False)
            tick = int.from_bytes(lmxfile.read(4),
                                    byteorder=sys.byteorder,
                                    signed=False)

            return number, tick  # , numberstring, tickstring

        except:

            return None, None  # , numberstring, tickstring

    def getDetectorIndices(number):

        indices = []
        i = 1
        while number:

            if number & 1: indices.append(i)
            number >>= 1
            i += 1

        return indices

    events = []
    addclock = 0

    finaltime = 0.0

    while True:

        number, tick = readPair(file)

        if number:

            # accumulate time
            time = (tick + addclock) * ticklength

            # loop over indices
            for index in getDetectorIndices(number):
                events.append(Event(time,index))
                # pbar.update(10)

        elif number == 0:

            # flag, flagtick, flagstring, flagtickstring = readPair( lmxfile )
            flag, flagtick = readPair(file)

            # rollover flag
            if flag == 1:

                print('ROOOOOLLLLLLL OOOOOVEEEEER')
                addclock = addclock + tick

            # stop recording flag
            elif flag == 2:

                print('active mode: stop recording data')

            # start recording flag
            elif flag == 3:

                print('active mode: start recording data')

            # end of measurement flag
            elif flag == 4294967295:

                finaltime = (flagtick + addclock) * ticklength
                print('End of measurement. Measurement time (ns): ', finaltime)
                break

            else:

                print('unknown flag or no event during tick?', flag, flagtick)

        else:

            print('Unexpected end of file')
            break

    return events, finaltime



#--------------------------------------------------------
def readHeader(lmxfile):

        def readKeyValue(line):
            pieces = line.decode('ascii').split(sep=':', maxsplit=1)
            if len(pieces) == 1:
                return pieces[0].rstrip().strip(), None

            else:
                return pieces[0].rstrip().strip(), pieces[1].rstrip().strip()
            
        #returns just the value, not unit (changed from other implementation, not using ValueUnit test)
        def parseValueUnit(string: str):
            if string.lower() != 'unknown':
                pattern = re.compile('^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)' + '([\ ]*[\[](.*)[\]])?$')
                match = pattern.match(string)

                if match:
                    return (float(match[1]))

                else:
                    raise ValueError('Expected a value with a unit, got \'' + string + '\' instead')

            else:
                return None

        def extractRowRatio(string: str):
            try:
                return float(string)

            except ValueError:
                raise ValueError('Expected a value without a unit, got \'' + string + '\' instead')

        ticklength = None
        MsmtDuration = None
        AvgCountRate = None
        FaceToSource = None
        CenterToFloor = None
        FifoLostCounts = None

        RR12, RR13, RR23 = None, None, None

        header_dict = {'Comment': []}
        key, value = None, None
        while key != 'BinaryDataFollows':

            key, value = readKeyValue(lmxfile.readline())
            if key == 'Comment':

                header_dict['Comment'].append(value)

            elif key == 'AverageCountRate':

                AvgCountRate = parseValueUnit(value)

            elif key == 'DistanceDetFaceToSource':

                FaceToSource = parseValueUnit(value)

            elif key == 'DistanceDetCenterToFloor':

                CenterToFloor = parseValueUnit(value)

            elif key == 'BinaryDataClockTickLength':

                ticklength = parseValueUnit(value)

            elif key == 'DurationRealTime':

                MsmtDuration = parseValueUnit(value)

            elif key == 'DistanceDetCenterToFloor':

                CenterToFloor = parseValueUnit(value)

            elif key == 'FifoLostCounts':

                FifoLostCounts = int(value)

            elif key == 'RowRatio(1/2)':

                RR12 = extractRowRatio(value)

            elif key == 'RowRatio(1/3)':

                RR13 = extractRowRatio(value)

            elif key == 'RowRatio(2/3)':

                RR23 = extractRowRatio(value)

            elif key not in header_dict:

                header_dict[key] = value

            else:

                print('This key is present twice: ' + key)

        return ticklength, header_dict['InternalScaler']




#--------------------------------------------------------



def readLMXFile(fileName):
        # open the lmx file
    print('Opening file \'' + fileName + '\'')
    with open(fileName, 'rb') as lmxfile:

        # read the header
        tickLength, internalScaler = readHeader(lmxfile)

        # verify required data
        if not tickLength:
            raise RuntimeError('Tick length not found in header, '
                               + 'cannot convert to absolute time')

        # read the events
        events, endtime = readData(lmxfile, tickLength, internalScaler)

    return events



