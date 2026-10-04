# tests: email, calendar and webhooks

## Overview

The 90 test files that pin the email, calendar/CalDAV, contacts/CardDAV, ICS, webhook and
web-fetch/search surfaces, plus the few that hang off them (`tests/test_diagnostics_*`,
`tests/test_ai_*`, `tests/test_calendar_*_js.py`).

The boundary: the product behaviour these files pin belongs to the `src-*` and `services-*`
sections, and the collection-time harness they run on (`tests/conftest.py`, `tests/helpers/`, the
`area_*` markers) belongs to `tests-harness`. This section judges only what each file can catch —
whether a test that names a defect would fail if that defect came back. Where the production defect
is already reported elsewhere, the finding here is the coverage gap and the defect is
cross-referenced rather than restated: `src-email-integrations.md:112` reports the CalDAV
rebinding window whose absence of a pinning test is the fourth finding below, and
`src-security.md:237` reports the default-off `block_private` policy that the third finding's stubs
hide.

## Coverage

Line numbers refer to `2992bf6d368a`; `git diff --stat 2992bf6d368a -- tests/` is empty, so the
working tree matches the reviewed commit for every path below.

**Read fully:** 89 of the 90 assigned paths, 12,342 lines.

**Read partially:** `tests/test_email_urgency_checkpoint.py`, the largest file in the set (1,328
lines). Read: the fake IMAP/DB harness at `:1-130` and two further regions (`:385-565`,
`:695-805`) — 420 lines covering 4 of its 20 test functions. The remaining 16 are the file's
fencing, generation and checkpoint-transition cases, which I did not read; no claim is made about
them. Everything I did read there is strong: `test_scan_keeps_registration_generation_when_cleanup_precedes_basis`
(`:702-797`) parks a thread inside the second account enumeration and asserts the cleanup pass
cannot become the stale scan's baseline, which is a real interleaving rather than a restatement of
the code.

**Not read:** none.

**Checks run.** Every assigned suite. The count below reproduces in the target tree, and every
mutation probe that follows ran in a throwaway copy at `/tmp/probe-repo` so the target stayed
untouched:

```
$ cd /home/lhl/github/lhl/odysseus
$ venv/bin/python -m pytest -q <the 90 assigned files>
492 passed, 80 warnings in 14.20s
```

Each finding below also quotes the mutation probe it rests on. Every probe ran in that same copy
and was reverted afterwards; `diff -rq --exclude=.git --exclude=venv --exclude=__pycache__` against
the target then showed no residual difference, and no path outside `audit/` is modified in the
target (`git status --porcelain | grep -v 'audit/'` is empty).

The pass rate is not the subject of this section — several of the strongest files in the set are
also the ones with the fewest tests. `tests/test_email_account_default_serialization.py:124-155`
parks a writer inside the account-mutation lock and asserts the contender blocks on the *database*
lock rather than an in-process one, and
`tests/test_calendar_default_transaction.py:215-320` does the same for the lazy default calendar;
`tests/test_email_test_connection_oauth.py:291-436` asserts the certificate check runs *before* the
OAuth token is loaded, in both IMAP and SMTP TLS modes.

### [BUG] The CalDAV prune regression is pinned against a copy of the query, not the query

- **Location:** `tests/test_caldav_sync_prune_local_events.py:39-50`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the module docstring states the fix "adds an `origin` column and gates the prune on
  `origin == "caldav"`", and that "this test replicates the exact prune query against an in-memory
  DB (the prune is pure DB logic; `_sync_blocking` itself needs a live CalDAV client)". The replica
  is `_prune` (`:39-50`), whose own docstring calls it "The exact prune filter from
  src/caldav_sync.py (post-fix)". The production filter (`src/caldav_sync.py:470-478`) has since
  grown two guards the copy does not have:

  ```python
  # src/caldav_sync.py:470-478
  stale = db.query(CalendarEvent).filter(
      CalendarEvent.calendar_id == local_cal.id,
      CalendarEvent.origin == "caldav",
      CalendarEvent.dtstart >= start,
      CalendarEvent.dtstart <= end,
      CalendarEvent.remote_href.isnot(None),
      CalendarEvent.caldav_sync_pending.is_(None),
      ~CalendarEvent.uid.in_(seen_uids) if seen_uids else CalendarEvent.uid.isnot(None),
  ).all()
  ```

  Deleting the `origin == "caldav"` line — precisely the regression the file exists to prevent,
  since a locally-created row carries a NULL origin and would be swept up — leaves it green:

  ```
  $ python3 -c "...drop 'CalendarEvent.origin == \"caldav\",' from src/caldav_sync.py..."
  occurrences: 1
  $ venv/bin/python -m pytest -q tests/test_caldav_sync_prune_local_events.py
  2 passed, 1 warning in 0.10s
  ```

  The same copy leaves `remote_href.isnot(None)` and `caldav_sync_pending.is_(None)` unpinned here;
  they are asserted only as source substrings in `tests/test_caldav_bidirectional_sync.py:38-40`.
- **Impact:** the silent data loss the file names (#2704 — agent-, email-triage- and
  failed-writeback-created events deleted from a synced calendar) can return with its regression
  suite still green, and a reader of this file reasonably concludes the invariant is covered.
- **Fix:** move the filter into a module-level helper in `src/caldav_sync.py` — the sibling
  `_should_prune_window` (`:257-268`) already shows the pattern, and
  `tests/test_caldav_prune_parse_failure.py:14-19` calls that one directly. Have `_prune` in the
  test call the helper with a real `Session` instead of rebuilding the `filter(...)` chain.

### [SECURITY] Every CalDAV test-connection test runs with the URL guard stubbed out

- **Location:** `tests/test_caldav_test_connection_ssl.py:74-81`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the suite's shared `_post_test` harness replaces the module the route imports
  lazily, so the pass-through stands in for the SSRF guard on every one of its four tests:

  ```python
  # tests/test_caldav_test_connection_ssl.py:74-81
  # Stub the caldav_sync module so the lazy `from src.caldav_sync import validate_caldav_url`
  # inside the route body resolves to a pass-through.
  caldav_sync_stub = MagicMock()
  caldav_sync_stub.validate_caldav_url = lambda u: u
  ...
  patch.dict(sys.modules, {"src.caldav_sync": caldav_sync_stub}),
  ```

  Neutering the real guard leaves the file green while the guard's own suite collapses:

  ```
  $ python3 -c "...replace validate_caldav_url's body with 'return raw_url'..."
  $ venv/bin/python -m pytest -q tests/test_caldav_test_connection_ssl.py
  4 passed, 1 warning in 0.13s
  $ venv/bin/python -m pytest -q tests/test_caldav_url_hardening.py
  17 failed, 1 passed, 1 warning in 0.10s
  ```

  The route's own call to the guard is pinned only by a source substring —
  `tests/test_caldav_url_hardening.py:171-177` asserts
  `"validate_caldav_url(body.get(\"url\", \"\"))" in text` — so the wiring from the endpoint a
  signed-in user reaches when adding an account is asserted nowhere in behavioural form.
- **Impact:** a change that drops, reorders or short-circuits the `validate_caldav_url` call in
  `POST /api/calendar/test` passes every test that covers that route, while the guard itself stays
  fully green. The gap is invisible to the two suites that look closest to it.
- **Fix:** narrow the stub to the network layer — patch `httpx.AsyncClient` only, monkeypatch
  `_resolve_caldav_host_ips` to a public address (as `tests/test_caldav_url_hardening.py:108-112`
  does), and let the real guard run. Then add one case that posts a loopback or
  `169.254.169.254` URL and asserts no client is constructed, matching what
  `tests/test_email_test_connection_oauth.py:256-289` already does for the inline-OAuth variant of
  the same route.

### [SECURITY] The CardDAV security suite stubs the outbound-URL guard in all four tests

- **Location:** `tests/test_contacts_carddav_security.py:8-16`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** every test in the file replaces `check_outbound_url` with a lambda that returns a
  hand-written verdict — `:8-16` (metadata target), `:19-27` (non-string), `:30-45` (`_abs_url`),
  `:48-66` (`_vcard_url`). The production wrapper under test does nothing except call that guard and
  raise its reason:

  ```python
  # routes/contacts/contacts_routes.py:66-74
  def _validate_carddav_url(url: str) -> str:
      cleaned = (url if isinstance(url, str) else "").strip().rstrip("/")
      ok, reason = check_outbound_url(
          cleaned,
          block_private=os.getenv("CARDDAV_BLOCK_PRIVATE_IPS", "false").lower() == "true",
      )
      if not ok:
          raise ValueError(f"Rejected CardDAV URL: {reason}")
      return cleaned
  ```

  With the real guard neutered (`return (True, "")`) the suite still passes, while the guard's own
  suite fails ten tests:

  ```
  $ python3 -c "...insert 'return (True, \"\")' as the first statement of check_outbound_url..."
  $ venv/bin/python -m pytest -q tests/test_contacts_carddav_security.py
  4 passed, 1 warning in 0.06s
  $ venv/bin/python -m pytest -q tests/test_url_safety.py
  10 failed, 3 passed, 1 warning in 0.09s
  ```

  The stubs are also gratuitous: the real guard returns the exact strings the lambdas fabricate, so
  the two tests that assert on the reason text pass unchanged without them.

  ```
  $ venv/bin/python -c "from src.url_safety import check_outbound_url as c; \
      print(c('http://169.254.169.254/latest/meta-data')); print(c(''))"
  (False, 'link-local address blocked (SSRF metadata risk): 169.254.169.254')
  (False, 'URL is required')

  $ venv/bin/python -m pytest -q tests/_probe_carddav_unstubbed.py   # a scratch copy of the
  # same two tests with the stub removed, since deleted
  2 passed, 2 warnings in 0.05s
  ```
- **Impact:** the file's name and docstring present it as the CardDAV SSRF coverage, but a change
  that makes `_validate_carddav_url` call the guard with the wrong argument, or drop the call
  entirely, is not caught here. `test_vcard_url_validates_base_and_quotes_uid:66` additionally pins
  `block_private=False` as the expected call, so the file would fail if a fix passed `True` — see
  `src-security.md:237` for that policy itself.
- **Fix:** drop the `check_outbound_url` stubs; the metadata and non-string cases pass against the
  real guard as shown above. Keep the `_get_carddav_config` stub, which is what isolates the
  address-pinning behaviour, and keep the `seen` assertion only after confirming it reflects the
  intended `CARDDAV_BLOCK_PRIVATE_IPS` default.

### [SECURITY] Nothing exercises the CalDAV guard-to-connect pair, so the rebinding window has no test to fail on

- **Location:** `tests/test_caldav_url_hardening.py:95-112`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the closest test in the set resolves a mixed answer set and asserts the guard
  raises:

  ```python
  # tests/test_caldav_url_hardening.py:104-112
  def test_validate_caldav_url_blocks_mixed_dns_in_any_order(monkeypatch, addrs):
      # A host that resolves to BOTH a public and an internal address must be
      # rejected regardless of record order — every resolved address is checked,
      # so one internal answer is enough to block. Defends DNS round-robin and a
      # rebind that slips an internal A-record alongside a public one.
  ```

  That is one `_resolve_caldav_host_ips` call, one guard verdict. The defect
  `src-email-integrations.md:112-165` measures is a *second* resolution inside the client, which no
  test in this set reaches: `_resolve_caldav_host_ips` is referenced only by
  `tests/test_caldav_url_hardening.py` and `tests/test_caldav_url_nonstring.py`, and the sync and
  test-connection suites either stub the guard (`tests/test_caldav_test_connection_ssl.py:74-81`) or
  a fake client. The comment above therefore reads as coverage of the rebinding shape that the
  assertion does not provide.
- **Impact:** a fix that pins the TCP connect to the address the guard approved — the shape
  `src/webhook_manager.py:130-160` uses — would have no test in this section that fails without it,
  and a partial fix that only tightens the guard's address list would look equally green. Since
  `_build_dav_client` (`src/caldav_sync.py:231-254`) already documents and closes the *redirect*
  route into internal space, a reader can reasonably conclude this window is closed too.
- **Fix:** add an end-to-end test in the shape of `tests/test_webhook_dns_rebinding_pin.py:71-156`
  — a resolver that answers the validating lookup publicly and every later lookup with `127.0.0.1`,
  plus a loopback HTTP sink, asserting the sink receives no request and no stored credential.

### [BUG] The ICS export suite serializes with a copy of the exporter

- **Location:** `tests/test_ics_export_escaping.py:25-52`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_export` imports the real `_ics_escape` (`:27`) but rebuilds the rest of the
  serializer line by line, including the two behaviours the file's assertions rest on:

  ```python
  # tests/test_ics_export_escaping.py:43-45
  _dt_suffix = "Z" if getattr(ev, "is_utc", False) else ""
  lines.append(f"DTSTART:{ev.dtstart.strftime('%Y%m%dT%H%M%S')}{_dt_suffix}")
  lines.append(f"DTEND:{ev.dtend.strftime('%Y%m%dT%H%M%S')}{_dt_suffix}")
  ```

  The production copy of those lines is `routes/calendar_routes.py:1575-1599`. Removing the
  `_dt_suffix` logic from the exporter leaves the seven tests green, because they serialize with
  the test's own copy:

  ```
  $ python3 -c "...set _dt_suffix = \"\" in routes/calendar_routes.py..."
  1589:                    _dt_suffix = ""  # probe: UTC marker dropped from export
  $ venv/bin/python -m pytest -q tests/test_ics_export_escaping.py
  7 passed, 1 warning in 0.07s
  ```

  The copy has already drifted from the product: production appends
  `if ev.rrule: lines.append(f"RRULE:{ev.rrule}")` (`routes/calendar_routes.py:1596-1597`) and the
  test's version has no such line, so no export test covers RRULE at all.
- **Impact:** `test_utc_event_gets_z_suffix` and `test_non_utc_event_no_z_suffix` — the two
  assertions the file exists for — cannot fail when the export path they name regresses. A dropped
  `Z` suffix silently shifts every exported timed event by the viewer's UTC offset.
- **Fix:** drive the export route (`routes/calendar_routes.py:1561-1600`) with a seeded
  `CalendarEvent` and assert on its response body, or extract the per-event serialization into a
  helper both the route and the test call. Either removes the second copy; the RRULE field then
  comes along with it.

### [BUG] The ICS re-import dedup tests never touch the storage conversion they claim to match

- **Location:** `tests/test_ics_import_dedup_tz.py:39-43`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the docstring says "The shared `_ics_naive_dtstart` helper now drives both", but
  the storage side is a separate inline expression (`routes/calendar_routes.py:1512`), and the one
  test that claims to tie the two together restates it rather than calling it:

  ```python
  # tests/test_ics_import_dedup_tz.py:39-43
  def test_dedup_key_equals_storage_conversion():
      dt_val = datetime(2026, 11, 1, 9, 30, tzinfo=zi.ZoneInfo("America/New_York"))
      stored = dt_val.astimezone(timezone.utc).replace(tzinfo=None)
      assert _ics_naive_dtstart(dt_val) == stored
  ```

  `stored` is the test's own arithmetic. Reverting the storage conversion to exactly the bug the
  docstring describes leaves all five tests green:

  ```
  $ python3 -c "...replace 'dt_val.astimezone(_tz.utc).replace(tzinfo=None)' at
      routes/calendar_routes.py:1512 with 'dt_val.replace(tzinfo=None)'..."
  storage site found: 1
  $ venv/bin/python -m pytest -q tests/test_ics_import_dedup_tz.py
  5 passed, 1 warning in 0.07s
  ```

  No test in the set drives `import_ics` with a TZID event: `TZID` appears in this file only, and
  the only other file that mentions the import route
  (`tests/test_calendar_import_zero_duration.py`) uses all-day `DATE` values.
- **Impact:** the duplicate-event regression returns in full — a TZID event re-imported on every
  sync — with the suite that names it still passing. `tests/test_calendar_import_zero_duration.py`
  shows the route is drivable in-process, so the gap is not an import constraint.
- **Fix:** post an ICS body with `DTSTART;TZID=America/New_York:20261101T093000` to the import
  route twice and assert one `CalendarEvent` row whose `dtstart` is `2026-11-01 14:30` (EST), then
  replace `test_dedup_key_equals_storage_conversion` with an assertion that the imported row's
  stored value equals `_ics_naive_dtstart(...)` for the same input.

### [BUG] The web_search icon test renders a hand-written copy of chat.js

- **Location:** `tests/test_web_search_tool_icon_js.py:22-60`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_CHECK_JS` is a string literal in the test file holding an invented rendering
  stack — `_searchIcon`, a two-entry `_toolLabels`, `renderIcon`, `renderLabel` and
  `renderThreadHTML` — and `_run` passes it to `node` on stdin. The file never reads
  `static/js/chat.js`: `_REPO` (`:19`) is used only as node's `cwd`, and `grep -c chat.js` on the
  file returns 0. The functions under test do not exist in the product:

  ```
  $ grep -rn "renderThreadHTML\|function renderIcon\|function renderLabel" static/js/
  (no output)
  ```

  The production code is an inline map plus one template literal at
  `static/js/chat.js:2254-2279` and `:3552-3556`, with twenty-one `_toolLabels` entries where the
  test's copy has two. Replacing the production icon with a placeholder and deleting its
  registration leaves all six tests green:

  ```
  $ python3 -c "...set _searchIcon = 'PROBE-ICON-REMOVED' and delete the
      web_search entry from _toolIcons in static/js/chat.js..."
  2254:      const _searchIcon = 'PROBE-ICON-REMOVED';
  $ venv/bin/python -m pytest -q tests/test_web_search_tool_icon_js.py
  6 passed, 1 warning in 0.19s
  ```
- **Impact:** the file reports coverage of "the web_search tool-icon rendering in the agent thread"
  while asserting only that its own copy behaves as written. Every other JS harness in this set
  loads the real file — `tests/test_calendar_css_url_escape_js.py:24-26,44` imports
  `static/js/calendar/utils.js` by absolute path, `tests/test_email_open_dedup_js.py:12-24` slices
  the real function body out of `emailLibrary.js` — so this one is also inconsistent with its
  neighbours.
- **Fix:** extract the real `_toolLabels`/`_toolIcons` block and the thread-node template literal
  from `static/js/chat.js` (slice by `source.index(...)` as `tests/test_email_open_dedup_js.py`
  does), feed those into the node harness, and assert the rendered icon and label come from them.
  Then `test_default_tool_icon_is_triangle` and `test_unknown_tool_case_insensitive_matches_icons`
  test the product's twenty-one-entry map instead of the copy's two.

### [BUG] The email-to-calendar owner-scope tests assert on source text, and nothing drives the filter

- **Location:** `tests/test_ai_interaction_owner_scope.py:13-31`
- **Severity:** low
- **Disposition:** next
- **Evidence:** two of the file's four tests read a function's source with `inspect.getsource` and
  assert on substrings:

  ```python
  # tests/test_ai_interaction_owner_scope.py:13-18
  def test_model_resolver_applies_owner_filter():
      body = _source(ai_interaction._resolve_model)

      assert "owner: Optional[str] = None" in body
      assert "from src.auth_helpers import owner_filter" in body
      assert "owner_filter(query, ModelEndpoint, owner)" in body
  ```

  Turning the real `src/auth_helpers.owner_filter` into a pass-through — which is the failure the
  file exists to prevent, and which every other suite in the tree would then be exposed to — leaves
  it green while the sibling scope suite fails:

  ```
  $ python3 -c "...replace owner_filter's body with 'return query'..."
  $ venv/bin/python -m pytest -q tests/test_ai_interaction_owner_scope.py
  4 passed, 1 warning in 0.07s
  $ venv/bin/python -m pytest -q tests/test_gallery_image_endpoint_owner_scope.py
  2 failed, 3 passed, 1 warning in 0.08s
  ```
- **Impact:** `_resolve_model` and `do_generate_image` are the model-selection entry points every
  other suite stubs, so a query that stops being owner-scoped here leaks another user's endpoint
  configuration and headers — and the only test naming that invariant would not notice.
- **Fix:** the sibling file shows the shape: seed two owners' `ModelEndpoint` rows in a temp SQLite
  session and assert `_resolve_model(..., owner="alice")` cannot return bob's row. Keep the
  `asyncio.to_thread(_resolve_model, ..., owner=owner)` substring assertion (`:28-31`) if the
  threading contract needs pinning, but pair it with a behavioural case.

### [BUG] The webhook trigger token check is pinned by a substring, on a premise that does not hold

- **Location:** `tests/test_webhook_trigger_auth_exempt.py:80-96`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the file's first test pulls the `AUTH_EXEMPT_PATTERNS` regex literals out of
  `app.py` and applies them to a representative path, so it does exercise the real patterns; the
  second reads `routes/task/task_routes.py` as text and asserts two substrings, explaining that it
  "Read[s] the source directly — importing task_routes pulls in SQLAlchemy and fails under the
  conftest stubs". That premise is false: the module imports inside the test process, and a sibling
  suite already drives the very endpoint:

  ```
  $ venv/bin/python -m pytest -q -s tests/_probe_import_check.py
  IMPORT OK: /tmp/probe-repo/routes/task/task_routes.py
  1 passed, 2 warnings in 0.06s

  $ grep -n 'webhook/{token}' tests/test_task_cookbook_admin_gate.py
  241:    webhook_trigger = _endpoint("POST", "/api/tasks/{task_id}/webhook/{token}")
  ```

  (The same test calls that endpoint with the seeded task's correct token at `:244`, then asserts
  the 403 a different gate produces.)

  Blocking the module for a whole run leaves this file passing while the suites that actually use
  it fail:

  ```
  $ PROBE_BLOCK_MODULES=routes.task.task_routes venv/bin/python -m pytest -q -p blockmod \
      tests/test_webhook_trigger_auth_exempt.py
  2 passed, 1 warning in 0.06s
  $ PROBE_BLOCK_MODULES=routes.task.task_routes venv/bin/python -m pytest -q -p blockmod \
      tests/test_task_routes_shim.py tests/test_task_cookbook_admin_gate.py
  !!! Interrupted: 2 errors during collection !!!
  ```

  The 404-on-token-mismatch branch itself (`routes/task/task_routes.py:1045-1056`) has no test: the
  sibling call at `tests/test_task_cookbook_admin_gate.py:231-250` passes the *correct* token and
  asserts the 403 that a different gate produces.
- **Impact:** this test is the stated justification for the endpoint's auth exemption, and a
  refactor that compares the token against the wrong row or returns the task on mismatch would keep
  it green. The endpoint is reachable without a session, so the blast radius is any task whose
  token leaks.
- **Fix:** replace the grep with a seeded `ScheduledTask` and a call to the real endpoint with a
  wrong token, asserting `HTTPException(404)` and that the task did not run — the fixture
  `tests/test_task_cookbook_admin_gate.py:112-140` already builds the row.

### [BUG] Two "no offenders" guards pass when the code they guard is deleted

- **Location:** `tests/test_webhook_emitters_use_manager.py:44-54`, `tests/test_web_user_agent_constant.py:12-18`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** both files are negative scans over source text. The webhook guard looks for
  `asyncio.create_task(webhook_manager.fire(...))` by AST shape; redirecting all four real emitter
  call sites — `routes/chat_helpers.py:423,1256`, `routes/session_routes.py:482`,
  `routes/webhook/webhook_routes.py:388` — to an undefined name (a `NameError` at runtime, and no
  webhook ever delivered) leaves it green:

  ```
  $ grep -rn "fire_and_forget" routes/ --include=*.py   # after the probe
  (no output)
  $ venv/bin/python -m pytest -q tests/test_webhook_emitters_use_manager.py
  1 passed, 1 warning in 0.29s
  ```

  The User-Agent guard scans `services/search/**/*.py` for the literal `Mozilla/`. Re-inlining a
  stale UA as two adjacent literals — which Python concatenates at compile time, so the wire value
  is identical — passes, while the same string written normally fails:

  ```
  $ # services/search/providers.py:141,253,392 -> "Mozilla" "/5.0 (stale inlined UA)"
  $ venv/bin/python -m pytest -q tests/test_web_user_agent_constant.py
  1 passed, 1 warning in 0.05s
  $ # same value spelled "Mozilla/5.0 (stale inlined UA)"
  $ venv/bin/python -m pytest -q tests/test_web_user_agent_constant.py
  1 failed, 1 warning in 0.07s
  ```
- **Impact:** both guards are the only thing standing between a copy-pasted regression and the
  tree, and each is defeated by a spelling rather than by a behaviour change. The webhook case is
  the more consequential: the guard's own docstring explains that an untracked fire task can be
  garbage-collected before it sends, so the silent-drop failure it names is exactly what its
  probe-state allows.
- **Fix:** for the webhook guard, assert positively that each of the four call sites routes through
  `webhook_manager.fire_and_forget` (a fixed allowlist of `(file, line)` pairs, or an AST walk that
  collects every call whose callee name ends in `fire`), so removing one is a failure rather than
  an empty offender list. For the UA guard, stub the transport and assert the outgoing
  `User-Agent` is the constant — `tests/test_web_fetch_size_caps.py:175-186` captures the outgoing
  headers the same way for `Accept-Encoding` — or normalise adjacent literals before scanning.

### [BUG] The CalDAV bidirectional-sync suite is mostly source-substring assertions

- **Location:** `tests/test_caldav_bidirectional_sync.py:35-82`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** four of the file's six tests read a production file and assert that specific lines
  are present:

  ```python
  # tests/test_caldav_bidirectional_sync.py:35-40
  def test_caldav_pull_prune_skips_unsynced_or_pending_local_rows():
      source = Path("src/caldav_sync.py").read_text()
      assert 'existing.caldav_sync_pending in {"create", "update"}' in source
      assert "CalendarEvent.remote_href.isnot(None)" in source
      assert "CalendarEvent.caldav_sync_pending.is_(None)" in source
  ```

  With `routes/calendar_routes.py` unimportable for a whole run the file still passes, while the
  sibling suite that drives those routes fails six tests:

  ```
  $ PROBE_BLOCK_MODULES=routes.calendar_routes venv/bin/python -m pytest -q -p blockmod \
      tests/test_caldav_bidirectional_sync.py
  6 passed, 2 warnings in 0.15s
  $ PROBE_BLOCK_MODULES=routes.calendar_routes venv/bin/python -m pytest -q -p blockmod \
      tests/test_calendar_owner_scope.py
  6 failed, 1 passed, 1 warning in 0.10s
  ```

  Its tombstone test (`:85-169`) also builds the tombstone itself and then asserts the retry cleans
  it up, so the writer under test — `_record_caldav_delete_tombstone` — is stubbed out of its own
  regression. The four reads also use CWD-relative paths (`:36,44,56,68`); that pattern is already
  reported for six other files in `tests-session-chat-memory.md:414`.
- **Impact:** the file's four push-path tests cannot distinguish "the push is wired" from "the
  string is still in the file", so a change that keeps the call sites but breaks the pending-state
  bookkeeping passes. The related `tests/test_caldav_sync_uid_scope.py:57-66`
  (`test_alice_event_is_not_moved`) is vacuous in the same way — it calls only the read-only
  `_find_existing_event` and then asserts `ev.calendar_id == "calA"`, which nothing in the test can
  change.
- **Fix:** for the push path, seed a local calendar and event, call the write route with a fake
  client, and assert the pending marker and the recorded call; for the tombstone, let the real
  `_record_caldav_delete_tombstone` write the row. Drop or rewrite
  `test_alice_event_is_not_moved` to run the sync's lookup-and-move decision against a seeded
  second calendar.

### [BUG] The email front-end regressions are pinned by source substrings and a call-site count

- **Location:** `tests/test_email_library_bulk_actions.py:49-75`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** all three tests slice `static/js/emailLibrary.js` as text and assert substrings;
  the third closes with a count rather than a behaviour:

  ```python
  # tests/test_email_library_bulk_actions.py:73-75
  assert "state._libAccountId = btn.dataset.accId || null;" in text
  assert text.count("_loadEmailsFresh();") >= 5
  assert "state._libSearchDraft = input.value;" in text
  ```

  The two sibling files that cover the same change in `static/js/settings.js` are the same shape:
  `tests/test_email_oauth_connect_smtp_security.py:10-14` and
  `tests/test_email_oauth_settings_redirect.py:9-19` slice the real handler body and assert that
  strings appear in it. The slices are honest — they are cut out of the production file, not
  re-typed — but the assertions are still presence checks, so a handler that reads
  `el('eaf-smtp-security').value` and then discards it passes.
- **Impact:** the selection-state invariant ("IMAP UIDs are folder/account scoped, so stale bulk
  selections must die") is asserted by counting one function call in the file. A context-change
  path that resets state without rerendering, or a sixth call site added in a place that never
  fires, keeps the count and the test green.
- **Fix:** drive the real functions in the node harness the set already uses
  (`tests/test_email_open_dedup_js.py:11-24` shows how to load and slice
  `emailLibrary.js`): seed `state._selectedUids`, invoke the folder/account/filter change, and
  assert the selection is empty and the bulk bar hidden. For the settings pair, keep the slice but
  assert on the object the handler builds rather than the property reads inside it.
