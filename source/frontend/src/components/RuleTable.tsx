/**
 * RuleTable.tsx — Table listing all rules with toggle + delete actions.
 */
import { Trash2 } from "lucide-react";
import type { Rule } from "../types";

const OPERATOR_SYMBOLS: Record<string, string> = {
  gt:  ">",
  lt:  "<",
  gte: ">=",
  lte: "<=",
  eq:  "=",
  neq: "!=",
};

interface Props {
  rules:    Rule[];
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  onEdit:   (rule: Rule) => void;
}

export function RuleTable({ rules, onToggle, onDelete, onEdit }: Props) {
  if (rules.length === 0) {
    return (
      <p className="text-gray-500 text-sm text-center py-8">
        No rules defined yet. Create one below.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-gray-800">
      <table className="w-full text-sm">
        <thead className="bg-gray-900 text-gray-400 text-xs uppercase">
          <tr>
            <th className="px-4 py-3 text-left">Name</th>
            <th className="px-4 py-3 text-left">Condition</th>
            <th className="px-4 py-3 text-left">Action</th>
            <th className="px-4 py-3 text-center">Enabled</th>
            <th className="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-800">
          {rules.map((rule) => (
            <tr
              key={rule.id}
              className="bg-gray-950 hover:bg-gray-900 transition-colors"
            >
              <td className="px-4 py-3 font-medium text-white">{rule.name}</td>
              <td className="px-4 py-3 text-gray-400 font-mono text-xs">
                {rule.condition.source_id} · {rule.condition.metric}{" "}
                <span className="text-mars-400">{OPERATOR_SYMBOLS[rule.condition.operator] ?? rule.condition.operator}</span>{" "}
                {rule.condition.threshold}
              </td>
              <td className="px-4 py-3 text-gray-400 text-xs">
                {rule.action.actuator_name} →{" "}
                <span
                  className={rule.action.state === "ON" ? "text-green-400" : "text-red-400"}
                >
                  {rule.action.state}
                </span>
              </td>
              <td className="px-4 py-3 text-center">
                <button
                  onClick={() => onToggle(rule.id!)}
                  className={`w-10 h-5 rounded-full transition-colors ${
                    rule.enabled ? "bg-green-600" : "bg-gray-700"
                  }`}
                  title={rule.enabled ? "Click to disable" : "Click to enable"}
                >
                  <span className="sr-only">{rule.enabled ? "Enabled" : "Disabled"}</span>
                </button>
              </td>
              <td className="px-4 py-3 text-right">
                <div className="flex items-center justify-end gap-2">
                  <button
                    onClick={() => onEdit(rule)}
                    className="btn-secondary btn text-xs"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => onDelete(rule.id!)}
                    className="text-gray-500 hover:text-red-400 transition-colors p-1"
                    title="Delete rule"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
