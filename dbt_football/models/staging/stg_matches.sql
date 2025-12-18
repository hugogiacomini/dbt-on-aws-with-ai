-- Staging model for matches
-- Clean and standardize raw match data

{{ config(materialized='view') }}

select
    id as match_id,
    competition_id,
    season_id,
    utc_date as match_date,
    status as match_status,
    matchday,
    stage as match_stage,
    "group" as match_group,
    home_team_id,
    home_team_name,
    away_team_id,
    away_team_name,
    winner,
    duration,
    full_time_home as home_score,
    full_time_away as away_score,
    half_time_home as home_halftime_score,
    half_time_away as away_halftime_score,
    case
        when winner = 'HOME_TEAM' then home_team_id
        when winner = 'AWAY_TEAM' then away_team_id
        else null
    end as winning_team_id,
    case
        when winner = 'DRAW' then true
        else false
    end as is_draw,
    extracted_at
from {{ source('raw', 'matches') }}
