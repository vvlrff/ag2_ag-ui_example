from autogen.beta.config import OpenAIConfig
from dishka import Provider, provide
from dishka_ag2 import AG2Scope

from ag2_example.config import Settings


class AgentProvider(Provider):
    scope = AG2Scope.APP

    @provide
    def provide_openai_config(self, settings: Settings) -> OpenAIConfig:
        return OpenAIConfig(
            model=settings.openai_model,
            api_key=settings.openai_api_key.get_secret_value(),
        )
