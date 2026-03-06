/**
 * api/alerts.ts — Alert history endpoints.
 *
 * GET    /api/alerts           → AlertsPage (supports ?rule_id, ?source_id, ?skip, ?limit)
 * DELETE /api/alerts/{id}      → 204
 */

import { get, del } from "./client";
import type { Alert, AlertsPage } from "../types";

export interface AlertsParams {
  rule_id?:   string;
  source_id?: string;
  skip?:      number;
  limit?:     number;
}

export const fetchAlerts = (params: AlertsParams = {}): Promise<AlertsPage> => {
  const qs = new URLSearchParams();
  if (params.rule_id   != null)  qs.set("rule_id",   params.rule_id);
  if (params.source_id != null)  qs.set("source_id", params.source_id);
  if (params.skip      != null)  qs.set("skip",      String(params.skip));
  if (params.limit     != null)  qs.set("limit",     String(params.limit));
  const suffix = qs.toString() ? `?${qs}` : "";
  return get<AlertsPage>(`/alerts${suffix}`);
};

export const fetchAlert = (id: string): Promise<Alert> =>
  get<Alert>(`/alerts/${id}`);

export const deleteAlert = (id: string): Promise<void> =>
  del(`/alerts/${id}`);
