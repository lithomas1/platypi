-- Sometimes we can't figure out the version, platform tags, etc. from the filename.
-- This happens when we don't have a wheel or sdist(any file that doesn't end in .tar.gz, .zip, or .whl)
-- We need to pull info from the table manually in that case.
SELECT
    CASE
        -- We need to escape the last dollar sign at the end, by using $$
        WHEN REGEXP_CONTAINS (file.filename, r'^.*\.(tar.gz|zip|whl)$$')
        THEN file.filename
        ELSE CONCAT(file.filename, ' ', file.version, ' ', file.type)
    END
        AS file, count(*) AS download_counts


FROM `bigquery-public-data.pypi.file_downloads`
WHERE project = @projectname
AND DATE(timestamp)
    BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL $interval)
    AND CURRENT_DATE()
GROUP BY file
