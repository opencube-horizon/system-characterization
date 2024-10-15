# Network - MPI Characterization

This folder provides data and visualisation scripts for MPI network characterization using the OSU Micro-Benchmark suite.
The results are reported in D4.1 in Figures 3, 4, and 6.

## Requirements

- OSU (http://mvapich.cse.ohio-state.edu/benchmarks/)
- Python 3.11
  - see global README for package requirements

## Usage

> If you want to reproduce Figures 3,4,6, then run `visualisation/analyze_osu.py` using your configured Python.
> The figures will be placed in `visualisation/figures`.
> The data used for these figures are already present in `data/`.

### Gather Data 

Note: The below procedure has been developed and tested on the OpenCUBE prototype testbed system and is therefore built upon several assumptions.
This includes the presence of servers at well-known hostnames/IP addresses, as well as existence of binaries at specific locations.
If you wish to use this procedure on different systems, then it is necessary to adapt the script accordingly.

The procedure outlined below and the scripts attached are primarily meant for validation purposes.

1. Install the `OSU` suite. Consult the project repositories for guidance.
2. Run `measurement_src/osu_cluster.sh`
   - This will create and populate a folder at `$cwd/measurements_osu_{MPI-version}_{host}_{timestamp}` (`$cwd`: current working directory)

This script accepts the following parameters:

- `--host-set`, can be one of `cn` (Compute Node) and `infra` (Infrastructure node)
- `--mpi-type`, can be one of `openmpi` (for both cn and infra) and `openmpi-native` (just for infra - used for Slingshot)

These settings correspond to the following figures:

| Figure | `--host-set` | `--mpi-type`     | 
|:------:|:-------------|:-----------------|
|   3    | `cn`         | `openmpi`        |
|   4    | `infra`      | `openmpi`        |
|   6    | `infra`      | `openmpi-native` |


### Visualise Data

1. Adapt `visualisation/analyse_osu.py`
    - see notes below
2. Run `visualisation/analyse_osu.py` using your configured Python.
3. The resulting figures are saved in `visualisation/figures`.

Notes:
This script expects the measurement CSVs to be stored in `data/` and loads & visualises these by name.
Move the `measurements_*` folders created above into `data/` if necessary.

Uncomment and adapt the last lines 191ff with your measurements.
