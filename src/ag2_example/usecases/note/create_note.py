from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from ag2_example.domain.entities import Note, NoteId
from ag2_example.gateways import NoteRepository
from ag2_example.usecases.uow import UnitOfWork


@dataclass(kw_only=True)
class CreateNoteRequest:
    title: str
    body: str = ""


@dataclass(kw_only=True)
class CreateNoteResponse:
    note: Note


class CreateNoteUseCase:
    def __init__(self, repo: NoteRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    async def execute(self, request: CreateNoteRequest) -> CreateNoteResponse:
        note = Note(
            id=NoteId(uuid4()),
            title=request.title,
            body=request.body,
            created_at=datetime.now(UTC),
        )
        created = await self._repo.create(note)
        await self._uow.commit()
        return CreateNoteResponse(note=created)
