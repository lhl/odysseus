# static: chat, sessions and composer UI

## Overview

The thirteen modules assigned here are the main chat surface: `chat.js` (6,738 lines — the send
path, the SSE reader, the detached-stream lifecycle, the composer wiring and the terminal handlers),
`sessions.js` (the session list, `selectSession`, the history pager, background-stream polling and
the running/completed rail state), `chatRenderer.js` (message bubbles, footers, metrics popups and
the model-provenance labels), the stream pipeline (`chatStream.js`, `streamingSegmenter.js`,
`streamingRenderer.js`, `chatStreamErrors.js`, `liveThinkingThrottle.js`), the composer helpers
(`composerArrowUpRecall.js`, `slashAutocomplete.js`, `slashCommands.js`) and two small support
modules (`assistant.js`, `chatModelProvenance.js`).

The boundary: this section covers what these modules render and what they persist, not the
endpoints they call. `/api/chat_stream`, `/api/history/{id}`, `/api/session*` and the metrics
payload's server-side construction belong to `routes-chat-session`, `src-chat-session` and
`src-llm-core`; the markdown renderer the bubbles go through is `static-js-rest` (`markdown.js`),
and `static/js/spinner.js` — the sink behind the first finding below — is also assigned to
`static-js-rest`. The research pipeline that feeds the first finding
(`src/deep_research.py`, `services/search/providers.py`) is covered by `src-research-*` and
`services-search`; the lines cited here are the ones that establish provenance, not a review of
those modules. The theme store behind the second finding (`static/js/theme.js`) is
`static-js-rest`.

Three things this section was asked to settle, and the answers:

- **Markup injection.** The stream renderer is disciplined: model output reaches the DOM only
  through `markdownModule.processWithThinking(...)` into `innerHTML` (by design, after escaping) or
  through `textContent`. Two `innerHTML` sinks in this slice take values that are *not* model output
  and *not* escaped — the research spinner message (finding 1) and custom theme names in slash
  replies (finding 2). The model-provenance model id is a third (finding 3). Everything else that
  interpolates external data in these files goes through `uiModule.esc`/`ctx.esc`, including every
  `<pre>` block in `slashCommands.js`.
- **Session switch mid-stream.** The detach path is consistent: `detachCurrentStream` hands the
  reader to `_backgroundStreams`, `sessionModule.markStreaming` lights the sidebar dot, the poll in
  `sessions.js` reloads the session when the entry clears, and `resumeStream` re-attaches to the
  server-side run (replaying its buffer) when the page comes back. I could not break the
  switch-away / switch-back / complete sequence by reading: every terminal branch either reloads the
  history or clears the running state on the next poll. The two session-switch defects I did find
  are in the *identification* of the session to stream into (findings 4 and 5).
- **Persisted state replayed as markup.** `localStorage`/`sessionStorage` in these modules holds
  drafts, toggles, the last session id, the model choice, folder collapse state, incognito ids and
  scroll/pager state. None of it is replayed as markup: the toggles are booleans, the folder and
  session names are written with `textContent` (`sessions.js:1222`, `:573`), and the arrow-recall
  and slash-autocomplete paths write into the textarea's `value`, not into HTML. The one stored
  value that *is* replayed as markup — a custom theme name — arrives from the model, not from the
  user's own storage writes (finding 2).

## Coverage

**Read fully:** `assistant.js` (475 lines), `chatModelProvenance.js` (104), `chatStream.js` (327),
`chatStreamErrors.js` (23), `composerArrowUpRecall.js` (171), `liveThinkingThrottle.js` (206),
`slashAutocomplete.js` (313), `streamingRenderer.js` (206), `streamingSegmenter.js` (190) — 2,215
lines. `chatRenderer.js` (3,126) and `sessions.js` (3,689) were read in full across the two passes
of this section.

**Read partially:** `chat.js` (6,738) — read in full for the send path (`:1106-2065`), the stream
reader and its terminal branches (`:2066-4600`, `:4700-5250`), the research spinner and progress
handlers (`:3125-3165`, `:6040-6080`), the thinking/reply boundary heuristics (`:2645-2670`,
`:2960-3000`, `:4090-4115`) and the composer wiring (`:808-853`); the image/vision rendering and
the file-preflight region were skimmed rather than read line by line. `slashCommands.js` (6,520) —
read the registry and dispatcher, the reply sinks (`slashReply` `:309-336`, `typewriterReply`), the
`/theme` family, and every call site that interpolates non-literal text; the individual command
handlers I did not cite were not read line by line. `chatRenderer.js` and `sessions.js` were also
re-read at each cited range.

**Not read:** the rest of `static/js/` (other sections), the CSS that styles these components, and
the server routes these modules call, beyond the specific lines cited as provenance below. Line
numbers are the reviewed commit `2992bf6d368a`; the tree's HEAD is four audit-doc commits later
(`4cff473d`), and none of the files cited here differs between the two
(`git diff --stat 2992bf6d368a..HEAD -- <cited files>` is empty), while
`git status --porcelain -- . ':(exclude)audit'` shows no code changes.

**Checks run:** `ls tests | grep -iE 'chat|session|stream|spinner|slash|composer|assistant|thinking'`
→ 71 candidate suites; the 16 that exercise these modules were run:

```
$ venv/bin/python -m pytest -q tests/test_chat_stream_errors_js.py \
    tests/test_composer_arrow_up_recall_js.py tests/test_chat_model_provenance_js.py \
    tests/test_streaming_segmenter_js.py tests/test_live_thinking_scheduler_js.py \
    tests/test_spinner_stops_when_never_attached_js.py tests/test_slash_autocomplete_static.py \
    tests/test_startup_session_bootstrap_js.py tests/test_new_chat_clears_input.py \
    tests/test_new_chat_model_preference.py tests/test_deleted_session_sidebar_regression.py \
    tests/test_session_ghost_delete.py tests/test_copy_message_strips_thinking_js.py \
    tests/test_chat_metrics.py tests/test_chat_stream_scope.py
57 passed, 1 warning in 1.99s
$ venv/bin/python -m pytest -q tests/test_chat_tool_screenshot_xss.py
8 passed, 1 warning in 0.07s
```

`tests/test_chat_tool_screenshot_xss.py` is a static-assertion XSS guard suite over `chat.js`,
`chatRenderer.js` and `compare/stream.js`; its assertions are cited as evidence of the escaping
pattern the findings below depart from. Two Node probes under `/tmp` settle the DOM sinks the
findings rest on: `/tmp/probe_spinner_sink.mjs` (the spinner message reaches `innerHTML` for the
`wave` and default animations, `textContent` for `whirlpool`) and `/tmp/probe_projector.mjs`,
which tests whether the module-global `DISPLAY_FILTER_BOUNDARY_RE`
(`liveThinkingThrottle.js:44`, no `g` flag) leaks `lastIndex` between projector instances or across
`reset()` — it does not, so that hypothesis is recorded as rejected rather than reported. A third
probe, `/tmp/probe_reply_prefixes.py`, compared the five copies of the reply-prefix list
programmatically; its output is quoted in finding 7.

### [SECURITY] A hostile search-result title reaches the research spinner's `innerHTML`, injecting markup into the app origin

- **Location:** `static/js/chat.js:3153` and `:6068` (the message), `static/js/chat.js:2042` and
  `:6051` (the spinner those messages go to), sink at `static/js/spinner.js:332` via
  `:383-390`
- **Severity:** high
- **Disposition:** fix-now
- **Evidence:** the research progress handler interpolates a web page title into the spinner:

  ```js
  // chat.js:3152-3159 (the live stream) and :6067-6072 (the reconnect spinner)
  } else if (rp.phase === 'reading') {
    spinner.updateMessage(rp.title ? `Reading: ${rp.title}` : `Round ${rp.round || '?'}: Reading ...`);
  ...
  } else if (rp.phase === 'error') {
    spinner.updateMessage(rp.message || 'Search error');
  ```

  `rp.title` is the search result's title, taken verbatim from the search provider's JSON
  (`services/search/providers.py:178` `"title": r.get("title", "")`), stored unchanged
  (`src/deep_research.py:531`), used as the event's display title (`src/deep_research.py:612-613`
  `display = title or url` / `self._emit(phase="reading", url=url, title=display, ...)`) and framed
  onto the SSE stream without escaping (`routes/chat_routes.py:1766`
  `json.dumps({'type': 'research_progress', 'data': progress})` — `json.dumps` does not escape `<`).
  Nothing between the provider and the spinner sanitizes it.

  The spinner is created with the ASCII-frame animation, whose message path is `innerHTML`:

  ```js
  // chat.js:2042-2045
  spinner = spinnerModule.create('Initializing', 'right', 'wave');
  ...
  bodyDiv.appendChild(spinner.createElement());
  ```

  ```js
  // spinner.js:325-332
  let display = '';
  if (this.style === "left") { display = `${frame} ${this.message}`; }
  else if (this.style === "right") { display = `${this.message} ${frame}`; }
  else { display = this.message; }
  this.element.innerHTML = display;
  ```

  `updateMessage` routes to `textContent` only for the canvas animations (`spinner.js:383-390`:
  `if ((this.animation === 'sinewave' || this.animation === 'whirlpool') && this._msgSpan)`), so
  `wave` and the default `spinner` animation go through `innerHTML`. Probe output
  (`node /tmp/probe_spinner_sink.mjs`, message `Reading: <img src=x onerror="document.title=1">`):

  ```
  --- wave (chat.js:2042 research spinner) ---
    innerHTML writes : 2 "Reading: <img src=x onerror=\"document.title=1\"> ▁▂▃"
    textContent writes: 0 []
    raw "<" survived into innerHTML: true
  --- default (chat.js:6051 reconnect spinner) ---
    innerHTML writes : 2 "Reading: <img src=x onerror=\"document.title=1\"> ▁▂▃"
    raw "<" survived into innerHTML: true
  --- whirlpool (control) ---
    innerHTML writes : 0
    textContent writes: 2 ["","Reading: <img src=x onerror=\"document.title=1\">"]
  ```

  The probe installs the same browser stubs the repository's own
  `tests/test_spinner_stops_when_never_attached_js.py` uses and imports the real module, so the
  sink is the shipped code path, not a reimplementation. That pass did not run a browser.
- **Impact:** any authenticated user who runs Deep Research with web search enabled — research is a
  per-user privilege that defaults on (`routes/chat_routes.py:1562`
  `_privs.get("can_use_research", True)`), not an admin feature — has attacker-authored markup
  parsed into the Odysseus origin as soon as a hostile page's title appears among the results. The
  attacker only has to get a page into the result set for the user's query and put the payload in
  its `<title>`; the spinner re-assigns `innerHTML` on every animation frame (150 ms), so the
  payload re-parses for as long as the reading phase lasts.

  The app's CSP refuses the inline handler and does not refuse a frame. The chat page is served by
  `core/middleware.py:141-147` with `script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net`, so
  an injected `<img onerror>` or `<script>` does not run. An injected `<iframe srcdoc>` whose
  document loads a script from `cdn.jsdelivr.net` does: the frame inherits the page's origin and
  policy, and that CDN serves any public npm package or GitHub file. The script then acts with the
  user's session against every API the user can call, which for an admin includes the shell routes.
  The policy defect is its own finding in `core-auth-session`.

  One link is not measured: whether a given search provider returns a markup-bearing title of about
  75 characters unmodified. The providers' JSON titles are passed through as read
  (`services/search/providers.py:178`, `:346`, `:442`), and nothing in this repository strips them.

  The `error` phase has the same problem through `rp.message`, which carries the provider exception
  text (`src/deep_research.py:329`, reached after `max_empty_rounds` consecutive empty rounds, with
  `_last_search_error = f"{prov}: {e}"` at `:591`) — a string that can include an upstream response
  body.
- **Re-review (2026-10-05):** raised from medium to high. The first pass reasoned that the CSP
  stops execution and did not run a browser. In headless Chromium, with `spinner.js` imported
  unmodified, the app's policy string and a title carrying an `<iframe srcdoc>` whose document
  loads `https://cdn.jsdelivr.net/npm/lodash@4.17.21/lodash.min.js`, the CDN script ran in a frame
  whose origin is the page's. The `<img onerror>` title gave no execution. The 150 ms re-parse did
  not prevent the load. The probe and its output are in the policy finding in `core-auth-session`.
- **Fix:** make the message text, not markup, at the sink: in `spinner.js` `updateDisplay`, build
  the frame and message as two nodes (`element.textContent = display` plus a text-only frame span,
  or `element.replaceChildren(frameText, msgText)`), which also removes the re-parse per frame. If
  the sink must stay, escape the message at the two `reading` call sites (`chat.js:3153`, `:6068`)
  and the `error` one (`:3159`) with `uiModule.esc`, but fixing the sink is the change that holds.

### [SECURITY] Custom theme names are stored from the model's `ui_control` call and rendered unescaped into slash replies

- **Location:** `static/js/slashCommands.js:1468-1470` and `:1498-1500` (`customNames.join(', ')`
  into `slashReply`, which assigns `innerHTML` at `:320`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_cmdTheme` builds the usage and the unknown-theme reply from the custom theme
  store's keys and interpolates them without escaping, in a file where every other server-derived
  string goes through `ctx.esc` (compare `:1139`, `:1526`, `:1575`, `:1640`, `:1899`):

  ```js
  // :1465-1470
  const custom = tm && tm.getCustomThemes ? tm.getCustomThemes() : {};
  const customNames = Object.keys(custom);
  ...
  const customLabel = customNames.length ? `\nCustom: ${customNames.join(', ')}` : '';
  slashReply(`Usage:\n ... Presets: ${presetNames.join(', ')}${customLabel}`);
  ```

  ```js
  // :1496-1500
  if (!colors) {
    const customLabel = customNames.length ? ` | Custom: ${customNames.join(', ')}` : '';
    slashReply(`Unknown theme "${name}". Available: ${presetNames.join(', ')}${customLabel}`);
  ```

  Those names come from the model. `ui_control` is a normal agent tool
  (`src/tool_schemas.py:471`, `src/tool_index.py:61`, dispatched at
  `src/tool_execution.py:1169`), and its `create_theme` action passes the name through
  unvalidated — `src/tool_schemas.py:1566-1573` builds `content = f"create_theme {theme_name} ..."`
  from the tool argument, and `src/ai_interaction.py:759` derives the name with
  `parts[1].lower().replace(" ", "-")` and no character check, so a name such as
  `<img/src=x/onerror=alert(1)>` (no spaces needed) survives. The client then persists it as an
  object key:

  ```js
  // chatStream.js:114-134 (ui_control create_theme)
  var name = uiData.theme_name || 'custom';
  ...
  if (tm2.saveCustomTheme) tm2.saveCustomTheme(name, colors2, Object.keys(opts).length ? opts : undefined);
  ```

  ```js
  // theme.js:91-109 — stored as a localStorage key and synced to the server
  ct[name] = entry;
  _saveCustomThemes(ct);
  _syncCustomThemesToServer(ct);   // PUT /api/prefs/custom-themes
  ```

  The same value reaches a second, more automatic sink in `theme.js:661-668`, which renders custom
  swatches with `data-theme="${name}"` and `<span class="theme-swatch-name">${name}</span>` via
  `innerHTML` whenever the theme grid is built. `theme.js` is `static-js-rest`'s path; it is cited
  here as reachability, not claimed as this section's finding.
- **Impact:** untrusted content that steers the model (a web page, an email, a tool result) plants
  a payload in the user's persisted theme store with one `create_theme` call. It is parsed when the
  user runs bare `/theme` or `/theme <unknown>` in this section's sink, and — more likely, and
  without any slash command — when the theme grid renders, which is the same origin-wide
  consequence as finding 1. The user sees a "custom theme" they never created.
- **Re-review (2026-10-05):** stands at medium, with two corrections. A name carrying an `<iframe
  srcdoc>` runs script from `cdn.jsdelivr.net` in the app origin (measured for the theme grid; see
  the policy finding in `core-auth-session`), so the consequence is execution, not markup only.
  And the model cannot be steered freely: `ui_control` carries `ToolEffect.UI_SIDE_EFFECT`
  (`src/tool_capabilities.py:226-231`), which `decision_for` blocks once untrusted content is in
  the run unless the user approves the call (`:553-564`, `:654-684`). The reach is a call made
  before the gate arms, or a theme-creation prompt the user approves. That gate is why this is not
  high.
- **Fix:** escape the names where they are interpolated (`customNames.map(ctx.esc).join(', ')` in
  both places), and validate the name at the boundary: restrict `theme_name` to
  `[a-z0-9_-]+` in `src/ai_interaction.py`'s `create_theme` branch (and in `theme.js`
  `saveCustomTheme`) so a markup-bearing key can never be stored in the first place.

### [SECURITY] The provider-reported model id is interpolated unescaped into two chat popups

- **Location:** `static/js/chatRenderer.js:2109` and `:2195`, value built at `:2048`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `displayMetrics` reads the model out of the server's metrics payload and drops it
  into `innerHTML` twice, while the same file escapes the same value in the model picker's popup
  (`:750` `uiModule.esc(modelName.split('/').pop())`):

  ```js
  // chatRenderer.js:2048
  const model = metrics.model || 'Unknown';
  ```

  ```js
  // :2106-2111 — Message Stats popup
  popup.innerHTML = `
    <div style="font-weight:600;margin-bottom:6px;color:var(--fg);">Message Stats</div>
    <div><span class="ctx-label">Model</span> ${model.split('/').pop()}</div>
  ```

  ```js
  // :2180, :2193-2195 — Context Window popup
  const modelShort = model.split('/').pop();
  ...
  <div><span class="ctx-label">Model</span> ${modelShort}</div>
  ```

  `metrics.model` is the *provider's* model identifier, not the id the user picked:
  `src/agent_loop.py:6391` passes `model=actual_model` into the metrics dict, `actual_model` comes
  from the streamed `model_actual`/usage events, and `src/llm_core.py:444-451`
  (`_annotate_usage_model` → `_reported_model_name`, which only strips whitespace at `:431-433`)
  copies the upstream response's `model` field into `usage["model"]` unchanged. The payload reaches
  the renderer through the metrics event (`static/js/chat.js:5124`
  `if (metricsData) displayMetrics(holder, metricsData);`, also `:3470`, `:3490`, `:4247`).
- **Impact:** a user who points Odysseus at an OpenAI-compatible endpoint that reports a
  markup-bearing `model` field has that markup parsed into the app origin when they open the metrics
  popup on a response. The endpoint already sees that user's prompts, so the added capability is
  "the endpoint can also author markup in the browser" — a real widening. An injected inline
  handler is refused by the nonce policy (`core/middleware.py:141-147`); an injected
  `<iframe srcdoc>` that loads script from `cdn.jsdelivr.net` is not, as the policy finding in
  `core-auth-session` measures, so the endpoint can run script in the user's session. It requires the user or their admin to have configured that endpoint. The two
  popups are also inconsistent with the escaping used
  everywhere else in the file, which is what makes this an oversight rather than a decision — the
  repository already pins that discipline for this surface in
  `tests/test_chat_tool_screenshot_xss.py` ("Streaming tool labels are escaped before inner_html":
  `'<span class="agent-thread-tool">${esc(toolLabel)}</span>' in chat`).
- **Re-review (2026-10-05):** stands at low. The impact was corrected: the first pass said the
  policy rules out code execution, and a `srcdoc` frame is not ruled out. Low is kept because the
  input is the model id of an endpoint the user or an admin configured.
- **Fix:** escape at both interpolations (`uiModule.esc(model.split('/').pop())`, as `:750` already
  does), or set the model row with `textContent` after the popup is built.

### [ERROR-HANDLING] The send path adopts an unvalidated URL-hash session id, and `selectSession` never checks the history response status

- **Location:** `static/js/chat.js:400-407` (the unvalidated id), `static/js/sessions.js:1970-1980`
  (the unchecked fetch), `:1858` and `:1868` (the id is adopted and persisted), `:1935` (the id is
  also interpolated into a CSS selector); the silent failure lands at `static/js/chat.js:2098-2104`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the startup and `hashchange` paths validate the hash against the session list
  (`sessions.js:1746` `hashId && activeSessions.some(s => s.id === hashId)`, `:2541-2546`
  `const target = sessions.find(...); if (target) selectSession(hashId);`), but the send-time
  adoption path does not — it takes any hash that is not one of the known non-session prefixes
  (`chat.js:383-392`) and passes it straight to `selectSession`:

  ```js
  // chat.js:399-407
  const activeRowId = document.querySelector('.list-item.active-session[data-session-id], ...')?.dataset?.sessionId || '';
  const hashId = _hashSessionCandidate();
  const lastSelectedId = String(window.__odysseusLastSelectedSessionId || '').trim();
  const targetId = activeRowId || hashId || lastSelectedId;
  ...
  await sessionModule.selectSession(targetId, { keepSidebar: true, showLoading: false });
  ```

  `selectSession` then sets the id and persists it before it knows the session exists, and treats
  any history response as a success:

  ```js
  // sessions.js:1858-1870
  currentSessionId = id;
  ...
  Storage.set('lastSessionId', id);      // _meta is undefined here, so not treated as transient
  ```

  ```js
  // sessions.js:1970-1980
  const res = await fetch(_historyUrl(id, { limit: _historyPageLimit() }));
  const data = await res.json();          // no res.ok check
  ...
  msgHistory = data.history || [];
  ```

  `/api/history/{id}` answers a missing session with `HTTPException(404, ...)`
  (`routes/history/history_routes.py:156-158`), whose JSON body parses fine and leaves
  `data.history` undefined — so a deleted or never-existent id renders as an empty chat with no
  error. The id is also interpolated into a selector at `:1935`
  (`.list-item[data-session-id="${id}"]`), so a hash containing a quote throws a `SyntaxError`
  that is caught by the enclosing handler at `:2133` and shown as "Failed to load this chat" —
  after `currentSessionId` and `lastSessionId` have already been set to that string.
- **Impact:** a bookmark, back-button entry or `#<id>` URL for a session that no longer exists (or
  any bogus hash) leaves the composer attached to a session that is not there. The user's next
  prompt is accepted by the UI and then dropped by the 404 branch below, with the user bubble left
  on screen and no explanation; the id is re-persisted as `lastSessionId` on every such
  `selectSession`. It self-heals on a full reload (`sessions.js:1753` re-validates `savedId` against
  the list), so the damage is confined to the tab where it happened.
- **Fix:** check the response status in `selectSession` (`if (!res.ok) { throw ... }` before
  `res.json()`, so the existing catch reports it and the id is not adopted), and validate the
  candidate in `_adoptOpenedSessionBeforeAutoCreate` the way `loadSessions` does
  (`sessions.some(s => s.id === targetId)`), falling through to the normal new-chat path when it
  does not resolve.

### [ERROR-HANDLING] A 404 from `/api/chat_stream` discards the turn with no message

- **Location:** `static/js/chat.js:2098-2104`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the send path removes the assistant bubble, reloads the sidebar and returns without
  telling the user anything:

  ```js
  if (!res.ok) {
    clearResponseTimeout();
    if (res.status === 404) {
      // Session was deleted (e.g. by AI) — reload and go to welcome
      holder.remove();
      if (sessionModule) await sessionModule.loadSessions();
      return;
    }
  ```

  Every other failure branch below it renders the error into the bubble
  (`typewriterInto(holder.querySelector('.body'), errText)`, `:2131`). The 404 branch is reachable
  without the phantom-session path above: the model can delete the session the user is typing into
  (`manage_session`), and the delete happens server-side while the client still holds that id.
- **Impact:** the user's prompt — already added to the transcript as an optimistic user bubble — is
  never sent and never stored, and the only visible effect is that the assistant bubble disappears.
  Typing a new prompt into a session that the model just deleted produces the same silence, so the
  user retypes into a session that keeps failing.
- **Fix:** keep the recovery but make it visible and clean up the optimistic bubble: show a toast
  ("This chat was deleted — starting a new one"), clear the composer state for that turn, and route
  to the new-chat view instead of silently returning.

### [FOOTGUN] The arrow-recall capture listener swallows the slash popup's arrow keys

- **Location:** `static/js/composerArrowUpRecall.js:80-85` (registered capture-phase at `:168`) and
  `static/js/slashAutocomplete.js:269-278`
- **Severity:** low
- **Disposition:** next
- **Evidence:** both modules listen for `keydown` on the same textarea. The recall handler is
  registered in the capture phase and calls `stopImmediatePropagation`:

  ```js
  // composerArrowUpRecall.js:80-85
  composer.addEventListener('keydown', (e) => {
    if (e.key !== 'ArrowUp' && e.key !== 'ArrowDown') return;
    if (e.shiftKey || e.altKey || e.ctrlKey || e.metaKey) return;
    if (e.isComposing) return;
    if (typeof window !== 'undefined' && window._ghostAutocomplete?.isActive?.()) return;
  ```

  ```js
  // composerArrowUpRecall.js:113-115 — reached when the composer is empty or exactly matches a
  // prompt in this chat
  e.preventDefault();
  e.stopPropagation?.();
  e.stopImmediatePropagation?.();
  ```

  ```js
  // composerArrowUpRecall.js:168
  }, true);
  ```

  The popup's arrow navigation is a plain (bubble-phase) listener on the same element
  (`slashAutocomplete.js:269-278`) and has no guard against the recall handler having already
  acted. For a `keydown` whose target is the composer itself, the capture listener runs before the
  bubble one, so `stopImmediatePropagation` from the recall handler cancels the popup's handler —
  the same class of interference the codebase already documented for two capture listeners on this
  element (`static/app.js:3886-3889`, issue #5862). The recall handler only acts when the trimmed
  composer value is empty or `history.findIndex((item) => norm(item) === currentValue)` matches, so
  the collision needs the composer to hold exactly one of the chat's previous user messages —
  i.e. the user retypes a command or prompt they already sent, which is also the case where the
  popup is showing.
- **Impact:** with the popup open and the composer holding a previously sent prompt that starts
  with `/`, ArrowUp and ArrowDown move through prompt history instead of the command list, and the
  composer text is replaced by an older prompt. The popup stays visible and re-renders from the new
  text, so the user sees the menu react to nothing. I could not confirm the ordering in a browser
  during this pass; it follows from the DOM event dispatch order for listeners on the target
  (capture before bubble), which I could not execute here.
- **Fix:** give the recall handler the same deference it already gives the ghost autocomplete
  (`if (document.getElementById('slash-autocomplete')?.style.display === 'block') return;`), or
  expose a `slashModule.isPopupVisible()` check; alternatively have the popup register its keydown
  in the capture phase with a lower registration priority and consume the keys it handles.

### [DUP] The reply-prefix list is declared three times in `chat.js`, identically

- **Location:** `static/js/chat.js:2653` (`_rpStarts`), `:2971` (`_replyPrefixes`), `:4101`
  (`_rs2`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the same 20-entry list and the same two-step matching logic (line scan, then an
  inline `[.!?]\s*` regex with an `m.index > 20` guard) appear in three places — the non-tag
  thinking/reply splitter at `:2653-2667`, the streaming "is this still reasoning" check at
  `:2971-2995`, and the final-response extractor at `:4101-4115`. A script that extracts and
  compares all copies shows they are byte-identical, and that two further copies exist outside this
  section's files:

  ```
  $ python3 /tmp/probe_reply_prefixes.py
  chat.js:2653: n=20
  chat.js:2971: n=20
  chat.js:4101: n=20
  markdown.js:319: n=20
  liveThinkingThrottle.js:33: n=20
  chat.js:2653 identical set: True | identical order: True
  chat.js:2971 identical set: True | identical order: True
  chat.js:4101 identical set: True | identical order: True
  markdown.js:319 identical set: True | identical order: True
  liveThinkingThrottle.js:33 identical set: True | identical order: True
  ```

  `liveThinkingThrottle.js:33` is this section's file (`REPLY_PREFIX_SOURCE`, the regex form) and
  `markdown.js:319` is `static-js-rest`'s; the three `chat.js` copies are the ones that can drift
  silently.
- **Impact:** the streaming path and the finalization path must agree for a message to be split
  the same way live and after the fact. Adding a greeting or prefix for a new model to one copy
  (the obvious edit, since each sits next to its own comment) makes the stream show text as
  reasoning that finalization then renders as the reply — or the reverse, which is the "thinking
  leaked into the bubble" bug class these heuristics exist to prevent. Nothing fails loudly: the
  lists are only compared to model output.
- **Fix:** export one list (and its two derived regexes) from `liveThinkingThrottle.js` — which
  already owns `REPLY_PREFIX_SOURCE`, `REPLY_LINE_RE` and `REPLY_INLINE_RE` — and import it in
  `chat.js` at all three sites, deleting the local copies; `markdown.js` can consume the same
  export instead of its own list.

### [DEAD-CODE] The send path builds a status string that is never read

- **Location:** `static/js/chat.js:2017-2029`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `loadingText` is assigned in all three branches and never used again —
  `grep -c loadingText chat.js` returns 4, all of them writes:

  ```js
  // chat.js:2017-2029
  let loadingText = 'Initializing...';

  if (el('web-toggle').checked && !_isAgent) {
    const _searchLabel = searchModule ? searchModule.getProviderLabel() : 'web';
    loadingText = `Searching via ${_searchLabel}...<br>
                   <span style="font-size: 0.9em; opacity: 0.8;">
                   Query: "${msg.substring(0, 50)}${msg.length > 50 ? '...' : ''}"<br>
                   Fetching top results...</span>`;
  } else if (el('research-toggle').checked) {
    loadingText = 'Deep research mode active...';
  } else {
    loadingText = 'Processing request...';
  }
  ```

  The status text the user actually sees is set on the spinner immediately below
  (`:2048-2057`, `spinner.updateMessage(...)`).
- **Impact:** dead weight in the hottest function in the file, and a trap: the string is shaped as
  HTML (`<br>`, an inline style) and interpolates the user's own prompt
  (`msg.substring(0, 50)`) without escaping, so re-wiring it into the bubble as it was presumably
  once wired (`holder.querySelector('.body').innerHTML = loadingText`) re-introduces a
  self-inflicted markup injection. It is also the reason the pre-spinner "initializing" state has
  no mode-specific text — the assignments look live to a reader skimming the send path.
- **Fix:** delete the block and let the spinner messages at `:2048-2057` be the only status source;
  if the mode-specific text is wanted, pass it to `spinner.updateMessage` (escaped or via
  `textContent`).
