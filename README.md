# OpenCUBE Testbed System Characterization
[![DOI](https://zenodo.org/badge/740965899.svg)](https://doi.org/10.5281/zenodo.13941777)

This repository contains all datasets and visualization code for the OpenCUBE Testbed System Characterization, as reported in Deliverable 4.1
It also contains the source code and instructions to gather the data used for these figures.

> Note that the source code has been developed and tested on the OpenCUBE prototype testbed system and is therefore built upon several assumptions.
> This includes the presence of servers at well-known hostnames/IP addresses, as well as existence of binaries at specific locations.
> The data gathering source code included in this repository are primarily meant for validation purposes.

## Requirements

Visualising the included data requires a recent Python 3 interpreter (tested with 3.11) and several packets listed in `requirements.txt`.
Install them using `pip install -r requirements.txt`. Ideally create a new virtual environment to avoid collisions.

Aggregating the underlying data primarily uses third-party benchmark code and wrapping bash scripts. 
The requirements and installation instructions are listed in the figure-specific `README.md` files.

## Usage

Each figure-specific folder contains at least a `data` subfolder which contains the measurement data gathered on the OpenCUBE testbed
and a `visualisation` subfolder containing the visualisation Python code. 
Most folders also include a third subfolder `measurement_src`, which contains the measurement source code.

All `data` folders are pre-populated with the gathered measurement data. Running the respective visualisation scripts
will generate the figures as presented in D4.1.

# License

All code is under the Apache 2 license.
All images are under the CC-BY 4.0 license.
