*** 5 个 Source Systems:
** System 1 — Workforce
* employees:
employee_id
organisation_id
job_role
department
employment_type
region
start_date

System 2 — Organisation
organisations

字段：

organisation_id
organisation_name
industry
employee_count
region
created_date

System 3 — Safety
incidents

字段：

incident_id
organisation_id
employee_id
incident_date
incident_type
severity
location
description

System 4 — Injury
injuries

字段：

injury_id
incident_id
employee_id
injury_type
body_part
severity
medical_cost
days_off_work

System 5 — Claims
claims

字段：

claim_id
injury_id
employee_id
claim_date
claim_type
claim_amount
claim_status