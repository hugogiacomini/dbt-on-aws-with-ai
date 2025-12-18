-- Analytics model: Match results with enriched data
-- Provides comprehensive match information with team and competition details

{{ config(materialized='table') }}

select
    m.match_id,
    m.match_date,
    m.match_status,
    m.matchday,
    m.match_stage,
    m.competition_id,
    c.competition_name,
    c.competition_code,
    m.home_team_id,
    m.home_team_name,
    ht.team_venue as home_team_venue,
    m.away_team_id,
    m.away_team_name,
    at.team_venue as away_team_venue,
    m.home_score,
    m.away_score,
    m.home_halftime_score,
    m.away_halftime_score,
    m.winner,
    m.is_draw,
    m.home_score + m.away_score as total_goals,
    abs(m.home_score - m.away_score) as goal_margin,
    case
        when m.home_score > m.away_score then 'HOME_WIN'
        when m.away_score > m.home_score then 'AWAY_WIN'
        else 'DRAW'
    end as result_type,
    case
        when m.home_score + m.away_score > 2.5 then true
        else false
    end as over_2_5_goals,
    case
        when m.home_score > 0 and m.away_score > 0 then true
        else false
    end as both_teams_scored,
    date_trunc('month', m.match_date) as match_month,
    extract(year from m.match_date) as match_year,
    current_timestamp as calculated_at
from {{ ref('stg_matches') }} m
left join {{ ref('stg_competitions') }} c on m.competition_id = c.competition_id
left join {{ ref('stg_teams') }} ht on m.home_team_id = ht.team_id
left join {{ ref('stg_teams') }} at on m.away_team_id = at.team_id
where m.match_status = 'FINISHED'
