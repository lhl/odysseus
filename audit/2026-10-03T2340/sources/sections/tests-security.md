# tests: security, guard and prompt-injection

## Overview

`tests/test_auth_config_lock_concurrency.py`, `tests/test_auth_disabled_document_access.py`, `tests/test_auth_event_loop.py`, `tests/test_auth_policy.py`, `tests/test_auth_regressions.py`, `tests/test_auth_require_privilege_nondict.py`, `tests/test_auth_root_path.py`, `tests/test_auth_session_revocation.py`, `tests/test_db_stubs_helper.py`, `tests/test_is_youtube_url_nonstring.py`, `tests/test_is_youtube_url_nonstring_svc.py`, `tests/test_pr_blocker_audit.py`, `tests/test_pr_description_check.py`, `tests/test_prompt_injection_audit.py`, `tests/test_prompt_security.py`, `tests/test_security_headers_middleware.py`, `tests/test_security_headers_pdf_preview.py`, `tests/test_security_regressions.py`, `tests/test_token_cache_atomic_swap.py`, `tests/test_vault_password_not_in_argv.py`, `tests/test_vault_routes_shim.py`.

This section asks what these tests prove, not whether they pass. A test that passes without
exercising the guard it names is worse than no test, because it is counted as coverage. The
question for each file is therefore: what is the assertion, what is the fixture, and which
behaviour would have to break for the assertion to fail?

The boundary: the test harness itself (`tests/conftest.py`, `tests/helpers/*`,
`tests/run_focus.py`, `tests/TESTING_STANDARD.md` as an artifact) belongs to `tests-harness`; it
is cited here only as the repository's own rulebook for what a test is required to do. The
production code these files pin belongs to the matching `src-*`, `routes-*`, `core-*` and
`services-*` sections. Where a weak test maps onto a defect another section already reports, the
finding cross-references it instead of restating it — `src-security` for the
`require_privilege` fail-open, `services-media` for the `is_youtube_url` substring match,
`repository-root` for the `X-Odysseus-Owner` override, `build-install-deploy` for the compose
bind assertions.

## Coverage

**Read fully:** all 21 assigned files, 5,731 lines — `tests/test_auth_config_lock_concurrency.py`
(240), `tests/test_auth_disabled_document_access.py` (280), `tests/test_auth_event_loop.py` (118),
`tests/test_auth_policy.py` (363), `tests/test_auth_regressions.py` (370),
`tests/test_auth_require_privilege_nondict.py` (36), `tests/test_auth_root_path.py` (283),
`tests/test_auth_session_revocation.py` (173), `tests/test_db_stubs_helper.py` (121),
`tests/test_is_youtube_url_nonstring.py` (14), `tests/test_is_youtube_url_nonstring_svc.py` (13),
`tests/test_pr_blocker_audit.py` (964), `tests/test_pr_description_check.py` (327),
`tests/test_prompt_injection_audit.py` (261), `tests/test_prompt_security.py` (203),
`tests/test_security_headers_middleware.py` (67), `tests/test_security_headers_pdf_preview.py`
(36), `tests/test_security_regressions.py` (1,546), `tests/test_token_cache_atomic_swap.py` (188),
`tests/test_vault_password_not_in_argv.py` (117), `tests/test_vault_routes_shim.py` (11).

**Read partially — the code each finding rests on:** `app.py:376-396` (the internal-tool
impersonation branch); `routes/mcp/mcp_routes.py` handler definitions and `require_admin` call
sites (`:121-123`, `:382-391`); `routes/diagnostics_routes.py` (`:25-96`); `src/auth_helpers.py`
(`:163-188`); `routes/task/task_routes.py:427-465`; `src/task_action_policy.py` (whole, 47 lines);
`src/constants.py:12-25`; `src/runtime_paths.py:20-30`; `core/auth.py` (`:52`, `:93-104`,
`:255-280`); `services/youtube/youtube_handler.py:61-64`; `src/youtube_handler.py` (whole, 23
lines); `.github/scripts/check-pr-description.js:128-184`;
`tests/TESTING_STANDARD.md:88-134`; `tests/helpers/import_state.py` (whole);
`tests/conftest.py:42-53`; `tests/helpers/db_stubs.py` (via its self-test).

**Not read:** the production code behind the assertions this section did not need to evaluate —
`src/prompt_security.py` beyond what `test_prompt_security.py` quotes, `src/agent_loop.py` beyond
the `_build_system_prompt` call contract, `src/visual_report.py`, `services/search/content.py`,
`routes/vault/vault_routes.py`, `core/middleware.py` beyond `SecurityHeadersMiddleware`, and every
other section's paths. `scripts/pr_blocker_audit.py` was skimmed by the `scripts` section, not
re-read here. Line numbers are the working tree at `2992bf6d368a`.

**Checks run:** the 21 assigned files in one process, and each failing group in isolation:

```
$ venv/bin/python -m pytest -q <the 21 files>
10 failed, 292 passed, 1 warning, 7 errors in 38.10s

$ venv/bin/python -m pytest -q -m area_security          # broader lane, 832 tests
832 passed, 5124 deselected, 19 warnings in 43.37s
```

The 309 collected tests include five `@pytest.mark.slow` concurrency tests
(`test_auth_config_lock_concurrency.py:66`, `:105`, `:133`, `:159`, `:206`) that a plain pytest
invocation runs and only the documented fast lane (`not slow`, `tests/README.md:50-55`) excludes.
**Zero xfail.** Two conditional skips exist and neither triggered: `test_pr_description_check.py:14`
skips when `node` is absent (`node v24.16.0` here, so all 19 tests ran) and
`test_security_regressions.py:102-105` skips the key-file mode assertion on `win32` (POSIX here).
Probes under `/tmp/audit-probe/` are quoted in the findings that use them; none is part of the
target tree.

### [BUG] `tests/test_auth_regressions.py` leaves empty module stubs in `sys.modules`, so a focused run of these suites fails 17 tests

- **Location:** `tests/test_auth_regressions.py:305` (with `:61`, `:87-89`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the module plants empty modules at runtime and never removes them:

  ```python
  # :305-309, inside test_pop_notifications_owner_filtered
  for s in ["src.builtin_actions", "src.ai_interaction", "src.endpoint_resolver",
            "src.agent_loop", "src.session_manager"]:
      if s not in sys.modules:
          mod = types.ModuleType(s)
          sys.modules[s] = mod
  ```

  Its autouse fixture does the same for `src.endpoint_resolver` through `_ensure_stub`, which
  writes `sys.modules` directly (`:61`) and is then wrapped in `monkeypatch.setitem` (`:87-89`).
  Because the entry already exists when `setitem` records it, the fixture's teardown restores the
  stub rather than removing it. Measured after running the file alone, in
  `pytest -q -s tests/test_auth_regressions.py /tmp/audit-probe/probe_module_state.py`:

  ```
  PROBE src.agent_loop: file=None type=module has_build_system_prompt=False
  PROBE src.endpoint_resolver: file=None type=module has_build_system_prompt=False
  ```

  The consequence is a two-module, order-dependent failure that reproduces in pairs:

  ```
  $ venv/bin/python -m pytest -q tests/test_auth_regressions.py tests/test_prompt_injection_audit.py
  9 failed, 15 passed, 1 warning in 0.31s
      ImportError: cannot import name '_build_system_prompt' from 'src.agent_loop' (unknown location)

  $ venv/bin/python -m pytest -q tests/test_prompt_injection_audit.py tests/test_auth_regressions.py
  24 passed, 1 warning in 0.45s

  $ venv/bin/python -m pytest -q tests/test_auth_regressions.py tests/test_token_cache_atomic_swap.py
  15 passed, 1 warning, 7 errors in 1.06s
      ImportError: cannot import name 'resolve_utility_fallback_candidates' from
      'src.endpoint_resolver' (unknown location)   # src/task_endpoint.py:3

  $ venv/bin/python -m pytest -q tests/test_auth_regressions.py "tests/test_security_regressions.py::test_inprocess_pollers_gate"
  1 failed, 15 passed, 1 warning in 0.23s
  ```

  Over the whole assigned set the same collision produces `10 failed, 292 passed, 7 errors`.
  `tests/TESTING_STANDARD.md:93` says "never assign at module scope" for `sys.modules` and
  `:112-113` says "a test must not depend on a sibling having imported, cached, or stubbed
  something first. Order-sensitivity is a bug to fix". `tests/helpers/import_state.py` exists for
  exactly this and is not used here. The same module-scope pattern appears in
  `tests/test_prompt_injection_audit.py:22-30`, which replaces `core.database`, `core.models`,
  `src.agent_loop`'s dependencies and `sqlalchemy` with `MagicMock()` at import time (guarded by
  `if _mod not in sys.modules`); I did not measure a failure from that one because collection order
  happened to import those modules first.
- **Impact:** a subset that includes these files but not the files that happen to import the real
  modules first fails 17 tests, so the selection, not the code under test, decides the outcome. The
  failures are loud here, but the same stub can equally silence a test that consumes a stubbed
  resolver. The full `area_security` lane passes (832) only because some earlier file happens to
  import the real modules first.
- **Fix:** plant the stubs through `monkeypatch.setitem` only (never a bare
  `sys.modules[s] = mod`), so teardown removes what was added, and add
  `tests.helpers.import_state.clear_fake_endpoint_resolver_modules()` where a stub must outlive a
  single test. `tests/helpers/db_stubs.py:32` shows the pattern done correctly, and the
  `test_db_stubs_helper.py` self-test in this section verifies its undo behaviour.

### [FOOTGUN] `_make_manager` overwrites the real password hasher on the live `core.auth` module and does not restore it

- **Location:** `tests/test_auth_policy.py:36` (with `tests/test_auth_session_revocation.py:36-37`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** both files build their manager by mutating the imported module object, outside any
  fixture teardown:

  ```python
  # tests/test_auth_policy.py:34-39
  def _make_manager(tmp_path):
      auth_mod = _auth_module()
      auth_mod._hash_password = lambda password: f"hash:{password}"
      auth_mod._verify_password = lambda password, hashed: hashed == f"hash:{password}"
  ```

  `_auth_module()` re-imports `core.auth` and leaves the mutated object in `sys.modules`. Measured
  with `pytest -q -s "tests/test_auth_policy.py::test_policy_returns_password_min_length" /tmp/audit-probe/probe_hash_password.py`:

  ```
  PROBE core.auth._hash_password is: <function _make_manager.<locals>.<lambda> at 0x...>
  PROBE core.auth._verify_password is: <function _make_manager.<locals>.<lambda> at 0x...>
  PROBE _hash_password('secret') -> hash:secret
  ```

  `tests/test_auth_session_revocation.py` reproduces it from a single-test selection. Inside a
  full-file run the mutation is usually discarded, because the next `_real_core_package()` call
  clears and re-imports the module, which is why no downstream failure was produced: I ran the
  single policy test followed by `test_rename_user_owner_sync.py`,
  `test_delete_user_revokes_api_tokens.py`, `test_api_token_routes.py` and `test_set_admin.py` and
  got `66 passed`. The leak is therefore real but only bites under a selection or order where a
  later test consumes `core.auth` without re-importing it.
- **Impact:** bcrypt hashing and verification silently become a string-formatting fake for the
  rest of the process. A later test that asserts a stored password is hashed, or that
  `verify_password` rejects a wrong password, can pass against the fake instead of the real
  dependency. The two files that do this safely — `tests/test_rename_user_owner_sync.py:98` and
  `tests/test_delete_user_revokes_api_tokens.py:76` — use `monkeypatch.setattr`.
- **Fix:** replace the two assignments with `monkeypatch.setattr(auth_mod, "_hash_password", ...)`
  (the same for `_verify_password`), or pass a fake hasher into `AuthManager`.

### [SECURITY] The test that claims to pin `app.AuthMiddleware`'s impersonation check asserts on a local copy of the logic

- **Location:** `tests/test_security_regressions.py:768`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the test defines the branch it is supposed to pin and asserts only on that local
  function:

  ```python
  # :768-785
  def test_internal_tool_owner_header_logic_requires_known_user():
      """Pin the owner-attribution branch used by app.AuthMiddleware without
      booting the full FastAPI app."""
      users = {
          "alice": {"is_admin": False},
          "AdminUser": {"is_admin": True},
      }

      def resolve_owner(header_value):
          impersonate = (header_value or "").strip()
          if impersonate and impersonate in users:
              return impersonate
          return "internal-tool"

      assert resolve_owner("alice") == "alice"
      assert resolve_owner("doesnotexist") == "internal-tool"
  ```

  The file never imports `app`; the only occurrence of `AuthMiddleware` in it is that docstring
  (`grep -n "import app\|\bapp\.py\|AuthMiddleware" tests/test_security_regressions.py` returns
  `769:    """Pin the owner-attribution branch used by app.AuthMiddleware without`). The real
  branch is `app.py:390-395`:

  ```python
  _impersonate = (request.headers.get("X-Odysseus-Owner") or "").strip()
  _auth_mgr = getattr(request.app.state, "auth_manager", None) or auth_manager
  if _impersonate and _impersonate in getattr(_auth_mgr, "users", {}):
      request.state.current_user = _impersonate
  else:
      request.state.current_user = INTERNAL_TOOL_USER
  ```

  Because the assertion is against a re-implementation, deleting the membership check from
  `app.py` (making every header value impersonate, including a user that does not exist) leaves
  the test green. `repository-root.md:195` documents the override itself but reports the
  missing documentation, not the missing pin; this finding is about the test only.
- **Impact:** the guard that decides which user an in-process agent call is attributed to — the
  `X-Odysseus-Owner` path over a loopback request carrying the internal tool token — has no
  regression test. A change that broadens impersonation to unknown or admin usernames would ship
  with the suite green, and the test's name would be cited as evidence that it cannot.
- **Fix:** drive the real middleware with a Starlette app the way
  `tests/test_auth_root_path.py:120-283` already does, or import the branch's helper out of
  `app.py` and call it. If a real drive is impractical, assert on `app.py`'s source only as an
  explicitly-labelled proxy — but then it is still not a pin of the behaviour.

### [SECURITY] `test_token_cache_atomic_swap.py` bootstraps the application's live data directory with an admin account

- **Location:** `tests/test_token_cache_atomic_swap.py:34`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the fixture imports the real `app` and calls first-run setup on the real manager:

  ```python
  # :24-34
  monkeypatch.setenv("AUTH_ENABLED", "true")
  monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
  ...
  import app as app_mod
  app_mod.SessionLocal = MagicMock()
  app_mod.logger = MagicMock()
  app_mod.auth_manager.setup("admin", "<hardcoded password literal>")
  ```

  Nothing sets `ODYSSEUS_DATA_DIR`, and `app.auth_manager` is `AuthManager(AUTH_FILE)` where
  `AUTH_FILE = os.path.join(DATA_DIR, "auth.json")` and `DATA_DIR` defaults to `<repo>/data`
  (`src/constants.py:12`, `src/runtime_paths.py:20-30`); verified with
  `venv/bin/python -c "from src.constants import AUTH_FILE; print(AUTH_FILE)"` →
  `/home/lhl/github/lhl/odysseus/data/auth.json`. `data/` is ignored (`.gitignore:28`), so a fresh
  clone has no `data/auth.json`. Running the file against an empty data directory shows what the
  test creates (`rm -rf /tmp/audit-probe/data && ODYSSEUS_DATA_DIR=/tmp/audit-probe/data
  venv/bin/python -m pytest -q tests/test_token_cache_atomic_swap.py` → `7 passed`):

  ```
  -rw------- 1 lhl lhl 596 auth.json
  $ python -c "import json;d=json.load(open('/tmp/audit-probe/data/auth.json'));print({u: sorted(v.keys()) for u,v in d['users'].items()})"
  {'admin': ['created', 'is_admin', 'password_hash', 'privileges']}
  ```

  A control run with the same empty directory shows the import alone is not the cause: `import app`
  leaves `auth.json` absent and `is_configured: False`; the `setup(...)` call in the fixture is what
  writes the account. The repository's own `data/auth.json` was not modified by my runs
  (`sha256sum` unchanged, `git status --porcelain` still shows only `?? audit/`).
- **Impact:** a developer or CI job that runs this file before ever configuring Odysseus gets an
  install that already has an `admin` account whose password is a literal in the test source, and
  the first-run setup screen never appears (`is_configured` is now true). On a machine where the
  app is later exposed, that account is a published credential.
- **Fix:** point the test at an isolated data directory — set `ODYSSEUS_DATA_DIR` to `tmp_path`
  before importing `app`, or construct the `AuthManager` on `tmp_path / "auth.json"` instead of
  calling setup on the process-global manager.

### [BUG] Five regression tests in `test_security_regressions.py` assert on source text, so the guard can be deleted without a failure

- **Location:** `tests/test_security_regressions.py:863` (with `:999`, `:1009`, `:1019`, `:1190`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `test_mcp_config_listing_is_admin_gated` asserts only that three handler
  signatures exist:

  ```python
  # :863-868
  def test_mcp_config_listing_is_admin_gated():
      from routes import mcp_routes
      src = Path(mcp_routes.__file__).read_text()
      assert "def list_servers(request: Request):" in src
      assert "def list_tools(request: Request):" in src
      assert "def list_server_tools(server_id: str, request: Request):" in src
  ```

  Mutation probe: deleting every `require_admin(request)` statement from the canonical
  `routes/mcp/mcp_routes.py` (11 calls, including `:123`, `:384` and `:391`) into
  `/tmp/audit-probe/mcp_routes_mutated.py` leaves all three assertions true:

  ```
  require_admin calls: original=11 mutated=0
  assert 'def list_servers(request: Request):' in mutated_source -> True
  assert 'def list_tools(request: Request):' in mutated_source -> True
  assert 'def list_server_tools(server_id: str, request: Request):' in mutated_source -> True
  ```

  The same shape recurs: `test_diagnostics_routes_are_admin_gated` (`:999-1006`) asserts four
  signatures plus `text.count("require_admin(request)") >= 4`, which stays true if one of the four
  handlers loses its gate and an unrelated handler keeps one (the file has six gated handlers
  today, `routes/diagnostics_routes.py:28`, `:34`, `:58`, `:68`, `:75`, `:96`);
  `test_email_thread_rendering_sanitizes_body_html` (`:1009-1017`) asserts
  `text.count("t.body_html") == text.count("_sanitizeHtml(t.body_html")`, which holds even if
  `_sanitizeHtml` becomes an identity function; `test_session_html_export_escapes_name`
  (`:1019-1025`) asserts an `html.escape(...)` assignment and two absent f-strings;
  `test_chat_active_document_lookup_is_owner_scoped` (`:1190-1205`) asserts three
  `_owner_session_filter(..., ctx.user)` call strings. `tests/TESTING_STANDARD.md:118-123` names
  this pattern ("Avoid `read_text()` + substring assertions ... can pass even when behavior
  regresses") and permits it only where the invariant cannot be driven at runtime (`:128-132`).
  These five can be: the mcp and diagnostics gates are reachable with `TestClient` and a
  non-admin session, the email sanitizer through the existing Node wrapper, and the chat document
  lookup through a seeded temp DB, which is the standard's own example.
- **Impact:** each of these is a claimed regression pin that cannot detect the regression it
  describes. A reviewer reading the test names would conclude that MCP config listing, diagnostics
  admin gating, email HTML sanitization, session-export escaping and chat active-document owner
  scoping are covered; only the code's current text is.
- **Fix:** drive the route with a non-admin caller and assert the 403, and for the JS path call
  `_sanitizeHtml` on a payload through the Node harness. Where a source assertion must stay, say in
  the docstring which behaviour it stands in for.

### [DOC-DRIFT] `test_auth_event_loop.py` claims to prove bcrypt runs off the event loop, but its fixture runs the calls on the loop thread

- **Location:** `tests/test_auth_event_loop.py:87`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the docstring says "This test asserts those calls run on a worker thread, not the
  loop thread; it fails if they are awaited inline again" (`:12-13`), and the test's fixture
  replaces `asyncio.to_thread` with a coroutine that calls the function directly:

  ```python
  # :91-94
  async def fake_to_thread(fn, *args, **kwargs):
      calls.append(fn)
      return fn(*args, **kwargs)
  ```

  With that fixture the calls run on the caller's thread. Measured by re-running the same fixture
  shape in `/tmp/audit-probe/probe_to_thread_ident.py`:

  ```
  event-loop thread ident: 140463735031680
  <MagicMock name='mock.verify_password' ...>: thread 140463735031680 -> on the event-loop thread: True
  <MagicMock name='mock.create_session_trusted' ...>: thread 140463735031680 -> on the event-loop thread: True
  ```

  The test does prove something useful — `assert calls == [auth.verify_password,
  auth.create_session_trusted]` (`:118`) fails if the handler stops routing those two calls through
  `asyncio.to_thread` — but "runs on a worker thread" is not what it establishes.
- **Impact:** a future change that keeps the `to_thread` call but blocks the loop elsewhere (for
  example an added synchronous bcrypt call the assertion list does not name, or a `to_thread` that
  is awaited inside another blocking section) would not be distinguished by this test, while the
  docstring asserts the stronger property.
- **Fix:** assert the thread identity the way the probe does (compare `threading.get_ident()`
  inside the patched function against the loop thread), or reword the docstring to say the test
  pins the call routing, not the offload.

### [BUG] `test_require_privilege_still_blocks_disallowed` accepts any exception, and its sibling pins fail-open as the contract

- **Location:** `tests/test_auth_require_privilege_nondict.py:35` (with `:22-29`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the negative test asserts only that something was raised:

  ```python
  # :32-36
  def test_require_privilege_still_blocks_disallowed(monkeypatch):
      monkeypatch.setattr(auth_helpers, "require_user", lambda request: "bob")
      req = _request(_Mgr({"do_x": False}))
      with pytest.raises(Exception):
          require_privilege(req, "do_x")
  ```

  Mutation probe `/tmp/audit-probe/probe_require_privilege_mutation.py` replaces the 403 in a copy
  of `src/auth_helpers.py:187` with an `AttributeError` and re-runs the assertion:

  ```
  MUTATION: raised AttributeError(AttributeError('mutated: not the 403 the test claims to pin'))
  -> pytest.raises(Exception) still PASSES: True
  ```

  The first test in the file documents the fail-open contract explicitly — "It should fall back to
  the documented fail-open behaviour" (`:23-26`) — and asserts
  `require_privilege(req, "do_x") == "bob"` for a corrupt `privileges` value (`:29`). That
  behaviour is the subject of a low-severity finding in `src-security.md:99-146`: the blanket
  `except Exception` at `src/auth_helpers.py:178-181` makes an authorization check skip itself, and the
  `isinstance(privs, dict)` guard on the following line shows a non-dict was already anticipated.
  This test turns the fallback into a requirement, so the fix proposed there would fail here unless
  the test is updated in the same change.
- **Impact:** the pair cannot tell "the user was denied" from "the check crashed", and the file
  reads as coverage for a privilege gate while actually freezing a fail-open decision that the
  code review flagged.
- **Fix:** assert `pytest.raises(HTTPException)` and the 403 status; for the non-dict case, decide
  the contract in `src-security`'s finding and encode that decision here, including the expected
  outcome for an unreadable `privileges` value.

### [BUG] `test_auth_regressions.py` claims to pin the `create_task` admin gate but only asserts a frozenset's contents

- **Location:** `tests/test_auth_regressions.py:334`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the module docstring promises "Task `create_task` blocks shell-executing action
  types for non-admins (`run_local`, `run_script`, `ssh_command`)" (`:5-7`), and the test that
  stands for it is:

  ```python
  # :334-341
  def test_admin_only_actions_set_contains_shell_runners():
      """The constant defining shell-executing action types must include
      the three risky entries. Catches accidental removal."""
      from src.task_action_policy import ADMIN_ONLY_TASK_ACTIONS
      assert "run_local" in ADMIN_ONLY_TASK_ACTIONS
      assert "run_script" in ADMIN_ONLY_TASK_ACTIONS
      assert "ssh_command" in ADMIN_ONLY_TASK_ACTIONS
  ```

  Nothing in the file calls `create_task`. The enforcement is
  `_require_admin_for_task_action` at `routes/task/task_routes.py:433`, called from
  `create_task` at `:463`. A tree-wide search for the three action names in `tests/`
  (`grep -rln "run_local\|ADMIN_ONLY_TASK_ACTIONS\|is_admin_only_task_action" tests/`) returns only
  this file, and the route-level admin-gate suite that does exist
  (`tests/test_task_cookbook_admin_gate.py`) exercises `cookbook_serve` only.
- **Impact:** the route-level refusal for the three shell-executing action types — the case the
  file was written to protect — has no test. Removing the `_require_admin_for_task_action` call, or
  narrowing `is_admin_only_task_action` to `task_type == "action"` while a caller passes `None`,
  leaves the suite green; the constant membership assertion still passes.
- **Fix:** add a route test that posts a `TaskCreate(task_type="action", action="run_local")` as a
  non-admin and asserts 403, mirroring `tests/test_task_cookbook_admin_gate.py:144`.

### [BUG] `test_pr_description_check.py` never exercises the update or delete comment paths

- **Location:** `tests/test_pr_description_check.py:56`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** every test runs the checker through one harness whose `listComments` always returns
  nothing:

  ```javascript
  // :54-62, the harness string in _run_checker
  const calls = [];
  const listFiles = async () => {};
  const listComments = async () => {};
  ...
    if (method === listComments) return [];
  ```

  The checker branches on the existing comment (`MARKER` match) in two places:
  `.github/scripts/check-pr-description.js:141-144` deletes the stale bot comment when the
  description is clean, and `:179-182` updates it instead of creating a new one when it is not.
  With an empty comment list, `existing` is always undefined, so only the `createComment` branch
  runs — and `_comment(calls)` (`:133-135`) only reads `createComment`. No test asserts that a
  second run of the workflow updates rather than duplicates the bot comment, or that a clean PR
  removes it.
- **Impact:** a regression that stops the checker finding or updating its own comment — the
  duplicate-comment spam case, or a wrong `comment_id` — is invisible to this suite. The checker is
  CI tooling, so the consequence is noise and mislabelling on pull requests, not a trust-boundary
  break.
- **Fix:** parameterise the harness with an `existingComments` array (the checker's `MARKER` plus a
  body) and assert `updateComment`/`deleteComment` for the dirty and clean cases.

### [BUG] The two `is_youtube_url` tests pin the true-positive direction only, encoding the loose substring match as correct

- **Location:** `tests/test_is_youtube_url_nonstring.py:13-14` (with `tests/test_is_youtube_url_nonstring_svc.py:12-13`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** both files end with the same two positive cases:

  ```python
  def test_is_youtube_url_detects_real_urls():
      assert is_youtube_url("https://www.youtube.com/watch?v=x") is True
      assert is_youtube_url("https://youtu.be/x") is True
  ```

  The implementation is `return "youtube.com" in url or "youtu.be" in url`
  (`services/youtube/youtube_handler.py:61-64`), so the assertion is true for any input containing
  the substring — including `https://notyoutube.com/watch?v=abc` and
  `https://example.com/post?ref=youtube.com`, both of which `services-media.md:107-140` measures as
  `True` and reports as a medium defect. Neither test file has a false-positive case, so a change
  that tightens the check to a host match would have to update these tests, and a change that
  widens it further would not be noticed. `test_is_youtube_url_nonstring.py` imports the
  `src.youtube_handler` path, which `src/youtube_handler.py:23` replaces with the canonical module
  object, so the two files exercise the same function twice.
- **Impact:** the test pair is consistent with the defect rather than a guard against it: it
  documents the substring behaviour as intended. The two import paths are pinned, which is the only
  distinct thing the duplication buys.
- **Fix:** add the false-positive cases the `services-media` finding measures, with the expectation
  that matches the decided contract for `is_youtube_url`, and keep one of the two files as the
  import-path pin with a comment saying so.

### [BUG] `test_path_name_strips_traversal` asserts on `pathlib`, not on the code that relies on it

- **Location:** `tests/test_security_regressions.py:296`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the whole test is a parametrised comparison against the standard library:

  ```python
  # :296-300
  def test_path_name_strips_traversal(token, expected):
      """`Path(token).name` is the one-line defense the send/upload paths
      rely on. Pin its behaviour so a future "let's just use the raw
      token" regression is caught by tests."""
      assert Path(token).name == expected
  ```

  The docstring names the regression it cannot catch: if a caller stops wrapping the token in
  `Path(...)`, this test still passes because `Path("../etc/passwd").name` is still `"passwd"`. No
  case in the test touches a route or a handler. The cross-owner and PDF-marker tests in the same
  file (`:365-513`) do exercise real resolver behaviour and are the stronger half of this file's
  upload coverage.
- **Impact:** the compose-upload path traversal defense is pinned only by a test of `pathlib`. The
  behaviour the finding needs — that the route refuses a traversal-shaped token — is untested here.
- **Fix:** drive the send/upload handler with `"../../etc/passwd"` as the token and assert the
  request is refused or resolved inside `COMPOSE_UPLOADS_DIR`; keep the parametrised `Path` cases
  only as a comment on why the shape is safe.
