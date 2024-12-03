# Hash-And-Adjust

![Figure 5a](plots/5a.pdf "Fig. 5a")

## Dependencies

To run the simulation-code, the modules ```bitstring```, ```scipy``` and ```pandas``` are required.

For the plotting functionality, other packages such as ```seaborn``` are used. A detailed list can be found in ```requirements.txt```. 

## Experiments

The experimentation code can be found in ```implementation```. 
It fetches the datasets from ```data``` and generates data in ```data_handling```.

### Experiment setup

We advise to use PyCharm (it offers the possibility to take care of the dependencies) and set the working directory to the parent folder ``` .\Hash-And-Adjust\ ```.

### Run the experiments

All relevant experiments can be run from ```main.py``` in the root folder. The output will be saved in the ```results``` folder.

### Data

Temporal-locality data can be generated on the fly. We uploaded the click-dataset to ```data```, 
while the CAIDA-Dataset needs to be requested from the official source.

## Plotting

The plotting code can be found in the ```plotter.py``` file: 
it uses the output from ```results``` and can be run independently from the experimentation code (see comments in ```main.py```).
Generated plots are saved in the ```plots``` folder.
