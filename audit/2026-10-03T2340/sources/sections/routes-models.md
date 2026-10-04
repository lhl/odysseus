# routes: model serving

## Overview

The model-endpoint registry and every surface built on it: `routes/model_routes.py` holds the
per-user model picker (`GET /api/models`), the endpoint CRUD (`POST`/`GET`/`PATCH`/`DELETE
/api/model-endpoints`, plus the `/models` and `/dependents` sub-resources), the probe and refresh
endpoints (`GET /api/ping`, `/api/probe`, `/api/model-endpoints/{id}/probe`,
`/api/model-endpoints/{id}/models`, `POST /api/probe-selected`, `POST /api/model-endpoints/test`),
local discovery (`GET /api/providers`, `/api/discover`, `/api/model-endpoints/probe-local`), the
default-chat resolution (`GET /api/default-chat`), the background model-cache refresh and the
stale-cookbook-endpoint sweep, and the tool on/off list (`GET`/`POST /api/tools`).

The boundary: the request-authenticating middleware and the `require_admin` gate these routes call
are `core-auth-session`; the `ModelEndpoint` row and its encrypted key column are
`core-data-platform`; the URL and header builders the probes use (`resolve_url`, `normalize_base`,
`build_chat_url`, `build_models_url`, `build_headers`, `resolve_endpoint_runtime`) are
`src-llm-core`; `src/auth_helpers.py` (`effective_user`, `owner_filter`) is `src-security`; the
settings store the CRUD reads and writes is `src-memory-rag`; the health report that probes the same
endpoints is `src-platform`, reached through `routes-rest-integrations-misc`. This section covers
what these routes do with a caller-supplied endpoint URL, who may call them, and what they reveal —
not whether the store, the URL builders, or the middleware are themselves correct.

## Coverage

**Read fully:** `routes/model_routes.py` (2,717 lines).

**Read partially:** the boundary code and callers the findings rest on:

- `core/middleware.py` at `require_admin` (`:57-82`)
- `src/auth_helpers.py` in full (199 lines: `get_current_user`, `effective_user`, `owner_filter`,
  `_auth_disabled`)
- `core/database.py` at the `ModelEndpoint` model (`:520-554`)
- `src/endpoint_resolver.py` at `resolve_endpoint_runtime` (`:146-162`), `resolve_url` (`:209-222`),
  `normalize_base` (`:225-234`), `_validated_endpoint_base` (`:237-242`), `_prepare_endpoint_base`
  (`:245-247`), `build_chat_url` (`:271-283`), `build_models_url` (`:286-315`) and `build_headers`
  (`:318-340`)
- `core/log_safety.py` (`:1-27`)
- `src/readiness.py` in full (61 lines — it checks the database and the data directory and does not
  touch the model-endpoint store)
- `src/service_health.py` at `providers_health` (`:346-382`) and the enabled-endpoint query it feeds
  (`:435-445`)
- `app.py` at the auth-exempt list (`:265-292`) and `/api/health` (`:956-958`)
- `routes/diagnostics_routes.py` at `get_service_health` (`:23-30`)
- `src/tool_security.py` at `NON_ADMIN_BLOCKED_TOOLS` (`:42-78`)
- `src/agent_tools/admin_tools.py` at `do_manage_endpoints` (`:22-80`)
- `routes/cookbook_routes.py` at the serve-registration block (`:1888-1925`) and
  `save_cookbook_state` (`:3395-3415`)
- `routes/chatgpt_subscription_routes.py` (`:55-95`) and `routes/copilot_routes.py` (`:55-90`)
- `src/chatgpt_subscription.py` at `resolve_runtime_credentials` (`:254-286`)
- the chat-side credential resolution (`src/ai_interaction.py:137`, `src/agent_loop.py:1029`,
  `routes/chat_routes.py:605`, `routes/chat_helpers.py:484`)
- `static/js/admin.js` at the add-endpoint form (`:1100-1135`), the refresh control (`:680-700`) and
  `_normalizeBaseUrl` (`:966-1000`)
- `static/js/markdown.js` at `_isModelEndpointUrl` (`:168-177`), `_appendEndpointAddButtons`
  (`:1122-1142`) and `_registerEndpointFromButton` (`:1144-1180`)
- `static/js/cookbookRunning.js` at `_removeEndpointByUrl` (`:529-543`)
- `static/js/models.js:202`
- the module's own tests (`tests/test_model_routes.py`, `tests/test_endpoint_probing.py`,
  `tests/test_endpoint_owner_scope_followup.py`) for what is already pinned

**Not read:**

- `src/llm_core.py` internals (`_detect_provider`, `httpx_get_kimi_aware`, the payload builders)
  beyond the call signatures
- `src/settings.py`
- `core/database.py` beyond the `ModelEndpoint` model (the encryption column, the session store)
- `core/middleware.py` beyond `require_admin` (the request-authentication middleware itself belongs
  to `core-auth-session`)
- `src/chatgpt_subscription.py` beyond `resolve_runtime_credentials`
- the cookbook serve pipeline and `_active_cookbook_endpoint_ids`' producer beyond the state-file
  shape cited below
- the rest of the front end
- every other `routes-*` module

**Checks run:**

- six probes with throwaway scripts under `/tmp` (not part of the target tree), each quoted in the
  finding it settles — the URL helpers against a query-bearing base
- `GET /api/models` and `GET /api/default-chat` and `DELETE /api/model-endpoints/{id}` with one such
  row visible, through `fastapi.testclient` with the stores stubbed
- `POST /api/model-endpoints` and `POST /api/model-endpoints/test` with the same URL
- the manual-refresh path with a subscription endpoint row, capturing the `api_key` the probe
  receives and the log record it emits
- `POST /api/probe-selected` with five body shapes
- `_disable_stale_cookbook_local_endpoints` against a state file holding only a stopped serve task
  and then one holding a running task

Also a grep for the callers of `_resolve_probe_key` and of the model-endpoint probe helpers. The 54
suites matching `ls tests | grep -iE 'model|endpoint|ready'` were run over this surface — **714
passed**.

### [BUG] An endpoint `base_url` carrying a query or fragment is accepted, then breaks the model picker and cannot be deleted

- **Location:** `routes/model_routes.py:1570` (`_fetch_models`), `:2483` (`get_default_chat`), `:2616` (`_session_uses_endpoint_url`), with the two write boundaries at `:1993` (`base_url: str = Form(...)`) and `:2554` (`if "base_url" in body`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** nothing on the write path rejects a query or fragment. `create_model_endpoint`
  normalizes the value and stores it (`:2011`, `:2159-2165`), and the PATCH branch does the same
  with no probe at all:

  ```python
  if "base_url" in body and isinstance(body["base_url"], str):
      _new_base = body["base_url"].strip().rstrip("/")
      for _suffix in ("/models", "/chat/completions", "/completions", "/v1/messages"):
          if _new_base.endswith(_suffix):
              _new_base = _new_base[: -len(_suffix)].rstrip("/")
      _new_base = _normalize_base(_new_base)
      if _new_base:
          ep.base_url = _new_base
  ```

  `_normalize_base` keeps the query, and every URL builder the read paths call goes through
  `src/endpoint_resolver.py:237-242`, which refuses it:

  ```
  $ venv/bin/python -c "... build_chat_url(normalize_base('http://localhost:1234/v1?api_key=…'))"
  normalize_base -> http://localhost:1234/v1?api_key=…
  build_chat_url -> ValueError: Endpoint base URL must not include query or fragment
  build_models_url -> ValueError: Endpoint base URL must not include query or fragment
  ```

  Measured end to end through `fastapi.testclient` with `SessionLocal` stubbed and the admin gate
  replaced by a no-op, so the handler body runs as written (the row the POST creates has
  `owner=None`, because `shared` defaults to `"true"` at `:2008`):

  ```
  POST /api/model-endpoints (skip_probe=true) -> 200
    stored base_url: http://198.51.100.7:8080/v1?api_key=…  |  row.owner: None
  GET  /api/models        as non-admin "alice" -> 500
  GET  /api/default-chat  as non-admin "alice" -> 500
  DELETE /api/model-endpoints/ep-q             -> 500   (db.delete never reached)
  DELETE again after clearing the query        -> 200 {'deleted': True, 'cleared_sessions': 1}
  ```

  The DELETE fails inside `_clear_sessions_for_endpoint` → `_session_uses_endpoint_url`
  (`:2608-2618`), which calls `build_chat_url(base)` at `:2616` for every session row. `POST
  /api/model-endpoints/test` with the same URL is a 500 as well, where the intended answer is the
  400 that `_model_endpoint_error_message` builds.

  Reachability of the store path: `POST` skips the probe whenever the caller sends
  `skip_probe=true` (`:2031-2033`), and a shipped button does exactly that with a URL taken from a
  rendered chat message — `static/js/markdown.js:1122-1142` adds an "Add to model picker" button to
  every `a[href]` whose path is `/v1` (`_isModelEndpointUrl`, `:168-177`, ignores the query), and
  `_registerEndpointFromButton` posts that href verbatim with `skip_probe=true` (`:1174`). The
  browser add form is safe by comparison: `static/js/admin.js:984` strips `?`/`#` before posting.
- **Impact:** one admin action — clicking that button on a link whose URL carries a query string, or
  any API/agent call that stores one — leaves a row that makes `GET /api/models` and
  `GET /api/default-chat` return 500 for every caller who can see it. Because the row is registered
  shared (null owner) by default, that is every user on the instance, and the model picker is the
  app's main model-selection surface. The row also cannot be removed through the API: `DELETE
  /api/model-endpoints/{id}` raises the same `ValueError` before `db.delete`, so the admin has to
  edit the database. Chat sessions already bound to a good endpoint are unaffected.
- **Fix:** validate at the two write boundaries — reject a `base_url` containing `?` or `#` with a
  400 (the PATCH branch currently validates nothing at all) — and make the read paths defensive:
  `_fetch_models` and `get_default_chat` should skip or degrade a row whose URL cannot produce a
  chat URL, and `_session_uses_endpoint_url` should treat the failure as "does not match" rather
  than letting it abort the DELETE.

### [SECURITY] Endpoint URLs that can embed credentials are written to the log unredacted on the refresh and probe paths

- **Location:** `routes/model_routes.py:2333` (with `:172`, `:1059`, `:663`, `:674`, `:683`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the module imports the redactor and uses it on the probe's own log lines, but not on
  the other URL-bearing ones:

  ```python
  from core.log_safety import redact_url as _redact_url_for_log      # :20
  ...
  logger.info("Endpoint still loading model at %s", _redact_url_for_log(url))     # :1033
  logger.warning("Failed to probe %s with API key: %s", _redact_url_for_log(url), e)  # :1037
  ...
  logger.warning("Manual model refresh failed for endpoint %s at %s: %s", ep_id, base, exc)  # :2333
  logger.debug(f"Ollama /api/tags probe failed for {base}: {e}")                 # :1059
  logger.debug("Provider detection failed for %s: %s", base_url, exc)            # :663
  ```

  `base` at `:2333` is `_normalize_base(ep.base_url)` and `base_url` at `:663`/`:674`/`:683` is the
  caller's value, so the userinfo and the query survive. That is the case the helper documents:

  ```python
  # core/log_safety.py:3-6
  """Endpoint URLs configured by admins can embed credentials in the userinfo
  (``https://user:pass@host``) or query string (``?api_key=...``). Logging them
  raw leaks those secrets, so route/diagnostic logs run URLs through
  ``redact_url`` first.
  ```

  Measured by running the manual-refresh path with the row's `base_url` carrying a query and
  capturing the module logger:

  ```
  refresh header: failed
  LOG: Manual model refresh failed for endpoint ep-q at http://198.51.100.7:8080/v1?api_key=…: Endpoint base URL must not include query or fragment
  ```

  The same convention is kept elsewhere: `routes/chat_routes.py:728`, `:1670` and
  `routes/contacts/contacts_routes.py:723` all log their URLs through `redact_url`. The
  redactor has its own blind spot for scheme-less URLs
  (`core-auth-session.md`, `redact_url` returns a scheme-less value unchanged); the six lines
  here leak even a well-formed URL, so the two defects are independent.
- **Impact:** an operator who configures an endpoint as `https://user:pass@host/v1` or
  `https://host/v1?api_key=…` gets that credential written into `data/logs/app.log` — at WARNING for
  the refresh failure, at DEBUG for the probe helpers — instead of the redacted form used two
  functions away. The log is local and served only to admins
  (`/api/diagnostics/logs`), and it requires the credential to live in the URL rather than in the
  `api_key` field, which is the supported place for it; the fix is cheap and the rule is the
  project's own.
- **Fix:** route these six call sites through `_redact_url_for_log`, as `_probe_endpoint` already
  does.

### [BUG] Every probe sends the stored static key and never the session-backed one, because `_resolve_probe_key` has no caller

- **Location:** `routes/model_routes.py:691-699` (the helper), with the probe call sites at `:1432`/`:1502` (`_should_refresh_endpoint` / `_refresh_caches_bg`), `:1782`, `:1873`, `:2271`, `:2280`, `:2331`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_resolve_probe_key` resolves the live credential through
  `resolve_endpoint_runtime` — the same call the chat paths use — and nothing calls it:

  ```
  $ grep -rn "_resolve_probe_key" --include=*.py .
  ./routes/model_routes.py:691:def _resolve_probe_key(ep) -> Optional[str]:
  ./tests/test_endpoint_probing.py:53:        _resolve_probe_key,
  ./tests/test_endpoint_probing.py:451:# ── _resolve_probe_key: static key vs provider-auth runtime token ──
  ```

  The three assertions under that comment (`tests/test_endpoint_probing.py:453-477`) pin both
  branches: a static endpoint returns its column, a `provider_auth_id` endpoint returns the
  resolved runtime token, and a resolution failure returns `None`. No production module appears in
  that grep.

  Every production call site passes the row's static column instead — `ep.api_key` at `:1782`,
  `:2331`, `ep_data["api_key"]` at `:2271`/`:2280`, `ep.get("api_key")` at `:1873`, and
  `info["api_key"] = getattr(ep, "api_key", None)` at `:1432` for the background refresh. For a
  subscription-backed endpoint that column is null by construction: the ChatGPT sign-in route writes
  `ep.api_key = None` with `ep.provider_auth_id = auth.id`
  (`routes/chatgpt_subscription_routes.py:82-83`), and `_probe_endpoint` (`:965-969`) returns an
  empty list when it has no key:

  ```python
  if provider == "chatgpt-subscription":
      from src.chatgpt_subscription import fetch_available_models
      if api_key:
          return fetch_available_models(api_key, timeout=timeout)
      return []
  ```

  Measured on the manual-refresh route with such a row, stubbing `_probe_endpoint` to record the key
  it receives and stubbing `resolve_endpoint_runtime` to return a live token:

  ```
  manual refresh status header: failed
  api_key the probe was called with: [None]
  what the unwired resolver would return: live-bearer
  ```

  The chat side does resolve it (`src/ai_interaction.py:137`, `src/agent_loop.py:1029`,
  `routes/chat_routes.py:605`), so the omission is specific to probing.
- **Impact:** an administrator can never refresh or probe a subscription-backed endpoint: the
  Refresh control on `/api/model-endpoints/{id}/models?refresh=true` returns
  `X-Model-Refresh-Status: failed`, and the admin UI surfaces that as a warning toast
  (`static/js/admin.js:686-691`), while the background refresh records the endpoint as failing. Chat
  keeps working, and the model list seeded at sign-in is still served, so the damage is a dead admin
  control rather than a broken flow — but the dead control is also the only way to update that list.
  The same static key is what `src/service_health.py:441-442` hands to the probe, so the health
  report counts such an endpoint as unreachable too.
- **Fix:** pass `_resolve_probe_key(ep)` at those call sites (keeping the static key as the
  fallback it already is), or resolve the runtime credential in `_probe_endpoint`'s callers the way
  the chat path does. The helper's own tests already pin the intended behaviour.

### [ERROR-HANDLING] `POST /api/probe-selected` returns 500 for a malformed entry in `models`

- **Location:** `routes/model_routes.py:1797-1809`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the body is typed, so a non-object body is rejected — but the list elements are not
  checked before they are used as mappings:

  ```python
  @router.post("/probe-selected")
  def probe_selected(request: Request, request_body: dict = Body(...)):
      require_admin(request)
      models_to_probe = request_body.get("models", [])
      ...
      for item in models_to_probe:
          ep_id = item.get("endpoint_id", "")
  ```

  Measured through `fastapi.testclient` with the admin gate stubbed out:

  ```
  body=['a']                          -> HTTP 422
  body='a'                            -> HTTP 422
  body={'models': ['a']}              -> HTTP 500 Internal Server Error
  body={'models': 'a'}                -> HTTP 500 Internal Server Error
  body={'models': [{'model': 'm'}]}   -> HTTP 200
  ```

  This is the same class as the non-object-body finding in `routes-rest-auth-admin.md`
  (`routes/auth_routes.py:329`, `:784`, `:794`): an unchecked request shape reaches an unhandled
  `AttributeError` and the caller gets a 500 instead of a 400. Here the outer body is validated by
  the `dict` annotation, so the unchecked part is the element shape.
- **Impact:** an admin or a script that sends a string instead of an object list gets a 500 and a
  traceback in the log where the rest of the file answers 400 (as the two `request.json()` handlers
  in this file do, `:2376` and `:2503`). Admin-only, so the cost is a confusing failure, not an
  exposed path.
- **Fix:** reject or skip a non-dict element — `if not isinstance(item, dict): results.append(...);
  continue`, or a 400 up front — matching the guards the two raw-body handlers already use.

### [BUG] The stale-cookbook sweep cannot disable the last stale endpoint

- **Location:** `routes/model_routes.py:151-155` (with `_active_cookbook_endpoint_ids` at `:123-148`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the sweep returns before looking at any row whenever no serve task is currently
  active, and `_active_cookbook_endpoint_ids` returns the empty set both for "no serve task is
  active" and for "the state file is missing or unreadable":

  ```python
  def _disable_stale_cookbook_local_endpoints(db) -> int:
      """Disable enabled cookbook endpoints whose serve task is no longer active."""
      active_ids = _active_cookbook_endpoint_ids()
      if not active_ids:
          return 0
  ```

  A stopped serve task stays in the state file (the cookbook status handler counts "accumulated
  stopped tasks", `routes/cookbook_routes.py:4436-4448`), so the ordinary end state — the last serve
  stopped — is exactly the empty-set case. Measured with a state file holding one stopped serve task
  and one enabled `local-` row, then one holding a running task beside it:

  ```
  active ids with only a stopped serve task: set()
  disabled count (stopped-only state): 0 | row.is_enabled now: True
  active ids with one running serve task: {'local-live'}
  disabled count (one active task): 1 | row.is_enabled now: False
  ```

  The docstring and the function's own comment state the opposite intent: "If a tmux stream is
  stopped or an old task lingers, the row must stop participating in model selection and defaults"
  (`:127-129`).
- **Impact:** after the only served model is stopped, a lingering `local-*` row stays enabled, so it
  keeps appearing in the picker as a candidate and keeps being probed — the state the sweep exists to
  clear. The mitigation is that the admin UI deletes the row when it stops a serve
  (`static/js/cookbookRunning.js:539`, `_removeEndpointByUrl`), so this only bites when the row
  outlives the task: a browser that closed mid-stop, a stop performed outside the UI, or a state
  file that was removed.
- **Fix:** distinguish the two cases — when the state file is readable and its `tasks` list contains
  no active serve task, every enabled `local-%` row is stale; keep the early return only for the
  missing/unreadable state file (where the answer really is unknown).

