"""
rules-engine/src/consumer.py — RabbitMQ consumer loop.

Binds an exclusive queue to the `mars.events` fanout exchange and processes
each message by:
  1. Deserialising the JSON body into an InternalEvent.
  2. Updating the Redis state cache + publishing to the Redis events channel.
  3. Running the rule evaluator (DB query + optional alert + actuator call).
"""
from __future__ import annotations

import asyncio
import json
import logging

import aio_pika
from aio_pika import ExchangeType
from sqlalchemy.ext.asyncio import AsyncSession

from shared.schemas import InternalEvent
from .config import settings
from .db import AsyncSessionLocal, engine
from .evaluator import evaluate_event
from .state_store import StateStore

logger = logging.getLogger(__name__)

_RECONNECT_DELAY = 5  # seconds


async def _process_message(
    message: aio_pika.IncomingMessage,
    store: StateStore,
) -> None:
    """Deserialise and handle a single RabbitMQ message."""
    async with message.process(requeue=False):
        try:
            raw  = json.loads(message.body)
            event = InternalEvent.model_validate(raw)
        except Exception as exc:
            logger.error("Cannot parse message: %s  body=%s", exc, message.body[:200])
            return

        # Update Redis state
        await store.set_state(event)
        await store.publish_event(event)

        # Evaluate rules (each message gets its own session)
        async with AsyncSessionLocal() as session:
            try:
                await evaluate_event(event, session, store)
            except Exception as exc:
                logger.error("Rule evaluation error for source_id=%s: %s", event.source_id, exc)
                await session.rollback()


async def consume_loop(store: StateStore) -> None:
    """
    Connect to RabbitMQ, bind an exclusive queue to `mars.events`, and
    consume messages in a loop.  Reconnects automatically on failure.
    """
    while True:
        try:
            logger.info("Connecting to RabbitMQ at %s ...", settings.rabbitmq_url)
            connection: aio_pika.RobustConnection = await aio_pika.connect_robust(
                settings.rabbitmq_url
            )
            channel: aio_pika.RobustChannel = await connection.channel()
            await channel.set_qos(prefetch_count=10)

            exchange = await channel.declare_exchange(
                settings.rabbitmq_exchange,
                ExchangeType.FANOUT,
                durable=True,
            )

            # Exclusive auto-delete queue — one per consumer instance
            queue = await channel.declare_queue("", exclusive=True, auto_delete=True)
            await queue.bind(exchange)

            logger.info("Consuming from exchange '%s' ...", settings.rabbitmq_exchange)
            async with queue.iterator() as q:
                async for message in q:
                    await _process_message(message, store)

        except Exception as exc:
            logger.warning(
                "Consumer connection error (%s). Reconnecting in %ds ...",
                exc, _RECONNECT_DELAY,
            )
            await asyncio.sleep(_RECONNECT_DELAY)
