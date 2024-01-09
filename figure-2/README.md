# Figure 2 - Point-to-Point Network Metrics

## Requirements

- iperf3 3.15 (https://github.com/esnet/iperf)
- netperf 2.7.1 (https://github.com/HewlettPackard/netperf)
- Python 3.11
  - see global README for package requirements

## Usage

> If you want to reproduce Figure 2, then run `visualisation/main-iperf.py` and `visualisation/main-netperf.py` using your configured Python.
> The figures will be placed in `visualisation/figures`.
> The data used for these figures are already present in `data/`.

### Gather Data 

Note: The below procedure has been developed and tested on the OpenCUBE prototype testbed system and is therefore built upon several assumptions.
This includes the presence of servers at well-known hostnames/IP addresses, as well as existence of binaries at specific locations.
If you wish to use this procedure on different systems, then it is necessary to adapt the script accordingly.

The procedure outlined below and the scripts attached are primarily meant for validation purposes.

1. Install `iperf3` and `netperf` . Consult the project repositories for guidance.
2. Run `measurement_src/iperf_cluster.sh` and `measurement_src/netperf_cluster.sh`
    - This will create and populate a folder at `$cwd/measurements_{iperf,netperf}_{timestamp}` (`$cwd`: current working directory)

### Visualise Data

1. Adapt `visualisation/main-iperf.py` and `visualisation/main-netperf.py`
    - see notes below
2. Run `visualisation/main-iperf.py` and `visualisation/main-netperf.py` using your configured Python.
3. The resulting figures are saved in `visualisation/figures`.

Notes:
This script expects the measurement CSVs to be stored in `data/` and loads & visualises these by name.
Move the `measurements_*` folders created above into `data/` if necessary.

Adapt the `date` variable in line 33/31 (iperf/netperf) to match the previously created
timestamp in `measurements_{iperf,netperf}_{timestamp}`.
