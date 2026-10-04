# src: agent tool implementations

## Overview

This section covers what a tool does once the dispatcher reaches it: the `TOOL_HANDLERS`
registry and the filesystem, shell, web, document, session, model-interaction, and admin tool
classes, plus the domain functions under `src/tools/` for notes, calendar, contacts, vault,
research, skills, scheduled tasks, the cookbook, and the generic internal-API bridge. The
dispatcher itself (`src/tool_execution.py`), the schemas (`src/tool_schemas.py`), and the
capability and policy tables (`src/tool_capabilities.py`, `src/tool_policy.py`) are assigned to
the three `src-tools-*` sections; the routes these tools call are assigned to the `routes-*` sections. A finding here
is about a tool's own behaviour, not about whether the dispatcher should have allowed the call.

## Coverage

**Read fully:** all 22 files (8,537 lines).

| File | Lines |
| --- | ---: |
| `src/tools/cookbook.py` | 1,713 |
| `src/agent_tools/filesystem_tools.py` | 1,140 |
| `src/agent_tools/document_tools.py` | 894 |
| `src/agent_tools/admin_tools.py` | 804 |
| `src/tools/system.py` | 737 |
| `src/tools/calendar.py` | 568 |
| `src/agent_tools/session_tools.py` | 493 |
| `src/agent_tools/subprocess_tools.py` | 383 |
| `src/tools/notes.py` | 332 |
| `src/agent_tools/model_interaction_tools.py` | 215 |
| `src/tools/vault.py` | 189 |
| `src/agent_tools/web_tools.py` | 171 |
| `src/tools/contacts.py` | 161 |
| `src/agent_tools/__init__.py` | 158 |
| `src/tools/research.py` | 146 |
| `src/agent_tools/bg_job_tools.py` | 98 |
| `src/agent_tools/interaction_tools.py` | 94 |
| `src/agent_tools/coding_tools.py` | 67 |
| `src/tools/image.py` | 66 |
| `src/tools/search.py` | 51 |
| `src/tools/__init__.py` | 32 |
| `src/tools/_common.py` | 25 |

Every cited line was re-read at `2992bf6d368a`.

**Read partially:**

- `src/tool_execution.py` only at the dispatch branches cited, to establish which handler runs with
  which `owner`
- its policy logic belongs to `src-tools-capabilities-policy`. `app.py` only at the bearer-token
  branch (`:314-337`, `:417-440`) cited in the `manage_tokens` finding
- the rest of the file belongs to `repository-root` and `build-install-deploy`.
  `routes/chat_routes.py` only at `:1552-1566`, the privilege-to-disabled-tools mapping that
  establishes `manage_research`'s reachability. `src/tool_security.py` only at the blocklist
  memberships quoted. `src/tool_schemas.py` only at the two schema entries quoted

**Not read:** the route implementations these tools call (`routes/gallery/gallery_routes.py`,
`routes/email_routes.py`, `routes/research/research_routes.py`, `routes/cookbook_routes.py`, and
the rest), beyond the lines cited as evidence. Whether a route accepts a tool's request is
established here only where a finding cites it. No test file was read.

### [SECURITY] The `app_api` path blocklist is bypassed by percent-encoded and dot-segment paths

- **Location:** `src/tools/system.py:669` (the check), with `:675` (the per-method check) and `:537-544` (the list)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `do_app_api` refuses a set of sensitive prefixes before sending the request, using
  the caller-supplied path string:

  ```python
  _APP_API_BLOCKLIST_PREFIXES = (
      "/api/auth", "/api/users", "/api/tokens", "/api/admin",
      "/api/shell", "/api/backup/restore",
  )
  ...
  if any(path.startswith(p) for p in _APP_API_BLOCKLIST_PREFIXES):
      return {"error": f"Path blocked for safety: {path}. ..."}
  ```

  The string that is checked is not the path the server routes. Two transformations happen after
  the check, and either one defeats it.

  The server percent-decodes. `uvicorn/protocols/http/h11_impl.py:205` sets
  `path = unquote(raw_path.decode("ascii"))`, and Starlette routes on that value. Measured against
  the running instance:

  ```
  $ for p in /nope-xyz /%61pi/nope-xyz /%61pi/health /api/health; do
      curl -s -m 3 -o /dev/null -w "$p -> %{http_code}\n" "http://127.0.0.1:7000$p"; done
  /nope-xyz -> 302
  /%61pi/nope-xyz -> 401
  /%61pi/health -> 200
  /api/health -> 200
  ```

  `/nope-xyz` is treated as a non-API path and redirected; `/%61pi/nope-xyz` is treated as the
  API path `/api/nope-xyz` (401, not 302); `/%61pi/health` reaches the health route.

  The client collapses dot segments. `do_app_api` sends with `httpx` (`:706-712`), and httpx
  0.28.1 normalizes the path before the request leaves the process, so no encoding is needed:

  ```
  $ venv/bin/python -c "<httpx.Request('GET', 'http://127.0.0.1:7000' + p).url.raw_path>"
  '/%61pi/tokens'      -> b'/%61pi/tokens'
  '/x/../api/tokens'   -> b'/api/tokens'
  '/./api/tokens'      -> b'/api/tokens'
  '/api/../api/tokens' -> b'/api/tokens'
  ```

  `/x/../api/tokens` does not start with `/api/tokens`, so it passes `:669`, and it is sent as
  `/api/tokens`. The per-method list at `:675` compares the same unnormalized string and is
  bypassed the same way, which includes `POST /api/cookbook/state`, the whole-file overwrite its
  comment records the agent performing once. No request carrying the internal token was sent to
  a blocked route in this pass; the two transformations were measured separately as shown.
- **Impact:** a path written as `/%61pi/tokens` or `/x/../api/tokens` executes with the internal
  tool headers against every class the list refuses in plain form: `/api/users`, `/api/tokens`
  (`routes/api_token_routes.py:130`), `/api/admin`, and `/api/shell`. Three things already bound
  this, and they set the severity:

  - `app_api` is refused for non-admins twice (`src/tool_security.py:65`, and the `_ADMIN_TOOLS`
    check at `src/tool_execution.py:1064`), so the caller is an administrator's agent.
  - `app_api` is registered with `ToolEffect.ADMIN_CHANGE` (`src/tool_capabilities.py:247-260`),
    which is in `POST_EXTERNAL_BLOCKED_EFFECTS` (`:553-565`). Once untrusted content has entered
    the run, `ToolRunSecurityContext.decision_for` (`:654-684`) blocks the call unless the user
    approves that exact action or has granted the chat session approval. A prompt injection
    arrives as untrusted content, so the injected call meets that gate first.
  - An administrator's agent normally also holds `bash`, which reaches the same host under the
    same gate. The list's own comment states its purpose as bounding "accidental account or
    command mistakes", not as a boundary against the administrator.

  What the bypass does remove is the guard in the configurations where it is the only one: an
  administrator who has switched `bash` off for the turn (`routes/chat_routes.py:1492-1493`) or
  listed it in the global `disabled_tools` setting still has `/api/shell` reachable through
  `app_api`, and a run with chat-session approval has no second check. The mechanism does not
  deliver what it claims; it is not an escalation past a boundary the caller did not already hold.
- **Fix:** normalize before checking, and check what will be routed: reject a path containing
  `%`, a `.` or `..` segment, or `//`, then compare path segments instead of string prefixes. A
  test that runs each blocked prefix through the encoded and dot-segment forms belongs beside it.
- **Re-review (2026-10-04):** re-derived in full and lowered from high. The first pass recorded
  the percent-encoding bypass, cited the list (`:537`) as the location, and described a
  prompt-injected token mint without the post-untrusted-content gate. This pass added the
  dot-segment bypass, moved the location to the check, and restated the impact with the three
  mitigations above. The finding was retitled, so its ID changed.

### [SECURITY] `manage_research` ignores the owner and operates on every user's research files

- **Location:** `src/tools/research.py:17`
- **Severity:** high
- **Disposition:** next
- **Evidence:** the function accepts `owner` and never reads it — the name appears only in the
  signature. All three actions operate on the shared directory without a filter:

  ```python
  async def do_manage_research(content: str, owner: Optional[str] = None) -> Dict:
      ...
      for p in data_dir.glob("*.json"):          # list: every user's file
  ```

  `read` loads `data_dir / f"{rid}.json"` and returns its body (`:48-62`); `delete` unlinks the
  same path (`:64-73`). The saved JSON carries an owner — `src/research_handler.py:628-629` stamps
  it with the comment "SECURITY: stamp owner so route handlers can filter by user" — and the HTTP
  library route enforces that field:

  ```python
  # SECURITY: only show research belonging to this user. Legacy
  # JSONs without an `owner` field are hidden — auth was the only
  # gate before, so every user saw every other user's reports.
  if d.get("owner") != user:
      continue
  ```

  (`routes/research/research_routes.py:381-385`.) `manage_research` is not in
  `NON_ADMIN_BLOCKED_TOOLS` (`src/tool_security.py:42-70`), and no privilege disables it. The
  per-user privilege block at `routes/chat_routes.py:1546-1566` adds tools to `disabled_tools` for
  `can_use_bash`, `can_use_browser`, `can_use_documents`, `can_generate_images` and
  `can_manage_memory`; for `can_use_research` it only clears a flag:

  ```python
  if not _privs.get("can_use_research", True):
      _research_flags["do"] = False
  ```

  `_research_flags` gates the research pre-pass (`:1620`), not the tool. Every user who can use
  agent mode therefore reaches `manage_research`, including one whose research privilege an
  administrator removed. The dispatcher passes the caller's `owner` (`src/tool_execution.py:1246`),
  and the function drops it.
- **Impact:** a user's agent can list every user's research titles and ids, read any report body
  (the report can quote private mail or web content), and delete any report. The delete path is
  destructive and irreversible. The route's own comment shows this leak class was already treated
  as worth fixing once; the tool path was not given the same filter.
- **Fix:** filter the scan by `d.get("owner") == owner`, and on read/delete load the JSON and
  return not-found unless the owner matches, hiding existence as the route does. Hide owner-less
  legacy files from authenticated callers, matching the route.
- **Re-review (2026-10-04):** re-derived in full; high stands. `owner` appears in
  `src/tools/research.py` only in the two signatures and in the `_internal_headers(owner)` call of
  the other function. The preconditions are a second account and nothing else: `list` returns the
  ids that `read` and `delete` take. The first pass said `routes/chat_routes.py:1562` disables the
  tool for callers without `can_use_research`; that line does not touch `disabled_tools`, so the
  evidence above was corrected and the reach is wider than first stated.

### [BUG] `edit_image` calls four routes that do not exist

- **Location:** `src/tools/image.py:33`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the schema advertises four actions — `"enum": ["upscale", "rembg", "inpaint",
  "harmonize"]` (`src/tool_schemas.py:1042`) — and the implementation posts a JSON body to a
  constructed path:

  ```python
  resp = await client.post(f"{_INTERNAL_BASE}/api/gallery/{action}", json=payload)
  ```

  No POST route matches `/api/gallery/upscale`, `/api/gallery/rembg`, `/api/gallery/inpaint`, or
  `/api/gallery/harmonize`. The gallery router's POST paths are `upload`, the `{image_id}/…`
  sub-routes, `ai-upscale`, `style-transfer`, `albums`, tag jobs, `download-zip`, and the tag
  maintenance routes; background removal, inpaint, and harmonize live under `/api/image/`. None
  of them implements the tool's contract of taking `image_id` JSON and returning a new image id:
  `ai-upscale` reads a multipart `image` file, and the `/api/image/*` handlers expect image and
  mask payloads. The call also omits `_internal_headers(owner)`, so even a matching route would
  fail `require_privilege` in auth-enabled mode. Every action falls into the error branch with
  `data.get("error", f"{action} failed")` on a 404 JSON body.
- **Impact:** the `edit_image` tool is non-functional for all four advertised actions. The model
  either reports a bare failure or retries; no image is ever modified.
- **Fix:** point each action at the real route with the shape it expects (multipart upload for
  `ai-upscale`; image/mask bodies for inpaint, harmonize, and remove-background) and pass
  `_internal_headers(owner)`, or remove the tool from the schema and registry until it is wired.

### [BUG] `manage_tokens` mints tokens the middleware cannot authenticate

- **Location:** `src/agent_tools/admin_tools.py:466`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `create` builds the raw token without the `ody_` prefix and constructs `ApiToken`
  with no `owner` and no `scopes`:

  ```python
  raw_token = secrets.token_urlsafe(32)
  token_hash = bcrypt.hashpw(raw_token.encode(), bcrypt.gensalt()).decode()
  ...
  t = ApiToken(id=tid, name=name, token_hash=token_hash,
               token_prefix=raw_token[:8], is_active=True, ...)
  ```

  The middleware enters bearer handling only for `Bearer ody_...`
  (`app.py:418`), and the token cache drops any active row whose owner does not resolve to a
  known user (`app.py:323-330`), which includes `owner IS NULL`. The other two construction
  sites set all three fields: `routes/api_token_routes.py:130-141` builds
  `"ody_" + secrets.token_urlsafe(32)` with `owner=owner` and `scopes=scopes_value`, and
  `companion/pairing.py:196` sets them too.
- **Impact:** the tool reports "Created token 'x'" and returns the raw token, but that token is
  rejected as an invalid bearer for lack of the prefix, and the cache would skip it even if the
  prefix were present. An admin who asks the agent to mint an integration token receives a dead
  credential. The `list` and `delete` actions are unscoped, but the tool is admin-blocked
  (`src/tool_security.py:61`), so that part stays inside admin authority.
- **Fix:** build the token exactly as the admin route does — `"ody_" + secrets.token_urlsafe(32)`,
  `owner=owner`, and a `scopes` value — and factor the construction into one helper so the three
  sites cannot drift again.

### [PERF] `list_models` probes endpoints with synchronous HTTP on the event loop

- **Location:** `src/agent_tools/model_interaction_tools.py:163`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `list_models` is an `async def`, but it calls the synchronous `httpx.get` once per
  enabled endpoint, sequentially, and the handler awaits it on the event loop:

  ```python
  for ep in endpoints:
      ...
      models_url = build_models_url(base)
      if models_url:
          r = httpx.get(models_url, headers=headers, timeout=5)
  ```

  Nothing offloads the call. The same file uses `asyncio.to_thread` for `_resolve_model`
  (`:50`, `:82`), and the surrounding tool layer runs on the loop (the registry handler
  `ListModelsTool.execute` awaits this function directly). `list_models` is not in
  `NON_ADMIN_BLOCKED_TOOLS` (`src/tool_security.py:42-70`).
- **Impact:** each enabled endpoint blocks the entire process for up to 5 seconds; ten configured
  endpoints stall every concurrent request for up to 50 seconds. Any user's agent can trigger it.
- **Fix:** use an `httpx.AsyncClient` (or `asyncio.to_thread`) and probe the endpoints
  concurrently with `asyncio.gather` and a bounded per-endpoint timeout.

### [BUG] `adopt_served_model`'s endpoint registration always fails on a key mismatch

- **Location:** `src/tools/cookbook.py:1361`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the adopt path calls `do_manage_endpoints` with `endpoint_url`:

  ```python
  ep_result = await do_manage_endpoints(json.dumps({
      "action": "add",
      "name": display_name,
      "endpoint_url": endpoint_url,
      "is_local": False,
  }), owner=owner)
  ```

  `do_manage_endpoints` reads `args.get("base_url", "")` and returns `{"error": "base_url is
  required"}` when it is absent (`src/agent_tools/admin_tools.py:42-44`). Registration is the
  default branch (`add_endpoint = args.get("add_endpoint", True)`), so the output always ends
  with "Endpoint registration skipped: base_url is required".
- **Impact:** an adopted server is tracked in cookbook state but never appears in the endpoint
  list, which is the second half of what the tool's docstring promises. The user must add it
  manually. The adoption and health-check paths still work.
- **Fix:** send `"base_url": endpoint_url`, and drop `is_local`, which `do_manage_endpoints` also
  ignores; or accept `endpoint_url` as an alias in `do_manage_endpoints`.

### [BUG] `resolve_contact`'s email-history lookup sends no internal tool headers

- **Location:** `src/tools/contacts.py:59`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the CardDAV leg runs in-process with a comment explaining why, but the
  email-history leg goes over HTTP with no headers:

  ```python
  resp = await client.get(f"{_INTERNAL_BASE}/api/email/resolve-contact", params={"name": name})
  ```

  The route depends on `require_owner` (`routes/email_routes.py:4471`), which authenticates the
  request. Every other loopback call in this section passes `_internal_headers(owner)` (for
  example `src/tools/research.py:123`, `src/tools/system.py:698`). The surrounding
  `except Exception: pass` swallows the resulting 401.
- **Impact:** in an auth-enabled deployment, email history silently contributes nothing to
  `resolve_contact`; only CardDAV results are returned. In auth-disabled single-user mode the
  route accepts the unauthenticated call, so the bug is invisible there.
- **Fix:** pass `headers=_internal_headers(owner)` and log the failure instead of swallowing it,
  or call the mail-search helper in-process like the CardDAV leg.

### [DEAD-CODE] `todowrite` persists a per-session file that nothing reads

- **Location:** `src/agent_tools/coding_tools.py:55`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the tool writes `data/agent_todos/<session>.json`:

  ```python
  path = os.path.join(_TODO_DIR, f"{session_id}.json")
  with open(path, "w", encoding="utf-8") as f:
      json.dump({"todos": normalized}, f, ensure_ascii=False, indent=2)
  ```

  A repository-wide search for `agent_todos` (Python files, excluding `audit/`) returns only this
  module: `_TODO_DIR` is defined here, and nothing reads the file — not the tool, not a route,
  not the frontend's server side. The session id comes from `ctx` or the caller's JSON
  (`args.get("session_id")`), so the path is not an owner-keyed store either.
- **Impact:** none at runtime — the tool's return value carries the list — but the on-disk state
  is write-only. Nothing resumes from it after a restart, and no reader exists to point at it, so
  it presents persistence that does not exist.
- **Fix:** delete the file write, or add the reader that makes it meaningful and key it by owner
  and session.

### [DEAD-CODE] The facade's `SHELL_TIMEOUT` and `PYTHON_TIMEOUT` are unused and disagree with the shell defaults

- **Location:** `src/agent_tools/__init__.py:75`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the module defines them under a comment that names `src.constants` as the single
  source of truth:

  ```python
  # Constants (re-exported for backward compatibility — single source of truth
  # is src.constants; always prefer importing from there for new code)
  MAX_AGENT_ROUNDS = 50
  SHELL_TIMEOUT = 60
  PYTHON_TIMEOUT = 30
  ```

  `src/constants.py` defines none of the three. `MAX_AGENT_ROUNDS` is imported from here by
  `src/agent_loop.py:68` and `routes/chat_routes.py:2311`; `SHELL_TIMEOUT` and `PYTHON_TIMEOUT`
  have no reader anywhere in the repository. The timeouts the shell tools actually use are
  `DEFAULT_BASH_TIMEOUT` and `DEFAULT_PYTHON_TIMEOUT`, both 3600
  (`src/agent_tools/subprocess_tools.py:12-13`).
- **Impact:** the constants are a trap for the next caller: importing `SHELL_TIMEOUT` expecting
  the tool's timeout yields 60, not 3600, and the comment sends readers to a module that does not
  define it.
- **Fix:** remove the two unused constants and correct the comment, or move `MAX_AGENT_ROUNDS`
  into `src.constants` where the comment claims it lives.
