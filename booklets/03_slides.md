---
marp: true
theme: default
paginate: true
backgroundColor: #0f172a
color: #e2e8f0
style: |
  section {
    font-family: 'Segoe UI', sans-serif;
    padding: 40px 60px;
  }
  h1 { color: #f97316; font-size: 2.2em; }
  h2 { color: #fb923c; border-bottom: 2px solid #f97316; padding-bottom: 8px; }
  h3 { color: #fdba74; }
  code { background: #1e293b; padding: 2px 6px; border-radius: 4px; }
  table { width: 100%; }
  th { background: #1e3a5f; color: #93c5fd; }
  td { border-bottom: 1px solid #334155; }
  strong { color: #fb923c; }
  .small { font-size: 0.75em; }
---

# 🔴 Mars Operations
## Distributed IoT Automation Platform

**Lab of Advanced Programming 2025/2026**
Hackathon — March 2026

Student ID: **2082600**

---

## Mission Briefing

> *"Mars 2036. Your automation stack is partially destroyed. Devices speak incompatible dialects. Rebuild it — or face thermodynamic consequences."*

### The Problem
- Mars habitat generates **heterogeneous** sensor data
- Devices use **two transport protocols**: REST polling + SSE streams
- Operators need **real-time visibility** and **automatic responses**
- All state must survive service restarts

### Our Solution
A fully **event-driven**, **containerised** automation platform with:
- Unified data normalisation pipeline
- IF-THEN rule engine with actuator control
- Real-time React dashboard

---

## System Architecture

```
  ┌───────────────────────────────────────────────────────┐
  │                mars-iot-simulator :8080               │
  │  8 REST sensors (poll 5s)  │  7 SSE telemetry topics  │
  └──────────────┬─────────────┴────────────┬─────────────┘
                 │ HTTP/SSE                  │ SSE
                 ▼                          ▼
          ┌──────────────┐         ┌───────────────────────┐
          │  collector   │──AMQP──►│  RabbitMQ 3.13        │
          │ (Python/asyncio)│      │  fanout: mars.events  │
          └──────────────┘         └───────────┬───────────┘
                                               │ consume
                                               ▼
     ┌─────────────────────────────────────────────────────┐
     │                  rules-engine (Python/asyncio)      │
     │  • State cache write → Redis                        │
     │  • Evaluate rules → PostgreSQL                      │
     │  • Trigger actuators → simulator                    │
     │  • Publish alerts → Redis pub/sub                   │
     └───────────────────────┬─────────────────────────────┘
                Redis/PG     │
                             ▼
                    ┌─────────────────┐
                    │  api (FastAPI)  │──SSE──► frontend (React 18 / nginx)
                    │  port 8000      │◄─REST──  port 3000
                    └─────────────────┘
```

---

## Data Pipeline — From Sensor to Dashboard

1. **Ingest** — Collector polls 8 REST endpoints every 5 s; maintains 7 persistent SSE connections

2. **Normalise** — 8 raw schemas → 1 `InternalEvent` (UUID, timestamp, source_id, category, metrics[], status)

3. **Publish** — InternalEvent sent to RabbitMQ `mars.events` fanout (PERSISTENT delivery)

4. **Process** — Rules Engine consumes, writes `state:{id}` to Redis (TTL 1h), evaluates all enabled rules

5. **Alert** — On rule match: POST actuator to simulator + INSERT alert to PostgreSQL + PUBLISH to Redis

6. **Stream** — API subscribes to Redis pub/sub, relays as named SSE events to the browser

7. **Render** — React SSE hook (`useSSE`) pre-fetches all states on load, then merges live events

---

## Automation Engine

### Rule Model

```json
{
  "condition": { "source_id": "greenhouse_temperature",
                 "metric": "value", "operator": "gt", "threshold": 35.0 },
  "action":    { "actuator_name": "cooling_fan", "state": "ON" }
}
```

### Operators: `gt` `lt` `gte` `lte` `eq` `neq`

### Lifecycle
| Action | Endpoint | US |
|---|---|---|
| Create | `POST /api/rules` | 13 |
| List / Get | `GET /api/rules` | 14 |
| Edit | `PUT /api/rules/{id}` | 15 |
| Enable / Disable | `PATCH /api/rules/{id}/toggle` | 16 |
| Delete | `DELETE /api/rules/{id}` | 17 |
| **Persist across restarts** | PostgreSQL + pg_data volume | **18** |

---

## Frontend Dashboard — 7 Pages

| Page | Key Features | User Stories |
|---|---|---|
| **Dashboard** | All sensor cards, live SSE updates, status badges | 1, 2, 3, 4 |
| **Power** | 6 Recharts line charts (solar, bus, consumption) | 5 |
| **Environment** | Radiation/life_support at top; REST sensor widgets | 6, 9, 10 |
| **Airlock & Thermal** | Airlock state badge (IDLE/PRESSURIZING/…); thermal charts | 7, 8 |
| **Actuators** | ON/OFF toggle cards, 5 s auto-refresh | 11, 12 |
| **Rules** | RuleForm + RuleTable, full CRUD + toggle | 13–18 |
| **Alerts** | Timeline, rule/source dropdowns, SSE prepend, pagination | 19, 20 |

### Real-time Architecture
- `useSSE` hook: pre-fetches `/api/state/` → opens `EventSource /api/stream`
- Named events: `sensor_update` → updates `sensorStates` map; `alert` → prepends to alert list
- 3 s auto-reconnect on disconnect

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Ingestion** | Python 3.12, asyncio, httpx, aio-pika, pydantic v2 |
| **Message Broker** | RabbitMQ 3.13 (fanout exchange, durable, persistent) |
| **Processing** | Python 3.12, asyncio, SQLAlchemy 2 async, asyncpg, alembic |
| **State Cache** | Redis 7 — `state:{id}` TTL=3600 s + pub/sub channels |
| **Database** | PostgreSQL 16 — `rules` + `alerts` tables (JSONB columns) |
| **API** | FastAPI, Uvicorn, sse-starlette, CORS middleware |
| **Frontend** | React 18, TypeScript, Vite, TailwindCSS, Recharts, lucide-react |
| **Serving** | nginx (SPA fallback + `/api/` reverse proxy) |
| **IaC** | Docker Compose — 8 containers, healthchecks, named volumes |

---

## Docker Compose — One Command Start

```bash
# Load provided simulator image (one-time)
./source/load-image.sh

# Start everything
cd source && docker compose up
```

**8 containers:** `mars-iot-simulator`, `rabbitmq`, `redis`, `postgres`, `collector`, `rules-engine`, `api`, `frontend`

**Startup order:** infrastructure → simulator → collector + rules-engine → api → frontend

**Healthchecks** ensure each service waits for its dependencies (`condition: service_healthy`)

**Volumes:**
- `pg_data` — rule and alert persistence (US 18)
- `rabbitmq_data` — durable message persistence
- `redis_data` — optional state cache persistence

---

## Lessons Learned

### Challenges
- **Schema diversity** — 8 raw payload formats required a clean dispatcher pattern in the normalizer
- **SSE reconnection** — both the collector (simulator topics) and frontend (API stream) needed resilient auto-reconnect loops
- **Race conditions** — pre-fetching state before opening SSE prevented blank-dashboard on load (US 4)
- **JSONB filtering** — PostgreSQL JSONB operator `@>` used to filter alerts by `source_id` inside `triggered_event`

### Key Design Decisions
- **Fanout exchange** → decouples collector from all consumers; adding a new service requires zero collector changes
- **Redis pub/sub** → zero-latency relay from rules-engine to API SSE clients without polling
- **Alembic migrations** → schema-as-code; rules-engine runs `alembic upgrade head` on every boot

---

## Live Demo

### Demo Script
1. `docker compose up` — show all 8 containers healthy
2. **Dashboard** — live sensor values updating every 5 s
3. **Power page** — 6 line charts updating in real-time
4. **Actuators** — manually toggle `cooling_fan` ON/OFF
5. **Rules** — create rule: `greenhouse_temperature > 28 → cooling_fan ON`
6. Watch rule trigger automatically → alert appears in **Alerts** page
7. **Filter alerts** by rule name / source dropdown
8. `docker compose down && docker compose up` — rules survive restart (US 18)

### Endpoints
- Dashboard: http://localhost:3000
- API docs: http://localhost:8000/docs
- RabbitMQ UI: http://localhost:15672 (guest/guest)
