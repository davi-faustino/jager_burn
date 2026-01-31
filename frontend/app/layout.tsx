import { Analytics } from "@vercel/analytics/next";
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Jager Burn Calculator",
  description:
    "Burn summary and projection calculator for JAGER (dead address burn).",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen">
          <header className="border-b border-zinc-800">
            <div className="mx-auto max-w-6xl px-4 py-4 flex items-center justify-between">
              <div>
                <div className="text-lg font-semibold">
                  Jager Burn Calculator
                </div>
              </div>
            </div>
          </header>

          <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>

          <footer className="border-t border-zinc-800">
            <div className="mx-auto max-w-6xl px-4 py-4 text-sm text-zinc-500">
              Burns are aggregated by UTC day (00:00–23:59:59).
            </div>
          </footer>
        </div>

        <Analytics />
      </body>
    </html>
  );
}
