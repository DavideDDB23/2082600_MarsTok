/**
 * types/index.ts — Barrel re-export for backward compatibility.
 *
 * All types now live in the dedicated sub-modules:
 *   types/sensor.ts  — Metric, SensorState, StateMap
 *   types/rule.ts    — Operator, RuleCondition, RuleAction, Rule
 *   types/alert.ts   — Alert
 *
 * This file re-exports everything so existing imports of "@/types" keep working.
 */

export type { Metric, SensorState, StateMap } from "./sensor";
export type { Operator, RuleCondition, RuleAction, Rule } from "./rule";
export type { Alert } from "./alert";

// ── Legacy / convenience aliases ─────────────────────────────────────────────

/** "InternalEvent" was the old name for SensorState. Kept for backward compat. */
export type { SensorState as InternalEvent } from "./sensor";

/** MetricReading → Metric alias kept for backward compat. */
export type { Metric as MetricReading } from "./sensor";

/** Convenience: category / source-type literal unions. */
export type SourceType = "rest_sensor" | "telemetry_topic";
export type Category   = "environment" | "power" | "life_support" | "airlock" | "thermal";

/** Actuator snapshot returned by GET /api/actuators */
export interface ActuatorsResponse {
  actuators: Record<string, "ON" | "OFF">;
}

/** Paginated alerts response from GET /api/alerts */
export interface AlertsPage {
  total: number;
  skip:  number;
  limit: number;
  items: import("./alert").Alert[];
}
