from dataclasses import dataclass

from ag2_example.domain.entities import Note
from ag2_example.gateways import NoteRepository


@dataclass(kw_only=True)
class ListNotesRequest:
    limit: int = 20
    offset: int = 0


@dataclass(kw_only=True)
class ListNotesResponse:
    notes: list[Note]


class ListNotesUseCase:
    def __init__(self, repo: NoteRepository) -> None:
        self._repo = repo

    async def execute(self, request: ListNotesRequest) -> ListNotesResponse:
        notes = await self._repo.list(limit=request.limit, offset=request.offset)
        return ListNotesResponse(notes=notes)
