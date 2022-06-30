import os
import json
from google.cloud import bigquery

client = None
dataset = None


def init_client():
    global client
    # Convert env var key back to a json file
    json.dump(
        json.loads(os.getenv("GBQ_SERVICE_ACCOUNT_KEY")),
        open("service_account.json", "w"),
    )
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account.json"

    client = bigquery.Client()


def init_dataset():
    global dataset
    if client is None:
        raise ValueError("Client must be intialized before getting dataset")
    dataset_ref = client.dataset("pypi", project="bigquery-public-data")
    dataset = client.get_dataset(dataset_ref)


def execute_query(query):
    query_job = client.query(query)
    return query_job.to_dataframe()
