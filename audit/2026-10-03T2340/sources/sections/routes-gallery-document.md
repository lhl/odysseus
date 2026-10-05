# routes: gallery and documents

## Overview

The gallery and document surfaces. `routes/gallery/gallery_routes.py` owns the photo library
(upload with EXIF extraction and SHA-256 de-duplication, library search and facets, albums,
favourites, AI tagging, soft delete) and the image-edit proxies (inpaint, harmonize, sharpen,
denoise, upscale, SAM mask, background removal, face enhancement); `routes/gallery/gallery_helpers.py`
holds the EXIF reader, the row serializer, the owner filter and the patch model.
`routes/document/document_routes.py` owns document CRUD and version history, the document library,
PDF import and text re-extraction, page rendering, form export and the signed-reply handoff, plus the
tidy paths; `routes/document/document_helpers.py` holds the request models, the serializers,
`_verify_doc_owner`, the upload locator and the PDF-marker ownership check.

This section covers whether each handler authenticates, scopes and confines correctly, not whether
the stores underneath are safe. Each neighbour owns one piece:

| Owner | What it owns |
| --- | --- |
| `build-install-deploy` | The request-authenticating middleware and the `/api/generated-image/{filename}` file server, both in `app.py` |
| `core-data-platform` | The `Document`, `DocumentVersion`, `GalleryAlbum`, `GalleryImage` and `Signature` models in `core/database.py` |
| `src-documents` | The upload store, the PDF form document builders and the PDF/VL processor |
| `src-security` | The upload byte caps |
| `routes-chat-session` | The gallery file cleanup that runs when sessions are deleted, in `routes/session_routes.py` |

## Coverage

**Read fully:** all six assigned files (4,548 lines).

| File | Lines |
| --- | ---: |
| `routes/gallery/gallery_routes.py` | 2,338 |
| `routes/document/document_routes.py` | 1,810 |
| `routes/document/document_helpers.py` | 243 |
| `routes/gallery/gallery_helpers.py` | 145 |
| `routes/gallery/__init__.py` | 6 |
| `routes/document/__init__.py` | 6 |

**Read partially:** the boundary code the findings rest on:

- `src/auth_helpers.py` in full, covering:
  - `get_current_user`
  - `effective_user`
  - `require_user`
  - `require_privilege`
  - `owner_filter`
  - `_auth_disabled`
- `app.py` at the `/api/generated-image/{filename}` handler (`:513-553`) and the auth-exempt lists
  (`:263-296`)
- `core/database.py` at the `Document`/`DocumentVersion`/`GalleryAlbum`/ `GalleryImage` definitions
  (`:283-383`)
- `src/upload_limits.py` in full (the gallery caps and `read_upload_limited`)
- `src/upload_handler.py` at `max_upload_size` (`:217`), `detect_content_type` (`:282-302`),
  `is_safe_file_type` (`:366-385`) and `save_upload` (`:1205-1250`)
- `src/document_processor.py` at `_process_pdf` (`:112-152`) and `analyze_image_with_vl_result` /
  `analyze_image_with_vl` (`:333-392`)
- `src/llm_core.py` at `llm_call` (`:1969-2045`) and `httpx_post_kimi_aware` (`:934-947`)
- `src/pdf_runtime.py` in full
- `src/generated_images.py` at `GENERATED_IMAGE_HEADERS` and `resolve_generated_image_path`
  (`:14-22`)
- `routes/session_routes.py` at the all-sessions delete path (`:677-731`)
- `routes/upload_routes.py` at `_promote_chat_image_to_gallery` (`:195-250`)
- `src/chat_handler.py` at `_sync_upload_vision_to_gallery` (`:33-53`)
- `routes/email_helpers.py` at `_attach_compose_uploads` / `_cleanup_compose_uploads` (`:515-551`)
- `static/js/gallery.js` at the library render (`:625-629`), the patch/delete helpers (`:190-226`),
  rotate (`:1810-1830`), the set-as-cover button (`:1843-1858`) and rename (`:1887`)
- `static/js/document.js` at the AI-fill call (`:1796`) and the compose-attachment removal
  (`:3610-3618`)

**Not read:**

- the auth middleware itself (`core/middleware.py` and `app.py`'s `AuthMiddleware`), assigned to
  `core-auth-session` and `build-install-deploy`
- the `UploadHandler` internals other than the functions named above (`src-documents`)
- the `Signature` model and the PDF form builders (`src-documents`)
- the front end beyond the regions named above
- the other `routes-*` sections that call into these modules

**Checks run:**

- the 46 suites matching `ls tests | grep -iE 'gallery|document|image'` — **182 passed**
- a request-level probe that mounts both routers in a FastAPI app with a real SQLite session factory
  (the shape `tests/test_gallery_null_user_routes.py` uses) and posts a JSON array and a JSON string
  to every raw-body endpoint, quoted in the non-object-body finding
- the same probe with a seeded album row for the three album sub-routes
- an end-to-end probe of the set-cover → delete → list-albums sequence, quoted in the album-cover
  finding
- a probe that runs the vision call `_process_pdf` makes inside a live event loop with a heartbeat
  task, quoted in the blocking-work finding
- greps for `to_thread` / `run_in_threadpool` in these two files, for `request.json()`, for
  `file_hash` readers, for `is_active = False` sites and for `import fitz`

### [PERF] PDF and image processing runs synchronously inside the async handlers

- **Location:** `routes/document/document_routes.py:275` (with `:530`, `:1227`, `:1431`, `:1554`,
  `:1693`, and `routes/gallery/gallery_routes.py:1779`, `:1827`, `:1860`, `:2019`, `:2090`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `import_pdf` is an `async def` and calls the synchronous PDF processor inline:

  ```python
  # routes/document/document_routes.py:275, inside `async def import_pdf`
  body_text = strip_pdf_content_marker(_process_pdf(pdf_path, owner=user))
  ```

  `_process_pdf` walks every page and sends every image-heavy page to the vision model through the
  synchronous `llm_call`:

  ```python
  # src/document_processor.py:112-146
  def _process_pdf(path: str, owner: str | None = None) -> str:
      ...
      for page_num, page in enumerate(reader.pages):
          ...
          if images and len(page_text) < 50:
              for img_index, img in enumerate(images[:3]):  # cap at 3 images per page
                  ...
                          ocr_text = analyze_image_with_vl(temp_img_path, owner=owner)
  ```

  ```python
  # src/document_processor.py:375
  description = llm_call(_url, _model, vl_messages, headers=_headers, timeout=120)
  ```

  and `llm_call` is a blocking `httpx.post` (`src/llm_core.py:937`) with a 120-second timeout, once
  per image. Measured by running that call shape inside a live loop with a 50 ms heartbeat task,
  against a local endpoint that sleeps one second:

  ```
  vision call returned 'page text' after 1.15s
  heartbeats (50 ms interval) during the call: 0
  ```

  No other task ran while the call was in flight. The same shape recurs in the render and image
  handlers: `page.get_pixmap(...)` at `:1227` and `:1301`, `fill_fields(...)` at `:1431`, `:1554` and
  `:1693`, and in the gallery `upsampler.enhance` (`routes/gallery/gallery_routes.py:1779`, `:1827`),
  `_load_sam_backend()` plus the SAM forward pass (`:1860`), `remove(crop)` (`:2019`) and
  `restorer.enhance(...)` (`:2090`) — a model load and a torch inference per request, on the loop.
  Neither file offloads any of it: `grep -rn 'to_thread\|run_in_threadpool' routes/gallery/
  routes/document/` returns nothing, while sibling route modules do offload (`routes/email_routes.py:2391`,
  `routes/personal_routes.py:197`, `routes/cookbook_routes.py:4048`).
- **Impact:** importing a scanned PDF freezes every other request on the instance for as long as the
  vision calls take — up to 3 per page across every page, each with a 120-second timeout, and the
  handler waits for all of them before it answers. A single AI mask, background removal, upscale or
  denoise request blocks the loop for the length of a local model inference, and each PDF page render
  blocks it for the render. The app runs a single uvicorn process — `uvicorn.run(app, host=bind_host,
  port=bind_port, log_level="info")` with no `workers=` argument (`launcher.py:149`, `app.py:1306`) —
  so "the loop" is the whole server, including streaming chat turns, while any of these run.
- **Fix:** run these calls through `await asyncio.to_thread(...)` (the `_process_pdf` calls, the
  `fill_fields`/`stamp_*`/`get_pixmap` block, and the model invocations), as the sibling route modules
  already do. The handlers are already `async def`, so the change is local; the cost is one worker
  thread per in-flight request.

### [BUG] An album keeps a cover that points at a deleted photo, and the album list renders the dead URL

- **Location:** `routes/gallery/gallery_routes.py:828-832` (with `:1149-1161`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `delete_gallery_image` soft-deletes the row and unlinks the file, but nothing clears
  `GalleryAlbum.cover_id`:

  ```python
  # routes/gallery/gallery_routes.py:1147-1161
  img_filename = img.filename
  img.is_active = False
  db.commit()
  ...
              img_path = _gallery_image_path(img_filename)
              if img_path.exists():
                  img_path.unlink()
  ```

  The album list then resolves that cover without checking `is_active`, and its fallback branch is
  only reached when `cover_id` is NULL:

  ```python
  # routes/gallery/gallery_routes.py:827-840
  cover_url = None
  if a.cover_id:
      cover_q = db.query(GalleryImage).filter(GalleryImage.id == a.cover_id)
      cover = _owner_filter(cover_q, user).first()
      if cover:
          cover_url = f"/api/generated-image/{cover.filename}"
  elif count > 0:
      ...
  ```

  Measured end to end, with an album holding two photos, the first set as cover through
  `PUT /api/gallery/albums/alb-1` (the call `static/js/gallery.js:1846-1849` makes):

  ```
  albums before delete    -> {'albums': [{'id': 'alb-1', 'name': 'Album', 'description': '', 'cover_url': '/api/generated-image/cover.png', 'count': 2, 'created_at': '2026-10-03T19:28:12.339536'}]}
  DELETE /api/gallery/img-1 -> {'status': 'deleted', 'id': 'img-1'}
  file exists after       -> False
  albums after delete     -> {'albums': [{'id': 'alb-1', 'name': 'Album', 'description': '', 'cover_url': '/api/generated-image/cover.png', 'count': 1, 'created_at': '2026-10-03T19:28:12.339536'}]}
  ```

  The front end renders that URL whenever the album still has photos —
  `const cover = (a.cover_url && a.count > 0) ? '<img src="...">' : placeholder` (`static/js/gallery.js:628`)
  — so the card shows a broken image.
- **Impact:** a user who sets a photo as an album cover and later deletes that photo gets a broken
  cover image on the Albums view, instead of the newest remaining photo in the album, until they set
  a new cover by hand. The album's `count` is correct; only the cover is stale. Re-uploading a file
  with the same name does not repair it (the URL is the deleted row's filename).
- **Fix:** in `delete_gallery_image`, clear `cover_id` on the albums that reference the row
  (`db.query(GalleryAlbum).filter(GalleryAlbum.cover_id == image_id).update({"cover_id": None})`),
  and/or add `GalleryImage.is_active == True` to the cover lookup so the `elif count > 0` fallback
  takes over.

### [BUG] The replace route leaves `file_hash` and `file_size` describing the file it replaced

- **Location:** `routes/gallery/gallery_routes.py:451-465` (with `:551-552`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `gallery_replace` writes the new bytes and refreshes only the dimensions:

  ```python
  # routes/gallery/gallery_routes.py:451-465
  content = await read_upload_limited(file, GALLERY_UPLOAD_MAX_BYTES, "Gallery replacement")
  GALLERY_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
  img_path = _gallery_image_path(img.filename)
  img_path.write_bytes(content)

  # Refresh dimensions in case the editor resized the canvas.
  # updated_at auto-bumps via TimestampMixin's onupdate hook.
  try:
      from PIL import Image
      from io import BytesIO
      with Image.open(BytesIO(content)) as new_im:
          img.width = new_im.width
          img.height = new_im.height
  except Exception:
      pass
  ```

  The sibling route that rewrites image bytes updates both fields:

  ```python
  # routes/gallery/gallery_routes.py:550-553, gallery_rotate
  img_path.write_bytes(content)
  img.file_hash = hashlib.sha256(content).hexdigest()
  img.file_size = len(content)
  img.width, img.height = rotated.size
  ```

  `file_hash` is not decorative: the upload path uses it for de-duplication
  (`routes/gallery/gallery_routes.py:377-380`), `_promote_chat_image_to_gallery` returns the *existing* row when an
  attachment's hash matches (`routes/upload_routes.py:207-217`), and
  `_sync_upload_vision_to_gallery` writes a generated caption onto the row it finds
  (`src/chat_handler.py:33-49`). `file_size` is displayed as the photo's size
  (`static/js/gallery.js:1394`). The route also does not check `is_active`, so it will re-create the
  bytes on disk for a row that was already deleted (its file unlinked, its row inactive and absent
  from every listing).
- **Impact:** after a replace, the gallery shows the old file size and the stored hash identifies
  content that is no longer in the file. A later chat attachment of the *old* bytes matches the
  replaced row and is treated as that row (`routes/upload_routes.py:216-217` returns its id), so the chat
  bubble and the gallery row disagree about which image the upload is; the caption-sync path can
  write the vision caption for the new upload onto the replaced row. Replacing a deleted photo's
  bytes silently restores an unreferenced file on disk.
- **Fix:** recompute `img.file_hash = hashlib.sha256(content).hexdigest()` and
  `img.file_size = len(content)` in `gallery_replace`, and reject a replace for a row whose
  `is_active` is false.

### [ERROR-HANDLING] Seventeen raw-body endpoints answer 500 to a JSON array or string

- **Location:** `routes/gallery/gallery_routes.py:484` (with `:513`, `:855`, `:1002`, `:1267`,
  `:1525`, `:1720`, `:1744`, `:1795`, `:1847`, `:1979`, `:2061`, `:2147`, `:2181`, `:2199`) and
  `routes/document/document_routes.py:570`, `:1255`
- **Severity:** low
- **Disposition:** next
- **Evidence:** every one of these handlers calls `await request.json()` and then treats the result as
  a mapping, for example:

  ```python
  # routes/gallery/gallery_routes.py:483-484
  data = await request.json()
  new_name = (data.get("name") or "").strip()
  ```

  ```python
  # routes/document/document_routes.py:565-570 — the try/except covers the parse, not the shape
  try:
      data = await request.json()
  except Exception as e:
      logger.warning("Failed to parse export request body, defaulting to empty", exc_info=e)
      data = {}
  ids = data.get("ids") or []
  ```

  Measured by mounting both routers in a FastAPI app with a real SQLite session factory and posting
  `[1]` and `"x"` as `application/json` (a seeded album row for the three album sub-routes, and a
  stubbed `fitz` for the AI-fill endpoint, whose `import fitz` runs first — see the finding below):

  ```
  body=[1]  body="x"   handler                              route
    500      500   gallery_rename                         POST /api/gallery/img-1/rename
    500      500   gallery_rotate                         POST /api/gallery/img-1/rotate
    500      500   create_album                           POST /api/gallery/albums
    500      500   update_album                           PUT  /api/gallery/albums/alb-1
    500      500   add_to_album                           POST /api/gallery/albums/alb-1/add
    500      500   remove_from_album                      POST /api/gallery/albums/alb-1/remove
    500      500   gallery_download_zip                   POST /api/gallery/download-zip
    500      500   sharpen_image                          POST /api/image/sharpen
    500      500   denoise_image                          POST /api/image/denoise
    500      500   upscale_image_local                    POST /api/image/upscale-local
    500      500   smart_mask                             POST /api/image/mask
    500      500   remove_background                      POST /api/image/remove-bg
    500      500   enhance_face                           POST /api/image/enhance-face
    500      500   harmonize_image                        POST /api/image/harmonize
    500      500   inpaint_proxy                          POST /api/image/inpaint
    500      500   documents_export_zip                   POST /api/documents/export-zip
    500      500   ai_fill_annotations                    POST /api/document/doc-1/ai-fill-annotations
    422      422   patch_gallery_image (GalleryPatch)     PATCH /api/gallery/img-1
    422      422   update_document (DocumentUpdate)       PUT  /api/document/doc-1
  ```

  With server exceptions raised, sixteen of the seventeen raise
  `AttributeError: 'list' object has no attribute 'get'`; `inpaint_proxy` raises
  `TypeError: pop expected at most 1 argument, got 2` (`body.pop("_endpoint", "")`,
  `routes/gallery/gallery_routes.py:1267`). The last two rows are the contrast: the
  endpoints that take a Pydantic model answer 422 for the same bodies. This is the same class
  reported in `routes-rest-auth-admin.md`; it recurs here. The two handlers above at least guard the
  parse (`routes/gallery/gallery_routes.py:998-1001`, `routes/document/document_routes.py:565-569`),
  but a JSON array parses cleanly and then fails on `.get`; the repository already has the shape guard
  the fix needs (`routes/backup_routes.py:73`).
- **Impact:** an authenticated API client — a script or an integration — that posts a JSON array or
  string to one of these endpoints gets a 500 and an unhandled traceback in the server log where the
  section's typed endpoints answer 422. No data is written and no privilege is crossed; the cost is a
  misclassified failure and log noise. The endpoints are not auth-exempt (`app.py:264-296` lists none
  of them), so only an authenticated caller can reach the path.
- **Fix:** add the same `if not isinstance(body, dict): raise HTTPException(400, "Expected a JSON
  object")` guard the backup import uses, or convert these bodies to Pydantic models the way the
  sibling `PATCH /api/gallery/{id}` and `PUT /api/document/{id}` already are.

### [ERROR-HANDLING] The AI-fill endpoint imports PyMuPDF unguarded, so a missing optional dependency is a 500 instead of the 503 its siblings return

- **Location:** `routes/document/document_routes.py:1249` (with `:96-102`, `:1151`, `:1220`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `ai_fill_annotations` imports the optional PDF library directly:

  ```python
  # routes/document/document_routes.py:1247-1255
  import base64
  import json
  import fitz
  from src.pdf_form_doc import find_source_upload_id
  ...
  body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
  ```

  Every other PDF handler in the same file goes through the helper that turns the missing dependency
  into a user-facing setup hint:

  ```python
  # routes/document/document_routes.py:96-102
  def _load_pdf_viewer_fitz():
      from src.pdf_runtime import load_pymupdf_for_pdf_viewer

      try:
          return load_pymupdf_for_pdf_viewer()
      except RuntimeError as exc:
          raise HTTPException(503, str(exc)) from exc
  ```

  called at `:1151` (`render_pages`) and `:1220` (`render_page_png`), and again in `render_pdf`.
  PyMuPDF is an optional dependency (`requirements-optional.txt:35`, under the AGPL note), and it is
  absent in this checkout:

  ```
  $ venv/bin/python -c "import fitz"
  ModuleNotFoundError: No module named 'fitz'

  $ POST /api/document/doc-1/ai-fill-annotations   body=[1]
  500   ModuleNotFoundError: No module named 'fitz'
  ```

  The front end calls this endpoint from the PDF editor (`static/js/document.js:1796`).
- **Impact:** on an install that did not take the optional PDF dependencies — a supported
  configuration, since the rest of the PDF surface degrades to a 503 with the install command — the
  editor's AI-fill button returns a bare 500 and a traceback instead of the same actionable message
  its sibling endpoints give. The import runs before the document lookup, so every call fails the same
  way regardless of the document.
- **Fix:** replace `import fitz` with `fitz = _load_pdf_viewer_fitz()`, matching `render_pages` and
  `render_page_png`.
