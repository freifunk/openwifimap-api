import logging

import pytest

from backend.app import create_app

LOG = logging.getLogger(__name__)


pytest_plugins = [
    "tests.database_plugin",
    "tests.uvicorn_asyncio_plugin"
]


@pytest.fixture
def test_app(uvicorn_client, database, monkeypatch):
    app = create_app()
    yield uvicorn_client(app, config_args={"proxy_headers": False})
