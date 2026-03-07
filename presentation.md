---
marp: true
theme: default
size: 16:9
paginate: true
style: |
  section {
    background: #0f172a;
    color: #e2e8f0;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    padding: 48px 68px;
    font-size: 21px;
    line-height: 1.55;
  }
  h1 { color: #f97316; font-size: 2.6em; margin: 0 0 8px; font-weight: 800; letter-spacing: -0.02em; }
  h2 { color: #f97316; font-size: 1.55em; font-weight: 700; border-bottom: 2px solid #f97316; padding-bottom: 8px; margin: 0 0 18px; }
  h3 { color: #fb923c; font-size: 1.0em; font-weight: 700; margin: 14px 0 7px; text-transform: uppercase; letter-spacing: 0.05em; }
  strong { color: #ffffff; }
  em { color: #94a3b8; }
  p { margin: 5px 0; }
  ul { padding-left: 1.3em; margin: 5px 0; }
  li { margin: 4px 0; }
  li::marker { color: #f97316; }
  ol li::marker { color: #f97316; font-weight: 700; }
  blockquote {
    border-left: 4px solid #f97316;
    background: rgba(249,115,22,0.08);
    border-radius: 0 8px 8px 0;
    padding: 14px 22px;
    margin: 10px 0;
    color: #94a3b8;
    font-style: italic;
    font-size: 0.92em;
  }
  code {
    background: #1e293b;
    color: #34d399;
    padding: 2px 7px;
    border-radius: 5px;
    font-family: 'Fira Code', 'JetBrains Mono', 'Courier New', monospace;
    font-size: 0.82em;
  }
  pre {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 16px 20px;
    margin: 8px 0;
  }
  pre code { color: #e2e8f0; background: none; padding: 0; font-size: 0.75em; line-height: 1.55; }
  table { width: 100%; border-collapse: collapse; font-size: 0.8em; margin: 10px 0; }
  th { background: #1e293b; color: #f97316; padding: 10px 14px; text-align: left; border-bottom: 2px solid #334155; text-transform: uppercase; font-size: 0.8em; letter-spacing: 0.06em; }
  td { padding: 9px 14px; border-bottom: 1px solid #1e293b; }
  tr:nth-child(even) td { background: rgba(255,255,255,0.015); }
  section::after { color: #475569; font-size: 0.65em; }
  section.lead { display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 60px; }
  section.lead h1 { font-size: 3em; margin-bottom: 12px; line-height: 1.1; }
  section.lead h2 { border: none; color: #94a3b8; font-weight: 400; font-size: 1.25em; margin: 0; }
  .two-col   { display: grid; grid-template-columns: 1fr 1fr;       gap: 30px; margin-top: 6px; }
  .col-6040  { display: grid; grid-template-columns: 1.5fr 1fr;     gap: 30px; margin-top: 6px; }
  .col-4060  { display: grid; grid-template-columns: 1fr 1.5fr;     gap: 30px; margin-top: 6px; }
  .col { min-width: 0; }
  .card { background: #1e293b; border: 1px solid #334155; border-radius: 9px; padding: 12px 16px; margin: 5px 0; }
  .card-o { border-left: 3px solid #f97316; }
  .card-g { border-left: 3px solid #22c55e; }
  .card-a { border-left: 3px solid #f59e0b; }
  .pill { display: inline-block; padding: 2px 10px; border-radius: 16px; font-size: 0.74em; font-weight: 700; margin: 2px; border: 1px solid; }
  .p-o { background: rgba(249,115,22,0.15); color: #f97316;  border-color: #f97316; }
  .p-g { background: rgba(34,197,94,0.12);  color: #22c55e;  border-color: #22c55e; }
  .p-b { background: rgba(96,165,250,0.12); color: #60a5fa;  border-color: #60a5fa; }
  .p-p { background: rgba(168,85,247,0.12); color: #a855f7;  border-color: #a855f7; }
  .p-c { background: rgba(6,182,212,0.12);  color: #06b6d4;  border-color: #06b6d4; }
  .hl { background: rgba(249,115,22,0.1); border: 1px solid rgba(249,115,22,0.3); border-radius: 8px; padding: 10px 16px; margin: 8px 0; color: #fff; font-size: 0.88em; }
  .stat-row { display: flex; gap: 14px; margin-top: 14px; }
  .stat { background: #1e293b; border: 1px solid #334155; border-radius: 9px; padding: 11px 14px; text-align: center; flex: 1; }
  .stat-n { font-size: 1.65em; font-weight: 800; color: #f97316; line-height: 1; }
  .stat-l { font-size: 0.63em; color: #94a3b8; margin-top: 3px; text-transform: uppercase; letter-spacing: 0.05em; }
  .url { background: #1e293b; border: 1px solid #334155; border-radius: 7px; padding: 8px 14px; font-family: 'Fira Code', monospace; font-size: 0.8em; color: #34d399; margin: 5px 0; }
  .step { display: flex; gap: 11px; margin: 6px 0; align-items: flex-start; }
  .sn { background: #f97316; color: #fff; border-radius: 6px; width: 23px; height: 23px; display: flex; align-items: center; justify-content: center; font-size: 0.7em; font-weight: 800; flex-shrink: 0; margin-top: 2px; }
  .st { flex: 1; font-size: 0.88em; }
  .mu { color: #94a3b8; font-size: 0.82em; }
  .pipe { display: flex; align-items: center; gap: 0; margin: 8px 0; flex-wrap: wrap; }
  .pb  { background: #1e293b; border: 1px solid #334155; border-radius: 6px; padding: 5px 11px; font-size: 0.74em; text-align: center; }
  .pa  { color: #f97316; padding: 0 5px; font-size: 1em; flex-shrink: 0; }
---

<!-- _class: lead -->
<!-- _paginate: false -->

# 🔴 Mars Operations

## Distributed IoT Automation Platform

<br>

<div style="color:#94a3b8;font-size:0.78em;line-height:2.4">
Lab of Advanced Programming 2025/2026 &nbsp;·&nbsp; Hackathon — March 2026<br>
<span class="pill p-o">Student ID: 2082600</span>&nbsp;
<span class="pill p-o">Project: MarsTok</span>
</div>

---

## 🚨 Problem &amp; Solution

> *"Mars 2036. Your automation stack is partially destroyed. Devices speak incompatible dialects. Rebuild it — or face thermodynamic consequences."*

<div class="two-col">
<div class="col">

### ❌ The Challenge
- **15 devices**, **8 raw JSON schemas**, two transport protocols
- REST polling + persistent SSE streams — no unified format
- Operators face a **blank dashboard** on page load
- Automation must fire **without human intervention**
- Configuration must **survive service restarts**

</div>
<div class="col">

### ✅ Our Solution
<div class="card card-o">Unified <strong>InternalEvent</strong> normalisation layer</div>
<div class="card card-o">Event-driven pipeline via <strong>RabbitMQ</strong> fanout</div>
<div class="card card-o"><strong>IF-THEN rule engine</strong> — auto-triggers actuators</div>
<div class="card card-o">React dashboard with <strong>live SSE push</strong></div>
<div class="card card-o">Full <strong>Docker Compose IaC</strong> — one command start</div>
</div>
</div>

---

## 🏗️ System Architecture

<div class="col-6040">
<div class="col">

<div class="card" style="border:2px solid #ef4444;text-align:center;padding:10px 14px">
🔴 <strong>mars-iot-simulator :8080</strong><br>
<span class="mu">8 REST sensors (poll 5 s) &nbsp;·&nbsp; 7 SSE telemetry topics</span>
</div>
<div style="text-align:center;color:#f97316;font-size:0.9em;margin:2px 0">↙ HTTP GET every 5 s &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ↘ SSE EventSource</div>

<div class="card" style="border-color:#3b82f6;text-align:center;padding:10px 14px">
🔵 <strong>collector</strong> — Python 3.12 asyncio<br>
<span class="mu">polls + streams + normalises (8 schemas) + publishes</span>
</div>
<div style="text-align:center;color:#f97316;font-size:0.9em;margin:2px 0">↓ AMQP PERSISTENT publish</div>

<div class="card" style="border-color:#a855f7;text-align:center;padding:10px 14px">
🟣 <strong>RabbitMQ 3.13</strong> &nbsp;—&nbsp; fanout exchange <code>mars.events</code>
</div>
<div style="text-align:center;color:#f97316;font-size:0.9em;margin:2px 0">↓ exclusive queue consume</div>

<div class="card" style="border-color:#f97316;text-align:center;padding:10px 14px">
🟠 <strong>rules-engine</strong> — Python 3.12 asyncio<br>
<span class="mu">cache state → evaluate rules → actuate → persist alerts → publish</span>
</div>
<div style="text-align:center;color:#f97316;font-size:0.9em;margin:2px 0">↓ REST &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ↓ Redis &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ↓ PostgreSQL</div>

<div class="two-col" style="gap:8px;margin-top:0">
<div class="card" style="border-color:#06b6d4;text-align:center;padding:8px">🩵 <strong>api</strong> — FastAPI :8000</div>
<div class="card" style="border-color:#22c55e;text-align:center;padding:8px">🟢 <strong>frontend</strong> — React 18 :3000</div>
</div>

</div>
<div class="col">

### Infrastructure

<div class="card" style="margin-bottom:8px;font-size:0.83em">
<span class="pill p-p">📨 RabbitMQ 3.13</span><br>
fanout <code>mars.events</code> · durable · persistent
</div>

<div class="card" style="margin-bottom:8px;font-size:0.83em">
<span class="pill p-c">⚡ Redis 7</span><br>
<code>state:{id}</code> TTL=3600 s<br>
pub/sub: <code>mars.events</code> · <code>mars.alerts</code>
</div>

<div class="card" style="font-size:0.83em">
<span class="pill p-b">🐘 PostgreSQL 16</span><br>
tables: <code>rules</code> + <code>alerts</code><br>
JSONB columns · Alembic migrations
</div>

</div>
</div>

---

## ⚡ Data Pipeline &amp; Unified Schema

<div class="two-col">
<div class="col">

### 7-Step Pipeline

<div class="step"><div class="sn">1</div><div class="st"><strong>Ingest</strong> — poll 8 REST sensors every 5 s; maintain 7 persistent SSE connections</div></div>
<div class="step"><div class="sn">2</div><div class="st"><strong>Normalise</strong> — 8 raw schemas → 1 <code>InternalEvent</code> via dispatcher</div></div>
<div class="step"><div class="sn">3</div><div class="st"><strong>Publish</strong> — PERSISTENT to RabbitMQ fanout <code>mars.events</code></div></div>
<div class="step"><div class="sn">4</div><div class="st"><strong>Process</strong> — write <code>state:{id}</code> to Redis TTL=1 h, evaluate all enabled rules</div></div>
<div class="step"><div class="sn">5</div><div class="st"><strong>Alert</strong> — POST actuator to simulator + INSERT PostgreSQL + PUBLISH Redis</div></div>
<div class="step"><div class="sn">6</div><div class="st"><strong>Stream</strong> — API subscribes Redis pub/sub → relays named SSE events</div></div>
<div class="step"><div class="sn">7</div><div class="st"><strong>Render</strong> — <code>useSSE</code> pre-fetches state on load, then merges live stream</div></div>

</div>
<div class="col">

### InternalEvent Schema

```json
{
  "event_id":    "550e8400-...",
  "timestamp":   "2026-03-06T12:00:00Z",
  "source_id":   "greenhouse_temperature",
  "source_type": "rest_sensor",
  "category":    "environment",
  "metrics": [
    { "name": "value", "value": 22.5, "unit": "degC" }
  ],
  "status":     "ok | warning | null",
  "raw_schema": "rest.scalar.v1"
}
```

<div class="mu" style="margin-top:8px;font-size:0.77em">
<strong style="color:#fff">8 schemas handled:</strong><br>
rest.scalar.v1 · rest.chemistry.v1 · rest.level.v1 · rest.particulate.v1<br>
topic.power.v1 · topic.environment.v1 · topic.thermal_loop.v1 · topic.airlock.v1
</div>

</div>
</div>

---

## ⚙️ Automation Engine

<div class="two-col">
<div class="col">

### Rule Model

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
  "action": {
    "actuator_name": "cooling_fan",
    "state":         "ON"
  }
}
```

<div class="hl" style="margin-top:8px">
🔁 Evaluated on <strong>every</strong> incoming event<br>
<span class="mu"><code>SELECT * FROM rules WHERE enabled = true</code></span>
</div>

</div>
<div class="col">

### Supported Operators

<span class="pill p-o">&gt;&nbsp; greater than</span>
<span class="pill p-o">&lt;&nbsp; less than</span>
<span class="pill p-o">&ge;&nbsp; gte</span>
<span class="pill p-o">&le;&nbsp; lte</span>
<span class="pill p-o">=&nbsp; equal</span>
<span class="pill p-o">&ne;&nbsp; not equal</span>

### Rule Lifecycle

| Action | Endpoint | US |
|---|---|---|
| Create | `POST /api/rules` | 13 |
| List / Get | `GET /api/rules` | 14 |
| Edit | `PUT /api/rules/{id}` | 15 |
| Toggle | `PATCH /api/rules/{id}/toggle` | 16 |
| Delete | `DELETE /api/rules/{id}` | 17 |

<div class="card card-g" style="margin-top:10px;font-size:0.82em">
✅ <strong>Persisted in PostgreSQL</strong> — survive <code>docker compose down</code><br>
Alembic migration runs automatically on every boot
</div>

</div>
</div>

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

### Real-time Data Flow

<div class="pipe">
<div class="pb">Page load</div>
<div class="pa">→</div>
<div class="pb"><code>GET /api/state/</code><br><span class="mu" style="font-size:0.88em">pre-fetch all states</span></div>
<div class="pa">→</div>
<div class="pb"><code>EventSource /api/stream</code><br><span class="mu" style="font-size:0.88em">persistent SSE</span></div>
<div class="pa">→</div>
<div class="pb"><code>sensor_update</code><br><span class="mu" style="font-size:0.88em">update state map</span></div>
<div class="pa">+</div>
<div class="pb"><code>alert</code><br><span class="mu" style="font-size:0.88em">prepend to list</span></div>
<div class="pa">→</div>
<div class="pb">3 s auto-reconnect<br><span class="mu" style="font-size:0.88em">on disconnect</span></div>
</div>

<div class="mu" style="margin-top:6px;font-size:0.76em">React 18 · TypeScript · Vite · TailwindCSS · Recharts · lucide-react · react-router-dom v6</div>

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

<div class="stat-row">
<div class="stat"><div class="stat-n">8</div><div class="stat-l">Containers</div></div>
<div class="stat"><div class="stat-n">3</div><div class="stat-l">Backend Services</div></div>
<div class="stat"><div class="stat-n">20</div><div class="stat-l">User Stories</div></div>
<div class="stat"><div class="stat-n">1</div><div class="stat-l">docker compose up</div></div>
<div class="stat"><div class="stat-n">5</div><div class="stat-l">Days</div></div>
</div>

---

## 🐳 Infrastructure as Code

<div class="two-col">
<div class="col">

### One Command Start

```bash
# One-time: load the simulator OCI image
./source/load-image.sh

# Start the entire platform
cd source && docker compose up
```

### Startup Dependency Chain

<div style="font-size:0.83em">
<div class="card" style="text-align:center;border-color:#a855f7;padding:8px 12px">
🟣 rabbitmq &nbsp;·&nbsp; ⚡ redis &nbsp;·&nbsp; 🐘 postgres &nbsp;·&nbsp; 🔴 simulator
</div>
<div style="text-align:center;color:#f97316;margin:3px 0">↓ <span class="mu" style="font-size:0.85em">condition: service_healthy</span></div>
<div class="card" style="text-align:center;border-color:#3b82f6;padding:8px 12px">
🔵 <strong>collector</strong> &nbsp;&nbsp;&nbsp; 🟠 <strong>rules-engine</strong>
</div>
<div style="text-align:center;color:#f97316;margin:3px 0">↓</div>
<div class="card" style="text-align:center;border-color:#06b6d4;padding:8px 12px">🩵 <strong>api</strong> :8000</div>
<div style="text-align:center;color:#f97316;margin:3px 0">↓</div>
<div class="card" style="text-align:center;border-color:#22c55e;padding:8px 12px">🟢 <strong>frontend</strong> :3000</div>
</div>

</div>
<div class="col">

### Named Volumes

<div class="card card-o" style="margin-bottom:8px;font-size:0.85em">
🗄️ <strong>pg_data</strong><br>
Rules + alerts persist across restarts<br>
<span class="pill p-o" style="font-size:0.7em">US 18 — rule persistence</span>
</div>
<div class="card card-o" style="margin-bottom:8px;font-size:0.85em">
📨 <strong>rabbitmq_data</strong><br>
Durable messages survive broker restart
</div>
<div class="card card-o" style="font-size:0.85em">
⚡ <strong>redis_data</strong><br>
Cache repopulates within seconds on loss
</div>

<div class="hl" style="margin-top:14px">
No manual steps after <code>docker compose up</code><br>
<span class="mu">Alembic migrations run automatically on boot</span>
</div>

</div>
</div>

---

## 💡 Lessons Learned

<div class="two-col">
<div class="col">

### ⚠️ Challenges

<div class="card card-a" style="margin-bottom:7px;font-size:0.84em">
<strong>Schema diversity</strong><br>
8 raw formats required a dispatcher pattern in the normalizer — each schema maps to its own handler function.
</div>
<div class="card card-a" style="margin-bottom:7px;font-size:0.84em">
<strong>SSE double reconnection</strong><br>
Both collector (→ simulator) and frontend (→ API) needed independent 3 s auto-retry loops.
</div>
<div class="card card-a" style="margin-bottom:7px;font-size:0.84em">
<strong>Blank dashboard on load</strong><br>
Opening SSE first = empty cards for up to 5 s. Fix: pre-fetch <code>GET /api/state/</code> <em>before</em> opening <code>EventSource</code>.
</div>
<div class="card card-a" style="font-size:0.84em">
<strong>JSONB alert filtering</strong><br>
Used PostgreSQL <code>@&gt;</code> containment operator to filter <code>source_id</code> inside the stored JSONB event.
</div>

</div>
<div class="col">

### ✅ Design Decisions

<div class="card card-g" style="margin-bottom:7px;font-size:0.84em">
<strong>Fanout exchange</strong><br>
Collector publishes once → any consumer binds its own queue. Zero collector changes to add a new service.
</div>
<div class="card card-g" style="margin-bottom:7px;font-size:0.84em">
<strong>Redis pub/sub relay</strong><br>
True zero-latency push from rules-engine to API SSE clients — no polling needed.
</div>
<div class="card card-g" style="margin-bottom:7px;font-size:0.84em">
<strong>Alembic on boot</strong><br>
<code>alembic upgrade head</code> runs at rules-engine startup — schema always in sync, no manual step.
</div>
<div class="card card-g" style="font-size:0.84em">
<strong>Exclusive anonymous queues</strong><br>
No stale messages accumulate on consumer restart. Broker stays clean automatically.
</div>

</div>
</div>

---

## 🎬 Live Demo

<div class="two-col">
<div class="col">

### Demo Script

<div class="step"><div class="sn">1</div><div class="st"><code>docker compose up</code> — watch all 8 containers reach healthy state</div></div>
<div class="step"><div class="sn">2</div><div class="st"><strong>Dashboard</strong> — cards populate instantly (US 4 pre-fetch); values update every 5 s</div></div>
<div class="step"><div class="sn">3</div><div class="st"><strong>Power page</strong> — 6 live line charts; show rolling window updating in real-time</div></div>
<div class="step"><div class="sn">4</div><div class="st"><strong>Actuators</strong> — manually toggle <code>cooling_fan</code> ON → OFF; verify optimistic update</div></div>
<div class="step"><div class="sn">5</div><div class="st"><strong>Rules</strong> — create: <em>greenhouse_temperature &gt; 28 → cooling_fan ON</em></div></div>
<div class="step"><div class="sn">6</div><div class="st"><strong>Alerts page</strong> — alert appears live; filter by rule and source dropdowns</div></div>
<div class="step"><div class="sn">7</div><div class="st"><code>docker compose down &amp;&amp; docker compose up</code> → rules still there ✅ (US 18)</div></div>

</div>
<div class="col">

### Endpoints

<div class="url">🖥️&nbsp; http://localhost:3000</div>
<div class="mu" style="font-size:0.73em;margin:0 0 10px 4px">React dashboard</div>

<div class="url">📖&nbsp; http://localhost:8000/docs</div>
<div class="mu" style="font-size:0.73em;margin:0 0 10px 4px">FastAPI interactive docs</div>

<div class="url">📨&nbsp; http://localhost:15672</div>
<div class="mu" style="font-size:0.73em;margin:0 0 14px 4px">RabbitMQ Management UI &nbsp;(guest / guest)</div>

<div class="stat-row">
<div class="stat"><div class="stat-n">20</div><div class="stat-l">User Stories</div></div>
<div class="stat"><div class="stat-n">8</div><div class="stat-l">Containers</div></div>
<div class="stat"><div class="stat-n">5</div><div class="stat-l">Days</div></div>
</div>

<div class="hl" style="text-align:center;margin-top:12px">
<strong>1 command &nbsp;·&nbsp; 0 manual setup &nbsp;·&nbsp; No blank screens.</strong>
</div>

</div>
</div>

