import os
import pathlib
from importlib import resources
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Base paths - handle both development and installed package
try:
    # When installed as package
    with resources.path("fpl_mcp", "__init__.py") as p:
        BASE_DIR = p.parent
except (ImportError, ModuleNotFoundError):
    # During development
    BASE_DIR = pathlib.Path(__file__).parent.absolute()

SCHEMAS_DIR = BASE_DIR / "schemas"
# Use user cache dir for persistent cache
CACHE_DIR = pathlib.Path(os.getenv("FPL_CACHE_DIR", str(pathlib.Path.home() / ".cache" / "fpl-mcp")))

# FPL API configuration
FPL_API_BASE_URL = "https://fantasy.premierleague.com/api"
FPL_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
FPL_LOGIN_URL = "https://users.premierleague.com/accounts/login/"

# Enhanced headers for FPL API compatibility
FPL_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://fantasy.premierleague.com/",
    "Origin": "https://fantasy.premierleague.com",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}

# Caching configuration
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # Default: 1 hour

# Schema paths
STATIC_SCHEMA_PATH = SCHEMAS_DIR / "static_schema.json"

# Rate limiting configuration
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "20"))
RATE_LIMIT_PERIOD_SECONDS = int(os.getenv("RATE_LIMIT_PERIOD_SECONDS", "60"))

# League configuration
LEAGUE_RESULTS_LIMIT = 25

# Proxy configuration for bypassing FPL API restrictions
PROXY_ENABLED = os.getenv("PROXY_ENABLED", "true").lower() == "true"

# Free proxy services (will be rotated)
# These are public proxies - replace with your own for better reliability
PROXY_LIST = [
    # Public HTTP proxies (may be unstable)
    "http://20.206.106.192:8123",
    "http://103.149.162.194:80",
    "http://47.74.152.29:8888",
    "http://103.167.109.69:80",
    "http://20.111.54.16:8123",
    # Add your own reliable proxies here
    # Commercial proxy services like:
    # - ProxyMesh: "http://username:password@proxy.proxymesh.com:31280"
    # - Bright Data: "http://username:password@zproxy.lum-superproxy.io:22225"
    # - SmartProxy: "http://username:password@gate.smartproxy.com:10000"
]

# Load proxies from environment variable (comma-separated)
if os.getenv("PROXY_URLS"):
    PROXY_LIST.extend(os.getenv("PROXY_URLS").split(","))

# Proxy rotation settings
PROXY_ROTATION_ENABLED = len(PROXY_LIST) > 0 and PROXY_ENABLED
PROXY_MAX_RETRIES = 2  # Max retries per proxy
PROXY_TIMEOUT = 30  # Timeout per proxy request