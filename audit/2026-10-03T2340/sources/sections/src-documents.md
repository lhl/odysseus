# src: documents, uploads, PDF and office

## Overview

The document pipeline behind a chat attachment and the upload store behind it: the
`UploadHandler` (rate limit, size/type checks, dedup, the `uploads.json` index, reservation
against cleanup, owner rename, retention sweep), the persistence form for message content and
attachment references, the PDF/office/text extraction `build_user_content` runs, the auto-created
`Document` rows for attached PDFs and Office files, the optional-dependency shims for
markitdown and PyMuPDF, the AcroForm helpers (field extraction, value fill, signature and
annotation stamping), and the generated-image filename resolver.

The boundary: the upload, document-library and gallery routes that call these helpers are
`routes-rest-media-files` and `routes-gallery-document`; the `/api/generated-image/{filename}`
handler that serves the file this section resolves is in `app.py` (`build-install-deploy`); the
byte caps are `src/upload_limits.py` (`src-security`); `Document`/`DocumentVersion` and the
`chat_messages` FTS table are `core-data-platform`; the session write that calls
`persistable_message_content` is `core-auth-session`/`src-chat-session`; the agent tool that
reaches `run_document_tidy` and the dispatcher around it are `src-agent-tools` and
`src-tools-parse-exec`; the scheduler that triggers the tidy action is
`src-research-scheduling`. This section covers what these helpers do with a caller-supplied
filename, upload id or document body, and what they do when a file or an optional dependency is
missing — not whether the routes that call them authenticate or scope correctly.

## Coverage

**Read fully:** all ten assigned files (3,429 lines).

| File | Lines |
| --- | ---: |
| `src/upload_handler.py` | 1,393 |
| `src/document_processor.py` | 607 |
| `src/pdf_form_doc.py` | 441 |
| `src/pdf_forms.py` | 401 |
| `src/document_actions.py` | 197 |
| `src/attachment_refs.py` | 164 |
| `src/markitdown_runtime.py` | 106 |
| `src/office_doc.py` | 73 |
| `src/generated_images.py` | 32 |
| `src/pdf_runtime.py` | 15 |

Line references are to the working tree at `2992bf6d368a`; `git status --porcelain` showed only the
untracked `audit/` directory.

**Read partially:** the boundary code the findings rest on:

- `routes/document/document_routes.py` at the PDF import (`:225-300`), the tidy route (`:852-965`),
  the render/export/AI-fill handlers (`:1380-1440`, `:1491-1625`) and the unguarded `import fitz`
  (`:1247-1255`)
- `routes/document/document_helpers.py` at `_verify_doc_owner`, `_owner_session_filter`,
  `_resolve_user_upload_path`, `_locate_upload` and `_assert_pdf_marker_upload_owned` (`:1-215`)
- `routes/upload_routes.py` at the download handler (`:360-425`) and the offloaded cleanup
  (`:325-327`)
- `app.py` at `/api/generated-image/{filename}` (`:513-553`), the exception handlers (`:616-633`)
  and the startup seeding of housekeeping tasks (`:1160-1180`)
- `core/session_manager.py` at the message persist (`:265-285`)
- `core/database.py` at `_scrub_legacy_chat_message_fts_media` (`:2264-2292`)
- `src/agent_tools/document_tools.py` at the active-document globals and owner query helpers
  (`:1-80`), the read/update/suggest targets (`:470-500`, `:705-735`) and the `manage_documents`
  dispatch (`:763-892`)
- `src/tool_execution.py` at `_direct_fallback` (`:765-780`), `_document_tool_dispatch`
  (`:783-802`), `execute_tool_block` (`:810-965`) and the `manage_documents` branch (`:1133-1144`)
- `src/agent_loop.py` at the SSE tool wrapper (`:5785-5825`)
- `routes/chat_routes.py` at the active-document fallback (`:1445-1475`) and the stream handler's
  `try`/`except`/`finally` (`:2309`, `:2336`, `:2551`, `:2590-2600`)
- `src/builtin_actions.py` at `TaskNoop` (`:412-422`) and `action_tidy_documents` (`:453-461`)
- `src/task_scheduler.py` at `HOUSEKEEPING_DEFAULTS` (`:253`) and the seeding/status block
  (`:2474-2507`)
- `src/tool_security.py` at `owner_is_admin_or_single_user` and `blocked_tools_for_owner`
  (`:237-271`)
- `src/owner_identity.py:17-25`
- `src/upload_limits.py` in full (72 lines — the chat cap this handler reads)
- `requirements-optional.txt` at the PyMuPDF and markitdown entries (`:30-46`)

**Not read:**

- the rest of `routes/document/document_routes.py`, `routes/chat_routes.py`, `src/agent_loop.py`,
  `src/tool_execution.py`, `src/agent_tools/document_tools.py`, `core/session_manager.py` and
  `src/task_scheduler.py` (each assigned to another section)
- the front end that renders attachments, documents and the PDF editor
- the RAG indexer's use of markitdown (`src/personal_docs.py`, assigned elsewhere)
- the other `routes-*` and `src-*` sections
- every path that needs PyMuPDF, which is not installed in this checkout (`venv/bin/python -c
  "import fitz"` → `ModuleNotFoundError`) — `extract_fields`, `fill_fields`, `stamp_signatures` and
  `stamp_annotations` were read, not run

The library's own tests were executed, not read end to end.

**Checks run:**

- `git log --oneline -1` / `git status --porcelain` (clean apart from `audit/`), the
  optional-dependency imports (`markitdown`, `fitz`, `magic`, `pypdf`, `PIL`, `charset_normalizer`),
  and eleven throwaway probe scripts under `/tmp` (not part of the target tree)
- the ones quoted below are: a crafted `.docx` with the zip encryption bit set, one with compression
  method 9, and one with ten zeroed bytes in its deflate stream, through `_extract_docx_native`,
  `convert_to_markdown` and `build_user_content`
- the same `build_user_content` call on a healthy `.docx` as a control
- the real dispatcher (`execute_tool_block` with a `manage_documents` `tidy` block, and
  `action=list` as the control) against a temp app DB with nothing to tidy, with
  `AUTH_ENABLED=false` so the admin gate does not short-circuit
- `run_document_tidy` against a temp app DB holding an archived junk document, an active document
  and an archived copy of it
- the same function over 500 documents (2.9 MB) inside a live event loop with a 10 ms ticker
- `_process_pdf` on six malformed or hostile PDFs
- the `DATA_URL_RE` match set over six data-URL shapes

Also greps for the callers of `resolve_upload`, `reserve_upload`, `get_upload_info`,
`persistable_message_content`, `strip_inline_data_urls`, `build_user_content`, `run_document_tidy`,
`set_active_document` and `TaskNoop`, and an AST scan for functions in these ten files with no
reference outside their file.

The required discovery command, `ls tests | grep -iE
'upload|document|markitdown|pdf|office|attachment|generated_image'`, selected 48 suites. Running
`PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q -p no:cacheprovider` with those paths
produced **217 passed, 2 skipped** in 3.67s. The skips are `tests/test_markitdown_runtime.py:64`
(`could not import 'markitdown'`) and `tests/test_upload_content_detection_magic.py:41`
(`libmagic/python-magic not installed in this environment`). The only warning is the existing
SQLAlchemy `declarative_base()` deprecation. Every cited line was reopened before writing.

### [BUG] A tidy run that finds nothing raises `TaskNoop` out of the agent tool dispatcher instead of returning a result

- **Location:** `src/document_actions.py:189-192` (with `src/agent_tools/document_tools.py:883-892`, `src/tool_execution.py:1133-1145`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the function ends a no-op run with a sentinel meant for the scheduler:

  ```python
  # src/document_actions.py:189-192
          if deleted == 0:
              # Use sentinel so the scheduler can drop the run row entirely.
              from src.builtin_actions import TaskNoop
              raise TaskNoop(f"scanned {len(docs)} document(s), no junk")
  ```

  `TaskNoop` inherits from `BaseException` on purpose, so `except Exception` wrappers do not
  catch it (`src/builtin_actions.py:412-421`), and the tool path that awaits the same function is
  wrapped only in `except Exception`:

  ```python
  # src/agent_tools/document_tools.py:883-892
              elif action == "tidy":
                  from src.document_actions import run_document_tidy
                  result = await run_document_tidy(owner or "")
                  return {"response": result, "exit_code": 0}
  ...
          except Exception as e:
              logger.error(f"manage_documents error: {e}")
              return {"error": str(e), "exit_code": 1}
  ```

  Measured with a temp app DB holding one ordinary document and no junk, through the real
  dispatcher (`AUTH_ENABLED=false` so the non-admin tool gate does not answer first):

  ```
  $ AUTH_ENABLED=false venv/bin/python /tmp/probe_tidy_dispatcher.py
  action=tidy: execute_tool_block RAISED TaskNoop: scanned 1 document(s), no junk
  action=list: returned desc='manage_documents: {"action": "list"}' result={'response': 'Found 1 document(s), ...'}
  ```

  The same call on the handler alone (`/tmp/probe_tidy_tasknoop.py`) gives
  `handler RAISED TaskNoop (BaseException subclass: True)`. Nothing above the handler absorbs it:
  `manage_documents` is routed through `_document_tool_dispatch`, which has no `try` of its own
  (`src/tool_execution.py:783-802`), while the sibling fallback catches `Exception` only (`:777`);
  the SSE tool wrapper's `_run_tool` has a bare `finally` and no handler
  (`src/agent_loop.py:5791-5805`), so `desc, result = await _tool_task` at `:5818` re-raises, and
  the `try` block that wraps the agent loop in the stream handler (opened at `:2309`) is closed
  only by `except (asyncio.CancelledError, GeneratorExit)` (`routes/chat_routes.py:2551`) and a
  bare `finally` at `:2590`.
- **Impact:** when the agent runs `manage_documents action=tidy` against a library with nothing to
  delete — the common outcome, since the junk rules are conservative — the tool never returns a
  result and the exception leaves the tool layer. The model is not told "nothing to tidy"; the
  `/api/chat_stream` turn ends on an unhandled `BaseException` with no terminal event, instead of
  a tool result the loop can continue from. The scheduler path is unaffected and behaves as
  documented, which is why the sentinel exists. The raise was verified at the handler and at
  `execute_tool_block`; the aborted-stream end state is read from the handlers named above, not
  observed in a full chat turn.
- **Fix:** keep the sentinel for the scheduler and return normally for the tool. Either raise it
  in the scheduler-facing wrapper (`action_tidy_documents`, `src/builtin_actions.py:453-461`) when
  the returned string says nothing was removed, or catch `TaskNoop` around the call in
  `document_tools.py` and answer `{"response": result, "exit_code": 0}`.

### [ERROR-HANDLING] The native `.docx` fallback raises on a damaged or password-protected file instead of degrading

- **Location:** `src/markitdown_runtime.py:57-61` (the `except` clause), with the fallback call at `:85-97`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the fallback extractor absorbs only three failure modes of `ZipFile.read`:

  ```python
  # src/markitdown_runtime.py:57-61, inside _extract_docx_native
      try:
          with zipfile.ZipFile(path) as z:
              xml_bytes = z.read("word/document.xml")
      except (zipfile.BadZipFile, KeyError, OSError):
          return None
  ```

  A corrupt deflate stream raises `zlib.error`, an encrypted entry raises `RuntimeError`, and an
  unsupported compression method raises `NotImplementedError`; none is in that tuple, and
  `convert_to_markdown`'s own `except Exception` wraps only the markitdown call (`:98-106`), not
  the fallback at `:89`. Measured on crafted files:

  ```
  $ venv/bin/python /tmp/probe_docx_encrypted.py
  baseline (plain docx): 'hello'
  encrypted: RAISED RuntimeError: File 'word/document.xml' is encrypted, password required for extraction
  encrypted: convert_to_markdown RAISED RuntimeError: File 'word/document.xml' is encrypted, password required for extraction
  deflate64: RAISED NotImplementedError: That compression method is not supported
  deflate64: convert_to_markdown RAISED NotImplementedError: That compression method is not supported

  $ venv/bin/python /tmp/probe_docx_trunc.py
  trunc 0.30 (72B): returned None
  corrupt: RAISED error: Error -3 while decompressing data: invalid bit length repeat
  ```

  (`corrupt` is a valid `.docx` with ten bytes of its deflate stream zeroed; the truncated copies
  are the handled `BadZipFile` case and return `None`.) The same input through the chat
  attachment builder, with a healthy file as the control:

  ```
  $ venv/bin/python /tmp/probe_build_user_content_corrupt.py
  corrupt deflate: build_user_content RAISED error: Error -3 while decompressing data: invalid bit length repeat
  encrypted: build_user_content RAISED RuntimeError: File 'word/document.xml' is encrypted, password required for extraction
  healthy: returned 'summarize this\n\n[Document content — probe_min]:\nhello'
  ```

  markitdown is absent in this checkout, which is a supported configuration:
  `requirements-optional.txt:37-41` documents it as optional, with the Office formats falling
  back to a friendly install banner rather than extracting, and the module states the contract
  twice — "When absent, callers degrade gracefully (chat shows a hint; the RAG indexer skips the
  file)" (`:5-8`) and "Returns the extracted Markdown, or ``None`` if markitdown is unavailable
  or the conversion fails — callers degrade gracefully rather than erroring" (`:78-79`). Nothing
  between the helper and the route catches it: `_process_office_document` calls
  `convert_to_markdown` unguarded (`src/document_processor.py:226`), `build_user_content` calls
  that unguarded (`:575-582`), and the app's exception handlers cover four custom types, none of
  them `zlib.error` (`app.py:616-633`).
- **Impact:** on an install without markitdown, a user who attaches a `.docx` whose deflate stream
  is damaged, or a zip-encrypted one, gets an unhandled exception on the request thread instead of
  the "[Attached document … no extractable text found]" banner the fallback exists to produce.
  Only the uploader's own turn is affected, and only when the file is damaged; the truncation and
  wrong-container cases already degrade. `tests/test_markitdown_runtime.py` covers the
  missing-dependency path and a markitdown converter that raises (`:36-45`), but not a corrupt
  file on the native path.
- **Fix:** widen the clause to the family the extractor is meant to absorb — add `RuntimeError`,
  `NotImplementedError` and `zlib.error` to the tuple (or `except Exception`, in a function whose
  contract is "return `None` on failure") — and wrap the `_extract_docx_native` call in
  `convert_to_markdown` the way the markitdown call is wrapped.

### [DUP] The REST tidy route reimplements the scheduled tidy, and the two delete different documents

- **Location:** `routes/document/document_routes.py:852-871` (the inline copy) against `src/document_actions.py:53-195`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the route keeps its own copy of the rules and imports only the title set, with a
  comment that claims parity:

  ```python
  # routes/document/document_routes.py:869-872
              # Same junk-detection logic as the scheduled tidy_documents
              # action (src/document_actions.py). Keep these two in sync.
              import re as _re
              from src.document_actions import _JUNK_TITLES
  ```

  The two disagree in three visible ways. The route restricts the candidate set to live,
  non-archived documents, while the shared helper queries every document for the owner:

  ```python
  # routes/document/document_routes.py:858-863
              q = (
                  db.query(Document)
                  .outerjoin(DbSession, Document.session_id == DbSession.id)
                  .filter(Document.is_active == True)
                  .filter((Document.archived == False) | (Document.archived.is_(None)))
              )
  ```

  ```python
  # src/document_actions.py:68-74
          if owner:
              docs = db.query(Document).filter(Document.owner == owner).all()
          else:
              docs = db.query(Document).all()
  ```

  The route also has an email-stub rule and a title-repair pass the helper lacks
  (`routes/document/document_routes.py:902-935`), and the helper has the duplicate-content pass
  the route lacks (`src/document_actions.py:148-184`). Measured on a temp app DB holding an
  archived document titled `asdf`, an active document, and an archived copy of it:

  ```
  $ venv/bin/python /tmp/probe_tidy_archived.py
  tidy result: Removed 2 of 3: asdf (junk title 'asdf'); Report (+1 duplicate copies) · 1 kept
  survivors: [('dup-archived', 'Report', True, True)]
  ```

  The helper hard-deleted the archived `asdf` document the button leaves alone, and kept the
  archived copy of the duplicate pair while deleting the active one.
- **Impact:** the manual tidy button and the automatic `tidy_documents` action delete different
  sets. The action is event-triggered after five document creations and seeded active by default
  (`src/task_scheduler.py:253` has no `ship_paused`, and `:2502` sets `status="paused" if
  ships_paused else "active"`), so a user can lose an archived document, or the active copy of a
  duplicate pair, without ever pressing the button. Every row the helper deletes is junk or a duplicate by
  its own rules, so the loss is bounded — but which copy survives is decided by `updated_at`, not
  by `archived`, so the archived member can be the survivor.
- **Fix:** have the route call `run_document_tidy` (it can keep the title-repair counting), or
  lift the rule sets into one function with an explicit parameter for the archived/inactive
  policy.

### [BUG] `strip_inline_data_urls` leaves data URLs that carry a parameter before `;base64,` in persisted history

- **Location:** `src/attachment_refs.py:15-18`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the pattern's media-type run stops at the first `;`, so a data URL with any
  parameter before `;base64,` never matches:

  ```python
  # src/attachment_refs.py:15-18
  DATA_URL_RE = re.compile(
      r"data:[^;,\s\"']+;base64,[A-Za-z0-9+/=]+",
      re.IGNORECASE,
  )
  ```

  Measured on six shapes (each with a 200-character payload, output length in characters):

  ```
  $ venv/bin/python /tmp/probe_data_url_params.py
  plain              in= 226 out=  49 stripped=True
  charset param      in= 241 out= 241 stripped=False
  svg+xml            in= 230 out=  49 stripped=True
  name param         in= 248 out= 248 stripped=False
  percent-encoded    in= 229 out=  52 stripped=True
  wrapped newline    in= 227 out= 150 stripped=True
  ```

  `charset param` is `data:text/plain;charset=utf-8;base64,…`, `name param` is
  `data:application/pdf;name=report.pdf;base64,…`; `wrapped newline` is a base64 body split across
  a newline, where only the first segment is replaced. This helper is the only thing standing
  between provider media and the database on both write paths: `persistable_message_content` runs
  on every message that reaches `chat_messages` (`core/session_manager.py:274-276`), and the
  legacy FTS scrub selects rows by `instr(content, ';base64,') > 0` and re-indexes them through
  `search_index_text`, the same regex (`core/database.py:2264-2292`) — so a parameterised payload
  is not cleaned up by the scrub either. Both call sites state the opposite intent
  (`src/attachment_refs.py:1-6`, `core/session_manager.py:274-275`).
- **Impact:** a message whose text contains a data URL with a parameter — the common shape is
  `data:text/plain;charset=utf-8;base64,…` — is stored in `chat_messages.content` and indexed in
  `chat_messages_fts` at full base64 size, and is replayed to the model on a later turn. That is
  exactly the duplication the module exists to prevent. Reachability is limited to a parameterised
  data URL arriving in message text, and the payload is the caller's own data; the stored bytes
  and index entries are the cost.
- **Fix:** allow parameter segments before the marker, for example
  `r"data:[^,\s\"']*;base64,[A-Za-z0-9+/=]+"` (or `(?:[^;,\s\"']*;)*base64,`), and let the base64
  run span whitespace if wrapped payloads are in scope.
