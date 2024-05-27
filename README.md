# Simple tooling for running a photocatalysis HTE

## How to 

0. Set up experimental config. 
    a. `experiments.yml` defines the experiments 
    b. `setup.yml` defines the setup (firesting, power supply, folders)
1. Set up experimental setup 
2. Start AutoSuite Program 
3. In the `base` Python environment run `python run.py` in the `experiments` folder of this repo


## Config files 

### `experiments.yml` 
This file lists experimental conditions. If `run: false`, the condition will not be run (this is read by the Chemspeed AutoSuite and then leaves the code in a `while` loop where nothing physically happens). 

The meaning of the parameters is:

- `name`: human-readable name of the experiments. Will be used for naming the log file 
- `voltage`: voltage in `V` for the light source (ensure that there is a minimum current)
- `volume_water`: the volume of water in `mL`
- `volume_sacrificial_oxidant`: the volume of sacrificial oxidant in `mL` 
- 

An example file looks like 

```yaml
- 
  name: MR-1
  voltage: 0.18
  volume_water: 0.1
  volume_sacrificial_oxidant: 0.1
  volume_ruthenium_solution:  0.1
  volume_buffer_solution_1: 0.1
  volume_buffer_solution_2: 0.1
  degassing_time: 20
  measurement_time: 10 
  run: true 
- 
  name: MR-1
  voltage: 0.18
  volume_water: 0.1
  volume_sacrificial_oxidant: 0.1
  volume_ruthenium_solution:  0.1
  volume_buffer_solution_1: 0.1
  volume_buffer_solution_2: 0.1
  degassing_time: 20
  measurement_time: 10 
  run: false 
```