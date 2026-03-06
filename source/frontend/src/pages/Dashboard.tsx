/**
 * Dashboard.tsx — Overview of all live sensor states.
 *
 * Reads from the SSE context established in App.tsx — no local polling needed.
 */
import { useLiveData } from "../App";
import { SensorWidget } from "../components/SensorWidget";

export default function Dashboard() {
  const { sensorStates, connected } = useLiveData();

  const events = Object.values(sensorStates).sort((a, b) =>
    a.source_id.localeCompare(b.source_id),
  );

  return (
    <div>
      <h1 className="text-xl font-bold text-white mb-1">Dashboard</h1>
      <p className="text-sm text-gray-400 mb-6">
        Live sensor readings — {events.length} source{events.length !== 1 ? "s" : ""}
      </p>

      {!connected && events.length === 0 && (
        <p className="text-gray-500 text-sm">
          Connecting to live stream… make sure the Collector is running.
        </p>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {events.map((ev) => (
          <SensorWidget key={ev.source_id} event={ev} />
        ))}
      </div>
    </div>
  );
}
