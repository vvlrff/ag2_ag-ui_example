from autogen.beta import Agent
from autogen.beta.config import OpenAIConfig
from autogen.beta.middleware import Middleware
from dishka import AsyncContainer
from dishka_ag2 import DishkaAsyncMiddleware

from ag2_example.api.agent.prompts import SYSTEM_PROMPT
from ag2_example.api.agent.tools import notes_toolkit, weather


def build_agent(config: OpenAIConfig, container: AsyncContainer) -> Agent:
    return Agent(
        name="example_assistant",
        prompt=SYSTEM_PROMPT,
        config=config,
        tools=[weather, notes_toolkit()],
        middleware=[Middleware(DishkaAsyncMiddleware, container=container)],
    )
