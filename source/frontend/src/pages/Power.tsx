/**
 * Power.tsx — Live power metrics: solar array, power bus, consumption.
 */
import { LiveChart } from "../components/LiveChart";

const POWER_SOURCES = [
  { id: "mars/telemetry/solar_array",       metric: "power_kw",  label: "Solar Array — Power (kW)",       color: "#facc15" },
  { id: "mars/telemetry/solar_array",       metric: "voltage_v", label: "Solar Array — Voltage (V)",      color: "#fb923c" },
  { id: "mars/telemetry/power_bus",         metric: "power_kw",  label: "Power Bus — Power (kW)",         color: "#34d399" },
  { id: "mars/telemetry/power_bus",         metric: "current_a", label: "Power Bus — Current (A)",        color: "#60a5fa" },
  { id: "mars/telemetry/power_consumption", metric: "power_kw",  label: "Consumption — Power (kW)",       color: "#f87171" },
  { id: "mars/telemetry/power_consumption", metric: "cumulative_kwh", label: "Consumption — Cumulative (kWh)", color: "#c084fc" },
];

export default function Power() {
  return (
    <div>
      <h1 className="text-xl font-bold text-white mb-1">Power</h1>
      <p className="text-sm text-gray-400 mb-6">
        Live charts for solar array, power bus and consumption telemetry.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {POWER_SOURCES.map((s) => (
          <LiveChart
            key={`${s.id}-${s.metric}`}
            sourceId={s.id}
            metricName={s.metric}
            color={s.color}
            title={s.label}
          />
        ))}
      </div>
    </div>
  );
}
