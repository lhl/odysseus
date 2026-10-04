# static: remaining first-party JS

## Overview

This section covers the 44 paths assigned to it — 42 first-party JavaScript modules plus
`MODULE_SUMMARY.md` and `package.json` — that are left after the other `static/js` sections took
their slices: the shared utilities (`ui.js`, `storage.js`, `platform.js`, `panels.js`, `init.js`,
`workspace.js`, `section-management.js`, `sidebar-layout.js`, `toolWindowZOrder.js`, `ui_visibility.js`,
`a11y.js`, `keyboard-shortcuts.js`, `dragSort.js`, `escMenuStack.js`, `tourHints.js`, `tourAutoplay.js`,
`startupShell.js`, `appConfig.js`, `util/ordinal.js`, `color/hex.js`), the input and media helpers
(`codeRunner.js`, `fileHandler.js`, `censor.js`, `markdown.js`, `markdown/tableRow.js`,
`emojiPicker.js`, `emojiShortcodes.js`, `langIcons.js`, `voiceRecorder.js`, `tts-ai.js`), the window
management layer (`modalManager.js`, `modalSnap.js`, `tileManager.js`, `windowDrag.js`,
`windowResize.js`), the four large panels that have no section of their own (`settings.js`,
`tasks.js`, `skills.js`, `group.js`), and `theme.js` with the colour picker.

The boundary: `static-js-chat` owns `chat.js`, `chatStream.js`, `chatRenderer.js` and
`slashCommands.js` — where the theme name of this section's first finding, and the spinner message
that section reports, enter the client — and its findings are cross-referenced here, not restated;
`static-js-cookbook-settings-models` owns `cookbook*`, `admin.js`, `models.js`, `modelPicker.js`,
`providers.js` and the `settings/*.js` framework, and explicitly leaves `settings.js`, `tasks.js`
and `ui.js` to this section; `static-js-documents-email` and `static-js-editor` own the library and editor modules that
call into `windowDrag.js`, `modalSnap.js` and `tileManager.js`. The Python routes, services and
agent tools these modules call are out of scope (`routes-*`, `src-*` and `src-mcp` own those), so
this section reviews what the browser does with a value it already has — not whether the server
should have sent it.

## Coverage

**Read fully:** the 32 modules at or under ~530 lines (7,537 lines) plus the section's two
non-JavaScript paths — `util/ordinal.js` (13), `color/hex.js` (14), `markdown/tableRow.js` (19),
`toolWindowZOrder.js` (46), `platform.js` (47), `panels.js` (53), `ui_visibility.js` (73),
`appConfig.js` (86), `escMenuStack.js` (102), `storage.js` (125), `tourAutoplay.js` (133),
`startupShell.js` (153), `a11y.js` (165), `tourHints.js` (179), `langIcons.js` (187),
`workspace.js` (208), `windowResize.js` (233), `section-management.js` (260), `dragSort.js` (265),
`voiceRecorder.js` (283), `keyboard-shortcuts.js` (292), `emojiPicker.js` (313), `windowDrag.js`
(333), `censor.js` (356), `tileManager.js` (394), `codeRunner.js` (403), `init.js` (421),
`colorPicker.js` (453), `emojiShortcodes.js` (458), `spinner.js` (463), `fileHandler.js` (483),
`tts-ai.js` (524), `MODULE_SUMMARY.md` (229) and `package.json` (1).

**Read in targeted ranges, or at structure level only:** the ten modules over 1,000 lines plus
`sidebar-layout.js`. For these the section claims only what is listed, and every citation in the
findings resolves inside a claimed range:

- `theme.js` (2,115): the module init and server sync (`:2076-2115`), the custom-theme store
  (`:85-120`), the swatch renderer (`:523-700`), the auto-save paths (`:860-875`, `:1010-1020`) and
  the drag wiring (`:1465-1490`)
- `tasks.js` (3,188): the API helpers (`:29-192`), the form renderer and its type options
  (`:1180-1310`), the filter chips (`:2200-2210`) and the log renderer (`:2456-2800`)
- `settings.js` (5,659): the panel-activation helpers and the shared `esc` (`:47-68`), the logout
  wipe (`:2120-2137`), the appearance tab (`:1558-1660`) and the MCP server detail view
  (`:4930-4999`); the tab-init function list was read by name only
- `skills.js` (2,025): the escapers and fetch helpers (`:19-70`), the list renderer entry points
  (`:624-922`) and the skill test flow (`:1190-1240`)
- `modalManager.js` (1,560): the state map, dock persistence and remembered docks (`:1-108`), the
  dock renderer and chip drag (`:150-450`), registration and `unregister` (`:1140-1230`) and the
  auto-wire/swipe-dismiss tail (`:1360-1560`)
- `modalSnap.js` (1,079): the width resolution, clamp helpers and email split geometry (`:1-270`);
  the observer-heavy left-dock half was not read
- `sidebar-layout.js` (613), `markdown.js` (1,229), `ui.js` (1,329) and `group.js` (1,017): read at
  structure level — exports, DOM sinks, storage keys — and `markdown.js` and `group.js` are
  additionally pinned by `tests/test_markdown_rendering_js.py` and
  `tests/test_group_character_dropdown.py` below; no completeness claim is made for these four, and
  no finding rests on them

**Not read:** nothing assigned to this section was left unopened. `static/lib/*` (the vendored
bundles) belongs to another section and was not reviewed here.

**Checks run:**

```
$ ls tests | grep -iE 'markdown|emoji|censor|esc_menu|ordinal|hex_to|ui_visib|lang_icon|tile_manager|
    spinner|group|panel_loader|startup_shell|platform|popup_opener|snap|settings_shell|workspace_confine|
    app_config|keybind|matchescombo|modal|notes_z_order'
→ 33 matches: 32 pytest files and the standalone node script
  tests/markdown_codefence_placeholder_regression.mjs. 29 of the pytest files exercise these
  modules and were run; the three that did not are test_ollama_multimodal.py,
  test_replace_messages_multimodal.py and test_sanitize_multimodal_merge.py, which matched on
  "modal" in their names and cover the multimodal upload path, not these modules.

$ venv/bin/python -m pytest -q tests/test_censor_pref_js.py tests/test_emoji_shortcodes_js.py \
    tests/test_esc_menu_stack_js.py tests/test_ordinal_suffix_js.py tests/test_hex_to_rgb_js.py \
    tests/test_ui_visibility_js.py tests/test_lang_icon_null_opts_js.py \
    tests/test_tile_manager_snap_zones_js.py tests/test_spinner_stops_when_never_attached_js.py \
    tests/test_group_character_dropdown.py tests/test_panel_loader_js.py tests/test_startup_shell_js.py \
    tests/test_platform_compat.py tests/test_popup_opener_isolation_js.py \
    tests/test_markdown_dom_xss_helpers.py tests/test_markdown_rendering_js.py \
    tests/test_markdown_table_row_js.py tests/test_markdown_lazy_lib_loading_js.py \
    tests/test_emoji_svg_hardening.py tests/test_snap_other_layers_nonarray_js.py \
    tests/test_app_config_shared_fetch_js.py tests/test_keybind_altgr_js.py \
    tests/test_matchescombo_nonstring_js.py tests/test_workspace_confine.py \
    tests/test_settings_shell_js_behavior.py tests/test_modal_dock_composer_clearance.py \
    tests/test_group_chat_storage.py tests/test_notes_z_order_js.py \
    tests/test_form_markdown_roundtrip.py
200 passed, 1 warning in 5.65s

$ node tests/markdown_codefence_placeholder_regression.mjs
ok

$ for f in <the 42 assigned .js files>; do node --check "$f"; done    # CONTRIBUTING.md:52
parsed OK: 42  failed: 0
```

Four probes back the findings below and are quoted where they are used:
`/tmp/probe_theme_swatch.mjs`, `/tmp/probe_theme_swatch2.mjs` (theme swatch template),
`/tmp/probe_task_textarea.mjs` (task form template) and `/tmp/probe_mcp_esc.mjs` (MCP tool list
escaping). All four slice the template or the escaper out of the target file and run it unchanged;
nothing was written into the repository.

One already-reported defect lives in a file assigned to this section and is not restated:
`static-js-chat` reports the `innerHTML` spinner sink at `static/js/spinner.js:325-332` (message
built at `:383-390`) as its first finding, with the message arriving from `chat.js:3153`. This
section owns `spinner.js` and confirms the sink is as described; the fix belongs there, but the
finding is counted in that section.

### [SECURITY] A stored custom-theme name is rendered into the theme grid as markup on every page load

- **Location:** `static/js/theme.js:660-669` (element-content sink at `:668`, attribute sinks at
  `:661` and `:669`)
- **Severity:** medium
- **Disposition:** fix-now
- **Evidence:** `initThemeUI()` builds the custom-swatch grid with the theme name interpolated
  unescaped in three positions, one of which is element content:

  ```js
  // theme.js:660-669
  userGrid.innerHTML = customEntries.map(([name, c]) => `
    <div class="theme-swatch${name === activeName ? ' active' : ''}" data-theme="${name}" data-custom="1">
      ...
      <span class="theme-swatch-name">${name}</span>
      <button type="button" class="theme-delete-btn" data-delete="${name}" title="Delete theme">...</button>
    </div>
  `).join('');
  ```

  The name is an unvalidated object key end to end. `saveCustomTheme` stores it (`theme.js:107`
  `ct[name] = entry`), persists it to `localStorage` and to `PUT /api/prefs/custom-themes`
  (`:108-109`, endpoint at `:120-126`), then re-renders immediately (`:110`). The value comes from the model's `ui_control`
  call — `static/js/chatStream.js:118` `var name = uiData.theme_name || 'custom'` → `:134`
  `tm2.saveCustomTheme(name, colors2, ...)` — and `src/ai_interaction.py`'s `create_theme` branch
  only lowercases it and swaps spaces for dashes (`:759`
  `name = parts[1].lower().replace(" ", "-")`); the colours are validated as `#RRGGBB`
  (`:763-765`, `:784-786`) but the name is not, so `<`, `>` and `"` survive into the store.
  `theme.js` is loaded as a module by `static/index.html:2582`, and `_initWithSync()` ends with
  `initThemeUI()` (`theme.js:2108`), so a stored name is re-rendered — and a payload re-fires — on
  every page load of the app, and immediately on create.

  Probe, which slices the template out of the file and runs the same map callback with a
  markup-bearing name:

  ```
  $ node /tmp/probe_theme_swatch.mjs
  === 1. hostile theme NAME (element-content position, theme.js:668) ===
  <span class="theme-swatch-name"><img src=x onerror=alert(1)></span>
  live markup: true
  ```

  The same template interpolates the four colour values into `style="background:${c.bg}"` (`:663-666`).
  A quote in a colour breaks out of the attribute — `node /tmp/probe_theme_swatch2.mjs` renders
  `<span style="background:red"><img src=x onerror=alert(2)>"></span>` for `bg = 'red"><img src=x
  onerror=alert(2)>'` — but every writer of those values is hex-validated server-side and the theme
  editor's colour inputs emit `#rrggbb`, so that half is reported as hardening, not as a reachable
  path.
- **Impact:** one `create_theme` call from the model — reachable from any content that steers it,
  a fetched page, an email or a tool result — plants a payload in the user's persisted theme store,
  and the payload then re-parses in the app origin on every load without any further interaction.
  Its inline handler does not execute there: the chat page carries the nonce policy at `core/middleware.py:141-147`
  (`script-src 'self' 'nonce-{nonce}'`, no `'unsafe-inline'`, nonce templated into `index.html`'s
  inline blocks), so the probe's `onerror` handler is refused. The stored payload is still worse
  than the reflected one below, because it is persistent and needs no user action: the injected
  markup sits in the theme picker on every load, where it can spoof or cover UI, carry an attacker
  link, or fire an `<img src>` beacon (`img-src` allows `https:`). The user's only visible clue is a
  custom theme they never created. The same root cause is reported by `static-js-chat` as a `medium`
  finding for the slash-reply sink in `slashCommands.js:1468-1470`; this section reports the second
  sink of that root cause and keeps it at `medium` so the run does not count one cause twice, even
  though this sink needs no slash command and no user interaction.
- **Re-review (2026-10-05):** stands at medium, with two corrections. With the swatch template
  copied by line range onto a page served with the app's policy, the name
  `<iframe/srcdoc="<script/src=https://cdn.jsdelivr.net/npm/lodash@4.17.21/lodash.min.js></script>">`
  (no spaces, lower case, as `src/ai_interaction.py:759` leaves it) ran the CDN script in a
  same-origin frame on render. So a stored name executes on every page load. And the path in is
  narrower than "any content that steers the model": `ui_control` carries
  `ToolEffect.UI_SIDE_EFFECT`, which `decision_for` blocks once untrusted content is in the run
  unless the user approves the call (`src/tool_capabilities.py:226-231`, `:553-564`, `:654-684`).
  That gate is why this is not high.
- **Fix:** escape the name at the sink (`uiModule.esc(name)` at `theme.js:661`, `:668`, `:669`) and
  reject markup-bearing names at the boundary — restrict `theme_name` to `[a-z0-9_-]+` in
  `src/ai_interaction.py`'s `create_theme` branch and in `saveCustomTheme` before it is stored — so
  a bad key can never enter `localStorage` or the preferences row.

### [SECURITY] A model-authored task prompt is interpolated into the task form's textarea unescaped

- **Location:** `static/js/tasks.js:1299`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the task form builds its prompt field by string concatenation into `innerHTML` with
  the stored prompt in element content, while the field immediately above it escapes the same kind
  of server value:

  ```js
  // tasks.js:1224 (name, escaped)
  <input type="text" id="task-form-name" class="task-form-input" value="${_esc(existing?.name || '')}" ... />

  // tasks.js:1299 (prompt, raw)
  <textarea id="task-form-prompt" class="task-form-input task-form-textarea" rows="4" placeholder="${placeholder}">${existing?.prompt || ''}</textarea>
  ```

  `_esc` is defined at `tasks.js:1053-1057` (a `textContent` → `innerHTML` round trip) and is what
  the name field uses. `existing` is the task row the client cached from `/api/tasks`, and the
  prompt is stored verbatim from the agent tool: `src/tools/system.py:359` writes
  `prompt=args.get("prompt")` on the `action == "create"` branch (`:332`), which the agent prompt
  tells the model to call for any recurring request (`src/agent_loop.py:335`). Probe, slicing the
  template out of the file and running it with a prompt that closes the textarea:

  ```
  $ node /tmp/probe_task_textarea.mjs
  rendered textarea line:
  <textarea id="task-form-prompt" class="task-form-input task-form-textarea" rows="4" placeholder="What should the AI do?"></textarea><img src=x onerror=alert(1)></textarea>
  textarea closed early: true
  ```
- **Impact:** a prompt that arrives from model output (for example, one derived from an email or a
  fetched page) is stored as a scheduled task and then executed as markup when the user opens that
  task's edit form — the one place the raw prompt is rendered. The form is opened from the task list
  by a deliberate click, which is what keeps this at `low`; the escape hatch is that the payload
  only fires while editing that specific task. A second, quieter consequence is that a prompt
  containing `</textarea>` truncates the field the user sees.
- **Re-review (2026-10-05):** stands at low. A prompt that closes the textarea and opens an
  `<iframe srcdoc>` can load script from `cdn.jsdelivr.net` (the policy finding in
  `core-auth-session`); this sink was not probed. Low is kept because the payload fires only when
  the user opens that task's edit form.
- **Fix:** `${_esc(existing?.prompt || '')}` at `tasks.js:1299`, matching the name field above it.

### [SECURITY] The MCP tool list shadows the quote-escaping `esc` with a weaker local one, so tool metadata injects markup

- **Location:** `static/js/settings.js:4937` (the shadowing definition) and `:4984` (the sink)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the MCP server detail view declares its own `esc` that escapes `&` and `<` but not
  `"`, shadowing the module-level `esc` at `:61` (`uiModule.esc`, which does escape quotes):

  ```js
  // settings.js:4937 — shadows the module-level esc for the rest of this block
  const esc = s => String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;');
  ```

  Both values it protects are placed inside double-quoted attributes:

  ```js
  // settings.js:4984
  panel.innerHTML = `... ${tools.map(t => `<label title="${esc(t.description)}"><input type="checkbox" data-mcp-tool-name="${esc(t.name)}" ...`).join('')} ...`;
  ```

  `tools` is the JSON body of `/api/mcp/servers/<id>/tools`, and the names and descriptions in it
  are whatever the connected server declared: `src/mcp_manager.py:210` and `:279` pass
  `"name": tool.name` through from the SDK, and the installed SDK's `Tool.name` is an unconstrained
  string (`venv/bin/python -c "from mcp.types import Tool; import json;
  print(json.dumps(Tool.model_json_schema()['properties']['name']))"` →
  `{"title": "Name", "type": "string"}`, no pattern). Probe of the escaper as written:

  ```
  $ node /tmp/probe_mcp_esc.mjs
  <label title="reads files" autofocus onfocus="alert(2)"><input type="checkbox" data-mcp-tool-name="list_files" onmouseover="alert(1)" checked></label>
  breaks out of data-mcp-tool-name: true
  ```
  (both attribute values in that output are synthetic; no real credential is involved). The panel
  renders as soon as the user opens that server in Settings → MCP, so a name containing `">`
  breaks the attribute on render, and a description containing a quote needs one hover over the row.
- **Impact:** a user who has connected an MCP server — including a server whose metadata is later
  changed, or one reachable through a URL the user added — has that server's tool metadata parsed
  as markup in the app origin when they open its page in Settings. This is markup injection and not
  script execution: the Settings panel is part of the chat page, which carries the nonce policy
  (`core/middleware.py:141-147`, `script-src 'self' 'nonce-{nonce}'`, no `'unsafe-inline'`), so the
  injected attributes are honoured while an injected handler is refused — the reachable effects are
  CSS from `style-src 'unsafe-inline'` overlaying or hiding the panel, an attacker link, and an
  `<img src>` beacon. The same breakout also corrupts
  `data-mcp-tool-name`, so the enable/disable checkboxes for that server stop persisting the right
  tool (the save path reads `cb.dataset.mcpToolName` at `:4987`). `src-mcp.md` reads this panel as
  boundary context (`:4939-4980`) and does not report it.
- **Fix:** delete the local `esc` at `:4937` so the block uses the module-level `uiModule.esc`, or
  add `.replace(/"/g,'&quot;')` to it. Validating tool names at the manager boundary
  (`src/mcp_manager.py`, where the inventory is built) would fix the class rather than this sink.

### [DEAD-CODE] `enableFullscreen` is hardcoded off, so five callers' fullscreen callbacks can never run

- **Location:** `static/js/windowDrag.js:64` (the hardcoded value), `:239` and `:255-259` (the only
  readers)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the option is documented as honoured and then ignored:

  ```js
  // windowDrag.js:36-37 — the API doc block
  //     enableFullscreen: bool — enable top-edge fullscreen snap.
  //                        Default true when onEnterFullscreen is supplied.
  // windowDrag.js:64
    const enableFullscreen = false;
  ```

  `enableFullscreen` is read in exactly two places — `:239` `_showSnapHint(enableFullscreen &&
  inTopBand)` and `:255-259`, which is the only caller of `_enterFs()`:

  ```js
  // windowDrag.js:255-259
      if (enableFullscreen && typeof cy === 'number' && cy <= SNAP_PX) {
        if (rightDock) rightDock.release();
        if (leftDock) leftDock.release();
        _enterFs();
        return;
      }
  ```

  `_enterFs` (`:131-135`) is the only caller of `onEnterFullscreen`, so every `onEnterFullscreen`
  passed by a caller is unreachable: `static/js/memory.js:131`, `static/js/notes.js:168`,
  `static/js/theme.js:1475`, `static/js/emailLibrary.js:3420` and
  `static/js/documentLibrary.js:1801`. Two fullscreen classes those callbacks add have no other
  writer anywhere in the tree (`grep -rn "doclib-fullscreen" --include=*.js --include=*.html
  --include=*.py` → only `documentLibrary.js:1763-1799` and `style.css`; the same for
  `notes-window-fullscreen` → only `notes.js:164-185`), and `documentLibrary.js:1803` still passes
  `enableFullscreen: false` as though the option were live. `git log -L 64,64:static/js/windowDrag.js`
  shows the disable is deliberate and recent:

  ```
  22bd77ee fix(windowDrag): disable duplicate top-edge fullscreen snap (#3495)
  -  const enableFullscreen = options.enableFullscreen !== false && !!onEnterFullscreen;
  +  const enableFullscreen = false;
  ```

  (22bd77ee is an ancestor of the reviewed commit.) What the disable leaves behind is the drift:
  `static/js/tourHints.js:91` still tells the user "drag any window's title bar to a screen edge to
  snap it. Drag to the top for fullscreen", `emailLibrary.js:3358-3359` still documents the top-edge
  snap for its own `_makeDraggable`, and the API block still promises the default. The exit half
  (`_isFullscreen` at `:180`, `_exitFs` at `:204`) is *not* fully dead: `static/app.js:1214` adds
  `email-lib-fullscreen` for the email route, so the email modal can still enter that state by a
  path that does not go through `makeWindowDraggable`. The side-edge docks are unaffected.
- **Impact:** the "drag to the top for fullscreen" gesture silently does nothing for every window
  built through this helper, including the four whose authors wired a fullscreen callback for it, and
  the tour hint promises it to the user. The next person who adds a caller, or who flips `:64` back
  to honour the option, has no signal that five callbacks and two CSS states are waiting for it.
- **Fix:** pick one and make the code say it. Either delete the option, the two `enableFullscreen`
  reads, `_enterFs`/`_showSnapHint`'s top band and the five callbacks' fullscreen halves, and drop
  the promise from `tourHints.js:91`; or restore `options.enableFullscreen !== false &&
  !!onEnterFullscreen` and keep the duplicate-snap fix that #3495 was after at the call sites that
  still double up.

### [BUG] A pointer released outside the window leaves the tile-snap tracker armed, so the next click snaps the window

- **Location:** `static/js/tileManager.js:259-292` (handlers at `:244`, `:259`, `:283`; state at
  `:27-28`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the module arms a module-level tracker on `pointerdown` over a modal header and
  clears it only in the `pointerup` handler:

  ```js
  // tileManager.js:244-256
  document.addEventListener('pointerdown', (e) => {
    if (!_isDesktop()) return;
    const content = _findDragTarget(e);
    if (!content) return;
    ...
    _tracking = { content, startX: e.clientX, startY: e.clientY, willUnsnap: ... };
  });

  // tileManager.js:259-265 — no e.buttons check, no pointercancel listener
  document.addEventListener('pointermove', (e) => {
    if (!_tracking) return;
    if (!_isDesktop()) return;
    const dx = e.clientX - _tracking.startX;
    const dy = e.clientY - _tracking.startY;
    if (Math.hypot(dx, dy) < 6) return;
    ...
    _showGhost(zone.rect);
    _activeZone = zone;

  // tileManager.js:283-291
  document.addEventListener('pointerup', () => {
    if (!_tracking) return;
    const t = _tracking;
    _tracking = null;
    _hideGhost();
    if (_activeZone && _isDesktop()) { _applySnap(t.content, _activeZone.rect, _activeZone.name); }
    _activeZone = null;
  });
  ```

  A mouse released outside the browser window delivers no `pointerup` to the document (there is no
  pointer capture on this path), so `_tracking` and `_activeZone` survive the gesture. Moving back
  over the page then fires `pointermove` with no button held, which re-arms the ghost from the stale
  `startX/startY` and unsnaps the window (`_unsnap` at `:267-270`), and the next `pointerup`
  anywhere in the page runs `_applySnap` and tiles the window to the zone under the cursor. The
  codebase already treats this as a known failure mode elsewhere: `windowResize.js:176-181`
  self-heals the identical case — "Self-heal a missed mouseup (released outside the window, dropped
  event, window blur): a move with no buttons pressed means the drag is over" — with
  `if (e.buttons === 0) { mu(); return; }`. `grep -n "buttons\|pointercancel"
  static/js/tileManager.js` returns no match, and the same grep over `windowDrag.js` and
  `modalSnap.js` returns none either. I did not reproduce this in a browser in this pass; the
  claim is read from the handlers and from the missing release path.
- **Impact:** after a drag that ends off-window, the user's next click in the app also snaps the
  window they were dragging to whatever tile the cursor is over, and the ghost preview reappears
  while they move the mouse. Low severity because it needs an off-window release and is undone by
  dragging the window back, but it is a click that does something the user did not ask for.
- **Fix:** treat a button-less move as the end of the gesture, the way `windowResize.js` does — add
  `if (e.buttons === 0) { _tracking = null; _activeZone = null; _hideGhost(); return; }` at the top
  of the `pointermove` handler — and add a `pointercancel` listener that clears both.
