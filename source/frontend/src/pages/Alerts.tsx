/**
 * Alerts.tsx — Alert history with live SSE updates for new alerts.
 *
 * Historical pages come from GET /api/alerts (REST).
 * New alerts are delivered via the SSE context in App.tsx.
 * US20: filter bar (dropdowns) lets operators filter by rule or source.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { AlertTimeline } from "../components/AlertTimeline";
import { useLiveData } from "../App";
import { deleteAlert, getAlerts, fetchRules } from "../api";
import type { Alert } from "../types";
import type { Rule } from "../types/rule";

const PAGE_SIZE = 50;

export default function Alerts() {
  const { recentAlerts, sensorStates } = useLiveData();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [total,  setTotal]  = useState(0);
  const [offset, setOffset] = useState(0);
  const [error,  setError]  = useState<string | null>(null);

  // ── Dropdown option lists ────────────────────────────────────────────────
  const [rules, setRules] = useState<Rule[]>([]);
  useEffect(() => {
    fetchRules().then(setRules).catch(() => {/* ignore — dropdowns just stay empty */});
  }, []);

  const sourceIds = useMemo(
    () => Object.keys(sensorStates).sort(),
    [sensorStates],
  );

  // ── US20: filter state ───────────────────────────────────────────────────
  const [filterRuleId,   setFilterRuleId]   = useState("");
  const [filterSourceId, setFilterSourceId] = useState("");

  // Track which alert ids we've already added to avoid duplicates when
  // a live SSE alert also appears in the paginated REST response.
  const seenRef = useRef<Set<string>>(new Set());

  const refresh = useCallback(async (off = offset) => {
    try {
      const page = await getAlerts({
        offset:    off,
        limit:     PAGE_SIZE,
        rule_id:   filterRuleId   || undefined,
        source_id: filterSourceId || undefined,
      });
      seenRef.current = new Set(page.items.map((a) => a.id));
      setAlerts(page.items);
      setTotal(page.total);
      setError(null);
    } catch (e) {
      setError(String(e));
    }
  }, [offset, filterRuleId, filterSourceId]);

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

  // Changing a dropdown resets to page 0; React 18 batches the two setStates
  // so `refresh` re-runs once with both new values via the useEffect above.
  const handleRuleChange = (val: string) => {
    setFilterRuleId(val);
    setOffset(0);
  };

  const handleSourceChange = (val: string) => {
    setFilterSourceId(val);
    setOffset(0);
  };

  const clearFilters = () => {
    setFilterRuleId("");
    setFilterSourceId("");
    setOffset(0);
  };

  const prevPage = () => {
    const next = Math.max(0, offset - PAGE_SIZE);
    setOffset(next);
    refresh(next);
  };

  const nextPage = () => {
    const next = offset + PAGE_SIZE;
    setOffset(next);
    refresh(next);
  };

  const isFiltered = filterRuleId !== "" || filterSourceId !== "";

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

      {/* ── US20: Filter bar (dropdowns) ─────────────────────────────────────── */}
      <div className="flex flex-wrap gap-3 items-end mb-6 p-4 bg-gray-900 border border-gray-800 rounded-xl">
        {/* Rule dropdown */}
        <div className="flex flex-col gap-1">
          <label className="text-xs text-gray-400">Rule</label>
          <select
            className="input w-56"
            value={filterRuleId}
            onChange={(e) => handleRuleChange(e.target.value)}
          >
            <option value="">All rules</option>
            {rules.map((r) => (
              <option key={r.id} value={r.id!}>
                {r.name}
              </option>
            ))}
          </select>
        </div>

        {/* Source ID dropdown */}
        <div className="flex flex-col gap-1">
          <label className="text-xs text-gray-400">Source</label>
          <select
            className="input w-56"
            value={filterSourceId}
            onChange={(e) => handleSourceChange(e.target.value)}
          >
            <option value="">All sources</option>
            {sourceIds.map((id) => (
              <option key={id} value={id}>{id}</option>
            ))}
          </select>
        </div>

        {isFiltered && (
          <button type="button" onClick={clearFilters} className="btn-secondary self-end">
            Clear filters
          </button>
        )}
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
            disabled={offset === 0}
            className="btn-secondary disabled:opacity-40"
          >
            ← Previous
          </button>
          <span className="text-xs text-gray-500">
            {offset + 1}–{Math.min(offset + PAGE_SIZE, total)} of {total}
          </span>
          <button
            onClick={nextPage}
            disabled={offset + PAGE_SIZE >= total}
            className="btn-secondary disabled:opacity-40"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}

