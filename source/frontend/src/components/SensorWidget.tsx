/**
 * SensorWidget.tsx — Compact card showing the latest reading for one sensor.
 */
import type { InternalEvent } from "../types";
import StatusBadge from "./sensors/StatusBadge";

interface Props {
  event: InternalEvent;
}

export function SensorWidget({ event }: Props) {
  const ts = new Date(event.timestamp).toLocaleTimeString();

  return (
    <div className="card flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-mono text-gray-400 truncate">{event.source_id}</span>
        <StatusBadge status={event.status} size="xs" />
      </div>

      <div className="space-y-1">
        {event.metrics.map((m) => (
          <div key={m.name} className="flex items-baseline justify-between">
            <span className="text-xs text-gray-500 truncate">{m.name}</span>
            <span className="text-lg font-semibold text-white ml-2">
              {m.value.toFixed(2)}
              <span className="text-xs text-gray-400 ml-1">{m.unit}</span>
            </span>
          </div>
        ))}
      </div>

      <p className="text-[10px] text-gray-600 mt-auto">{ts}</p>
    </div>
  );
}
