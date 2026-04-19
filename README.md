# ag2-ag-ui-example

A public reference example showing how to wire **[AG2.beta](https://github.com/ag2ai/ag2)** (the `autogen.beta` API) with the **[Dishka](https://dishka.readthedocs.io/)** DI container via the **[`dishka-ag2`](https://github.com/C3EQUALZz/dishka-ag2)** integration package, streaming agent output over the **[AG-UI protocol](https://github.com/ag-ui-protocol/ag-ui)** from a production-shaped **FastAPI** backend.

## Why this exists

`autogen.beta` has its own DI system (`fast-depends`), and Dishka has its own scopes (`APP` / `REQUEST`). Naively bridging them leads to hacks like "pass a `dependencies` dict by string keys". The community package `dishka-ag2` solves it properly with a custom scope (`AG2Scope`) and a middleware (`DishkaAsyncMiddleware`) that opens the right scope on every agent turn / tool call.

The result: **agent tools look like regular Dishka handlers** — `@tool @inject async def list_notes(uc: FromDishka[ListNotesUseCase], ...)`. No string keys, no manual wiring in the HTTP endpoint, no `dependencies=` dict passed to `AGUIStream.dispatch`.

## What's inside

- `FastAPI` with clean layered architecture (`domain → models → gateways → usecases → api → main`)
- `Dishka` container with `AG2Scope` — a single container serves both HTTP handlers and agent tools
- `autogen.beta.Agent` configured as an app-level singleton, with `DishkaAsyncMiddleware` attached
- AG-UI SSE chat endpoint via `autogen.beta.ag_ui.AGUIStream`
- PostgreSQL + SQLAlchemy 2.0 via async `psycopg3`
- Alembic migrations
- `import-linter` contracts
- `pytest` unit + integration tests
- `uv` deps, multi-stage Dockerfile, docker-compose with Postgres, GitHub Actions CI

## Quickstart

```bash
cp .env.example .env   # set AG2EX__OPENAI_API_KEY
docker compose up --build
```

Smoke-test:

```bash
curl http://127.0.0.1:8000/api/health                       # {"status":"healthy"}
curl -X POST http://127.0.0.1:8000/api/notes \
  -H 'Content-Type: application/json' \
  -d '{"title":"hello","body":"world"}'

curl -N -X POST http://127.0.0.1:8000/api/chat \
  -H 'Content-Type: application/json' \
  -H 'Accept: text/event-stream' \
  -d '{
    "threadId":"t1","runId":"r1",
    "messages":[{"id":"m1","role":"user","content":"Create a note titled hello with body world, then list all notes"}],
    "state":{},"context":[],"tools":[],"forwardedProps":{}
  }'
```

Expect an SSE stream: `RUN_STARTED → TOOL_CALL_START(create_note) → TOOL_CALL_RESULT → TOOL_CALL_START(list_notes) → TOOL_CALL_RESULT → TEXT_MESSAGE_CHUNK* → RUN_FINISHED`.

## How the bridge works

1. **One container, one scope family.** The container uses `AG2Scope` (from `dishka-ag2`). `AG2Scope.APP` holds app-level singletons; `AG2Scope.REQUEST` is opened both on every HTTP request and on every agent tool call.
2. **Agent is a singleton** built once in [`main/entrypoint.py`](src/ag2_example/main/entrypoint.py). `DishkaAsyncMiddleware` is attached to it and carries the container reference:
   ```python
   agent = Agent(
       ...,
       tools=[calculator, weather, notes_toolkit()],
       middleware=[Middleware(DishkaAsyncMiddleware, container=container)],
   )
   ```
3. **A tiny ASGI middleware** ([`main/middleware.py`](src/ag2_example/main/middleware.py)) opens `AG2Scope.REQUEST` on every HTTP request and attaches the request-scoped container to `request.state.dishka_container` — so the standard `dishka.integrations.fastapi` `@inject` keeps working for REST endpoints.
4. **Tools are just `@tool @inject` functions** — see [`api/agent/tools/notes.py`](src/ag2_example/api/agent/tools/notes.py):
   ```python
   @tool
   @inject
   async def list_notes(
       uc: FromDishka[ListNotesUseCase],
       limit: int = 20,
   ) -> list[dict[str, str]]:
       response = await uc.execute(ListNotesRequest(limit=limit))
       return [...]
   ```
   `DishkaAsyncMiddleware` opens an `AG2Scope.REQUEST` child container before the tool runs, and `dishka-ag2`'s `@inject` resolves `FromDishka[T]` out of it.
5. **The chat endpoint** ([`api/routes/chat.py`](src/ag2_example/api/routes/chat.py)) has **zero DI plumbing** — it just hands the agent to `AGUIStream` and streams:
   ```python
   @router.post("")
   async def run_agent(run_input, request, accept=Header(None)) -> StreamingResponse:
       agent = request.app.state.agent
       return StreamingResponse(
           AGUIStream(agent).dispatch(run_input, accept=accept),
           media_type=accept or "text/event-stream",
       )
   ```

## Writing a new tool

1. Add a use case in `src/ag2_example/usecases/…`.
2. Register it in [`main/providers/usecases.py`](src/ag2_example/main/providers/usecases.py) (`scope=AG2Scope.REQUEST`).
3. Add a tool function:
   ```python
   @tool
   @inject
   async def my_tool(uc: FromDishka[MyUseCase], arg: str) -> str:
       return await uc.execute(...)
   ```
4. Include it in [`api/agent/agent_factory.py`](src/ag2_example/api/agent/agent_factory.py) (`tools=[...]`).

That's it — no endpoint changes.

## Project layout

```
src/ag2_example/
├── config.py / logging_config.py
├── alembic/                     # Alembic migrations + env
├── domain/entities/             # frozen dataclasses (pure)
├── models/                      # SQLAlchemy imperative mappers + registry
├── gateways/db/note/            # NoteRepository (Protocol) + AlchemyNoteRepository
├── usecases/                    # Request/Response pattern + UnitOfWork
├── api/
│   ├── middlewares/request_id.py
│   ├── schemas/note.py
│   ├── routes/{health,notes,chat}.py
│   └── agent/
│       ├── agent_factory.py     # build_agent(config, container) → Agent
│       ├── prompts.py
│       └── tools/
│           ├── utility.py       # calculator + weather (no DI)
│           └── notes.py         # CRUD tools via FromDishka[UseCase]
└── main/
    ├── entrypoint.py            # create_app(): builds container + agent, wires middleware
    ├── di.py                    # create_container, default_providers()
    ├── middleware.py            # AG2ContainerMiddleware — opens AG2Scope.REQUEST per HTTP request
    └── providers/{settings,database,repositories,usecases,agent}.py
```

## Testing

```bash
docker compose up -d db

uv run pytest                    # unit + integration
uv run pytest tests/unit         # unit-only
uv run pytest tests/integration  # REST CRUD + SSE smoke
```

`tests/integration/test_chat_sse.py::test_chat_sse_streams_run_started_and_finished` is skipped unless `AG2EX__OPENAI_API_KEY` or `OPENAI_API_KEY` is set.

## Local dev without Docker

```bash
uv sync
docker compose up -d db
uv run alembic upgrade head
uv run uvicorn ag2_example.main.entrypoint:app --reload
```

## Architecture invariants

`uv run lint-imports` enforces:

1. **Layer direction** — `main → api → usecases → gateways → models → domain`
2. **Agent framework isolation** — `autogen` imports never leak below `api.agent` / `main.providers.agent`
3. **FastAPI isolation** — `fastapi` / `starlette` stay out of `domain` / `gateways` / `usecases`

## What this example does NOT cover

Auth, OAuth, Redis, Kafka, S3, email, websockets, observability dashboards, rate limiting. The goal is the shortest possible path to **AG2.beta + Dishka + AG-UI** done right.

## License

Apache 2.0
