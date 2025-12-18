# Setup Instructions

This guide will help you set up and run the Football Analytics application locally.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ installed
- Football-Data.org API key (get one at https://www.football-data.org/)
- (Optional) OpenAI API key or DeepSeek API key for CrewAI agents

## Project Structure

```
dbt-on-aws-with-ai/
├── docker/                    # Docker initialization scripts
│   └── init-db.sql           # PostgreSQL database initialization
├── dbt_football/             # dbt project
│   ├── models/
│   │   ├── staging/          # Staging models
│   │   └── analytics/        # Analytics models
│   ├── dbt_project.yml
│   └── profiles.yml
├── src/
│   ├── api_extraction/       # API extraction scripts
│   │   ├── football_api_client.py
│   │   ├── database_loader.py
│   │   └── extract_football_data.py
│   ├── airflow/
│   │   └── dags/             # Airflow DAGs
│   └── crewai_agents/        # AI agents
│       ├── agents.py
│       ├── tasks.py
│       └── crew.py
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Step 1: Environment Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:
```bash
# Required
FOOTBALL_API_KEY=your_football_api_key_here

# Optional (for CrewAI agents)
OPENAI_API_KEY=your_openai_api_key_here
# OR
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

## Step 2: Start Docker Services

Start all services (PostgreSQL, Airflow, Metabase):

```bash
docker-compose up -d
```

This will:
- Start PostgreSQL on port 5432
- Initialize the database with schemas (raw, staging, analytics)
- Start Airflow webserver on port 8080
- Start Airflow scheduler
- Start Metabase on port 3000

Wait a few minutes for all services to be healthy.

## Step 3: Verify Services

Check that all services are running:

```bash
docker-compose ps
```

All services should show as "healthy" or "running".

Access the web interfaces:
- **Airflow**: http://localhost:8080 (username: `admin`, password: `admin`)
- **Metabase**: http://localhost:3000 (setup required on first visit)

## Step 4: Install Python Dependencies

If you want to run scripts locally (outside Docker):

```bash
pip install -r requirements.txt
```

## Step 5: Test API Extraction

Test the API extraction script locally:

```bash
cd src/api_extraction
python extract_football_data.py
```

This will:
- Extract competitions from Football-Data.org API
- Extract teams, matches, and standings for major European leagues
- Load data into PostgreSQL (raw schema)

## Step 6: Run dbt Transformations

Transform raw data into analytics models:

```bash
cd dbt_football
dbt deps --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
```

This will create views in the `staging` schema and tables in the `analytics` schema.

## Step 7: Configure Metabase

1. Open http://localhost:3000
2. Complete the initial setup wizard
3. Add a database connection:
   - Database type: PostgreSQL
   - Host: `postgres` (or `localhost` if connecting from outside Docker)
   - Port: `5432`
   - Database name: `football_analytics`
   - Username: `airflow`
   - Password: `airflow`

4. Start creating dashboards using the analytics tables:
   - `analytics.team_performance`
   - `analytics.match_results`
   - `analytics.competition_summary`
   - `analytics.team_head_to_head`

## Step 8: Trigger Airflow DAG

1. Open Airflow UI at http://localhost:8080
2. Find the `football_etl_pipeline` DAG
3. Enable it by clicking the toggle switch
4. Click "Trigger DAG" to run it manually

The DAG will:
1. Extract competitions
2. Extract data for major competitions
3. Run dbt dependencies
4. Run dbt transformations
5. Run dbt tests

## Step 9: Run CrewAI Agents (Optional)

To run the AI team that reviews and improves the implementation:

```bash
cd src/crewai_agents
python crew.py
```

The agents will:
1. **BI Analyst**: Define business requirements
2. **Lead Data Engineer**: Create technical specifications
3. **Data Engineer**: Review pipeline implementation
4. **Data Analyst**: Review dbt models
5. **BI Analyst**: Plan Metabase visualizations
6. **Lead Data Engineer**: Summarize findings and next steps

## Troubleshooting

### API Rate Limiting
Football-Data.org free tier has rate limits. The client handles this automatically with retries.

### Docker Services Not Starting
```bash
# Check logs
docker-compose logs -f

# Restart services
docker-compose down
docker-compose up -d
```

### Database Connection Issues
```bash
# Connect to PostgreSQL directly
docker exec -it football_postgres psql -U airflow -d football_analytics

# List tables
\dt raw.*
\dt staging.*
\dt analytics.*
```

### dbt Errors
```bash
# Check dbt debug
cd dbt_football
dbt debug --profiles-dir .

# View dbt logs
cat target/run.log
```

## Stopping Services

Stop all services:
```bash
docker-compose down
```

Stop and remove all data:
```bash
docker-compose down -v
```

## Next Steps

1. Explore the data in PostgreSQL
2. Create custom dbt models for specific analytics
3. Build Metabase dashboards
4. Schedule the Airflow DAG to run daily
5. Run CrewAI agents for recommendations
6. Deploy to cloud (AWS, GCP, Azure)
