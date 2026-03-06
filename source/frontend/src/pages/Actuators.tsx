/**
 * Actuators.tsx — List and control all simulator actuators.
 */
import { ActuatorCard } from "../components/ActuatorCard";
import { useActuators } from "../hooks/useActuators";

export default function Actuators() {
  const { actuators, loading, error, toggle } = useActuators();

  const entries = Object.entries(actuators).sort(([a], [b]) => a.localeCompare(b));

  return (
    <div>
      <h1 className="text-xl font-bold text-white mb-1">Actuators</h1>
      <p className="text-sm text-gray-400 mb-6">
        Control habitat actuators. State is refreshed every 5 s.
      </p>

      {loading && <p className="text-gray-500 text-sm">Loading actuators...</p>}
      {error   && <p className="text-red-400 text-sm">{error}</p>}

      {!loading && entries.length === 0 && (
        <p className="text-gray-500 text-sm">
          No actuators found. Is the Simulator running?
        </p>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {entries.map(([name, state]) => (
          <ActuatorCard key={name} name={name} state={state} onToggle={toggle} />
        ))}
      </div>
    </div>
  );
}
