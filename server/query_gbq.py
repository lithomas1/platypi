import json
import os

from google.cloud import bigquery

client = None
dataset = None


def init_client():
    global client
    if not client:
        client = bigquery.Client()


def init_dataset():
    global dataset
    if dataset:
        # Already initialized
        return
    if client is None:
        raise ValueError("Client must be intialized before getting dataset")
    dataset_ref = client.dataset("pypi", project="bigquery-public-data")
    dataset = client.get_dataset(dataset_ref)


def execute_query(query, job_config=None):
    query_job = client.query(query, job_config)
    return query_job.to_dataframe()
