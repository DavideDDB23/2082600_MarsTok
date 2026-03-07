# SYSTEM DESCRIPTION:

Mars Operations is a distributed, event-driven IoT automation platform for monitoring and controlling a Mars base habitat. It ingests heterogeneous sensor and telemetry data from a Mars base simulator, normalizes it into a unified event format, evaluates IF-THEN automation rules, triggers actuators automatically, and exposes everything through a real-time dashboard.

# USER STORIES:

1) As an operator, I want to see all live sensor readings on a unified dashboard so that I can monitor the base status at a glance.
2) As an operator, I want sensor status badges (ok/warning) highlighted visually so that I can immediately identify which sensors are in anomalous states.
3) As an operator, I want the dashboard to update in real-time without manual page refresh so that I always see the most current data.
4) As an operator, I want to see the latest sensor state immediately on page load so that I never face a blank dashboard.
5) As an operator, I want to see live line charts for power metrics so that I can analyze energy trends over time.
6) As an operator, I want to see real-time radiation and life support measurements so that I can monitor crew safety.
7) As an operator, I want to see thermal loop temperature and flow rate in real-time so that I can detect cooling failures.
8) As an operator, I want to see the airlock state and cycles-per-hour so that I can track EVA activity.
9) As an operator, I want to see environmental sensors (temperature, humidity, CO2, pressure) so that I can ensure habitat integrity.
10) As an operator, I want to see air quality data (VOC, PM2.5, water pH) so that I can ensure breathable air.
11) As an operator, I want to see the current ON/OFF state of all actuators so that I know the system configuration.
12) As an operator, I want to manually toggle any actuator ON or OFF so that I can respond to emergencies.
13) As an operator, I want to create an IF-THEN automation rule so that the platform reacts automatically.
14) As an operator, I want to list all automation rules so that I can audit the automation logic.
15) As an operator, I want to edit an existing rule so that I can tune thresholds and actions.
16) As an operator, I want to enable or disable a rule without deleting it so that I can test changes safely.
17) As an operator, I want to delete a rule so that I can keep the rule list clean.
18) As an operator, I want rules to persist across restarts so that I never lose my configuration.
19) As an operator, I want to see a chronological alert log so that I can audit all automated actions.
20) As an operator, I want to filter the alert log by rule or sensor so that I can investigate specific issues.


# CONTAINERS:

## CONTAINER_NAME: Collector

### DESCRIPTION:
Ingests all sensor data from the Mars base simulator. Polls 8 REST sensors every 5 seconds and maintains persistent SSE subscriptions to all 7 telemetry topics. Normalizes every raw payload from 8 different simulator schemas into a single unified InternalEvent format and publishes it to the RabbitMQ message broker.

### USER STORIES:
1) As an operator, I want to see all live sensor readings on a unified dashboard so that I can monitor the base status at a glance.
3) As an operator, I want the dashboard to update in real-time without manual page refresh.
5) As an operator, I want to see live line charts for power metrics.
6) As an operator, I want to see real-time radiation and life support measurements.
7) As an operator, I want to see thermal loop temperature and flow rate in real-time.
8) As an operator, I want to see the airlock state and cycles-per-hour.
9) As an operator, I want to see environmental sensors.
10) As an operator, I want to see air quality data.

### PORTS:
None (no HTTP port exposed; pure worker)

### DESCRIPTION:
The Collector container is a stateless async worker. It establishes HTTP connections to the simulator and produces normalized events to RabbitMQ.

### PERSISTENCE EVALUATION
The Collector does not require data persistence. It is a pure ingestion worker. Any lost events during downtime are simply skipped (the simulator continuously generates new ones).

### EXTERNAL SERVICES CONNECTIONS
Connects to:
- `mars-iot-simulator:8080` — source of all sensor and telemetry data
- `rabbitmq:5672` — publishes InternalEvents to the `mars.events` fanout exchange

### MICROSERVICES:

#### MICROSERVICE: collector
- TYPE: backend
- DESCRIPTION: Asynchronous Python worker that polls REST sensors and subscribes to SSE telemetry streams from the simulator, normalizes all payloads, and publishes InternalEvents to RabbitMQ.
- PORTS: None
- TECHNOLOGICAL SPECIFICATION:
  The microservice is developed in Python 3.12 and uses:
  - `httpx[asyncio]` for async HTTP/REST polling and SSE stream consumption
  - `aio-pika` for async RabbitMQ publishing via AMQP
  - `pydantic` v2 for InternalEvent schema validation and serialization
  - `asyncio` for concurrent polling and streaming tasks
- SERVICE ARCHITECTURE:
  Single async `main()` function spawns two concurrent long-running coroutines via `asyncio.gather()`:
  1. `polling_loop()` — cycles through all 8 REST sensors every `POLL_INTERVAL_SECONDS` using `asyncio.gather()` for parallel requests
  2. `subscribe_all_topics()` — spawns one persistent SSE connection per telemetry topic; each reconnects automatically on disconnect
  All raw payloads pass through `normalizer.normalize()` which dispatches on schema type and returns an `InternalEvent`. The `publisher.publish_event()` function serializes and sends to the RabbitMQ fanout exchange.

- ENDPOINTS:
  None (no HTTP server)


---

## CONTAINER_NAME: Rules Engine

### DESCRIPTION:
The Rules Engine is the core processing layer. It consumes every InternalEvent from RabbitMQ, writes the latest state to Redis, evaluates all enabled automation rules, triggers actuators on the simulator when conditions are met, persists alert records to PostgreSQL, and publishes alert notifications to a Redis pub/sub channel.

### USER STORIES:
3) As an operator, I want the dashboard to update in real-time without manual page refresh.
4) As an operator, I want to see the latest sensor state immediately on page load.
13) As an operator, I want to create an IF-THEN automation rule so that the platform reacts automatically.
18) As an operator, I want rules to persist across platform restarts.
19) As an operator, I want to see a chronological alert log.

### PORTS:
None (no HTTP port exposed; pure consumer/worker)

### DESCRIPTION:
The Rules Engine is a stateful async worker. It maintains connections to RabbitMQ (consumer), Redis (state writes + pub/sub), and PostgreSQL (rules read + alerts write).

### PERSISTENCE EVALUATION
The Rules Engine requires persistence for:
- **Rules** (PostgreSQL `rules` table): IF-THEN rules created by the operator survive restarts
- **Alerts** (PostgreSQL `alerts` table): History of all rule-triggered events
- **Latest state** (Redis `state:{source_id}` keys, TTL=1h): Not persistent across Redis restarts, but repopulated automatically within seconds of boot

### EXTERNAL SERVICES CONNECTIONS
Connects to:
- `rabbitmq:5672` — consumes via an exclusive anonymous queue bound to the `mars.events` fanout exchange
- `redis:6379` — writes state cache keys; publishes to `mars.events` and `mars.alerts` pub/sub channels
- `postgres:5432` — reads rules, writes alerts
- `mars-iot-simulator:8080` — POST requests to trigger actuators

### MICROSERVICES:

#### MICROSERVICE: rules-engine
- TYPE: backend
- DESCRIPTION: Async consumer that processes InternalEvents, caches state in Redis, evaluates rules from PostgreSQL, triggers actuators, and records alerts.
- PORTS: None
- TECHNOLOGICAL SPECIFICATION:
  Developed in Python 3.12 with:
  - `aio-pika` for async AMQP consumption
  - `redis[asyncio]` for async Redis read/write and pub/sub
  - `sqlalchemy[asyncio]` + `asyncpg` for async PostgreSQL access
  - `alembic` for automatic schema migrations on service boot
  - `httpx[asyncio]` for actuator POST requests to simulator
  - `pydantic` v2 for event deserialization
- SERVICE ARCHITECTURE:
  On startup: runs `alembic upgrade head` to ensure DB schema is current, then connects to all dependencies with retry loops.
  Consumer loop: for each RabbitMQ message:
  1. Deserialize to `InternalEvent`
  2. Write `state:{source_id}` key to Redis with 1h TTL
  3. Publish raw event JSON to Redis pub/sub channel `mars.events`
  4. Load all enabled rules from PostgreSQL
  5. For each matching rule, evaluate the condition operator
  6. On match: POST to simulator actuator, insert `Alert` row in PostgreSQL, publish alert JSON to Redis pub/sub `mars.alerts`
  7. ACK RabbitMQ message

- DB STRUCTURE:

  **_rules_** : | **_id_** (UUID PK) | name (TEXT) | enabled (BOOL) | condition (JSONB) | action (JSONB) | created_at (TIMESTAMPTZ) | updated_at (TIMESTAMPTZ) |

  **_alerts_** : | **_id_** (UUID PK) | rule_id (UUID FK→rules.id) | rule_name (TEXT NOT NULL) | triggered_event (JSONB) | triggered_at (TIMESTAMPTZ) |


---

## CONTAINER_NAME: API

### DESCRIPTION:
The HTTP and SSE gateway between the frontend and all backend services. Provides REST endpoints for reading sensor state, managing rules, browsing alert history, and proxying actuator commands to the simulator. Also exposes a single SSE endpoint that subscribes to Redis pub/sub and streams live events and alerts to the frontend.

### USER STORIES:
1) As an operator, I want to see all live sensor readings on a unified dashboard.
2) As an operator, I want sensor status badges highlighted visually.
3) As an operator, I want the dashboard to update in real-time.
4) As an operator, I want to see the latest sensor state immediately on page load.
11) As an operator, I want to see the current ON/OFF state of all actuators.
12) As an operator, I want to manually toggle any actuator ON or OFF.
13) As an operator, I want to create an IF-THEN automation rule.
14) As an operator, I want to list all automation rules.
15) As an operator, I want to edit an existing rule.
16) As an operator, I want to enable or disable a rule.
17) As an operator, I want to delete a rule.
19) As an operator, I want to see a chronological alert log.
20) As an operator, I want to filter the alert log by rule or sensor.

### PORTS:
8000:8000

### DESCRIPTION:
The API container is a FastAPI application served by Uvicorn. It has no internal business logic — it reads from Redis and PostgreSQL and proxies to the simulator. It acts as the single integration point for the frontend.

### PERSISTENCE EVALUATION
The API service does not own any persistent storage. It reads and writes PostgreSQL (full CRUD on rules; read and delete on alerts) and reads Redis (state cache). All persistent data is owned and migrated by the Rules Engine container.

### EXTERNAL SERVICES CONNECTIONS
Connects to:
- `redis:6379` — reads state cache; subscribes to pub/sub for SSE relay
- `postgres:5432` — reads and writes rules; reads alerts
- `mars-iot-simulator:8080` — proxies actuator GET and POST requests

### MICROSERVICES:

#### MICROSERVICE: api
- TYPE: backend
- DESCRIPTION: FastAPI HTTP + SSE gateway exposing all platform capabilities to the frontend.
- PORTS: 8000
- TECHNOLOGICAL SPECIFICATION:
  Developed in Python 3.12 with:
  - `fastapi` + `uvicorn[standard]` for the ASGI HTTP server
  - `sqlalchemy[asyncio]` + `asyncpg` for async PostgreSQL access
  - `redis[asyncio]` for async Redis reads and pub/sub subscriptions
  - `httpx[asyncio]` for proxying requests to the simulator
  - `pydantic` v2 for request/response validation
- SERVICE ARCHITECTURE:
  Single FastAPI app with 5 routers mounted under `/api`. CORS middleware allows requests from the frontend origin. The `/api/stream` endpoint uses `StreamingResponse` with an async generator that subscribes to Redis pub/sub and yields SSE-formatted lines.

- ENDPOINTS:

  | HTTP METHOD | URL | Description | User Stories |
  | ----------- | --- | ----------- | ------------ |
  | GET | /api/health | Health check | — |
  | GET | /api/state | Returns all latest sensor states from Redis | 1, 4 |
  | GET | /api/state/{source_id} | Returns latest state for one sensor | 1, 2, 4 |
  | GET | /api/actuators | Proxies GET /api/actuators from simulator | 11 |
  | POST | /api/actuators/{name} | Proxies POST to simulator; body: {"state":"ON\|OFF"} | 12 |
  | GET | /api/rules | Returns all rules from PostgreSQL | 14 |
  | POST | /api/rules | Creates a new rule | 13 |
  | GET | /api/rules/{rule_id} | Returns a single rule | 14, 15 |
  | PUT | /api/rules/{rule_id} | Full update of a rule | 15 |
  | PATCH | /api/rules/{rule_id} | Sets rule enabled state; body: {"enabled": true/false} | 16 |
  | PATCH | /api/rules/{rule_id}/toggle | Flips the enabled boolean | 16 |
  | DELETE | /api/rules/{rule_id} | Deletes a rule | 17 |
  | GET | /api/alerts | Returns paginated alerts; query: ?rule_id=, ?source_id=, ?limit=, ?offset= | 19, 20 |
  | GET | /api/alerts/{alert_id} | Returns a single alert | 19 |
  | DELETE | /api/alerts/{alert_id} | Deletes an alert | 19 |
  | GET | /api/stream | SSE stream: sensor_update and alert events from Redis pub/sub | 3, 5, 6, 7, 8, 19 |
  | GET | /api/stream/events | SSE stream: sensor_update events only | 3 |
  | GET | /api/stream/alerts | SSE stream: alert events only | 19 |

- DB STRUCTURE:

  **_rules_** : | **_id_** (UUID PK) | name (TEXT) | enabled (BOOL) | condition (JSONB) | action (JSONB) | created_at (TIMESTAMPTZ) | updated_at (TIMESTAMPTZ) |

  **_alerts_** : | **_id_** (UUID PK) | rule_id (UUID FK→rules.id) | rule_name (TEXT NOT NULL) | triggered_event (JSONB) | triggered_at (TIMESTAMPTZ) |


---

## CONTAINER_NAME: Frontend

### DESCRIPTION:
Real-time monitoring dashboard for Mars base operators. Displays live sensor values, telemetry charts, actuator controls, a rule management interface, and an alert timeline. Built as a Single Page Application served by nginx.

### USER STORIES:
1) As an operator, I want to see all live sensor readings on a unified dashboard.
2) As an operator, I want sensor status badges highlighted visually.
3) As an operator, I want the dashboard to update in real-time.
4) As an operator, I want to see the latest sensor state on page load.
5) As an operator, I want to see live line charts for power metrics.
6) As an operator, I want to see radiation and life support measurements.
7) As an operator, I want to see thermal loop data in real-time.
8) As an operator, I want to see airlock state and cycles.
9) As an operator, I want to see environmental sensors.
10) As an operator, I want to see air quality data.
11) As an operator, I want to see actuator states.
12) As an operator, I want to manually toggle actuators.
13) As an operator, I want to create automation rules.
14) As an operator, I want to list automation rules.
15) As an operator, I want to edit a rule.
16) As an operator, I want to enable/disable a rule.
17) As an operator, I want to delete a rule.
19) As an operator, I want to see an alert log.
20) As an operator, I want to filter the alert log.

### PORTS:
3000:80

### DESCRIPTION:
The Frontend container is a React 18 SPA built with Vite and served by nginx. It communicates exclusively with the API service via REST calls and one persistent SSE connection.

### PERSISTENCE EVALUATION
No persistence. The frontend is stateless; all data is fetched from the API service on load and kept in memory via React state and the SSE hook.

### EXTERNAL SERVICES CONNECTIONS
Connects to:
- `api:8000` — all REST calls and SSE stream (via nginx reverse proxy: `/api/` → `http://api:8000/api/`)

### MICROSERVICES:

#### MICROSERVICE: frontend
- TYPE: frontend
- DESCRIPTION: React 18 Single Page Application with real-time dashboard, power charts, environment panels, actuator controls, rule management, and alert history.
- PORTS: 80 (nginx; exposed as 3000 on host)
- TECHNOLOGICAL SPECIFICATION:
  Built with:
  - React 18 + TypeScript + Vite (build tool)
  - TailwindCSS for styling, lucide-react for icons
  - Recharts for live line charts
  - react-router-dom v6 for client-side routing
  - Native `EventSource` API for SSE consumption
  - nginx for production serving and API proxying

- PAGES:

  | Name | Description | Related Microservice | User Stories |
  | ---- | ----------- | -------------------- | ------------ |
  | Dashboard | Grid of SensorWidget cards for all sensors; updates live via SSE | api | 1, 2, 3, 4, 9, 10 |
  | Power | Six live Recharts LineCharts for solar array, power bus, and consumption metrics (power, voltage, current, cumulative) | api | 5 |
  | Environment | Life support & radiation telemetry cards with status badges, environmental REST sensor widgets (temperature, humidity, CO₂, pressure, air quality, water level), and live trend charts | api | 6, 9, 10 |
  | Airlock & Thermal | Airlock state badge + thermal loop LiveChart | api | 7, 8 |
  | Actuators | ActuatorCard toggles for all actuators with live state | api | 11, 12 |
  | Rules | RuleTable + RuleForm dialog for full CRUD + enable/disable | api | 13, 14, 15, 16, 17, 18 |
  | Alerts | AlertTimeline with filter bar; live alerts prepended from SSE | api | 19, 20 |


---

## CONTAINER_NAME: Infrastructure

### DESCRIPTION:
Supporting infrastructure containers managed by Docker Compose. No application logic.

### USER STORIES:
18) As an operator, I want rules to persist across platform restarts.
3) As an operator, I want the dashboard to update in real-time.

### PORTS:
15672:15672 (RabbitMQ Management UI)

### DESCRIPTION:
Three infrastructure services: message broker, state cache, and relational database.

### PERSISTENCE EVALUATION
- **RabbitMQ**: messages are durable; persisted in `rabbitmq_data` Docker volume
- **Redis**: state cache; `redis_data` volume (optional, repopulates quickly on restart)
- **PostgreSQL**: primary persistence for rules and alerts; `pg_data` Docker volume

### EXTERNAL SERVICES CONNECTIONS
None.

### MICROSERVICES:

#### MICROSERVICE: rabbitmq
- TYPE: backend
- DESCRIPTION: RabbitMQ 3.13 message broker with management UI. Hosts the `mars.events` fanout exchange.
- PORTS: 15672 (management UI)
- TECHNOLOGICAL SPECIFICATION:
  Image: `rabbitmq:3.13-management`. Default credentials: guest/guest. Fanout exchange `mars.events` declared by Collector on startup.
- SERVICE ARCHITECTURE:
  Single broker instance. Exchange: `mars.events` (fanout, durable). Queues: one durable queue per consumer service bound to the exchange.

#### MICROSERVICE: redis
- TYPE: backend
- DESCRIPTION: Redis 7 in-memory data store. Used as state cache (latest sensor values) and pub/sub bus (live event relay to API SSE endpoint).
- PORTS: 6379 (internal only)
- TECHNOLOGICAL SPECIFICATION:
  Image: `redis:7-alpine`. No authentication required for internal Docker network use.
- SERVICE ARCHITECTURE:
  Two logical uses: (1) String keys `state:{source_id}` for latest InternalEvent JSON, TTL=3600s. (2) Pub/sub channels `mars.events` and `mars.alerts` for live fan-out to SSE clients.

#### MICROSERVICE: postgres
- TYPE: backend
- DESCRIPTION: PostgreSQL 16 relational database. Stores automation rules and alert history.
- PORTS: 5432 (internal only)
- TECHNOLOGICAL SPECIFICATION:
  Image: `postgres:16-alpine`. Database: `mars`. User/password: `mars/mars`. Schema managed by Alembic migrations run by the rules-engine service on startup.
- SERVICE ARCHITECTURE:
  Two tables: `rules` and `alerts`. See DB STRUCTURE above.

- DB STRUCTURE:

  **_rules_** : | **_id_** (UUID PK) | name (TEXT NOT NULL) | enabled (BOOL DEFAULT TRUE) | condition (JSONB NOT NULL) | action (JSONB NOT NULL) | created_at (TIMESTAMPTZ) | updated_at (TIMESTAMPTZ) |

  **_alerts_** : | **_id_** (UUID PK) | rule_id (UUID FK→rules) | rule_name (TEXT NOT NULL) | triggered_event (JSONB NOT NULL) | triggered_at (TIMESTAMPTZ) |
