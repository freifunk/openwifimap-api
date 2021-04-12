import asyncio
import logging
import os

import pytest
import asyncpg

from yoyo import read_migrations
from yoyo import get_backend

from backend.utils import DB_URL

LOG = logging.getLogger(__name__)


def create_db(db_url: str):
    backend = get_backend(db_url)
    sqlfolder = os.path.abspath(os.path.join(__file__, '..', '..', "sql"))
    migrations = read_migrations(sqlfolder)
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))


async def drop_all(pool: asyncpg.pool.Pool):
    await pool.execute(
        """
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
            FOR r in (SELECT n.nspname AS "schema", t.typname
                      FROM pg_catalog.pg_type t
                      JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
                      JOIN pg_catalog.pg_enum e ON t.oid = e.enumtypid
                      WHERE n.nspname = 'public'
                      GROUP BY 1, 2) LOOP
                EXECUTE 'DROP TYPE IF EXISTS ' || quote_ident(r.typname) || ' CASCADE';
            END LOOP;
        END $$;
        """)


@pytest.fixture
def database(loop: asyncio.events.AbstractEventLoop):
    pool = loop.run_until_complete(asyncpg.create_pool(DB_URL, loop=loop))
    try:
        create_db(DB_URL)
        yield pool

    finally:
        LOG.info("Test done, dropping tables")
        loop.run_until_complete(drop_all(pool))
        loop.run_until_complete(pool.close())
