from typing import Any, cast

from sqlalchemy import CursorResult, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ag2_example.domain.entities import Note, NoteId
from ag2_example.gateways.db.note.interface import NoteRepository
from ag2_example.models.tables import notes_table


class AlchemyNoteRepository(NoteRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, note: Note) -> Note:
        self.session.add(note)
        await self.session.flush()
        return note

    async def get_by_id(self, note_id: NoteId) -> Note | None:
        stmt = select(Note).where(notes_table.c.id == note_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def list(self, limit: int = 20, offset: int = 0) -> list[Note]:
        stmt = select(Note).order_by(notes_table.c.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def delete(self, note_id: NoteId) -> bool:
        stmt = delete(notes_table).where(notes_table.c.id == note_id)
        result = cast(CursorResult[Any], await self.session.execute(stmt))
        return (result.rowcount or 0) > 0
