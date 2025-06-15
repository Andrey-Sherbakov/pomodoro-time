import asyncio
import json
from dataclasses import dataclass

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from fastapi import FastAPI

from src.core.config import Settings


@dataclass
class BrokerClient:
    settings: Settings
    _producer: AIOKafkaProducer | None = None
    _consumer: AIOKafkaConsumer | None = None
    _consumer_task: asyncio.Task | None = None

    async def start(self):
        await self._start_producer()
        await self._start_consumer()

    async def stop(self):
        await self._stop_producer()
        await self._stop_consumer()

    async def send_mail(self, message: dict) -> None:
        await self._producer.send_and_wait(self.settings.BROKER_MAIL_TOPIC, message)

    @staticmethod
    async def mail_callback_message_handler(message: dict):
        print("Received message:", message)

    async def _start_producer(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self.settings.BROKER_URL,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self._producer.start()

    async def _stop_producer(self) -> None:
        if self._producer:
            await self._producer.stop()

    async def _start_consumer(self) -> None:
        self._consumer = AIOKafkaConsumer(
            self.settings.BROKER_MAIL_CALLBACK_TOPIC,
            bootstrap_servers=self.settings.BROKER_URL,
            group_id=self.settings.BROKER_GROUP_ID,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )
        await self._consumer.start()
        self._consumer_task = asyncio.create_task(self._consume_loop())

    async def _stop_consumer(self) -> None:
        if self._consumer_task:
            self._consumer_task.cancel()
        if self._consumer:
            await self._consumer.stop()

    async def _consume_loop(self) -> None:
        try:
            async for message in self._consumer:
                await self.mail_callback_message_handler(message.value)
        except asyncio.CancelledError:
            pass


async def broker_startup(app: FastAPI, settings: Settings):
    broker_client = BrokerClient(settings=settings)
    app.state.broker_client = broker_client
    await broker_client.start()


async def broker_shutdown(app: FastAPI):
    await app.state.broker_client.stop()
