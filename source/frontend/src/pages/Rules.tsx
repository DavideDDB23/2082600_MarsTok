/**
 * Rules.tsx — CRUD interface for automation rules.
 */
import { useCallback, useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { RuleForm } from "../components/RuleForm";
import { RuleTable } from "../components/RuleTable";
import { createRule, deleteRule, getRules, toggleRule, updateRule } from "../api";
import type { Rule } from "../types";

export default function Rules() {
  const [rules,   setRules]   = useState<Rule[]>([]);
  const [editing, setEditing] = useState<Rule | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [error,   setError]   = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setRules(await getRules());
      setError(null);
    } catch (e) {
      setError(String(e));
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const handleSave = async (rule: Rule) => {
    try {
      if (rule.id != null) {
        await updateRule(rule.id, rule);
      } else {
        await createRule(rule);
      }
      setEditing(null);
      setShowForm(false);
      await refresh();
    } catch (e) {
      setError(String(e));
    }
  };

  const handleToggle = async (id: string) => {
    try {
      await toggleRule(id);   // hits PATCH /rules/{id}/toggle — flips enabled
      await refresh();
    } catch (e) { setError(String(e)); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this rule?")) return;
    try {
      await deleteRule(id);
      await refresh();
    } catch (e) { setError(String(e)); }
  };

  const handleEdit = (rule: Rule) => {
    setEditing(rule);
    setShowForm(true);
  };

  const handleCancel = () => {
    setEditing(null);
    setShowForm(false);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-white mb-1">Rules</h1>
          <p className="text-sm text-gray-400">Automation rules: condition → actuator action.</p>
        </div>
        {!showForm && (
          <button
            onClick={() => { setEditing(null); setShowForm(true); }}
            className="btn-primary flex items-center gap-2"
          >
            <Plus size={14} /> New Rule
          </button>
        )}
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-950 border border-red-800 rounded-lg text-red-300 text-sm">
          {error}
        </div>
      )}

      {showForm && (
        <div className="mb-6">
          <RuleForm
            initial={editing}
            onSave={handleSave}
            onCancel={handleCancel}
          />
        </div>
      )}

      <RuleTable
        rules={rules}
        onToggle={handleToggle}
        onDelete={handleDelete}
        onEdit={handleEdit}
      />
    </div>
  );
}
