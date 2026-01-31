# Jager Burn Backend (FastAPI + Moralis + SQLite cache)

API para calcular:

- Burn diário (Transfer para 0x...dEaD) com cache local
- Summary (ontem/hoje)
- Projeções (mean/regression)
- Token metrics (max supply via env, burned total via dead balance, % burned, remaining supply, price via Moralis)

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

## Endpoints

- GET /health
- GET /token/meta
- GET /token/metrics
- GET /burn/summary
- GET /burn/series?window_days=30
- GET /burn/projection?window_days=30&horizon_days=365&model=mean

## Importante sobre créditos do Moralis (anti-surpresa)

Por padrão, `ALLOW_FETCH_MISSING_HISTORICAL_DAYS=false`.

Isso significa:

- Dias passados **NÃO** serão buscados no Moralis automaticamente.
- Se algum dia histórico estiver faltando no SQLite, o endpoint vai retornar erro `MISSING_HISTORICAL_CACHE` com a lista de dias.
- Para preencher o histórico, rode **uma vez**:

```bash
python -m app.backfill --start 2025-04-28
```

### Reutilizar cache antigo

Se você já tinha um `cache.sqlite3` com histórico e trocou o código por um ZIP novo, copie o arquivo `cache.sqlite3` antigo para o caminho definido em `CACHE_DB_PATH`.

### Compatibilidade de cache

Este backend detecta automaticamente a tabela `burn_daily` (legado) ou `daily_burn` (novo) e utiliza a que existir no seu arquivo SQLite.

## Importante: cálculo de burn (Moralis)

Este backend usa o endpoint **por wallet** do Moralis (`/:address/erc20/transfers`) com `contract_addresses[]=TOKEN` para calcular burns (incoming para 0x...dEaD). O endpoint por contrato (`/erc20/:address/transfers`) não possui filtro por `to_address`, então não é adequado para burns.
