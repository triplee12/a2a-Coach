import os
import asyncio
import aioredis
from fastapi import FastAPI
from databases import Database
from agent.core.config import DATABASE_URL
from agent.core.logger import logger
from agent.core.config import REDIS_URL

redis = None

MAX_RETRIES = 5
INITIAL_DELAY = 2


async def redis_connect(app: FastAPI):
    global redis
    redis = await aioredis.from_url(REDIS_URL)
    await redis.set("agent_startup", "1")
    app.state._redis = redis


async def redis_disconnect(app: FastAPI):
    global redis
    if redis:
        await redis.close()
    app.state._redis = None


async def connect_to_db(app: FastAPI) -> None:
    db_url = f"""{DATABASE_URL}{os.environ.get("DB_SUFFIX", "")}"""
    database = Database(db_url, min_size=2, max_size=10)

    retries = 0
    delay = INITIAL_DELAY

    while retries < MAX_RETRIES:
        try:
            await database.connect()
            app.state._db = database
            logger.info("Connected to the database.")
            return
        except Exception as e:
            logger.error(f"DB CONNECTION ERROR (attempt {retries + 1})")
            logger.error(e)
            retries += 1

            if retries < MAX_RETRIES:
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
                delay *= 2
            else:
                logger.error("Max retries reached. Could not connect to the database.")
                raise e


async def close_db_connection(app: FastAPI) -> None:
    try:
        await app.state._db.disconnect()
    except Exception as e:
        logger.error("--- DB DISCONNECT ERROR ---")
        logger.error(e)
        logger.error("--- DB DISCONNECT ERROR ---")
