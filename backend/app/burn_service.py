from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import time
import math
import json

from .db import CacheDB
from .moralis import MoralisClient, TokenMeta
from .utils import (
    utc_today,
    day_start_end_iso,
    raw_to_tokens,
    tokens_to_T,
    fmt_decimal,
    pct,
)

@dataclass
class DailyBurn:
    day: str
    burn_raw: str
    burn: str

class MissingHistoricalCache(Exception):
    def __init__(self, missing_days: List[str]):
        super().__init__("Missing historical cache days: " + ", ".join(missing_days))
        self.missing_days = missing_days

class BurnService:
    def __init__(
        self,
        moralis: MoralisClient,
        db: CacheDB,
        token_address: str,
        dead_address: str,
        decimals_fallback: int,
        cache_ttl_seconds: int,
        max_supply_tokens: str,
        allow_fetch_missing_historical_days: bool = False,
        series_cache_ttl_seconds: int = 300,
    ):
        self.moralis = moralis
        self.db = db
        self.token_address = token_address
        self.dead_address = dead_address
        self.decimals_fallback = decimals_fallback
        self.cache_ttl_seconds = cache_ttl_seconds
        self.series_cache_ttl_seconds = series_cache_ttl_seconds
        self.allow_fetch_missing_historical_days = allow_fetch_missing_historical_days
        self._meta: Optional[TokenMeta] = None
        self.max_supply_tokens_str = max_supply_tokens

    async def get_meta(self) -> TokenMeta:
        if self._meta:
            return self._meta
        meta = await self.moralis.get_token_metadata(self.token_address)
        if not meta:
            meta = TokenMeta(name="", symbol="", decimals=self.decimals_fallback)
        self._meta = meta
        return meta

    async def _fetch_burn_raw_for_day(self, day: date) -> int:
        # Sum transfers to dead during that UTC day
        start_iso, end_iso = day_start_end_iso(day)
        total = 0
        async for t in self.moralis.iter_burn_transfers(
            token_address=self.token_address,
            to_address=self.dead_address,
            from_date_iso=start_iso,
            to_date_iso=end_iso,
        ):
            v = t.get("value")
            if v is None:
                continue
            total += int(v)
        return total

    async def ensure_day_cached(self, day: date, force_refresh: bool = False) -> int:
        day_s = day.isoformat()
        row = self.db.get_daily(day_s)
        now = int(time.time())
        is_today = (day == utc_today())

        # Cache rule:
        # - Past days: never change. We only fetch from Moralis if:
        #   a) force_refresh=True (backfill), or
        #   b) allow_fetch_missing_historical_days=True and doesn't exist in cache.
        # - Today: can change. Updates every cache_ttl_seconds.
        if row is None:
            if (not is_today) and (not force_refresh) and (not self.allow_fetch_missing_historical_days):
                raise MissingHistoricalCache([day_s])
            burn_raw = await self._fetch_burn_raw_for_day(day)
            self.db.upsert_daily(day_s, str(burn_raw), now)
            return burn_raw

        if is_today and ((now - row.updated_at) > self.cache_ttl_seconds or force_refresh):
            burn_raw = await self._fetch_burn_raw_for_day(day)
            self.db.upsert_daily(day_s, str(burn_raw), now)
            return burn_raw

        if force_refresh:
            burn_raw = await self._fetch_burn_raw_for_day(day)
            self.db.upsert_daily(day_s, str(burn_raw), now)
            return burn_raw

        return int(row.burn_raw)

    def _series_cache_key(self, window_days: int, today_iso: str) -> str:
        return f"series:{window_days}:{today_iso}"

    async def get_daily_series(self, window_days: int) -> Tuple[List[DailyBurn], int, str, str, int]:
        meta = await self.get_meta()
        today = utc_today()

        # "Last N days" = includes today and the N-1 previous days
        start_day = today - timedelta(days=window_days - 1)

        cache_key = self._series_cache_key(window_days, today.isoformat())
        now = int(time.time())
        kv = self.db.get_kv(cache_key)
        if kv and (now - kv.updated_at) <= self.series_cache_ttl_seconds:
            payload = json.loads(kv.payload_json)
            daily = [DailyBurn(**d) for d in payload["daily"]]
            return daily, int(payload["total_raw"]), payload["start_day"], payload["end_day"], int(payload["today_updated_epoch"])

        days: List[date] = []
        d = start_day
        while d <= today:
            days.append(d)
            d += timedelta(days=1)

        daily: List[DailyBurn] = []
        total_raw = 0
        missing: List[str] = []
        today_updated_epoch: int = 0

        for day in days:
            try:
                burn_raw = await self.ensure_day_cached(day)
            except MissingHistoricalCache as e:
                missing.extend(e.missing_days)
                continue

            if day == today:
                row = self.db.get_daily(day.isoformat())
                today_updated_epoch = int(row.updated_at) if row else 0

            burn_tokens = raw_to_tokens(burn_raw, meta.decimals)
            daily.append(
                DailyBurn(
                    day=day.isoformat(),
                    burn_raw=str(burn_raw),
                    burn=fmt_decimal(burn_tokens, 18),
                )
            )
            total_raw += burn_raw

        if missing:
            # Don't fetch historical data automatically (protects credits)
            raise MissingHistoricalCache(sorted(set(missing)))

        payload = {
            "daily": [d.__dict__ for d in daily],
            "total_raw": str(total_raw),
            "start_day": start_day.isoformat(),
            "end_day": today.isoformat(),
            "today_updated_epoch": today_updated_epoch,
        }
        self.db.upsert_kv(cache_key, payload, now)

        return daily, total_raw, start_day.isoformat(), today.isoformat(), today_updated_epoch

    async def summary(self) -> Dict:
        meta = await self.get_meta()
        today = utc_today()
        yesterday = today - timedelta(days=1)

        y_raw = await self.ensure_day_cached(yesterday)
        t_raw = await self.ensure_day_cached(today)

        t_row = self.db.get_daily(today.isoformat())
        t_updated = t_row.updated_at if t_row else None

        return {
            "token": {
                "address": self.token_address,
                "name": meta.name,
                "symbol": meta.symbol,
                "decimals": meta.decimals,
                "dead_address": self.dead_address,
            },
            "yesterday": {
                "day": yesterday.isoformat(),
                "burn_raw": str(y_raw),
                "burn": fmt_decimal(raw_to_tokens(y_raw, meta.decimals)),
                "label": "Yesterday X tokens were burned",
            },
            "today": {
                "day": today.isoformat(),
                "burn_raw": str(t_raw),
                "burn": fmt_decimal(raw_to_tokens(t_raw, meta.decimals)),
                "label": "Today X tokens have been burned (Updated every 5 minutes)",
                "last_updated_epoch": t_updated,
            },
            "data_source": "moralis+sqlite-cache",
        }

    def _linear_regression_slope(self, xs: List[float], ys: List[float]) -> float:
        n = len(xs)
        if n < 2:
            return 0.0
        x_mean = sum(xs) / n
        y_mean = sum(ys) / n
        num = sum((xs[i] - x_mean) * (ys[i] - y_mean) for i in range(n))
        den = sum((xs[i] - x_mean) ** 2 for i in range(n))
        if den == 0:
            return 0.0
        return num / den

    def _projection_cache_key(self, window_days: int, horizon_days: int, model: str, today_iso: str) -> str:
        return f"projection:{model}:{window_days}:{horizon_days}:{today_iso}"

    async def projection(self, window_days: int, horizon_days: int, model: str) -> Dict:
        today_iso = utc_today().isoformat()
        now = int(time.time())
        cache_key = self._projection_cache_key(window_days, horizon_days, model, today_iso)
        kv = self.db.get_kv(cache_key)
        if kv and (now - kv.updated_at) <= self.series_cache_ttl_seconds:
            payload = json.loads(kv.payload_json)
            payload["cached"] = True
            return payload

        meta = await self.get_meta()
        daily, total_raw, start_day, end_day, today_updated_epoch = await self.get_daily_series(window_days)
        burns_tokens = [Decimal(d.burn) for d in daily]  # tokens per day

        assumption = ""
        used_model = model

        if model == "mean":
            x = sum(burns_tokens) / Decimal(len(burns_tokens))
            y = x * Decimal(horizon_days)
            assumption = "Daily average burn over the last W days."
        else:
            cum = []
            running = Decimal(0)
            for b in burns_tokens:
                running += b
                cum.append(running)
            xs = [float(i) for i in range(len(cum))]
            ys = [float(c) for c in cum]
            slope = self._linear_regression_slope(xs, ys)  # tokens/day
            if not math.isfinite(slope) or slope < 0:
                used_model = "regression_fallback_mean"
                x = sum(burns_tokens) / Decimal(len(burns_tokens))
                y = x * Decimal(horizon_days)
                assumption = "Unstable/negative regression; fallback to mean."
            else:
                x = Decimal(str(slope))
                y = x * Decimal(horizon_days)
                assumption = "Linear regression on cumulative burn (slope = tokens/day)."

        tokenomics = await self.token_metrics()
        max_supply = Decimal(tokenomics["max_supply_tokens"])
        burned_now = Decimal(tokenomics["burned_tokens"])
        burned_future = burned_now + y
        if burned_future > max_supply:
            burned_future = max_supply
        remaining_future = max_supply - burned_future
        burned_pct_future = pct(burned_future, max_supply)

        tokenomics_projected = {
            "burned_tokens": fmt_decimal(burned_future),
            "burned_t": fmt_decimal(tokens_to_T(burned_future)),
            "burned_pct": fmt_decimal(burned_pct_future),
            "remaining_tokens": fmt_decimal(remaining_future),
            "remaining_t": fmt_decimal(tokens_to_T(remaining_future)),
        }

        payload = {
            "model": used_model,
            "window_days": window_days,
            "horizon_days": horizon_days,
            "x_burn_per_day_raw": str(int((x * (Decimal(10) ** Decimal(meta.decimals))).to_integral_value())),
            "x_burn_per_day": fmt_decimal(x),
            "y_burn_raw": str(int((y * (Decimal(10) ** Decimal(meta.decimals))).to_integral_value())),
            "y_burn": fmt_decimal(y),
            "assumption": assumption,
            "data_source": "moralis+sqlite-cache",
            "today_last_updated_epoch": today_updated_epoch,
            "tokenomics": tokenomics,
            "tokenomics_projected": tokenomics_projected,
            "cached": False,
        }
        self.db.upsert_kv(cache_key, payload, now)
        return payload

    async def token_metrics(self) -> Dict:
        key = "token_metrics"
        now = int(time.time())
        row = self.db.get_kv(key)
        if row and (now - row.updated_at) <= self.cache_ttl_seconds:
            payload = json.loads(row.payload_json)
            payload["last_updated_epoch"] = row.updated_at
            return payload

        meta = await self.get_meta()
        max_supply_tokens = Decimal(self.max_supply_tokens_str or "0")
        if max_supply_tokens <= 0:
            raise RuntimeError("MAX_SUPPLY_TOKENS inválido ou não definido.")

        burned_raw = await self.moralis.get_wallet_erc20_balance_raw(self.dead_address, self.token_address)
        if burned_raw is None:
            raise RuntimeError("Falha ao obter balance da dead wallet no Moralis.")

        burned_tokens = raw_to_tokens(burned_raw, meta.decimals)
        remaining_tokens = max_supply_tokens - burned_tokens
        if remaining_tokens < 0:
            remaining_tokens = Decimal(0)

        burned_pct = pct(burned_tokens, max_supply_tokens)

        price = await self.moralis.get_token_price_usd(self.token_address)
        price_str = None
        if price is not None:
            price_str = f"{price:.18f}".rstrip("0").rstrip(".")

        payload = {
            "token": {
                "address": self.token_address,
                "name": meta.name,
                "symbol": meta.symbol,
                "decimals": meta.decimals,
                "dead_address": self.dead_address,
            },
            "max_supply_tokens": fmt_decimal(max_supply_tokens),
            "max_supply_t": fmt_decimal(tokens_to_T(max_supply_tokens)),
            "burned_raw": str(burned_raw),
            "burned_tokens": fmt_decimal(burned_tokens),
            "burned_t": fmt_decimal(tokens_to_T(burned_tokens)),
            "burned_pct": fmt_decimal(burned_pct),
            "remaining_tokens": fmt_decimal(remaining_tokens),
            "remaining_t": fmt_decimal(tokens_to_T(remaining_tokens)),
            "price_usd": price_str,
            "data_source": "moralis+sqlite-cache",
        }

        self.db.upsert_kv(key, payload, now)
        payload["last_updated_epoch"] = now
        return payload
