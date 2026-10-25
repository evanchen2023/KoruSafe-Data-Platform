{{ config(materialized='view') }}

WITH source AS (

    SELECT *
    FROM {{ source('korusafe_raw', 'claims') }}

),

renamed AS (

    SELECT
        claim_id,
        injury_id,
        employee_id,

        claim_date,

        TRIM(claim_type) AS claim_type,
        claim_amount,
        TRIM(claim_status) AS claim_status

    FROM source

)

SELECT *
FROM renamed