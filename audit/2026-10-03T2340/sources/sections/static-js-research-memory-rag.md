# static: research, memory and search UI

## Overview

These seven files are the front end of four features: the Brain memory panel (`memory.js` — list,
filter, sort, inline edit, bulk delete, import/export, tidy), the deep-research panel and its job
queue (`research/jobs.js` owns the queue, the SSE stream and the pollers; `research/panel.js`
renders the panel, the job cards and the library), the live research graph
(`researchSynapse.js`), and the two search surfaces (`search-chat.js` is the Ctrl+K conversation
palette; `search.js` is the provider label the chat spinner reads).

Five of the seven display data a server or a model produced — `search.js` holds only a provider
label and `research/jobs.js` only queue state — so the first question this section answers is the
insertion path: which of them put model-, web- or document-controlled text into `innerHTML`. Only
`research/panel.js` interpolates that text into `innerHTML`; every other surface either builds
nodes and assigns `textContent` (`memory.js`, `rag.js`, `researchSynapse.js`) or escapes through
`uiModule.esc` first (`search-chat.js`). The research panel is also where the job lifecycle's
rendering cost lives, which is the section's second subject.

Boundary. The shared renderers these files call belong to other sections: `static/js/markdown.js`
(the `renderContent` / `mdToHtml` pair), `static/js/ui.js` (`esc`, `styledConfirm`) and
`static/js/spinner.js` are `static-js-rest`; the chat side of the research link and of the
`research_started` ui_event (`chat.js`, `chatStream.js`, `chatRenderer.js`) is `static-js-chat`;
`static/js/documentLibrary.js`, which renders the same research reports through `mdToHtml`, is
`static-js-documents-email`; the report text and progress events the panel displays come from
`services/research/research_handler.py` and `src/deep_research.py` (`services-research`,
`src-research-scheduling`), and the endpoints the queue polls from
`routes/research/research_routes.py` (`routes-rest-memory-personal-research`). This section covers
what these seven files do with that data, not whether the backend is sound.

## Coverage

**Read fully:** all seven assigned files (3,872 lines): `memory.js` (1,550),
`research/panel.js` (1,259), `research/jobs.js` (382), `researchSynapse.js` (225),
`search-chat.js` (223), `rag.js` (177), `search.js` (56).

**Read partially:** the modules and call sites each finding rests on — `static/js/markdown.js` at
`renderContent` (`:933-943`), `mdToHtml` (`:609-700`) and `sanitizeAllowedHtml` (`:180-300`),
because `panel.js` calls the first of them; `static/js/ui.js` at `esc` (`:779-788`) and
`styledConfirm` (`:584-624`); `static/app.js` at the boot sequence and the call sites of these
modules (`:49`, `:60`, `:851`, `:1011`, `:1689-1694`, `:3211-3222`, `:3705-3715`, `:4345-4346`);
`static/js/chatRenderer.js` at the hash-link delegate (`:1331-1421`); `static/js/chatStream.js` at
the `research_started` handler (`:145-190`); `routes/research/research_routes.py` at
`/api/research/active`, `/status`, `/stream` and `/result-peek` (`:212-300`, `:560-620`);
`services/research/research_handler.py` at `start_research`, `get_status` and
`_format_research_report` (`:52-150`, `:335-420`); and `src/deep_research.py` for the progress
events the panel consumes (the `_emit` call sites, `:273-353`, `:613`).

**Not read:** the rest of `markdown.js`, `ui.js`, `app.js`, `chat.js`, `chatRenderer.js`,
`chatStream.js`, `documentLibrary.js` and `research_routes.py`; `static/index.html` beyond the
element ids cited; `static/style.css`; and every other section's paths. Line numbers are the
working tree at `2992bf6d368a`; `git diff 2992bf6d368a -- static/js/memory.js static/js/rag.js
static/js/research/jobs.js static/js/research/panel.js static/js/researchSynapse.js
static/js/search-chat.js static/js/search.js` is empty, so the citations match the reviewed
commit.

**Checks run:** `node --check` (the JS half of the `check` gate in `.github/workflows/ci.yml`) on
all seven files — every one OK:

```
$ for f in static/js/memory.js static/js/rag.js static/js/research/jobs.js static/js/research/panel.js \
           static/js/researchSynapse.js static/js/search-chat.js static/js/search.js; do \
      printf "%-40s " "$f"; node --check "$f" && echo OK; done
static/js/memory.js                      OK
static/js/rag.js                         OK
static/js/research/jobs.js               OK
static/js/research/panel.js              OK
static/js/researchSynapse.js             OK
static/js/search-chat.js                 OK
static/js/search.js                      OK
```

No suite executes any of the seven modules; the closest coverage is
`tests/test_research_source_link_xss.py`, which asserts on `panel.js` as source text (it pins
`_safeSourceHref`). The suites that do cover the modules this surface calls and the endpoints it
polls were run in two batches:

```
$ venv/bin/python -m pytest -q tests/test_research_source_link_xss.py tests/test_markdown_rendering_js.py \
    tests/test_memory_add_submit_regression.py tests/test_notes_select_esc_listener_js.py \
    tests/test_panel_loader_js.py tests/test_search_provider_json.py tests/test_research_routes_shim.py \
    tests/test_research_chat_stream_owner.py tests/test_research_status_avg_duration.py \
    tests/test_research_session_id_validation.py tests/test_research_report_read.py
56 passed, 1 warning in 1.51s

$ venv/bin/python -m pytest -q tests/test_deep_research_date_context.py tests/test_deep_research_extraction_controls.py \
    tests/test_deep_research_parse_json_array_echo.py tests/test_deep_research_search_error.py \
    tests/test_deep_research_synthesis_resilience.py tests/test_research_handler_analyzed_urls.py \
    tests/test_research_handler_path_confinement.py tests/test_research_handler_raw_nondict.py \
    tests/test_research_handler_sources_nondict.py tests/test_research_probe_errors.py \
    tests/test_research_query_fallback.py tests/test_research_service.py tests/test_research_utils.py \
    tests/test_research_utils_low_quality_nonstring.py tests/test_research_routes_path_confinement.py \
    tests/test_research_owner_scope_routes.py tests/test_research_endpoint_owner_scope.py
153 passed, 3 warnings in 1.64s
```

Two throwaway Chromium probes under `/tmp` (pages served over `127.0.0.1`; the repository was not
modified): one reproduces the module duplication reported below, one calls the real
`static/js/markdown.js` with an HTML payload. Each probe's output is quoted where it is used. Two
symbols are unused with no behavioural effect, so they are recorded here rather than as findings:
`escapeHtml` (`memory.js:11`, an alias of `uiModule.esc` never called in the file) and
`_isDismissed` (`research/jobs.js:22`, never referenced).

### [BUG] The research panel and its job queue are each evaluated twice, so two panel instances share one set of DOM ids

- **Location:** `static/js/research/panel.js:4`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the same two modules are imported under two different URLs. `static/app.js:49`
  loads the panel with a cache-busting query, and the panel in turn loads the queue with one:

  ```js
  // static/app.js:49
  import * as researchPanelModule from './js/research/panel.js?v=20260630researchthumb';
  // static/js/research/panel.js:4
  import * as jobs from './jobs.js?v=20260630researchthumb';
  ```

  Two other files import the same modules with no query — `static/js/chatRenderer.js:1419`
  (`import('./research/panel.js').then(mod => {`) and `static/js/chatStream.js:164`
  (`import('./research/jobs.js').then(function(mod) {`). A module's URL is its identity, so each
  pair is two modules. Measured in headless Chromium against a fixture that mirrors this import
  graph (three files, served over `127.0.0.1:8733`, `/tmp/jsmodprobe3`):

  ```
  BROWSER RESULT: {"jobs_module_evaluations":2,"panel_module_evaluations":2,
                   "same_panel_instance":false,"jobs_seen_by_app_panel":0,
                   "jobs_seen_by_chatstream_adopt":1}
  ```

  So `chatStream.js`'s `adoptSession(rsid)` — added so an agent-started run appears without waiting
  for the poll — pushes into a `_jobs` array the panel never renders, and `chatRenderer.js`'s
  `openPanel(id)` runs on a second panel instance whose `_open`, `_jobSynapses` and `_expandedJobId`
  are separate from the app's. Both instances build the same ids (`panel.js:258` sets
  `overlay.id = 'research-overlay'`), and `closePanel` removes whichever one `getElementById`
  returns first:

  ```js
  // static/js/research/panel.js:341-342
  const overlay = document.getElementById('research-overlay');
  if (overlay) overlay.remove();
  ```

  With the app instance's `_open` left false, its own close button then returns at the
  `if (!_open) return;` guard (`:329`), and its ESC handler was already detached. `isOpen()`
  (`:219`) likewise reports false while the other instance's pane is on screen, so `app.js:851`
  (close the panel when switching sessions) does not close it either.
- **Impact:** clicking a `#research-<id>` link in a chat message — the "Open in Deep Research"
  anchor the agent loop emits for its own runs, which `chatRenderer.js:1331-1421` turns into an
  `openPanel(id)` call — creates the panel from the second instance. Opening the panel again from
  the rail button (`app.js:1011` → `toggle()`) adds a second overlay with the same id, after which
  closing removes the wrong overlay and leaves the visible pane stuck on screen until the page is
  reloaded. The same split silently disables the immediate-adopt path for agent-started research,
  which then appears only at the next 20s poll. This is reachable by an ordinary user through two
  clicks, which is why it is the one medium finding here.
- **Fix:** use one specifier for each module — drop the `?v=` query from the `panel.js` and
  `jobs.js` imports (or add the same query to every importer). A `window`-guarded singleton inside
  `openPanel` would mask the symptom but not the duplicate module state.

### [SECURITY] The research report body is inserted as raw HTML, so page-derived markup would execute in the panel

- **Location:** `static/js/research/panel.js:1133`
- **Severity:** low
- **Disposition:** fix-now
- **Evidence:** `_renderResult` calls `renderContent`, which is not a renderer — it returns its
  argument unchanged (`static/js/markdown.js:933-943`), and the result is interpolated straight
  into the card's HTML:

  ```js
  // static/js/research/panel.js:1131-1135
  const bodyCls = `research-job-report-body${cat ? ' research-body-' + cat : ''}`;
  if (_markdownModule) {
    html += `<div class="${bodyCls}">${_markdownModule.renderContent(job.result)}</div>`;
  } else {
    html += `<div class="${bodyCls}"><pre>${_esc(job.result)}</pre></div>`;
  }
  ```

  Measured in headless Chromium against the real `static/js/markdown.js` (served read-only from
  the repository, `/tmp/mdprobe`), with the same string construction as the line above:

  ```
  BROWSER RESULT: {"renderContent_output_equals_input":true,
                   "renderContent_output":"<img src=x onerror=\"window.__xss=1\">",
                   "img_injected_into_live_dom":1,"onerror_handler_ran":true,
                   "mdToHtml_output":"<img src=\"x\">"}
  ```

  The sibling export `mdToHtml` — what `chat.js:4124` and `documentLibrary.js:2750` use for the
  same text — strips the handler. `job.result` is not model prose alone: the report embeds each
  finding's page title and extracted page text verbatim
  (`services/research/research_handler.py:362-366` builds `- [{title}]({url})` from
  `f.get("title")` / `f.get("summary")`, and `:384-388` appends up to 2000 characters of
  `evidence` per finding), and `panel.js:1131` also feeds `job.result` through
  `research-job-report-body` as HTML. The reachability caveat is real and is why this is `low`:
  the only caller of `_renderResult` is gated on `_expandedJobId` (`panel.js:1017`), which is
  never assigned — see the next finding.
- **Impact:** latent stored markup injection in an authenticated session. A page a research run reads
  can put `<img src=x onerror=…>` in its title or body; if the expansion gate is ever wired up (the
  fix for the dead flag below is the natural way to do it), that markup is parsed with the app's
  origin — not executed, since the panel carries the same nonce policy
  (`core/middleware.py:141-147`, no `'unsafe-inline'`), so the payload's handler is refused and what
  it can do is spoof or cover panel content, carry a link, or fire an `<img src>` beacon. Today the
  branch does not render, so no payload is reachable; the trap is that fixing the dead code without
  fixing this line makes it reachable.
- **Fix:** `_markdownModule.mdToHtml(job.result)` instead of `renderContent`, matching the Library
  and chat callers; keep the `_esc` fallback branch as it is.

### [RACE] A running job that leaves the server's active list is never reconciled, so its card runs forever

- **Location:** `static/js/research/jobs.js:65`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_reconnectActive` only ever adds jobs — it compares the server's list against
  `_jobs` to find new ones and never looks for local jobs the server no longer reports:

  ```js
  // static/js/research/jobs.js:63-79, condensed
  if (res.ok) {
    const data = await res.json();
    for (const task of (data.active || [])) {
      if (_jobs.some(j => j.id === task.session_id)) continue;
      const job = { id: task.session_id, query: task.query, status: 'running', … };
      _jobs.push(job);
      _connectStream(job);
    }
  }
  ```

  The only exits from `status: 'running'` are the SSE final message (`:317-321`) and
  `_pollFallback`, whose only entry point is `es.onerror` (`:327-330`) — it re-arms itself every
  2s once started (`:346`). The server's
  `/api/research/active` lists only `entry.get("status") == "running"` rows
  (`routes/research/research_routes.py:259-276`), so a job that finished, failed, was cancelled, or
  was lost to a server restart is absent from it — the 20s poll (`:43`) sees nothing and does
  nothing. A stream that stays open but delivers no final event (a buffering proxy; the response
  sets only `X-Accel-Buffering: no`, `research_routes.py:607-611`) therefore leaves the card in the
  Active section with its per-second timer (`:303-305`) still running, for the life of the page.
- **Impact:** a permanently "running" card, a per-second re-render that never stops, and — if the
  user had started a queue — `startAllQueuedSequential` waits in `if (job.status !== 'running')`
  (`:182-190`) forever, so the remaining queued jobs never launch and no further work starts. The
  card cannot be cancelled either: `cancelJob` finishes locally but the server call is fire-and-
  forget (`:207-212`).
- **Fix:** reconcile in `_reconnectActive`: for every local job still `running` whose id is absent
  from `data.active`, ask `/api/research/status/{id}` and finish it (or drop it when the status
  endpoint 404s), the same way `_pollFallback` already does.

### [DEAD-CODE] `_expandedJobId` is never assigned, so a finished job's report body never renders

- **Location:** `static/js/research/panel.js:61`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the flag has exactly two occurrences in the file and neither writes it:

  ```
  $ grep -rn "_expandedJobId" static/js/ static/app.js
  static/js/research/panel.js:61:let _expandedJobId = null;
  static/js/research/panel.js:895:  const isExpanded = _expandedJobId === job.id;
  ```

  `isExpanded` is therefore always false and the only branch that calls `_renderResult` never runs:

  ```js
  // static/js/research/panel.js:1017
  ${isExpanded ? `<div class="research-job-result">${_renderResult(job)}</div>` : ''}
  ```

  `git log -S"_expandedJobId" -- static/js/research/panel.js` returns a single commit
  (`e5c99a5e`, the initial import), so nothing ever set it; `_renderResult` (`:1097`) has no other
  caller.
- **Impact:** the in-panel report body — sources list plus the rendered report — is unreachable.
  A finished card offers only the action buttons, so the report can be read through the Visual
  Report page or the Library but not in the panel where the job lives. It also keeps the raw-HTML
  insertion above latent rather than live.
- **Fix:** wire an expand/collapse toggle on the done card that sets `_expandedJobId` (and fix the
  escaping at `:1133` in the same change), or delete the flag, the branch and `_renderResult` if
  the report is meant to be read only in the Library.

### [PERF] The 20s adopt poll never stops, and every running job re-renders the whole job list once a second

- **Location:** `static/js/research/jobs.js:43`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the interval is created once from `init` and nothing in the module, the panel, or
  `app.js` ever clears it — there is no teardown export, and `closePanel` (`panel.js:328-343`)
  touches only the overlay:

  ```js
  // static/js/research/jobs.js:42-43
  if (_activePollInterval) clearInterval(_activePollInterval);
  _activePollInterval = setInterval(() => { _reconnectActive(); }, 20000);
  ```

  Separately, each running job owns a one-second timer whose only work is `_notify()`:

  ```js
  // static/js/research/jobs.js:303-305
  job._timerInterval = setInterval(() => {
    job.elapsed = Date.now() - job.startedAt;
    _notify();
  }, 1000);
  ```

  `_notify()` calls the callback registered at `panel.js:215` (`jobs.setRenderCallback(_renderJobs)`),
  and `_renderJobs` starts with `_syncResearchRail()` and then clears and rebuilds the entire list
  (`panel.js:663-694`, `container.innerHTML = '';`). The card rebuild is the only thing that
  advances the elapsed clock, so the whole list is reconstructed to move one number.
- **Impact:** an authenticated page polls `/api/research/active` every 20 seconds for as long as it
  is open, including when the user has never opened the research panel and when no job exists; and
  while N jobs run, the browser performs N full list rebuilds per second (each rebuild also
  re-queries the rail button and restarts the orbit rAF loop), even with the panel closed. Cost
  grows with the number of jobs in the queue, not with the work being displayed.
- **Fix:** start the poll when the panel opens or the first job starts and clear it when nothing is
  running; replace the per-job one-second timer with a single shared ticker that updates the
  elapsed text node in place instead of calling `_notify()`.

### [BUG] After an SSE drop, a cancelled job is reported as an error

- **Location:** `static/js/research/jobs.js:342`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the fallback poll collapses every non-`done` status to `error`, while the SSE path
  keeps `cancelled` distinct:

  ```js
  // static/js/research/jobs.js:341-344
  if (d.status !== 'running') {
    _finishJob(job, d.status === 'done' ? 'done' : 'error');
    if (d.status === 'done') _fetchResult(job);
    return;
  }
  ```
  ```js
  // static/js/research/jobs.js:319
  _finishJob(job, d.status === 'done' ? 'done' : d.status === 'cancelled' ? 'cancelled' : 'error');
  ```

  The status endpoint returns the task's own status string
  (`services/research/research_handler.py:106-117`), and `cancelled` is a value it really reports —
  set in `cancel_research` (`:144`) and when the task is cancelled (`:95`).
- **Impact:** a job the user cancelled from another tab or from the CLI, whose SSE stream had
  dropped, comes back as a red error card offering Retry and Edit — the UI invites the user to
  restart work they deliberately stopped, and the job's state no longer matches the server's.
  Needs a broken stream to reach, which is why it is low.
- **Fix:** mirror the SSE mapping — `d.status === 'cancelled' ? 'cancelled' : …` — in
  `_pollFallback`.

### [DEAD-CODE] `rag.js` is inert, and one of its callers calls a method it does not export

- **Location:** `static/js/rag.js:27`
- **Severity:** low
- **Disposition:** next
- **Evidence:** every entry point of the module looks up an element that exists nowhere in the
  tree. A search of the markup and the code finds only the lookups themselves (plus the
  `.rag-upload-zone` CSS rules):

  ```
  $ grep -rn "docs-view\|rag-upload-zone\|rag-file-input\|add-directory-btn\|rag-directory" \
      --include=*.js --include=*.html --include=*.py --exclude-dir=.git --exclude-dir=audit .
  ./static/app.js:3210:  const addDirBtn = el('add-directory-btn');
  ./static/app.js:3217:  const directoryInput = el('rag-directory');
  ./static/js/rag.js:27:  const box = document.getElementById('docs-view');
  ./static/js/rag.js:111:  const zone = document.getElementById('rag-upload-zone');
  ./static/js/rag.js:140:  const zone = document.getElementById('rag-upload-zone');
  ./static/js/rag.js:141:  const input = document.getElementById('rag-file-input');
  ```

  No HTML file and no Python template defines any of those ids; the only other matches are the
  `.rag-upload-zone` rules in `static/style.css` (`:2392`, `:2402`) and the separate
  `.admin-rag-upload-zone` block (`:15733`). So `loadPersonalDocs` returns at `:28`,
  `_setupUploadZone` returns at `:142`, and `uploadRagFiles` is called only from the handlers
  those two never install. `app.js` still calls into the module on a schedule and in two handlers,
  one of which names a method the module object does not have:

  ```js
  // static/js/rag.js:171-175, condensed
  const ragModule = { init, loadPersonalDocs, uploadRagFiles };
  // static/app.js:3213 and :3221
  ragModule.addRagDirectory(uiModule.showToast, uiModule.showError);
  ```

  `addRagDirectory` appears nowhere in `static/` except those two call sites, so it is `undefined`;
  the guard above each call is `if (addDirBtn)` (`app.js:3211`) or `if (directoryInput)`
  (`app.js:3218`), and neither element exists, so the TypeError is not reachable today.
  `app.js:4345` still schedules
  `ragModule.loadPersonalDocs()` nine seconds after boot, which is a no-op.
- **Impact:** a 177-line module and its boot-time call are shipped dead, and the API has drifted
  from its only caller — restoring the panel markup without adding the method would throw on the
  first click. The live replacements are the admin RAG controls (`static/js/admin.js:2416-2507`) and
  the `/rag` slash commands (`static/js/slashCommands.js:1887-1945`), which use the same endpoints.
- **Fix:** delete `rag.js` and its three call sites in `app.js`, or restore the panel markup and
  add the missing `addRagDirectory` export. Cross-reference: `routes-rest-memory-personal-research`
  owns the `/api/personal` endpoints this module called.

### [RACE] The conversation palette can display the results of an older query

- **Location:** `static/js/search-chat.js:186`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the debounced handler captures `query` and has no way to tell whether its response
  is still the newest; the render call reuses the captured string for highlighting:

  ```js
  // static/js/search-chat.js:186-196
  debounceTimer = setTimeout(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(query)}&limit=20`);
      if (!res.ok) return;
      const data = await res.json();
      renderResults(data, query);
    } catch (err) {
      console.error('Search error:', err);
    }
  }, 300);
  ```

  `renderResults` (`:86`) then rebuilds the list and `highlightMatch` (`:65-70`) marks the substrings
  matching that same stale query. The 300ms debounce (`:195`) only guarantees a request fires after
  a pause, not that the previous one has finished.
- **Impact:** with a response slower than the gap between keystrokes — a large history, a busy
  server — an earlier response can land last and replace the current results, and the highlights
  will match the old query. Clicking a row still navigates to the right session (each row carries
  its own `data-session`), so the effect is a wrong, stale list. Everything is escaped through
  `uiModule.esc`, so there is no injection path here.
- **Fix:** keep a request sequence number (or an `AbortController`) in module scope, capture it in
  the closure, and drop a response whose sequence is not the latest.

### [FOOTGUN] The running job card interpolates the server's `phase` string without escaping

- **Location:** `static/js/research/panel.js:943`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `formatPhase` falls through to the raw field for any phase it does not know, and the
  card template puts the result into `innerHTML` unescaped:

  ```js
  // static/js/research/jobs.js:255
  default: return p.phase;
  ```
  ```js
  // static/js/research/panel.js:931 and :943
  const phase = jobs.formatPhase(job.progress, phaseMaxR);
  …
  <div class="research-job-phase">${phase}</div>
  ```

  Every producer today emits a literal — the only events that reach the panel come from
  `DeepResearcher._emit` (`src/deep_research.py:273-353`, `planning` / `searching` / `reading` /
  `analyzing` / `writing` / `error` / `warning`), and the free-text producers elsewhere
  (`src/research_handler.py:376`, `:784`) are not on that path — but the field is the only
  unescaped interpolation in the card, next to `_esc(job.query)` and `_esc(job.errorMsg)` on the
  same lines, and a page-derived value does travel in the same event object
  (`src/deep_research.py:613` emits `title=display`; `researchSynapse.js:177-179` handles it
  through `textContent`).
- **Impact:** none today. The next producer that puts free text in `phase` — a plugin engine, a
  message-carrying warning — executes it in every open panel, with the same consequence as the
  report-body finding above.
- **Fix:** `_esc(jobs.formatPhase(job.progress, phaseMaxR))`, or make `formatPhase`'s default
  return a fixed label instead of `p.phase`.

### [PERF] Every rendered memory item adds a document-level click listener that is never removed

- **Location:** `static/js/memory.js:976`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the listener that dismisses an item's dropdown is registered inside the per-item
  loop, once per item per render, and nothing ever removes it:

  ```js
  // static/js/memory.js:975-976
  // Close dropdown on outside click
  document.addEventListener('click', () => { if (dropdown.parentNode) dropdown.remove(); }, { once: false });
  ```

  `grep -n removeEventListener static/js/memory.js` returns nothing. `renderMemoryList` runs on
  every keystroke in the search box (`static/app.js:1689-1694`), when the Brain modal is opened
  (`app.js:1675-1680`), after every load (`memory.js:372-405`), and on every select-mode change, so
  the count is items × renders. Each closure retains its item's dropdown subtree (five
  `.dropdown-item-compact` nodes) after the dropdown is removed from the DOM.
- **Impact:** with a few hundred memories, typing a ten-character search adds on the order of a
  thousand retained listeners and their detached subtrees, and every later document click runs all
  of them. The panel grows slower the longer a session stays open, and nothing releases the memory
  until the page is reloaded.
- **Fix:** register one document-level handler (module scope, installed once) that closes whichever
  `.memory-item-dropdown` is open, or remove the listener when the dropdown is removed.

### [DOC-DRIFT] The adopt-poll comment says 12 seconds; the interval is 20

- **Location:** `static/js/research/jobs.js:47`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the comment on the fast path and the interval it is compared against disagree:

  ```js
  // static/js/research/jobs.js:43
  _activePollInterval = setInterval(() => { _reconnectActive(); }, 20000);
  ```
  ```js
  // static/js/research/jobs.js:46-47
  // Allow an immediate adopt when the chat stream signals a new research
  // session (research_started ui_event) — faster than the 12s poll.
  ```

  The same "12s" is repeated on the chat side (`static/js/chatStream.js:161`), which is why the
  number is worth correcting in both places rather than only where the interval lives.
- **Impact:** no behaviour change; the comment misstates how long a user would otherwise wait for an
  agent-started run to appear, which is exactly the quantity `adoptSession` exists to shorten.
- **Fix:** say 20s (or name the constant) in both comments.
