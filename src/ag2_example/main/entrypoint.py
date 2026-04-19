from contextlib import asynccontextmanager
from typing import Any

import httpx
from autogen.beta import Agent
from autogen.beta.config import OpenAIConfig
from dishka import Provider
from fastapi import FastAPI

from ag2_example.api.agent import build_agent
from ag2_example.api.middlewares import RequestIDMiddleware
from ag2_example.api.routes import routers as api_routers
from ag2_example.config import Settings
from ag2_example.logging_config import configure_logging
from ag2_example.main.di import create_container, default_providers
from ag2_example.main.middleware import AG2ContainerMiddleware


def create_app(
    *providers: Provider,
    settings: Settings | None = None,
    context: dict[Any, Any] | None = None,
) -> FastAPI:
    settings = settings or Settings()

    configure_logging(level=settings.log_level, json_output=settings.log_json)

    container = create_container(
        *(providers or default_providers()),
        context={**(context or {}), Settings: settings},
    )

    openai_http_client: httpx.AsyncClient | None = None
    openai_kwargs: dict[str, Any] = {
        "model": settings.openai_model,
        "api_key": settings.openai_api_key.get_secret_value(),
    }
    if settings.openai_proxy_url:
        openai_http_client = httpx.AsyncClient(proxy=settings.openai_proxy_url)
        openai_kwargs["http_client"] = openai_http_client

    agent: Agent = build_agent(OpenAIConfig(**openai_kwargs), container)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            yield
        finally:
            if openai_http_client is not None:
                await openai_http_client.aclose()
            await container.close()

    app = FastAPI(
        title=settings.app_name,
        description="Public reference example: FastAPI + Dishka + AG2.beta",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(AG2ContainerMiddleware, container=container)
    app.state.dishka_container = container
    app.state.agent = agent

    app.router.prefix = "/api"
    for router in api_routers:
        app.include_router(router)

    return app


app = create_app()
