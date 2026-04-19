from dirty_equals import IsDatetime, IsStr
from fastapi.testclient import TestClient


def test_crud_round_trip(client: TestClient) -> None:
    created = client.post("/api/notes", json={"title": "hello", "body": "world"})
    assert created.status_code == 201, created.text
    note = created.json()
    assert note == {
        "id": IsStr,
        "title": "hello",
        "body": "world",
        "created_at": IsDatetime(iso_string=True),
    }
    note_id = note["id"]

    listed = client.get("/api/notes")
    assert listed.status_code == 200
    assert listed.json() == {"notes": [note], "total": 1}

    fetched = client.get(f"/api/notes/{note_id}")
    assert fetched.status_code == 200
    assert fetched.json() == note

    removed = client.delete(f"/api/notes/{note_id}")
    assert removed.status_code == 204

    missing = client.get(f"/api/notes/{note_id}")
    assert missing.status_code == 404


def test_list_empty(client: TestClient) -> None:
    resp = client.get("/api/notes")
    assert resp.status_code == 200
    assert resp.json() == {"notes": [], "total": 0}
