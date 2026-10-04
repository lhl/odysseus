# src: email, calendar and integrations

## Overview

The outbound integration layer. `src/caldav_sync.py` pulls a remote CalDAV server into the local
`CalendarCal`/`CalendarEvent` tables and retries the pending local→remote pushes;
`src/caldav_writeback.py` performs one create, update or delete against the remote calendar;
`src/email_thread_parser.py` splits an email body (HTML or plaintext) into quoted reply turns;
`src/integrations.py` owns the registered HTTP integrations, their stored credential, and the
`api_call` execution path; `src/webhook_manager.py` validates a webhook target and fires the
outgoing POSTs; `src/youtube_handler.py` is the compatibility alias that resolves to
`services.youtube.youtube_handler`.

The boundary: the CalDAV account configuration, the sync endpoint and the write-back triggers are
`routes-skills-calendar-task` (`routes/calendar_routes.py`); the read path that calls the thread
parser is `routes-email` (`routes/email_routes.py`); webhook registration is
`routes-rest-integrations-misc` (`routes/webhook/webhook_routes.py`); integration CRUD is
`routes-rest-auth-admin` (`routes/auth_routes.py`); the per-user preferences file the CalDAV
accounts live in is `routes-rest-media-files` (`routes/prefs_routes.py`); the Fernet key store,
`src/url_safety.py` and `src/api_key_manager.py` are `src-security`; `CalendarEvent` is
`core-data-platform`; the `api_call` tool wrapper and dispatcher are `src-agent-tools` and
`src-tools-parse-exec`; the canonical YouTube module is `services-media`. This section covers what
these six modules do with a caller-supplied URL, a stored credential and an untrusted body — not
whether the routes that call them are gated correctly.

## Coverage

Citations refer to the working tree at `2992bf6d368a`; `git status --porcelain` showed only the
untracked `audit/` directory.

**Read fully:** all six assigned files (2,935 lines) — the 6 items listed below. Also read fully for
the credential-storage and outbound-URL claims: `src/secret_storage.py` (87), `src/url_safety.py`
(108) and `routes/prefs_routes.py` (125, the per-user store the CalDAV accounts live in).

- `src/integrations.py` (810)
- `src/caldav_sync.py` (722)
- `src/email_thread_parser.py` (614)
- `src/webhook_manager.py` (455)
- `src/caldav_writeback.py` (311)
- `src/youtube_handler.py` (23)

**Read partially:** the boundary code and callers this section's claims rest on:

- `routes/calendar_routes.py` at `_require_user` (`:69-80`), the CalDAV config and account CRUD
  (`:819-995`), `_push_caldav_event_after_commit` (`:151-179`), `_record_caldav_delete_tombstone`
  (`:181-198`), the test-connection route (`:995-1085`) and `/sync` (`:1086-1093`)
- `routes/email_routes.py` at the read path's parser call (`:3117-3128`) and the `asyncio.to_thread`
  that runs it (`:3216`)
- `routes/webhook/webhook_routes.py` at the webhook CRUD and test routes (`:64-160`)
- `routes/auth_routes.py` at the integration CRUD (`:759-917`)
- `core/database.py` at `CalendarEvent` (`:1856-1888`)
- `src/settings.py` at `save_settings` (`:250-254`)
- `src/api_key_manager.py` at `get_or_create_key` / `encrypt_api_key` / `decrypt_api_key` (`:17-51`)
- `src/tools/system.py` at `do_api_call` (`:496-524`)
- `src/tool_capabilities.py` at the `api_call`/`app_api` registration (`:247-261`) and
  `tool_result_should_arm_gate` (`:505-547`)
- `src/task_scheduler.py` at the retired-action set (`:265-269`) and the integrations caller
  (`:1398-1420`)
- `services/youtube/youtube_handler.py` (`:1-60`), `services/youtube/__init__.py`,
  `services/__init__.py` and `src/chat_handler.py:19-26` for the alias check
- `static/js/emailLibrary.js` at the two `thread_turns` render sites (`:5769-5771`, `:6188-6216`)
  and the `_sanitizeHtml` calls that feed them (`:5826-5847`)
- `static/js/settings.js` at the integration auth-type select (`:3160-3187`). Of the module's own
  tests: `tests/test_caldav_sync_uid_scope.py`, `tests/test_caldav_redirect_hardening.py`,
  `tests/test_integrations_url_join.py` and `tests/test_webhook_ssrf_resilience.py` fully
- `tests/test_integrations_store_shape.py` at its first cases

**Not read:** the rest of every caller file named above:

- `routes/email_routes.py` (~6,100 further lines), `routes/calendar_routes.py`,
  `routes/auth_routes.py` and `routes/webhook/webhook_routes.py` outside the regions cited
- `src/task_scheduler.py` outside its two cited regions
- `src/agent_loop.py` beyond the integrations-prompt call (`:2733-2743`)
- `src/tool_execution.py` beyond the `api_call` dispatch (`:1178`)
- `core/database.py` beyond `CalendarEvent`
- `services/youtube/youtube_handler.py` beyond `:60`
- the IMAP/SMTP code that produces the email bodies, the email front end beyond the sanitizer sites,
  and the `caldav` and `httpx` library internals beyond the behavior the probes exercised
- `mcp_servers/`

The other sections' findings were read only where a cross-reference is named.

**Checks run:**

- the 32 suites matching `ls tests | grep -iE
  'caldav|integrations|webhook|youtube|email_thread|carddav'` — `venv/bin/python -m pytest -q -p
  no:cacheprovider <32 files>` from the repository root → **163 passed** in 4.59s, 7 warnings (the
  `datetime.utcnow()` deprecations at `src/caldav_sync.py:309-310` and one at
  `tests/test_caldav_google_principal_url.py:45`). Thirteen throwaway probe scripts under `/tmp`,
  outside the target tree. The ones the findings quote: the CalDAV DNS-flip probe (three runs; two
  quoted below), the VEVENT-UID collision probe (three runs, including one with a non-colliding
  second event), the parser probes (four runs: a nesting-depth sweep, a sibling-count sweep, a
  deep-chain run, and a smoke set of six real-world bodies), and the webhook guard probe (two runs,
  comparing the accepted address list with `src/url_safety._classify`). The last is the `api_call`
  path-join probe recorded under the dropped hypotheses. Also the greps each finding records: the
  `parse_thread` caller set, the `turns_json` writer set, the `validate_webhook_url` /
  `_is_private_url` callers, the `_join_integration_url` / `mask_integration_secret` /
  `load_integrations` callers, the `set_loop` / `fire_and_forget` callers, the `untrusted_content`
  consumers, `uvicorn.run`'s worker count, and `_find_integration` / `_stable_cal_id` call sites.
  Four hypotheses were checked and dropped rather than reported: a `//host` path cannot move the
  `api_call` request to another host (`_join_integration_url` strips every leading slash before
  `urljoin`, measured)
- the parser's turn HTML is not a new XSS surface (the client runs `body_html` through
  `_sanitizeHtml`)
- the integration store's read-modify-write has no interleaving caller (every writer is an `async`
  handler whose load-and-save block contains no await, and `app.py:1306` launches uvicorn with no
  worker count)
- a missing `untrusted_content` flag on a successful `api_call` does not arm the gate less than a
  failure (the tool is registered `ResultIntegrity.EXTERNAL_UNTRUSTED` at
  `src/tool_capabilities.py:247-261`, which `tool_result_should_arm_gate` consults for both)

### [SECURITY] The CalDAV host guard resolves once, so a rebinding DNS answer reaches loopback with the stored credentials

- **Location:** `src/caldav_sync.py:90-103` (`_validate_caldav_hostname`), `:231-253` (`_build_dav_client`), with the validate-then-connect pair at `:644-645`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the guard resolves the host and vets every address, and the client then resolves it
  again independently at connect time. Nothing pins the socket to the address that passed:

  ```python
  def _validate_caldav_hostname(host: str) -> None:
      ...
      try:
          addrs = _resolve_caldav_host_ips(host)
      except OSError:
          raise ValueError("CalDAV URL host does not resolve")
      if not addrs:
          raise ValueError("CalDAV URL host does not resolve")
      for addr in addrs:
          _validate_caldav_address(addr)
  ```

  `_build_dav_client` closes the *redirect* route into internal space
  (`client.session.max_redirects = 0`) and its docstring says so; it does not close this one.
  `sync_caldav` validates and syncs back to back, so the window is one request:

  ```python
  url = validate_caldav_url(url)
  result = await asyncio.to_thread(_sync_blocking, owner, url, user, pw, account_id)
  ```

  The two sibling outbound paths in this section close exactly this TOCTOU by pinning the connect
  to the IP the guard returned — `src/webhook_manager.py:130-160` (`_validated_public_ips`, whose
  docstring names the rebinding window) and `src/integrations.py:565-584` (the recording resolver,
  whose comment names the same window) — and `tests/test_webhook_dns_rebinding_pin.py` pins it for
  webhooks. `src/caldav_writeback.py:295-301` has the same unpinned shape.

  Measured with a probe that answers the validating lookup with a public address and every later
  lookup with `127.0.0.1`, against a loopback HTTP server standing in for an internal service:

  ```
  validate_caldav_url -> http://rebind.example:59455/dav | resolver calls: 1
  sink hits: [('PROPFIND', '/dav', None),
              ('PROPFIND', '/dav', 'Basic <base64 of the configured username:password>')]
  ```

  The first PROPFIND is unauthenticated; the sink answered it with
  `401 WWW-Authenticate: Basic realm="internal"` and the retry carried the account's Basic
  credential (a synthetic one in the probe). Through `_sync_blocking` on the same flip, the sink
  received two PROPFINDs and the sync reported the failure its own body produced
  (`'NoneType' object has no attribute 'tag'`), confirming the response that was parsed came from
  loopback.
- **Impact:** any signed-in user may add a CalDAV account (`routes/calendar_routes.py:914-941`,
  `_require_user` at `:69-80`) and trigger the sync (`POST /api/calendar/sync`, `:1086-1093`). A
  user who points an account at a hostname whose DNS answer they control can therefore make the
  server issue CalDAV requests — PROPFIND/REPORT on the pull, PUT/DELETE on the write-back — to
  loopback, link-local or RFC-1918 addresses, which is exactly what `_validate_caldav_address`
  exists to refuse, and hand the stored CalDAV username and password to an internal service that
  challenges with 401. The response is parsed by the CalDAV client rather than returned to the
  caller, so the attacker's view is blind; the reachability requirement is a DNS record that
  answers differently on two lookups milliseconds apart.
- **Fix:** pin the connect to the IP `_validate_caldav_hostname` returned, the way
  `_validated_public_ips` + `_PinnedAsyncTransport` do for webhooks and `api_call`. The `caldav`
  client uses a `requests` session, so this means mounting an adapter that connects to that
  address while preserving the `Host` header and TLS SNI, and re-validating when the pinned
  address is refused. A per-URL session is the cost.
- **Re-review (2026-10-04):** lowered from medium. Three things have to hold: a signed-in user who is hostile, a DNS record
  that user controls answering differently on two lookups milliseconds apart, and an internal
  service worth reaching blind, since the response is parsed by the CalDAV client and not returned.
  The credentials sent to the internal address are the attacker's own account's.


### [BUG] A VEVENT UID that another calendar already holds discards that calendar's whole pull, while the counts still report it as synced

- **Location:** `src/caldav_sync.py:418`, `:437-455`, `:483-486`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the per-calendar loop adds a row for every UID the calendar does not already hold
  and commits the batch once. `CalendarEvent.uid` is the global primary key
  (`core/database.py:1860`), so a UID that another calendar holds raises at that commit, and the
  handler for the calendar rolls the entire unit of work back:

  ```python
  existing = _find_existing_event(db, pending, uid_val, local_cal.id)
  ...
  new_ev = CalendarEvent(uid=uid_val, calendar_id=local_cal.id, ...)
  db.add(new_ev)
  pending[uid_val] = new_ev
  result["events"] += 1
  db.commit()
  ...
  except Exception as e:
      logger.exception("CalDAV sync failed for one calendar")
      result["errors"].append(str(e)[:200])
      db.rollback()
  ```

  The containment is deliberate — `_find_existing_event`'s docstring
  (`src/caldav_sync.py:166-177`) says "a genuine
  cross-user uid collision then fails the PK insert inside the per-calendar try/except instead of
  hijacking the row" — but its granularity is the calendar, not the event, and
  `result["events"] += 1` has already counted the rows the rollback discards.

  Measured through the real `_sync_blocking` with a fake DAV client returning two events, a
  temporary database, and `core.database.SessionLocal` pointed at it. The trigger is the one that
  docstring names: the same remote calendar syncing under a second local calendar (here the
  account is deleted and re-added, which mints a new account id and therefore a new calendar id
  from `_stable_cal_id`, `src/caldav_sync.py:143-151`):

  ```
  first sync  : {'calendars': 1, 'events': 2, 'deleted': 0} errors: 0
  re-added    : {'calendars': 1, 'events': 2, 'deleted': 0} errors: ['(sqlite3.IntegrityError) UNIQUE constraint failed: cale']
  retry again : {'calendars': 1, 'events': 2, 'deleted': 0} errors: ['(sqlite3.IntegrityError) UNIQUE constraint failed: cale']
  calendar caldav-d8d60e1fce6e30622a0b6 name='Shared' events=2
  calendar caldav-8600239d70b7cfc40de1f1 name='Shared' events=0
  ```

  The second event in that pull has a UID no other row holds (`ev2@svc`); it is rolled back with
  the colliding one, so the loss is not limited to the colliding event.
- **Impact:** the affected calendar never syncs again. Its `CalendarCal` row is created and stays
  empty, every sync attempt ends with the same `IntegrityError` in the result the UI shows, and no
  remote event from that calendar is ever visible locally. The two ways in are a shared or
  subscribed calendar on the same server reaching two owners (or two accounts of one owner, the
  case `_stable_cal_id`'s account scoping was added for), and deleting then re-adding an account
  so the new calendar row re-fetches events whose UIDs the old row still owns. Locally created
  events are not a trigger: the ICS import mints a fresh uuid per event
  (`routes/calendar_routes.py:1449-1454`).
- **Fix:** contain the collision at the event, not the calendar — insert each new row inside a
  `db.begin_nested()` SAVEPOINT (or pre-check for a UID owned by another calendar) so only the
  colliding event is skipped, and record it as a per-event error. Increment `result["events"]`
  only for rows that survive the commit.

### [PERF] The HTML thread parser re-walks each subtree at every nesting level, so a crafted email body occupies a worker thread for ~20 seconds

- **Location:** `src/email_thread_parser.py:535-548` (`_walk`, with the same shape in `_walk_with_meta` at `:578-591`), `:451-463`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** at every level the walk asks BeautifulSoup for the node's whole subtree and filters
  it, then does the same for each child:

  ```python
  nested = [t for t in node.find_all(True, recursive=True) if _is_quote_container(t)]
  ...
  direct_nested = [n for n in nested if not has_quote_between(n, node)]
  ```

  so the work is (nodes × nesting depth), and the top-level pass adds an ancestor walk per
  candidate (`tops = [t for t in all_quotes if not has_quote_ancestor(t)]`). The only bound is the
  200,000-character input cap at `:437`. Measured, with the sibling count fixed and the nesting
  depth varied, then at the worst case that fits the cap:

  ```
  depth= 100 len=106500   1.50s
  depth= 200 len=109000   2.93s
  depth= 400 len=114000   5.86s
  depth= 800 len=124000  11.93s
  depth= 900 siblings=6000 len=178500 turns=6900 elapsed=20.10s
  ```

  The one production caller runs it synchronously inside `asyncio.to_thread`
  (`routes/email_routes.py:3216` → `_read_email_sync`), and that caller's `except Exception`
  (`:3122-3127`) turns a failure into a flat render rather than a retry. Nothing absorbs a repeat
  read: `email_boundaries.turns_json` has no writer (`routes-email.md` records this in its
  thread-turn-cache finding), so the parse runs again for every open of the same message.
- **Impact:** the body is attacker-controlled — anyone who can send the user mail — and 178 KB is
  an ordinary newsletter size. Opening one such message holds a default-executor worker for the
  measured ~20 seconds and delays that read by the same amount; several opened at once occupy the
  executor that every other `asyncio.to_thread` call in the process shares. The cost scales
  linearly with nesting depth, so the attacker tunes it against the 200 KB cap rather than needing
  a large message.
- **Fix:** walk only the direct children (`node.find_all(True, recursive=False)` or
  `node.children`) and build the quote-container index once, keyed by parent, instead of
  re-scanning each subtree; cap the nesting depth the parser follows, as the plaintext path
  already caps input length.

### [SECURITY] The webhook URL guard accepts the carrier-grade-NAT range the sibling guard rejects

- **Location:** `src/webhook_manager.py:30-40`, `:47-63`, `:115-127`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the module's stated policy is to block internal targets, and `_ip_is_private`
  implements it with the stdlib predicates plus an explicit list:

  ```python
  _PRIVATE_NETWORKS = [
      ipaddress.ip_network("10.0.0.0/8"), ..., ipaddress.ip_network("fe80::/10"),
  ]
  ...
      if (
          addr.is_private
          or addr.is_loopback
          or addr.is_link_local
          or addr.is_reserved
          or addr.is_multicast
          or addr.is_unspecified
      ):
          return True

      return any(addr in net for net in _PRIVATE_NETWORKS)
  ```

  `100.64.0.0/10` (RFC 6598 shared address space — the range Tailscale and several cluster CNIs
  allocate from) is in neither, and CPython does not classify it as private. `src/url_safety.py:28-34`
  documents that exact classification gap and closes it for the other outbound guard. Measured:

  ```
  100.64.0.0/10 in webhook _PRIVATE_NETWORKS: False
  IPv4Address('100.64.0.1').is_private: False
  validate_webhook_url('http://100.64.0.1/hook') -> http://100.64.0.1/hook
  _validated_public_ips('http://100.64.0.1/hook') -> [IPv4Address('100.64.0.1')]
  url_safety._classify(100.64.0.1, block_private=True) -> private/shared/loopback address blocked: 100.64.0.1
  ```

  `_validated_public_ips` re-uses the same predicate, so the delivery transport pins the connection
  to that address too. `tests/test_webhook_ssrf_resilience.py` lists the address classes it pins
  (`[::]`, `::ffff:127.0.0.1`, `::ffff:169.254.169.254`, `127.0.0.1`, `0.0.0.0`) and does not
  include this one.
- **Impact:** a stored webhook URL can target a tailnet or cluster address that this guard exists
  to refuse, and each delivery then sends the event payload and its HMAC signature there. The
  mitigation that keeps this low is that only an admin can register a webhook
  (`routes/webhook/webhook_routes.py:103`), so the caller is already trusted; the defect is a guard
  that does not cover the range it claims to.
- **Fix:** add `ipaddress.ip_network("100.64.0.0/10")` to `_PRIVATE_NETWORKS` — or have the module
  share `src/url_safety._classify` — and add the address to the reject list in
  `tests/test_webhook_ssrf_resilience.py`.
