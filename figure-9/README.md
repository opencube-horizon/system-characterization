# Figure 9 - Memory Latency

## Requirements

- Microbenchmarks (https://github.com/clamchowder/Microbenchmarks/tree/master)
- Python 3.11
  - see global README for package requirements

## Usage

> If you want to reproduce Figure 9, then run `visualisation/analyze_caches.py` using your configured Python.
> The figures will be placed in `visualisation/figures`.
> The data used for these figures are already present in `data/`.

### Gather Data

1. Install the `Microbenchmarks` suite. Consult the project repositories for guidance.
2. Run `./MemoryLatency_{arch} -test asm -iter 100000000` (`arch`: System architecture, such as `x86`, `aarch64`)
3. Run `./MemoryLatency_{arch} -test asm -hugetables -iter 100000000`
4. For both runs: Copy the resulting data (Lines after `Region,Latency (ns)`) into a `.csv` file

### Visualise Data

1. Adapt `visualisation/analyze_caches.py`
    - see notes below
2. Run `visualisation/analyze_caches.py` using your configured Python.
3. The resulting figures are saved in `visualisation/figures`.

Notes:
This script expects the measurement CSVs to be stored in `data/` and loads & visualises these by name.
Move the above created `.csv` files into `data/`.

Uncomment and adapt the last lines 120ff with your measurements. 
- `YOURMEASUREMENTS{_HUGEPAGES}` refers to the name given to respective CSV file.
- `L{1,2,3},SLC` refer to the respective cache sizes. These can be taken from the manufacturer TRM or the `lscpu` command
- (Optional) `ANNOTATION_POINTS` refers to a list of annotation points in kB to be added to the figures
- (Optional) `SYSTEMARCH` refers to the architecture
