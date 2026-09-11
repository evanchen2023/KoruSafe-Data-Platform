# KoruSafe Data Platform

## Overview

KoruSafe is an enterprise-style data engineering platform designed to integrate workplace safety, injury and claims data from multiple operational systems.

The project currently provides a local foundation for generating synthetic operational data, loading it into PostgreSQL, and validating core data quality rules with pytest.

## Business Problem

Workplace safety data is often spread across separate systems owned by different business functions. Organisation data, workforce records, safety incidents, injury details and insurance claims may all exist in different formats and locations.

This creates several problems:

- Safety teams cannot easily see incident trends across organisations, regions or departments.
- Claims teams may struggle to connect claim cost back to the original incident and employee context.
- Business leaders lack a reliable single source of truth for workplace risk and operational safety performance.
- Data quality issues such as missing keys, invalid dates or broken relationships can reduce trust in reporting.

KoruSafe addresses this by modelling the key source systems, standardising their data into CSV files, and loading them into a PostgreSQL database for future analytics, transformation and reporting.

## Architecture

Current local architecture:

```text
Synthetic source data
        |
        v
data_generator/generate_data.py (For testing right now)
        |
        v
CSV files in data_generator/data/generated/
        |
        v
ingestion/load_to_postgres.py
        |
        v
PostgreSQL running in Docker
        |
        v
Data validation with pytest
```

PostgreSQL is provided by Docker Compose using the `postgres:16` image. The database runs inside the `korusafe-postgres` container and is exposed to the local machine on port `5432`.

Default database connection:

```text
postgresql://postgres:postgres@localhost:5432/korusafe
```

The ingestion script also supports overriding the connection string with the `DATABASE_URL` environment variable.

## Data Sources

The platform currently models five operational source systems:

| Source System | Table | Description |
| --- | --- | --- |
| Organisation | `organisations` | Company-level organisation, industry, region and employee count data |
| Workforce | `employees` | Employee records linked to organisations |
| Safety | `incidents` | Workplace safety incidents linked to employees and organisations |
| Injury | `injuries` | Injury records linked to incidents and employees |
| Claims | `claims` | Insurance or compensation claims linked to injuries and employees |

Generated CSV files:

```text
data_generator/data/generated/organisations.csv
data_generator/data/generated/employees.csv
data_generator/data/generated/incidents.csv
data_generator/data/generated/injuries.csv
data_generator/data/generated/claims.csv
```

## Technology Stack

- Python
- PostgreSQL
- Docker
- SQL
- Pandas
- SQLAlchemy
- Pytest
- Faker (For testing right now)

## Data Model

The current data model is centred on workplace safety events and their downstream injury and claims outcomes.

```text
organisations
    |
    | organisation_id
    v
employees
    |
    | employee_id, organisation_id
    v
incidents
    |
    | incident_id, employee_id
    v
injuries
    |
    | injury_id, employee_id
    v
claims
```

### organisations

| Column | Description |
| --- | --- |
| `organisation_id` | Unique organisation identifier |
| `organisation_name` | Organisation name |
| `industry` | Industry category |
| `employee_count` | Number of employees |
| `region` | Operating region |
| `created_date` | Organisation creation date |

### employees

| Column | Description |
| --- | --- |
| `employee_id` | Unique employee identifier |
| `organisation_id` | Organisation the employee belongs to |
| `job_role` | Employee role |
| `department` | Department |
| `employment_type` | Employment type |
| `region` | Employee region |
| `start_date` | Employment start date |

### incidents

| Column | Description |
| --- | --- |
| `incident_id` | Unique incident identifier |
| `organisation_id` | Organisation where the incident occurred |
| `employee_id` | Employee involved in the incident |
| `incident_date` | Incident date |
| `incident_type` | Type of safety incident |
| `severity` | Incident severity |
| `location` | Incident location |
| `description` | Incident description |

### injuries

| Column | Description |
| --- | --- |
| `injury_id` | Unique injury identifier |
| `incident_id` | Related incident |
| `employee_id` | Injured employee |
| `injury_type` | Type of injury |
| `body_part` | Affected body part |
| `severity` | Injury severity |
| `medical_cost` | Estimated medical cost |
| `days_off_work` | Days away from work |

### claims

| Column | Description |
| --- | --- |
| `claim_id` | Unique claim identifier |
| `injury_id` | Related injury |
| `employee_id` | Employee associated with the claim |
| `claim_date` | Claim submission date |
| `claim_type` | Type of claim |
| `claim_amount` | Claim amount |
| `claim_status` | Claim processing status |

## Data Pipeline

### 1. Generate source data

Run the data generator to create synthetic CSV files:

```bash
.venv/bin/python data_generator/generate_data.py
```

The generator creates deterministic sample data using Faker and a fixed random seed.

### 2. Start PostgreSQL

Start the local PostgreSQL container:

```bash
docker compose up -d
```

Check that the container is running:

```bash
docker ps
```

### 3. Load CSV files into PostgreSQL

Run the ingestion script:

```bash
.venv/bin/python ingestion/load_to_postgres.py
```

The script loads tables in dependency order:

```text
organisations -> employees -> incidents -> injuries -> claims
```

Before loading, the script truncates the target tables so repeated local runs do not fail because of duplicate primary keys.

### 4. Validate the loaded data manually

Connect to PostgreSQL:

```bash
docker exec -it korusafe-postgres psql -U postgres -d korusafe
```

Example checks:

```sql
SELECT COUNT(*) FROM organisations;
SELECT COUNT(*) FROM employees;
SELECT COUNT(*) FROM incidents;
SELECT COUNT(*) FROM injuries;
SELECT COUNT(*) FROM claims;
```

## Data Quality

The test suite validates the generated CSV files before ingestion.

Current checks include:

- All expected CSV files exist.
- All CSV files can be read by pandas.
- CSV columns match the expected table schemas.
- Primary keys are unique and not null.
- Employee counts are positive.
- Medical costs, days off work and claim amounts are non-negative.
- Date columns can be parsed as valid dates.
- Employee records reference valid organisations.
- Incident records reference valid organisations and employees.
- Injury records reference valid incidents and employees.
- Claim records reference valid injuries and employees.

Run tests:

```bash
.venv/bin/pytest -q
```

## Project Roadmap

### Week 1 - Foundation & Ingestion

- Define source systems and core data model.
- Generate synthetic operational CSV data.
- Run PostgreSQL locally with Docker.
- Load CSV files into PostgreSQL.
- Add initial pytest data quality checks.

### Week 2 - Airflow + dbt + Data Warehouse

- Add Airflow orchestration for generation, ingestion and validation.
- Introduce dbt models for staging and warehouse layers.
- Build fact and dimension tables for analytics.
- Add dbt tests for schema, uniqueness, relationships and accepted values.

### Week 3 - AWS + Governance + CI/CD + Monitoring

- Move storage and orchestration patterns toward AWS services.
- Add CI/CD checks for tests and data pipeline code.
- Add monitoring for pipeline failures and row count anomalies.
- Document data ownership, lineage and governance rules.

### Week 4 - Data Product + ML + Documentation

- Build analytics-ready safety and claims data products.
- Add dashboards or reporting outputs for business users.
- Explore ML use cases such as incident severity prediction or claim cost estimation.
- Finalise architecture documentation and project presentation materials.

## Local Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the database:

```bash
docker compose up -d
```

Run tests:

```bash
.venv/bin/pytest -q
```

Load data:

```bash
.venv/bin/python ingestion/load_to_postgres.py
```
