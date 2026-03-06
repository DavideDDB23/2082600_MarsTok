# Mars Operations — Master Project Plan

> **Hackathon:** Laboratory of Advanced Programming — March 2026  
> **Duration:** 5 days  
> **Team size:** 4 developers  
> **Repo:** `DavideDDB23/2082600_MarsTok`

---

## 1. Project Mission

Build a **distributed, event-driven IoT automation platform** that:
1. Ingests heterogeneous sensor/telemetry data from the Mars base simulator (Docker image `mars-iot-simulator:multiarch_v1`)
2. Normalizes all data into a **unified internal event schema**
3. Caches the latest state in-memory for instant dashboard loads
4. Evaluates **IF-THEN automation rules** against each arriving event
5. Triggers actuators automatically when rules fire
6. Streams everything live to a **real-time monitoring dashboard**

Everything boots with a single `docker compose up` — zero manual setup.

---

## 2. Repository Layout (Required)

```
2082600_MarsTok/
├── input.md                    ← System overview + 20 user stories + schemas
├── Student_doc.md              ← Container/microservice deployment spec
├── source/                     ← ALL source code lives here
│   ├── docker-compose.yml
│   ├── .env.example
│   ├── load-image.sh           ← One-time OCI → Docker daemon loader
│   ├── shared/                 ← Shared Pydantic schemas (copied into collector + rules-engine)
│   ├── collector/              ← Ingestion service
│   ├── rules-engine/           ← Rule evaluation + state cache service
│   ├── api/                    ← HTTP/SSE gateway service
│   └── frontend/               ← React dashboard
└── booklets/                   ← LoFi mockups, C4 diagrams, slide deck
```

---

## 3. Technology Stack

| Layer | Technology | Justification |
|---|---|---|
| **Backend services** | Python 3.12 + FastAPI + asyncio | Native async HTTP (`httpx`), SSE, WebSocket; Pydantic v2 for schema enforcement; fastest iteration in a hackathon |
| **Message broker** | RabbitMQ 3.13 (`aio-pika`) | Zero ZooKeeper overhead vs Kafka; ships with management UI on `:15672`; `aio-pika` is a clean async API; more than sufficient for ~200 msg/s |
| **State cache** | Redis 7 | Sub-millisecond key-value reads for latest sensor state; also used as pub/sub bus between rules-engine → api for alert fan-out |
| **Rules + alerts DB** | PostgreSQL 16 + SQLAlchemy 2 + Alembic | JSONB columns hold flexible condition/action blobs; survives restarts; Alembic handles schema migrations automatically on service boot |
| **Frontend** | React 18 + Vite + TypeScript + TailwindCSS + shadcn/ui + Recharts | Fastest scaffold; `EventSource` for SSE; Recharts for real-time line charts; shadcn/ui for polished components with zero custom CSS |
| **Containerization** | Docker + Docker Compose v2 | Mandated by spec; one `docker compose up --build` boots everything |
| **Simulator image** | `mars-iot-simulator:multiarch_v1` (OCI image in `March 2026/`) | Provided; must be loaded into Docker daemon before compose up |

---

## 4. Service Inventory

| Service | Container name | Image / Build | Internal port | Exposed port | Role |
|---|---|---|---|---|---|
| Simulator | `simulator` | `mars-iot-simulator:multiarch_v1` | 8080 | **8080** | Sensor source + actuator target |
| RabbitMQ | `rabbitmq` | `rabbitmq:3.13-management` | 5672 / 15672 | **15672** (mgmt UI) | Message broker |
| Redis | `redis` | `redis:7-alpine` | 6379 | — (internal only) | State cache + pub/sub bus |
| PostgreSQL | `postgres` | `postgres:16-alpine` | 5432 | — (internal only) | Rules + alerts persistence |
| Collector | `collector` | `./collector` | — | — | REST polling + SSE ingestion → RabbitMQ |
| Rules Engine | `rules-engine` | `./rules-engine` | — | — | RabbitMQ consumer → Redis state + rule eval + actuator calls |
| API | `api` | `./api` | 8000 | **8000** | REST + SSE gateway for frontend |
| Frontend | `frontend` | `./frontend` | 80 | **3000** | React dashboard (served by nginx) |

---

## 5. Architecture Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     mars-iot-simulator (:8080)                      │
│  REST sensors: GET /api/sensors/{name}                              │
│  SSE streams:  GET /api/telemetry/stream/{topic}                    │
│  Actuators:    POST /api/actuators/{name}                           │
└───────────────┬────────────────────────────────┬────────────────────┘
                │ poll every 5s / subscribe SSE   │ POST on rule trigger
                ▼                                 │
┌──────────────────────┐                          │
│      COLLECTOR       │                          │
│  Normalise → publish │──── InternalEvent ──▶ RabbitMQ (mars.events fanout)
└──────────────────────┘                          │
                                                  ▼
                                   ┌──────────────────────────┐
                                   │      RULES ENGINE        │
                                   │  1. Write latest state   │──▶ Redis  state:{id}
                                   │  2. Load rules from PG   │──▶ PostgreSQL (read rules)
                                   │  3. Evaluate conditions  │──▶ PostgreSQL (write alerts)
                                   │  4. Trigger actuator     │──▶ simulator POST
                                   │  5. Publish alert event  │──▶ Redis pub/sub mars.alerts
                                   └──────────────────────────┘

                                                  │  Redis pub/sub
                                                  ▼
                                   ┌──────────────────────────┐
                                   │           API            │
                                   │  GET  /api/state         │◀── Redis
                                   │  GET  /api/actuators     │◀── simulator proxy
                                   │  POST /api/actuators/{n} │──▶ simulator proxy
                                   │  CRUD /api/rules         │◀▶─ PostgreSQL
                                   │  GET  /api/alerts        │◀── PostgreSQL
                                   │  GET  /api/stream (SSE)  │◀── Redis pub/sub
                                   └──────────┬───────────────┘
                                              │ SSE + REST
                                              ▼
                                   ┌──────────────────────────┐
                                   │        FRONTEND          │
                                   │  React 18 + Vite         │
                                   │  Dashboard, Charts,      │
                                   │  Actuators, Rules, Alerts│
                                   └──────────────────────────┘
```

---

## 6. Port Map (exposed on host)

| Port | Service | URL |
|---|---|---|
| 3000 | Frontend (nginx) | http://localhost:3000 |
| 8000 | API (FastAPI) | http://localhost:8000/docs |
| 8080 | Simulator | http://localhost:8080 |
| 15672 | RabbitMQ Management UI | http://localhost:15672 (guest/guest) |

---

## 7. Environment Variables (`.env.example`)

```env
# Simulator
SIMULATOR_BASE_URL=http://simulator:8080

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
RABBITMQ_EXCHANGE=mars.events

# Redis
REDIS_URL=redis://redis:6379

# PostgreSQL
POSTGRES_DSN=postgresql+asyncpg://mars:mars@postgres:5432/mars
POSTGRES_USER=mars
POSTGRES_PASSWORD=mars
POSTGRES_DB=mars

# API
API_BASE_URL=http://api:8000

# Collector
POLL_INTERVAL_SECONDS=5
```

---

## 8. Simulator API Reference (Quick Reference)

### REST Sensors (`GET /api/sensors/{name}`)
| Sensor name | Schema | Key fields |
|---|---|---|
| `greenhouse_temperature` | `rest.scalar.v1` | `value`, `unit`, `status` |
| `entrance_humidity` | `rest.scalar.v1` | `value`, `unit`, `status` |
| `co2_hall` | `rest.scalar.v1` | `value`, `unit`, `status` |
| `corridor_pressure` | `rest.scalar.v1` | `value`, `unit`, `status` |
| `hydroponic_ph` | `rest.chemistry.v1` | `measurements[]` |
| `air_quality_voc` | `rest.chemistry.v1` | `measurements[]` |
| `air_quality_pm25` | `rest.particulate.v1` | `pm1_ug_m3`, `pm25_ug_m3`, `pm10_ug_m3` |
| `water_tank_level` | `rest.level.v1` | `level_pct`, `level_liters` |

### Telemetry Topics (SSE: `GET /api/telemetry/stream/{topic}`, WS: `WS /api/telemetry/ws?topic={topic}`)
| Topic | Schema | Key fields |
|---|---|---|
| `mars/telemetry/solar_array` | `topic.power.v1` | `power_kw`, `voltage_v`, `current_a`, `cumulative_kwh` |
| `mars/telemetry/power_bus` | `topic.power.v1` | same |
| `mars/telemetry/power_consumption` | `topic.power.v1` | same |
| `mars/telemetry/radiation` | `topic.environment.v1` | `measurements[]`, `status` |
| `mars/telemetry/life_support` | `topic.environment.v1` | `measurements[]`, `status` |
| `mars/telemetry/thermal_loop` | `topic.thermal_loop.v1` | `temperature_c`, `flow_l_min`, `status` |
| `mars/telemetry/airlock` | `topic.airlock.v1` | `cycles_per_hour`, `last_state` |

### Discovery
- `GET /api/discovery` — returns all available sensors and topics
- `GET /api/actuators` — returns all actuators and their current state

---

## 9. Day-by-Day Schedule

### Day 1 — Foundation (All hands)
| Time | Activity |
|---|---|
| Morning | Load OCI image, verify `docker compose up` with just simulator + infra; hit `GET /api/discovery` to confirm exact sensor/actuator names |
| Morning | Agree on unified `InternalEvent` JSON schema (see `DATA_SCHEMAS.md`); write shared Pydantic models in `source/shared/schemas.py` |
| Afternoon | Dev A: complete `docker-compose.yml` + all Dockerfiles + `.env.example` |
| Afternoon | Dev B: scaffold `collector/` with Dockerfile + requirements; implement `config.py` and `rest_poller.py` |
| Afternoon | Dev C: scaffold `rules-engine/` + `api/`; implement Alembic migrations; implement `state_store.py` |
| Afternoon | Dev D: scaffold `frontend/` with Vite + Tailwind; implement Sidebar + routing |
| EOD | Integration checkpoint: collector publishes at least one event to RabbitMQ |

### Day 2 — Core Ingestion + State
| Owner | Work |
|---|---|
| Dev B | Complete `sse_subscriber.py` + `normalizer.py` + `publisher.py`; collector fully functional for all 8 REST sensors and all 7 telemetry topics |
| Dev C | Implement `consumer.py` in rules-engine; implement `state_store.py` (Redis writes); verify state is persisted in Redis |
| Dev C | Implement `GET /api/state` and `GET /api/state/{source_id}` in API; test with curl |
| Dev D | Implement `Dashboard.tsx` reading from `/api/state`; implement `SensorWidget.tsx` + `StatusBadge.tsx` |
| Dev A | docker-compose health checks + restart policies; test full boot sequence |

### Day 3 — Rules Engine + Actuator Control
| Owner | Work |
|---|---|
| Dev C | Implement `evaluator.py` (load rules from PG, evaluate conditions, call actuator, write alert, publish to Redis) |
| Dev C | Implement full CRUD `/api/rules` + `GET /api/alerts` + `POST /api/actuators/{name}` |
| Dev B | Implement `GET /api/stream` SSE endpoint that relays Redis pub/sub to browser |
| Dev D | Implement `Actuators.tsx` + `ActuatorCard.tsx` (toggle + live state) |
| Dev D | Implement `Rules.tsx` + `RuleForm.tsx` + `RuleTable.tsx` |
| EOD | Integration checkpoint: create a rule in the UI, trigger it by sensor data, see actuator switch |

### Day 4 — Telemetry Panels + Real-Time Charts
| Owner | Work |
|---|---|
| Dev D | Implement `Power.tsx` with 3 Recharts `<LineChart>` fed by SSE |
| Dev D | Implement `Environment.tsx` (radiation + life_support) and `AirlockThermal.tsx` |
| Dev D | Implement `Alerts.tsx` + `AlertTimeline.tsx` |
| Dev B | Ensure SSE stream sends both `sensor_update` and `alert` typed events to frontend |
| Dev C | Add pagination to `/api/alerts`; add `?rule_id` and `?source_id` filter query params |
| Dev A | Write `source/load-image.sh`; test clean-machine bootstrap; fix any compose issues |

### Day 5 — Polish, Documentation & Booklets
| Owner | Work |
|---|---|
| All | Fill `input.md` and `Student_doc.md` completely |
| Dev A | Write `booklets/architecture/` — C4 Context + Container diagrams |
| Dev D | Write `booklets/mockups/` — one LoFi sketch per user story group |
| All | Create `booklets/presentation/` — 10-slide deck |
| All | Final smoke test from a fresh `git clone` |

---

## 10. Definition of Done

- [x] `docker compose up --build` starts all services from zero with no manual steps
- [x] Simulator OCI image loads automatically via `load-image.sh` (or compose `pre-pull` hook)
- [x] Dashboard shows live sensor values that refresh ≤ 10 s
- [x] All 7 telemetry topics stream in real-time to the frontend
- [x] User can create/edit/delete/toggle rules via the UI
- [x] At least one rule auto-triggers an actuator call within 10 s of condition being met
- [x] Alert log persists across container restarts
- [x] `input.md` complete with system description, 20 user stories, event schema, rule model
- [x] `Student_doc.md` complete with all container specs, endpoints, DB tables
- [ ] `booklets/` contains mockups, C4 diagrams, and presentation slides
- [ ] All source code in `source/`; repo pushed to `DavideDDB23/2082600_MarsTok`

---

## 11. Team Assignments Summary

| Developer | Primary Ownership |
|---|---|
| **Dev A** | `docker-compose.yml`, all Dockerfiles, `load-image.sh`, `.env.example`, infra health checks, `booklets/architecture/` |
| **Dev B** | `source/collector/` (REST polling, SSE subscription, normalization, RabbitMQ publish), SSE relay in `api/routers/stream.py` |
| **Dev C** | `source/rules-engine/` (consumer, evaluator, state store, actuator client), `source/api/` (all routers + DB models) |
| **Dev D** | `source/frontend/` (all pages, components, charts, SSE hook), `booklets/mockups/` |
