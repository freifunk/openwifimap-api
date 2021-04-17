import logging
import os

from asyncpg import create_pool
from starlette.middleware.cors import CORSMiddleware

from starlette.requests import Request
from starlette.responses import Response
from yoyo import get_backend, read_migrations

from fastapi import FastAPI

from backend import restapi
from backend.utils import DB_URL

LOG = logging.getLogger(__name__)


def create_app():
    app = FastAPI(title="OWM Backend")

    async def startup():
        database_url = DB_URL
        backend = get_backend(database_url)
        sqlfolder = os.path.abspath(os.path.join(__file__, '..', '..', "sql"))
        migrations = read_migrations(sqlfolder)
        with backend.lock():
            backend.apply_migrations(backend.to_apply(migrations))
        app.extra["db"] = await create_pool(dsn=database_url, max_size=25)

    async def shutdown():
        await app.extra["db"].close()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://map.weimarnetz.de", "https://openwifimap.net", "http://localhost:3000"], allow_headers=["*"], allow_methods=["*"]
    )

    app.add_event_handler('startup', startup)
    app.add_event_handler('shutdown', shutdown)

    app.include_router(restapi.router, prefix="")

    @app.exception_handler(Exception)
    async def custom_exception_handler(request: Request, exception: Exception):
        LOG.exception("uncaught exception")
        return Response(status_code=500)

    return app
