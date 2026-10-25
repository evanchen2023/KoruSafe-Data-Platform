{{ config(materialized='view') }}

WITH source AS (

    SELECT *
    FROM {{ source('korusafe_raw', 'injuries') }}

),

renamed AS (

    SELECT
        injury_id,
        incident_id,
        employee_id,

        TRIM(injury_type) AS injury_type,
        TRIM(body_part) AS body_part,
        TRIM(severity) AS severity,

        medical_cost,
        days_off_work

    FROM source

)

SELECT *
FROM renamed