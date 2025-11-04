import uvicorn
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse
from fastapi import FastAPI, Request
from agent.core import config
# from agent.core import tasks
from agent.core.logger import logger
from agent.api.routes.health_route import router as health_router
from agent.api.routes.agents.a2a import router as a2a_router


BASE_PATH = "/a2a-coach"

tags_metadata = [
    {"name": "Health", "description": "Health status of the API Endpoints"},
    {"name": "A2A-Coach", "description": "Multi-Modal Coach Agent (A2A) API Routes"},
]

def get_application():
    fast_api = FastAPI(
        title=config.PROJECT_NAME,
        version=config.VERSION,
        docs_url=(
            f"{BASE_PATH}/docs"
        ),
        openapi_url=f"{BASE_PATH}/docs/openapi.json",
        redoc_url=f"{BASE_PATH}/redoc",
    )

    fast_api.add_middleware(
        CORSMiddleware,
        allow_origins=config.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    fast_api.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY)

    # fast_api.add_event_handler("startup", tasks.create_start_app_handler(fast_api))
    # fast_api.add_event_handler("shutdown", tasks.create_stop_app_handler(fast_api))

    fast_api.include_router(health_router, prefix=BASE_PATH)
    fast_api.include_router(a2a_router, prefix=BASE_PATH)

    return fast_api


app = get_application()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    status_code, detail, url_path = exc.status_code, exc.detail, request.url.path
    logger.error(f"status code: {status_code}, detail: {detail}, url path: {url_path}")
    return JSONResponse(status_code=status_code, content=detail)


def main():
    logger.info("Starting A2A-Coach API Platform...")
    uvicorn.run(
        "agent.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False if config.ENV.startswith("deployment") else True,
        workers=1
    )


if __name__ == "__main__":
    main()
