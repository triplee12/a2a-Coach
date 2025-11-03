import redis
from rq import Queue
from agent.core.config import REDIS_URL
from agent.core.logger import logger
from agent.services.agent import run_gemini

redis_conn = redis.from_url(REDIS_URL)
queue = Queue("telex_tasks", connection=redis_conn)


def long_coach_task(user_input: str):
    """Long-running background analysis that calls the LLM (sync wrapper)."""
    logger.info({"event": "background_coaching", "user_input": user_input})
    try:
        result = run_gemini(user_input)
    except Exception as e:
        result = f"Background task failed: {e}"
    logger.info("[worker] background coaching result:\n", result)
    return result


if __name__ == "__main__":
    from rq import Worker, connections

    with connections.RedisConnection(redis_conn):
        worker = Worker([queue])
        worker.work()