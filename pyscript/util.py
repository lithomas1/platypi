from io import StringIO
from math import pi

import pandas as pd
from js import XMLHttpRequest
from packaging.utils import (InvalidSdistFilename, InvalidWheelFilename,
                             Version, parse_sdist_filename,
                             parse_wheel_filename)

# A dictionary of aliases from old to new platform tags
# as defined in PEP 600.
# https://peps.python.org/pep-0600/#legacy-manylinux-tags
# We will use this to de-dup in get_tags
legacy_tag_aliases = {
    "manylinux1_x86_64": "manylinux_2_5_x86_64",
    "manylinux1_i686": "manylinux_2_5_i686",
    "manylinux2010_x86_64": "manylinux_2_12_x86_64",
    "manylinux2010_i686": "manylinux_2_12_i686",
    "manylinux2014_x86_64": "manylinux_2_17_x86_64",
    "manylinux2014_i686": "manylinux_2_17_i686",
    "manylinux2014_aarch64": "manylinux_2_17_aarch64",
    "manylinux2014_armv7l": "manylinux_2_17_armv7l",
    "manylinux2014_ppc64": "manylinux_2_17_ppc64",
    "manylinux2014_ppc64le": "manylinux_2_17_ppc64le",
    "manylinux2014_s390x": "manylinux_2_17_s390x",
}


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
            # Get tag alias if exists, otherwise use current tag platform
            platforms.add(legacy_tag_aliases.get(tag.platform, tag.platform))

        # Can still have multiple interpreters, e.g. wheel w/ Python Limited API can
        # support multiple Python interpreter versions
        interpreters = tuple(interpreters)
        abis = tuple(abis)
        platforms = str(
            platforms.pop()
        )  # There should only be one unique platform tag now

        # Flatten if possible
        if len(interpreters) == 1:
            interpreters = interpreters[0]
        if len(abis) == 1:
            abis = abis[0]
    else:
        interpreters = None
        abis = None
        platforms = None

    return pd.Series([interpreters, abis, platforms])


def calculate_pie_chart_angle(data: pd.DataFrame, count_col: str) -> pd.DataFrame:
    data["angle"] = data[count_col] / data[count_col].sum() * 2 * pi
    return data
