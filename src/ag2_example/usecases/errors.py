from ag2_example.domain.entities import NoteId


class NoteNotFoundError(Exception):
    def __init__(self, note_id: NoteId) -> None:
        super().__init__(f"Note {note_id} not found")
        self.note_id = note_id
