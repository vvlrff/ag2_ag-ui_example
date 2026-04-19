from dishka import Provider, WithParents, provide
from dishka_ag2 import AG2Scope

from ag2_example.gateways.db.note import AlchemyNoteRepository


class RepositoryProvider(Provider):
    scope = AG2Scope.REQUEST

    note_repository = provide(
        AlchemyNoteRepository,
        provides=WithParents[AlchemyNoteRepository],
    )
