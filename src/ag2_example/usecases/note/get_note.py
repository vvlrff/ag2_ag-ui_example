from dataclasses import dataclass

from ag2_example.domain.entities import Note, NoteId
from ag2_example.gateways import NoteRepository
from ag2_example.usecases.errors import NoteNotFoundError


@dataclass(kw_only=True)
class GetNoteRequest:
    note_id: NoteId


@dataclass(kw_only=True)
class GetNoteResponse:
    note: Note


class GetNoteUseCase:
    def __init__(self, repo: NoteRepository) -> None:
        self._repo = repo

    async def execute(self, request: GetNoteRequest) -> GetNoteResponse:
        note = await self._repo.get_by_id(request.note_id)
        if note is None:
            raise NoteNotFoundError(request.note_id)
        return GetNoteResponse(note=note)
