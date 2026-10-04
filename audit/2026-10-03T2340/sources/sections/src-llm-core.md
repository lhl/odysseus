# src: LLM interaction, endpoints, model capability

## Overview

`src/ai_interaction.py`, `src/chatgpt_subscription.py`, `src/copilot.py`, `src/endpoint_resolver.py`, `src/foreground_model_routing.py`, `src/image_model_ids.py`, `src/llm_core.py`, `src/model_capabilities.py`, `src/model_capability_readers/__init__.py`, `src/model_capability_readers/base.py`, `src/model_capability_readers/generic_openai.py`, `src/model_capability_readers/google.py`, `src/model_capability_readers/google_ai_studio_mapping.py`, `src/model_capability_readers/llamacpp.py`, `src/model_capability_readers/lmstudio.py`, `src/model_capability_readers/ollama.py`, `src/model_capability_readers/openai.py`, `src/model_capability_readers/openrouter.py`, `src/model_context.py`, `src/model_discovery.py`.

The outbound LLM layer. `src/llm_core.py` holds the three call entry points (`llm_call`,
`llm_call_async`, `stream_llm`), provider detection, the per-provider URL and payload builders, the
SSE protocol the front end and the agent loop consume, and the local-model concurrency gate.
`src/endpoint_resolver.py` turns a setting prefix, an endpoint id or a model spec into a
`(url, model, headers)` triple and builds the request URL and auth headers for each provider.
`src/model_context.py` discovers and caches the context window, `src/model_capabilities.py` and the
nine reader modules in `src/model_capability_readers/` describe what a model supports, and
`src/model_discovery.py` lists model ids. `src/ai_interaction.py` is the agent-side tool dispatch;
`src/foreground_model_routing.py`, `src/chatgpt_subscription.py`, `src/copilot.py` and
`src/image_model_ids.py` carry the provider-specific policy.

The boundary: the handlers that call `llm_call`/`stream_llm` are `routes-chat-session`,
`routes-models` and the `routes-rest-*` sections; the agent loop that consumes the SSE protocol and
the tool schemas that parse a streamed tool call are `src-agent-loop` and `src-tools-*`; the
`ModelEndpoint`/`Session` schema, the settings store `resolve_endpoint` reads and the
`ProviderAuthSession` row are `core-data-platform`; the middleware that authenticates a request is
`core-auth-session`; the search, memory and RAG helpers `ai_interaction` calls are `services-search`
and `src-memory-rag`. This section covers what this layer sends, to whom, with which credential, and
what it does with the reply.

## Coverage

**Read fully:** all 20 assigned files (10,231 lines): `src/llm_core.py` (3,730),
`src/ai_interaction.py` (1,489), `src/model_capabilities.py` (934), `src/endpoint_resolver.py`
(672), `src/model_context.py` (520), `src/model_capability_readers/llamacpp.py` (428),
`src/model_capability_readers/base.py` (316), `src/chatgpt_subscription.py` (315),
`src/model_discovery.py` (293), `src/copilot.py` (256), `src/foreground_model_routing.py` (206),
`src/model_capability_readers/ollama.py` (204), `src/model_capability_readers/openrouter.py` (200),
`src/model_capability_readers/lmstudio.py` (186),
`src/model_capability_readers/google_ai_studio_mapping.py` (162),
`src/model_capability_readers/__init__.py` (95), `src/model_capability_readers/openai.py` (65),
`src/model_capability_readers/google.py` (60),
`src/model_capability_readers/generic_openai.py` (58), `src/image_model_ids.py` (42).

**Read partially:** the boundary code each finding rests on — `src/tool_schemas.py` at
`function_call_to_tool_block` (`:1370-1400`, the consumer of the streamed tool-call event);
`src/tool_execution.py` at the `pipeline`/`manage_memory`/`ui_control` dispatch into
`dispatch_ai_tool` (`:1169-1171`); `routes/chat_helpers.py` at the context-length, compaction and
trim block (`:737`, `:745-805`) and the ChatGPT-subscription branch (`:455-465`);
`routes/chat_routes.py` at `_session_url_matches_endpoint` (`:415-425`), the subscription recovery
block (`:551-600`), `_reconcile_selected_route` (`:670-728`) and the foreground-policy block
(`:822-880`); `src/context_compactor.py` at `trim_for_context` (`:224-236`) and `maybe_compact`
(`:323-345`); `routes/model_routes.py` at endpoint creation (`:2000-2050`) and the probe hints
(`:1175-1230`); `routes/cookbook_routes.py` at the local-endpoint registration (`:1800-1915`);
`routes/chatgpt_subscription_routes.py` (`:26-95`) and `routes/copilot_routes.py` (`:38-90`);
`core/database.py` at the `Session.headers` JSON column (`:199`) and `provider_auth_id` (`:553`);
`core/session_manager.py` at the three `headers` normalizations (`:134-145`, `:190-200`,
`:470-485`); `src/url_safety.py` at `check_outbound_url` (`:1-80`); `app.py` at the uvicorn start
(`:1306`); `specs/model-capability-canonical.md` at its "Current Gaps" list (`:168-180`);
`tests/test_resolve_model_offloaded.py` and `tests/test_llm_core_usage_finish_delta.py` in full for
what is already pinned; `static/js/chat.js` at the interrupted-response control (`:1215-1235`).

**Not read:** `src/agent_loop.py` except the two frames a stack trace named during the checks
(`_strip_think_blocks` at `:1253-1280`, entered from `:5572`); `src/agent_tools/*`; `src/tool_schemas.py` beyond `function_call_to_tool_block`; the
`routes-*` handlers beyond the cited regions (they belong to their own sections); `src/settings.py`
and the `ProviderAuthSession` schema; `core/middleware.py`; `routes/session_routes.py`,
`routes/email_routes.py` and `routes/webhook/webhook_routes.py` (the API-chat path that combines a
caller-supplied `base_url` with a key, `routes/webhook/webhook_routes.py:296-312`, is that section's
to judge); the front end beyond the cited file; and every other section's files.

**Checks run:** seven probes with throwaway scripts under `/tmp/probe/` (outside the target tree),
each quoted in the finding it settles — the event-loop stall, request log and cache behaviour of
`get_context_length` (`p_ctx_stall.py`); the same probe against an endpoint whose `/v1/models`
requires a key (`p_ctx_auth.py`); the probe URLs captured through a monkeypatched `httpx.get` for
five base-URL shapes; the real `stream_llm` driven against a stub SSE server whose body is complete,
closed after one chunk, ended with `finish_reason: "length"`, and cut mid-tool-call
(`p_stream_cut.py`); a `200 text/html` body through `llm_call`, `llm_call_async` and
`llm_call_async_with_route_fallback` (`p_nonjson.py`, `p_nonjson2.py`); the
`CHATGPT_SUBSCRIPTION_BASE_URL` override through `_detect_provider`, `build_chat_url` and
`build_headers` (`p_cgpt.py`); and the local-model gate's waiting counter with one holder and one
waiter (`p_gate.py`). Also `httpx.get("http://slots", timeout=5)` timed directly, and greps for the
importers of `src/model_capability_readers` (only `tests/test_model_capability_readers.py`),
`finish_reason` across `src/`, `routes/`, `core/` and `static/js/` (one comment, no reader),
`CHATGPT_SUBSCRIPTION_BASE_URL` writers, producers of a list-content `system` message, writers of a
string-typed `Session.headers`, and the credential-forwarding shape in `_reconcile_selected_route`
(`routes/chat_routes.py:670-700`). On the SSRF question specifically: nothing in this section accepts
a caller-supplied endpoint URL. `_resolve_model` (`src/ai_interaction.py:78-213`) matches a model
name against the caller's enabled `ModelEndpoint` rows and takes the URL *and* the key from the same
row via `resolve_endpoint_runtime`, and `_reconcile_selected_route` uses a form-supplied
`selected_endpoint_url` only to match a stored row, building the request from that row
(`routes/chat_routes.py:697-700`). The two `check_outbound_url` calls in `src/ai_interaction.py`
(`:1149`, `:1431`) guard the *provider-supplied* image result URL, not an endpoint.

One ordering artifact, recorded because it is a check result rather than a finding: run in a
non-alphabetical order (`test_llm_core_*.py` before `test_foreground_model_routing.py`) the same 44
suites hang. The stack trace at the hang names
`tests/test_foreground_model_routing.py:2257` → `src/agent_loop.py:5572` →
`_strip_think_blocks` (`:1272`), where a `Mock` reached the `text` argument, so
`lowered.find(" thinking", pos)` never returns `-1` and the loop spins until GC. It does not
reproduce in the suite's natural order (604 passed, 8.5s), so the CI job is unaffected; the leaking
suite is outside this section and was not chased.
The 44 suites matching this surface — `tests/test_llm_core_*.py` (22 files),
`tests/test_model_context.py`, `tests/test_model_capabilities.py`,
`tests/test_model_capability_readers.py`, `tests/test_model_defaults.py`,
`tests/test_model_discovery_status.py`, `tests/test_context_budget.py`,
`tests/test_context_cache_per_endpoint.py`, `tests/test_context_compactor*.py`,
`tests/test_compact_truncate_tool_call_args.py`, `tests/test_estimate_tokens_tool_calls.py`,
`tests/test_endpoint_resolver_{headers,models,urls}.py`, `tests/test_resolve_endpoint_fallbacks.py`,
`tests/test_resolve_model_offloaded.py`, `tests/test_resolve_session_auth_chatgpt.py`,
`tests/test_foreground_model_routing.py`, `tests/test_copilot*.py`,
`tests/test_chatgpt_subscription_routes.py`, `tests/test_ai_interaction_owner_scope.py` — were run
over this surface in their natural order: **604 passed**.

Four hypotheses did not survive checking and are not findings. (1) A `Session.headers` value that is
a JSON string would raise `ValueError` in the Ollama branch (`h.update(headers)`,
`src/llm_core.py:2620`) and `AttributeError` in the Anthropic branch (`_build_anthropic_headers`),
where the sync `llm_call` explicitly tolerates one (`:180`); no live writer stores a string — the
three assignment sites pass `build_headers(...)` or `{}`, and `core/session_manager.py` normalizes a
string to a dict on load. (2) A `system` message whose `content` is a list would raise `TypeError` in
`_sanitize_llm_messages`; no caller in `src/`, `routes/` or `core/` builds one. (3) The reader
modules in `src/model_capability_readers/` have no production caller (only their own test file
imports the package) — that is the documented state, not a defect:
`specs/model-capability-canonical.md:170` records "Canonical records are not yet used by runtime
discovery, endpoint resolution, model context, request shaping, or frontend pickers." (4) A
caller-supplied endpoint URL or model name cannot redirect a request to a chosen address or attach a
stored credential — see the SSRF note in the checks above.

### [PERF] Context-length discovery runs two synchronous HTTP probes on the event loop, once per local request

- **Location:** `src/model_context.py:424` and `:450` (`_query_context_length`), called from `src/llm_core.py:2623`, `:2377`, `:2017`, `src/context_compactor.py:338` and `routes/chat_helpers.py:791`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_query_context_length` makes both probes with a synchronous client, on a 5-second
  budget (`REQUEST_TIMEOUT = 5`, `src/model_context.py:107`), and has no `async` variant:

  ```python
  r = httpx.get(f"{base}/slots", timeout=REQUEST_TIMEOUT)          # :424
  ...
  r = httpx.get(models_url, timeout=REQUEST_TIMEOUT)               # :450
  ```

  The Ollama branch of the async stream builder calls it inline, for every request:

  ```python
  elif provider == "ollama":
      target_url = _normalize_ollama_url(url)
      ...
      payload = _build_ollama_payload(
          model, messages_copy, temperature, max_tokens,
          stream=True, tools=tools, num_ctx=get_context_length(url, model),   # :2623
      )
  ```

  `_stream_llm_inner` is an `async def`, and the same call appears in `llm_call_async` (`:2377`),
  `maybe_compact` (`src/context_compactor.py:323-338`, `async def`) and
  `build_chat_context` (`routes/chat_helpers.py:791`). A ticker task on the loop, with a local
  endpoint that delays each response by 1.0s (`/tmp/probe/p_ctx_stall.py`):

  ```
  A) a 1.0s-slow local endpoint, called from the event loop
    inline (no thread)         elapsed=5.25s  ticker iterations=0  ctx=128000
  B) the same call moved off the loop
    asyncio.to_thread          elapsed=4.74s  ticker iterations=467  ctx=128000
  ```

  Zero iterations means the loop did not run once during the call. The 5.25s is mostly the mangled
  `/slots` URL of the next finding (3.98s of DNS) plus the server's 1.0s; the per-call ceiling is
  `REQUEST_TIMEOUT`, and a lookup that reaches both probes can spend 10s. The lookup also repeats
  work: `_configured_endpoint_kind` opens a session and scans the enabled endpoints
  (`db.query(ModelEndpoint).filter(ModelEndpoint.is_enabled == True).all()`,
  `src/model_context.py:56-88`) four times per `get_context_length` call — counted by wrapping the
  function — and nothing is cached for a local endpoint:

  ```
  D) repeat calls (local endpoints are never cached)
     call 1: 4.74s, server requests=1, cache entries=0
     call 2: 5.00s, server requests=1, cache entries=0
  ```

- **Impact:** while the lookup runs, every other request on the single uvicorn worker
  (`app.py:1306` starts uvicorn with no `workers=`) waits. The reachable case is a local endpoint
  that is slow to answer, wedged, or unreachable-but-not-refusing: a llama.cpp server busy loading a
  model, or a Tailscale peer that drops packets. `routes-chat-session` reports the same class of
  stall for `build_context_preface` (that section's "The chat path runs synchronous LLM, web-search
  and URL-fetch calls on the event loop"); this is a different callee on a different call site, and
  it fires on the Ollama stream path where that one does not.
- **Fix:** offload the two `httpx.get` calls, or the whole `get_context_length` call, with
  `asyncio.to_thread` at the four async call sites — the idiom this repository already uses for the
  identical defect in `_resolve_model` (`src/ai_interaction.py:275`, `:695`, `:1048`, pinned by
  `tests/test_resolve_model_offloaded.py`). An `async def get_context_length_async` avoids
  re-doing the offload at each caller, at the cost of a second entry point.

### [BUG] Context-length discovery sends no credential, so an authenticated endpoint's real window is never read

- **Location:** `src/model_context.py:450` (and `:424`, `:367`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_query_context_length(endpoint_url, model)` takes no headers and passes none, even
  though the callers hold the endpoint's credential: `maybe_compact(..., sess.headers, ...)` is
  invoked from `routes/chat_helpers.py:794` and then calls `get_context_length(endpoint_url, model)`
  without them (`src/context_compactor.py:338`). Against a stub endpoint whose `/v1/models` requires
  `Authorization: Bearer sk-probe-key` (`/tmp/probe/p_ctx_auth.py`):

  ```
  known table has 'unlisted-model-9': False

  get_context_length('unlisted-model-9') -> 128000
     GET /slots  Authorization=None   (endpoint answers 401)
     GET /v1/models  Authorization=None   (endpoint answers 401)

  what the same endpoint reports when the key is sent:
     unlisted-model-9: context_length=32768
  ```

- **Impact:** for an endpoint that requires a key on `/v1/models` and serves a model the built-in
  table does not list (`KNOWN_CONTEXT_WINDOWS`, `src/model_context.py:112`), the window is never
  read and the caller gets `DEFAULT_CONTEXT` (128000). In `routes/chat_helpers.py:790-800` that
  number is both the compaction threshold and the trim budget:

  ```python
  context_length = get_context_length(sess.endpoint_url, sess.model)
  ...
  messages = trim_for_context(messages, context_length)
  ```

  so a real window *smaller* than the default — a 32K model behind an authenticated vLLM or LiteLLM
  proxy — is never compacted or trimmed, and the request goes out over the window: the silent
  truncation the code's own comment at `routes/chat_helpers.py:744` warns about ("window is silently
  truncated there"). A real window *larger* than the default only costs an early compaction. The
  known-model table covers most well-known ids, which is why the fallback is invisible for common
  models.
- **Fix:** add `headers: Optional[dict] = None` to `get_context_length`, `get_context_length_known`,
  `_get_context_length_cached`, `_query_context_length` and `_proxy_catalog_context`, and pass
  `headers=headers` to the three `httpx.get` calls; every caller in this section already has the
  headers in scope. The cache key is `(endpoint_url, model)` today; the probe shows the same endpoint
  answers differently with and without a key, so a keyless result cached under that key would
  outlive the fix unless the key is cleared or the cache key includes the credential.

### [ERROR-HANDLING] A stream that ends without `[DONE]`, or is cut off at the token limit, is reported as a complete answer

- **Location:** `src/llm_core.py:3337-3343` (the end-of-stream block), `:3183-3191` (the delta parser)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the OpenAI-compatible parser reads only `delta` from the choice object; the
  `finish_reason` that rides in the same object is never read (it appears once in the file, in a
  comment at `:3141`):

  ```python
  _c0 = (j["choices"] or [None])[0]          # :3183
  if _c0 is None:
      continue
  delta = _c0.get("delta") or {}             # :3186
  ```

  and the end of the response is handled unconditionally, whether or not a terminator arrived:

  ```python
  # End of stream (no explicit [DONE] received)      # :3337
  for event in _format_routed_content(_harmony_router.flush()):
      yield event
  tc_event = _emit_tool_calls()
  if tc_event:
      yield tc_event
  yield "data: [DONE]\n\n"                            # :3343
  ```

  The real `stream_llm` driven against a stub server (`/tmp/probe/p_stream_cut.py`) emits the same
  events for a complete response, a response whose connection is closed after the first chunk, and a
  response the provider stopped at the limit:

  ```
  complete  -> ['data: {"delta": "Hello"}', 'data: [DONE]']
  cut       -> ['data: {"delta": "Hello"}', 'data: [DONE]']
  length    -> ['data: {"delta": "Hello"}', 'data: [DONE]']
  ```

  A cut tool call is emitted the same way, and its consumer then drops it:

  ```
  cut_tool  -> ['data: {"type": "tool_calls", "calls": [{"id": "", "name": "bash", "arguments": "{\\"command\\": \\"ls"}]}', 'data: [DONE]']

  function_call_to_tool_block('bash', '{"command": "ls') -> None
  function_call_to_tool_block('bash', '') -> ToolBlock(tool_type='bash', content='')
  ```

  The last two lines come from `src/tool_schemas.py:1370-1385`: truncated arguments fail `json.loads`, are
  logged as "Failed to parse function call arguments for bash", and the call is discarded; empty
  arguments coerce to an empty command. Two signals that would distinguish the cases are already in
  the protocol and unused: the requested final usage chunk (`stream_options: {"include_usage": True}`,
  `:2639-2640`, for every provider except OpenRouter and Groq) and `finish_reason`. The front end
  offers a manual "Continue" control for an interrupted message
  (`static/js/chat.js:1215-1235`), but nothing sets it from a stream that ended early.
- **Impact:** a reply the provider truncated — at the token limit, or because the connection dropped
  mid-answer — is persisted and displayed as a complete answer, and an agent turn whose tool call was
  cut off simply ends as if the model had chosen not to call one. Nobody sees an error. The stored
  message is also what the next turn's context is built from.
- **Fix:** forward the terminal chunk's `finish_reason` as its own SSE event and let the agent loop
  and the front end treat `length`/`max_tokens` as a truncation; alternatively treat a missing usage
  chunk as truncation when it was requested. Passing the field through is the smaller change and does
  not guess.

### [BUG] The `/slots` context probe loses its host for a base URL without a path

- **Location:** `src/model_context.py:423`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the probe target is built by string surgery:

  ```python
  base = endpoint_url.split("/v1")[0] if "/v1" in endpoint_url else endpoint_url.rsplit("/", 1)[0]
  r = httpx.get(f"{base}/slots", timeout=REQUEST_TIMEOUT)
  ```

  For a base URL with no path, `rsplit("/", 1)[0]` returns `http:/`, and `f"{base}/slots"` is
  `http://slots` — a request to a host named `slots`. Captured with a monkeypatched `httpx.get`:

  ```
  http://localhost:11434           -> ctx=128000
       requested http://slots   headers=None
       requested http://localhost:11434/api/tags   headers=None
  http://localhost:11434/v1        -> ctx=128000
       requested http://localhost:11434/slots   headers=None
  http://192.168.1.50:8080         -> ctx=128000
       requested http://slots   headers=None
  ```

  That request fails on DNS, and the failure is not instant:

  ```
  $ httpx.get('http://slots', timeout=5)
  failed after 3.98s: ConnectError: [Errno -2] Name or service not known
  ```

  A pathless base URL is a supported shape: the add-endpoint route only calls `normalize_base`,
  which strips suffixes and never adds `/v1` (`routes/model_routes.py:2011`), and `_detect_provider`
  classifies a pathless URL as Ollama. The cookbook's own local endpoints are created with `/v1`
  (`routes/cookbook_routes.py:1813`), where the probe URL is correct.
- **Impact:** every context lookup for a pathless endpoint pays a DNS lookup for `slots` — 3.98s
  measured here, bounded by the 5s timeout — and the llama.cpp `n_ctx` probe never runs. Ollama has
  no `/slots` endpoint, so for the shape that triggers it the lost value is only the wasted request;
  a llama-server configured without `/v1` loses the reported window and falls back to the models
  catalog or the default. The stall lands on the event loop through the previous finding.
- **Fix:** derive the probe target from the parsed URL —
  `f"{parsed.scheme}://{parsed.netloc}/slots"` — and skip the probe when the endpoint is Ollama,
  since `/slots` is a llama.cpp endpoint and `/api/tags` does not report a window.

### [ERROR-HANDLING] A 200 response with a non-JSON body escapes as a `JSONDecodeError` instead of the documented 502

- **Location:** `src/llm_core.py:2044` (`llm_call`), `:2429` (`llm_call_async`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `data = r.json()` sits one line above the schema guard that turns a bad body into a
  502:

  ```python
  if not r.is_success:
      raise HTTPException(502, f"Upstream {target_url} -> {r.status_code}: {r.text}")
  data = r.json()                       # :2044
  try:
      ...
  except Exception:
      raise HTTPException(502, f"Unexpected schema from {target_url}: {str(data)[:400]}")   # :2065
  ```

  `llm_call_async` repeats the shape (`data = r.json()` at `:2429`, inside no `try`). A stub server
  answering `200 text/html` with an nginx-style error page (`/tmp/probe/p_nonjson.py`):

  ```
  llm_call         raised JSONDecodeError: Expecting value: line 1 column 1 (char 0)
  llm_call_async   raised JSONDecodeError: Expecting value: line 1 column 1 (char 0)
  ```

  The route-fallback chain shows the inconsistency directly — the same HTML body is a friendly
  `HTTPException` when the status is 502 and an unhandled `JSONDecodeError` when it is 200
  (`/tmp/probe/p_nonjson2.py`):

  ```
  html200   raised JSONDecodeError: Expecting value: line 1 column 1 (char 0)
  real502   raised HTTPException: 502: local endpoint is having an outage (HTTP 502). <html>...
  ```

  The streaming path already handles the equivalent case by skipping the bad line
  (`:3333-3335`, "Error parsing stream data").
- **Impact:** a reverse proxy or gateway that answers 200 with an HTML body produces an unexpected
  exception type instead of the documented failure mode: `llm_call_async_with_route_fallback` cannot
  classify it, so a route returns a 500 traceback where every other upstream failure yields a clean
  502 with a friendly message.
- **Fix:** move `data = r.json()` inside the existing `try:` block in both functions, or add
  `except ValueError: raise HTTPException(502, f"Non-JSON body from {target_url}: {r.text[:200]}")`
  next to the existing status check.

### [BUG] `CHATGPT_SUBSCRIPTION_BASE_URL` cannot work: provider detection keys on the literal `chatgpt.com` host

- **Location:** `src/chatgpt_subscription.py:20-23` and `:64-75` (`is_chatgpt_subscription_base`), consumed by `src/llm_core.py:991-993` (`_detect_provider`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the module reads the environment variable into
  `DEFAULT_CHATGPT_SUBSCRIPTION_BASE_URL` (`:20-23`), and the classifier accepts only one host:

  ```python
  return host == "chatgpt.com" and (
      path == "/backend-api/codex" or path.startswith("/backend-api/codex/")
  )
  ```

  With the variable set to a gateway (`/tmp/probe/p_cgpt.py`):

  ```
  DEFAULT_CHATGPT_SUBSCRIPTION_BASE_URL = https://llm-gateway.internal.example/backend-api/codex
  is_chatgpt_subscription_base(base) = False
  _detect_provider(base)   = openai
  build_chat_url(base)     = https://llm-gateway.internal.example/backend-api/codex/chat/completions
  build_headers(token)     = [('Authorization', 'Bearer ACCESS-TOKEN')]

  the stock base URL for comparison:
    _detect_provider       = chatgpt-subscription
    build_chat_url         = https://chatgpt.com/backend-api/codex/responses
  ```

  The override is what the provisioner stores: `base_url=base` on the `ProviderAuthSession`
  (`routes/chatgpt_subscription_routes.py:51`) and on the `ModelEndpoint` it creates (`:71-78`), and
  `resolve_runtime_credentials` falls back to the same constant (`src/chatgpt_subscription.py:286`).
- **Impact:** an operator who points the subscription provider at a mirror or a gateway gets the
  OpenAI-compatible request path (`/chat/completions` instead of `/responses`), a plain bearer header
  without the Codex `Accept`/`Origin`/`Referer` set, and the OpenAI-compatible SSE parser instead of
  the Responses one — a 404 or a protocol mismatch on every request, with no error that names the
  cause. The model list is fetched from the hardcoded `https://chatgpt.com/...` URL regardless
  (`:94-98`), so the override is half-wired in either direction.
- **Fix:** have `is_chatgpt_subscription_base` also return True for
  `DEFAULT_CHATGPT_SUBSCRIPTION_BASE_URL`, or drop the environment override and hardcode the base in
  one place. If the variable is only a test seam, deleting it is the smaller change.

### [BUG] The local-model gate decrements its foreground-waiting counter twice per call

- **Location:** `src/llm_core.py:98` (increment), `:123` and `:135` (two decrements)
- **Severity:** low
- **Disposition:** next
- **Evidence:** a foreground request increments once and decrements on acquire *and* again in the
  `finally`:

  ```python
  if kind == "foreground":
      _LOCAL_MODEL_WAITING_FOREGROUND += 1                          # :98
  ...
  try:
      await _LOCAL_MODEL_LOCK.acquire()
      acquired = True
      if kind == "foreground":
          _LOCAL_MODEL_WAITING_FOREGROUND = max(0, _LOCAL_MODEL_WAITING_FOREGROUND - 1)   # :123
      ...
      yield
  finally:
      if kind == "foreground":
          _LOCAL_MODEL_WAITING_FOREGROUND = max(0, _LOCAL_MODEL_WAITING_FOREGROUND - 1)   # :135
  ```

  The counter is the signal that keeps background work out of the local model pipe
  (`while _LOCAL_MODEL_WAITING_FOREGROUND > 0 or has_foreground_activity(): await asyncio.sleep(0.25)`,
  `:115`). One holder and one waiter (`/tmp/probe/p_gate.py`):

  ```
  holder inside slot      : counter=0
  after B starts waiting  : counter=1 (B is waiting for the lock)
  after the holder exits  : counter=0 (B is still waiting)
  after B finishes        : counter=0
  ```

  The holder's `finally` clears the waiter's increment, so the counter reads zero while a foreground
  request is still waiting — exactly the window the signal exists for. A second foreground request
  arriving later can also have its own increment consumed by an earlier call's `finally`, because the
  `max(0, ...)` clamp hides the negative.
- **Impact:** a background request entering that window skips the busy-wait and queues directly on
  the lock, so the priority mechanism the docstring describes ("foreground chat taking priority",
  `:83`) is weaker than it reads. The mitigation is that `asyncio.Lock` serves its waiters in order,
  so the waiting foreground request is still served first and no foreground request is starved; this
  is a wrong signal, not a wrong order.
- **Fix:** delete the decrement at `:123` and keep the one in the `finally`, or move the increment
  into a `try` whose `finally` owns the single matching decrement.
