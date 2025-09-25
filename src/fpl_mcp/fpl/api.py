import httpx
import asyncio
import json
import jsonschema
import logging
import time
import random
from typing import Any, Dict, List, Optional

from .cache import cache, cached
from .rate_limiter import RateLimiter
from ..config import (
    FPL_API_BASE_URL,
    FPL_USER_AGENT,
    FPL_HEADERS,
    STATIC_SCHEMA_PATH,
    RATE_LIMIT_MAX_REQUESTS,
    RATE_LIMIT_PERIOD_SECONDS,
    PROXY_ENABLED,
    PROXY_LIST,
    PROXY_ROTATION_ENABLED,
    PROXY_MAX_RETRIES,
    PROXY_TIMEOUT
)

# Set up logging
logger = logging.getLogger(__name__)

class FPLAPI:
    """
    FPL API client with schema validation, caching, and rate limiting.
    Handles fetching data from the Fantasy Premier League API.
    """
    def __init__(self,
                 base_url: str = FPL_API_BASE_URL,
                 schema_path: str = STATIC_SCHEMA_PATH,
                 headers: Dict[str, str] = None):
        """
        Initialize the FPL API client.

        Args:
            base_url: FPL API base URL
            schema_path: Path to JSON schema for validation
            headers: Custom headers for requests (uses FPL_HEADERS by default)
        """
        self.base_url = base_url
        self.schema_path = schema_path
        self.headers = headers or FPL_HEADERS.copy()
        self.rate_limiter = RateLimiter(
            max_requests=RATE_LIMIT_MAX_REQUESTS,
            per_seconds=RATE_LIMIT_PERIOD_SECONDS
        )

        # Initialize proxy settings
        self.proxy_enabled = PROXY_ENABLED
        self.proxy_list = PROXY_LIST.copy() if PROXY_LIST else []
        self.proxy_rotation_enabled = PROXY_ROTATION_ENABLED
        self.current_proxy_index = 0

        if self.proxy_rotation_enabled:
            logger.info(f"Proxy rotation enabled with {len(self.proxy_list)} proxies")
        elif self.proxy_enabled:
            logger.info("Proxy enabled but no proxy URLs configured")
        else:
            logger.info("Proxy disabled - using direct connections")
        
        # Load schema for bootstrap-static if available
        self.schema = None
        try:
            with open(schema_path, 'r') as f:
                schema_data = json.load(f)
                self.schema = schema_data.get('schema')
                logger.info(f"Loaded schema from {schema_path}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load schema: {e}")
    
    def _get_next_proxy(self) -> Optional[str]:
        """Get the next proxy in rotation"""
        if not self.proxy_rotation_enabled:
            return None

        if self.current_proxy_index >= len(self.proxy_list):
            self.current_proxy_index = 0

        proxy = self.proxy_list[self.current_proxy_index]
        self.current_proxy_index += 1
        return proxy

    async def _make_request_with_proxy(self, url: str, proxy: str = None) -> Dict[str, Any]:
        """Make a request with optional proxy"""
        client_kwargs = {
            "timeout": PROXY_TIMEOUT,
            "follow_redirects": True
        }

        if proxy:
            client_kwargs["proxies"] = proxy
            logger.debug(f"Using proxy: {proxy}")

        async with httpx.AsyncClient(**client_kwargs) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def _make_request(self, endpoint: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Make an HTTP request to the FPL API with proxy rotation and retry logic.

        Args:
            endpoint: API endpoint to request (without base URL)
            max_retries: Maximum number of retry attempts

        Returns:
            JSON response data

        Raises:
            httpx.HTTPError: On HTTP error
        """
        url = f"{self.base_url}/{endpoint}"
        last_error = None

        # First try without proxy (direct connection)
        for attempt in range(max_retries + 1):
            await self.rate_limiter.acquire()

            try:
                logger.debug(f"Direct request to {url} (attempt {attempt + 1})")

                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(url, headers=self.headers, follow_redirects=True)
                    response.raise_for_status()
                    return response.json()

            except httpx.HTTPStatusError as e:
                last_error = e
                logger.warning(f"Direct request failed with HTTP {e.response.status_code}")

                if e.response.status_code == 403:
                    logger.info("403 Forbidden - will try proxy rotation if available")
                    break  # Don't retry direct connection for 403, try proxies
                elif attempt < max_retries:
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Retrying direct connection in {delay:.1f}s")
                    await asyncio.sleep(delay)

            except httpx.RequestError as e:
                last_error = e
                if attempt < max_retries:
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Request error, retrying in {delay:.1f}s: {str(e)}")
                    await asyncio.sleep(delay)

        # If direct connection failed with 403 and we have proxies, try proxy rotation
        if self.proxy_rotation_enabled and isinstance(last_error, httpx.HTTPStatusError) and last_error.response.status_code == 403:
            logger.info("Trying proxy rotation to bypass 403 Forbidden")

            for proxy_attempt in range(len(self.proxy_list)):
                proxy = self._get_next_proxy()
                if not proxy:
                    break

                for retry in range(PROXY_MAX_RETRIES):
                    await self.rate_limiter.acquire()

                    try:
                        logger.debug(f"Proxy request to {url} via {proxy} (attempt {retry + 1})")
                        result = await self._make_request_with_proxy(url, proxy)
                        logger.info(f"✅ Success via proxy {proxy}")
                        return result

                    except httpx.HTTPStatusError as e:
                        if e.response.status_code == 403:
                            logger.warning(f"Proxy {proxy} also got 403 Forbidden")
                            break  # Try next proxy
                        elif retry < PROXY_MAX_RETRIES - 1:
                            delay = 1 + random.uniform(0, 0.5)
                            logger.warning(f"Proxy request failed, retrying in {delay:.1f}s")
                            await asyncio.sleep(delay)

                    except httpx.RequestError as e:
                        logger.warning(f"Proxy {proxy} connection failed: {str(e)}")
                        if retry < PROXY_MAX_RETRIES - 1:
                            delay = 1 + random.uniform(0, 0.5)
                            await asyncio.sleep(delay)
                        else:
                            break  # Try next proxy

        # All attempts failed
        if isinstance(last_error, httpx.HTTPStatusError) and last_error.response.status_code == 403:
            logger.error("❌ FPL API returned 403 Forbidden after trying all methods:")
            logger.error("1. Direct connection failed")
            if self.proxy_rotation_enabled:
                logger.error(f"2. All {len(self.proxy_list)} proxies failed")
            logger.error("This may be due to:")
            logger.error("- Widespread IP blocking by FPL")
            logger.error("- Geographic restrictions")
            logger.error("- API maintenance or changes")
            logger.error("Consider using a different proxy service or VPN")

        # Re-raise the last error
        raise last_error
    
    def validate_data(self, data: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> bool:
        """
        Validate data against JSON schema.
        
        Args:
            data: Data to validate
            schema: Schema to validate against (uses self.schema if None)
            
        Returns:
            True if validation succeeds, False otherwise
        """
        if not schema and not self.schema:
            logger.warning("No schema available for validation")
            return True
            
        try:
            jsonschema.validate(instance=data, schema=schema or self.schema)
            return True
        except jsonschema.exceptions.ValidationError as e:
            logger.warning(f"Schema validation failed: {e}")
            return False
    
    @cached("bootstrap_static")
    async def get_bootstrap_static(self) -> Dict[str, Any]:
        """
        Get main FPL static data (players, teams, game settings).
        Uses caching with 1-hour TTL by default.
        
        Returns:
            Bootstrap static data
        """
        data = await self._make_request("bootstrap-static/")
        
        # Fix null values that should be integers according to schema
        if 'phases' in data:
            for phase in data['phases']:
                if phase.get('highest_score') is None:
                    phase['highest_score'] = 0
        
        # Validate against schema if available
        if self.schema:
            self.validate_data(data)
            
        return data
    
    @cached("fixtures")
    async def get_fixtures(self) -> List[Dict[str, Any]]:
        """
        Get fixture data for all matches.
        
        Returns:
            List of fixtures
        """
        return await self._make_request("fixtures/")
    
    @cached("gameweeks")
    async def get_gameweeks(self) -> List[Dict[str, Any]]:
        """
        Get all gameweeks data.
        
        Returns:
            List of gameweeks
        """
        static_data = await self.get_bootstrap_static()
        return static_data.get("events", [])
    
    @cached("current_gameweek", ttl=600)  # 10-minute TTL for current GW
    async def get_current_gameweek(self) -> Dict[str, Any]:
        """
        Get current gameweek data.
        
        Returns:
            Current gameweek data or None if not found
        """
        gameweeks = await self.get_gameweeks()
        for gw in gameweeks:
            if gw.get("is_current", False):
                return gw
                
        # If no current gameweek found, return next one
        for gw in gameweeks:
            if gw.get("is_next", False):
                return gw
                
        # If no next gameweek either, return first one
        return gameweeks[0] if gameweeks else {}
    
    @cached("element_summary")
    async def get_player_summary(self, player_id: int) -> Dict[str, Any]:
        """
        Get detailed data for a specific player.
        
        Args:
            player_id: FPL player ID
            
        Returns:
            Player summary data
        """
        return await self._make_request(f"element-summary/{player_id}/")
        
    async def get_players(self) -> List[Dict[str, Any]]:
        """
        Get all players data.
        
        Returns:
            List of player data
        """
        static_data = await self.get_bootstrap_static()
        return static_data.get("elements", [])
    
    async def get_teams(self) -> List[Dict[str, Any]]:
        """
        Get all teams data.
        
        Returns:
            List of team data
        """
        static_data = await self.get_bootstrap_static()
        return static_data.get("teams", [])


# Create a singleton instance
api = FPLAPI()