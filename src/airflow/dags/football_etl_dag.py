"""Airflow DAG for Football-Data.org ETL pipeline."""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import sys
import os

# Add the api_extraction module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'plugins'))

from api_extraction.extract_football_data import (
    extract_competitions,
    extract_competition_data,
)
from api_extraction.football_api_client import FootballAPIClient
from api_extraction.database_loader import DatabaseLoader


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'football_etl_pipeline',
    default_args=default_args,
    description='ETL pipeline for Football-Data.org API',
    schedule_interval='0 6 * * *',  # Daily at 6 AM UTC
    start_date=days_ago(1),
    catchup=False,
    tags=['football', 'etl', 'api'],
)


def extract_competitions_task():
    """Task to extract competitions data."""
    api_client = FootballAPIClient()
    db_loader = DatabaseLoader()
    extract_competitions(api_client, db_loader)


def extract_major_competitions_task():
    """Task to extract data for major competitions."""
    api_client = FootballAPIClient()
    db_loader = DatabaseLoader()

    # Major European competitions
    major_competition_ids = [
        2021,  # Premier League
        2014,  # La Liga
        2002,  # Bundesliga
        2019,  # Serie A
        2015,  # Ligue 1
        2001,  # Champions League
        2146,  # Europa League
    ]

    extract_competition_data(api_client, db_loader, major_competition_ids)


# Define tasks
task_extract_competitions = PythonOperator(
    task_id='extract_competitions',
    python_callable=extract_competitions_task,
    dag=dag,
)

task_extract_major_competitions = PythonOperator(
    task_id='extract_major_competitions',
    python_callable=extract_major_competitions_task,
    dag=dag,
)

# dbt tasks
task_dbt_deps = BashOperator(
    task_id='dbt_deps',
    bash_command='cd /opt/airflow/dbt_football && dbt deps --profiles-dir .',
    dag=dag,
)

task_dbt_run = BashOperator(
    task_id='dbt_run',
    bash_command='cd /opt/airflow/dbt_football && dbt run --profiles-dir .',
    dag=dag,
)

task_dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command='cd /opt/airflow/dbt_football && dbt test --profiles-dir .',
    dag=dag,
)

# Define task dependencies
task_extract_competitions >> task_extract_major_competitions
task_extract_major_competitions >> task_dbt_deps
task_dbt_deps >> task_dbt_run
task_dbt_run >> task_dbt_test
