# Sample Scripts for LMX neutron noise processing

This repository provides samples scripts for the LMX python package for neutron noise processing of time
dependent data. The Rossi-alpha and Feynman neutron noise techniques are the main methods implemented.
The scripts are divided into simple and nuanced version of implementing the ```feynman``` or ```rossi```
package. Initial data can be in ```.lmx```, ```.npy```, or ```.txt``` formats. The samples scripts are:

* ```NeutronNoiseProcessing```:   script for simple implementation of both ```rossi``` and ```feynman``` for a single data set.
* ```NuancedFeynmanProcessing```: script for exploring features of the ```feynman``` module.
* ```NuancedRossiProcessing```:   script for exploring features of the ```rossi``` module.
* ```SimpleFeynmanProcessing```:  script for simple implemenation from data to Y2/gatewidth regression.
* ```SimpleRossiProcessing```:    script for simple implementation from data to Rossi regression.