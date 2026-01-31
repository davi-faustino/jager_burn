export function formatCompactNumber(value: number): string {
  if (!isFinite(value)) return "—";
  const abs = Math.abs(value);

  const units: Array<[number, string]> = [
    [1e12, "T"],
    [1e9, "B"],
    [1e6, "M"],
    [1e3, "K"],
  ];

  for (const [threshold, suffix] of units) {
    if (abs >= threshold) {
      const v = value / threshold;
      return `${v.toFixed(v >= 100 ? 0 : v >= 10 ? 1 : 2)}${suffix}`;
    }
  }

  return value.toFixed(abs >= 100 ? 0 : abs >= 10 ? 1 : 2);
}

export function formatTokenAmount(tokenAmount: string): string {
  const num = Number(tokenAmount);
  if (!isFinite(num)) return tokenAmount;
  return formatCompactNumber(num);
}

// Formats integer/decimal numbers that may exceed JS safe integer, without converting to Number.
export function formatDecimalString(value: string, maxDecimals: number = 4): string {
  if (!value) return "—";
  const neg = value.startsWith("-");
  const raw = neg ? value.slice(1) : value;
  const [intPartRaw, fracRaw] = raw.split(".");

  const intPart = intPartRaw.replace(/^0+(?=\d)/, "");
  const intWithSep = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ",");

  if (!fracRaw || maxDecimals <= 0) return (neg ? "-" : "") + intWithSep;

  const frac = fracRaw.slice(0, maxDecimals).replace(/0+$/, "");
  if (!frac) return (neg ? "-" : "") + intWithSep;

  return (neg ? "-" : "") + `${intWithSep}.${frac}`;
}

// T values are small enough to be safely formatted as Number (max ~14600T here).
export function formatT(valueT: string, maxDecimals: number = 3): string {
  const num = Number(valueT);
  if (!isFinite(num)) return valueT;
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 0,
    maximumFractionDigits: maxDecimals,
  }).format(num);
}

export function formatPercentString(pct: string, decimals: number = 4): string {
  const num = Number(pct);
  if (!isFinite(num)) return `${pct}%`;
  return `${num.toFixed(decimals)}%`;
}

export function formatUsdString(usd: string | null | undefined, sigDigits: number = 3): string {
  if (!usd) return "—";
  const s = usd.trim().replace(/^\$/, "");
  // Use compact-leading-zeros format for very small prices: $0.0ₙXYZ
  if (s.startsWith("0.")) {
    const frac = s.split(".")[1] ?? "";
    let i = 0;
    while (i < frac.length && frac[i] === "0") i++;
    // Only compact if there are at least 3 leading zeros after the decimal point
    if (i >= 3 && i < frac.length) {
      const sig = frac.slice(i, i + sigDigits);
      const sub = toSubscript(i);
      return `$0.0${sub}${sig}`;
    }
  }
  // Fallback: keep as-is
  return `$${s}`;
}

function toSubscript(n: number): string {
  const map: Record<string, string> = {
    "0": "₀",
    "1": "₁",
    "2": "₂",
    "3": "₃",
    "4": "₄",
    "5": "₅",
    "6": "₆",
    "7": "₇",
    "8": "₈",
    "9": "₉",
  };
  return String(n)
    .split("")
    .map((c) => map[c] ?? c)
    .join("");
}

export function epochToUtcString(epoch: number | null | undefined): string {
  if (!epoch) return "—";
  const d = new Date(epoch * 1000);
  return d.toISOString().replace("T", " ").replace(".000Z", " UTC");
}

export function horizonToDays(value: number, unit: "days" | "months" | "years"): number {
  if (!isFinite(value) || value <= 0) return 1;
  if (unit === "days") return Math.round(value);
  if (unit === "months") return Math.round(value * 30);
  return Math.round(value * 365);
}
