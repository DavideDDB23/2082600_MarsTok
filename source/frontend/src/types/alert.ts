/**
 * types/alert.ts — Alert type.
 *
 * Mirrors `AlertSchema` from shared/schemas.py.
 * `triggered_event` is the full `SensorState` snapshot at the time the rule fired.
 */

import type { SensorState } from "./sensor";

export interface Alert {
  id:              string;
  rule_id:         string;
  rule_name:       string;
  triggered_event: SensorState;
  triggered_at:    string;
}
