"use client";

import { useEffect, useState } from "react";
import type { TokenMetricsResponse } from "@/app/lib/types";
import { api } from "@/app/lib/api";
import { epochToUtcString, formatPercentString, formatT, formatDecimalString, formatUsdString } from "@/app/lib/format";

export function TokenomicsCards() {
  const [data, setData] = useState<TokenMetricsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const d = (await api.tokenMetrics()) as TokenMetricsResponse;
      setData(d);
    } catch (e: any) {
      setError(e?.message || String(e));
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const id = setInterval(load, 5 * 60 * 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <section className="rounded-xl border border-zinc-800 bg-zinc-900/30 p-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <div className="text-lg font-semibold">Tokenomics</div>
          <div className="text-sm text-zinc-400">
            Max supply (env) + burned (dead balance) + price (Moralis). Updates every 5 minutes.
          </div>
        </div>
        <button
          onClick={load}
          className="rounded-lg border border-zinc-700 px-3 py-2 text-sm hover:bg-zinc-800 disabled:opacity-60"
          disabled={loading}
        >
          {loading ? "Loading..." : "Refresh"}
        </button>
      </div>

      {error ? (
        <div className="mt-4 rounded-lg border border-red-900/60 bg-red-950/30 p-3 text-sm text-red-200">
          {error}
        </div>
      ) : null}

      <div className="mt-4 grid gap-4 md:grid-cols-5">
        <div className="rounded-xl border border-zinc-800 bg-zinc-950/40 p-4">
          <div className="text-sm text-zinc-400">Max supply</div>
          <div className="mt-2 text-lg font-semibold">{data ? `${formatT(data.max_supply_t)}T` : "—"}</div>
          <div className="mt-1 text-xs text-zinc-500">{data ? `${formatDecimalString(data.max_supply_tokens, 0)} tokens` : "—"}</div>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-zinc-950/40 p-4">
          <div className="text-sm text-zinc-400">Burned</div>
          <div className="mt-2 text-lg font-semibold">{data ? `${formatT(data.burned_t)}T` : "—"}</div>
          <div className="mt-1 text-xs text-zinc-500">{data ? `${formatDecimalString(data.burned_tokens, 4)} tokens` : "—"}</div>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-zinc-950/40 p-4">
          <div className="text-sm text-zinc-400">Burned %</div>
          <div className="mt-2 text-lg font-semibold">{data ? formatPercentString(data.burned_pct) : "—"}</div>
          <div className="mt-1 text-xs text-zinc-500">of max supply</div>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-zinc-950/40 p-4">
          <div className="text-sm text-zinc-400">Remaining supply</div>
          <div className="mt-2 text-lg font-semibold">{data ? `${formatT(data.remaining_t)}T` : "—"}</div>
          <div className="mt-1 text-xs text-zinc-500">{data ? `${formatDecimalString(data.remaining_tokens, 4)} tokens` : "—"}</div>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-zinc-950/40 p-4">
          <div className="text-sm text-zinc-400">Price</div>
          <div className="mt-2 text-lg font-semibold">{data ? formatUsdString(data.price_usd) : "—"}</div>
          <div className="mt-1 text-xs text-zinc-500">Updated: {epochToUtcString(data?.last_updated_epoch)}</div>
        </div>
      </div>
    </section>
  );
}
