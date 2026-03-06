"""
collector/src/publisher.py — Robust RabbitMQ publisher using aio-pika.

Declares the `mars.events` fanout exchange and publishes InternalEvent
messages as persistent JSON blobs.
"""
from __future__ import annotations

import asyncio
import logging

import aio_pika
from aio_pika import ExchangeType, Message

from shared.schemas import InternalEvent

logger = logging.getLogger(__name__)

_RECONNECT_DELAY = 5  # seconds between retry attempts


async def connect_rabbitmq(
    url: str,
    exchange_name: str,
) -> tuple[aio_pika.RobustConnection, aio_pika.RobustChannel, aio_pika.Exchange]:
    """
    Establish a robust (auto-reconnecting) connection to RabbitMQ and
    declare the fanout exchange.  Retries indefinitely until success.

    Returns (connection, channel, exchange).
    """
    while True:
        try:
            logger.info("Connecting to RabbitMQ at %s ...", url)
            connection: aio_pika.RobustConnection = await aio_pika.connect_robust(url)
            channel: aio_pika.RobustChannel       = await connection.channel()
            exchange = await channel.declare_exchange(
                exchange_name,
                ExchangeType.FANOUT,
                durable=True,
            )
            logger.info("RabbitMQ ready. Exchange '%s' declared.", exchange_name)
            return connection, channel, exchange
        except Exception as exc:
            logger.warning(
                "RabbitMQ not ready (%s). Retrying in %ds ...",
                exc, _RECONNECT_DELAY,
            )
            await asyncio.sleep(_RECONNECT_DELAY)


async def publish_event(exchange: aio_pika.Exchange, event: InternalEvent) -> None:
    """
    Serialize an InternalEvent to JSON and publish it to the fanout exchange.
    Messages are marked PERSISTENT so they survive a RabbitMQ restart.
    """
    body = event.model_dump_json().encode()
    message = Message(
        body=body,
        content_type="application/json",
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
    )
    await exchange.publish(message, routing_key="")
    logger.debug(
        "Published event: source_id=%s schema=%s metrics=%d",
        event.source_id, event.raw_schema, len(event.metrics),
    )
