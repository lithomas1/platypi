SELECT project, count(*) AS download_counts
FROM `bigquery-public-data.pypi.file_downloads`
WHERE DATE(timestamp) = CURRENT_DATE()
GROUP BY project