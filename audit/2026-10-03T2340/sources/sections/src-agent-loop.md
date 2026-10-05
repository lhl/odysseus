# src: agent loop, runs, approvals and gates

## Overview

This section covers the loop that turns a chat message into tool calls: intent routing and tool
retrieval, system-prompt assembly, the multi-round execution loop, the detached-run manager, the
background-activity gate, and the exact-action approval store. The tool implementations are in
`src-agent-tools`; the route that starts a run is in `routes-chat-session`. A finding here is about
a decision the loop makes, not about whether a tool implementation is correct.

## Coverage

**Read fully:** all eight files.

| File | Lines |
| --- | ---: |
| `src/agent_loop.py` | 6,456 |
| `src/tool_approvals.py` | 513 |
| `src/agent_runs.py` | 271 |
| `src/interactive_gate.py` | 219 |
| `src/action_intents.py` | 165 |
| `src/tool_approval_scopes.py` | 160 |
| `src/task_action_policy.py` | 47 |
| `src/goal_based_extractor.py` | 23 |

Every cited line was re-read at `2992bf6d368a`.

**Not read:** the tool dispatcher and tool implementations (`src/agent_tools/`, assigned to
`src-agent-tools`), the routes that build the initial message list and consume the loop's events
(`routes/chat_routes.py`, `routes/chat_helpers.py`, assigned to `routes-chat-session`),
`src/tool_capabilities.py` and `src/tool_policy.py` (assigned to `src-tools-capabilities-policy`), and
`src/teacher_escalation.py` (assigned to `src-research-scheduling`). Statements about how those
modules consume values built here rest on the call sites visible in this section.

One hypothesis was tested and rejected; it is recorded in `sources/coverage-boundaries.md`.

### [BUG] An ordinary "on <word>" phrase switches the turn to the workspace toolset

- **Location:** `src/agent_loop.py:1182`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** The third alternative in `_LOCAL_COMPUTER_REFERENCE_RE` matches `on` or `from`
  followed by any 2-32 character word outside a five-word blocklist:

  ```python
  r"|\b(?:on|from)\s+(?!this\b|my\b|the\b|a\b|an\b)(?:[a-z][a-z0-9_.-]{1,31})\b",
  ```

  `_looks_like_local_computer_request` (`:1205`) returns True on that match, and the
  tool-selection block treats it as one arm of a condition that replaces the whole retrieved set
  (`:3985` for the call, `:3990` for the assignment):

  ```python
  or _looks_like_local_computer_request(_retrieval_query or _last_user)
  ...
  _relevant_tools = set(_WORKSPACE_TERMINUS_TOOLS)
  ```

  Measured with the compiled expression:

  ```
  $ python3 -c "<regex from :1182, re.search>"
  True   add a meeting on Friday
  True   send an email to bob on Monday
  True   what is on Netflix tonight
  True   summarize the report from Alice
  True   schedule a dentist appointment on Tuesday at 3pm
  True   who is on call this weekend
  False  add milk on my todo list
  False  search for the weather in Berlin
  ```

  `_classify_agent_request` (`:1390`) routes "add a meeting on Friday" to `notes_calendar_tasks`,
  which seeds `manage_calendar` into `_relevant_tools` at `:3957-3958`; the replacement at `:3990`
  discards it. `_WORKSPACE_TERMINUS_TOOLS` (`:542`) is the `files` domain plus six named tools
  (`manage_skills`, `ask_teacher`, the two web tools, `ask_user` and `update_plan`). It has no
  email, calendar, notes, memory, contacts, documents or UI tools. `_assemble_prompt` (`:847`) builds the
  system prompt from that set and `_tool_schemas_for_route` (`:4486`) filters the schema list the
  same way, so the dropped tools are absent from both channels.

- **Impact:** A turn whose text contains "on X" or "from X" — a common English construction, not
  only a machine name — loses the domain tools it needs and is given the coding toolset instead.
  "add a meeting on Friday" and "send an email to Bob on Monday" are answered by an agent holding
  `bash` and `read_file` but no `manage_calendar` or `send_email`. The comment above the regex
  calls the third alternative a "named computer task request"; the match is wider than that.
- **Fix:** Match named machines against the configured Cookbook server names and SSH aliases
  rather than any bare word, or require an explicit machine marker ("on the machine", "host: X").
  Excluding weekday and month names closes the most common false positive but not the class.

### [BUG] The first-turn low-signal shortcut answers non-English action requests with no tools

- **Location:** `src/agent_loop.py:3544`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_classify_agent_request` is English-only apart from three Polish patterns. A
  German request is classified `low_signal` with no domains:

  ```
  $ venv/bin/python -c "<import src.agent_loop; _classify_agent_request>"
  'Recherchiere im Internet nach der aktuellen Temperatur in Berlin'
    {'low_signal': True, 'continuation': False, 'domains': set(), 'retrieval_query': '...'}
  ```

  `_direct_low_signal` (`:3544-3556`) is true for that turn: it is the first user turn, not a
  continuation, and no document, email, workspace, forced tool, or retrieved tool is present.
  `_is_casual_low_signal` is False, but the three `(_casual_low_signal_turn or not ...)` arms pass
  because each context is empty. The direct path then calls the model with only the latest user
  text and no tools (`:3597` for a non-Qwen model), caps the reply at 128 tokens (`:3696`), and
  returns before tool retrieval runs.

  The retrieval path it skips states the opposite intent (`:3885-3887`):

  ```python
  # Don't short-circuit: fall through to RAG retrieval below.
  # Non-English queries are flagged low_signal by the English-only
  # intent classifier, but fastembed retrieval works across languages.
  ```

  That branch is unreachable for a first-turn non-English message because the direct path has
  already returned. `tests/test_agent_loop.py:67` covers the Polish patterns; no test covers any
  other language.

- **Impact:** A first message in a language the classifier does not cover is answered from model
  memory with no web, calendar, email, or file tools, even when it names an action.
  "Recherchiere im Internet nach ..." gets a recalled answer instead of a `web_search`, and the
  128-token cap applies to the same call. The shortcut also drops the upload manifest that
  `stream_agent_loop` inserts at `:3521`; whether that loses attachment content depends on whether
  the route already inlined it into the user message, which is outside this section.
- **Fix:** Make `_direct_low_signal` require `_casual_low_signal_turn`, so only casual first turns
  skip retrieval, and let the other low-signal turns reach the RAG path the comment describes.

### [DEAD-CODE] The first `_AGENT_RULES` and `_API_AGENT_RULES` are shadowed by a second definition

- **Location:** `src/agent_loop.py:307`
- **Severity:** low
- **Disposition:** next
- **Evidence:** The three prompt constants are assigned twice at module level:

  ```
  $ grep -n '^_AGENT_PREAMBLE = \|^_AGENT_RULES = \|^_API_AGENT_RULES = ' src/agent_loop.py
  307:_AGENT_PREAMBLE = """\
  313:_AGENT_RULES = """\
  360:_API_AGENT_RULES = """\
  425:_AGENT_PREAMBLE = """\
  429:_AGENT_RULES = """\
  440:_API_AGENT_RULES = """\
  ```

  The second assignment wins at import. `_assemble_prompt` (`:847`) reads the module globals at
  call time, so lines 307-423 — 117 lines — never reach a prompt. The two revisions differ: the
  shadowed `_AGENT_RULES` is the long operational block, and the live `_AGENT_RULES` (`:429`) is
  the short "Base rules" text; the domain rules it drops are restated separately in
  `_DOMAIN_RULES` (`:467`) and `_LINK_RULES`.

- **Impact:** A maintainer editing the first copy changes nothing, and the file gives no signal
  that one of the two copies is inert. The two revisions have already drifted, so which rules ship
  cannot be read off the file without tracking the rebinding.
- **Fix:** Delete the first block, keeping any text still wanted by folding it into the live
  constants or `_DOMAIN_RULES`. A test asserting that a known rule string appears in
  `AGENT_SYSTEM_PROMPT` would catch a reintroduced shadow.

### [BUG] The Odysseus-Qwen artifact normalizer rewrites the word "star" to "start"

- **Location:** `src/agent_loop.py:1971`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_ODY_QWEN_TEXT_FIXES` (`:1948`) lists
  `(re.compile(r"\bstar\b", re.IGNORECASE), "start")` among repairs for dropped final letters.
  `_normalize_ody_qwen_text_artifacts` (`:1979`) applies every entry to each streamed delta
  (`:5212`), to deterministic tool summaries (`:6132`), and to the final response (`:6330`) when
  the model is an `odysseus-qwen3*` finetune. "star" is a complete English word:

  ```
  $ venv/bin/python -c "<import src.agent_loop; _normalize_ody_qwen_text_artifacts>"
  'The North Star is bright tonight.' -> 'The North start is bright tonight.'
  'a rising star' -> 'a rising start'
  'Star Wars' -> 'start Wars'
  ```

- **Impact:** Any response from that model containing "star" is altered before display, including
  quoted text and titles. The other entries in the list ("accoun", "documen", "reques", "migh")
  are not English words; "star" is the entry that corrupts valid prose. Scope is the shipped
  finetune models, not the general path.
- **Fix:** Remove the `star` entry. If the finetune really drops the final "t" from "start", key
  the repair on context that distinguishes the two words rather than on the standalone token.

### [PERF] The base-prompt cache never avoids the prompt build

- **Location:** `src/agent_loop.py:2258`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** On a cache hit, `_build_system_prompt` assigns the cached string and then calls
  `_build_base_prompt` anyway to obtain the skill-index block, discarding the freshly built
  prompt:

  ```python
  if _cached_base_prompt and _cached_base_prompt_key == cache_key and not active_document:
      agent_prompt = _cached_base_prompt
      # ... Skill index ... is NOT cached. Always recompute when the cache hits.
      _, _skill_index_block = _build_base_prompt(
          disabled_tools, mcp_mgr, needs_admin, relevant_tools,
          mcp_disabled_map=mcp_disabled_map, compact=compact, owner=owner,
          suppress_local_context=suppress_local_context,
          suppress_skills=suppress_skills,
      )
  else:
      agent_prompt, _skill_index_block = _build_base_prompt(...)
  ```

  The hit branch and the miss branch run the same call; the only difference is which of two
  strings built from the same inputs is assigned. `_cached_base_prompt` and
  `_cached_base_prompt_key` save no work, and the cache-key computation at `:2257` is overhead.

- **Impact:** Low. `_build_base_prompt`'s dominant cost, `SkillsManager.index_for`, must run on
  every request to build the skill index regardless, so the wasted work is the string assembly in
  `_assemble_prompt`. It is recorded because the cache reads as an optimization and is not one,
  which invites a wrong conclusion when prompt-assembly cost is profiled later.
- **Fix:** Split the skill-index build out of `_build_base_prompt` so a hit skips the assembly, or
  delete the cache and its key.

### [DEAD-CODE] Four helpers and one parameter are defined and never used

- **Location:** `src/agent_loop.py:100`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** Repo-wide references, excluding this run:

  ```
  $ for sym in _looks_like_notes_list_request _compact_tool_line _is_local_openai_compat_url \
  >            _code_write_intent; do grep -rn "$sym" --include='*.py' . | grep -v '^./audit/'; done
  src/agent_loop.py:100:def _looks_like_notes_list_request(text: str) -> bool:
  src/agent_loop.py:823:def _compact_tool_line(name: str, section: str) -> str:
  src/agent_loop.py:945:def _is_local_openai_compat_url(endpoint_url: str) -> bool:
  src/agent_loop.py:1427:    _code_write_intent = has(
  ```

  `_looks_like_notes_list_request` (10 lines) and `_compact_tool_line` (20 lines) have no call
  sites. `_is_local_openai_compat_url` has none; its sibling `_is_ollama_openai_compat_url`
  (`:930`) is called at `:1058`. `_code_write_intent` is assigned inside `_classify_agent_request`
  and never read. `_build_base_prompt` (`:2850`) takes `mcp_disabled_map` and never references it;
  the map is consumed in `_build_system_prompt` at `:2288` and `:2749`.

- **Impact:** Low. Each is a place a maintainer can read or extend with no effect.
  `_is_local_openai_compat_url` restates the local-endpoint policy that the live classifier
  implements differently at `:1027`, so the two can be mistaken for one.
- **Fix:** Delete the unused functions and the assignment, and drop the `mcp_disabled_map`
  parameter from `_build_base_prompt`.

### [BUG] A native model's auto-created document result never reaches the model

- **Location:** `src/agent_loop.py:5414`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** When a round contains a large code block and no document tool call, the fallback
  appends a synthetic `create_document` block to `tool_blocks` (`:5414`), after
  `_resolve_tool_blocks` (`:2944`) has produced `converted_calls` aligned 1:1 with the block list.
  Execution then yields one more result than there are converted calls. `_append_tool_results`
  (`:2995`), called at `:6290`, iterates the converted calls and indexes the result lists by the
  same position:

  ```python
  for j, tc in enumerate(native_tool_calls):
      result_text = tool_result_texts[j] if j < len(tool_result_texts) else ""
  ```

  The auto-created block's result sits at the last index, outside that range, and is dropped. The
  fenced path includes it, because that branch joins the full `tool_results` list into one text
  message.

- **Impact:** Low. A native-function-calling model that emits a non-document tool call and a large
  code block in the same round gets a document created in the editor without any tool result in
  its next context, so it can answer as if the code existed only in chat. If it repeats the code,
  the fallback can create a second document; whether models do that was not measured.
- **Fix:** Give the synthetic block the same treatment as the converted calls — synthesize a
  matching assistant tool call so the result has an id — or, in native mode, emit its result as a
  separate context message instead of dropping it.
