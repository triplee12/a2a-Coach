"""
Centralized logic for declaring application environment variables
"""

import pathlib
import os
from databases import DatabaseURL
from starlette.config import Config
from starlette.datastructures import Secret

env_path = os.environ.get("ENV_FILE_PATH") or pathlib.Path(__file__).resolve().parents[0] / ".env"
config = Config(env_path)

PROJECT_NAME = config("APP_NAME", cast=str, default="multi_modal_coach-agent")
VERSION = config("APP_VERSION", cast=str)
ALLOWED_ORIGINS = config("ALLOWED_ORIGINS", cast=list)
SECRET_KEY = config("SECRET_KEY", cast=str)
ENV = config("ENV", cast=str)
LOG_PATH = os.getenv("AGENT_LOG_PATH", cast=str, default="agent_interactions.log")
AGENT_API_KEY = os.getenv("AGENT_API_KEY", cast=str, default=None)
TELEX_LOG_BASE = os.getenv("TELEX_LOG_BASE", cast=str, default="https://api.telex.im/agent-logs")

POSTGRES_USER = config("POSTGRES_USER", cast=str)
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", cast=Secret)
POSTGRES_SERVER = config("POSTGRES_HOST", cast=str)
POSTGRES_PORT = config("POSTGRES_PORT", cast=str, default="5432")
POSTGRES_DB = config("POSTGRES_DB", cast=str)

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

db_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

DATABASE_URL = config(
    "DATABASE_URL",
    cast=DatabaseURL,
    default=db_url
)

GEMINI_API_KEY=config("GEMINI_API_KEY", cast=str)

ACCESS_TOKEN_EXPIRE_MINS = config("ACCESS_TOKEN_EXPIRE_MINS", cast=int, default=30)
JWT_TOKEN_ALGORITHM = config("JWT_TOKEN_ALGORITHM", cast=str, default="HS256")
JWT_TOKEN_SECRET_KEY = config("JWT_TOKEN_SECRET_KEY", cast=str)
