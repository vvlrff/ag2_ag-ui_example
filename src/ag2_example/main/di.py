from typing import Any

from dishka import AsyncContainer, Provider, make_async_container
from dishka_ag2 import AG2Provider, AG2Scope

from ag2_example.main.providers import (
    AgentProvider,
    DatabaseProvider,
    RepositoryProvider,
    SettingsProvider,
    UseCaseProvider,
)


def default_providers() -> tuple[Provider, ...]:
    return (
        SettingsProvider(),
        DatabaseProvider(),
        RepositoryProvider(),
        UseCaseProvider(),
        AgentProvider(),
        AG2Provider(),
    )


def create_container(*providers: Provider, context: dict[Any, Any] | None = None) -> AsyncContainer:
    return make_async_container(
        *providers,
        context=context,
        scopes=AG2Scope,
    )
