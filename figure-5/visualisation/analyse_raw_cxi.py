import pandas as pd
from pathlib import Path
import matplotlib
import matplotlib.ticker
import matplotlib.patheffects
import matplotlib.pyplot as plt
from dataclasses import dataclass

import re 
import io 

matplotlib.rc('font', **{
	'family' : 'sans',
	'size'   : 22})

basepath = Path(__file__).parent

@dataclass
class Measurement:
	name: str
	df: pd.DataFrame
	mtype: str

	def get_name(self) -> str:
		return f"{self.name}"

	def x_filter(self, fr: int, to: int):
		self.df = self.df.loc[fr:to,]
		return self

def plot_multiple(measurements: [Measurement], 
	ylabel: str, 
	name: str = "",
	save: bool = False,
			 annotations: list[(int, str, int,int,int)] = None):
	fig,ax = plt.subplots(figsize=(9, 9))
	plt.rcParams['axes.titley'] = 1.075 

	for measurement in measurements:
		if measurement.mtype == "latency":
			ax.errorbar(measurement.df.index, measurement.df["Mean[us]"],
				yerr=measurement.df["StdDev[us]"], label=measurement.name)
		elif measurement.mtype == "bandwidth":
			ax.plot(measurement.df.index, measurement.df["BW[MB/s]"], label=measurement.name)
		else:
			print("Measurement Type not recognised!")
			return

	ax.set_xlabel("Size [B]")
	ax.set_ylabel(ylabel)
	ax.set_xscale("log",base=2)
	ax.set_yscale("log", base=10)
	ax.grid("x")
	ax.grid("y")
	ax.grid("x", which="minor", alpha=.25)
	ax.grid("y", which="minor", alpha=.25)
	ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter(r"{x:.0f}"))
	ax.xaxis.set_major_locator(matplotlib.ticker.LogLocator(base=2, numticks=len(measurements[0].df.index)))
	ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter(r"{x:.0f}"))
	ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', size=18)
	
	if annotations:
		for a_idx, col, a_pos, a_offset_x,a_offset_y in annotations:
			value = measurements[a_idx].df.loc[a_pos, col]
			ax.annotate(f"{value:.2f}", xy=(a_pos,value),
				fontsize=16, xytext=(a_pos*a_offset_x, value*a_offset_y),
				horizontalalignment="center",
				arrowprops=dict(arrowstyle="->", lw=1,path_effects=[matplotlib.patheffects.withStroke(
					linewidth=2, foreground="white")]),
				path_effects=[matplotlib.patheffects.withStroke(
					linewidth=4, foreground="white")])

	plt.legend()
	fig.tight_layout()
	if save:
		plt.savefig(basepath / "figures" / f"{name}.pdf")
	else: plt.show()

def load_measurements(basepath_measurements: Path, ts: str) -> dict[str,Measurement]:
	pattern_header_split = re.compile(r"(.*?)(?>  +|$)")
	pattern_remove_first_prefix = re.compile(r"^\s+", flags=re.MULTILINE)
	pattern_to_csv = re.compile(" +", flags=re.MULTILINE)

	measurements = {}
	for file in list(filter(lambda x: x.suffix == ".dat", (basepath_measurements / ts).iterdir())):
		with open(file, "r") as infile:
			lines = infile.read()

			# get lines starting with '--- [...]' and their index
			#  data lies between second and third '---' line
			_lines = lines.split("\n")
			enumerated = list(enumerate(_lines))
			enumerated = list(filter(lambda t: t[1].startswith("---"), enumerated))
			lines = '\n'.join([_lines[i] for i in range(enumerated[1][0]+2, enumerated[2][0])])
			headers = pattern_header_split.findall(_lines[enumerated[1][0]+1])
			lines_without_header = pattern_remove_first_prefix.sub("", lines)
			
			data = pattern_to_csv.sub(";", lines_without_header)
			data_buf = io.StringIO()
			data_buf.write(data + "\n")
			data_buf.seek(0)
			df = pd.read_csv(data_buf, sep=";", names=headers, index_col=headers[0])
			name = "_".join(file.stem.split("_")[2:])
			mtype = "bandwidth" if "_bw" in file.stem else "latency"
			measurements[name] = Measurement(df=df, name=name, mtype=mtype)	
			
	return measurements


def main():
	basepath_data = basepath.parent / "data"
	ts = "measurements_23-11-30T1546"
	measurements = load_measurements(basepath_data, ts)

	if not (basepath / "figures").is_dir():
		(basepath / "figures").mkdir(parents=True)

	save = True
	plot_multiple([
		measurements["cxi_write_lat"],		
		measurements["cxi_read_lat"],
		measurements["cxi_send_lat"],
		], 
		ylabel="Mean Latency [us]",
		annotations=[
			(0,"Mean[us]", 4194304,.35,.75),
			(2,"Mean[us]", 4194304,.75,.35),
			(0,"Mean[us]", 4,.5,1.5),
			(2,"Mean[us]", 4,1.75,1.5),
			],
		name="cxi_latency",
		save=save)

	plot_multiple([
		measurements["cxi_write_bw"],		
		measurements["cxi_read_bw"],
		measurements["cxi_send_bw"],
		], 
		ylabel="Bandwidth [MB/s]",
		annotations=[
			(0,"BW[MB/s]", 4194304,.15,.4),
			(2,"BW[MB/s]", 4194304,1,.3),
			],
		name="cxi_bandwidth",
		save=save)
if __name__ == "__main__": main()