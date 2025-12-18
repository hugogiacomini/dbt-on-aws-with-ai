-- Analytics model: Head-to-head statistics between teams
-- Calculates historical performance between pairs of teams

{{ config(materialized='table') }}

with all_matches as (
    select
        case when home_team_id < away_team_id then home_team_id else away_team_id end as team1_id,
        case when home_team_id < away_team_id then home_team_name else away_team_name end as team1_name,
        case when home_team_id < away_team_id then away_team_id else home_team_id end as team2_id,
        case when home_team_id < away_team_id then away_team_name else home_team_name end as team2_name,
        competition_id,
        case
            when home_team_id < away_team_id and winner = 'HOME_TEAM' then 'TEAM1_WIN'
            when home_team_id < away_team_id and winner = 'AWAY_TEAM' then 'TEAM2_WIN'
            when home_team_id > away_team_id and winner = 'HOME_TEAM' then 'TEAM2_WIN'
            when home_team_id > away_team_id and winner = 'AWAY_TEAM' then 'TEAM1_WIN'
            else 'DRAW'
        end as match_result,
        case when home_team_id < away_team_id then home_score else away_score end as team1_goals,
        case when home_team_id < away_team_id then away_score else home_score end as team2_goals
    from {{ ref('stg_matches') }}
    where match_status = 'FINISHED'
)

select
    team1_id,
    team1_name,
    team2_id,
    team2_name,
    competition_id,
    count(*) as total_matches,
    sum(case when match_result = 'TEAM1_WIN' then 1 else 0 end) as team1_wins,
    sum(case when match_result = 'TEAM2_WIN' then 1 else 0 end) as team2_wins,
    sum(case when match_result = 'DRAW' then 1 else 0 end) as draws,
    sum(team1_goals) as team1_total_goals,
    sum(team2_goals) as team2_total_goals,
    round(avg(team1_goals), 2) as team1_avg_goals,
    round(avg(team2_goals), 2) as team2_avg_goals,
    round((sum(case when match_result = 'TEAM1_WIN' then 1 else 0 end)::numeric / count(*)) * 100, 2) as team1_win_percentage,
    round((sum(case when match_result = 'TEAM2_WIN' then 1 else 0 end)::numeric / count(*)) * 100, 2) as team2_win_percentage,
    current_timestamp as calculated_at
from all_matches
group by team1_id, team1_name, team2_id, team2_name, competition_id
having count(*) >= 1
