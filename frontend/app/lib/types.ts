export type BurnSummaryResponse = {
  token: { address: string; name: string; symbol: string; decimals: number; dead_address: string };
  yesterday: { day: string; burn_raw: string; burn: string; label: string };
  today: { day: string; burn_raw: string; burn: string; label: string; last_updated_epoch: number | null };
  data_source: string;
};

export type BurnSeriesResponse = {
  token: { address: string; name: string; symbol: string; decimals: number; dead_address: string };
  window_days: number;
  start_day: string;
  end_day: string;
  total_burn_raw: string;
  total_burn: string;
  daily: Array<{ day: string; burn_raw: string; burn: string }>;
  data_source: string;
  today_last_updated_epoch?: number | null;
};

export type TokenMetricsResponse = {
  token: { address: string; name: string; symbol: string; decimals: number; dead_address: string };
  max_supply_tokens: string;
  max_supply_t: string;
  burned_raw: string;
  burned_tokens: string;
  burned_t: string;
  burned_pct: string;
  remaining_tokens: string;
  remaining_t: string;
  price_usd: string | null;
  data_source: string;
  last_updated_epoch: number;
};

export type BurnProjectionResponse = {
  model: "mean" | "regression" | "regression_fallback_mean";
  window_days: number;
  horizon_days: number;
  x_burn_per_day_raw: string;
  x_burn_per_day: string;
  y_burn_raw: string;
  y_burn: string;
  assumption: string;
  data_source: string;
  today_last_updated_epoch?: number | null;

  tokenomics?: TokenMetricsResponse;
  tokenomics_projected?: {
    burned_tokens: string;
    burned_t: string;
    burned_pct: string;
    remaining_tokens: string;
    remaining_t: string;
  };
};
