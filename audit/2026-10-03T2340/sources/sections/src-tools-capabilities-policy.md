# src: tool capabilities, policy and MCP builtins

## Overview

The tables and helpers every tool call is gated by, plus the built-in MCP registration:

| File | Lines | Role |
| --- | ---: | --- |
| `src/tool_capabilities.py` | 708 | Classifies each tool's effects and result integrity; holds the run-local `ToolRunSecurityContext` that blocks high-impact tools once untrusted context has entered the run |
| `src/tool_security.py` | 284 | The non-admin blocklist, the plan-mode allowlist and its mutator backstop, and the owner-admin check |
| `src/tool_policy.py` | 242 | Composes the per-turn policy: the caller's disabled set, the guide-only detector, the web toggles |
| `src/tool_utils.py` | 92 | The leaf module for the MCP-manager and upload-handler globals, output truncation and the shared tool-arg parser |
| `src/builtin_mcp.py` | 386 | Registers the built-in stdio MCP servers (Python and the npx browser server) at startup |

Four neighbouring sections own the code on the other side:

- `src-tools-parse-exec` owns the dispatcher that calls these tables (`execute_tool_block`) and the
  path-confinement helpers.
- `src-agent-tools` owns the handlers the tables admit.
- `src-mcp` owns `mcp_manager.py`, read here only at `_connect_stdio`.
- `src-tools-schema-index` owns the schema and index sources that `plan_mode_disabled_tools` and
  `known_tool_names` read.

## Coverage

**Read fully:**

| File | Lines |
| --- | ---: |
| `src/tool_capabilities.py` | 708 |
| `src/tool_policy.py` | 242 |
| `src/tool_security.py` | 284 |
| `src/tool_utils.py` | 92 |
| `src/builtin_mcp.py` | 386 |
| `tests/test_tool_policy.py` | 479 |
| `tests/test_email_registry_sync.py` | 86 |

The two suites that pin this section's policy partitions.

**Read partially:**

- `tests/test_external_context_tool_gate.py` (the capability assertions and the gate/approval cases,
  not all 1,473 lines)
- `tests/test_builtin_mcp_npx_cache.py`
- `src/mcp_manager.py` at `_connect_stdio` (`:180-200`)
- `src/agent_loop.py` at the `capabilities_for_action` call sites (`:3055-3090`, `:5745-5775`)
- `src/tool_approvals.py` at `_matches_unlocked` (`:235-275`)
- `src/agent_tools/coding_tools.py` (the `todowrite` handler, 74 lines)
- `src/agent_tools/session_tools.py` at `manage_session` (`:248-470`)
- `src/agent_tools/document_tools.py` at `ManageDocumentTool.execute` (`:740-900`)
- `src/tools/system.py` at `do_manage_skills` (`:24-130`) and `do_manage_tasks` (`:274-520`)
- `src/tools/calendar.py`, `src/tools/notes.py`, `src/tools/research.py`, `src/tools/contacts.py` at
  their action dispatch
- `src/ai_interaction.py` at `do_manage_memory` (`:341-560`)
- `website/setup.md:735-755`
- `specs/shell-mcp.md:88-100`
- `specs/testing-devops.md:218`

**Not read:**

- assigned to `src-tools-schema-index`: `src/tool_schemas.py`, `src/tool_index.py`,
  `src/tool_approval_scopes.py` and `src/tool_implementations.py`
- assigned to `src-tools-parse-exec`: `src/tool_execution.py`
- `src/agent_tools/*` beyond the handlers named above
- `mcp_servers/*`
- `src/mcp_manager.py` beyond `_connect_stdio`
- `src/teacher_escalation.py` beyond its `capabilities_for_action` call
- the JS/UI side of the tool toggles

**Checks run:**

- the seven gate and policy suites above under `venv/bin/python -m pytest -q`: `240 passed` in 2.0s
- a script that diffs each multiplexed tool's read and write action sets in
  `_PRIVATE_ACTION_READS` and `_PRIVATE_ACTION_WRITES` against its handler's `action ==` branches,
  for the nine multiplexed `manage_*` tools (calendar, contact, documents, memory, notes, research,
  session, skills and tasks). No read action mutates and no write action is classified read.
- a script computing `TOOL_TAGS - plan_mode_disabled_tools() - PLAN_MODE_READONLY_TOOLS`. The result
  is empty, so every fence-callable tool is either allowlisted or denied in plan mode.

## Findings

### [DOC-DRIFT] The browser MCP cache gate is off by default, and the setup guide documents the opposite

- **Location:** `src/builtin_mcp.py:212`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** The cache probe is only reached when `BROWSER_MCP_REQUIRE_CACHE` is true:

  ```python
  BROWSER_MCP_REQUIRE_CACHE = os.environ.get("ODYSSEUS_BROWSER_MCP_REQUIRE_CACHE", "").lower() in ("1", "true", "yes")
  ...
  if BROWSER_MCP_REQUIRE_CACHE and pkg_spec and not await _is_npx_package_cached(npx_path, pkg_spec):
  ```

  The comment above the gate states the intent — "the default path lets `npx -y` install
  @playwright/mcp on first start. Locked-down installs can opt back into the old no-network
  startup behavior with ODYSSEUS_BROWSER_MCP_REQUIRE_CACHE=1" (`:206-209`) — and
  `tests/test_builtin_mcp_npx_cache.py:39-43` pins the default to `False`. Measured with
  `venv/bin/python` against a stub manager, with `_is_npx_package_cached` stubbed to record its
  calls and report "not cached":

  ```
  --- default (env unset) ---
    REQUIRE_CACHE=False probe_called=False connect_attempted=True
    args: -y @playwright/mcp@latest --headless --caps vision --executable-path /usr/bin/chromium --isolated --no-sandbox
  --- ODYSSEUS_BROWSER_MCP_REQUIRE_CACHE=1 ---
    REQUIRE_CACHE=True probe_called=True connect_attempted=False
  ```

  Both shipped documents describe the `=1` behavior as the default. `website/setup.md:741`:
  "The npx-based ones (currently the browser server, `@playwright/mcp`) only start when their
  npm package is already in the local npx cache. If a package isn't cached, that server is
  skipped with a startup log message ... so a fresh install does not block on a multi-minute
  npm download". `specs/shell-mcp.md:96`: "It is cache-gated by checking npm's `_npx` cache ...
  uncached/missing browser MCP is logged with install guidance and skipped rather than blocking
  startup or downloading packages at boot." `specs/testing-devops.md:218` likewise calls it
  "cache-gated `@playwright/mcp@latest`". `ODYSSEUS_BROWSER_MCP_REQUIRE_CACHE` appears in no
  document at the snapshot (`grep -rn BROWSER_MCP_REQUIRE_CACHE --include='*.md'` over the
  repository outside the untracked `audit/` run returns nothing), so the switch that restores
  the documented behavior is undiscoverable.
- **Impact:** On a fresh install the browser server is not skipped; a background task runs
  `npx -y @playwright/mcp@latest`, which downloads and executes an unpinned third-party package
  (~300 MB with Playwright) as the app user, with the full parent environment inherited
  (`src/mcp_manager.py:193` passes `{**os.environ, **env}` to the stdio child). An operator who
  read `website/setup.md` and relies on the no-download-at-boot contract — an air-gapped or
  metered host, or a supply-chain policy that expects the package to be vetted into the cache
  first — does not get it, and the documented install step is no longer required. The app's own
  startup is not blocked (the work runs in `_spawn_bg`), but the server-registration behavior
  the document describes is inverted.
- **Fix:** Either make the documented behavior the default
  (`os.environ.get("ODYSSEUS_BROWSER_MCP_REQUIRE_CACHE", "1")`) and document `=0` as the
  auto-install opt-out, or keep the current default and rewrite `website/setup.md:741` and
  `specs/shell-mcp.md:96` and add the variable to the setup guide's environment table. Pinning
  `@playwright/mcp` to a version narrows the execution risk but does not close the mismatch.
