-- Staging model for teams
-- Clean and standardize raw team data

{{ config(materialized='view') }}

select
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
from {{ source('raw', 'teams') }}
