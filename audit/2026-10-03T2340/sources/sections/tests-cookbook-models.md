# tests: cookbook, models and providers

## Overview

The 112 pytest modules that pin the Cookbook (model serve, downloads, dependency installs, the
diagnosis tables) and the model/provider layer (`src/endpoint_resolver.py`, `src/llm_core.py`,
`src/model_capabilities.py` and the per-vendor readers, `src/cookbook_serve_lifecycle.py`, the
`services/hwfit` ranking helpers, the embedding lanes, and the small STT/TTS/YouTube regressions).
The boundary: the production modules these tests point at belong to `routes-cookbook`,
`routes-models`, `src-llm-core` and `services-hwfit`, which judge the behaviour; this section judges
only what the tests prove about it. Two consequences of that split are cross-referenced rather than
restated — the `_diagnose_serve_output` duplicate (`routes-cookbook`, finding at
`routes/cookbook_routes.py:432`) and the module-scope stub-leak pattern that `tests-harness`
already describes at `tests/conftest.py:20`.

## Coverage

Line numbers refer to `2992bf6d368a`; `git diff --stat 2992bf6d368a -- tests/` is empty, so the
working tree matches the reviewed commit for every path below.

**Read fully (59 of 112 files, 5,162 lines):**

- all 23 `tests/test_cookbook_*.py` files
- the whole `tests/test_provider_endpoints_*.py` group, plus `test_provider_label_js.py`,
  `test_providers_mixtral_logo_js.py` and `test_provider_device_flow_js.py`
- all three `tests/test_endpoint_resolver_*.py` files
- `test_model_interaction_registry.py`, `test_model_helper_owner_scope.py`,
  `test_model_name_tooltip.py` and `test_model_sort_js.py`
- `test_gpu_compose_standalone.py`
- five of the seventeen `tests/test_hwfit_*.py` files, named by their suffix: bandwidth_nonstring,
  gpu_count_nonnumeric, models_nonstring_fields, params_b_malformed and remote_validation
- `test_llm_core_concurrency.py`, `test_llm_core_connect_timeout.py`,
  `test_llm_core_reasoning_content_fallback.py` and `test_llm_core_sanitize_tool_calls.py`
- `test_embedding_cache_confinement.py` and `test_embedding_endpoint_config.py`
- three of the four `tests/test_tts_*.py` files, plus `test_stt_leak.py`
- all five `tests/test_youtube_*.py` files

**Sampled: the region each claim rests on, plus the whole test-name index (5 files, 2,732 lines).**
Every one of the 112 files was parsed to an AST index of its test-function names, so the *names* of
all 929 test functions were read. Beyond that I opened:

- `tests/test_llm_core_fallback.py`: the fallback-eligibility region `:1400-1500`, plus greps over
  the whole file
- `tests/test_model_capability_readers.py`: imports and `:1-80`, then the test-name index
- `tests/test_endpoint_owner_scope_followup.py`: the three source-text tests at `:360-414`
- `tests/test_tts_service_enforce_cache_limit.py`: `:19-96`
- `tests/test_hwfit_container_visibility_warning.py`: `:1-47`

Selection rule: I read in full every file that is itself a source-text or JavaScript assertion
(because that is this section's subject), every file named by the run brief's two priority surfaces
(Cookbook shell-command construction, provider URL handling), and every file that a `grep` over the
slice flagged as a `*_js.py` or `read_text` module. I sampled the remaining groups by reading
their test names and grepping them for the failure shapes this section hunts, rather than by
reading their bodies:

- `test_llm_core_*` transport
- `test_hwfit_*` ranking
- `test_embedding_lanes*`
- `test_provider_classification*` and `test_provider_detection_*`

**Not read at all (48 files, 8,363 lines):**

- the six `tests/test_embedding_lanes*.py` files, `test_embeddings.py` and `test_embeddings_client.py`
- `tests/test_endpoint_probing.py`
- eleven `tests/test_hwfit_*.py` files, named by their suffix: amd, apple_bandwidth,
  cpu_arch_detection, cpu_only_fallback, gemma4_12b, macos, manual_backend, native_quant_labels,
  quant_formats, unified_nvidia and windows
- seventeen `tests/test_llm_core_*.py` files (Anthropic cache and temperature, Mistral content,
  Ollama, reasoning, streaming, SSE, usage deltas, thinking models)
- five `tests/test_model_*.py` files, named by their suffix: capabilities, context, defaults,
  discovery_status and routes. The last is 2,179 lines and is the largest single gap in this
  section.
- the six `tests/test_provider_classification*.py` and `test_provider_detection_*.py` files

For these I can say only that the collection succeeded and the tests passed; I make no claim about
what they prove, and the counts below should be read with that caveat. The provider **rejection**-path
question the brief raises is answered from the `test_provider_endpoints_*` and
`test_endpoint_resolver_*` files, which I did read fully. The unread
`test_provider_classification*` and `test_provider_detection_*` files are the classification
tables, not the URL builders.

**Checks run** (project venv, from the repository root):

```
$ venv/bin/python -m pytest -q tests/test_cookbook_*.py tests/test_embedding*.py \
    tests/test_endpoint_*.py tests/test_gpu_compose_standalone.py tests/test_hwfit_*.py \
    tests/test_llm_core_*.py tests/test_model_*.py tests/test_provider_*.py tests/test_stt_leak.py \
    tests/test_tts_*.py tests/test_youtube_*.py
4 failed, 1222 passed, 1 skipped, 1 warning in 14.12s      # the 4 are the first finding below

$ venv/bin/python -m pytest -q          # whole suite, the CI command (.github/workflows/ci.yml:145)
5952 passed, 4 skipped, 127 warnings in 139.91s (0:02:19)

$ venv/bin/python -m pytest -q tests/test_model_interaction_registry.py
5 passed, 1 warning in 0.09s
```

The whole-suite run is green and the slice run is not, and the difference is a collection-order
effect rather than a difference in the tests; that is finding 1. Nothing else in this section reaches
the network or the wall clock. The probes are all under `/tmp` (`/tmp/probe/block_module.py`, a
`find_spec`-raising pytest plugin; `/tmp/grepprobe/`; `/tmp/jsprobe/`) and none of them wrote inside
the repository.

Three shapes I looked for and cleared, so a later reader does not re-open them. The
`_pip_install_attempt` tests (`tests/test_cookbook_helpers.py:465-519`) look like they hit the
network, but `python3 -m pip install __nonexistent_package_12345__` fails locally on the invalid
requirement name in under a second and the whole selection runs in 0.48 s. `tests/test_stt_leak.py:16-30`
scans the global temp directory rather than a `tmp_path`, which is a fragility rather than a false
pass: the `.webm` suffix it filters on is the real one (`services/stt/stt_service.py:97`) and the
`finally` unlink it pins is at `:113-115`. And `tests/test_cookbook_download_toast_duration.py`'s
line-oriented regex (`:19-27`) fails rather than silently passing when a toast call is reformatted
onto several lines, because `assert lines` at `:23` catches the empty selection first.

### [FOOTGUN] Four tests in this slice fail whenever they are selected after two sibling files that leave `src.agent_tools` as a `MagicMock`

- **Location:** `tests/test_llm_core_reasoning_content_fallback.py:101` (with
  `tests/test_llm_core_sanitize_tool_calls.py:23`, `tests/test_model_interaction_registry.py:17`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** both `test_llm_core_*` files install module-scope stubs during collection and never
  remove them:

  ```python
  # tests/test_llm_core_reasoning_content_fallback.py:101-109
  for _mod in [
      "sqlalchemy", "sqlalchemy.orm", "sqlalchemy.ext",
      "sqlalchemy.ext.declarative", "sqlalchemy.ext.hybrid",
      "sqlalchemy.sql", "sqlalchemy.sql.expression",
      "src.database", "src.agent_tools",
      "core.models", "core.database",
  ]:
      if _mod not in sys.modules:
          sys.modules[_mod] = MagicMock()
  ```

  `tests/test_llm_core_sanitize_tool_calls.py:23-30` is the same loop with the same names. The root
  conftest pre-imports only five modules: `sqlalchemy` and `sqlalchemy.orm`, then `core.database`,
  `src.database`, `core.models` (`tests/conftest.py:25-31`, `:53-57`), so `src.agent_tools` is
  not protected. If it has not been imported by the time either file is collected, the guard fires
  and the stub stays in `sys.modules` for the rest of the session.
  `tests/test_model_interaction_registry.py:17` binds
  `from src.agent_tools import model_interaction_tools as mit`, so it then tests a mock. Measured:

  ```
  $ venv/bin/python -m pytest -q tests/test_model_interaction_registry.py
  5 passed, 1 warning in 0.09s

  $ venv/bin/python -m pytest -q tests/test_llm_core_reasoning_content_fallback.py \
      tests/test_model_interaction_registry.py
  E   AssertionError: chat_with_model missing from TOOL_HANDLERS
  E   assert 'chat_with_model' in TOOL_HANDLERS
  E   ValueError: a coroutine was expected, got <MagicMock name='mock.model_interaction_tools.ChatWithModelTool().execute()'>
  FAILED tests/test_model_interaction_registry.py::test_model_interaction_tools_registered
  FAILED tests/test_model_interaction_registry.py::test_chat_with_model_threads_owner_and_returns
  FAILED tests/test_model_interaction_registry.py::test_ask_teacher_threads_owner_and_marks_teacher
  FAILED tests/test_model_interaction_registry.py::test_list_models_no_endpoints
  4 failed, 6 passed, 1 warning in 0.18s
  ```

  A probe plugin that reports the module object at collection time confirms the stub, not the real
  package, is what the later file sees:

  ```
  $ PYTHONPATH=/tmp/probe venv/bin/python -m pytest -q -s -p watch_agenttools \
      tests/test_agent_loop.py tests/test_llm_core_reasoning_content_fallback.py \
      tests/test_model_interaction_registry.py
  [probe] collection_finish src.agent_tools = MAGICMOCK
  4 failed, 60 passed, 1 warning in 0.25s
  ```

  `tests/test_agent_loop.py:1-51` is the contrast: it installs the same stub set and then removes the
  ones it created in a `finally`, and it ships a test for exactly that
  (`tests/test_agent_loop.py:53`, `test_import_stubs_do_not_leak_into_later_tests`). The two
  `test_llm_core_*` files have no equivalent. The full suite passes because some file collected
  earlier imports the real `src.agent_tools`, which makes the `not in sys.modules` guard dead:
  the same probe over `venv/bin/python -m pytest -q -s -p watch_agenttools` prints
  `[probe] collection_finish src.agent_tools = module(/home/lhl/github/lhl/odysseus/src/agent_tools/__init__.py)`.
  `tests-harness` reports the general dead-guard property at `tests/conftest.py:20`; this is the
  concrete failure it predicts, in a file this section owns.
- **Impact:** the suite's verdict depends on which files are in the run, not on the code. Anyone
  running the two files they touched — a plausible focused selection for a change that spans the
  model-interaction tools and the agent loop — gets four failures that say nothing about their
  change, and the natural reading is that they broke the tool registry. Conversely, in the runs where
  the stub does install, `test_model_interaction_tools_registered` and the three behaviour tests are
  not testing the registry at all. `tests/TESTING_STANDARD.md:112-114` calls order-sensitivity a bug
  to fix rather than a constraint to encode.
- **Fix:** put the two stub loops under `tests.helpers.import_state.preserve_import_state`, which
  `tests/README.md:177` documents for exactly this, or copy `test_agent_loop.py`'s
  `_INJECTED_IMPORT_STUBS` / `finally` cleanup into both files.

### [BUG] The Cookbook source-text guards pass against a file with no implementation

- **Location:** `tests/test_cookbook_cpu_only_serve.py:22` (with `tests/test_cookbook_diagnosis_js.py:8`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** 57 of the 929 test functions in this slice assert only that a string appears in a
  production source file, and the two probes below show what that is worth. The #1291 guard is three
  regexes over `static/js/cookbook.js`:

  ```python
  # tests/test_cookbook_cpu_only_serve.py:22-32
  def test_cpu_only_drops_gpu_only_flags():
      text = SRC.read_text(encoding="utf-8")
      assert re.search(r"_cpuOnly\s*=\s*String\(f\.ngl\)\.trim\(\)\s*===\s*'0'", text), ...
      assert re.search(r"if\s*\(\s*f\.flash_attn\s*&&\s*!_cpuOnly\s*\)", text), ...
      assert "f.unified_mem && !_cpuOnly" in text, ...
  ```

  A mutant of `static/js/cookbook.js` in `/tmp/grepprobe/` that comments the three gates out and
  restores the pre-fix behaviour — `const _cpuOnly = false;` and `if (f.flash_attn) {` — still
  contains every asserted string, so the whole file passes:

  ```
  $ venv/bin/python -m pytest -q /tmp/grepprobe/tests/test_mutant.py     # only SRC differs
  15 passed in 0.02s
  ```

  The same shape, taken further: `tests/test_cookbook_diagnosis_js.py` asserts five substrings of
  `static/js/cookbook-diagnosis.js` (`:18-22`) and one quoted pip spec plus one "not in" (`:11-12`).
  Pointed at a file whose entire content is those strings inside comments, both tests pass:

  ```
  $ cat /tmp/jsprobe2/cookbook-diagnosis.js
  // Deleted implementation. Only the strings the tests assert on remain.
  // '"kernels<0.15"'
  // r"Python\.h"  r"libnuma\.so\.1"
  // "SGLang native kernel/runtime"
  // "libnuma-dev python3.12-dev build-essential"
  // "sglang-kernel"
  $ venv/bin/python -m pytest -q /tmp/jsprobe2/test_mutant.py
  2 passed in 0.00s
  ```

  The affected files and their shares are `test_cookbook_cpu_only_serve.py` 15 of 15,
  `test_cookbook_dependency_completion_regression.py` 9 of 9, `test_cookbook_same_host_server_profiles_js.py`
  5 of 6, `test_model_helper_owner_scope.py` 5 of 5, `test_model_name_tooltip.py` 3 of 4,
  `test_cookbook_helpers.py` 6 of 74, `test_cookbook_package_detection.py` 2 of 6,
  `test_cookbook_gemma4_thinking_template.py` 2 of 2, `test_cookbook_diagnosis_js.py` 2 of 2,
  `test_endpoint_owner_scope_followup.py` 2 of 11, `test_cookbook_endpoint_registration.py` 3 of 3,
  `test_cookbook_deps_recipes.py` 1 of 1, `test_cookbook_windows_stop_tree_js.py` 1 of 2 and
  `test_model_interaction_registry.py` 1 of 5. `tests/test_cookbook_cpu_only_serve.py:157` is the
  shape at its weakest — `assert 'if local_windows:' in routes`, a bare substring that any
  occurrence of the phrase satisfies, including one inside a comment.
  Not every one is worthless: `tests/test_cookbook_same_host_server_profiles_js.py:65-74` asserts that four
  specific `servers.find(s => s.host === …)` expressions are *absent*, and
  `tests/test_cookbook_gemma4_thinking_template.py:22` asserts a superseded template is absent, which do
  fail on a plausible regression. The files that execute their JavaScript instead —
  `test_cookbook_port_parsing_js.py`, `test_cookbook_progress_signal_js.py`,
  `test_model_sort_js.py`, `test_provider_device_flow_js.py`, plus `test_provider_label_js.py` and
  `test_providers_mixtral_logo_js.py` — can fail on a behaviour change and are the model the rest
  should follow.
- **Impact:** the #1291 CPU-only regression (a `-ngl 0` serve that also emits `--flash-attn on` and
  `GGML_CUDA_ENABLE_UNIFIED_MEMORY=1`) can be reintroduced by anyone who keeps the old line in a
  comment or an `else if`, and CI stays green. The same holds for the other 40 text assertions: they
  pin the *presence of an expression* in a file that is edited by hand, which is a much weaker
  property than the one their names and docstrings claim.
- **Fix:** for the gates, assert the rendered command instead of the source: `cookbook.js` builds the
  serve command from a form object, so a small Node harness of the kind
  `tests/test_cookbook_port_parsing_js.py:18-28` already uses can call the builder with `ngl: '0'`
  and assert `--flash-attn` is absent. Where a text assertion must stay, extract the *statement* the
  way `tests/test_model_helper_owner_scope.py:6-13` does with `ast.get_source_segment` and match on
  code lines rather than on the raw file, so a comment cannot satisfy it.

### [BUG] `test_remote_windows_stop_tree_payload_survives_shell_parsing` asserts on a payload the test writes itself

- **Location:** `tests/test_cookbook_windows_stop_tree_js.py:39`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the test's whole subject is a PowerShell string literal defined two lines above the
  assertion, and the production file it is named for is never opened in that function:

  ```python
  # tests/test_cookbook_windows_stop_tree_js.py:39-54
  def test_remote_windows_stop_tree_payload_survives_shell_parsing():
      ps = (
          "function Stop-Tree([int]$Id) { "
          "Get-CimInstance Win32_Process -Filter ('ParentProcessId = ' + $Id) "
          ...
      )
      remote_command = f'powershell -Command "{ps}"'
      shell_command = f"ssh -p 2222 winbox {_posix_quote(remote_command)}"

      argv = shlex.split(shell_command)

      assert argv == ["ssh", "-p", "2222", "winbox", remote_command]
  ```

  `RUNNING_JS` is read only in the other test (`:16`). Pointing it at a path that does not exist
  removes that test and leaves this one passing:

  ```
  $ venv/bin/python -m pytest -q /tmp/jsprobe/test_stoptree_missing.py
  FAILED test_stoptree_missing.py::test_windows_graceful_kill_reuses_recursive_stop_tree_helper
  1 failed, 1 passed in 0.02s
  ```

  What it actually proves is that `shlex.split` and the local `_posix_quote` (`:35-36`) round-trip a
  string the test itself composed — a property of the standard library, true for any payload. The
  real quoting lives in `static/js/cookbookRunning.js`'s `_shQuote` and `_winSessionStopTreePs`, and
  the sibling test at `:22-31` checks those only as substrings of the file.
- **Impact:** the payload-safety claim in the test's name has no test. If `_shQuote` or the
  `powershell -Command "…"` wrapper in `cookbookRunning.js` stops escaping correctly, both tests in
  this file keep passing while a remote Windows stop command arrives mangled or, worse, splits into
  extra arguments on the remote shell.
- **Fix:** build the command with the real helpers — `cookbookRunning.js` can be loaded under Node
  the way `tests/test_provider_label_js.py:25-36` loads `providers.js` (strip the `export`, run the
  function, feed its output to `shlex.split`) — or, if the file must stay a text test, assert on
  `_shQuote`'s body extracted with `ast`-style slicing rather than on a hand-copied payload.

### [BUG] `test_dispatched_via_registry_not_dispatch_ai_tool` examines the wrong branch, so its "no longer routed" check cannot fail

- **Location:** `tests/test_model_interaction_registry.py:93`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the test takes the *last* `elif tool in (` before the first occurrence of
  `from src.ai_interaction import dispatch_ai_tool`, which is not the branch it names:

  ```python
  # tests/test_model_interaction_registry.py:96-104
  source = (Path(__file__).resolve().parent.parent / "src" / "tool_execution.py").read_text(...)
  assert 'elif tool in ("chat_with_model", "ask_teacher", "list_models"):' in source

  marker = "from src.ai_interaction import dispatch_ai_tool"
  idx = source.index(marker)
  branch_head = source.rfind("elif tool in (", 0, idx)
  legacy_tuple = source[branch_head:idx]
  for name in _MODEL_TOOLS:
      assert f'"{name}"' not in legacy_tuple, f"{name} still routed via dispatch_ai_tool"
  ```

  Replaying the four lines against the file shows what `legacy_tuple` is:

  ```
  $ venv/bin/python - <<'PY'
  ... source = Path("src/tool_execution.py").read_text(); idx = source.index(marker)
  ... branch_head = source.rfind("elif tool in (", 0, idx)
  ... print(source[branch_head:idx])
  PY
  first marker index: 47156 line: 1170
  branch_head index: 47090 line: 1169
  elif tool in ("pipeline", "manage_memory", "ui_control"):
  ```

  The slice is the *pipeline* branch head (`src/tool_execution.py:1169`), which contains none of the
  three names by construction, so the loop is a tautology. The model-tools branch the test names is
  still present at `src/tool_execution.py:1152` — the first assertion requires that string to exist,
  which is the opposite of what the test's docstring says it checks ("no longer in the
  `dispatch_ai_tool` elif tuple"). `src/tool_execution.py:1152-1159` does route through the registry
  (`_document_tool_dispatch`), so there is no production defect here; the test simply cannot detect
  a regression to `dispatch_ai_tool`.
- **Impact:** the migration to the registry has a guard that reads as enforcement and enforces
  nothing. If a later edit moved `chat_with_model` back onto the `dispatch_ai_tool` branch, or added
  a fourth model tool to the legacy tuple, this test — the only test in the slice that looks at
  `src/tool_execution.py`'s dispatch — would still pass, and the failure would surface as a
  production bug rather than a red test.
- **Fix:** assert on the branch that is supposed to route through the registry: locate
  `elif tool in ("chat_with_model", "ask_teacher", "list_models"):` and assert that
  `_document_tool_dispatch` appears in its body before the next `elif`, or delete the first assertion
  and compare the tuple literals directly (`ast.literal_eval` on each `elif tool in (...)` target),
  which is what the test's docstring describes.

### [BUG] The only test that drives `POST /api/model/serve` to a shell launch captures the command and asserts nothing about it

- **Location:** `tests/test_cookbook_docker_access.py:232`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the fixture records every command handed to the shell, and the assertion is only that
  the list is non-empty:

  ```python
  # tests/test_cookbook_docker_access.py:198-200, :219-232
  async def launch(command, **kwargs):
      launched_commands.append(command)
      return _Process()
  ...
  monkeypatch.setattr(cookbook_routes.asyncio, "create_subprocess_shell", launch)
  ...
  assert checked_binaries == ["tmux", "docker"]
  assert launched_commands
  ```

  Printing the captured list in a `/tmp` copy of the test shows it holds exactly the tmux launch
  command that reaches the shell (`routes/cookbook_routes.py:2762` builds it, `:2772` runs it):

  ```
  [probe] shell command handed to create_subprocess_shell:
      'tmux set-option -g history-limit 100000 2>/dev/null; tmux new-session -d -s serve-2a76b38d
       /tmp/pytest-of-lhl/pytest-154/test_local_container_serve_all0/serve-2a76b38d_run.sh'
  ```

  This is the only test in the 112-file slice that reaches the shell: grepping the slice for
  `new-session`, `tmux set-option`, `launched_commands` or `create_subprocess_shell` finds this one
  capture and `tests/test_cookbook_remote_windows_diffusers.py:42`, which asserts the shell is *not*
  reached. The runner script itself is read once, at `:234`, and only for one substring
  (`assert "docker exec ollama-rocm ollama show llama3" in runner`). Nothing asserts the session name
  interpolation, the remote `scp`/`ssh` setup command (`routes/cookbook_routes.py:2756-2760`), the PATH
  exports, or the `export HF_TOKEN=…` line that `routes-cookbook` reports as world-readable
  (`routes/cookbook_routes.py:2165`).
- **Impact:** the one seam where a user-supplied value becomes a shell command has no assertion on
  the command. `routes-cookbook` reports the consequences elsewhere (the HF token in the runner, the
  GGUF-prelude bypass); what is missing here is the test that would have caught them, and the
  cheapest place to add it is a line in a test that already has the command in hand.
- **Fix:** assert the captured command — `assert launched_commands[0].startswith("tmux set-option -g
  history-limit 100000 2>/dev/null; tmux new-session -d -s ")` and that it ends with the quoted
  runner path — and add one assertion that the runner contains no `HF_TOKEN` when
  `load_stored_hf_token` is stubbed to return `""` (the fixture already stubs it at `:214`).

### [BUG] The provider rejection paths are pinned for `?` and `#` only; no test covers a bad scheme or a private address

- **Location:** `tests/test_endpoint_resolver_urls.py:68` (with `tests/test_provider_endpoints_url_building.py:24`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the three provider URL modules I read in full are happy-path tables plus one
  rejection case. `tests/test_endpoint_resolver_urls.py:68-76` and `:88-96` parametrize
  `"https://api.example.com/v1?token=abc"`, `"…#fragment"` and `"http://localhost:1234?"` against
  `pytest.raises(ValueError, match="query or fragment")` for both builders — that path is genuinely
  pinned, and it is the only rejection case in the group. `tests/test_provider_endpoints_url_building.py`
  is twelve `(base, chat_url, models_url)` triples (`:24-63`) and no failure case;
  `tests/test_provider_endpoints_normalization.py` and `tests/test_provider_endpoints_headers.py`
  likewise. Nothing in the 112-file slice passes a non-HTTP scheme or a link-local address to a
  builder. There is no scheme check to pin: calling the real builders with such inputs shows the
  `?`/`#` guard is the only validation in `src/endpoint_resolver.py:237-242`:

  ```
  $ venv/bin/python - <<'PY'
  ... from src.endpoint_resolver import build_chat_url, build_models_url
  ... for c in ["file:///etc/passwd", "javascript:alert(1)", "ftp://h/v1",
  ...           "http://169.254.169.254/latest/meta-data",
  ...           "http://localhost:1234/v1?api_key=x"]:
  ...     try: print(repr(c), "->", repr(build_chat_url(c)))
  ...     except Exception as e: print(repr(c), "-> RAISES", type(e).__name__, e)
  PY
  'file:///etc/passwd' -> 'file:///etc/passwd/chat/completions'
  'javascript:alert(1)' -> 'javascript:alert(1)/chat/completions'
  'ftp://h/v1' -> 'ftp://h/v1/chat/completions'
  'http://169.254.169.254/latest/meta-data' -> 'http://169.254.169.254/latest/meta-data/chat/completions'
  'http://localhost:1234/v1?api_key=x' -> RAISES ValueError: Endpoint base URL must not include query or fragment
  ```

  `src/endpoint_resolver.py` belongs to `src-llm-core`, and `POST /api/model-endpoints`
  (`routes/model_routes.py:2011`) normalizes and stores whatever it is given; whether a missing
  scheme check is a defect there is that section's call, not this one. What this section can say is
  that no test in the slice would notice either way.
- **Impact:** a later change to the URL builders' validation has no test to fail on: tightening the
  guard (rejecting non-HTTP schemes, or link-local addresses) would pass the whole slice, and so
  would removing the query/fragment guard's callers if the guard itself stayed. The concrete gap this
  leaves is that `src/endpoint_resolver.py` accepts `file:///etc/passwd` and
  `http://169.254.169.254/latest/meta-data` as bases and rewrites them into plausible-looking chat
  URLs; whether that matters depends on which callers reach the builders, which is outside this
  section, but the coverage claim "the endpoint URL validation is tested" is not true today.
- **Fix:** add the rejection cases to the existing parametrized table in
  `tests/test_endpoint_resolver_urls.py` next to the query/fragment one, so the guard's scope is
  stated by a test whichever way the production decision goes.

### [BUG] The only bad-scheme input in this slice is decorative, because the fixture raises for every URL

- **Location:** `tests/test_llm_core_fallback.py:1432`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `test_nonstream_request_configuration_error_is_ineligible` passes `ftp://` as the
  candidate URL, but the stubbed transport raises `httpx.UnsupportedProtocol` before looking at it:

  ```python
  # tests/test_llm_core_fallback.py:1417-1424, :1430-1434
  async def fake_post(client, url, headers, **kwargs):
      calls.append(url)
      raise httpx.UnsupportedProtocol("unsupported protocol")
  ...
      [
          ("ftp://selected.example", "selected", {}),
          ("https://backup.example/v1", "backup", {}),
      ],
  ```

  Swapping the scheme for a valid one leaves the test passing unchanged, so the scheme plays no part
  in the outcome:

  ```
  $ diff <(grep -n 'selected.example' tests/test_llm_core_fallback.py) \
         <(grep -n 'selected.example' /tmp/jsprobe/test_ftp_swapped.py)
  11c11
  < 1432:                ("ftp://selected.example", "selected", {}),
  ---
  > 1432:                ("https://selected.example/v1", "selected", {}),
  $ venv/bin/python -m pytest -q /tmp/jsprobe/test_ftp_swapped.py -k configuration_error_is_ineligible
  1 passed, 76 deselected, 2 warnings in 0.12s
  ```

  The test does prove what its name says — that `httpx.UnsupportedProtocol` is classified as
  ineligible for fallback rather than as a retryable failure — and the classification is the
  production behaviour under test. The `ftp://` literal is only misleading: it reads as a scheme
  check that does not exist.
- **Impact:** a reader scanning this file for "does anything reject a bad scheme?" finds a test that
  looks like the answer and is not one. The cost is a wrong coverage claim rather than a missed
  regression.
- **Fix:** either drop the scheme from the literal (the URL is never parsed) or keep it and add the
  missing assertion elsewhere; do not leave it as the slice's only evidence about schemes.
