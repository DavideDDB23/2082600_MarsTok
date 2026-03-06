# SYSTEM DESCRIPTION:

Mars Operations is a distributed, event-driven IoT automation platform for monitoring and controlling a Mars base habitat. The platform ingests heterogeneous sensor and telemetry data from a simulated Mars base in real time, normalizes it into a unified event format, caches the latest state for instant access, and evaluates user-defined IF-THEN automation rules that automatically trigger actuators when conditions are met. Operators interact through a real-time monitoring dashboard that displays live sensor readings, telemetry charts, actuator controls, rule management, and a complete alert history. The system handles two data transport modalities: periodic REST polling for scalar sensors and persistent SSE/WebSocket streams for high-frequency telemetry topics.

# USER STORIES:

1) As an operator, I want to see all live sensor readings on a unified dashboard so that I can monitor the base status at a glance.
2) As an operator, I want sensor status badges (ok/warning) highlighted visually so that I can immediately identify which sensors are in anomalous states.
3) As an operator, I want the dashboard to update in real-time without manual page refresh so that I always see the most current data.
4) As an operator, I want to see the latest sensor state immediately on page load (even before new data arrives) so that I never face a blank dashboard.
5) As an operator, I want to see live line charts for power metrics (solar array, power bus, power consumption) so that I can analyze energy trends over time.
6) As an operator, I want to see real-time radiation and life support measurements with status indicators so that I can monitor crew safety.
7) As an operator, I want to see thermal loop temperature and flow rate updating in real-time so that I can detect cooling system failures early.
8) As an operator, I want to see the airlock state (IDLE / PRESSURIZING / DEPRESSURIZING) and cycles-per-hour so that I can track EVA activity.
9) As an operator, I want to see greenhouse and corridor environmental sensors (temperature, humidity, CO2, pressure) so that I can ensure habitat air quality and integrity.
10) As an operator, I want to see air quality data (VOC concentration, PM1/PM2.5/PM10 particulates, water pH) so that I can detect chemical hazards and ensure breathable air.
11) As an operator, I want to see the current ON/OFF state of all actuators so that I always know the current system configuration.
12) As an operator, I want to manually toggle any actuator ON or OFF from the dashboard so that I can respond to emergencies without waiting for automation.
13) As an operator, I want to create an automation rule specifying IF a sensor metric crosses a threshold THEN set an actuator to a target state, so that the platform reacts automatically to conditions.
14) As an operator, I want to list all existing automation rules so that I can audit the current automation logic.
15) As an operator, I want to edit an existing rule (change name, threshold, target actuator or state) so that I can tune automation as conditions change.
16) As an operator, I want to enable or disable a rule without deleting it so that I can safely test changes without losing configuration.
17) As an operator, I want to delete a rule that is no longer needed so that I can keep the rule list clean and relevant.
18) As an operator, I want rules to persist across platform restarts so that I never lose my automation configuration due to a reboot.
19) As an operator, I want to see a chronological log of all rule-triggered alerts (with timestamp, rule name, and metric value that triggered it) so that I can audit all automated actions.
20) As an operator, I want to filter the alert log by rule or by sensor ID so that I can investigate a specific subsystem's alert history.

# STANDARD EVENT SCHEMA:

All data collected by the platform is normalized into a single unified `InternalEvent` JSON object before being routed through the message broker and stored in the state cache.

```json
{
  "event_id":    "550e8400-e29b-41d4-a716-446655440000",
  "timestamp":   "2026-03-06T12:00:00.000Z",
  "source_id":   "greenhouse_temperature",
  "source_type": "rest_sensor | telemetry_topic",
  "category":    "environment | power | life_support | airlock | thermal",
  "metrics": [
    { "name": "value", "value": 22.5, "unit": "degC" }
  ],
  "status":      "ok | warning | null",
  "raw_schema":  "rest.scalar.v1",
  "extra_fields": {}
}
```

# RULE MODEL:

Automation rules are persisted in PostgreSQL and evaluated on every incoming event.

```json
{
  "id":      "uuid",
  "name":    "High Greenhouse Temp -> Cooling Fan ON",
  "enabled": true,
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

Supported operators: `gt` (>), `lt` (<), `gte` (>=), `lte` (<=), `eq` (==), `neq` (!=).
