"""CrewAI task definitions for football analytics workflow."""

from crewai import Task
from typing import List


def create_bi_requirements_task(agent) -> Task:
    """Create task for BI Analyst to define requirements.

    Args:
        agent: BI Analyst agent

    Returns:
        Task for defining business requirements
    """
    return Task(
        description="""Analyze the football analytics use case and define key business
        requirements. Identify the most important questions stakeholders would want
        answered, such as:

        - Which teams are performing best overall?
        - What are the trends in home vs away performance?
        - Which competitions are most competitive?
        - What patterns exist in scoring and goals?
        - How do teams compare head-to-head?

        Create a list of 5-7 key business questions that should be answered through
        dashboards and visualizations. For each question, specify what metrics and
        dimensions would be needed.

        Output a structured document with business requirements.""",
        agent=agent,
        expected_output="""A document containing:
        1. List of 5-7 key business questions
        2. For each question: required metrics, dimensions, and suggested visualizations
        3. Priority ranking of questions
        4. Any additional context or assumptions"""
    )


def create_technical_specs_task(agent, context: List[Task]) -> Task:
    """Create task for Lead Engineer to create technical specifications.

    Args:
        agent: Lead Data Engineer agent
        context: Previous tasks to use as context

    Returns:
        Task for creating technical specifications
    """
    return Task(
        description="""Review the business requirements from the BI Analyst and translate
        them into detailed technical specifications.

        For each business question, specify:
        - What API endpoints need to be called
        - What raw data tables are needed
        - What dbt transformations should be created
        - What final analytics tables/views should be built
        - What data quality checks should be implemented

        Create a comprehensive technical architecture document that the Data Engineer
        and Data Analyst can follow.""",
        agent=agent,
        context=context,
        expected_output="""A technical specification document containing:
        1. API extraction requirements (endpoints, frequency, data points)
        2. Database schema design (raw, staging, analytics layers)
        3. dbt model specifications (what transformations are needed)
        4. Data quality requirements
        5. Airflow DAG requirements and schedule"""
    )


def create_pipeline_review_task(agent, context: List[Task]) -> Task:
    """Create task for Data Engineer to review pipeline implementation.

    Args:
        agent: Data Engineer agent
        context: Previous tasks to use as context

    Returns:
        Task for reviewing pipeline implementation
    """
    return Task(
        description="""Review the existing ETL pipeline implementation against the
        technical specifications. Evaluate:

        1. API extraction code (football_api_client.py, extract_football_data.py)
           - Is error handling robust?
           - Are rate limits handled properly?
           - Is the data coverage sufficient?

        2. Database loader (database_loader.py)
           - Are tables properly structured?
           - Is upsert logic correct?
           - Are indexes needed for performance?

        3. Airflow DAG (football_etl_dag.py)
           - Is the schedule appropriate?
           - Are task dependencies correct?
           - Is retry logic adequate?

        Provide specific recommendations for improvements or confirm the implementation
        is production-ready.""",
        agent=agent,
        context=context,
        expected_output="""A code review document containing:
        1. Assessment of each component (API client, database loader, Airflow DAG)
        2. List of issues found (if any) with severity levels
        3. Specific recommendations for improvements
        4. Confirmation of what is working well
        5. Overall readiness assessment"""
    )


def create_dbt_review_task(agent, context: List[Task]) -> Task:
    """Create task for Data Analyst to review dbt models.

    Args:
        agent: Data Analyst agent
        context: Previous tasks to use as context

    Returns:
        Task for reviewing dbt implementation
    """
    return Task(
        description="""Review the existing dbt models against the technical specifications
        and business requirements. Evaluate:

        1. Staging models (stg_competitions, stg_teams, stg_matches, stg_standings)
           - Are all necessary fields extracted?
           - Are data types appropriate?
           - Is the naming convention consistent?

        2. Analytics models (team_performance, match_results, competition_summary, team_head_to_head)
           - Do they answer the business questions?
           - Are calculations correct?
           - Are there missing metrics that should be added?

        3. Data quality
           - Are tests defined?
           - Are there data quality issues to address?

        Provide specific recommendations for additional models, metrics, or improvements.""",
        agent=agent,
        context=context,
        expected_output="""A dbt review document containing:
        1. Assessment of staging layer completeness
        2. Assessment of analytics models against business requirements
        3. List of missing models or metrics
        4. Recommendations for additional transformations
        5. Data quality assessment and test recommendations"""
    )


def create_visualization_plan_task(agent, context: List[Task]) -> Task:
    """Create task for BI Analyst to plan Metabase visualizations.

    Args:
        agent: BI Analyst agent
        context: Previous tasks to use as context

    Returns:
        Task for planning visualizations
    """
    return Task(
        description="""Based on the available analytics models and business requirements,
        create a detailed plan for Metabase dashboards and visualizations.

        For each business question, specify:
        - Dashboard name and purpose
        - Individual charts/visualizations needed
        - What analytics table(s) to query
        - What filters should be available
        - Chart type (bar, line, pie, table, etc.)
        - Key metrics to highlight

        Design 2-3 comprehensive dashboards that would provide maximum value to
        stakeholders.""",
        agent=agent,
        context=context,
        expected_output="""A visualization plan document containing:
        1. Dashboard 1: Overview dashboard with key metrics
           - List of charts and their specifications
        2. Dashboard 2: Team performance dashboard
           - List of charts and their specifications
        3. Dashboard 3: Competition analysis dashboard
           - List of charts and their specifications
        4. For each chart: data source, filters, chart type, and purpose
        5. Sample SQL queries for key visualizations"""
    )


def create_implementation_summary_task(agent, context: List[Task]) -> Task:
    """Create task for Lead Engineer to summarize implementation.

    Args:
        agent: Lead Data Engineer agent
        context: Previous tasks to use as context

    Returns:
        Task for creating implementation summary
    """
    return Task(
        description="""Synthesize all the reviews and recommendations from the team
        into a comprehensive implementation summary and next steps document.

        Include:
        - What has been implemented successfully
        - What improvements should be prioritized
        - What additional features could be added
        - Clear action items for each team member
        - Timeline considerations

        This should serve as a roadmap for taking the project from its current state
        to production-ready.""",
        agent=agent,
        context=context,
        expected_output="""An implementation summary containing:
        1. Executive summary of current state
        2. Completed components and their status
        3. Prioritized list of improvements needed
        4. Action items by team member (BI Analyst, Data Analyst, Data Engineer)
        5. Future enhancements to consider
        6. Deployment and monitoring recommendations"""
    )
