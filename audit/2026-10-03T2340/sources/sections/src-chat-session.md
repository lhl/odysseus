# src: chat processing, context and sessions

## Overview

The non-route half of the chat pipeline. `src/chat_handler.py` preprocesses a turn (uploads,
YouTube transcripts, image/vision handling), `src/chat_processor.py` assembles the memory, RAG,
web and skills context preface, `src/context_compactor.py` decides what survives when the
conversation approaches the model's window and `src/context_budget.py` computes the agent's
input budget, `src/request_models.py` holds the pydantic bodies, `src/session_search.py` and
`src/topic_analyzer.py` read transcripts across sessions, `src/session_actions.py` and
`src/session_image_cleanup.py` tidy and delete session data, `src/chat_helpers.py` is the
URL/validation helper set, and `src/assistant_log.py` is the activity-log shim.

This section covers what these modules do to a conversation once a route hands it over: what
compaction keeps, what they read or delete and on whose behalf, and what runs on the event loop. It
does not cover whether the routes, the store or the transport are themselves correct. Each
neighbour owns one piece:

| Owner | What it owns |
| --- | --- |
| `routes-chat-session` | The routes that call these modules: `routes/chat_routes.py`, `routes/session_routes.py`, `routes/chat_helpers.py` |
| `core-auth-session` | The session store, its cache and the message writes (`core/session_manager.py`, `core/models.py`). Its findings (the global 100-row sidebar cache, the no-op `save_sessions`) are relied on here, not restated. |
| `core-auth-session`, `build-install-deploy` | The middleware that stamps the caller |
| `src-llm-core` | The LLM transport and model-window lookup: `src/llm_core.py`, `src/model_context.py`, `src/endpoint_resolver.py` |
| `src-documents` | The upload resolver |
| `src-tools-parse-exec` | The tool dispatcher that calls `search_chats` |
| `src-research-scheduling`, `src-tools-builtin-actions` | The scheduler that fires the tidy action |

## Coverage

**Read fully:** all 11 assigned files (2,840 lines).

| File | Lines |
| --- | ---: |
| `src/context_compactor.py` | 527 |
| `src/chat_processor.py` | 525 |
| `src/session_search.py` | 369 |
| `src/chat_handler.py` | 352 |
| `src/chat_helpers.py` | 316 |
| `src/session_actions.py` | 250 |
| `src/request_models.py` | 137 |
| `src/session_image_cleanup.py` | 130 |
| `src/topic_analyzer.py` | 104 |
| `src/context_budget.py` | 82 |
| `src/assistant_log.py` | 48 |

Line numbers refer to `2992bf6d368a`.

**Read partially:** the boundary code the findings rest on:

- `core/session_manager.py` at `get_session` / `sync_session_metadata` / `_touch_session`
  (`:421-539`), `_persist_message` (`:244-255`), `replace_messages` (`:352-412`) and
  `delete_session` (`:587-627`)
- `core/models.py` in full (191 lines — `ChatMessage`, `Session`, `get_context_messages`)
- `routes/chat_helpers.py` at `build_chat_context` (`:588-830`), `preprocess` (`:328-350`) and
  `add_user_message` (`:409-418`)
- `routes/chat_routes.py` at the chat-endpoint context build (`:780-870`) and `GET /api/search`
  (`:2696-2717`)
- `routes/session_routes.py` at `_verify_session_owner` (`:104-131`) and the auto-sort route's Phase
  1 (`:1120-1145`)
- `src/agent_loop.py` at the compaction call sites (`:4276-4300`, `:4827-4840`) and the `_protected`
  context messages (`:2430-2455`, `:2515-2530`)
- `src/llm_core.py` at `_sanitize_llm_messages` (`:1673-1740`) and the response parse in both call
  paths (`:2061`, `:2436-2465`)
- `src/document_processor.py` at `analyze_image_with_vl_result` (`:333-393`)
- `src/task_scheduler.py` at `_execute_action` (`:1242-1275`), `HOUSEKEEPING_DEFAULTS` (`:251-263`)
  and `ensure_defaults` (`:2313-2340`)
- `src/builtin_actions.py` at `action_tidy_sessions` (`:433-446`)
- `routes/task/task_routes.py` at `_owner` and the create handler (`:301-302`, `:453`, `:528-545`)
- `src/prompt_security.py` at `untrusted_context_message` (`:64-96`)
- `src/tool_execution.py:1151`
- `app.py` at the assistant-log wiring (`:589-590`), the housekeeping seeding (`:1155-1177`) and the
  uvicorn launch (`:1306`)

**Not read:**

- the rest of `routes/chat_routes.py` and `routes/session_routes.py` (assigned to
  `routes-chat-session`)
- `core/middleware.py` and the auth middleware in `app.py` (assigned to `core-auth-session` /
  `build-install-deploy`) — the findings here rest on the `effective_user` / `_verify_session_owner`
  call sites quoted, not on the middleware
- the LLM transport beyond the cited lines (`src/model_context.py`, `src/endpoint_resolver.py`)
- `src/upload_handler.py` and the document pipeline behind `build_user_content` (assigned to
  `src-documents`)
- the tool dispatcher beyond the one `do_search_chats` call site
- the front end
- every other `src-*` module

**Checks run:**

- five throwaway probes under `/tmp` (not part of the target tree), each quoted in the finding it
  settles — `maybe_compact` with a realistic preface and an 11-message history
- the same call with the summary model returning `""`
- a 1.0 s blocking VL call against a ticker task on the same loop
- `search_session_messages` against a 2,000-message in-memory DB with a statement-counting event
  listener, plus `EXPLAIN QUERY PLAN` for its LIKE leg
- `run_auto_sort("")` against a temp app DB holding one empty session for each of two owners
- greps for the unused symbols cited in the dead-code finding
- greps for the callers of `run_auto_sort`, `search_session_messages`, `maybe_compact` and
  `model_supports_vision`, and of `_sanitize_tool_messages`
- the suites matching `ls tests | grep -iE 'chat|session|context|topic|compactor|request_models|assistant_log'`,
  which yields 64 files
- running them gives **1 failed, 523 passed**

The failure is the order-dependent pair already documented in `routes-chat-session`
(`tests/test_session_list_owner_scope.py` passes alone — 2 passed; with
`tests/test_archived_sessions_model_filter.py` ahead of it, 1 failed / 4 passed). The compactor's
own suites outside that glob (`tests/test_compaction_summary_failure.py`,
`tests/test_context_compactor.py`, `tests/test_context_compactor_nonstring.py`,
`tests/test_context_budget.py`) are **41 passed**, and the neighbouring budget suites (the 6 test
files listed below) are **25 passed**.

- `tests/test_compact_truncate_tool_call_args.py`
- `tests/test_agent_tool_budget_nonnumeric.py`
- `tests/test_budget_auto_sentinel.py`
- `tests/test_manage_settings_token_budget.py`
- `tests/test_history_compact_tool_calls.py`
- `tests/test_document_processor_attachment_budget.py`

### [BUG] Compaction rewrites the wrong slice of the session history, dropping messages it never summarized

- **Location:** `src/context_compactor.py:504-518` (with `:362`, `:432`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `maybe_compact` splits the system-stripped conversation at its midpoint and
  hands `_update_session_history` that index together with the request's system-message count:

  ```python
  split_point = len(convo_msgs) // 2                          # :362
  ...
  if persist:
      _update_session_history(session, split_point, summary, system_msg_count=len(system_msgs))  # :432
  ```

  `system_msgs` is counted over the request's message list, which starts with the preface
  `build_context_preface` builds: the untrusted-context policy message is appended
  unconditionally (`src/chat_processor.py:305-308`) and memory/RAG/web/URL/skills context add
  more. None of those are in `session.history` — the chat path only ever appends the user turn
  (`routes/chat_helpers.py:416`) and the model's reply — yet `_update_session_history` uses the
  count as an offset into it:

  ```python
  effective_split = system_msg_count + split_point            # :504
  system_prefix = list(session.history[:system_msg_count])    # :510
  recent_history = session.history[effective_split:]          # :511
  new_history = system_prefix + [summary_msg] + recent_history
  ```

  Measured with a throwaway probe (`venv/bin/python /tmp/probe_compaction_slice_p1.py`: one
  preface system message — the minimum — an 11-message history and a stubbed summary call):

  ```
  was_compacted : True
  history before: ['m0-…', 'm1-…', 'm2-…', 'm3-…', 'm4-…', 'm5-…', 'm6-…', 'm7-…', 'm8-…', 'm9-…', 'm10-curr']
  history after : ['m0-…', '[Convers…', 'm7-…', 'm8-…', 'm9-…', 'm10-curr']
  summarized    : m0..m5  (convo_msgs[:split_point])
  turns dropped from session.history     : ['m1-…', 'm2-…', 'm3-…', 'm4-…', 'm5-…', 'm6-…']
  ```

  `m1..m5` were summarized; `m6` was not — it survives only in the request built for this turn,
  and `replace_messages` deletes and re-inserts the stored rows
  (`core/session_manager.py:380-400`), so it is gone from the transcript. `m0` is kept verbatim
  *and* summarized, so it is duplicated. The same probe with three preface system messages drops
  `m3..m8`; the number of never-summarized turns lost equals the number of system messages in
  the preface. The agent path passes `session=None` and applies the plan later through
  `apply_compaction_state_for_session` (`:472-487`), which calls the same function with the same
  offset.
- **Impact:** every compaction permanently drops as many turns from the stored transcript as the
  request had system messages (one at minimum, two to four in the ordinary case) and keeps the
  oldest few twice. The user reloading the chat sees messages missing from the middle of the
  conversation, and the model on the next turn never received a summary covering them. Nothing
  logs the dropped range and `was_compacted=True` is reported, so the loss is silent.
  `tests/test_context_compactor.py` cannot catch it: it stubs `_update_session_history` out.
- **Fix:** compute the offset from the list being rewritten, not from the request — the number
  of leading `system` entries of `session.history`, or have `maybe_compact` return the count of
  history messages it summarized and slice `session.history` by that. A test that builds a real
  `Session`, calls `maybe_compact` with a preface, and asserts that the messages it summarized
  are the messages that left the history would pin it.

### [ERROR-HANDLING] An empty compaction summary is accepted, replacing the older half with a bare header

- **Location:** `src/context_compactor.py:410-432`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `llm_call_async` returns the completion text and does not raise for a 200 with
  empty content — `response = content or msg.get("reasoning_content") or ""`
  (`src/llm_core.py:2461`; the sync path has the same line at `:2061`) — and it caches that empty
  string (`_set_cached_response`, `:2462-2466`). `maybe_compact` only strips a leading title
  before using it:

  ```python
  summary = normalize_compaction_summary(summary)      # :410
  summary_msg = {
      "role": "system",
      "content": f"[Conversation summary — earlier messages were compacted]\n{summary}",   # :412-415
  }
  ```

  Measured with the summary call returning `""` (`venv/bin/python /tmp/probe_empty_summary.py`,
  the shape of `tests/test_compaction_summary_failure.py` with an empty return instead of a
  raise):

  ```
  was_compacted: True
  history before: ['m0-…', 'm1-…', …, 'm10-curr']
  history after : ['m0-…', '[Conversation summary]\n', 'm7-…', 'm8-…', 'm9-…', 'm10-curr']
  summary message content: '[Conversation summary]\n'
  ```

  The older half is gone and its replacement is a header with nothing under it. The `except`
  branch twenty lines above states the contract this breaks — "Degrade gracefully: keep the
  conversation intact rather than silently dropping the older half" (`:406-407`) — and the suite
  that pins that branch only exercises a summary call that raises.
- **Impact:** a compaction/utility model that returns an empty completion (a truncated
  reasoning-model reply, an empty `choices[0].message.content`, a proxy that sends
  `content: null`) silently destroys the older half of the conversation while reporting success.
  Because the empty response is cached under the request's cache key, a retry of the same
  compaction returns the empty string again.
- **Fix:** treat an empty summary as a failure before any rewrite —
  `if not summary.strip(): return messages, context_length, False` — so the caller keeps the
  conversation and `trim_for_context` handles the length, as the raising path already does.

### [PERF] `preprocess_message` runs the vision-model call inline on the event loop while offloading the vision probe beside it

- **Location:** `src/chat_handler.py:264` (with `:209`, `:217`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the async preprocessor offloads the LM Studio capability probe and then calls
  the vision description synchronously:

  ```python
  main_is_vision = await asyncio.to_thread(                    # :209
      model_supports_vision,
      sess.model or "",
      getattr(sess, "endpoint_url", "") or "",
  )
  ...
  if not vl_desc:
      vl_result = analyze_image_with_vl_result(file_info["path"], owner=owner)   # :264
  ```

  `analyze_image_with_vl_result` is a plain `def` (`src/document_processor.py:333`) that runs a
  synchronous `llm_call(..., timeout=120)` per candidate endpoint (`:375`), and its caller is
  awaited directly: `routes/chat_helpers.py:336` awaits `chat_handler.preprocess_message`, from
  `build_chat_context` (`:643`), which the async chat handlers await. Measured with the VL call
  replaced by a 1.0 s blocking sleep and a ticker task on the same loop
  (`venv/bin/python /tmp/probe_vl_blocking.py`):

  ```
  inline analyze_image_with_vl_result          elapsed=1.00s  ticker iterations=1
  VL call actually made: ['/tmp/photo.png']
  baseline: same 1.0s via asyncio.to_thread    elapsed=1.00s  ticker iterations=99
  ```

  The loop is held for the whole call, and the call sits inside the per-attachment loop
  (`:217-282`), so a turn with several images pays it once per image. The same path also writes
  the description to the gallery with a synchronous DB round-trip
  (`_sync_upload_vision_to_gallery`, `:32-59`).
- **Impact:** attaching an image to a turn whose main model is text-only freezes the process for
  the duration of the VL call — up to the 120 s timeout when the vision endpoint is cold or
  slow — on the single uvicorn worker the app starts (`app.py:1306`). During that window no
  other session's stream advances and `/api/health` does not answer. `routes-chat-session`
  reports the same class for `build_context_preface` and the ChatGPT catalog fetch; this is a
  third site, in a different file, with the largest timeout of the three.
- **Fix:** `vl_result = await asyncio.to_thread(analyze_image_with_vl_result, file_info["path"],
  owner=owner)`, and offload the gallery sync the same way.

### [PERF] Every transcript search runs both search legs and builds context for candidate hits it then discards

- **Location:** `src/session_search.py:336-355` (with `:171`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** when the FTS leg returns anything, the LIKE leg runs anyway, and each leg
  materializes full results — including two context queries per hit — before the merge truncates
  to `limit`:

  ```python
  if fts_results is not None:
      like_results = _search_like(                     # :337
          db, query, limit, owner, include_archived, context_messages,
          restrict_owner, include_legacy_owner,
      )
      merged: list[SessionSearchResult] = []
      seen: set[str] = set()
      for result in [*fts_results, *like_results]:     # :349
          ...
          if len(merged) >= limit:
              break
  ```

  `_rows_to_results` runs `_context_for_message(db, msg, context_messages)` for every hit
  (`:171`), which issues one query for the messages before the hit and one for the messages
  after it (`:143-165`). Measured with a statement-counting event listener on an in-memory DB
  holding 2,000 messages across five sessions (`venv/bin/python
  /tmp/probe_session_search_queries.py`):

  ```
  messages in db            : 2000
  results returned          : 20
  SQL statements for 1 call : 84
  elapsed                   : 25 ms
  statement mix             : {'SELECT 1': 1, 'SELECT m.id': 1, 'SELECT chat_messages.id': 82}
  ```

  82 of the 84 statements are context queries for 41 candidate hits (21 from the FTS leg, 20
  from the LIKE leg) of which 20 are returned. The LIKE leg cannot use an index for a
  leading-wildcard match — `EXPLAIN QUERY PLAN` for that query (`/tmp/probe_like_plan.py`) is
  `SEARCH sessions USING INDEX ix_sessions_owner (owner=?)` then `SEARCH chat_messages USING
  INDEX ix_messages_session_time (session_id=?)`, i.e. a `lower(content) LIKE lower('%q%')`
  comparison on every message of each of the caller's non-archived sessions. Both callers run it
  inline: the async `GET /api/search` (`routes/chat_routes.py:2707`) and the agent's
  `search_chats` tool (`src/tool_execution.py:1151`).
- **Impact:** each search costs roughly four times the statements it needs and a per-message scan
  of the caller's transcripts, on the event loop of a single-worker process, for results that are
  then dropped. At the measured 2,000-message scale the whole call is 25 ms; the scan grows with
  the transcript while the discarded queries do not shrink.
- **Fix:** run the LIKE leg only when the FTS leg returned fewer than `limit` rows, and fetch
  context after the merge for the returned page only (or batch the before/after queries per
  session).

### [BUG] The tidy action deletes session rows behind the session manager's back, so a chat that is still open loses its next turn

- **Location:** `src/session_actions.py:89-91` and `:136-140`
- **Severity:** low
- **Disposition:** next
- **Evidence:** both delete branches call `db.delete(row)` and commit without going through
  `SessionManager.delete_session`:

  ```python
  if (row.name or "").strip() == "Incognito":
      deleted_throwaway += 1
      db.delete(row)                 # :91 — no age check at all
      continue
  ...
  if should_delete:
      db.delete(row)                 # :137
  ...
  if deleted_empty or deleted_throwaway:
      db.commit()                    # :140
  ```

  The in-memory session survives, so the next turn is still accepted —
  `_verify_session_owner` allows an in-memory ghost the caller owns
  (`routes/session_routes.py:125-129`) — but the write is dropped:

  ```python
  if db_session is None:
      # A stream/tool callback can outlive a session delete. ...
      self.sessions.pop(session_id, None)
      logger.warning("Dropping message for deleted session %s", session_id)
      return
  ```
  (`core/session_manager.py:249-255`)

  The path is reachable from the shipped housekeeping task: `tidy_sessions` is seeded for every
  owner and is not ship-paused (`src/task_scheduler.py:252`, `ensure_defaults`), fires every
  five `session_created` events, and calls
  `run_auto_sort(owner, skip_llm=True, delete_throwaway=False)` (`src/builtin_actions.py:441`).
  An empty session is deleted once it is ten minutes old and no timestamp is newer
  (`_FRESH_EMPTY_SESSION_GRACE`, `:25`; `is_session_recently_active`, `:42-52`), so an open but
  idle empty chat is eligible. The sibling implementation in the route does what this one
  omits — after the same `db.delete(row)` it calls `session_manager.delete_session(row.id)`
  (`routes/session_routes.py:1136-1141`).
- **Impact:** a chat left open and idle for ten minutes loses the next exchange: the reply
  streams, nothing is written to the transcript, and the turn after that answers 404 because the
  cache entry was evicted on the dropped write. The direct delete also skips the generated-image
  cleanup and document detach that `delete_session` performs
  (`core/session_manager.py:591-600`), so a deleted throwaway chat's images stay active in the
  gallery. An `Incognito`-named row is deleted with no age check (the shipped browser names its
  incognito session `Nobody`, `static/js/sessions.js:2284`, which this branch does not match).
- **Fix:** route both branches through the manager when one is available
  (`manager.delete_session(row.id)`), keeping the direct delete as the fallback, so the cache
  entry, the linked images and the documents follow the same path as `DELETE /api/session/{id}`.

### [FOOTGUN] `run_auto_sort` treats a missing owner as "every owner"

- **Location:** `src/session_actions.py:78-81` (with `:145-148`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** an empty or `None` owner removes the filter instead of matching nothing, in both
  the delete pass and the folder-assignment pass:

  ```python
  rows = db.query(DbSession).filter(
      DbSession.archived == False,
      *([DbSession.owner == owner] if owner else []),
  ).all()
  ```

  The one production caller forwards a column that is nullable and empty in the documented
  no-login mode: `action_tidy_sessions(owner, ...)` (`src/builtin_actions.py:433`) is invoked
  with `kwargs = {"owner": task.owner, ...}` (`src/task_scheduler.py:1256`),
  `ScheduledTask.owner` is `Column(String, nullable=True)` (`core/database.py:735`), and the
  create route fills it from `get_current_user`, which is `None` when auth is disabled
  (`routes/task/task_routes.py:301-302`, `:530`). Measured against a temp app DB holding one
  90-day-old empty session for each of two owners
  (`venv/bin/python /tmp/probe_auto_sort_owner.py`):

  ```
  sessions before: ['alice', 'bob']
  run_auto_sort('') -> Cleaned 2 sessions. Too few remaining to sort.
  sessions after : []
  ```

  The docstring says the opposite of what the code does with an empty owner — "owner: user whose
  sessions to process" (`:60`) — and this is a delete path. No current caller passes an empty
  owner in the shipped configuration (`ensure_defaults` is called per username), so today the
  unfiltered branch is reached only when a task row has a null owner.
- **Impact:** none today in a correctly seeded instance. The next caller that forgets the owner,
  or a task row created in the no-login mode described above, turns this into a cross-owner
  delete and folder rewrite over every account's sessions — including the `is_important` guard
  and the per-owner grace that the filtered path applies to one user's rows.
- **Fix:** fail closed — `if not owner: return "No owner; nothing to clean."` before the query,
  and keep the filter unconditional so an empty owner matches no rows.

### [DEAD-CODE] The section's files carry public API nothing calls, including a whole shim module

- **Location:** `src/assistant_log.py:19-48` (with `src/chat_handler.py:115`, `:326`,
  `src/chat_helpers.py:188`, `src/request_models.py:30`, `:51`, `:107`, `:113`, `:131`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** greps over `src/ routes/ core/ services/ app.py` (tests excluded) return only the
  definitions:

  ```
  $ grep -rn "\btrim_history_if_needed\b" --include=*.py src/ routes/ core/ services/ app.py
  src/chat_handler.py:326:    def trim_history_if_needed(self, session):
  $ grep -rn "\b_LEGACY_TAG_RE\b" ...        → src/assistant_log.py:31:_LEGACY_TAG_RE = re.compile(...)
  $ grep -rn "\bSessionCreateRequest\b" ...  → src/request_models.py:30:class SessionCreateRequest(BaseModel):
  $ grep -rn "\bvalidate_file_upload\b" ...  → src/chat_helpers.py:188:def validate_file_upload(file: UploadFile) -> UploadFile:
  ```

  and the same for `enhance_message_if_needed` (`src/chat_handler.py:115`) and for four model classes:
  `MemoryUpdateRequest`, `ErrorResponse`, `UploadResponse` and `MemoryResponse`.
  `MAX_CONTEXT_MESSAGES` (`src/constants.py:87`) is read only by the dead
  `trim_history_if_needed`. In `src/assistant_log.py`:

  - the module global is assigned by `set_session_manager` (`:19-24`, called from
    `app.py:589-590`) and never read
  - the `_LEGACY_TAG_RE` regex has no reader
  - `log_to_assistant` logs at DEBUG and returns (`:47-48`), while four production call sites still
    call it: `src/task_scheduler.py:1236`, `src/tools/vault.py:126` and
    `routes/cookbook_routes.py` at `:1395` and `:2820`

  The no-op is deliberate per its docstring, but the callers read as if the assistant's activity
  feed receives the text.
- **Impact:** a reader or a new caller can pick up `trim_history_if_needed` (which slices
  `session.history` without the tool-pairing repair `_sanitize_tool_messages` performs for
  `trim_for_context`), `validate_file_upload`, or a request model no route validates against, and
  get behaviour the app never exercised. The assistant-log shim makes four call sites look like
  they notify the user when the text reaches only the debug log.
- **Fix:** delete the unused symbols and the shim module together with its `app.py` wiring and
  the four call sites, or mark them deprecated in place. `trim_history_if_needed` should not be
  re-wired as written — `trim_for_context` is the live path.
