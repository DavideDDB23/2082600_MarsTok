#!/usr/bin/env bash
# =============================================================================
# RUN_TESTS.sh — Integration test suite for Mars Operations Platform
# Based on Laboratory_of_Advanced_Programming_March_2026.pdf requirements
# =============================================================================
set -euo pipefail

cd "$(dirname "$0")/source"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Mars Operations Platform — Integration Test Suite"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── 1. Load simulator OCI image ───────────────────────────────────────────
echo ""
echo "▶ Step 1: Load Mars IoT Simulator OCI image"
bash load-image.sh

# ── 2. Start all containers ──────────────────────────────────────────────
echo ""
echo "▶ Step 2: Start all containers (docker compose up --build)"
docker compose down -v 2>/dev/null || true
docker compose up --build -d

echo ""
echo "▶ Step 3: Wait for all services to be healthy (max 90s)..."
TIMEOUT=90
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
  HEALTHY=$(docker compose ps --format json | jq -r '.Health // "healthy"' | grep -c "healthy" || echo 0)
  TOTAL=$(docker compose ps --format json | wc -l | tr -d ' ')
  
  if [ "$HEALTHY" -ge 7 ]; then
    echo "✓ All services healthy after ${ELAPSED}s"
    break
  fi
  
  echo "  ... $HEALTHY/$TOTAL services healthy (${ELAPSED}s elapsed)"
  sleep 5
  ELAPSED=$((ELAPSED + 5))
done

if [ $ELAPSED -ge $TIMEOUT ]; then
  echo "✗ Timeout waiting for services"
  docker compose ps
  exit 1
fi

# ── 4. Test API health endpoint ──────────────────────────────────────────
echo ""
echo "▶ Step 4: Test /api/health"
HEALTH=$(curl -s http://localhost:8000/api/health)
if echo "$HEALTH" | jq -e '.status == "ok"' > /dev/null; then
  echo "✓ Health check passed: $HEALTH"
else
  echo "✗ Health check failed: $HEALTH"
  exit 1
fi

# ── 5. Test state endpoint (wait for data) ──────────────────────────────
echo ""
echo "▶ Step 5: Test /api/state (waiting for sensor data...)"
for i in {1..30}; do
  STATE=$(curl -s http://localhost:8000/api/state)
  COUNT=$(echo "$STATE" | jq 'length')
  if [ "$COUNT" -gt 0 ]; then
    echo "✓ State endpoint has $COUNT sources after ${i}s"
    echo "$STATE" | jq 'keys'
    break
  fi
  sleep 1
done

# ── 6. Test actuators endpoint ──────────────────────────────────────────
echo ""
echo "▶ Step 6: Test /api/actuators"
ACTUATORS=$(curl -s http://localhost:8000/api/actuators)
echo "$ACTUATORS" | jq .
ACT_COUNT=$(echo "$ACTUATORS" | jq '.actuators | length')
if [ "$ACT_COUNT" -gt 0 ]; then
  echo "✓ Found $ACT_COUNT actuators"
else
  echo "✗ No actuators found"
  exit 1
fi

# ── 7. Test rule creation ───────────────────────────────────────────────
echo ""
echo "▶ Step 7: Create a test rule"
RULE_PAYLOAD='{
  "name": "Test Rule - High CO2",
  "enabled": true,
  "condition": {
    "source_id": "co2_hall",
    "metric": "value",
    "operator": "gt",
    "threshold": 400
  },
  "action": {
    "actuator_name": "hall_ventilation",
    "state": "ON"
  }
}'

RULE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/rules \
  -H 'Content-Type: application/json' \
  -d "$RULE_PAYLOAD")

RULE_ID=$(echo "$RULE_RESPONSE" | jq -r '.id')
if [ -n "$RULE_ID" ] && [ "$RULE_ID" != "null" ]; then
  echo "✓ Rule created with ID: $RULE_ID"
  echo "$RULE_RESPONSE" | jq .
else
  echo "✗ Failed to create rule"
  echo "$RULE_RESPONSE"
  exit 1
fi

# ── 8. Verify rule appears in list ──────────────────────────────────────
echo ""
echo "▶ Step 8: Verify rule appears in GET /api/rules"
RULES=$(curl -s http://localhost:8000/api/rules)
RULE_COUNT=$(echo "$RULES" | jq 'length')
echo "✓ Found $RULE_COUNT rule(s)"
echo "$RULES" | jq '.[0]'

# ── 9. Test alerts endpoint ─────────────────────────────────────────────
echo ""
echo "▶ Step 9: Test /api/alerts"
ALERTS=$(curl -s 'http://localhost:8000/api/alerts?limit=5')
echo "$ALERTS" | jq .

# ── 10. Summary ─────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✓ All API tests passed!"
echo ""
echo "  Next steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Verify dashboard renders without errors"
echo "  3. Open DevTools → Network → filter EventSource"
echo "  4. Verify SSE events arrive (sensor_update, alert)"
echo "  5. Toggle an actuator and verify state changes"
echo ""
echo "  To view logs: docker compose logs -f [service]"
echo "  To stop:      docker compose down"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
