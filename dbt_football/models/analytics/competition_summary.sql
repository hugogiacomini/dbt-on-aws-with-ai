-- Analytics model: Competition summary statistics
-- Aggregates key metrics for each competition

{{ config(materialized='table') }}

with match_stats as (
    select
        competition_id,
        count(*) as total_matches,
        sum(home_score + away_score) as total_goals,
        avg(home_score + away_score) as avg_goals_per_match,
        sum(case when is_draw then 1 else 0 end) as total_draws,
        sum(case when home_score > away_score then 1 else 0 end) as home_wins,
        sum(case when away_score > home_score then 1 else 0 end) as away_wins,
        max(home_score + away_score) as highest_scoring_match,
        count(distinct home_team_id) + count(distinct away_team_id) as unique_teams
    from {{ ref('stg_matches') }}
    where match_status = 'FINISHED'
    group by competition_id
),

team_count as (
    select
        competition_id,
        count(distinct team_id) as total_teams
    from {{ ref('stg_standings') }}
    group by competition_id
)

select
    c.competition_id,
    c.competition_name,
    c.competition_code,
    c.competition_type,
    c.area_name,
    c.area_code,
    coalesce(tc.total_teams, 0) as total_teams,
    coalesce(ms.total_matches, 0) as total_matches,
    coalesce(ms.total_goals, 0) as total_goals,
    round(coalesce(ms.avg_goals_per_match, 0), 2) as avg_goals_per_match,
    coalesce(ms.total_draws, 0) as total_draws,
    coalesce(ms.home_wins, 0) as home_wins,
    coalesce(ms.away_wins, 0) as away_wins,
    round((ms.home_wins::numeric / nullif(ms.total_matches, 0)) * 100, 2) as home_win_percentage,
    round((ms.away_wins::numeric / nullif(ms.total_matches, 0)) * 100, 2) as away_win_percentage,
    round((ms.total_draws::numeric / nullif(ms.total_matches, 0)) * 100, 2) as draw_percentage,
    coalesce(ms.highest_scoring_match, 0) as highest_scoring_match,
    current_timestamp as calculated_at
from {{ ref('stg_competitions') }} c
left join match_stats ms on c.competition_id = ms.competition_id
left join team_count tc on c.competition_id = tc.competition_id
