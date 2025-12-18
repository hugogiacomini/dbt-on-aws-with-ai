# Metabase Setup and Dashboard Guide

## Initial Setup

1. **Open Metabase**: <http://localhost:3000>

2. **Complete Setup Wizard**:
   - **Language**: Select English (or your preference)
   - **Create Account**:
     - First name: Your name
     - Last name: Your last name
     - Email: <your-email@example.com>
     - Password: Choose a secure password
   - **Add your data**:
     - Database type: **PostgreSQL**
     - Name: **Football Analytics**
     - Host: **postgres** (or **localhost** if connecting from outside Docker)
     - Port: **5432**
     - Database name: **football_analytics**
     - Username: **airflow**
     - Password: **airflow**
   - Click **Connect database**
   - Skip usage data collection (or allow if you prefer)

## Ready-to-Use SQL Queries for Dashboards

### Dashboard 1: Competition Overview

#### Chart 1: Competition Statistics Table

```sql
SELECT
  competition_name,
  total_teams,
  total_matches,
  total_goals,
  avg_goals_per_match,
  home_win_percentage,
  away_win_percentage,
  draw_percentage
FROM analytics.competition_summary
ORDER BY total_matches DESC;
```

**Visualization**: Table

#### Chart 2: Goals Per Match by Competition (Bar Chart)

```sql
SELECT
  competition_name,
  avg_goals_per_match
FROM analytics.competition_summary
WHERE total_matches > 0
ORDER BY avg_goals_per_match DESC;
```

**Visualization**: Bar chart (X-axis: competition_name, Y-axis: avg_goals_per_match)

#### Chart 3: Home vs Away Win Rates (Grouped Bar)

```sql
SELECT
  competition_name,
  home_win_percentage,
  away_win_percentage
FROM analytics.competition_summary
WHERE total_matches > 0
ORDER BY competition_name;
```

**Visualization**: Grouped bar chart

### Dashboard 2: Team Performance

#### Chart 1: Top Teams by Points (Premier League)

```sql
SELECT
  team_name,
  total_games,
  points,
  total_wins,
  total_draws,
  total_losses,
  goal_difference,
  avg_goals_for,
  avg_goals_against
FROM analytics.team_performance
WHERE competition_id = 2021  -- Premier League
ORDER BY points DESC, goal_difference DESC
LIMIT 20;
```

**Visualization**: Table
**Add Filter**: competition_id (to switch between competitions)

#### Chart 2: Goals Scored vs Goals Conceded (Scatter Plot)

```sql
SELECT
  team_name,
  total_goals_for as "Goals Scored",
  total_goals_against as "Goals Conceded",
  points
FROM analytics.team_performance
WHERE competition_id = 2021
  AND total_games > 0;
```

**Visualization**: Scatter plot (X: Goals Scored, Y: Goals Conceded, Size: points)

#### Chart 3: Home vs Away Performance (Comparison)

```sql
SELECT
  team_name,
  home_win_percentage,
  away_win_percentage
FROM analytics.team_performance
WHERE competition_id = 2021
  AND total_games > 0
ORDER BY (home_win_percentage - away_win_percentage) DESC
LIMIT 10;
```

**Visualization**: Grouped bar chart

### Dashboard 3: Match Analysis

#### Chart 1: Recent Matches

```sql
SELECT
  match_date::date,
  competition_name,
  home_team_name,
  home_score,
  away_score,
  away_team_name,
  total_goals,
  result_type
FROM analytics.match_results
ORDER BY match_date DESC
LIMIT 50;
```

**Visualization**: Table

#### Chart 2: Goals Over Time (Line Chart)

```sql
SELECT
  match_month::date as month,
  SUM(total_goals) as total_goals,
  AVG(total_goals) as avg_goals_per_match
FROM analytics.match_results
GROUP BY match_month
ORDER BY match_month;
```

**Visualization**: Line chart (X: month, Y: total_goals and avg_goals_per_match)

#### Chart 3: Match Outcomes Distribution (Pie Chart)

```sql
SELECT
  result_type,
  COUNT(*) as count
FROM analytics.match_results
GROUP BY result_type;
```

**Visualization**: Pie chart

#### Chart 4: High-Scoring Matches

```sql
SELECT
  match_date::date,
  competition_name,
  home_team_name,
  home_score,
  away_score,
  away_team_name,
  total_goals
FROM analytics.match_results
WHERE total_goals >= 4
ORDER BY total_goals DESC, match_date DESC;
```

**Visualization**: Table

### Dashboard 4: Head-to-Head Analysis

#### Chart 1: Most Competitive Rivalries

```sql
SELECT
  team1_name,
  team2_name,
  total_matches,
  team1_wins,
  team2_wins,
  draws,
  team1_avg_goals,
  team2_avg_goals
FROM analytics.team_head_to_head
WHERE total_matches >= 2
ORDER BY total_matches DESC
LIMIT 20;
```

**Visualization**: Table

### Key Metrics (Big Numbers)

Create these as "Number" visualizations for dashboard headers:

#### Total Matches

```sql
SELECT SUM(total_matches) as "Total Matches"
FROM analytics.competition_summary;
```

#### Total Goals

```sql
SELECT SUM(total_goals) as "Total Goals"
FROM analytics.competition_summary;
```

#### Average Goals Per Match

```sql
SELECT ROUND(AVG(avg_goals_per_match), 2) as "Avg Goals/Match"
FROM analytics.competition_summary
WHERE total_matches > 0;
```

#### Total Teams

```sql
SELECT COUNT(DISTINCT team_id) as "Total Teams"
FROM analytics.team_performance;
```

## Creating Your First Dashboard

1. **Create New Dashboard**:
   - Click "+" in top right
   - Select "Dashboard"
   - Name it "Football Overview"

2. **Add Questions**:
   - Click "Add a question"
   - Select "Native query" (SQL)
   - Paste one of the queries above
   - Click "Visualize"
   - Choose visualization type
   - Save the question

3. **Arrange Dashboard**:
   - Drag and resize charts
   - Add text cards for context
   - Add filters for interactivity

4. **Add Filters**:
   - Click "Add a filter"
   - Choose field (e.g., competition_id)
   - Wire filter to questions

## Dashboard Themes

### Theme 1: Executive Summary

- Big number metrics at top
- Competition comparison table
- Goals over time trend
- Top performers

### Theme 2: Team Deep Dive

- Team selector filter
- Team performance metrics
- Recent matches
- Head-to-head records
- Goals analysis

### Theme 3: Match Analysis

- Recent results
- Upcoming fixtures
- Scoring patterns
- Home advantage analysis

## Tips for Great Dashboards

1. **Use Filters**: Add competition, team, and date filters
2. **Mix Visualizations**: Combine tables, charts, and big numbers
3. **Color Coding**: Use conditional formatting for wins/losses
4. **Tooltips**: Add descriptions to explain metrics
5. **Auto-Refresh**: Set dashboards to refresh every 6 hours

## Advanced Queries

### Win Streak Analysis

```sql
SELECT
  team_name,
  total_wins,
  total_games,
  win_percentage,
  points
FROM analytics.team_performance
WHERE total_games >= 5
ORDER BY win_percentage DESC
LIMIT 10;
```

### Both Teams Scored Frequency

```sql
SELECT
  competition_name,
  COUNT(CASE WHEN both_teams_scored THEN 1 END) as btts_count,
  COUNT(*) as total_matches,
  ROUND(
    COUNT(CASE WHEN both_teams_scored THEN 1 END)::numeric /
    COUNT(*) * 100,
    2
  ) as btts_percentage
FROM analytics.match_results
GROUP BY competition_name
ORDER BY btts_percentage DESC;
```

### Over 2.5 Goals Analysis

```sql
SELECT
  competition_name,
  COUNT(CASE WHEN over_2_5_goals THEN 1 END) as over_count,
  COUNT(*) as total_matches,
  ROUND(
    COUNT(CASE WHEN over_2_5_goals THEN 1 END)::numeric /
    COUNT(*) * 100,
    2
  ) as over_percentage
FROM analytics.match_results
GROUP BY competition_name
ORDER BY over_percentage DESC;
```

## Sharing Dashboards

1. **Public Link**: Share with anyone
2. **Email Subscriptions**: Send daily/weekly reports
3. **Embed**: Embed in websites or apps
4. **PDF Export**: Download as PDF
5. **Slack Integration**: Send to Slack channels

## Next Steps

1. Create the 3-4 main dashboards
2. Set up auto-refresh
3. Add more competitions from the API
4. Create custom metrics
5. Set up alerts for unusual patterns
6. Share with stakeholders

Enjoy exploring your football data! ⚽📊
