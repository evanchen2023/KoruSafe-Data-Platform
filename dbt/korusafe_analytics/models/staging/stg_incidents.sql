{{ config(materialized='view') }}

WITH source AS (

    SELECT *
    FROM {{ source('korusafe_raw', 'incidents') }}

),

renamed AS (

    SELECT
        incident_id,
        organisation_id,
        employee_id,

        incident_date,

        TRIM(incident_type) AS incident_type,
        TRIM(severity) AS severity,
        TRIM(location) AS location,
        TRIM(description) AS description

    FROM source

)

SELECT *
FROM renamed