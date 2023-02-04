from bokeh.models import ColumnDataSource
from bokeh.palettes import Category20c
from bokeh.plotting import Figure, figure
from bokeh.transform import cumsum
from pandas import DataFrame
from .util import calculate_pie_chart_angle

category20c = Category20c[20]

def plot_top_downloaded_files(data: DataFrame, packagename: str, n: int) -> Figure:
    topn_df = data.head(n)[["file", "download_counts"]]
    source = ColumnDataSource(topn_df)
    # Reverse the data. Bokeh plots ascending in descending order
    # We have descending, so need to reverse.
    y_range = topn_df[::-1]["file"].values
    p = figure(
        title=f"Top {n} downloaded wheels for package {packagename}",
        y_range=y_range,
        x_axis_label="Download count",
        y_axis_label="File name",
    )
    p.y_range.factors = y_range
    p.hbar(y="file", right="download_counts", source=source)
    return p


def plot_wheel_coverage(data: DataFrame, packagename: str) -> Figure:
    grouped_stats = data.groupby("ftype")
    ftype_counts = grouped_stats["download_counts"].sum().reset_index()
    # Manually calculate pie chart angles since bokeh doesn't do that
    # for us
    ftype_counts["download_pcts"] = (ftype_counts["download_counts"] / ftype_counts["download_counts"].sum()) * 100
    ftype_counts = calculate_pie_chart_angle(ftype_counts, "download_counts")
    ftype_counts["color"] = list(category20c[:len(ftype_counts)])
    p = figure(title="Wheel coverage", tooltips="@ftype: @download_counts (@download_pcts%)")
    p.wedge(
        x=0,
        y=1,
        radius=0.4,
        start_angle=cumsum("angle", include_zero=True),
        end_angle=cumsum("angle"),
        legend_group="ftype",
        fill_color="color",
        source=ftype_counts,
    )
    return p


def plot_platforms(data: DataFrame, packagename: str, n: int) -> Figure:
    wheel_info = data[data["ftype"] == "wheel"]
    plat_download_counts = wheel_info.groupby("platformtag")["download_counts"].sum()
    plat_download_counts = plat_download_counts / plat_download_counts.sum()
    plat_download_counts = plat_download_counts.sort_values(ascending=False)
    plat_download_counts = plat_download_counts.reset_index()
    source = ColumnDataSource(plat_download_counts.head(n))
    # Reverse the data. Bokeh plots ascending in descending order
    # We have descending, so need to reverse.
    y_range = plat_download_counts.head(n)[::-1]["platformtag"].values
    p = figure(
        title=f"Top {n} platforms wheels were downloaded on for package {packagename}",
        x_axis_label="Platform Tag",
        y_axis_label="Proportion of downloads",
        y_range=y_range,
    )
    p.y_range.factors = y_range
    p.hbar(y="platformtag", right="download_counts", source=source)
    return p


def plot_versions(data: DataFrame, packagename: str, n: int) -> Figure:
    data["version"] = data["version"].astype(str)
    grouped_version_stats = data.groupby("version")
    grouped_version_stats = (
        grouped_version_stats["download_counts"].sum().sort_values(ascending=False)
    )
    topn_versions = grouped_version_stats.head(n)
    topn_versions["other"] = grouped_version_stats[n:].sum()
    topn_versions = topn_versions.reset_index()
    topn_versions["download_pcts"] = (topn_versions["download_counts"] / topn_versions["download_counts"].sum()) * 100
    topn_versions = calculate_pie_chart_angle(topn_versions, "download_counts")
    topn_versions["color"] = list(category20c[:len(topn_versions)])
    p = figure(
        title=f"Top {n} downloaded versions for package {packagename}",
        tooltips="@version: @download_counts (@download_pcts%)",
    )
    p.wedge(
        x=0,
        y=1,
        radius=0.4,
        start_angle=cumsum("angle", include_zero=True),
        end_angle=cumsum("angle"),
        legend_group="version",
        fill_color="color",
        source=topn_versions,
    )
    return p
