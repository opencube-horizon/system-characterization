# Compute - Core-to-Core Latency

This folder provides data and visualisation scripts for core-to-core latency metrics.
The results are reported in D4.1. in Figures 7 and 8.

## Requirements

- https://github.com/nviennot/core-to-core-latency
- Python 3.11
  - see global README for package requirements

## Usage

> If you want to reproduce Figures 7 and 8, then run `visualisation/analyse-c2c.py` using your configured Python.
> The figures will be placed in `visualisation/figures`.
> The data used for these figures are already present in `data/`.

### Gather Data 

1. Download and compile the `core-to-core-latency` tool. Consult the project repository for guidance.
2. Run `./core-to-core-latency --bench 1 --csv 5000 600 2>/dev/null 1>measurement.csv`
    - Notes: 
      - `2>/dev/null` hides runtime output. This is optional.
      - `1>measurement.csv` redirects the actual CSV output into a file named `measurement.csv` _in the current working directory_. Make sure this does not overwrite any preexisting files!

### Visualise Data

1. Run `visualisation/analyse-c2c.py` using your configured Python.
2. The resulting figures are saved in `visualisation/figures`.

Notes:
This script expects the measurement CSVs to be stored in `data/` and loads & visualises these by name.
Say that you ran `./core-to-core-latency --bench 1 --csv 5000 600 2>/dev/null 1>server1.csv`. 
Copy the resulting file `server1.csv` into `data/` and add the necessary load & visualisation instructions to `analyse-c2c.py`.
Lines 137-141 contain a commented-out version of these instructions.
