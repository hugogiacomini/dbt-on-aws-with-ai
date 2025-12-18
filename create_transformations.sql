-- Create all staging views and analytics tables

-- Staging: stg_competitions
CREATE OR REPLACE VIEW staging.stg_competitions AS
SELECT
    id as competition_id,
    name as competition_name,
    code as competition_code,
    type as competition_type,
    emblem as competition_emblem,
    area_name,
    area_code,
    (current_season->>'id')::integer as current_season_id,
    (current_season->>'startDate')::date as season_start_date,
    (current_season->>'endDate')::date as season_end_date,
    extracted_at
FROM raw.competitions;

-- Staging: stg_teams
CREATE OR REPLACE VIEW staging.stg_teams AS
SELECT
    id as team_id,
    name as team_name,
    short_name as team_short_name,
    tla as team_tla,
    crest as team_crest,
    address as team_address,
    website as team_website,
    founded as founded_year,
    club_colors,
    venue as team_venue,
    extracted_at
FROM raw.teams;

-- Staging: stg_matches
CREATE OR REPLACE VIEW staging.stg_matches AS
SELECT
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
    CASE
        WHEN winner = 'HOME_TEAM' THEN home_team_id
        WHEN winner = 'AWAY_TEAM' THEN away_team_id
        ELSE NULL
    END as winning_team_id,
    CASE
        WHEN winner = 'DRAW' THEN true
        ELSE false
    END as is_draw,
    extracted_at
FROM raw.matches;

-- Staging: stg_standings
CREATE OR REPLACE VIEW staging.stg_standings AS
SELECT
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
    ROUND(points::numeric / NULLIF(played_games, 0), 2) as points_per_game,
    ROUND((won::numeric / NULLIF(played_games, 0)) * 100, 2) as win_percentage,
    extracted_at
FROM raw.standings;

-- Analytics: team_performance
DROP TABLE IF EXISTS analytics.team_performance CASCADE;
CREATE TABLE analytics.team_performance AS
WITH home_matches AS (
    SELECT
        home_team_id as team_id,
        home_team_name as team_name,
        competition_id,
        COUNT(*) as home_games_played,
        SUM(CASE WHEN winner = 'HOME_TEAM' THEN 1 ELSE 0 END) as home_wins,
        SUM(CASE WHEN is_draw THEN 1 ELSE 0 END) as home_draws,
        SUM(CASE WHEN winner = 'AWAY_TEAM' THEN 1 ELSE 0 END) as home_losses,
        SUM(home_score) as home_goals_for,
        SUM(away_score) as home_goals_against
    FROM staging.stg_matches
    WHERE match_status = 'FINISHED'
    GROUP BY home_team_id, home_team_name, competition_id
),
away_matches AS (
    SELECT
        away_team_id as team_id,
        away_team_name as team_name,
        competition_id,
        COUNT(*) as away_games_played,
        SUM(CASE WHEN winner = 'AWAY_TEAM' THEN 1 ELSE 0 END) as away_wins,
        SUM(CASE WHEN is_draw THEN 1 ELSE 0 END) as away_draws,
        SUM(CASE WHEN winner = 'HOME_TEAM' THEN 1 ELSE 0 END) as away_losses,
        SUM(away_score) as away_goals_for,
        SUM(home_score) as away_goals_against
    FROM staging.stg_matches
    WHERE match_status = 'FINISHED'
    GROUP BY away_team_id, away_team_name, competition_id
),
combined AS (
    SELECT
        COALESCE(h.team_id, a.team_id) as team_id,
        COALESCE(h.team_name, a.team_name) as team_name,
        COALESCE(h.competition_id, a.competition_id) as competition_id,
        COALESCE(h.home_games_played, 0) + COALESCE(a.away_games_played, 0) as total_games,
        COALESCE(h.home_games_played, 0) as home_games,
        COALESCE(a.away_games_played, 0) as away_games,
        COALESCE(h.home_wins, 0) + COALESCE(a.away_wins, 0) as total_wins,
        COALESCE(h.home_draws, 0) + COALESCE(a.away_draws, 0) as total_draws,
        COALESCE(h.home_losses, 0) + COALESCE(a.away_losses, 0) as total_losses,
        COALESCE(h.home_goals_for, 0) + COALESCE(a.away_goals_for, 0) as total_goals_for,
        COALESCE(h.home_goals_against, 0) + COALESCE(a.away_goals_against, 0) as total_goals_against,
        COALESCE(h.home_wins, 0) as home_wins,
        COALESCE(h.home_draws, 0) as home_draws,
        COALESCE(h.home_losses, 0) as home_losses,
        COALESCE(a.away_wins, 0) as away_wins,
        COALESCE(a.away_draws, 0) as away_draws,
        COALESCE(a.away_losses, 0) as away_losses
    FROM home_matches h
    FULL OUTER JOIN away_matches a ON h.team_id = a.team_id AND h.competition_id = a.competition_id
)
SELECT
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
    ROUND((total_wins::numeric / NULLIF(total_games, 0)) * 100, 2) as win_percentage,
    ROUND((total_draws::numeric / NULLIF(total_games, 0)) * 100, 2) as draw_percentage,
    ROUND((total_losses::numeric / NULLIF(total_games, 0)) * 100, 2) as loss_percentage,
    ROUND(total_goals_for::numeric / NULLIF(total_games, 0), 2) as avg_goals_for,
    ROUND(total_goals_against::numeric / NULLIF(total_games, 0), 2) as avg_goals_against,
    ROUND((home_wins::numeric / NULLIF(home_games, 0)) * 100, 2) as home_win_percentage,
    ROUND((away_wins::numeric / NULLIF(away_games, 0)) * 100, 2) as away_win_percentage,
    (total_wins * 3) + total_draws as points,
    CURRENT_TIMESTAMP as calculated_at
FROM combined;

-- Analytics: match_results
DROP TABLE IF EXISTS analytics.match_results CASCADE;
CREATE TABLE analytics.match_results AS
SELECT
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
    ABS(m.home_score - m.away_score) as goal_margin,
    CASE
        WHEN m.home_score > m.away_score THEN 'HOME_WIN'
        WHEN m.away_score > m.home_score THEN 'AWAY_WIN'
        ELSE 'DRAW'
    END as result_type,
    CASE
        WHEN m.home_score + m.away_score > 2.5 THEN true
        ELSE false
    END as over_2_5_goals,
    CASE
        WHEN m.home_score > 0 AND m.away_score > 0 THEN true
        ELSE false
    END as both_teams_scored,
    DATE_TRUNC('month', m.match_date) as match_month,
    EXTRACT(year FROM m.match_date) as match_year,
    CURRENT_TIMESTAMP as calculated_at
FROM staging.stg_matches m
LEFT JOIN staging.stg_competitions c ON m.competition_id = c.competition_id
LEFT JOIN staging.stg_teams ht ON m.home_team_id = ht.team_id
LEFT JOIN staging.stg_teams at ON m.away_team_id = at.team_id
WHERE m.match_status = 'FINISHED';

-- Analytics: competition_summary
DROP TABLE IF EXISTS analytics.competition_summary CASCADE;
CREATE TABLE analytics.competition_summary AS
WITH match_stats AS (
    SELECT
        competition_id,
        COUNT(*) as total_matches,
        SUM(home_score + away_score) as total_goals,
        AVG(home_score + away_score) as avg_goals_per_match,
        SUM(CASE WHEN is_draw THEN 1 ELSE 0 END) as total_draws,
        SUM(CASE WHEN home_score > away_score THEN 1 ELSE 0 END) as home_wins,
        SUM(CASE WHEN away_score > home_score THEN 1 ELSE 0 END) as away_wins,
        MAX(home_score + away_score) as highest_scoring_match
    FROM staging.stg_matches
    WHERE match_status = 'FINISHED'
    GROUP BY competition_id
),
team_count AS (
    SELECT
        competition_id,
        COUNT(DISTINCT team_id) as total_teams
    FROM staging.stg_standings
    GROUP BY competition_id
)
SELECT
    c.competition_id,
    c.competition_name,
    c.competition_code,
    c.competition_type,
    c.area_name,
    c.area_code,
    COALESCE(tc.total_teams, 0) as total_teams,
    COALESCE(ms.total_matches, 0) as total_matches,
    COALESCE(ms.total_goals, 0) as total_goals,
    ROUND(COALESCE(ms.avg_goals_per_match, 0), 2) as avg_goals_per_match,
    COALESCE(ms.total_draws, 0) as total_draws,
    COALESCE(ms.home_wins, 0) as home_wins,
    COALESCE(ms.away_wins, 0) as away_wins,
    ROUND((ms.home_wins::numeric / NULLIF(ms.total_matches, 0)) * 100, 2) as home_win_percentage,
    ROUND((ms.away_wins::numeric / NULLIF(ms.total_matches, 0)) * 100, 2) as away_win_percentage,
    ROUND((ms.total_draws::numeric / NULLIF(ms.total_matches, 0)) * 100, 2) as draw_percentage,
    COALESCE(ms.highest_scoring_match, 0) as highest_scoring_match,
    CURRENT_TIMESTAMP as calculated_at
FROM staging.stg_competitions c
LEFT JOIN match_stats ms ON c.competition_id = ms.competition_id
LEFT JOIN team_count tc ON c.competition_id = tc.competition_id;

-- Analytics: team_head_to_head
DROP TABLE IF EXISTS analytics.team_head_to_head CASCADE;
CREATE TABLE analytics.team_head_to_head AS
WITH all_matches AS (
    SELECT
        CASE WHEN home_team_id < away_team_id THEN home_team_id ELSE away_team_id END as team1_id,
        CASE WHEN home_team_id < away_team_id THEN home_team_name ELSE away_team_name END as team1_name,
        CASE WHEN home_team_id < away_team_id THEN away_team_id ELSE home_team_id END as team2_id,
        CASE WHEN home_team_id < away_team_id THEN away_team_name ELSE home_team_name END as team2_name,
        competition_id,
        CASE
            WHEN home_team_id < away_team_id AND winner = 'HOME_TEAM' THEN 'TEAM1_WIN'
            WHEN home_team_id < away_team_id AND winner = 'AWAY_TEAM' THEN 'TEAM2_WIN'
            WHEN home_team_id > away_team_id AND winner = 'HOME_TEAM' THEN 'TEAM2_WIN'
            WHEN home_team_id > away_team_id AND winner = 'AWAY_TEAM' THEN 'TEAM1_WIN'
            ELSE 'DRAW'
        END as match_result,
        CASE WHEN home_team_id < away_team_id THEN home_score ELSE away_score END as team1_goals,
        CASE WHEN home_team_id < away_team_id THEN away_score ELSE home_score END as team2_goals
    FROM staging.stg_matches
    WHERE match_status = 'FINISHED'
)
SELECT
    team1_id,
    team1_name,
    team2_id,
    team2_name,
    competition_id,
    COUNT(*) as total_matches,
    SUM(CASE WHEN match_result = 'TEAM1_WIN' THEN 1 ELSE 0 END) as team1_wins,
    SUM(CASE WHEN match_result = 'TEAM2_WIN' THEN 1 ELSE 0 END) as team2_wins,
    SUM(CASE WHEN match_result = 'DRAW' THEN 1 ELSE 0 END) as draws,
    SUM(team1_goals) as team1_total_goals,
    SUM(team2_goals) as team2_total_goals,
    ROUND(AVG(team1_goals), 2) as team1_avg_goals,
    ROUND(AVG(team2_goals), 2) as team2_avg_goals,
    ROUND((SUM(CASE WHEN match_result = 'TEAM1_WIN' THEN 1 ELSE 0 END)::numeric / COUNT(*)) * 100, 2) as team1_win_percentage,
    ROUND((SUM(CASE WHEN match_result = 'TEAM2_WIN' THEN 1 ELSE 0 END)::numeric / COUNT(*)) * 100, 2) as team2_win_percentage,
    CURRENT_TIMESTAMP as calculated_at
FROM all_matches
GROUP BY team1_id, team1_name, team2_id, team2_name, competition_id
HAVING COUNT(*) >= 1;
