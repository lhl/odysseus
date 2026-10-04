# routes: uploads, embeddings, presets and preferences

## Overview

`routes/upload_routes.py`, `routes/embedding_routes.py`, `routes/editor_draft_routes.py`,
`routes/signature_routes.py`, `routes/preset_routes.py`, `routes/prefs_routes.py`,
`routes/font_routes.py`, `routes/emoji_routes.py`, `routes/tts_routes.py`,
`routes/stt_routes.py`, and `routes/cookbook_output.py`.

File and preference endpoints outside the chat and document-library routers: uploads,
embedding-model downloads and endpoint configuration, editor drafts, visual signature stamps,
presets, user preferences, custom-font discovery, the emoji proxy, and speech synthesis and
transcription. `cookbook_output.py` supplies pure output-classification helpers and cache-probe
scripts to the Cookbook router; it is not itself an HTTP output reader. The embedding routes do
not index or query owner documents.

The boundary: authentication is in `core-auth-session` and `app.py`; upload limits are in
`src-security`; upload storage is in `src-documents`; the database models are in
`core-data-platform`; preset management and embedding configuration
consumers are in `src-memory-rag`; speech services are in `services-media`. Preference
load/save helpers are implemented in the route file reviewed here. Cookbook execution and
status endpoints remain in `routes-cookbook`.

## Coverage

**Read fully:** all eleven assigned files, 1,882 lines: `routes/upload_routes.py` (533),
`routes/embedding_routes.py` (376), `routes/editor_draft_routes.py` (188),
`routes/signature_routes.py` (151), `routes/preset_routes.py` (126), `routes/prefs_routes.py`
(125), `routes/emoji_routes.py` (109), `routes/tts_routes.py` (87),
`routes/cookbook_output.py` (75), `routes/stt_routes.py` (57), and `routes/font_routes.py`
(55). Boundary helpers `core/atomic_io.py` and `src/upload_limits.py` were also read fully.
Line references are to the working tree at `2992bf6d368a`; `git status --short` showed only
the untracked audit directory.

**Read partially:** `app.py` at the authentication setup, exemptions and complete
`AuthMiddleware` implementation (250–489), plus router-registration searches;
`core/middleware.py` through line 140, including `require_admin`;
`src/auth_helpers.py` through line 160, including identity resolution and `require_user`;
`src/upload_handler.py` at filename/ID validation (1–89), construction, size policy,
hashing and MIME/extension handling (187–406), index loading (776–855), and upload
resolution, rate cleanup, statistics and the complete `save_upload` implementation
(1100–1394), with searches for ownership and reservation helpers;
`src/preset_manager.py` at persistence and all route-called mutators/getters (115–190),
with searches of loading/defaults; `core/database.py` at `Signature` and `EditorDraft`;
`services/tts/tts_service.py` at cache operations and synthesis (90–259);
`services/stt/stt_service.py` at local/API transcription and statistics (90–199);
`src/document_processor.py` at vision analysis (333–392);
`routes/calendar_routes.py` at preference-writing CalDAV configuration handlers (805–984);
`src/builtin_actions.py` at the scheduled model-serve preference update (3270–3354);
caller searches in `routes/`, `src/caldav_sync.py`, `src/task_scheduler.py`, and
`routes/cookbook_routes.py`. Test-source reads covered `tests/conftest.py`,
`tests/test_prefs_routes.py`, `tests/test_editor_draft_payload.py`,
`tests/test_preset_expand_owner_scope.py` and `tests/test_cookbook_dead_download_status.py`;
the other selected tests were executed, not read end to end.

**Not read:** no assigned route file remains unread. Boundary modules beyond the regions
above, the embedding/vector stores and their indexing/query paths, the rest of the speech
services and model pipelines, the Cookbook execution router, and the front-end consumers
were not reviewed. No real credential authentication, external speech/vision/embedding
provider, local inference model, browser rendering, or multi-process preference-write race
was exercised. The upload content-detector integration test could not run without libmagic/
python-magic. Run-level build and audit gates were not run, as required by this assignment.

**Checks run:** `git rev-parse --short HEAD`, `git status --short`, route/caller searches,
and an inline `venv/bin/python` probe using a temporary preference file and an in-memory
SQLite database. The probe exercised real preference/draft/signature endpoints with the
state that middleware stamps for two different bearer owners, called the three raw-JSON
handlers with a non-object body, and recorded the thread used by stub speech services.
It did not mint or authenticate real bearer credentials. A separate AST check found zero
`await` expressions in both `set_pref` and `_save_for_user`: ordinary preference PUTs on one
event loop do not interleave inside their read-modify-write operation. This does not establish
safety across workers or other threaded writers.

The required discovery command, `ls tests | grep -iE
'upload|embedding|prefs|signature|font|emoji|tts|stt|preset|editor_draft'`, selected 50 Python
suites. Running `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q -p no:cacheprovider`
with those paths produced **220 passed, 1 skipped**. A second focused invocation added
`tests/test_cookbook_dead_download_status.py` and repeated
`tests/test_upload_content_detection_magic.py` with `-rs`: **12 passed, 1 skipped**, of which
11 passes were additional Cookbook tests. Total distinct tests: **231 passed, 1 skipped**.
The skip reason was `libmagic/python-magic not installed in this environment`; both invocations
reported the existing SQLAlchemy `declarative_base()` deprecation warning. Every finding's
cited source span was reopened with line numbers before writing.

### [SECURITY] Bearer callers share the same preferences, editor drafts and signatures across token owners

- **Location:** `routes/prefs_routes.py:108-122`, `routes/editor_draft_routes.py:83-88`, `:113-118`, `:171-178`, `routes/signature_routes.py:88-95`, `:103-110`, `:132-139`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** these handlers use the middleware's generic caller identity as the storage
  owner without rejecting bearer requests or resolving their actual owner:

  ```python
  user = get_current_user(request)
  prefs = _load_for_user(user)
  prefs[key] = body.get("value")
  _save_for_user(user, prefs)
  ```

  Draft and signature creation similarly store `owner=user`; their list and mutation
  checks compare against that same value. `src/auth_helpers.py:10-12` simply returns
  `request.state.current_user`. For every successfully authenticated bearer token,
  `app.py:458-460` sets:

  ```python
  # Keep bearer-token callers out of normal cookie/user
  request.state.current_user = "api"
  request.state.api_token = True
  ```

  The middleware allows these paths through after authentication; none of these three
  routers uses the bearer rejection in `require_user` (`src/auth_helpers.py:132-133`).
  An inline Python probe registered the real routers against temporary stores and stamped
  that state with a different bearer-token owner for each of two requests. After the first owner
  wrote data, the second owner's requests produced:

  ```text
  different bearer owner reads prefs: {'key': 'review', 'value': 'alice-data'}
  different bearer owner reads draft: 200 {'review': 'alice-data'}
  different bearer owner deletes draft: 200
  signature create: 200
  different bearer owner lists signatures: 1
  different bearer owner deletes signature: 200
  ```

  The probe substituted authentication state, not token validation; the state assignment
  and absence of a later gate were verified in the middleware and router registration.
- **Impact:** a valid delegated token can read or mutate data another token owner created
  through these APIs. Listing reveals the draft/signature IDs, so guessing an ID is not a
  prerequisite. Cookie-created data remains separated by username: the demonstrated exposure
  is the shared bearer-created bucket, not every browser user's existing records. Bearer-created
  records are also absent from their human owner's ordinary browser view.
- **Fix:** use `require_user` if these are browser-only routes. If bearer access is intended,
  require an explicit token scope and use its resolved owner for every read and write. Handle
  existing `api`-owned rows separately; their actual owners cannot be inferred from these rows.
- **Re-review (2026-10-04):** re-derived in full and lowered from high. The middleware assignment (`app.py:458-463`) and the
  three routers' use of `get_current_user` are as quoted, and no later gate exists. The shared
  bucket holds only what a bearer client stored through these three routers, and no shipped bearer
  client calls them: `grep -rln "api/prefs\|editor-draft\|api/signatures\|editor_draft" companion
  swift integrations mcp_servers` returns nothing, and the Codex and Claude integrations use the
  scope-aware `/api/codex/*` routes. Cookie users' records are not reachable this way. The defect
  that remains is that a token of any scope reaches three unscoped stores, which is a scope check
  that does not deliver what it claims, hence medium.


### [PERF] Speech, upload processing and vision analysis run blocking work on the request event loop

- **Location:** `routes/tts_routes.py:41`, `:50`, `routes/stt_routes.py:39`, `routes/upload_routes.py:291-292`, `:484`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the handlers are asynchronous, but invoke synchronous processing directly:

  ```python
  audio_b64 = tts_service.synthesize_to_base64(request.text)
  audio_data = tts_service.synthesize(request.text)
  text = stt_service.transcribe(audio_bytes)
  meta = upload_handler.save_upload(u, client_ip, owner=owner)
  gallery_id = _promote_chat_image_to_gallery(meta, owner, session_id)
  text = analyze_image_with_vl(path, owner=current_user) or ""
  ```

  The endpoint speech implementations call synchronous `httpx.post(..., timeout=60)`
  (`services/tts/tts_service.py:189`, `services/stt/stt_service.py:144`); their public
  methods call those implementations directly. The local-provider branches also perform
  inference synchronously. Vision delegates directly to its synchronous implementation
  (`src/document_processor.py:390-392`), which calls
  `llm_call(..., timeout=120)` (`:375`). Upload saving hashes and copies the file and writes
  the index before returning; promotion copies the image and commits a database row.

  An inline Python probe called the real TTS and STT handlers from an event loop with stub
  services that compared `threading.get_ident()` with the loop thread:

  ```text
  TTS runs on event-loop thread: True
  STT runs on event-loop thread: True
  ```

  In contrast, the same upload router already offloads manual cleanup:

  ```python
  cleaned_count = await asyncio.to_thread(
      _run_reference_safe_cleanup,
      upload_handler,
  )
  ```

  (`routes/upload_routes.py:325-327`). No real model or network latency was measured.
- **Impact:** a cache-miss speech or vision request stalls other requests and streaming work
  on the same server event loop while inference or synchronous network I/O runs. A slow
  endpoint can hold that loop through its configured socket timeout; those timeout values
  are not measured end-to-end deadlines. Upload hashing, copying and image processing add
  shorter stalls proportional to file size. Authentication, upload limits and caches limit
  reach and repeated work, but do not prevent an ordinary authorized request from blocking
  unrelated users on the same worker.
- **Fix:** offload the complete blocking service calls and upload-processing operations with
  `asyncio.to_thread`, or move suitable handlers to synchronous FastAPI endpoints. Bound
  inference concurrency and verify shared service/store locking before introducing parallel
  calls; simply removing event-loop serialization must not introduce new store races.

### [ERROR-HANDLING] Three raw-JSON endpoints raise unhandled errors on non-object bodies

- **Location:** `routes/preset_routes.py:79-81`, `:122-123`, `routes/upload_routes.py:516-519`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the handlers parse arbitrary JSON and immediately use mapping methods:

  ```python
  data = await request.json()
  draft = (data.get("prompt") or "").strip()
  # save_group_presets:
  data = await request.json()
  preset_manager.save_group_presets(data.get("groups", []))
  # put_vision_text:
  body = await request.json()
  # ... JSONDecodeError handler ...
  text = (body or {}).get("text", "")
  ```

  Catching `JSONDecodeError` does not reject valid JSON with the wrong shape. An inline
  Python probe called these actual endpoint functions with `json()` returning a nonempty
  list, using a stub model import and an existing temporary upload:

  ```text
  non-object /api/presets/expand AttributeError
  non-object /api/presets/groups AttributeError
  non-object /api/upload/{file_id}/vision AttributeError
  ```

  For the upload route an empty list happens to fall back to `{}`; a nonempty list or string
  does not. This is a recurrence of the raw-JSON shape failure reported in
  `routes-rest-auth-admin.md`, not a separate failure class for each endpoint.
- **Impact:** malformed client input produces an unhandled server error instead of a 4xx
  validation response. The group writer is admin-only, the upload path checks ownership
  before parsing the body, and all three paths require upstream authentication; this is
  limited to error handling for authorized callers, not an authentication bypass.
- **Fix:** validate `isinstance(body, dict)` before using mapping methods, or give each
  endpoint a Pydantic request model, including string types for the prompt/name/text fields.
