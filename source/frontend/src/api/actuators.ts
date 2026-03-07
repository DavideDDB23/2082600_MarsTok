/**
 * api/actuators.ts — Actuator endpoints.
 *
 * GET   /api/actuators            → { actuators: Record<string, "ON"|"OFF"> }
 * POST  /api/actuators/{name}     → { actuator, state, updated_at }
 */

import { get, post } from "./client";
import type { ActuatorsResponse } from "../types";

export interface SetActuatorResponse {
  actuator:   string;
  state:      "ON" | "OFF";
  updated_at: string;
}

export const fetchActuators = (): Promise<ActuatorsResponse> =>
  get<ActuatorsResponse>("/actuators/");

export const setActuator = (
  name:  string,
  state: "ON" | "OFF",
): Promise<SetActuatorResponse> =>
  post<SetActuatorResponse>(`/actuators/${encodeURIComponent(name)}`, { state });
