"use client";

import { useEffect, useState } from "react";
import type { BurnSummaryResponse } from "@/app/lib/types";
import { api } from "@/app/lib/api";
import { epochToUtcString, formatTokenAmount } from "@/app/lib/format";

export function SummaryCards() {
  const [data, setData] = useState<BurnSummaryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const d = (await api.summary()) as BurnSummaryResponse;
      setData(d);
    } catch (e: any) {
      setError(e?.message || String(e));
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
    <section className="grid gap-4 md:grid-cols-2">
      <div className="rounded-xl border border-zinc-800 bg-zinc-900/30 p-4">
        <div className="text-sm text-zinc-400">Yesterday</div>
        <div className="mt-2 text-2xl font-semibold">
          {loading ? "Loading..." : data ? `${formatTokenAmount(data.yesterday.burn)} ${data.token.symbol}` : "—"}
        </div>
        <div className="mt-1 text-sm text-zinc-500">UTC day: {data?.yesterday.day ?? "—"}</div>
      </div>

      <div className="rounded-xl border border-zinc-800 bg-zinc-900/30 p-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="text-sm text-zinc-400">Today (updates every 5 min)</div>
            <div className="mt-2 text-2xl font-semibold">
              {loading ? "Loading..." : data ? `${formatTokenAmount(data.today.burn)} ${data.token.symbol}` : "—"}
            </div>
            <div className="mt-1 text-sm text-zinc-500">UTC day: {data?.today.day ?? "—"}</div>
          </div>
          <button
            onClick={load}
            className="rounded-lg border border-zinc-700 px-3 py-2 text-sm hover:bg-zinc-800 disabled:opacity-60"
            disabled={loading}
          >
            Refresh
          </button>
        </div>

        <div className="mt-2 text-sm text-zinc-500">Last update: {epochToUtcString(data?.today.last_updated_epoch)}</div>

        {error ? (
          <div className="mt-3 rounded-lg border border-red-900/60 bg-red-950/30 p-3 text-sm text-red-200">
            {error}
          </div>
        ) : null}
      </div>
    </section>
  );
}
