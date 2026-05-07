from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from autogen.beta import Toolkit, tool
from dishka_ag2 import FromDishka, inject

from ag2_example.domain.entities import Note, NoteId
from ag2_example.usecases import (
    CreateNoteRequest,
    CreateNoteUseCase,
    DeleteNoteRequest,
    DeleteNoteUseCase,
    ListNotesRequest,
    ListNotesUseCase,
)


@dataclass(slots=True, frozen=True)
class NoteToolResult:
    id: UUID
    title: str
    body: str
    created_at: datetime

    @classmethod
    def from_entity(cls, note: Note) -> "NoteToolResult":
        return cls(
            id=note.id,
            title=note.title,
            body=note.body,
            created_at=note.created_at,
        )


@tool
@inject
async def list_notes(
    uc: FromDishka[ListNotesUseCase],
    limit: int = 20,
) -> list[NoteToolResult]:
    """List notes stored in the database.

    Args:
        limit: maximum number of notes to return (newest first).
    """
    response = await uc.execute(ListNotesRequest(limit=limit))
    return [NoteToolResult.from_entity(n) for n in response.notes]


@tool
@inject
async def create_note(
    uc: FromDishka[CreateNoteUseCase],
    title: str,
    body: str = "",
) -> NoteToolResult:
    """Create a new note in the database.

    Args:
        title: short title of the note.
        body: full text body (optional).
    """
    response = await uc.execute(CreateNoteRequest(title=title, body=body))
    return NoteToolResult.from_entity(response.note)


@tool
@inject
async def delete_note(
    uc: FromDishka[DeleteNoteUseCase],
    note_id: str,
) -> str:
    """Delete a note by its UUID.

    Args:
        note_id: UUID of the note to delete.
    """
    await uc.execute(DeleteNoteRequest(note_id=NoteId(UUID(note_id))))
    return "deleted"


def notes_toolkit() -> Toolkit:
    return Toolkit(list_notes, create_note, delete_note)
