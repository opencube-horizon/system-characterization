import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path

from mpl_toolkits import axes_grid1

pd.options.display.width = 1920
pd.options.display.max_columns = 99

matplotlib.rc('font', **{
	'family' : 'sans',
	'size'   : 22})

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

def main():
	file_path = Path(__file__).parent
	basepath = file_path.parent / "data"

	date = "23-11-03T1606"
	measurement_dir = f"measurements_netperf_{date}"

	measurement_file = list(filter(lambda x: x.suffix == ".csv", (basepath/measurement_dir).iterdir()))[0]
	df = pd.read_csv(measurement_file, sep=";")
	df.rename(columns={"from":"server", "to":"client"}, inplace=True)
	metric = "mean_latency"

	ct = pd.crosstab(index=df["server"], columns=df["client"],
					 values=df[metric], aggfunc="first")
	ct_std = pd.crosstab(index=df["server"], columns=df["client"],
					 values=df["stddev_latency"], aggfunc="first")
	fig, ax = plt.subplots(figsize=(12,12))
	fig: plt.Figure
	ax: plt.Axes

	im = ax.imshow(ct)

	def _format(input: float) -> str:
		if np.isnan(input): return ""
		rounded = round(input, 2)
		return str(rounded)

	textcolors = ["white", "black"]
	threshold = 0.5
	for i in range(len(ct.columns)):
		for j in range(len(ct.columns)):
			try:
				datum = ct.iloc[i,j]
				color = textcolors[int(im.norm(datum) > threshold)]
				ax.text(j,i, f"{_format(datum)}\n±{_format(ct_std.iloc[i,j])}", 
					ha="center",va="center", color=color)
			except Exception as e: print(e)
	cbar = add_colorbar(im)
	cbar.set_label("Latency [μs]")
	plt.rcParams['axes.titley'] = 1.075  # y is in axes-relative coordinates.
	ax.set_xticks(np.arange(len(ct.columns)), labels=ct.columns)
	ax.set_yticks(np.arange(len(ct.columns)), labels=ct.columns)
	ax.xaxis.tick_top()

	fig.tight_layout()
	if not (file_path / "figures").is_dir():
		(file_path / "figures").mkdir(parents=True)
	plt.savefig("figures/netperf_frontend.pdf")

if __name__ == "__main__": main()