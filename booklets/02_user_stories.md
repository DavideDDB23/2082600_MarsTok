# Mars Operations — User Stories & LoFi Mockups

## User Story Format

Each entry includes:
- **Story** — the user story text
- **Page** — which frontend page implements it
- **Acceptance Criteria** — what must be true for the story to be done
- **NFRs** — Non-Functional Requirements
- **LoFi Mockup** — screen layout sketch

---

## US 1 — Unified Dashboard

> As an operator, I want to see all live sensor readings on a unified dashboard so that I can monitor the base status at a glance.

**Page:** Dashboard  
**Acceptance Criteria:**
- All sensor sources (REST + telemetry) appear as cards on one screen
- Each card shows: source_id, category, all metric name/value/unit pairs
- Cards are sorted consistently (alphabetically by source_id)

**NFRs:**
- Layout must remain usable with up to 20 sensor cards (responsive grid)
- Card content must be readable at 1280×800 minimum resolution

**LoFi Mockup:**
```
┌─────────────────────────────────────────────────────────────┐
│  🔴 Mars Operations         Dashboard        ● LIVE  14:23  │
├──────────┬──────────────────────────────────────────────────┤
│ Dashboard│                                                   │
│ Power    │  ┌──────────────┐ ┌──────────────┐ ┌──────────┐ │
│ Environm.│  │ airlock      │ │ co2_hall     │ │ corridor │ │
│ Airlock  │  │ airlock      │ │ environment  │ │ pressure │ │
│ Actuators│  │ ● ok         │ │ ● ok         │ │ ● warn   │ │
│ Rules    │  │ last_state   │ │ value        │ │ value    │ │
│ Alerts   │  │ IDLE         │ │ 412 ppm      │ │ 101.2 kPa│ │
│          │  └──────────────┘ └──────────────┘ └──────────┘ │
│          │  ┌──────────────┐ ┌──────────────┐ ┌──────────┐ │
│          │  │ greenhouse_T │ │ life_support │ │ radiation│ │
│          │  │ environment  │ │ life_support │ │ life_supp│ │
│          │  │ ● ok         │ │ ● ok         │ │ ● ok     │ │
│          │  │ value        │ │ o2_pct  21.1%│ │ sievert  │ │
│          │  │ 23.4 °C      │ │ co2_ppm 410  │ │ 0.003 Sv │ │
│          │  └──────────────┘ └──────────────┘ └──────────┘ │
│          │  [ ... more cards ... ]                          │
└──────────┴──────────────────────────────────────────────────┘
```

---

## US 2 — Status Badges

> As an operator, I want sensor status badges (ok/warning) highlighted visually so that I can immediately identify which sensors are in anomalous states.

**Page:** Dashboard (all pages with SensorWidget)  
**Acceptance Criteria:**
- `ok` status → green badge with text "ok"
- `warning` status → amber badge with text "warning"
- `null` / unknown → grey badge

**NFRs:**
- Colour must be distinguishable for deuteranopia (use shape/text in addition to colour)
- Badge must update within the same render cycle as the metric value

**LoFi Mockup:**
```
  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
  │ greenhouse_T    │     │ co2_hall        │     │ corridor_press  │
  │ ╔═══╗           │     │ ╔══════════╗    │     │ ╔═══════╗       │
  │ ║ ok║  23.4 °C  │     │ ║ warning  ║    │     │ ║  null ║       │
  │ ╚═══╝  [green]  │     │ ╚══════════╝    │     │ ╚═══════╝       │
  │                 │     │ [amber]         │     │ [grey]          │
  │                 │     │  1842 ppm       │     │  — kPa          │
  └─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## US 3 — Real-time Updates

> As an operator, I want the dashboard to update in real-time without manual page refresh so that I always see the most current data.

**Page:** All pages  
**Acceptance Criteria:**
- New sensor events update displayed values within 1 second of receipt
- No page reload required
- SSE connection indicator visible in top bar (green dot = connected, grey = reconnecting)

**NFRs:**
- SSE reconnection must happen automatically after a disconnect (3 s retry)
- Browser back-button and tab switching must not break the SSE connection

**LoFi Mockup:**
```
  Top bar: ● LIVE  (green pulsing dot — connected)
           ○ OFFLINE  (grey dot — reconnecting)
           Last update: 2 s ago
```

---

## US 4 — Instant State on Page Load

> As an operator, I want to see the latest sensor state immediately on page load so that I never face a blank dashboard.

**Page:** Dashboard (and all pages with live data)  
**Acceptance Criteria:**
- `GET /api/state/` is called before opening the SSE stream
- Cards are populated with pre-fetched data while SSE connects
- No "loading skeleton" or blank cards visible after initial fetch resolves

**NFRs:**
- Pre-fetch must complete before SSE stream is opened
- Pre-fetch latency < 500 ms on local network

**LoFi Mockup:**  
_Same as US 1 — the key behaviour is that cards are populated from the first paint; no blank state is shown._

---

## US 5 — Power Metrics Charts

> As an operator, I want to see live line charts for power metrics (solar array, power bus, power consumption) so that I can analyze energy trends over time.

**Page:** Power  
**Acceptance Criteria:**
- 6 separate line charts: solar_array (power_kw, voltage_v), power_bus (power_kw, voltage_v), power_consumption (power_kw, cumulative_kwh)
- Each chart shows a rolling window of the last 60 data points
- X-axis: timestamp; Y-axis: metric value with unit label

**NFRs:**
- Charts update in real-time as SSE events arrive (no polling)
- Y-axis auto-scales to fit current window data

**LoFi Mockup:**
```
┌──────────────────────────────────────────────────────────────┐
│  Power Metrics                               ● LIVE  14:23   │
├──────────┬───────────────────────────────────────────────────┤
│ Dashboard│  solar_array — power_kw              ┐            │
│ Power  ← │  ▲                                   │            │
│ Environm.│  │  ╭─╮    ╭──╮  ╭──╮               │ 6 charts   │
│ Airlock  │  │ ╯  ╰──╯    ╰──╯   ╰─             │ in a 2×3   │
│ Actuators│  └──────────────────────►            │ or 3×2     │
│ Rules    │                                      │ grid       │
│ Alerts   │  power_bus — voltage_v               │            │
│          │  ▲                                   │            │
│          │  │ ─────────────────────             │            │
│          │  └──────────────────────►            ┘            │
└──────────┴───────────────────────────────────────────────────┘
```

---

## US 6 — Radiation & Life Support

> As an operator, I want to see real-time radiation and life support measurements with status indicators so that I can monitor crew safety.

**Page:** Environment  
**Acceptance Criteria:**
- Dedicated section at top of Environment page for radiation + life_support telemetry cards
- Cards show all metrics from the telemetry payload with status badge
- Status badge reflects `status` field from InternalEvent

**NFRs:**
- These cards must be visually separated / prioritised above REST sensor data (crew safety critical)

**LoFi Mockup:**
```
┌──────────────────────────────────────────────────────────────┐
│  Environment                                                 │
├──────────┬───────────────────────────────────────────────────┤
│          │  ┌── Crew Safety Telemetry ──────────────────────┐│
│          │  │  ┌────────────────┐   ┌────────────────┐      ││
│          │  │  │ radiation      │   │ life_support   │      ││
│          │  │  │ ● ok           │   │ ● ok           │      ││
│          │  │  │ dose: 0.003 Sv │   │ o2: 21.1 %     │      ││
│          │  │  │                │   │ co2: 412 ppm   │      ││
│          │  │  └────────────────┘   └────────────────┘      ││
│          │  └───────────────────────────────────────────────┘│
│          │  ┌── Environmental REST Sensors ─────────────────┐│
│          │  │  [ greenhouse_T ]  [ entrance_humidity ]  …   ││
│          │  └───────────────────────────────────────────────┘│
└──────────┴───────────────────────────────────────────────────┘
```

---

## US 7 — Thermal Loop Data

> As an operator, I want to see thermal loop temperature and flow rate updating in real-time so that I can detect cooling system failures early.

**Page:** Airlock & Thermal  
**Acceptance Criteria:**
- thermal_loop metrics (temperature_c, flow_rate_lpm) displayed as live line chart
- Values update in real-time from SSE stream

**NFRs:**
- Chart must show minimum last 60 seconds of data

**LoFi Mockup:**
```
┌──────────────────────────────────────────────────────────────┐
│  Airlock & Thermal                                           │
├──────────┬───────────────────────────────────────────────────┤
│          │  ┌── Airlock State ───────────────────────────┐   │
│          │  │  State: [ IDLE ]  green badge              │   │
│          │  │  Cycles/h: 0.4                             │   │
│          │  └────────────────────────────────────────────┘   │
│          │  ┌── Thermal Loop ─────────────────────────────┐  │
│          │  │  temperature_c  [live line chart]           │  │
│          │  │  flow_rate_lpm  [live line chart]           │  │
│          │  │  last_state     [live line chart]           │  │
│          │  └────────────────────────────────────────────┘   │
└──────────┴───────────────────────────────────────────────────┘
```

---

## US 8 — Airlock State & Cycles

> As an operator, I want to see the airlock state (IDLE / PRESSURIZING / DEPRESSURIZING) and cycles-per-hour so that I can track EVA activity.

**Page:** Airlock & Thermal  
**Acceptance Criteria:**
- `last_state` displayed as a coloured badge: IDLE → green, PRESSURIZING → yellow, DEPRESSURIZING → orange
- `cycles_per_hour` metric displayed numerically

**NFRs:**
- State badge colour change must be visible within 1 s of state transition

**LoFi Mockup:**
```
  ┌──────────────────────────────────────────┐
  │  Airlock Status                          │
  │                                          │
  │  State:   [ PRESSURIZING ]  (yellow)     │
  │  Cycles/h: 1.2                           │
  │                                          │
  └──────────────────────────────────────────┘
```

---

## US 9 — Environmental Sensors

> As an operator, I want to see greenhouse and corridor environmental sensors (temperature, humidity, CO2, pressure) so that I can ensure habitat air quality and integrity.

**Page:** Environment  
**Acceptance Criteria:**
- Cards for: greenhouse_temperature, entrance_humidity, co2_hall, corridor_pressure
- Each shows value, unit, and status badge

**NFRs:**
- Values refreshed every 5 s matching the simulator polling interval

**LoFi Mockup:**  
_See US 6 mockup — lower "Environmental REST Sensors" section._

---

## US 10 — Air Quality Data

> As an operator, I want to see air quality data (VOC concentration, PM1/PM2.5/PM10 particulates, water pH) so that I can detect chemical hazards and ensure breathable air.

**Page:** Environment  
**Acceptance Criteria:**
- Cards for: air_quality_pm25, air_quality_voc, hydroponic_ph, water_tank_level
- All metrics shown with units

**NFRs:**
- PM2.5 warning threshold (35 µg/m³) is reflected in `warning` status badge

**LoFi Mockup:**  
_See US 6 mockup — same section as US 9._

---

## US 11 — Actuator States

> As an operator, I want to see the current ON/OFF state of all actuators so that I always know the current system configuration.

**Page:** Actuators  
**Acceptance Criteria:**
- All 4 actuators (cooling_fan, entrance_humidifier, hall_ventilation, habitat_heater) shown as cards
- ON state → green-bordered card with Power icon highlighted
- OFF state → default card

**NFRs:**
- States auto-refreshed every 5 s via polling

**LoFi Mockup:**
```
┌──────────────────────────────────────────────────────────────┐
│  Actuators                                                   │
├──────────┬───────────────────────────────────────────────────┤
│          │  ┌──────────────┐  ┌──────────────┐              │
│          │  │ ⚡ cooling_fan│  │ entrance_hum │              │
│          │  │              │  │              │              │
│          │  │  [ON]  ──────│  │  [OFF]       │              │
│          │  │              │  │              │              │
│          │  │ [Turn OFF]   │  │ [Turn ON]    │              │
│          │  └──────────────┘  └──────────────┘              │
│          │  ┌──────────────┐  ┌──────────────┐              │
│          │  │ hall_vent    │  │ habitat_heat │              │
│          │  │  [OFF]       │  │  [ON]        │              │
│          │  │ [Turn ON]    │  │ [Turn OFF]   │              │
│          │  └──────────────┘  └──────────────┘              │
└──────────┴───────────────────────────────────────────────────┘
```

---

## US 12 — Manual Actuator Toggle

> As an operator, I want to manually toggle any actuator ON or OFF from the dashboard so that I can respond to emergencies without waiting for automation.

**Page:** Actuators  
**Acceptance Criteria:**
- "Turn ON" / "Turn OFF" button on each ActuatorCard
- Click sends `POST /api/actuators/{name}` with appropriate state
- Button label and card style update optimistically, reverted on error

**NFRs:**
- Action must complete (API round-trip) within 2 s
- Error shown to user if toggle fails

**LoFi Mockup:**  
_See US 11 mockup — the toggle button is the primary interactive element._

---

## US 13 — Create Automation Rule

> As an operator, I want to create an automation rule specifying IF a sensor metric crosses a threshold THEN set an actuator to a target state, so that the platform reacts automatically to conditions.

**Page:** Rules  
**Acceptance Criteria:**
- Form fields: Name, Source ID (dropdown from live sensors), Metric, Operator (gt/lt/gte/lte/eq/neq), Threshold, Actuator Name (dropdown from live actuators), State (ON/OFF), Enabled
- `POST /api/rules` on submit
- New rule appears immediately in the rules table

**NFRs:**
- Threshold must be numeric; validation error shown otherwise
- Form must be accessible via keyboard (tab order correct)

**LoFi Mockup:**
```
┌───────────────────────────────────────────────────────────┐
│  ┌── New Rule ──────────────────────────────────────────┐ │
│  │  Name:       [High Greenhouse Temp → Cooling Fan ON ] │ │
│  │  ── Condition ─────────────────────────────────────── │ │
│  │  Source ID:  [ greenhouse_temperature ▼ ]             │ │
│  │  Metric:     [ value                  ]               │ │
│  │  Operator:   [ gt ▼ ]  Threshold: [ 35.0 ]            │ │
│  │  ── Action ────────────────────────────────────────── │ │
│  │  Actuator:   [ cooling_fan ▼ ]  State: [ ON ▼ ]       │ │
│  │  Enabled:    [✓]                                       │ │
│  │                          [Cancel]  [Save Rule]         │ │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

---

## US 14 — List Rules

> As an operator, I want to list all existing automation rules so that I can audit the current automation logic.

**Page:** Rules  
**Acceptance Criteria:**
- Table shows: Name, Source ID, Operator, Threshold, Actuator, State, Enabled, Actions
- Empty state message when no rules exist
- `GET /api/rules` polled on page load

**NFRs:**
- Table must be sortable by name

**LoFi Mockup:**
```
┌──────────────────────────────────────────────────────────────────────┐
│  Rules Management                               [+ New Rule]          │
├──────────────────┬──────────────┬──────┬───────┬──────────┬──────────┤
│ Name             │ Condition    │ Op   │ Thresh│ Actuator │ Actions  │
├──────────────────┼──────────────┼──────┼───────┼──────────┼──────────┤
│ High GH Temp     │ greenhouse_T │  gt  │  35.0 │ cool_fan │ ● ✏ 🗑  │
│ Low O2           │ life_support │  lt  │  19.5 │ hab_heat │ ○ ✏ 🗑  │
└──────────────────┴──────────────┴──────┴───────┴──────────┴──────────┘
   ● = enabled  ○ = disabled   ✏ = edit   🗑 = delete
```

---

## US 15 — Edit Rule

> As an operator, I want to edit an existing rule (change name, threshold, target actuator or state) so that I can tune automation as conditions change.

**Page:** Rules  
**Acceptance Criteria:**
- Edit button opens the same RuleForm pre-populated with current values
- `PUT /api/rules/{id}` on save
- Table row updates to reflect new values

**NFRs:**
- Unsaved changes must be discardable (Cancel button)

**LoFi Mockup:**  
_Same as US 13 mockup with fields pre-filled._

---

## US 16 — Enable / Disable Rule

> As an operator, I want to enable or disable a rule without deleting it so that I can safely test changes without losing configuration.

**Page:** Rules  
**Acceptance Criteria:**
- Toggle pill in the table row (green = enabled, grey = disabled)
- Click sends `PATCH /api/rules/{id}/toggle`
- Visual state updates immediately (optimistic)

**NFRs:**
- Toggle must not require a page reload

**LoFi Mockup:**
```
  Name         │ Condition     │ Enabled
  High GH Temp │ greenhouse_T  │  ●──  (green, on)
  Low O2       │ life_support  │  ──○  (grey, off)
```

---

## US 17 — Delete Rule

> As an operator, I want to delete a rule that is no longer needed so that I can keep the rule list clean and relevant.

**Page:** Rules  
**Acceptance Criteria:**
- Delete button (🗑) in table row
- Confirmation dialog before deletion
- `DELETE /api/rules/{id}` on confirm
- Row removed from table immediately

**NFRs:**
- Accidental deletion must be prevented by a confirmation step

**LoFi Mockup:**
```
  ┌─────────────────────────────────────────┐
  │  Delete Rule?                           │
  │  "High Greenhouse Temp → Cooling Fan"   │
  │                                         │
  │       [Cancel]    [Delete]              │
  └─────────────────────────────────────────┘
```

---

## US 18 — Rule Persistence

> As an operator, I want rules to persist across platform restarts so that I never lose my automation configuration due to a reboot.

**Page:** Rules (and entire backend)  
**Acceptance Criteria:**
- Rules survive `docker compose down && docker compose up`
- PostgreSQL `pg_data` volume persists between restarts
- Alembic migration runs on rules-engine startup to ensure schema is current

**NFRs:**
- Zero data loss on clean restart
- Schema migration must be idempotent

**LoFi Mockup:**  
_No dedicated UI — verified by operational test. The Rules page simply shows the same rules after restart._

---

## US 19 — Chronological Alert Log

> As an operator, I want to see a chronological log of all rule-triggered alerts (with timestamp, rule name, and metric value that triggered it) so that I can audit all automated actions.

**Page:** Alerts  
**Acceptance Criteria:**
- Alerts displayed newest-first
- Each entry shows: rule name, source_id, triggered metric values, timestamp, delete button
- New SSE alert events prepended to the list in real-time
- Paginated (limit 20 per page, offset-based)

**NFRs:**
- Timestamps displayed in local timezone
- Pagination controls must update offset correctly

**LoFi Mockup:**
```
┌──────────────────────────────────────────────────────────────┐
│  Alert Log                                                   │
├──────────┬──────────────────┬──────────────────┬────────────┤
│          │  Rule filter: [─────────────── ▼]   │            │
│          │  Source filter: [───────────── ▼]   │            │
│          │                                     [Clear]       │
│          │ ┌──────────────────────────────────────────────┐ │
│          │ │ 🔔 High GH Temp  ·  greenhouse_temperature   │ │
│          │ │    value: 38.2 °C  ·  14:22:01              │ │
│          │ │                                        [🗑]  │ │
│          │ ├──────────────────────────────────────────────┤ │
│          │ │ 🔔 Low O2  ·  life_support                   │ │
│          │ │    o2_pct: 18.9 %  ·  14:18:44              │ │
│          │ │                                        [🗑]  │ │
│          │ └──────────────────────────────────────────────┘ │
│          │  [← Prev]  Page 1 of 3  [Next →]                │
└──────────┴───────────────────────────────────────────────────┘
```

---

## US 20 — Filter Alert Log

> As an operator, I want to filter the alert log by rule or by sensor ID so that I can investigate a specific subsystem's alert history.

**Page:** Alerts  
**Acceptance Criteria:**
- Rule dropdown populated from `GET /api/rules` — shows rule names, value is rule UUID
- Source dropdown populated from live `sensorStates` keys (from SSE context)
- Changing either dropdown resets offset to 0 and re-fetches alerts automatically
- "Clear filters" button visible only when at least one filter is active

**NFRs:**
- Filters must be combinable (rule AND source simultaneously)
- Dropdown must update dynamically if new rules or sensors appear

**LoFi Mockup:**  
_See US 19 mockup — the filter bar with both dropdowns is shown at top._

---

## Summary Table

| US | Story (short) | Page | Priority |
|---|---|---|---|
| 1 | Unified live dashboard | Dashboard | Must |
| 2 | ok/warning status badges | Dashboard | Must |
| 3 | Real-time updates (no refresh) | All | Must |
| 4 | State on page load | All | Must |
| 5 | Power metrics line charts | Power | Must |
| 6 | Radiation + life support cards | Environment | Must |
| 7 | Thermal loop live chart | Airlock & Thermal | Must |
| 8 | Airlock state badge + cycles | Airlock & Thermal | Must |
| 9 | Environmental REST sensors | Environment | Must |
| 10 | Air quality data | Environment | Must |
| 11 | Actuator ON/OFF states | Actuators | Must |
| 12 | Manual actuator toggle | Actuators | Must |
| 13 | Create IF-THEN rule | Rules | Must |
| 14 | List all rules | Rules | Must |
| 15 | Edit existing rule | Rules | Must |
| 16 | Enable/disable rule | Rules | Must |
| 17 | Delete rule | Rules | Must |
| 18 | Rule persistence across restarts | Backend + DB | Must |
| 19 | Chronological alert log | Alerts | Must |
| 20 | Filter alert log by rule/source | Alerts | Must |
