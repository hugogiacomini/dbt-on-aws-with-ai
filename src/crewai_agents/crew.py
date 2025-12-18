"""CrewAI crew setup for football analytics team."""

from crewai import Crew, Process
from agents import (
    create_bi_analyst,
    create_data_analyst,
    create_data_engineer,
    create_lead_data_engineer
)
from tasks import (
    create_bi_requirements_task,
    create_technical_specs_task,
    create_pipeline_review_task,
    create_dbt_review_task,
    create_visualization_plan_task,
    create_implementation_summary_task
)


def create_football_analytics_crew() -> Crew:
    """Create and configure the football analytics crew.

    Returns:
        Configured Crew instance
    """
    # Create agents
    bi_analyst = create_bi_analyst()
    data_analyst = create_data_analyst()
    data_engineer = create_data_engineer()
    lead_engineer = create_lead_data_engineer()

    # Create tasks
    task_bi_requirements = create_bi_requirements_task(bi_analyst)
    task_technical_specs = create_technical_specs_task(
        lead_engineer,
        context=[task_bi_requirements]
    )
    task_pipeline_review = create_pipeline_review_task(
        data_engineer,
        context=[task_technical_specs]
    )
    task_dbt_review = create_dbt_review_task(
        data_analyst,
        context=[task_technical_specs]
    )
    task_visualization_plan = create_visualization_plan_task(
        bi_analyst,
        context=[task_dbt_review]
    )
    task_implementation_summary = create_implementation_summary_task(
        lead_engineer,
        context=[
            task_pipeline_review,
            task_dbt_review,
            task_visualization_plan
        ]
    )

    # Create crew
    crew = Crew(
        agents=[bi_analyst, data_analyst, data_engineer, lead_engineer],
        tasks=[
            task_bi_requirements,
            task_technical_specs,
            task_pipeline_review,
            task_dbt_review,
            task_visualization_plan,
            task_implementation_summary
        ],
        process=Process.sequential,
        verbose=True
    )

    return crew


def run_crew():
    """Execute the football analytics crew."""
    crew = create_football_analytics_crew()
    result = crew.kickoff()
    return result


if __name__ == "__main__":
    print("Starting Football Analytics AI Team...")
    print("=" * 80)
    result = run_crew()
    print("=" * 80)
    print("Crew execution completed!")
    print("\nFinal Output:")
    print(result)
