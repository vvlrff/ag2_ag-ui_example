from dataclasses import dataclass
from datetime import datetime
from typing import NewType
from uuid import UUID

NoteId = NewType("NoteId", UUID)


@dataclass(kw_only=True)
class Note:
    id: NoteId
    title: str
    body: str
    created_at: datetime
