# standard imports
import unittest

# third party imports

# local imports
from lmx.factory import readLMXFile
from lmx.Event import Event

class TestFactory( unittest.TestCase ) :
    """unit test for the readLMXFile functions."""

    def test_readLMXFile( self ) :

        filename = 'lmx/test/resources/2017_01_26_184649_stripped.lmx'

        myLMXFile = readLMXFile( name = filename )

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
                  'Comment'                       : [ 'If all channels are zero, this indicates channels',
                                                      'in next event is a flag (not a real event)',
                                                      'Flag = 0x00000001 (Clock rollover occurred)',
                                                      'Flag = 0x00000002 (Gate input started)',
                                                      'Flag = 0x00000003 (Gate input ended)',
                                                      'Flag = 0xFFFFFFFF (End of binary data)' ],
                  'BinaryDataEventSizeInBytes'    : '8',
                  'BinaryDataChannelFormat'       : 'unsigned int32',
                  'BinaryDataClockFormat'         : 'unsigned int32',
                  'BinaryDataActiveChannels'      : '0xFFFFFFFF',
                  'BinaryDataFollows'             : '' }

        events = [ Event( detector = 11, time =   274657280. ),
                   Event( detector =  1, time =  3283262208. ),
                   Event( detector = 20, time =  5759411456. ),
                   Event( detector = 21, time =  9118155648. ),
                   Event( detector =  9, time = 11090793344. ),
                   Event( detector =  6, time = 12274567552. ),
                   Event( detector =  5, time = 13335184896. ),
                   Event( detector =  8, time = 13388469632. ),
                   Event( detector = 20, time = 14469435776. ),
                   Event( detector = 25, time = 15519375616. ),
                   Event( detector =  8, time = 15972364416. ),
                   Event( detector = 23, time = 22447522176. ),
                   Event( detector = 30, time = 22686134144. ),
                   Event( detector = 29, time = 22953387008. ),
                   Event( detector = 21, time = 23004926976. ),
                   Event( detector = 31, time = 25179997184. ),
                   Event( detector = 11, time = 26850289408. ),
                   Event( detector = 20, time = 29378750336. ),
                   Event( detector =  2, time = 32888332800. ) ]

        self.assertEqual( myLMXFile.header.ticklength.value, 128.0 )
        self.assertEqual( myLMXFile.header.ticklength.unit, 'ns' )
        self.assertEqual( myLMXFile.header.MsmtDuration.value, 1800 )
        self.assertEqual( myLMXFile.header.MsmtDuration.unit, 's' )
        self.assertEqual( myLMXFile.header.AvgCountRate.value, 0.75 )
        self.assertEqual( myLMXFile.header.AvgCountRate.unit, 'counts/s' )
        self.assertEqual( myLMXFile.header.FaceToSource.value, 15.0 )
        self.assertEqual( myLMXFile.header.FaceToSource.unit, 'cm' )
        self.assertEqual( myLMXFile.header.CenterToFloor.value, 69.0 )
        self.assertEqual( myLMXFile.header.CenterToFloor.unit, 'cm' )
        self.assertEqual( myLMXFile.header.FifoLostCounts, 0.0 )
        self.assertEqual( myLMXFile.header.RR12, 0.758 )
        self.assertEqual( myLMXFile.header.RR13, 0.877 )
        self.assertEqual( myLMXFile.header.RR23, 1.156 )
        self.assertEqual( myLMXFile.header.other, stuff )
        self.assertEqual( myLMXFile.events, events )

if __name__ == '__main__' :

    unittest.main()
