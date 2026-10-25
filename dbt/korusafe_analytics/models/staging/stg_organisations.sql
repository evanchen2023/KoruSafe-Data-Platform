{{ config(materialized='view') }}

WITH source AS (

    SELECT *
    FROM {{ source('korusafe_raw', 'organisations') }}

),

renamed AS (

    SELECT
        organisation_id,
        TRIM(organisation_name) AS organisation_name,
        TRIM(industry) AS industry,
        employee_count,
        TRIM(region) AS region,
        created_date

    FROM source

)

SELECT *
FROM renamed