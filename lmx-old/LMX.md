# LMX File Processing
Part of this repository provides analysis of the LMX file format.
The LMX file provides substantial information regarding the given experiment.
The data is divided into the header and the events. This document will explain how 
the python program will extract the information into usable formats.

The process has various aspects:
* [Event](Event.py) 
* [Header](Header.py)
* [LMXFile](LMXFile.py)
* [factory](factory.py)
* [ToEvents](ToEvents.py)

## Event
An ```Event``` is the basic unit for extracting the time value and detector 
identifier pair data from LMX file. Several functions will handle this for you, but an
explanation is important for creative and unique use/analysis.

### Using Event
To make a single ```Event```:

```python
from lmx.Event import Event

time = 1.0    # positive measurement time
detector = 1  # detector associated with time
single_event = Event(time=time, detector=detector)
```
The resulting ```single_event``` now has the information stored. Note that the 
```time``` and ```detector``` cannot be negative. To access/edit the data in the class:
```python
print(single_event.time)
print(single_event.detector)
print(single_event)
single_event.time = 2.0
print(single_event.time)
```
Output:
```commandline
1.0
1
An event occured at 1.0 seconds in detector 1
2.0
```
The majority of analysis will require a list of ```Event``` types. The Event class
makes it easy to create a list and access its contents. 

## Header
The LMX file ```header``` has information on the experiment. The ```factory``` will
extract the information from the lmx file. The user is given this data automatically 
and is not forced to carry this data throughout the analysis.

### Using Header
The Header has both explicit values that are expected in the LMX file and other values
that are not consistently entered. To access the explicit values:
```python
from lmx.Header import Header

# An example of a built in value
ticklength = header.ticklength.value
```
Other values that are built in are ```ticklength```, 
```MsmtDuration```,
```AvgCountRate```,
```FaceToSource```,
```CenterToFloor```, 
```FifoLostCounts```,
```RR12```,
```RR13```, and ```RR23```. These values can only be access by applying a ```.value```
to the end of the header call. Otherwise the value will not be found.

All other values are stored in a dictionary called ```other```. To access values is 
identical to a python dictionary call:
```python
# access the value as extracted from LMX
internal_scalar = header.other.get("InternalScaler")

# as extracted from LMX means that the values are a string type that must be changed
internal_scalar = int(internal_scalar)
```
For all ```other```dictionary values, the type must be changed from being string types.

## LMXFile
The ```LMXFile``` class combines a list of ```Event``` types and a ```Header``` into
 a single class. This class will typically not be created by the user. It will be the 
output of the ```factory``` function. However, the ```LMXFile``` class has functions 
that make processing easier. For example:
```python
from lmx.LMXFile import LMXFile

lmx = LMXFile(header=header, events=events)
first_detector = lmx.detectorEvents(1) # Get all Events from detector 1
counts_in_detector1 = lmx.detectorCounts(1) # Get amount of counts from detector 1
counts = lmx.allDetectorCounts() # Get amount of counts from all detectors
```

## Factory
The ```factory``` ties together the ```LMXFile```, ```Header```, and ```Event``` class types.
The ```factory``` takes a lmx file and outputs an ```LMXFile``` class type. 
```python
from lmx.factory import readLMXFile

LMXFile_type = readLMXFile("sample.lmx")
```
The ```factory``` is incorporated into the ```ToEvents``` function.

## ToEvents
This file contains several function for extracting the events alone from various 
file types. To get events:
```python
from lmx.ToEvents import *

# Extraction from lmx file
lmx = eventsFromLMX("file.lmx")

# Extraction from a numpy pickled file
unickled_events = eventsFromPickle("file.npy")

# Default extraction from numpy file
numpy = eventsFromNumpy("file.npy", times_index=0, detectors_index=None)

# Default extraction from text file
txt = eventsFromTxt("file.txt", times_index=0, detectors_index=None)
```
Pickled ```Event``` lists are an easy way to analyze a single measuremnt when 
processing over an extended period of time. Numpy and text files come in several 
arrangements. To account for that the functions 
include a ```times_index``` to select the column/row index position for times and 
```detectors_index``` to select the column/row index position for the detector 
assocaited with the times. By default, ```times_index```= 0 and ```detectors_index```
= None. This allows for files that consistent only of time stamps to be turned into
```Event``` types. The detector-time pair values are turned to an ```Event```
list. 

### Saving Events
To save events and avoid reprocessing the LMX binary format this section of 
```ToEvents``` contains functions for numpy pickling and saving to text.
```python
from lmx.ToEvents import *

# How to save to text files
saveToText("file1.txt", events)
saveToText("file1", events)

# How to pickle to numpy binary file
saveToPickle("file1.npy", events)
saveToPickle("file1", events)
```
Text files can be opened as previously mentioned with ```eventsFromTxt```.