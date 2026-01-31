# Jager Burn Calculator (Next.js)

Frontend Next.js para consumir o backend FastAPI (burn summary + series + projections).

## Rodar

```bash
npm install
npm run dev
```

Abra: http://localhost:3000

## Configurar backend

Crie `.env.local`:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```


## Tokenomics
This UI calls `GET /token/metrics` to display max supply (env), burned total (dead balance) and price (Moralis).