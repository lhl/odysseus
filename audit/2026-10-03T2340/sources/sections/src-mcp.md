# src: MCP management and OAuth

## Overview

`src/mcp_manager.py` owns everything below the MCP route layer: the three transports (stdio, SSE
and Streamable HTTP with the OAuth handshake), the tool inventory discovered from each server, the
prompt text and OpenAI function schemas rendered from it, the plan-mode read-only classification,
the tool call path, and the connection registry the routes, the agent loop and the scheduler read.

`src/mcp_oauth.py` holds the remote-server OAuth pieces: the loopback redirect URI, the
pending-authorization registry that bridges the SDK's browser flow to `/api/mcp/oauth/callback`,
and `DbTokenStorage`, the SDK token store backed by the encrypted `McpServer.oauth_tokens` column.

The boundary: the route layer that creates, toggles, reconnects and deletes servers and drives the
OAuth browser flow is `routes-rest-agent-admin` (its findings are cross-referenced here, not
restated); the agent-facing `manage_mcp` tool and its command allowlist are `src-agent-tools`; the
`McpServer` row, its columns and the encryption type are `core-data-platform`; the dispatcher that
calls `call_tool` and the loop that renders the schemas are `src-tools-parse-exec` and
`src-agent-loop`; the built-in servers registered into this manager are
`src-tools-capabilities-policy` and `mcp-servers`. This section covers what the manager does with a
server's configuration and with the tool data a server supplies — not whether the routes
authenticate, whether the agent allowlist is sufficient, or whether the built-in servers behave.

## Coverage

**Read fully:** both assigned files (920 lines): `src/mcp_manager.py` (709), `src/mcp_oauth.py`
(211).

**Read partially:** the callers and boundary code the findings rest on:

- `routes/mcp/mcp_routes.py` in full (710 lines), because it is the caller set for the manager
  (`add_server`, `reconnect_server`, `toggle_server`, `delete_server`, and the OAuth
  authorize/callback/exchange handlers)
- `src/agent_tools/admin_tools.py` at `_validate_mcp_command` and `do_manage_mcp`'s
  add/enable/reconnect branches (`:100-360`)
- `core/database.py` at the `McpServer` model (`:570-584`) and `EncryptedText` (`:150-172`)
- `src/tool_execution.py` at the two MCP dispatch sites (`:675-700`, `:1290-1320`)
- `src/task_scheduler.py` at the two `call_tool` sites (`:1470-1480`, `:2240-2245`)
- `src/agent_loop.py` at the MCP prompt block (`:2746-2756`), the schema merge (`:2286-2289`), the
  plan-mode block (`:3857-3864`) and the tool-result truncation (`:5968-6002`)
- `app.py` at `load_dotenv` (`:48`), the startup connect task (`:1068-1076`) and the shutdown
  disconnect (`:1291-1296`)
- `src/builtin_mcp.py` at `builtin_python_env` (`:148-160`) and the two `connect_server` call sites
- `static/js/settings.js` at the MCP server panel (`:4939-4980`)
- the SDK the manager drives — `mcp/client/stdio/__init__.py` (`get_default_environment`,
  `stdio_client`), `mcp/client/streamable_http.py` (`streamablehttp_client`,
  `streamable_http_client`), `mcp/client/session.py` and `mcp/shared/session.py` (the read-timeout
  handling), `mcp/client/auth/oauth2.py` (the refresh path)
- the module's own tests for what is already pinned

SDK and anyio paths named in the findings are the installed packages
(`venv/lib/python3.12/site-packages/`: `mcp` 1.30.0, anyio 4.15.1, httpx 0.28.1), not files in the
target tree.

**Not read:**

- `src/builtin_mcp.py` beyond `builtin_python_env` and the two `connect_server` call sites
- `mcp_servers/*`
- the rest of `agent_loop.py`, `tool_execution.py`, `task_scheduler.py` and `admin_tools.py`
- `src/settings.py`
- the MCP front end beyond the server panel
- the SDK beyond the functions named above
- every other section's paths

Line numbers are the working tree at `2992bf6d368a` (clean apart from this run's untracked `audit/`
directory).

**Checks run:** a throwaway MCP server (`/tmp/mcp_probe_server.py`, a FastMCP server declaring one
mutating tool with `readOnlyHint=False`, one tool that reports its own environment variable names,
and one that sleeps for 600s) driven by four probe scripts under `/tmp`, none of them part of the
target tree; each probe's output is quoted in the finding it settles. Also a direct call of
`_format_mcp_params` with malformed `required` values, a `grep` for timeouts in the callers, and a
uvicorn probe confirming that two requests run in two different tasks (each request is a
`RequestResponseCycle.run_asgi()` task; three requests produced three distinct task objects). The
18 suites matching this surface — the 17 files from `ls tests | grep -iE 'mcp'` plus
`tests/test_plan_mode.py`, which pins the classifier the annotation finding touches — were run:
**127 passed**.

### [BUG] Nothing bounds an MCP session call, so a server that stops answering wedges whatever is waiting on it

- **Location:** `src/mcp_manager.py:511` (with `:202`, `:271`, `:359`, `:442-458`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the call path passes no timeout, and neither does the session it uses:

  ```python
  # :509-511
  async def _do_call(self, session, tool_name: str, arguments: Dict) -> Dict:
      """Execute a single MCP tool call and return result dict."""
      result = await session.call_tool(tool_name, arguments)
  ```

  All three `ClientSession` constructions omit `read_timeout_seconds` — `:202` (stdio), `:271`
  (SSE), `:359` (HTTP):

  ```python
  session = await stack.enter_async_context(ClientSession(read_stream, write_stream))   # :202
  ```

  The SDK reads that as "wait forever": `ClientSession.__init__(read_timeout_seconds: timedelta |
  None = None)` (`mcp/client/session.py:126`), and `send_request` only bounds the wait when a
  timeout exists (`timeout = None` … `with anyio.fail_after(timeout)`,
  `mcp/shared/session.py:283-291`); `call_tool` itself accepts a per-call
  `read_timeout_seconds` (`mcp/client/session.py:386-394`) that this code does not pass. The only
  timeout in the file is the startup one, applied by `connect_all_enabled` and nowhere else:

  ```python
  # :442-458
  async def _connect_with_timeout(self, srv):
      args = json.loads(srv.args) if srv.args else []
      env = json.loads(srv.env) if srv.env else {}
      try:
          await asyncio.wait_for(self.connect_server(...), timeout=20)
  ```

  Measured against a stdio server whose handshake succeeds and whose tool sleeps 600s:

  ```
  == 3. call with no answer ==
  call_tool still waiting after 5.0s; probe's own 5s bound fired
  == 3b. connect to a stdio server that never answers ==
  connect_server still waiting after 7.1s; probe's own 5s bound fired
  ```

  The callers add nothing: `grep -n 'wait_for\|timeout' src/tool_execution.py` returns nothing,
  and the scheduled-task call sites (`src/task_scheduler.py:1474`, `:2243`) await `call_tool`
  directly.
- **Impact:** a stdio or SSE server that accepts a request and never answers — a wedged process, a
  tool blocked on a resource, a server whose stdout reader died — leaves `call_tool` awaiting
  forever. The chat turn that made the call stalls with no error and no timeout, and the SSE stream
  stops producing events; the user's only exit is to close the tab, which cancels the tool task.
  The same path serves scheduled tasks (`src/task_scheduler.py:1474`, `:2243`), where there is no
  client to disconnect and the task simply stops progressing. The HTTP transport is partly covered
  by the httpx timeouts the SDK sets (`streamable_http.py:714-716`: 30s connect/read, 300s SSE
  read), so the exposure is stdio and SSE. The connect side matters for the admin routes too:
  `POST /api/mcp/servers` awaits `connect_server` with no bound, so a stdio server that never
  completes `initialize()` hangs that request.
- **Fix:** pass `read_timeout_seconds` to the three `ClientSession` constructions, or wrap
  `_do_call` in `asyncio.wait_for` with a configurable limit; the SDK raises `McpError` with code
  408 on timeout, which `call_tool` already turns into an error result. Give the route-facing
  connect path the same bound `_connect_with_timeout` gives the startup one.

### [SECURITY] A stdio server with any configured env var receives the whole application environment

- **Location:** `src/mcp_manager.py:193`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the environment handed to the child depends on whether the row has any env vars at
  all, and the non-empty branch replaces the SDK's whitelist with everything:

  ```python
  # :190-194
  server_params = StdioServerParameters(
      command=command,
      args=args,
      env={**os.environ, **env} if env else None,
  )
  ```

  The SDK's default is deliberately narrow — `stdio_client` builds
  `{**get_default_environment(), **server.env} if server.env is not None else
  get_default_environment()` (`mcp/client/stdio/__init__.py:127`), and
  `get_default_environment()` returns only `HOME`, `LOGNAME`, `PATH`, `SHELL`, `TERM` and `USER`
  (`:28-45`). Passing `None` selects that whitelist; passing `{**os.environ, **env}` bypasses it.
  Measured with a stdio server whose tool returns its own `os.environ` names, in a process holding
  a canary variable:

  ```
  no stored env:      connected=True count=4  names=['HOME', 'LC_CTYPE', 'PATH', 'SHELL']
  one stored env var: connected=True count=22 names=['EMAIL_ADDRESS', 'HOME', …, 'PROBE_CANARY',
                                                     'PWD', 'SHELL', 'SHLVL', '_']
  ```

  (The fourth name in the first row is the child interpreter's own locale coercion, not the
  manager's doing.) `app.py:48` runs `load_dotenv(encoding="utf-8-sig")` at import, so every value
  the operator keeps in `.env` is in `os.environ` when a server is spawned; `.env.example`
  documents API keys, a search secret, an OAuth client secret and the admin password among them.
- **Impact:** an admin who adds a third-party stdio server and gives it the one variable it needs —
  an account name, an API key — also hands it every other secret in the process environment. The
  mitigation is real and lowers this to `low`: a stdio server is arbitrary code running as the app
  user, which the add-server route's own docstring states ("registering a stdio server is
  equivalent to executing arbitrary binaries on the host", `routes/mcp/mcp_routes.py:170-172`), so
  a hostile one could read the data directory and the encryption key anyway. What this adds is the
  secrets that exist only in the environment (a container `-e` value, a variable exported by the
  operator's shell) plus an exposure the SDK's default was written to prevent. The trap is the
  asymmetry: a server with no env config gets the whitelist, and adding one innocuous variable
  flips it to the entire environment.
- **Fix:** keep the full environment for the built-in servers, which read `PYTHONPATH` and the
  app's own variables (`src/builtin_mcp.py:148-160`), and let the SDK's whitelist stand for
  admin-added ones — `env={**os.environ, **env} if self.is_builtin(server_id) else (env or None)`.
  The cost: a third-party server that depends on an app environment variable would have to have it
  added to its own env config.

### [BUG] A tool schema whose `required` is not an array raises in the prompt renderer and drops every MCP description

- **Location:** `src/mcp_manager.py:77`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `properties` is type-checked one line above; `required` is not, and `set()` on a
  number or a boolean raises:

  ```python
  # :74-79
  props = input_schema.get("properties")
  if not isinstance(props, dict) or not props:
      return ""
  required = set(input_schema.get("required") or [])
  parts = []
  ```

  Measured, both directly and through the entry point the prompt builder calls:

  ```
  $ venv/bin/python -c "from src.mcp_manager import _format_mcp_params, McpManager; ..."
  normal:        Args (JSON): {"path": string (required)}
  required=5:    TypeError: 'int' object is not iterable
  required=True: TypeError: 'bool' object is not iterable
  get_tool_descriptions_for_prompt -> TypeError 'int' object is not iterable
  ```

  Nothing between the server and this function checks the shape: discovery stores the server's
  `inputSchema` verbatim (`:212`, `:281`, `:368`), and the SDK types it only as a dict
  (`Tool.inputSchema`). The caller swallows the failure at DEBUG, so it leaves no visible trace:

  ```python
  # src/agent_loop.py:2747-2756
      if mcp_mgr:
          try:
              _mcp_desc = mcp_mgr.get_tool_descriptions_for_prompt(mcp_disabled_map or {})
              ...
          except Exception as _mcp_err:
              logger.debug(f"MCP description injection skipped: {_mcp_err}")
  ```

  The result is not cached on failure, so every later request fails the same way. This is the class
  the renderer's own docstring claims to have closed — "MCP servers are third-party, so names/types
  are sanitized and the parameter count + total length are capped (issue #2660)" (`:69-70`) — but
  the caps cover names and lengths, not the shape of `required`.
- **Impact:** one server declaring `"required"` as a number or boolean (a hand-written schema
  saying `"required": true` for a single parameter is the plausible mistake) removes the whole MCP
  tool-description block from the agent prompt on every request — for every server, not just that
  one — taking with it each tool's description, argument names and required flags, which is what
  issue #2509 added. The native function schemas are built by a separate method
  (`get_all_openai_schemas`) and still go out, so the model keeps the tool list but loses the
  argument hints. Only a DEBUG line records it, and the root logger is set to INFO
  (`app.py:95`), so the shipped setup never writes it.
- **Fix:** check the type instead of assuming it —
  `required = set(input_schema.get("required")) if isinstance(input_schema.get("required"), list)
  else set()` — and raise the caller's log level to WARNING when a server's schema costs the whole
  block.

### [BUG] Streamable HTTP discovery drops each tool's read-only annotations, so plan mode classifies those servers by name alone

- **Location:** `src/mcp_manager.py:365-369`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the stdio and SSE discovery loops record the server's annotations (`:213-216`,
  `:282-285`); the HTTP loop does not:

  ```python
  # :364-369
  for tool in tools_result.tools:
      tools.append({
          "name": tool.name,
          "description": tool.description or "",
          "input_schema": tool.inputSchema if hasattr(tool, "inputSchema") else {},
      })
  ```

  `mcp_tool_is_readonly` reads exactly that key and prefers it over the name heuristic
  (`:107-133`): `readOnlyHint is True` → read-only, `readOnlyHint is False` or
  `destructiveHint is True` → write. `plan_mode_blocked_mcp` (`:623-637`) blocks every tool it
  classifies as a write, both from the schema list and by qualified name at runtime
  (`src/agent_loop.py:3857-3864`). Measured with one FastMCP server declaring a single mutating
  tool (`readOnlyHint=False`, `destructiveHint=True`) named `get_and_delete_all`, connected over
  both transports in the same probe:

  ```
  stdio  connected=True tool keys=['annotations', 'description', 'input_schema', 'name']
  stdio  mcp_tool_is_readonly=False plan_mode_blocked={'mcp__s_ann__get_and_delete_all', ...}
  http   connected=True tool keys=['description', 'input_schema', 'name']
  http   mcp_tool_is_readonly=True plan_mode_blocked={'mcp__s_ann__hang', 'mcp__s_ann__env_keys'}
  ```

  `tests/test_plan_mode.py:61-71` pins the classifier with annotations supplied directly, but no
  test pins what discovery stores per transport — `grep -rn annotations tests/*.py` finds no other
  MCP annotation test — so the drop is unguarded.
- **Impact:** for a remote Streamable HTTP server, plan mode loses the server's own declaration and
  falls back to the leading-verb heuristic, so a mutating tool whose name starts with `get`,
  `list`, `read`, `search`, `fetch`, `query`, `find`, `describe`, `show`, `view`, `lookup`,
  `count`, `status`, `info`, `inspect` or `summar` is offered to the model and allowed to run in
  the mode that promises read-only investigation. The same server over stdio or SSE is classified
  correctly, so the gate's behaviour depends on the transport the admin picked. Preconditions: plan
  mode on, an HTTP-transport server, and a mutating tool named with a read verb — which is why
  this is `low`, but the annotation is data the client already received and threw away.
- **Fix:** add the `annotations` key to the HTTP tool dict, as the other two transports do.

### [ERROR-HANDLING] Disconnecting a server cannot close its transport, because the context was entered in another task

- **Location:** `src/mcp_manager.py:407-412`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the stored exit stack holds the SDK's transport context managers, which are anyio
  task groups and must be exited in the task that entered them; anyio raises otherwise
  (`anyio/_backends/_asyncio.py:463-467`). The manager closes the stack from whatever task calls
  it:

  ```python
  # :407-412
  stack = self._stacks.pop(server_id, None)
  if stack:
      try:
          await stack.aclose()
      except Exception as e:
          logger.warning(f"Error closing MCP server {server_id}: {e}")
  ```

  In the app the connect and the disconnect are always different tasks: each request runs as its
  own `RequestResponseCycle.run_asgi()` task (measured: three requests produced three distinct task
  objects under uvicorn), `add_server` connects, `delete_server`/`toggle_server`/
  `reconnect_server` disconnect, the startup task connects every enabled server
  (`app.py:1068-1076`) and shutdown disconnects them from another (`app.py:1294`). Measured with
  the connect and the disconnect each in their own task, as the request handlers run them:

  ```
  children after connect: [3994701]
  Error closing MCP server t1: Attempted to exit cancel scope in a different task than it was entered in
  children after disconnect from a different task: []
  manager state: {'status': 'disconnected'} | sessions: [] | stacks: []
  ```

  The same warning appears for an HTTP server (`Error closing MCP server h1: …`). The exception
  comes from `TaskGroup.__aexit__`'s final `cancel_scope.__exit__` call
  (`anyio/_backends/_asyncio.py:846-853`), after the group collected its own errors — so the
  group's `BaseExceptionGroup` is replaced by the ownership error and the transport's real errors
  are dropped. The scope is never exited; in a probe whose connecting task was still alive, a later
  await in that task raised `CancelledError: Cancelled via cancel scope <the same scope>`.
- **Impact:** every disconnect — delete, disable, reconnect, shutdown — logs a warning that reads
  like a failure ("Error closing MCP server …"), and the transport's task-group shutdown does not
  happen: its errors are discarded and its cancel scope stays registered in anyio's per-task state.
  The child process is still terminated, because the SDK's `stdio_client` generator runs its
  `finally` (closing stdin, then SIGTERM/SIGKILL) before the task group is exited, and the probe
  shows no child surviving the disconnect; this is not an orphan-process defect. What is lost is
  the log's meaning and any error the transport itself raised, plus the possibility of a stray
  cancellation in the connecting task if it is still running when the disconnect arrives. Whether a
  real startup or route sequence reaches that last case was not established.
- **Fix:** give each server an owner task that holds its exit stack and performs the close there
  (the pattern the SDK's transports require), or have `connect_server` hand back a close callback
  that runs inside the connecting task. Catching `RuntimeError` here would only silence the log and
  leave the scope unexited.
