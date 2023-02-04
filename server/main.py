import os
from string import Template

import query_gbq
from query_gbq import execute_query, init_client, init_dataset

import functions_framework
from google.cloud import bigquery

# Dict mapping query_type to the file containing the queries
query_types = {
    "packages_today": "queries/packages_today.sql",
    "package_info": "queries/package_info.sql",
}

valid_intervals = {"1-Day", "2-Week", "1-Month", "6-Month"}

def load_template(path, **kwargs):
    with open(path, "r") as file:
        template = Template(file.read())
        return template.substitute(**kwargs)
@functions_framework.http
def process_pypi_query(request):
    # Allow CORS
    # TODO: restrict origin?
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "x-requested-with",
        "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
        "Content-Type": "application/json"
    }
    # Set CORS headers for the preflight request
    # xref https://stackoverflow.com/questions/64070688/enabling-cors-google-cloud-function-python
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        return ('', 204, headers)
    query_type = request.args["query_type"]
    if query_type not in query_types.keys():
        return ("Invalid query", 400, headers)

    interval = request.args.get("interval", "1-Day")
    if interval not in valid_intervals:
        return ("Invalid query", 400, headers)
    interval = interval.replace("-", " ")

    init_client()
    init_dataset()

    job_config = None

    if query_type == "package_info":
        package_name = request.args["package_name"]
        # Parametrized queries to prevent SQL injection
        # https://cloud.google.com/bigquery/docs/parameterized-queries#using_arrays_in_parameterized_queries
        # We already validated interval to one of our values, so we'll handle that substitution ourseles.
        # Also I don't think GBq supports parametrized interval types
        query = load_template(
            query_types["package_info"], interval=interval
        )
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("projectname", "STRING", package_name),
            ]
        )
    else:
        # packages_today
        query = load_template(query_types["packages_today"])
    df = execute_query(query, job_config=job_config)
    return (df.to_json(), 200, headers)
