# Executive summary

**2026-10-05 — all 58 sections reviewed; two re-review passes done.**

The run holds five high-severity defects. Three are in the Python backend and two are script
execution in the browser. Eight patterns account for most of the medium findings.

- **[Findings at a glance](#findings-at-a-glance)** holds the generated counts and the full medium
  list.

## Fix first

| Finding | What happens | Fix |
| --- | --- | --- |
| [`manage_research` ignores the owner](#security-manage_research-ignores-the-owner-and-operates-on-every-users-research-files) | Any user who can use agent mode lists, reads and deletes every user's research reports. No privilege disables the tool. | Filter the scan by the owner recorded in each file, as the HTTP route for the same files does. |
| [The Codex and Claude email send never delivers](#bug-the-codex-and-claude-email-send-endpoint-reports-the-message-queued-and-never-delivers-it) | The endpoint answers `{"success": true, "queued": true}` and drops the message. | Pass the injected `BackgroundTasks` object through to the send handler. |
| [Concurrent memory writes lose entries](#race-concurrent-memory-writes-lose-entries-raise-filenotfounderror-and-can-leave-memoryjson-unreadable) | Two concurrent writers lost an entry in 43 of 50 bursts, measured under a forced switch interval. Twelve writers left `memory.json` unparsable once in 30 bursts. | Lock the read-modify-write and stage through a unique temp file. The memory MCP server writes the same file from a second process, so a process-local lock is not enough. |
| [A search-result title runs script in the app](#security-a-hostile-search-result-title-reaches-the-research-spinners-innerhtml-injecting-markup-into-the-app-origin) | During Deep Research, a page title is assigned to `innerHTML`. A title carrying a `srcdoc` frame loaded a CDN script in the app's origin. Whether a live search provider returns such a title unmodified was not tested. | Write the spinner message as text. |
| [A calendar event's location runs script in the app](#security-a-calendar-events-location-is-only-partly-escaped-so-a-synced-or-imported-event-injects-html-and-css-into-the-calendar-ui) | A synced or imported event whose location starts with a URL has the rest of the text parsed as HTML. The same frame technique ran a CDN script when the event was opened. | Escape the whole string, then linkify the escaped copy. |

The last two depend on [the script policy allowlisting a public CDN](#security-script-src-allowlists-cdnjsdelivrnet-so-injected-markup-runs-attacker-hosted-script-through-a-srcdoc-frame).
Removing `cdn.jsdelivr.net` from `script-src` closes that route for every markup sink in the run;
the sinks still need fixing.

## Patterns in the backend

### Owner identity is resolved handler by handler

Handlers take the caller's identity and do not apply it, or apply the pseudo-user that every
bearer token shares. One user's action then reads, rewrites or deletes another user's records.

**Shared fix:** one helper that returns the storage owner, called by tools, routes and scheduled
actions.

- [`manage_research` operates on every user's files](#security-manage_research-ignores-the-owner-and-operates-on-every-users-research-files) (high)
- [Bearer callers share preferences, drafts and signatures](#security-bearer-callers-share-the-same-preferences-editor-drafts-and-signatures-across-token-owners)
- [Bearer callers share one comparison owner](#security-bearer-callers-share-one-comparison-owner-and-can-read-and-delete-each-others-records)
- [The session list deletes every owner's incognito rows](#security-the-session-list-deletes-every-owners-incognito-rows-not-just-the-callers)
- [`daily_brief` reads the default mailbox](#bug-daily_brief-reads-the-default-mailbox-instead-of-the-task-owners)

### `async def` handlers make synchronous calls

A blocking IMAP, CardDAV, HTTP or model call inside an `async def` handler holds the event loop.
The app runs one worker, so every other request waits.

**Shared fix:** declare the handler `def`, or wrap the call in `asyncio.to_thread`.

- [Nineteen email handlers](#perf-nineteen-async-def-handlers-run-blocking-imap-smtp-or-http-io-on-the-event-loop)
- [The chat path](#perf-the-chat-path-runs-synchronous-llm-web-search-and-url-fetch-calls-on-the-event-loop)
- [Context-length discovery](#perf-context-length-discovery-runs-two-synchronous-http-probes-on-the-event-loop-once-per-local-request)
- [CardDAV requests](#perf-carddav-requests-run-synchronously-inside-async-contact-handlers)

### Features report success and do nothing

These fail without an error, so neither the user nor a status-code test sees them.

**Shared fix for the agent tools:** compare each tool's schema against the tool registry and the
routes it calls.

- [The Codex and Claude email send](#bug-the-codex-and-claude-email-send-endpoint-reports-the-message-queued-and-never-delivers-it) (high)
- [`edit_image` calls four routes that do not exist](#bug-edit_image-calls-four-routes-that-do-not-exist)
- [`manage_tokens` mints tokens the middleware cannot authenticate](#bug-manage_tokens-mints-tokens-the-middleware-cannot-authenticate)
- [The email-urgency triage never reaches its classifier](#bug-the-email-urgency-triage-never-reaches-its-llm-classifier-and-still-requires-an-llm-endpoint)
- [The scheduled-send poller starts only after an inbox request](#bug-the-scheduled-send-poller-starts-only-when-a-client-asks-for-the-inbox-list)

### State and secret files are written without a lock, an atomic replace, or a mode

Memories, preferences, jobs and credentials live in JSON files. Writers truncate in place or share
one temp path, and secret-bearing files land at the umask default.

**Shared fix:** one write helper that locks, stages to a unique temp file, replaces atomically and
sets the mode.

- [Concurrent memory writes lose entries](#race-concurrent-memory-writes-lose-entries-raise-filenotfounderror-and-can-leave-memoryjson-unreadable) (high)
- [The hourly null-owner sweep rewrites two stores non-atomically](#bug-the-hourly-null-owner-sweep-rewrites-memoryjson-and-user_prefsjson-non-atomically)
- [`atomic_write_json` leaves the auth and settings stores at the umask default](#security-atomic_write_json-leaves-the-auth-and-settings-stores-at-the-umask-default)
- [`snapshot` writes the archive world-readable](#security-snapshot-writes-the-archive-world-readable-beside-the-key-it-contains)

### Failures are returned as normal results

A truncated, failed or partial operation is handed back as if it had completed.

- [A cut-off model stream is reported as a complete answer](#error-handling-a-stream-that-ends-without-done-or-is-cut-off-at-the-token-limit-is-reported-as-a-complete-answer)
- [Compaction drops messages it never summarized](#bug-compaction-rewrites-the-wrong-slice-of-the-session-history-dropping-messages-it-never-summarized)
- [A failing vector collection is reported as an empty, healthy one](#error-handling-a-collection-that-fails-is-reported-as-an-empty-healthy-lane-so-retrieval-returns-nothing-with-no-diagnostic)

## Patterns outside the backend

### Untrusted text is written into markup

Client code writes a page title, a calendar location, a theme name, a model id and a task prompt
into `innerHTML`. The first pass rated these as markup injection because the script policy has no
`'unsafe-inline'`. The re-review on 2026-10-05 measured script execution at three of them, raised
two to high, and added the policy finding.

**Shared fix:** escape at the sink for the context written into, and remove the CDN from
`script-src`.

- [The script policy allowlists a public CDN](#security-script-src-allowlists-cdnjsdelivrnet-so-injected-markup-runs-attacker-hosted-script-through-a-srcdoc-frame)
- [A stored theme name is rendered as markup on every page load](#security-a-stored-custom-theme-name-is-rendered-into-the-theme-grid-as-markup-on-every-page-load)
- [A sender's display name escapes its attribute](#security-a-senders-display-name-and-attachment-filename-escape-their-attribute-because-_esc-is-used-where-an-attribute-escaper-is-needed)
- [The email sanitizer keeps remote URLs in styles and `poster`](#security-the-email-html-sanitizer-keeps-remote-urls-in-inline-styles-and-poster-so-an-html-mail-beacons-without-the-users-consent)

The theme name needs a `ui_control` call, which the tool gate blocks after untrusted content unless
the user approves. The last two are attribute and CSS injection and do not reach script.

### The written material describes a different program

32 of the run's 35 `DOC-DRIFT` findings are outside the backend: in the specifications, the root
documents and the website.

**Shared fix:** one pass over `specs/`, the root documents and `website/` that re-derives each claim
from the code, security claims first.

- [26 of the 61 specs name a baseline commit that does not exist](#doc-drift-26-of-the-61-specs-are-stamped-with-a-baseline-commit-that-does-not-exist-in-this-repository)
- [The threat model does not state multi-user isolation as a goal](#doc-drift-the-threat-model-does-not-state-multi-user-data-isolation-as-a-goal-while-the-code-enforces-owner-scoping-and-this-audit-found-that-enforcement-failing)
- [`ACKNOWLEDGMENTS.md` describes the core as permissive after the AGPL relicense](#doc-drift-acknowledgmentsmd-still-describes-the-shipped-core-as-permissive-four-months-after-the-project-relicensed-to-agpl-30)

### Tests pin a copy of the code

The recurring defect in the 8 test sections is a test that checks a source substring, a hand-written
copy, or a stub in place of the guard. It passes when the behaviour it names is removed.

**Shared fix:** drive the real call path.

- [Four source-text pins pass with the code made unimportable](#bug-four-source-text-pins-pass-with-the-code-they-name-made-unimportable)
- [Every CalDAV test-connection test stubs the URL guard](#security-every-caldav-test-connection-test-runs-with-the-url-guard-stubbed-out)
- [The `web_search` sources tests assert on a copy of the fix](#bug-the-web_search-sources-tests-in-test_agent_looppy-assert-on-a-copy-of-the-fix-so-reverting-the-fix-leaves-the-suite-green)
- [`test_chat_route_tool_policy.py` re-implements the tool policy](#bug-test_chat_route_tool_policypys-functional-half-re-implements-the-tool-policy-and-passes-with-routeschat_routes-unimportable)

## What this run does not establish

- **The test sections sampled.** `tests-rest` read 47 of its 322 files end to end, `tests-llm-tools`
  46 of 121, and `tests-cookbook-models` 59 of 112.
- **No build or deployment was run.** Measurements are the probes each finding quotes.
- **Most lows carry first-pass evidence only.** The two re-reviews re-derived every high and every
  `fix-now` finding and opened every medium. For the 290 lows, a script checked the quoted code and
  cited locations against the source, and 11 were read. See
  [Re-review, 2026-10-05](#re-review-2026-10-05).
- **A finding count is a floor.** A file this run did not read has not been checked.

Suspected defects that did not survive checking are under
[Hypotheses tested and rejected](#hypotheses-tested-and-rejected).
