import json
import pandas as pd
from js import Bokeh, JSON
from bokeh.embed import json_item
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.models import ColumnDataSource
from bokeh.layouts import layout
from util import make_request, parse_filename
from stats import plot_top_downloaded_files, plot_wheel_coverage


def plot_package_info(*args, **kwargs):
    packagename = Element("packagename").element.value
    df = make_request("package_info", package_name=packagename)
    df = df.sort_values("download_counts", ascending=False, ignore_index=True)
    df[["name", "version", "build_number", "tags", "ftype"]] = df["file"].apply(parse_filename)
    p1 = plot_top_downloaded_files(df, packagename, 10)
    p2 = plot_wheel_coverage(df, packagename)
    p = layout([[p1,p2]], sizing_mode="scale_both")
    p_json = json.dumps(json_item(p, "charts"))
    Bokeh.embed.embed_item(JSON.parse(p_json))

def plot_top_packages(*args, **kwargs):
    num_top_packages = int(Element("topn").element.value)
    df = make_request("packages_today")
    df = df.sort_values("download_counts", ascending=False, ignore_index=True)
    source = ColumnDataSource(df.head(num_top_packages))  # Take the top n most downloaded files
    p = figure(
        title=f"Top {num_top_packages} packages",
        y_range=df.head(num_top_packages)["project"].values,
        x_axis_label="Download count",
        y_axis_label="Package name",
    )
    p.sizing_mode = "scale_both"  # autoscale width/height
    p.hbar(y="project", right="download_counts", source=source)
    p_json = json.dumps(json_item(p, "charts"))
    Bokeh.embed.embed_item(JSON.parse(p_json))
