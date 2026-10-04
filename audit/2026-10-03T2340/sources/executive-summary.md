# Executive summary

**2026-10-04 — all 58 sections reviewed.** The run holds 399 findings: three high, 106 medium and
290 low.

Five patterns account for most of the medium findings in the 35 backend sections (126,017 lines).
Three more run through the 23 non-backend sections: written material that describes a different
program, escaping that does not fit its context, and tests that pin a copy of the code rather than
the code.

- **[Findings at a glance](#findings-at-a-glance)** holds the generated counts and the full medium
  list, so it is current even where this summary is not.

## Fix first

| Finding | What happens | Fix |
| --- | --- | --- |
| [`manage_research` ignores the owner](#security-manage_research-ignores-the-owner-and-operates-on-every-users-research-files) | Any user who can use agent mode lists, reads and deletes every user's research reports. No privilege disables the tool. | Filter the scan by the owner recorded in each file, as the HTTP route for the same files does. |
| [The Codex and Claude email send never delivers](#bug-the-codex-and-claude-email-send-endpoint-reports-the-message-queued-and-never-delivers-it) | The endpoint answers `{"success": true, "queued": true}` and drops the message. Every send through the documented integration is lost without an error. | Pass the injected `BackgroundTasks` object through to the send handler. |
| [Concurrent memory writes lose entries](#race-concurrent-memory-writes-lose-entries-raise-filenotfounderror-and-can-leave-memoryjson-unreadable) | Two concurrent writers lost an entry in 43 of 50 bursts. Twelve writers left `memory.json` unparsable once in 30 bursts. | Lock the read-modify-write and stage through a unique temp file. The bundled memory MCP server writes the same file from a second process, so a process-local lock is not enough. |

## Patterns across the backend

Each pattern names its cause, the findings that belong to it, and the shared fix where one exists.

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

### State and secret files are written without a lock, an atomic replace, or a mode

The app keeps memories, preferences, background jobs and credentials in JSON files, and writes the
app key, `.env`, the setup password database and the cookbook runner scripts beside them. Writers
truncate in place or share one temp path, and secret-bearing files land at the umask default — a
backup archive carries the app key beside the database it decrypts, the "stolen backup" case
`src/secret_storage.py` names as its threat model.

**Shared fix:** route every write through one helper that locks, stages to a unique temp file,
replaces atomically and sets the mode, and apply the same to the members a restore writes.

- [Concurrent memory writes lose entries](#race-concurrent-memory-writes-lose-entries-raise-filenotfounderror-and-can-leave-memoryjson-unreadable) (high)
- [The hourly null-owner sweep rewrites two stores non-atomically](#bug-the-hourly-null-owner-sweep-rewrites-memoryjson-and-user_prefsjson-non-atomically)
- [The background-job store has no writer lock](#race-a-killed-background-job-can-still-be-auto-continued-the-job-store-has-no-writer-lock)
- [`atomic_write_json` leaves the auth and settings stores at the umask default](#security-atomic_write_json-leaves-the-auth-and-settings-stores-at-the-umask-default)
- [`snapshot` writes the archive world-readable, beside the key it contains](#security-snapshot-writes-the-archive-world-readable-beside-the-key-it-contains)
- [`restore` does not restore file modes](#security-restore-does-not-restore-file-modes-so-the-app-key-comes-back-world-readable)
- [The HuggingFace token is written in cleartext to world-readable runner scripts](#security-the-huggingface-token-is-written-in-cleartext-to-world-readable-runner-scripts-that-the-serve-path-never-removes)
- [First-run setup writes the password database and `.env` world-readable](#footgun-first-run-setup-writes-the-password-database-and-the-env-file-world-readable)

### Failures are returned as normal results

A truncated, failed or partial operation is handed back as if it had completed. The cost is lost
or missing data that nothing reports.

- [A cut-off model stream is reported as a complete answer](#error-handling-a-stream-that-ends-without-done-or-is-cut-off-at-the-token-limit-is-reported-as-a-complete-answer)
- [Compaction drops messages it never summarized](#bug-compaction-rewrites-the-wrong-slice-of-the-session-history-dropping-messages-it-never-summarized)
- [A failing vector collection is reported as an empty, healthy one](#error-handling-a-collection-that-fails-is-reported-as-an-empty-healthy-lane-so-retrieval-returns-nothing-with-no-diagnostic)
- [A duplicate event UID discards a calendar's whole pull](#bug-a-vevent-uid-that-another-calendar-already-holds-discards-that-calendars-whole-pull-while-the-counts-still-report-it-as-synced)
- [The research library omits saved partial reports](#bug-the-research-library-silently-drops-saved-partial-reports-with-null-statistics)

## Outside the backend

No non-backend section holds a high-severity finding, so the fix-first table stands. Three patterns
run through these 23 sections.

### The written material describes a different program than the code

27 of the run's 30 `DOC-DRIFT` findings are here — 11 in the 61 specification files, 7 in the root
documents, 9 across the website, build and companion files — against 3 in the 35 backend sections.

**Shared fix:** one pass over `specs/`, the root documents and `website/` that re-derives each claim
from the code at the reviewed commit, security-relevant claims first.

- [26 of the 61 specs are stamped with a baseline commit that does not exist in this repository](#doc-drift-26-of-the-61-specs-are-stamped-with-a-baseline-commit-that-does-not-exist-in-this-repository)
- [The threat model does not state multi-user data isolation as a goal](#doc-drift-the-threat-model-does-not-state-multi-user-data-isolation-as-a-goal-while-the-code-enforces-owner-scoping-and-this-audit-found-that-enforcement-failing)
- [`SECURITY.md`'s fork-publishing scan returns two dozen false positives on the repository it ships with](#doc-drift-securitymds-fork-publishing-scan-returns-two-dozen-false-positives-on-the-repository-it-ships-with)
- [The pairing credential is described as one-time but is a permanent, replayable bearer token](#doc-drift-the-pairing-credential-is-described-as-one-time-but-is-a-permanent-replayable-bearer-token)
- [`shell-mcp.md` describes `ShellService` as "safe command execution" with "output caps"](#doc-drift-shell-mcpmd-describes-shellservice-as-safe-command-execution-with-output-caps)

### Escaping does not fit its context

Seven client-side sinks interpolate untrusted text into markup: a web page's `<title>` into the
research spinner, a model-authored theme name into the theme grid and the slash replies, MCP tool
metadata and calendar locations into quoted attributes, an email's `style` and `poster` URLs into
CSS. Two files use the right escaper one context too early — `_esc` is a `textContent` round-trip,
so it does not escape a quote inside an attribute.

**The policy, not the code, keeps this short of script execution.** The chat page carries
`script-src 'self' 'nonce-…'` with no `'unsafe-inline'` (`core/middleware.py:141-147`), so injected
handlers are refused; the report page is served with `'unsafe-inline'` (`:115-123`), where the same
injection executes.

**Shared fix:** escape at the sink, in the context it is written into, and treat a relaxed policy
anywhere as turning every one of these into an execution bug.

- [A hostile search-result title reaches the research spinner's `innerHTML`](#security-a-hostile-search-result-title-reaches-the-research-spinners-innerhtml-injecting-markup-into-the-app-origin)
- [A stored custom-theme name is rendered into the theme grid as markup on every page load](#security-a-stored-custom-theme-name-is-rendered-into-the-theme-grid-as-markup-on-every-page-load)
- [The MCP tool list shadows the quote-escaping `esc` with a weaker local one](#security-the-mcp-tool-list-shadows-the-quote-escaping-esc-with-a-weaker-local-one-so-tool-metadata-injects-markup)
- [A calendar event's location is only partly escaped](#security-a-calendar-events-location-is-only-partly-escaped-so-a-synced-or-imported-event-injects-html-and-css-into-the-calendar-ui)
- [A sender's display name and attachment filename escape their attribute](#security-a-senders-display-name-and-attachment-filename-escape-their-attribute-because-_esc-is-used-where-an-attribute-escaper-is-needed)
- [The email HTML sanitizer keeps remote URLs in inline styles and `poster`](#security-the-email-html-sanitizer-keeps-remote-urls-in-inline-styles-and-poster-so-an-html-mail-beacons-without-the-users-consent)

### The tests pin a copy of the code, so they pass when it changes

The recurring defect in the 8 tests sections is a test that reproduces the logic it is meant to
check — a source substring, a hand-written copy of the module, or a stub that replaces the very
guard under test. Such a file stays green when the behaviour it names is removed, which is why
several of these findings were proved by making the module unimportable and watching the file pass.

**Shared fix:** drive the real call path. Where a unit is hard to reach, say so in the test rather
than testing a transcription of it.

- [Four source-text "pins" pass with the code they name made unimportable](#bug-four-source-text-pins-pass-with-the-code-they-name-made-unimportable)
- [Every CalDAV test-connection test runs with the URL guard stubbed out](#security-every-caldav-test-connection-test-runs-with-the-url-guard-stubbed-out) — neutering the real guard leaves the suite green while the guard's own suite collapses to 17 failures
- [The `web_search` sources tests assert on a copy of the fix](#bug-the-web_search-sources-tests-in-test_agent_looppy-assert-on-a-copy-of-the-fix-so-reverting-the-fix-leaves-the-suite-green)
- [The Cookbook source-text guards pass against a file with no implementation](#bug-the-cookbook-source-text-guards-pass-against-a-file-with-no-implementation)
- [`conftest.py`'s pre-import block makes the module-scope stub guards dead in 23 files](#doc-drift-conftestpys-pre-import-block-makes-the-module-scope-stub-guards-for-the-modules-it-pre-imports-dead-in-23-files)
- [`test_chat_route_tool_policy.py`'s functional half re-implements the tool policy](#bug-test_chat_route_tool_policypys-functional-half-re-implements-the-tool-policy-and-passes-with-routeschat_routes-unimportable)

## What this pass does not establish

- **The test sections sampled rather than read the suite.** `tests-rest` read 47 of its 322 files
  end to end and did not open 267; `tests-llm-tools` read 46 of 121; `tests-cookbook-models` read 59
  of 112. Each states its sample and method, so the tests findings are the shape of what a sample
  turns up, not a count of the suite.
- **No build or deployment was run.** Measurements are the probes each finding quotes.
- **Most findings carry first-pass evidence only.** The
  [re-review on 2026-10-04](#re-review-2026-10-04) re-derived the 26 findings then rated high or
  medium, confirmed all 26 and lowered 10 severities. Nothing found since has been re-reviewed.
- **A finding count is a floor.** It is set by what was read. A file this pass did not read has not
  been checked.

Suspected defects that did not survive checking are under
[Hypotheses tested and rejected](#hypotheses-tested-and-rejected).
