import pandas as pd
from pathlib import Path
import matplotlib
import matplotlib.ticker
import matplotlib.patheffects
import matplotlib.pyplot as plt
from dataclasses import dataclass


matplotlib.rc('font', **{
	'family' : 'sans',
	'size'   : 22})


basepath = Path(__file__).parent

@dataclass
class Run:
	name: str
	df: pd.DataFrame
	arch: str = ""

	def set_name(self, name: str):
		self.name = name
		return self

	def merge(self, other, col_new: str):
		self.df = self.df.join(other.df.rename(columns={"Latency (ns)": col_new}))
		return self

	def set_arch(self, arch: str):
		self.arch = arch
		return self


def plot_one(run: Run, save: bool = False, 
			 annotations: list[int] = None,
			 cache_levels: list[int] = None):
	fig,ax = plt.subplots(figsize=(9, 7))
	
	plt.rcParams['axes.titley'] = 1.075 

	hugepages = "Latency Hugepages (ns)" in run.df.columns
	ax.plot(run.df.index, run.df["Latency (ns)"], label="default")
	if hugepages:
		ax.plot(run.df.index, run.df["Latency Hugepages (ns)"], label="hugepages", zorder=0)

	ax.set_xscale("log", base=2)
	ax.set_yscale("log", base=10)

	ax.set_ylim(1, 160)
	ax.set_xlim(min(run.df.index) - .5, max(run.df.index) + 2**18)
	ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', size=18)
	ax.tick_params(axis='y', labelsize=18)
	ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter(r"{x:.0f}"))
	ax.xaxis.set_major_locator(matplotlib.ticker.LogLocator(base=2, numticks=len(run.df.index)))
	ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter(r"{x:.0f}"))

	ax.set_xlabel("Test Size [kB]")
	ax.set_ylabel("Latency [ns]")

	if cache_levels:
		for level in cache_levels:
			ax.axvline(x=level, color="red")

	if annotations:
		for annotation in annotations:
			value = run.df.loc[annotation, "Latency Hugepages (ns)"]
			ax. annotate(f"{value:.2f}", xy=(annotation,value),
				fontsize=16, xytext=(annotation, value*1.5),
				horizontalalignment="center",
				arrowprops=dict(arrowstyle="->", lw=1),
				path_effects=[matplotlib.patheffects.withStroke(
					linewidth=6, foreground="white")])

	ax.grid("x")
	ax.grid("y")
	ax.grid("x", which="minor", alpha=.25)
	ax.grid("y", which="minor", alpha=.25)
	
	if hugepages:
		plt.legend(loc="upper left")
	fig.tight_layout()
	if save:
		plt.savefig(basepath / "figures" / f"caches_{run.name}.pdf")
	else: plt.show()


def main():
	basepath_data = basepath.parent / "data"
	if not (basepath / "figures").is_dir():
		(basepath / "figures").mkdir(parents=True)

	runs = {}
	for f in list(filter(lambda x: x.suffix == ".csv", basepath_data.iterdir())):
		df = pd.read_csv(f, sep=",").set_index("Region")
		r = Run(name=f.stem, df=df)
		runs[r.name] = r
	
	save = True

	# Infrastructure Node
	plot_one(runs["asm_test_cn03"].set_arch("Ampere Altra Max")
			 .merge(runs["asm_test_hugepages_cn03"], "Latency Hugepages (ns)"), 
		cache_levels=[64, 1024, 32768], # data from `lscpu` and processor TRM
		annotations=[16,256,8192],
		save=save)

	# Compute Node
	plot_one(runs["asm_test_infra2"].set_arch("AMD EPYC")
		 .merge(runs["asm_test_hugepages_infra2"], "Latency Hugepages (ns)"), 
	cache_levels=[32, 512, 32768], # data from `lscpu` and processor TRM
		annotations=[16,256,8192],
	save=save)

	## Example
	# plot_one(runs["<YOURMEASUREMENTS>"].set_arch("<SYSTEMARCH>")
	# 		 .merge(runs["<YOURMEASUREMENTS_HUGEPAGES>"], "Latency Hugepages (ns)"),
	# 		 cache_levels=[<L1>, <L2>, <L3/SLC>],  # true cache size in kB - data from `lscpu` and processor TRM
	# 		 annotations=[<ANNOTATION_POINTS...>],
	# 		 save=save)

if __name__ == "__main__": main()