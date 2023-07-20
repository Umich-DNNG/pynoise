# prints .lmx header information


# standard imports

# local imports
from lmx.factory import readLMXFile
from lmx.Header import *

def print_header(lmxfile):
    print('#######################################')
    print('File header information')
    if lmxfile.header.ticklength != None:
        header_tick_length = lmxfile.header.ticklength.value
        print('Tick length = ',header_tick_length,' nsec')
    else:
        header_tick_length = 'N/A'
        print('No tick length listed in the .lmx header.')
    if lmxfile.header.MsmtDuration != None:
        header_measurement_time = lmxfile.header.MsmtDuration.value
        print('Measurement time = ',header_measurement_time,' sec')
    else:
        header_measurement_time = 'N/A'
        print('No measurement time given in the .lmx header.')
    if lmxfile.header.AvgCountRate != None:
        header_count_rate = lmxfile.header.AvgCountRate.value
        print('Count rate = ',header_count_rate,' cts/sec')
    else:
        header_count_rate = 'N/A'
        print('No count rate is listed in the .lmx header.')
    if lmxfile.header.FaceToSource != None:
        header_SD = lmxfile.header.FaceToSource.value
        print('S/D = ',header_SD,' cm')
    else:
        header_SD = 'N/A'
        print('No S/D is in the .lmx header.')
    if lmxfile.header.CenterToFloor != None:
        header_RD = lmxfile.header.CenterToFloor.value
        print('R/D = ',header_RD,' cm')
    else:
        header_RD = 'N/A'
        print('No R/D is in the .lmx header.')
    if lmxfile.header.FifoLostCounts != None:
        header_FIFO = lmxfile.header.FifoLostCounts
        print('FIFO losses = ',header_FIFO)
    else:
        header_FIFO = 'N/A'
        print('FIFO losses are not listed in the .lmx header.')
    if lmxfile.header.RR12 != None:
        header_RR12 = lmxfile.header.RR12
        print('Row ratio R1/R2 = ',header_RR12)
    else:
        header_RR12 = 'N/A'
        print('Row ratio R1/R2 is not given in the .lmx header.')
    if lmxfile.header.RR13 != None:
        header_RR13 = lmxfile.header.RR13
        print('Row ratio R1/R3 = ',header_RR13)
    else:
        header_RR13 = 'N/A'
        print('Row ratio R1/R3 is not given in the .lmx header.')
    if lmxfile.header.RR23 != None:
        header_RR23 = lmxfile.header.RR23
        print('Row ratio R2/R3 = ',header_RR23)
    else:
        header_RR23 = 'N/A'
        print('Row ratio R2/R3 is not given in the .lmx header.')
    print('End file header information')
    print('#######################################')
          
    return header_tick_length, header_measurement_time, header_count_rate, header_SD, header_RD, header_FIFO, header_RR12, header_RR13, header_RR23