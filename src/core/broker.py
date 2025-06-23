import json
import uuid
from dataclasses import dataclass
from typing import Awaitable, Callable

import aio_pika
from aio_pika.abc import (
    AbstractIncomingMessage,
    AbstractQueue,
    AbstractRobustChannel,
    AbstractRobustConnection,
)
from fastapi import FastAPI

from src.core.config import Settings


@dataclass
class BrokerClient:
    settings: Settings
    message_handler: Callable[[AbstractIncomingMessage], Awaitable[None]] | None = None
    _connection: AbstractRobustConnection | None = None
    _channel: AbstractRobustChannel | None = None
    _queue: AbstractQueue | None = None
    _callback_queue: AbstractQueue | None = None

    @staticmethod
    async def default_message_handler(message: AbstractIncomingMessage):
        async with message.process():
            body = message.body.decode()
            correlation_id = message.correlation_id
            print(body, correlation_id)

    async def send_mail(self, body: dict):
        message = aio_pika.Message(
            body=json.dumps(body).encode(),
            correlation_id=str(uuid.uuid4()),
            reply_to=self.settings.BROKER_MAIL_CALLBACK_TOPIC,
        )
        await self._channel.default_exchange.publish(
            message=message, routing_key=self.settings.BROKER_MAIL_TOPIC
        )

    async def start(self):
        self._connection = await aio_pika.connect_robust(self.settings.BROKER_URL)
        self._channel = await self._connection.channel()
        self._queue = await self._channel.declare_queue(
            self.settings.BROKER_MAIL_TOPIC, durable=True
        )
        self._callback_queue = await self._channel.declare_queue(
            self.settings.BROKER_MAIL_CALLBACK_TOPIC, durable=True
        )

    async def stop(self):
        await self._channel.close()
        await self._connection.close()

    async def consume(self):
        handler = self.default_message_handler
        if self.message_handler:
            handler = self.message_handler

        await self._callback_queue.consume(handler)


async def broker_startup(
    app: FastAPI,
    settings: Settings,
    message_handler: Callable[[AbstractIncomingMessage], Awaitable[None]] | None = None,
):
    broker_client = BrokerClient(settings=settings, message_handler=message_handler)
    app.state.broker_client = broker_client
    await broker_client.start()
    await broker_client.consume()


async def broker_shutdown(app: FastAPI):
    await app.state.broker_client.stop()