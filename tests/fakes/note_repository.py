from ag2_example.domain.entities import Note, NoteId
from ag2_example.gateways import NoteRepository


class FakeNoteRepository(NoteRepository):
    def __init__(self) -> None:
        self._notes: dict[NoteId, Note] = {}

    async def create(self, note: Note) -> Note:
        self._notes[note.id] = note
        return note

    async def get_by_id(self, note_id: NoteId) -> Note | None:
        return self._notes.get(note_id)

    async def list(self, limit: int = 20, offset: int = 0) -> list[Note]:
        items = sorted(self._notes.values(), key=lambda n: n.created_at, reverse=True)
        return items[offset : offset + limit]

    async def delete(self, note_id: NoteId) -> bool:
        return self._notes.pop(note_id, None) is not None
