# src: tool parsing and execution

## Overview

`src/tool_parsing.py` (1,525 lines) turns raw model text into executable `ToolBlock`s — fenced
blocks, `[TOOL_CALL]`, `<invoke>`/`<tool_call>`/DSML/StepFun/Gemma/`<tool_code>` markup, raw
OpenAI tool-call JSON — and provides the mirror `strip_tool_blocks` used for display and
persistence. `src/tool_execution.py` (1,417 lines) is the dispatcher: per-turn workspace
binding, the path-confinement helpers (`_resolve_tool_path`, `_resolve_search_root`,
`agent_cwd`, `vet_workspace`), the MCP-vs-native routing for each tool name, the
capability/admin/policy gates, and `format_tool_result`. The capability and policy tables
themselves (`src/tool_capabilities.py`, `src/tool_policy.py`, `src/tool_security.py`) are
assigned to `src-tools-capabilities-policy`; the individual tool handlers
(`src/agent_tools/*`) to `src-agent-tools`; the loop that calls the dispatcher to
`src-agent-loop`.

## Coverage

**Read fully:** `src/tool_parsing.py` (1,525 lines), `src/tool_execution.py` (1,417 lines).
Every cited line was re-read at `2992bf6d368a`.

**Read partially:** `src/builtin_mcp.py` (the `_BUILTIN_SERVERS` table and its comment);
`src/mcp_manager.py` at `call_tool` (`:467-508`); `src/agent_tools/subprocess_tools.py` at
`BashTool.execute` (`:298-357`) and the tmux helpers (`:41-176`); `src/agent_loop.py` at
`_resolve_tool_blocks` (`:2944-2990`), the two `execute_tool_block` call sites (`:4559`,
`:5793`), the `strip_tool_blocks` call sites (`:5007`, `:5425`), and the try/except structure
of `stream_agent_loop`; `routes/chat_routes.py` at `_resolve_request_workspace` (`:348-372`)
and the stream's only handler (`:2551`); `tests/test_redos_llm_parsers.py` (201 lines);
`tests/test_agent_bash_windows.py` at the tmux cases (`:55-100`); `src/preset_manager.py` and
`static/js/presets.js` only for the `max_tokens: 0` presets.

**Not read:** `src/tool_capabilities.py`, `src/tool_policy.py`, `src/tool_security.py`,
`src/tool_approvals.py`, `src/tool_schemas.py`, `src/tool_utils.py` (other sections); the
`src/agent_tools/*` handlers beyond the `ctx` reads cited here; the MCP servers under
`mcp_servers/`; `src/ai_interaction.py`; `src/tool_implementations.py`. No test suite was run.

## Findings

### [ERROR-HANDLING] An uncaught `RecursionError` from `raw_decode` aborts the chat stream

- **Location:** `src/tool_parsing.py:755`
- **Severity:** low
- **Disposition:** next
- **Evidence:** Both raw-OpenAI scanners try to decode from every `[` or `{` in the response
  and catch only `json.JSONDecodeError`:

  ```python
  for match in re.finditer(r"[\[{]", text):
      try:
          parsed, _end = decoder.raw_decode(text[match.start():])
      except json.JSONDecodeError:
          continue
  ```

  `_strip_raw_openai_tool_call_json` has the same shape at `:783-785`. CPython's JSON scanner
  raises `RecursionError`, not `JSONDecodeError`, when array nesting exceeds the recursion
  limit. Measured with the project's `venv/bin/python`:

  ```
  parse_tool_blocks('"function"' + '['*9000)   OK              0.763s
  parse_tool_blocks('"function"' + '['*10000)  RecursionError   0.001s
  strip_tool_blocks('"function"' + '['*12000)  RecursionError
  ```

  Both entry points run on every response: `_parse_raw_openai_tool_call_json` is Pattern 4d of
  `parse_tool_blocks` (`:1462`), and `_strip_raw_openai_tool_call_json` runs unconditionally in
  `strip_tool_blocks` (`:1513`). Neither `_resolve_tool_blocks` (`src/agent_loop.py:2944`) nor
  the body of `stream_agent_loop` wraps those calls in a `try`, and the only handler around the
  stream is `except (asyncio.CancelledError, GeneratorExit)` (`routes/chat_routes.py:2551`), so
  the exception propagates out of the SSE generator.
- **Impact:** A model response (or prompt-injected text the model echoes) containing the literal
  `"function"` followed by ~10,000 nested `[` kills the turn: the client sees a truncated stream
  with no error event, and no assistant message is persisted. At 9,000 brackets the same scan is
  quadratic and already takes 0.76s.
- **Fix:** Catch `RecursionError` alongside `json.JSONDecodeError` in both scanners, or reject a
  candidate whose bracket nesting exceeds a small bound before decoding. The repo's ReDoS suite
  (`tests/test_redos_llm_parsers.py`) is the place for the regression case.
- **Re-review (2026-10-04):** lowered from medium. The input is a model response carrying about 10,000 nested brackets after
  the literal `"function"`, and the damage is that one turn. No request from another user is
  affected.


### [BUG] The MCP fallback drops `session_id`, so the per-session tmux shell never runs

- **Location:** `src/tool_execution.py:696`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_MCP_TOOL_MAP` still routes bash through the MCP manager (`:564`), but
  `src/builtin_mcp.py:63-67` records that the bash/python/filesystem/web_search servers were
  folded into native execution, and `_BUILTIN_SERVERS` (`:72-77`) registers only
  image_gen/memory/rag/email. Every bash call therefore takes the fallback at `:1116` /
  `:696`, and `_call_mcp_tool` has no `session_id` to forward:

  ```python
  async def _call_mcp_tool(
      tool: str,
      content: str,
      progress_cb: Optional[Callable[[Dict], Awaitable[None]]] = None,
  ) -> Dict:
      ...
      if not mcp:
          return await _direct_fallback(tool, content, progress_cb=progress_cb) or ...
      ...
      fallback = await _direct_fallback(tool, content, progress_cb=progress_cb)
  ```

  `_direct_fallback` builds `ctx["session_id"]` from its own default `None`, and
  `BashTool.execute` gates the tmux persistence path on that value:

  ```python
  session_id = ctx.get("session_id")
  ...
  if session_id and not IS_WINDOWS and shutil.which("tmux"):
      stdout, stderr, rc, timed_out = await _run_tmux_bash(...)
  ```

  Measured with a stub MCP manager returning the not-connected result (`src/mcp_manager.py:481`),
  tmux installed at `/usr/bin/tmux`, and `_run_tmux_bash` patched to record invocation:

  ```
  execute_tool_block(ToolBlock("bash", "echo hello"), session_id="sess-1", owner="admin")
  desc: bash: echo hello
  result keys: ['exit_code', 'output']
  calls: [('mcp', 'mcp__bash__bash')]
  tmux used: False
  ```

- **Impact:** Every foreground bash call spawns a fresh `create_subprocess_exec`; `cd`, exported
  variables, and activated venvs do not survive to the next call in the same chat, the
  timeout path that sends Ctrl-C to a live tmux session is unreachable, and the
  `tmux_session` field the tool returns is never populated. The whole persistence feature is
  dead on a default deployment, including on the `get_mcp_manager() is None` branch, which
  drops `session_id` the same way.
- **Fix:** Add `session_id`/`owner` parameters to `_call_mcp_tool` (`:679`) and forward them in
  both `_direct_fallback` calls; pass them at the dispatch site (`:1116`).

### [PERF] `_strip_bare_invoke_markup` re-lowercases the whole response on every iteration

- **Location:** `src/tool_parsing.py:1020`
- **Severity:** low
- **Disposition:** next
- **Evidence:** The scan calls `text.lower()` inside the loop, so each `<invoke>` block found
  copies and lowercases the entire remaining string — twice:

  ```python
  while True:
      start = text.lower().find("<invoke", pos)
      ...
      close = text.lower().find("</invoke>", tag_end + 1)
  ```

  The function is called unconditionally at the end of `strip_tool_blocks` (`:1523`), which
  runs on every round response. Measured on closed blocks, so every iteration pays both
  lowercases:

  ```
  '<invoke name="x"></invoke>' *  5000   130,000 chars    0.269s
  '<invoke name="x"></invoke>' * 10000   260,000 chars    1.071s
  '<invoke name="x"></invoke>' * 20000   520,000 chars    4.274s
  '<invoke name="x"></invoke>' * 40000 1,040,000 chars   17.315s
  ```

  Clean quadratic (4x per doubling). Response length is not bounded by default: a preset with
  `max_tokens: 0` sends the endpoint its own default (`src/preset_manager.py:59`), and
  `static/js/presets.js:470` maps any value above 8192 to 0, so a looping local model can
  emit megabytes.
- **Impact:** A response that repeats a closed `<invoke ...></invoke>` pair — a plausible
  local-model repetition loop — stalls the agent loop for 4s at 520 KB and 17s at 1 MB, on
  every round and on the model-failure path. The sibling scanners in this file were converted
  to forward-only iteration precisely to avoid this class (see `_iter_delimited`'s docstring
  at `:1178`).
- **Fix:** Hoist `lowered = text.lower()` before the loop (one pass instead of one per block),
  or drive the scan through `_iter_delimited`/`_strip_delimited` with a bare-`<invoke` opener
  carrying `re.IGNORECASE`.
- **Re-review (2026-10-04):** lowered from medium. The timings quoted are for a single model response of
  1 MB. That is beyond what one generation produces under an ordinary output-token limit, and the
  cost at the sizes a turn does produce is a fraction of a second because the scan is quadratic.
  The defect is real and the fix is the one stated; the reachability is what makes it low.


### [PERF] The Gemma tool-call pattern is the remaining quadratic delimiter scan

- **Location:** `src/tool_parsing.py:170`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_GEMMA_TOOL_CALL_RE` is a lazy delimiter pattern that is still applied with
  `finditer`/`sub`, unlike every sibling pattern, which was split and moved to the
  forward-only `_iter_delimited`/`_strip_delimited`:

  ```python
  _GEMMA_TOOL_CALL_RE = re.compile(
      r"<\|?tool_call\|?>\s*call:([\w\d_-]+)\s*(\{[\s\S]*?\})\s*<\|?tool_call\|?>",
      re.IGNORECASE,
  )
  ```

  Used at `:1443` (`parse_tool_blocks`) and `:1511` (`strip_tool_blocks`). With an opener
  flood and no closing token, the engine rescans to end-of-string from every opener. Measured:

  ```
  parse_tool_blocks("<|tool_call|>call:x{" *  2000)    40,000 chars    0.234s
  parse_tool_blocks("<|tool_call|>call:x{" *  5000)   100,000 chars    1.464s
  parse_tool_blocks("<|tool_call|>call:x{" * 10000)   200,000 chars    5.872s
  parse_tool_blocks("<|tool_call|>call:x{" * 20000)   400,000 chars   23.589s
  strip_tool_blocks("<|tool_call|>call:x{" * 10000)   200,000 chars    5.886s
  ```

- **Impact:** A local model stuck in a repetition loop (or injected output) that emits the
  Gemma opener without the closing token stalls the round for 5.9s at 200 KB and 23.6s at
  400 KB, in both the parse and the display/persistence path. The same input is the one the
  repo's `tests/test_redos_llm_parsers.py` budget of 4s is meant to catch, but that suite does
  not cover this pattern.
- **Fix:** Split the pattern into open/close delimiters and use `_iter_delimited` for parse and
  `_strip_delimited` for strip, as `[TOOL_CALL]`, `<tool_call>`, `<tool_code>`, and
  `<function_model>` already do.
- **Re-review (2026-10-04):** lowered from medium. The timings quoted are for a single model response of
  200-400 KB. That is beyond what one generation produces under an ordinary output-token limit, and the
  cost at the sizes a turn does produce is a fraction of a second because the scan is quadratic.
  The defect is real and the fix is the one stated; the reachability is what makes it low.


### [PERF] `_parse_raw_web_json_lookup` re-decodes every brace in each mention's window

- **Location:** `src/tool_parsing.py:591`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** For every `web_search` mention, the function scans a 1200-char window for `{`
  and calls `raw_decode` on the whole remaining response for each one:

  ```python
  for mention in _RAW_WEB_JSON_TOOL_RE.finditer(text):
      search_start = mention.end()
      search_end = min(len(text), search_start + 1200)
      for brace in re.finditer(r"\{", text[search_start:search_end]):
          start = search_start + brace.start()
          try:
              parsed, end = decoder.raw_decode(text[start:])
          except json.JSONDecodeError:
              continue
  ```

  Dense text makes the windows overlap: each mention retries the braces the previous mention
  already rejected. Measured on `"web_search {" * n`, and profiled at n=20,000:

  ```
  parse_tool_blocks("web_search {" *  5000)    60,000 chars    0.671s
  parse_tool_blocks("web_search {" * 10000)   120,000 chars    1.634s
  parse_tool_blocks("web_search {" * 20000)   240,000 chars    4.151s
  strip_tool_blocks("web_search {" * 20000)   240,000 chars    4.124s

  $ cProfile, n=20000: 1,995,050 raw_decode calls (~8 per input character), each
  failure constructing a JSONDecodeError.
  ```

  Reached through Pattern 6 (`:1468`) and the strip path (`:1517`), both gated on
  `not skip_fenced`, so it applies to fenced/local models.
- **Impact:** A response with many `web_search` mentions followed by braces — an odd but
  cheap-to-generate repetition — costs ~4s at 240 KB, with growth steeper than linear
  (0.67s → 1.63s → 4.15s per doubling) and both parse and strip paying it. The default
  `max_tokens` caps this in practice; an unbounded preset does not.
- **Fix:** Try only the first brace per mention, or cap the attempts and skip past a brace
  that failed, and check that the byte after `{` is `"` or `}` before calling `raw_decode`.
