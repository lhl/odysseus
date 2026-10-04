# services: research and docs

## Overview

The two service-layer facades under `services/`: `services/docs/__init__.py` and
`services/docs/service.py` wrap the personal-document RAG lane in a `DocsService` that returns
`DocChunk` and `IndexResult` values, and `services/research/__init__.py`,
`services/research/research_handler.py` and `services/research/service.py` wrap a second copy of the
deep-research handler in a `ResearchService` that returns `ResearchResult`/`ResearchSource` values
and starts background jobs. Neither facade is constructed anywhere in production: the only importers
are the packages' own `__init__.py` files, `services/__init__.py`, and the tests, and the research
copy is recorded as a retirement item at `specs/research.md:150`.

The boundary: the live research handler is `src/research_handler.py` — `src/app_initializer.py:117`
constructs it, `app.py:713` hands it to the research routes, and `src/task_scheduler.py:2018` imports
it — so the file of that name in this section is a copy, not the runtime one. That copy, the routes
that serve it (`routes/research/research_routes.py`), and the report store and research engine are
`src-research-scheduling` and `routes-rest-memory-personal-research`; this section cites their code
where a finding rests on it and does not restate their findings. The vector lane the docs facade
calls (`src/rag_manager.py`, `src/rag_vector.py`, `src/embedding_lanes.py`) is `src-memory-rag`, and
`services/__init__.py`, which re-exports both packages, is `services-media`. "Docs" here is
personal-document RAG, not the living-document store that `scripts/odysseus-docs` and the document
routes read.

## Coverage

**Read fully:** all five assigned files (805 lines): `services/research/research_handler.py` (487),
`services/research/service.py` (167), `services/docs/service.py` (121), `services/docs/__init__.py`
(18), `services/research/__init__.py` (12). Working-tree line numbers refer to `2992bf6d368a`
(`git rev-parse --short=12 HEAD`); `git status --short` showed only the untracked `audit/`
directory, and the five files are unmodified against `HEAD`.

**Read partially:** the boundary code the findings rest on — the live handler
`src/research_handler.py` at `_research_json_path` (`:53-62`), `start_research` (`:240-364`), the
status/result/sources/raw-findings readers (`:407-521`) and `_handle_research_failure` (`:943-949`);
`src/rag_manager.py` in full (70 lines); `src/rag_vector.py` at `__init__`/`healthy` (`:76-142`),
`search` and its keyword fallback (`:348-443`), `index_personal_documents` (`:495-556`) and the
owner-scoped document-id helper (`:48-55`); `src/rag_singleton.py` in full (63 lines);
`src/constants.py` at the data-path constants (`:41-56`); `services/__init__.py` in full (27 lines);
`services/search/service.py` at the offloaded `comprehensive_web_search` call (`:64-77`);
`src/chat_processor.py:366`; `routes/personal_routes.py` at `_rag()`, the index-job lock and the
add-directory route (`:150-260`); `routes/research/research_routes.py` at the library owner gate
(`:367-386`); `src/app_initializer.py:117-124`; `app.py:713`; `src/task_scheduler.py:2014-2024` and
`:2122-2132`; `src/deep_research.py` at the round loop and the time budget (`:296`, `:536`,
`:796-797`); `specs/research.md:105-157` and `specs/documents-rag-uploads.md:150-170`. Tests read in
full: `tests/test_docs_query_nondict_rows.py`, `tests/test_research_handler_path_confinement.py`,
`tests/test_services_research_low_quality_sources.py`; the suites named under *Checks run* were
otherwise read only by result.

**Not read:** the live handler's other ~630 lines (`rename_owner`, the report HTML and image-hide
paths, the research-service call and the parts of the report formatter the copy does not share);
`src/deep_research.py` beyond the round loop and the time budget; the embedding, Chroma-client and
personal-docs internals (`src/embedding_lanes.py`, `src/chroma_client.py`, `src/embeddings.py`,
`src/personal_docs.py` beyond `retrieve_personal`); the rest of `routes/personal_routes.py` and
`routes/research/research_routes.py`; `src/task_scheduler.py` beyond the two regions above; the front
end; and every other `services-*` section. No live model, embedding service, Chroma instance or
browser was exercised, and no directory was indexed against a real vector store; the RAG probes below
stub the lane query and the chunk splitter so the surrounding code path stays real.

**Checks run:** `git rev-parse --short=12 HEAD`, `git status --short`, `wc -l` on the assigned files;
caller searches for the five assigned modules and their classes
(`grep -rn "services\.research\|services/research" --include=*.py .`, `grep -rn
'ResearchService\|ResearchHandler\|DocsService\|DocChunk\|IndexResult' app.py core routes src scripts`,
`grep -rn services scripts/`); greps for the store-directory constants (`CHROMA_DIR`, `RAG_DIR`); a
search for
`wait_for|TimeoutError|hard_timeout` in both research handlers; and four probes under
`venv/bin/python` with data directories in `/tmp` (outside the checkout), each quoted in the finding
it settles:

- **Report-path probe.** The copy's `get_status`, `get_result` and `_save_result` were called with
  `session_id="../outside"` and `RESEARCH_DATA_DIR` redirected to a temporary directory holding a
  sibling `outside.json`; the same id was passed to the live handler's `_research_json_path`.
- **Lane-filter and chunk-metadata probe.** `DocsService.query` and `DocsService.index` were run
  against the real `RAGManager`/`VectorRAG` code with `query_lanes`/`lane_count` stubbed to record the
  `where` filter, and with `add_document`/`_split_into_chunks` stubbed to record the metadata the
  indexer writes.
- **Index-result probe.** `DocsService.index` was run against the real `index_personal_documents`
  for a directory that does not exist, and the keys that method can return were read from its source.
- **Import probe.** `import services.search` was timed and inspected in `sys.modules` to see what the
  package `__init__` pulls in.

`venv/bin/python -m pytest -q` was run with the 41 files matching `ls tests | grep -iE
'research|docs|report'` (the docs/RAG, research, deep-research, personal-docs and visual-report
suites, `tests/run_order_report.py` and `tests/test_run_order_report.py` included) — **245 passed**,
3 warnings in 3.86s. The suites that pin this section's own modules
(`tests/test_docs_query_nondict_rows.py`, `tests/test_research_service.py`,
`tests/test_services_research_low_quality_sources.py`, `tests/test_svc_research_sources_nondict.py`,
`tests/test_research_handler_analyzed_urls.py`) are among them. The full suite and `audit.py` were not
run; run-level generation, counts and secret-gate validation belong to the coordinating reviewer.

### [SECURITY] The compatibility research handler joins an unvalidated session id into its report path

- **Location:** `services/research/research_handler.py:117`, `:154`, `:174`, `:202`, `:219`
- **Severity:** low
- **Disposition:** next
- **Evidence:** five methods build the on-disk report path by joining the caller's id with no
  validation — `get_status` (`:117`), `get_result` (`:154`), `get_sources` (`:174`), `clear_result`
  (`:202`, which unlinks it) and `_save_result` (`:219`, which overwrites it):

  ```python
  path = RESEARCH_DATA_DIR / f"{session_id}.json"
  ```

  `ResearchService` forwards its caller's `session_id` unchanged (`services/research/service.py:157`,
  `:163`, `:167`). The live handler guards exactly this id with a regex plus a resolve-and-contain
  check, and its callers rely on it:

  ```python
  # src/research_handler.py:53-62
  def _research_json_path(session_id: str) -> Optional[Path]:
      if not isinstance(session_id, str) or not _RESEARCH_SESSION_ID_RE.fullmatch(session_id):
          return None
      root = RESEARCH_DATA_DIR.resolve()
      path = (RESEARCH_DATA_DIR / f"{session_id}.json").resolve()
      try:
          path.relative_to(root)
      except ValueError:
          return None
      return path
  ```

  `tests/test_research_handler_path_confinement.py:24-28` pins that `"../escape"`, `".."`,
  `"rp/test"` and `""` are rejected for the live module. Measured on the copy, with
  `RESEARCH_DATA_DIR` pointed at a temporary directory beside a file the id escapes to:

  ```
  svc path expr  : /tmp/svcprobe-jyv7er81/deep_research/../outside.json
  resolves to    : /tmp/svcprobe-jyv7er81/outside.json
  inside dir?    : False
  svc get_status("../outside") -> {'status': 'done', 'progress': {}, 'query': 'OUTSIDE-DIR-REPORT', 'started_at': 0}
  live _research_json_path("../outside") -> None
  outside.json after svc _save_result -> {"query": "OVERWRITTEN", "status": "done", "result": "OVERWRITTEN", ...}
  ```

  Reachability: nothing in production constructs this handler. `grep -rn
  'ResearchService|ResearchHandler|DocsService' app.py core routes src scripts` returns the live
  class in `src/app_initializer.py:23`, `:117`, `src/research_handler.py:65` and
  `src/task_scheduler.py:2018`, no reference to the copies (the one other hit,
  `routes/auth_routes.py:474`, is a comment about the live handler's registry), and no reader of
  either facade; the copies reach the runtime only as
  imports, because `services/research/__init__.py:5` re-exports this handler and
  `services/__init__.py:13` re-exports that, so any `from services.X import Y` in the app executes the
  chain (`import services.search` left `services.research.research_handler` and
  `services.docs.service` in `sys.modules`). `specs/research.md:120` and `:150` record the copy as
  compatibility surface to retire, and `specs/research.md:129` states the policy it does not meet
  ("Persisted report access and mutations should return 404 for cross-owner or null-owner JSON").
- **Impact:** a caller of `ResearchService` — or of the handler directly, which is how the project's
  own parity test loads it — that passes an id containing `..` or a path separator reads, overwrites
  or deletes a `*.json` file outside `data/deep_research`: another application store under `data/`, or
  a file outside the data directory entirely. No caller exists today, so this is a latent defect in
  the surface the spec asks to keep at parity, not a live vulnerability; the gap is specific to the
  copy, which did not receive the guard the live module got.
- **Fix:** retire the copy as `specs/research.md:150` proposes, or give it the same
  `_research_json_path` helper and reject an invalid id in `start_research` the way
  `src/research_handler.py:265-266` does.

### [SECURITY] The docs facade cannot scope a search or an index write to an owner

- **Location:** `services/docs/service.py:52` (`query`), `:104` (`index`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** neither method takes an owner, and the lane treats an absent owner as "no filter":

  ```python
  results = self.rag.search(query, k=top_k)              # services/docs/service.py:52
  result = self.rag.index_personal_documents(directory)  # services/docs/service.py:104
  ```

  ```python
  # src/rag_vector.py:357 (search)
  where_filter = {"owner": owner} if owner else None
  # src/rag_vector.py:536-537 (index_personal_documents)
  if owner:
      meta['owner'] = owner
  ```

  The keyword fallback applies the same rule (`if owner and meta.get("owner") != owner: continue`,
  `src/rag_vector.py:420`). `RAGManager` forwards an owner when it is given one
  (`src/rag_manager.py:35-37`, `:39-50`), and the live callers pass it:
  `src/chat_processor.py:366` (`rag_manager.search(message, k=5, owner=owner)`),
  `routes/personal_routes.py:232` (`rag.index_personal_documents(directory, owner=owner)`) and
  `src/personal_docs.py:302`. Measured with the real `search`/`index_personal_documents` code and the
  lane query stubbed to record its filter:

  ```
  lane filter from DocsService.query() -> [('search', None)]
  lane filter with owner='alice'      -> [('search', {'owner': 'alice'})]
  chunk metadata written             -> [{'source': '/tmp/.../a.txt', 'filename': 'a.txt', 'directory': '/tmp/...', 'type': '.txt', 'chunk_id': 0}]
  chunk metadata with owner='alice'  -> [{'source': ..., 'owner': 'alice', 'chunk_id': 0}]
  ```

  No production module constructs `DocsService` (`grep -rn 'DocsService' app.py core routes src
  scripts` returns nothing).
- **Impact:** a consumer of the facade searches every owner's indexed personal documents — `owner=None`
  disables the lane filter, so the query is unscoped — and writes chunks that carry no owner, which
  every owner-filtered search then excludes. Nothing is exposed today because nothing calls it; the
  hazard is that `services/docs/service.py` is the documented facade for this lane
  (`specs/documents-rag-uploads.md:159`) and it cannot express the scoping the live paths use, so the
  first caller to adopt it gets both failure modes.
- **Fix:** add an `owner` parameter to `query` and `index` and pass it to the lane, or delete the
  facade in favour of `RAGManager`/`VectorRAG`, whose signatures already take it.

### [ERROR-HANDLING] `DocsService.index` cannot report an error: the key it reads is never returned and `success` is dropped

- **Location:** `services/docs/service.py:104-109`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the facade reads three keys, and the only backend supplies two of them:

  ```python
  result = self.rag.index_personal_documents(directory)
  return IndexResult(
      indexed=result.get("indexed_count", result.get("indexed", 0)),
      failed=result.get("failed_count", result.get("failed", 0)),
      errors=result.get("errors", []),
  )
  ```

  `self.rag` is a `RAGManager`, which delegates to `VectorRAG.index_personal_documents`
  (`src/rag_manager.py:39-50`), whose two returns are
  `{success, indexed_count, failed_count, message}` (`src/rag_vector.py:548-553`, `:556`) — no
  `errors` key, and its per-file error text goes to the log only (`:545`). Read from the source and
  measured for a directory that does not exist:

  ```
  return keys of VectorRAG.index_personal_documents: ['chunk_id', 'directory', 'failed_count', 'filename', 'indexed_count', 'message', 'source', 'success', 'type']
  any 'errors' key in that source: False
  DocsService.index body reads: ['indexed_count', 'indexed', 'failed_count', 'failed', 'errors']

  missing dir -> IndexResult(indexed=0, failed=0, errors=[])
  raw backend -> {'success': True, 'indexed_count': 0, 'failed_count': 0, 'message': 'Indexed 0 chunks from /nonexistent/dir/xyz'}
  ```

  The module's own test supplies the missing key from a fake and names the case after the live shape:
  `tests/test_docs_query_nondict_rows.py:22` returns `{"indexed_count": 7, "failed_count": 2,
  "errors": ["bad.pdf"]}` under `test_index_maps_live_vectorrag_result_shape` (`:37`), so its
  `errors` assertion (`:45`) pins a shape the live backend does not produce. The spec describes the
  mapping as `indexed_count`/`failed_count` plus the legacy `indexed`/`failed`
  (`specs/documents-rag-uploads.md:159`).
- **Impact:** every failure shape collapses into the same success-shaped result. A directory that does
  not exist, an empty directory and a directory whose files all failed to extract are indistinguishable
  (`indexed=0, failed=0, errors=[]`), and the per-file reasons never reach the caller. The live route
  branches on the flag the facade drops (`if result["success"]:`, `routes/personal_routes.py:233`,
  `:250`), so this is a facade-specific loss rather than a backend one.
- **Fix:** carry `success` (and `message`) on `IndexResult` and populate it from the result — raising
  or returning a failed result when it is false — and either have the backend return `errors` or drop
  the field and fix the test to use the live shape.

### [PERF] The async entry points run blocking index, search and web-search work on the event loop

- **Location:** `services/docs/service.py:52` and `:104`, `services/research/research_handler.py:445`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `DocsService.query` and `DocsService.index` are `async def` (`:41`, `:94`) and call the
  synchronous Chroma/embedding work inline, where the live route moves the identical call to a worker
  thread:

  ```python
  # routes/personal_routes.py:247-248, with the blocking cost noted at :151-154
  async with _index_job_lock:
      result = await run_in_threadpool(_index_directory)
  ```

  `_index_directory` is `rag.index_personal_documents(directory, owner=owner)`
  (`routes/personal_routes.py:232`), and the route reads the `success` flag the docs facade drops
  (`:233`, `:250`). The research copy's failure fallback has the same shape with an
  outbound fetch: `comprehensive_web_search` is synchronous, and the sibling service runs it in a
  thread with a comment saying why —

  ```python
  # services/search/service.py:66-72
  # comprehensive_web_search is synchronous ... Run it off the event
  # loop so we don't block it, ...
  _context, raw_results = await asyncio.to_thread(
      comprehensive_web_search,
  ```

  — while the copy calls it directly from the async `call_research_service` path:

  ```python
  # services/research/research_handler.py:443-445
  from src.search import comprehensive_web_search
  search_result = comprehensive_web_search(query)
  ```

  That last line is identical to the live handler's (`src/research_handler.py:949`), so it is not
  unique to the copy; the docs-side calls are, since no other code path in this section has a worker
  thread between the coroutine and the store.
- **Impact:** a caller that awaits `DocsService.index` on a large directory stalls every other
  coroutine in that process for the walk, the text extraction and the embedding calls, and
  `DocsService.query` does the same per query; the research fallback blocks the loop for a multi-page
  web search. No caller exists today, so the cost is unpaid — this is the shape a future caller
  inherits, and the two sibling implementations already show the fix.
- **Fix:** `await asyncio.to_thread(self.rag.index_personal_documents, directory)` and the same for
  `search` and `comprehensive_web_search`, or make these entry points synchronous so the caller owns
  the decision to offload.
