# Architecture Overview

This document describes the architecture of the Football Analytics application.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Football-Data.org API                     │
│                  https://api.football-data.org               │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ API Requests
                            │ (Rate Limited)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Python API Client                         │
│              (football_api_client.py)                        │
│  • Handles rate limiting and retries                         │
│  • Extracts competitions, teams, matches, standings          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ Raw Data
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Database Loader                            │
│              (database_loader.py)                            │
│  • Creates raw data tables                                   │
│  • Handles upserts and data updates                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ INSERT/UPDATE
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                PostgreSQL Database                           │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ RAW SCHEMA                                           │  │
│  │  • raw.competitions                                  │  │
│  │  • raw.teams                                         │  │
│  │  • raw.matches                                       │  │
│  │  • raw.standings                                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│                            │ dbt transformations              │
│                            ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ STAGING SCHEMA (Views)                               │  │
│  │  • staging.stg_competitions                          │  │
│  │  • staging.stg_teams                                 │  │
│  │  • staging.stg_matches                               │  │
│  │  • staging.stg_standings                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│                            │ dbt transformations              │
│                            ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ ANALYTICS SCHEMA (Tables)                            │  │
│  │  • analytics.team_performance                        │  │
│  │  • analytics.match_results                           │  │
│  │  • analytics.competition_summary                     │  │
│  │  • analytics.team_head_to_head                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              │ SQL Queries
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        Metabase                              │
│  • Dashboards and visualizations                            │
│  • Team performance analytics                                │
│  • Competition statistics                                    │
│  • Match analysis                                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   Apache Airflow                             │
│  Orchestrates the entire pipeline:                           │
│  1. Extract API data                                         │
│  2. Load to database                                         │
│  3. Run dbt transformations                                  │
│  4. Run dbt tests                                            │
│  Schedule: Daily at 6 AM UTC                                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    CrewAI Agents                             │
│  AI team that plans, reviews, and improves:                  │
│  • BI Analyst: Business requirements                         │
│  • Data Analyst: dbt models review                           │
│  • Data Engineer: Pipeline review                            │
│  • Lead Engineer: Architecture and coordination              │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Extraction Layer
- **Component**: Python scripts using `requests` library
- **Source**: Football-Data.org API
- **Endpoints Used**:
  - `/v4/competitions` - List of competitions
  - `/v4/competitions/{id}/teams` - Teams in a competition
  - `/v4/competitions/{id}/matches` - Matches in a competition
  - `/v4/competitions/{id}/standings` - League standings
- **Output**: Raw JSON data loaded into PostgreSQL raw schema

### 2. Storage Layer
- **Component**: PostgreSQL database
- **Schemas**:
  - `raw`: Raw data from API with full JSON stored
  - `staging`: Cleaned and typed data (views)
  - `analytics`: Business logic and aggregations (tables)

### 3. Transformation Layer
- **Component**: dbt (data build tool)
- **Models**:
  - **Staging**: Light transformations, type casting, renaming
  - **Analytics**: Complex aggregations, joins, business logic
- **Materialization**:
  - Staging: Views (no storage overhead)
  - Analytics: Tables (optimized for query performance)

### 4. Orchestration Layer
- **Component**: Apache Airflow
- **DAG**: `football_etl_pipeline`
- **Tasks**:
  1. `extract_competitions` - Get all competitions
  2. `extract_major_competitions` - Get detailed data for major leagues
  3. `dbt_deps` - Install dbt dependencies
  4. `dbt_run` - Run transformations
  5. `dbt_test` - Validate data quality
- **Schedule**: Daily at 6 AM UTC (configurable)

### 5. Visualization Layer
- **Component**: Metabase
- **Purpose**: Business intelligence and dashboards
- **Connects To**: PostgreSQL analytics schema
- **Use Cases**:
  - Team performance dashboards
  - League standings and statistics
  - Match outcome analysis
  - Historical trends

### 6. AI Agent Layer
- **Component**: CrewAI framework
- **Agents**:
  1. **Business Intelligence Analyst**
     - Defines business requirements
     - Plans dashboards and KPIs
     - Expert in football industry

  2. **Data Analyst**
     - Reviews dbt models
     - Suggests new transformations
     - Expert in SQL and data modeling

  3. **Data Engineer**
     - Reviews ETL pipeline
     - Ensures data quality
     - Expert in Python and Airflow

  4. **Lead Data Engineer**
     - Coordinates the team
     - Translates business to technical requirements
     - Provides architecture guidance

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| API Client | Python + requests | Extract data from Football-Data.org |
| Database | PostgreSQL 15 | Store raw and transformed data |
| Transformations | dbt-core | Transform and model data |
| Orchestration | Apache Airflow | Schedule and monitor workflows |
| Visualization | Metabase | Create dashboards and reports |
| AI Agents | CrewAI + LangChain | Automated planning and review |
| Containerization | Docker Compose | Local development environment |

## Data Models

### Raw Schema
- `raw.competitions` - Competition metadata
- `raw.teams` - Team information
- `raw.matches` - Match details and scores
- `raw.standings` - League table positions

### Staging Schema
- `staging.stg_competitions` - Cleaned competition data
- `staging.stg_teams` - Cleaned team data
- `staging.stg_matches` - Cleaned match data
- `staging.stg_standings` - Cleaned standings data

### Analytics Schema
- `analytics.team_performance` - Aggregated team statistics
- `analytics.match_results` - Enriched match information
- `analytics.competition_summary` - Competition-level metrics
- `analytics.team_head_to_head` - Historical matchup statistics

## Deployment Options

### Local Development (Current)
- Docker Compose
- All services on localhost
- Good for development and testing

### Cloud Deployment (Future)

#### AWS Option
- **RDS**: PostgreSQL database
- **MWAA**: Managed Airflow
- **ECS/Fargate**: Metabase container
- **Lambda**: API extraction functions
- **S3**: dbt artifacts and logs

#### GCP Option
- **Cloud SQL**: PostgreSQL database
- **Cloud Composer**: Managed Airflow
- **Cloud Run**: Metabase container
- **Cloud Functions**: API extraction
- **GCS**: dbt artifacts and logs

## Scalability Considerations

1. **API Rate Limits**: Football-Data.org free tier has limits
   - Implement caching
   - Schedule extractions during off-peak hours
   - Consider paid tier for production

2. **Database Performance**
   - Add indexes on frequently queried columns
   - Partition large tables by date
   - Use materialized views for expensive queries

3. **dbt Performance**
   - Incremental models for large tables
   - Use dbt snapshots for slowly changing dimensions
   - Parallelize model runs

4. **Airflow Scalability**
   - Use CeleryExecutor for distributed processing
   - Add worker nodes as needed
   - Implement task-level retries and alerts

## Security Considerations

1. **API Keys**: Store in environment variables or secrets manager
2. **Database**: Use strong passwords, restrict network access
3. **Airflow**: Enable authentication, use Fernet key for encryption
4. **Metabase**: Set up user authentication and role-based access
