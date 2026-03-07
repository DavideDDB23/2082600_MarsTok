/**
 * useSSE.ts — Live data hook for the combined /api/stream endpoint.
 *
 * Connects to GET /api/stream (sse-starlette) which multiplexes two named
 * event types:
 *
 *   event: sensor_update   data: <InternalEvent JSON>
 *   event: alert           data: <AlertSchema JSON>
 *
 * Returns:
 *   sensorStates  — latest snapshot per source_id (Record<string, SensorState>)
 *   recentAlerts  — up to MAX_ALERTS most-recent alerts (newest first)
 *   connected     — true while the EventSource is in OPEN state
 *   lastUpdated   — Date of the most recent message
 */
import { useCallback, useEffect, useRef, useState } from "react";
import type { SensorState, StateMap } from "../types/sensor";
import type { Alert } from "../types/alert";

const SSE_URL    = "/api/stream";
const MAX_ALERTS = 50;
const RETRY_MS   = 3_000;

export interface SSEState {
  sensorStates: StateMap;
  recentAlerts: Alert[];
  connected:    boolean;
  lastUpdated:  Date | null;
}

export function useSSE(): SSEState {
  const [sensorStates, setSensorStates] = useState<StateMap>({});
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([]);
  const [connected,    setConnected]    = useState(false);
  const [lastUpdated,  setLastUpdated]  = useState<Date | null>(null);

  const retryRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const esRef    = useRef<EventSource | null>(null);

  // ── US4: Pre-populate state from REST on mount so the dashboard is never blank ──
  useEffect(() => {
    fetch("/api/state/")
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((states: StateMap) => {
        setSensorStates((prev) => {
          // SSE updates take priority over the snapshot — merge, live wins
          const merged = { ...states, ...prev };
          return merged;
        });
        setLastUpdated(new Date());
      })
      .catch(() => {/* silently ignore — SSE will populate shortly */});
  }, []);

  const handleSensorUpdate = useCallback((e: MessageEvent) => {
    try {
      const event = JSON.parse(e.data) as SensorState;
      setSensorStates(prev => ({ ...prev, [event.source_id]: event }));
      setLastUpdated(new Date());
    } catch {/* ignore malformed */}
  }, []);

  const handleAlert = useCallback((e: MessageEvent) => {
    try {
      const alert = JSON.parse(e.data) as Alert;
      setRecentAlerts(prev => [alert, ...prev].slice(0, MAX_ALERTS));
      setLastUpdated(new Date());
    } catch {/* ignore malformed */}
  }, []);

  useEffect(() => {
    let cancelled = false;

    function connect() {
      if (cancelled) return;

      const es = new EventSource(SSE_URL);
      esRef.current = es;

      es.onopen = () => setConnected(true);

      // Named event listeners (sse-starlette sends `event: <type>` lines)
      es.addEventListener("sensor_update", handleSensorUpdate);
      es.addEventListener("alert",         handleAlert);

      es.onerror = () => {
        setConnected(false);
        es.close();
        esRef.current = null;
        if (!cancelled) {
          retryRef.current = setTimeout(connect, RETRY_MS);
        }
      };
    }

    connect();

    return () => {
      cancelled = true;
      if (retryRef.current) clearTimeout(retryRef.current);
      if (esRef.current) {
        esRef.current.removeEventListener("sensor_update", handleSensorUpdate);
        esRef.current.removeEventListener("alert",         handleAlert);
        esRef.current.close();
        esRef.current = null;
      }
      setConnected(false);
    };
  }, [handleSensorUpdate, handleAlert]);

  return { sensorStates, recentAlerts, connected, lastUpdated };
}

// ── Legacy generic overload ───────────────────────────────────────────────────
// Kept so old call-sites that pass (url, callback) still compile without errors.
// New code should use the zero-argument form above.
export function useSSELegacy(url: string, onMessage: (data: string) => void): void {
  const cbRef = useRef(onMessage);
  cbRef.current = onMessage;

  useEffect(() => {
    let retryTimeout: ReturnType<typeof setTimeout>;
    let es: EventSource;

    function connect() {
      es = new EventSource(url);
      es.onmessage = (e) => cbRef.current(e.data);
      es.onerror   = () => { es.close(); retryTimeout = setTimeout(connect, RETRY_MS); };
    }

    connect();
    return () => { clearTimeout(retryTimeout); es?.close(); };
  }, [url]);
}
