from uuid import UUID

from autogen.beta import Toolkit, tool
from dishka_ag2 import FromDishka, inject

from ag2_example.domain.entities import NoteId
from ag2_example.usecases import (
    CreateNoteRequest,
    CreateNoteUseCase,
    DeleteNoteRequest,
    DeleteNoteUseCase,
    ListNotesRequest,
    ListNotesUseCase,
)


@tool
@inject
async def list_notes(
    uc: FromDishka[ListNotesUseCase],
    limit: int = 20,
) -> list[dict[str, str]]:
    """List notes stored in the database.

    Args:
        limit: maximum number of notes to return (newest first).
    """
    response = await uc.execute(ListNotesRequest(limit=limit))
    return [{"id": str(n.id), "title": n.title, "body": n.body} for n in response.notes]


@tool
@inject
async def create_note(
    uc: FromDishka[CreateNoteUseCase],
    title: str,
    body: str = "",
) -> dict[str, str]:
    """Create a new note in the database.

    Args:
        title: short title of the note.
        body: full text body (optional).
    """
    response = await uc.execute(CreateNoteRequest(title=title, body=body))
    note = response.note
    return {"id": str(note.id), "title": note.title, "body": note.body}


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
