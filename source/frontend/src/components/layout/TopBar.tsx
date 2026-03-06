/**
 * components/layout/TopBar.tsx — Thin horizontal bar at the top of each page.
 *
 * Shows:
 *  • Current page title (passed as prop or derived from <title> via usePageTitle)
 *  • Live / Offline SSE badge
 *  • "Last updated" relative timestamp
 */
import { useEffect, useState } from "react";
import { Wifi, WifiOff } from "lucide-react";

interface TopBarProps {
  title:       string;
  connected:   boolean;
  lastUpdated: Date | null;
}

/** Format a Date as a human-readable relative string ("just now", "5 s ago", …). */
function relativeTime(date: Date): string {
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
  if (seconds < 5)  return "just now";
  if (seconds < 60) return `${seconds} s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} min ago`;
  return date.toLocaleTimeString();
}

export default function TopBar({ title, connected, lastUpdated }: TopBarProps) {
  // Re-render every 5 s so the relative time stays fresh.
  const [, tick] = useState(0);
  useEffect(() => {
    const id = setInterval(() => tick(n => n + 1), 5_000);
    return () => clearInterval(id);
  }, []);

  return (
    <header className="flex items-center justify-between h-12 px-6 border-b border-gray-800 bg-gray-900 shrink-0">
      {/* Page title */}
      <h1 className="text-sm font-semibold text-gray-100 tracking-wide">{title}</h1>

      {/* Right side badges */}
      <div className="flex items-center gap-3">
        {lastUpdated && (
          <span className="text-xs text-gray-500">
            Updated {relativeTime(lastUpdated)}
          </span>
        )}

        {connected ? (
          <span className="flex items-center gap-1.5 text-xs font-medium text-emerald-400">
            <Wifi size={13} />
            Live
          </span>
        ) : (
          <span className="flex items-center gap-1.5 text-xs font-medium text-gray-500">
            <WifiOff size={13} />
            Offline
          </span>
        )}
      </div>
    </header>
  );
}
