# tests: LLM, tools and agent loop

## Overview

This section covers the 121 test modules that pin the agent loop, the tool surface and the LLM call
path: `tests/test_agent_loop*`, `tests/test_action_intents*`, `tests/test_tool_*`,
`tests/test_skill*`, `tests/test_search_*`, `tests/test_research_*`, `tests/test_task*`,
`tests/test_scheduler*` and the MCP tests. Its job is not to describe what the tests are named
after, but to establish what they prove: whether a file drives the real loop or a transcription of
it, and whether its assertions would fail if the behaviour under test changed.

Boundary: the implementation defects those tests are meant to catch belong to `src-agent-loop`,
`src-tools-parse-exec`, `src-tools-capabilities-policy` and `src-tools-schema-index`; the route that
composes the per-turn tool set is `routes-chat-session`. This section reports test-side defects
only — a test that cannot fail, a fixture that replaces the thing under test, an assertion on a copy
of the code — and cross-references implementation findings instead of restating them.

Three surfaces the brief asked about, answered up front:

- **The per-turn tool gate that decides whether `bash` and `web_search` are offered.** Covered in
  this slice at the loop end: `tests/test_tool_policy.py` drives the real `stream_agent_loop` and
  measures 1,681 executed lines of `src/agent_loop.py`, including the disabled-tool filtering of the
  schema list and the blocked-before-execution path. The *composition* of that disabled set from
  `allow_bash` / `allow_web_search` / `can_use_bash` / `can_use_browser` is not covered here; it
  lives in `tests/test_chat_route_tool_policy.py`, whose functional half is a hand-written replica of
  `chat_stream`, already reported as `[BUG]` at `tests-session-chat-memory.md:134`.
- **The tool-schema-to-registry agreement.** `tests/test_tool_index_schema_parity.py` pins one edge
  (`FUNCTION_TOOL_SCHEMAS ⊆ BUILTIN_TOOL_DESCRIPTIONS`) and nothing else; the missing
  `schemas ⊆ TOOL_TAGS` edge that lets `tail_serve_output` be advertised to native models and
  rejected is reported at `src-tools-schema-index.md:149` and `:197`. Not restated here.
- **Stream completion and abort handling.** Genuinely covered.
  `tests/test_tool_task_cancelled_on_disconnect.py` closes the generator mid-tool-call and asserts
  the tool task observed cancellation from inside the same coroutine, and
  `tests/test_agent_rounds_exhausted.py` reaches the `rounds_exhausted` emitter
  (`src/agent_loop.py:6314`) and the intent-nudge emitter (`:5540`) under a line tracer. The
  `[DONE]`-synthesis defect is in `src/llm_core.py:3337-3343` and is covered by files outside this
  slice (`src-llm-core.md:274`, `tests-session-chat-memory.md:509`).

## Coverage

**Read fully (46 of 121).** Every line of:
`test_agent_loop.py`, `test_agent_loop_tool_output_truncation.py`, `test_action_intents.py`,
`test_action_intents_shell_verbs.py`, `test_agent_rounds_exhausted.py`, `test_agent_bash_windows.py`,
`test_agent_migration_manifest.py`, `test_agent_round_model_provenance_ui.py`,
`test_agent_tool_budget_nonnumeric.py`, `test_agent_tools_truncate_nonstring.py`,
`test_ask_user_persistence.py`, `test_bg_jobs_store.py`, `test_bg_monitor_stream.py`,
`test_compaction_summary_failure.py`, `test_loop_breaker_runaway.py`, `test_mcp_common_truncate.py`,
`test_mcp_dependency_compatibility.py`, `test_mcp_routes_shim.py`, `test_research_routes_shim.py`,
`test_research_session_id_validation.py`, `test_research_source_link_xss.py`,
`test_search_analytics_defaults.py`, `test_search_content_extraction_parity.py`,
`test_search_content_url_guards.py`, `test_search_module_consolidation.py`, `test_search_query.py`,
`test_search_routes_shim.py`, `test_skill_edit_no_collapse_on_outside_click_js.py`,
`test_skill_extractor_rows.py`, `test_skill_format_timestamp.py`, `test_skill_index_toolset_gating.py`,
`test_task_routes_shim.py`, `test_task_session_folder.py`, `test_tool_approval_frontend_routing.py`,
`test_tool_approval_single_action_scope.py`, `test_tool_implementations_shim.py`,
`test_tool_index_keyword_boundaries.py`, `test_tool_index_schema_parity.py`,
`test_tool_output_prompt_injection.py`, `test_tool_parsing_bare_end_marker.py`,
`test_tool_parsing_hermes_json.py`, `test_tool_parsing_nonstring.py`,
`test_tool_task_cancelled_on_disconnect.py`, `test_tool_utils_import_clean.py`, `test_tool_policy.py`,
`tests/conftest.py`.

**Read partially (3).** `test_agent_state_dir_confinement.py` — the module docstring, all 47 test
names, the default-roots block (`:60-160`) and three bodies (`:108-140`, `:487-506`, `:573-590`); it
is a behavioural suite that builds real temp trees, and every sampled body asserts on a runtime
result — `LsTool`/`GlobTool`/`GrepTool` output, `_agent_readable_data_subdirs()`, or a raised
`ValueError` — rather than on source text. `test_tool_path_confinement.py` — the first 70 lines and every file
I/O site; unit assertions against `_is_sensitive_path` plus temp-file round trips.
`test_app_db_permissions.py` — the first 60 lines: a subprocess-based `init_db()` test that checks
the real on-disk mode bits, with the umask caveat written into the docstring.

**Scanned but not read (all 121).** An AST pass over every assigned file recorded test and assert
counts, module-scope `sys.modules` stubbing, source-file reads, `monkeypatch` use, `importlib` /
`inspect` use and whether the file calls `stream_agent_loop`. That scan chose the files above; it is
not a coverage claim for the rest.

**Not opened (72).** Named so the shape of the gap is visible: the MCP group
(`test_mcp_add_server_args_validation`, `test_mcp_cache_invalidation`, `test_mcp_email_decode_header_spaces`,
`test_mcp_manager`, `test_mcp_memory_owner_scope`, `test_mcp_oauth`, `test_mcp_param_hint_hardening`,
`test_mcp_reconnect_args`, `test_mcp_tool_params_in_prompt`), the research group (15 files, including
`test_research_routes_path_confinement`, `test_research_owner_scope_routes`, `test_research_service`,
`test_research_utils`), the search group (13 files, including `test_search_ranking*`,
`test_search_config_no_key_leak`, `test_search_query_nonstring`), the skills group (14 files,
including `test_skill_importer_security`, `test_skill_importer_ssrf_redirect`,
`test_skills_manager_owner_isolation`, `test_skill_index_prompt_injection`), the task/scheduler group
(11 files), `test_tool_approvals`, `test_tool_approval_task_scope`, `test_tool_path_confinement`'s
remainder, `test_tool_rag_*`, `test_tool_support_heuristic`, `test_ask_user_tool`, `test_bg_job_tools`
and the three remaining `test_app_*` files. Their absence from the findings below is an absence of
evidence, not evidence of quality.

**Checks run.** All 121 assigned files, and separately the 57 files that mention `web_search`,
`SOURCES`, `web_sources` or `stream_agent_loop`; a line tracer over `src/agent_loop.py` for three of
those files; a one-line revert of the #443 fix in a throwaway copy of the tree
(`/tmp/odysseus-mut`), followed by the full suite there; and a probe that drives the real
`stream_agent_loop` with a `web_search` result carrying the `SOURCES` marker against both the
pristine tree and the copy. The repository itself was not modified; the mutation lives only in
`/tmp/odysseus-mut`.

```
$ venv/bin/python -m pytest -q $(cat /tmp/assigned.txt | tr '\n' ' ')
848 passed, 16 warnings in 50.44s
```

`tests-harness.md:139` already records the systemic version of the module-scope stub problem. The
concrete instance in this slice, measured with a `pytest_configure` probe that prints
`sys.modules` before any test module is imported:

```
$ PYTHONPATH=/tmp venv/bin/python -m pytest -q -p stubprobe tests/test_agent_loop.py -s
STUBPROBE already in sys.modules (stub skipped):
  sqlalchemy / sqlalchemy.orm / sqlalchemy.ext / sqlalchemy.ext.declarative /
  sqlalchemy.sql / sqlalchemy.sql.expression / src.database / core.models / core.database
STUBPROBE absent (stub WILL install): sqlalchemy.ext.hybrid, src.agent_tools
```

So 9 of the 11 stub targets in `tests/test_agent_loop.py:7-14` — and, by the same list, 9 of the 10
in `tests/test_compaction_summary_failure.py:12-19` — are already imported by `tests/conftest.py`,
and their `if mod not in sys.modules` guard never fires. Cross-referenced, not re-reported.

### [BUG] The `web_search` sources tests in `test_agent_loop.py` assert on a copy of the fix, so reverting the fix leaves the suite green

- **Location:** `tests/test_agent_loop.py:435`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `TestWebSearchSourcesKeyLookup` (`:435-504`) is the only test in the tree for the
  issue-#443 `<!-- SOURCES:…-->` extraction at `src/agent_loop.py:5883-5902`. No test in the class
  calls the loop, and `stream_agent_loop` appears in the file exactly once, in a docstring at
  `:437` (the other hits are the module name `src.agent_loop`, imported for its helpers):

  ```
  $ grep -n "stream_agent_loop\|src.agent_loop" tests/test_agent_loop.py
  15:_PREEXISTING_AGENT_LOOP = sys.modules.get("src.agent_loop")
  37:    from src.agent_loop import (
  437:    The sources-extraction block in stream_agent_loop must read from the
  ```

  Each test re-derives the value it asserts on from a local dict built by the fixture:

  ```python
  # tests/test_agent_loop.py:443-450
  _SOURCES = [{"title": "Example", "url": "https://example.com", "snippet": "test"}]

  def _make_result(self, key: str = "output") -> dict:
      sources_json = _json.dumps(self._SOURCES)
      text = f"Search results here.\n\n<!-- SOURCES:{sources_json} -->"
      return {key: text, "exit_code": 0}

  # :460-465
  def test_fixed_lookup_finds_output_key(self):
      """After the fix, "output" is checked first so _src_text is non-empty."""
      result = self._make_result("output")
      src_text = result.get("output") or result.get("results") or result.get("stdout") or ""
      assert src_text != ""
      assert "SOURCES" in src_text
  ```

  `src_text` is the test's own expression, character-for-character the line it claims to pin
  (`src/agent_loop.py:5883`). `test_old_lookup_missed_output_key` (`:452-458`) asserts the *pre-fix*
  expression returns `""` — true of any dict lacking a `results`/`stdout` key, and true whether or
  not the shipped code has the fix.

  A line tracer over the suite (`sys.settrace` + `pytest.main`, `/tmp/cov_probe.py`) shows the block
  never executes:

  ```
  $ venv/bin/python /tmp/cov_probe.py "src/agent_loop.py" tests/test_agent_loop.py
  54 passed, 1 warning in 0.26s
  PROBE target=src/agent_loop.py lines_hit=583      # highest line reached: 3454
  ```

  3454 is the final line of `stream_agent_loop`'s multi-line `def` statement, evaluated at import
  time; its first body statement is `src/agent_loop.py:3466`, and `:5883` is not among the 583 lines
  reached. The same tracer over `tests/test_tool_policy.py`, which does drive the loop, reaches
  1,681 lines of the same file.

  In a throwaway copy of the tree (`/tmp/odysseus-mut`), reverting the fix — `src/agent_loop.py:5883`
  reduced to `result.get("results") or result.get("stdout") or ""` — leaves the whole suite green:

  ```
  $ cd /tmp/odysseus-mut && venv/bin/python -m pytest -q tests/
  5945 passed, 11 skipped, 127 warnings in 142.20s (0:02:22)
  ```

  The revert is behaviour-changing, and the probe shows exactly what it changes:

  ```
  $ venv/bin/python /tmp/sources_probe.py /home/lhl/github/lhl/odysseus   # pristine
  event types: ['agent_prep', 'delta', 'tool_start', 'web_sources', 'tool_output', 'agent_step', ...]
  web_sources emitted: True
  SOURCES marker reached round-2 context: False

  $ venv/bin/python /tmp/sources_probe.py /tmp/odysseus-mut               # fix reverted
  event types: ['agent_prep', 'delta', 'tool_start', 'tool_output', 'agent_step', ...]
  web_sources emitted: False
  SOURCES marker reached round-2 context: True
  ```

- **Impact:** A maintainer reading `tests/test_agent_loop.py` concludes the #443 regression is
  pinned; it is not. The fix can be reverted, or a later refactor can move the extraction back to
  the `results`/`stdout` keys, with no failing test anywhere in the repository — the raw
  `<!-- SOURCES:{…} -->` blob then reappears in the model's round-2 context and the frontend
  source list stops being emitted. This is the highest-trust file in the slice, which makes the
  false signal worse than no test.
- **Fix:** Drive the loop: yield a `web_search` tool block from a fake `stream_llm_with_fallback`,
  return `{"output": "…<!-- SOURCES:[…] -->", "exit_code": 0}` from a fake `execute_tool_block`, and
  assert the `web_sources` event and that no message handed to the second round contains `SOURCES`
  (the harness in `tests/test_tool_policy.py:39-42` and `:100-124` is the shape to copy). Delete
  `test_old_lookup_missed_output_key`, which asserts the bug rather than the fix.

### [BUG] `test_research_session_id_validation.py` tests a private copy of the path-traversal regex, not the route that enforces it

- **Location:** `tests/test_research_session_id_validation.py:6`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** The module re-declares the pattern and asserts only on that declaration:

  ```python
  # tests/test_research_session_id_validation.py:6
  _SESSION_ID_RE = re.compile(r"^[a-zA-Z0-9-]{1,128}$")

  # :29-33
  def test_rejects_dot_slash_traversal(self):
      self.assertIsNone(_SESSION_ID_RE.fullmatch("../../data/auth"))

  def test_rejects_deep_traversal(self):
      self.assertIsNone(_SESSION_ID_RE.fullmatch("../../../etc/passwd"))
  ```

  The two production patterns it means to guard are
  `routes/research/research_routes.py:21` (`_SESSION_ID_RE = re.compile(r"^[a-zA-Z0-9-]{1,128}$")`,
  used by `_validate_session_id` at `:24-27`, which raises HTTP 400) and
  `src/research_handler.py:24` (`_RESEARCH_SESSION_ID_RE`, checked at `:54`). Both happen to be
  character-class-identical today, so the test is green — but nothing connects the copy to either
  one:

  ```
  $ grep -rn "_validate_session_id" tests/
  (no output, exit 1)
  $ grep -rn "_SESSION_ID_RE" tests/
  tests/test_research_session_id_validation.py:6:_SESSION_ID_RE = re.compile(r"^[a-zA-Z0-9-]{1,128}$")
  ... 13 more hits, all in the same file
  ```

  Tightening the test's copy would fail it; loosening either production regex, or deleting the
  `_validate_session_id` call from the route, would not.
- **Impact:** This is the only test covering the research `session_id` path parameter, and it cannot
  detect a regression in it. The route builds `f"{session_id}.json"` under the research storage root
  (`routes/research/research_routes.py:34-53`), so a loosened pattern is a path-traversal surface,
  and the test that a reviewer would cite as its guard would still pass.
- **Fix:** Import and call the real functions —
  `from routes.research.research_routes import _validate_session_id` and assert it raises
  `HTTPException` for each traversal string, plus one case for
  `src.research_handler._research_json_path`, which returns `None` for the same inputs. Keep the
  parametrised traversal list; drop the local `re.compile`.

### [BUG] `test_agent_loop_tool_output_truncation.py` never touches the agent loop, so the delegation it documents is unpinned

- **Location:** `tests/test_agent_loop_tool_output_truncation.py:1`
- **Severity:** low
- **Disposition:** next
- **Evidence:** The file name and docstring are about the loop — "Previously agent_loop sliced tool
  output to a hard character limit (`[:2000]` or `[:4000]`) with no signal to the UI that data was
  lost. Now it delegates to tool_utils._truncate" (`:3-6`) — and the word `agent_loop` appears only
  in that docstring:

  ```
  $ grep -n "agent_loop" tests/test_agent_loop_tool_output_truncation.py
  3:Previously agent_loop sliced tool output to a hard character limit ([:2000]
  ```

  The file's only import is the leaf helper (`:9`,
  `from src.tool_utils import _truncate, MAX_OUTPUT_CHARS`), and all five tests call `_truncate`
  directly. Nothing asserts that `src/agent_loop.py` calls it at its seven tool-output sites
  (`:4652`, `:4732`, `:5980`, `:5984`, `:5988`, `:5990`, `:5992`) or that the tool bubble carries the
  `... (truncated, N chars total)` suffix the docstring says the frontend depends on. The same leaf
  is covered twice more in this slice — `tests/test_agent_tools_truncate_nonstring.py:7` (via the
  re-export in `src/agent_tools/__init__.py:18`) and `tests/test_mcp_common_truncate.py:7` — so
  three files pin one function and none pins a caller.
- **Impact:** Replacing `_truncate(raw)` with a hard slice at any agent-loop call site — the exact
  regression the file is named for — produces no failure. A reader who greps for truncation
  coverage finds three green files.
- **Fix:** Add one test to this file that drives `stream_agent_loop` with a fake tool result longer
  than `MAX_OUTPUT_CHARS` and asserts the emitted `tool_output` event carries the truncation suffix,
  or rename the file to `test_tool_utils_truncate.py` and let the loop's use of it stand unclaimed.

### [BUG] `test_task_session_folder.py` asserts a substring of three function bodies, so nothing checks which session got the folder

- **Location:** `tests/test_task_session_folder.py:6`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** The file is three `inspect.getsource` substring checks and nothing else:

  ```python
  # tests/test_task_session_folder.py:6-11
  def test_llm_task_session_gets_tasks_folder():
      """_execute_llm_task must create sessions with folder='Tasks'."""
      source = inspect.getsource(TaskScheduler._execute_llm_task)
      assert 'folder="Tasks"' in source or "folder='Tasks'" in source, (
          "LLM task session creation must set folder='Tasks'"
      )
  ```

  (`:14-19` and `:22-27` repeat the pattern for `_deliver_task_result` and `_execute_research_task`.)
  No scheduler object is constructed and no session is created. The string is present today at
  `src/task_scheduler.py:1549`, `:1736` and `:2104`, each inside a `DbSession(...)` construction, so
  the assertion passes — but it would pass equally if the keyword were attached to a different
  object in the same function, if the folder were reassigned afterwards, or if the branch holding it
  became unreachable. `folder="Tasks"` appears nowhere else under `tests/`, so there is no
  behavioural coverage of this property at all.
- **Impact:** The folder value is what the client uses to treat a task session as transient
  (`static/js/sessions.js:1716` and `:1866`: `s.folder === 'Assistant' || s.folder === 'Tasks'`),
  so a session created without it is presented to the user as an ordinary chat instead of a task
  thread — and the test stays green through exactly that regression.
- **Fix:** Call the scheduler against a fake `db` session (the suites already stub `DbSession` in
  this area) and assert `sess.folder == "Tasks"` on the object the method adds, or assert on the
  `DbSession` kwargs captured by a fake. `tests/test_task_scheduler_session_delivery.py` is the
  harness to extend.

### [BUG] `test_tool_utils_import_clean.py` is blind to `import src.X`, the form its own docstring names

- **Location:** `tests/test_tool_utils_import_clean.py:13`
- **Severity:** low
- **Disposition:** next
- **Evidence:** The guard reads `src/tool_utils.py`, walks the AST, and checks only
  `ast.ImportFrom` nodes that carry a `module`:

  ```python
  # tests/test_tool_utils_import_clean.py:16-22
  for node in ast.walk(tree):
      if isinstance(node, (ast.Import, ast.ImportFrom)):
          if isinstance(node, ast.ImportFrom) and node.module:
              msg = f"Illegal project import in tool_utils.py: {node.module}"
              assert node.module in ("src.constants",) or not node.module.startswith(
                  "src."
              ), msg
  ```

  The `ast.Import` branch is entered and then discarded by the inner `isinstance`. Running the same
  loop over synthetic sources:

  ```
  $ python3 /tmp/import_guard_probe.py
  FAILS  (guard fires)  from src.settings import get_setting
  PASSES (guard blind)  import src.database
  PASSES (guard blind)  import src.database as db
  PASSES (guard blind)  from . import sibling
  PASSES (guard blind)  from src import database
  ```

  `from src import database` slips through as well, because the guard compares `node.module` to
  `"src.constants"` and tests `startswith("src.")` — the bare module name `"src"` satisfies neither
  condition and falls to the `not ...startswith("src.")` arm. The docstring's own example, "an
  import from src.settings, src.database, or any other project module" (`:3-4`), is what
  `import src.database` would look like.
- **Impact:** The circular-import contract the module documents at `src/tool_utils.py:1-6` is guarded
  for one of the three import forms. The most natural way to break it — `import src.database` or
  `from src import database` at the top of the file — is invisible to the guard, and the failure it
  produces (a partially initialized module) surfaces as an unrelated error somewhere else.
- **Fix:** Handle both node types: for `ast.Import`, check each `alias.name`; for `ast.ImportFrom`,
  also reject `node.module == "src"` and any `node.level > 0`. Two lines, and the guard then covers
  the import form it was written to catch.

### [BUG] `test_mcp_keyword_gate_matches_literal_mcp_requests` asserts a frozenset's contents, not the gate

- **Location:** `tests/test_agent_loop.py:63`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** The whole test is one membership assertion on a module constant:

  ```python
  # tests/test_agent_loop.py:63-64
  def test_mcp_keyword_gate_matches_literal_mcp_requests():
      assert "mcp" in _MCP_KEYWORDS
  ```

  The behaviour the name describes is the substring gate in the tool-selection block,
  `wants_mcp = any(keyword in _last_user.lower() for keyword in _MCP_KEYWORDS)`
  (`src/agent_loop.py:4521`), which decides whether MCP tools are offered for a turn. The assertion
  is true for every possible user message and would stay true if the gate at `:4521` were deleted,
  inverted, or fed the wrong text. `_MCP_KEYWORDS` itself is defined at `src/agent_loop.py:919`.
- **Impact:** Low on its own, but it sits in the file a maintainer trusts most and its name reads as
  behavioural coverage of the MCP gate, which this slice does not have.
- **Fix:** Drive the loop the way `tests/test_tool_policy.py:100-124` does and assert the schema
  list handed to `stream_llm_with_fallback` contains the MCP route schemas for a turn whose text
  contains an MCP keyword and not for one that does not — that is the only way to reach the gate,
  which lives in the nested `_tool_schemas_for_route` (`src/agent_loop.py:4486`, used at `:4522`).
  Failing that, rename the test to `test_mcp_keywords_include_mcp` so it stops claiming to cover the
  gate.
