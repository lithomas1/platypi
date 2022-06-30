import json
import pandas as pd
from js import Bokeh, JSON
from bokeh.embed import json_item
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.models import ColumnDataSource
from util import make_request


def query_and_render(*args, **kwargs):
    packagename = Element("packagename").element.value
    # https://github.com/pyodide/pyodide/issues/2659#issuecomment-1147533310
    # url = f"https://platypi.herokuapp.com/query?query_type=package_info&package_name={packagename}"
    # req = XMLHttpRequest.new()
    # req.open("GET", url, False)
    # req.send(None)
    # df = pd.read_json(StringIO(req.response))
    df = make_request("package_info", package_name=packagename)
    df = df.sort_values("download_counts", ascending=False, ignore_index=True)
    source = ColumnDataSource(df.head(10))  # Take the top 10 most downloaded files
    p = figure(
        title=f"Top 10 downloaded files for package {packagename}",
        y_range=df.head(10)["file"].values,
        x_axis_label="Download count",
        y_axis_label="File name",
    )
    p.sizing_mode = "scale_both"  # autoscale width/height
    p.hbar(y="file", right="download_counts", source=source)
    p_json = json.dumps(json_item(p, "bar_chart"))
    Bokeh.embed.embed_item(JSON.parse(p_json))
