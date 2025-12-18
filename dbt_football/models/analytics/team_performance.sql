-- Analytics model: Team performance metrics
-- Aggregates team statistics across all matches

{{ config(materialized='table') }}

with home_matches as (
    select
        home_team_id as team_id,
        home_team_name as team_name,
        competition_id,
        count(*) as home_games_played,
        sum(case when winner = 'HOME_TEAM' then 1 else 0 end) as home_wins,
        sum(case when is_draw then 1 else 0 end) as home_draws,
        sum(case when winner = 'AWAY_TEAM' then 1 else 0 end) as home_losses,
        sum(home_score) as home_goals_for,
        sum(away_score) as home_goals_against
    from {{ ref('stg_matches') }}
    where match_status = 'FINISHED'
    group by home_team_id, home_team_name, competition_id
),

away_matches as (
    select
        away_team_id as team_id,
        away_team_name as team_name,
        competition_id,
        count(*) as away_games_played,
        sum(case when winner = 'AWAY_TEAM' then 1 else 0 end) as away_wins,
        sum(case when is_draw then 1 else 0 end) as away_draws,
        sum(case when winner = 'HOME_TEAM' then 1 else 0 end) as away_losses,
        sum(away_score) as away_goals_for,
        sum(home_score) as away_goals_against
    from {{ ref('stg_matches') }}
    where match_status = 'FINISHED'
    group by away_team_id, away_team_name, competition_id
),

combined as (
    select
        coalesce(h.team_id, a.team_id) as team_id,
        coalesce(h.team_name, a.team_name) as team_name,
        coalesce(h.competition_id, a.competition_id) as competition_id,
        coalesce(h.home_games_played, 0) + coalesce(a.away_games_played, 0) as total_games,
        coalesce(h.home_games_played, 0) as home_games,
        coalesce(a.away_games_played, 0) as away_games,
        coalesce(h.home_wins, 0) + coalesce(a.away_wins, 0) as total_wins,
        coalesce(h.home_draws, 0) + coalesce(a.away_draws, 0) as total_draws,
        coalesce(h.home_losses, 0) + coalesce(a.away_losses, 0) as total_losses,
        coalesce(h.home_goals_for, 0) + coalesce(a.away_goals_for, 0) as total_goals_for,
        coalesce(h.home_goals_against, 0) + coalesce(a.away_goals_against, 0) as total_goals_against,
        coalesce(h.home_wins, 0) as home_wins,
        coalesce(h.home_draws, 0) as home_draws,
        coalesce(h.home_losses, 0) as home_losses,
        coalesce(a.away_wins, 0) as away_wins,
        coalesce(a.away_draws, 0) as away_draws,
        coalesce(a.away_losses, 0) as away_losses
    from home_matches h
    full outer join away_matches a on h.team_id = a.team_id and h.competition_id = a.competition_id
)

select
    team_id,
    team_name,
    competition_id,
    total_games,
    home_games,
    away_games,
    total_wins,
    total_draws,
    total_losses,
    total_goals_for,
    total_goals_against,
    total_goals_for - total_goals_against as goal_difference,
    round((total_wins::numeric / nullif(total_games, 0)) * 100, 2) as win_percentage,
    round((total_draws::numeric / nullif(total_games, 0)) * 100, 2) as draw_percentage,
    round((total_losses::numeric / nullif(total_games, 0)) * 100, 2) as loss_percentage,
    round(total_goals_for::numeric / nullif(total_games, 0), 2) as avg_goals_for,
    round(total_goals_against::numeric / nullif(total_games, 0), 2) as avg_goals_against,
    round((home_wins::numeric / nullif(home_games, 0)) * 100, 2) as home_win_percentage,
    round((away_wins::numeric / nullif(away_games, 0)) * 100, 2) as away_win_percentage,
    (total_wins * 3) + total_draws as points,
    current_timestamp as calculated_at
from combined
