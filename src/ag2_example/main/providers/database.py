from collections.abc import AsyncIterator

from dishka import AnyOf, Provider, provide
from dishka_ag2 import AG2Scope
from sqlalchemy import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ag2_example.config import Settings
from ag2_example.usecases.uow import UnitOfWork


class DatabaseProvider(Provider):
    @provide(scope=AG2Scope.APP)
    async def provide_async_engine(self, settings: Settings) -> AsyncIterator[AsyncEngine]:
        engine = create_async_engine(
            make_url(settings.database_url),
            pool_size=10,
            max_overflow=10,
            pool_timeout=10,
            pool_pre_ping=True,
        )
        yield engine
        await engine.dispose()

    @provide(scope=AG2Scope.APP)
    def provide_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker[AsyncSession](
            bind=engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    @provide(scope=AG2Scope.REQUEST)
    async def provide_async_session(
        self, pool: async_sessionmaker[AsyncSession]
    ) -> AsyncIterator[AnyOf[AsyncSession, UnitOfWork]]:
        async with pool() as session:
            yield session
