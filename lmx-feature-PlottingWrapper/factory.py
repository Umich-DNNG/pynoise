# standard imports
import math
import numpy
from tqdm import tqdm
import sys
import re

# third party imports

# local imports
from lmx.Header import Header
from lmx.Event import Event
from lmx.LMXFile import LMXFile
from lmx.ValueUnit import ValueUnit

def readLMXFile(name: str):
    """Read an LMX binary file and return an LMX

       Usage:

           # open file
           path = '/some/path/to/MyLMXFile.lmx'
           lmx = readLMXFile( path )

           # do stuff with it
           print( lmx.header.ticklength )

       Arguments:
           name : the name of the file to be opened

       Exceptions:
           ValueError : something went wrong
    """

    def readHeader(lmxfile):

        def readKeyValue(line):
            pieces = line.decode('ascii').split(sep=':', maxsplit=1)
            if len(pieces) == 1:
                return pieces[0].rstrip().strip(), None

            else:
                return pieces[0].rstrip().strip(), pieces[1].rstrip().strip()

        def parseValueUnit(string: str):
            if string.lower() != 'unknown':
                pattern = re.compile('^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)' + '([\ ]*[\[](.*)[\]])?$')
                match = pattern.match(string)

                if match:
                    return ValueUnit(float(match[1]), match[4])

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

            elif key == 'RowRatio(1/2)' or key == 'RowRatio(1 / 2)':

                RR12 = extractRowRatio(value)

            elif key == 'RowRatio(1/3)' or key == 'RowRatio(1 / 3)':

                RR13 = extractRowRatio(value)

            elif key == 'RowRatio(2/3)' or key == 'RowRatio(2 / 3)':

                RR23 = extractRowRatio(value)

            elif key not in header_dict:

                header_dict[key] = value

            else:

                print('This key is present twice: ' + key)

        return Header(ticklength=ticklength, MsmtDuration=MsmtDuration,
                      AvgCountRate=AvgCountRate, FaceToSource=FaceToSource,
                      CenterToFloor=CenterToFloor,
                      FifoLostCounts=FifoLostCounts, RR12=RR12,
                      RR13=RR13, RR23=RR23, other=header_dict)

    def readData(file, ticklength):

        def getDetectorIndices(number):
            indices = []

            logged = math.log2(number)
            if logged%1 == 0 :
                indices.append(int(logged)+1)

            else:
                i = 1
                while number:
                    if number & 1: indices.append(i)
                    number >>= 1
                    i += 1

            return indices

        try:
            data = numpy.fromfile(file,dtype=("uint32"))
        except RuntimeError:
            raise RuntimeError(" Binary data was unable to be read")
            return

        numbers = data[::2]
        ticks = data[1::2].astype(numpy.int64)

        # Account for rollovers
        where_zeros = numpy.where(numbers == 0)[0]
        where_flags = [flag for flag in where_zeros+1 if flag<len(numbers)]
        addclock = [ticks[flag + 1] for flag in where_flags if numbers[flag]==1]

        if numbers[-1]!= 4294967295:
            print(" End of file flag not found. Events will continue to be generated.")

        for indexer, value in enumerate([flag for flag in where_flags if numbers[flag]==1]):
            ticks[value + 1:] += addclock[indexer] + ticks[value] - ticks[value+1]
            print(' ROOOOOLLLLLLL OOOOOVEEEEER')

        finaltime = 0
        for special_flag in where_flags:
            # rollover flag
            if numbers[special_flag] == 0 or numbers[special_flag] == 1:
                pass

            # stop recording flag
            elif numbers[special_flag] == 2:
                print(' active mode: stop recording data')

            # start recording flag
            elif numbers[special_flag] == 3:
                print(' active mode: start recording data')

            # end of measurement flag
            elif numbers[special_flag] == 4294967295:
                finaltime = ticks[special_flag]*ticklength

            else:
                print(' unknown flag or no event during tick?', numbers[special_flag], ticks[special_flag])


        numbers = numpy.delete(numbers, numpy.concatenate((where_zeros, where_flags)))
        ticks = numpy.delete(ticks, numpy.concatenate((where_zeros, where_flags)))
        where_multi_detector = numpy.where( numpy.log2(numbers)%1 != 0 )[0]
        ticks = ticks * ticklength

        events = []
        start = 0
        if list(where_multi_detector):
            for pos in tqdm(where_multi_detector):
                events.extend([Event(*singlet) for singlet in zip(numbers[start:pos], ticks[start:pos])])
                start = pos + 1

                for index in getDetectorIndices(pos):
                    events.append(Event(index, ticks[pos]))

                while start in where_multi_detector:
                    start += 1

            last = where_multi_detector[-1] + 1
            if last < len(numbers):
                events.extend([Event(*singlet) for singlet in zip(numbers[last:], ticks[last:])])
        else:
            combo_holder = zip(numbers, ticks)
            events = [Event(*singlet) for singlet in tqdm(combo_holder, total=len(numbers))]

        return events, finaltime

    # open the lmx file
    print(' Opening file \'' + name + '\'')
    with open(name, 'rb') as lmxfile:

        # read the header
        header = readHeader(lmxfile)

        # verify required data
        if not header.ticklength:
            raise RuntimeError(' Tick length not found in header, '
                               + 'cannot convert to absolute time')

        # read the events
        events, endtime = readData(lmxfile, header.ticklength.value)
        print(' End of measurement. Measurement time (ns): ', endtime)
        return LMXFile(header, events)

def readLMXFile_old(name: str):
    """Read an LMX binary file and return an LMX

       Usage:

           # open file
           path = '/some/path/to/MyLMXFile.lmx'
           lmx = readLMXFile( path )

           # do stuff with it
           print( lmx.header.ticklength )

       Arguments:
           name : the name of the file to be opened

       Exceptions:
           ValueError : something went wrong
    """

    def readHeader(lmxfile):

        def readKeyValue(line):
            pieces = line.decode('ascii').split(sep=':', maxsplit=1)
            if len(pieces) == 1:
                return pieces[0].rstrip().strip(), None

            else:
                return pieces[0].rstrip().strip(), pieces[1].rstrip().strip()

        def parseValueUnit(string: str):
            if string.lower() != 'unknown':
                pattern = re.compile('^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)' + '([\ ]*[\[](.*)[\]])?$')
                match = pattern.match(string)

                if match:
                    return ValueUnit(float(match[1]), match[4])

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

            elif key == 'RowRatio(1/2)' or key == 'RowRatio(1 / 2)':

                RR12 = extractRowRatio(value)

            elif key == 'RowRatio(1/3)' or key == 'RowRatio(1 / 3)':

                RR13 = extractRowRatio(value)

            elif key == 'RowRatio(2/3)' or key == 'RowRatio(2 / 3)':

                RR23 = extractRowRatio(value)

            elif key not in header_dict:

                header_dict[key] = value

            else:

                print('This key is present twice: ' + key)

        return Header(ticklength=ticklength, MsmtDuration=MsmtDuration,
                      AvgCountRate=AvgCountRate, FaceToSource=FaceToSource,
                      CenterToFloor=CenterToFloor,
                      FifoLostCounts=FifoLostCounts, RR12=RR12,
                      RR13=RR13, RR23=RR23, other=header_dict)

    #def readData(file, ticklength, counts):
    def readData(file, ticklength):

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
                    events.append(Event(index, time))
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

    # open the lmx file
    print('Opening file \'' + name + '\'')
    with open(name, 'rb') as lmxfile:

        # read the header
        header = readHeader(lmxfile)

        # verify required data
        if not header.ticklength:
            raise RuntimeError('Tick length not found in header, '
                               + 'cannot convert to absolute time')

        # read the events
        #events, endtime = readData(lmxfile, header.ticklength.value, int(header.other.get("InternalScaler")))
        events, endtime = readData(lmxfile, header.ticklength.value)
        return LMXFile(header, events)


