/**
 * api/index.ts — Barrel re-export for backward compatibility.
 *
 * All API logic now lives in dedicated sub-modules:
 *   api/client.ts     — low-level get/post/put/patch/del helpers
 *   api/state.ts      — fetchAllState, fetchState
 *   api/actuators.ts  — fetchActuators, setActuator
 *   api/rules.ts      — fetchRules, createRule, updateRule, toggleRule, deleteRule
 *   api/alerts.ts     — fetchAlerts, deleteAlert
 *
 * This file re-exports everything so existing `import { … } from "../api"` keep working.
 */

// ── Core helpers ──────────────────────────────────────────────────────────────
export { get, post, put, patch, del } from "./client";

// ── State ─────────────────────────────────────────────────────────────────────
export { fetchAllState, fetchState } from "./state";

// ── Actuators ─────────────────────────────────────────────────────────────────
export { fetchActuators, setActuator } from "./actuators";
export type { SetActuatorResponse } from "./actuators";

// ── Rules ─────────────────────────────────────────────────────────────────────
export {
  fetchRules,
  fetchRule,
  createRule,
  updateRule,
  setRuleEnabled,
  toggleRule,
  deleteRule,
} from "./rules";

// ── Alerts ────────────────────────────────────────────────────────────────────
export { fetchAlerts, fetchAlert, deleteAlert } from "./alerts";
export type { AlertsParams } from "./alerts";

// ── Legacy name aliases (old api/index.ts exports) ───────────────────────────
export { fetchAllState as getState }    from "./state";
export { fetchState    as getOneState } from "./state";
export { fetchActuators as getActuators } from "./actuators";
export { fetchRules    as getRules }    from "./rules";
export { fetchRule     as getRule }     from "./rules";
export { fetchAlerts   as getAlerts }   from "./alerts";
