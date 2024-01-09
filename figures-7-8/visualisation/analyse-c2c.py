import pandas as pd
import numpy as np
from pathlib import Path
from mpl_toolkits import axes_grid1
import matplotlib
import matplotlib.colors
import matplotlib.ticker
import matplotlib.pyplot as plt
from dataclasses import dataclass

matplotlib.rc('font', **{
	'family' : 'sans',
	'size'   : 24})

basepath = Path(__file__).parent

@dataclass
class Run:
	name: str
	df: pd.DataFrame
	arch: str = ""

	def merge(self, other_run):
		_vals = np.array([self.df.values, other_run.df.values])
		self.df = pd.DataFrame(np.mean(_vals, axis=0))
		return self

	def set_name(self, name: str):
		self.name = name
		return self

	def set_arch(self, arch: str):
		self.arch = arch
		return self

	def reorder(self):
		self.df = reorder(self.df)
		return self

# courtesy to https://stackoverflow.com/a/33505522
def add_colorbar(im, aspect=20, pad_fraction=0.5, **kwargs):
	"""Add a vertical color bar to an image plot."""
	divider = axes_grid1.make_axes_locatable(im.axes)
	width = axes_grid1.axes_size.AxesY(im.axes, aspect=1./aspect)
	pad = axes_grid1.axes_size.Fraction(pad_fraction, width)
	current_ax = plt.gca()
	cax = divider.append_axes("right", size=width, pad=pad)
	plt.sca(current_ax)
	return im.axes.figure.colorbar(im, cax=cax, **kwargs)

def reorder(df: pd.DataFrame) -> pd.DataFrame:
	"""
	Convert Linux ordering to Windows orderning (for SMT systems)
	Place physically related cores next to each other
	"""
	num_cores = len(df)
	num_physical_cores = num_cores//2
	mapping = {}
	for core in range(num_physical_cores):
		mapping[core] = core*2
		mapping[num_physical_cores+core] = core*2+1

	df.rename(columns=mapping, inplace=True)
	df = df.reindex(sorted(df.columns), axis=1)

	df.rename(index=mapping, inplace=True)
	df.sort_index(inplace=True)
	
	return df

def plot_one(run: Run, save: bool = False, ticker_locator = None, zoom: (int,int)=None):
	fig,ax = plt.subplots(figsize=(12, 12))
	plt.rcParams['axes.titley'] = 1.1 
	im = ax.imshow(run.df, cmap="viridis")

	cbar = add_colorbar(im)
	cbar.set_label("Core-to-Core Latency [ns]")
	ax.tick_params(axis='x', labelrotation = 90, labelsize=24)
	ax.tick_params(axis='y', labelsize=24)
	if ticker_locator:
		ax.xaxis.set_major_locator(ticker_locator)
		ax.yaxis.set_major_locator(ticker_locator)

	ax.set_xlabel("Core ID")
	ax.set_ylabel("Core ID")
	ax.xaxis.tick_top()
	ax.xaxis.set_label_position("top")

	if zoom:
		ax.set_xlim(zoom[0]-.5, zoom[1]+.5)
		ax.set_ylim(zoom[1]+.5, zoom[0]-.5)
	fig.tight_layout()
	if save: plt.savefig(basepath / "figures" / f"c2c_{run.name}{'_zoom' if zoom else ''}.pdf")
	else:    plt.show()

def main():
	runs = {}

	basepath_data = basepath.parent / "data"
	if not (basepath / "figures").is_dir():
		(basepath / "figures").mkdir(parents=True)

	for f in list(filter(lambda x: x.suffix == ".csv", basepath_data.iterdir())):
		df = pd.read_csv(f, header=None)
		df = df.combine_first(df.T)
		name = f.stem.replace(".csv", "")

		r = Run(name=name, df=df)
		runs[r.name] = r

	save = True

	# C2C Compute Nodes
	# compute node is noisier than infrastructure, so measure twice and merge/average both runs
	df_ampere = runs["cn03c1_run1"].set_arch("Ampere Altra Max")\
	            .merge(runs["cn03c1_run2"]).set_name("cn03c1")
	plot_one(df_ampere,
		ticker_locator=matplotlib.ticker.MultipleLocator(4),
		save=save)

	plot_one(df_ampere,
		ticker_locator=matplotlib.ticker.MultipleLocator(1),
		zoom=[0,7],
		save=save)

	# C2C Infrastructure Node
	df_amd = runs["infra2c1"].reorder()
	plot_one(df_amd,
		ticker_locator=matplotlib.ticker.MultipleLocator(2),
		save=save)

	plot_one(df_amd,
		ticker_locator=matplotlib.ticker.MultipleLocator(1),
		zoom=[12,19],
		save=save)

	## Example for custom measurement
	# df_example = runs["server1"].reorder()
	# plot_one(df_example,
	# 		 ticker_locator=matplotlib.ticker.MultipleLocator(2),
	# 		 save=save)

if __name__ == "__main__": main()