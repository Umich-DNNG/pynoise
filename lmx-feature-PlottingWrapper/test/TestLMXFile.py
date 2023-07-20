# standard imports
import unittest

# third party imports

# local imports
from lmx.Event import Event
from lmx.Header import Header
from lmx.LMXFile import LMXFile
from lmx.ValueUnit import ValueUnit

class TestEvent( unittest.TestCase ) :
    """Unit test for the Event class."""

    def test_constructors( self ) :

        stuff = { 'ListModeDataFileVersion'       : '1.06',
                  'InstrumentType'                : 'Neutron Multiplicity',
                  'InstrumentModel'               : 'MC-15',
                  'SerialNumber'                  : 'S/N LANL 001',
                  'HardwareVersion'               : 'MB6-E17P',
                  'FirmwareVersion'               : 'faa00720',
                  'CCodeVersion'                  : '28000915',
                  'LCDVersion'                    : '168C',
                  'MeasurementID'                 : '2017_01_26_184649',
                  'MeasurementDescription'        : 'GTFO BATHROOM BACKGROUND',
                  'MeasurementSample'             : '2 of 2',
                  'MeasurementMode'               : 'Multiple',
                  'FrontPanelConfig'              : 'Together',
                  'AnalysisChannels'              : '0x7FFF7FFF',
                  'DateStart'                     : '2017-01-26 [Z]',
                  'TimeStart'                     : '18:46:49 [Z]',
                  'InternalScaler'                : '1356',
                  'HighVoltageSetPoint'           : '1680 [V]',
                  'HighVoltageActual'             : '1683 [V]',
                  'TemperatureCPU'                : '75 [C]',
                  'TemperatureLCD'                : '50 [C]',
                  'TemperatureInternal'           : '0 [C]',
                  'HumidityInternal'              : '-2 [%]',
                  'BarometerElevation'            : '0 [m]',
                  'FirmwareChannelDeadtime'       : '256 [ns]',
                  'Comment'                       : 'If all channels are zero, this indicates channels'
                                                    + 'in next event is a flag (not a real event)'
                                                    + 'Flag = 0x00000001 (Clock rollover occurred)'
                                                    + 'Flag = 0x00000002 (Gate input started)'
                                                    + 'Flag = 0x00000003 (Gate input ended)'
                                                    + 'Flag = 0xFFFFFFFF (End of binary data)',
                  'BinaryDataEventSizeInBytes'    : '8',
                  'BinaryDataChannelFormat'       : 'unsigned int32',
                  'BinaryDataClockFormat'         : 'unsigned int32',
                  'BinaryDataActiveChannels'      : '0xFFFFFFFF' }

        myHeader = Header( ticklength = ValueUnit( 128, 'ns' ), MsmtDuration = ValueUnit( 1800, 's' ),
                 AvgCountRate = ValueUnit( 0.75, 'counts/s' ), FaceToSource = ValueUnit( 15.0, 'cm' ),
                 CenterToFloor = ValueUnit( 69.0, 'cm' ), FifoLostCounts = 0, RR12 = 0.758, RR13 = 0.877,
                 RR23 = 1.156, other = stuff )

        myEvents = [ Event(detector = 7, time = 54), Event(detector = 7, time = 55) ]

        myLMXFile = LMXFile( myHeader, myEvents )

        self.assertEqual( myLMXFile.header, myHeader )
        self.assertEqual( myLMXFile.events, myEvents )

        self.assertEqual( myLMXFile.detectorEvents( 1 ), [] )
        self.assertEqual( myLMXFile.detectorEvents( 7 ), [ Event(detector = 7, time = 54), Event(detector = 7, time = 55) ] )

        #Check number of events occurring in each detector:
        self.assertEqual( myLMXFile.detectorCounts( 7 ), 2 )
        self.assertEqual( myLMXFile.detectorCounts( 1 ), 0 )

        #Check total counts in each detector:
        self.assertEqual( myLMXFile.allDetectorCounts(), { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 2 } )

if __name__ == '__main__' :

    unittest.main()
