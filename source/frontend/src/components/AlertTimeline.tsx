/**
 * AlertTimeline.tsx — Scrollable list of alerts, newest first.
 * Accepts an optional `live` prop to append incoming SSE alerts at the top.
 */
import { Bell, Trash2 } from "lucide-react";
import type { Alert } from "../types";

interface Props {
  alerts:   Alert[];
  onDelete: (id: string) => void;
}

export function AlertTimeline({ alerts, onDelete }: Props) {
  if (alerts.length === 0) {
    return (
      <p className="text-gray-500 text-sm text-center py-8">
        No alerts yet. Rules will create alerts here when they fire.
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className="card flex items-start gap-3 border-l-4 border-l-mars-500"
        >
          <Bell size={16} className="text-mars-400 mt-0.5 shrink-0" />

          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2">
              <p className="text-sm font-medium text-white truncate">
                {alert.rule_name}
              </p>
              <time className="text-[10px] text-gray-500 shrink-0">
                {new Date(alert.triggered_at).toLocaleString()}
              </time>
            </div>
            <p className="text-xs text-gray-400 mt-0.5">
              Source:{" "}
              <span className="font-mono text-gray-300">
                {alert.triggered_event.source_id}
              </span>
              {alert.triggered_event.metrics.length > 0 && (
                <span className="ml-2">
                  {alert.triggered_event.metrics.map((m) => (
                    <span key={m.name} className="mr-2">
                      {m.name}={m.value.toFixed(2)} {m.unit}
                    </span>
                  ))}
                </span>
              )}
            </p>
          </div>

          <button
            onClick={() => onDelete(alert.id)}
            className="text-gray-600 hover:text-red-400 transition-colors shrink-0"
            title="Dismiss alert"
          >
            <Trash2 size={13} />
          </button>
        </div>
      ))}
    </div>
  );
}
