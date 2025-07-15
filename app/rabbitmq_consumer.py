import json
import os

import aio_pika

from app.repositories.user_repo import user_repo

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
QUEUE_NAME = os.getenv("QUEUE_NAME", "user_created_queue")


async def handle_message(message: aio_pika.IncomingMessage):
    async with message.process():
        data = json.loads(message.body.decode())
        username = data["username"]

        print(f"[INFO] Received message: creating user with username='{username}'")
        user_repo.create_user(username)
        print(f"[INFO] User '{username}' successfully created in Follow service")


async def start_consumer():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()

    queue = await channel.declare_queue(QUEUE_NAME, durable=True)
    await queue.consume(handle_message)

    print(f"[INFO] Listening to the queue '{QUEUE_NAME}' for user creation events...")
