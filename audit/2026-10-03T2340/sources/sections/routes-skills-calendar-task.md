# routes: skills, calendar, tasks

## Overview

The self-service skills library, the local calendar, and the scheduled-task CRUD surface:
`routes/skills_routes.py` (SKILL.md CRUD, slash-command invocation, the manual and autonomous
skill audit, the built-in tool-override editor), `routes/calendar_routes.py` (calendar and event
CRUD, ICS import and export, CalDAV account configuration, the natural-language quick-parse), and
`routes/task/task_routes.py` with `routes/task/__init__.py` (task CRUD, pause/resume/revert,
manual run and webhook triggers, run history, the natural-language task parser).

The boundary: the skills store these routes drive (`services/memory/skills.py`,
`skill_format.py`, `skill_importer.py`) is `services-memory`; the scheduler, its executors and
`compute_next_run` are `src-research-scheduling`; the CalDAV client and its write-back are
`src-email-integrations`; the `CalendarCal` / `CalendarEvent` / `ScheduledTask` / `TaskRun` tables
are `core-data-platform`; request authentication and `require_admin` are `core-auth-session`; the
`cookbook_serve` action is `routes-cookbook`; the calendar and task front end is in the
`static-*` sections. This section covers whether each route authenticates, scopes to its owner,
validates what it accepts, and bounds the work it starts — not whether the store, the scheduler or
the middleware underneath is correct.

## Coverage

**Read fully:** the four assigned files (4,860 lines): `routes/skills_routes.py` (1,899),
`routes/calendar_routes.py` (1,775), `routes/task/task_routes.py` (1,181),
`routes/task/__init__.py` (5).

**Read fully, outside the assigned paths:** `services/memory/skill_importer.py` (487),
`src/auth_helpers.py` (199), `src/upload_limits.py` (72), `src/task_action_policy.py` (47).

**Read partially:** `src/task_scheduler.py` at `compute_next_run` (`:113-231`),
`HOUSEKEEPING_DEFAULTS` (`:251-263`), the loop (`:673-700`), `_check_due_tasks` (`:701-735`),
`_execute_task` / `_execute_task_locked` (`:737-1159`), `run_task_now` / `stop_task`
(`:2264-2290`); `services/memory/skills.py` at the path helpers (`:76-83`), `_iter_skill_files` /
`_read_skill` / `_write_skill` (`:159-181`), `load` (`:278-287`), `add_skill` (`:293-383`),
`import_bundle_from_files` (`:384-431`), `update_skill` / `delete_skill` / `read_skill_md`
(`:432-575`); `services/memory/skill_format.py` at `slugify` (`:65-72`); `src/caldav_sync.py` at
`validate_caldav_url` (`:106-131`) and the sync entry points (`:617-722`); `core/middleware.py` at
`require_admin` (`:57-82`); `core/database.py` at `ScheduledTask` (`:730-760`), `TaskRun`
(`:810-825`), `CalendarCal` (`:1838-1855`) and `CalendarEvent` (`:1856-1875`);
`src/builtin_actions.py` at the urgency-cache writer (`:2275-2290`, `:2532`);
`routes/email_helpers.py` at `OWNER_SCOPED_EMAIL_CACHE_TABLES` (`:566-586`); `src/tools/system.py`
at the `manage_tasks` action (`:285-310`, `:340-365`); `app.py` at the uvicorn launch
(`:1300-1306`); `Dockerfile:113`; `specs/calendar-tasks-notes.md:52`; `static/js/tasks.js` at the
run-now paths (`:150-151`, `:1874-1877`, `:2767`).

**Not read:** the middleware that authenticates the request — what stamps
`request.state.current_user` lives in `app.py` and `core/middleware.py` (assigned to
`core-auth-session`), and only `require_admin`, `require_user` and `get_current_user` were read;
the task executors the scheduler dispatches into (`_execute_llm_task`, `_execute_action`,
`_execute_research_task`, `_deliver_task_result`, `_deliver_via_mcp`) beyond their call sites;
`src/agent_loop.stream_agent_loop` and the tool surface a skill test or an audit run reaches; the
CalDAV sync implementation (`_sync_blocking`, `src/caldav_writeback.py`) and
`src/url_safety.check_outbound_url`; the skills, calendar and task front end beyond the regions
cited; the `do_manage_*` agent tools (their own sections) beyond the `scheduled_day` pass-through
cited; the remaining 2,000-odd lines of `src/task_scheduler.py` (delivery, notifications,
research and check-in execution).

**Checks run:** four throwaway probes under `/tmp` that call the real handlers — a non-object-body
probe (the router built with a stub skills manager, mirroring
`tests/test_integrations_store_shape.py`), an ICS-import probe over a temp SQLite database
mirroring `tests/test_calendar_import_zero_duration.py`, a `create_task` probe over the same
harness, and a self-request repro mirroring `_try_delete`'s call shape; `_expand_rrule` timed
directly with a stub event; the dateutil expansion timed separately; and the `icalendar` parse of
100,000 `VEVENT`s timed. The
sixty-six suites matching `ls tests | grep -iE 'skill|calendar|task|ics'` were run —
**319 passed**.

### [BUG] Deleting a cookbook task calls its own API from a blocking client, so the cascade never runs and the delete stalls for 10 seconds

- **Location:** `routes/task/task_routes.py:771` (the call), `:62-69` (the blocking client), `:89-91` (the fallback scan)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `delete_task` is an `async def` and calls the cascade synchronously, and the
  cascade reaches the running server over HTTP with a synchronous client:

  ```python
  _maybe_cascade_calendar_event(task)          # :771, inside `async def delete_task`
  ...
  def _try_delete(uid: str) -> bool:           # :62
      try:
          with httpx.Client(timeout=10) as client:
              r = client.delete(
                  f"{internal_api_base()}/api/calendar/events/{uid}",
                  headers=headers,
              )
  ```

  (The `...` line is an elision, not source.)

  The shipped deployment is one process with one event loop: `uvicorn.run(app, host=bind_host,
  port=bind_port, log_level="info")` (`app.py:1306`, no `workers=`) and
  `CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7000"]` (`Dockerfile:113`), with
  `internal_api_base()` resolving to this same listener. While the handler blocks in the sync
  client, the only event loop is not reading the socket, so the request it is waiting for is never
  served. Measured with a throwaway app that has the same shape (async handler, sync
  `httpx.Client(timeout=10)`, self-request on a single-worker uvicorn):

  ```
  GET /outer -> {'inner_error': 'ReadTimeout: timed out', 'elapsed': 10.011528253555298} wall=10.0s
  ```

  So every `DELETE /api/tasks/{id}` for a `cookbook_serve` task (an admin-only action) blocks
  every other request for ten seconds and then discards the failure — `_try_delete` catches the
  exception and returns `False`, and the caller ignores the result (`:80-82`). The spec states the
  opposite of what the code does: "task deletion cleans up the linked event when present, falling
  back to exact-summary matching for legacy events without a stored UID"
  (`specs/calendar-tasks-notes.md:52`). The comment above the call promises the same thing
  (`routes/task/task_routes.py:766-770`).
- **Impact:** the linked Cookbook calendar event is never deleted, so the calendar keeps a phantom
  event for a task that no longer exists — the outcome the cascade was written to prevent. In the
  fallback path (a task with no `cookbook_event_uid` marker) the
  stall repeats: the same handler makes two more loopback calls (`:91`, `:107`) before giving up.
  A multi-worker deployment would make the self-request serviceable, but neither launch path in
  the repository uses more than one worker.
- **Fix:** run the cascade off the event loop and let it finish before the row is deleted —
  `await asyncio.to_thread(_maybe_cascade_calendar_event, task)` — or call the calendar route's
  logic in-process instead of over HTTP. Offloading alone is enough for the loop to serve the
  self-request.

### [PERF] An unvalidated RRULE makes a single calendar read block the event loop for seconds to minutes

- **Location:** `routes/calendar_routes.py:752` (the expansion loop), `:1249` and `:1300` (the unvalidated `rrule` writes), `:1188` (the call site)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** both write paths store the caller's `rrule` verbatim with no parse or bound
  (`rrule=data.rrule or ""` at `:1249`, `ev.rrule = data.rrule` at `:1300`), and the ICS import
  stores `comp.get("rrule").to_ical().decode()` (`:1538`). `list_events` then expands every
  recurring row synchronously on the event loop (`:1188`, inside `async def list_events` at
  `:1140`), and `_expand_rrule` asks dateutil for occurrences starting at the *window* while
  iterating from `DTSTART`:

  ```python
  expand_start = start - duration                                    # :746
  ...
  for occ_start in rule.xafter(expand_start, inc=True):              # :752
  ```

  (The `...` line is an elision, not source.)

  `_RRULE_EXPANSION_LIMIT` (`:661`, 1000) caps the results returned, not the work done to reach
  them, and the `if occ_start >= end: break` only fires after dateutil has walked every occurrence
  between `DTSTART` and the window. Measured with a stub event whose `DTSTART` is 2020-01-01 and
  `rrule = FREQ=MINUTELY;INTERVAL=1`, calling the real `_expand_rrule`:

  ```
  today's window (2026-10-04..+31d): 1000 occurrences, 4.34s
  _expand_rrule window 2026-01-01..+1d: 1000 occurrences, 3.95s
  _expand_rrule window 2028-01-01..+1d: 1000 occurrences, 5.25s
  _expand_rrule window 2100-01-01: 1000 occurrences, 51.83s
  ```

  End to end through the real handlers over a temp database — one `POST /api/calendar/import` of a
  one-event file, then one `GET /api/calendar/events`:

  ```
  minutely rrule + far window: import OK {...'imported': 1...} in 0.01s
     list 2030-01-01T00:00:00..2030-01-02T00:00:00: 1000 events in 6.28s
  ```

  (The `{...}` in the import line elides the rest of the printed dict.)

  `FREQ=SECONDLY` is worse: the same `rrulestr(...).xafter(2100-01-01)` call took 2946 s (49
  minutes) when measured directly. Any authenticated user can plant such an event — the calendar
  routes carry no admin gate — and a later `GET /api/calendar/events` for any window after the
  event's `DTSTART` pays the cost.
- **Impact:** the calendar view is not a one-off request: the cost is paid on every events request
  while the row exists, and the expansion runs on the event loop, so the whole instance (chat
  streams, task runs, other users) stalls for the duration — about 4 s for the ordinary
  current-month window with a minutely rule planted in 2020, 52 s for a window in 2100, and tens
  of minutes for a secondly rule.
- **Fix:** bound the iteration, not just the result — start the expansion from the later of
  `DTSTART` and `expand_start` (or reject a rule whose computed first occurrence is more than N
  iterations away), and validate `rrule` on write with `rrulestr` plus a minimum interval for
  `FREQ=MINUTELY`/`FREQ=SECONDLY`. Running `_expand_rrule` in `asyncio.to_thread` would keep the
  loop responsive but leave the per-request cost.

### [BUG] A weekly task with a negative `scheduled_day` is created with a past `next_run` and re-runs forever

- **Location:** `src/task_scheduler.py:194-201` (the weekly branch), `routes/task/task_routes.py:498-503` (the create path), `:148` (the field)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `scheduled_day` is accepted as any integer and only cron expressions and
  `scheduled_date` are validated on the way in (`routes/task/task_routes.py:148`, `:498-503`). The
  weekly branch adds a negative `days_ahead` to today instead of normalizing it into the next
  seven days:

  ```python
  if schedule == "weekly":
      day = scheduled_day if scheduled_day is not None else 0  # 0=Monday
      candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
      days_ahead = day - candidate.weekday()
      if days_ahead < 0 or (days_ahead == 0 and candidate <= now):
          days_ahead += 7
      candidate += timedelta(days=days_ahead)
  ```

  `day = -100` on a Monday gives `days_ahead = -100 - 0 = -100`, then `-93`, so the returned time
  is 93 days in the past. Measured on `compute_next_run("weekly", "09:00", day, None, after=now)`
  with `now` a Monday at noon:

  ```
  scheduled_day=  -10 -> next_run=2026-10-02 09:00:00  in_past=True  delta_days=-4
  scheduled_day= -100 -> next_run=2026-07-04 09:00:00  in_past=True  delta_days=-94
  scheduled_day=    6 -> next_run=2026-10-11 09:00:00  in_past=False  delta_days=5
  ```

  and the same input through the real `POST /api/tasks` handler over a temp database:

  ```
  created: {'schedule': 'weekly', 'scheduled_day': -100, 'next_run': '2026-06-27T09:00:00Z', 'status': 'active'}
  now (naive utc): 2026-10-03T20:27:42.001450
  next_run in the past? True  delta: -99 days, 12:32:17.998550
  ```

  `status` is `"active"` because `next_run` is truthy (`routes/task/task_routes.py:544`), so
  `_check_due_tasks` selects it on the next tick (`ScheduledTask.status == "active",
  ScheduledTask.next_run <= now`, `src/task_scheduler.py:716-720`). After each run the scheduler
  recomputes the same past value (`:1027-1032`), so the task is due again immediately, and the
  loop's sleep is derived from that past value:

  ```python
  delta = (next_run[0] - _utcnow()).total_seconds()
  sleep_for = max(1.0, min(60.0, delta))          # src/task_scheduler.py:693-694
  ```

  A negative delta clamps to the 1-second floor, so the scheduler ticks every second.
- **Impact:** the task runs back to back for as long as it exists — an LLM task re-sends its prompt
  to the configured endpoint on every cycle — and the scheduler polls at 1 Hz instead of its
  normal ≤60 s cadence. The owner of the task is the one billed, but the instance never idles and
  every run writes a `task_runs` row. Reachable from the API (`scheduled_day` is an unvalidated
  integer on create and update) and from the agent's `manage_tasks` tool, which passes
  `args.get("scheduled_day")` straight through (`src/tools/system.py:296-308`, `:347`); the UI's
  own selector only offers 0-6, because it is built from the seven-entry `DAYS_OF_WEEK`
  (`static/js/tasks.js:27`, `:1416-1419`).
- **Fix:** validate the range where the value enters — `0 <= scheduled_day <= 6` for `weekly` and
  `1 <= scheduled_day <= 31` for `monthly` — and normalize a negative `days_ahead` with
  `days_ahead %= 7` in `compute_next_run` so a stored bad value cannot produce a past `next_run`.

### [PERF] The ICS import has no event-count cap: a 10 MB file writes 100,000 rows in one 25-second request

- **Location:** `routes/calendar_routes.py:1446-1541` (the import loop), `:1419` (the byte cap)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the upload is capped in bytes (`read_upload_limited(file, ICS_MAX_BYTES, ...)`,
  `ICS_MAX_BYTES` = 10 MB, `src/upload_limits.py:59-61`) but nothing bounds the number of
  components, and the loop runs synchronously inside `async def import_ics` (`:1412`), one
  `SELECT` per event with a UID plus one `INSERT`:

  ```python
  for comp in cal_data.walk():                          # :1446
      ...
      existing = (
          db.query(CalendarEvent)
          .filter(
              CalendarEvent.calendar_id == target_cal.id,
              CalendarEvent.dtstart == naive_src,
              CalendarEvent.summary == str(comp.get("summary", "")),
          )
          .first()
      )                                                 # :1471-1479
      ...
      db.add(ev)                                        # :1540
  ```

  (The `...` marks are elisions — not source lines, and not the full printed dicts.)

  Measured end to end through the real handler over a temp SQLite database:

  ```
  20000 events: import OK {'ok': True, 'imported': 20000, ...} in 4.77s
  bytes: 10277842 events: 100000
  import of 100000 events: {'ok': True, 'imported': 100000, ...} in 24.99s
  ```

  The 100,000-event file is 10,277,842 bytes, just under the cap, and the parser is not the
  bottleneck: `icalendar.Calendar.from_ical` on that same file took 5.79 s, the rest is the row
  loop.
- **Impact:** one authenticated request (no admin gate on `POST /api/calendar/import`) stalls every
  other request in the instance for ~25 s and permanently adds 100,000 rows to
  `calendar_events`, which every subsequent `list_events` then filters and, for the recurring
  ones, expands. The caller can repeat it with different calendar names.
- **Fix:** cap the number of imported components (a few thousand is generous for a personal
  calendar) and fail the request with 400/413 past it, and move the parse and insert loop into
  `asyncio.to_thread` so the loop stays free while the transaction runs.

### [PERF] The skill import route performs its whole synchronous GitHub fetch on the event loop

- **Location:** `routes/skills_routes.py:1361` (the call), `services/memory/skill_importer.py:246-252` (the client)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `import_skill_from_url` is an `async def` and calls the importer inline; the
  importer is synchronous end to end (`_PinnedBackend(httpcore.SyncBackend)`, `:124-128`) and uses
  a blocking client per hop:

  ```python
  files, _src = fetch_skill_bundle(body.url.strip())     # routes/skills_routes.py:1361
  ...
  with httpx.Client(
      transport=_PinnedTransport(pinned_ips),
      follow_redirects=False,
      timeout=timeout,
  ) as client:                                            # services/memory/skill_importer.py:248-252
  ```

  (The `...` line is an elision, not source.)

  Each request gets a 30 s timeout, up to five redirect hops are followed by hand
  (`_MAX_FETCH_REDIRECTS`), and a bundle can hold `MAX_FILES = 64` text files
  (`services/memory/skill_importer.py:19`, `:398-431`), so the handler can hold the loop for
  minutes on a slow or hostile host. The repository's convention is to offload exactly this
  (`await asyncio.to_thread(_fetch_sync)`, `routes/cookbook_routes.py:4048`;
  `routes/email_routes.py:2391`), and the CalDAV path does it
  (`src/caldav_sync.py:645`).
- **Impact:** while an administrator imports a skill, every other request waits — including
  streaming chat turns. Admin-gated and infrequent, so this is a stall rather than an outage.
- **Fix:** `files, _src = await asyncio.to_thread(fetch_skill_bundle, body.url.strip())`, and
  optionally pass the timeout budget down so a slow host cannot hold a thread for minutes.

### [BUG] Clearing the email-urgency task cache deletes every owner's cache files

- **Location:** `routes/task/task_routes.py:632-639`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the database half of this handler is owner-scoped — the branch above it uses
  `_email_cache_owner_clause(user)` for every table in `OWNER_SCOPED_EMAIL_CACHE_TABLES`
  (`routes/email_helpers.py:566-573`) and `owner = ? OR owner = ''` for `email_tags` — but the file
  half removes every `*.json` in the shared cache directory:

  ```python
  if action == "check_email_urgency":
      cache_dir = Path(EMAIL_URGENCY_CACHE_DIR)
      if cache_dir.exists():
          for child in cache_dir.glob("*.json"):
              child.unlink()
              removed_files += 1
  ```

  Those files are per *account*, not per owner — the writer names them `CACHE_DIR / f"{acc.id}.json"`
  (`src/builtin_actions.py:2532`) in one instance-wide directory
  (`EMAIL_URGENCY_CACHE_DIR = os.path.join(DATA_DIR, "email_urgency_cache")`,
  `src/constants.py:51`) — and the per-owner state file beside them is handled separately with an
  owner slug (`routes/task/task_routes.py:640-648`), which shows the author was tracking ownership
  for the state and not for the cache.
- **Impact:** a user clearing their own Email Tags task cache discards every other user's
  already-triaged UID checkpoints, so each of their urgency tasks re-scores up to 30 recent
  messages per account with LLM calls on its next run. Nothing is lost permanently — it is a cache
  — but the work and the token spend are another owner's.
- **Fix:** delete only the files for accounts the caller owns (join `EmailAccount` on
  `owner == user`), or move the cache under a per-owner subdirectory.

### [ERROR-HANDLING] Ten JSON endpoints answer 500 to a non-object body (recurrence of the class reported in `routes-rest-auth-admin.md`)

- **Location:** `routes/calendar_routes.py:1638-1639` (`quick_parse`), `:861-865` (`save_config`), `:919-923` (`add_caldav_account`), `:947-952` (`update_caldav_account`), `:991-994` (`test_connection`); `routes/skills_routes.py:1491-1492` (`test_skill`), `:1714-1715` (`audit_all_skills`), `:1808-1809` (`save_skill_markdown`), `:1890-1891` (`search_skills`); `routes/task/task_routes.py:1101-1102` (`parse_task`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** each handler parses the body and immediately calls `.get` on it, so a JSON array or
  string raises `AttributeError` inside the handler and FastAPI returns 500:

  ```python
  body = await request.json()                       # routes/calendar_routes.py:1638
  text = (body.get("text") or "").strip()           # :1639
  ...
  body = await request.json()                       # routes/skills_routes.py:1491
  task = (body.get("task") or "").strip()           # :1492
  ...
  body = await request.json()                       # routes/task/task_routes.py:1101
  desc = (body.get("description") or "").strip()    # :1102
  ```

  Measured by calling the real endpoint functions with a fake request whose `json()` returns `[]`
  (the same shape `tests/test_integrations_store_shape.py` uses for the auth routes):

  ```
  POST /api/calendar/quick-parse  body=[]: AttributeError: 'list' object has no attribute 'get'
  POST /api/calendar/config       body=[]: AttributeError: 'list' object has no attribute 'get'
  POST /api/calendar/test         body=[]: AttributeError: 'list' object has no attribute 'get'
  POST /api/calendar/config/accounts body=[]: AttributeError: 'list' object has no attribute 'get'
  PUT  /api/calendar/config/accounts/{id} body=[] (account exists): AttributeError 'list' object has no attribute 'get'
  POST /api/skills/search             body=[]: AttributeError: 'list' object has no attribute 'get'
  POST /api/skills/{id}/markdown     body=[]: AttributeError: 'list' object has no attribute 'get'
  POST /api/skills/{id}/test         body=[]: AttributeError: 'list' object has no attribute 'get'
  POST /api/skills/audit-all         body=[] (json ct): AttributeError: 'list' object has no attribute 'get'
  POST /api/tasks/parse              body=[]: AttributeError: 'list' object has no attribute 'get'
  ```

  Two handlers in the same files already keep the contract — `invoke_skill`
  (`routes/skills_routes.py:1425`, `... if isinstance(body, dict) else ""`) and
  `approve_skill_test_action` (`:1583-1584`, `raise HTTPException(400, "Tool approval body must be
  a JSON object.")`) — as does `import_data` in the section that reported this class
  (`routes/backup_routes.py:73`). The `try/except` wrappers around `await request.json()` at
  `routes/calendar_routes.py:860-863`, `:918-921`, `:946-949` and `:990-993` do not help: a JSON
  array parses successfully, so the fallback `body = {}` is never taken.
- **Impact:** an API client that sends a JSON array or string gets a 500 and an unhandled traceback
  in the log where a 400 is the contract the rest of the file keeps. Not reachable from the shipped
  UI, so the cost is a confusing failure and log noise, not a broken flow. `update_caldav_account`
  only reaches the raise when the caller already has a CalDAV account (otherwise the 404 at `:952`
  fires first), and `audit_all_skills` only when the request carries a JSON content type
  (`:1714`).
- **Fix:** add the `isinstance(body, dict)` guard used by `invoke_skill` to the ten handlers, or
  move them onto a Pydantic model the way the sibling event routes already are.

### [ERROR-HANDLING] A malformed DTSTART in an uploaded .ics is answered with 500 instead of 400

- **Location:** `routes/calendar_routes.py:1421-1424` (the guarded parse) and `:1464` (the unguarded access)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the route wraps only `iCal.from_ical` in the 400 handler; `icalendar` does not raise
  there for a malformed `DTSTART` — it stores a broken property whose `.dt` raises on access, which
  the import loop reaches one line later:

  ```python
  try:
      cal_data = iCal.from_ical(content)
  except Exception as e:
      raise HTTPException(400, f"Invalid ICS file: {e}")      # :1421-1424
  ...
  src_dtstart = dtstart.dt                                     # :1464
  ```

  Measured through the real `POST /api/calendar/import` handler with a one-event file whose
  `DTSTART` is `not-a-date`:

  ```
  Failed to import ICS: Cannot access 'dt' on broken property 'DTSTART' (expected 'vDDDTypes'): Expected datetime, date, or time. Got: 'not-a-date'
  malformed DTSTART: import raised HTTPException: 500: Failed to import ICS in 0.03s
  ```

  The exception is logged at error level by the handler's own `logger.error("Failed to import
  ICS: %s", e)` (`:1556`) and the file is rejected — nothing is written — so this is a
  status-code and log-level defect, not a data defect.
- **Impact:** a user importing a file from a non-conforming exporter gets a 500 "Failed to import
  ICS" where the route's own intent (`Invalid ICS file`) is a 400, and every such upload adds an
  error-level traceback to the operator's log.
- **Fix:** move the `dtstart.dt` / `dtend.dt` accesses inside the same `try` that answers 400 (or
  catch `icalendar.error.BrokenCalendarProperty` alongside `ValueError`) so a bad property value
  is reported as a bad file.
