from dataclasses import dataclass

from ag2_example.domain.entities import NoteId
from ag2_example.gateways import NoteRepository
from ag2_example.usecases.errors import NoteNotFoundError
from ag2_example.usecases.uow import UnitOfWork


@dataclass(kw_only=True)
class DeleteNoteRequest:
    note_id: NoteId


class DeleteNoteUseCase:
    def __init__(self, repo: NoteRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    async def execute(self, request: DeleteNoteRequest) -> None:
        deleted = await self._repo.delete(request.note_id)
        if not deleted:
            raise NoteNotFoundError(request.note_id)
        await self._uow.commit()
