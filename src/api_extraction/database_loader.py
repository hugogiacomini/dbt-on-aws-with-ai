"""Database loader for storing Football-Data.org API data."""

import os
import json
from typing import List, Dict, Any
from datetime import datetime
import logging
from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, JSON, MetaData, Boolean, Float
from sqlalchemy.dialects.postgresql import insert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseLoader:
    """Loader for storing API data in PostgreSQL."""

    def __init__(self, connection_string: str = None):
        """Initialize the database loader.

        Args:
            connection_string: PostgreSQL connection string
        """
        if connection_string:
            self.connection_string = connection_string
        else:
            # Build connection string from environment variables
            host = os.getenv('POSTGRES_HOST', 'localhost')
            port = os.getenv('POSTGRES_PORT', '5432')
            db = os.getenv('POSTGRES_DB', 'football_analytics')
            user = os.getenv('POSTGRES_USER', 'airflow')
            password = os.getenv('POSTGRES_PASSWORD', 'airflow')
            self.connection_string = f'postgresql://{user}:{password}@{host}:{port}/{db}'

        self.engine = create_engine(self.connection_string)
        self.metadata = MetaData(schema='raw')
        self._create_tables()

    def _create_tables(self):
        """Create raw data tables if they don't exist."""
        # Competitions table
        self.competitions_table = Table(
            'competitions',
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String),
            Column('code', String),
            Column('type', String),
            Column('emblem', String),
            Column('area_name', String),
            Column('area_code', String),
            Column('current_season', JSON),
            Column('raw_data', JSON),
            Column('extracted_at', DateTime, default=datetime.utcnow),
            schema='raw'
        )

        # Teams table
        self.teams_table = Table(
            'teams',
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String),
            Column('short_name', String),
            Column('tla', String),
            Column('crest', String),
            Column('address', String),
            Column('website', String),
            Column('founded', Integer),
            Column('club_colors', String),
            Column('venue', String),
            Column('raw_data', JSON),
            Column('extracted_at', DateTime, default=datetime.utcnow),
            schema='raw'
        )

        # Matches table
        self.matches_table = Table(
            'matches',
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('competition_id', Integer),
            Column('season_id', Integer),
            Column('utc_date', DateTime),
            Column('status', String),
            Column('matchday', Integer),
            Column('stage', String),
            Column('group', String),
            Column('home_team_id', Integer),
            Column('home_team_name', String),
            Column('away_team_id', Integer),
            Column('away_team_name', String),
            Column('winner', String),
            Column('duration', String),
            Column('full_time_home', Integer),
            Column('full_time_away', Integer),
            Column('half_time_home', Integer),
            Column('half_time_away', Integer),
            Column('raw_data', JSON),
            Column('extracted_at', DateTime, default=datetime.utcnow),
            schema='raw'
        )

        # Standings table
        self.standings_table = Table(
            'standings',
            self.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('competition_id', Integer),
            Column('season_id', Integer),
            Column('stage', String),
            Column('type', String),
            Column('group', String),
            Column('team_id', Integer),
            Column('team_name', String),
            Column('position', Integer),
            Column('played_games', Integer),
            Column('won', Integer),
            Column('draw', Integer),
            Column('lost', Integer),
            Column('points', Integer),
            Column('goals_for', Integer),
            Column('goals_against', Integer),
            Column('goal_difference', Integer),
            Column('raw_data', JSON),
            Column('extracted_at', DateTime, default=datetime.utcnow),
            schema='raw'
        )

        # Create all tables
        self.metadata.create_all(self.engine)
        logger.info("Database tables created successfully")

    def load_competitions(self, competitions: List[Dict]) -> int:
        """Load competitions data into the database.

        Args:
            competitions: List of competition dictionaries

        Returns:
            Number of records loaded
        """
        if not competitions:
            logger.warning("No competitions to load")
            return 0

        records = []
        for comp in competitions:
            record = {
                'id': comp.get('id'),
                'name': comp.get('name'),
                'code': comp.get('code'),
                'type': comp.get('type'),
                'emblem': comp.get('emblem'),
                'area_name': comp.get('area', {}).get('name'),
                'area_code': comp.get('area', {}).get('code'),
                'current_season': comp.get('currentSeason'),
                'raw_data': comp,
                'extracted_at': datetime.utcnow()
            }
            records.append(record)

        with self.engine.connect() as conn:
            stmt = insert(self.competitions_table).values(records)
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_={
                    'name': stmt.excluded.name,
                    'code': stmt.excluded.code,
                    'type': stmt.excluded.type,
                    'emblem': stmt.excluded.emblem,
                    'area_name': stmt.excluded.area_name,
                    'area_code': stmt.excluded.area_code,
                    'current_season': stmt.excluded.current_season,
                    'raw_data': stmt.excluded.raw_data,
                    'extracted_at': stmt.excluded.extracted_at
                }
            )
            conn.execute(stmt)
            conn.commit()

        logger.info(f"Loaded {len(records)} competitions")
        return len(records)

    def load_teams(self, teams: List[Dict]) -> int:
        """Load teams data into the database.

        Args:
            teams: List of team dictionaries

        Returns:
            Number of records loaded
        """
        if not teams:
            logger.warning("No teams to load")
            return 0

        records = []
        for team in teams:
            record = {
                'id': team.get('id'),
                'name': team.get('name'),
                'short_name': team.get('shortName'),
                'tla': team.get('tla'),
                'crest': team.get('crest'),
                'address': team.get('address'),
                'website': team.get('website'),
                'founded': team.get('founded'),
                'club_colors': team.get('clubColors'),
                'venue': team.get('venue'),
                'raw_data': team,
                'extracted_at': datetime.utcnow()
            }
            records.append(record)

        with self.engine.connect() as conn:
            stmt = insert(self.teams_table).values(records)
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_={
                    'name': stmt.excluded.name,
                    'short_name': stmt.excluded.short_name,
                    'tla': stmt.excluded.tla,
                    'crest': stmt.excluded.crest,
                    'address': stmt.excluded.address,
                    'website': stmt.excluded.website,
                    'founded': stmt.excluded.founded,
                    'club_colors': stmt.excluded.club_colors,
                    'venue': stmt.excluded.venue,
                    'raw_data': stmt.excluded.raw_data,
                    'extracted_at': stmt.excluded.extracted_at
                }
            )
            conn.execute(stmt)
            conn.commit()

        logger.info(f"Loaded {len(records)} teams")
        return len(records)

    def load_matches(self, matches: List[Dict]) -> int:
        """Load matches data into the database.

        Args:
            matches: List of match dictionaries

        Returns:
            Number of records loaded
        """
        if not matches:
            logger.warning("No matches to load")
            return 0

        records = []
        for match in matches:
            score = match.get('score', {})
            full_time = score.get('fullTime', {})
            half_time = score.get('halfTime', {})

            record = {
                'id': match.get('id'),
                'competition_id': match.get('competition', {}).get('id'),
                'season_id': match.get('season', {}).get('id'),
                'utc_date': match.get('utcDate'),
                'status': match.get('status'),
                'matchday': match.get('matchday'),
                'stage': match.get('stage'),
                'group': match.get('group'),
                'home_team_id': match.get('homeTeam', {}).get('id'),
                'home_team_name': match.get('homeTeam', {}).get('name'),
                'away_team_id': match.get('awayTeam', {}).get('id'),
                'away_team_name': match.get('awayTeam', {}).get('name'),
                'winner': score.get('winner'),
                'duration': score.get('duration'),
                'full_time_home': full_time.get('home'),
                'full_time_away': full_time.get('away'),
                'half_time_home': half_time.get('home'),
                'half_time_away': half_time.get('away'),
                'raw_data': match,
                'extracted_at': datetime.utcnow()
            }
            records.append(record)

        with self.engine.connect() as conn:
            stmt = insert(self.matches_table).values(records)
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_={
                    'competition_id': stmt.excluded.competition_id,
                    'season_id': stmt.excluded.season_id,
                    'utc_date': stmt.excluded.utc_date,
                    'status': stmt.excluded.status,
                    'matchday': stmt.excluded.matchday,
                    'stage': stmt.excluded.stage,
                    'group': stmt.excluded.group,
                    'home_team_id': stmt.excluded.home_team_id,
                    'home_team_name': stmt.excluded.home_team_name,
                    'away_team_id': stmt.excluded.away_team_id,
                    'away_team_name': stmt.excluded.away_team_name,
                    'winner': stmt.excluded.winner,
                    'duration': stmt.excluded.duration,
                    'full_time_home': stmt.excluded.full_time_home,
                    'full_time_away': stmt.excluded.full_time_away,
                    'half_time_home': stmt.excluded.half_time_home,
                    'half_time_away': stmt.excluded.half_time_away,
                    'raw_data': stmt.excluded.raw_data,
                    'extracted_at': stmt.excluded.extracted_at
                }
            )
            conn.execute(stmt)
            conn.commit()

        logger.info(f"Loaded {len(records)} matches")
        return len(records)

    def load_standings(self, standings_data: Dict, competition_id: int) -> int:
        """Load standings data into the database.

        Args:
            standings_data: Standings data dictionary from API
            competition_id: Competition ID

        Returns:
            Number of records loaded
        """
        standings = standings_data.get('standings', [])
        if not standings:
            logger.warning("No standings to load")
            return 0

        records = []
        for standing in standings:
            stage = standing.get('stage')
            type_ = standing.get('type')
            group = standing.get('group')

            for table_entry in standing.get('table', []):
                record = {
                    'competition_id': competition_id,
                    'season_id': standings_data.get('season', {}).get('id'),
                    'stage': stage,
                    'type': type_,
                    'group': group,
                    'team_id': table_entry.get('team', {}).get('id'),
                    'team_name': table_entry.get('team', {}).get('name'),
                    'position': table_entry.get('position'),
                    'played_games': table_entry.get('playedGames'),
                    'won': table_entry.get('won'),
                    'draw': table_entry.get('draw'),
                    'lost': table_entry.get('lost'),
                    'points': table_entry.get('points'),
                    'goals_for': table_entry.get('goalsFor'),
                    'goals_against': table_entry.get('goalsAgainst'),
                    'goal_difference': table_entry.get('goalDifference'),
                    'raw_data': table_entry,
                    'extracted_at': datetime.utcnow()
                }
                records.append(record)

        if records:
            with self.engine.connect() as conn:
                # Delete existing standings for this competition and season
                season_id = standings_data.get('season', {}).get('id')
                conn.execute(
                    self.standings_table.delete().where(
                        (self.standings_table.c.competition_id == competition_id) &
                        (self.standings_table.c.season_id == season_id)
                    )
                )

                # Insert new standings
                conn.execute(self.standings_table.insert(), records)
                conn.commit()

        logger.info(f"Loaded {len(records)} standing records")
        return len(records)
