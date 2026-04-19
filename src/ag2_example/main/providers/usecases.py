from dishka import Provider, provide_all
from dishka_ag2 import AG2Scope

from ag2_example.usecases import (
    CreateNoteUseCase,
    DeleteNoteUseCase,
    GetNoteUseCase,
    ListNotesUseCase,
)


class UseCaseProvider(Provider):
    all = provide_all(
        CreateNoteUseCase,
        DeleteNoteUseCase,
        GetNoteUseCase,
        ListNotesUseCase,
        scope=AG2Scope.REQUEST,
    )
