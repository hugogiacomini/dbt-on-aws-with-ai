# Usage Guide

This guide explains how to use the Football Analytics application after setup.

## Quick Start

After completing the setup in `SETUP.md`:

```bash
# 1. Start all services
docker-compose up -d

# 2. Wait for services to be healthy (2-3 minutes)
docker-compose ps

# 3. Trigger the ETL pipeline
# Access Airflow UI at http://localhost:8080
# Login: admin / admin
# Enable and trigger the "football_etl_pipeline" DAG
```

## Using the API Extraction Scripts

### Run Extraction Manually

Extract data outside of Airflow:

```bash
cd src/api_extraction
export $(cat ../../.env | xargs)  # Load environment variables
python3 extract_football_data.py
```

### Customize What Data to Extract

Edit `extract_football_data.py` to change which competitions to extract:

```python
major_competition_ids = [
    2021,  # Premier League
    2014,  # La Liga
    2002,  # Bundesliga
    # Add more competition IDs here
]
```

Common competition IDs:

- **2021**: Premier League (England)
- **2014**: La Liga (Spain)
- **2002**: Bundesliga (Germany)
- **2019**: Serie A (Italy)
- **2015**: Ligue 1 (France)
- **2001**: UEFA Champions League
- **2146**: UEFA Europa League
- **2152**: Championship (England)
- **2003**: Eredivisie (Netherlands)
- **2013**: Série A (Brazil)

### Extract Specific Date Range

Modify the date range in `extract_competition_data()`:

```python
date_from = '2024-01-01'
date_to = '2024-12-31'
matches = api_client.get_competition_matches(
    comp_id,
    date_from=date_from,
    date_to=date_to
)
```

## Working with dbt Models

### Run dbt Transformations

```bash
cd dbt_football

# Install dependencies
dbt deps --profiles-dir .

# Run all models
dbt run --profiles-dir .

# Run specific model
dbt run --select stg_matches --profiles-dir .

# Run with full refresh (drop and recreate tables)
dbt run --full-refresh --profiles-dir .
```

### Test Data Quality

```bash
# Run all tests
dbt test --profiles-dir .

# Test specific model
dbt test --select stg_matches --profiles-dir .
```

### Generate Documentation

```bash
# Generate and serve documentation
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

### Create Custom Models

Add a new analytics model in `dbt_football/models/analytics/`:

```sql
-- models/analytics/top_scorers.sql
{{ config(materialized='table') }}

select
    home_team_name as team_name,
    sum(home_score) as total_goals_scored,
    count(*) as matches_played,
    round(sum(home_score)::numeric / count(*), 2) as avg_goals_per_match
from {{ ref('stg_matches') }}
where match_status = 'FINISHED'
group by home_team_name
order by total_goals_scored desc
limit 20
```

Then run:

```bash
dbt run --select top_scorers --profiles-dir .
```

## Using Airflow

### Access Airflow UI

- URL: <http://localhost:8080>
- Username: `admin`
- Password: `admin`

### Trigger DAG Manually

1. Navigate to DAGs page
2. Find `football_etl_pipeline`
3. Click the play button (▶) to trigger

### Monitor DAG Execution

1. Click on the DAG name
2. View the Graph or Grid view
3. Click on individual tasks to see logs

### Modify DAG Schedule

Edit `src/airflow/dags/football_etl_dag.py`:

```python
dag = DAG(
    'football_etl_pipeline',
    schedule_interval='0 6 * * *',  # Daily at 6 AM UTC
    # Change to:
    # '0 */6 * * *'  # Every 6 hours
    # '0 0 * * 0'    # Weekly on Sunday
    # None           # Manual trigger only
)
```

Restart Airflow to apply changes:

```bash
docker-compose restart airflow-scheduler airflow-webserver
```

### View Task Logs

1. Click on a task in the DAG graph
2. Click "Log" button
3. View detailed execution logs

## Using Metabase

### Initial Setup

1. Access <http://localhost:3000>
2. Create admin account
3. Add database connection:
   - **Name**: Football Analytics
   - **Database type**: PostgreSQL
   - **Host**: `postgres` (or `localhost` if outside Docker)
   - **Port**: `5432`
   - **Database name**: `football_analytics`
   - **Username**: `airflow`
   - **Password**: `airflow`

### Create Your First Dashboard

1. Click "New" → "Dashboard"
2. Name it "Football Overview"
3. Click "Add a question"

#### Example Question 1: Top Teams by Points

```sql
SELECT
  team_name,
  competition_id,
  points,
  total_wins,
  total_draws,
  total_losses,
  goal_difference
FROM analytics.team_performance
ORDER BY points DESC
LIMIT 20
```

Choose visualization: **Table** or **Bar chart**

#### Example Question 2: Goals Over Time

```sql
SELECT
  DATE_TRUNC('month', match_date) as month,
  SUM(total_goals) as total_goals,
  AVG(total_goals) as avg_goals_per_match
FROM analytics.match_results
GROUP BY month
ORDER BY month
```

Choose visualization: **Line chart**

#### Example Question 3: Home vs Away Win Rate

```sql
SELECT
  competition_name,
  home_win_percentage,
  away_win_percentage,
  draw_percentage
FROM analytics.competition_summary
ORDER BY competition_name
```

Choose visualization: **Grouped bar chart**

### Dashboard Filters

Add filters to your dashboard:

1. Edit dashboard
2. Add filter (e.g., "Competition", "Date Range")
3. Connect filter to questions
4. Save dashboard

## Using CrewAI Agents

### Run the AI Team

Execute the crew to get recommendations:

```bash
cd src/crewai_agents
export $(cat ../../.env | xargs)  # Load environment variables
python3 crew.py
```

The agents will:

1. Analyze business requirements
2. Review technical implementation
3. Suggest improvements
4. Provide recommendations

### Customize Agent Behavior

Edit `agents.py` to modify agent roles:

```python
def create_bi_analyst() -> Agent:
    return Agent(
        role='Business Intelligence Analyst',
        goal='Your custom goal here',
        backstory="""Your custom backstory""",
        # Adjust temperature for creativity
        llm=OpenAI(temperature=0.5)  # Lower = more focused
    )
```

### Add Custom Tasks

Edit `tasks.py` to add new tasks:

```python
def create_custom_task(agent) -> Task:
    return Task(
        description="""Your task description""",
        agent=agent,
        expected_output="""Expected output format"""
    )
```

Then add to the crew in `crew.py`.

## Querying the Database Directly

### Using psql

```bash
# Connect to database
docker exec -it football_postgres psql -U airflow -d football_analytics

# List all schemas
\dn

# List tables in raw schema
\dt raw.*

# Query data
SELECT * FROM analytics.team_performance LIMIT 5;

# Exit
\q
```

### Using Python

```python
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST', 'localhost'),
    port=os.getenv('POSTGRES_PORT', 5432),
    database=os.getenv('POSTGRES_DB', 'football_analytics'),
    user=os.getenv('POSTGRES_USER', 'airflow'),
    password=os.getenv('POSTGRES_PASSWORD', 'airflow')
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM analytics.competition_summary")
results = cursor.fetchall()

for row in results:
    print(row)

cursor.close()
conn.close()
```

## Common Workflows

### Daily Operations

1. **Check Airflow**: Verify DAG ran successfully
2. **Review Logs**: Check for any errors
3. **Refresh Metabase**: Dashboards update automatically
4. **Monitor Data**: Ensure data is fresh

### Adding New Competition

1. Find competition ID from API or documentation
2. Add to `major_competition_ids` in `extract_football_data.py`
3. Run extraction script or wait for scheduled DAG
4. Verify data in database
5. Update Metabase dashboards

### Debugging Issues

#### API Extraction Fails

```bash
# Check API key
echo $FOOTBALL_API_KEY

# Test API manually
curl -H "X-Auth-Token: YOUR_API_KEY" \
  https://api.football-data.org/v4/competitions

# Check logs
docker-compose logs airflow-scheduler
```

#### dbt Model Fails

```bash
# Run with debug flag
dbt run --select model_name --profiles-dir . --debug

# Check compiled SQL
cat dbt_football/target/compiled/dbt_football/models/analytics/model_name.sql

# Test database connection
dbt debug --profiles-dir .
```

#### Airflow Task Stuck

```bash
# View task logs
docker-compose logs airflow-scheduler | grep task_id

# Restart scheduler
docker-compose restart airflow-scheduler

# Clear task state in Airflow UI
# Go to task → Clear
```

## Performance Optimization

### Database Indexes

Add indexes for frequently queried columns:

```sql
-- Connect to database
docker exec -it football_postgres psql -U airflow -d football_analytics

-- Add indexes
CREATE INDEX idx_matches_competition ON raw.matches(competition_id);
CREATE INDEX idx_matches_date ON raw.matches(utc_date);
CREATE INDEX idx_matches_teams ON raw.matches(home_team_id, away_team_id);
```

### dbt Incremental Models

Convert large tables to incremental:

```sql
{{ config(
    materialized='incremental',
    unique_key='match_id'
) }}

select * from {{ ref('stg_matches') }}

{% if is_incremental() %}
where match_date > (select max(match_date) from {{ this }})
{% endif %}
```

## Maintenance

### Update Data

```bash
# Trigger Airflow DAG manually
# Or wait for scheduled run
```

### Backup Database

```bash
# Backup all data
docker exec football_postgres pg_dump -U airflow football_analytics > backup.sql

# Restore from backup
cat backup.sql | docker exec -i football_postgres psql -U airflow football_analytics
```

### Clean Up Old Data

```sql
-- Delete old matches (e.g., older than 2 years)
DELETE FROM raw.matches
WHERE utc_date < NOW() - INTERVAL '2 years';

-- Vacuum to reclaim space
VACUUM FULL;
```

## Troubleshooting

### Service Won't Start

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs service_name

# Restart specific service
docker-compose restart service_name

# Rebuild containers
docker-compose down
docker-compose build
docker-compose up -d
```

### Out of Memory

```bash
# Check Docker resources
docker stats

# Increase memory in Docker settings
# Docker Desktop → Settings → Resources
```

### API Rate Limit Hit

- Free tier: 10 requests per minute
- Solution: Upgrade to paid tier or reduce extraction frequency
- The client automatically handles rate limits with retries

## Next Steps

1. **Explore the data**: Query tables in PostgreSQL
2. **Create dashboards**: Build visualizations in Metabase
3. **Add custom models**: Extend dbt with your own analytics
4. **Run AI agents**: Get recommendations from CrewAI team
5. **Deploy to cloud**: Follow cloud deployment guides
6. **Share insights**: Export dashboards and reports
