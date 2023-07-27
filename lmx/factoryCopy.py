# standard imports
from typing import List
import glob
from math import log
import sys
import re

# third party imports

# local imports
from lmx.Header import Header
from lmx.Event import Event
from lmx.LMXFile import LMXFile
from lmx.ValueUnit import ValueUnit

def readLMXFile( name : str ) :
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

    def readHeader( lmxfile ) :

        def readKeyValue( line ) :

            pieces = line.decode( 'ascii' ).split( sep = ':', maxsplit = 1 )
            if len( pieces ) == 1 :

                return pieces[0].rstrip().strip(), None

            else :

                return pieces[0].rstrip().strip(), pieces[1].rstrip().strip()

        def parseValueUnit( string : str ) :

            pattern = re.compile( '^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)'
                                  + '([\ ]*[\[](.*)[\]])?$' )

            if string.lower() != 'unknown' :

                match = pattern.match( string )
                if match :

                    return ValueUnit( float( match[1] ), match[4] )

                else :

                    raise ValueError( 'Expected a value with a unit, got \''
                                      + string + '\' instead' )

            else :

                return None

        def extractRowRatio( string : str ) :

            try :

                return float( string )

            except ValueError :

                raise ValueError( 'Expected a value without a unit, got \''
                                  + string + '\' instead' )

        ticklength = None
        MsmtDuration = None
        AvgCountRate = None
        FaceToSource = None
        CenterToFloor = None
        FifoLostCounts = None

        RR12, RR13, RR23 = None, None, None

        header = { 'Comment' : [] }
        key, value = None, None
        while key != 'BinaryDataFollows' :

            key, value = readKeyValue( lmxfile.readline() )
            if key == 'Comment' :

                header[ 'Comment' ].append( value )

            elif key == 'AverageCountRate' :

                AvgCountRate = parseValueUnit( value )

            elif key == 'DistanceDetFaceToSource' :

                FaceToSource = parseValueUnit( value )

            elif key == 'DistanceDetCenterToFloor' :

                CenterToFloor = parseValueUnit( value )

            elif key == 'BinaryDataClockTickLength' :

                ticklength = parseValueUnit( value )

            elif key == 'DurationRealTime' :

                MsmtDuration = parseValueUnit( value )

            elif key == 'DistanceDetCenterToFloor' :

                CenterToFloor = parseValueUnit( value )

            elif key == 'FifoLostCounts' :

                FifoLostCounts = int( value )

            elif key == 'RowRatio(1/2)' :

                RR12 = extractRowRatio( value )

            elif key == 'RowRatio(1/3)' :

                RR13 = extractRowRatio( value )

            elif key == 'RowRatio(2/3)' :

                RR23 = extractRowRatio( value )

            elif key not in header :

                header[ key ] = value

            else :

                print( 'This key is present twice: ' + key )

        return Header( ticklength = ticklength, MsmtDuration = MsmtDuration,
                       AvgCountRate = AvgCountRate, FaceToSource = FaceToSource,
                       CenterToFloor = CenterToFloor,
                       FifoLostCounts = FifoLostCounts, RR12 = RR12,
                       RR13 = RR13, RR23 = RR23, other = header )

    def readData( lmxfile, ticklength ) :

        def readPair( lmxfile ) :

            numberstring = lmxfile.read(4)
            tickstring = lmxfile.read(4)

            if numberstring :

                number = int.from_bytes( numberstring,
                                         byteorder = sys.byteorder,
                                         signed = False )
                tick = int.from_bytes( tickstring,
                                       byteorder = sys.byteorder,
                                       signed = False )

                return number, tick #, numberstring, tickstring

            else :

                return None, None #, numberstring, tickstring

        def getDetectorIndices( number ) :

            indices = []
            i = 1
            while number :

                if number & 1 : indices.append( i )
                number >>= 1
                i += 1

            return indices

        events = []
        addclock = 0

        finaltime = 0.0

        while True :

            number, tick = readPair( lmxfile )

            if number :

                # accumulate time
                time = ( tick + addclock ) * ticklength

                # loop over indices
                for index in getDetectorIndices( number ) :

                    events.append( Event( index, time ) )

            elif number == 0 :

                #flag, flagtick, flagstring, flagtickstring = readPair( lmxfile )
                flag, flagtick = readPair( lmxfile )

                # rollover flag
                if flag == 1 :

                    print( 'ROOOOOLLLLLLL OOOOOVEEEEER' )
                    addclock = addclock + tick

                # stop recording flag
                elif flag == 2 :

                    print('active mode: stop recording data')

                # start recording flag
                elif flag == 3 :

                    print('active mode: start recording data')

                # end of measurement flag
                elif flag == 4294967295:

                    finaltime = ( flagtick + addclock ) * ticklength
                    print('End of measurement. Measurement time (ns): ', finaltime)
                    break

                else :

                    print( 'unknown flag or no event during tick?', flag, flagtick )

            else :

                print( 'Unexpected end of file' )
                break

        return events, finaltime

    # open the lmx file
    print( 'Opening file \'' + name + '\'' )
    with open(name, 'rb') as lmxfile:

        # read the header
        header = readHeader( lmxfile )

        # verify required data
        if not header.ticklength :

            raise RuntimeError( 'Tick length not found in header, '
                                + 'cannot convert to absolute time' )

        # read the events
        events, endtime = readData( lmxfile, header.ticklength.value )
        return LMXFile( header, events )
