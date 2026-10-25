{{ config(materialized='view') }}

WITH source AS (

    SELECT *
    FROM {{ source('korusafe_raw', 'employees') }}

),

renamed AS (

    SELECT
        employee_id,
        organisation_id,

        TRIM(job_role) AS job_role,
        TRIM(department) AS department,
        TRIM(employment_type) AS employment_type,
        TRIM(region) AS region,

        start_date

    FROM source

)

SELECT *
FROM renamed