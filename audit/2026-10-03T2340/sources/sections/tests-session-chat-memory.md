# tests: session, chat, memory and RAG

## Overview

`tests/test_chat_attachment_picker.py`, `tests/test_chat_cached_model_normalization.py`, `tests/test_chat_helpers.py`, `tests/test_chat_helpers_bg_tasks_tracked.py`, `tests/test_chat_image_routing.py`, `tests/test_chat_metrics.py`, `tests/test_chat_model_provenance_js.py`, `tests/test_chat_preprocess_tool_policy.py`, `tests/test_chat_processor_pinned_memory.py`, `tests/test_chat_processor_web_search.py`, `tests/test_chat_route_tool_policy.py`, `tests/test_chat_stream_errors_js.py`, `tests/test_chat_stream_scope.py`, `tests/test_chat_tool_screenshot_xss.py`, `tests/test_chat_upload_limit_config.py`, `tests/test_chat_url_prefetch_failure_context.py`, `tests/test_chatgpt_subscription_routes.py`, `tests/test_chroma_client.py`, `tests/test_context_budget.py`, `tests/test_context_cache_per_endpoint.py`, `tests/test_context_compactor.py`, `tests/test_context_compactor_nonstring.py`, `tests/test_memory_add_submit_regression.py`, `tests/test_memory_audit_timeout.py`, `tests/test_memory_bullet_extraction.py`, `tests/test_memory_cli_add_nondict.py`, `tests/test_memory_extract_chat_nondict.py`, `tests/test_memory_extraction_parse.py`, `tests/test_memory_extractor_rows.py`, `tests/test_memory_extractor_vector_cross_tenant.py`, `tests/test_memory_extractor_vector_degraded.py`, `tests/test_memory_fallback_dislike.py`, `tests/test_memory_imports.py`, `tests/test_memory_owner_isolation.py`, `tests/test_memory_provider.py`, `tests/test_memory_recall_nondict_rows.py`, `tests/test_memory_routes_session_owner.py`, `tests/test_memory_routes_shim.py`, `tests/test_memory_store_unreadable_no_wipe.py`, `tests/test_memory_validate_entries_nondict.py`, `tests/test_personal_delete_file_confinement.py`, `tests/test_personal_dir_symlink_escape.py`, `tests/test_personal_docs_exclusions.py`, `tests/test_personal_docs_keyword_nondict.py`, `tests/test_personal_docs_lists.py`, `tests/test_personal_docs_office_index.py`, `tests/test_personal_docs_pdf_index.py`, `tests/test_personal_docs_state_store.py`, `tests/test_personal_index_hidden_dirs.py`, `tests/test_personal_remove_dir_confinement.py`, `tests/test_personal_upload_isolation.py`, `tests/test_personal_upload_privilege.py`, `tests/test_rag_index_hidden_dirs.py`, `tests/test_rag_keyword_fallback_owner.py`, `tests/test_rag_manager_owner_compat.py`, `tests/test_rag_remove_directory_scope.py`, `tests/test_rag_search_signature.py`, `tests/test_rag_server_directory_nonstring.py`, `tests/test_rag_vector_id_stability.py`, `tests/test_rag_vector_rename_owner.py`, `tests/test_searchservice_search_call.py`, `tests/test_session_actions_cleanup.py`, `tests/test_session_concurrent.py`, `tests/test_session_context_excludes_slash.py`, `tests/test_session_discovery_message_count.py`, `tests/test_session_endpoint_owner_scope.py`, `tests/test_session_export_filename.py`, `tests/test_session_export_nonstring_content.py`, `tests/test_session_ghost_delete.py`, `tests/test_session_image_cleanup.py`, `tests/test_session_list_owner_scope.py`, `tests/test_session_manager.py`, `tests/test_session_manager_cleanup.py`, `tests/test_session_manager_persist_guard.py`, `tests/test_session_mode_helpers.py`, `tests/test_session_owner_attribution.py`, `tests/test_session_routes_utcnow.py`, `tests/test_session_search.py`, `tests/test_session_search_batch_fetch.py`, `tests/test_session_tools_registry.py`, `tests/test_topic_analyzer.py`.

This section asks what these 81 modules prove, not whether they pass. Most of them are
regression pins written against a specific reported bug, so the question for each is: what is
the assertion, what is the fixture, and which edit to the production code would make it fail?
The two answers this section spends its findings on are "the assertion is a substring of the
production source" and "the fixture is a re-implementation of the production logic".

The boundary: the test harness itself (`tests/conftest.py`, `tests/helpers/*`,
`tests/TESTING_STANDARD.md` as an artifact) belongs to `tests-harness`; it is cited here only
as the repository's own rulebook. The production code these files pin belongs to
`src-chat-session`, `src-memory-rag`, `src-llm-core`, `core-auth-session`, `services-memory`,
`routes-chat-session`, `routes-rest-memory-personal-research`, `static-js-chat` and the other
matching sections. Where a weak test sits on top of a defect another section already reports,
this section names the test and cross-references the defect rather than restating it.

## Coverage

**Read fully:** all 81 assigned files, 7,682 lines. The largest are `tests/test_chat_helpers.py`
(582), `tests/test_chat_route_tool_policy.py` (344), `tests/test_session_search.py` (298),
`tests/test_context_compactor.py` (294), `tests/test_memory_routes_session_owner.py` (289),
`tests/test_chatgpt_subscription_routes.py` (280), `tests/test_memory_store_unreadable_no_wipe.py`
(255), `tests/test_chat_metrics.py` (214), `tests/test_chat_model_provenance_js.py` (203),
`tests/test_session_tools_registry.py` (198), `tests/test_session_manager.py` (194); the
remainder are between 6 and 181 lines each. Nothing in the assigned list was left unopened.

**Read partially — the production code each finding rests on:** `routes/chat_routes.py`
`:305-317` (`_BROWSER_MCP_TOOLS`), `:428-441` (`_clear_orphaned_session_endpoint`), `:493-510`,
`:541-575`, `:1478-1620` (the `disabled_tools` block) and the four `owner_filter(q,
ModelEndpoint, owner)` sites; `routes/chat_helpers.py:520-580` (`_match_cached_model_id`,
`_normalize_model_id_from_cache`) and `:752`; `routes/session_routes.py:260-290` (the incognito
purge); `src/agent_loop.py:4225-4250` (the hard-max read); `src/llm_core.py:3335-3345` (the
end-of-stream block); `src/memory.py:261-280` (`save`); `static/js/chat.js:2790-2796`,
`:3975-3990`; `static/js/chatRenderer.js:33-54`; `static/js/chatStreamErrors.js` (whole, 23
lines); `tests/TESTING_STANDARD.md:88-133` (the determinism and behavioral-first rules);
`tests/pr6020`-style Node harness idioms in `tests/test_pr6020_browser_review_regressions.py`
`:26-56`. Line numbers are the working tree at `2992bf6d368a`.

**Not read:** the production modules these tests cover beyond the ranges above — `src/memory.py`
beyond `save`/`load_all_for_update`, `src/personal_docs.py`, `src/rag_vector.py`,
`src/rag_manager.py`, `src/context_compactor.py`, `src/topic_analyzer.py`, `core/session_manager.py`,
`core/database.py` beyond `get_db_session`/`get_session_mode`/`set_session_mode`,
`mcp_servers/memory_server.py`, `mcp_servers/rag_server.py`, and every other section's paths.
`static/js/chat.js` and `static/js/chatRenderer.js` were read only at the cited ranges. The
81 test files are the coverage claim; the code they exercise is the other sections' claim.

**Checks run:** the assigned set in one process, and the probes quoted in the findings:

```
$ venv/bin/python -m pytest -q <the 81 files>
360 passed, 6 warnings in 6.85s

$ venv/bin/python -m pytest -q --collect-only <the 81 files>
360 tests collected in 5.48s
```

**Zero skipped, zero xfail** in the assigned set. Five `pytest.skip("node is not installed")`
guards exist and none fired — four in `tests/test_chat_model_provenance_js.py:17`, `:66`, `:129`,
`:168` and one in `tests/test_chat_stream_errors_js.py:17` (`node v24.16.0` is installed) — as do
three `importorskip` guards: `pytest.importorskip("chromadb")` at `tests/test_chroma_client.py:44`
(chromadb 1.5.9), `pytest.importorskip("mcp")` at
`tests/test_rag_server_directory_nonstring.py:11`, and the `importorskip("sqlalchemy")` plus
MagicMock guard at `tests/test_session_actions_cleanup.py:15-17` (sqlalchemy 2.1.3). The two
Node-backed files are the only tests here that execute the front-end code rather than reading it,
and they run in full.

### [BUG] `test_chat_tool_screenshot_xss.py` cannot detect the removal of either DOM-sink whitelist it names

- **Location:** `tests/test_chat_tool_screenshot_xss.py:36` (with `:17`, `:9`, `:41-48`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** every one of the file's eight tests asserts that a string appears in a JS file
  and that a known-unsafe string does not. The two that name the URL whitelists assert the
  *text of the regex* and the *name of the function at its call site*:

  ```python
  # tests/test_chat_tool_screenshot_xss.py:17-23
  def test_restored_tool_screenshot_uses_raster_data_url_whitelist():
      renderer = (_REPO / "static" / "js" / "chatRenderer.js").read_text(encoding="utf-8")

      assert "export function safeToolScreenshotSrc(raw)" in renderer
      assert "(?:png|jpe?g|gif|webp)" in renderer
      assert "safeToolScreenshotSrc(ev.screenshot)" in renderer
      assert 'src="${esc(ev.screenshot)}"' not in renderer

  # :36-50
  def test_generated_image_urls_are_vetted_before_assignment_or_open():
      ...
      assert "export function safeDisplayImageSrc(raw)" in renderer
      assert "safeDisplayImageSrc(imageUrl)" in renderer
      assert "img.src = safeImageUrl" in renderer
  ```

  Mutation probe: the tree was copied to `/tmp/audit-probe/fakerepo` and the body of
  `safeDisplayImageSrc` (`static/js/chatRenderer.js:41-53`) was replaced with
  `return String(raw || '');`, leaving the exported name and both call sites
  (`static/js/chatRenderer.js:1445`) byte-identical. The real test file, unmodified, was then run against
  that copy:

  ```
  $ cd /tmp/audit-probe/fakerepo && venv/bin/python -m pytest -q tests/test_chat_tool_screenshot_xss.py
  8 passed in 0.01s
  ```

  The same mutation applied to `safeToolScreenshotSrc` alone (`static/js/chatRenderer.js:33-39`) — the
  sink that renders an agent tool's screenshot into `static/js/chat.js:3706` — also leaves all eight
  green, because `assert "(?:png|jpe?g|gif|webp)" in renderer` is satisfied by the *sibling*
  function's regex. Only removing both regexes at once fails anything, and then only on the
  string assertion (`1 failed, 7 passed`). The whitelist itself is a four-alternative data-URL
  match; the behaviour it prevents — an arbitrary string reaching `img.src` and
  `window.open(...)` — is exactly what a Node test could call. `chatRenderer.js` is not
  importable as-is (`node --input-type=module -e "await import('file://.../chatRenderer.js')"`
  → `ReferenceError: HTMLInputElement is not defined`), but the repository already has both
  remedies in use: `static/js/chatStreamErrors.js` is a dependency-free helper imported directly
  by `tests/test_chat_stream_errors_js.py:22`, and
  `tests/test_pr6020_browser_review_regressions.py:32-44` ships an extracted source region to
  Node verbatim.
- **Impact:** the file's name and docstring ("Regression guards for agent-tool screenshot DOM
  sinks") are the only evidence a reviewer gets that the two XSS sinks are guarded. A change
  that turns either vetting function into a pass-through — the regression the guard exists for —
  ships green. `static-js-chat.md` reports the surrounding render paths as code; this finding is
  that the test cannot see them change.
- **Fix:** call the exported helper under Node the way `test_chat_model_provenance_js.py` calls
  `chatModelProvenance.js`, asserting `safeToolScreenshotSrc('javascript:alert(1)') === ''` and
  `safeToolScreenshotSrc('data:image/svg+xml;base64,...') === ''`; if importing
  `chatRenderer.js` stays impractical, move the two helpers into a small dependency-free module
  (the `chatStreamErrors.js` pattern) and import that. Keep the call-site assertions as wiring
  checks only.

### [BUG] `test_chat_route_tool_policy.py`'s functional half re-implements the tool policy, and passes with `routes/chat_routes` unimportable

- **Location:** `tests/test_chat_route_tool_policy.py:133` (the copy; the real logic is
  `routes/chat_routes.py:1478-1515`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the file's own section header is "Functional tests of the disabled-tools logic",
  and the function those tests call is a transcription of `chat_stream`:

  ```python
  # tests/test_chat_route_tool_policy.py:133-142
  def _build_disabled_tools(
      allow_bash=None, allow_web_search=None, use_web=None,
      can_use_bash=True, can_use_browser=True,
      explicit_web_intent=False, global_disabled=None,
  ):
      """Replicate the disabled-tools logic from chat_stream for unit testing.
  ```

  17 of the file's 25 tests (the whole functional half, including the `#3229` cases the file
  was written for) call only that copy. Measured with a pytest plugin that makes
  `import routes.chat_routes` raise:

  ```
  $ PYTHONPATH=/tmp/audit-probe PYTEST_PLUGINS=block_chat_routes venv/bin/python -m pytest -q \
      tests/test_chat_route_tool_policy.py --deselect <the 6 source guards and 2 front-end guards>
  17 passed, 8 deselected, 1 warning in 0.08s

  $ PYTHONPATH=/tmp/audit-probe venv/bin/python -c "import block_chat_routes, importlib; \
      importlib.import_module('routes.chat_routes')"
  CONTROL OK: PROBE: routes.chat_routes import blocked
  ```

  The copy has already drifted from the code it transcribes. It disables `"builtin_browser"` in
  the prompt-web-intent branch (`:162`) and again for `can_use_browser=False` (`:175`); the real
  branch (`routes/chat_routes.py:1501-1510`) ends at `"api_call"`, and the browser tools the
  production code actually disables are the twelve `mcp__builtin_browser__*` names in
  `_BROWSER_MCP_TOOLS` (`routes/chat_routes.py:305-317`, applied at `:1555` and `:1583`). The
  copy also omits the incognito block (`:1519-1529`), the active-email block, the
  delegated-credential block (`:1486`) and the plan-mode branch (`:1607-1608`).
- **Impact:** the per-turn tool gate is the mechanism that decides whether `web_search`,
  `web_fetch`, `bash` and `python` are offered to a model. A regression in `chat_stream`'s
  branch — the exact class of bug the file's docstring says it pins — cannot fail any of these
  17 tests, because they never run that branch. The green file is counted as coverage for the
  web/bash toggles.
- **Fix:** drive the real handler with a `TestClient` request that sets `allow_bash` /
  `allow_web_search` and assert on the tool set the loop receives, or extract
  `chat_stream`'s disabled-tools block into a named helper in `routes/chat_routes.py` and call
  it. Delete `_build_disabled_tools`; a copy that must be kept in sync by hand is a liability,
  not a fixture.

### [BUG] `test_session_concurrent.py` runs no concurrency, and the memory-store write race has no test in this section

- **Location:** `tests/test_session_concurrent.py:35` (with `:64`, `:106`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the module docstring says "These tests verify that the async streaming chat path
  maintains session isolation even under concurrent access patterns" (`:1-5`), and its three
  tests `await asyncio.gather(...)` over coroutines that contain no `await`:

  ```python
  # tests/test_session_concurrent.py:29-38
  async def add_to_session(sid, msgs):
      sess = sm.sessions[sid]
      for role, content in msgs:
          sess.add_message(ChatMessage(role, content))

  # Simulate concurrent adds
  await asyncio.gather(
      add_to_session("sess-a", [("user", "hello from A"), ("assistant", "reply A")]),
      add_to_session("sess-b", [("user", "hello from B")]),
  )
  ```

  With no suspension point inside the loop body, asyncio runs each coroutine to completion
  before starting the next. Reproducing the same shape with an execution-order log and
  `sys.setswitchinterval(1e-6)` to force GIL hand-offs:

  ```
  $ venv/bin/python /tmp/audit-probe/probe_session_concurrent.py
  interleaving log: a:0 a:1 a:2 a:3 a:4 b:0 b:1 b:2 b:3 b:4 a:0 a:1 a:2
  switches between different sessions while one was mid-loop: 2
  ```

  Every coroutine ran straight through; the two "switches" are the hand-offs between whole
  coroutines. The tests also bypass the store entirely (`sm.sessions = {}`, "Bypass DB load"),
  so nothing in the file touches the async chat path, the DB, or a lock. `src-memory-rag.md:38`
  reports the concurrency defect that this surface is named for — `MemoryManager.save` staging
  every writer through the fixed temp name `memory.json.tmp` (`src/memory.py:275-278`) — and no
  assigned file exercises it: `grep -n "threading\|Thread(\|multiprocessing\|executor\|asyncio.gather\|create_task"
  <the 81 files>` returns `test_session_concurrent.py:35`, `:64`, `:106` and the AST guard in
  `tests/test_chat_helpers_bg_tasks_tracked.py`, which only inspects `asyncio.create_task` calls
  statically and starts no task. `tests/test_memory_store_unreadable_no_wipe.py:19`
  states the scope of the nearest neighbour explicitly: "A live exclusive lock is NOT the
  dangerous case". Two writers released at once is.
- **Impact:** the only file in the suite whose name claims concurrent-session and concurrent-write
  coverage cannot fail for any scheduling reason, and the run's highest-severity defect has no
  failing test to mark the fix. A reader who greps for "concurrent" finds this file and stops.
- **Fix:** drive the store the way `tests/test_memory_store_unreadable_no_wipe.py` already does
  (a `MemoryManager` on `tmp_path`), release two writers with a `threading.Barrier` around
  `load_all_for_update()` → append → `save()`, and assert both entries survive. Keep the
  in-memory session-isolation assertions only if the coroutines gain a real suspension point;
  otherwise rename them to what they are (sequential isolation checks).

### [BUG] `test_agent_loop_reads_hard_max_setting` never touches the agent loop and asserts on its own copy of the parse

- **Location:** `tests/test_context_budget.py:113` (the test starts at `:101`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the docstring claims end-to-end coverage — "a saved settings.json value for
  agent_input_token_hard_max must reach compute_input_token_budget on the real agent_loop call
  path" (`:102-103`) — but the file never imports `src.agent_loop` (`grep -n agent_loop
  tests/test_context_budget.py` matches only those two prose lines). The second half
  re-implements the production parse in the test body and asserts on the re-implementation:

  ```python
  # tests/test_context_budget.py:113-124
  # Malformed value falls back to DEFAULT_HARD_MAX (defensive, matches the
  # try/except in src/agent_loop.py).
  f.write_text(json.dumps({"agent_input_token_hard_max": "huge"}), encoding="utf-8")
  monkeypatch.setattr(settings, "_settings_cache", None)
  raw = settings.get_setting("agent_input_token_hard_max", DEFAULT_HARD_MAX)
  try:
      parsed = int(raw)
  except (TypeError, ValueError):
      parsed = DEFAULT_HARD_MAX
  if parsed <= 0:
      parsed = DEFAULT_HARD_MAX
  assert parsed == DEFAULT_HARD_MAX
  ```

  The code this mirrors is `src/agent_loop.py:4236-4243`, followed by
  `compute_input_token_budget(..., hard_max=hard_max)` at `:4245-4250`. The assertion is true for
  any input the test can construct, because `parsed` is computed by the test itself. Deleting
  the `if hard_max <= 0` guard, or the whole `try/except`, from `src/agent_loop.py` leaves the
  test green. The first half (`:107-111`) does assert a real thing — that `settings.get_setting`
  reads the value out of the saved file — but that is `src/settings.py`'s behaviour, not the
  agent loop's.
- **Impact:** the only test named for the agent loop's hard-max plumbing does not execute it.
  The clamp that keeps a malformed settings value from reaching the token budget has no
  regression test; `src-chat-session.md:108` counts this file as passing coverage for the
  budget surface.
- **Fix:** either call the real helper that reads the setting out of `agent_loop`, or drive the
  budget branch through `agent_loop` with a small context window and assert the resulting
  `trim_for_context` budget. If neither is practical, drop "End-to-end" and "real agent_loop
  call path" from the docstring.

### [BUG] `test_chat_cached_model_normalization.py` is four source substrings, and the one behavioural test of the call site stubs the function out

- **Location:** `tests/test_chat_cached_model_normalization.py:8` (with `:16`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the whole 20-line file is `read_text()` plus `in`:

  ```python
  # tests/test_chat_cached_model_normalization.py:7-12
  def test_chat_context_uses_cached_models_before_live_model_probe():
      source = (ROOT / "routes" / "chat_helpers.py").read_text()

      assert "def _normalize_model_id_from_cache" in source
      assert "cached_models" in source
      assert "norm = _normalize_model_id_from_cache(sess) or normalize_model_id" in source
  ```

  `cached_models` appears exactly once in the module — the `getattr(ep, "cached_models", None)` at
  `routes/chat_helpers.py:563` — so that assertion only requires the one lookup line to survive;
  the function-name assertion is satisfied by the `def` line alone; and the third assertion pins
  an assignment's spelling, not that the cached value wins over the live probe. The functions are
  drivable: `_match_cached_model_id` (`routes/chat_helpers.py:520-531`) is pure, and
  `_normalize_model_id_from_cache` (`:534-580`) needs only a `SessionLocal` bound to a temp
  SQLite, which `tests/test_session_list_owner_scope.py:20-28` already demonstrates. The one
  test that reaches the call site (`routes/chat_helpers.py:752`) replaces the function with
  `lambda sess: None`:

  ```python
  # tests/test_chat_helpers.py:511-512
  monkeypatch.setattr(chat_helpers, "_normalize_model_id_from_cache", lambda sess: None)
  monkeypatch.setattr(chat_helpers, "normalize_model_id", lambda endpoint_url, model, **kwargs: None)
  ```
- **Impact:** the behaviour the file names — a session whose model id is normalized from the
  endpoint's cached model list *before* a live `/models` probe — has no test. Widening the
  cached path (for example returning a model id from another endpoint's cache) or inverting the
  precedence would keep all four assertions true. `tests/TESTING_STANDARD.md:118-124` names this
  pattern and requires the narrow exception to be justified in a docstring; this file has none.
- **Fix:** call `_match_cached_model_id` with a requested id and a model list (exact match,
  basename match, no match) and `_normalize_model_id_from_cache` with two endpoints in a temp
  DB, asserting which model id comes back; keep at most the precedence assertion as a comment.

### [BUG] The owner-scoping pin in `test_session_endpoint_owner_scope.py` survives deleting the filter it names

- **Location:** `tests/test_session_endpoint_owner_scope.py:96` (the assertions are `:101-106`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the last test in the file reads two route modules and asserts six substrings:

  ```python
  # tests/test_session_endpoint_owner_scope.py:96-106
  def test_chat_endpoint_recovery_paths_are_owner_scoped():
      root = Path(__file__).resolve().parents[1]
      chat_routes = (root / "routes" / "chat_routes.py").read_text(encoding="utf-8")
      chat_helpers = (root / "routes" / "chat_helpers.py").read_text(encoding="utf-8")

      assert "def _clear_orphaned_session_endpoint(sess, owner:" in chat_routes
      assert "def _recover_empty_session_model(sess, session_id: str, owner:" in chat_routes
      assert "q = owner_filter(q, ModelEndpoint, owner)" in chat_routes
      assert "resolve_session_auth(sess, session, owner=effective_user(request))" in chat_routes
      assert "def resolve_session_auth(sess, session_id: str, owner:" in chat_helpers
      assert "update_q = update_q.filter(DBSession.owner == owner)" in chat_helpers
  ```

  `q = owner_filter(q, ModelEndpoint, owner)` occurs four times in `routes/chat_routes.py`
  (`:437`, `:502`, `:571`, `:686`), so the assertion is not tied to the function it is written
  for. Mutation probe: delete line `:437` (the filter inside `_clear_orphaned_session_endpoint`,
  `:428`) from a copy of the module and re-evaluate all six assertions:

  ```
  $ venv/bin/python /tmp/audit-probe/probe_recovery_grep.py
  line 437 before mutation:             q = owner_filter(q, ModelEndpoint, owner)
  owner_filter(q, ModelEndpoint, owner) occurrences: original=4 mutated=3
  ALL ASSERTIONS STILL TRUE: True
  ```

  The file's other five test functions are behavioural — they call
  `_reject_raw_endpoint_url_for_non_admin` and `_reject_delegated_session_options` with
  `SimpleNamespace` requests and assert the 403 — so the file is not uniformly a grep test.
  The same class of assertion, with the same absence of a justifying docstring, appears in
  `tests/test_session_routes_utcnow.py:9-11` (`inspect.getsource` plus two negative substrings,
  which a `_dt.datetime.utcnow()` alias would satisfy) and
  `tests/test_memory_audit_timeout.py:5-10` (the path string is asserted inside a slice of the
  `_TIMEOUT_EXEMPT_PREFIXES` tuple, `app.py:180-191`, so a comment placed in the tuple would
  satisfy it as well as a live entry). `tests/TESTING_STANDARD.md:128-132` permits this shape
  only with a docstring saying why the invariant cannot be driven; none of the three has one.
- **Impact:** the recovery path that decides which endpoint a session falls back to — the same
  surface as the owner-scoping defects in `routes-chat-session.md` — is pinned by text that
  another call site supplies. Removing the owner filter from the helper would leave the suite
  green.
- **Fix:** seed a temp SQLite with two owners' endpoints and call
  `_clear_orphaned_session_endpoint(sess, owner)` and `_recover_empty_session_model(sess, sid,
  owner)`, asserting that only the caller's endpoint is chosen — the harness in
  `tests/test_session_list_owner_scope.py:20-28` is the pattern. Where a source assertion
  stays, add the docstring the standard asks for.

### [BUG] `test_delete_session_removes_from_cache` has no assertion

- **Location:** `tests/test_session_manager.py:101`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the test's entire body after the setup is a comment and `pass`:

  ```python
  # tests/test_session_manager.py:101-112
  def test_delete_session_removes_from_cache(self, sm):
      """delete_session must remove session from in-memory cache even when DB lookup fails."""
      s = Session(id="unique-del", name="ToDelete", endpoint_url="http://ep", model="model")
      sm.sessions["unique-del"] = s
      assert "unique-del" in sm.sessions
      sm.delete_session("unique-del")
      # Note: In production, delete_session also deletes from DB.
      # In this unit test without real DB, the cache entry is cleaned
      # by the method's DB-query path. If that path fails, the session
      # stays in cache — this is the pre-existing behavior.
      # The real fix is to always delete from cache regardless of DB result.
      pass
  ```

  The only assertion is that the key the test just inserted is present. The docstring states a
  property ("must remove session from in-memory cache even when DB lookup fails") that the test
  does not check, and the comment names the change that would satisfy it. The behaviour is
  pinned elsewhere — `tests/test_session_ghost_delete.py:117-123` monkeypatches `SessionLocal`
  to return no row and asserts `mgr.delete_session("ghost") is True` and that the key is gone —
  which is what this test should have been.
- **Impact:** a test that can only fail on the setup line is counted as coverage for the
  ghost-session cache eviction path (`core-auth-session` and `routes-chat-session` both discuss
  what that path leaves behind). Its name is misleading in a file whose other ten tests do
  assert.
- **Fix:** replace the body with the `tests/test_session_ghost_delete.py` shape — a `MagicMock`
  `SessionLocal` whose query returns no row, then `assert sm.delete_session("unique-del") is True`
  and `assert "unique-del" not in sm.sessions` — or delete the test and let the ghost-delete
  file own the property.

### [BUG] Six tests read their subject through a cwd-relative path, and one writes scratch state into the repository root

- **Location:** `tests/test_chat_stream_scope.py:6` (with `tests/test_memory_audit_timeout.py:5`,
  `tests/test_memory_add_submit_regression.py:14-15`, `tests/test_context_budget.py:95`,
  `tests/test_chat_helpers.py:176`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** four files read their subject through a CWD-relative path, unlike their
  siblings that anchor on `Path(__file__).resolve().parents[1]`:

  ```python
  # tests/test_chat_stream_scope.py:6
  source = Path("static/js/chat.js").read_text(encoding="utf-8")
  # tests/test_memory_audit_timeout.py:5
  source = Path("app.py").read_text()
  # tests/test_memory_add_submit_regression.py:14-15
  APP_JS = Path("static/app.js")
  INDEX_HTML = Path("static/index.html")
  # tests/test_context_budget.py:95
  src = Path("src/agent_tools/admin_tools.py").read_text()
  ```

  Measured by invoking the same four files from outside the repository root:

  ```
  $ cd /tmp && venv/bin/python -m pytest -q <repo>/tests/test_chat_stream_scope.py \
      <repo>/tests/test_memory_audit_timeout.py <repo>/tests/test_memory_add_submit_regression.py \
      <repo>/tests/test_context_budget.py
  6 failed, 12 passed, 1 warning in 0.30s
  ```

  `tests/TESTING_STANDARD.md:100-101` says "never assert against cwd-relative paths like
  `./data`. Use a temp workspace helper instead." Separately,
  `tests/test_chat_helpers.py:176` builds a scratch directory inside the repository rather than
  under pytest's `tmp_path`:

  ```python
  # tests/test_chat_helpers.py:175-177
  def _manifest_test_dir(name):
      root = Path(__file__).resolve().parents[1] / "tmp_pytest_probe" / f"{name}-{uuid.uuid4().hex}"
      root.mkdir(parents=True, exist_ok=False)
  ```

  Both manifest tests clean up with `shutil.rmtree(root, ignore_errors=True)` in a `finally`, so
  an ordinary run leaves only an empty `/home/lhl/github/lhl/odysseus/tmp_pytest_probe/` behind;
  `git check-ignore -v tmp_pytest_probe` exits 1, so a run killed between `mkdir` and the
  `finally` leaves an untracked directory in the working tree.
- **Impact:** the four CWD-relative files only pass when the invocation directory happens to be
  the repository root, which rules out running them from a checkout wrapper, a container with a
  different workdir, or an IDE test runner that sets its own root. The scratch directory is
  invisible to `git status` while empty, so residue from an aborted run is easy to miss.
- **Fix:** replace the four relative reads with `Path(__file__).resolve().parents[1] / ...`, and
  change `_manifest_test_dir` to take pytest's `tmp_path` instead of building under the repo
  root.

### [BUG] `test_session_list_owner_scope.py` drives the real session list but never reaches the incognito purge branch

- **Location:** `tests/test_session_list_owner_scope.py:55` (the purge is
  `routes/session_routes.py:269-271`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the file is the strongest session-ownership test in this section: it builds a
  real SQLite database, binds `routes.session_routes.SessionLocal` to it, stubs
  `effective_user` to return `"alice"`, resolves the real `GET /api/sessions` endpoint out of
  the router, and asserts `bob_id not in returned_ids`. It passes. But the two rows it seeds are
  ordinary named sessions:

  ```python
  # tests/test_session_list_owner_scope.py:55-58
  db.add(DbSession(id=alice_id, owner="alice", name="alice session", ...))
  db.add(DbSession(id=bob_id, owner="bob", name="bob session", ...))
  ```

  and the branch that deletes rows out of the same handler selects on a different name:

  ```python
  # routes/session_routes.py:269-271
  _ghosts = _purge_db.query(DbSession).filter(
      DbSession.name.in_(("Nobody", "Incognito")),
      DbSession.created_at < _cutoff,
  ).all()
  ```

  `_ghosts` is therefore empty for this test and the loop body — the `db.delete`, the message
  delete and the `session_manager.delete_session` call — never runs. `routes-chat-session.md:83`
  reports that branch as deleting every owner's incognito rows, and built its probe on this very
  harness; the missing pin is two rows away: rename them `Nobody` and back-date `created_at` by
  eleven minutes.
- **Impact:** the one test that exercises the real `/api/sessions` handler with two owners stops
  short of the multi-owner write in the same handler, so a reviewer reading it would conclude
  the endpoint's owner scoping is covered. The test's own harness is the right place to pin the
  reported defect.
- **Fix:** add a case that seeds one `Nobody`-named row per owner, older than the ten-minute
  cutoff, calls the same endpoint as alice, and asserts bob's row and its messages survive.

### [BUG] `test_chat_stream_errors_js.py` pins the client's EOF classification, but the server synthesizes the `[DONE]` that makes the client skip it

- **Location:** `tests/test_chat_stream_errors_js.py:27`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the test executes the real helper under Node and asserts that a client-side
  end-of-stream error is auto-retryable:

  ```javascript
  // tests/test_chat_stream_errors_js.py:26-28 (the script shipped to node)
  terminalRecoverable: isRecoverableStreamError(stringError),
  eofRecoverable: isRecoverableStreamError(new Error('Stream closed before completion')),
  networkRecoverable: isRecoverableStreamError(new TypeError('fetch failed')),
  ```

  That literal is the error the send path throws at `static/js/chat.js:3985`, guarded by
  `if (!_streamSawDone)` at `:3983`; `_streamSawDone` is set only when a `[DONE]` frame arrives
  (`:2794-2795`). The server emits that frame whether or not the provider sent one:

  ```
  $ venv/bin/python /tmp/audit-probe/probe_stream_truncation.py
  events delivered to the caller for a stream cut after one chunk (no [DONE] from upstream):
      data: {"delta": "Hello"}
      data: [DONE]
  ```

  (`src/llm_core.py:3343`, `yield "data: [DONE]\n\n"`, reached unconditionally at the
  "End of stream (no explicit [DONE] received)" comment at `:3337`.) So for the truncation case
  the client's EOF check is never entered, and the classification this test proves is never
  consulted. The server-side defect and its own measurement are `src-llm-core.md:274`.
- **Impact:** the front end's retry policy for a cut stream is tested at the helper boundary and
  cannot be reached end to end; a fix that forwards `finish_reason` or drops the synthetic
  `[DONE]` will need a client-side assertion that does not exist yet. The test itself is sound —
  it drives the module rather than reading it — this finding is about what it can see.
- **Fix:** keep this test, and add a case that drives `chat.js`'s reader loop (or the extracted
  region, as `tests/test_pr6020_browser_review_regressions.py:32-44` does) with a stream that
  ends without `[DONE]`, asserting the terminal-error path is taken.
