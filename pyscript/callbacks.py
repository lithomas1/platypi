import json

import pandas as pd
from bokeh.embed import json_item
from bokeh.layouts import column, layout, row
from bokeh.models import ColumnDataSource, Div
from bokeh.plotting import figure
from bokeh.resources import CDN
from js import JSON, Bokeh
from stats import (plot_platforms, plot_top_downloaded_files, plot_versions,
                   plot_wheel_coverage)
from util import get_tags, make_request, parse_filename
from packaging.version import Version


def plot_package_info(*args, **kwargs):
    packagename = Element("packagename").element.value
    n = 10  # TODO: Let user configure?
    df = make_request("package_info", package_name=packagename)
    df = df.sort_values("download_counts", ascending=False, ignore_index=True)
    df[["name", "version", "build_number", "tags", "ftype"]] = df["file"].apply(
        parse_filename
    )
    df[["pytag", "abitag", "platformtag"]] = df["tags"].apply(get_tags)
    p1 = plot_top_downloaded_files(df, packagename, n)
    p2 = plot_wheel_coverage(df, packagename)
    p3 = plot_platforms(df, packagename, n)
    p4 = plot_versions(df, packagename, n)
    p = layout(
        column(
            Div(text="<h4>Global stats</h4>", css_classes=["d-flex", "align-items-center", "justify-content-center"]),
            row([p1, p2]),
            row(p3, p4),
            Div(text="<h4>Version specific stats</h4>", css_classes=["d-flex", "align-items-center", "justify-content-center"]),
            Div(text="")
        ),
        sizing_mode="scale_both",
    )
    p_json = json.dumps(json_item(p, "charts"))
    Bokeh.embed.embed_item(JSON.parse(p_json))

    versions = df["version"].astype(str).unique()
    dropdown = Element("versionDropDownMenu")
    dropdown_option_template = Element("versionDropDownTemplate").select("option", from_content=True)
    for version in versions:
        dropdown_option = dropdown_option_template.clone(version, to=dropdown)
        dropdown_option.element.innerText = version
        dropdown_option.element.setAttribute("value", version)
        dropdown.element.appendChild(dropdown_option.element)
    # show dropdown
    Element("versionSelector").element.style.visibility = "visible"
    df.to_json("package-info.json") # This will write to browser in-memory virtual file system

def plot_version_package_info(*args, **kwargs):
    # TODO: we should store this value instead of hacking like this
    packagename = Element("packagename").element.value
    n = 10  # TODO: Let user configure?
    df = pd.read_json("package-info.json")
    print(df)
    version = Element("versionDropDownMenu").element.value
    df = df[df["version"] == version]
    print(df)
    p1 = plot_top_downloaded_files(df, packagename, n)
    p2 = plot_wheel_coverage(df, packagename)
    p3 = plot_platforms(df, packagename, n)
    #p4 = plot_versions(df, packagename, n)
    p = layout(
        column(
            Div(text=f"<h5>Stats for version {version}</h5>", css_classes=["d-flex", "align-items-center", "justify-content-center"]),
            row([p1, p2]),
            row(p3),
        ),
        sizing_mode="scale_both",
    )
    p_json = json.dumps(json_item(p, "version_charts"))
    Bokeh.embed.embed_item(JSON.parse(p_json))

def plot_top_packages(*args, **kwargs):
    num_top_packages = int(Element("topn").element.value)
    df = make_request("packages_today")
    df = df.sort_values("download_counts", ascending=False, ignore_index=True)
    source = ColumnDataSource(
        df.head(num_top_packages)
    )  # Take the top n most downloaded files
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
