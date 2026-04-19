from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, HTTPException, Path, Query, status

from ag2_example.api.schemas.note import NoteCreate, NoteList, NoteRead
from ag2_example.domain.entities import NoteId
from ag2_example.usecases import (
    CreateNoteRequest,
    CreateNoteUseCase,
    DeleteNoteRequest,
    DeleteNoteUseCase,
    GetNoteRequest,
    GetNoteUseCase,
    ListNotesRequest,
    ListNotesUseCase,
)
from ag2_example.usecases.errors import NoteNotFoundError

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_note(
    payload: NoteCreate,
    use_case: FromDishka[CreateNoteUseCase],
) -> NoteRead:
    response = await use_case.execute(CreateNoteRequest(title=payload.title, body=payload.body))
    return NoteRead.from_entity(response.note)


@router.get("")
@inject
async def list_notes(
    use_case: FromDishka[ListNotesUseCase],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> NoteList:
    response = await use_case.execute(ListNotesRequest(limit=limit, offset=offset))
    return NoteList(
        notes=[NoteRead.from_entity(n) for n in response.notes],
        total=len(response.notes),
    )


@router.get("/{note_id}")
@inject
async def get_note(
    note_id: Annotated[UUID, Path()],
    use_case: FromDishka[GetNoteUseCase],
) -> NoteRead:
    try:
        response = await use_case.execute(GetNoteRequest(note_id=NoteId(note_id)))
    except NoteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return NoteRead.from_entity(response.note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_note(
    note_id: Annotated[UUID, Path()],
    use_case: FromDishka[DeleteNoteUseCase],
) -> None:
    try:
        await use_case.execute(DeleteNoteRequest(note_id=NoteId(note_id)))
    except NoteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
