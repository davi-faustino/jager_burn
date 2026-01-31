"use client";

import { useState } from "react";
import { TokenomicsCards } from "@/app/components/TokenomicsCards";
import { SummaryCards } from "@/app/components/SummaryCards";
import { ProjectionCalculator } from "@/app/components/ProjectionCalculator";
import { BurnChart } from "@/app/components/BurnChart";

export default function Page() {
  const [chartWindowDays, setChartWindowDays] = useState<number>(30);

  return (
    <div className="space-y-6">
      <TokenomicsCards />
      <SummaryCards />
      <ProjectionCalculator />

      <section className="rounded-xl border border-zinc-800 bg-zinc-900/30 p-4">
        <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="text-lg font-semibold">Chart controls</div>
            <div className="text-sm text-zinc-400">
              Select the window for the daily burn chart.
            </div>
          </div>
          <select
            value={chartWindowDays}
            onChange={(e) => setChartWindowDays(Number(e.target.value))}
            className="rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm"
          >
            {[7, 14, 30, 60, 90, 180, 365].map((d) => (
              <option key={d} value={d}>
                Last {d} days
              </option>
            ))}
          </select>
        </div>
      </section>

      <BurnChart windowDays={chartWindowDays} />
    </div>
  );
}
