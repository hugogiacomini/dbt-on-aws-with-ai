"""Football-Data.org API client for data extraction."""

import os
import requests
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FootballAPIClient:
    """Client for interacting with Football-Data.org API."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize the API client.

        Args:
            api_key: API key for Football-Data.org
            base_url: Base URL for the API
        """
        self.api_key = api_key or os.getenv('FOOTBALL_API_KEY')
        self.base_url = base_url or os.getenv('FOOTBALL_API_BASE_URL', 'https://api.football-data.org/v4')

        if not self.api_key:
            raise ValueError("FOOTBALL_API_KEY must be provided or set in environment")

        self.headers = {
            'X-Auth-Token': self.api_key
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a request to the API with rate limiting and error handling.

        Args:
            endpoint: API endpoint to call
            params: Query parameters

        Returns:
            JSON response data
        """
        url = f"{self.base_url}/{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=30)

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('X-RateLimit-Reset', 60))
                logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                return self._make_request(endpoint, params)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {str(e)}")
            raise

    def get_competitions(self) -> List[Dict]:
        """Get all available competitions.

        Returns:
            List of competition dictionaries
        """
        logger.info("Fetching competitions...")
        data = self._make_request('competitions')
        return data.get('competitions', [])

    def get_competition_standings(self, competition_id: int, season: Optional[int] = None) -> Dict:
        """Get standings for a specific competition.

        Args:
            competition_id: ID of the competition
            season: Season year (defaults to current)

        Returns:
            Standings data
        """
        logger.info(f"Fetching standings for competition {competition_id}...")
        endpoint = f'competitions/{competition_id}/standings'
        params = {'season': season} if season else None
        return self._make_request(endpoint, params)

    def get_competition_teams(self, competition_id: int, season: Optional[int] = None) -> List[Dict]:
        """Get teams in a competition.

        Args:
            competition_id: ID of the competition
            season: Season year (defaults to current)

        Returns:
            List of team dictionaries
        """
        logger.info(f"Fetching teams for competition {competition_id}...")
        endpoint = f'competitions/{competition_id}/teams'
        params = {'season': season} if season else None
        data = self._make_request(endpoint, params)
        return data.get('teams', [])

    def get_competition_matches(
        self,
        competition_id: int,
        season: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get matches for a competition.

        Args:
            competition_id: ID of the competition
            season: Season year (defaults to current)
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            status: Match status (SCHEDULED, LIVE, IN_PLAY, PAUSED, FINISHED, etc.)

        Returns:
            List of match dictionaries
        """
        logger.info(f"Fetching matches for competition {competition_id}...")
        endpoint = f'competitions/{competition_id}/matches'

        params = {}
        if season:
            params['season'] = season
        if date_from:
            params['dateFrom'] = date_from
        if date_to:
            params['dateTo'] = date_to
        if status:
            params['status'] = status

        data = self._make_request(endpoint, params)
        return data.get('matches', [])

    def get_team(self, team_id: int) -> Dict:
        """Get detailed information about a team.

        Args:
            team_id: ID of the team

        Returns:
            Team data dictionary
        """
        logger.info(f"Fetching team {team_id}...")
        return self._make_request(f'teams/{team_id}')

    def get_team_matches(
        self,
        team_id: int,
        season: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get matches for a specific team.

        Args:
            team_id: ID of the team
            season: Season year
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            status: Match status

        Returns:
            List of match dictionaries
        """
        logger.info(f"Fetching matches for team {team_id}...")
        endpoint = f'teams/{team_id}/matches'

        params = {}
        if season:
            params['season'] = season
        if date_from:
            params['dateFrom'] = date_from
        if date_to:
            params['dateTo'] = date_to
        if status:
            params['status'] = status

        data = self._make_request(endpoint, params)
        return data.get('matches', [])

    def get_match(self, match_id: int) -> Dict:
        """Get detailed information about a specific match.

        Args:
            match_id: ID of the match

        Returns:
            Match data dictionary
        """
        logger.info(f"Fetching match {match_id}...")
        return self._make_request(f'matches/{match_id}')
