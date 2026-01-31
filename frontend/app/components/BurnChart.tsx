"use client";

import { useEffect, useMemo, useState } from "react";
import type { BurnSeriesResponse } from "@/app/lib/types";
import { api } from "@/app/lib/api";
import { formatCompactNumber } from "@/app/lib/format";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

type Props = { windowDays: number };

export function BurnChart({ windowDays }: Props) {
  const [data, setData] = useState<BurnSeriesResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const d = (await api.series(windowDays)) as BurnSeriesResponse;
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
  }, [windowDays]);

  const chartData = useMemo(() => {
    if (!data) return [];
    return data.daily.map((d) => ({
      day: d.day.slice(5),
      burn: Number(d.burn),
      burnFullDay: d.day,
    }));
  }, [data]);

  return (
    <section className="rounded-xl border border-zinc-800 bg-zinc-900/30 p-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <div className="text-lg font-semibold">Burn per day (UTC)</div>
          <div className="text-sm text-zinc-400">
            Window: last {windowDays} days{data ? ` • ${data.start_day} → ${data.end_day}` : ""}
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

      <div className="mt-4 h-[320px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="day" />
            <YAxis tickFormatter={(v) => formatCompactNumber(Number(v))} />
            <Tooltip
              formatter={(value: any) => [formatCompactNumber(Number(value)), "Burn"]}
              labelFormatter={(_label: any, payload: any) => {
                const item = payload?.[0]?.payload;
                return item?.burnFullDay ? `Day: ${item.burnFullDay}` : "Day";
              }}
            />
            <Bar dataKey="burn" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {data ? (
        <div className="mt-3 text-sm text-zinc-500">
          Total burn in window: <span className="text-zinc-200">{formatCompactNumber(Number(data.total_burn))}</span>{" "}
          {data.token.symbol}
        </div>
      ) : null}
    </section>
  );
}
