# Mars Operations — Full Task Checklist

> Track progress by checking off items as they are completed.  
> Items are organized by **Developer** → **Service** → **File**.  
> See `MASTER_PLAN.md` for architecture and `DATA_SCHEMAS.md` for all data contracts.

---

## Phase 0 — Day 1 Morning: Shared Setup (All Devs)

- [ ] Load OCI image into Docker daemon:
  ```bash
  cd "March 2026/mars-iot-simulator-oci"
  skopeo copy oci:. docker-daemon:mars-iot-simulator:multiarch_v1
  # OR if skopeo not available:
  # docker load < (skopeo copy oci:. docker-archive:/dev/stdout)
  ```
- [ ] Verify simulator boots: `docker run --rm -p 8080:8080 mars-iot-simulator:multiarch_v1`
- [ ] Hit `GET http://localhost:8080/api/discovery` — save the full JSON response to `source/docs/discovery.json`
- [ ] Hit `GET http://localhost:8080/api/actuators` — note all actuator names (needed for `config.py`)
- [x] All 4 devs agree on `InternalEvent` schema (see `DATA_SCHEMAS.md`) — no changes after Day 1
- [x] Create `source/shared/schemas.py` with shared Pydantic models (see `DATA_SCHEMAS.md` §2)

---

## Developer A — Infrastructure

### `source/load-image.sh`
- [x] Shell script: detect OCI directory path relative to `source/`, call `skopeo copy oci:... docker-daemon:mars-iot-simulator:multiarch_v1`
- [x] `chmod +x load-image.sh`; test on clean shell

### `source/.env.example`
- [x] Copy all keys from `MASTER_PLAN.md §7` into `.env.example` with placeholder values
- [x] Create `source/.env` (gitignored) as a copy of `.env.example` with real values for local dev

### `source/docker-compose.yml`
- [x] `version: '3.9'`
- [x] **Service: `simulator`**
  - image: `mars-iot-simulator:multiarch_v1`
  - ports: `"8080:8080"`
  - healthcheck: `GET http://localhost:8080/api/discovery` every 10s
- [x] **Service: `rabbitmq`**
  - image: `rabbitmq:3.13-management`
  - ports: `"15672:15672"` (management UI — no AMQP port exposed externally)
  - environment: `RABBITMQ_DEFAULT_USER=guest`, `RABBITMQ_DEFAULT_PASS=guest`
  - healthcheck: `rabbitmq-diagnostics ping`
  - volumes: `rabbitmq_data:/var/lib/rabbitmq`
- [x] **Service: `redis`**
  - image: `redis:7-alpine`
  - no external ports
  - healthcheck: `redis-cli ping`
  - volumes: `redis_data:/data`
- [x] **Service: `postgres`**
  - image: `postgres:16-alpine`
  - no external ports
  - environment: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` from `.env`
  - healthcheck: `pg_isready -U mars`
  - volumes: `pg_data:/var/lib/postgresql/data`
- [x] **Service: `collector`**
  - build: `./collector`
  - env_file: `.env`
  - depends_on: `rabbitmq` (healthy), `simulator` (healthy)
  - restart: `on-failure`
- [x] **Service: `rules-engine`**
  - build: `./rules-engine`
  - env_file: `.env`
  - depends_on: `rabbitmq` (healthy), `redis` (healthy), `postgres` (healthy)
  - restart: `on-failure`
- [x] **Service: `api`**
  - build: `./api`
  - ports: `"8000:8000"`
  - env_file: `.env`
  - depends_on: `redis` (healthy), `postgres` (healthy), `simulator` (healthy)
  - restart: `on-failure`
- [x] **Service: `frontend`**
  - build: `./frontend`
  - ports: `"3000:80"`
  - depends_on: `api` (service_started)
  - restart: `on-failure`
- [x] Top-level `volumes:` block: `rabbitmq_data`, `redis_data`, `pg_data`

### `source/collector/Dockerfile`
- [x] Base: `python:3.12-slim`
- [x] `WORKDIR /app`
- [x] `COPY requirements.txt .` → `RUN pip install --no-cache-dir -r requirements.txt`
- [x] `COPY ../shared ./shared`
- [x] `COPY src/ ./src/`
- [x] `CMD ["python", "-m", "src.main"]`

### `source/rules-engine/Dockerfile`
- [x] Same structure as collector
- [x] CMD runs Alembic upgrade then starts consumer: `CMD ["sh", "-c", "alembic upgrade head && python -m src.main"]`

### `source/api/Dockerfile`
- [x] Base: `python:3.12-slim`
- [x] CMD: `["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]`

### `source/frontend/Dockerfile`
- [x] **Stage 1 (build):** `node:20-alpine` → `npm ci` → `npm run build`
- [x] **Stage 2 (serve):** `nginx:stable-alpine` → copy `dist/` to `/usr/share/nginx/html`
- [x] Copy `nginx.conf` to `/etc/nginx/conf.d/default.conf`

### `source/frontend/nginx.conf`
- [x] Serve `index.html` for all routes (SPA fallback: `try_files $uri /index.html`)
- [x] Proxy `/api/` → `http://api:8000/api/` (so frontend calls relative `/api/...`)

---

## Developer B — Collector Service

### `source/collector/requirements.txt`
```
httpx[asyncio]==0.27.*
aio-pika==9.*
pydantic==2.*
pydantic-settings==2.*
python-dotenv==1.*
```

### `source/collector/src/config.py`
- [x] `Settings` class (Pydantic BaseSettings) with fields:
  - `simulator_base_url: str`
  - `rabbitmq_url: str`
  - `rabbitmq_exchange: str = "mars.events"`
  - `poll_interval_seconds: int = 5`
- [x] `REST_SENSORS: list[str]` — hardcoded list from `GET /api/discovery`:
  `["greenhouse_temperature", "entrance_humidity", "co2_hall", "corridor_pressure", "hydroponic_ph", "air_quality_voc", "air_quality_pm25", "water_tank_level"]`
- [x] `TELEMETRY_TOPICS: list[str]` — all 7 topics from SCHEMA_CONTRACT

### `source/collector/src/normalizer.py`
Function `normalize(raw: dict, sensor_name_or_topic: str) -> InternalEvent`:
- [x] Case `rest.scalar.v1` (when `"value"` key present, no `"measurements"`, no `"pm25_ug_m3"`, no `"level_pct"`):
  - metrics = `[{"name": raw["metric"], "value": raw["value"], "unit": raw["unit"]}]`
- [x] Case `rest.chemistry.v1` (when `"measurements"` key present, source is REST):
  - metrics = `raw["measurements"]` as-is
- [x] Case `rest.particulate.v1` (when `"pm25_ug_m3"` key present):
  - metrics = 3 entries: `pm1_ug_m3`, `pm25_ug_m3`, `pm10_ug_m3`
- [x] Case `rest.level.v1` (when `"level_pct"` key present):
  - metrics = 2 entries: `level_pct`, `level_liters`
- [x] Case `topic.power.v1` (when `"power_kw"` key present):
  - metrics = `power_kw`, `voltage_v`, `current_a`, `cumulative_kwh`
- [x] Case `topic.environment.v1` (when `"measurements"` key present, source is topic):
  - metrics = `raw["measurements"]` as-is; `source_id` = raw["source"]["system"]
- [x] Case `topic.thermal_loop.v1` (when `"temperature_c"` key present):
  - metrics = `temperature_c`, `flow_l_min`
- [x] Case `topic.airlock.v1` (when `"airlock_id"` key present):
  - metrics = `cycles_per_hour`; include `last_state` in a metadata field
- [x] Set `category` enum correctly for each case
- [x] Set `status` from `raw.get("status")` (None for power/airlock)
- [x] Generate `event_id` with `uuid.uuid4()`
- [x] Set `timestamp` from `raw.get("captured_at") or raw.get("event_time") or datetime.utcnow().isoformat()`

### `source/collector/src/publisher.py`
- [x] `connect_rabbitmq(url, exchange_name)` → returns `(connection, channel, exchange)`
- [x] `publish_event(exchange, event: InternalEvent)` → serialize to JSON, publish with `routing_key=""`
- [x] Reconnect logic: wrap in try/except, backoff 5s on failure

### `source/collector/src/rest_poller.py`
- [x] `async def poll_sensor(client: httpx.AsyncClient, sensor_name: str, exchange, settings) -> None`
  - `GET {SIMULATOR_BASE_URL}/api/sensors/{sensor_name}`
  - On 200: normalize → publish
  - On error: log warning, continue
- [x] `async def polling_loop(exchange, settings) -> None`
  - Create one `httpx.AsyncClient`
  - Run `asyncio.gather(*[poll_sensor(...) for s in REST_SENSORS])` in a `while True` loop with `asyncio.sleep(POLL_INTERVAL_SECONDS)`

### `source/collector/src/sse_subscriber.py`
- [x] `async def subscribe_topic(topic: str, exchange, settings) -> None`
  - `GET {SIMULATOR_BASE_URL}/api/telemetry/stream/{topic_url_encoded}`
  - Use `httpx.AsyncClient.stream()` to read SSE line by line
  - Filter lines starting with `data:`, parse JSON
  - normalize → publish
  - On connection drop: log + reconnect after 3s
- [x] `async def subscribe_all_topics(exchange, settings) -> None`
  - `asyncio.gather(*[subscribe_topic(t, ...) for t in TELEMETRY_TOPICS])`

### `source/collector/src/main.py`
- [x] `async def main()`:
  - Connect to RabbitMQ with retry (wait for broker health)
  - Declare `mars.events` fanout exchange
  - `asyncio.gather(polling_loop(...), subscribe_all_topics(...))`
- [x] `if __name__ == "__main__": asyncio.run(main())`

---

## Developer C — Rules Engine + API

### `source/rules-engine/requirements.txt`
```
aio-pika==9.*
redis[asyncio]==5.*
sqlalchemy[asyncio]==2.*
asyncpg==0.29.*
alembic==1.*
httpx[asyncio]==0.27.*
pydantic==2.*
pydantic-settings==2.*
python-dotenv==1.*
```

### `source/rules-engine/src/config.py`
- [x] `Settings` with: `rabbitmq_url`, `rabbitmq_exchange`, `redis_url`, `postgres_dsn`, `simulator_base_url`

### `source/rules-engine/src/models.py`
- [x] `Rule` SQLAlchemy model:
  - `id: UUID PK`
  - `name: str`
  - `enabled: bool default True`
  - `condition: JSONB` — `{ source_id, metric, operator, threshold }`
  - `action: JSONB` — `{ actuator_name, state }`
  - `created_at: datetime`
  - `updated_at: datetime`
- [x] `Alert` SQLAlchemy model:
  - `id: UUID PK`
  - `rule_id: UUID FK → rules.id`
  - `triggered_event: JSONB` — snapshot of the InternalEvent
  - `triggered_at: datetime`

### `source/rules-engine/alembic/` (full Alembic setup)
- [x] `alembic init alembic` inside rules-engine directory
- [x] Edit `alembic/env.py` to use async engine from `config.py`
- [x] Create `alembic/versions/001_initial.py`: create `rules` table + `alerts` table

### `source/rules-engine/src/db.py`
- [x] Async SQLAlchemy engine + `AsyncSession` factory
- [x] `async def get_session()` context manager

### `source/rules-engine/src/state_store.py`
- [x] `redis_client = redis.from_url(settings.redis_url, decode_responses=True)`
- [x] `async def set_latest_state(source_id: str, event: InternalEvent) -> None`
  - `await redis_client.set(f"state:{source_id}", event.model_dump_json(), ex=3600)`
- [x] `async def get_latest_state(source_id: str) -> dict | None`
  - `val = await redis_client.get(f"state:{source_id}")`

### `source/rules-engine/src/actuator_client.py`
- [x] `async def trigger_actuator(actuator_name: str, state: str, base_url: str) -> dict`
  - `POST {base_url}/api/actuators/{actuator_name}` with body `{"state": state}`
  - Return response JSON; log on error

### `source/rules-engine/src/evaluator.py`
Function `async def evaluate(event: InternalEvent, session, redis, settings) -> list[str]` (returns list of fired rule IDs):
- [x] Load all enabled rules from PostgreSQL: `SELECT * FROM rules WHERE enabled = true`
- [x] For each rule:
  - Match `rule.condition.source_id == event.source_id`
  - Find the metric in `event.metrics` by `name == rule.condition.metric`
  - Evaluate: `op = rule.condition.operator` (gt, lt, eq, gte, lte, neq)
  - If condition passes:
    - Call `trigger_actuator(rule.action.actuator_name, rule.action.state, ...)`
    - Insert `Alert` row into PostgreSQL
    - Publish alert JSON to Redis pub/sub channel `mars.alerts`
- [x] Return list of fired rule IDs

### `source/rules-engine/src/consumer.py`
- [x] `async def consume(channel, session_factory, redis, settings) -> None`
  - Declare queue bound to `mars.events` exchange
  - For each message:
    1. Deserialize to `InternalEvent`
    2. `await state_store.set_latest_state(event.source_id, event)`
    3. `await evaluator.evaluate(event, session, redis, settings)`
    4. Acknowledge message
    5. Publish event to Redis pub/sub `mars.events` (for API SSE relay)

### `source/rules-engine/src/main.py`
- [x] Connect to RabbitMQ, Redis, PostgreSQL with retry loops
- [x] Run Alembic migrations (or check table existence)
- [x] Start `consume()` loop

---

### API Service

### `source/api/requirements.txt`
```
fastapi==0.111.*
uvicorn[standard]==0.29.*
sqlalchemy[asyncio]==2.*
asyncpg==0.29.*
redis[asyncio]==5.*
httpx[asyncio]==0.27.*
pydantic==2.*
pydantic-settings==2.*
python-dotenv==1.*
```

### `source/api/src/config.py`
- [x] `Settings` with: `redis_url`, `postgres_dsn`, `simulator_base_url`

### `source/api/src/db.py`
- [x] Async engine + `AsyncSession` factory (same pattern as rules-engine; consider copying)

### `source/api/src/models.py`
- [x] Same `Rule` and `Alert` SQLAlchemy models (copy from rules-engine or use shared package)

### `source/api/src/redis_client.py`
- [x] Singleton async Redis client
- [x] `async def get_redis()` dependency (for FastAPI DI)

### `source/api/src/routers/state.py`
- [x] `GET /api/state` → scan Redis keys `state:*` → return all as `{ source_id: {...} }`
- [x] `GET /api/state/{source_id}` → `GET state:{source_id}` from Redis → 404 if missing

### `source/api/src/routers/actuators.py`
- [x] `GET /api/actuators` → proxy `GET {SIMULATOR_BASE_URL}/api/actuators` → return response JSON
- [x] `POST /api/actuators/{actuator_name}` → proxy `POST {SIMULATOR_BASE_URL}/api/actuators/{name}` with body `{"state": "ON"|"OFF"}`

### `source/api/src/routers/rules.py`
- [x] `GET /api/rules` → return all rules from PostgreSQL
- [x] `POST /api/rules` → create new rule (validate condition/action shape)
- [x] `GET /api/rules/{rule_id}` → return single rule or 404
- [x] `PUT /api/rules/{rule_id}` → update rule fields (full replace)
- [x] `PATCH /api/rules/{rule_id}/toggle` → flip `enabled` boolean
- [x] `DELETE /api/rules/{rule_id}` → delete rule

### `source/api/src/routers/alerts.py`
- [x] `GET /api/alerts` → return recent alerts (default limit=50)
  - Query params: `?rule_id=`, `?source_id=`, `?limit=`, `?offset=`
- [x] Join with `rules` table to include rule name in response

### `source/api/src/routers/stream.py`
- [x] `GET /api/stream` → SSE endpoint (MediaType: `text/event-stream`)
  - Subscribe to Redis pub/sub channels: `mars.events` AND `mars.alerts`
  - For each message: format as `data: {json}\n\n` with `event: sensor_update` or `event: alert`
  - Send `ping` comment every 15s to keep connection alive
  - Handle client disconnect gracefully

### `source/api/src/main.py`
- [x] `app = FastAPI(title="Mars Operations API")`
- [x] Include all routers with prefix `/api`
- [x] Add CORS middleware: allow `http://localhost:3000`
- [x] Startup event: verify Redis + PostgreSQL connectivity
- [x] `GET /api/health` → `{"status": "ok"}`

---

## Developer D — Frontend

### Scaffold
- [x] `npm create vite@latest frontend -- --template react-ts`
- [x] `npm install tailwindcss postcss autoprefixer recharts axios react-router-dom`
- [x] `npx tailwindcss init -p`
- [x] Install shadcn/ui: `npx shadcn-ui@latest init` (choose zinc theme, CSS variables)
- [x] Install shadcn components: `Badge`, `Button`, `Card`, `Dialog`, `Input`, `Label`, `Select`, `Switch`, `Table`, `Toast`

### `source/frontend/src/types/`

#### `types/sensor.ts`
- [x] `interface Metric { name: string; value: number; unit: string; }`
- [x] `interface SensorState { event_id: string; timestamp: string; source_id: string; source_type: string; category: string; metrics: Metric[]; status: "ok" | "warning" | null; raw_schema: string; }`

#### `types/rule.ts`
- [x] `type Operator = "gt" | "lt" | "eq" | "gte" | "lte" | "neq"`
- [x] `interface RuleCondition { source_id: string; metric: string; operator: Operator; threshold: number; }`
- [x] `interface RuleAction { actuator_name: string; state: "ON" | "OFF"; }`
- [x] `interface Rule { id: string; name: string; enabled: boolean; condition: RuleCondition; action: RuleAction; created_at: string; updated_at: string; }`

#### `types/alert.ts`
- [x] `interface Alert { id: string; rule_id: string; rule_name: string; triggered_event: SensorState; triggered_at: string; }`

### `source/frontend/src/api/`

#### `api/client.ts`
- [x] `const BASE = "/api"` (nginx proxies `/api` → `http://api:8000/api`)
- [x] Export typed `get<T>`, `post<T>`, `put<T>`, `patch<T>`, `del` helpers using `fetch`

#### `api/state.ts`
- [x] `fetchAllState(): Promise<Record<string, SensorState>>`
- [x] `fetchState(sourceId: string): Promise<SensorState>`

#### `api/actuators.ts`
- [x] `fetchActuators(): Promise<Record<string, "ON"|"OFF">>`
- [x] `setActuator(name: string, state: "ON"|"OFF"): Promise<{actuator: string; state: string; updated_at: string}>`

#### `api/rules.ts`
- [x] `fetchRules(): Promise<Rule[]>`
- [x] `createRule(data: Omit<Rule, "id"|"created_at"|"updated_at">): Promise<Rule>`
- [x] `updateRule(id: string, data: Partial<Rule>): Promise<Rule>`
- [x] `toggleRule(id: string): Promise<Rule>`
- [x] `deleteRule(id: string): Promise<void>`

#### `api/alerts.ts`
- [x] `fetchAlerts(params?: { rule_id?: string; source_id?: string; limit?: number }): Promise<Alert[]>`

### `source/frontend/src/hooks/`

#### `hooks/useSSE.ts`
```ts
// Custom hook that:
// 1. Opens EventSource("/api/stream")
// 2. Listens for event types: "sensor_update" and "alert"
// 3. Maintains sensorStates: Record<string, SensorState> (updated on each sensor_update)
// 4. Maintains recentAlerts: Alert[] (prepended on each alert, capped at 50)
// 5. Calls onOpen/onError callbacks
// 6. Cleans up EventSource on unmount
```
- [x] Implement the hook above
- [x] Export `{ sensorStates, recentAlerts, connected }`

#### `hooks/useActuators.ts`
- [x] Poll `GET /api/actuators` every 5 s (or re-fetch after manual toggle)
- [x] Expose `{ actuators, toggle, loading }`

### `source/frontend/src/components/`

#### `components/layout/Sidebar.tsx`
- [x] Navigation links to all pages: Dashboard, Power, Environment, Airlock & Thermal, Actuators, Rules, Alerts
- [x] Highlight active route with `react-router-dom`'s `NavLink`
- [x] Show connection status indicator (SSE connected/disconnected dot)

#### `components/layout/TopBar.tsx`
- [x] Page title
- [x] Connection status badge (green=connected, red=disconnected)
- [x] Last updated timestamp

#### `components/sensors/SensorWidget.tsx`
Props: `sensor: SensorState`
- [x] Card with sensor name, primary metric value + unit, secondary metrics (if multiple)
- [x] `StatusBadge` showing ok/warning/unknown
- [x] Subtle background pulse animation on update (use CSS transition on value change)

#### `components/sensors/StatusBadge.tsx`
- [x] `ok` → green badge
- [x] `warning` → amber/orange badge
- [x] `null` → gray badge

#### `components/charts/LiveChart.tsx`
Props: `title: string, data: {time: string, value: number}[], unit: string, color?: string`
- [x] Recharts `<ResponsiveContainer>` + `<LineChart>`
- [x] Keep only last 60 data points (sliding window)
- [x] X-axis: formatted time (`HH:mm:ss`)
- [x] Y-axis: auto-domain with some padding

#### `components/actuators/ActuatorCard.tsx`
Props: `name: string, state: "ON"|"OFF", onToggle: () => void, loading: boolean`
- [x] shadcn `Card` with actuator name
- [x] shadcn `Switch` bound to ON/OFF state
- [x] Disabled + spinner while `loading`
- [x] Color: green ring when ON, gray when OFF

#### `components/rules/RuleTable.tsx`
Props: `rules: Rule[], onEdit, onDelete, onToggle`
- [x] shadcn `Table` with columns: Name | Condition | Action | Enabled | Actions
- [x] Condition rendered as human-readable: `greenhouse_temperature.value > 35 → cooling_fan ON`
- [x] Actions: Edit (pen icon), Delete (trash icon), Toggle (Switch)
- [x] Confirm dialog before delete

#### `components/rules/RuleForm.tsx`
Props: `initialValues?: Rule, onSubmit, onCancel`
- [x] shadcn `Dialog` with form fields:
  - Name (text input)
  - Source ID (Select — populated from `fetchAllState()` keys)
  - Metric (Select — populated from selected sensor's metrics)
  - Operator (Select — gt/lt/eq/gte/lte/neq)
  - Threshold (number input)
  - Actuator name (Select — populated from `fetchActuators()` keys)
  - State (Select — ON/OFF)
- [x] Validation: all fields required, threshold must be a number
- [x] Submit calls `createRule` or `updateRule`

#### `components/alerts/AlertTimeline.tsx`
Props: `alerts: Alert[]`
- [x] Vertical timeline list
- [x] Each entry: timestamp, rule name, sensor id + metric + value, actuator triggered
- [x] Color: red border-left for warning status events
- [x] "Load more" button (calls `fetchAlerts` with offset)

### `source/frontend/src/pages/`

#### `pages/Dashboard.tsx` (US 1–4)
- [x] Import `useSSE` hook
- [x] Render `SensorWidget` grid for all entries in `sensorStates`
- [x] Group by category (environment, power, life_support, airlock, thermal)
- [x] Show `TopBar` with last-updated time
- [x] If `sensorStates` is empty on first load → fetch from `GET /api/state` as initial data

#### `pages/Power.tsx` (US 5, 16)
- [x] 3 `LiveChart` components: Solar Array, Power Bus, Power Consumption
- [x] Each chart tracks `power_kw` over time
- [x] Show current voltage + current as `SensorWidget` summary cards
- [x] Data source: `useSSE` filtered for `category === "power"`

#### `pages/Environment.tsx` (US 6, 17)
- [x] Radiation sensor: measurements as a card list with status badge
- [x] Life Support: measurements as `SensorWidget` cards
- [x] `LiveChart` for any numeric life support measurement
- [x] Data source: `useSSE` filtered for `category === "life_support"` + radiation

#### `pages/AirlockThermal.tsx` (US 7, 8, 18, 19)
- [x] Airlock section: state badge (IDLE/PRESSURIZING/DEPRESSURIZING), cycles-per-hour gauge or card
- [x] Thermal loop section: `LiveChart` for `temperature_c` and `flow_l_min`
- [x] Status badge for thermal loop
- [x] Data source: `useSSE` filtered for `category === "airlock"` and `"thermal"`

#### `pages/Actuators.tsx` (US 11, 12)
- [x] Fetch actuator list from `/api/actuators` on mount
- [x] Render `ActuatorCard` for each actuator
- [x] On toggle: call `POST /api/actuators/{name}` then refresh state

#### `pages/Rules.tsx` (US 13–18)
- [x] Fetch all rules on mount
- [x] Render `RuleTable`
- [x] "New Rule" button → open `RuleForm` dialog
- [x] On edit → open `RuleForm` with prefilled values
- [x] On delete → confirmation dialog → call `deleteRule`
- [x] On toggle → call `toggleRule` → update row in-place

#### `pages/Alerts.tsx` (US 19–20)
- [x] Fetch alerts on mount
- [x] Filter bar: by rule name (Select) and by sensor (text input)
- [x] Render `AlertTimeline`
- [x] Live alerts from `useSSE.recentAlerts` prepended to the list

### `source/frontend/src/App.tsx`
- [x] `BrowserRouter` wrapping all routes
- [x] Layout: `Sidebar` + `TopBar` + `<Outlet>`
- [x] Routes: `/`, `/power`, `/environment`, `/airlock-thermal`, `/actuators`, `/rules`, `/alerts`

---

## Shared Schema

### `source/shared/__init__.py`
- [x] Empty file

### `source/shared/schemas.py`
- [x] `class MetricReading(BaseModel): name: str; value: float; unit: str`
- [x] `class Category(str, Enum): ENVIRONMENT="environment"; POWER="power"; LIFE_SUPPORT="life_support"; AIRLOCK="airlock"; THERMAL="thermal"`
- [x] `class SourceType(str, Enum): REST_SENSOR="rest_sensor"; TELEMETRY_TOPIC="telemetry_topic"`
- [x] `class InternalEvent(BaseModel):`
  - `event_id: str` (UUID)
  - `timestamp: str` (ISO-8601)
  - `source_id: str`
  - `source_type: SourceType`
  - `category: Category`
  - `metrics: list[MetricReading]`
  - `status: str | None`
  - `raw_schema: str`
  - `extra_fields: dict = {}` (for airlock `last_state`, thermal `loop`, power `subsystem`)

---

## Integration Tests (Day 4–5)

- [ ] From clean clone: `bash source/load-image.sh` → must succeed
- [ ] `docker compose up --build` → all containers healthy within 90 s
- [ ] `curl http://localhost:8000/api/health` → `{"status": "ok"}`
- [ ] `curl http://localhost:8000/api/state` → non-empty JSON within 15 s of boot
- [ ] `curl http://localhost:8000/api/actuators` → returns actuator list
- [ ] Create a rule via `POST http://localhost:8000/api/rules` — verify it appears in `GET /api/rules`
- [ ] Open `http://localhost:3000` — verify dashboard renders without errors
- [ ] Open browser DevTools → Network → filter EventStream → verify SSE events arrive
- [ ] Toggle an actuator in the UI → verify `POST /api/actuators/{name}` called and state updates
- [ ] Rule fires: set a rule with a threshold that current sensor data crosses → verify alert appears in `GET /api/alerts` within 10 s

---

## Documentation Deliverables (Day 5)

### `input.md` (required deliverable)
- [x] System description paragraph
- [x] All 20 user stories in standard format
- [x] Unified InternalEvent JSON schema (from `DATA_SCHEMAS.md`)
- [x] Rule model JSON schema

### `Student_doc.md` (required deliverable)
- [x] Fill all container sections (collector, rules-engine, api, frontend, infra)
- [x] All endpoints with HTTP method, URL, description, user story references
- [x] All DB table schemas

### `booklets/architecture/`
- [ ] C4 Context diagram (PNG or draw.io)
- [ ] C4 Container diagram (PNG or draw.io)

### `booklets/mockups/`
- [ ] One LoFi mockup per page: Dashboard, Power, Environment, Airlock/Thermal, Actuators, Rules, Alerts

### `booklets/presentation/`
- [ ] 10-slide deck: Problem, Architecture, Demo flow, Tech choices, Lessons learned
