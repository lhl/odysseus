# Executive summary

**2026-10-04 — backend review complete; documentation, build and client sections in progress;
front-end JavaScript and tests unread.**

The Python backend (`core`, `src`, `routes` and `services`: 126,017 lines in 35 sections) holds
three high-severity defects and five patterns that account for most of its medium findings. Each
high has a fix of a few lines. The patterns are worth fixing once at their shared cause instead of
finding by finding.

- **[Findings at a glance](#findings-at-a-glance)** has the counts by section, disposition and
  tag, and the full list of medium findings. Those tables are generated, so they are current even
  where this summary is not.

## Fix first

| Finding | What happens | Fix |
| --- | --- | --- |
| [`manage_research` ignores the owner](#security-manage_research-ignores-the-owner-and-operates-on-every-users-research-files) | Any user who can use agent mode lists, reads and deletes every user's research reports. No privilege disables the tool. | Filter the scan by the owner recorded in each file, as the HTTP route for the same files does. |
| [The Codex and Claude email send never delivers](#bug-the-codex-and-claude-email-send-endpoint-reports-the-message-queued-and-never-delivers-it) | The endpoint answers `{"success": true, "queued": true}` and drops the message. Every send through the documented integration is lost without an error. | Pass the injected `BackgroundTasks` object through to the send handler. |
| [Concurrent memory writes lose entries](#race-concurrent-memory-writes-lose-entries-raise-filenotfounderror-and-can-leave-memoryjson-unreadable) | Two concurrent writers lost an entry in 43 of 50 bursts. Twelve writers left `memory.json` unparsable once in 30 bursts. | Lock the read-modify-write and stage through a unique temp file. The bundled memory MCP server writes the same file from a second process, so a process-local lock is not enough. |

## Patterns across the backend

Each pattern names its cause, the shared fix, and the high and medium findings that belong to it.

### Owner identity is resolved handler by handler

Six handlers take the caller's identity and do not apply it, or apply the pseudo-user that every
bearer token shares. One user's action then reads, rewrites or deletes another user's records.

**Shared fix:** one helper that returns the storage owner, called by tools, routes and scheduled
actions.

- [`manage_research` operates on every user's files](#security-manage_research-ignores-the-owner-and-operates-on-every-users-research-files) (high)
- [Bearer callers share preferences, drafts and signatures](#security-bearer-callers-share-the-same-preferences-editor-drafts-and-signatures-across-token-owners)
- [Bearer callers share one comparison owner](#security-bearer-callers-share-one-comparison-owner-and-can-read-and-delete-each-others-records)
- [The session list deletes every owner's incognito rows](#security-the-session-list-deletes-every-owners-incognito-rows-not-just-the-callers)
- [`classify_events` uses one user's memories on every user's calendar](#bug-classify_events-classifies-every-users-calendar-events-with-one-users-memories)
- [`daily_brief` reads the default mailbox](#bug-daily_brief-reads-the-default-mailbox-instead-of-the-task-owners)

Two more findings are missing gates, not missing owner filters:
[memory edit, pin, delete and audit skip the memory-management privilege](#security-memory-pin-edit-delete-and-audit-bypass-the-memory-management-privilege),
and
[the hardware-fit routes let a non-admin run SSH probes against a host the caller chooses](#security-hardware-fit-routes-let-non-admins-run-server-side-ssh-probes-against-caller-selected-hosts).

### `async def` handlers make synchronous calls

A blocking IMAP, CardDAV, HTTP or model call inside an `async def` handler holds the event loop,
so every other request waits until it returns.

**Shared fix:** declare the handler `def`, or wrap the call in `asyncio.to_thread`.

- [Nineteen email handlers](#perf-nineteen-async-def-handlers-run-blocking-imap-smtp-or-http-io-on-the-event-loop)
- [The chat path: model, web-search and URL-fetch calls](#perf-the-chat-path-runs-synchronous-llm-web-search-and-url-fetch-calls-on-the-event-loop)
- [Context-length discovery, once per local request](#perf-context-length-discovery-runs-two-synchronous-http-probes-on-the-event-loop-once-per-local-request)
- [PDF and image processing in the gallery and document routes](#perf-pdf-and-image-processing-runs-synchronously-inside-the-async-handlers)
- [CardDAV requests in the contact handlers](#perf-carddav-requests-run-synchronously-inside-async-contact-handlers)
- [Speech, upload processing and vision analysis](#perf-speech-upload-processing-and-vision-analysis-run-blocking-work-on-the-request-event-loop)
- [Both search POST handlers](#perf-both-search-post-handlers-execute-synchronous-network-work-on-the-event-loop)
- [`list_models` endpoint probes](#perf-list_models-probes-endpoints-with-synchronous-http-on-the-event-loop)

### Features report success and do nothing

These fail without an error, so neither the user nor a test that checks the status code sees them.

**Shared fix:** for the agent tools, one pass that compares each tool's schema against the tool
registry and the routes it calls. The others need their own fixes.

- [The Codex and Claude email send](#bug-the-codex-and-claude-email-send-endpoint-reports-the-message-queued-and-never-delivers-it) (high)
- [`edit_image` calls four routes that do not exist](#bug-edit_image-calls-four-routes-that-do-not-exist)
- [`manage_tokens` mints tokens the middleware cannot authenticate](#bug-manage_tokens-mints-tokens-the-middleware-cannot-authenticate)
- [`tail_serve_output` is rejected on every native call](#bug-tail_serve_output-is-advertised-to-native-models-but-missing-from-tool_tags-so-every-native-call-is-rejected)
- [`manage_research` has no native schema](#bug-manage_research-has-no-native-schema-so-the-report-read-path-the-prompt-and-rag-steer-to-is-unreachable-for-native-models)
- [The email-urgency triage never reaches its classifier](#bug-the-email-urgency-triage-never-reaches-its-llm-classifier-and-still-requires-an-llm-endpoint)
- [The scheduled-send poller starts only after an inbox request](#bug-the-scheduled-send-poller-starts-only-when-a-client-asks-for-the-inbox-list)

### JSON stores are written without a lock or an atomic replace

The app keeps memories, preferences, background jobs and credentials in JSON files. Several writers
truncate in place or share one temp path, and one writer leaves credential files world-readable.

**Shared fix:** route every store through one writer that locks, stages to a unique temp file,
replaces atomically and sets the file mode.

- [Concurrent memory writes lose entries](#race-concurrent-memory-writes-lose-entries-raise-filenotfounderror-and-can-leave-memoryjson-unreadable) (high)
- [The hourly null-owner sweep rewrites two stores non-atomically](#bug-the-hourly-null-owner-sweep-rewrites-memoryjson-and-user_prefsjson-non-atomically)
- [The background-job store has no writer lock](#race-a-killed-background-job-can-still-be-auto-continued-the-job-store-has-no-writer-lock)
- [`atomic_write_json` leaves the auth and settings stores at the umask default](#security-atomic_write_json-leaves-the-auth-and-settings-stores-at-the-umask-default)

### Failures are returned as normal results

A truncated, failed or partial operation is handed back as if it had completed. The cost is lost
or missing data that nothing reports.

- [A cut-off model stream is reported as a complete answer](#error-handling-a-stream-that-ends-without-done-or-is-cut-off-at-the-token-limit-is-reported-as-a-complete-answer)
- [Compaction drops messages it never summarized](#bug-compaction-rewrites-the-wrong-slice-of-the-session-history-dropping-messages-it-never-summarized)
- [A failing vector collection is reported as an empty, healthy one](#error-handling-a-collection-that-fails-is-reported-as-an-empty-healthy-lane-so-retrieval-returns-nothing-with-no-diagnostic)
- [A duplicate event UID discards a calendar's whole pull](#bug-a-vevent-uid-that-another-calendar-already-holds-discards-that-calendars-whole-pull-while-the-counts-still-report-it-as-synced)
- [The research library omits saved partial reports](#bug-the-research-library-silently-drops-saved-partial-reports-with-null-statistics)

## Outside the backend

The repository root, build and deployment files, specifications, scripts, bundled MCP servers,
companion apps, website and vendored static assets were under review when this summary was written
on 2026-10-04. Their findings appear in [Findings at a glance](#findings-at-a-glance) as they are
recorded. This summary does not yet draw conclusions from them.

## What this pass does not establish

- **The first-party front end is unread.** The seven `static-js-*` sections have no coverage
  statement. This audit makes no claim about cross-site scripting, client-side authorization or UI
  correctness.
- **The tests are unread.** The eight `tests-*` sections (113,318 lines) have no coverage
  statement. Sections ran the test suites that cover the code they read, and each section's
  Coverage records them. The full suite was not run, and whether it asserts negative cases is not
  established.
- **No build or deployment was run.** Measurements are the small probes each finding quotes.
- **Most findings carry first-pass evidence only.** The
  [re-review on 2026-10-04](#re-review-2026-10-04) re-derived the 5 findings then rated high and 21
  of the 67 then rated medium. It confirmed all 26 and lowered 10 severities. No later finding has
  been re-reviewed.
- **A finding count is a floor.** It is set by what was read. A file this pass did not read has not
  been checked.

Suspected defects that did not survive checking are listed under
[Hypotheses tested and rejected](#hypotheses-tested-and-rejected), so a later pass does not
re-derive them.
