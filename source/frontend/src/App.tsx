/**
 * App.tsx — Root component: wires together Sidebar, TopBar, and page routes.
 *
 * The `useSSE()` hook is mounted once here so its state (sensorStates,
 * recentAlerts, connected) is available to all pages via React context.
 */
import { createContext, useContext } from "react";
import { Outlet, useMatches } from "react-router-dom";
import Sidebar  from "./components/layout/Sidebar";
import TopBar   from "./components/layout/TopBar";
import { useSSE } from "./hooks/useSSE";
import type { SSEState } from "./hooks/useSSE";

// ── SSE context ───────────────────────────────────────────────────────────────

const SSEContext = createContext<SSEState>({
  sensorStates: {},
  recentAlerts: [],
  connected:    false,
  lastUpdated:  null,
});

/** Consume live SSE data anywhere in the component tree. */
export const useLiveData = () => useContext(SSEContext);

// ── Route handle typing ───────────────────────────────────────────────────────

interface RouteHandle { title?: string }

function usePageTitle(): string {
  const matches = useMatches();
  for (let i = matches.length - 1; i >= 0; i--) {
    const handle = matches[i].handle as RouteHandle | undefined;
    if (handle?.title) return handle.title;
  }
  return "Mars Operations";
}

// ── Root layout ───────────────────────────────────────────────────────────────

export default function App() {
  const sse   = useSSE();
  const title = usePageTitle();

  return (
    <SSEContext.Provider value={sse}>
      <div className="flex h-screen overflow-hidden">
        <Sidebar connected={sse.connected} />

        {/* Right panel: TopBar + scrollable page content */}
        <div className="flex flex-col flex-1 overflow-hidden">
          <TopBar
            title={title}
            connected={sse.connected}
            lastUpdated={sse.lastUpdated}
          />
          <main className="flex-1 overflow-y-auto bg-gray-950">
            <div className="max-w-7xl mx-auto px-6 py-6">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </SSEContext.Provider>
  );
}
