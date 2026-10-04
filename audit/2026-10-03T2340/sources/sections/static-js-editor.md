# static: image editor

## Overview

The 53 modules under `static/js/editor/` that make up the gallery image editor: the AI tool
surface (`ai-inpaint.js`, `ai-rembg.js`, `ai-models.js`, `ai-tool-runner.js`, `ai-tools-misc.js`),
the canvas core (`canvas-coords.js`, `canvas-events.js`, `canvas-transforms.js`,
`clipboard-and-drop.js`, `checkerboard.js`, `composite-helpers.js`, `mask-utils.js`,
`stroke-pipeline.js`, `snap.js`, `state.js`), the tools (`tools/`), the FX/pixel pipeline
(`fx/`, `filters/`, `layer-helpers.js`, `layer-panel.js`), and the topbar/panel build and wiring
modules (`build/`, `wire-*.js`, `keyboard-shortcuts.js`, `slider-ux.js`).

The boundary: the orchestrator that imports and wires every one of these modules —
`static/js/galleryEditor.js` (`_buildEditor`, `composite`, `_saveState`/`_snapshotState`,
`createLayer`, `closeEditor`, `openEditor`) — is assigned to `static-js-documents-email` together with
`static/js/gallery.js`, so it is read here only as evidence and its own defects are not restated.
The server side of every AI call these modules make (`routes/gallery/gallery_routes.py`:
`/api/image/inpaint`, `/api/image/harmonize`, `/api/image/remove-bg`, `/api/image/upscale-local`,
`/api/image/sharpen`, `/api/gallery/style-transfer`) belongs to `routes-gallery-document`; this
section covers what the client sends and what it does with what comes back, not how the server
validates or executes it. `static-js-rest` owns `static/js/modelSort.js`, which `ai-models.js`
imports. Findings below are located in the editor modules even where the visible symptom only
appears through `galleryEditor.js`.

## Coverage

Line numbers refer to the reviewed commit `2992bf6d368a`. `git diff --stat 2992bf6d368a HEAD --
static/js/editor/` is empty, so every citation also resolves in the working tree.

**Read fully:** all 53 assigned files (9,045 lines) — `find static/js/editor -type f | wc -l` = 53,
all of them `.js`, and the 53 match the section's `paths` list exactly.

| Area | Files | Lines |
| --- | ---: | ---: |
| `ai-*.js` (inpaint, rembg, models, tool-runner, tools-misc) | 5 | 1,246 |
| canvas core + `tools/` | 22 | 2,899 |
| `fx/`, `filters/`, layer/mask helpers | 9 | 2,042 |
| `build/`, `wire-*.js`, panels, keyboard/slider | 17 | 2,858 |

Largest single files: `fx/adj-popup.js` (677), `layer-panel.js` (601), `build/controls.js` (401),
`tools/transform-session.js` (381), `ai-inpaint.js` (380).

**Read partially** — boundary files, read only where a finding or a reachability claim rests on
them, none of them assigned to this section:

- `static/js/galleryEditor.js` at `_getSelectedAIEndpoint` (`:230-244`), `composite` (`:831-870`),
  `_snapshotState`/`_saveState` (`:967-1050`), `_ensureActiveMaskLayer` (`:653-672`),
  `_wandToMask` (`:2231-2262`), `_buildEditor`'s wiring block (`:2890-3620`),
  `_registerDocClickAway` (`:166-169`), the `ge-save` click handler (`:3274-3280`),
  `_wireInpaintPopoverWindow` (`:2844-2870`), `_promptCanvasSize` (`:3931-3945`),
  `openEditor`/`closeEditor` (`:4068-4375`)
- `static/js/platform.js` at `isAltGrEvent` (`:40-47`), for the keyboard-shortcut guard
- `routes/gallery/gallery_routes.py` at the `_endpoint` handling of `inpaint_proxy` (`:1267-1300`),
  `harmonize_image` (`:1529-1565`), `sharpen_image` (`:1716-1734`), `upscale_image_local`
  (`:1792-1832`), `remove_background` (`:1963-2050`), `gallery_style_transfer` (`:596-640`)
- `static/style.css` at `.ge-inpaint-popover-head` (`:29585`), `.ge-canvas-size` (`:30107`), and the
  `.ge-edge-menu` / `.ge-resize-menu` rules

**Not read:** nothing in the slice. No vendored, minified or generated file is assigned here.

**Checks run** (all commands run from the repository root; probes live in `/tmp`, nothing was
written inside the repository):

- `venv/bin/python -m pytest -q tests/test_canvas_coords_empty_touches_js.py
  tests/test_snap_other_layers_nonarray_js.py tests/test_harmonize_masks_invalid_layers_js.py
  tests/test_keybind_altgr_js.py tests/test_editor_draft_payload.py
  tests/test_spinner_stops_when_never_attached_js.py tests/test_gallery_endpoint_ssrf.py
  tests/test_gallery_endpoint_hardening.py tests/test_gallery_endpoint_matching.py
  tests/test_gallery_image_endpoint_owner_scope.py tests/test_gallery_result_image_ssrf.py
  tests/test_gallery_model_input_device.py tests/test_gallery_image_privileges.py`
  → `61 passed, 1 warning in 1.59s`. The first three cover `canvas-coords.js`, `snap.js` and
  `harmonize-masks.js` directly (they drive the real modules through `node --input-type=module`);
  `test_keybind_altgr_js.py` pins the `isAltGrEvent` guard that `keyboard-shortcuts.js` calls; the
  rest pin the server side of the AI endpoints the runner posts to.
- `node /tmp/probe-keydown.mjs` — a stub-`document` harness that calls `wireKeyboardShortcuts()`
  three times (three editor opens) and then dispatches one Ctrl+Z through every registered
  listener. Output: `document keydown listeners after 3 editor opens: 3` /
  `undo() calls produced by one Ctrl+Z press: 3`.
- `node /tmp/probe-adjcache.mjs` — imports the real `fx/pixel-pass.js` with a stub canvas and calls
  `renderLayerWithAdjLayers()` twice, replacing `layer.canvas` in between. Output:
  `cache returned the pre-stroke render: true`.
- `node -e` counting the checkerboard loop for four document sizes (see the PERF finding), and
  `node -e` reproducing the `::` split for an IPv6 base URL (see the last finding).
- Dedup sweep: `grep -rn "js/editor" audit/2026-10-03T2340/sources/sections/` matches only this
  section's own path list, and no section mentions `_adjFinal`, `checkerboard`, `ge-edge-menu`,
  `ge-wand-rembg`, `filter-string` or `_getSelectedAIEndpoint`, so none of the findings below is a
  restatement. `static-js-research-memory-rag.md:458` already reports the "document-level listener
  registered per render and never removed" class in `static/js/memory.js`; the accumulation finding
  here is a different call site and is cross-referenced rather than repeated.

### [BUG] A layer's adjustment cache is keyed only by the adjustment stack, so strokes and pixel edits on that layer never render

- **Location:** `static/js/editor/fx/pixel-pass.js:225`
- **Severity:** medium
- **Disposition:** fix-now
- **Evidence:** `composite()` draws every visible layer through
  `_renderLayerWithAdjLayers(layer)` (`static/js/galleryEditor.js:843`). That function memoises its
  output and keys the cache on the adjustment stack only:

  ```js
  // static/js/editor/fx/pixel-pass.js:222-225
  const sig = stack.map(a => `${a.id}:${a.visible?1:0}:${a.opacity}:${a.type}:${JSON.stringify(a.params)}`).join('|') +
    (staged ? `|S:${staged.type}:${JSON.stringify(staged.params)}` : '') +
    (editingId ? `|E:${editingId}` : '');
  if (layer._adjFinal && layer._adjFinalKey === sig) return layer._adjFinal;
  ```

  `sig` contains no reference to the layer's pixels, and `layer._adjFinal` is a *separate* canvas
  produced by `applyAdjustment` (`:246`), not a live view of `layer.canvas`. The pixel-writing
  paths never clear the key: `stroke-pipeline.js:153` (`ctx.stroke()`) → `:158` (`composite()`) for
  brush/eraser/inpaint/clone, `mask-utils.js:64-83` (`applyInpaintFeather`), `ai-rembg.js:125-129`
  (`rembgApplyEdgeNow`, the live feather/grow tuner), `ai-tools-misc.js:80-90` (canvas upscale).
  Only `canvas-transforms.js:73-74` and `:120-121` (rotate/flip), the FX popup
  (`fx/adj-popup.js:262`, `:416`, `:429`, `:561`) and `layer-panel.js:411-456` clear it — which is
  why rotation and FX edits refresh correctly while painting does not. `_saveState`, called at the
  start of every stroke (`tools/stroke.js:90`), only pushes an undo snapshot; it does not touch
  `_adjFinalKey`. Probe (`node /tmp/probe-adjcache.mjs`, real module, stub canvas):

  ```
  render #1 drew: canvas | _adjFinalKey = "adj-1:1:1:brightness-contrast:{\"brightness\":1.5,\"contrast\":1}"
  render #2 drew: canvas
  cache returned the pre-stroke render: true
  ```

  Render #2 returned the identical canvas object after `layer.canvas` was replaced, i.e. the cache
  hit and the new pixels were ignored.
- **Impact:** on any layer that carries an FX adjustment sub-layer (Brightness/Contrast,
  Hue/Saturation, Levels, Color Balance — i.e. after one Apply from the layer's FX button), every
  subsequent brush stroke, eraser stroke, clone stamp, inpaint feather tweak or upscale is written
  into `layer.canvas` but never appears on the canvas. The user paints, sees nothing, and may paint
  again over the same spot. The stale render is also what `exportPNG`/`exportToGallery` flatten
  (`static/js/galleryEditor.js:3622`, `:3680` → `flatten()` at `:3586`, which draws
  `_renderLayerWithAdjLayers(layer)` at `:3595`), so the edit can be missing from the saved image as
  well. It self-heals only when the adjustment stack changes (another Apply, a toggle of the
  sub-row eye, rotate/flip, undo).
- **Fix:** make the cache key depend on the pixels as well as the stack — bump a per-layer revision
  counter in every path that writes `layer.ctx`/`layer.canvas` and append it to `sig`; or clear
  `layer._adjFinalKey` (and `layer._adjCacheKey` for the legacy pixel-pass path) in
  `stroke-pipeline.js` `strokeTo`/`cloneStrokeTo` and the other pixel writers, the way
  `canvas-transforms.js` already does.

### [BUG] Rotate, flip and upscale do not transform mask sub-layers, and rotate/upscale clear the active mask

- **Location:** `static/js/editor/canvas-transforms.js:84`
- **Severity:** medium
- **Disposition:** fix-now
- **Evidence:** `rotateAll` resizes the *active* mask canvas and never redraws it:

  ```js
  // static/js/editor/canvas-transforms.js:83-87
  if (state.maskCanvas) {
    state.maskCanvas.width = newW;
    state.maskCanvas.height = newH;
  }
  ```

  Assigning `canvas.width`/`height` resets the bitmap, so this both discards the pixels the user
  painted and leaves every *other* mask sub-layer at the pre-rotation dimensions (the loop above at
  `:45-79` only walks `state.layers[].canvas`). `flipAll` (`:103-130`) never touches masks at all,
  so after a horizontal flip the mask bitmap still covers the pre-flip region while the image
  content underneath it has moved. `state.maskCanvas` is a live mask sub-layer's canvas — it is
  assigned from `mask.canvas` at `layer-panel.js:322`, `layer-panel.js:564` and
  `tools/stroke.js:76-83` — so the clearing is user-visible data loss, not scratch space. The two
  upscale paths repeat the pattern: `ai-tools-misc.js:90` (`canvasUpscale`) and `:139` (AI upscale).
  `wire-topbar-menus.js:60-68` (the Canvas… resize) shows the preserve-then-resize form the other
  paths lack:

  ```js
  // static/js/editor/wire-topbar-menus.js:60-68
  if (state.maskCanvas) {
    const tmpMask = document.createElement('canvas');
    tmpMask.width = state.maskCanvas.width;
    tmpMask.height = state.maskCanvas.height;
    tmpMask.getContext('2d').drawImage(state.maskCanvas, 0, 0);
    state.maskCanvas.width = newW;
    state.maskCanvas.height = newH;
    state.maskCtx.drawImage(tmpMask, 0, 0);
  }
  ```
- **Impact:** for anyone who has drawn an inpaint mask: Rotate 90/180/270 and both upscale buttons
  silently wipe the active mask, and every mask is left un-rotated/un-mirrored, so the red overlay
  no longer sits on the same image content. The next Generate/Remove then sends the model a mask
  that selects the wrong region of the transformed image. Ctrl+Z restores the masks from the undo
  snapshot, so the loss is recoverable, but nothing on screen says the mask was dropped.
- **Fix:** apply the same transform to every `layer.masks[].canvas` (rotate/flip the bitmap, resize
  for the upscale paths, rebuild `ctx`), and keep `state.maskCanvas`/`state.maskCtx` pointed at the
  rebuilt canvas instead of assigning `.width` on the live one.

### [BUG] The editor keydown handler is registered again on every open, so one Ctrl+Z undoes N steps

- **Location:** `static/js/editor/keyboard-shortcuts.js:68`
- **Severity:** medium
- **Disposition:** fix-now
- **Evidence:** `wireKeyboardShortcuts` is called from `_buildEditor`
  (`static/js/galleryEditor.js:3514`), which `openEditor` calls on every open
  (`static/js/galleryEditor.js:4100`), and it registers an anonymous document-level listener with no
  guard and no teardown:

  ```js
  // static/js/editor/keyboard-shortcuts.js:68
  document.addEventListener('keydown', (e) => {
    if (!state.editorOpen) return;
  ```

  `closeEditor` removes only the click handlers registered through `_registerDocClickAway`
  (`static/js/galleryEditor.js:166-169` pushes to `state.editorDocClickHandlers`, drained at
  `:4311-4314`) — the comment there ("Without this, dropdown closers accumulated across reopens
  (six handlers × N opens)") confirms that repeated open/close in one page session is the expected
  usage. Probe (`node /tmp/probe-keydown.mjs`, real module, stub `document`):

  ```
  document keydown listeners after 3 editor opens: 3
  undo() calls produced by one Ctrl+Z press: 3
  ```

  Every copy passes the same `state.editorOpen` gate, so they all run; none calls
  `stopImmediatePropagation`. The same "register per open, never detach" pattern appears in five
  more editor modules, with no misbehaviour demonstrated but the same unbounded growth:
  `canvas-events.js:44-45` (`window` mousemove/mouseup), `clipboard-and-drop.js:36` (`window` paste,
  registered in the capture phase — the `true` option is at `:76`), `tools/transform-session.js:294-311`
  (five `document` handlers, added per Transform popup open), `build/right-panel.js:181,189`
  (`document` mousemove/mouseup, per panel build) and `slider-ux.js:116,131` (`document`
  pointermove/pointerup).
- **Impact:** after the Nth open/close cycle in one page session, one Ctrl+Z performs N undo steps
  and one Ctrl+Shift+Z N redo steps — silent loss of undo depth and a state the user did not ask
  for. Ctrl+S clicks the Save menu item N times (each accumulated handler calls
  `document.getElementById('ge-save')?.click()` at `keyboard-shortcuts.js:110`, and that handler has
  no re-entrancy guard, `galleryEditor.js:3274`), `?` toggles the shortcuts popover N times, and
  `[`/`]` multiply the brush size N times. This is the same listener-leak class already reported for
  `static/js/memory.js` in `static-js-research-memory-rag.md:458`.
- **Fix:** register the keydown listener once at module scope (guarded by `state.editorOpen`, which
  the handler already checks) and have the per-open call only attach the per-open closures; or
  return a teardown function from each `wire*`/`create*` call and invoke it from `closeEditor`, the
  way `state.editorDocClickHandlers` is drained.

### [PERF] The transparency checkerboard is re-rasterised cell by cell on every composite

- **Location:** `static/js/editor/checkerboard.js:17`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `drawCheckerboard` paints one `fillRect` per 10 px cell on every call:

  ```js
  // static/js/editor/checkerboard.js:17-23
  for (let y = 0; y < h; y += size) {
    for (let x = 0; x < w; x += size) {
      if ((Math.floor(x / size) + Math.floor(y / size)) % 2 === 0) {
        ctx.fillRect(x, y, size, size);
      }
    }
  }
  ```

  `composite()` calls it for the full document on every redraw (`galleryEditor.js:835`), and
  `composite()` runs once per stroke sample — `stroke-pipeline.js:158` at the end of `strokeTo`,
  which `tools/stroke.js:107` calls from `_continueDraw` (`galleryEditor.js:1445`) on every
  `mousemove`/`touchmove` (`canvas-events.js:44`, `:103`). Measured loop counts (`node -e`, same
  bounds and step):

  ```
  1024x1024: fillRect calls per composite() = 10609
  2048x1536: fillRect calls per composite() = 31570
  3840x2160: fillRect calls per composite() = 82944
  6000x4000: fillRect calls per composite() = 240000
  ```

  `tools/crop.js:104` (crop-rect drag) and `galleryEditor.js:947` (`_drawCropOverlay`) draw it again,
  so the same cost recurs per pointermove while dragging a crop rect.
- **Impact:** a large document spends tens of thousands of `fillRect` calls per frame on a pattern
  that never changes — pure overhead on the hot path for brush strokes, move drags and crop drags
  on 4K+ images, where the editor is already slow enough that rotate shows a blocking spinner
  (`canvas-transforms.js:33-37`). The cost is bounded by the fact that the fills are opaque
  axis-aligned rectangles, so this is an avoidable overhead rather than a proven frame-time
  regression (no browser frame timing was measured in this pass).
- **Fix:** build the 20×20 px checkerboard tile once, keep it in module state, and paint it with a
  single `ctx.fillRect` using `ctx.createPattern(tile, 'repeat')`; the pattern only needs rebuilding
  if the size changes.

### [DEAD-CODE] Five wirings in the topbar modules target element IDs that no longer exist in any markup

- **Location:** `static/js/editor/wire-topbar.js:161`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** each ID below appears only in the wiring module (and, for three of them, in
  `static/style.css`); none is produced by `build/topbar.js`, which is the only place the topbar
  markup is created, and `grep -rn "<id>" --include='*' .` finds no other producer:

  | ID | Referenced at | Also in `static/style.css`? |
  | --- | --- | --- |
  | `ge-edge-menu-btn`, `ge-edge-menu`, `ge-edge-width`, `ge-edge-feather`, `ge-edge-delete` | `wire-topbar.js:152,161,162,167,171,174,178,182` | only `.ge-edge-menu` |
  | `ge-resize-menu-btn`, `ge-resize-menu` | `wire-topbar-menus.js:148-172`, `wire-topbar.js:39-40` | only `.ge-resize-menu` |
  | `ge-topbar-mask-color` | `wire-inpaint-controls.js:156,162,164` | `.ge-topbar-mask-color*` (3 rules) |

  `build/topbar.js:50-76` emits only `resize`, `rotate-90`, `rotate-180`, `flip-h` and `flip-v` as
  `data-image-action` values, so the `selection` and `fill` branches in `wire-topbar-menus.js:108-109`
  are unreachable too. The consequence of the first row is that `applyEdgeAction`
  (`wire-topbar.js:149-159`, the selection edge feather/delete) has no caller: its `if (btn && menu)`
  block at `:163` is never entered, and the Image-menu item that used to click it is gone. The third
  row means `attachColorPicker(topbarMaskColor)` (`wire-inpaint-controls.js:164-167`) never runs and
  the "keep the topbar swatch and the inpaint-section swatch in sync" logic (`:150-160`) is
  half-dead.
- **Impact:** dead weight only — no user-visible failure beyond the features being absent from the
  UI (edge feather/delete is currently unreachable, and the mask tint colour can only be changed
  from the inpaint section). It costs maintenance attention: the topbar modules look like they wire
  features that do not exist, and `closeOtherTopbarMenus`/the outside-click net iterate over two
  menu IDs that always resolve to `null`.
- **Fix:** delete the five blocks (and their orphaned CSS rules), or restore the markup in
  `build/topbar.js`; either way drop `ge-resize-menu`/`ge-resize-menu-btn` from `TOPBAR_MENU_IDS` and
  `TOPBAR_TRIGGER_IDS`.

### [DEAD-CODE] The selection-constrained Bg Remove button is wired to an element that does not exist

- **Location:** `static/js/editor/wire-selection-controls.js:159`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `document.getElementById('ge-wand-rembg')?.addEventListener(...)` is guarded by
  optional chaining, and `git grep -l "ge-wand-rembg"` matches only this file — the ID appears in no
  markup and no CSS rule, though three comments still describe the button as live
  (`ai-rembg.js:26`, `:199`, `galleryEditor.js:3385`). The wand controls markup in
  `build/controls.js:76-102` has `ge-wand-grow`, `ge-wand-vis`, `ge-wand-clear`, `ge-wand-invert`,
  `ge-wand-delete`, `ge-wand-copy` and `ge-wand-mask`, but no `ge-wand-rembg`. The handler is
  therefore never attached and its `wandClear()` / `applyImageTool('/api/image/remove-bg', …)` path
  is unreachable.
- **Impact:** none at runtime; the selection-hint rembg path (`buildSelectionHintMask`, returned by
  `ai-rembg.js:203`) is still reachable through the toolbar Bg Remove button, which calls it at
  `ai-rembg.js:62`. The dead handler is misleading about which entry points exist.
- **Fix:** delete the block, or add the button to the wand section markup if the per-selection
  shortcut is still wanted.

### [DEAD-CODE] Both exports of fx/filter-string.js are imported but never called

- **Location:** `static/js/editor/fx/filter-string.js:16`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `layerFilterString` (`:16-23`) and `fxFilterToSlider` (`:32-38`) have no call site:
  `grep -rn "layerFilterString\|fxFilterToSlider" static/js/` matches only the two definitions and
  the import in `galleryEditor.js:25-28` (`_layerFilterString`, `_fxFilterToSlider`), which are then
  never used — the only other mention is the comment at `galleryEditor.js:623`. The module is a pure
  helper with no side effects, so nothing else depends on it.
- **Impact:** none at runtime. The adjustment-to-CSS-filter conversion it implements is not used by
  the current composite path, which renders adjustments through `fx/pixel-pass.js` instead, so a
  reader can be misled about how layer adjustments reach the canvas.
- **Fix:** delete the module and its import, or call it from the composite path if the CSS-filter
  shortcut is intended to be the cheap path for B/C and H/S.

### [BUG] The topbar canvas-size badge can never be shown

- **Location:** `static/js/editor/build/topbar.js:50`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the badge is created with the `hidden` attribute
  (`static/js/editor/build/topbar.js:50`):

  ```html
  <span class="ge-canvas-size" id="ge-canvas-size" title="Canvas size" hidden></span>
  ```

  Eight call sites write its text content (`canvas-transforms.js:88`, `ai-tools-misc.js:93,140`,
  `wire-topbar-menus.js:73`, `wire-topbar-overflow.js:20`, `galleryEditor.js:1348,4147,4218`), but
  nothing removes `hidden` — `grep -rn "ge-canvas-size" static/js/` shows only `textContent`
  assignments. The single CSS rule for the class lives inside a media query and sets only font,
  padding and line-height (`static/style.css:30107-30111`), so the user-agent `[hidden] {
  display: none }` rule still applies. (`#ge-canvas-size-overlay`, `galleryEditor.js:3938`, is the
  canvas-size prompt modal, an unrelated element.)
- **Impact:** the document dimensions are never visible in the editor topbar; the writers run on
  every resize/rotate/upscale for nothing. The dedicated mobile rule suggests the badge was meant
  to be visible at least at narrow widths, so this looks like a dropped `hidden` removal rather than
  a deliberate choice.
- **Fix:** drop the `hidden` attribute (or delete the badge and its writers, if the size is meant to
  be shown elsewhere).

### [BUG] The model-dropdown value encoding is ambiguous for an IPv6 endpoint base URL

- **Location:** `static/js/editor/ai-models.js:120`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** each option value is built by joining the endpoint base URL and the model id with
  `::`:

  ```js
  // static/js/editor/ai-models.js:119-120
  // Encode "<base_url>::<model_id>" so the value carries both pieces.
  const value = `${ep.base_url}::${modelId}`;
  ```

  and decoded by splitting at the *first* `::` (`static/js/galleryEditor.js:243-244`,
  `raw.indexOf('::')`). An IPv6 literal in the base URL contains `::` itself, so the split lands
  inside the host. Reproduced with `node -e`:

  ```
  "http://127.0.0.1:8080::sd-xl" -> endpoint: "http://127.0.0.1:8080" model: "sd-xl"
  "http://[::1]:8080::sd-xl" -> endpoint: "http://[" model: "1]:8080::sd-xl"
  ```

  The mangled `_endpoint` is then sent in the body of `/api/image/inpaint` (`ai-inpaint.js:148`) and
  `/api/image/harmonize` (`ai-tool-runner.js:74`, sent at `:81`); the server resolves it against the
  owner's visible `ModelEndpoint` rows by base URL (`routes/gallery/gallery_routes.py:1296`, `:1561`)
  and raises `HTTPException(403, "Choose a registered image endpoint")` when nothing matches
  (`:1297-1298`, `:1562-1563`).
- **Impact:** a user whose image endpoint is configured with an IPv6 literal (e.g.
  `http://[::1]:8080`) gets a dropdown that lists models but sends a base URL the server cannot
  resolve, so the request fails with a 403 "Choose a registered image endpoint" instead of running
  the chosen model. Reachability depends on an IPv6-literal endpoint, which is why this is low; the
  parsing itself is deterministic.
- **Fix:** use `raw.lastIndexOf('::')` in `_getSelectedAIEndpoint` (model ids cannot contain `::`),
  or encode the pair as JSON / keep the endpoint in a `data-` attribute instead of a joined string.
