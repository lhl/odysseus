# tests: documents, uploads, gallery and media

## Overview

The 57 modules assigned to this section are the suites that pin the document editor and document
library, the upload handler and its retention rules, the gallery routes, the notes and reminder
routes, and the image-model ranking helper — 256 tests in total. This section establishes what
those tests prove: each finding quotes the assertion and the fixture and says which behaviour is
left untested.

The boundary with the neighbouring sections. Where the code itself is at fault, those sections are
cross-referenced in prose rather than restated; everything reported below is a defect in a test.

The production code these suites exercise belongs to:

| Section | What it owns |
| --- | --- |
| `src-documents` | The processor, actions, agent tools and `attachment_refs` |
| `routes-gallery-document`, `routes-rest-media-files` | The gallery, upload and document routes |
| `static-js-documents-email`, `static-js-editor` | `document.js`, `documentLibrary.js`, `notes.js`, `fileHandler.js` |
| `services-media` | The media services |

On the test side the neighbours are:

| Section | What it owns |
| --- | --- |
| `tests-security` | Auth and security regressions |
| `tests-session-chat-memory` | Chat, session and memory suites |
| `tests-harness` | conftest, helpers, taxonomy, run tooling |
| `tests-rest`, `tests-llm-tools`, `tests-cookbook-models`, `tests-email-calendar` | The remaining test groups |

This section owns exactly the 57 `tests/` paths listed for `tests-documents-media` in `run.toml`.

## Coverage

Line numbers are the working tree at `2992bf6d368a`.

**Read fully:** all 57 assigned files (5,940 lines, 256 tests).

| Area | Files | Tests | Paths |
| --- | ---: | ---: | --- |
| Documents, editor, PDF | 20 | 61 | `tests/test_document_*.py`, `tests/test_doc_library_*.py`, `tests/test_pdf_*.py` |
| Gallery and media | 17 | 70 | `tests/test_gallery_*.py`, `tests/test_image_models_*.py`, `tests/test_load_features_permission_error.py` |
| Notes and reminders | 9 | 29 | `tests/test_note_*.py`, `tests/test_notes_*.py` |
| Uploads and attachments | 11 | 96 | `tests/test_upload_*.py`, `tests/test_attachment_refs.py` |

**Read partially:** the production code and harness each finding rests on:

- `src/document_processor.py` at the PDF marker producer and consumer (`:112-152`, `:282-294`)
- `src/upload_handler.py` at `_index_lock` (`:240`), `_atomic_write_json` (`:692-742`) and the two
  `save_upload` read-modify-write sites (`:1270-1288`, `:1293-1315`)
- `routes/gallery/gallery_routes.py` at `list_albums` (`:813-848`), `_get_or_404_album`
  (`:2124-2130`), `_first_visible_image_endpoint`/`_visible_image_endpoint_for_base` (`:299-319`),
  the ten `require_privilege(request, "can_generate_images")` call sites and `_is_openai_api_base` /
  `_join_checked_gallery_endpoint`
- `routes/document/document_routes.py` at `_aggregate_language_facets` /
  `_library_language_for_document` (`:29-60`) and the render-pdf handler
- `src/agent_tools/document_tools.py` at `_owned_document_query` (`:58-65`) and the lazy
  `SessionLocal` imports each tool uses (`:359`, `:482`, `:717`, `:771`)
- `src/document_actions.py` at `run_document_tidy` (`:53-66`)
- `static/js/notes.js` at `_safeImgSrc`/`_attrEsc` (`:495-512`) and `openPanel`;
  `static/js/documentLibrary.js` at `libraryRemoveDocumentFromState` (`:406-424`);
  `static/js/fileHandler.js` at `uploadPending` (`:270-357`)
- `Dockerfile` (`:30-90`), `tests/TESTING_STANDARD.md` (the behavioral-first and isolation rules)
  and `tests/conftest.py`

**Not read:** the modules under test outside the regions above, and the other 57 sections' paths.
The coverage claim here is about the test files; the code they exercise was reviewed by the owning
sections and is not re-reviewed. The sibling suites for this surface that belong to other sections'
assignments were opened only where a finding cross-references them:

- `test_build_user_content_pdf_marker.py`, `test_owned_document_query.py`
- `test_replace_messages_upload_reservations.py`, `test_security_headers_pdf_preview.py`
- `test_active_document_clear.py`, `test_auth_disabled_document_access.py`
- `test_personal_upload_*.py`, `test_generated_image_confinement.py`
- the rest of `tests/`

**Checks run:** the 57 files as one suite, plus throwaway probes under `/tmp/probe` (two pytest
plugins — one that swaps a module for a textually mutated copy, one that raises from `find_spec`
for a named module — and three scripts). None of them write into the repository. Outputs are quoted
in the findings they settle.

```
$ venv/bin/python -m pytest -q -p no:randomly <the 57 assigned paths>
255 passed, 1 skipped, 2 warnings in 5.11s
```

The one skip is the only behavioural assertion in `tests/test_upload_content_detection_magic.py`
(finding 4).

### What these tests are made of

21 of the 57 files assert on the text of a source file rather than on behaviour. 12 have no
behavioural assertion at all, and 9 mix source-text assertions with behavioural ones.

The 12 with no behavioural assertion:

- `test_doc_library_open_orphaned.py`, `test_document_ai_preview_refresh_js.py`
- `test_document_deeplink.py`, `test_document_diff_discard_on_update_js.py`
- `test_document_editor_scroll.py`, `test_document_library_delete_counters.py`
- `test_gallery_album_owner_scope.py`, `test_gallery_image_privileges.py`
- `test_notes_dom_xss_helpers.py`, `test_notes_search_reset_on_reopen_js.py`
- `test_notes_select_esc_listener_js.py`, `test_upload_error_surfaced.py`

The repository's own standard discourages this and permits it only when the invariant cannot be
driven at runtime, with the reason stated in the docstring (`tests/TESTING_STANDARD.md:118-132`).
Most of the JS files state that reason ("document.js is browser-coupled and not importable in
pytest"), which the Node-driven `tests/test_notes_z_order_js.py` shows is not true of every module
in this set but is true of the ones making the claim. Three do not state a reason
(`test_document_ai_preview_refresh_js.py`, `test_gallery_image_privileges.py`,
`test_notes_dom_xss_helpers.py`), and one states a reason the repository's own tests contradict
(finding 1). The findings below are the individual cases where the source-text shortcut, or a
fixture, leaves a named behaviour unverified.

### Upload retention and attachment references

These tests do cover the retention and reference machinery, and mostly by behaviour rather than by
text. Four files carry it:

- `tests/test_upload_handler_cleanup.py` (13 tests) drives `cleanup_old_uploads` and the
  `manual_cleanup` route endpoint against seeded upload indexes and a real temporary SQLite
  database. It covers:
  - retention of an upload referenced from chat content and metadata
  - retention of an upload referenced from `Document.current_content` or `DocumentVersion.content`
  - retention of an upload referenced from `Note.image_url` or `color`
  - retention of an upload referenced from `CalendarCal.color`, or from `CalendarEvent.color`,
    `description` or `location`
  - retention of an upload referenced from a gallery row's stored content hash
  - retention when two index rows disagree, or when a row has no authoritative lifecycle metadata
  - fail-closed behaviour for a missing or corrupt index
  - index restore when file removal fails, and a 503 when reference discovery raises
- `tests/test_upload_handler_atomicity.py` covers the `uploads.json` read-modify-write race and
  `.bak` recovery (though one of its two concurrency tests is finding 2 below).
- `tests/test_attachment_refs.py` exercises `persistable_message_content`, `search_index_text` and
  `attachment_ref` (including its hash aliases) on real inputs.
- `tests/test_upload_routes_owner_scope.py` pins the owner gate and symlink confinement on the
  download and vision endpoints.

What is *not* covered by these files: `persistable_message_content` with a string or scalar
argument, and the `owner` argument of `UploadHandler.resolve_upload`. The attachment-budget and
media-subtype tests replace the real handler with a stub whose `resolve_upload(self, fid,
owner=None)` ignores `owner`, so no test in this set proves an attachment cannot be pulled into a
turn by an id belonging to another user. The `src-documents` and `routes-rest-media-files`
sections own the corresponding code.

### [BUG] The gallery album owner-scope tests assert on source text, and an unfiltered count and cover pass all five

- **Location:** `tests/test_gallery_album_owner_scope.py:40-48` (with `:6-8`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the file's own justification for the source-text approach is that the handlers
  cannot be driven:

  ```python
  # tests/test_gallery_album_owner_scope.py:6-8
  queries. The gallery route handlers are closures, so — matching the AST-assertion
  convention of test_gallery_image_privileges.py — we assert the guards are present
  in the source.
  ```

  The assertions are four substring searches in the function's source segment:

  ```python
  # tests/test_gallery_album_owner_scope.py:41-48
  fns = _function_sources()
  body = fns["list_albums"]
  # The album list, per-album image count, explicit cover, and cover-fallback
  # queries should all share the same gallery owner policy.
  assert "q = _owner_filter(q, user, GalleryAlbum)" in body
  assert "_count_q = _owner_filter(_count_q, user)" in body
  assert "cover = _owner_filter(cover_q, user).first()" in body
  assert "_cover_q = _owner_filter(_cover_q, user)" in body
  ```

  The premise is false: sibling tests in the same directory drive exactly this router through
  `TestClient` (`tests/test_gallery_null_user_routes.py:61-62`,
  `tests/test_gallery_filename_confinement.py:118`), so the standard's narrow exception does not
  apply here. Measured: a copy of `routes/gallery/gallery_routes.py` whose per-album count and
  cover-fallback queries were rewritten to drop the owner filter, leaving the `_owner_filter(...)`
  assignments in place but unused —

  ```python
  # /tmp/probe_mut/routes/gallery/gallery_routes.py:826,838 (mutant)
  count = db.query(GalleryImage).filter(GalleryImage.album_id == a.id, GalleryImage.is_active == True).count()  # MUTANT: owner filter unused
  first = db.query(GalleryImage).filter(GalleryImage.album_id == a.id, GalleryImage.is_active == True).order_by(GalleryImage.created_at.desc()).first()  # MUTANT: owner filter unused
  ```

  — leaves the file green while the endpoint leaks another owner's row:

  ```
  $ cd /tmp/probe_mut && .../venv/bin/python -m pytest -q .../tests/test_gallery_album_owner_scope.py
  5 passed, 1 warning in 0.27s

  $ venv/bin/python /tmp/probe/album_mutant_probe.py     # one album, one alice image + one bob image
  real   GET /api/gallery/albums as alice -> {'albums': [{... 'count': 1, 'cover_url': '/api/generated-image/b455d722….png'}]}
  mutant GET /api/gallery/albums as alice -> {'albums': [{... 'count': 2, 'cover_url': '/api/generated-image/b314f444….png'}]}
  ```

  The control that the swap was real is the failing test when the guard line itself is deleted:
  `1 failed, 4 passed` with
  `FAILED …::test_patch_validates_target_album_ownership` — i.e. the file detects a *deleted* call
  but not an ineffective one. `list_albums` is correct today (`routes/gallery/gallery_routes.py:825`,
  `:830`, `:837`).
- **Impact:** the per-album `count` and `cover_url` in `GET /api/gallery/albums` are an owner-scoped
  view of another user's images when the filter is lost, and issue #2754's regression test cannot
  see it. Any authenticated user is the audience once the regression lands; today the exposure is a
  missing safety net on a security control, not a live leak.
- **Fix:** drive `setup_gallery_routes()` with a seeded temp database and two owners, as
  `tests/test_gallery_null_user_routes.py:14-62` already does, and assert the returned `count` and
  `cover_url` for the caller's own images only. Keep the four source assertions as wiring checks if
  they still add value, but drop the "handlers are closures" justification — it is contradicted by
  two tests in the same directory.

### [BUG] `test_concurrent_inserts_lose_entries` re-implements the production critical section, so removing the production lock leaves it green

- **Location:** `tests/test_upload_handler_atomicity.py:92-118` (the claim at `:97`, the self-lock at
  `:105`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the docstring states the test's contract:

  ```python
  # tests/test_upload_handler_atomicity.py:95-97
  The production code does the reload + write under ``_index_lock``,
  and ``_atomic_write_json`` gives readers a consistent on-disk view.
  If either protection is removed, this test will fail.
  ```

  The insert it runs is written in the test, and takes the lock itself:

  ```python
  # tests/test_upload_handler_atomicity.py:104-108
  def insert(idx: int) -> None:
      with handler._index_lock:
          current = json.load(open(db_path)) if os.path.exists(db_path) else {}
          current[f"owner:hash_{idx}"] = {"id": f"file_{idx}", "owner": "owner"}
          handler._atomic_write_json(db_path, current)
  ```

  It never calls `save_upload`, which is where the production read-modify-write lives
  (`src/upload_handler.py:1270-1288`, `:1293-1315`). Measured with a plugin that replaced every
  `with self._index_lock:` in a copy of the module with a fresh per-call lock:

  ```
  $ PYTHONPATH=/tmp/probe SWAP_MODULE=src.upload_handler \
      SWAP_FROM='with self._index_lock:' SWAP_TO='with threading.Lock():' \
      venv/bin/python -m pytest -q -p swapmod tests/test_upload_handler_atomicity.py
  [swapmod] replaced src.upload_handler (6 site(s)); module file reported as …/src/upload_handler.py
  FAILED tests/test_upload_handler_atomicity.py::test_save_upload_concurrent_retains_all_entries
  FAILED tests/test_upload_handler_atomicity.py::test_duplicate_vs_insert_race_preserves_both
  2 failed, 10 passed, 1 warning in 0.12s

  $ ...same plugin... -k test_concurrent_inserts_lose_entries
  1 passed, 11 deselected, 1 warning in 0.08s
  ```

  The mutation is effective — the two production-path tests fail — and the test that names the bug
  still passes. Baseline for the same selection: `2 passed, 10 deselected` (three runs).
- **Impact:** the file reads as two independent guards for the `uploads.json` lost-update race. Only
  `test_save_upload_concurrent_retains_all_entries` (`:121`) and
  `test_duplicate_vs_insert_race_preserves_both` (`:156`) are; this one proves only that
  `threading.Lock` and `_atomic_write_json` behave, which is not the regression it was written for.
  A refactor that moves the production critical section out of `save_upload` keeps it green.
- **Fix:** delete the test-local critical section and call `handler.save_upload(...)` from the
  threads, as `:121` already does, or extract the index insert into a production helper and call
  that. Either way the test should fail if the lock is removed from the code path it names.

### [BUG] The `#4875` regression guard is a Dockerfile substring search, and its only behavioural assertion skips on this machine

- **Location:** `tests/test_upload_content_detection_magic.py:29-46` (with `Dockerfile:37`, `:84`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the file pins the fix for "the official Docker image shipped without python-magic"
  with two assertions, one on the Dockerfile text and one on behaviour:

  ```python
  # tests/test_upload_content_detection_magic.py:32-35
  # The C library python-magic dlopens, installed via apt...
  assert "libmagic1" in dockerfile
  # ...and the wrapper itself, installed via pip in the image.
  assert "python-magic" in dockerfile

  # :38-41
  def test_content_detection_overrides_misleading_extension(tmp_path):
      handler = UploadHandler(base_dir=str(tmp_path), upload_dir=str(tmp_path))
      if handler.file_detector is None:
          pytest.skip("libmagic/python-magic not installed in this environment")
  ```

  The skip fires here, so the behavioural half does not run:

  ```
  $ venv/bin/python -m pytest -q -rs tests/test_upload_content_detection_magic.py
  SKIPPED [1] tests/test_upload_content_detection_magic.py:41: libmagic/python-magic not installed in this environment
  1 passed, 1 skipped, 1 warning in 0.07s
  ```

  (`python-magic` is absent from the venv; `libmagic.so` is present.) The Dockerfile assertions
  cannot fail for the reason they exist: both strings also appear in the explanatory comments at
  `Dockerfile:47-52` and `:81-82`, so deleting both install lines still satisfies them, and the
  lines that keep them true are comments:

  ```
  removed lines: [(37, 'libmagic1 \\'), (84, 'RUN pip install --no-cache-dir python-magic==0.4.27')]
  'libmagic1' in dockerfile    : True
  'python-magic' in dockerfile : True
  original lines that still satisfy them:
    Dockerfile:47: # libmagic1 is the shared lib (libmagic.so.1) that python-magic dlopens for
    Dockerfile:49: # (libmagic1 + the python-magic wrapper, below) rather than in requirements.txt
    Dockerfile:50: # because python-magic resolves libmagic at import time: where the lib is
    Dockerfile:81: # python-magic powers content-based MIME sniffing in src/upload_handler.py.
    Dockerfile:82: # Image-only (not in requirements.txt) because it needs the libmagic1 system
  ```

  The install lines themselves are present and correct (`Dockerfile:37` in the apt list, `:84`
  `RUN pip install --no-cache-dir python-magic==0.4.27`). Two other sections record the same skip in
  their check summaries (`src-documents.md`, `routes-rest-media-files.md`); neither reports it as a
  finding.
- **Impact:** the file that exists to keep content-based MIME detection alive in the image passes
  whether or not the image installs it, and passes on a machine where the feature is dead. The
  standard calls a skip "a coverage gap to be aware of, not a pass"
  (`tests/TESTING_STANDARD.md:109-111`), and here the gap and the regression are the same condition.
- **Fix:** assert on the install statements, not the strings — parse the `apt-get install` block and
  the `RUN pip install` line for `libmagic1` and `python-magic`. Make the behavioural test runnable
  where the fix matters by adding `python-magic` to the dev/test requirements (the C library is
  present on Debian-based CI images), or mark the file as an acknowledged coverage gap.

### [BUG] The test that claims to guard the PDF marker constant cannot see the producer change it names

- **Location:** `tests/test_document_pdf_marker.py:20-22`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the test asserts a constant against a literal:

  ```python
  # tests/test_document_pdf_marker.py:20-22
  def test_marker_constant_matches_processor_output():
      # If _process_pdf's prefix ever changes, this guards the consumer.
      assert _PDF_CONTENT_MARKER == "\n\n[PDF content]:"
  ```

  The producer does not use that constant. `_process_pdf` writes its own literal:

  ```python
  # src/document_processor.py:148-151
  if pdf_text:
      if len(pdf_text) > 15000:
          pdf_text = pdf_text[:15000] + "\n[PDF content truncated]"
      return f"\n\n[PDF content]:{pdf_text}"
  ```

  while the consumer strips the second copy (`:282` `_PDF_CONTENT_MARKER = "\n\n[PDF content]:"`,
  `:294` `return (text or "").removeprefix(_PDF_CONTENT_MARKER).strip()`). Changing `:151` alone
  leaves the constant — and the assertion — untouched. Measured with the producer drifted:

  ```
  $ PYTHONPATH=/tmp/probe SWAP_MODULE=src.document_processor \
      SWAP_FROM='return f"\n\n[PDF content]:{pdf_text}"' \
      SWAP_TO='return f"\n\n[PDF TEXT]:{pdf_text}"' \
      venv/bin/python -m pytest -q -p swapmod tests/test_document_pdf_marker.py
  [swapmod] replaced src.document_processor (1 site(s)); module file reported as …/src/document_processor.py
  4 passed, 1 warning in 0.07s

  $ venv/bin/python -  # the same mutant, executed directly
  mutant _PDF_CONTENT_MARKER    : '\n\n[PDF content]:'
  mutant strip(producer output) : '[PDF TEXT]:\n\n[Page 1 text]:\nto the board, content begins'
  test assertion still true?    : True
  ```

  Control: the plugin reaches the test module — a mutant whose
  `strip_pdf_content_marker` returns `""` gives
  `2 failed, 2 passed` (`FAILED …::test_marker_removed_without_eating_following_text`,
  `FAILED …::test_text_without_marker_is_only_stripped`). The consumer call sites are
  `routes/document/document_routes.py:275`, `:530` and `src/document_processor.py:489`. The sibling
  regression for the same wrapper, `tests/test_build_user_content_pdf_marker.py:36-38` (owned by
  `tests-rest`), also assumes the shape by monkeypatching `_process_pdf`, so no test in the tree
  derives the prefix from the producer.
- **Impact:** the coupling the test advertises is untested. If `_process_pdf`'s prefix changes, every
  test in the file still passes and the `[PDF content]:` wrapper — up to 15,000 characters of
  extracted text — is stored in the document body instead of being stripped, which is the failure
  the file's docstring was written about.
- **Fix:** make the producer use the constant
  (`return f"{_PDF_CONTENT_MARKER}{pdf_text}"` at `src/document_processor.py:151`) so the assertion
  compares the constant with the value the producer actually emits, or replace the assertion with a
  round-trip through `_process_pdf` on a text-bearing PDF fixture (pypdf 6.19.0 is installed, but no
  test in the tree builds one).

### [BUG] `test_gallery_routes_imports_privilege_helper` asserts two strings that a 2,000-line file cannot fail to contain

- **Location:** `tests/test_gallery_image_privileges.py:39-42`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the whole test is:

  ```python
  # tests/test_gallery_image_privileges.py:39-42
  def test_gallery_routes_imports_privilege_helper():
      source = _gallery_source()
      assert "get_current_user" in source
      assert "require_privilege" in source
  ```

  Both names appear in the eight handlers the test names, and in two more gated handlers the set
  omits — `sharpen_image` (`routes/gallery/gallery_routes.py:1716`, gate at `:1718`) and
  `smart_mask` (`:1838`, gate at `:1845`) — for ten `require_privilege(request,
  "can_generate_images")` call sites in all (`:565`, `:609`, `:1263`, `:1522`, `:1718`, `:1742`,
  `:1793`, `:1845`, `:1977`, `:2059`). The assertion holds even when the import it names is gone:

  ```
  $ venv/bin/python -   # remove the line "from src.auth_helpers import get_current_user, owner_filter, require_privilege"
  import line removed: True
  assert "get_current_user" in source  -> True
  assert "require_privilege" in source -> True
  occurrences of require_privilege after removing the import: 10
  ```

  The same file's real assertions (`:34-36`, the eight handler names each containing
  `require_privilege(request, "can_generate_images")`) are source searches too, and its
  `GATED_IMAGE_FUNCTIONS` set (`:5-14`) omits `sharpen_image` and `smart_mask`, so two privileged
  endpoints are outside the list entirely. Measured with the module made unimportable — a plugin
  that raises from `find_spec` for `routes.gallery.gallery_routes`:

  ```
  $ PYTHONPATH=/tmp/probe BLOCK_MODULE=routes.gallery.gallery_routes \
      venv/bin/python -m pytest -q -p blockmod \
      tests/test_gallery_album_owner_scope.py tests/test_gallery_image_privileges.py
  7 passed, 1 warning in 0.40s

  $ ...same block... tests/test_gallery_image_endpoint_owner_scope.py
  ERROR tests/test_gallery_image_endpoint_owner_scope.py
  !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
  ```

  The second run is the control: a file that imports the module cannot even be collected, so the
  block is in force. The privilege gate is currently correct — `require_privilege` is the 2nd to
  14th line of each of the ten handlers — and `src/auth_helpers.require_privilege` itself is
  covered elsewhere in the run.
- **Impact:** the test named for the import cannot fail if the import is deleted, and the file's
  claimed pin on the image-generation privilege gate cannot see a behavioural regression in it (for
  example a handler that calls the helper on a branch that the caller cannot reach). It is counted
  as coverage for the gate.
- **Fix:** delete `test_gallery_routes_imports_privilege_helper` — the import is exercised by every
  handler the other test names — and drive one gated handler through `TestClient` with a user
  lacking `can_generate_images`, asserting the 403, in the same style as
  `tests/test_gallery_null_user_routes.py:14-62`.

### [FOOTGUN] `test_document_close_clears_active_route` rebinds `routes.document_routes.SessionLocal` at module scope and never restores it

- **Location:** `tests/test_document_close_clears_active_route.py:35-43`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the fixture is module-level, so it runs at collection and outlives every test:

  ```python
  # tests/test_document_close_clears_active_route.py:35-43
  _TMPDB = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
  _ENGINE = create_engine(
      f"sqlite:///{_TMPDB.name}",
      connect_args={"check_same_thread": False},
      poolclass=NullPool,
  )
  cdb.Base.metadata.create_all(_ENGINE)
  _TS = sessionmaker(bind=_ENGINE, autoflush=False, autocommit=False)
  droutes.SessionLocal = _TS  # route handlers resolve SessionLocal at call time
  ```

  Measured with a probe test that asserts the production default is intact:

  ```
  $ venv/bin/python -m pytest -q -s /tmp/probe/test_sessionlocal_leak.py     # control
  droutes.SessionLocal -> sessionmaker(… bind=Engine(sqlite:////home/lhl/github/lhl/odysseus/data/app.db) …)
  core.database.SessionLocal -> sessionmaker(… bind=Engine(sqlite:////home/lhl/github/lhl/odysseus/data/app.db) …)
  1 passed

  $ venv/bin/python -m pytest -q -s tests/test_document_close_clears_active_route.py /tmp/probe/test_sessionlocal_leak.py
  droutes.SessionLocal -> sessionmaker(… bind=Engine(sqlite:////tmp/tmpg0fpyxsi.db) …)
  core.database.SessionLocal -> sessionmaker(… bind=Engine(sqlite:///%3Amemory%3A) …)
  1 failed, 3 passed
  ```

  Every other document-route file in this set that binds the same global restores it —
  `tests/test_document_session_owner_scope.py:52-56` and `:121` save and restore,
  `tests/test_document_render_pdf_iframe.py:128` uses `monkeypatch.setattr`. The standard's
  isolation rule is explicit: "never assign at module scope" (`tests/TESTING_STANDARD.md:93`, and
  `:41` for the general rule). The temporary database file is also never unlinked.
- **Impact:** for the rest of the pytest process, any document-route test that does not bind its own
  `SessionLocal` silently reads and writes a stale, empty temporary database instead of the session
  database. Nothing fails today because the files that follow bind their own, but the suite's
  order-independence — which the standard lists as a requirement (`:112-114`) and which the
  project's CI plan intends to test with `pytest-randomly` — depends on that coincidence.
- **Fix:** move the binding into an autouse fixture using `monkeypatch.setattr(droutes,
  "SessionLocal", _TS)`, or copy the save/restore block from
  `tests/test_document_session_owner_scope.py:52-56`, and unlink the temporary database on teardown.

### [BUG] The "reset before render" assertion in `test_notes_search_reset_on_reopen_js` disables itself when the render call is absent

- **Location:** `tests/test_notes_search_reset_on_reopen_js.py:21-25`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the second assertion is a conditional expression, so it evaluates to `assert True`
  whenever the thing it looks for is missing:

  ```python
  # tests/test_notes_search_reset_on_reopen_js.py:21-25
  def test_open_panel_resets_search_query():
      body = _open_panel_body()
      assert "_searchQuery = ''" in body, body[:400]
      # reset must sit with the other open-time state resets, before render
      assert body.index("_searchQuery = ''") < body.index("_renderNotes") if "_renderNotes" in body else True
  ```

  The guard is live today — the extracted `openPanel` body is 14,754 characters and contains six
  `_renderNotes()` calls — but a rename or removal of that call turns the line into `assert True`
  rather than into a failure, and `body.index` would otherwise raise on the missing name. The
  file's docstring (issue #2919: "openPanel must reset `_searchQuery` so a reopened Notes panel
  doesn't keep filtering by a stale query") makes the ordering the substance of the test.
- **Impact:** the ordering half of the pin can silently disappear; a future edit that moves the
  reset after the first render keeps this test green while reintroducing the stale-filter bug the
  file exists for.
- **Fix:** split the assertion and fail loudly when the anchor is missing, for example
  `assert "_renderNotes" in body` followed by the ordering assertion, so an absent render call is a
  failure rather than a skipped check.
