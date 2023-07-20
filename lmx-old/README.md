# LMX neutron noise processing tools
This repository provides a python package related to neutron noise processing of time
dependent data from LMX files. The functionality is organised into several subpackages depending on
their use:
* ```feynman``` : for reading, creating, modifying and writing Feynman Histograms
* ```rossi``` : for reading, creating, modifying and writing Rossi Histograms
* ```Sample Scripts``` : for pre-made scripts for neutron noise processing
* ```test``` : for testing feynman and rossi abilities and packages

```feynman``` and ```rossi``` also accept other time dependent data files  such
as text files and numpy arrays. 

The faust packages may become shared between labs and/or made open source within
international projects such as the VANDAL project at the OECD/NEA Databank.

Documentation for each subpackage can be found in their respective documentation
folder:

[feynman](./feynman/documentation/feynman.md)
[rossi](./rossi/documentation/rossi.md)
[Sample Scripts](./Sample Scripts/documentation/Sample Scripts.md)

## Dependencies and requirements
The lmx package depends on the  ```marshmallow``` and ```smores``` packages. 
The [marshmallow](https://pypi.org/project/marshmallow/) is a third-party package and ```smores``` 
package can be found in the ```faust``` directory. 

## Setting up the package

We currently do not provide an easy way to install the package. For now, you
can modify the python search path by appending the directory in which the
package is installed (note: this is not recommended way of installing
python packages):
```
import sys
sys.path.append( '/home/me/python' )
```

We will try to provide a better way for installing python packages as soon as
possible

## Running unit tests

The package has unit tests associated to it using the ```unittest``` package.
To run the unit tests from the command line, use the following command:
```
python -m unittest discover -v -p "Test*"
```