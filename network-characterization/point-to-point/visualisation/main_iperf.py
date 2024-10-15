import json

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

	date = "23-11-03T1352"
	measurement_dir = f"measurements_iperf_{date}"

	data = []
	for file in filter(lambda x: x.suffix == ".json",
					   (basepath/measurement_dir).iterdir()):
		file_parts = file.stem.split("_")
		with open(file, "r") as infile:
			content = json.load(infile)
			intervals = content["intervals"]
			data += [
				{**interval["sum"],
				 "server": file_parts[3],
				 "client": file_parts[4],
				 "rtt_mean": np.mean(list(map(lambda x: x["rtt"], interval["streams"])))
				 }
				for interval in intervals
				if not interval["sum"]["omitted"]
			]
	df = pd.DataFrame(data)
	df["gbits_per_second"] = df.bits_per_second / 1e9

	metric = "gbits_per_second"

	ct = pd.crosstab(index=df["server"], columns=df["client"],
					 values=df[metric], aggfunc="mean")
	ct_std = pd.crosstab(index=df["server"], columns=df["client"],
					 values=df[metric], aggfunc="std")

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
				ax.text(j,i, f"{_format(datum)}\n±{_format(ct_std.iloc[i,j])}", ha="center",va="center", color=color)
			except: pass
	cbar = add_colorbar(im)
	cbar.set_label("Throughput [Gbit/sec]")
	plt.rcParams['axes.titley'] = 1.075  # y is in axes-relative coordinates.

	ax.set_xticks(np.arange(len(ct.columns)), labels=ct.columns)
	ax.set_yticks(np.arange(len(ct.columns)), labels=ct.columns)
	ax.xaxis.tick_top()

	fig.tight_layout()
	if not (file_path / "figures").is_dir():
		(file_path / "figures").mkdir(parents=True)
	plt.savefig(file_path / "figures" / "iperf3_frontend.pdf")

if __name__ == "__main__": main()