# services: memory

## Overview

Files in this section:

- `services/memory/__init__.py`
- `services/memory/memory.py`
- `services/memory/memory_extractor.py`
- `services/memory/memory_vector.py`
- `services/memory/service.py`
- `services/memory/skill_extractor.py`
- `services/memory/skill_format.py`
- `services/memory/skill_importer.py`
- `services/memory/skills.py`

This is the package the rest of the app imports for memory and skills. Two of the nine files are
compatibility re-exports of canonical modules (`memory.py` re-exports `src.memory.MemoryManager` and
its helpers, `memory_vector.py` re-exports `src.memory_vector.MemoryVectorStore`). The others hold the
background memory extractor and its consolidating audit (`memory_extractor.py`), the background skill
extractor (`skill_extractor.py`), the SKILL.md reader/writer (`skill_format.py`), the disk-backed skill
store (`skills.py`), the GitHub/skills.sh bundle importer (`skill_importer.py`), and a `MemoryService`
facade (`service.py`) that no production caller uses.

The boundary: the stores and their own guards — `src/memory.py` (`MemoryManager`,
`MemoryStoreUnreadable`, the atomic write, the owner filter), `src/memory_vector.py`, the embedding
lanes, the Chroma client and the RAG index — are `src-memory-rag`; `services/memory/memory_vector.py`
is a five-line re-export of one of them, so this section reports only what the wrappers here do with
it. The route handlers that call the extractors, the audit and the importer, and the owner and
privilege checks they run first, are `routes-rest-memory-personal-research`
(`routes/memory/memory_routes.py`) and `routes-skills-calendar-task` (`routes/skills_routes.py`); the
agent-facing `manage_skills` and `manage_memory` wrappers are `src-agent-tools`; the teacher-escalation
loop that also writes skills is `src-research-scheduling`. A finding here is about what these modules
do with the values they are handed, not about whether their callers scoped them.

## Coverage

Line numbers refer to `2992bf6d368a`. `git status --short` showed only the untracked `audit/`
directory before and after the checks.

**Read fully:** all nine assigned files, 2,835 lines.

| File | Lines |
| --- | ---: |
| `skills.py` | 716 |
| `memory_extractor.py` | 678 |
| `skill_importer.py` | 487 |
| `skill_format.py` | 483 |
| `skill_extractor.py` | 305 |
| `service.py` | 126 |
| `memory.py` | 20 |
| `__init__.py` | 15 |
| `memory_vector.py` | 5 |

**Read partially:**

- the boundary code the findings rest on. `src/memory.py` at `_read_entries` (`:125-164`),
  `load_all` / `load_all_for_update` / `load` (`:166-194`), `_validate_entries` (`:215-232`), `save`
  (`:261-278`) and `add_entry` (`:280-299`)
- `src/memory_vector.py` in full (251 lines — the store the extractor drives)
- `src/memory_provider.py` at the `NativeMemoryProvider` method signatures (`:114-256`)
- `src/embedding_lanes.py` at `EmbeddingLane` (`:24-56`), `_create_lane` (`:232-249`) and
  `build_embedding_lanes` (`:252-272`)
- `src/embeddings.py` at `FastEmbedClient` (`:132-192`)
- `src/chroma_client.py` (`:1-60`)
- `routes/memory/memory_routes.py` at `_load_for_update` (`:38-50`) and `api_audit_memories`
  (`:289-337`)
- `routes/chat_helpers.py` at the extraction dispatch (`:1154-1250`)
- `routes/skills_routes.py` at `SkillAddRequest` (`:37-62`), `import-from-url` (`:1351-1378`), `add`
  (`:1381-1412`) and `save_skill_markdown` (`:1804-1851`)
- `src/tools/system.py` at `do_manage_skills` (`:24-245`)
- `src/builtin_actions.py` at `action_test_skills` and `action_audit_skills` (`:1910-2050`)
- `setup.py` at the `MEMORY_VECTORS_DIR` entry (`:14-40`)

**Not read:**

- `src/memory.py` outside the regions above (search, consolidation, the chat-extraction helpers)
- the `src/memory_provider.py` method bodies
- `src/rag_vector.py`, `src/personal_docs.py` and the rest of `src-memory-rag`'s files
- the skills front end (`static/js/skills*.js`) and every other `static-*` path
- `src/teacher_escalation.py`
- `mcp_servers/memory_server.py`
- `services/__init__.py`
- the parts of `routes/skills_routes.py`, `routes/memory/memory_routes.py` and
  `routes/chat_helpers.py` outside the regions above

No live LLM, embedding endpoint or ChromaDB server was reachable in this environment, so no
extraction, audit or import was run end to end against a real model or a real GitHub URL.

**Checks run:**

- `git rev-parse --short=12 HEAD` and `git status --short`
- caller greps for `MemoryService(`, `audit_memories`, `extract_and_store` and `MEMORY_VECTORS_DIR`
- caller greps for `to_thread` and `run_in_threadpool` across `routes/`, `src/` and `services/`
- four throwaway probes under `/tmp` (not part of the target tree), each quoted in the finding it
  settles: the SKILL.md round trip, a non-list `steps`/`tags` add and a nested-path import
  (`/tmp/probe_mem/skill_probes.py`)
- `audit_memories` against an unparseable store (`/tmp/probe_mem/audit_unreadable.py`)
- a real `MemoryVectorStore.rebuild` of 300 entries with the real fastembed encoder over a
  Chroma-shaped stub collection (`/tmp/probe_mem/rebuild_loop_block.py`)
- `_PinnedTransport.handle_request` over a stub httpcore pool streaming 5 MiB
  (`/tmp/probe_mem/transport_buffer.py`)

The 49 suites matching `ls tests | grep -iE 'memory|skill'` were run over this surface — **205
passed**, 2 warnings, 3.55s.

### [PERF] The memory audit re-embeds every owner's memories inside the request coroutine and stalls the event loop

- **Location:** `services/memory/memory_extractor.py:668` (with `:516`, `:658`, `:672`), reached from
  `routes/memory/memory_routes.py:316`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `audit_memories` is `async` for one `await` (the LLM call at `:550`); every other step
  runs synchronously on the caller's event loop. After the model answers, it writes the whole store
  and then re-embeds every entry in it, including entries belonging to other owners:

  ```python
  memory_manager.save(saved_entries)                                   # :658
  ...
  # Rebuild vector index from the full saved set, not just this owner's
  # slice — otherwise the shared collection is wiped of every other
  # owner's entries until they happen to run their own audit.
  if memory_vector and memory_vector.healthy:
      memory_vector.rebuild(saved_entries)                             # :668
  ...
  _save_tidy_state(memory_manager, owner, _fingerprint_entries(final_entries))   # :672
  ```

  `MemoryVectorStore.rebuild` (`src/memory_vector.py:188-244`) deletes and recreates the collections
  and encodes every entry in batches of 100 (`embeddings=lane.encode(batch_texts)`, `:236`), and
  `EmbeddingLane.encode` (`src/embedding_lanes.py:38-40`) runs the encoder inline. Probe with the real
  store and the real fastembed encoder, calling `rebuild` from inside a coroutine while a 10 ms
  heartbeat task ran:

  ```
  healthy: True lanes: ['fastembed']
  warm rebuild(300) inside coroutine: 0.40s wall; heartbeat ticks=5 max gap=0.41s
  ```

  The heartbeat was starved for the whole rebuild — 5 ticks instead of roughly 40, one 0.41 s gap —
  so the loop was blocked for the entire call, about 1.3 ms per stored memory on this machine. The
  route awaits the audit directly (`result = await audit_memories(...)`, `routes/memory/memory_routes.py:316`)
  and the automatic trigger at `:485` calls it from the background extraction task. Sibling paths in
  this codebase move the same class of work off the loop: `routes/personal_routes.py:196-197` wraps the
  personal-docs re-index in `await run_in_threadpool(...)`, `src/teacher_escalation.py:239` uses
  `asyncio.to_thread`, and 79 call sites for the two helpers exist under `routes/`, `src/` and
  `services/`; none of them is in a memory path.
- **Impact:** every request served by the same worker waits for the audit's synchronous half. The cost
  scales with the total stored memory count across all owners, not with the caller's slice, so a store
  of a few thousand entries blocks the loop for seconds at a time. `POST /api/memory/audit` is
  reachable by any authenticated user — the missing `can_manage_memory` gate on that route is
  `routes-rest-memory-personal-research.md`'s finding — and the automatic audit fires every five
  extracted memories (`AUDIT_INTERVAL`, `:114`), so this is not a rare admin action. The re-embedding
  itself is deliberate (the collection is shared); running it on the loop is not.
- **Fix:** move the blocking halves to a worker thread, e.g.
  `await asyncio.to_thread(memory_vector.rebuild, saved_entries)`, and the same for
  `memory_manager.save(...)` and the fingerprint/state writes if the store is large.

### [BUG] Saving a SKILL.md drops every `##` heading outside the four known section names

- **Location:** `services/memory/skill_format.py:292-295` (`parse_body`), with `:40-41`, `:346-349` and
  `services/memory/skills.py:428`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `parse_body` looks each `##` heading up in `_HEADING_TO_KEY` and starts a section with
  `key=None` when the lookup fails — the heading line itself is dropped, and the lines under it become
  `body_extra`:

  ```python
  for line in body.splitlines():
      m = re.match(r"^##\s+(.*?)\s*$", line)
      if m:
          heading = m.group(1).strip().lower()
          key = _HEADING_TO_KEY.get(heading)
          sections.append((key, []))
          continue
      sections[-1][1].append(line)
  ```

  `emit_body` writes the known sections first and appends `body_extra` last (`:346-349`), so the
  surviving text also moves to the end of the file. Probe (`/tmp/probe_mem/skill_probes.py`)
  round-tripping a SKILL.md in the common third-party layout:

  ```
  --- headings in input : ['# Release checklist', '## When to Use', '## Instructions', '## Examples']
  --- headings in output: ['## When to Use', '# Release checklist']
  ```

  The same round trip drops frontmatter keys the schema does not know (`license` and `allowed-tools`
  in the probe) and rewrites `status`, `confidence`, `source` and `created`. The rewritten text is what
  lands on disk: `import_bundle_from_files` writes `sk.to_markdown()` (`services/memory/skills.py:428`)
  instead of the fetched file, and every edit goes through `update_skill` (`:432`) → `_write_skill`
  (`:175-181`, `atomic_write_text(path, sk.to_markdown())` at `:179`), which
  `POST /api/skills/{id}/markdown` reaches at `routes/skills_routes.py:1827`. The module docstring states the opposite for the body: "Anything else
  (raw paragraphs after the last known section) is preserved in `body_extra` and round-trips on save"
  (`:40-41`) — the paragraphs survive, their headings do not.
- **Impact:** a user who saves a skill whose markdown carries `## Notes`, `## Instructions` or
  `## Examples` — through the raw-markdown route or any later edit — or who imports a third-party
  SKILL.md written for a different section vocabulary, gets a file back whose headings are gone and
  whose sections have been reordered to the end of the document. The text is
  still there, so nothing is unrecoverable except the headings and the unknown frontmatter keys, and
  the original file is still at the source URL for an import — but the saved skill no longer reads the
  way it was written, and nothing warns.
- **Fix:** keep the unknown heading line when a `##` heading does not map to a known key (append it to
  `body_extra` before its lines, or store an ordered list of raw sections), and carry unknown
  frontmatter keys through `to_frontmatter` the way `body_extra` is carried. If the normalisation is
  intended, say so in the docstring and in the import response instead of claiming a round trip.

### [ERROR-HANDLING] An unreadable memory store is reported as "nothing to audit", so the Tidy route answers 200 for a store it could not read

- **Location:** `services/memory/memory_extractor.py:516-519`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the audit's first read uses the lenient loader, which answers a failed read with an
  empty list, and the empty list is then reported as a successful no-op:

  ```python
  existing = memory_manager.load(owner=owner)
  if not existing:
      logger.info("Memory audit: nothing to audit")
      return {"before": 0, "after": 0}
  ```

  Probe (`/tmp/probe_mem/audit_unreadable.py`) with a store holding `{"not": "a list"}`:

  ```
  corrupt store: load_all() -> []
  corrupt store: load_all_for_update() -> MemoryStoreUnreadable: .../memory.json is not a JSON array (got dict)
  audit_memories() -> {'before': 0, 'after': 0}
  route response would be -> {'ok': True, 'before': 0, 'after': 0, 'removed': 0}
  ```

  The route builds that response from the result (`routes/memory/memory_routes.py:328-337`), so the
  caller gets HTTP 200 and `ok: true`. Every other path in the same file and module treats this state
  as an error: `extract_and_store` loads through `load_all_for_update()` and returns with
  "Skipping auto memory extraction, store unreadable" (`:392-399`), the audit's own merge step does the
  same and returns `{"error": "store_unreadable"}` (`:640-648`), and the route module's
  `_load_for_update` answers 503 "Memory store is temporarily unreadable — no changes were made"
  (`routes/memory/memory_routes.py:38-50`). The store is not damaged by this path — nothing is written
  — but the failure is invisible.
- **Impact:** a user whose `memory.json` is truncated or holds the wrong shape sees "Tidy" report 0
  before and 0 after with no error, which reads as "your memory is empty and clean" rather than "the
  store could not be read". That is the state `MemoryStoreUnreadable` exists to make loud, and the
  same state on the add path is already a 503. The user's actual memories are unaffected, so this is a
  diagnostic failure, not data loss.
- **Fix:** load through `load_all_for_update()` and return `{"error": "store_unreadable"}` (or raise)
  on `MemoryStoreUnreadable`, so the route answers 503 instead of 200 with zero counts.

### [BUG] Importing a bundle whose SKILL.md sits at a nested path leaves a second, unowned copy of the skill on disk

- **Location:** `services/memory/skills.py:414-416` (with `:403`, `:428` and `:159-164`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the importer preserves the bundle's own layout under the skill directory and then also
  writes a root `SKILL.md`, so a bundle fetched from a skill folder keeps its original nested file:

  ```python
  # Preserve bundle layout (templates/, references/, etc.) under the skill dir.
  for rel, content in files.items():
      safe = _safe_relpath(rel)
      dest = os.path.join(skill_dir, safe)
      os.makedirs(os.path.dirname(dest), exist_ok=True)
      atomic_write_text(dest, content)
  ...
  atomic_write_text(self._skill_file(cat, nm), sk.to_markdown())      # :428
  ```

  The keys in `files` are repo-root-relative (`_list_github_dir` builds them as
  `f"{rel_dir}/{name}"`, `services/memory/skill_importer.py:416`), so a bundle fetched from
  `.../tree/main/skills/release-checklist` keeps
  `skills/release-checklist/SKILL.md` as a sub-path. `_iter_skill_files` (`:159-164`) yields *every*
  directory containing a file named `SKILL.md`, so the nested copy becomes a second skill record.
  Probe (`/tmp/probe_mem/skill_probes.py`) importing such a bundle:

  ```
  files on disk: ['imported/release-checklist/SKILL.md', 'imported/release-checklist/skills/release-checklist/SKILL.md', 'imported/release-checklist/skills/release-checklist/reference.md']
  load_all() names : ['release-checklist', 'release-checklist']
  load_all() owners: ['None', 'alice']
  load(owner=alice) : ['release-checklist']
  ```

  The nested copy keeps the frontmatter's own fields, so it is unowned (`None`) while the root copy
  carries the importing user. `load(owner=...)` filters strictly, so the duplicate is invisible in the
  owner's own list, but `load_all()` — used by `add_skill`'s name set (`:353`) and by the backup
  import (`routes/backup_routes.py:112`) — returns both. The nested directory is also what
  `read_skill_reference` serves: a reference file under it is readable through the preserved sub-path
  (`skills/release-checklist/reference.md` in the probe).
- **Impact:** one import can create two records for one skill. The unowned copy occupies the name in
  the global name set, so a later `add_skill` or import of that name is silently renamed
  (`name-2`) even though the user cannot see the skill that caused the collision; in the no-auth
  single-user deployment, where `load(owner=None)` returns everything, both copies are listed and the
  first delete removes only one of them. Disk use is doubled for the bundle. Nothing is lost, and an
  owner-scoped delete of the skill removes the whole directory including the nested copy.
- **Fix:** skip a bundle file whose basename is `SKILL.md` when its path differs from the chosen
  `pick_skill_md` key (or flatten it), so a bundle contributes exactly one `SKILL.md` per skill
  directory; alternatively, make `_iter_skill_files` ignore `SKILL.md` files below the skill root.

### [TYPE-SAFETY] A non-list `steps` or `tags` value from the skill extractor's LLM reply is stored as a per-character list

- **Location:** `services/memory/skills.py:365` and `:375` (with `services/memory/skill_extractor.py:280-281`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `add_skill` coerces both fields with `list(...)` and no type check, and the extractor
  passes the model's JSON values straight through:

  ```python
  steps=data.get("steps", []),        # skill_extractor.py:280
  tags=data.get("tags", []),          # skill_extractor.py:281
  ```
  ```python
  tags=list(tags or []),                                            # skills.py:365
  procedure=list(procedure if procedure is not None else (steps or [])),   # skills.py:375
  ```

  Probe (`/tmp/probe_mem/skill_probes.py`) with `steps="1. build\n2. push"` and `tags="deploy ci"`:

  ```
  procedure stored as: ['1', '.', ' ', 'b', 'u', 'i', 'l', 'd', '\n', '2', '.', ' ', 'p', 'u', 's', 'h']
  tags stored as     : ['d', 'e', 'p', 'l', 'o', 'y', ' ', 'c', 'i']
  --- SKILL.md on disk ---
  tags: [d, e, p, l, o, y,  , c, i]
  ...
  ## Procedure

  1. 1
  2. .
  3.  
  4. b
  ```

  The skill is created and written, so the corruption is persisted rather than rejected. `str` is not
  the only shape: a dict or a list of dicts reaches `to_frontmatter`/`_emit_scalar` the same way. The
  HTTP add path is typed (`tags: List[str]`, `procedure: List[str]`,
  `routes/skills_routes.py:42-47`) and the agent tool path passes the model's JSON arguments
  unvalidated (`src/tools/system.py:120-140`), so the exposure is the two model-authored paths, not
  the form. `title` is handled: a non-string title raises `AttributeError` at
  `skill_extractor.py:238`, which the enclosing `except Exception` turns into a logged drop.
- **Impact:** a model that answers with a string (or an object) for `steps`/`tags` — a common
  LLM-output shape — produces a skill whose procedure is a list of single characters and whose tags
  are single letters, written to `data/skills/<category>/<name>/SKILL.md` and served to the agent by
  `read_skill_md`. It needs no further mistake to cause harm, but the damage is confined to one
  auto-created skill, which the user can delete, and a re-run of the extractor after the first
  creation is dropped as a duplicate title.
- **Fix:** coerce with a shape check before use — `steps = [str(s) for s in steps] if isinstance(steps, list) else []`
  (and the same for `tags`) in `add_skill`, or validate the parsed object in `_extract_json_object`'s
  callers. Rejecting the field is better than splitting it.

### [PERF] The skill importer buffers a whole response body before applying its 400 KB file cap

- **Location:** `services/memory/skill_importer.py:211` (the transport), with `:21` and `:379-386`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the pinned transport reads the entire body into memory before httpx hands it back,
  and the only size guard runs afterwards:

  ```python
  core_response = self._pool.handle_request(core_request)
  content = b"".join(cast(Iterable[bytes], core_response.stream))    # :211
  ```
  ```python
  def _fetch_bytes(url: str) -> bytes:
      r = _get_checked(url, headers={"Accept": "application/vnd.github+json"}, timeout=30.0)
      if r.status_code >= 400:
          raise _github_response_error(r)
      _assert_github_url(str(r.url), context="redirect target")
      if len(r.content) > MAX_FILE_BYTES:                            # :384
          raise SkillImportError(f"file too large: {url}")
  ```

  Probe (`/tmp/probe_mem/transport_buffer.py`) driving the real `_PinnedTransport` with a stub httpcore
  pool that streams 80 × 64 KiB:

  ```
  MAX_FILE_BYTES               : 400000
  chunks the transport drained : 80 x 65536 bytes
  len(response.content)        : 5242880
  buffer exceeds the cap by    : 4842880 bytes
  ```

  Every fetch goes through this path — the SKILL.md, each sibling asset, and each entry of the
  directory listing (`_fetch_text`, `:389-393`), which fetches any file whose suffix is in
  `ALLOWED_SUFFIXES` (`.json`, `.csv`, `.md`, …). The GitHub contents API already returns a `size` per
  entry, which the listing loop ignores.
- **Impact:** the 400 KB / 2 MB limits bound what the importer *keeps*, not what it *reads*: a single
  allowed-suffix file in the imported repository is downloaded in full before it is rejected, so an
  admin importing from a repository that carries a large asset pays its whole size in server memory.
  Reachability is limited — the caller is an authenticated admin pasting a GitHub URL, and the
  repository is a third party's, not the requester's own — so the exposure is a memory spike on one
  request rather than a remotely triggerable outage. I did not measure what body size
  `raw.githubusercontent.com` will serve.
- **Fix:** check the listing's `size` before fetching an entry, and bound the read in
  `_PinnedTransport.handle_request` (accumulate the stream and abort past `MAX_FILE_BYTES`) so the cap
  holds for the raw and redirect paths too.

### [DEAD-CODE] `MemoryService` has no production caller, and its `delete` and `recall` carry no owner

- **Location:** `services/memory/service.py:32-126` (with `:42-48`, `:90-108`, `:116-126`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** nothing outside the module and its tests constructs it:

  ```
  $ grep -rn "MemoryService(" --include=*.py .
  ./services/memory/service.py:37:        service = MemoryService()          # the docstring example
  ./tests/test_memory_imports.py:29:    service = MemoryService(str(tmp_path))
  ./tests/test_memory_recall_nondict_rows.py:20:    svc = MemoryService(str(tmp_path))
  ```

  The class is still imported on every memory request — `services/memory/__init__.py:4` imports it and
  `routes/memory/memory_routes.py:24` and `routes/backup_routes.py:9` import the package — so it is
  live code that looks live. Its API has no owner anywhere: `delete(memory_id)` rewrites the whole
  store from `load_all()` and removes the matching vector row (`:116-126`), `recall` delegates to
  `NativeMemoryProvider` without an owner, and `get_all` returns the first 100 entries of the shared
  store (`:111-113`). The two tests that exercise it pin its shape, not its reachability
  (`tests/test_memory_imports.py` drives remember/get_all/recall/delete on a single-user store).
- **Impact:** none today — no caller reaches it. It matters as a hazard and as a false signal: the
  module is exported from `services/__init__.py` as the service-layer memory API and its docstring
  shows `await service.remember(...)` usage, so the next caller to wire it up inherits an
  id-only delete that crosses owners on a multi-user instance, where the live path
  (`MemoryManager` through the routes) checks ownership on every mutation. Its
  `MemoryVectorStore` construction is also gated on `data/memory_vectors` existing
  (`:44-46`), a directory only `setup.py` creates.
- **Fix:** delete `service.py` and its exports from `services/memory/__init__.py` and
  `services/__init__.py` (and the two tests), or, if the facade is meant to be the service-layer
  entry point, give `remember`/`recall`/`get_all`/`delete` an owner argument and route them through
  `NativeMemoryProvider`'s owner-aware methods.
