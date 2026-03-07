/**
 * Environment.tsx — Life-support & radiation monitoring + environmental REST sensors.
 *
 * US6: Life support and radiation measurement cards with status badges
 *      (mars/telemetry/radiation, mars/telemetry/life_support)
 * US9: Greenhouse and corridor environmental sensors (temperature, humidity, CO₂, pressure)
 * US10: Air quality data (VOC, PM2.5, water pH)
 *
 * Live data comes from the SSE context in App.tsx.
 */
import { useLiveData } from "../App";
import { LiveChart } from "../components/LiveChart";
import { SensorWidget } from "../components/SensorWidget";

// ── US6: Life support + radiation telemetry topics ─────────────────────────────
const LIFE_SUPPORT_SOURCES = [
  "mars/telemetry/radiation",
  "mars/telemetry/life_support",
];

// ── US9 + US10: Environmental REST sensors ─────────────────────────────────────
const ENV_REST_SOURCES = [
  "greenhouse_temperature",
  "entrance_humidity",
  "co2_hall",
  "corridor_pressure",
  "hydroponic_ph",
  "air_quality_voc",
  "air_quality_pm25",
  "water_tank_level",
];

// Live trend charts for REST scalar sensors (metric names as emitted by normalizer)
const CHARTS = [
  { id: "greenhouse_temperature", metric: "temperature_c", label: "Greenhouse Temperature",  color: "#fb923c" },
  { id: "entrance_humidity",      metric: "humidity_pct",  label: "Entrance Humidity",        color: "#60a5fa" },
  { id: "co2_hall",               metric: "co2_ppm",       label: "CO₂ Hall",                 color: "#34d399" },
  { id: "corridor_pressure",      metric: "pressure_kpa",  label: "Corridor Pressure",        color: "#facc15" },
  { id: "air_quality_pm25",       metric: "pm25_ug_m3",    label: "Air Quality PM2.5",        color: "#f87171" },
  { id: "water_tank_level",       metric: "level_pct",     label: "Water Tank Level (%)",     color: "#a78bfa" },
];

export default function Environment() {
  const { sensorStates } = useLiveData();

  return (
    <div>
      <h1 className="text-xl font-bold text-white mb-1">Environment</h1>
      <p className="text-sm text-gray-400 mb-6">
        Life support &amp; radiation monitoring · REST environmental sensors
      </p>

      {/* ── US6: Life Support & Radiation ─────────────────────────────────── */}
      <h2 className="text-sm font-semibold text-gray-300 mb-3">
        Life Support &amp; Radiation
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
        {LIFE_SUPPORT_SOURCES.map((id) =>
          sensorStates[id] ? (
            <SensorWidget key={id} event={sensorStates[id]} />
          ) : (
            <div key={id} className="card text-xs text-gray-600 font-mono">
              {id}<br /><span className="text-gray-700">waiting for telemetry…</span>
            </div>
          ),
        )}
      </div>

      {/* ── US9 + US10: Environmental REST sensors ──────────────────────────── */}
      <h2 className="text-sm font-semibold text-gray-300 mb-3">
        Environmental Sensors
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 mb-8">
        {ENV_REST_SOURCES.map((id) =>
          sensorStates[id] ? (
            <SensorWidget key={id} event={sensorStates[id]} />
          ) : (
            <div key={id} className="card text-xs text-gray-600 font-mono">
              {id}<br /><span className="text-gray-700">waiting…</span>
            </div>
          ),
        )}
      </div>

      {/* ── Live trend charts for REST sensors ──────────────────────────────── */}
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
