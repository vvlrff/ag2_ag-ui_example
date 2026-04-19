from dishka import AsyncContainer
from dishka_ag2 import AG2Scope
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send


class AG2ContainerMiddleware:
    def __init__(self, app: ASGIApp, container: AsyncContainer) -> None:
        self.app = app
        self.container = container

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive, send)
        async with self.container(
            context={Request: request},
            scope=AG2Scope.REQUEST,
        ) as request_container:
            request.state.dishka_container = request_container
            await self.app(scope, receive, send)
