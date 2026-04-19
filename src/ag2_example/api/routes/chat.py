from typing import Annotated

from autogen.beta import Agent
from autogen.beta.ag_ui import AGUIStream, RunAgentInput
from fastapi import APIRouter, Body, Header, Request
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def run_agent(
    run_input: Annotated[RunAgentInput, Body()],
    request: Request,
    accept: Annotated[str | None, Header()] = None,
) -> StreamingResponse:
    agent: Agent = request.app.state.agent
    stream = AGUIStream(agent)
    return StreamingResponse(
        stream.dispatch(run_input, accept=accept),
        media_type=accept or "text/event-stream",
    )
