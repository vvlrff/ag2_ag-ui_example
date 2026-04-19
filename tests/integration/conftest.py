from collections.abc import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine

from ag2_example.config import Settings
from ag2_example.main.entrypoint import create_app
from ag2_example.models import mapper_registry


@pytest.fixture(scope="module")
def settings() -> Settings:
    return Settings()


@pytest_asyncio.fixture
async def _db_ready(settings: Settings) -> AsyncIterator[None]:
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.drop_all)
        await conn.run_sync(mapper_registry.metadata.create_all)
    await engine.dispose()
    yield


@pytest.fixture
def app(_db_ready, settings: Settings) -> FastAPI:
    return create_app(settings=settings)


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c
