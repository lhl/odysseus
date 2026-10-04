# src: research, scheduling and background work

## Overview

`src/bg_jobs.py`,
`src/bg_monitor.py`,
`src/cleanup_service.py`,
`src/cookbook_serve_lifecycle.py`,
`src/deep_research.py`,
`src/research_handler.py`,
`src/research_utils.py`,
`src/task_endpoint.py`,
`src/task_scheduler.py`,
`src/teacher_escalation.py`,
`src/visual_report.py`.

The deep-research engine and its job store, the scheduled-task scheduler and its background-job
runner, session cleanup, the cookbook serve reaper, and the teacher-escalation and
visual-report generators. The routes that expose these (`routes/research/research_routes.py`,
`routes/task/task_routes.py`, `routes/cleanup/cleanup_routes.py`) are other sections; this one
covers the code they call and the stores they read. `src/deep_research.py` and
`src/research_handler.py` call the search providers and the fetcher in `services/search/`
(`services-search`); `src/visual_report.py` renders into the report page whose client script is
`static-js-research-memory-rag`; `src/task_scheduler.py` invokes the action handlers in
`src/builtin_actions.py` (`src-tools-builtin-actions`); the session store it reads is
`core/session_manager.py` (`core-auth-session`). `core/atomic_io.py` and the SQLite engine setup
are `core-data-platform`.

## Coverage

**Read fully:** all eleven assigned files (8,451 lines): `src/task_scheduler.py` (2,675),
`src/visual_report.py` (1,933), `src/research_handler.py` (991), `src/deep_research.py` (929),
`src/teacher_escalation.py` (810), `src/bg_jobs.py` (297), `src/cleanup_service.py` (293),
`src/cookbook_serve_lifecycle.py` (219), `src/bg_monitor.py` (168), `src/task_endpoint.py` (73),
`src/research_utils.py` (63). In `src/visual_report.py` the CSS/palette ranges (1277–1684 and the
style block of the template) were skimmed by pattern scan for code rather than read line by line;
every executable region of that file was read. Working-tree line numbers refer to `2992bf6d368a`;
`git status --short` showed only the untracked `audit/` directory, and the eleven files are
unmodified against `HEAD`.

**Read partially:** `core/session_manager.py` at the session cache and message-count maintenance;
`core/database.py` at the `ChatMessage`/`Session` foreign keys and the SQLite pragma listener;
`routes/cleanup/cleanup_routes.py` (all 60 lines), `routes/chat_routes.py` at the research
continuation (`1700–1750`), `routes/task/task_routes.py` at the three task-trigger routes,
`routes/assistant_routes.py` at the assistant trigger, `routes/research/research_routes.py` at the
report, library and image routes; `src/endpoint_resolver.py` at `normalize_base`, `build_headers`
and `resolve_endpoint`; `src/agent_loop.py` at the teacher-escalation call site; `app.py` at
`AuthMiddleware`; `core/middleware.py`; `services/search/content.py` at `fetch_webpage_content`;
`src/builtin_actions.py` at `action_ping_events`, the action registry and `action_ping_notes`;
`src/settings.py` at `get_setting`/`load_settings`; `static/js/tasks.js` and
`static/js/research/panel.js` by search.

**Not read:** no assigned file remains unread. The search-provider chain (`src/search/core.py`,
`src/search/providers.py`), the fetcher's SSRF/redirect internals, the PDF/office parsers behind
the report sources, the tool-approval store, the scheduler's email/calendar action bodies, and the
front end beyond the searches above. No live model, embedding service, browser session, real
cron boundary, multi-process run or load benchmark was exercised.

**Checks run:** `git rev-parse --short=12 HEAD` (`2992bf6d368a`), `git status --short`, `wc -l` on
the assigned files, and focused searches for `create_task`, `except Exception: pass`, ownership
filters, datetime handling and dead symbols. Four probes ran under `venv/bin/python` with data
directories in `/tmp`, outside the checkout:

- **Report inline-JSON probe.** `src/visual_report.py`'s own `generate_visual_report` rendered a
  report twice, once with a source image URL of `https://evil.example/x<!--<script>alert(1)</script>`
  and once with a clean URL, and the two documents were parsed with `html5lib` 1.1 (installed into
  `/tmp/h5`, spec-compliant tokenizer). Result: the control script element closes normally; the
  crafted one never closes (see the finding below).
- **Background-job store probe.** Two threads released by a barrier, one calling
  `src.bg_jobs.kill()` on a job whose exit file had just appeared and one calling
  `src.bg_jobs.refresh()`, with `_kill` stubbed and `_STORE`/`_JOBS_DIR` redirected: **144 of 200
  trials** ended with `followed_up` False.
- **Research-record probe.** Two threads hiding different images in one record: **159 of 200
  trials** lost a hide and **120 of 200** had a caller read a truncated file and return False. A
  separate call of `_save_result` over a record holding `hidden_images` and `consumed` dropped
  both keys.
- **Endpoint predicate probe.** The substring predicate from `src/task_scheduler.py:1889` evaluated
  with the real `normalize_base` over two endpoint base URLs.

`venv/bin/python -m pytest -q` was run with these thirty-eight suites: `tests/test_bg_jobs_store.py`,
`tests/test_bg_job_tools.py`, `tests/test_bg_monitor_stream.py`, `tests/test_cleanup_owner_scope.py`,
`tests/test_cleanup_routes_shim.py`, `tests/test_cleanup_service_utcnow.py`,
`tests/test_cookbook_serve_lifecycle.py`, `tests/test_builtin_actions_cookbook_serve_state.py`,
the five `tests/test_deep_research_*.py`, `tests/test_research_handler_path_confinement.py`,
`tests/test_research_handler_raw_nondict.py`, `tests/test_research_handler_sources_nondict.py`,
`tests/test_research_handler_analyzed_urls.py`, `tests/test_research_status_avg_duration.py`,
`tests/test_research_report_read.py`, `tests/test_research_session_id_validation.py`,
`tests/test_research_utils.py`, `tests/test_research_utils_low_quality_nonstring.py`,
`tests/test_research_source_link_xss.py`, `tests/test_research_probe_errors.py`,
`tests/test_research_query_fallback.py`, `tests/test_task_endpoint_normalization.py`,
`tests/test_task_scheduler_cache.py`, `tests/test_task_scheduler_cancel.py`,
`tests/test_task_scheduler_session_delivery.py`, `tests/test_task_routes_shim.py`,
`tests/test_teacher_eval_tier2.py`, `tests/test_teacher_eval_nonstring_reply.py`,
`tests/test_teacher_audit_owner_scope.py`, and the five `tests/test_visual_report*.py` —
**168 passed**, one SQLAlchemy deprecation warning. The full suite and `audit.py` were not run;
run-level generation, counts and secret-gate validation belong to the coordinating reviewer.

### [RACE] A killed background job can still be auto-continued — the job store has no writer lock

- **Location:** `src/bg_jobs.py:266-283` (`kill`), `:191-235` (`refresh`), `:57-71` (`_load`/`_save`), `:238-244` (`pending_followups`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** every mutation is a whole-file read-modify-write with no lock. `kill()` loads the
  store, marks the job failed, sets `followed_up = True` — its docstring says why: "Sets
  followed_up so the monitor does not also fire an auto-continue for a job the agent deliberately
  stopped" (`:269-270`) — and saves the snapshot it loaded:

  ```python
  jobs = _load()
  rec = jobs.get(job_id)
  ...
  if rec.get("status") == "running":
      _kill(rec.get("pid"))
      rec["status"] = "failed"
      ...
      rec["followed_up"] = True
      _save(jobs)
  ```

  `refresh()` does the same on an independently loaded snapshot, marking a job done/failed and
  saving whenever anything changed (`:224-235`). Both are reachable concurrently: `refresh()` runs
  from the monitor's `pending_followups()` every 5 s (`src/bg_monitor.py:152-160`), from every
  status poll (`get()` `:253-260`, `list_for_session()` `:262-263`), and `kill()` from the route.
  Measured with two threads released by a barrier — one `kill(JOB)` on a job whose exit file had
  just appeared, one `refresh()`, `_kill` stubbed, store in `/tmp` — **144/200 trials ended with
  `followed_up` False**, so `pending_followups()` returns the job the user just stopped and the
  monitor re-invokes the agent with its output. The module's guarantee at `:10-13` ("a job stays
  {done, followed_up: False} until the agent has actually been re-invoked") is the same flag read
  in the opposite direction, and it is the only thing separating "the agent hears back" from "the
  agent continues work the user ended".
- **Impact:** killing a job in the moment it finishes can still produce a headless agent
  continuation in that session (`src/bg_monitor.py:101-140` appends the job's output and runs up
  to 12 agent rounds), so the agent performs further tool calls after an explicit stop. The
  window is the load-modify-save span, so the two writers must overlap, but both are triggered by
  routine user and UI activity.
- **Fix:** hold a module-level `threading.Lock` across every load-modify-save in `bg_jobs`, or
  funnel all store writes through one owner, so `kill()`, `mark_followed_up()` and `refresh()`
  cannot clobber each other's snapshots.

### [SECURITY] An og:image URL containing `<!--` breaks the report's inline script out of its element

- **Location:** `src/visual_report.py:1921-1933` (`_json_for_script`), `:933` (`__spareImages`), `:1770-1778` (image admission)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_json_for_script` escapes one sequence and documents a stronger claim than it
  enforces:

  ```python
  def _json_for_script(value) -> str:
      """JSON-encode a value safe to embed inside a <script> block.

      json.dumps doesn't escape '/', so a string containing the literal
      substring '</script>' would terminate the script element early.
      Escape the closing slash to keep the inline JSON inert as HTML.
      """
      return json.dumps(value).replace("</", "<\\/")
  ```

  The `spare_images` list is scraped-page data: any `https://` URL taken from a source's
  `og:image` that is not an icon/logo or `.svg`/`.ico`/`.gif` is admitted (`:1770-1778`) and
  embedded at `:933`. Rendering a report with one source image set to
  `https://evil.example/x<!--<script>alert(1)</script>` emitted:

  ```
  var __spareImages = ["https://cdn.example/b.jpg", "https://evil.example/x<!--<script>alert(1)<\/script>"];
  ```

  A raw `<!--` inside a script element puts the HTML tokenizer into script-data-escaped state, and
  `<script>` then takes it to double-escaped state, where only a literal `</script` returns it.
  Parsing both documents with html5lib 1.1: the control script text is 11,247 chars and ends at
  the JavaScript; the crafted script text is 11,300 chars and ends
  `…td.classList.add('cmp-mid');\n  });\n}\n</script>\n</body>\n</html>\n` — the element's real
  `</script>` never closes it and the trailing markup is script text, so the whole script fails to
  parse.
- **Impact:** any page that sets `og:image` to a URL containing `<!--` — the meta tag is
  attacker-controlled — disables every scripted feature of the report for whoever opens it: TOC
  highlight, image hide and reroll, the restore button, the export menu, the Discuss call to
  action and ESC-to-close. The `</`→`<\/` escape is the only thing keeping the same gap from
  being XSS, so an inline-JSON consumer that drops that escape, or a value embedded without it,
  is injectable. Mitigation: report content itself is allowlist-sanitized (`_md_to_html`
  `:68-100`), and the hero image, figure and `data-img-url` paths use `html.escape`, which does
  escape `<`.
- **Fix:** escape `<` in `_json_for_script`, e.g. `json.dumps(value).replace("<", "\\u003c")`,
  which covers `<!--` and `</` together.

### [SECURITY] The teacher takeover note interpolates a tool-output snippet outside the untrusted fence

- **Location:** `src/teacher_escalation.py:612-619` (`note_content`), `:104-113` (snippet source)
- **Severity:** low
- **Disposition:** next
- **Evidence:** Tier 1 copies the head of the tool result that tripped a pattern into the failure
  reason:

  ```python
  if isinstance(text, str):
      for pat in _TOOL_ERROR_PATTERNS:
          if pat.search(text):
              snippet = text[:120].strip()
              return ("failure", f"tool result matched error pattern {pat.pattern!r}: {snippet!r}")
  ```

  and `run_teacher_inline` writes that reason into a **user-role** message for the teacher, in
  the trusted position of the conversation:

  ```python
  note_content = (
      f"{user_request or '(no user request captured)'}\n\n"
      "[teacher-takeover] The previous attempt by the student model "
      f"failed.\nFailure signal: {reason}\n"
      "Please solve the request above using your own tools. The user "
      "is watching your tool calls live."
  )
  teacher_messages = history + [{"role": "user", "content": note_content}]
  ```

  The same file fences this class of content for the skill-distillation prompt
  (`_UNTRUSTED_TRACE_GUARD` `:133-146`, `_format_trace` `:347-359`), and the repo wraps untrusted
  tool output elsewhere (`untrusted_context_message`, used for the same job output in
  `src/bg_monitor.py:27-36`). The patterns are reachable from any tool result: `^Unknown action`,
  `^Failed to`, `^Invalid`, `\bnot found\b`, `\berror:\s` (`:74-88`). Mitigations: the student's
  `external_untrusted_context_seen` is forwarded to the teacher run
  (`src/agent_loop.py:6446-6448`), so its tool calls run under the tainted-run policy; a
  teacher-generated skill is persisted only through an exact-approval card
  (`tool_approval_store.create` `:747`); and the takeover is streamed to the user as it happens.
- **Impact:** a page, email or document that gets its first 120 characters copied into the
  failure signal lands in the teacher's instruction context as if the user had written it, in a
  run that then calls tools with the user's authority. A payload only needs to appear at the head
  of a tool result and match one pattern.
- **Fix:** wrap `reason` with `untrusted_context_message(...)`, or pass only the matched pattern
  name instead of the snippet, before building `note_content`.

### [BUG] Task endpoints are matched by substring, so the wrong endpoint's API key can be attached

- **Location:** `src/task_scheduler.py:1889-1890`, `:2065-2066`
- **Severity:** low
- **Disposition:** next
- **Evidence:** both sites pick the request's credentials with a substring test over every enabled
  endpoint, in query order, taking the first hit:

  ```python
  for ep in eps:
      if normalize_base(ep.base_url) in endpoint_url or endpoint_url in normalize_base(ep.base_url):
          headers = build_headers(ep.api_key, normalize_base(ep.base_url))
          break
  ```

  `normalize_base` (`src/endpoint_resolver.py:225-234`) strips only known suffixes (`/models`,
  `/chat/completions`, `/completions`, `/v1/messages`, `/responses`, `/api/chat`, `/api/tags`,
  `/api/generate`); it neither reduces the URL to an origin nor requires a path boundary. Running
  that predicate with the real `normalize_base` over two enabled endpoints —
  `http://gw.example.com/v1` and `http://gw.example.com/v1-beta`, with the resolved task URL
  `http://gw.example.com/v1-beta/chat/completions` — selects `http://gw.example.com/v1`, i.e. the
  other endpoint's key is attached to a request aimed at `v1-beta`. The surrounding block is
  wrapped in `except Exception: pass`, so a resolution failure is silent.
- **Impact:** an endpoint's API key is sent to a different endpoint — a different service or
  tenant on a shared host — and the run then fails authentication or authenticates as the wrong
  service. It needs two enabled endpoints where one base URL is a prefix of the other, which is
  what a `/v1` and `/v1-…` pair on one gateway looks like. Mitigation: the resolver path runs
  first and its headers are used when it returns them (`:2028-2034`), so this only affects URLs
  that arrive without resolver headers.
- **Fix:** resolve credentials by the endpoint's stored `id`, or compare parsed origin plus full
  path instead of substrings.

### [BUG] `_save_result` rewrites the research record without the fields other writers own

- **Location:** `src/research_handler.py:601-631` (record built at `:611-629`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_save_result` builds a fresh dict — `query`, `status`, `result`, `raw_report`,
  `sources`, `raw_findings`, `stats`, `category`, `started_at`, `completed_at`, `owner` — and
  writes it over the whole file, while two other writers keep their state in the same file:
  `hide_image` appends to `hidden_images` (`:691-695`) and `clear_result` sets `consumed`
  (`:594-597`). Neither key is in the fresh dict. Measured: a record holding
  `hidden_images: ["https://a/x.jpg", "https://b/y.jpg"]` and `consumed: true`, after
  `_save_result` writes, has keys `category, completed_at, owner, query, raw_findings, raw_report,
  result, sources, started_at, stats, status` — both keys gone. Reachable: a chat-side
  continuation reuses the session id (`routes/chat_routes.py:1700-1745` reads the prior record via
  `_get_session_json` and calls `start_research(..., prior_report=…)` with the same session), so
  the record the user's hide choices live in is the one that gets overwritten.
- **Impact:** images the user hid on a report reappear after continuing that research, and a
  consumed report re-renders as new. The same write is not atomic (see the finding below), so a
  crash during it leaves a record no reader can parse.
- **Fix:** load the existing record first (`data = self._get_session_json(session_id) or {}`) and
  assign the fresh keys into it, so fields owned by other writers survive.

### [RACE] The research record is read-modify-written without a lock, so concurrent hides lose updates

- **Location:** `src/research_handler.py:682-700` (`hide_image`), `:702-717` (`unhide_all_images`), `:584-600` (`clear_result`), `:631` (`_save_result`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** all four writers do `json.loads(path.read_text())` → mutate → `path.write_text(...)`
  with no lock and no atomic replace. Measured with two threads released by a barrier, each hiding
  a different image in the same record: **159/200 trials lost one of the two hides**, and in
  **120/200 trials at least one caller got `False`** because it parsed a file another writer had
  truncated mid-write (`Failed to hide image: Expecting value: line 1 column 1 (char 0)`). The
  route converts that `False` into `HTTPException(404, "Research not found")`
  (`routes/research/research_routes.py:350-352`). A reader that hits the truncation window treats
  the research as absent: `get_result` (`:463-481`) and `get_status` (`:407-440`) swallow the
  decode error and return `None`.
- **Impact:** a second rapid hide is dropped, so an image the user removed reappears on the next
  render; a hide request can answer 404 for a research that exists; and any crash or kill during
  a save leaves a truncated record that hides the report until it is re-saved. The report record
  is the only place the rendered report, its sources and its image choices live.
- **Fix:** write through `core.atomic_io.atomic_write_json` and hold a per-session lock across the
  read-modify-write.

### [DEAD-CODE] The calendar-event reminder scanner is never started

- **Location:** `src/task_scheduler.py:624-642` (`_event_pings_loop`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the loop's docstring claims a live dispatch path — "Built-in calendar-event
  scanner — same recipe as note pings. Runs every 10 min, fires reminders via
  `dispatch_reminder`. Not a user task." — and it carries a per-owner fix from an earlier review
  ("passing owner="" globally would email User B's events to User A's configured SMTP 'from'
  address — see review C3"). Nothing calls it: startup creates only `_note_pings_loop`
  (`:559`), and a search for `_event_pings_loop` over the tree returns the definition alone. Its
  only callee, `action_ping_events` (`src/builtin_actions.py:1513`), is referenced only from that
  loop (`:637`), and it is absent from `BUILTIN_ACTIONS`, where the comment records the decision:
  "ping_events removed from the user-facing registry. Calendar reminders are represented as Notes,
  so note pings are the single dispatch path" (`:3403-3404`); `core/database.py:1737-1755` drops
  the previously seeded ping tasks.
- **Impact:** the code and its docstring assert a dispatch path that does not exist, so a reader
  (or the next maintainer) concludes event reminders are dispatched by the scheduler. Re-enabling
  it is one `create_task` away and would double-notify, because reminders already arrive through
  the note scanner.
- **Fix:** delete `_event_pings_loop` and `action_ping_events`, or replace both docstrings with a
  line stating that they are retired and must not be restarted.

### [DOC-DRIFT] `teacher_escalation`'s stated gates no longer match its code, and its background path is unreachable

- **Location:** `src/teacher_escalation.py:1-23` (module docstring), `:49-68` (`is_self_hosted`), `:147-229` (`_TEACHER_ESCALATION_PROMPT`), `:435-448` (`escalate_and_learn`), `:450-510` (`maybe_escalate`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the docstring's trigger list requires "The student's endpoint is self-hosted (not
  a known SOTA cloud API)" and calls Tier 2 "a TODO … Not in first cut". The code says the
  opposite on both counts: `maybe_escalate` carries the comment "(No self-hosted-only gate —
  users run cheap cloud students like deepseek-v4-flash with a SOTA teacher; the toggle is the
  control.)" (`:470-471`), and Tier 2 is implemented (`evaluate_turn_llm` `:390-433`) and
  reachable from `run_teacher_inline` behind `teacher_tier2_enabled` (`:575-590`). Searches over
  `routes/`, `src/`, `core/` and `app.py` excluding the module: `_TEACHER_ESCALATION_PROMPT`
  (`:147-229`), `maybe_escalate` (`:450-510`) and `escalate_and_learn` (`:435-448`) have no
  caller at all, and `is_self_hosted` (`:49-68`) is used only by `tests/test_kimi_code_hosts.py`
  and `tests/test_venice_hosts.py`. `escalate_and_learn` is a stub that logs "background teacher
  learning skipped: generated skills require an interactive exact approval".
- **Impact:** an operator reading the module concludes escalation fires only for self-hosted
  students; it fires for any endpoint whenever the toggle is on, spending a second paid model per
  escalation. About 170 lines — including a 75-line prompt — look live but cannot run, and
  restoring `escalate_and_learn`'s body would re-open a skill-persistence path that the approval
  gate now closes.
- **Fix:** correct the docstring (toggle-gated, any endpoint; Tier 2 implemented) and delete the
  unreachable prompt and escalation helpers together with the tests that cover them.
