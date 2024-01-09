from pathlib import Path

import pandas as pd
import re
import io

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker
import matplotlib.patheffects

from dataclasses import dataclass

pd.options.display.max_columns=99
pd.options.display.width=1920
pd.options.display.max_rows=99

matplotlib.rc('font', **{
	'family' : 'sans',
	'size'   : 22})

@dataclass
class Measurement:
	name: str
	mpi_type: str
	df: pd.DataFrame

	def get_name(self) -> str:
		return f"{self.name}"#" @ {self.mpi_type}"

	def x_filter(self, fr: int, to: int):
		self.df = self.df.loc[fr:to,]
		return self

def visualise(measurement: Measurement, save: bool = False, basepath: Path = None):
	fig, ax = plt.subplots(figsize=(12,6))


	df = measurement.df
	ax.plot(df[[df.columns[0]]])

	ax.set_xscale("log")
	ax.set_yscale("log")
	ax.set_ylabel(df.columns[0])
	ax.set_xlabel("Message Size (byte)")

	ax.xaxis.grid()
	ax.yaxis.grid()
	ax.yaxis.grid(which="minor", alpha=.3)
	if not save:
		ax.set_title(measurement.name)
	fig.tight_layout()

	if save:
		plt.savefig(basepath / "figures" / f"{measurement.get_name()}.pdf")

	plt.show()


def visualise_multiple(measurements: [Measurement],
					   annotations: list[(int,int,int,int)] = None, 
					   save: bool = False, 
					   name: str = "", basepath: Path = None):
	fig, ax = plt.subplots(figsize=(9,9))

	for measurement in measurements:
		ax.plot(measurement.df[[measurement.df.columns[0]]], 
			    label=measurement.get_name())

	ax.set_xscale("log", base=2)
	ax.set_yscale("log")
	ax.set_ylabel(measurements[0].df.columns[0])
	ax.set_xlabel("Message Size (byte)")

	ax.xaxis.grid()
	ax.yaxis.grid()
	ax.yaxis.grid(which="minor", alpha=.3)

	ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', size=18)
	ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter(r"{x:.0f}"))
	ax.xaxis.set_major_locator(matplotlib.ticker.LogLocator(base=2, numticks=len(measurements[0].df.index)))
	ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter(r"{x:.0f}"))


	if annotations:
		for a_idx, a_pos, a_offset_x,a_offset_y in annotations:
			value = measurements[a_idx].df.loc[a_pos, measurements[a_idx].df.columns[0]]
			ax. annotate(f"{value:.2f}", xy=(a_pos,value),
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
	else:
		plt.show()

def load_measurements(basepath_measurements: Path, ts: str) -> dict[str,Measurement]:
	pattern_header = re.compile(r"# Size\s+(.*?)$", flags=re.MULTILINE)
	pattern_remove_prefixes = re.compile(r"#.*?$\n", flags=re.MULTILINE)
	pattern_to_csv = re.compile(" +", flags=re.MULTILINE)

	measurements = {}
	for file in list(filter(lambda x: x.suffix == ".dat", (basepath_measurements / ts).iterdir())):
		with open(file, "r") as infile:
			lines = infile.read()
			matches = pattern_header.search(lines)
			header_raw = matches.group(1)
			header_split = [s.strip() for s in header_raw.split(")") if len(s) > 0]
			headers = [f"{s})" for s in header_split]
			lines_without_header = pattern_remove_prefixes.sub("", lines)
			data = pattern_to_csv.sub(";", lines_without_header)
			data_buf = io.StringIO()
			data_buf.write(data + "\n")
			data_buf.seek(0)
			df = pd.read_csv(data_buf, sep=";", names=headers)
			name = "_".join(file.stem.split("_")[-2:])
			mpi_type = ts.split("_")[2]
			measurements[name] = Measurement(df=df, mpi_type=mpi_type, name=name)	
	return measurements

def main():
	basepath = Path(__file__).parent
	basepath_measurements = basepath.parent / "data"
	save = True

	if not (basepath / "figures").is_dir():
		(basepath / "figures").mkdir(parents=True)

	# OMB Frontend - Compute Node
	measurements_cn = load_measurements(basepath_measurements,
		"measurements_osu_openmpi_cn_23-11-22T1111")
	visualise_multiple([measurements_cn["osu_bw"],
						measurements_cn["osu_bibw"]],
						annotations=[(1,65536/2,1,.35),(0,4194304,1,.35)],
						save=save, basepath=basepath, name="omb_bw_cn")
	
	visualise_multiple([
		measurements_cn["osu_latency"],
		measurements_cn["osu_gather"],
		measurements_cn["osu_alltoall"]],
						annotations=[(1,4,2,1.5),
     								 (0,4,.5,1.5),
									 (2,4,1,1.5),
								     (0,4194304,1,.35)],
						save=save, basepath=basepath, name="omb_latency_cn")


	# OMB Frontend - Infrastructure Node
	measurements_infra = load_measurements(basepath_measurements,
		"measurements_osu_openmpi_infra_23-11-27T0955")
	visualise_multiple([measurements_infra["osu_bw"],
						measurements_infra["osu_bibw"]],
						annotations=[(1,65536/2,1,.35),(0,4194304,1,.35)],
						save=save, basepath=basepath, name="omb_bw_infra")
	
	visualise_multiple([
		measurements_infra["osu_latency"],#.x_filter(fr=1,to=1048576),
		measurements_infra["osu_gather"],
		measurements_infra["osu_alltoall"]],
						annotations=[(1,4,2,1.5),
									 (2,4,.5,1.5),
									 (0,4194304,1,.35)],
						save=save, basepath=basepath, name="omb_latency_infra")


	# OMB Slingshot - Infrastructure Node
	measurements_infra_sl = load_measurements(basepath_measurements,
		"measurements_osu_openmpi-native_infra_23-11-30T1154")

	visualise_multiple([measurements_infra_sl["osu_bw"],
						measurements_infra_sl["osu_bibw"]],
						annotations=[(1,4194304,.25,.5),(0,4194304,1,.35)],
						save=save, basepath=basepath, name="omb_bw_infra_slingshot")
	
	visualise_multiple([
		measurements_infra_sl["osu_latency"],#.x_filter(fr=1,to=1048576),
		measurements_infra_sl["osu_gather"],
		measurements_infra_sl["osu_alltoall"]],
						annotations=[(1,4,2,1.5),
									 (2,4,.5,1.5),
									 (0,4194304,1,.35)],
						save=save, basepath=basepath, name="omb_latency_infra_slingshot")

	## OMB Example
	# measurements_example = load_measurements(basepath_measurements,
	# 										  "<YOUR_MEASUREMENTS>")
	#
	# visualise_multiple([measurements_example["osu_bw"],
	# 					measurements_example["osu_bibw"]],
	# 				   annotations=[(1, 4194304, .25, .5), (0, 4194304, 1, .35)],
	# 				   save=save, basepath=basepath, name="omb_bw_<SPECIFY_NAME>")
	#
	# visualise_multiple([
	# 	measurements_example["osu_latency"],  # .x_filter(fr=1,to=1048576),
	# 	measurements_example["osu_gather"],
	# 	measurements_example["osu_alltoall"]],
	# 	annotations=[(1, 4, 2, 1.5),
	# 				 (2, 4, .5, 1.5),
	# 				 (0, 4194304, 1, .35)],
	# 	save=save, basepath=basepath, name="omb_latency_<SPECIFY_NAME>")


if __name__ == "__main__": main()