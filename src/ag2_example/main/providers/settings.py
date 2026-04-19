from dishka import Provider, from_context
from dishka_ag2 import AG2Scope

from ag2_example.config import Settings


class SettingsProvider(Provider):
    settings = from_context(Settings, scope=AG2Scope.APP)
