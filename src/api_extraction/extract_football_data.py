"""Main extraction script for Football-Data.org API data."""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

from football_api_client import FootballAPIClient
from database_loader import DatabaseLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def extract_competitions(api_client: FootballAPIClient, db_loader: DatabaseLoader):
    """Extract and load competitions data.

    Args:
        api_client: Football API client
        db_loader: Database loader
    """
    logger.info("Extracting competitions...")
    competitions = api_client.get_competitions()
    count = db_loader.load_competitions(competitions)
    logger.info(f"Successfully extracted and loaded {count} competitions")


def extract_competition_data(
    api_client: FootballAPIClient,
    db_loader: DatabaseLoader,
    competition_ids: list
):
    """Extract teams, matches, and standings for specified competitions.

    Args:
        api_client: Football API client
        db_loader: Database loader
        competition_ids: List of competition IDs to extract
    """
    for comp_id in competition_ids:
        try:
            logger.info(f"Extracting data for competition {comp_id}...")

            # Extract teams
            teams = api_client.get_competition_teams(comp_id)
            teams_count = db_loader.load_teams(teams)
            logger.info(f"Loaded {teams_count} teams for competition {comp_id}")

            # Extract standings
            standings = api_client.get_competition_standings(comp_id)
            standings_count = db_loader.load_standings(standings, comp_id)
            logger.info(f"Loaded {standings_count} standings for competition {comp_id}")

            # Extract matches (last 30 days and next 30 days)
            date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            date_to = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            matches = api_client.get_competition_matches(
                comp_id,
                date_from=date_from,
                date_to=date_to
            )
            matches_count = db_loader.load_matches(matches)
            logger.info(f"Loaded {matches_count} matches for competition {comp_id}")

        except Exception as e:
            logger.error(f"Error extracting data for competition {comp_id}: {str(e)}")
            continue


def main():
    """Main extraction workflow."""
    try:
        # Initialize clients
        api_client = FootballAPIClient()
        db_loader = DatabaseLoader()

        # Extract all competitions first
        extract_competitions(api_client, db_loader)

        # Extract detailed data for major European competitions
        # Premier League (PL), La Liga (PD), Bundesliga (BL1), Serie A (SA), Ligue 1 (FL1)
        # Champions League (CL), Europa League (EL)
        major_competition_ids = [
            2021,  # Premier League
            2014,  # La Liga
            2002,  # Bundesliga
            2019,  # Serie A
            2015,  # Ligue 1
            2001,  # Champions League
            2146,  # Europa League (UEFA Europa League)
        ]

        extract_competition_data(api_client, db_loader, major_competition_ids)

        logger.info("Data extraction completed successfully!")

    except Exception as e:
        logger.error(f"Data extraction failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
