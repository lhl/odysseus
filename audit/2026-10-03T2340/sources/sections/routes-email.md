# routes: email

## Overview

The email feature's server surface: `routes/email_routes.py` (every `/api/email/*` handler —
inbox list, read, attachments, flag/move/delete, compose, send, draft, schedule, AI summary,
reply and translate, writing style, and the account and Google OAuth CRUD),
`routes/email_helpers.py` (the auth dependencies, account-config resolution, IMAP/SMTP
connection helpers, message parsing and attachment extraction, the `scheduled_emails` schema
and the owner-scoped cache tables) and `routes/email_pollers.py` (the scheduled-send poller
and the auto-summarize/reply/classify pass).

The boundary: the middleware that stamps `request.state.current_user` and the
`AuthManager` behind `owner_is_admin_or_single_user` are `core-auth-session` /
`routes-rest-auth-admin`; the `EmailAccount` table and its encryption are
`core-data-platform` / `src-security`; the MCP tool that stages `agent_draft` rows is
`mcp-servers`; the reader that renders the returned HTML is `static-js-documents-email`.
This section covers whether each route authenticates, scopes and offloads correctly, and
whether the credentials these helpers hold stay server-side — not whether the store
underneath is safe.

## Coverage

**Read fully:** all three assigned files (9,725 lines).

| File | Lines |
| --- | ---: |
| `routes/email_routes.py` | 6,152 |
| `routes/email_helpers.py` | 2,008 |
| `routes/email_pollers.py` | 1,565 |

**Read partially:** the boundary code the findings rest on:

- `src/auth_helpers.py` at `get_current_user`/`effective_user` (`:11-38`)
- `src/tool_security.py` at `owner_is_admin_or_single_user` (`:237-262`)
- `src/email_thread_parser.py` at the output shape (`:14-22`) and `parse_thread` (`:605-614`)
- `src/task_scheduler.py` at `RETIRED_HOUSEKEEPING_ACTIONS` (`:265-269`)
- `app.py` at the router construction (`:860-864`)
- `static/js/emailLibrary.js` at `_sanitizeHtml` and its three call sites (`:5826-5847`, `:6175`)
- the three `docker-compose*.yml` files and `.env.example` at `ODYSSEUS_INPROCESS_POLLERS`
- `specs/email-contacts.md:93`

**Not read:**

- the auth middleware and `AuthManager` internals (assigned to `core-auth-session` and
  `routes-rest-auth-admin`)
- `src/auth_helpers.py` below `:40` and `src/owner_identity.py`
- the `EmailAccount` model, its migrations and `src/secret_storage.py` beyond the
  `encrypt`/`decrypt` call sites in these files (assigned to `core-data-platform`)
- the MCP email server (assigned to `mcp-servers`)
- `scripts/odysseus-mail` and the cron/systemd deployment path
- the front end beyond the sanitizer cited above

**Checks run:**

- a route-level probe that built the real router with `setup_email_routes()` and (a) confirmed
  `require_owner`'s sub-dependency carries the `account_id` query parameter and that a foreign
  `account_id` on `GET /api/email/list` reaches `_assert_owns_account`, (b) called the
  `/accounts/test` coroutine with a JSON array and a JSON string body, (c) printed
  `attachment_extract_dir` for two inputs
- an event-loop stall measurement against a black-hole IMAP listener, quoted in the `PERF` finding
- an `import app` probe that printed the poller state at startup, quoted in the first finding
- a `grep` for the callers of `_send_email_sync`, `_auto_summarize_poller` and `email_boundaries`
- the writer/caller greps cited in each finding

Forty-three suites were run over this surface — every file matching `ls tests | grep -iE
'email|mail|imap|smtp'`, from `tests/test_active_email_reply_guard.py` and
`tests/test_email_account_default_serialization.py` through `tests/test_imap_uid_commands.py` and
`tests/test_schedule_email_offset_normalization.py` — **269 passed**.

### [BUG] The scheduled-send poller starts only when a client asks for the inbox list

- **Location:** `routes/email_pollers.py:1542-1565` (with `routes/email_routes.py:2370-2372`, `:1514`, `app.py:863`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `setup_email_routes()` calls `_start_poller()` (`routes/email_routes.py:1514`),
  and `app.py:863` calls that at import time, before uvicorn has a running loop. `_launch`
  therefore raises `RuntimeError` and the only remaining start path is a hook that a route
  has to await:

  ```python
  def _launch():
      global _poller_task, _summarize_task
      loop = asyncio.get_running_loop()
      if _poller_task is None:
          _poller_task = loop.create_task(_scheduled_email_poller())
          logger.info("Started scheduled email poller")
      _summarize_task = None

  try:
      _launch()
  except RuntimeError:
      # No running loop yet (import-time call). Retry on first request
      # by registering a one-shot startup coroutine.
      ...
      _start_poller._deferred = _deferred_start
  ```

  `grep -rn '_deferred' routes/ app.py src/` finds exactly one consumer of that hook, inside
  `GET /api/email/list`:

  ```python
  _deferred = getattr(_start_poller, '_deferred', None)
  if _deferred:
      await _deferred()
  ```

  Measured by loading the app the way uvicorn does:

  ```
  $ ODYSSEUS_DATA_DIR=/tmp/audit-email-probe-data venv/bin/python -c "import app; import routes.email_pollers as ep; ..."
  _poller_task after import        : None
  _start_poller._deferred set      : True
  running loop at import           : no
  ```

  Nothing else in the repository starts it: `grep -rn '_start_poller\|email_pollers' app.py`
  matches only the `setup_email_routes` import and call.
- **Impact:** the in-process task that delivers `scheduled_emails` rows does not exist until
  someone opens the email list. A server that restarts while no browser is connected — or an
  install driven through the API, the MCP tools or a mobile client — holds due rows
  indefinitely: the row stays `pending`, `GET /api/email/scheduled` shows it as scheduled, and
  the poller that would send it was never created. The same delay applies to a `/pending` agent
  draft the user approves, since approval only flips the row to `pending`. All three compose
  files default `ODYSSEUS_INPROCESS_POLLERS` to `1`, so this is the default deployment, and
  nothing logs that the poller never started.
- **Fix:** start the poller from the app's lifespan/startup hook (where a loop exists) instead
  of relying on a route to await the deferred starter, or keep the deferred hook and also call
  it from startup so the first request is not required.

### [PERF] Nineteen `async def` handlers run blocking IMAP, SMTP or HTTP I/O on the event loop

- **Location:** `routes/email_routes.py:3304` (with `:3286`, `:3331`, `:3393`, `:3714`, `:3736`, `:3753`, `:3768`, `:3800`, `:3815`, `:3854`, `:3906`, `:3992`, `:4008`, `:4205`, `:4474`, `:5893`, `:5938`, `:6059`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** each cited line opens a connection or issues a command inside a coroutine that
  has not awaited anything, so the whole round-trip runs on the loop thread. The same file
  offloads identical work elsewhere — `:2391`, `:3216`, `:3966`, `:4767`, `:4829` and `:4919`
  use `asyncio.to_thread` — and two routes spell out why:

  ```python
  # routes/email_routes.py:2770-2772
  # Sync def: the body is blocking IMAP I/O with no awaits. As `async def` it ran
  # directly on the event loop and stalled the whole app during a search; as a sync
  # def FastAPI runs it in a threadpool, keeping the loop responsive.
  ```

  The six attachment handlers fetch the whole message inline (`_imap_uid_fetch(conn, uid,
  "(RFC822)")` at `:3288`, `:3306`, `:3333`, `:3395`, `:3716`, `:4207`), so their stall scales
  with message size; the flag/move/delete handlers each pay a `SELECT` plus a `STORE`/`MOVE`
  round-trip, and `resolve_contact` issues up to 200 serial header fetches per folder across
  three folders (`uids = data[0].split()[-200:]`, `:4484`; `conn.fetch(...)`, `:4487`).
  `test_account_config` connects and logs in to IMAP and SMTP inline (`_open_imap_connection`,
  `:5893`; `smtplib.SMTP_SSL`, `:5938`), and `google_oauth_callback` makes two blocking `httpx`
  calls (`:6059`, `:6081`). Measured with
  `ODYSSEUS_IMAP_TIMEOUT_SECONDS=3` and a listener that accepts and never sends an IMAP
  greeting, running the real `/accounts/test` coroutine next to a 50 ms heartbeat:

  ```
  endpoint returned in 5.03s: {'ok': False, 'imap': {'ok': False, 'error': 'timed out'}, 'smtp': None}
  heartbeat ticks before/during/after: 5; max gap between ticks: 5.08s
  ```

  The heartbeat made no progress at all for the duration of the call. The shipped IMAP timeout
  is 30 s by default (`routes/email_helpers.py:1149-1157`, clamped to 5-300 s) and the SMTP
  connect carries its own 10 s timeout, so one "Test connection" click on an unreachable host
  can stall every other request for tens of seconds; a 20 MB attachment fetch stalls the loop
  for as long as the mailbox takes to deliver it.
- **Impact:** while any of these handlers is running, every other request in the process —
  including a streaming chat turn and the SSE progress stream — is frozen. Any authenticated
  user can trigger the long ones repeatedly (one click each, no special privilege), and the
  attachment routes are on the normal reading path. The mitigation the file already applies to
  its sibling routes (`asyncio.to_thread`, or a sync `def` so FastAPI's threadpool runs it) is
  simply missing here.
- **Fix:** wrap the IMAP/SMTP/httpx work in `await asyncio.to_thread(...)` (or make the handler
  a sync `def`, as `search_emails` and `archive_email` already are).

### [RACE] Attachment extraction is keyed on folder and UID only, so two mailboxes share one file path

- **Location:** `routes/email_helpers.py:685-696` (with the write at `:1618-1621` and the call sites `routes/email_routes.py:3313`, `:3345`, `:3415`, `:3452`, `:3722`, `:4212`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the directory name is built from the two request values and nothing else — the
  owner and the account are not part of the key:

  ```python
  key = re.sub(r"[^A-Za-z0-9._-]", "_", f"{folder}_{uid}") or "_"
  target = (ATTACHMENTS_DIR / key).resolve()
  ```

  Measured:

  ```
  attachment_extract_dir('INBOX', '5') -> /tmp/audit-email-probe-data/mail-attachments/INBOX_5
  attachment_extract_dir('../../etc', '5') -> /tmp/audit-email-probe-data/mail-attachments/.._.._etc_5
  ```

  (The traversal attempt is flattened and then re-checked against the base directory, so the
  containment claim in the docstring holds.) All six call sites pass `(folder, uid)`.
  `_extract_attachment_to_disk` writes the file with a truncating open and returns the path, and
  `download_attachment` hands that same path to `FileResponse`:

  ```python
  target_dir = attachment_extract_dir(folder, uid)          # :3313
  filepath = _extract_attachment_to_disk(msg, index, target_dir)
  ...
  return FileResponse(path=str(filepath), filename=filepath.name, media_type="application/octet-stream")
  ```

  (`routes/email_routes.py:3313-3323`; the elided lines are the not-found check.)

  Nothing locks the directory, and nothing deletes the file when the response finishes.
- **Impact:** two users whose mailboxes both have an `INBOX` and a message at the same UID and
  an attachment that sanitizes to the same filename map to one path. A request from the second
  user that lands between the first user's write and the end of its streaming response
  overwrites the bytes the first response is reading, so a response can carry the other user's
  attachment or a truncated one; `attachment_as_doc` reads the file after extracting it in the
  same window. Every mailbox has an `INBOX` and low UIDs, so the folder/UID half collides
  routinely; the filename must collide too, which is what keeps this low.
- **Fix:** include the account (and owner) in the directory key — `attachment_extract_dir(owner,
  account_id, folder, uid)` — so each mailbox extracts into its own directory.

### [BUG] A process death mid-send leaves a scheduled email in `sending` forever, invisible to the UI

- **Location:** `routes/email_pollers.py:1421-1424` (with `:1480`, `:1488`, `routes/email_routes.py:4368`, `:4389`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the row is claimed before any work and only two paths change the status
  afterwards — success to `sent`, an in-process exception to `failed`:

  ```python
  claim_cur = claim_conn.execute(
      "UPDATE scheduled_emails SET status='sending' WHERE id=? AND status='pending'",
      (sid,),
  )
  ...
  conn2.execute("UPDATE scheduled_emails SET status='sent' WHERE id=?", (sid,))
  ```

  Nothing else reads or writes that state: `grep -rn "'sending'" routes/ src/ core/ scripts/`
  returns that one `UPDATE`. The list endpoint filters `status IN ('pending', 'failed')`
  (`routes/email_routes.py:4368`) and cancel deletes only `status = 'pending'` (`:4389`), and
  there is no age-based reaper.
- **Impact:** a process that dies between the claim and the completion (SIGKILL, OOM kill,
  container stop, power loss) leaves the message permanently in `sending`: it is never retried,
  never listed, never cancellable, and it never sends. The claim's own comment explains why the
  claim exists, but the recovery half is missing; a kill during a `docker compose restart` while
  a send is in flight is enough.
- **Fix:** at the start of each poll pass, reset rows whose `sending` state is older than a few
  minutes back to `pending` (a `sending_at` timestamp, or reuse `created_at`), and show
  `sending` rows in the list so the user can see the state.

### [ERROR-HANDLING] `POST /api/email/accounts/test` answers 500 for a non-object JSON body

- **Location:** `routes/email_routes.py:5792-5803`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the `try` covers only the parse, and the next statement assumes a mapping:

  ```python
  try:
      body = await req.json()
  except Exception:
      return {"ok": False, "imap": {"ok": False, "error": "invalid request body"}}

  ...
  acc_id = body.get("account_id")
  ```

  Measured with the real route coroutine and a request whose `json()` returns the parsed body:

  ```
  body=[]: AttributeError: 'list' object has no attribute 'get'
  body='x': AttributeError: 'str' object has no attribute 'get'
  ```

  This is a recurrence of the class reported for three admin endpoints in
  `routes-rest-auth-admin.md`. It is the only occurrence here: the other JSON endpoints in these
  files take a `data: dict` parameter (FastAPI answers 422 for an array or a string) or a
  Pydantic model such as `SendEmailRequest`.
- **Impact:** an authenticated client that sends `[]` or `"x"` gets an unhandled traceback and a
  500 where this handler's own contract is `{"ok": False, "imap": {"ok": False, "error":
  "invalid request body"}}`. Not reachable from the shipped UI, so the cost is a confusing
  failure and a log line.
- **Fix:** after the parse, `if not isinstance(body, dict): return {"ok": False, "imap": {"ok":
  False, "error": "invalid request body"}}`.

### [BUG] The attachment-metadata cache falls back to another account's row

- **Location:** `routes/email_routes.py:1234-1242`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the exact-account lookup is followed by one that drops `account_key`:

  ```python
  row = conn.execute(
      """
      SELECT attachments_json
      FROM email_attachment_metadata_cache
      WHERE owner=? AND account_key=? AND folder=? AND uid=?
      """,
      (owner or "", _account_cache_key(account_id, owner), folder, str(uid)),
  ).fetchone()
  if not row:
      row = conn.execute(
          """
          SELECT attachments_json
          FROM email_attachment_metadata_cache
          WHERE owner=? AND folder=? AND uid=?
          ORDER BY updated_at DESC
          LIMIT 1
          """,
          (owner or "", folder, str(uid)),
      ).fetchone()
  ```

  Every sibling cache read in the file keys on `owner` and `account_key` together (for example
  `_email_preview_cache_get`, `:1158-1183`).
- **Impact:** for one owner with two accounts, `/attachments/{uid}?folder=INBOX&account_id=B`
  returns account A's cached attachment list whenever B has no cached row for that UID — the
  chips show another mailbox's filenames, sizes and content types. The bytes come from the
  right message because `/attachment/{uid}/{index}` re-extracts from the requested account, so
  the user can click a chip whose name does not match what downloads. No cross-owner exposure:
  the owner predicate is still in the query.
- **Fix:** drop the fallback, or restrict it to legacy rows whose `account_key` is empty
  (`AND (account_key='' OR account_key IS NULL)`).

### [FOOTGUN] The thread-turn cache is read by Message-ID with no owner scope, and its rows carry message bodies

- **Location:** `routes/email_routes.py:3074-3077` (with `routes/email_helpers.py:933-941`, `:566-573`, `:720`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the read selects a row by Message-ID alone:

  ```python
  _row3 = _c.execute(
      "SELECT sig_start, quote_start, turns_json FROM email_boundaries WHERE message_id = ?",
      (message_id.strip(),),
  ).fetchone()
  ```

  and `turns_json` is returned to the caller as `thread_turns`/`boundaries`. The table has no
  owner column:

  ```sql
  CREATE TABLE IF NOT EXISTS email_boundaries (
      message_id TEXT PRIMARY KEY,
      uid TEXT,
      folder TEXT,
      sig_start INTEGER,
      quote_start INTEGER,
      model_used TEXT,
      created_at TEXT NOT NULL
  )
  ```

  The payload is message content — each turn carries the body (`src/email_thread_parser.py:14-22`:
  `{"level": 1, "body_html": "...", "meta": "Alice <a@x> · May 5"}`). Every neighbouring
  Message-ID-keyed cache is owner-scoped for exactly this reason
  (`OWNER_SCOPED_EMAIL_CACHE_TABLES`, `routes/email_helpers.py:566-573`; the migration comment at
  `:720`: "Message-IDs are global, so AI-derived cache rows must be owner-scoped just like
  email_tags"), and `email_boundaries` is not in that set. Nothing in the current tree writes the
  table — `grep -rn 'email_boundaries' routes/ src/` finds the schema, the `turns_json`
  migration and this read, and the writer that used to populate it is gone
  (`mark_email_boundaries` is in `RETIRED_HOUSEKEEPING_ACTIONS`, `src/task_scheduler.py:265-269`)
  — so only rows written by an earlier release can be served.
- **Impact:** on an install upgraded from a release that populated the table, opening a message
  whose Message-ID matches a row written for another owner returns that owner's parsed thread
  text and fold offsets instead of parsing the caller's own copy. The cache's version check
  guards the parser version, not the owner. Low because nothing writes new rows and it needs a
  Message-ID collision (an attacker who sends the same Message-ID to two users can create one,
  but only for a row that predates the upgrade).
- **Fix:** add `owner` to the table and to this read (and to `OWNER_SCOPED_EMAIL_CACHE_TABLES`),
  or delete the cache read and always parse on the fly, which is what already happens for every
  message with no cached row.

### [DEAD-CODE] Two background/send implementations have no callers, and the docstrings still describe them as live

- **Location:** `routes/email_routes.py:4245` (with `routes/email_pollers.py:1370`, `:8`, `:11-12`, `:1548`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `grep -rn 'send_email_sync'` over the whole repository returns only the
  definition, whose docstring says the opposite:

  ```python
  async def _send_email_sync(
      to, cc, bcc, subject, body, in_reply_to, references, attachments,
      account_id=None, owner="", odysseus_kind=None, odysseus_ref=None,
  ):
      """Shared send logic used by both /send and scheduled delivery.

      SECURITY: callers MUST pass `owner` (the authed user) so the config
      lookup is scoped — ...
  ```

  `/send` builds its own MIME message inline (`:4533-4540`) and the scheduled poller builds its
  own (`routes/email_pollers.py:1435-1442`). `_auto_summarize_poller`
  (`routes/email_pollers.py:1370`) is likewise unreachable: nothing calls it, `_launch` clears
  its handle (`_summarize_task = None`, `:1548`), and its own docstring already says it is
  "[k]ept for backward compatibility" (`:1371-1372`) — while the module docstring above it still
  advertises "driver that wakes the pass on a 30-min cadence" (`:8`), and `_start_poller`'s says
  it "spawns both pollers" (`:11-12`).
- **Impact:** a maintainer reading this section believes the auto-summarize pass runs on a
  30-minute timer (the live drivers are the `summarize_emails` scheduled task,
  `src/builtin_actions.py:1006`, and the new-mail path at `routes/email_routes.py:422-423`) and
  that `_send_email_sync` is the shared send path (it is never called, so a fix or a security
  change made there changes nothing at runtime — and its owner-scoping warning is not attached
  to either live copy).
- **Fix:** delete both, or delete the stale docstring lines; if `_send_email_sync` is meant to
  replace the two inline copies, wire `/send` and the poller to it.
