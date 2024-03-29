# platypi

This repo for contains the source code for a [website](https://lithomas1.github.io/platypi) for analyzing PyPI download information (via the
[Google BigQuery dataset](https://console.cloud.google.com/marketplace/product/gcp-public-data-pypi/pypi?_ga=2.229813535.-2089851614.1652743720)), and
notebooks that you can run yourself locally to do the same analysis.

This tool is meant to supplement other websites that track PyPI stats such as [PyPI stats](pypistats.org) and [PePy](pepy.tech)
by providing more fine-grained statistics about the platforms and Python versions packages are downloaded on,
to help guide package maintainers in making decisions on the kinds of platforms to support and provide wheels
for, and the kinds of platforms to drop.

## Deploying the Cloud Functions

You can deploy the function like so with the gcloud cli.
```
gcloud beta functions deploy process-pypi-query --gen2 --region=us-central1 --runtime=python310 --source=server --entry-point=process_pypi_query --trigger-http --memory=2048
```
You will need to modify the variable ``gcf_url`` to the URL of your cloud function, though.
