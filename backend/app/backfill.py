from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone, timedelta, date

from dotenv import load_dotenv
load_dotenv()

from .config import settings
from .db import CacheDB
from .moralis import MoralisClient
from .burn_service import BurnService


def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()

async def run(start: date):
    db = CacheDB(settings.cache_db_path)
    moralis = MoralisClient(api_key=settings.moralis_api_key, chain=settings.chain)
    svc = BurnService(
        moralis=moralis,
        db=db,
        token_address=settings.token_address,
        dead_address=settings.dead_address,
        decimals_fallback=settings.token_decimals,
        cache_ttl_seconds=settings.cache_ttl_seconds,
        max_supply_tokens=settings.max_supply_tokens,
        allow_fetch_missing_historical_days=True,  # backfill can always fetch historical data
        series_cache_ttl_seconds=settings.series_cache_ttl_seconds,
    )

    today = datetime.now(timezone.utc).date()
    d = start
    while d <= (today - timedelta(days=1)):
        await svc.ensure_day_cached(d, force_refresh=True)
        print("cached", d.isoformat())
        d += timedelta(days=1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="YYYY-MM-DD")
    args = ap.parse_args()
    asyncio.run(run(parse_date(args.start)))

if __name__ == "__main__":
    main()
