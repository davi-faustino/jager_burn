from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Optional, List, Dict
import json
import threading

_LOCK = threading.Lock()

@dataclass
class DailyBurnRow:
    day: str
    burn_raw: str
    updated_at: int

@dataclass
class KVRow:
    key: str
    payload_json: str
    updated_at: int

class CacheDB:
    """
    Compat:
    - Alguns builds anteriores usavam tabela `burn_daily`.
    - Builds posteriores usaram `daily_burn`.
    Este wrapper detecta automaticamente qual existe e usa a mesma,
    evitando perda de cache/histórico ao atualizar o código.
    """
    def __init__(self, path: str):
        self.path = path
        self._daily_table: str = "burn_daily"
        self._init()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _table_exists(self, conn: sqlite3.Connection, name: str) -> bool:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (name,))
        return cur.fetchone() is not None

    def _init(self) -> None:
        with _LOCK:
            conn = self._conn()
            try:
                cur = conn.cursor()

                # KV cache (sempre o mesmo)
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS kv_cache (
                        key TEXT PRIMARY KEY,
                        payload_json TEXT NOT NULL,
                        updated_at INTEGER NOT NULL
                    );
                    """
                )

                has_burn_daily = self._table_exists(conn, "burn_daily")
                has_daily_burn = self._table_exists(conn, "daily_burn")

                # Preferir burn_daily se existir, para compatibilidade com seu cache.sqlite3
                if has_burn_daily:
                    self._daily_table = "burn_daily"
                elif has_daily_burn:
                    self._daily_table = "daily_burn"
                else:
                    # default: criar burn_daily
                    self._daily_table = "burn_daily"
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS burn_daily (
                            day TEXT PRIMARY KEY,
                            burn_raw TEXT NOT NULL,
                            updated_at INTEGER NOT NULL
                        );
                        """
                    )

                conn.commit()
            finally:
                conn.close()

    # ----- Daily burn -----

    def get_daily(self, day: str) -> Optional[DailyBurnRow]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT day, burn_raw, updated_at FROM {self._daily_table} WHERE day = ?", (day,))
            row = cur.fetchone()
            if not row:
                return None
            return DailyBurnRow(day=row["day"], burn_raw=row["burn_raw"], updated_at=int(row["updated_at"]))
        finally:
            conn.close()

    def upsert_daily(self, day: str, burn_raw: str, updated_at: int) -> None:
        with _LOCK:
            conn = self._conn()
            try:
                cur = conn.cursor()
                # SQLite UPSERT requires PK; day is PK in both schemas
                cur.execute(
                    f"INSERT INTO {self._daily_table}(day, burn_raw, updated_at) VALUES(?,?,?) "
                    f"ON CONFLICT(day) DO UPDATE SET burn_raw=excluded.burn_raw, updated_at=excluded.updated_at",
                    (day, burn_raw, int(updated_at)),
                )
                conn.commit()
            finally:
                conn.close()

    def list_daily_range(self, start_day: str, end_day: str) -> List[DailyBurnRow]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                f"SELECT day, burn_raw, updated_at FROM {self._daily_table} "
                f"WHERE day >= ? AND day <= ? ORDER BY day ASC",
                (start_day, end_day),
            )
            rows = cur.fetchall()
            return [
                DailyBurnRow(day=r["day"], burn_raw=r["burn_raw"], updated_at=int(r["updated_at"]))
                for r in rows
            ]
        finally:
            conn.close()

    # ----- KV cache -----

    def get_kv(self, key: str) -> Optional[KVRow]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT key, payload_json, updated_at FROM kv_cache WHERE key = ?", (key,))
            row = cur.fetchone()
            if not row:
                return None
            return KVRow(key=row["key"], payload_json=row["payload_json"], updated_at=int(row["updated_at"]))
        finally:
            conn.close()

    def upsert_kv(self, key: str, payload: Dict, updated_at: int) -> None:
        payload_json = json.dumps(payload, ensure_ascii=False)
        with _LOCK:
            conn = self._conn()
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO kv_cache(key, payload_json, updated_at) VALUES(?,?,?) "
                    "ON CONFLICT(key) DO UPDATE SET payload_json=excluded.payload_json, updated_at=excluded.updated_at",
                    (key, payload_json, int(updated_at)),
                )
                conn.commit()
            finally:
                conn.close()
