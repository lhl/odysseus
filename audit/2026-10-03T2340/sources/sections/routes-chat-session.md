# routes: chat and session

## Overview

The core chat and session surface: `routes/chat_routes.py` (`POST /api/chat`, the SSE
`POST /api/chat_stream` with its `/api/chat/resume`, `/api/chat/stop` and
`/api/chat/stream_status` companions, `POST /api/rewrite`, `POST /api/inject_context` and
`GET /api/search`), `routes/session_routes.py` (session create, list, rename, archive,
star, compact, export, delete and bulk delete, the admin `DELETE /api/sessions/all` wipe,
and the AI folder tidy), and `routes/chat_helpers.py`, the shared context builder,
privilege gate and post-response task runner those routes call.

The boundary: the context builder the routes hand off to is `src-chat-session`
(`src/chat_processor.py`, `src/chat_helpers.py`); the agent loop is `src-agent-loop`; the
streaming client and provider fallback are `src-llm-core`; the session cache and message
store are `core-auth-session`; the tables are `core-data-platform`; the middleware that
authenticates the request and stamps `request.state.current_user` is `AuthMiddleware` in
`app.py` (`build-install-deploy`), and the `require_admin` gate one endpoint here uses is
`core-auth-session` (`core/middleware.py:57`); the browser end of the stream is
`static-js-chat`. This section covers whether each endpoint resolves a session against the
authenticated owner before it reads or mutates it, what the stream does on failure and on
disconnect, and what deletion and pruning leave behind — not whether the store or the loop
underneath is correct.

## Coverage

**Read fully:** all three assigned files (5,478 lines): `routes/chat_routes.py` (2,829),
`routes/session_routes.py` (1,386), `routes/chat_helpers.py` (1,263). Line numbers refer to
`2992bf6d368a`.

**Read partially:** the boundary code the findings rest on — `core/session_manager.py` at
`get_session`/`_load_session_from_db` (`:421-524`), `sync_session_metadata` (`:454-498`),
`replace_messages` (`:353-400`), `create_session` (`:541-578`), `delete_session`
(`:587-627`) and `get_sessions_for_user`/`save_sessions` (`:700-710`);
`src/auth_helpers.py` at `get_current_user`/`effective_user` (`:10-36`),
the delegated-credential predicate (`:44-55`) and `require_api_token_scope` /
`require_chat_api_token_scope` (`:60-80`); `src/agent_runs.py` end to end (the
detach/subscribe/evict machinery behind the stream); `src/chat_processor.py` at
`build_context_preface` (`:263-470`); `src/chat_helpers.py` at
`coerce_message_and_session` (`:251-316`); `src/upload_handler.py` at `reserve_upload`
(`:864-965`); `src/session_image_cleanup.py` (`:23-121`); `src/chatgpt_subscription.py` at
`fetch_available_models` (`:90-120`); `src/session_actions.py` at
`is_session_recently_active` (`:42-52`); `src/tool_security.py` at
`owner_is_admin_or_single_user` (`:237-262`); `src/tool_execution.py` at `vet_workspace`
(`:466-491`); `src/llm_core.py` at the `llm_call` definition (`:1969`);
`services/search/core.py:250` and `services/search/content.py:181` (definition lines);
`app.py` at the auth-exempt lists (`:264-296`), the exception handlers (`:617-629`), the
session-router mount (`:683`) and the uvicorn launch (`:1306`); `static/js/sessions.js` at
the incognito cleanup helpers (`:261-267`, `:1083`), the list request (`:1682-1684`) and
session materialization (`:2276-2300`); `tests/test_session_list_owner_scope.py` and
`tests/test_archived_sessions_model_filter.py` (the harnesses the first and third findings
quote).

**Not read:** the middleware itself (`core/middleware.py`); the models and the
session/message tables (`core/database.py`); the agent loop (`src/agent_loop.py`); the LLM
streaming path and provider fallback (`src/llm_core.py` beyond the one definition line);
the compactor and preprocessor (`src/context_compactor.py`, `src/chat_handler.py`); the
research handler; the memory, RAG and search stores behind the context preface; the front
end beyond the cited lines; and the other `routes-*` sections.

**Checks run:** three throwaway probes under `/tmp` (a two-owner incognito-purge probe
built on the `tests/test_session_list_owner_scope.py` harness; a probe that calls the three
handlers with a list/string body; a loop-stall measurement for an inline synchronous
`httpx.get`), a double-`setup_session_routes` closure probe, a `grep` for `to_thread` in
the three files and for the `setup_session_routes` call sites, and the 55 suites matching
`ls tests | grep -iE 'chat|session'` — **1 failed, 289 passed**. The failure is the subject
of the third finding and is reproducible as a pair.

### [SECURITY] The session list deletes every owner's incognito rows, not just the caller's

- **Location:** `routes/session_routes.py:269-277` (with `:250-251`, `:280`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `list_sessions` resolves the caller at `:251` and then purges incognito
  rows without ever using it. The only row the query excludes is the one named in the
  caller's own `active_incognito_id` query parameter:

  ```python
  @router.get("/sessions")
  def list_sessions(request: Request):
      user = effective_user(request)
      active_incognito_id = str(request.query_params.get("active_incognito_id") or "").strip()
      ...
              _ghosts = _purge_db.query(DbSession).filter(
                  DbSession.name.in_(("Nobody", "Incognito")),
                  DbSession.created_at < _cutoff,
              ).all()
              for _g in _ghosts:
                  if active_incognito_id and _g.id == active_incognito_id:
                      continue
                  _purge_db.query(_DbMsg).filter(_DbMsg.session_id == _g.id).delete()
                  _purge_db.delete(_g)
                  if hasattr(session_manager, "delete_session"):
                      try:
                          session_manager.delete_session(_g.id)
  ```

  An incognito session is an ordinary owned row: the browser creates one through
  `POST /api/session` with the name `Nobody` (`static/js/sessions.js:2284`), and that route
  stamps `owner=user` from `effective_user(request)` (`routes/session_routes.py:468`). The
  front end sends `active_incognito_id` only for the session it is currently in
  (`static/js/sessions.js:1682-1684`), so the exemption protects the caller and nobody
  else.

  Measured with the two-owner harness from `tests/test_session_list_owner_scope.py`
  (temporary SQLite database, both rows named `Nobody`, both older than the 10-minute
  cutoff, caller = alice):

  ```
  $ ODYSSEUS_DATA_DIR=/tmp/odysseus_probe_data venv/bin/python /tmp/probe_incognito_purge.py
  caller                : alice (cookie user)
  alice incognito row   : DELETED
  bob incognito row     : DELETED
  bob incognito message : DELETED
  session_manager.delete_session calls: 2
  ```

  The `delete_session` call widens the damage: it unlinks the session's generated image
  files and detaches its documents (`core/session_manager.py:591-600`, reached through
  `src/session_image_cleanup.py:84-121`), and it drops the in-memory copy from the shared
  session cache. No test pins this behaviour: `grep -rn 'Nobody\|Incognito' tests/*.py`
  exits 1 with no output.
- **Impact:** on any instance with more than one account, one user's sidebar load destroys
  another user's incognito chat. Bob's row and messages are gone and the cached session
  object is gone, so his next message is refused by `_verify_session_owner`
  (`routes/session_routes.py:104-131`) with a 404 even though his transcript is still
  sitting in the process-local `_INCOGNITO_CONTEXTS` map (`routes/chat_helpers.py:60-100`)
  that only that session id can reach. Any chat-scoped bearer token reaches the same
  endpoint through the router dependency. The victim has to have been in the incognito
  session for more than ten minutes (`created_at < utcnow - 10min`), which is the ordinary
  case for a conversation worth having; a shorter session is spared.
- **Fix:** filter the purge by the caller — `DbSession.owner == user`, with the
  null-owner branch when `user` is None — and keep the `active_incognito_id` exemption for
  the caller's own live session.

### [PERF] The chat path runs synchronous LLM, web-search and URL-fetch calls on the event loop

- **Location:** `routes/chat_helpers.py:737` (with `routes/chat_routes.py:607`, `:799`, `:1258`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `build_chat_context` is an `async def` and calls the context builder
  inline, with no thread:

  ```python
  preface, rag_sources, web_sources = chat_processor.build_context_preface(**_preface_kwargs)
  ```

  `build_context_preface` is a plain `def` (`src/chat_processor.py:263`) and makes three
  blocking network calls inside it:

  ```python
  generated_query = llm_call(                              # :404, timeout=15
  ...
  web_context, web_sources = comprehensive_web_search(     # :446
  ...
  result = fetch_webpage_content(url)                      # :466, timeout=5
  ```

  All three are synchronous clients — `src/llm_core.py:1969`,
  `services/search/core.py:250`, `services/search/content.py:181`. The callers are
  `async def chat_endpoint` (`routes/chat_routes.py:772`) and `async def chat_stream`
  (`:963`), which run on the single uvicorn worker the app starts
  (`app.py:1306`: `uvicorn.run(app, host=bind_host, port=bind_port, log_level="info")`,
  no `workers=`).

  The URL loop fires for any message that carries a non-YouTube URL (message under 2000
  characters, at most three URLs), so pasting a link into the composer is enough;
  `use_web=true` adds the query-generation `llm_call` and the search. Measured stall for
  the same call shape (a synchronous `httpx.get` against a local server that sleeps 1.0s,
  with a ticker task on the loop):

  ```
  $ venv/bin/python /tmp/probe_blocking_fetch.py
  inline (no thread)   elapsed=1.02s  ticker iterations=48
  asyncio.to_thread    elapsed=1.01s  ticker iterations=995
  ```

  A second site in the same route does it again: `_recover_empty_session_model` calls
  `fetch_available_models(api_key)` at `routes/chat_routes.py:607`, which is
  `httpx.get("https://chatgpt.com/...", timeout=10.0)` (`src/chatgpt_subscription.py:90-98`),
  and it is called inline from both async handlers (`:799`, `:1258`). Sibling modules in
  this repository offload the same shape — `routes/auth_routes.py:140`, `:160`, `:171`,
  `:181`, `routes/email_routes.py:2391`, `:2466` — and none of the three files in this
  section does: `grep -n 'to_thread\|run_in_executor' routes/chat_routes.py
  routes/session_routes.py routes/chat_helpers.py` returns nothing.
- **Impact:** during a link-prefetch or web-search turn the loop cannot schedule anything
  else: other users' SSE heartbeats stall, `/api/health` and `/api/ready` stop answering,
  and a second chat turn waits behind the first. The stall lasts as long as the blocking
  calls take — up to 15s for the query LLM plus the search and up to 5s per URL fetch, or
  up to 10s for the ChatGPT-subscription catalog fetch. Nothing in the section's suites
  covers the blocking shape.
- **Fix:** `await asyncio.to_thread(chat_processor.build_context_preface, **_preface_kwargs)`,
  and wrap the `fetch_available_models` call the same way. The cleaner version moves the
  synchronous I/O inside `src/chat_processor.py` onto awaitable helpers, but the two call
  sites are enough to stop the stall.

### [BUG] `setup_session_routes` appends to a module-level router, so a second call's handlers never serve

- **Location:** `routes/session_routes.py:134` (with `:237`, `:250`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the router is built at import and every call to the factory decorates that
  same object and returns it:

  ```python
  router = APIRouter(                                     # :134
      prefix="/api",
      tags=["sessions"],
      dependencies=[Depends(require_chat_api_token_scope)],
  )
  ...
  def setup_session_routes(                               # :237
      session_manager: SessionManager,
      config: dict,
      ...
      @router.get("/sessions")                            # :250
      def list_sessions(request: Request):
  ```

  Each call therefore registers a second full copy of the handler set, each closing over
  the `session_manager` and `config` of that call. Starlette matches in registration
  order, so the first call's closures are the ones that serve. Measured by calling the
  factory twice with distinguishable `MagicMock` managers:

  ```
  $ venv/bin/python - <<'PY'
  returned router is the module-level object: True True
  distinct session_manager closures on /api/sessions: 2
  first handler closes over the FIRST manager: True
  second handler closes over the SECOND manager: True
  ```

  The sibling factory builds its router inside the function
  (`routes/chat_routes.py:763`), which is why the same double-call there is harmless.

  The repository's own suite already fails on this. Four test modules call
  `setup_session_routes`; `tests/test_archived_sessions_model_filter.py` runs first
  alphabetically, registers its `MagicMock()` manager, and
  `tests/test_session_list_owner_scope.py` then picks
  `next(r.endpoint for r in router.routes ...)`, which is the earlier file's handler:

  ```
  $ venv/bin/python -m pytest -q tests/test_archived_sessions_model_filter.py tests/test_session_list_owner_scope.py
  1 failed, 4 passed
  $ venv/bin/python -m pytest -q tests/test_session_list_owner_scope.py
  2 passed
  ```

  Production has one call site (`app.py:683`), so no request is served by a stale handler
  today.
- **Impact:** the factory's contract is not what it appears to be: the router returned by
  the second call does not use the manager it was given, and its routes are unreachable.
  Today that costs one red test in the section's own suite and depends on test file order
  to appear; the next caller that builds a session router — a second entry point, an
  embedded mode, another test — gets a silently misconfigured one.
- **Fix:** move `router = APIRouter(...)` inside `setup_session_routes` and return it, as
  `routes/chat_routes.py` does, or raise when the factory is called twice.

### [ERROR-HANDLING] Three chat and session endpoints raise an unhandled `AttributeError` on a non-object JSON body

- **Location:** `routes/chat_routes.py:989` (`chat_stream`), `:2731` (`rewrite_message`),
  `routes/session_routes.py:582` (`inject_messages`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** each handler reads the body and calls `.get` on whatever came back:

  ```python
  body = await request.json()                             # chat_routes.py:969
  ...
  selected_endpoint_id = str(
      form_data.get("selected_endpoint_id")
      or (body or {}).get("selected_endpoint_id")         # :989
      or ""
  ).strip()
  ```
  ```python
  body = await request.json()                             # chat_routes.py:2727
  ...
  session_id = body.get("session_id")                     # :2731
  ```
  ```python
  body = await request.json()                             # session_routes.py:581
  messages = body.get("messages", [])                     # :582
  ```

  Measured by calling the three handlers with a request whose `json()` returns the
  payload, the harness style of `tests/test_integrations_store_shape.py`:

  ```
  $ venv/bin/python /tmp/probe_nondict_bodies.py
  POST /api/chat_stream  body=[1,2]  : AttributeError: 'list' object has no attribute 'get'  (raised at chat_routes.py:989)
  POST /api/chat_stream  body=[]     : HTTPException: 400: {'error': 'REQUEST_PROCESSING_ERROR', ...}  (raised at chat_routes.py:1153)
  POST /api/chat_stream  body="x"    : AttributeError: 'str' object has no attribute 'get'  (raised at chat_routes.py:989)
  POST /api/rewrite      body=[]     : AttributeError: 'list' object has no attribute 'get'  (raised at chat_routes.py:2731)
  POST /api/rewrite      body=[1,2]  : AttributeError: 'list' object has no attribute 'get'  (raised at chat_routes.py:2731)
  POST /api/session/x/inject_messages body=[]: AttributeError: 'list' object has no attribute 'get'  (raised at session_routes.py:582)
  POST /api/session/x/inject_messages body="x": AttributeError: 'str' object has no attribute 'get'  (raised at session_routes.py:582)
  ```

  `app.py` registers handlers for `SessionNotFoundError`, `InvalidFileUploadError`,
  `LLMServiceError` and `WebSearchError` (`app.py:617-629`) and none for a generic
  exception, so the `AttributeError` reaches the client as a 500. This is a recurrence of
  the class reported for three admin endpoints in `routes-rest-auth-admin.md`
  (`routes/auth_routes.py:329`, `:784`, `:794`). Two siblings in these files already keep
  the contract: `bulk_delete_sessions` wraps its parse in `try/except`
  (`routes/session_routes.py:619-622`), and `chat_stream`'s own JSON parse answers 400
  (`routes/chat_routes.py:966-975`).
- **Impact:** an API client that sends a JSON array or string to one of these endpoints
  gets a 500 and an unhandled traceback where the rest of the surface answers 400;
  `POST /api/rewrite` is the worst of the three, because an empty array is enough. The
  shipped UI always sends an object, so the cost is a confusing failure and a log line.
- **Fix:** add the `isinstance(body, dict)` guard used by `routes/backup_routes.py:73` to
  the three handlers after each `await request.json()`.
