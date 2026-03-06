"""
collector/src/normalizer.py — Raw simulator payload → InternalEvent

Implements all 8 schema variants from SCHEMA_CONTRACT v1.2.0:
  REST:   rest.scalar.v1 | rest.chemistry.v1 | rest.particulate.v1 | rest.level.v1
  Topics: topic.power.v1 | topic.environment.v1 | topic.thermal_loop.v1 | topic.airlock.v1
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from shared.schemas import Category, InternalEvent, MetricReading, SourceType

logger = logging.getLogger(__name__)

# ── Category lookup ────────────────────────────────────────────────────────────
_CATEGORY_MAP: dict[str, Category] = {
    # REST – environment
    "greenhouse_temperature": Category.ENVIRONMENT,
    "entrance_humidity":      Category.ENVIRONMENT,
    "co2_hall":               Category.ENVIRONMENT,
    "corridor_pressure":      Category.ENVIRONMENT,
    "hydroponic_ph":          Category.ENVIRONMENT,
    "air_quality_voc":        Category.ENVIRONMENT,
    "air_quality_pm25":       Category.ENVIRONMENT,
    "water_tank_level":       Category.ENVIRONMENT,
    # Telemetry – power
    "mars/telemetry/solar_array":       Category.POWER,
    "mars/telemetry/power_bus":         Category.POWER,
    "mars/telemetry/power_consumption": Category.POWER,
    # Telemetry – life support / radiation
    "mars/telemetry/radiation":    Category.LIFE_SUPPORT,
    "mars/telemetry/life_support": Category.LIFE_SUPPORT,
    # Telemetry – thermal
    "mars/telemetry/thermal_loop": Category.THERMAL,
    # Telemetry – airlock
    "mars/telemetry/airlock": Category.AIRLOCK,
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize(raw: dict, source_id: str) -> InternalEvent:
    """
    Convert a raw simulator JSON payload into a unified InternalEvent.

    ``source_id`` is the sensor name (REST) or the full topic path (telemetry).
    Schema variant is detected by discriminating keys in ``raw``.
    """
    timestamp = raw.get("captured_at") or raw.get("event_time") or _now_iso()
    status    = raw.get("status")   # None for schemas that omit it

    # ── rest.particulate.v1 ────────────────────────────────────────────────────
    if "pm25_ug_m3" in raw:
        metrics = [
            MetricReading(name="pm1_ug_m3",  value=float(raw["pm1_ug_m3"]),  unit="ug/m3"),
            MetricReading(name="pm25_ug_m3", value=float(raw["pm25_ug_m3"]), unit="ug/m3"),
            MetricReading(name="pm10_ug_m3", value=float(raw["pm10_ug_m3"]), unit="ug/m3"),
        ]
        raw_schema  = "rest.particulate.v1"
        source_type = SourceType.REST_SENSOR
        extra: dict = {}

    # ── rest.level.v1 ─────────────────────────────────────────────────────────
    elif "level_pct" in raw:
        metrics = [
            MetricReading(name="level_pct",    value=float(raw["level_pct"]),    unit="%"),
            MetricReading(name="level_liters", value=float(raw["level_liters"]), unit="L"),
        ]
        raw_schema  = "rest.level.v1"
        source_type = SourceType.REST_SENSOR
        extra       = {}

    # ── topic.power.v1 ────────────────────────────────────────────────────────
    elif "power_kw" in raw:
        metrics = [
            MetricReading(name="power_kw",      value=float(raw["power_kw"]),      unit="kW"),
            MetricReading(name="voltage_v",      value=float(raw["voltage_v"]),     unit="V"),
            MetricReading(name="current_a",      value=float(raw["current_a"]),     unit="A"),
            MetricReading(name="cumulative_kwh", value=float(raw["cumulative_kwh"]), unit="kWh"),
        ]
        raw_schema  = "topic.power.v1"
        source_type = SourceType.TELEMETRY_TOPIC
        extra       = {"subsystem": raw.get("subsystem", "")}

    # ── topic.thermal_loop.v1 ─────────────────────────────────────────────────
    elif "temperature_c" in raw:
        metrics = [
            MetricReading(name="temperature_c", value=float(raw["temperature_c"]), unit="°C"),
            MetricReading(name="flow_l_min",    value=float(raw["flow_l_min"]),    unit="L/min"),
        ]
        raw_schema  = "topic.thermal_loop.v1"
        source_type = SourceType.TELEMETRY_TOPIC
        extra       = {"loop": raw.get("loop", "")}

    # ── topic.airlock.v1 ──────────────────────────────────────────────────────
    elif "airlock_id" in raw:
        metrics = [
            MetricReading(
                name="cycles_per_hour",
                value=float(raw["cycles_per_hour"]),
                unit="cycles/h",
            ),
        ]
        raw_schema  = "topic.airlock.v1"
        source_type = SourceType.TELEMETRY_TOPIC
        extra       = {
            "airlock_id": raw.get("airlock_id", ""),
            "last_state": raw.get("last_state", ""),
        }

    # ── rest.chemistry.v1  /  topic.environment.v1 (both have "measurements") ─
    elif "measurements" in raw:
        measurements = raw["measurements"]
        metrics = [
            MetricReading(
                name=m["metric"],
                value=float(m["value"]),
                unit=m["unit"],
            )
            for m in measurements
        ]
        if "topic" in raw:
            # topic.environment.v1 — payload contains a "topic" field
            raw_schema  = "topic.environment.v1"
            source_type = SourceType.TELEMETRY_TOPIC
            src         = raw.get("source", {})
            extra       = {
                "source_system":  src.get("system", ""),
                "source_segment": src.get("segment", ""),
            }
        else:
            # rest.chemistry.v1
            raw_schema  = "rest.chemistry.v1"
            source_type = SourceType.REST_SENSOR
            extra       = {}

    # ── rest.scalar.v1 — simple single-value sensor ───────────────────────────
    elif "value" in raw:
        metrics = [
            MetricReading(
                name=raw["metric"],
                value=float(raw["value"]),
                unit=raw["unit"],
            )
        ]
        raw_schema  = "rest.scalar.v1"
        source_type = SourceType.REST_SENSOR
        extra       = {}

    else:
        logger.warning(
            "Unknown payload shape for source_id=%s; top-level keys=%s",
            source_id, list(raw.keys()),
        )
        raise ValueError(f"Cannot normalize payload for source_id={source_id!r}")

    category = _CATEGORY_MAP.get(source_id, Category.ENVIRONMENT)

    return InternalEvent(
        source_id=source_id,
        source_type=source_type,
        category=category,
        timestamp=timestamp,
        metrics=metrics,
        status=status,
        raw_schema=raw_schema,
        extra_fields=extra,
    )
