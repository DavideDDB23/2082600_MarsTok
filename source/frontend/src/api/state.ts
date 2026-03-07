/**
 * api/state.ts — Sensor-state endpoints.
 *
 * GET /api/state           → full StateMap (all source_ids)
 * GET /api/state/{id}      → single SensorState
 */

import { get } from "./client";
import type { StateMap, SensorState } from "../types/sensor";

export const fetchAllState = (): Promise<StateMap> =>
  get<StateMap>("/state/");

export const fetchState = (sourceId: string): Promise<SensorState> =>
  get<SensorState>(`/state/${encodeURIComponent(sourceId)}`);
