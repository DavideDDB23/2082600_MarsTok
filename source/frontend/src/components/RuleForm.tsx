/**
 * RuleForm.tsx — Create / edit a rule.
 */
import { useEffect, useState } from "react";
import type { Rule } from "../types";

const OPERATORS: { value: string; label: string }[] = [
  { value: "gt",  label: ">"  },
  { value: "lt",  label: "<"  },
  { value: "gte", label: ">=" },
  { value: "lte", label: "<=" },
  { value: "eq",  label: "="  },
  { value: "neq", label: "!=" },
];

const EMPTY_RULE: Rule = {
  name:      "",
  enabled:   true,
  condition: { source_id: "", metric: "", operator: "gt", threshold: 0 },
  action:    { actuator_name: "", state: "ON" },
};

interface Props {
  initial?: Rule | null;
  onSave:   (rule: Rule) => void;
  onCancel: () => void;
}

export function RuleForm({ initial, onSave, onCancel }: Props) {
  const [form, setForm] = useState<Rule>(initial ?? EMPTY_RULE);

  useEffect(() => {
    setForm(initial ?? EMPTY_RULE);
  }, [initial]);

  const set = (path: string, value: unknown) => {
    setForm((prev) => {
      const next = structuredClone(prev);
      const keys = path.split(".");
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      let node: any = next;
      for (let i = 0; i < keys.length - 1; i++) node = node[keys[i]];
      node[keys[keys.length - 1]] = value;
      return next;
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(form);
  };

  return (
    <form onSubmit={handleSubmit} className="card space-y-4 max-w-xl">
      <h3 className="text-sm font-semibold text-white">
        {initial?.id ? "Edit Rule" : "New Rule"}
      </h3>

      {/* Rule name */}
      <div>
        <label className="label">Rule name</label>
        <input
          className="input"
          value={form.name}
          onChange={(e) => set("name", e.target.value)}
          placeholder="e.g. High CO₂ alert"
          required
        />
      </div>

      {/* Condition */}
      <fieldset className="border border-gray-800 rounded-lg p-3 space-y-3">
        <legend className="text-xs text-gray-400 px-1">Condition</legend>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Source ID</label>
            <input
              className="input"
              value={form.condition.source_id}
              onChange={(e) => set("condition.source_id", e.target.value)}
              placeholder="co2_hall"
              required
            />
          </div>
          <div>
            <label className="label">Metric</label>
            <input
              className="input"
              value={form.condition.metric}
              onChange={(e) => set("condition.metric", e.target.value)}
              placeholder="value"
              required
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Operator</label>
            <select
              className="input"
              value={form.condition.operator}
              onChange={(e) => set("condition.operator", e.target.value)}
            >
              {OPERATORS.map((op) => (
                <option key={op.value} value={op.value}>{op.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Threshold</label>
            <input
              type="number"
              step="any"
              className="input"
              value={form.condition.threshold}
              onChange={(e) => set("condition.threshold", parseFloat(e.target.value))}
              required
            />
          </div>
        </div>
      </fieldset>

      {/* Action */}
      <fieldset className="border border-gray-800 rounded-lg p-3 space-y-3">
        <legend className="text-xs text-gray-400 px-1">Action</legend>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Actuator name</label>
            <input
              className="input"
              value={form.action.actuator_name}
              onChange={(e) => set("action.actuator_name", e.target.value)}
              placeholder="cooling_fan"
              required
            />
          </div>
          <div>
            <label className="label">State</label>
            <select
              className="input"
              value={form.action.state}
              onChange={(e) => set("action.state", e.target.value)}
            >
              <option value="ON">ON</option>
              <option value="OFF">OFF</option>
            </select>
          </div>
        </div>
      </fieldset>

      {/* Enable toggle */}
      <label className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          checked={form.enabled}
          onChange={(e) => set("enabled", e.target.checked)}
          className="w-4 h-4 accent-mars-500"
        />
        <span className="text-sm text-gray-300">Enabled</span>
      </label>

      {/* Buttons */}
      <div className="flex gap-2 justify-end pt-1">
        <button type="button" onClick={onCancel} className="btn-secondary">
          Cancel
        </button>
        <button type="submit" className="btn-primary">
          {initial?.id ? "Save changes" : "Create rule"}
        </button>
      </div>
    </form>
  );
}
