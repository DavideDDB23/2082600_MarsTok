---
title: Mars Operations — Distributed IoT Automation Platform
author: "Student ID: 2082600 · MarsTok"
date: "Hackathon — March 2026 · Lab of Advanced Programming 2025/2026"
---

## 🔴 Mars Operations

**Distributed IoT Automation Platform**

Lab of Advanced Programming 2025/2026 · Hackathon — March 2026

Student ID: **2082600** · Project: **MarsTok**

---

## 🚨 Problem & Solution

> *"Mars 2036. Your automation stack is partially destroyed. Devices speak incompatible dialects. Rebuild it — or face thermodynamic consequences."*

**The Challenge**

- 15 devices, 8 raw JSON schemas, two transport protocols
- REST polling + persistent SSE streams — no unified format
- Operators face a blank dashboard on page load
- Automation must fire without human intervention
- Configuration must survive service restarts

**Our Solution**

- Unified **InternalEvent** normalisation layer
- Event-driven pipeline via **RabbitMQ** fanout exchange
- **IF-THEN rule engine** — auto-triggers actuators
- React dashboard with **live SSE push**
- Full **Docker Compose IaC** — one command start

---

## 🏗️ System Architecture

**Flow (top to bottom)**

1. `mars-iot-simulator :8080` — 8 REST sensors + 7 SSE telemetry topics
2. `collector` — Python 3.12 asyncio — polls + streams + normalises (8 schemas) + publishes
3. RabbitMQ 3.13 — fanout exchange `mars.events` — durable, persistent
4. `rules-engine` — Python 3.12 asyncio — cache state → evaluate rules → actuate → persist alerts → publish
5. `api` — FastAPI :8000
6. `frontend` — React 18 :3000

**Infrastructure**

| Service | Details |
|---|---|
| RabbitMQ 3.13 | fanout `mars.events` · durable · persistent delivery |
| Redis 7 | `state:{id}` TTL=3600 s · pub/sub: `mars.events` + `mars.alerts` |
| PostgreSQL 16 | tables: `rules` + `alerts` · JSONB columns · Alembic migrations |

---

## ⚡ Data Pipeline & Unified Schema

**7-Step Pipeline**

1. **Ingest** — poll 8 REST sensors every 5 s; maintain 7 persistent SSE connections
2. **Normalise** — 8 raw schemas → 1 `InternalEvent` via dispatcher
3. **Publish** — PERSISTENT to RabbitMQ fanout `mars.events`
4. **Process** — write `state:{id}` to Redis TTL=1 h, evaluate all enabled rules
5. **Alert** — POST actuator to simulator + INSERT PostgreSQL + PUBLISH Redis
6. **Stream** — API subscribes Redis pub/sub → relays named SSE events
7. **Render** — `useSSE` pre-fetches state on load, then merges live stream

**InternalEvent Schema**

```json
{
  "event_id":    "550e8400-...",
  "timestamp":   "2026-03-06T12:00:00Z",
  "source_id":   "greenhouse_temperature",
  "source_type": "rest_sensor",
  "category":    "environment",
  "metrics": [{ "name": "value", "value": 22.5, "unit": "degC" }],
  "status":      "ok | warning | null",
  "raw_schema":  "rest.scalar.v1"
}
```

8 schemas handled: `rest.scalar.v1` · `rest.chemistry.v1` · `rest.level.v1` · `rest.particulate.v1` · `topic.power.v1` · `topic.environment.v1` · `topic.thermal_loop.v1` · `topic.airlock.v1`

---

## ⚙️ Automation Engine

**Rule Model**

```json
{
  "name": "High Temp → Cooling Fan ON",
  "enabled": true,
  "condition": {
    "source_id": "greenhouse_temperature",
    "metric":    "value",
    "operator":  ">",
    "threshold": 35.0
  },
  "action": { "actuator_name": "cooling_fan", "state": "ON" }
}
```

Evaluated on **every** incoming event — `SELECT * FROM rules WHERE enabled = true`

**Supported Operators:** `>` gt · `<` lt · `>=` gte · `<=` lte · `=` eq · `!=` neq

**Rule Lifecycle (CRUD)**

| Action | Endpoint | US |
|---|---|---|
| Create | `POST /api/rules` | 13 |
| List / Get | `GET /api/rules` | 14 |
| Edit | `PUT /api/rules/{id}` | 15 |
| Toggle | `PATCH /api/rules/{id}/toggle` | 16 |
| Delete | `DELETE /api/rules/{id}` | 17 |

✅ Persisted in PostgreSQL — survive `docker compose down` · Alembic migration runs automatically on boot

---

## 🖥️ Frontend Dashboard — 7 Pages

| Page | Key Features | User Stories |
|---|---|---|
| **Dashboard** | All sensor cards · live SSE · ok/warning status badges | 1, 2, 3, 4 |
| **Power** | 6 live Recharts line charts (solar array, power bus, consumption) | 5 |
| **Environment** | Radiation + life support cards at top · REST sensor widgets below | 6, 9, 10 |
| **Airlock & Thermal** | State badge IDLE / PRESSURIZING / DEPRESSURIZING · thermal charts | 7, 8 |
| **Actuators** | ON/OFF toggle cards for all 4 actuators · 5 s auto-refresh | 11, 12 |
| **Rules** | RuleForm dialog + RuleTable · full CRUD + enable/disable toggle | 13–18 |
| **Alerts** | Timeline · rule/source dropdowns · SSE live prepend · pagination | 19, 20 |

**Real-time Data Flow**

Page load → `GET /api/state/` (pre-fetch all states) → `EventSource /api/stream` (persistent SSE) → `sensor_update` (update state map) + `alert` (prepend to list) → 3 s auto-reconnect on disconnect

React 18 · TypeScript · Vite · TailwindCSS · Recharts · lucide-react · react-router-dom v6

---

## 🔧 Technology Stack

| Layer | Technology |
|---|---|
| **Ingestion** | Python 3.12 · asyncio · httpx · aio-pika · pydantic v2 |
| **Message Broker** | RabbitMQ 3.13 · fanout exchange · durable · persistent delivery |
| **Processing** | Python 3.12 · SQLAlchemy 2 async · asyncpg · alembic · httpx |
| **State Cache** | Redis 7 · `state:{id}` TTL=3600 s · pub/sub channels |
| **Database** | PostgreSQL 16 · `rules` + `alerts` tables · JSONB columns |
| **API Gateway** | FastAPI · Uvicorn · sse-starlette · CORS middleware · pydantic v2 |
| **Frontend** | React 18 · TypeScript · Vite · TailwindCSS · Recharts · lucide-react |
| **IaC / Serving** | Docker Compose · nginx · 8 containers · named volumes · healthchecks |

**Stats:** 8 Containers · 3 Backend Services · 20 User Stories · 1 `docker compose up` · 5 Days

---

## 🐳 Infrastructure as Code

**One Command Start**

```bash
# One-time: load the simulator OCI image
./source/load-image.sh

# Start the entire platform
cd source && docker compose up
```

**Startup Dependency Chain**

`rabbitmq` + `redis` + `postgres` + `simulator` (all healthy) → `collector` + `rules-engine` → `api :8000` → `frontend :3000`

**Named Volumes**

- `pg_data` — Rules + alerts persist across restarts (US 18 — rule persistence)
- `rabbitmq_data` — Durable messages survive broker restart
- `redis_data` — Cache repopulates within seconds on loss

No manual steps after `docker compose up` · Alembic migrations run automatically on boot

---

## 💡 Lessons Learned

**⚠️ Challenges**

- **Schema diversity** — 8 raw formats required a dispatcher pattern in the normalizer; each schema maps to its own handler function
- **SSE double reconnection** — both collector (→ simulator) and frontend (→ API) needed independent 3 s auto-retry loops
- **Blank dashboard on load** — opening SSE first = empty cards for up to 5 s; fix: pre-fetch `GET /api/state/` *before* opening `EventSource`
- **JSONB alert filtering** — used PostgreSQL `@>` containment operator to filter `source_id` inside the stored JSONB event

**✅ Design Decisions**

- **Fanout exchange** — collector publishes once → any consumer binds its own queue; zero collector changes to add a new service
- **Redis pub/sub relay** — true zero-latency push from rules-engine to API SSE clients; no polling needed
- **Alembic on boot** — `alembic upgrade head` runs at rules-engine startup; schema always in sync, no manual step
- **Exclusive anonymous queues** — no stale messages accumulate on consumer restart; broker stays clean automatically

---

## 🎬 Live Demo

**Demo Script**

1. `docker compose up` — watch all 8 containers reach healthy state
2. **Dashboard** — cards populate instantly (US 4 pre-fetch); values update every 5 s
3. **Power page** — 6 live line charts; show rolling window updating in real-time
4. **Actuators** — manually toggle `cooling_fan` ON → OFF; verify optimistic update
5. **Rules** — create: *greenhouse_temperature > 28 → cooling_fan ON*
6. **Alerts page** — alert appears live; filter by rule and source dropdowns
7. `docker compose down && docker compose up` → rules still there ✅ (US 18)

**Endpoints**

- `http://localhost:3000` — React dashboard
- `http://localhost:8000/docs` — FastAPI interactive docs
- `http://localhost:15672` — RabbitMQ Management UI (guest / guest)

**1 command · 0 manual setup · No blank screens.**

20 User Stories · 8 Containers · 5 Days
