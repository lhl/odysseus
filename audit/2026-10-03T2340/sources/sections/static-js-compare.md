# static: model comparison UI

## Overview

The ten modules under `static/js/compare/` are the model-comparison tool:

- `index.js` is the orchestrator (selector entry, `[CMP]` session creation, run/teardown, export)
- `selector.js` the model/provider picker and the pre-start probe
- `stream.js` the SSE pump into panes
- `panes.js` the pane lifecycle (add/remove/swap/reroll/expand/preview)
- `vote.js` and `scoreboard.js` the voting and history surfaces
- `probe.js` the toolbar Probe button
- `models.js` the `/api/models` fetch and model classification
- `state.js` the shared mutable state
- `icons.js` the SVG icons, eval prompts and storage keys

This section covers what these modules send to and render from the compare endpoints, not the
endpoints themselves. Three groups of code belong to other sections:

- The endpoints and their gates belong to `routes-models`, `routes-rest-*` and `core-auth-session`:
  - `/api/probe-selected`, `/api/models`, `/api/session`
  - `/api/chat_stream`, `/api/search/query`, `/api/compare/record`
- The markdown renderer the panes write model output through is `static-js-rest` (`markdown.js`)
  and `static-js-chat` (`chatRenderer.js`, which also owns the `getModelCost`, `renderAskUserCard`
  and `safeDisplayImageSrc` helpers `stream.js` imports).
- The `[CMP]` blind-mode naming contract is `routes-sessions`; its redaction tests are cited below
  rather than restated.

Security provenance of the probe path, which this section was asked to settle: **no API key, bearer
token or Authorization header exists anywhere in `static/js/compare/`** — `grep -rn
"api_key\|apiKey\|Authorization\|Bearer" static/js/compare/` returns no match — and both probe call
sites send only `{endpoint_id, model, endpoint, with_tools}` to the same-origin
`/api/probe-selected` with `credentials: 'same-origin'` (`probe.js:45-49`, `selector.js:1009-1013`),
so the request carries the session cookie and nothing else. The `endpoint` value is the chat URL the
server itself returned in `GET /api/models` (`routes/model_routes.py:1587`, built by
`build_chat_url`), not something the user types in compare.

Browser storage holds model ids, endpoint chat URLs, endpoint names, the shuffle-pool exclusions and
vote records (display names, prompt text, winner, blind flag, per-model costs) — no credentials. The one trust decision on that URL is
server-side: when `endpoint_id` does not resolve, `/api/probe-selected` falls back to the
client-supplied `endpoint` as the probe target (`routes/model_routes.py:1821-1828`). The route is
admin-only (`:1799`) and an admin can already register an arbitrary endpoint URL through
`POST /api/model-endpoints`, so the fallback grants no capability that caller class did not already
have; it is recorded in the rejected-hypotheses ledger rather than reported as a finding.

## Coverage

**Read fully:** all ten assigned files (5,410 lines).

| File | Lines |
| --- | ---: |
| `index.js` | 1,545 |
| `selector.js` | 1,335 |
| `stream.js` | 919 |
| `panes.js` | 817 |
| `vote.js` | 254 |
| `scoreboard.js` | 223 |
| `models.js` | 104 |
| `probe.js` | 78 |
| `icons.js` | 77 |
| `state.js` | 58 |

**Read partially:** the boundary code the findings rest on.

- `routes/model_routes.py` at `api_models`' item construction (`:1584-1601`) and `probe_selected`
  (`:1796-1835`)
- `core/middleware.py` at `require_admin` (`:57-82`)
- `src/endpoint_resolver.py` at `normalize_base` (`:225-234`)
- `routes/chat_routes.py` at the research start (`:1739-1747`)
- `src/deep_research.py` at the provider override (`:563-573`)
- `static/js/ui.js` at `esc` (`:781-788`)
- `static/js/escMenuStack.js` at its exports and the dismissal contract (first 60 of 102 lines —
  `panes.js` uses `bindMenuDismiss`)
- `static/index.html` at the composer mode toggle (`:1197-1206`)
- `static/js/ui_visibility.js` at the compare visibility key (`:22`)
- `static/js/chat.js`, `static/js/sessions.js` and `static/js/models.js` at their
  `window.compareModule` call sites
- `specs/compare.md` in full
- the six compare test suites plus `tests/test_esc_menu_stack_js.py` for what is already pinned

**Not read:**

- every other module in `static/js/`
- the compare, session, search and model routes beyond the handlers named above
- `src/research_handler.py` and `src/deep_research.py` beyond the provider selection
- the Bombadil harness
- every other section's paths

Line numbers are the working tree at `2992bf6d368a` (clean apart from this run's untracked `audit/`
directory).

**Checks run:** the six suites matching this surface, discovered with `ls tests | grep -iE 'compare'`:

- `test_blind_compare_redaction.py`
- `test_compare_ask_user_routing.py`
- `test_compare_endpoint_owner_scope.py`
- `test_compare_js.py`
- `test_compare_routes_shim.py`
- `test_compare_stop_disconnect_poll.py`

Also `tests/test_esc_menu_stack_js.py`, which pins the dropdown-dismiss registry `panes.js` uses.
Run:

```
$ venv/bin/python -m pytest -q tests/test_blind_compare_redaction.py \
    tests/test_compare_ask_user_routing.py tests/test_compare_endpoint_owner_scope.py \
    tests/test_compare_js.py tests/test_compare_routes_shim.py \
    tests/test_compare_stop_disconnect_poll.py tests/test_esc_menu_stack_js.py
.......................................                                  [100%]
39 passed, 1 warning in 0.48s
```

`tests/test_compare_js.py` drives `state.js` and `icons.js` through `node --input-type=module` (node
24.16.0 is present, so its five cases ran rather than skipping). Four of the six compare suites
assert on source text rather than behaviour (`test_compare_ask_user_routing.py`) or on the
server-side detached-run manager (`test_compare_stop_disconnect_poll.py`), so no pane-lifecycle
behaviour in this section is executed by the suite — the findings below rest on reading the code and
on the two probes quoted in them. `tests/bombadil-spec.ts` is a browser spec for login/chat that
needs a running app and the Bombadil harness — not run. Two throwaway probes under `/tmp`
(`/tmp/cmp-probe/esc_verbatim.mjs`, `/tmp/cmp-probe/esc_probe.mjs`) reproduce the escaping defect
quoted below; neither is part of the target tree.

### [BUG] Switching the composer to Chat or Agent after a search-mode comparison leaves every pane unable to stream

- **Location:** `static/js/compare/index.js:262-267` (search mode builds no sessions),
  `static/js/compare/index.js:970-972` and `static/js/compare/index.js:980` (the chat path
  iterates that empty array), with the switch at `static/js/compare/index.js:104-106` and
  `static/js/compare/index.js:301-310`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_buildCompareUI` creates a `[CMP]` session per pane only when the compare type is
  not `search`, and otherwise leaves the array empty for good:

  ```js
  // :242-265
  // 1. Create sessions (skip for search mode — no LLM sessions needed)
  if (state._compareMode !== 'search') {
    ...
    state._paneSessionIds = sessionIds;
  } else {
    state._paneSessionIds = [];
  }
  ```

  The chat/agent branch of `_executeCompare` then drives the panes off that array — it never creates
  a session and never checks its length:

  ```js
  // :968-972
  if (state._parallel) {
    // Run all panes at once
    await Promise.all(state._paneSessionIds.map((sid, i) =>
      streamToPane(i, sid, message, aiElements[i], { searchContext: sharedSearchContext, timeout: runTimeout })
    ));
  ```

  The composer's Agent/Chat toggle stays live during compare — step 5 of `_buildCompareUI` unlocks it
  (`_modeToggle.style.pointerEvents = ''`, `:318-319`) and re-wires both buttons with a capture-phase
  listener that calls `_syncCompareModeFromToolbar` (`:303-310`), which sets
  `state._compareMode = mode === 'agent' ? 'agent' : 'chat'` (`:106`). Nothing else touches
  `_paneSessionIds` afterwards: the only writers are this build (`:262`, `:264`), `panes.js:399`
  (one push per added pane) and `deactivate` (`index.js:181`).
- **Impact:** a user who picks Search in the model selector (the selector's type tabs are the only
  way to reach search mode, `static/js/compare/selector.js:350-366`), runs a comparison, and then
  clicks Agent or Chat in the composer gets a silent dead end. Each send appends the user bubble and
  a "Processing..." spinner (`static/js/compare/index.js:905-927`), `Promise.all([])` resolves at
  once, no request is issued, no error is shown, and the `finally` sees no live controllers
  (`static/js/compare/index.js:1012`) so the send button returns to "send".
  The panes keep spinning until the user closes compare, which reloads the page. Adding a pane after
  the switch makes it worse rather than better: `_addPane` filters `state._cachedModels` by
  `state._compareMode` (`panes.js:280-282`), which now matches, so the new pane's session is the only
  entry in the array (`panes.js:398-401`) and the map hands it to pane 0 — the added model's answer
  appears under pane 0's title and panes 1..n get nothing.
- **Fix:** before streaming in the chat/agent branch, create a session for every pane index missing
  from `state._paneSessionIds` (the loop is already in `_buildCompareUI:245-261`), or make
  `_syncCompareModeFromToolbar` refuse to leave search mode while compare is active. Session ids and
  models must stay paired either way.

### [ERROR-HANDLING] The probe never checks the response status, so a non-admin user sees every model reported as failed

- **Location:** `static/js/compare/probe.js:45-59` and `static/js/compare/selector.js:1009-1015`
- **Severity:** low
- **Disposition:** next
- **Evidence:** neither call site looks at `res.ok`; both parse the body and treat "no `results`
  key" as a model failure:

  ```js
  // probe.js:45-52
  const res = await fetch(`${state.API_BASE}/api/probe-selected`, {
    method: 'POST', credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ models: [{ endpoint_id: m.endpointId || '', model: m.model, endpoint: m.endpoint || '' }] }),
  });
  const data = await res.json();
  const result = (data.results || [])[0];
  if (result && result.status === 'ok') {
  ```

  `selector.js:1014-1015` is the same shape with the fallback `{ status: 'fail', error: 'No
  response' }`. The endpoint is admin-only: `probe_selected` opens with `require_admin(request)`
  (`routes/model_routes.py:1799`), which raises `HTTPException(403, "Admin only")` unless auth is
  disabled or the in-process tool token is presented (`core/middleware.py:57-82`). FastAPI answers
  that with a JSON body (`{"detail": "Admin only"}`) that has no `results` key, so it lands in the
  failure branch. Nothing in the compare modules consults `window._isAdmin` — `grep -rn "admin"
  static/js/compare/*.js` returns no match — while the Probe button is created unconditionally
  (`index.js:372-378`) and the selector probes before it will start (`selector.js:906-918`). Compare
  itself is not admin-gated; it is a per-user visibility switch (`static/js/ui_visibility.js:22`,
  `tool-compare`).
- **Impact:** on an instance with authentication enabled, an ordinary user who clicks Probe gets one
  `<model> failed: unknown` toast per model (`static/js/compare/probe.js:58`), and one who starts a
  comparison gets a probe card with every row failed, the detail line "No response"
  (`static/js/compare/selector.js:1055-1058`) and only "Go Back" / "Start Anyway"
  (`static/js/compare/selector.js:1273-1284`). The comparison still runs if they choose
  "Start Anyway", so this is a misleading dead end rather than a blocked flow — but the same missing
  status check also turns a genuine 401, 500 or proxy error into "the model failed" for an admin, and
  `_checkUnprobed`'s per-model catch swallows a non-JSON body entirely
  (`static/js/compare/probe.js:60-62`).
- **Fix:** check `res.ok` before parsing and report the status, e.g.
  `if (res.status === 403) return { status: 'fail', error: 'Probe requires an admin account' };`, and
  hide the Probe button (or label it as admin-only) when `window._isAdmin` is false.

### [BUG] A search-mode synthesis session is orphaned whenever the synthesis stream is stopped

- **Location:** `static/js/compare/stream.js:222-290` (`_runSynthForPane`), at
  `static/js/compare/stream.js:242` and `static/js/compare/stream.js:285`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the temporary session is created at `:234`, and its only cleanup is the last
  statement of the `try` block:

  ```js
  // :284-289
  // Cleanup temp session
  fetch(`${state.API_BASE}/api/session/${createData.id}`, { method: 'DELETE' }).catch(() => {});
  } catch (e) {
    if (spinner) spinner.stop();
    synthBody.innerHTML = '<div style="color:var(--color-error);font-size:0.85em;">Synthesis failed: ' + escapeHtml(e.message) + '</div>';
  }
  ```

  An abort throws out of the read loop (`:256-258`, signal attached at `:247`) straight into that
  catch, which never deletes the session. Aborting is an ordinary user action: the synth controller
  is appended to `state._abortControllers` (`:242`), and every stop path aborts that array —
  `stopAll` (`panes.js:38-40`), the send button acting as stop (`index.js:577-581`), closing compare
  (`index.js:159-161`), and voting while a pane is still streaming (`vote.js:169-170`). Compare's own
  teardown cannot recover it either: `deactivate` deletes only `state._paneSessionIds`
  (`index.js:174-176`) and the `beforeunload` beacon sends only those ids (`index.js:58-65`), while
  search mode leaves that array empty by construction (`:264`). The synthesis stream is also never
  status-checked (`:243-250`): a non-2xx `/api/chat_stream` answer contains no `data:` lines, so the
  pane ends with the spinner stopped and an empty "Analysis" bubble while the session is deleted as
  if the run had succeeded.
- **Impact:** stopping a search comparison (or voting, or closing compare) while a pane is analysing
  leaves one session per pane named "Synthesis" in the session list, holding the partial report and
  the search results. Compare is otherwise careful to delete its sessions, so this is the one path
  that leaves litter behind, and it survives both the close-compare reload and a refresh.
- **Fix:** track `createData.id` and delete it from a `finally` (or an `AbortController` `abort`
  handler), keeping the success-path delete only if the `finally` cannot run there; add
  `if (!streamRes.ok) throw new Error('HTTP ' + streamRes.status);` after `:248`.

### [BUG] Research mode's per-pane search-provider picker stores a value nothing reads, in the slot search mode uses for its synthesis model

- **Location:** `static/js/compare/selector.js:757-772`, against `static/js/compare/stream.js:383-384`
  and `routes/chat_routes.py:1739-1747`
- **Severity:** low
- **Disposition:** next
- **Evidence:** in research mode the picker writes a bare provider id into `state._searchSynthModels`:

  ```js
  // selector.js:762-771
  researchProviders.forEach((p, pi) => {
    const optEl = document.createElement('option');
    optEl.value = p.id;
    optEl.textContent = p.label;
    ...
  provSelect.addEventListener('change', () => { state._searchSynthModels[idx] = provSelect.value; });
  if (!state._searchSynthModels[idx]) state._searchSynthModels[idx] = provSelect.value;
  ```

  Nothing consumes it. The only execution-time readers of `_searchSynthModels` are the search branch
  of `_executeCompare` (`index.js:764`, `:831`) and the probe's provider phase
  (`selector.js:1186`); the research request carries no provider at all — `streamToPane` appends only
  `use_research=true` (`stream.js:383-384`) — and the route calls
  `research_handler.start_research(...)` without `search_provider` (`routes/chat_routes.py:1739-1747`),
  so the pipeline falls back to the `research_search_provider` / `search_provider` settings
  (`src/deep_research.py:567-571`). The two shapes also collide: search mode stores an object
  `{model, endpoint, endpointId, name}` in the same slot (`selector.js:612`, `:625`, `:631`) and
  dereferences it (`modelToUse.endpoint` / `modelToUse.model` at `stream.js:226-227`,
  `state._searchSynthModels[idx].model` at `selector.js:627`). `setModeTab` saves and restores
  `selections` per tab but not `_searchSynthModels` (`selector.js:350-353`), so picking a research
  provider and then switching to the Search tab leaves a string where an object is expected: the
  picker renders with an empty box (`selector.js:439-442` finds no match), the pre-start probe calls
  it "ok / No model" through the `!m.model` branch (`selector.js:1006-1007`), and the synthesis run
  posts `model=''` and `endpoint_url=''` (`stream.js:226-227`), which fails session creation and
  prints "Synthesis failed".
- **Impact:** in research compare the per-pane "Search provider" select is decorative — the choice is
  persisted to localStorage (`static/js/compare/models.js:43-44`) and used for nothing, so a user who
  picks a different provider per pane gets whatever the instance setting says. Switching the type tab
  to Search afterwards turns the synthesis pane into a session-creation error instead of an analysis.
- **Fix:** give research its own state key (`state._researchProviders[idx]`) or store the object shape
  the search branch uses and send it with the research request; and clear `_searchSynthModels` in
  `setModeTab` when the tab moves between search and research.

### [BUG] The endpoint name is HTML-escaped when display names are built and escaped again at every insertion point

- **Location:** `static/js/compare/models.js:33` (with `static/js/compare/vote.js:151`,
  `static/js/compare/vote.js:184-187`, `static/js/compare/vote.js:198-201`,
  `static/js/compare/index.js:452` and `static/js/compare/scoreboard.js:139`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_modelDisplayNames` returns an already-escaped fragment for the endpoint name:

  ```js
  // models.js:31-35
  return models.map(m => {
    const short = m.name || m.model.split('/').pop();
    if (nameCount[short] > 1 && m.endpointName) return short + ' (' + escapeHtml(m.endpointName) + ')';
    return short;
  });
  ```

  `escapeHtml` is `uiModule.esc`, which maps `& < > " '` to entities (`static/js/ui.js:781-788`), and
  every consumer escapes again or inserts the string as text. Measured with those two definitions
  extracted verbatim from `static/js/ui.js:781-788` (the module itself cannot be imported without a
  full DOM):

  ```
  $ node /tmp/cmp-probe/esc_verbatim.mjs
  {"endpointName":"OpenRouter & Friends <beta>",
   "after_modelDisplayNames":"model-x (OpenRouter &amp; Friends &lt;beta&gt;)",
   "after_vote_js_escape":"model-x (OpenRouter &amp;amp; Friends &amp;lt;beta&amp;gt;)",
   "vote_label_textContent":"model-x (OpenRouter &amp; Friends &lt;beta&gt;)"}
  ```

  The second escape is `vote.js:184-187` (the pane title after a vote) and `vote.js:151` (the same on
  reveal); `vote.js:198-201` writes the same string through `textContent`, which shows the entity
  literally too. The pane title is built the same way at `index.js:452` from `modelShorts`
  (`index.js:239`), and at `panes.js:412`, `:505`, `:610` and `:737` for the add/remove/swap/shuffle
  paths. The escaped form is what gets persisted: `_saveVote` stores `_modelDisplayNames(...)` in
  localStorage and posts it to `/api/compare/record` (`vote.js:104-113`, `:130-138`), the compare
  folder name is built from it (`index.js:165-166`), and the scoreboard escapes it once more for its
  model column (`scoreboard.js:139`).
- **Impact:** an endpoint whose *display name* contains `&`, `<`, `>` or a quote renders mangled —
  `&amp;` / `&lt;` appear literally in pane titles after a vote or reveal, in the per-pane AI role
  labels, in the `Compare:` session folder name, in the stored vote record and in the scoreboard's
  model column. Cosmetic only: escaping one layer early cannot produce XSS, and every consumer stays
  safe. Reachability is limited to endpoints whose name contains one of those characters and to a
  model id that appears on more than one endpoint (`nameCount[short] > 1`).
- **Fix:** return the raw name — `return short + ' (' + m.endpointName + ')';` — because all consumers
  escape or use `textContent`. Keep the escaping at the insertion sites, not in the display-name
  builder.

### [DUP] Two shared constants are declared twice, and the duplicate is the copy that gets used

- **Location:** `static/js/compare/stream.js:12` (with `static/js/compare/models.js:94`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `static/js/compare/icons.js:24` exports `WAVE_FRAMES`, and `probe.js:3` and
  `selector.js:6` import it; `static/js/compare/stream.js:12` declares a byte-identical private copy
  and animates the tool-block wave from it (`stream.js:546`, the only animation `stream.js` drives):

  ```js
  // stream.js:12
  const WAVE_FRAMES = ['▁▂▃', '▂▃▄', '▃▄▅', '▄▅▆', '▅▆▇', '▆▅▄', '▅▄▃', '▄▃▂'];
  // icons.js:24
  export const WAVE_FRAMES = ['▁▂▃', '▂▃▄', '▃▄▅', '▄▅▆', '▅▆▇', '▆▅▄', '▅▄▃', '▄▃▂'];
  ```

  The shuffle-pool key is the same story: `icons.js:30` exports `POOL_STORAGE_KEY` and `models.js:94`
  declares its own copy with the same value, which is the only one used (`models.js:97`, `:101`).
  `grep -rn "POOL_STORAGE_KEY" static/js/` shows icons.js's export has no importer — only
  `tests/test_compare_js.py` reads it, from icons.js.
- **Impact:** the animation strip lives in two files, and the three wave animations split across them
  (`probe.js` and `selector.js` use the imported copy; `stream.js` uses its own) can drift silently:
  editing `icons.js` leaves the tool-block wave on the old frames with no test failing. The storage
  key is pinned by a test against the copy nothing imports, so a typo in `static/js/compare/models.js:94`
  would pass the suite and orphan every user's exclusion list.
- **Fix:** import both from `icons.js` — `import { WAVE_FRAMES, POOL_STORAGE_KEY } from './icons.js';`
  — and delete the two local declarations.

### [DEAD-CODE] `_exportComparison` duplicates the markdown builder and has no caller

- **Location:** `static/js/compare/index.js:1157-1214`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `grep -rn "_exportComparison" --include=*.js --include=*.html .` (excluding
  `node_modules`) matches only the definition at `index.js:1157`. The export menu wires the three
  other paths (`index.js:1079-1081`), all of which call `_buildComparisonMarkdown` (`:1035`), added
  later with the same body — the pane loop at `:1173-1192` is the same logic as `:1048-1066`,
  including the grade-badge mark, the metrics line and the `## name` heading.

  ```
  $ grep -rn "_exportComparison" --include=*.js --include=*.html . | grep -v node_modules
  ./static/js/compare/index.js:1157:async function _exportComparison(btn) {
  ```
- **Impact:** 58 lines of duplicated rendering that nothing calls. Nothing breaks today; the cost is
  that a change to the export format has two places to edit and one of them is unreachable, so it
  will silently diverge (it already has: only `_buildComparisonMarkdown` is reachable from the menu).
- **Fix:** delete `_exportComparison`.
