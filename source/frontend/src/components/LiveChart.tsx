/**
 * LiveChart.tsx — Real-time line chart for a single metric using Recharts.
 *
 * Reads from the SSE context (App.tsx) — no local EventSource needed.
 * Keeps the last MAX_POINTS data points in a rolling buffer.
 */
import { useEffect, useRef, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useLiveData } from "../App";

interface Props {
  sourceId:   string;   // which source_id to track
  metricName: string;   // which metric within the event to plot
  color?:     string;   // line colour (default: #ff6b2b)
  maxPoints?: number;   // rolling window size (default: 60)
  title?:     string;
}

interface Point {
  t:     string;   // formatted time label
  value: number;
}

const MAX_DEFAULT = 60;

export function LiveChart({
  sourceId,
  metricName,
  color = "#ff6b2b",
  maxPoints = MAX_DEFAULT,
  title,
}: Props) {
  const { sensorStates } = useLiveData();
  const [points, setPoints] = useState<Point[]>([]);
  const maxRef = useRef(maxPoints);
  maxRef.current = maxPoints;

  // Watch the specific sensor and append a new point whenever it changes.
  const event = sensorStates[sourceId];
  useEffect(() => {
    if (!event) return;
    const metric = event.metrics.find((m) => m.name === metricName);
    if (!metric) return;
    const label = new Date(event.timestamp).toLocaleTimeString();
    setPoints((prev) => {
      const next = [...prev, { t: label, value: metric.value }];
      return next.length > maxRef.current
        ? next.slice(next.length - maxRef.current)
        : next;
    });
    // `event` reference changes on every new SSE message for this sourceId
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [event]);

  return (
    <div className="card">
      {title && (
        <p className="text-xs font-medium text-gray-400 mb-3">{title}</p>
      )}
      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={points}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey="t"
            tick={{ fontSize: 10, fill: "#6b7280" }}
            interval="preserveStartEnd"
          />
          <YAxis tick={{ fontSize: 10, fill: "#6b7280" }} width={40} />
          <Tooltip
            contentStyle={{ background: "#111827", border: "1px solid #374151" }}
            labelStyle={{ color: "#9ca3af" }}
            itemStyle={{ color: "#f3f4f6" }}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            dot={false}
            strokeWidth={2}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
