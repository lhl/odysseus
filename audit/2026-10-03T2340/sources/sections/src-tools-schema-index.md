# src: tool schemas, index and implementations

## Overview

The three sources that decide which tools a model is told about, and how a native function
call becomes a tool invocation. `src/tool_schemas.py` (1,601 lines) holds
`FUNCTION_TOOL_SCHEMAS` — the 71 OpenAI-style function definitions sent to native
function-calling endpoints — and `function_call_to_tool_block`, the converter that turns a
native call's JSON arguments back into the text `ToolBlock` the execution pipeline consumes.
`src/tool_index.py` (629) holds `BUILTIN_TOOL_DESCRIPTIONS` (the RAG corpus), the `ToolIndex`
that embeds it so agent mode can retrieve the top-K tools per message, and the deterministic
keyword hints that force-include a toolset when retrieval is unavailable or thin.
`src/tool_implementations.py` (115) is a facade re-exporting the `do_*` handlers from
`src/tools/*` and `src/agent_tools/*`, and owns the active-email globals.

The boundary with a neighbouring section: `src-tools-parse-exec` owns the parsers
(`src/tool_parsing.py`) and the dispatcher (`src/tool_execution.py`) that consume this
module's `ToolBlock` output; `src-agent-tools` owns the `do_*` handler bodies;
`src-agent-loop` owns the loop that calls `function_call_to_tool_block`, assembles the prompt
from `TOOL_SECTIONS`, and filters the schema list it sends. The `TOOL_TAGS` set is defined in
`src/agent_tools/__init__.py`, but it is the fence-callable set this module's converter
checks against, so it is reviewed here; its other consumers (the plan-mode denylist, the
capability tables) belong to `src-tools-capabilities-policy`.

## Coverage

**Read fully:** `src/tool_schemas.py` (1,601 lines — every schema and the whole converter),
`src/tool_index.py` (629), `src/tool_implementations.py` (115);
`tests/test_tool_index_schema_parity.py` (56), `tests/test_research_report_read.py` (66),
`tests/test_tool_rag_keyword_hints.py` (65), `tests/test_tool_implementations_shim.py` (165).

**Read partially:** `src/agent_loop.py` at `_resolve_tool_blocks` (`:2944-2992`),
`_assemble_prompt` (`:848-865`), the domain/keyword tables (`:528-556`),
`_classify_agent_request` (`:1390-1489`), the `manage_session`/`manage_documents`/
`manage_research` prompt sections (`:693-702`), the native call site and per-block loop
(`:5631-5832`), the empty-tool-blocks exit (`:5433`), and the fenced gate (`:2983`);
`src/tool_execution.py` at `_split_bg_marker` (`:737-747`), the bash call (`:1087`),
`_MCP_ARG_PARSERS` (`:627-637`), and the `tail_serve_output` dispatch (`:1205-1207`);
`src/agent_tools/__init__.py` at the `TOOL_TAGS` set (`:79-114`);
`src/agent_tools/document_tools.py` (`:799-890`), `session_tools.py` (`:302-350`),
`web_tools.py` (`:8-30`), `filesystem_tools.py` (`:243-256`);
`src/tool_security.py` at `_PLAN_MODE_KNOWN_MUTATORS` (`:130-166`); `src/agent_runs.py` at
`_drain` (`:115-173`); `routes/chat_routes.py` at the active-email block (`:1091-1140`);
`src/tools/system.py`, `src/tools/calendar.py`, `src/tools/notes.py` and
`src/ai_interaction.py` at their action dispatch, to compare each multiplexed tool's enum
with its handler.

**Not read:** the `do_*` handler bodies beyond their action dispatch (assigned to
`src-agent-tools`); `src/tool_execution.py` beyond the call sites named;
`src/tool_parsing.py` (assigned to `src-tools-parse-exec`); `static/js/*` (the UI side of the
tool toggles and pickers); the embedding/ChromaDB lanes behind `ToolIndex`.

**Checks run:** a three-way set diff of the schema names, `TOOL_TAGS` and
`BUILTIN_TOOL_DESCRIPTIONS` keys (findings 2 and 3); `function_call_to_tool_block` driven
with seven malformed-but-plausible argument objects, each resulting block fed to its first
consumer (finding 1); a `ToolIndex` with retrieval stubbed to exercise the keyword hints for
four report-reading queries (finding 3); each multiplexed tool's enum compared with its
handler's `action ==` branches (finding 4). `venv/bin/python -m pytest -q` on the three test
files listed as read fully: `10 passed`.

## Findings

### [ERROR-HANDLING] A non-string argument from a native call crashes the turn instead of returning a tool error

- **Location:** `src/tool_schemas.py:1416-1419`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** For every tool whose content is built from a single argument, the converter
  copies the model's value through without a type check:

  ```python
  if tool_type == "bash":
      content = args.get("command", "")
  elif tool_type == "python":
      content = args.get("code", "")
  ...
  elif tool_type == "read_file":
      ...
      content = args.get("path", "")
  ```

  The empty-argument guard above it (`:1399-1402`) coerces with `str(...)`, so a dict counts
  as a non-empty value and passes:

  ```python
  required_args = _REQUIRED_NATIVE_TOOL_ARGS.get(tool_type)
  if required_args and not any(str(args.get(key) or "").strip() for key in required_args):
  ```

  `_REQUIRED_NATIVE_TOOL_ARGS` (`:22-29`) lists `web_search`, `web_fetch`, `read_file`,
  `write_file`, `edit_file`, `apply_patch` — not `bash`, `python` or `create_document`. The
  converters that wrap the value in `json.dumps` (`grep`, `edit_file`, `todowrite`, `ls`,
  `glob`) are safe; the concatenating ones are not. Measured with the project's
  `venv/bin/python`, converter output and then the first consumer of that output:

  ```
  bash             -> content type 'dict' value {'command': 'echo hi'}
  python           -> content type 'list' value ['print(1)']
  read_file        -> content type 'dict' value {'p': '/etc/hostname'}
  create_document  -> CONVERTER RAISED TypeError: sequence item 0: expected str instance, dict found
  web_search       -> content type 'dict' value {'q': 'weather'}
  write_file       -> content type 'str'  value '{"path": "/tmp/x", "content": {"body": "hi"}}'
  grep             -> content type 'str'  value '{"pattern": 3}'

  _split_bg_marker({"command": "echo hi"})      -> AttributeError 'dict' object has no attribute 'split'
  WebSearchTool().execute({'q': 'weather'}, {}) -> AttributeError 'dict' object has no attribute 'strip'
  ```

  The consumers are `content.split("\n")` in `_split_bg_marker` (`src/tool_execution.py:740`,
  reached for any bash call with a `session_id` at `:1087`), `content.strip()` in
  `WebSearchTool.execute` (`src/agent_tools/web_tools.py:12`), and
  `content.split("\n", 1)[0]` in `ReadFileTool.execute`
  (`src/agent_tools/filesystem_tools.py:246`). `create_document` raises inside the converter
  itself (`src/tool_schemas.py:1459-1463`). `web_search` and `read_file` are not admin-only,
  so the dispatcher crashes are reachable for a normal user. Nothing catches the exception:
  `function_call_to_tool_block` is called at `src/agent_loop.py:2959`, the per-block loop has
  no handler, and an AST query for the `try` statements enclosing `desc, result = await
  _tool_task` (`:5819`) reports only one — the `try/finally` at `5808-5832`, with no
  `except`. For a normal chat the exception reaches `src/agent_runs.py:157`, which publishes
  a generic `event: error` ("Agent run failed before completion.") and marks the run
  `error`; compare panes stream without that wrapper and lose the connection.
- **Impact:** A model that emits a structured value where the schema says string — the class
  of output the non-object-arguments coercion at `src/tool_schemas.py:1392-1397` already
  defends against — kills the whole turn with a generic 500-class error instead of returning
  a tool result the model could correct on the next round. The user's message is saved and
  the assistant turn is not; a tool that was mid-work in the same round is abandoned.
  `bash` and `read_file` need an admin owner, `web_search` and `create_document` do not.
- **Fix:** Coerce at the converter boundary: `content = str(args.get("command") or "")` for
  each concatenating branch (and `json.dumps` for the object-valued cases), or reject a
  non-string value for a required string argument in the `_REQUIRED_NATIVE_TOOL_ARGS` guard
  and return `None` so the loop logs "FAILED to convert" and the model sees a normal error
  result. A regression test that feeds each schema's required string argument a dict and
  asserts no exception belongs next to `tests/test_function_call_non_object_args.py`.

### [BUG] `tail_serve_output` is advertised to native models but missing from `TOOL_TAGS`, so every native call is rejected

- **Location:** `src/agent_tools/__init__.py:103-108`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** The `TOOL_TAGS` comment above the cookbook block states the contract and the
  exact failure mode:

  ```
  # Cookbook tools (LLM serving + downloads). Without these
  # entries, native function calls to e.g. list_served_models
  # are rejected as "Unknown function call" before reaching
  # the dispatcher — silent failure for the whole cookbook
  # surface.
  "download_model", "serve_model",
  "list_served_models", "stop_served_model",
  ...
  ```

  `tail_serve_output` is the one cookbook tool absent from the set. It has a schema
  (`src/tool_schemas.py:899`), an index description (`src/tool_index.py:130`), a prompt
  section telling the model to call it after a failed serve (`src/agent_loop.py:763`, plus
  the recovery hint at `:5506`), and a dispatcher branch (`src/tool_execution.py:1205`).
  Measured set diff at the snapshot:

  ```
  counts: schemas=71 tags=77 descs=73
  schemas - tags  : ['tail_serve_output']
  descs - tags    : ['tail_serve_output']
  ```

  It is reachable: the `cookbook` domain fires on `serve|launch|start|...`
  (`src/agent_loop.py:1417`) and seeds `_DOMAIN_TOOL_MAP["cookbook"]` (`:532`), which
  contains `tail_serve_output`, so for "why did the vllm serve crash on startup?" the
  schema is sent (measured: `domains=['cookbook'] tail_serve_output seeded=True`). The
  converter then rejects the call at `src/tool_schemas.py:1411` — `if tool_type not in
  TOOL_TAGS: logger.warning(f"Unknown function call: {name}")` — and `_resolve_tool_blocks`
  logs `FAILED to convert native call`. With no tool block produced, the turn takes the
  `if not tool_blocks:` exit at `src/agent_loop.py:5433` and accepts the model's prose as
  the final answer.
- **Impact:** The documented debug loop — `serve_model` → `list_served_models` reports
  `crashed` → `tail_serve_output` → retry with adjusted flags — cannot complete on any
  native function-calling endpoint (GPT/Claude/Qwen3/DeepSeek-V class). The model's log
  read is silently dropped, the turn ends as if it had answered, and the user gets a
  diagnosis the model made up rather than the traceback. The other 12 cookbook tools were
  added to this set precisely to prevent that; this one was missed. `schemas - tags` and
  `descs - tags` are both exactly this name, so the gap is a single missing string.
- **Fix:** Add `"tail_serve_output"` to the cookbook group in `TOOL_TAGS`. The existing
  parity test only pins one edge of the triangle (`tests/test_tool_index_schema_parity.py`
  asserts `schemas ⊆ descriptions`); extend it to assert `schemas ⊆ TOOL_TAGS` so a new
  schema cannot ship without a fence tag.

### [BUG] `manage_research` has no native schema, so the report-read path the prompt and RAG steer to is unreachable for native models

- **Location:** `src/agent_loop.py:702`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** The prompt section tells every model that reading a finished deep-research
  report means calling this tool, including how to resolve the id and what not to do
  instead:

  > This IS how you read a finished report: when the user refers to a just-completed
  > deep-research job ("check it out", "read that report", "summarize the research") WITHOUT
  > giving an id, call `manage_research` with `action:list` to get the most-recent id, then
  > `action:read` with that id, and answer from the returned text. Do NOT `web_fetch`/
  > `app_api` the `/api/research/report/{id}` URL.

  `manage_research` is in `TOOL_TAGS` (`src/agent_tools/__init__.py:110`), in
  `BUILTIN_TOOL_DESCRIPTIONS` (`src/tool_index.py:102`), and in the RAG hint that fires for
  exactly these queries (`src/tool_index.py:445`: `{"manage_research", "trigger_research"}`
  for "my research", "the report", "saved research", …) — but it has no entry in
  `FUNCTION_TOOL_SCHEMAS` (measured: the only research-named schema is `trigger_research`).
  For a native model the tool is therefore advertised and unreachable at the same time.
  Measured with retrieval stubbed:

  ```
  query='summarize the research on fusion'
    relevant_tools: [ask_user, manage_memory, manage_research, trigger_research, ui_control, update_plan]
    schemas sent   : ask_user, manage_memory, trigger_research, ui_control, update_plan
    manage_research in relevant_tools: True
    manage_research in sent schemas  : False
    compact prompt line: ['- `manage_research`']
  ```

  The compact prompt used for native models (`_assemble_prompt(..., compact=True)`,
  `src/agent_loop.py:852-865`) lists the tool by name and says "Only the tool schemas
  provided by the API are available for this turn", so the model is told a tool exists that
  the API never declared. The fenced channel is closed too: for an API model
  `parse_tool_blocks` runs with `skip_fenced=True` (`src/agent_loop.py:2983`, gated on
  `is_api_model and not allow_fenced_for_api`), and a probe with a
  ```manage_research fence returns no block for `is_api_model=True` while the same input
  returns a block for a local model. `tests/test_research_report_read.py` pins the handler
  and the instruction text, not reachability, so the regression it guards (issue #1363 —
  the agent web-fetching the HTML report) can still reproduce on native endpoints. The
  handler's separate owner-scoping defect (it ignores `owner`) is recorded in
  `src-agent-tools.md`; this finding is only about reaching the tool at all.
- **Impact:** For every native function-calling endpoint the advertised way to read a saved
  report does not exist. The model either answers from nothing, or falls back to the two
  things the prompt forbids — `app_api`/`web_fetch` on the HTML render, or a fresh
  `trigger_research` — which is the behaviour #1363 was fixed for on the textual path. The
  `trigger_research` schema *is* sent on the same turn, so the cheapest available action is
  the wrong one.
- **Fix:** Add a `manage_research` schema (action enum `list|read|delete`, `id`, `search`)
  next to `trigger_research` in `FUNCTION_TOOL_SCHEMAS`; the handler already accepts the JSON
  form the other multiplexed tools use. If fence-only is deliberate, say so in the prompt
  section and stop steering native models to it, and extend the parity test to assert that
  every tool named in `TOOL_SECTIONS` is either schema-backed or in a documented
  fence-only list.

### [BUG] Two native schema enums omit actions their handler and prompt support

- **Location:** `src/tool_schemas.py:813`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `manage_documents` advertises three actions and a `document_id` described
  only as "for delete":

  ```python
  "description": "Manage documents: list all documents ..., delete documents, or run tidy cleanup.",
  "action": {"type": "string", "enum": ["list", "delete", "tidy"]},
  "document_id": {"type": "string", "description": "Document ID (for delete)"},
  ```

  The handler accepts the read family (`src/agent_tools/document_tools.py:828`:
  `elif action in ("read", "view", "open", "get")`), and the prompt section for the same
  tool tells the model `{"action": "list|read|delete|tidy"}` and "`read` (aliases:
  view/open/get) takes `document_id` and returns the content" (`src/agent_loop.py:701`).
  `manage_session` has the same gap in the other direction: its enum (`:426`) is
  `["rename", "archive", "unarchive", "delete", "important", "unimportant", "truncate",
  "fork"]` and `required: ["action", "session_id"]` (`:430`), while the handler also
  implements `list` (`src/agent_tools/session_tools.py:302`) and
  `switch/open/select/view` (`:325`), and its prompt section lists them
  (`src/agent_loop.py:693`). No code validates arguments against these enums (a search for
  `["enum"]`/`jsonschema` in `src/`, `routes/`, `core/`, `services/` finds no reader), so a
  model that ignores the enum still works; the other nine multiplexed tools
  (`manage_notes`, `manage_memory`, `manage_tasks`, `manage_calendar`, `manage_contact`,
  `manage_skills`, `manage_research`, `ui_control`, `edit_image`) match their handlers
  exactly.
- **Impact:** A model that honours the function definition's enum cannot read a document or
  list/switch chats through these tools: the only available actions are destructive or
  administrative, and the "open/show/read my document" flow degrades to a list of clickable
  rows. For `manage_session` the `switch` flow has no alternative tool, so "open my X chat"
  is unavailable to a strict model. The enum and the prompt disagree, which is also the kind
  of contradiction that makes a model emit a call outside the declared contract.
- **Fix:** Add the supported actions to both enums and to their descriptions
  (`["list", "read", "delete", "tidy"]`; `["list", "switch", "rename", ...]`), make
  `session_id` required only for the actions that need it (or keep it and document
  `"current"`), and add a test that asserts each multiplexed tool's enum equals the set of
  actions its handler dispatches on.

### [DEAD-CODE] Three `ToolIndex` members are assigned and never read

- **Location:** `src/tool_index.py:153`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `self._embedder` is assigned the embedding client (`:153`) and never read;
  `self._fingerprint` is initialised (`:159`) and recomputed (`:219`) and never read; the
  `_embed` method (`:168-174`) has no caller. A search for `self._embed(`, `self._embedder`
  and `self._fingerprint` over the file returns only the definition sites, and the repo-wide
  search over `src/`, `routes/`, `services/`, `tests/` finds no external reader. Retrieval
  goes through the lanes (`self._lanes[...]`), which own their clients.
- **Impact:** The fingerprint is a SHA-256 over the sorted tool names
  (`",".join(sorted(BUILTIN_TOOL_DESCRIPTIONS.keys()))`), computed and stored after each
  builtin reindex, but nothing reads it, so the apparent "did the corpus change" guard is not
  one. The MCP path keeps its own live guard in `self._mcp_generation` (`:230-231`), which
  makes the unused attribute look like the intended builtin counterpart. The unused method and
  attribute also make the class look like it has a second embedding path.
- **Fix:** Delete `_embed`, `_embedder` and `_fingerprint`, or wire the fingerprint into a
  rebuild decision the way `_mcp_generation` guards `index_mcp_tools`, with a test asserting a
  reindex is skipped when the tool-name set is unchanged.

### [DEAD-CODE] The active-email global is written on every chat submit and never read

- **Location:** `src/tool_implementations.py:90-115`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `set_active_email` / `clear_active_email` / `get_active_email` manage a
  module global whose comment states the purpose — "Email tools can resolve 'this email'
  without guessing a UID" (`:87-89`). The frontend sends the open email on each submit
  (`static/js/chat.js:1867-1873`), the route calls `set_active_email(...)` /
  `clear_active_email()` around the turn (`routes/chat_routes.py:1099`, `:1131`), and
  `get_active_email` has no caller anywhere in the repository. The feature itself works
  through an explicit parameter: the route builds `active_email_ctx` from the form fields
  (`routes/chat_routes.py:1104-1126`), passes it to `stream_agent_loop(active_email=...)`,
  and the prompt injection reads the parameter (`src/agent_loop.py:2472-2478`).
  `tests/test_tool_implementations_shim.py:49-51` records that `get_active_email` has no
  in-repo importer and keeps the symbol for facade compatibility.
- **Impact:** Nothing breaks today, but the documented resolution mechanism does nothing,
  and the only reader that could be added is process-global state that the last chat submit
  overwrote — reviving `get_active_email()` inside an email handler would resolve "this
  email" from another user's turn. The per-request set/clear pair is otherwise dead weight
  on the chat path.
- **Fix:** Delete the global and the two `set_`/`clear_` calls from `routes/chat_routes.py`,
  keeping `get_active_email` (and the shim's `_EXPECTED` entry) only if the facade contract
  requires it; if the global is meant to be the source of truth, have the loop read it and
  key it by owner and session.
