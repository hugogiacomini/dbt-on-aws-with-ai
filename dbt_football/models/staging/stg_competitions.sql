-- Staging model for competitions
-- Clean and standardize raw competition data

{{ config(materialized='view') }}

select
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
from {{ source('raw', 'competitions') }}
