from uuid import uuid4

import pytest

from ag2_example.domain.entities import NoteId
from ag2_example.usecases.errors import NoteNotFoundError
from ag2_example.usecases.note import (
    CreateNoteRequest,
    CreateNoteUseCase,
    DeleteNoteRequest,
    DeleteNoteUseCase,
    GetNoteRequest,
    GetNoteUseCase,
    ListNotesRequest,
    ListNotesUseCase,
)
from tests.fakes.note_repository import FakeNoteRepository
from tests.fakes.uow import FakeUnitOfWork


@pytest.mark.asyncio
async def test_create_note_commits_and_returns_note():
    repo = FakeNoteRepository()
    uow = FakeUnitOfWork()
    uc = CreateNoteUseCase(repo=repo, uow=uow)

    response = await uc.execute(CreateNoteRequest(title="hello", body="world"))

    assert response.note.title == "hello"
    assert response.note.body == "world"
    assert uow.commits == 1
    assert await repo.get_by_id(response.note.id) is response.note


@pytest.mark.asyncio
async def test_list_notes_returns_newest_first():
    repo = FakeNoteRepository()
    create_uc = CreateNoteUseCase(repo=repo, uow=FakeUnitOfWork())
    first = (await create_uc.execute(CreateNoteRequest(title="first"))).note
    second = (await create_uc.execute(CreateNoteRequest(title="second"))).note

    response = await ListNotesUseCase(repo=repo).execute(ListNotesRequest(limit=10))

    assert [n.id for n in response.notes] == [second.id, first.id]


@pytest.mark.asyncio
async def test_get_note_raises_when_missing():
    uc = GetNoteUseCase(repo=FakeNoteRepository())
    with pytest.raises(NoteNotFoundError):
        await uc.execute(GetNoteRequest(note_id=NoteId(uuid4())))


@pytest.mark.asyncio
async def test_delete_note_removes_and_commits():
    repo = FakeNoteRepository()
    uow = FakeUnitOfWork()
    note = (
        await CreateNoteUseCase(repo=repo, uow=FakeUnitOfWork()).execute(
            CreateNoteRequest(title="todo")
        )
    ).note

    await DeleteNoteUseCase(repo=repo, uow=uow).execute(DeleteNoteRequest(note_id=note.id))

    assert await repo.get_by_id(note.id) is None
    assert uow.commits == 1


@pytest.mark.asyncio
async def test_delete_note_raises_when_missing():
    uc = DeleteNoteUseCase(repo=FakeNoteRepository(), uow=FakeUnitOfWork())
    with pytest.raises(NoteNotFoundError):
        await uc.execute(DeleteNoteRequest(note_id=NoteId(uuid4())))
