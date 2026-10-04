# routes: memory, personal files and research

## Overview

`routes/memory/__init__.py`,
`routes/memory/memory_routes.py`,
`routes/memory_routes.py`,
`routes/personal_routes.py`,
`routes/research/__init__.py`,
`routes/research/research_routes.py`,
`routes/research_routes.py`.

Memory CRUD and search, the personal-file library and its indexing, and the research job API
with report listing and HTML rendering. The stores and vector lanes they call are
`src-memory-rag` and `services-memory`; the live research handler is `src/research_handler.py`
(`src-research-scheduling`), not the similarly named `services/research/research_handler.py`.
Authentication is the `core-auth-session` boundary and the middleware in `app.py`.

## Coverage

**Read fully:** all seven assigned files (1,861 lines): `routes/memory/memory_routes.py` (568),
`routes/personal_routes.py` (465), `routes/research/research_routes.py` (783),
`routes/memory_routes.py` (18), `routes/research_routes.py` (17), and
`routes/memory/__init__.py` and `routes/research/__init__.py` (5 each). Boundary files read fully:
`src/auth_helpers.py`, `core/middleware.py`, `services/memory/__init__.py`, and
`services/memory/memory.py` (the compatibility import of `src.memory.MemoryManager`).
Working-tree line numbers refer to `2992bf6d368a`; `git status --short` showed only the untracked
`audit/` directory before and after the checks.

**Read partially:** `app.py` at authentication, exemptions, identity stamping and adjacent
static/image setup (250–549), plus the memory/research router registration search;
`src/app_initializer.py` at the `ResearchHandler` import, construction and return sites;
`src/memory.py` (1–310: reads, owner filtering, validation, save and entry construction);
`services/memory/memory_extractor.py` at `audit_memories` (495 through end), including its
owner-scoped merge and vector rebuild; `src/research_handler.py` (35–89 and 240–859: path
confinement, task launch, cancellation, timeout/error recovery, persistence, report/image access,
and the live research-service call); `src/personal_docs.py` (230–344: tracking and exclusions);
`src/rag_vector.py` (495–624 and 678 through end: owner metadata on indexing, directory/source
deletion); `src/request_models.py` (1–110: memory and directory body models); `core/auth.py`
(15–64: privilege defaults); `static/js/admin.js` and `static/js/init.js` by
`can_manage_memory` search. Tests read: `tests/test_memory_owner_isolation.py`,
`tests/test_research_owner_scope_routes.py` and `tests/test_personal_delete_file_confinement.py`
in full; the other executed tests were not read. The non-runtime
`services/research/research_handler.py` was searched for task/owner methods, not read fully.

**Not read:** no assigned route file remains unread. The rest of the authentication, memory,
vector, personal-document and research implementations beyond the regions above; the deep
research engine, endpoint resolver internals, visual-report renderer, PDF parser and front end
beyond the privilege searches. No live model, embedding service, browser flow, large-library
latency benchmark or multi-process race test was run.

**Checks run:** `git rev-parse --short=12 HEAD`, `git status --short`, assigned-file `wc -l`,
`ls tests | grep -iE 'memory|personal|research'`, focused route-import and privilege/JSON-call
searches, and two inline `venv/bin/python -` probes using temporary data directories outside
the checkout. The probes exercised actual routers through `TestClient` with a stamped user
and stub privilege manager, and the actual research persistence/library functions with model
work replaced by a deterministic timeout. The four JSON-body routes (memory add, personal
add-directory, research start and hide-image) returned **422 for both an array and a string**;
there is no `await request.json()` in these assigned routes, so the auth/admin section's
non-object-body error does not recur here. The two module-alias suites passed, including
legacy/canonical object identity and monkeypatch behavior.

`venv/bin/python -m pytest -q` was run with these fourteen files:
`tests/test_memory_owner_isolation.py`, `tests/test_memory_routes_session_owner.py`,
`tests/test_memory_routes_shim.py`, `tests/test_personal_delete_file_confinement.py`,
`tests/test_personal_dir_symlink_escape.py`, `tests/test_personal_remove_dir_confinement.py`,
`tests/test_personal_upload_isolation.py`, `tests/test_personal_upload_privilege.py`,
`tests/test_research_endpoint_owner_scope.py`, `tests/test_research_owner_scope_routes.py`,
`tests/test_research_report_read.py`, `tests/test_research_routes_path_confinement.py`,
`tests/test_research_routes_shim.py`, `tests/test_research_session_id_validation.py` —
**113 passed**, three deprecation warnings. A second invocation with
`tests/test_memory_bullet_extraction.py` and `tests/test_memory_store_unreadable_no_wipe.py`
returned **16 passed**, one deprecation warning. Total: **129 passed across 16 suites**.
The full suite and `audit.py` were not run; run-level generation, counts and secret-gate
validation belong to the coordinating reviewer.

### [SECURITY] Memory pin, edit, delete and audit bypass the memory-management privilege

- **Location:** `routes/memory/memory_routes.py:503-513` (pin), `:528-549` (edit), `:550-566` (delete), `:289-324` (audit)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** add and import explicitly call `require_privilege(request, "can_manage_memory")`
  (`:106-107`, `:346-347`), and a grep for the helper over the whole module returns only those
  two sites, so the other mutations resolve the owner and nothing else. Delete, at `:550-566`:

  ```python
  def delete_memory(request: Request, memory_id: str):
      """Delete a memory item by its ID."""
      user = _owner(request)
      all_mem = _load_for_update(memory_manager)
      # ... find target and verify ownership ...
      _verify_memory_owner(target, user)

      all_mem = [m for m in all_mem if m["id"] != memory_id]
      memory_manager.save(all_mem)
  ```

  Pin (`:503-513`) and edit (`:528-549`) have the same shape, and `api_audit_memories`
  (`:289-324`) calls `audit_memories(..., owner=user)` without the gate; the callee actually
  rewrites the owner's entries. The router has no
  shared privilege dependency. `src/auth_helpers.py:163-188` enforces the flag only when
  `require_privilege` is called; the app middleware authenticates the user, not this feature.

  An inline Python `TestClient` probe used a real temporary `MemoryManager`, an authenticated
  `alice` request state, and an auth manager returning `can_manage_memory=False`:

  ```text
  privilege false: POST /api/memory/add 403
  privilege false: PUT /api/memory/one 200
  privilege false: POST /api/memory/one/pin 200
  privilege false: DELETE /api/memory/one 200
  remaining memory rows: 0
  ```

- **Impact:** an account whose administrator disabled memory management can still change,
  pin and erase existing memories through HTTP, and can invoke the consolidating audit if a
  model is configured. Owner checks still hold: this does not permit changing another user's
  memories. The audit's missing gate was verified statically; no live LLM call was made.
- **Fix:** apply the same `can_manage_memory` gate to pin, edit, delete and audit before loading
  or mutating state, and test denied privileges on every memory mutation, not just add/import.

### [BUG] The research library silently drops saved partial reports with null statistics

- **Location:** `routes/research/research_routes.py:399-407`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the library defaults a missing `stats` key, but not a present null value:

  ```python
  "duration": d.get("stats", {}).get("Duration", ""),
  "rounds": d.get("stats", {}).get("Rounds", ""),
  # ...
  except Exception:
      continue
  ```

  Null is a value the live writer emits, not merely a malformed-file hypothesis:
  `src/research_handler.py:624` persists `"stats": entry.get("stats")`. The timeout recovery
  at `:356-367` formats the researcher's partial report, marks the entry `done` and saves it,
  but never assigns `entry["stats"]`. Its partial-error recovery has the same shape.

  An inline Python probe ran the actual `start_research` background task with
  `call_research_service` replaced by a coroutine that supplied an evolving report and raised
  `asyncio.TimeoutError`. Only report formatting and event dispatch were stubbed; persistence
  and the library route were real, using a temporary directory:

  ```text
  timeout recovery: status= done stats= None saved result present= True library total= 0
  ```

  A separate persistence/library probe changed only the saved `stats` value to `{}`:

  ```text
  saved stats: None
  library with null stats: {'research': [], 'total': 0}
  library after stats={} total: 1
  ```

- **Impact:** a partial report deliberately recovered after a research timeout is saved but
  absent from the user's library and its total count. The broad exception handler hides the
  failure. The JSON and result-access paths still retain the report, so this is loss of
  discoverability, not deletion of the saved research.
- **Fix:** normalize null statistics to an empty mapping before reading fields, preferably
  validate their shape as well, and persist the recovery statistics when saving partial
  results. Add a library test using the timeout recovery's real saved shape.

### [PERF] Research library listing reads every report synchronously on the event loop

- **Location:** `routes/research/research_routes.py:367-380`, `:419`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the async handler walks and reads the shared directory without yielding:

  ```python
  async def research_library(
      # ...
  ):
      # ...
      for p in data_dir.glob("*.json"):
          try:
              d = json.loads(p.read_text(encoding="utf-8"))
      # ... owner filtering, thumbnail selection and sorting ...
      return {"research": items[:limit], "total": len(items)}
  ```

  Filtering by owner happens after the full JSON read, and the response limit is applied
  after all reads and sorting. An inline Python probe instrumented `Path.read_text` with
  two valid reports, one owned by the caller and one by another user:

  ```text
  library limit=1: JSON reads= 2 returned= 1 async handler= True
  ```

  In contrast, the sibling personal reload route at `routes/personal_routes.py:192-198`
  explicitly moves its blocking scan into `await run_in_threadpool(...)`.
- **Impact:** listing even one library item blocks other coroutines in that server process
  for the directory scan and parsing of every saved report, including other owners' reports.
  The work grows with total stored report bytes, not the requested page size. This is a
  scaling defect, not a measured outage: production library sizes and stall durations were
  not benchmarked.
- **Fix:** move the complete listing/filter/sort operation to a worker thread (or make this
  non-awaiting handler synchronous so FastAPI offloads it). A persistent metadata index can
  bound repeated full-report reads later; offloading is the smallest event-loop fix.
