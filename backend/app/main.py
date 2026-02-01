import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
load_dotenv()

from .config import settings
from .db import CacheDB
from .moralis import MoralisClient
from .burn_service import BurnService, MissingHistoricalCache


def _require_env(value: str, name: str) -> str:
    if not value:
        raise RuntimeError(f"{name} não definido.")
    return value

_require_env(settings.moralis_api_key, "MORALIS_API_KEY")
_require_env(settings.token_address, "TOKEN_ADDRESS")
_require_env(settings.max_supply_tokens, "MAX_SUPPLY_TOKENS")

app = FastAPI(title="Jager Burn Projection API", version="2.2.0")

def _cors_list() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    return [o.strip() for o in raw.split(",") if o.strip()]

origins = _cors_list()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # e.g.: ["http://localhost:3000", "https://your-front.com"]
    allow_credentials=False,      # leave False unless you use cookies/credentials
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    allow_fetch_missing_historical_days=settings.allow_fetch_missing_historical_days,
    series_cache_ttl_seconds=settings.series_cache_ttl_seconds,
)

@app.get("/")
async def root():
    return {"ok": True, "docs": "/docs", "health": "/health"}

@app.get("/health")
async def health():
    return {"ok": True}

@app.get("/token/meta")
async def token_meta():
    meta = await svc.get_meta()
    return {
        "address": settings.token_address,
        "name": meta.name,
        "symbol": meta.symbol,
        "decimals": meta.decimals,
        "dead_address": settings.dead_address,
    }

@app.get("/token/metrics")
async def token_metrics():
    try:
        return await svc.token_metrics()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/burn/summary")
async def burn_summary():
    try:
        return await svc.summary()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/burn/series")
async def burn_series(window_days: int = Query(30, ge=1, le=settings.max_window_days)):
    try:
        daily, total_raw, start_day, end_day, today_updated_epoch = await svc.get_daily_series(window_days)
        meta = await svc.get_meta()
        from .utils import raw_to_tokens, fmt_decimal
        total_tokens = raw_to_tokens(int(total_raw), meta.decimals)

        return {
            "token": {
                "address": settings.token_address,
                "name": meta.name,
                "symbol": meta.symbol,
                "decimals": meta.decimals,
                "dead_address": settings.dead_address,
            },
            "window_days": window_days,
            "start_day": start_day,
            "end_day": end_day,
            "total_burn_raw": str(int(total_raw)),
            "total_burn": fmt_decimal(total_tokens),
            "daily": [d.__dict__ for d in daily],
            "data_source": "moralis+sqlite-cache",
            "today_last_updated_epoch": today_updated_epoch,
        }
    except MissingHistoricalCache as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "MISSING_HISTORICAL_CACHE",
                "missing_days": e.missing_days,
                "how_to_fix": "Execute o backfill uma vez para preencher o histórico (ex.: python -m app.backfill --start 2025-04-28). "
                              "Ou copie o cache.sqlite3 antigo para o caminho definido em CACHE_DB_PATH.",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/burn/projection")
async def burn_projection(
    window_days: int = Query(30, ge=1, le=settings.max_window_days),
    horizon_days: int = Query(365, ge=1, le=settings.max_horizon_days),
    model: str = Query("mean", pattern="^(mean|regression)$"),
):
    try:
        return await svc.projection(window_days=window_days, horizon_days=horizon_days, model=model)
    except MissingHistoricalCache as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "MISSING_HISTORICAL_CACHE",
                "missing_days": e.missing_days,
                "how_to_fix": "Execute o backfill uma vez para preencher o histórico (ex.: python -m app.backfill --start 2025-04-28). "
                              "Ou copie o cache.sqlite3 antigo para o caminho definido em CACHE_DB_PATH.",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
