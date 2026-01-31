"use client";

import { useMemo, useState } from "react";
import type { BurnProjectionResponse } from "@/app/lib/types";
import { api } from "@/app/lib/api";
import {
  epochToUtcString,
  formatPercentString,
  formatTokenAmount,
  formatUsdString,
  formatT,
  horizonToDays,
} from "@/app/lib/format";

export function ProjectionCalculator() {
  const [windowDays, setWindowDays] = useState<number>(30);
  const [model, setModel] = useState<"mean" | "regression">("mean");
  const [horizonValue, setHorizonValue] = useState<number>(365);
  const [horizonUnit, setHorizonUnit] = useState<"days" | "months" | "years">(
    "days"
  );

  const horizonDays = useMemo(
    () => horizonToDays(horizonValue, horizonUnit),
    [horizonValue, horizonUnit]
  );

  const [data, setData] = useState<BurnProjectionResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    setLoading(true);
    setError(null);
    try {
      const d = (await api.projection(
        windowDays,
        horizonDays,
        model
      )) as BurnProjectionResponse;
      setData(d);
    } catch (e: any) {
      setError(e?.message || String(e));
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const token = data?.tokenomics?.token;

  return (
    <section className="rounded-xl border border-zinc-800 bg-zinc-900/30 p-4">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <div className="text-lg font-semibold">Projection calculator</div>
          <div className="text-sm text-zinc-400">
            If the burn continues at rate X, we will burn Y tokens in Z days.
          </div>
        </div>

        <button
          onClick={run}
          className="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-zinc-900 hover:bg-zinc-200 disabled:opacity-60"
          disabled={loading}
        >
          {loading ? "Calculating..." : "Calculate"}
        </button>
      </div>

      <div className="mt-4 grid gap-4 md:grid-cols-3">
        <div>
          <label className="text-sm text-zinc-400">Window (W)</label>
          <select
            value={windowDays}
            onChange={(e) => setWindowDays(Number(e.target.value))}
            className="mt-2 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm"
          >
            {[7, 14, 30, 60, 90, 180, 365].map((d) => (
              <option key={d} value={d}>
                Last {d} days
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-sm text-zinc-400">Horizon (Z)</label>
          <div className="mt-2 flex gap-2">
            <input
              type="number"
              min={1}
              value={horizonValue}
              onChange={(e) => setHorizonValue(Number(e.target.value))}
              className="w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm"
            />
            <select
              value={horizonUnit}
              onChange={(e) => setHorizonUnit(e.target.value as any)}
              className="rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm"
            >
              <option value="days">days</option>
              <option value="months">months</option>
              <option value="years">years</option>
            </select>
          </div>
          <div className="mt-1 text-xs text-zinc-500">
            Converted to: {horizonDays} days
          </div>
        </div>

        <div>
          <label className="text-sm text-zinc-400">Model</label>
          <select
            value={model}
            onChange={(e) => setModel(e.target.value as any)}
            className="mt-2 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm"
          >
            <option value="mean">Mean (stable)</option>
            <option value="regression">Regression (trend)</option>
          </select>
        </div>
      </div>

      {error ? (
        <div className="mt-4 rounded-lg border border-red-900/60 bg-red-950/30 p-3 text-sm text-red-200">
          {error}
        </div>
      ) : null}

      {data ? (
        <div className="mt-5 space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-xl border border-zinc-800 bg-zinc-950/40 p-4">
              <div className="text-sm text-zinc-400">Rate (X)</div>
              <div className="mt-2 text-xl font-semibold">
                {formatTokenAmount(data.x_burn_per_day)} / day
              </div>
              <div className="mt-1 text-xs text-zinc-500">
                Based on W = {data.window_days} days
              </div>
            </div>

            <div className="rounded-xl border border-zinc-800 bg-zinc-950/40 p-4">
              <div className="text-sm text-zinc-400">Projected burn (Y)</div>
              <div className="mt-2 text-xl font-semibold">
                {formatTokenAmount(data.y_burn)}
              </div>
              <div className="mt-1 text-xs text-zinc-500">
                For Z = {data.horizon_days} days
              </div>
            </div>

            <div className="rounded-xl border border-zinc-800 bg-zinc-950/40 p-4">
              <div className="text-sm text-zinc-400">Notes</div>
              <div className="mt-2 text-sm text-zinc-200">
                {data.assumption}
              </div>
              <div className="mt-2 text-xs text-zinc-500">
                Today updated: {epochToUtcString(data.today_last_updated_epoch)}
              </div>
            </div>
          </div>

          {data.tokenomics ? (
            <div className="grid gap-4 md:grid-cols-4">
              <div className="rounded-xl border border-zinc-800 bg-zinc-950/40 p-4">
                <div className="text-sm text-zinc-400">Current burned %</div>
                <div className="mt-2 text-xl font-semibold">
                  {formatPercentString(data.tokenomics.burned_pct)}
                </div>
                <div className="mt-1 text-xs text-zinc-500">
                  Burned: {formatT(data.tokenomics.burned_t)}T of{" "}
                  {formatT(data.tokenomics.max_supply_t)}T
                </div>
              </div>

              <div className="rounded-xl border border-zinc-800 bg-zinc-950/40 p-4">
                <div className="text-sm text-zinc-400">Current remaining</div>
                <div className="mt-2 text-xl font-semibold">
                  {formatT(data.tokenomics.remaining_t)}T
                </div>
                <div className="mt-1 text-xs text-zinc-500">
                  {formatTokenAmount(data.tokenomics.remaining_tokens)} tokens
                </div>
              </div>

              {data.tokenomics_projected && (
                <>
                  <div className="rounded-xl border border-zinc-800 bg-zinc-950/40 p-4">
                    <div className="text-sm text-zinc-400">
                      Projected burned %
                    </div>
                    <div className="mt-2 text-xl font-semibold">
                      {formatPercentString(
                        data.tokenomics_projected.burned_pct
                      )}
                    </div>
                    <div className="mt-1 text-xs text-zinc-500">
                      Burned: {formatT(data.tokenomics_projected.burned_t)}T of{" "}
                      {formatT(data.tokenomics.max_supply_t)}T
                    </div>
                  </div>

                  <div className="rounded-xl border border-zinc-800 bg-zinc-950/40 p-4">
                    <div className="text-sm text-zinc-400">
                      Projected remaining
                    </div>
                    <div className="mt-2 text-xl font-semibold">
                      {formatT(data.tokenomics_projected.remaining_t)}T
                    </div>
                    <div className="mt-1 text-xs text-zinc-500">
                      {formatTokenAmount(
                        data.tokenomics_projected.remaining_tokens
                      )}{" "}
                      tokens
                    </div>
                  </div>
                </>
              )}
            </div>
          ) : null}
        </div>
      ) : (
        <div className="mt-4 text-sm text-zinc-500">
          Configure W/Z/model and click Calculate to generate a projection.
        </div>
      )}
    </section>
  );
}
