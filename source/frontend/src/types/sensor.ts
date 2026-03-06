/**
 * types/sensor.ts — Sensor state types as specified in TASKS.md (Developer D).
 *
 * `SensorState` is the frontend representation of the backend `InternalEvent`.
 * `Metric` mirrors `MetricReading` from shared/schemas.py.
 */

export interface Metric {
  name:  string;
  value: number;
  unit:  string;
}

export interface SensorState {
  event_id:     string;
  timestamp:    string;
  source_id:    string;
  source_type:  "rest_sensor" | "telemetry_topic";
  category:     "environment" | "power" | "life_support" | "airlock" | "thermal";
  metrics:      Metric[];
  status:       "ok" | "warning" | null;
  raw_schema:   string;
  extra_fields: Record<string, unknown>;
}

/** Keyed by source_id — the full live-state map returned by GET /api/state */
export type StateMap = Record<string, SensorState>;
