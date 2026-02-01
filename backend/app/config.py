from pydantic import BaseModel
import os

def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()

def _env_bool(name: str, default: str = "false") -> bool:
    v = _env(name, default).lower()
    return v in ("1", "true", "yes", "y", "on")

class Settings(BaseModel):
    moralis_api_key: str = _env("MORALIS_API_KEY")
    token_address: str = _env("TOKEN_ADDRESS")
    token_decimals: int = int(_env("TOKEN_DECIMALS", "18"))
    max_supply_tokens: str = _env("MAX_SUPPLY_TOKENS", "")

    # Cache local (SQLite)
    cache_db_path: str = _env("CACHE_DB_PATH", "./cache.sqlite3")
    cache_ttl_seconds: int = int(_env("CACHE_TTL_SECONDS", "300"))  # 5 minutes

    # If FALSE: endpoints never fetch missing historical days from Moralis (protects credits).
    # Use the backfill script to populate history.
    allow_fetch_missing_historical_days: bool = _env_bool("ALLOW_FETCH_MISSING_HISTORICAL_DAYS", "false")

    # Cache for /burn/series and /burn/projection results (reduces repeated frontend calls)
    series_cache_ttl_seconds: int = int(_env("SERIES_CACHE_TTL_SECONDS", _env("CACHE_TTL_SECONDS", "300")))

    max_window_days: int = int(_env("MAX_WINDOW_DAYS", "3650"))
    max_horizon_days: int = int(_env("MAX_HORIZON_DAYS", "3650"))

    dead_address: str = "0x000000000000000000000000000000000000dEaD"
    chain: str = "bsc"

settings = Settings()
