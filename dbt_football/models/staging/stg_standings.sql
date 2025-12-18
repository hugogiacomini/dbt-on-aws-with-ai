-- Staging model for standings
-- Clean and standardize raw standings data

{{ config(materialized='view') }}

select
    competition_id,
    season_id,
    stage,
    type as standing_type,
    "group" as standing_group,
    team_id,
    team_name,
    position,
    played_games,
    won as wins,
    draw as draws,
    lost as losses,
    points,
    goals_for,
    goals_against,
    goal_difference,
    round(points::numeric / nullif(played_games, 0), 2) as points_per_game,
    round((won::numeric / nullif(played_games, 0)) * 100, 2) as win_percentage,
    extracted_at
from {{ source('raw', 'standings') }}
