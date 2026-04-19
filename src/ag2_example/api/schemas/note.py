from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from ag2_example.domain.entities import Note


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=512)
    body: str = ""


class NoteRead(BaseModel):
    id: UUID
    title: str
    body: str
    created_at: datetime

    @classmethod
    def from_entity(cls, note: Note) -> "NoteRead":
        return cls(
            id=note.id,
            title=note.title,
            body=note.body,
            created_at=note.created_at,
        )


class NoteList(BaseModel):
    notes: list[NoteRead]
    total: int
