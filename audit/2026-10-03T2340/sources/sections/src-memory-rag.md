# src: memory, RAG, embeddings and settings

## Overview

Files in this section:

- `src/chroma_client.py`
- `src/embedding_lanes.py`
- `src/embeddings.py`
- `src/index_walk.py`
- `src/memory.py`
- `src/memory_provider.py`
- `src/memory_vector.py`
- `src/personal_docs.py`
- `src/preset_manager.py`
- `src/rag_manager.py`
- `src/rag_singleton.py`
- `src/rag_vector.py`
- `src/settings.py`

This section covers what the assistant remembers with: the JSON memory store and the ChromaDB
vector index over memory entries, the personal-document index (vector and keyword), the embedding
lanes and clients that feed them, and the settings/presets stores. The route handlers that call into
it are covered by `routes-rest-memory-personal-research` and the other `routes-*` sections;
`core/database.py`'s hourly owner sweep and `core.atomic_io` are covered by `core-data-platform`;
the tool index's own copy of the embedding-lane bootstrap is covered by `src-tools-schema-index`.
A finding here is about the store or the index itself, not about who calls it.

## Coverage

**Read fully:** all thirteen files above, 3,667 lines.

Four findings rest on measurements taken at this snapshot against the real modules with
Chroma-shaped stub collections in place of ChromaDB (which is not reachable in this environment).
Each Evidence block states the probe, so the numbers can be reproduced; the stub replaces only the
external store, not the code under test.

### [RACE] Concurrent memory writes lose entries, raise `FileNotFoundError`, and can leave `memory.json` unreadable

- **Location:** `src/memory.py:275-278` (the shared temp path), with `:180-186` and `:261-274`
- **Severity:** high
- **Disposition:** fix-now
- **Evidence:** every writer stages through the same fixed temp name and then renames it:

  ```python
  tmp_file = self.memory_file + ".tmp"
  with open(tmp_file, "w", encoding="utf-8") as f:
      json.dump(entries, f, ensure_ascii=False, indent=2)
  os.replace(tmp_file, self.memory_file)
  ```

  No lock anywhere in the tree guards this store. Twelve threads released by a barrier, each
  running `load_all_for_update()` → append one entry → `save()` (13 entries written), 30 bursts,
  `sys.setswitchinterval(1e-5)` to force GIL hand-offs:

  ```
  25 runs: valid JSON, 2 entries      writer exceptions over 30 bursts:
   4 runs: valid JSON, 3 entries         FileNotFoundError      211
   1 run : UNREADABLE JSONDecodeError    MemoryStoreUnreadable    6
  ```

  The loss is not a stress-case artefact. With **two** concurrent writers (3 entries written),
  50 bursts: all 3 survived in 7, at least one was lost in 43, and a writer raised in 22. With
  three writers: 50 of 50 bursts lost an entry and 50 of 50 had a writer raise. Two writers
  colliding on `memory.json.tmp` also means one writer's `os.replace` can install a file the other
  writer had only truncated, which is how a burst leaves the store unparsable — the state
  `MemoryStoreUnreadable` was written to make loud (`:8-20`, "the writes are atomic, so the loss is
  durable"). The durability half of the same file is reported separately in
  `core-data-platform.md` — the hourly owner sweep rewrites `memory.json` with a plain truncating
  write (`core/database.py:1481-1482`); this finding is the concurrency half, which needs no crash.

  The write path is ordinary traffic, not an admin action: `src/chat_processor.py:352-354` calls
  `increment_uses` (a read-modify-write) after injecting memories into a turn,
  `src/chat_handler.py:338-340` saves on an inline "remember:" command, `src/ai_interaction.py:396-401`
  on the agent memory tool, `routes/memory/memory_routes.py:137,511,540,562` on add/pin/edit/delete,
  `routes/backup_routes.py:83-107` on import merge, and `src/memory_provider.py:164-166,233-249` on
  the provider API. `mcp_servers/memory_server.py` is a second **process** (`src/builtin_mcp.py:74`)
  that builds its own `MemoryManager(DATA_DIR)` (`:104`) and runs the same
  load-append-save (`:70,187,215,243`), so the app process and the built-in MCP server share both
  the file and the temp name with no coordination at all.
- **Impact:** three distinct failures, all silent to the caller: (1) a lost update — the last
  writer's snapshot wins and every other writer's change is gone, so a memory the user saved is
  simply absent; (2) `FileNotFoundError` propagates out of `save()` (nothing catches it there), so
  the request that called it fails; (3) the store can be left unreadable, after which every
  read-modify-write caller refuses to write (by design, `routes/memory/memory_routes.py:40-49`
  turns that into a 503) and the memory feature stops until the file is repaired. A memory entry is
  user data the user explicitly asked to keep.
- **Fix:** hold one lock across the whole read-modify-write and stop sharing a temp name. A
  `threading.Lock` on the manager plus an `update(fn)` helper used by the callers above covers the
  lost update — a lock inside `save()` alone does not, because the window is between the load and
  the save. `tempfile.mkstemp(dir=os.path.dirname(self.memory_file), prefix="memory.json.")` before
  the dump covers the rename collision. A process-local lock does not cover
  `mcp_servers/memory_server.py`; if that server keeps writing the same file, the lock must be a
  file lock (or the server must be pointed at the app's API instead of the file).
- **Re-review (2026-10-04):** re-derived in full; high stands. The source is as quoted and no lock exists
  (`grep -n "Lock\|flock\|fcntl" src/memory.py mcp_servers/memory_server.py` returns nothing). Two
  facts make the race reachable without the forced switch interval used above. The pin, edit and
  delete handlers are plain `def` routes (`routes/memory/memory_routes.py:503`, `:528`, `:550`), so
  FastAPI runs them on worker threads while `increment_uses` runs on the event loop for every chat
  turn that injected a memory. `mcp_servers/memory_server.py` is a separate process, so no in-process
  ordering covers it. The loss rates quoted were measured with `sys.setswitchinterval(1e-5)`; the
  rate under ordinary scheduling was not measured and is lower.


### [BUG] Re-indexing a directory never removes a changed file's previous chunks, so the index keeps serving the old text

- **Location:** `src/rag_vector.py:495-556` (`index_personal_documents`), with `:83-91` and `:191-198`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** document ids are a hash of the chunk text, so an edited chunk gets a new id, and
  the index path only ever adds:

  ```python
  doc_id = _generate_doc_id(text, metadata.get("owner") or "")
  ...
      existing = lane.collection.get(ids=[doc_id])
      if existing["ids"]:
          wrote = True
          continue
  ```

  Probe with a stub collection: index a one-file directory (`indexed_count=1`), edit the file, index
  the same directory again (`indexed_count=1`):

  ```
  rows in collection      : 2  (1 file on disk)
    doc_1fe6193099e0b755  source=note.md  text='version one content'
    doc_075032cb252826c2  source=note.md  text='version two content'
  ```

  Nothing in the tree removes the old rows. `reindex_directory` (`:599-613`) is the one method that
  removes before indexing and it has no caller — no route, no MCP action, nothing
  (`PersonalDocsManager.index_all_directories`, `src/personal_docs.py:448`, is likewise uncalled).
  The reachable index path is `POST /api/personal/add_directory`, which calls
  `rag.index_personal_documents(directory, owner=owner)` unconditionally
  (`routes/personal_routes.py:232`) even for a directory already tracked, and the agent-facing
  `mcp_servers/rag_server.py:116`.
- **Impact:** after an ordinary edit-then-re-add, retrieval can return the superseded text — for a
  small edit the old and new chunks embed almost identically and the stale one is a legitimate top
  hit — so the model answers from content the user has already changed. Each re-add also adds a
  copy of every changed chunk and nothing reclaims them, so the index grows monotonically with
  edits.
- **Fix:** after a file's chunks are written, delete that `source`'s rows whose ids are not among
  the ids just written. `delete_by_source` (`:686-687`) already implements the removal half, and the
  chunk ids for one file are computed in the same loop.

### [ERROR-HANDLING] A collection that fails is reported as an empty, healthy lane, so retrieval returns nothing with no diagnostic

- **Location:** `src/embedding_lanes.py:42-46` (`count`), with `:339-340`, `:366-373`, `:387`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `EmbeddingLane.count` swallows the error and reports zero, with no log line:

  ```python
  def count(self) -> int:
      try:
          return int(self.collection.count())
      except Exception:
          return 0
  ```

  Probe with a real `EmbeddingLane` over a collection whose `count()` raises (the client is a plain
  object, so `healthy` is true and the failure is exactly the one ChromaDB being down produces):

  ```
  lane.healthy            : True
  lane.count()            : 0   <- real EmbeddingLane.count()
  log records emitted     : 0
  search() results        : []
  collection.query calls  : 0
  collection.get calls    : 0
  get_stats()             : document_count=0 healthy=True
  lane stats              : {... 'count': 0, 'healthy': True}
  ```

  `lane_count` (`:339-340`) is the max over the lanes, so one failing lane makes it zero and
  `VectorRAG.search` returns before querying anything (`src/rag_vector.py:353-354`). The keyword
  fallback is never reached, and `query_lanes`'s `raise_if_all_failed` (`:387`) requires
  `attempted > 0`, which a `count()` that returns 0 never increments.
- **Impact:** a ChromaDB outage during a chat produces no results, no fallback, and no log line —
  the assistant silently stops using the user's documents and memories. The admin panel reports the
  index as healthy with 0 documents, which is indistinguishable from an empty index, so the
  operator has nothing to act on until they notice the behaviour.
- **Fix:** log the exception in `count()` (or raise a typed error) and mark the lane unhealthy so
  `get_stats()` and the search path can tell an outage from an empty index — the distinction
  `src/memory.py:125-155` already draws for `memory.json` with `MemoryStoreUnreadable`.

### [BUG] The personal-docs state files are written non-atomically, so a truncated write silently drops the tracked-directory list

- **Location:** `src/personal_docs.py:239-244` (`save_directories`), `:263-267` (`_save_excluded`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** both write the live file in place, with no temp file and no replace:

  ```python
  with open(self.directories_file, 'w', encoding="utf-8") as f:
      json.dump(_string_list(self.indexed_directories), f, indent=2)
  ```

  Every other JSON store in this section's files writes atomically through
  `core.atomic_io.atomic_write_json`: `src/settings.py:296`, `src/preset_manager.py:139`,
  `src/memory.py:275-278`. Probe: a truncated `indexed_directories.json` (a two-entry list cut
  mid-write) makes `load_directories` (`:223-236`) log one error and reset to empty:

  ```
  state file on disk      : '["/home/user/notes", "/home/user/work"'
  tracked directories     : []
  directories_count stat  : 1
  ```

- **Impact:** a crash or power loss inside the write loses the whole tracking list, and nothing
  reports it beyond one error line. The vector rows for those directories stay in the collection,
  but `remove_directory` returns early for an untracked directory (`:337`), `refresh_index` no
  longer walks it, and `get_file_list` no longer lists it — so the user cannot see or remove those
  indexed chunks from the UI until they re-add each directory by path. `excluded_files.json` has the
  same write and the same loss, which re-exposes files the user had excluded.
- **Fix:** write both through `core.atomic_io.atomic_write_json`, as the sibling stores do.

### [PERF] Two index paths transfer the whole collection to do bounded work

- **Location:** `src/rag_vector.py:415` (`_keyword_search_fallback`), `:578` (`remove_directory`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** both call `collection.get` with no `where` and no `limit`, then filter in Python.
  Probe for `remove_directory`: three rows indexed, one under the target directory —

  ```
  remove_directory(notes) -> {'success': True, 'removed_count': 1, ...}
  rows scanned by get()   : 3
  get() arguments         : ids=None include=['metadatas'] where=None limit=None
  rows that matched       : 1
  ```

  The same file shows the filtered alternative it does not use: `delete_by_source` asks Chroma for
  `where={"source": source}` (`:686-687`). `_keyword_search_fallback` loads every document from
  every lane (`:415`) to score word overlap for one query, and it runs on the request path
  precisely when a lane query has already failed (`:405`).
- **Impact:** a directory removal and every fallback search pull the entire index across the HTTP
  boundary. On a large index this is the dominant cost of an operation that touches one directory
  or returns `k` rows, and the fallback cost lands on the degraded path where the app is already
  failing. `remove_directory`'s scan is deliberate — no Chroma operator selects a scalar string by
  path prefix, as its docstring explains — but the fallback has no such constraint: it could score
  against the already-loaded keyword index (`src/personal_docs.py`) or bound the candidate set.
- **Fix:** bound the fallback scan (or serve it from the in-memory keyword index), and for
  `remove_directory` at least stop fetching documents — `include=["metadatas"]` is already minimal,
  so the remaining step is to page the scan or maintain a per-directory id list.

### [FOOTGUN] `VectorRAG._embed()` and `_collection` can come from different embedding lanes

- **Location:** `src/rag_vector.py:116-121` (`_embed`), with `:97-101` and `:93-95`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the lanes are built custom-first (`build_embedding_lanes`), but the collection
  prefers the fastembed lane while the model and the private encoder take the first lane:

  ```python
  self._collection = next(
      (lane.collection for lane in self._lanes if lane.name == LANE_FASTEMBED),
      self._lanes[0].collection,
  )
  self._model = self._lanes[0].client
  ...
  def _embed(self, texts: List[str]) -> List[List[float]]:
      return np.array(self._lanes[0].encode(texts), dtype=np.float32).tolist()
  ```

  With a custom endpoint configured, `_embed()` returns vectors from the custom model while
  `collection` is the fastembed lane's collection. Nothing calls either today: a grep for `_embed`
  and `.collection` across `routes/`, `src/`, `mcp_servers/` and `core/`, and in `app.py`, finds no external
  user, and `_embed` has no caller at all. But `collection` is documented as the public access
  point for route code ("Expose the ChromaDB collection for direct access by personal_routes etc.",
  `:93-95`). The same bootstrap is repeated in `src/memory_vector.py:34-52` and
  `src/tool_index.py:150-162`, which is why the three copies can disagree.
- **Impact:** the next caller to pair the documented property with the private encoder writes or
  searches vectors from the wrong model. A dimension mismatch fails loudly; equal dimensions (two
  models with the same width) return unrelated neighbours with no error.
- **Fix:** delete `_embed` (it has no caller), or have both it and `_collection` resolve from one
  named lane rather than from `_lanes[0]` and a name search.
