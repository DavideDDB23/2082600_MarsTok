/**
 * AirlockThermal.tsx — Airlock and Thermal Loop telemetry.
 *
 * Live data comes from the SSE context in App.tsx.
 * US8: Displays airlock state (IDLE / PRESSURIZING / DEPRESSURIZING) and
 *      cycles-per-hour so operators can track EVA activity.
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

/** Badge colour per airlock state */
function airlockStateColor(state: string | undefined): string {
  if (state === "PRESSURIZING")   return "bg-yellow-500 text-black";
  if (state === "DEPRESSURIZING") return "bg-orange-500 text-black";
  return "bg-green-700 text-white"; // IDLE or unknown
}

export default function AirlockThermal() {
  const { sensorStates } = useLiveData();
  const airlockEvent = sensorStates["mars/telemetry/airlock"];
  // last_state is stored in extra_fields by the normalizer (topic.airlock.v1)
  const lastState = airlockEvent?.extra_fields?.last_state as string | undefined;

  return (
    <div>
      <h1 className="text-xl font-bold text-white mb-1">Airlock &amp; Thermal</h1>
      <p className="text-sm text-gray-400 mb-6">Real-time airlock cycle and thermal loop monitoring.</p>

      {/* ── Airlock state badge (US8) ─────────────────────────────────────── */}
      {airlockEvent && (
        <div className="card flex items-center gap-4 mb-6">
          <div>
            <p className="text-xs text-gray-400 mb-1">Airlock State</p>
            <span
              className={`inline-block px-3 py-1 rounded-full text-sm font-semibold tracking-wide ${airlockStateColor(lastState)}`}
            >
              {lastState ?? "UNKNOWN"}
            </span>
          </div>
          {airlockEvent.metrics.map((m) => (
            <div key={m.name} className="border-l border-gray-700 pl-4">
              <p className="text-xs text-gray-400">{m.name}</p>
              <p className="text-xl font-bold text-white">
                {m.value.toFixed(1)}
                <span className="text-xs text-gray-400 ml-1">{m.unit}</span>
              </p>
            </div>
          ))}
        </div>
      )}

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

