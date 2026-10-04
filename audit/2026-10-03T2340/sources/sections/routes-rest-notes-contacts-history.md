# routes: notes, contacts and history

## Overview

Files in this section:

- `routes/note/__init__.py`
- `routes/note/note_routes.py`
- `routes/note_routes.py`
- `routes/contacts/__init__.py`
- `routes/contacts/contacts_routes.py`
- `routes/contacts_routes.py`
- `routes/history/__init__.py`
- `routes/history/history_routes.py`
- `routes/history_routes.py`

Notes with reminders and due dates, contacts with CardDAV and vCard/CSV import, and
chat history with display pagination, topics and compaction. Notes and history are
per-owner; contacts are a shared, admin-only address book, with one local JSON file,
CardDAV configuration and cache. There is no history-search or topic-id endpoint in
these files. The ownership model is `core-auth-session`'s; the database schema is
`core-data-platform`'s; the notes reminder scheduler is `src-research-scheduling`'s.
The earlier-registered session router and its live compaction endpoint belong to
`routes-chat-session`.

## Coverage

**Read fully:** all nine assigned files (2,765 lines).

| File | Lines |
| --- | ---: |
| `routes/note/note_routes.py` | 937 |
| `routes/contacts/contacts_routes.py` | 916 |
| `routes/history/history_routes.py` | 849 |

The three flat shims (18, 13 and 17 respectively), and each package's `__init__.py` (5 each).
Boundary files read fully: `src/auth_helpers.py`, `src/topic_analyzer.py`, `src/url_safety.py`,
`core/middleware.py` and `core/atomic_io.py`. Read the audit prompt, header, coverage boundaries,
review scaffold and both requested model sections. Citations refer to working-tree source at
`2992bf6d368a`; `git status --short` showed only the untracked `audit/` directory.

**Read partially:**

- `app.py` at authentication and request identity assignment (lines 259–499) and the
  session/history/note/contacts router registrations
- `routes/session_routes.py` at owner verification, the active-run guard, adjacent helpers and the
  live compaction handler (98–287, 1004–1103), plus searches for search/compaction definitions.
  `core/database.py` at the session factory and Session, ChatMessage and Note models (factory
  search, 175–274, 1808–1855)
- `core/session_manager.py` at message persistence/truncation (225–353), hydration (421–555), and
  owner filtering/no-op save (700–714)

The contacts JSON store and its writes were read fully as part of the canonical route module. Test
source read: `tests/conftest.py`, `tests/test_contacts_carddav_security.py`,
`tests/test_contacts_import_nonstring.py`, `tests/test_contacts_vcard_parse.py` (end to end), and
`tests/test_history_compact_tool_calls.py` (1–250).

**Not read:** no assigned file remains unread. Boundary code beyond those regions,
including the full session manager, full database initialization/migrations, upload
reservation implementation, settings/integration/SMTP stores, reminder scheduler,
LLM transport and front end, was not reviewed. Other discovered tests were executed,
not read. Full-text history search outside these files was not reviewed. No live
CardDAV/SMTP/LLM service, DNS-rebinding exploit, browser flow, deployment or load test
was exercised; URL guards and HTTP call placement were inspected, and the CardDAV
probe used a stub transport. No run-level audit gate was run, as instructed.

**Checks run:** `git rev-parse --short=12 HEAD`, `git status --short`, file line
counts, the requested `ls tests | grep -iE 'note|contact|history'`, and targeted
searches for router registrations, body readers, stores and compaction handlers.
An inline `venv/bin/python` probe (in-memory SQLite, temporary data directory,
bytecode disabled) confirmed all three shim identities, vCard address loss,
CardDAV GET executing on the event-loop thread, and the nine JSON-body failures
below. A second inline probe registered session then history routers as `app.py`
does and replaced the session router's owner check with an HTTP 418 sentinel:
POST `/api/session/example/compact` returned that sentinel, confirming the history
module's compaction implementation is not selected in the shipped registration
order. An initial attempt to inspect `app.routes` directly returned no matches;
the request-level probe, not that inconclusive inspection, established precedence.

The focused command was:

```sh
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q -p no:cacheprovider \
  $(ls tests | grep -iE 'note|contact|history' | grep '\.py$' | awk '{print "tests/"$0}')
```

**75 passed, 7 warnings in 2.08s**, over 22 files:
`test_contacts_add_null_name.py`, `test_contacts_carddav_security.py`,
`test_contacts_import_nonstring.py`, `test_contacts_routes_shim.py`,
`test_contacts_vcard_parse.py`, `test_history_compact_tool_calls.py`,
`test_history_db_fallback_hidden.py`, `test_history_display_model_hydration.py`,
`test_history_order_by_timestamp_regression.py`, `test_history_routes_shim.py`,
`test_history_topics_owner_scope.py`, `test_manage_notes_owner_gate.py`,
`test_note_reminder_email_oauth.py`, `test_note_reminder_fire_scope.py`,
`test_note_routes_shim.py`, `test_notes_dom_xss_helpers.py`,
`test_notes_fail_closed_auth.py`, `test_notes_search_reset_on_reopen_js.py`,
`test_notes_select_esc_listener_js.py`, `test_notes_update_due_date.py`,
`test_notes_z_order_js.py`, and `test_tool_rag_contacts_domain.py` (all under `tests/`).
Warnings were SQLAlchemy's deprecated `declarative_base` location and naive
`datetime.utcnow()` usage; there were no failed or skipped tests.

### [PERF] CardDAV requests run synchronously inside async contact handlers

- **Location:** `routes/contacts/contacts_routes.py:742-744`, with `:305-309`, `:363`, `:813-825` and `:832-837`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the list handler calls a synchronous helper without yielding:

  ```python
  async def list_contacts(_admin: str = Depends(require_admin)):
      """List all contacts."""
      contacts = _fetch_contacts()
  ```

  On a cache miss, `_fetch_contacts` performs synchronous REPORT and, if needed,
  GET requests:

  ```python
  contacts = _fetch_via_report(cfg, auth)
  if contacts is None:
      # Fallback: plain GET, concatenated vCards, no hrefs.
      r = httpx.get(cfg["url"], auth=auth, timeout=10)
  ```

  Search, add, import, export, edit and delete also call synchronous contact helpers
  from `async def`. Import can perform a sequential PUT for every card; export forces
  a fetch even while the cache is fresh. The inline probe invoked the real list
  endpoint with a cold cache, stubbed configuration/REPORT fallback, and replaced
  `httpx.get` with a function comparing its thread id to the running event loop's:

  ```text
  CardDAV GET runs on event-loop thread [True]
  ```

  The sibling reminder sender already uses `await _aio.to_thread(_smtp_send)`
  (`routes/note/note_routes.py:392`).
- **Impact:** a slow CardDAV server blocks unrelated requests and streaming work on
  the same event loop while each synchronous network operation waits. The socket
  timeout is 10 seconds for reads, not a short CPU-only pause, and imports multiply
  waits across cards. Admin-only access and the 60-second read cache limit frequency,
  not the effect on other users. The probe establishes thread placement, not measured
  production latency or a total wall-clock bound.
- **Fix:** move the synchronous handlers to FastAPI's synchronous endpoint threadpool,
  or offload the complete synchronous operation with `asyncio.to_thread`. Preserve
  serialization of shared contacts/settings read-modify-write operations when adding
  concurrency; atomic file replacement alone does not prevent lost updates.

### [BUG] vCard export silently drops every contact's postal address

- **Location:** `routes/contacts/contacts_routes.py:623-632`, with `:258-260` and `:843`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_contacts_to_vcf` rebuilds each card with name, UID, email and phone,
  but does not pass the stored address:

  ```python
  _build_vcard(
      c.get("name") or ((c.get("emails") or [""])[0].split("@")[0] if c.get("emails") else "Contact"),
      "",
      uid=c.get("uid") or str(uuid.uuid4()),
      emails=c.get("emails") or [],
      phones=c.get("phones") or [],
  )
  ```

  The builder already supports addresses and emits `ADR` only when one is supplied:

  ```python
  addr = (address or "").strip()
  if addr:
      lines.append(f"ADR:;;{_vesc(addr)};;;;")
  ```

  `/api/contacts/export` calls this helper for its default vCard format. An inline
  Python probe passed a synthetic contact with a nonempty address through
  `_contacts_to_vcf` and then `_parse_vcards`; the result was:

  ```text
  vCard address roundtrip ''
  ```

- **Impact:** exports omit postal addresses that the add/edit/import paths preserve.
  A user transferring the export to another address book, or using it to restore
  contacts, gets no addresses and no warning. Export does not erase the original
  store, so recovery is possible while that store remains available.
- **Fix:** pass `address=c.get("address") or ""` to `_build_vcard` and add an
  export/import round-trip test with a nonempty address.

### [ERROR-HANDLING] Nine notes and history endpoints return 500 for a non-object JSON body

- **Location:** `routes/note/note_routes.py:853-854`, `:905-906`; `routes/history/history_routes.py:255-256`, `:270-271`, `:288-289`, `:351-352`, `:461-462`, `:512-513`, `:601-602`
- **Severity:** low
- **Disposition:** next
- **Evidence:** this recurs from the non-object-body class reported in
  `routes-rest-auth-admin.md`. Each endpoint immediately uses `.get` on the result
  of `request.json()`, without verifying it is a mapping. For example:

  ```python
  body = await request.json()
  note_id = str(body.get("note_id") or "").strip()
  ```

  and:

  ```python
  body = await request.json()
  keep_count = body.get("keep_count", 0)
  ```

  An inline TestClient probe mounted the actual routers, stamped a synthetic
  authenticated identity, and stubbed history's session-owner lookup so it could
  reach body validation without a stored session. With exception propagation
  disabled, both `[]` and `"x"` returned 500 on every path:

  ```text
  /api/notes/fire-reminder
  /api/notes/reorder
  /api/session/example/truncate
  /api/session/example/message
  /api/session/example/delete-messages
  /api/session/example/edit-message
  /api/session/example/update-last-meta
  /api/session/example/merge-last-assistant
  /api/session/example/fork
  ```

  The history handlers that log the exception reported that `list` or `str` has no
  attribute `get`. As controls, the same two bodies returned 422 on POST
  `/api/notes` (Pydantic model) and POST `/api/contacts/import` (`data: dict`).
- **Impact:** an authenticated client sending a valid JSON value of the wrong shape
  receives an internal-error response rather than a validation error. The checked
  history paths require ownership before parsing, and the failure occurs before
  mutation; this is not an authorization bypass or demonstrated data loss.
- **Fix:** use request models, or reject non-dictionaries with 400 immediately after
  parsing. Keep any new validation exception outside broad handlers that would
  convert it back to 500.
