/**
 * types/rule.ts — Rule / automation types.
 *
 * Mirrors `RuleSchema`, `RuleCondition`, `RuleAction` from shared/schemas.py.
 */

export type Operator = "gt" | "lt" | "gte" | "lte" | "eq" | "neq";

export interface RuleCondition {
  source_id: string;
  metric:    string;
  operator:  Operator;
  threshold: number;
}

export interface RuleAction {
  actuator_name: string;
  state:         string;  // "ON" | "OFF"
}

export interface Rule {
  id?:       string;
  name:      string;
  enabled:   boolean;
  condition: RuleCondition;
  action:    RuleAction;
  created_at?: string;
  updated_at?: string;
}
