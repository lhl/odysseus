# routes: auth, API tokens, admin and provider sign-in

## Overview

The credential and administrator surface: `routes/auth_routes.py` (login, TOTP, session issuance
and revocation, user administration and privileges, settings, features and the integrations CRUD),
`routes/api_token_routes.py`, `routes/backup_routes.py`, `routes/device_flow.py` with the two
providers built on it (`routes/chatgpt_subscription_routes.py`, `routes/copilot_routes.py`),
`routes/admin_wipe/admin_wipe_routes.py` and the `routes/admin_wipe_routes.py` shim, plus
`routes/_validators.py` and `routes/__init__.py`.

The boundary: the middleware that consumes the sessions these routes issue is `core-auth-session`;
the tables they read are `core-data-platform`; the credential stores and guards they call are
`src-security`; the settings and integration stores they write are `src-memory-rag` and
`src-email-integrations`. This section covers whether each route authenticates, authorizes and
scopes correctly, not whether the store underneath is safe.

## Coverage

**Read fully:** all eleven files (2,114 lines): `routes/auth_routes.py` (919),
`routes/api_token_routes.py` (209), `routes/backup_routes.py` (221), `routes/device_flow.py` (193),
`routes/admin_wipe/admin_wipe_routes.py` (176), `routes/copilot_routes.py` (173),
`routes/chatgpt_subscription_routes.py` (170), `routes/admin_wipe_routes.py` (17),
`routes/_validators.py` (31), `routes/admin_wipe/__init__.py` (5), `routes/__init__.py` (0).

**Read partially:** the callees the findings rest on — `core/auth.py` at `setup`/`create_user`
(`:255-283`), `set_privileges` (`:387-403`), `status`/`policy` (`:669-680`); `src/integrations.py`
at `add_integration`/`update_integration` (`:269-315`); `src/rate_limiter.py` (`check`, `:25-36`);
`core/database.py` at `ProviderAuthSession` (`:556-568`) and `GalleryImage` (`:344-359`);
`routes/session_routes.py` at `/sessions/all` (`:677-731`); `routes/prefs_routes.py` at
`_load`/`_load_for_user` (`:17-52`); `src/memory.py` at `load_all_for_update`/`save` (`:180-187`,
`:261-278`); `core/database.py` at the transcript-FTS triggers (`:2178-2256`); `app.py` at the
auth-exempt list (`:265-289`), `_is_trusted_loopback` (`:348-362`) and the uvicorn launch
(`:1301-1306`); `launcher.py:135-149`; `core/middleware.py` at `require_admin`;
`src/agent_tools/admin_tools.py` at `do_manage_tokens` (`:445-489`); `static/js/admin.js` at the
token list (`:2555-2600`) and the Danger Zone (`:2896-2945`); `static/index.html` at the Danger Zone
modal (`:2455-2522`); `docker-compose.yml` at the app service (`:1-32`) and the other services'
port bindings; `website/setup.md` at the reverse-proxy guidance (`:530-540`) and the environment
table (`:716`); `.env.example` at `APP_BIND` (`:74-75`).

**Not read:** the middleware, `AuthManager` internals and models beyond the functions cited (their
sections); the settings, integrations, memory and skills stores beyond the call sites cited; the
front end beyond the token list and Danger Zone regions; the `routes-*` sections that own the
modules these routes call.

**Checks run:** a Docker peer-address probe (a container serving on a published
`127.0.0.1` port, curled from the host) and a `uvicorn.middleware.proxy_headers` probe under the
default trusted list, both quoted in the first finding; a bcrypt timing measurement; a route-level
probe that built the auth router with a stub manager (mirroring
`tests/test_integrations_store_shape.py`) and posted non-object bodies to the JSON endpoints,
quoted in the last finding; and a read of the callers of `APIKeyManager`/token rows. Twenty-seven
suites were run over this surface — `tests/test_api_token_routes.py`,
`tests/test_api_token_user_route_gate.py`, `tests/test_device_flow_routes.py`,
`tests/test_copilot_routes.py`, `tests/test_admin_wipe_gallery.py`,
`tests/test_admin_wipe_routes_shim.py`, `tests/test_backup_cli_security.py`,
`tests/test_backup_import_cross_user_dedup.py`, `tests/test_backup_import_skills.py`,
`tests/test_backup_import_skills_dedup.py`, `tests/test_auth_policy.py`,
`tests/test_auth_regressions.py`, `tests/test_auth_require_privilege_nondict.py`,
`tests/test_auth_root_path.py`, `tests/test_auth_session_revocation.py`,
`tests/test_rename_user_case_insensitive.py`, `tests/test_rename_user_owner_sync.py`,
`tests/test_rename_user_token_cache.py`, `tests/test_delete_user_invalidates_token_cache.py`,
`tests/test_delete_user_revokes_api_tokens.py`, `tests/test_setup_admin_user.py`,
`tests/test_rate_limiter.py`, `tests/test_totp_failclosed.py`, `tests/test_route_validators.py`,
`tests/test_integrations_store_shape.py`, `tests/test_cors_preflight.py`,
`tests/test_reserved_username_admin_escalation.py` — **203 passed**.

### [SECURITY] The login, signup and setup limiters key on the socket peer, which the documented deployment makes identical for every client

- **Location:** `routes/auth_routes.py:119-121` (the three limiters), `:130`, `:148`, `:167` (the `.check(request.client.host)` call sites)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the three limiters are constructed per process and keyed on `request.client.host`:

  ```python
  _login_limiter = RateLimiter(max_requests=15, window_seconds=60)
  _signup_limiter = RateLimiter(max_requests=3, window_seconds=300)
  _setup_limiter = RateLimiter(max_requests=3, window_seconds=300)
  ...
  @router.post("/login")
  async def login(body: LoginRequest, request: Request, response: Response):
      if not _login_limiter.check(request.client.host):
          raise HTTPException(429, "Too many requests — try again later")
  ```

  `src/rate_limiter.py:26` keys its window on the string it is handed and nothing else. The value
  `request.client.host` carries is the socket peer unless uvicorn's `ProxyHeadersMiddleware`
  rewrites it, and that middleware only rewrites it for a peer in its trusted list. In this
  installation (uvicorn 0.54.0) `proxy_headers` defaults to `True` and the trusted list defaults to
  `os.environ.get("FORWARDED_ALLOW_IPS", "127.0.0.1,::1")`; the app passes neither
  (`uvicorn.run(app, host=bind_host, port=bind_port, log_level="info")`, `app.py:1306` and
  `launcher.py:149`) and no compose file or entrypoint sets `FORWARDED_ALLOW_IPS`. Measured against
  that middleware, with the default trusted list:

  ```
  loopback peer (native proxy)      peer=127.0.0.1   xff='203.0.113.9' -> client=('203.0.113.9', 0)
  docker bridge gateway peer        peer=172.18.0.1  xff='203.0.113.9' -> client=('172.18.0.1', 51234)
  ```

  The shipped compose publishes the app on the host loopback only —
  `- "${APP_BIND:-127.0.0.1}:${APP_PORT:-7000}:7000"` (`docker-compose.yml:14`) — and the setup
  guide tells the operator to reach it through a local proxy: "If your access layer reaches
  Odysseus on the same host, proxy to `http://127.0.0.1:7000`" (`website/setup.md:537`). A request
  that arrives that way reaches the container from the Docker gateway, not from loopback.
  Measured with a container publishing `127.0.0.1:18080:3000` and curled from the host:

  ```
  $ curl -s http://127.0.0.1:18080/                         # no headers
  peer=::ffff:172.17.0.1
  xff=-
  $ curl -s -H 'X-Forwarded-For: 203.0.113.9' http://127.0.0.1:18080/
  peer=::ffff:172.17.0.1
  xff=203.0.113.9
  ```

  So in the default deployment every client — the operator's browser through the tunnel, a second
  user, an attacker — presents the same key to all three limiters. (A native install behind a
  proxy on the same host is the case that works, because the peer is loopback and the forwarded
  chain is trusted; `app.py:348-362` shows the codebase reasons about that topology elsewhere.)
- **Impact:** the login budget is instance-wide, not per client. Sixteen unauthenticated POSTs to
  `/api/auth/login` inside a minute make the next attempt from anyone return 429, including the
  administrator's, and about one request every four seconds keeps the lockout up indefinitely; the
  signup and first-run-setup budgets (3 per 5 minutes) are shared the same way, so a lockout also
  blocks a new instance's setup while it is still unconfigured. It also means the limiter cannot
  isolate one account's failed attempts from another's, which is the property the comment above
  `_login_limiter` and the `RateLimiter` docstring ("keyed by IP") claim. What it still does is cap
  the total guess rate.
- **Fix:** give uvicorn a peer it can trust for client identity in the container deployment (set
  `FORWARDED_ALLOW_IPS` for the app service and make the documented proxy overwrite
  `X-Forwarded-For` rather than append to it), and pin the keying with a test — the existing
  `tests/test_rate_limiter.py` exercises the limiter, not what it is keyed on. If the header cannot
  be trusted, key on something a single client cannot exhaust for everyone (for example
  `(username, peer)` with a separate global ceiling).

### [PERF] The admin create-user path hashes the password on the event loop while its siblings offload the same call

- **Location:** `routes/auth_routes.py:319` (with `:140`, `:160`, `:171-181`, `:235-238` and `:336`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `admin_create_user` is an `async def` and calls the synchronous
  `AuthManager.create_user` inline, so `bcrypt.gensalt()`/`hashpw` runs on the event loop:

  ```python
  @router.post("/users")
  async def admin_create_user(body: CreateUserRequest, request: Request):
      ...
      ok = auth_manager.create_user(body.username, body.password, body.is_admin)
  ```

  The three other credential paths in the same file offload it — `first_run_setup` uses
  `await asyncio.to_thread(auth_manager.setup, ...)`, `signup` uses
  `await asyncio.to_thread(auth_manager.create_user, body.username, body.password, is_admin=False)`,
  and `login` uses `asyncio.to_thread` for both the password check and session creation. Measured
  cost of one hash at the default bcrypt cost on this machine:

  ```
  bcrypt.gensalt()+hashpw default cost: 169 ms
  ```

  `rename_user` (`:336`) has the same shape with more work inline: an owner sweep over every mapped
  table with an `owner` column, `rglob` over `SKILLS_DIR` for `SKILL.md`, a walk of
  `DEEP_RESEARCH_DIR`, and a read-modify-write of `memory.json`, all inside the `async def`.
- **Impact:** while an administrator creates a user, every other in-flight request — including a
  streaming chat turn — stalls for about 170 ms; a rename stalls for as long as its file walks take.
  The route is admin-only and infrequent, so this is a stall rather than an outage, and it is the
  kind of work FastAPI's sync-endpoint threadpool or `asyncio.to_thread` exists for. Nothing in the
  section's suites covers the blocking shape.
- **Fix:** wrap the `create_user` call (and the file/DB portions of `rename_user`) in
  `await asyncio.to_thread(...)`, matching the sibling routes.

### [BUG] The token list shows every owner's tokens, but revoke and rename refuse any token whose owner is not the caller — including the null-owner tokens the agent tool mints

- **Location:** `routes/api_token_routes.py:83` (list), `:170` and `:204` (the refusals), with `src/agent_tools/admin_tools.py:469-471` and `static/js/admin.js:2572-2584`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the list is unfiltered:

  ```python
  def list_tokens(request: Request):
      require_admin(request)
      with get_db_session() as db:
          tokens = db.query(ApiToken).all()
  ```

  while both mutating endpoints refuse any row whose `owner` is not exactly the caller:

  ```python
  if current_user and token.owner != current_user:
      raise HTTPException(403, "Not your token")
  ```

  A null owner fails that comparison. Null-owner rows are exactly what the agent's token tool
  writes — `src/agent_tools/admin_tools.py:469-471` constructs `ApiToken(id=tid, name=name,
  token_hash=token_hash, token_prefix=raw_token[:8], is_active=True, ...)` with no `owner` and no
  `ody_` prefix (reported in `src-agent-tools.md`). The admin UI renders a Revoke button for every
  row (`static/js/admin.js:2572`) and ignores the response status:

  ```js
  await fetch(`/api/tokens/${btn.dataset.admDelToken}`, { method: 'DELETE', credentials: 'same-origin' });
  loadTokens();
  ```

- **Impact:** an administrator sees tokens they cannot revoke or rename. The click looks like a
  no-op (the list reloads with the row still there and no error shown), so the only way to remove
  such a row is direct database access. On an instance with more than one administrator the same
  applies to a colleague's tokens. The tokens themselves are inert — the middleware cannot
  authenticate one that lacks the prefix — so this is an unusable admin control, not an exposure.
- **Fix:** let an administrator revoke a row with no owner (`if token.owner and token.owner !=
  current_user`), or filter `list_tokens` to the caller's own and null-owner rows, and surface the
  403 in the UI instead of discarding the response.

### [ERROR-HANDLING] Three admin JSON endpoints raise an unhandled error on a non-object body

- **Location:** `routes/auth_routes.py:329` (`update_user_privileges`), `:784` (`create_integration`), `:794` (`update_integration_route`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** all three read the body and hand it straight to a function that expects a mapping:

  ```python
  body = await request.json()
  ok = auth_manager.set_privileges(username, body)      # :329
  ...
  body = await request.json()
  item = add_integration(body)                          # :784
  ...
  body = await request.json()
  item = update_integration(integration_id, body)       # :794
  ```

  and the callees iterate or `.get` it — `core/auth.py:397` (`for k, v in privileges.items()`),
  `src/integrations.py:273` (`preset_key = data.get("preset")`), `:304` (`data = dict(data)`).
  Measured by building the router with a stub manager and calling the endpoint functions with a
  fake request whose `json()` returns the body, the same shape
  `tests/test_integrations_store_shape.py` uses:

  ```
  PUT privileges body=[]: AttributeError: 'list' object has no attribute 'items'
  POST integrations body=[]: AttributeError: 'list' object has no attribute 'get'
  POST integrations body='x': AttributeError: 'str' object has no attribute 'get'
  PUT integrations/{id} body='x': ValueError: dictionary update sequence element #0 has length 1; 2 is required
  ```

  Two other handlers in this section already keep the contract — `routes/backup_routes.py:73`
  (`if not isinstance(body, dict): raise HTTPException(400, "Expected a JSON object")`) and
  `routes/api_token_routes.py:163` — as does the repository's `*_nondict` test convention.
- **Impact:** an API client that sends a JSON array or string to one of these endpoints gets a 500
  and an unhandled traceback in the log where a 400 is the contract the rest of the section keeps.
  Admin-only and not reachable from the shipped UI, so the cost is a confusing failure and a log
  line, not a broken flow.
- **Fix:** add the `isinstance(body, dict)` guard used by `import_data` to the three handlers.
