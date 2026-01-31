from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Set, Tuple, AsyncIterator, List
import asyncio
import httpx

MORALIS_BASE = "https://deep-index.moralis.io/api/v2.2"

@dataclass
class TokenMeta:
    name: str
    symbol: str
    decimals: int

class MoralisClient:
    def __init__(self, api_key: str, chain: str = "bsc", timeout: float = 30.0):
        if not api_key:
            raise RuntimeError("MORALIS_API_KEY não definido.")
        self.api_key = api_key
        self.chain = chain
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        return {"X-API-Key": self.api_key}

    async def _get(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        # Basic retry/backoff for 429 and transient 5xx
        max_attempts = 5
        backoff = 0.75
        async with httpx.AsyncClient(timeout=self.timeout, headers=self._headers()) as client:
            for attempt in range(1, max_attempts + 1):
                r = await client.get(url, params=params)
                if r.status_code == 429:
                    retry_after = r.headers.get("Retry-After")
                    wait_s = float(retry_after) if retry_after and retry_after.replace(".", "", 1).isdigit() else backoff * attempt
                    await asyncio.sleep(min(wait_s, 10.0))
                    continue
                if 500 <= r.status_code < 600:
                    await asyncio.sleep(min(backoff * attempt, 5.0))
                    continue
                r.raise_for_status()
                return r.json()
        raise httpx.HTTPStatusError("Too many requests / retry attempts exceeded", request=None, response=None)

    async def get_token_metadata(self, token_address: str) -> Optional[TokenMeta]:
        url = f"{MORALIS_BASE}/erc20/metadata"
        params = {"chain": self.chain, "addresses": token_address}
        data = await self._get(url, params)
        if isinstance(data, list) and len(data) > 0:
            item = data[0]
            decimals = int(item.get("decimals", 18))
            return TokenMeta(
                name=item.get("name", ""),
                symbol=item.get("symbol", ""),
                decimals=decimals,
            )
        return None

    async def get_token_price_usd(self, token_address: str) -> Optional[float]:
        url = f"{MORALIS_BASE}/erc20/{token_address}/price"
        params = {"chain": self.chain}
        data = await self._get(url, params)
        price = data.get("usdPrice")
        if price is None:
            return None
        return float(price)

    async def get_wallet_erc20_balance_raw(self, wallet_address: str, token_address: str) -> Optional[int]:
        url = f"{MORALIS_BASE}/{wallet_address}/erc20"
        params = {"chain": self.chain, "token_addresses": token_address}
        data = await self._get(url, params)
        if isinstance(data, list) and len(data) > 0:
            bal = data[0].get("balance")
            if bal is None:
                return None
            return int(bal)
        return None

    def _transfer_id(self, item: Dict[str, Any]) -> Optional[Tuple[str, str]]:
        tx = item.get("transaction_hash") or item.get("transactionHash")
        log_index = item.get("log_index") or item.get("logIndex")
        if tx is not None and log_index is not None:
            return (str(tx), str(log_index))
        bn = item.get("block_number") or item.get("blockNumber")
        ti = item.get("transaction_index") or item.get("transactionIndex")
        if tx is not None and bn is not None and ti is not None:
            return (str(tx), f"{bn}:{ti}")
        return None

    async def iter_burn_transfers(
        self,
        token_address: str,
        to_address: str | None = None,
        dead_address: str | None = None,
        from_date_iso: str = "",
        to_date_iso: str = "",
        page_limit: int = 100,
        max_pages: int = 200,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Retorna TRANSFERS para a carteira dead usando o endpoint **por wallet**:
          GET /:address/erc20/transfers

        Importante:
        - O endpoint por contrato (/erc20/:address/transfers) NÃO suporta filtro por `to_address`.
        - O endpoint por wallet suporta `contract_addresses[]`, reduzindo drasticamente a resposta.

        Compat:
        - builds antigos chamavam com `to_address=...`
        - builds novos chamavam com `dead_address=...`
        Aqui aceitamos ambos (to_address tem prioridade).

        Filtro:
        - contract_addresses=[token_address]
        - depois filtramos apenas itens com to_address == dead (incoming).

        Proteções:
        - dedupe por (tx_hash, log_index) quando disponível
        - break se cursor não avançar
        """
        target_address = (to_address or dead_address)
        if not target_address:
            raise ValueError("to_address/dead_address é obrigatório.")

        url = f"{MORALIS_BASE}/{target_address}/erc20/transfers"
        cursor: Optional[str] = None
        prev_cursor: Optional[str] = None
        pages = 0
        seen: Set[Tuple[str, str]] = set()

        dead_lc = target_address.lower()

        async with httpx.AsyncClient(timeout=self.timeout, headers=self._headers()) as client:
            while True:
                params: Dict[str, Any] = {
                    "chain": self.chain,
                    "from_date": from_date_iso,
                    "to_date": to_date_iso,
                    "limit": page_limit,
                    # Moralis aceita contract_addresses[] para filtrar apenas esse token
                    "contract_addresses": [token_address],
                }
                if cursor:
                    params["cursor"] = cursor

                payload: Optional[Dict[str, Any]] = None
                for attempt in range(1, 6):
                    r = await client.get(url, params=params)
                    if r.status_code == 429:
                        retry_after = r.headers.get("Retry-After")
                        wait_s = float(retry_after) if retry_after and retry_after.isdigit() else 0.75 * attempt
                        await asyncio.sleep(min(wait_s, 10.0))
                        continue
                    if 500 <= r.status_code < 600:
                        await asyncio.sleep(min(0.5 * attempt, 5.0))
                        continue
                    r.raise_for_status()
                    payload = r.json()
                    break

                if payload is None:
                    raise httpx.HTTPStatusError("429 Too Many Requests (retries exceeded)", request=None, response=None)

                result = payload.get("result", []) or []
                for item in result:
                    # Apenas incoming para dead
                    to_addr = (item.get("to_address") or "").lower()
                    if to_addr != dead_lc:
                        continue

                    tid = self._transfer_id(item)
                    if tid:
                        if tid in seen:
                            continue
                        seen.add(tid)

                    yield item

                prev_cursor = cursor
                cursor = payload.get("cursor")
                pages += 1

                if not cursor:
                    break
                if prev_cursor is not None and cursor == prev_cursor:
                    break
                if pages >= max_pages:
                    break
