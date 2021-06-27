# pylint: disable=too-many-statements

import asyncio
from unittest.mock import AsyncMock

import aiormq


async def test__rabbitmq(com_rabbitmq_connection: aiormq.Connection) -> None:
    channel = await com_rabbitmq_connection.channel()

    exchange_name = "test_direct_exchange"
    queue_name = "test_queue"

    await channel.exchange_declare(
        exchange_name,
        exchange_type="direct",
    )
    await channel.queue_declare(queue_name, durable=True)
    await channel.queue_bind(queue_name, exchange_name, routing_key=queue_name)

    message_handler = AsyncMock()
    await channel.basic_consume(
        queue_name, message_handler, no_ack=True,
    )

    channel = await com_rabbitmq_connection.channel()
    await channel.basic_publish(
        b"Hello World!",
        exchange=exchange_name,
        routing_key=queue_name,
    )
    await asyncio.sleep(0.5)

    message_handler.assert_awaited_once()
