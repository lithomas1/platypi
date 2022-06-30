from packaging.utils import (
    parse_wheel_filename,
    parse_sdist_filename,
    InvalidWheelFilename,
    InvalidSdistFilename,
    Version,
)
from io import StringIO
from js import XMLHttpRequest
import pandas as pd


def make_request(request_type, **kwargs):
    # Pyodide doesn't have built-in support for CORS
    # Workaround it
    url = f"https://platypi.herokuapp.com/query?query_type={request_type}"  # &package_name={packagename}"
    for key, value in kwargs.items():
        url += f"&{key}={value}"
    req = XMLHttpRequest.new()
    req.open("GET", url, False)
    req.send(None)
    return pd.read_json(StringIO(req.response))


def parse_filename(file):
    name, version, build, tags, ftype = None, None, None, None, None
    try:
        name, version, build, tags = parse_wheel_filename(file)
        ftype = "wheel"
    except InvalidWheelFilename:
        try:
            # No build number or tags on sdist on sdists
            name, version = parse_sdist_filename(file)
            ftype = "sdist"
        except InvalidSdistFilename:
            # Some weird people like to download old packages for EOL Pythons I guess...
            # We just need to extract info we pulled from the GBQ table here
            name, version, ftype = file.split(" ")
            version = Version(version)

    return pd.Series([name, version, build, tags, ftype])


def get_tags(tags):
    interpreters = set()
    abis = set()
    platforms = set()
    if tags is not None:
        for tag in list(tags):
            interpreters.add(tag.interpreter)
            abis.add(tag.abi)
            platforms.add(tag.platform)

    interpreters = frozenset(interpreters)
    abis = frozenset(abis)
    platforms = frozenset(platforms)

    return pd.Series([interpreters, abis, platforms])
