"""
collector/src/config.py — Environment-driven configuration via pydantic-settings.

Sensor and topic lists match the simulator's /api/discovery catalogue
(Schema Contract v1.2.0).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    simulator_base_url:    str = "http://simulator:8080"
    rabbitmq_url:          str = "amqp://guest:guest@rabbitmq:5672/"
    rabbitmq_exchange:     str = "mars.events"
    poll_interval_seconds: int = 5


# ── REST sensors (polled every POLL_INTERVAL_SECONDS) ─────────────────────────
# Schema mapping:
#   rest.scalar.v1     → greenhouse_temperature, entrance_humidity, co2_hall, corridor_pressure
#   rest.chemistry.v1  → hydroponic_ph, air_quality_voc
#   rest.particulate.v1→ air_quality_pm25
#   rest.level.v1      → water_tank_level
REST_SENSORS: list[str] = [
    "greenhouse_temperature",
    "entrance_humidity",
    "co2_hall",
    "corridor_pressure",
    "hydroponic_ph",
    "air_quality_voc",
    "air_quality_pm25",
    "water_tank_level",
]

# ── Telemetry topics (SSE stream) ─────────────────────────────────────────────
# Schema mapping:
#   topic.power.v1       → solar_array, power_bus, power_consumption
#   topic.environment.v1 → radiation, life_support
#   topic.thermal_loop.v1→ thermal_loop
#   topic.airlock.v1     → airlock
TELEMETRY_TOPICS: list[str] = [
    "mars/telemetry/solar_array",
    "mars/telemetry/power_bus",
    "mars/telemetry/power_consumption",
    "mars/telemetry/radiation",
    "mars/telemetry/life_support",
    "mars/telemetry/thermal_loop",
    "mars/telemetry/airlock",
]

settings = Settings()
