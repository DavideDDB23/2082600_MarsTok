/**
 * AirlockThermal.tsx — Airlock and Thermal Loop telemetry.
 *
 * Live data comes from the SSE context in App.tsx.
 */
import { useLiveData } from "../App";
import { LiveChart } from "../components/LiveChart";
import { SensorWidget } from "../components/SensorWidget";

const SOURCES = ["mars/telemetry/airlock", "mars/telemetry/thermal_loop"];

const CHARTS = [
  { id: "mars/telemetry/airlock",      metric: "cycles_per_hour", label: "Airlock — Cycles/Hour",        color: "#34d399" },
  { id: "mars/telemetry/thermal_loop", metric: "temperature_c",   label: "Thermal Loop — Temperature °C", color: "#fb923c" },
  { id: "mars/telemetry/thermal_loop", metric: "flow_l_min",      label: "Thermal Loop — Flow (L/min)",   color: "#60a5fa" },
];

export default function AirlockThermal() {
  const { sensorStates } = useLiveData();

  return (
    <div>
      <h1 className="text-xl font-bold text-white mb-1">Airlock & Thermal</h1>
      <p className="text-sm text-gray-400 mb-6">Real-time airlock cycle and thermal loop monitoring.</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
        {SOURCES.map((id) =>
          sensorStates[id] ? (
            <SensorWidget key={id} event={sensorStates[id]} />
          ) : (
            <div key={id} className="card text-xs text-gray-600 font-mono">{id}<br /><span className="text-gray-700">waiting...</span></div>
          ),
        )}
      </div>

      <h2 className="text-sm font-semibold text-gray-300 mb-3">Live Trends</h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {CHARTS.map((c) => (
          <LiveChart
            key={`${c.id}-${c.metric}`}
            sourceId={c.id}
            metricName={c.metric}
            color={c.color}
            title={c.label}
          />
        ))}
      </div>
    </div>
  );
}
