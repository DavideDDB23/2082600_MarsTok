/**
 * Alerts.tsx — Alert history with live SSE updates for new alerts.
 *
 * Historical pages come from GET /api/alerts (REST).
 * New alerts are delivered via the SSE context in App.tsx.
 */
import { useCallback, useEffect, useRef, useState } from "react";
import { AlertTimeline } from "../components/AlertTimeline";
import { useLiveData } from "../App";
import { deleteAlert, getAlerts } from "../api";
import type { Alert } from "../types";

const PAGE_SIZE = 50;

export default function Alerts() {
  const { recentAlerts } = useLiveData();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [total,  setTotal]  = useState(0);
  const [skip,   setSkip]   = useState(0);
  const [error,  setError]  = useState<string | null>(null);

  // Track which alert ids we've already added to avoid duplicates when
  // a live SSE alert also appears in the paginated REST response.
  const seenRef = useRef<Set<string>>(new Set());

  const refresh = useCallback(async (offset = skip) => {
    try {
      const page = await getAlerts({ skip: offset, limit: PAGE_SIZE });
      seenRef.current = new Set(page.items.map((a) => a.id));
      setAlerts(page.items);
      setTotal(page.total);
      setError(null);
    } catch (e) {
      setError(String(e));
    }
  }, [skip]);

  useEffect(() => { refresh(); }, [refresh]);

  // Merge live SSE alerts (prepend only new ones we haven't seen yet).
  useEffect(() => {
    const newOnes = recentAlerts.filter((a) => !seenRef.current.has(a.id));
    if (newOnes.length === 0) return;
    newOnes.forEach((a) => seenRef.current.add(a.id));
    setAlerts((prev) => [...newOnes, ...prev]);
    setTotal((t) => t + newOnes.length);
  }, [recentAlerts]);

  const handleDelete = async (id: string) => {
    try {
      await deleteAlert(id);
      seenRef.current.delete(id);
      setAlerts((prev) => prev.filter((a) => a.id !== id));
      setTotal((t) => Math.max(0, t - 1));
    } catch (e) {
      setError(String(e));
    }
  };

  const prevPage = () => {
    const next = Math.max(0, skip - PAGE_SIZE);
    setSkip(next);
    refresh(next);
  };

  const nextPage = () => {
    const next = skip + PAGE_SIZE;
    setSkip(next);
    refresh(next);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-white mb-1">Alerts</h1>
          <p className="text-sm text-gray-400">
            {total} alert{total !== 1 ? "s" : ""} total — new alerts appear live.
          </p>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-950 border border-red-800 rounded-lg text-red-300 text-sm">
          {error}
        </div>
      )}

      <AlertTimeline alerts={alerts} onDelete={handleDelete} />

      {/* Pagination */}
      {total > PAGE_SIZE && (
        <div className="flex items-center justify-between mt-6">
          <button
            onClick={prevPage}
            disabled={skip === 0}
            className="btn-secondary disabled:opacity-40"
          >
            ← Previous
          </button>
          <span className="text-xs text-gray-500">
            {skip + 1}–{Math.min(skip + PAGE_SIZE, total)} of {total}
          </span>
          <button
            onClick={nextPage}
            disabled={skip + PAGE_SIZE >= total}
            className="btn-secondary disabled:opacity-40"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
