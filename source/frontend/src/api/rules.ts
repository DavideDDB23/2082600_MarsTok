/**
 * api/rules.ts — Automation-rule CRUD endpoints.
 *
 * GET    /api/rules           → Rule[]
 * POST   /api/rules           → Rule
 * GET    /api/rules/{id}      → Rule
 * PUT    /api/rules/{id}      → Rule
 * PATCH  /api/rules/{id}      → Rule (set enabled explicitly)
 * PATCH  /api/rules/{id}/toggle → Rule (flip enabled)
 * DELETE /api/rules/{id}      → 204
 */

import { get, post, put, patch, del } from "./client";
import type { Rule } from "../types/rule";

export const fetchRules = (): Promise<Rule[]> =>
  get<Rule[]>("/rules");

export const fetchRule = (id: string): Promise<Rule> =>
  get<Rule>(`/rules/${id}`);

export const createRule = (
  data: Omit<Rule, "id" | "created_at" | "updated_at">,
): Promise<Rule> =>
  post<Rule>("/rules", data);

export const updateRule = (id: string, data: Partial<Rule>): Promise<Rule> =>
  put<Rule>(`/rules/${id}`, data);

export const setRuleEnabled = (id: string, enabled: boolean): Promise<Rule> =>
  patch<Rule>(`/rules/${id}`, { enabled });

/** Toggle the enabled flag without specifying a value. */
export const toggleRule = (id: string): Promise<Rule> =>
  patch<Rule>(`/rules/${id}/toggle`);

export const deleteRule = (id: string): Promise<void> =>
  del(`/rules/${id}`);
