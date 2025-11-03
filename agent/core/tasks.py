from typing import Callable
from fastapi import FastAPI
from agent.db.tasks import connect_to_db, close_db_connection, redis_connect, redis_disconnect


def create_start_app_handler(
    app: FastAPI
) -> Callable:
    async def start_app() -> None:
        await connect_to_db(app)
        await redis_connect(app)
    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        await close_db_connection(app)
        await redis_disconnect(app)
    return stop_app
