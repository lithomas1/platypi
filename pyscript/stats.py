from bokeh.models import ColumnDataSource
from pandas import DataFrame
from bokeh.plotting import figure
from bokeh.transform import cumsum
from bokeh.palettes import Category20c
from math import pi


def plot_top_downloaded_files(data: DataFrame, packagename: str, n: int):
    source = ColumnDataSource(data.head(n)[["file", "download_counts"]])
    p = figure(title=f"Top {n} downloaded wheels for package {packagename}",
                y_range=data.head(n)["file"].values,
                x_axis_label="Download count",
                y_axis_label="File name")
    p.hbar(y="file", right="download_counts", source=source)
    return p

def plot_wheel_coverage(data: DataFrame, packagename: str):
    grouped_stats = data.groupby("ftype")
    ftype_counts = grouped_stats["download_counts"].sum().reset_index()
    # Manually calculate pie chart angles since bokeh doesn't do that
    # for us
    ftype_counts["angle"] = ftype_counts["download_counts"]/ftype_counts["download_counts"].sum() * 2 * pi
    ftype_counts["color"] = Category20c[len(ftype_counts)]
    p = figure(title="Wheel coverage", tooltips="@ftype: @download_counts")
    p.wedge(x=0, y=1, radius=0.4, start_angle=cumsum("angle", include_zero=True), end_angle=cumsum("angle"), legend="ftype", fill_color="color", source=ftype_counts)
    return p

def plot_platforms(data: DataFrame, packagename: str, n: int):
    wheel_info = data[data["ftype"] == "wheel"]
    plat_download_counts = wheel_info.groupby("platformtag")["download_counts"].sum()
    plat_download_counts = plat_download_counts / plat_download_counts.sum()
    plat_download_counts = plat_download_counts.sort_values(ascending=False)
    plat_download_counts = plat_download_counts.reset_index()
    source = ColumnDataSource(plat_download_counts.head(n))
    p = figure(title=f"Top {n} platforms wheels were downloaded on for package {packagename}",
                y_range=plat_download_counts.head(n)["platformtag"].values)
    p.hbar(y="platformtag", right="download_counts", source=source)
    return p