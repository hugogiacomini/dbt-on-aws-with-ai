"""Script to verify the application setup and configuration."""

import os
import sys
from pathlib import Path


def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a file exists."""
    if Path(filepath).exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} - NOT FOUND")
        return False


def check_directory_exists(dirpath: str, description: str) -> bool:
    """Check if a directory exists."""
    if Path(dirpath).is_dir():
        print(f"✓ {description}: {dirpath}")
        return True
    else:
        print(f"✗ {description}: {dirpath} - NOT FOUND")
        return False


def main():
    """Run verification checks."""
    print("=" * 80)
    print("Football Analytics Application - Setup Verification")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 0

    # Check project structure
    print("[1] Checking Project Structure...")
    print("-" * 80)

    directories = [
        ("src/api_extraction", "API extraction directory"),
        ("src/airflow/dags", "Airflow DAGs directory"),
        ("src/crewai_agents", "CrewAI agents directory"),
        ("dbt_football/models/staging", "dbt staging models"),
        ("dbt_football/models/analytics", "dbt analytics models"),
        ("docker", "Docker configuration"),
    ]

    for dirpath, description in directories:
        total_checks += 1
        if check_directory_exists(dirpath, description):
            checks_passed += 1

    print()

    # Check configuration files
    print("[2] Checking Configuration Files...")
    print("-" * 80)

    config_files = [
        ("requirements.txt", "Python requirements"),
        (".env.example", "Environment variables example"),
        ("docker-compose.yml", "Docker Compose configuration"),
        ("docker/init-db.sql", "Database initialization script"),
        (".gitignore", "Git ignore file"),
    ]

    for filepath, description in config_files:
        total_checks += 1
        if check_file_exists(filepath, description):
            checks_passed += 1

    print()

    # Check API extraction files
    print("[3] Checking API Extraction Files...")
    print("-" * 80)

    api_files = [
        ("src/api_extraction/__init__.py", "API package init"),
        ("src/api_extraction/football_api_client.py", "Football API client"),
        ("src/api_extraction/database_loader.py", "Database loader"),
        ("src/api_extraction/extract_football_data.py", "Main extraction script"),
    ]

    for filepath, description in api_files:
        total_checks += 1
        if check_file_exists(filepath, description):
            checks_passed += 1

    print()

    # Check dbt files
    print("[4] Checking dbt Files...")
    print("-" * 80)

    dbt_files = [
        ("dbt_football/dbt_project.yml", "dbt project configuration"),
        ("dbt_football/profiles.yml", "dbt profiles"),
        ("dbt_football/models/staging/schema.yml", "Staging schema"),
        ("dbt_football/models/staging/stg_competitions.sql", "Staging competitions"),
        ("dbt_football/models/staging/stg_teams.sql", "Staging teams"),
        ("dbt_football/models/staging/stg_matches.sql", "Staging matches"),
        ("dbt_football/models/staging/stg_standings.sql", "Staging standings"),
        ("dbt_football/models/analytics/team_performance.sql", "Team performance analytics"),
        ("dbt_football/models/analytics/match_results.sql", "Match results analytics"),
        ("dbt_football/models/analytics/competition_summary.sql", "Competition summary"),
        ("dbt_football/models/analytics/team_head_to_head.sql", "Head-to-head analytics"),
    ]

    for filepath, description in dbt_files:
        total_checks += 1
        if check_file_exists(filepath, description):
            checks_passed += 1

    print()

    # Check Airflow files
    print("[5] Checking Airflow Files...")
    print("-" * 80)

    airflow_files = [
        ("src/airflow/dags/__init__.py", "Airflow DAGs package init"),
        ("src/airflow/dags/football_etl_dag.py", "Football ETL DAG"),
    ]

    for filepath, description in airflow_files:
        total_checks += 1
        if check_file_exists(filepath, description):
            checks_passed += 1

    print()

    # Check CrewAI files
    print("[6] Checking CrewAI Files...")
    print("-" * 80)

    crewai_files = [
        ("src/crewai_agents/__init__.py", "CrewAI package init"),
        ("src/crewai_agents/agents.py", "Agent definitions"),
        ("src/crewai_agents/tasks.py", "Task definitions"),
        ("src/crewai_agents/crew.py", "Crew configuration"),
    ]

    for filepath, description in crewai_files:
        total_checks += 1
        if check_file_exists(filepath, description):
            checks_passed += 1

    print()

    # Check documentation files
    print("[7] Checking Documentation Files...")
    print("-" * 80)

    doc_files = [
        ("README.md", "Project README"),
        ("PROMPT.md", "Project prompt"),
        ("SETUP.md", "Setup instructions"),
        ("ARCHITECTURE.md", "Architecture documentation"),
    ]

    for filepath, description in doc_files:
        total_checks += 1
        if check_file_exists(filepath, description):
            checks_passed += 1

    print()

    # Check environment variables
    print("[8] Checking Environment Configuration...")
    print("-" * 80)

    if Path(".env").exists():
        print("✓ .env file exists")
        checks_passed += 1
        print("  Note: Make sure to configure your API keys in .env")
    else:
        print("✗ .env file not found")
        print("  Action required: Copy .env.example to .env and configure your API keys")

    total_checks += 1

    print()

    # Summary
    print("=" * 80)
    print(f"Verification Summary: {checks_passed}/{total_checks} checks passed")
    print("=" * 80)

    if checks_passed == total_checks:
        print("✓ All checks passed! Your setup is complete.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your API keys")
        print("2. Run: docker-compose up -d")
        print("3. Wait for services to be healthy")
        print("4. Access Airflow at http://localhost:8080")
        print("5. Access Metabase at http://localhost:3000")
        print("\nFor detailed instructions, see SETUP.md")
        return 0
    else:
        print(f"✗ {total_checks - checks_passed} checks failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
