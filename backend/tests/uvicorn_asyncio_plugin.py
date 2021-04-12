import asyncio
import os
import sys
import logging
import gc
import contextlib
import warnings
import socket
from typing import Optional, Dict, Any
import uvloop
from pytest import fixture
import uvicorn
import httpx

# prevent asyncio debug logs
asyncio_logger = logging.getLogger("asyncio")
asyncio_logger.setLevel(logging.INFO)

# pytest async helper code is partially taken from
# https://github.com/aio-libs/aiohttp/blob/master/aiohttp/pytest_plugin.py
# Copyright 2013-2020 aio-libs collaboration.
# Licensed under the Apache License, Version 2.0


def pytest_addoption(parser):  # type: ignore
    parser.addoption(
        '--disable-extra-checks', action='store_true', default=False,
        help='run tests faster by disabling extra checks')
    parser.addoption(
        '--enable-loop-debug', action='store_true', default=False,
        help='enable event loop debug mode')


def teardown_test_loop(loop, fast=False):
    closed = loop.is_closed()
    if not closed:
        pending = asyncio.all_tasks(loop)
        loop.run_until_complete(asyncio.gather(*pending, loop=loop))
        loop.call_soon(loop.stop)
        loop.run_forever()
        loop.close()
    if not fast:
        gc.collect()
    asyncio.set_event_loop(None)


@contextlib.contextmanager
def _passthrough_loop_context(loop, fast=False):  # type: ignore
    """
    setups and tears down a loop unless one is passed in via the loop
    argument when it's passed straight through.
    """
    if loop:
        # loop already exists, pass it straight through
        yield loop
    else:
        # this shadows loop_context's standard behavior
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        yield loop
        teardown_test_loop(loop, fast=fast)


@contextlib.contextmanager
def _runtime_warning_context():  # type: ignore
    """
    Context manager which checks for RuntimeWarnings, specifically to
    avoid "coroutine 'X' was never awaited" warnings being missed.
    If RuntimeWarnings occur in the context a RuntimeError is raised.
    """
    with warnings.catch_warnings(record=True) as _warnings:
        yield
        rw = ['{w.filename}:{w.lineno}:{w.message}'.format(w=w)
              for w in _warnings
              if w.category == RuntimeWarning]
        if rw:
            raise RuntimeError('{} Runtime Warning{},\n{}'.format(
                len(rw),
                '' if len(rw) == 1 else 's',
                '\n'.join(rw)
            ))


def pytest_pyfunc_call(pyfuncitem):  # type: ignore
    """
    Run coroutines in an event loop instead of a normal function call.
    """
    fast = pyfuncitem.config.getoption("--disable-extra-checks")
    if asyncio.iscoroutinefunction(pyfuncitem.function):
        existing_loop = pyfuncitem.funcargs.get('loop', None)
        with _runtime_warning_context():
            with _passthrough_loop_context(existing_loop, fast=fast) as _loop:
                testargs = {arg: pyfuncitem.funcargs[arg]
                            for arg in pyfuncitem._fixtureinfo.argnames}
                _loop.run_until_complete(pyfuncitem.obj(**testargs))
        return True


@fixture(scope="session")
def fast(request):  # type: ignore
    """--fast config option"""
    return request.config.getoption('--disable-extra-checks')


@fixture(scope="session")
def loop_debug(request):  # type: ignore
    """--enable-loop-debug config option"""
    return request.config.getoption('--enable-loop-debug')


@fixture(scope="session")
def loop(fast, loop_debug):
    policy = uvloop.EventLoopPolicy()
    asyncio.set_event_loop_policy(policy)
    _loop = asyncio.new_event_loop()
    if loop_debug:
        _loop.set_debug(True)  # pragma: no cover
    asyncio.set_event_loop(_loop)
    yield _loop
    teardown_test_loop(_loop, fast=fast)


class TestClient:
    def __init__(self, host, port):
        self.base_url = f'http://{host}:{port}'
        self.client = httpx.AsyncClient()

    def get(self, url, *args, **kwargs):
        url = f'{self.base_url}{url}'
        return self.client.get(url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        url = f'{self.base_url}{url}'
        return self.client.post(url, *args, **kwargs)

    def put(self, url, *args, **kwargs):
        url = f'{self.base_url}{url}'
        return self.client.put(url, *args, **kwargs)

    def delete(self, url, *args, **kwargs):
        url = f'{self.base_url}{url}'
        return self.client.delete(url, *args, **kwargs)

    def options(self, url, *args, **kwargs):
        url = f'{self.base_url}{url}'
        return self.client.options(url, *args, **kwargs)


@fixture
def uvicorn_client(loop):
    servers = []

    async def _init_server(config):
        server = uvicorn.Server(config=config)
        config.load()
        server.lifespan = config.lifespan_class(config)
        await server.startup()
        return server

    def create_client(app, config_args: Optional[Dict[str,Any]] = None):
        """
        Run server for app on an unused port and return client for testing.
        """
        sock = get_port_socket('127.0.0.1', 0)
        host, port = sock.getsockname()[:2]
        if config_args is None:
            config_args = {}
        config = uvicorn.Config(app, port=port, log_config={
            "version": 1,
            "disable_existing_loggers": False
        }, **config_args)
        server = loop.run_until_complete(_init_server(config))
        assert not server.should_exit, "Failed to start server process"
        task = loop.create_task(server.main_loop())
        client = TestClient(host, port)
        servers.append((client, server, task))
        return client

    yield create_client

    async def _shutdown(client, server, task):
        await client.client.aclose()
        server.should_exit = True
        await task
        await server.shutdown()

    for (client, server, task) in servers:
        loop.create_task(_shutdown(client, server, task))


REUSE_ADDRESS = os.name == 'posix' and sys.platform != 'cygwin'


def get_port_socket(host: str, port: int) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if REUSE_ADDRESS:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    return s
