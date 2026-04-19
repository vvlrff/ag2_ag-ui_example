import os

import pytest
from fastapi.testclient import TestClient


@pytest.mark.skipif(
    not os.getenv("AG2EX__OPENAI_API_KEY") and not os.getenv("OPENAI_API_KEY"),
    reason="needs a real OpenAI API key to drive the LLM",
)
def test_chat_sse_streams_run_started_and_finished(client: TestClient) -> None:
    payload = {
        "threadId": "t1",
        "runId": "r1",
        "messages": [{"id": "m1", "role": "user", "content": "Calculate 2 + 2"}],
        "state": {},
        "context": [],
        "tools": [],
        "forwardedProps": {},
    }
    with client.stream(
        "POST",
        "/api/chat",
        json=payload,
        headers={"Accept": "text/event-stream"},
    ) as response:
        assert response.status_code == 200
        body = b"".join(response.iter_bytes()).decode()

    assert "RUN_STARTED" in body
    assert "RUN_FINISHED" in body


def test_chat_emits_run_started_even_without_llm(client: TestClient) -> None:
    payload = {
        "threadId": "t1",
        "runId": "r1",
        "messages": [{"id": "m1", "role": "user", "content": "hi"}],
        "state": {},
        "context": [],
        "tools": [],
        "forwardedProps": {},
    }
    with client.stream(
        "POST",
        "/api/chat",
        json=payload,
        headers={"Accept": "text/event-stream"},
        timeout=30,
    ) as response:
        assert response.status_code == 200
        first_chunk = b""
        for chunk in response.iter_bytes():
            first_chunk += chunk
            if b"RUN_STARTED" in first_chunk:
                break

    assert b"RUN_STARTED" in first_chunk
