import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel, AbstractIncomingMessage
from fastapi import FastAPI

from src.core.config import Settings


async def broker_connection_init(settings: Settings) -> AbstractRobustConnection:
    return await aio_pika.connect_robust(settings.BROKER_URL)


async def broker_channel_init(connection: AbstractRobustConnection) -> AbstractRobustChannel:
    return await connection.channel()


async def broker_startup(app: FastAPI, settings: Settings):
    app.state.publisher_connection = await broker_connection_init(settings=settings)
    app.state.publisher_channel = await broker_channel_init(
        connection=app.state.publisher_connection
    )

    app.state.consumer_connection = await broker_connection_init(settings=settings)
    app.state.consumer_channel = await broker_channel_init(connection=app.state.consumer_connection)
    await broker_consumer_init(settings=settings, channel=app.state.consumer_channel)


async def broker_shutdown(app: FastAPI):
    await app.state.publisher_channel.close()
    await app.state.publisher_connection.close()

    await app.state.consumer_channel.close()
    await app.state.consumer_connection.close()


async def broker_consumer_init(settings: Settings, channel: AbstractRobustChannel) -> None:
    queue = await channel.declare_queue(settings.BROKER_MAIL_CALLBACK_TOPIC, durable=True)

    await queue.consume(consume_callback_message)


async def consume_callback_message(message: AbstractIncomingMessage):
    async with message.process():
        email_body = message.body.decode()
        correlation_id = message.correlation_id
        print(email_body, correlation_id)
