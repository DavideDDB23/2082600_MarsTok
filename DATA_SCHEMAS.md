# Mars Operations — Data Schemas & Contracts

> **Contract version:** `1.2.0` (simulator) | Internal event schema version: `1.0.0`  
> This document is the single source of truth for all data structures in the system.  
> Any change here must be reflected in `source/shared/schemas.py`.

---

## 1. Simulator Input Schemas (read-only, from `SCHEMA_CONTRACT.md`)

These are the raw payloads produced by `mars-iot-simulator:multiarch_v1`. The Collector service consumes them and converts each to an `InternalEvent`.

### 1.1 `rest.scalar.v1`
Used by: `greenhouse_temperature`, `entrance_humidity`, `co2_hall`, `corridor_pressure`

```json
{
  "sensor_id":   "string",
  "captured_at": "2026-03-06T12:00:00Z",
  "metric":      "string",
  "value":       22.5,
  "unit":        "string",
  "status":      "ok | warning"
}
```

### 1.2 `rest.chemistry.v1`
Used by: `hydroponic_ph`, `air_quality_voc`

```json
{
  "sensor_id":    "string",
  "captured_at":  "2026-03-06T12:00:00Z",
  "measurements": [
    { "metric": "ph",  "value": 6.8, "unit": "pH" },
    { "metric": "voc", "value": 0.1, "unit": "ppm" }
  ],
  "status": "ok | warning"
}
```

### 1.3 `rest.particulate.v1`
Used by: `air_quality_pm25`

```json
{
  "sensor_id":   "string",
  "captured_at": "2026-03-06T12:00:00Z",
  "pm1_ug_m3":   3.2,
  "pm25_ug_m3":  7.4,
  "pm10_ug_m3":  12.1,
  "status":      "ok | warning"
}
```

### 1.4 `rest.level.v1`
Used by: `water_tank_level`

```json
{
  "sensor_id":    "string",
  "captured_at":  "2026-03-06T12:00:00Z",
  "level_pct":    82.5,
  "level_liters": 412.5,
  "status":       "ok | warning"
}
```

### 1.5 `topic.power.v1`
Used by: `mars/telemetry/solar_array`, `mars/telemetry/power_bus`, `mars/telemetry/power_consumption`

```json
{
  "topic":          "mars/telemetry/solar_array",
  "event_time":     "2026-03-06T12:00:00Z",
  "subsystem":      "string",
  "power_kw":       15.3,
  "voltage_v":      48.2,
  "current_a":      317.8,
  "cumulative_kwh": 1024.5
}
```

### 1.6 `topic.environment.v1`
Used by: `mars/telemetry/radiation`, `mars/telemetry/life_support`

```json
{
  "topic":      "mars/telemetry/radiation",
  "event_time": "2026-03-06T12:00:00Z",
  "source": {
    "system":  "string",
    "segment": "string"
  },
  "measurements": [
    { "metric": "dose_rate", "value": 0.24, "unit": "mSv/h" }
  ],
  "status": "ok | warning"
}
```

### 1.7 `topic.thermal_loop.v1`
Used by: `mars/telemetry/thermal_loop`

```json
{
  "topic":         "mars/telemetry/thermal_loop",
  "event_time":    "2026-03-06T12:00:00Z",
  "loop":          "string",
  "temperature_c": 21.5,
  "flow_l_min":    12.3,
  "status":        "ok | warning"
}
```

### 1.8 `topic.airlock.v1`
Used by: `mars/telemetry/airlock`

```json
{
  "topic":           "mars/telemetry/airlock",
  "event_time":      "2026-03-06T12:00:00Z",
  "airlock_id":      "string",
  "cycles_per_hour": 2,
  "last_state":      "IDLE | PRESSURIZING | DEPRESSURIZING"
}
```

---

## 2. Unified Internal Event Schema (v1.0.0)

This is the **canonical normalized event** published by the Collector to RabbitMQ and stored as the latest state in Redis. Every service downstream consumes only this format.

```json
{
  "event_id":    "550e8400-e29b-41d4-a716-446655440000",
  "timestamp":   "2026-03-06T12:00:00.000Z",
  "source_id":   "greenhouse_temperature",
  "source_type": "rest_sensor | telemetry_topic",
  "category":    "environment | power | life_support | airlock | thermal",
  "metrics": [
    {
      "name":  "value",
      "value": 22.5,
      "unit":  "°C"
    }
  ],
  "status":      "ok | warning | null",
  "raw_schema":  "rest.scalar.v1",
  "extra_fields": {
    "subsystem":  "solar_panel_alpha",
    "loop":       "primary",
    "airlock_id": "airlock_1",
    "last_state": "IDLE"
  }
}
```

### Field Definitions

| Field | Type | Description |
|---|---|---|
| `event_id` | `string (UUID v4)` | Unique event identifier |
| `timestamp` | `string (ISO-8601)` | Original sensor capture time; fallback to ingestion time |
| `source_id` | `string` | Sensor name (`greenhouse_temperature`) or topic path (`mars/telemetry/solar_array`) |
| `source_type` | `enum` | `"rest_sensor"` or `"telemetry_topic"` |
| `category` | `enum` | Logical grouping for the frontend |
| `metrics` | `array` | One or more normalized `{name, value, unit}` objects |
| `status` | `string\|null` | Forwarded from raw payload; `null` for sources without status |
| `raw_schema` | `string` | The originating schema name for traceability |
| `extra_fields` | `object` | Schema-specific fields that don't fit metrics (airlock state, loop name, etc.) |

### Category Mapping

| Source ID / Topic | Category |
|---|---|
| `greenhouse_temperature`, `entrance_humidity`, `co2_hall`, `corridor_pressure` | `environment` |
| `hydroponic_ph`, `air_quality_voc`, `air_quality_pm25`, `water_tank_level` | `environment` |
| `mars/telemetry/solar_array`, `mars/telemetry/power_bus`, `mars/telemetry/power_consumption` | `power` |
| `mars/telemetry/radiation`, `mars/telemetry/life_support` | `life_support` |
| `mars/telemetry/thermal_loop` | `thermal` |
| `mars/telemetry/airlock` | `airlock` |

### Normalization Rules

| Raw Schema | `source_id` | `metrics` |
|---|---|---|
| `rest.scalar.v1` | `sensor_id` from raw | `[{name: raw.metric, value: raw.value, unit: raw.unit}]` |
| `rest.chemistry.v1` | `sensor_id` from raw | `raw.measurements` as-is |
| `rest.particulate.v1` | `sensor_id` from raw | `[{name:"pm1_ug_m3",…}, {name:"pm25_ug_m3",…}, {name:"pm10_ug_m3",…}]` |
| `rest.level.v1` | `sensor_id` from raw | `[{name:"level_pct",…}, {name:"level_liters",…}]` |
| `topic.power.v1` | `raw.topic` | `[power_kw, voltage_v, current_a, cumulative_kwh]` |
| `topic.environment.v1` | `raw.topic` | `raw.measurements` as-is |
| `topic.thermal_loop.v1` | `raw.topic` | `[{name:"temperature_c",…}, {name:"flow_l_min",…}]` |
| `topic.airlock.v1` | `raw.topic` | `[{name:"cycles_per_hour",…}]`; `last_state` in `extra_fields` |

---

## 3. Rule Model

Rules are persisted in PostgreSQL and evaluated on every arriving `InternalEvent`.

### JSON Representation

```json
{
  "id":         "uuid",
  "name":       "High Temperature Alert",
  "enabled":    true,
  "condition": {
    "source_id": "greenhouse_temperature",
    "metric":    "value",
    "operator":  "gt",
    "threshold": 35.0
  },
  "action": {
    "actuator_name": "cooling_fan",
    "state":         "ON"
  },
  "created_at": "2026-03-06T12:00:00Z",
  "updated_at": "2026-03-06T12:00:00Z"
}
```

### Condition Operators

| Operator | Description |
|---|---|
| `gt` | `metric_value > threshold` |
| `lt` | `metric_value < threshold` |
| `gte` | `metric_value >= threshold` |
| `lte` | `metric_value <= threshold` |
| `eq` | `metric_value == threshold` |
| `neq` | `metric_value != threshold` |

### Example Rules

```json
[
  {
    "name": "High Greenhouse Temp → Cooling Fan ON",
    "condition": { "source_id": "greenhouse_temperature", "metric": "value", "operator": "gt", "threshold": 35 },
    "action": { "actuator_name": "cooling_fan", "state": "ON" }
  },
  {
    "name": "Low Water Tank → Water Pump ON",
    "condition": { "source_id": "water_tank_level", "metric": "level_pct", "operator": "lt", "threshold": 20 },
    "action": { "actuator_name": "water_pump", "state": "ON" }
  },
  {
    "name": "High CO2 → Ventilation ON",
    "condition": { "source_id": "co2_hall", "metric": "value", "operator": "gt", "threshold": 1000 },
    "action": { "actuator_name": "ventilation", "state": "ON" }
  },
  {
    "name": "High Solar Power → Charge Controller ON",
    "condition": { "source_id": "mars/telemetry/solar_array", "metric": "power_kw", "operator": "gt", "threshold": 20 },
    "action": { "actuator_name": "charge_controller", "state": "ON" }
  }
]
```

---

## 4. Alert Model

Alerts are written to PostgreSQL by the Rules Engine whenever a rule fires.

```json
{
  "id":          "uuid",
  "rule_id":     "uuid",
  "rule_name":   "High Greenhouse Temp → Cooling Fan ON",
  "triggered_event": { "...InternalEvent..." },
  "triggered_at": "2026-03-06T12:05:00Z"
}
```

---

## 5. Actuator API

### Simulator endpoint (proxied via API service)

**Set actuator state:**
```
POST /api/actuators/{actuator_name}
Body:     { "state": "ON" }
Response: { "actuator": "cooling_fan", "state": "ON", "updated_at": "2026-03-06T12:05:00Z" }
```

**List all actuators:**
```
GET /api/actuators
Response: { "actuators": { "cooling_fan": "ON", "water_pump": "OFF", ... } }
```

> **Note:** Hit `GET /api/actuators` on Day 1 to get the actual list of actuator names before hardcoding them in `config.py`.

---

## 6. PostgreSQL Table Definitions

### `rules` table

```sql
CREATE TABLE rules (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,
  enabled     BOOLEAN NOT NULL DEFAULT TRUE,
  condition   JSONB NOT NULL,
  action      JSONB NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `alerts` table

```sql
CREATE TABLE alerts (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rule_id          UUID NOT NULL REFERENCES rules(id) ON DELETE CASCADE,
  triggered_event  JSONB NOT NULL,
  triggered_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_alerts_rule_id     ON alerts(rule_id);
CREATE INDEX idx_alerts_triggered_at ON alerts(triggered_at DESC);
CREATE INDEX idx_alerts_source_id   ON alerts((triggered_event->>'source_id'));
```

---

## 7. Redis Key Patterns

| Key pattern | Type | TTL | Content |
|---|---|---|---|
| `state:{source_id}` | String (JSON) | 3600 s | Latest `InternalEvent` for this sensor/topic |
| *(pub/sub)* `mars.events` | Channel | — | `InternalEvent` JSON (fan-out to API SSE) |
| *(pub/sub)* `mars.alerts` | Channel | — | Alert JSON (fan-out to API SSE) |

**Example Redis commands:**
```bash
# Get latest greenhouse temperature
redis-cli GET "state:greenhouse_temperature"

# Scan all sensor states
redis-cli KEYS "state:*"

# Subscribe to live events (debug)
redis-cli SUBSCRIBE mars.events mars.alerts
```

---

## 8. RabbitMQ Topology

| Resource | Type | Name | Description |
|---|---|---|---|
| Exchange | `fanout` | `mars.events` | All normalized InternalEvents published here |
| Queue (rules-engine) | Durable | `mars.events.rules-engine` | Bound to `mars.events`; consumed by rules-engine |
| Queue (future) | — | — | Any future consumer binds its own queue to the same exchange |

**Why fanout?** Multiple consumers (rules-engine, potential future analytics service) can independently bind queues to the same exchange without the publisher needing to know about them.

```
Collector ──publish──▶ [mars.events fanout exchange]
                              │
                    ┌─────────┴──────────┐
                    ▼                    ▼
         [mars.events.rules-engine]   [mars.events.future-service]
                    │
                    ▼
              Rules Engine consumer
```

---

## 9. API SSE Event Format

The `GET /api/stream` endpoint emits Server-Sent Events in this format:

### Sensor update event
```
event: sensor_update
data: {"event_id":"...","timestamp":"...","source_id":"greenhouse_temperature","source_type":"rest_sensor","category":"environment","metrics":[{"name":"value","value":22.5,"unit":"°C"}],"status":"ok","raw_schema":"rest.scalar.v1","extra_fields":{}}

```

### Alert event
```
event: alert
data: {"id":"...","rule_id":"...","rule_name":"High Greenhouse Temp → Cooling Fan ON","triggered_event":{...},"triggered_at":"2026-03-06T12:05:00Z"}

```

### Keep-alive ping (every 15 s)
```
: ping

```

### Frontend consumption
```ts
const es = new EventSource("/api/stream");
es.addEventListener("sensor_update", (e) => {
  const event = JSON.parse(e.data) as SensorState;
  setSensorStates(prev => ({ ...prev, [event.source_id]: event }));
});
es.addEventListener("alert", (e) => {
  const alert = JSON.parse(e.data) as Alert;
  setAlerts(prev => [alert, ...prev].slice(0, 50));
});
```

---

## 10. `source/shared/schemas.py` — Pydantic Models

```python
from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime, timezone


class SourceType(str, Enum):
    REST_SENSOR     = "rest_sensor"
    TELEMETRY_TOPIC = "telemetry_topic"


class Category(str, Enum):
    ENVIRONMENT  = "environment"
    POWER        = "power"
    LIFE_SUPPORT = "life_support"
    AIRLOCK      = "airlock"
    THERMAL      = "thermal"


class MetricReading(BaseModel):
    name:  str
    value: float
    unit:  str


class InternalEvent(BaseModel):
    event_id:     str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp:    str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_id:    str
    source_type:  SourceType
    category:     Category
    metrics:      list[MetricReading]
    status:       Optional[str] = None
    raw_schema:   str
    extra_fields: dict = Field(default_factory=dict)


class RuleCondition(BaseModel):
    source_id: str
    metric:    str
    operator:  str   # gt | lt | gte | lte | eq | neq
    threshold: float


class RuleAction(BaseModel):
    actuator_name: str
    state:         str  # ON | OFF


class Rule(BaseModel):
    id:         Optional[str] = None
    name:       str
    enabled:    bool = True
    condition:  RuleCondition
    action:     RuleAction
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class Alert(BaseModel):
    id:               Optional[str] = None
    rule_id:          str
    rule_name:        Optional[str] = None
    triggered_event:  dict  # serialized InternalEvent
    triggered_at:     Optional[str] = None
```
