# platypi

WIP Repo for analyzing PyPI download information.

This tool is meant to supplement other websites that track PyPI stats such as (pypistats.org) and (pepy.tech)
by providing more fine-grained statistics about the platforms and Python versions packages are downloaded on,
to help guide package maintainers in making decisions on the kinds of platforms to support and provide wheels
for, and the kinds of platforms to drop.

Currently, a prototype (hosted on [Kaggle](https://www.kaggle.com/code/lithomas1/pypi-download-analysis)),
with all the stats to be scraped from the [Google BigQuery dataset](https://console.cloud.google.com/marketplace/product/gcp-public-data-pypi/pypi?_ga=2.229813535.-2089851614.1652743720) is in progress.

Eventually, the hope is to consolidate these stats into a webpage.
