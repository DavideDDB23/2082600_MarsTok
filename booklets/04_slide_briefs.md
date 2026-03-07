# Slide-by-Slide Presentation Brief
## Mars Operations — 10-minute talk (10 slides)

Each section below is a complete brief for one slide. Hand this to an LLM (or a designer) with the instruction: *"Generate a presentation slide exactly matching this brief. Dark space theme: background #0f172a, accent orange #f97316, body text #e2e8f0, code blocks on #1e293b. Use the Slide Title as the heading."*

Total time budget: **10 minutes** — pacing noted per slide.

---

---

## SLIDE 1 — Title Slide
**Time on slide: ~30 seconds**

### Purpose
First impression. Establish the project identity, tone, and context instantly.

### Layout
Full-bleed dark background. Content centred vertically and horizontally.

### Exact content to include

**Top-centre:** A large red circle emoji or Mars planet icon (🔴) followed immediately by the project name in large bold orange text:
> **Mars Operations**

**One line below, slightly smaller:**
> Distributed IoT Automation Platform

**Separator line** (thin orange horizontal rule)

**Three lines of metadata, left-aligned or centred, small grey text:**
- Lab of Advanced Programming — 2025/2026
- Hackathon · 5 March 2026
- Student ID: **2082600** · Project: **MarsTok**

### Tone / visual feel
Minimal. The title and subtitle should dominate. No diagrams, no bullet lists. Think a SpaceX-style launch slide — confident and clean.

### What to say
*"We are Mars Operations — a distributed IoT automation platform built in 5 days for the Sapienza Hackathon. Our mission: rebuild a broken automation stack on a simulated Mars base before the habitat fails."*

---

---

## SLIDE 2 — The Problem & Our Solution
**Time on slide: ~1 minute**

### Purpose
Frame the challenge. The examiner needs to understand WHY this system exists and what it does in 60 seconds.

### Layout
Two-column layout. Left column = The Problem (red/dark tones). Right column = Our Solution (green/orange tones). Or alternatively: a short italic quote at the top spanning full width, then two columns below.

### Exact content to include

**Full-width quote block at the top** (italic, slightly indented, orange left border):
> *"Mars 2036. Your automation stack is partially destroyed. Devices speak incompatible dialects. Rebuild it — or face thermodynamic consequences."*

**Left column — The Problem** (header in amber):
- Mars habitat generates **heterogeneous** sensor data from 15 devices
- Two incompatible transport protocols: **REST polling** and **SSE streams**
- Raw payloads come in **8 different JSON schemas**
- Operators need real-time visibility — blank screens are dangerous
- Automation actions must fire **automatically** without human intervention
- All configuration must **survive service restarts**

**Right column — Our Solution** (header in green):
- Unified **InternalEvent** schema — one format for everything
- **Event-driven pipeline**: collector → RabbitMQ → rules-engine → Redis → API → frontend
- **IF-THEN rule engine** that evaluates every incoming event and triggers actuators
- **Real-time React dashboard** with SSE push — no polling, no page refresh
- Full **Docker Compose IaC** — one command starts everything

### What to say
*"The simulator gives us 15 devices speaking 8 different data formats over two protocols. We needed to unify all of that, route it through a message broker, evaluate automation rules on every event, and push updates live to the dashboard — all containerised and reproducible."*

---

---

## SLIDE 3 — System Architecture
**Time on slide: ~1.5 minutes**

### Purpose
The architecture diagram. This is the most technically dense slide. Walk through it left-to-right, top-to-bottom.

### Layout
Mostly occupied by a clean architecture diagram. Small legend or annotation labels around it. Minimal additional text.

### Exact content to include

**Slide title:** System Architecture

**Main diagram** — draw as a proper flowchart with labelled arrows (not ASCII — use boxes with rounded corners, coloured by layer):

**Layer 1 — External (red border box, top):**
- Box: `mars-iot-simulator :8080`
- Sub-labels inside: "8 REST sensors (poll 5 s)" and "7 SSE telemetry topics"

**Layer 2 — Ingestion (blue):**
- Box: `collector` (Python 3.12 / asyncio)
- Arrow FROM simulator TO collector labelled: "HTTP GET every 5 s / SSE EventSource (persistent)"
- Arrow FROM collector TO RabbitMQ labelled: "AMQP PERSISTENT publish"

**Layer 3 — Broker (purple):**
- Box: `RabbitMQ 3.13`
- Sub-label: "fanout exchange: mars.events"

**Layer 4 — Processing (orange):**
- Box: `rules-engine` (Python 3.12 / asyncio)
- Arrow FROM RabbitMQ TO rules-engine labelled: "exclusive queue, async consume"
- Arrow FROM rules-engine TO Redis labelled: "SET state:{id} EX 3600 + PUBLISH"
- Arrow FROM rules-engine TO PostgreSQL labelled: "SELECT rules / INSERT alerts"
- Arrow FROM rules-engine TO simulator labelled: "POST /api/actuators/{name} (rule-triggered)"

**Layer 5 — Gateway (teal):**
- Box: `api` (FastAPI :8000)
- Arrow FROM Redis TO api labelled: "SUBSCRIBE mars.events + mars.alerts"
- Arrow FROM PostgreSQL TO api labelled: "CRUD rules / read alerts"
- Arrow FROM simulator TO api labelled: "GET/POST actuators proxy"

**Layer 6 — Presentation (green):**
- Box: `frontend` (React 18 / nginx :3000)
- Bidirectional arrow between api and frontend labelled: "REST calls + SSE stream (via nginx /api/ proxy)"

### Bottom-right corner — small legend:
- 🔴 External · 🔵 Ingestion · 🟣 Broker · 🟠 Processing · 🩵 Gateway · 🟢 Presentation

### What to say
*"The system has 8 containers. Data flows one direction: simulator → collector → RabbitMQ → rules-engine. The rules-engine is the brain — it caches state in Redis, evaluates every rule, fires actuators, and publishes alerts. The API then relays everything to the React frontend over a single persistent SSE connection."*

---

---

## SLIDE 4 — The Unified Event Schema
**Time on slide: ~45 seconds**

### Purpose
Show that we solved the heterogeneity problem with a single normalised schema. This directly addresses the spec requirement.

### Layout
Left half: a clean JSON code block. Right half: a mapping table of all 8 raw schemas to the unified format.

### Exact content to include

**Slide title:** Unified InternalEvent Schema

**Left — JSON code block** (syntax highlighted, on dark #1e293b background):
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
  "raw_schema":  "rest.scalar.v1"
}
```

**Right — Mapping table** (two columns: Raw Schema → Source):

| Raw Schema | Simulator Devices |
|---|---|
| `rest.scalar.v1` | greenhouse_temperature, entrance_humidity, co2_hall, corridor_pressure |
| `rest.chemistry.v1` | hydroponic_ph, air_quality_voc |
| `rest.level.v1` | water_tank_level |
| `rest.particulate.v1` | air_quality_pm25 |
| `topic.power.v1` | solar_array, power_bus, power_consumption |
| `topic.environment.v1` | radiation, life_support |
| `topic.thermal_loop.v1` | thermal_loop |
| `topic.airlock.v1` | airlock |

**Small caption below table** (grey, small font):
> All 8 schemas dispatched by `normalizer.normalize()` → single `InternalEvent` → RabbitMQ

### What to say
*"The collector's normalizer inspects each raw payload and dispatches it to the right handler. Every handler outputs an identical InternalEvent. Everything downstream — the rules engine, Redis, the frontend — only ever sees this one format."*

---

---

## SLIDE 5 — The Automation Engine
**Time on slide: ~1 minute**

### Purpose
Explain IF-THEN rules: the model, the operators, and the full lifecycle (CRUD + evaluate + actuate).

### Layout
Top section: rule model JSON + operator list. Bottom section: a small numbered lifecycle table.

### Exact content to include

**Slide title:** Automation Engine — IF-THEN Rules

**Top-left — JSON code block** (compact, syntax highlighted):
```json
{
  "condition": {
    "source_id": "greenhouse_temperature",
    "metric":    "value",
    "operator":  ">",
    "threshold": 35.0
  },
  "action": {
    "actuator_name": "cooling_fan",
    "state":         "ON"
  }
}
```

**Top-right — Operators box** (styled as a small card):
Title in orange: **Supported Operators**
Six pills/badges in a row, each with symbol and name:
- `>` greater than
- `<` less than  
- `>=` greater or equal
- `<=` less or equal
- `=` equal
- `!=` not equal

Below operators, one highlighted example line:
> `IF greenhouse_temperature > 28°C THEN set cooling_fan to ON`

**Bottom — Rule Lifecycle table** (5 rows):

| # | Action | HTTP | Persisted? |
|---|---|---|---|
| 1 | Create rule | POST /api/rules | ✅ PostgreSQL |
| 2 | List / inspect | GET /api/rules | — |
| 3 | Edit threshold/action | PUT /api/rules/{id} | ✅ PostgreSQL |
| 4 | Enable / Disable | PATCH /api/rules/{id}/toggle | ✅ PostgreSQL |
| 5 | Evaluate on every event | internal, no HTTP | — |
| 6 | Trigger actuator on match | POST to simulator | — |

**Small highlight box** (orange border):
> Rules survive `docker compose down` — persisted in PostgreSQL with Alembic migrations

### What to say
*"Every InternalEvent that arrives triggers a SELECT on all enabled rules. If a condition matches — source ID, metric name, operator, threshold — the engine immediately POSTs to the simulator actuator, inserts an alert in PostgreSQL, and publishes the alert to Redis. The whole cycle is under 50ms on local network."*

---

---

## SLIDE 6 — The Frontend Dashboard
**Time on slide: ~1 minute**

### Purpose
Show the 7-page React dashboard at a glance, explain the real-time architecture, and demonstrate SSE usage.

### Layout
Top: a 2×4 grid of small page preview cards (like a thumbnail grid). Bottom: a short 3-step SSE flow.

### Exact content to include

**Slide title:** Real-time Dashboard — 7 Pages

**Page thumbnail grid** (7 cards, each with page name, 1-sentence description, and user story numbers in a badge):

1. **Dashboard** — All sensor cards in a live grid. Status badges ok/warning. *(US 1–4)*
2. **Power** — 6 live Recharts line charts for solar array, power bus, power consumption. *(US 5)*
3. **Environment** — Radiation + life support cards (crew safety) at top; REST sensor widgets below. *(US 6, 9, 10)*
4. **Airlock & Thermal** — Coloured state badge (IDLE=green / PRESSURIZING=yellow / DEPRESSURIZING=orange) + thermal charts. *(US 7, 8)*
5. **Actuators** — ON/OFF toggle cards for all 4 actuators, auto-refresh every 5 s. *(US 11, 12)*
6. **Rules** — RuleForm dialog + RuleTable with inline enable/disable toggle. *(US 13–18)*
7. **Alerts** — Chronological timeline, rule + source dropdowns, live SSE prepend, pagination. *(US 19, 20)*

**Bottom — SSE real-time flow** (horizontal 3-step diagram with arrows):

```
Page load → GET /api/state/ (pre-fetch all sensor states)
         → EventSource /api/stream (persistent SSE connection)
         → sensor_update events → update React state map
                                → alert events → prepend to alert list
                                → auto-reconnect in 3 s on disconnect
```

**Small note** (grey, small):
> Built with React 18 · TypeScript · Vite · TailwindCSS · Recharts · lucide-react · react-router-dom v6

### What to say
*"The frontend is a React 18 SPA with 7 pages, each covering a different aspect of the habitat. The key pattern is our useSSE hook: on mount it pre-fetches the full sensor state from Redis — so there's never a blank dashboard — then opens a single EventSource connection that streams both sensor updates and rule-triggered alerts in real time."*

---

---

## SLIDE 7 — Technology Stack
**Time on slide: ~45 seconds**

### Purpose
One clean table summarising every technology choice per layer. No need to explain each one — just name them clearly so the examiner can see the full picture.

### Layout
Single centred table, 8 rows, 2 columns (Layer | Technology). Clean, readable, no clutter.

### Exact content to include

**Slide title:** Technology Stack

**Table:**

| Layer | Technology |
|---|---|
| **Ingestion** | Python 3.12 · asyncio · httpx · aio-pika · pydantic v2 |
| **Message Broker** | RabbitMQ 3.13 · fanout exchange · durable · persistent delivery |
| **Processing** | Python 3.12 · SQLAlchemy 2 async · asyncpg · alembic · httpx |
| **State Cache** | Redis 7 · `state:{id}` keys TTL=3600 s · pub/sub channels |
| **Database** | PostgreSQL 16 · `rules` + `alerts` tables · JSONB columns |
| **API Gateway** | FastAPI · Uvicorn · sse-starlette · CORS · pydantic v2 |
| **Frontend** | React 18 · TypeScript · Vite · TailwindCSS · Recharts · lucide-react |
| **IaC / Serving** | Docker Compose · nginx · 8 containers · named volumes · healthchecks |

**Below the table, one highlighted stat line** (orange, centred, slightly larger):
> **8 containers · 3 backend services · 20 user stories · 1 `docker compose up`**

### What to say
*"Python asyncio throughout the backend — no threads, no blocking. RabbitMQ as the decoupling layer between ingestion and processing. FastAPI for the API with sse-starlette for the SSE endpoint. PostgreSQL for persistence with Alembic so the schema is always in sync. Everything is in Docker Compose — reproducible on any machine."*

---

---

## SLIDE 8 — Docker Compose & IaC
**Time on slide: ~45 seconds**

### Purpose
Show that the system is truly reproducible — one command, healthchecks, proper startup order, named volumes.

### Layout
Left: a short code block with the two start commands. Right: a startup dependency graph and volumes list.

### Exact content to include

**Slide title:** Infrastructure as Code — One Command Start

**Left — Code block** (bash, dark background):
```bash
# One-time: load the provided simulator image
./source/load-image.sh

# Start the full platform
cd source && docker compose up
```

**Right — Startup order diagram** (vertical chain with arrows):
```
rabbitmq    ─────────────────────────┐
redis       ─────────────────────────┤ (healthy)
postgres    ─────────────────────────┤
simulator   ─────────────────────────┘
                    ↓
collector  (depends on: rabbitmq, simulator)
rules-engine (depends on: rabbitmq, redis, postgres, simulator)
                    ↓
api        (depends on: redis, postgres)
                    ↓
frontend   (depends on: api)
```

**Below — Named volumes** (small cards or bullet list):
- 🗄️ `pg_data` — rules + alerts (US 18: survive restarts)
- 📨 `rabbitmq_data` — durable messages
- ⚡ `redis_data` — state cache (repopulates in seconds if lost)

**Bottom note** (grey):
> `condition: service_healthy` on every depends_on — no race conditions on startup

### What to say
*"The Compose file uses healthchecks and dependency conditions so every service waits for its dependencies to be ready before starting. Three named volumes ensure rules and alerts persist across restarts. The whole thing starts from zero with a single command."*

---

---

## SLIDE 9 — Lessons Learned
**Time on slide: ~1 minute**

### Purpose
Show technical maturity — what went wrong, what we learned, what we'd do differently. This is often what examiners probe on.

### Layout
Two-column layout. Left: Challenges faced. Right: Key design decisions and their rationale.

### Exact content to include

**Slide title:** Lessons Learned

**Left column — Challenges** (header in amber ⚠️):

1. **Schema diversity**
   8 raw payload formats from the simulator required a clean dispatcher pattern in the normalizer. We solved it with a `match`-like dispatch on `raw_schema` field — each schema gets its own handler function.

2. **SSE double reconnection**
   Both the collector (subscribing to simulator topics) AND the frontend (subscribing to our API stream) needed independent resilient reconnect loops. A 3-second retry with exponential-like backoff was needed in both places.

3. **Blank dashboard on load**
   Opening SSE first meant the dashboard was empty until the next event arrived (up to 5 s). Fix: pre-fetch `GET /api/state/` before opening the EventSource — solved US 4 cleanly.

4. **JSONB alert filtering**
   Alerts store the full triggering event as JSONB. Filtering by `source_id` inside JSONB required PostgreSQL's `@>` containment operator: `triggered_event @> '{"source_id": "..."}'`.

**Right column — Design Decisions** (header in green ✅):

1. **Fanout exchange over direct routing**
   The collector publishes once; every consumer (rules-engine, future services) binds its own exclusive queue. Zero collector changes to add a new consumer.

2. **Redis pub/sub for SSE relay**
   Rather than polling Redis from the API, the rules-engine publishes alerts directly to a Redis channel that the API subscribes to. True zero-latency relay.

3. **Alembic migrations on boot**
   `rules-engine` runs `alembic upgrade head` on every startup. Schema is always in sync — no manual migrations needed after deploy.

4. **Exclusive anonymous queues**
   Each rules-engine instance gets a private auto-delete queue. No stale messages accumulate if a consumer restarts. Clean.

### What to say
*"The biggest surprise was the blank-dashboard problem — we only found it when testing page refresh. The fix was trivial once identified but it taught us to always consider the initial-load state separately from the streaming state. The JSONB filtering was the only database challenge — PostgreSQL's containment operator handles it cleanly without needing a separate source_id column on alerts."*

---

---

## SLIDE 10 — Live Demo
**Time on slide: ~3 minutes (demo time)**

### Purpose
This is the demo slide — it stays on screen during the live demonstration. It should serve as a checklist/script for the presenter AND give the audience context for what they're watching.

### Layout
Two columns. Left: numbered demo steps in order. Right: key URLs to visit and what to look for.

### Exact content to include

**Slide title:** 🎬 Live Demo

**Left column — Demo Script** (numbered, each step as a short imperative):

1. `docker compose up` — show all **8 containers healthy** in terminal
2. Open **http://localhost:3000** — Dashboard page  
   → Watch sensor cards populate immediately (US 4 pre-fetch)  
   → Watch values update every 5 s (US 3 real-time)  
   → Point out green/amber status badges (US 2)
3. Navigate to **Power page**  
   → 6 live line charts updating in real time (US 5)
4. Navigate to **Actuators page**  
   → Toggle `cooling_fan` ON → OFF manually (US 12)
5. Navigate to **Rules page**  
   → Create rule: `greenhouse_temperature > 28 → cooling_fan ON` (US 13)  
   → Show rule in table with `>` symbol (US 14)  
   → Toggle enable/disable (US 16)
6. Watch **Alerts page**  
   → Alert appears automatically when rule triggers (US 19)  
   → Filter by rule name dropdown (US 20)
7. `docker compose down && docker compose up`  
   → Navigate to Rules page → **rules still there** (US 18 persistence)

**Right column — URLs** (card-style, copyable):

| Service | URL |
|---|---|
| 🖥️ Dashboard | http://localhost:3000 |
| 📖 API Docs | http://localhost:8000/docs |
| 📨 RabbitMQ UI | http://localhost:15672 |
| (guest / guest) | |

**Bottom banner** (full width, orange background, white text, centred):
> **20 User Stories · 8 Containers · 5 Days · 1 Command**

### What to say
*"Let me start with docker compose up so you can see all 8 containers come up healthy. While that runs — the system loads the OCI simulator image, starts infrastructure, then application services in dependency order with healthchecks. [proceed through steps] — and finally, the restart test: rules persist because they're in PostgreSQL on a named volume. The platform is fully reproducible."*

---

---

## Timing Summary

| Slide | Title | Target Time |
|---|---|---|
| 1 | Title | 30 s |
| 2 | Problem & Solution | 60 s |
| 3 | Architecture | 90 s |
| 4 | Unified Event Schema | 45 s |
| 5 | Automation Engine | 60 s |
| 6 | Frontend Dashboard | 60 s |
| 7 | Technology Stack | 45 s |
| 8 | Docker Compose / IaC | 45 s |
| 9 | Lessons Learned | 60 s |
| 10 | Live Demo | 180 s |
| **Total** | | **~10 min** |

---

## Prompt to give an LLM for generation

Copy and paste this as the system prompt, then paste individual slide briefs:

> You are a presentation designer. Create a single slide using the following brief. The slide has a dark space theme: background colour #0f172a, primary accent colour #f97316 (orange), body text #e2e8f0 (light grey), secondary text #94a3b8 (muted grey), code block background #1e293b (dark navy), success colour #22c55e (green), warning colour #f59e0b (amber). Font: 'Inter' or 'Segoe UI'. The slide must be self-contained, visually clean, and readable when projected at 1080p. Follow the layout, content, and tone instructions exactly. Do not add content that is not specified. Output as HTML+CSS (single file, no external dependencies) OR as a JSON description for Marp/Reveal.js.
