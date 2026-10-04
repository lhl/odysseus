# routes: assistant, codex, MCP and workspace

## Overview

The integration surface: `routes/codex_routes.py` (the scope-gated `/api/codex/*` and
`/api/claude/plugin.zip` endpoints that external agents call, including the cookbook launch and
monitor wrappers), `routes/mcp/mcp_routes.py` (MCP server CRUD, tool enablement, and the OAuth
authorize/callback/exchange flow), its `sys.modules` shim at `routes/mcp_routes.py`,
`routes/assistant_routes.py` (the per-owner assistant singleton and its three check-in tasks), and
`routes/workspace_routes.py` (the admin-only directory picker).

The boundary: the API-token scopes and the bearer middleware these routes rely on are
`core-auth-session`'s; the tool-policy tables that decide what a non-admin owner may call are
`src-tools-capabilities-policy`'s; `src-mcp` owns the manager and transports; `routes-cookbook`
owns the serve/state implementation these wrappers call; `routes-email` owns the send and draft
handlers `codex_routes.py` invokes by function reference; `routes-gallery-document` owns the
document and gallery handlers it invokes the same way. This section covers whether the wrappers
authenticate, scope and forward correctly, not whether the handlers underneath are correct.

## Coverage

**Read fully:** all six files (2,055 lines).

| File | Lines |
| --- | ---: |
| `routes/codex_routes.py` | 910 |
| `routes/mcp/mcp_routes.py` | 710 |
| `routes/assistant_routes.py` | 327 |
| `routes/workspace_routes.py` | 85 |
| `routes/mcp_routes.py` | 18 |
| `routes/mcp/__init__.py` | 5 |

**Read partially:** the callees the findings rest on:

- `routes/email_routes.py` at `send_email` (`:4519-4725`)
- `routes/email_helpers.py` at `SendEmailRequest` (`:1990-2010`)
- `src/tools/notes.py` at `do_manage_notes` (`:19-42`, `:88-327`)
- `routes/_validators.py` (all 31 lines)
- `src/tool_security.py` at `owner_is_admin_or_single_user` and `blocked_tools_for_owner`
  (`:222-284`)
- `core/middleware.py` at `require_admin`
- `src/auth_helpers.py` at `get_current_user`, `require_user` and `require_authenticated_request`
- `app.py` at the auth-exempt lists (`:265-292`) and the logging setup (`:107-114`)
- `core/database.py` at the `McpServer`, `CrewMember` and `ScheduledTask` models and
  `Path(DATA_DIR).mkdir` (`:40`)
- `src/constants.py` at `DATA_DIR`, `MCP_OAUTH_DIR` and `COOKBOOK_STATE_FILE`
- `src/task_scheduler.py` at `compute_next_run` and `run_task_now`
- `src/owner_identity.py` at `REQUEST_SENTINEL_OWNERS`
- `routes/cookbook_helpers.py` at `ServeRequest` and the `hf_token` fields (`:1060-1090`)
- `integrations/codex/skills/odysseus/SKILL.md` and its `integrations/claude/` twin at the email
  endpoint documentation (`:106-107`)

**Not read:** `src/mcp_manager.py` and `src/mcp_oauth.py` (the manager and the pending-state
registry these routes drive), the MCP client transports, `src/task_scheduler.py` beyond the two
functions named, `routes/cookbook_routes.py` and `routes/cookbook_helpers.py` beyond
`ServeRequest` (the `routes-cookbook` section owns them), `routes/email_routes.py` outside the
send region, `src/upload_handler.py`, `core/atomic_io.py`, the contents of the two plugin bundles,
and the front end's MCP, assistant and workspace panels.

**Checks run:** three probes, all quoted in the findings:

- the framework semantics of a locally constructed `BackgroundTasks` against an injected one
- the cookbook stop and adopt endpoints with `asyncio.create_subprocess_shell` replaced by a
  recorder so that no tmux session was touched
- the caller-set greps quoted in the third finding

Twenty-one suites were run over this surface — the 21 test files listed below — **170 passed**.

- `tests/test_codex_cookbook_admin_gate.py`
- `tests/test_codex_ssh_host_validation.py`
- `tests/test_mcp_oauth.py`
- `tests/test_mcp_routes_shim.py`
- `tests/test_mcp_manager.py`
- `tests/test_manage_mcp_command_allowlist.py`
- `tests/test_mcp_add_server_args_validation.py`
- `tests/test_mcp_cache_invalidation.py`
- `tests/test_mcp_reconnect_args.py`
- `tests/test_mcp_memory_owner_scope.py`
- `tests/test_mcp_param_hint_hardening.py`
- `tests/test_mcp_email_decode_header_spaces.py`
- `tests/test_mcp_common_truncate.py`
- `tests/test_mcp_dependency_compatibility.py`
- `tests/test_multiple_mcp_servers_timeout.py`
- `tests/test_mcp_tool_params_in_prompt.py`
- `tests/test_builtin_mcp_bg_tasks.py`
- `tests/test_builtin_mcp_npx_cache.py`
- `tests/test_builtin_mcp_pythonpath.py`
- `tests/test_workspace_confine.py`
- `tests/test_merge_last_assistant_rows.py`

### [BUG] The Codex and Claude email-send endpoint reports the message queued and never delivers it

- **Location:** `routes/codex_routes.py:387` (with `routes/email_routes.py:4519`, `:4708`, `:4714`, `:4717`, and `routes/email_helpers.py:2004`)
- **Severity:** high
- **Disposition:** fix-now
- **Evidence:** the wrapper hands the send handler a `BackgroundTasks` object it constructed
  itself rather than the one the framework injects and runs:

  ```python
  # routes/codex_routes.py:387
  return await email_send_endpoint(req=req, background_tasks=BackgroundTasks(), owner=owner)
  ```

  The handler delivers through that object on its default path — inline only when the request
  opts in, otherwise as a background task:

  ```python
  # routes/email_routes.py:4519
  async def send_email(req: SendEmailRequest, background_tasks: BackgroundTasks, owner: str = Depends(require_owner)):
      """Queue an email for SMTP delivery. Returns immediately; send runs in background."""
      ...
      if req.wait_for_delivery:                      # :4708
          result = await asyncio.to_thread(_deliver)
          ...
      background_tasks.add_task(_deliver)            # :4714
      return {
          "success": True,
          "queued": True,                            # :4717
          "account_id": cfg.get("account_id") or req.account_id,
          "message": f"Email queued for {req.to}",
      }
  ```

  `wait_for_delivery` defaults to false (`routes/email_helpers.py:2004`), and neither shipped skill
  bundle documents it — both list the body fields as `to`, `cc`, `bcc`, `subject`, `body`,
  `body_html`, `attachments`, `account_id`, `in_reply_to`, `references`
  (`integrations/codex/skills/odysseus/SKILL.md:106-107` and the `integrations/claude/` twin), so
  every documented call takes the branch that schedules delivery on the discarded object. Measured
  with a two-route FastAPI app reproducing both call shapes:

  ```
  framework-injected BackgroundTasks -> ['delivered']
  locally constructed BackgroundTasks -> task did NOT run
  ```

  Only the instance resolved as a dependency is attached to the response and awaited; a locally
  constructed one is not referenced by anything. `routes/codex_routes.py:387` is the only place in
  the tree that calls the send handler with a constructed instance, and no test in `tests/` covers
  `/api/codex/emails/send` or `codex_email_send` at all.
- **Impact:** an external agent using the shipped integration asks to send mail, receives
  `{"success": true, "queued": true, "message": "Email queued for …"}`, and nothing is ever sent.
  The failure is silent in both directions: the caller cannot distinguish it from a real queue, and
  the user is told the message was queued. The scope the plugin asks the user to grant (`email:send`)
  and the capability table's `"email_send_requires_confirmation": True` both describe a working
  send. Nothing else in the path is broken — the same handler delivers correctly from the web UI,
  which passes the framework's instance.
- **Fix:** take `background_tasks: BackgroundTasks` as a parameter of `codex_email_send` and
  forward it, or set `wait_for_delivery=True` on the request the wrapper builds so the handler
  delivers inline before returning. Add a test that posts to `/api/codex/emails/send` and asserts
  the delivery call happened, since no test currently reaches this endpoint.
- **Re-review (2026-10-04):** re-derived in full; high stands. `routes/codex_routes.py:387` is the only
  `BackgroundTasks()` construction under `routes/` and `src/`, `wait_for_delivery` is read only at
  `routes/email_routes.py:4708` and defaults to false at `routes/email_helpers.py:2004`, and the
  skill documents the send body without it (`integrations/codex/skills/odysseus/SKILL.md:107`).


### [SECURITY] The MCP OAuth credentials are written to the application log in full

- **Location:** `routes/mcp/mcp_routes.py:213`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the handler logs the raw form field before parsing it, and that field is the
  credential document:

  ```python
  # routes/mcp/mcp_routes.py:213
  logger.info(f"MCP add_server: oauth_file={oauth_file!r}")
  ```

  The block immediately below parses the credentials out of that same string — the id at `:219`
  and the paired secret at `:220` — and writes them into the credentials file the MCP server reads
  (`:216-241`, writing at `:236`), so the logged value contains a live Google OAuth secret. (The
  two field names are not quoted verbatim here: the run's secret gate reads those
  thirteen-character literals as credentials and fails the build.) The log destination is
  `DATA_DIR/logs/app.log` through a `RotatingFileHandler` (`app.py:107-114`), and no logging filter
  anywhere in the tree scrubs secret-looking values — the only redaction helper is
  `core/log_safety.redact_url`, which handles URL userinfo, not a JSON document. The same handler
  writes the credentials file and the later token exchange writes the refresh token
  (`:575-576`) with plain `open(..., "w")` under a `DATA_DIR` created by
  `Path(DATA_DIR).mkdir(parents=True, exist_ok=True)` (`core/database.py:40`), which is the
  file-permission class already reported as a medium in `core-data-platform.md`; it is not
  re-reported here, but the two together mean the secret reaches disk twice, once deliberately and
  once in a log.
- **Impact:** anyone who can read the log file — any local user on a default-umask host, anyone
  given the log for debugging, and every log aggregator an operator forwards it to — obtains the
  secret half of the OAuth credentials for that MCP integration. The line fires on every attempt
  to add a server with credentials, including attempts that then fail.
- **Fix:** log the fact and the destination filename instead of the payload
  (`logger.info("MCP add_server: OAuth credentials supplied for %s", oauth_filename)`), or delete
  the line — the response already reports whether the server connected.

### [BUG] The cookbook stop endpoint kills any tmux session by name, tracked or not

- **Location:** `routes/codex_routes.py:685` (the endpoint is at `:676`, the sibling check at `:609`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `codex_cookbook_stop` looks the task up in cookbook state and then ignores the
  result, passing `task or {}` to the host resolver and building the kill command from the path
  parameter alone:

  ```python
  # routes/codex_routes.py:676
  @router.post("/cookbook/stop/{session_id}")
  async def codex_cookbook_stop(request: Request, session_id: str):
      _require_cookbook_scope(request, COOKBOOK_LAUNCH_SCOPES)
      import re as _re
      if not _re.fullmatch(r"[a-zA-Z0-9_-]+", session_id):
          raise HTTPException(400, "Invalid session id")
      state = _read_cookbook_state()
      tasks = state.get("tasks") or []
      task = next((t for t in tasks if t.get("sessionId") == session_id), None)
      host, port_flag = _ssh_prefix_for_task(task or {})   # :685 — no 404 when task is None
      if host:
          cmd = f"ssh {port_flag}{host} \"tmux kill-session -t {session_id}\""
      else:
          cmd = f"tmux kill-session -t {session_id}"       # :688
      result = await _run_shell(cmd, timeout=10)
  ```

  The read-only sibling does refuse untracked names — `codex_cookbook_output` raises 404 when the
  session is not in state (`:609-610`) — and its comment gives the reason: "anything else would let
  the agent run arbitrary `tmux capture-pane` targets". The session-id regex blocks shell
  metacharacters, so this is not injection; the missing piece is the existence check. Measured with
  `asyncio.create_subprocess_shell` replaced by a recorder, so no session was actually killed:

  ```
  stop(untracked session) -> {'session_id': 'zzz-not-a-cookbook-task', 'exit_code': 0, 'host': 'local'}
  shell ran: ['tmux kill-session -t zzz-not-a-cookbook-task']
  ```

- **Impact:** an API token holding `cookbook:launch` can kill any tmux session on the host — or on
  a configured remote host whose name it guesses — including sessions the user started by hand and
  that have nothing to do with the cookbook. The scope is documented as "start/stop serves", and
  every other endpoint in this family resolves its target through cookbook state, so the reachable
  set is wider than the surface describes. The blast radius is limited to tmux sessions, and the
  caller must already hold a scope that permits launching serve commands on the same hosts.
- **Fix:** raise `HTTPException(404, "task not found")` when `task is None`, as
  `codex_cookbook_output` does.

### [ERROR-HANDLING] Adopting a session returns a 500 when the port is not a number

- **Location:** `routes/codex_routes.py:869` (with `:836`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** every other field of the adopt body is validated — the tmux session name must match
  `[a-zA-Z0-9_-]+` and the model must be non-empty (`:838-843`), and the host goes through
  `validate_remote_host` (`:834`) — but the port is only defaulted and then converted in the
  payload literal:

  ```python
  port = norm.get("port") or 8000                      # :836
  ...
  "payload": {..., "port": int(port)},                 # :869
  ```

  Measured by calling the endpoint with a token-shaped request and the subprocess call faked:

  ```
  adopt(port='abc') -> ValueError: invalid literal for int() with base 10: 'abc'
  ```

  A dict or list port raises `TypeError` the same way. Both escape the handler, so FastAPI returns
  500 with a traceback in the log.
- **Impact:** an agent that sends a string or a structured value where an integer was expected gets
  a server error rather than the 400 that every other field of the same endpoint produces, and the
  failure is unattributable from the client side. Only reachable by an API token with
  `cookbook:launch`, so the cost is a confusing error and a log line.
- **Fix:** coerce the port the way the sibling payload fields are handled — parse it in a
  `try`/`except (TypeError, ValueError)` and raise `HTTPException(400, "Invalid port")`, or
  validate it with the same helper the SSH port uses.
