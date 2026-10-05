# routes: webhooks, vault, compare, hardware fit and shims

## Overview

Files in this section:

- `routes/webhook/__init__.py`
- `routes/webhook/webhook_routes.py`
- `routes/webhook_routes.py`
- `routes/hwfit_routes.py`
- `routes/compare/__init__.py`
- `routes/compare/compare_routes.py`
- `routes/compare_routes.py`
- `routes/vault/__init__.py`
- `routes/vault/vault_routes.py`
- `routes/vault_routes.py`
- `routes/diagnostics_routes.py`
- `routes/search/__init__.py`
- `routes/search/search_routes.py`
- `routes/search_routes.py`
- `routes/cleanup/__init__.py`
- `routes/cleanup/cleanup_routes.py`
- `routes/cleanup_routes.py`
- `routes/document_helpers.py`
- `routes/document_routes.py`
- `routes/gallery_helpers.py`
- `routes/gallery_routes.py`
- `routes/task_routes.py`

The remaining first-party route modules: outgoing webhook registration and last-delivery status,
token-authenticated synchronous chat, the vault, model comparison, hardware-fit detection,
diagnostics, search configuration and execution, session cleanup, and the five compatibility shims
(`routes/document_*`, `routes/gallery_*`, `routes/task_routes`) that alias their canonical
subpackage modules.

The boundary: authentication middleware is `core-auth-session`; database models are
`core-data-platform`; search execution is `services-search`; hardware detection and ranking are
`services-hwfit`. The document/gallery implementations belong to `routes-gallery-document`, and
the task implementation, including the incoming webhook receiver, belongs to
`routes-skills-calendar-task`. This section checks those five extra shims as aliases, not as
second implementations of their targets.

## Coverage

**Read fully:** all 22 assigned files (1,921 lines) listed in the Overview: the seven canonical
route modules, ten flat shims, and **five** package `__init__.py` files (including cleanup).
Working-tree citations refer to `2992bf6d368a`; `git status --short` showed only the untracked
`audit/` directory. Also read fully for the request/storage boundaries: the 7 items listed below.
Read the test harness `tests/conftest.py` and the three suites
`tests/test_hwfit_remote_validation.py`, `tests/test_search_routes_shim.py`, and
`tests/test_webhook_trigger_auth_exempt.py` fully.

- `core/middleware.py`
- `src/auth_helpers.py`
- `src/cleanup_service.py`
- `src/tools/vault.py`
- `services/search/core.py`
- `routes/_validators.py`
- `SECURITY.md`

**Read partially:**

- `app.py:259-518` (exempt paths, internal/loopback checks, bearer and cookie identity) and the
  seven routers' registration sites
- `core/database.py:175-284`, `:520-617`, `:648-680` (session/message, endpoint/comparison, and
  outgoing-webhook storage models)
- `core/platform_compat.py:39-159`, `:350-453` (permissions, process helpers and SSH execution)
- `services/hwfit/hardware.py:1-250`, `:710-908` (`_run`, initial GPU probes, visibility metadata
  and `detect_system`)
- `src/webhook_manager.py` by function/signature search and `:323-455` (delivery, signing, URL
  revalidation call sites and status writes)
- `services/search/providers.py:135-246` (SearXNG JSON search), plus provider/settings/HTTP-call
  searches
- `src/agent_tools/web_tools.py:1-100` and `src/deep_research.py:565-609` (offloaded search callers)
- `routes/cookbook_routes.py` at its admin-gate call sites and `:3135-3204` (GPU probing)
- `routes/session_routes.py:155-264` (raw-endpoint gate and neighbouring persistence helpers)
- `routes/task/task_routes.py` at webhook generation and update searches and `:1040` to end
  (incoming trigger, regeneration and neighbouring parser)
- `src/tool_security.py` at the vault blocklist and owner/delegated-tool gates

Read the audit rules, header, coverage boundaries, review scaffold and both supplied example
sections.

**Not read:** none of the assigned files. The document/gallery canonical modules were imported
for alias-identity checks, not source-reviewed. Task implementation outside the stated regions,
the scheduler behind its trigger, session-manager internals, hardware ranking/catalogue code,
search content transports, webhook transport internals, diagnostics' health/RAG/YouTube/research
callees, and the remaining database/auth/storage internals were not reviewed here. The other
54 selected test files were executed, not read end to end. No real provider, SSH host, GPU,
Bitwarden installation, browser deployment, or external webhook receiver was exercised.

**Checks run:** `git rev-parse --short=12 HEAD`, `git status --short`, `wc -l` over the 22 paths,
and the requested `ls tests | grep -iE 'webhook|hwfit|compare|vault|diagnostic|search|cleanup'`.
From that discovery, selected the seven module families plus blind-comparison coverage, rather
than unrelated research/session suites whose names also contain `search` or `cleanup`:

```sh
TEST_FILES=$(ls tests | grep -iE '^test_(webhook|hwfit|compare|vault|diagnostic|search|cleanup)|^test_blind_compare' | awk '{print "tests/" $0}')
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q -p no:cacheprovider $TEST_FILES
```

**57 files, 253 passed in 6.28s**, with one SQLAlchemy `declarative_base()` deprecation warning.

Two stdin Python probes used temporary data directories outside the checkout, an in-memory DB and
synthetic request state. Results appear below where they support findings. The probes checked:

- SSH reachability with a mocked runner
- event-loop execution with mocked search functions
- non-object JSON responses
- vault file modes
- all ten shim identities
- comparison ownership

All ten aliases were identical to their canonical module objects. The five typed JSON endpoints
(vault config, login and unlock; compare record; sync chat) returned 422 for both `[]` and a string.
The two search endpoints returned 200 with their missing-query error. So the non-object-body 500
class from `routes-rest-auth-admin` does not recur in this section's canonical handlers. The
adjacent task parser is outside this section's implementation scope.

Outgoing webhook management and all vault and diagnostics handlers require admin. The outgoing
webhook module has no unauthenticated receiver: `/api/v1/chat` additionally requires a chat-scoped
API token. None of these seven routers is auth-exempt.

The dynamic exemption is the task receiver's secret-bearing path. Its handler checks the stored
token and active status before asking the scheduler to run. It uses a reusable URL credential, not
a timestamped signature; repeated authorized triggers are intentional. External receivers' replay
checks were not tested.

Cleanup derives its owner from request state, not client input, and its service applies strict
owner filters to archival, deletion candidates and the protected recent-session set. It deletes
eligible session rows (messages have a cascading foreign key) and removes their cached sessions.
This pass did not establish cleanup of every ancillary file or table.

`audit.py` and run-level validation were not run, as instructed; integration and the secret gate
remain the parent's responsibility. No source, test, or other run file was edited.

### [SECURITY] Bearer callers share one comparison owner and can read and delete each other's records

- **Location:** `routes/compare/compare_routes.py:286`, `:310`, `:322-327`, `:348-358`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** record creation and history use the raw middleware username:

  ```python
  user = get_current_user(request)
  # record_comparison constructs Comparison(..., owner=user)
  ...
  user = get_current_user(request)
  ...
  if user:
      q = q.filter(Comparison.owner == user)
  ```

  Delete uses the same identity and rejects only `comp.owner != user`. For every valid bearer
  token, `app.py:458-464` stamps `request.state.current_user = "api"` while putting the token's
  real owner in a separate field on the same state object. `src/auth_helpers.py:10-12` returns the
  former unchanged.
  No comparison handler rejects bearer credentials or checks their scopes, and
  `app.py:815-816` registers the router without an additional dependency.

  A stdin probe run with `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -` mounted the real comparison
  router over a temporary SQLite table. Its middleware reproduced those bearer-state fields with
  distinct owners and chat scopes, without using real credentials. Alice recorded a synthetic
  comparison, then Bob requested history and deleted its returned id:

  ```text
  alice record: 200
  bob history: 200 contains alice record: True
  bob delete alice record: 200
  remaining records: 0
  ```

- **Impact:** token-created comparisons are shared between otherwise distinct owners. Another
  token holder can retrieve their prompt previews, model names and votes, then delete them.
  Normal browser-created comparisons retain their real owners and are not exposed by this
  particular path; the defect affects clients using bearer tokens on the comparison API. The
  probe tested route behavior with genuine middleware state shapes, not live token issuance.
- **Fix:** reject bearer callers with a router-level `require_user` dependency if comparisons are
  browser-only. If bearer comparison is supported, require an explicit scope and consistently use
  its resolved owner for creation, history, voting, deletion and endpoint lookup. Merely switching
  to `effective_user` without a scope gate would grant delegated credentials additional authority.

### [SECURITY] Hardware-fit routes let non-admins run server-side SSH probes against caller-selected hosts

- **Location:** `routes/hwfit_routes.py:182-191` (router and system route), `:319-332`, `:371` (profiles)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** neither the router nor its four endpoints has an administrative dependency:

  ```python
  router = APIRouter(prefix="/api/hwfit", tags=["hwfit"])
  ...
  def get_system(host: str = "", ssh_port: str = "", platform: str = "", fresh: bool = False):
      ...
      host, ssh_port = _validate_detection_target(host, ssh_port)
      return detect_system(host=host, ssh_port=ssh_port, platform=platform, fresh=fresh)
  ```

  `app.py:811-812` adds no dependency at registration. The middleware authenticates the caller
  but does not require admin for this path. `_validate_detection_target` checks syntax only.
  `services/hwfit/hardware.py:27-45` runs the fixed detection commands with `run_ssh_command`;
  `core/platform_compat.py:362-417` builds and executes ordinary `ssh`, using the server process's
  SSH configuration and credentials. The profiles route also passes a caller-supplied model path
  to `_inspect_model_path`, which runs directory/config/weight-size probes
  (`routes/hwfit_routes.py:137-170`). The comparable GPU route explicitly calls
  `require_admin(request)` (`routes/cookbook_routes.py:3160`).

  A stdin Python/FastAPI probe mounted the real hardware-fit router, stamped an ordinary user,
  supplied an auth manager whose `is_admin` returned false, and replaced only the hardware
  module's SSH runner with a recorder. A GET to `/api/hwfit/system` with a synthetic host,
  port 2222, Linux platform and a fresh scan produced:

  ```text
  hwfit non-admin HTTP: 200 SSH calls: 2 targets: [('audit-target.example', '2222')]
  ```

  No SSH connection was made by this probe.
- **Impact:** any signed-in user, and bearer callers without a hardware-management scope check,
  can make the service attempt SSH connections to chosen hosts and ports. Where the server's SSH
  credentials work, they can obtain hardware and limited model-directory metadata using the
  administrator's server-side access. This is not arbitrary shell-command execution: host/port
  validation and `shlex.quote` constrain the commands, and successful remote inspection still
  requires usable SSH access.
- **Fix:** apply `Depends(require_admin)` to the hardware-fit router, matching the cookbook
  probes. If non-admin model recommendations are required, expose cached/sanitized results
  separately without accepting a remote target, filesystem path or refresh operation.

### [PERF] Both search POST handlers execute synchronous network work on the event loop

- **Location:** `routes/search/search_routes.py:60-62`, `:103`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** both handlers are asynchronous but call blocking search functions directly:

  ```python
  context, sources = comprehensive_web_search(
      query, return_sources=True, time_filter=time_filter,
  )
  ...
  results = _call_provider(provider, query, min(count, 20))
  ```

  `_call_provider` dispatches synchronously (`services/search/core.py:96-110`), including to
  `httpx.get(..., timeout=15)` for SearXNG (`services/search/providers.py:186-192`). Comprehensive
  search also waits synchronously for its page-fetch futures
  (`services/search/core.py:368-384`); creating worker threads internally does not yield the
  calling event loop. The agent caller already offloads comprehensive search with
  `run_in_executor` (`src/agent_tools/web_tools.py:47-59`), and research uses
  `await asyncio.to_thread(_call_provider, ...)` (`src/deep_research.py:582`).

  A stdin Python probe called each real handler with a parsed JSON request and substituted a
  synchronous search recorder. Both recorders found the same running event loop as the handler.
  Each queued a `loop.call_soon` callback, which had not run when the handler returned and ran
  only after the probe yielded:

  ```text
  /api/search before handler return: [('provider_on_event_loop', True)]
  /api/search after yielding: [('provider_on_event_loop', True), ('callback', True)]
  /api/search/query before handler return: [('provider_on_event_loop', True)]
  /api/search/query after yielding: [('provider_on_event_loop', True), ('callback', True)]
  ```

- **Impact:** one authenticated standalone/Compare search prevents other coroutines in the same
  server worker from running while provider requests, retries and page fetching finish. A slow
  provider therefore stalls unrelated requests and streaming chat, rather than just the search
  caller. No real-network latency was measured; the synchronous execution path and the configured
  per-request timeout were verified.
- **Fix:** offload both search calls with `await asyncio.to_thread(...)`, as the research caller
  already does. Keep the provider socket timeouts; an outer coroutine timeout alone cannot stop
  a blocked worker thread.

### [SECURITY] The vault writer restricts permissions only after writing the session-bearing file

- **Location:** `routes/vault/vault_routes.py:72-77`, with the unlock write at `:199-202`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_save_config` writes directly to the destination before applying its promised
  private mode:

  ```python
  VAULT_FILE.parent.mkdir(parents=True, exist_ok=True)
  VAULT_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
  ...
  safe_chmod(str(VAULT_FILE), 0o600)
  ```

  Unlock places the CLI's returned session in `cfg` and calls this writer without requiring a
  pre-existing config file. A stdin Python probe redirected `VAULT_FILE` to a new temporary path,
  set umask 022, called the real `_save_config` with non-secret synthetic data, and wrapped
  `safe_chmod` to inspect the mode immediately before delegating to the real function:

  ```text
  vault first-write modes: ['0o644'] final: 0o600
  ```

  `core/platform_compat.py:40-55` also converts a chmod failure into `False`, which this caller
  does not inspect.
- **Impact:** on POSIX, a first unlock against an already logged-in CLI but absent `vault.json`
  can briefly publish the session-bearing file as world-readable under a typical umask. A local
  user who can traverse its parent directories can open it before chmod; an interrupted write
  before chmod leaves that mode in place. Existing files already at 0600 remain private, the
  normal save-config-before-unlock flow creates such a file first, restrictive directory modes
  mitigate access, and remote HTTP callers cannot read the session through the admin-only config
  endpoint. These conditions make this a low-severity local exposure, not an HTTP secret leak.
- **Fix:** create a same-directory temporary file with mode 0600 before writing, then atomically
  replace the destination. Fail rather than silently accept a permission-setting error on POSIX;
  preserve the separate Windows ACL policy.

