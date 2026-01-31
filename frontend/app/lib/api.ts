const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") || "http://localhost:8000";

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    cache: "no-store",
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return (await res.json()) as T;
}

export const api = {
  summary: () => fetchJson("/burn/summary"),
  series: (windowDays: number) => fetchJson(`/burn/series?window_days=${windowDays}`),
  projection: (windowDays: number, horizonDays: number, model: "mean" | "regression") =>
    fetchJson(`/burn/projection?window_days=${windowDays}&horizon_days=${horizonDays}&model=${model}`),
  tokenMetrics: () => fetchJson("/token/metrics"),
};
