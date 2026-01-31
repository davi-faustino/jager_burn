from __future__ import annotations

from datetime import datetime, timezone, timedelta, date
from decimal import Decimal, getcontext

getcontext().prec = 50

def utc_today() -> date:
    return datetime.now(timezone.utc).date()

def day_to_iso(day: date) -> str:
    return day.isoformat()

def day_start_end_iso(day: date) -> tuple[str, str]:
    start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    return start.isoformat().replace("+00:00", "Z"), end.isoformat().replace("+00:00", "Z")

def raw_to_tokens(raw: int, decimals: int) -> Decimal:
    return Decimal(raw) / (Decimal(10) ** Decimal(decimals))

def tokens_to_raw(tokens: Decimal, decimals: int) -> int:
    return int((tokens * (Decimal(10) ** Decimal(decimals))).to_integral_value())

def tokens_to_T(tokens: Decimal) -> Decimal:
    return tokens / Decimal(10) ** Decimal(12)

def fmt_decimal(d: Decimal, max_decimals: int = 18) -> str:
    # strip trailing zeros
    s = format(d, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s

def pct(part: Decimal, whole: Decimal) -> Decimal:
    if whole == 0:
        return Decimal(0)
    return (part / whole) * Decimal(100)
