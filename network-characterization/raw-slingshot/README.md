# Network - Raw Slingshot

This folder provides data and visualisation scripts for raw/direct HPE Cray Slingshot-11 network metrics.
The results are reported in D4.1. in Figure 5.

## Requirements

- Access to a Slingshot-enabled System
- Python 3.11
  - see global README for package requirements

## Usage

> If you want to reproduce Figure 5, then run `visualisation/analyze_raw_cxi.py` using your configured Python.
> The figures will be placed in `visualisation/figures`.
> The data used for these figures are already present in `data/`.

### Gather Data

1. Run `measurement_src/benchmark_cxi.sh`
    - This will create and populate a folder at `$cwd/measurements_{timestamp}` (`$cwd`: current working directory)

### Visualise Data

1. (Optional) Adapt `visualisation/analyze_raw_cxi.py`
    - see notes below
2. Run `visualisation/analyze_raw_cxi.py` using your configured Python.
3. The resulting figures are saved in `visualisation/figures`.

Notes:
This script expects the measurement CSVs to be stored in `data/` and loads & visualises these by name.
Move the above created folder(s) `measurements_{timestamp}` into `data/`.

Adapt the folder name in line 112 with your measurement folder, or leave at "measurements_23-11-30T1546" to visualise values from deliverable.
