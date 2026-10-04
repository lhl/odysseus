# odysseus Code Audit

| | |
| --- | --- |
| **Audit date** | 2026-10-03 |
| **Snapshot** | `2992bf6d368a` of https://github.com/odysseus-dev/odysseus |
| **Run** | `odysseus/2026-10-03T2340` |
| **Findings** | 190 — 3 high, 61 medium, 126 low |
| **Scope** | Self-hosted AI workspace: a FastAPI backend and a large first-party front end covering chat, an agent loop with a tool surface, email, calendar, documents and RAG, memory, research, model serving, and MCP. Python 3.11+ with a stdlib-plus-FastAPI backend. |
| **Language** | python |
| **Method** | Static analysis at the snapshot. Every cited line was re-read there. Claims that a command could settle were run, and the result is recorded with the finding. Anything that could not be run says so. |
| **Not covered** | See [Coverage boundaries](#coverage-boundaries). A file this pass did not read has not been checked. |

## How to read this document

Each finding carries a tag, a location, a severity, a disposition, evidence, impact, and a
suggested fix. Evidence quotes the code or reports a command and its result. Quoted code
and line anchors refer to `2992bf6d368a`; re-read them there rather than trusting a line
number after the code has moved.

- **Mitigations.** Where something else already limits an issue, the finding says so and
  the severity reflects it. A hypothesis that did not survive checking is recorded under
  [Coverage boundaries](#coverage-boundaries) rather than as a finding.
- **Unresolved state.** A finding that depends on something the repository does not show
  says what would settle it.
- **Coverage.** Each section states what was read fully, what was read partially, and what
  was not read.
- **Counting.** The tables under [Findings at a glance](#findings-at-a-glance) are computed
  from the findings by `./audit.py build`. `./audit.py check` fails when the counts in this
  header disagree with the sections, so the two cannot drift apart.
- **Editing.** Edit `sources/` and rebuild. `README.md` is generated, and `check` fails on
  a hand edit.
- **Credentials.** `./audit.py check` reads every secret-looking assignment in the target
  tree and fails if one appears anywhere in the run. No credential is quoted here.

## Tag legend

Each finding has one tag.

| Tag | Meaning |
| --- | --- |
| `BUG` | The code does not do what it is written to do. |
| `SECURITY` | Authentication, authorization, credentials, injection, or a trust boundary. |
| `RACE` | Concurrency, timing, or ordering hazard. |
| `PERF` | Avoidable work, unbounded growth, or a leak. |
| `FOOTGUN` | Correct today, but a likely next edit breaks it. |
| `DEAD-CODE` | Unreachable, unused, or permanently disabled code. |
| `DUP` | Duplicated logic. |
| `HARDCODE` | A constant or environment-specific value in source. |
| `UNDOCUMENTED` | Non-obvious behaviour with no documentation. |
| `DOC-DRIFT` | A document states something the code or configuration does not do. |
| `ERROR-HANDLING` | Swallowed, misclassified, or missing error paths. |
| `TYPE-SAFETY` | An unsafe cast or an unchecked narrowing. |
| `TEST-GAP` | A specific path with no test coverage, or a test no gate runs. |
| `REFACTOR` | Structure that needs rework before it can be changed safely. |
| `DEPENDENCY` | A third-party version, pin, or vendor boundary. |
| `GATE-GAP` | A check the release process assumes but no gate runs. |

## Severity legend

| Severity | Meaning |
| --- | --- |
| **high** | Breaks a shipped user flow, loses user data, or is exploitable. Correct before the next release. |
| **medium** | Wrong behaviour under identifiable conditions, or a mechanism that does not deliver what it claims. |
| **low** | Limited impact, or a hazard that needs one more mistake to cause harm. |

Severity rates impact and reachability, not fix effort. A low count is a result, not a
missing search.

## Disposition legend

The disposition is the maintainer's decision about the finding, and it is not derived from
the code. `./audit.py check` fails when a finding has no disposition.

| Disposition | Meaning |
| --- | --- |
| `fix-now` | Correct before the next release. |
| `next` | Owned by the next release; add it to that release's plan. |
| `backlog` | Real, accepted, and not scheduled. |
| `wontfix` | Recorded and deliberately not corrected. The finding states why. |

A finding may also carry an `**Issue:**` field naming the public issue that tracks it.

# Executive summary

**Findings: 190 — 3 high, 61 medium, 126 low**, on the thirty-five sections this pass read.

A re-review on 2026-10-04 re-derived the five findings then rated high and 21 of the 67 then rated
medium against the source at `2992bf6d368a`. All 26 defects were confirmed; none was removed. Ten
severities moved down: two high to medium and eight medium to low. The other 46 mediums and all the
lows the first pass recorded carry only their original evidence. The changes and the reasons are
under [Re-review, 2026-10-04](#re-review-2026-10-04).

This is a first pass over a 58-section scope. Thirty-five sections are done. `src-security` — the guards
the rest of the backend calls into: outbound URL admission, credential encryption at rest, secret
scrubbing for non-admin callers, privilege gating, upload caps, and the prompt-injection wrapper —
produced 7 findings, 1 medium and 6 low. `src-agent-loop` — intent routing, tool retrieval,
prompt assembly, the multi-round execution loop, the detached-run manager, the background-activity
gate, and the exact-action approval store — produced 7 more, 2 medium and 5 low. `src-agent-tools`
— the 22 files the dispatcher calls: the tool registry, the filesystem, shell, web, document,
session, model-interaction, and admin tool classes, and the domain functions for notes, calendar,
contacts, vault, research, skills, scheduled tasks, the cookbook, and the internal-API bridge —
produced 9: 1 high, 4 medium, and 4 low. `routes-shell` — the two command endpoints, their
streaming backends, and the Cookbook dependency routes — produced 7: 1 medium and 6 low.
`src-tools-builtin-actions` — `src/builtin_actions.py`, the scheduled-action registry — produced
5: 3 medium and 2 low. `src-tools-parse-exec` — `src/tool_parsing.py` and `src/tool_execution.py`,
the text-to-tool-block parsers and the tool dispatcher with its path-confinement helpers —
produced 5: 1 medium and 4 low. `src-tools-capabilities-policy` — the capability, policy and
security tables, the shared tool helpers, and the built-in MCP registration — produced 1 medium:
the browser MCP's cache gate is off by default while both the setup guide and the design spec
still document it as on. `src-tools-schema-index` — the 71 native function schemas and the
converter that turns their arguments back into tool blocks, the retrieval index that selects
which schemas are sent, and the `do_*` facade — produced 6: 3 medium and 3 low.
`core-auth-session` — `core/auth.py`, `core/session_manager.py`, `core/models.py`,
`core/middleware.py` and `core/log_safety.py`, the process-wide auth and chat-session state —
produced 5: 1 medium and 4 low. `core-data-platform` — `core/database.py`, the schema and its
boot-time migration ladder, the shared atomic JSON writer, the constants and exception shims, and
the POSIX/Windows helpers — produced 6: 3 medium and 3 low. `src-platform` — the shared runtime
layer: `src/constants.py`, `src/runtime_paths.py`, `src/app_initializer.py`, `src/config.py`,
`src/service_health.py`, `src/readiness.py`, `src/user_time.py`, `src/text_helpers.py` and the
`src/search/*` shims — produced 4: 1 medium and 3 low. `routes-rest-auth-admin` — the credential
and administrator surface: `routes/auth_routes.py`, the API-token routes, backup export and import,
the device-flow scaffold and its two providers, the admin wipe, and the shared validators —
produced 4: 1 medium and 3 low. `routes-rest-agent-admin` — the integration surface external
agents call: `routes/codex_routes.py` and its Claude twin, the MCP routes and their shim, the
assistant singleton, and the workspace picker — produced 4: 1 high and 3 low. `routes-rest-notes-contacts-history`
— the notes, contacts and history modules with their three import shims — produced 3: 2 medium and
1 low. `routes-rest-memory-personal-research` — memory CRUD, the personal-file library and the
research job API — produced 3: 2 medium and 1 low. `src-memory-rag` — the JSON memory store and
its ChromaDB vector index, the personal-document index (vector and keyword), the embedding lanes
and clients, and the settings and presets stores — produced 6: 1 high, 2 medium and 3 low, four of
them measured against the real modules with stub collections in place of ChromaDB.
`routes-rest-media-files` — uploads, embedding-model downloads and endpoint configuration, editor
drafts, signatures, presets, user preferences, custom fonts, the emoji proxy, and speech synthesis
and transcription — produced 3: 2 medium and 1 low. `src-research-scheduling` — the
background-job store, the research handler and engine, the task scheduler with its catch-up and
cleanup paths, the cookbook serve reaper, and the teacher-escalation and visual-report generators —
produced 8: 1 medium and 7 low. `routes-rest-integrations-misc` — the webhook, hardware-fit,
compare, vault, diagnostics, search and cleanup routers with their five compatibility shims —
produced 4: 3 medium and 1 low. `routes-models` — the model-endpoint registry and everything built
on it: the per-user model picker, endpoint CRUD, probe and refresh, local discovery, default-chat
resolution, the background cache refresh and the stale-cookbook sweep — produced 5: 1 medium and
4 low. `routes-chat-session` — the core chat and session surface: the SSE chat stream with its
resume, stop and status companions, the rewrite and context-injection endpoints, session create,
list, rename, archive, star, compact, export, delete and bulk delete, the admin all-sessions wipe,
and the shared context builder those routes call — produced 4: 2 medium and 2 low.
`routes-gallery-document` — the photo library with its EXIF extraction, hash de-duplication,
albums, favourites and AI tagging, the image-edit proxies, and document CRUD with version history,
PDF import, page rendering and the signed-reply handoff — produced 5: 1 medium and 4 low.
`routes-skills-calendar-task` — the skills library with its bundle and URL importers, the calendar
with ICS import/export and CalDAV accounts, and the task API with its scheduler-facing schedule
fields — produced 8: 4 medium and 4 low.
`routes-cookbook` — the model-serving cookbook with its remote setup and download flows, the serve
runner builders and the GGUF and vLLM command validators — produced 7: 2 medium and 5 low.
`routes-email` — the IMAP/SMTP routes, the attachment and cache helpers, and the scheduled-send
poller — produced 8: 2 medium and 6 low. That completes the `routes-*` surface.
`src-llm-core` — the LLM call core with its streaming parsers and provider builders, plus context
length discovery and the local-model gate — produced 7: 3 medium and 4 low.
`src-chat-session` — the conversation store's compaction, preprocessing, transcript search, tidy
actions and the assistant-log shim — produced 7: 3 medium and 4 low.
`src-documents` — the document and upload pipeline with its extraction fallbacks and tidy actions —
produced 4: 2 medium and 2 low.
`src-email-integrations` — CalDAV sync and write-back, the integration store, the webhook URL guard
and the email thread parser — produced 4: 2 medium and 2 low.
`src-mcp` — the MCP manager's three transports, tool inventory, prompt rendering and plan-mode
classification, plus its OAuth pieces — produced 5: 1 medium and 4 low. That completes the `src-*`
surface. `services-search` — the provider chain, the SearXNG scrape and its guards, ranking, the
content cache and the `SearchService` facade — produced 5: 1 medium and 4 low.
`services-memory` — the audit and extraction pipeline, the SKILL.md format, the skill store and the
bundle importer — produced 7, all low.
`services-research` — the research service and its compatibility handler, the docs facade and the
report store — produced 4, all low.
`services-hwfit` — the hardware probe, the model catalogue and ranking, the fit analysis and the
Hugging Face discovery paths — produced 6: 1 medium and 5 low.
`services-media` — the YouTube handler, the speech services, the shell facade and the package
`__init__` — produced 7: 2 medium and 5 low. That closes the delegated wave: every `core-*`,
`routes-*`, `src-*` and `services-*` section is now reviewed. The original
`src-tools` section (10,435 lines) was split into
four sub-sections during this pass, because one pass over all eleven of its files could not hold
the evidence standard; `src-tools-builtin-actions`, `src-tools-parse-exec`,
`src-tools-capabilities-policy` and `src-tools-schema-index` are the four
reviewed. The other 23 sections are untouched stubs — the repository root and deployment files,
`specs`, `scripts`, `website`, the eight `static-*`, the eight `tests-*`, `mcp-servers` and
`companion-and-swift`.

In `src-security`, four of the seven describe one thing: the project expresses "is this address
safe to contact" three times, and the copies have drifted. `src/outbound_fetch.py` — the copy on
the web-fetch path, reached by the agent's own fetch tool — omits the RFC 6598 shared range that
the other two block explicitly and that `src/url_safety.py:28-34` documents as a gap CPython will
not catch. The remaining three are independent: a privilege check that skips itself when its
lookup raises, a Fernet key generation path that loses a key under concurrency (measured: 8
threads, 2 distinct keys, 2 callers left holding a key no longer on disk), and a secret scrubber
that stops masking when a secret-shaped key holds a container.

In `src-agent-loop`, the two medium findings both change which tools a turn can use. A regex
intended to catch "work on gpu-box" matches any "on <word>" or "from <word>" phrase, so "add a
meeting on Friday" replaces the retrieved calendar tools with the coding toolset
(`src/agent_loop.py:1182`, `:3990`). The first-turn low-signal shortcut answers a non-English
message with no tools at all, returning before the retrieval path whose comment says non-English
queries should still reach it (`:3544`, `:3885-3887`). The five low findings are a pair of
shadowed prompt constants (117 lines that never reach a prompt), a normalizer that rewrites the
word "star" to "start", a prompt cache that never skips the build it caches, four unused helpers,
and an auto-created document whose result never reaches a native model.

In `src-agent-tools`, the high finding is a missing owner filter. `do_manage_research` accepts an
`owner` argument it never reads, so its list, read, and delete actions operate on every user's
research JSON; the route that serves the same files filters by owner with a comment calling the
unfiltered version a security bug (`src/tools/research.py:17`,
`routes/research/research_routes.py:381-385`). No privilege disables the tool: the
`can_use_research` branch at `routes/chat_routes.py:1562-1563` clears a flag and leaves
`disabled_tools` alone, so every user who can use agent mode reaches it. The `app_api` blocklist
finding is medium. `do_app_api` refuses `/api/tokens`, `/api/users`, `/api/admin`, and `/api/shell`
by prefix-matching the caller's path string, and two later transformations defeat that: the server
percent-decodes, so `/%61pi/tokens` routes as `/api/tokens`, and httpx collapses dot segments
before sending, so `/x/../api/tokens` does too (`src/tools/system.py:669`). It is medium because
the tool is admin-only, is blocked after untrusted content enters a run unless the user approves,
and sits beside `bash` in the same agent.
The other three mediums are mechanisms that do not deliver what they claim: `edit_image` posts to four
routes that do not exist, `manage_tokens` mints tokens without the `ody_` prefix and with a null
owner (the middleware can never authenticate them), and `list_models` probes each endpoint with
synchronous `httpx.get` on the event loop, stalling every concurrent request. The four lows are an
endpoint registration that always fails on a key mismatch, an email-history lookup that sends no
internal headers, a todo file nothing reads, and two facade constants that are unused and
contradict the shell defaults.

In `routes-shell`, the medium finding is the one a user hits by cancelling a long command: killing
the shell leaves its children running, and the timeout path can wait forever because a grandchild
holds the inherited pipes (reproduced with a throwaway script that mirrors the call shape). The six
lows are `timeout: 0` meaning "stop now" in `/api/shell/exec` where the model documents "no
timeout", dependency installs that report a timeout without stopping the install, a tmux tail that
re-reads the whole log every second on the event loop, a cross-site guard placed on the read-only
listing rather than the shell endpoints, tmux wrapper scripts and logs readable by other local
users, and an `install_package` path the UI never calls.

In `src-tools-builtin-actions`, the three mediums are all scoping or reachability failures in
scheduled actions: the email-urgency triage's LLM classifier is unreachable behind an early
`continue`, so the user's editable rules are ignored and the task still errors when no model is
configured; `classify_events` rewrites every user's calendar events and feeds the runner's
personal memories into prompts about other users' event titles; and `daily_brief` reads the
default mailbox instead of the task owner's. The two lows are `action_tidy_calendar`, which is
unreachable and would delete across owners if re-registered, and a sender-signature pass that
records success when it scanned nothing.

In `src-tools-parse-exec`, the medium is dropped context rather than a logic bug, and the first low is an uncaught exception.
The two raw-OpenAI JSON scanners catch only `JSONDecodeError`, so a model response containing
`"function"` followed by ~10,000 nested `[` raises `RecursionError` out of `parse_tool_blocks`
or `strip_tool_blocks`, which no caller catches and the route's only stream handler
(`CancelledError`/`GeneratorExit`) does not; the turn aborts with a truncated stream and nothing
persisted. The dispatcher's MCP fallback forwards no `session_id`, so `BashTool`'s tmux
persistence path — its only consumer — never runs: every bash call is a fresh shell, and `cd` or
exported state does not survive to the next call. The other three lows are the
quadratic scans the file's sibling patterns were already converted to avoid: an `<invoke>`
stripper that lowercases the whole remaining response per block (17s at 1MB), the Gemma tool-call
pattern left on `finditer`/`sub` (24s at 400KB), and a `web_search` JSON rescue that re-decodes
every brace in each mention's 1200-char window (~4s at 240KB).

In `src-tools-schema-index`, the three mediums are all one surface — what a native model is told
it can call. `tail_serve_output` has a schema, a prompt section and a retrieval description but is
missing from the fence-tool set the converter checks, so every native call to it is rejected as an
unknown function and the turn ends as if the model had answered; the cookbook block's own comment
says the other cookbook tools were added to that set for exactly this reason. `manage_research` is
the mirror image: the prompt and the keyword hints route all models to it to read a finished
report, but it has no native schema and native models may not use fences, so the fix for the
report-fetching bug (#1363) does not reach them. The converter also trusts the model's argument
types, so a non-string value for a single-argument tool (`web_search`, `bash`, `read_file`,
`create_document`) crashes the turn instead of returning a tool error. The three lows are two
schema enums that omit actions their handlers implement (`manage_documents` cannot read,
`manage_session` cannot list or switch), three `ToolIndex` members that are assigned and never
read, and an active-email global the front end and the route write on every submit that no code
reads.

In `core-auth-session`, the medium finding is a visibility bug rather than a logic error: the
sidebar list is built from a process-wide cache of the 100 most recently accessed sessions, so
on a multi-user instance one account's activity pushes another account's chats out of the list
entirely (measured: 101 sessions for one owner, two for a second, and the second owner's
`get_sessions_for_user` returns `{}`). The four lows are all mechanisms that do not deliver what
they claim: `save_sessions()` is a no-op that three call sites treat as a persist, and the next
`get_session` re-reads the row over the fields they set (measured on the `/session/openai`
Authorization header); `cleanup_empty_sessions` raises `TypeError` on its first empty session and
rolls back the whole pass (measured; nothing calls it — `src/cleanup_service.py` is the live
path); `redact_url` passes a scheme-less URL through with its `user:pass@` userinfo, which the
endpoint route accepts and the probe logs at WARNING; and `AuthManager.create_session()` issues a
seven-day session from the password alone, skipping TOTP, with no production caller left to
notice.

In `core-data-platform`, the three mediums are one security defect and two costs paid on every
startup. The shared JSON writer, `core/atomic_io.atomic_write_json`, creates its replacement file
at the process umask, so `data/auth.json` (bcrypt hashes, TOTP secrets, backup codes),
`data/sessions.json` (live session tokens) and `data/settings.json` (provider API keys) are left
0o644 while the database beside them is deliberately 0o600 (measured: a 0o600 target becomes
0o644 after one write; the live files are 0o644). The transcript-FTS migration ends with a
`WHERE NOT EXISTS` over an `UNINDEXED` FTS column, so SQLite scans the whole index once per
message — 15.5s at 20,000 messages on every boot, versus 0.03s when the index is actually empty
and a 1.6ms count guard; a `LEFT JOIN` rewrite was measured at 30s and is not a fix. The hourly
null-owner sweep rewrites `memory.json` and `user_prefs.json` with a truncating
`open(..,"w") + json.dump`; the memory store's own reader names that writer as the reason a
corrupt store is reachable. The three lows are `bulk_insert_messages`, which cannot insert a row
(measured: `NOT NULL constraint failed: chat_messages.id`) and is re-exported by the
`src.database` facade; the fail-open import guard that skips all three legacy-encryption
migrations when `src.secret_storage` is imported before `core` (reproduced; `import app` is
safe); and MCP server env vars, stored plaintext in the column next to the table's encrypted
OAuth tokens.

In `src-platform`, the one medium is a dead configuration layer that can still take the server
down. `src/config.py` builds four pydantic settings trees and a global `AppConfig()` at import;
nothing reads a field (`config.data`/`config.llm`/`config.search`/`config.security` appear nowhere
in `src/`, `routes/`, `core/`, `services/` or `app.py`, and the one caller, `app.py:721`'s
`setup_search_routes(config)`, never touches its parameter), yet `app.py:581` imports the module, so
the parse runs on every startup. Measured: `SECURITY_ALLOWED_ORIGINS=https://example.com python -c
"import app"` dies with a `SettingsError` on the list field, and `DATA_MAX_UPLOAD_SIZE=abc` or
`LLM_REQUEST_TIMEOUT=30s` dies with a `ValidationError` — the server does not start, because of
configuration it never consults. Values that do parse are silently inert; the live caps and
extension sets are in `src/upload_handler.py` and `src/chat_helpers.py`. The three lows are
mechanisms that do not deliver what they claim: `initialize_managers` logs "Loaded Brave API key
from saved configuration" after passing the key to `update_search_config`, whose docstring says the
argument is ignored for backward compatibility, and the `APIKeyManager` store it reads has no
production writer; an empty `ODYSSEUS_DATA_DIR` (`DATA_DIR = os.getenv("ODYSSEUS_DATA_DIR",
default)`) resolves to `""`, so `auth.json`, `app.db` and every cache land next to the working
directory — measured, and the fix is the `or` form the neighbouring `FASTEMBED_CACHE_PATH` constant
already documents for exactly this trap; and `CLEANUP_ENABLED` / `CLEANUP_INTERVAL_HOURS` are
documented in `.env.example` and injected by all three compose files, but no code reads either
constant, so an operator who changes the cadence gets the default silently.

In `routes-rest-auth-admin`, the medium finding is an authentication control that does not
distinguish clients in the documented deployment. The login, signup and first-run-setup limiters
are keyed on `request.client.host` (`routes/auth_routes.py:119-121`, `:130`, `:148`, `:167`), which
is the socket peer unless uvicorn's `ProxyHeadersMiddleware` rewrites it — and that middleware only
rewrites it for a peer in its trusted list, which defaults to `127.0.0.1,::1` (uvicorn 0.54.0;
neither `app.py:1306` nor `launcher.py:149` sets `FORWARDED_ALLOW_IPS` and no compose file does
either). The shipped compose publishes the app on the host loopback only
(`docker-compose.yml:14`) and the setup guide tells the operator to proxy to `127.0.0.1:7000`
(`website/setup.md:537`), so requests arrive at the container from the Docker gateway. Measured:
a container publishing `127.0.0.1:18080` sees `peer=::ffff:172.17.0.1` for a host curl, and the
middleware leaves a `172.18.0.1` peer unchanged while rewriting a `127.0.0.1` peer. Every client
shares one 15-per-60s login bucket, so sixteen unauthenticated POSTs lock every user — including
the admin — out of login, and one request every four seconds sustains it. The three lows are
mechanisms that do not deliver what they claim: `admin_create_user` hashes the password on the
event loop (measured 169 ms) while the setup, signup and login paths in the same file offload the
same call to a thread; the API-token list shows every owner's tokens but revoke and rename refuse
any row whose owner is not the caller, which includes every null-owner token the agent's token tool
mints, so the UI's Revoke button silently does nothing; and three admin JSON endpoints raise an
unhandled `AttributeError`/`ValueError` on a non-object body where the rest of the file returns
400.

The notes, contacts and history section contributes a second pair. Its vCard export rebuilds every
card through a builder that supports a postal address, but the export call does not pass the stored
one (`routes/contacts/contacts_routes.py:623-632`, where `:258-260` emits `ADR` only when an
address is supplied and the add and edit paths do pass it at `:420` and `:674`), so an export
silently drops a field the rest of the module preserves; the reviewer measured a round trip through
export and import and got an empty address back. Its other medium is the same blocking shape the
platform section found, in a worse form: the contacts handlers are `async def` around synchronous
CardDAV calls, so a cache-miss list performs a synchronous `REPORT` and a synchronous `GET` with a
10-second timeout on the event loop (`:742-744`, `:305-309`, `:363`), while the reminder sender in
the sibling notes module already offloads its SMTP call with `asyncio.to_thread`
(`routes/note/note_routes.py:392`). Its low is a recurrence rather than a new class: nine notes and
history endpoints parse the body and call `.get` on it without checking that it is a mapping, so a
JSON array or string returns 500 where the module's typed endpoints return 422.

The memory, personal-file and research section adds the first access-control finding in this route
family, narrow but real: memory add and import call
`require_privilege(request, "can_manage_memory")` and nothing else in the module does, so an
account whose administrator turned memory management off can still edit, pin and delete its own
memories and run the consolidating audit (`routes/memory/memory_routes.py:503-513`, `:528-549`,
`:550-566` and `:289-324`, against the only two gate sites at `:106-107` and `:346-347`). Measured
with the privilege flag false: add returns 403, edit, pin and delete all return 200. Owner checks
still hold, so this is a disabled-feature bypass rather than a cross-user one. Its other medium is
silent loss of discoverability: the research library reads `d.get("stats", {}).get("Duration", "")`,
which raises when `stats` is present and null, and the surrounding `except Exception: continue`
swallows it — while the timeout-recovery path saves partial reports without ever assigning `stats`
(`routes/research/research_routes.py:399-408`, `src/research_handler.py:624` and `:357-367`).
Measured: a recovered partial report is saved with a null statistics field and the library returns
`total: 0`. Its low repeats the contacts section's shape: the library listing reads and parses every
stored report on the event loop before applying the result limit.

The three high findings are the ones to fix first, and each fix is small: filter the research
scan by the owner already recorded in each file, pass the framework's background-task object
through to the email send handler, and give the memory store a lock and a unique temp name. The
email one is the cheapest: the Codex and Claude integration tells its caller
`{"success": true, "queued": true}` while the delivery call is attached to a `BackgroundTasks`
instance nothing runs, so every message sent through the documented integration path is dropped
without an error.

The bearer finding is medium. Every authenticated bearer token is stamped with the same
pseudo-user, and the preference, editor-draft and signature routes read that value as the storage
owner, so one token reads and mutates records another token's owner created through those routes.
No shipped bearer client calls those three routers, so the shared bucket holds only what a
third-party client put there, and cookie users' records are not reachable. The fix is unchanged:
resolve the token's owner, as the scope-aware routes already do.

The memory-store finding is a
concurrency defect measured at data loss: with two concurrent writers, an entry was lost in 43 of
50 bursts; with twelve, the store was left unparsable once in 30 bursts and 211 writer calls
raised `FileNotFoundError`, because every writer stages through the same `memory.json.tmp` and
nothing holds a lock across the read-modify-write.

The medium set is a cluster of tools that report success without
working, worth one pass comparing the schema against the registry, plus three scheduled actions
that lost their owner scope or their configured model, one dispatcher path that loses context
(a bash session that is never reused), one document that
promises a startup behavior the code no longer has, one dead settings tree that can still
stop the server from starting, and one rate limiter that keys on a peer the deployment makes
constant.

## What this pass does not establish

The reviewed surface is thirty-five sections of fifty-eight. A file this pass did not read has not been
checked, and the two largest trees in the repository — the front end and the test suite — were not
read at all. Read the coverage statements before treating any count here as a property of the
codebase.

Within the sections that *were* read, the largest gap is now the route handlers each tool invokes
and the scheduler that invokes the built-in actions (`src-research-scheduling`). The embedding
lanes `ToolIndex` retrieves through are now reviewed (`src-memory-rag`), and the first thing that
review turned up is that they fail silently: a collection that errors is reported as an empty,
healthy lane, and a search over it returns nothing without a query or a log line. This pass establishes
what each tool does once it is reached, which path the dispatcher takes, what the capability,
policy and plan-mode tables admit, which tools a model is actually told about, the shared
runtime, settings and health layer the policy reads, and — in the first route section read — how
the credential and administrator surface authenticates, authorizes and scopes its callers; it does
not establish the same for the other fifty-six route files. `core-data-platform` and `src-platform`
now cover the schema, the migration ladder and the runtime surface those routes read, and
`routes-rest-auth-admin` covers the routes that issue and revoke the sessions they use, so the
remaining backend gaps are the other route handlers themselves. Coverage should proceed through
the rest of the `routes-*` sections next.

Eighty-nine hypotheses that looked like findings did not survive checking and are recorded under
[Coverage boundaries](#coverage-boundaries): that `can_use_bash` is unenforced, that the container
check in `src/host_docker_access.py` is an authorization gate, that a chat-session approval grant
can be forged through a client metadata blob, that the prompt cache's missing `mcp_disabled_map`
key leaks disabled MCP tools into the prompt, that a mid-batch tool budget hit misaligns native
tool calls with their results, that the email-result zero-count guard discards runs that processed
mail, that a cached sender-signature row can crash on a NULL timestamp, the four an earlier pass
closed (an `app_api` SSRF, a research-id
traversal, `manage_tokens` owner scoping, and a `todowrite` path escape), and the seven this pass
closed (that `web_search`'s post-context availability or `web_fetch`'s plan-mode entry is an
egress gap, that the browser MCP's `--no-sandbox` default or its cache-probe fallback is a defect,
that a mutating `manage_*` action is classified read, that an unknown `mcp__email__` name is
aliased, and that a fence-callable tool is missing from the plan-mode partition), and the eight
this pass closed (that every fence-only tool is reachable another way, that `generate_image`'s
missing schema is the same gap as `manage_research`'s, that the empty-argument guard catches a
non-string value, that the other multiplexed tools' enums drift, that a `tail_serve_output` native
call reaches the dispatcher by another route, that a trailing comma in `list_email_accounts` is a
syntax defect, that `ToolIndex._fingerprint` gates the index rebuild, and that `get_active_email`
has an out-of-tree caller), and the seven the auth/session pass closed (that `message_count` drift
truncates the model context or inflates the displayed total, that `require_admin`'s raw
internal-token header is a remote admin bypass, that `get_sessions_for_user(None)` returns every
owner's sessions, that delete/rename leave the affected user's API tokens live, that
`change_password` leaves a stolen cookie valid, that the security-header nonce is unused, and
that `archive_session`/`mark_important` are the live archive paths), and the three the
database/platform pass closed (that the ssh port in `core/platform_compat._ssh_exec_argv` is
injectable — every caller validates it first, that the plaintext OAuth token columns are an
undocumented encryption gap — `specs/persistence.md:99` documents the manual encryption, and that
the `Integration` model is a second integrations store that has drifted — it is dead schema with
no reader or writer), and the four the platform pass closed (that the health report leaks
credentials through probe errors or endpoint URLs — `_classify_error` never returns the exception
text and `_safe_url` strips userinfo and the query; that `_bounded_map` leaks worker threads when a
probe hangs — each probe carries its own socket timeout; that the front-end persona list has
drifted from `src/reminder_personas.py` — the five IDs match exactly today; and that the unused
`src/app_helpers.py` helpers are a reachable path — neither has a caller), and the four the
auth/admin route pass closed (that a first-run setup race lets two callers both create the admin —
`setup` re-checks under its own lock and `create_user` takes the config lock; that `rename_user`
leaves file-backed owner references behind — every store it touches was traced, and the prefs
`_users` key, the research JSONs, `memory.json`, uploads, personal RAG, skills and the in-memory
session and token caches are all handled; that the Danger Zone's chats wipe mirrors
`/api/sessions/all` as its docstring says — it skips the image deactivation and file unlink, but
the modal text makes the narrower behavior deliberate, so the comment is stale rather than the
code wrong; and that the backup import's memory merge is a lost-update race — it is, but the
missing lock is `src/memory.py`'s, assigned to `src-memory-rag`, so it is noted there rather than
reported here), and the eight the agent/admin route pass closed (that a read-scoped todo token can
perform a write — the route's write set is a superset of the actions that write, aliases included;
that a cookie caller reaches the cookbook surface without admin — the scope helper adds
`require_admin` for every non-token caller; that the capabilities and timezone endpoints are
unauthenticated — the middleware covers both and neither payload is owner data; that
`enabled_tools` lets a non-admin grant admin tools — the dispatcher gates on the owner's blocked
set; that the MCP OAuth path confinement can be escaped — symlinks and `..` are both rejected
against the resolved base; that `_redact_task` misses a stored secret — the two keys it strips are
the two the launcher writes; that the `sys.modules` shim breaks importers — one module object is
reachable every documented way; and that `_as_owner` leaks its substituted identity — it restores
state in a `finally` and Starlette's state is per request), and the nine the notes/contacts/history
pass closed (that the three flat shims diverge from their canonical modules — each import resolves
to the same module object; that contacts leak across owners — contacts are a shared admin-only
address book rather than a per-owner store, which the reviewer corrected in that section's
Overview; that the notes list endpoint shows rows the id-based operations refuse — the list filters
by owner and the id operations reject mismatched or null owners; that history message edit and
delete reach another owner's rows — session ownership is verified first and the queries constrain
the session id; that topic analysis leaks across owners — it requires an owner and returns empty
without one; that an explicit history page size is unbounded — supplied limits clamp to 1–100 and
the no-limit full-history mode is deliberate; that a CardDAV href or UID can escape the configured
origin — hrefs are pinned to the origin, UID paths are quoted and base URLs are validated, though
DNS rebinding was not established either way; that non-string import fields or a null contact name
crash the importer — the fields are coerced and the name has a fallback, and the typed endpoints
answer 422; and that the history module's compaction timestamp ordering is a shipped defect — that
implementation is shadowed by the session router registered earlier, which the reviewer confirmed
with a sentinel request, so it is unreachable code rather than a live defect and is worth knowing
before anyone edits it), and the nine the memory/personal/research pass closed (that memory reads,
edits and deletes lack owner checks — filtered loads and explicit owner checks protect them, which
is what separates that section's privilege finding from an owner-isolation one; that session-keyed
memory operations expose another user's chat — session ownership guards cover extraction and
metadata access; that research report reads and deletes lack owner checks — disk and active-task
owner gates protect them and the focused suites pass; that research identifiers permit traversal or
symlink escape — identifier validation and resolved-path confinement reject them; that personal
global listings expose data to ordinary users — administrative dependencies protect listing and
directory management and uploads derive ownership from authenticated state; that personal deletion
or directory management escapes the filesystem boundary — resolved-path checks and the confinement
suites reject it, with global vector removal remaining an administrative operation; that the flat
shims diverge — the alias identity and monkeypatch suites pass; that the non-object-body error
recurs — all four JSON-body routes answer 422 for an array or a string; and that a research launch
discards its background work — the live handler retains the asyncio task and handles cancellation,
timeout and errors), and the twelve the model-serving pass closed (that a non-admin can register or
probe an endpoint and point a stored key at a caller-chosen URL — every probe and registration route
calls `require_admin` and the one caller-supplied key is admin-only; that stored keys are echoed on
read — responses carry a fingerprint only; that a non-admin reads another owner's endpoint config —
`owner_filter` and the admin-gated by-id routes hold; that any of these routes is unauthenticated or
that `require_admin` fails open on an unconfigured instance — neither holds; that the UI's add form
stores a query URL — it strips `?`/`#`, which is why the markdown button is the reachable path; and
that the orphaned-auth sweep can delete a live row — its only call site passes the deleted id), and
the fifteen the chat/session pass closed (that a mutating endpoint touches a row the caller does not
own — every chat and session endpoint resolves through `_verify_session_owner` except the purge the
section reports; that `GET /api/search` leaks other owners' messages — the owner filter and legacy
flag are set; that attachment or image ids escape the upload root — both helpers re-check
confinement and return `None`; that the stream hides a provider failure or leaks its registry on
disconnect — the detached path publishes an error event, pops the registry and evicts the buffer;
that session deletion orphans messages, the tidy deletes other owners' rows, the ghost branch
reaches another owner's in-memory session, the rewrite touches another owner's row, or the coercion
helper 500s on a list body — none holds; that the workspace helpers let a token bind a workspace — a
bearer caller is not an admin, so it is dropped; and that image generation keeps running after a
compare-pane stop — the task is indeed not cancelled, but the UI combination was not verified, so it
is not reported), and the twelve the gallery/document pass closed (that a filename, upload id or
image id escapes its directory — the path helpers sanitize, resolve and re-check the root, and the
confinement suites pass; that a read, update or delete is not owner-scoped — every query was walked
and the list and by-id paths agree; that an upload is unbounded or trusts the client's type — the
byte caps, the fixed extension set and the content detector hold; that one user's image-endpoint key
reaches another's — the query goes through `owner_filter`; that cross-owner deletion rides the chat
cleanup in the delete path — a match needs the owner's own message to reference the image; and that
an orphan file, a public cache header, a missing dimension cap, an abandoned compose copy or the
upload rate limiter is a finding here — none survived checking), and the eleven the
skills/calendar/task pass closed (that a skill name or bundle key escapes the skills directory —
slugify, a non-following walk and a relative-path check reject it; that the URL importer is an SSRF
— hosts are pinned, redirects re-validated and the socket pinned to the DNS snapshot; that a task's
owner can be set from the body — the models carry no owner field and the handler writes the
caller's; that an event read or write is not owner-scoped — the by-id helpers and the list filter
hold; that an imported ICS fetches a URL or injects export lines — the loop reads six fields and
the export escapes; that a mutating endpoint in these families lacks its admin gate — the gates and
the execution-time recheck hold; that `compute_next_run` never fires for other inputs — the monthly
and time branches clamp or fail closed; that `clear-cache` wipes other owners' database rows — only
the files are unscoped; that `?force=true` is a concurrency hole — it is the documented parallel
start; and that the CalDAV paths block the loop — they offload), and the seven the cookbook pass
closed (that the recipe-refresh endpoints and their cache are findings — the first is the same
reachable-but-not-reported call the model routes produced and the second shows no growth; that
`repo` in the recipe route is an SSRF or traversal — the host is fixed; that the runner scripts need
`0o755` — `bash <script>` does not; that the Windows setup branch escapes the quoting defect — it
does not; that the GGUF-prelude bypass reaches a non-admin — both callers are admin-only; and that
the two `_diagnose_serve_output` tables differ in their shared suggestions — 23 shared keys, none
different), and the six the email pass closed (that the list route is not owner-scoped — the probe
reaches `_assert_owns_account` with a foreign account id; that `attachment_extract_dir` is a path
traversal — the values are flattened and re-checked against the base; that the non-object-body 500
class covers the other JSON endpoints — they take `data: dict` or a model and get 422; that the
metadata fallback leaks another owner's rows — the owner predicate stays; that the thread-turn
cache serves current data across owners — nothing writes it in this tree; and that an email body
reaches the front end unsanitized — the sanitizer runs at all three call sites), and the five the
LLM-core pass closed (that a string-valued session header or a list-content system message breaks
the request builders — no live writer produces either; that the capability-reader package is dead
code — the spec records it as not yet wired; that a caller-supplied endpoint URL or model name can
redirect a request or attach a stored credential — the resolver takes both from the caller's own
row; and, on the hand-off from this section, that `POST /api/v1/chat` lets a token holder point the
server at any host — the token-supplied URL passes `validate_public_http_url`, which fails closed on
DNS and rejects private targets), and the four the conversation pass closed (that the order-dependent
test failure it saw is a second defect — it is the same pair the chat-session section reports; that
the compactor's own tests catch the slice loss — they stub the history rewrite out; that the
summary-failure test covers the empty-summary path — it exercises a raising call, not an empty one;
and that an empty owner is harmless in `run_auto_sort` — the probe deletes every owner's sessions),
and the fourteen the document pass closed (that a forged upload id or a crafted generated-image path
reads or escapes another owner's file — the marker resolves through an owner-scoped lookup and the
path passes a hex check plus `commonpath`; that an upload can collide across owners — the name is a
UUID in a date directory and dedup matches on hash and owner; that a malformed or hostile PDF
crashes the path or forges a form bullet — six inputs degrade to a failure string and the field
renderer escapes its label; that a null-owner document is readable or the active-document pointer
leaks across users — the owner check and the pointer's predicate both hold; that `run_document_tidy`
deletes across owners — its falsy-owner branch is the documented single-user mode, unlike the tidy
in the conversation section; that the native extractor is a zip bomb or the tidy blocks the loop —
the exposure is shared with the primary path and the tidy measured 153 ms for 500 documents; that
`get_upload_info` is dead or `upload_id` loses a link — the tests exercise the first and the second
has no consumer; that `.html` uploads are stored XSS or the PDF fill/stamp paths escape — the
download is an attachment with `nosniff` and the outputs are temp files; that a failed `uploads.json`
write orphans a file — no independent trigger; and that `extract_fields` 500s the import route —
unverifiable without PyMuPDF, so dropped rather than asserted), and the four the integrations pass
closed (that a `//host` path moves an `api_call` to another host — the join strips every leading
slash before `urljoin`; that the parser's turn HTML is a new XSS surface — the client sanitizes it;
that the integration store's read-modify-write interleaves — no writer awaits inside its
load-and-save block and the server runs one worker; and that a successful `api_call` without the
untrusted flag arms the gate less — the tool is registered `EXTERNAL_UNTRUSTED`, which the gate
consults for both outcomes), and the five the MCP pass closed (that a wedged server also strands the
Streamable HTTP transport — the SDK sets httpx timeouts there; that disconnecting a server orphans
its child — the SDK's generator reaps it before the task group exits; that a hostile stdio server
gains something it could not already do — it is arbitrary code either way, so only the secrets that
exist solely in the environment are added; and that the plan-mode gate is unreliable — the
classifier is pinned with direct annotations, only the per-transport discovery is unpinned). The
search pass closed thirteen, among them that the admin-set `search_url` is a provider-layer SSRF
(admin-only write, localhost default, no credential attached), that a non-string query crashes
ranking (guarded in `query.py` and coerced by both callers), that cache keys collide across owners
or queries (sha256 over query, count, filter and URL cap), that a corrupt cache entry is served or
crashes the caller (both read paths catch, unlink and refetch), that failed fetches are cached so a
guard verdict sticks (the failure paths return before the write), and that huge pages make
extraction unbounded (1.9 s for 1.37 MB under the 2 MB cap). The memory pass closed eleven more,
including that an import can overwrite another owner's skill (names are deduped against every
owner and `_safe_relpath` rejects traversal), that a hostile bundle escapes the skills directory
(every write goes through that same helper), that `read_skill_reference` can be walked out (realpath
plus commonpath), that a malformed LLM reply writes a partial record over a good store (the parser
returns empty, extraction returns before saving, and the read-modify-write uses the strict loader),
and that a hostile directory listing makes the importer recurse without bound (depth, file count and
byte total bound the walk). The research pass closed seven, including that the compatibility
handler's records leak another owner's report (the live route hides ownerless records and nothing
calls the copy), that its own source parser cannot read its report (disproved by probe), that the
docs facade reads a different Chroma store than the app (the persist directory is only used for a
`mkdir`), that a missing timeout leaves a job running forever (every inner call carries its own), and
that the duplicated handler is undocumented dead code (it is documented compatibility surface with a
retirement item). The hardware pass closed eleven, including that a caller-supplied host or port
reaches a shell (the host is one ssh argv element and the exec helper rejects a leading `-`), that a
caller-supplied model path becomes an arbitrary file read (path handling lives in the route layer and
the reader only opens `/proc` files), that a hung probe leaves the remote target set (every
exception is caught and each assignment is cleared before return), that a zero or missing VRAM
divides by zero (every divisor is guarded), and that the empty image-model registry means the image
list is always empty (the collections supply rows when the fetch succeeds). The media pass closed
thirteen more, including that the TTS cache key collides across users (it hashes provider, model,
voice, speed and text), that the speed setting is ignored locally (each provider applies it once),
that a playlist link is still web-fetched (the context builder filters every YouTube-shaped URL out),
that `ShellService` is what the live shell routes call (the route layer has its own helpers), that the
comment-fetch timeout is broken (it is wrapped with kill-and-reap and pinned), and that the fetch can
be aimed at an internal address or inject an argument (fixed URL template, argv list, no shell).
The
observation the
previous pass left unresolved — the encryption-migration
skip in `core/database.py` — is now a finding with a deterministic reproduction and a stated
non-trigger (`import app`).

No build or deployment was run. The commands that were run are the small ones the
findings cite, each with its result; the exception is the capability/policy section's own gate
suites — 240 tests over seven files — and the schema/index section's three suites, 10 tests, and
the auth/session section's three suites, 15 tests, and the database/platform section's nine
suites, 148 tests, the platform section's thirteen suites, 141 tests, the auth/admin route
section's twenty-seven suites, 203 tests, the agent/admin route section's twenty-one suites, 170
tests, the notes/contacts/history section's twenty-two suites, 75 tests, and the
memory/personal/research section's sixteen suites, 129 tests, each
run to check the surface that section had just read. Later sections kept the same discipline: the
media/files section ran fifty suites, 231 tests, the research/scheduling section thirty-eight suites,
168 tests, the integrations-misc section fifty-seven suites, 253 tests, and the model-serving
section fifty-four suites, 714 tests, and the chat/session section fifty-five suites — 1 failed, 289
passed, where the failure is the order-dependent test that section reports rather than a broken
product path, and the gallery/document section forty-six suites, 182 tests, and the
skills/calendar/task section sixty-six suites, 319 tests, the cookbook section twenty-six suites,
229 tests with 1 skipped, the email section forty-three suites, 269 tests, and the LLM-core section
forty-four suites, 604 tests, and the conversation section sixty-four suites, 1 failed and 523
passed plus its compactor and budget suites, and the document section forty-eight suites, 217 tests
with 2 skipped, the integrations section thirty-two suites, 163 tests, and the MCP section eighteen
suites, 127 tests, and the search section thirty-three suites, 230 tests, plus the wider
seventy-three-file set at 391 passed and 1 skipped, and the memory section forty-nine suites, 205
tests, and the research section forty-one suites, 245 tests, and the hardware section twenty suites, 126 tests, and the media section twenty-three suites, 150 tests.

# What is under audit

This audit reviews https://github.com/odysseus-dev/odysseus at `2992bf6d368a`, checked out at `/home/lhl/github/lhl/odysseus`.

Self-hosted AI workspace: a FastAPI backend and a large first-party front end covering chat, an agent loop with a tool surface, email, calendar, documents and RAG, memory, research, model serving, and MCP. Python 3.11+ with a stdlib-plus-FastAPI backend.

Describe the repository here in a short paragraph: what it ships, who runs it, and which
of its surfaces carry the most consequence if they are wrong. This is the paragraph a
reader uses to decide whether a finding matters, so name the real product boundary rather
than the directory layout.

## Sections

The run is divided into 58 sections. Each one is a section file under
`sources/sections/`, and each states its own coverage.

1. `repository-root` — Repository root and project policy
2. `build-install-deploy` — Build, install, launcher, CI and containers
3. `specs` — Specifications
4. `scripts` — Operational scripts
5. `core-auth-session` — core: auth, sessions, middleware, models
6. `core-data-platform` — core: database, atomic IO, constants, platform
7. `src-agent-loop` — src: agent loop, runs, approvals and gates
8. `src-llm-core` — src: LLM interaction, endpoints, model capability
9. `src-tools-parse-exec` — src: tool parsing and execution
10. `src-tools-capabilities-policy` — src: tool capabilities, policy and MCP builtins
11. `src-tools-schema-index` — src: tool schemas, index and implementations
12. `src-tools-builtin-actions` — src: scheduled built-in actions
13. `src-agent-tools` — src: agent tool implementations
14. `src-security` — src: prompt security, secrets, URL safety, limits
15. `src-chat-session` — src: chat processing, context and sessions
16. `src-memory-rag` — src: memory, RAG, embeddings and settings
17. `src-documents` — src: documents, uploads, PDF and office
18. `src-email-integrations` — src: email, calendar and integrations
19. `src-research-scheduling` — src: research, scheduling and background work
20. `src-mcp` — src: MCP management and OAuth
21. `src-platform` — src: config, runtime, health and remaining modules
22. `routes-email` — routes: email
23. `routes-cookbook` — routes: cookbook
24. `routes-chat-session` — routes: chat and session
25. `routes-models` — routes: model serving
26. `routes-shell` — routes: shell and code execution
27. `routes-gallery-document` — routes: gallery and documents
28. `routes-skills-calendar-task` — routes: skills, calendar, tasks
29. `routes-rest-auth-admin` — routes: auth, API tokens, admin and provider sign-in
30. `routes-rest-agent-admin` — routes: assistant, codex, MCP and workspace
31. `routes-rest-notes-contacts-history` — routes: notes, contacts and history
32. `routes-rest-memory-personal-research` — routes: memory, personal files and research
33. `routes-rest-media-files` — routes: uploads, embeddings, presets and preferences
34. `routes-rest-integrations-misc` — routes: webhooks, vault, compare, hardware fit and shims
35. `services-search` — services: search
36. `services-memory` — services: memory
37. `services-research` — services: research and docs
38. `services-hwfit` — services: hardware fit
39. `services-media` — services: shell, STT, TTS, faces, youtube
40. `static-js-editor` — static: image editor
41. `static-js-compare` — static: model comparison UI
42. `static-js-chat` — static: chat, sessions and composer UI
43. `static-js-documents-email` — static: documents, notes, email, calendar UI
44. `static-js-cookbook-settings-models` — static: cookbook, settings, models UI
45. `static-js-research-memory-rag` — static: research, memory and search UI
46. `static-js-rest` — static: remaining first-party JS
47. `static-assets-vendored` — static: vendored libraries, fonts, icons, CSS
48. `mcp-servers` — Bundled MCP servers
49. `companion-and-swift` — Companion apps and Swift clients
50. `website` — Project website
51. `tests-harness` — tests: harness, standards and helpers
52. `tests-security` — tests: security, guard and prompt-injection
53. `tests-email-calendar` — tests: email, calendar and webhooks
54. `tests-cookbook-models` — tests: cookbook, models and providers
55. `tests-llm-tools` — tests: LLM, tools and agent loop
56. `tests-session-chat-memory` — tests: session, chat, memory and RAG
57. `tests-documents-media` — tests: documents, uploads, gallery and media
58. `tests-rest` — tests: remaining test modules

`src-tools` (10,435 lines) was split into the four `src-tools-*` sections at
numbers 9–12 during the review pass, because one pass over all eleven files
would have been too large to review with the evidence standard the rest of the
run holds. The four sub-sections are listed in the order they should be
reviewed; a path appears in exactly one of them.

## How this run was scoped

The sections above were proposed by `./audit.py discover` from the repository's own
directory structure, then edited. Sizes are counted from the working tree at the snapshot.
A directory named in an area's `exclude` list is counted by its own area, so no line is
counted twice.

State here what the division is for. If two sections could be confused, say which one owns
the boundary between them. If a section covers a vendored or generated tree, say so and say
why it is still in scope.

## The release boundary

State what this repository ships and what it inherits. If it vendors, pins, or patches
third-party source, say so here: a finding in pinned third-party code is a finding about
the pin or the patch, not about the upstream project.

If there is a local gate and a continuous-integration gate, name both and say which one
covers what. `./audit.py table odysseus/2026-10-03T2340 gates` lists the commands it detected and
which of them each gate reaches.

## Findings at a glance

### Findings by section

| Section | Findings | High | Medium | Low |
| --- | ---: | ---: | ---: | ---: |
| [Repository root and project policy](#1-repository-root-and-project-policy) | 0 | 0 | 0 | 0 |
| [Build, install, launcher, CI and containers](#2-build-install-launcher-ci-and-containers) | 0 | 0 | 0 | 0 |
| [Specifications](#3-specifications) | 0 | 0 | 0 | 0 |
| [Operational scripts](#4-operational-scripts) | 0 | 0 | 0 | 0 |
| [core: auth, sessions, middleware, models](#5-core-auth-sessions-middleware-models) | 5 | 0 | 1 | 4 |
| [core: database, atomic IO, constants, platform](#6-core-database-atomic-io-constants-platform) | 6 | 0 | 3 | 3 |
| [src: agent loop, runs, approvals and gates](#7-src-agent-loop-runs-approvals-and-gates) | 7 | 0 | 2 | 5 |
| [src: LLM interaction, endpoints, model capability](#8-src-llm-interaction-endpoints-model-capability) | 7 | 0 | 3 | 4 |
| [src: tool parsing and execution](#9-src-tool-parsing-and-execution) | 5 | 0 | 1 | 4 |
| [src: tool capabilities, policy and MCP builtins](#10-src-tool-capabilities-policy-and-mcp-builtins) | 1 | 0 | 1 | 0 |
| [src: tool schemas, index and implementations](#11-src-tool-schemas-index-and-implementations) | 6 | 0 | 3 | 3 |
| [src: scheduled built-in actions](#12-src-scheduled-built-in-actions) | 5 | 0 | 3 | 2 |
| [src: agent tool implementations](#13-src-agent-tool-implementations) | 9 | 1 | 4 | 4 |
| [src: prompt security, secrets, URL safety, limits](#14-src-prompt-security-secrets-url-safety-limits) | 7 | 0 | 1 | 6 |
| [src: chat processing, context and sessions](#15-src-chat-processing-context-and-sessions) | 7 | 0 | 3 | 4 |
| [src: memory, RAG, embeddings and settings](#16-src-memory-rag-embeddings-and-settings) | 6 | 1 | 2 | 3 |
| [src: documents, uploads, PDF and office](#17-src-documents-uploads-pdf-and-office) | 4 | 0 | 2 | 2 |
| [src: email, calendar and integrations](#18-src-email-calendar-and-integrations) | 4 | 0 | 2 | 2 |
| [src: research, scheduling and background work](#19-src-research-scheduling-and-background-work) | 8 | 0 | 1 | 7 |
| [src: MCP management and OAuth](#20-src-mcp-management-and-oauth) | 5 | 0 | 1 | 4 |
| [src: config, runtime, health and remaining modules](#21-src-config-runtime-health-and-remaining-modules) | 4 | 0 | 1 | 3 |
| [routes: email](#22-routes-email) | 8 | 0 | 2 | 6 |
| [routes: cookbook](#23-routes-cookbook) | 7 | 0 | 2 | 5 |
| [routes: chat and session](#24-routes-chat-and-session) | 4 | 0 | 2 | 2 |
| [routes: model serving](#25-routes-model-serving) | 5 | 0 | 1 | 4 |
| [routes: shell and code execution](#26-routes-shell-and-code-execution) | 7 | 0 | 1 | 6 |
| [routes: gallery and documents](#27-routes-gallery-and-documents) | 5 | 0 | 1 | 4 |
| [routes: skills, calendar, tasks](#28-routes-skills-calendar-tasks) | 8 | 0 | 4 | 4 |
| [routes: auth, API tokens, admin and provider sign-in](#29-routes-auth-api-tokens-admin-and-provider-sign-in) | 4 | 0 | 1 | 3 |
| [routes: assistant, codex, MCP and workspace](#30-routes-assistant-codex-mcp-and-workspace) | 4 | 1 | 0 | 3 |
| [routes: notes, contacts and history](#31-routes-notes-contacts-and-history) | 3 | 0 | 2 | 1 |
| [routes: memory, personal files and research](#32-routes-memory-personal-files-and-research) | 3 | 0 | 2 | 1 |
| [routes: uploads, embeddings, presets and preferences](#33-routes-uploads-embeddings-presets-and-preferences) | 3 | 0 | 2 | 1 |
| [routes: webhooks, vault, compare, hardware fit and shims](#34-routes-webhooks-vault-compare-hardware-fit-and-shims) | 4 | 0 | 3 | 1 |
| [services: search](#35-services-search) | 5 | 0 | 1 | 4 |
| [services: memory](#36-services-memory) | 7 | 0 | 0 | 7 |
| [services: research and docs](#37-services-research-and-docs) | 4 | 0 | 0 | 4 |
| [services: hardware fit](#38-services-hardware-fit) | 6 | 0 | 1 | 5 |
| [services: shell, STT, TTS, faces, youtube](#39-services-shell-stt-tts-faces-youtube) | 7 | 0 | 2 | 5 |
| [static: image editor](#40-static-image-editor) | 0 | 0 | 0 | 0 |
| [static: model comparison UI](#41-static-model-comparison-ui) | 0 | 0 | 0 | 0 |
| [static: chat, sessions and composer UI](#42-static-chat-sessions-and-composer-ui) | 0 | 0 | 0 | 0 |
| [static: documents, notes, email, calendar UI](#43-static-documents-notes-email-calendar-ui) | 0 | 0 | 0 | 0 |
| [static: cookbook, settings, models UI](#44-static-cookbook-settings-models-ui) | 0 | 0 | 0 | 0 |
| [static: research, memory and search UI](#45-static-research-memory-and-search-ui) | 0 | 0 | 0 | 0 |
| [static: remaining first-party JS](#46-static-remaining-first-party-js) | 0 | 0 | 0 | 0 |
| [static: vendored libraries, fonts, icons, CSS](#47-static-vendored-libraries-fonts-icons-css) | 0 | 0 | 0 | 0 |
| [Bundled MCP servers](#48-bundled-mcp-servers) | 0 | 0 | 0 | 0 |
| [Companion apps and Swift clients](#49-companion-apps-and-swift-clients) | 0 | 0 | 0 | 0 |
| [Project website](#50-project-website) | 0 | 0 | 0 | 0 |
| [tests: harness, standards and helpers](#51-tests-harness-standards-and-helpers) | 0 | 0 | 0 | 0 |
| [tests: security, guard and prompt-injection](#52-tests-security-guard-and-prompt-injection) | 0 | 0 | 0 | 0 |
| [tests: email, calendar and webhooks](#53-tests-email-calendar-and-webhooks) | 0 | 0 | 0 | 0 |
| [tests: cookbook, models and providers](#54-tests-cookbook-models-and-providers) | 0 | 0 | 0 | 0 |
| [tests: LLM, tools and agent loop](#55-tests-llm-tools-and-agent-loop) | 0 | 0 | 0 | 0 |
| [tests: session, chat, memory and RAG](#56-tests-session-chat-memory-and-rag) | 0 | 0 | 0 | 0 |
| [tests: documents, uploads, gallery and media](#57-tests-documents-uploads-gallery-and-media) | 0 | 0 | 0 | 0 |
| [tests: remaining test modules](#58-tests-remaining-test-modules) | 0 | 0 | 0 | 0 |
| **Total** | **190** | **3** | **61** | **126** |

### Findings by disposition

| Disposition | Findings | High | Medium | Low |
| --- | ---: | ---: | ---: | ---: |
| `fix-now` | 2 | 2 | 0 | 0 |
| `next` | 157 | 1 | 61 | 95 |
| `backlog` | 31 | 0 | 0 | 31 |

### Findings by tag

| Tag | Count |
| --- | ---: |
| `BUG` | 67 |
| `PERF` | 30 |
| `SECURITY` | 29 |
| `ERROR-HANDLING` | 25 |
| `DEAD-CODE` | 16 |
| `RACE` | 6 |
| `FOOTGUN` | 5 |
| `DOC-DRIFT` | 3 |
| `DUP` | 3 |
| `HARDCODE` | 2 |
| `TYPE-SAFETY` | 2 |
| `DEPENDENCY` | 1 |
| `UNDOCUMENTED` | 1 |

### Act on first

Every high-severity finding (3) and every `fix-now` finding, 3 in all.

| Severity | Finding | Location |
| --- | --- | --- |
| high | [`manage_research` ignores the owner and operates on every user's research files](#security-manage_research-ignores-the-owner-and-operates-on-every-users-research-files) | `src/tools/research.py:17` |
| high | [Concurrent memory writes lose entries, raise `FileNotFoundError`, and can leave `memory.json` unreadable](#race-concurrent-memory-writes-lose-entries-raise-filenotfounderror-and-can-leave-memoryjson-unreadable) | `src/memory.py:275-278 (the shared temp path), with :180-186 and :261-274` |
| high | [The Codex and Claude email-send endpoint reports the message queued and never delivers it](#bug-the-codex-and-claude-email-send-endpoint-reports-the-message-queued-and-never-delivers-it) | `routes/codex_routes.py:387 (with routes/email_routes.py:4519, :4708, :4714, :4717, and routes/email_helpers.py:2004)` |

### Medium severity

61 findings: wrong behaviour under identifiable conditions, or a mechanism that does not deliver what it claims. In section order.

| Finding | Disposition | Location |
| --- | --- | --- |
| [The sidebar list is served from a global 100-row cache, so one user's sessions can hide another's](#bug-the-sidebar-list-is-served-from-a-global-100-row-cache-so-one-users-sessions-can-hide-anothers) | next | `core/session_manager.py:96-98 (with routes/session_routes.py:289, :352, and core/session_manager.py:700-707)` |
| [`atomic_write_json` leaves the auth and settings stores at the umask default](#security-atomic_write_json-leaves-the-auth-and-settings-stores-at-the-umask-default) | next | `core/atomic_io.py:32-39 (with core/auth.py:157, :222, src/settings.py:253, routes/prefs_routes.py:27)` |
| [The transcript FTS backfill is quadratic and runs on every startup](#perf-the-transcript-fts-backfill-is-quadratic-and-runs-on-every-startup) | next | `core/database.py:2244-2254 (with :2214, :2145, :2737)` |
| [The hourly null-owner sweep rewrites `memory.json` and `user_prefs.json` non-atomically](#bug-the-hourly-null-owner-sweep-rewrites-memoryjson-and-user_prefsjson-non-atomically) | next | `core/database.py:1481-1482 and :1513-1514 (with :2123, app.py:1225-1226)` |
| [An ordinary "on <word>" phrase switches the turn to the workspace toolset](#bug-an-ordinary-on-word-phrase-switches-the-turn-to-the-workspace-toolset) | next | `src/agent_loop.py:1182` |
| [The first-turn low-signal shortcut answers non-English action requests with no tools](#bug-the-first-turn-low-signal-shortcut-answers-non-english-action-requests-with-no-tools) | next | `src/agent_loop.py:3544` |
| [Context-length discovery runs two synchronous HTTP probes on the event loop, once per local request](#perf-context-length-discovery-runs-two-synchronous-http-probes-on-the-event-loop-once-per-local-request) | next | `src/model_context.py:424 and :450 (_query_context_length), called from src/llm_core.py:2623, :2377, :2017, src/context_compactor.py:338 and routes/chat_helpers.py:791` |
| [Context-length discovery sends no credential, so an authenticated endpoint's real window is never read](#bug-context-length-discovery-sends-no-credential-so-an-authenticated-endpoints-real-window-is-never-read) | next | `src/model_context.py:450 (and :424, :367)` |
| [A stream that ends without `[DONE]`, or is cut off at the token limit, is reported as a complete answer](#error-handling-a-stream-that-ends-without-done-or-is-cut-off-at-the-token-limit-is-reported-as-a-complete-answer) | next | `src/llm_core.py:3337-3343 (the end-of-stream block), :3183-3191 (the delta parser)` |
| [The MCP fallback drops `session_id`, so the per-session tmux shell never runs](#bug-the-mcp-fallback-drops-session_id-so-the-per-session-tmux-shell-never-runs) | next | `src/tool_execution.py:696` |
| [The browser MCP cache gate is off by default, and the setup guide documents the opposite](#doc-drift-the-browser-mcp-cache-gate-is-off-by-default-and-the-setup-guide-documents-the-opposite) | next | `src/builtin_mcp.py:212` |
| [A non-string argument from a native call crashes the turn instead of returning a tool error](#error-handling-a-non-string-argument-from-a-native-call-crashes-the-turn-instead-of-returning-a-tool-error) | next | `src/tool_schemas.py:1416-1419` |
| [`tail_serve_output` is advertised to native models but missing from `TOOL_TAGS`, so every native call is rejected](#bug-tail_serve_output-is-advertised-to-native-models-but-missing-from-tool_tags-so-every-native-call-is-rejected) | next | `src/agent_tools/__init__.py:103-108` |
| [`manage_research` has no native schema, so the report-read path the prompt and RAG steer to is unreachable for native models](#bug-manage_research-has-no-native-schema-so-the-report-read-path-the-prompt-and-rag-steer-to-is-unreachable-for-native-models) | next | `src/agent_loop.py:702` |
| [The email-urgency triage never reaches its LLM classifier, and still requires an LLM endpoint](#bug-the-email-urgency-triage-never-reaches-its-llm-classifier-and-still-requires-an-llm-endpoint) | next | `src/builtin_actions.py:2707` |
| [`classify_events` classifies every user's calendar events with one user's memories](#bug-classify_events-classifies-every-users-calendar-events-with-one-users-memories) | next | `src/builtin_actions.py:1369` |
| [`daily_brief` reads the default mailbox instead of the task owner's](#bug-daily_brief-reads-the-default-mailbox-instead-of-the-task-owners) | next | `src/builtin_actions.py:1828` |
| [The `app_api` path blocklist is bypassed by percent-encoded and dot-segment paths](#security-the-app_api-path-blocklist-is-bypassed-by-percent-encoded-and-dot-segment-paths) | next | `src/tools/system.py:669 (the check), with :675 (the per-method check) and :537-544 (the list)` |
| [`edit_image` calls four routes that do not exist](#bug-edit_image-calls-four-routes-that-do-not-exist) | next | `src/tools/image.py:33` |
| [`manage_tokens` mints tokens the middleware cannot authenticate](#bug-manage_tokens-mints-tokens-the-middleware-cannot-authenticate) | next | `src/agent_tools/admin_tools.py:466` |
| [`list_models` probes endpoints with synchronous HTTP on the event loop](#perf-list_models-probes-endpoints-with-synchronous-http-on-the-event-loop) | next | `src/agent_tools/model_interaction_tools.py:163` |
| [The web fetcher's address guard omits the carrier-grade NAT range the codebase blocks elsewhere](#security-the-web-fetchers-address-guard-omits-the-carrier-grade-nat-range-the-codebase-blocks-elsewhere) | next | `src/outbound_fetch.py:23` |
| [Compaction rewrites the wrong slice of the session history, dropping messages it never summarized](#bug-compaction-rewrites-the-wrong-slice-of-the-session-history-dropping-messages-it-never-summarized) | next | `src/context_compactor.py:504-518 (with :362, :432)` |
| [An empty compaction summary is accepted, replacing the older half with a bare header](#error-handling-an-empty-compaction-summary-is-accepted-replacing-the-older-half-with-a-bare-header) | next | `src/context_compactor.py:410-432` |
| [`preprocess_message` runs the vision-model call inline on the event loop while offloading the vision probe beside it](#perf-preprocess_message-runs-the-vision-model-call-inline-on-the-event-loop-while-offloading-the-vision-probe-beside-it) | next | `src/chat_handler.py:264 (with :209, :217)` |
| [Re-indexing a directory never removes a changed file's previous chunks, so the index keeps serving the old text](#bug-re-indexing-a-directory-never-removes-a-changed-files-previous-chunks-so-the-index-keeps-serving-the-old-text) | next | `src/rag_vector.py:495-556 (index_personal_documents), with :83-91 and :191-198` |
| [A collection that fails is reported as an empty, healthy lane, so retrieval returns nothing with no diagnostic](#error-handling-a-collection-that-fails-is-reported-as-an-empty-healthy-lane-so-retrieval-returns-nothing-with-no-diagnostic) | next | `src/embedding_lanes.py:42-46 (count), with :339-340, :366-373, :387` |
| [A tidy run that finds nothing raises `TaskNoop` out of the agent tool dispatcher instead of returning a result](#bug-a-tidy-run-that-finds-nothing-raises-tasknoop-out-of-the-agent-tool-dispatcher-instead-of-returning-a-result) | next | `src/document_actions.py:189-192 (with src/agent_tools/document_tools.py:883-892, src/tool_execution.py:1133-1145)` |
| [The native `.docx` fallback raises on a damaged or password-protected file instead of degrading](#error-handling-the-native-docx-fallback-raises-on-a-damaged-or-password-protected-file-instead-of-degrading) | next | `src/markitdown_runtime.py:57-61 (the except clause), with the fallback call at :85-97` |
| [A VEVENT UID that another calendar already holds discards that calendar's whole pull, while the counts still report it as synced](#bug-a-vevent-uid-that-another-calendar-already-holds-discards-that-calendars-whole-pull-while-the-counts-still-report-it-as-synced) | next | `src/caldav_sync.py:418, :437-455, :483-486` |
| [The HTML thread parser re-walks each subtree at every nesting level, so a crafted email body occupies a worker thread for ~20 seconds](#perf-the-html-thread-parser-re-walks-each-subtree-at-every-nesting-level-so-a-crafted-email-body-occupies-a-worker-thread-for-20-seconds) | next | `src/email_thread_parser.py:535-548 (_walk, with the same shape in _walk_with_meta at :578-591), :451-463` |
| [A killed background job can still be auto-continued — the job store has no writer lock](#race-a-killed-background-job-can-still-be-auto-continued-the-job-store-has-no-writer-lock) | next | `src/bg_jobs.py:266-283 (kill), :191-235 (refresh), :57-71 (_load/_save), :238-244 (pending_followups)` |
| [Nothing bounds an MCP session call, so a server that stops answering wedges whatever is waiting on it](#bug-nothing-bounds-an-mcp-session-call-so-a-server-that-stops-answering-wedges-whatever-is-waiting-on-it) | next | `src/mcp_manager.py:511 (with :202, :271, :359, :442-458)` |
| [`src/config.py` is an unused settings tree that can still stop the server from starting](#bug-srcconfigpy-is-an-unused-settings-tree-that-can-still-stop-the-server-from-starting) | next | `src/config.py:20-128, :176, :208 (with app.py:581, :721, routes/search/search_routes.py:39)` |
| [The scheduled-send poller starts only when a client asks for the inbox list](#bug-the-scheduled-send-poller-starts-only-when-a-client-asks-for-the-inbox-list) | next | `routes/email_pollers.py:1542-1565 (with routes/email_routes.py:2370-2372, :1514, app.py:863)` |
| [Nineteen `async def` handlers run blocking IMAP, SMTP or HTTP I/O on the event loop](#perf-nineteen-async-def-handlers-run-blocking-imap-smtp-or-http-io-on-the-event-loop) | next | `routes/email_routes.py:3304 (with :3286, :3331, :3393, :3714, :3736, :3753, :3768, :3800, :3815, :3854, :3906, :3992, :4008, :4205, :4474, :5893, :5938, :6059)` |
| [The remote setup endpoint interpolates its install script into a shell command, so no platform receives the script it built](#bug-the-remote-setup-endpoint-interpolates-its-install-script-into-a-shell-command-so-no-platform-receives-the-script-it-built) | next | `routes/cookbook_routes.py:2911 (the Linux command), :2889 (the Termux command), :2881 (the Windows command), :2919 (the success check)` |
| [The MiniMax M3 normalizer rewrites the model argument to a snapshot path under a developer's home directory](#hardcode-the-minimax-m3-normalizer-rewrites-the-model-argument-to-a-snapshot-path-under-a-developers-home-directory) | next | `routes/cookbook_routes.py:666-672` |
| [The session list deletes every owner's incognito rows, not just the caller's](#security-the-session-list-deletes-every-owners-incognito-rows-not-just-the-callers) | next | `routes/session_routes.py:269-277 (with :250-251, :280)` |
| [The chat path runs synchronous LLM, web-search and URL-fetch calls on the event loop](#perf-the-chat-path-runs-synchronous-llm-web-search-and-url-fetch-calls-on-the-event-loop) | next | `routes/chat_helpers.py:737 (with routes/chat_routes.py:607, :799, :1258)` |
| [An endpoint `base_url` carrying a query or fragment is accepted, then breaks the model picker and cannot be deleted](#bug-an-endpoint-base_url-carrying-a-query-or-fragment-is-accepted-then-breaks-the-model-picker-and-cannot-be-deleted) | next | `routes/model_routes.py:1570 (_fetch_models), :2483 (get_default_chat), :2616 (_session_uses_endpoint_url), with the two write boundaries at :1993 (base_url: str = Form(...)) and :2554 (if "base_url" in body)` |
| [Killing the shell leaves its children running, and the timeout path can wait forever](#bug-killing-the-shell-leaves-its-children-running-and-the-timeout-path-can-wait-forever) | next | `routes/shell_routes.py:591` |
| [PDF and image processing runs synchronously inside the async handlers](#perf-pdf-and-image-processing-runs-synchronously-inside-the-async-handlers) | next | `routes/document/document_routes.py:275 (with :530, :1227, :1431, :1554,` |
| [Deleting a cookbook task calls its own API from a blocking client, so the cascade never runs and the delete stalls for 10 seconds](#bug-deleting-a-cookbook-task-calls-its-own-api-from-a-blocking-client-so-the-cascade-never-runs-and-the-delete-stalls-for-10-seconds) | next | `routes/task/task_routes.py:771 (the call), :62-69 (the blocking client), :89-91 (the fallback scan)` |
| [An unvalidated RRULE makes a single calendar read block the event loop for seconds to minutes](#perf-an-unvalidated-rrule-makes-a-single-calendar-read-block-the-event-loop-for-seconds-to-minutes) | next | `routes/calendar_routes.py:752 (the expansion loop), :1249 and :1300 (the unvalidated rrule writes), :1188 (the call site)` |
| [A weekly task with a negative `scheduled_day` is created with a past `next_run` and re-runs forever](#bug-a-weekly-task-with-a-negative-scheduled_day-is-created-with-a-past-next_run-and-re-runs-forever) | next | `src/task_scheduler.py:194-201 (the weekly branch), routes/task/task_routes.py:498-503 (the create path), :148 (the field)` |
| [The ICS import has no event-count cap: a 10 MB file writes 100,000 rows in one 25-second request](#perf-the-ics-import-has-no-event-count-cap-a-10-mb-file-writes-100000-rows-in-one-25-second-request) | next | `routes/calendar_routes.py:1446-1541 (the import loop), :1419 (the byte cap)` |
| [The login, signup and setup limiters key on the socket peer, which the documented deployment makes identical for every client](#security-the-login-signup-and-setup-limiters-key-on-the-socket-peer-which-the-documented-deployment-makes-identical-for-every-client) | next | `routes/auth_routes.py:119-121 (the three limiters), :130, :148, :167 (the .check(request.client.host) call sites)` |
| [CardDAV requests run synchronously inside async contact handlers](#perf-carddav-requests-run-synchronously-inside-async-contact-handlers) | next | `routes/contacts/contacts_routes.py:742-744, with :305-309, :363, :813-825 and :832-837` |
| [vCard export silently drops every contact's postal address](#bug-vcard-export-silently-drops-every-contacts-postal-address) | next | `routes/contacts/contacts_routes.py:623-632, with :258-260 and :843` |
| [Memory pin, edit, delete and audit bypass the memory-management privilege](#security-memory-pin-edit-delete-and-audit-bypass-the-memory-management-privilege) | next | `routes/memory/memory_routes.py:503-513 (pin), :528-549 (edit), :550-566 (delete), :289-324 (audit)` |
| [The research library silently drops saved partial reports with null statistics](#bug-the-research-library-silently-drops-saved-partial-reports-with-null-statistics) | next | `routes/research/research_routes.py:399-407` |
| [Bearer callers share the same preferences, editor drafts and signatures across token owners](#security-bearer-callers-share-the-same-preferences-editor-drafts-and-signatures-across-token-owners) | next | `routes/prefs_routes.py:108-122, routes/editor_draft_routes.py:83-88, :113-118, :171-178, routes/signature_routes.py:88-95, :103-110, :132-139` |
| [Speech, upload processing and vision analysis run blocking work on the request event loop](#perf-speech-upload-processing-and-vision-analysis-run-blocking-work-on-the-request-event-loop) | next | `routes/tts_routes.py:41, :50, routes/stt_routes.py:39, routes/upload_routes.py:291-292, :484` |
| [Bearer callers share one comparison owner and can read and delete each other's records](#security-bearer-callers-share-one-comparison-owner-and-can-read-and-delete-each-others-records) | next | `routes/compare/compare_routes.py:286, :310, :322-327, :348-358` |
| [Hardware-fit routes let non-admins run server-side SSH probes against caller-selected hosts](#security-hardware-fit-routes-let-non-admins-run-server-side-ssh-probes-against-caller-selected-hosts) | next | `routes/hwfit_routes.py:182-191 (router and system route), :319-332, :371 (profiles)` |
| [Both search POST handlers execute synchronous network work on the event loop](#perf-both-search-post-handlers-execute-synchronous-network-work-on-the-event-loop) | next | `routes/search/search_routes.py:60-62, :103` |
| [An upstream HTTP error status puts the Google PSE API key into the log, the returned context and the research report](#security-an-upstream-http-error-status-puts-the-google-pse-api-key-into-the-log-the-returned-context-and-the-research-report) | next | `services/search/providers.py:487-501 (with :472-477, :325-330, :553-558, :614-619)` |
| [One probe's SSH target is process-global, so concurrent requests swap hosts and cache each other's hardware](#race-one-probes-ssh-target-is-process-global-so-concurrent-requests-swap-hosts-and-cache-each-others-hardware) | next | `services/hwfit/hardware.py:21-23 (the globals), :27-31 (_run reads them), :815 and :904 (detect_system sets and clears them), :689 (_cache_by_host)` |
| [A YouTube-shaped URL with no extractable video id is dropped from both the transcript path and the web-fetch path](#bug-a-youtube-shaped-url-with-no-extractable-video-id-is-dropped-from-both-the-transcript-path-and-the-web-fetch-path) | next | `services/youtube/youtube_handler.py:61 (with :78 and the two callers, src/chat_handler.py:149-152 and src/chat_processor.py:461)` |
| [The comment fetch shells out to `yt-dlp`, which no requirement file or image installs](#dependency-the-comment-fetch-shells-out-to-yt-dlp-which-no-requirement-file-or-image-installs) | next | `services/youtube/youtube_handler.py:217 (with _find_ytdlp at :39-45 and the failure branch at :274-276)` |


Each finding below carries its own location, severity, disposition, evidence, impact, and a suggested fix. The tables above are generated from the findings by `audit.py build`, so the counts and the body cannot drift apart.

## 1. Repository root and project policy

### Overview

`ACKNOWLEDGMENTS.md`, `CONTRIBUTING.md`, `LICENSE`, `README.md`, `ROADMAP.md`, `SECURITY.md`, `THREAT_MODEL.md`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 2. Build, install, launcher, CI and containers

### Overview

`.dockerignore`, `.env.example`, `.gitattributes`, `.github/CODEOWNERS`, `.github/ISSUE_TEMPLATE/bug_report.yml`, `.github/ISSUE_TEMPLATE/config.yml`, `.github/ISSUE_TEMPLATE/feature_request.yml`, `.github/dependabot.yml`, `.github/pull_request_review_template.md`, `.github/pull_request_template.md`, `.github/scripts/check-issue-description.js`, `.github/scripts/check-pr-description.js`, `.github/scripts/focused_test_guidance.py`, `.github/workflows/ci.yml`, `.github/workflows/codeql.yml`, `.github/workflows/container-scan.yml`, `.github/workflows/container-trivy.yml`, `.github/workflows/dependency-review.yml`, `.github/workflows/deploy-pages.yml`, `.github/workflows/docker-publish.yml`, `.github/workflows/issue-description-check.yml`, `.github/workflows/pr-description-check.yml`, `.github/workflows/secret-scan.yml`, `.github/workflows/workflow-security.yml`, `.gitignore`, `Dockerfile`, `Odysseus.spec`, `app.py`, `assets/branding/odysseus-browser.jpg`, `assets/branding/odysseus-wordmark.png`, `assets/branding/odysseus.jpg`, `build-macos-app.sh`, `build-windows-portable.ps1`, `config/searxng/settings.yml`, `docker-compose.gpu-amd.yml`, `docker-compose.gpu-nvidia.yml`, `docker-compose.yml`, `docker/build-realesrgan-wheels.sh`, `docker/entrypoint.sh`, `docker/gpu.amd.yml`, `docker/gpu.nvidia.yml`, `docker/host-docker.yml`, `install-service.sh`, `launch-windows.ps1`, `launcher.py`, `licenses/DeepResearch-Apache-2.0.txt`, `licenses/KaTeX-MIT-LICENSE.txt`, `licenses/Mermaid-MIT-LICENSE.txt`, `licenses/OpenDyslexic-OFL.txt`, `licenses/llmfit-MIT-LICENSE.txt`, `licenses/opencode-MIT-LICENSE.txt`, `odysseus-ui.service`, `package-lock.json`, `package.json`, `pyproject.toml`, `requirements-optional.txt`, `requirements.txt`, `setup.py`, `start-macos.sh`, `update_windows.bat`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 3. Specifications

### Overview

`specs/_readme.md`, `specs/agent-tools.md`, `specs/auth-security.md`, `specs/calendar-tasks-notes.md`, `specs/chat.md`, `specs/compare.md`, `specs/context-building.md`, `specs/cookbook-hwfit.md`, `specs/documents-rag-uploads.md`, `specs/email-contacts.md`, `specs/frontend.md`, `specs/gallery-editor-media.md`, `specs/integrations.md`, `specs/llm-models.md`, `specs/memory-skills.md`, `specs/model-capability-canonical.md`, `specs/model-providers/_readme.md`, `specs/model-providers/anthropic.md`, `specs/model-providers/atlas-cloud.md`, `specs/model-providers/azure-openai.md`, `specs/model-providers/bedrock.md`, `specs/model-providers/cerebras.md`, `specs/model-providers/chatgpt-subscription.md`, `specs/model-providers/cloudflare-workers-ai.md`, `specs/model-providers/cohere.md`, `specs/model-providers/deepseek.md`, `specs/model-providers/fireworks.md`, `specs/model-providers/github-copilot.md`, `specs/model-providers/github-models.md`, `specs/model-providers/google.md`, `specs/model-providers/groq.md`, `specs/model-providers/hugging-face.md`, `specs/model-providers/llama-cpp.md`, `specs/model-providers/lm-studio.md`, `specs/model-providers/local-compatible-engines.md`, `specs/model-providers/minimax.md`, `specs/model-providers/mistral.md`, `specs/model-providers/moonshot-kimi.md`, `specs/model-providers/nvidia-nim.md`, `specs/model-providers/ollama.md`, `specs/model-providers/openai-compatible.md`, `specs/model-providers/openai.md`, `specs/model-providers/opencode.md`, `specs/model-providers/openrouter.md`, `specs/model-providers/perplexity.md`, `specs/model-providers/sglang.md`, `specs/model-providers/siliconflow.md`, `specs/model-providers/together.md`, `specs/model-providers/venice.md`, `specs/model-providers/vllm.md`, `specs/model-providers/xai.md`, `specs/model-providers/zai.md`, `specs/model-quirks.md`, `specs/persistence.md`, `specs/research.md`, `specs/runtime.md`, `specs/search.md`, `specs/settings-admin.md`, `specs/shell-mcp.md`, `specs/speech.md`, `specs/testing-devops.md`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 4. Operational scripts

### Overview

`scripts/_completion/odysseus.bash`, `scripts/_completion/odysseus.zsh`, `scripts/_lib/__init__.py`, `scripts/_lib/cli.py`, `scripts/add_hwfit_models.py`, `scripts/agent_migration_manifest.py`, `scripts/backfill_model_release_dates.py`, `scripts/check-docker-amd-gpu.sh`, `scripts/check-docker-gpu.sh`, `scripts/claim_ownerless.py`, `scripts/demo_email/demo_account.py`, `scripts/demo_email/manage.sh`, `scripts/demo_email/seed_demo_emails.py`, `scripts/diffusion_server.py`, `scripts/encode_previews.sh`, `scripts/fix_paths.py`, `scripts/hf_download.py`, `scripts/import_from_vllm_recipes.py`, `scripts/index_documents.py`, `scripts/migrate_faiss_to_chroma.py`, `scripts/migrate_searxng_settings.py`, `scripts/mlx_image_server.py`, `scripts/odysseus`, `scripts/odysseus-backup`, `scripts/odysseus-calendar`, `scripts/odysseus-contacts`, `scripts/odysseus-cookbook`, `scripts/odysseus-docs`, `scripts/odysseus-gallery`, `scripts/odysseus-logs`, `scripts/odysseus-mail`, `scripts/odysseus-mcp`, `scripts/odysseus-memory`, `scripts/odysseus-notes`, `scripts/odysseus-personal`, `scripts/odysseus-preset`, `scripts/odysseus-research`, `scripts/odysseus-sessions`, `scripts/odysseus-signature`, `scripts/odysseus-skills`, `scripts/odysseus-tasks`, `scripts/odysseus-theme`, `scripts/odysseus-webhook`, `scripts/pr_blocker_audit.py`, `scripts/update_database.py`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 5. core: auth, sessions, middleware, models

### Overview

The process-wide auth and chat-session state. `core/auth.py` owns users, password hashing,
TOTP/backup codes, browser session tokens, reserved usernames, and the `data/auth.json` store;
`core/session_manager.py` owns the chat-session cache and every message/transcript write;
`core/models.py` is the pure dataclass pair those two share; `core/middleware.py` is the
`require_admin` gate, the internal-tool token, and the security-header middleware;
`core/log_safety.py` is the log redactor for endpoint URLs.

The boundary: the request-time auth middleware, the API-token cache and the auth-exempt path
list live in `app.py`, assigned to `build-install-deploy`; the routes that call these APIs are
assigned to the `routes-*` sections; the production session cleanup is `src/cleanup_service.py`
via `routes/cleanup/cleanup_routes.py`, not this section's `SessionManager`; the owner and
privilege vocabulary is `src/owner_identity.py` / `src/auth_helpers.py` (`src-platform`).

### Coverage

**Read fully:** `core/auth.py` (680 lines), `core/log_safety.py` (27), `core/middleware.py`
(152), `core/models.py` (191), `core/session_manager.py` (782);
`tests/test_session_manager_cleanup.py` (29), `tests/test_log_safety.py` (27);
`specs/auth-security.md` (169).

**Read partially:** `app.py` at the auth middleware (`:265-500`) — the token cache, bearer
verification and internal-tool bypass; `routes/session_routes.py` at `list_sessions`
(`:250-357`), `create_session` (`:359-495`), `inject_messages` (`:573-608`), archive/unarchive
(`:730-797`), `sessions_save_now`/`session/openai` (`:932-966`), the important route
(`:967-1003`) and `auto_sort_sessions` (`:1084-1100`, `:1175-1190`); `routes/auth_routes.py` at
login (`:168-182`), change-password (`:228-239`), 2FA setup/confirm/disable, user
delete/rename (`:336-470`) and `:592`; `routes/chat_helpers.py` at `resolve_session_auth`
(`:455-514`); `src/auth_helpers.py` at `effective_user` (`:15-36`); `src/agent_tools/session_tools.py`
at `create_session` (`:50-70`) and `list_sessions` (`:104`); `src/ai_interaction.py` at the
model-switch handler (`:705-725`); `src/cleanup_service.py` (`:1-160`) and
`routes/cleanup/cleanup_routes.py`; `src/endpoint_resolver.py` at `resolve_url`,
`normalize_base`, `_prepare_endpoint_base` and `build_chat_url` (`:209-285`);
`routes/model_routes.py` at endpoint create (`:1989-2060`) and the probe log sites
(`:1015-1045`); `tests/test_history_display_model_hydration.py` (the drift, hydration and fork
tests, `:1-407`), `tests/test_auth_session_revocation.py` (`:1-130`),
`tests/test_rename_user_owner_sync.py` (`:1-40`), `tests/test_session_list_owner_scope.py` (by
search only); `specs/persistence.md` and `specs/chat.md` at their session-relevant lines.

**Not read:** `core/database.py` (the session/message schema and migrations — assigned to
`core-data-platform`); the bodies of the `routes-*` handlers beyond the regions above; the front
end's session list/search code (`static/js/sessions.js` beyond the endpoints it fetches);
`src/task_scheduler.py`'s session use.

**Checks run:** four probes under `venv/bin/python` — a 104-row cache probe (finding 1), a
`cleanup_empty_sessions` run against a real SQLite row (finding 3), a `create_session` +
`save_sessions` + `sync_session_metadata` sequence (finding 2), and `redact_url` over a
scheme-less endpoint URL after `build_chat_url` (finding 4); plus caller greps for
`save_sessions`, `get_sessions_for_user`, `cleanup_empty_sessions` and
`AuthManager.create_session`. The three test files cited above: `15 passed`
(`tests/test_session_manager_cleanup.py`, `tests/test_log_safety.py`,
`tests/test_auth_session_revocation.py`).

#### [BUG] The sidebar list is served from a global 100-row cache, so one user's sessions can hide another's

- **Location:** `core/session_manager.py:96-98` (with `routes/session_routes.py:289`, `:352`, and `core/session_manager.py:700-707`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `load_sessions` caches one global, owner-agnostic slice:

  ```python
  db_sessions = db.query(DbSession).filter(
      DbSession.archived == False,
      DbSession.messages.any(),
  ).order_by(DbSession.last_accessed.desc()).limit(100).all()
  ```

  `get_sessions_for_user` then filters that same dict, and `GET /api/sessions` builds its
  response from it:

  ```python
  user_sessions = session_manager.get_sessions_for_user(user)   # routes/session_routes.py:289
  ...
  for s in user_sessions.values()                               # routes/session_routes.py:352
  ```

  Measured with a temp SQLite DB holding 101 recent sessions for `alice`, two older ones for
  `bob`, and one message-less `alice` session:

  ```
  cached sessions: 100 by owner: {'alice': 100}
  bob's sessions visible via get_sessions_for_user: []
  alice-empty cached: False
  ```

- **Impact:** after every process start, `GET /api/sessions` can only return the 100 sessions
  whose `last_accessed` is newest across all owners. On a multi-user instance the quieter
  account's sidebar is empty even though its rows are in the database (the same user can still
  reach them through `/api/search` or by opening the id). A session with no messages is never
  cached at all, so a draft chat created before a restart also disappears from the list. The
  rows are not lost, and the route already queries every non-archived row of the owner for its
  metadata maps (`routes/session_routes.py:301-302`); only the list itself comes from the cache.
- **Fix:** build the response from the rows the route already selects (add `DbSession.name`,
  `model`, `endpoint_url` and `rag` to that query), or make `load_sessions` cache per owner.
  Deleting the cache dependency also removes the empty-session special case.

#### [BUG] `save_sessions()` is a no-op that three call sites treat as a persist, and the next `get_session` overwrites what they set

- **Location:** `core/session_manager.py:709-710` (with `:483`, `routes/session_routes.py:961-962`, `src/agent_tools/session_tools.py:59-61`, `src/ai_interaction.py:716-717`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the method body is the docstring:

  ```python
  def save_sessions(self):
      """No-op for DB compatibility."""
  ```

  `sync_session_metadata`, which every `get_session` calls (`:441`), re-reads the row over the
  in-memory object:

  ```python
  session.headers = headers or {}      # core/session_manager.py:483
  ```

  Measured sequence, mirroring `routes/session_routes.py:953-962`:

  ```
  DB headers after save_sessions(): {}
  in-memory headers before get_session: {'Authorization': 'Bearer sk-[REDACTED]'}
  in-memory headers after get_session: {}
  ```

  There are 22 non-test `save_sessions()` call sites (`grep -rn '\.save_sessions()' src/ routes/`
  minus the definition).
- **Impact:** in-memory `Session` fields written after the row was created (`headers`, and any
  `name`/`model`/`endpoint_url` not persisted through a DB update) are silently discarded on the
  next read. `/session/openai` is the clearest case: it builds `Authorization` from the server's
  `OPENAI_API_KEY`, calls the no-op, and the next `get_session` — the chat send — hands the model
  call an empty header dict. The chat path re-derives auth only when an enabled `ModelEndpoint`
  row matches the session URL (`routes/chat_helpers.py:458-514`), so an env-key-only setup sends
  the request unauthenticated. The agent's `create_session` tool with explicit `headers` and the
  UI's `switch_model` action have the same shape and rely on the same recovery. The main create
  route is not affected: it persists headers through `_persist_session_headers`
  (`routes/session_routes.py:189-196`, called at `:478-479`).
- **Fix:** delete `save_sessions` and its 22 call sites (they are vestigial from the JSON-file
  store), or make it write the dirty fields; and persist the headers at the three sites that set
  them, the way `_persist_session_headers` does.

#### [BUG] `cleanup_empty_sessions` raises on its first empty session and rolls back the whole run

- **Location:** `core/session_manager.py:751-756` (with the re-raise at `:775-778`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the delete branch compares an aware datetime with a naive one:

  ```python
  if db_session.message_count == 0:
      if db_session.created_at is not None:
          created = db_session.created_at
          if created.tzinfo is None:
              created = created.replace(tzinfo=timezone.utc)
          if created > min_age:              # min_age = utcnow_naive() - ...
              continue  # Too young to delete
  ```

  The `except` at `:775-778` logs, rolls back and re-raises. Measured against a real SQLite row
  (one 90-day-old empty session, one 90-day-old session with messages):

  ```
  RAISED: TypeError can't compare offset-naive and offset-aware datetimes
  rows after cleanup: [('empty-old', False, 0), ('old-full', False, 3)]
  ```

  Nothing is called in production: the only caller is `tests/test_session_manager_cleanup.py`,
  which passes a `SimpleNamespace` with no `created_at` and therefore exercises only the archive
  branch. The route-reachable cleanup is `src/cleanup_service.py` via
  `routes/cleanup/cleanup_routes.py:50`.
- **Impact:** the method cannot delete any empty session, and because the comparison fails
  inside the loop, the archive work it did for earlier rows in the same pass is rolled back too
  (`old-full` stays `archived=False`). Since nothing calls it, the impact today is an unusable
  cleanup API and a test that pins only the branch that works; wiring it into a route would
  produce a 500 and no cleanup.
- **Fix:** compare in one frame — keep `min_age` and `created` both naive, or both aware; or
  delete the method and its test, since `src/cleanup_service.py` owns the live path.

#### [SECURITY] `redact_url` returns a scheme-less URL unchanged, including its userinfo

- **Location:** `core/log_safety.py:18-25`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `urlparse` treats `user:pass@host/v1` as scheme `user` plus path
  `pass@host/v1`, so `parsed.hostname` is empty and the reconstruction returns the input:

  ```python
  parsed = urlparse(url or "")
  host = parsed.hostname or ""
  ...
  return urlunparse((parsed.scheme, host, parsed.path, "", "", ""))
  ```

  Measured:

  ```
  'user:pass@host/v1' -> build_chat_url -> 'user:pass@host/v1/chat/completions' -> redact -> 'user:pass@host/v1/chat/completions'
  ```

  The input is accepted by the endpoint route, which validates only that the base URL is
  non-empty (`routes/model_routes.py:2011-2013`) and whose `resolve_url` returns the string
  unchanged when `urlparse` finds no hostname (`src/endpoint_resolver.py:211-214`); the model
  probe then logs the redacted form at WARNING on failure (`routes/model_routes.py:1033-1044`),
  as does the chat route (`routes/chat_routes.py:728`, `:1670`). `tests/test_log_safety.py:26-27`
  claims the no-userinfo-survives property but only asserts it for a garbage string.
- **Impact:** an admin-configured endpoint whose base URL lacks a scheme but embeds credentials
  (`user:pass@host`) writes that password to the application log on every failed probe. The
  module docstring names this exact input class ("Endpoint URLs configured by admins can embed
  credentials in the userinfo") as the reason the helper exists, so the guard is expected to
  cover it.
- **Fix:** when `parsed.scheme` is empty, strip a leading `userinfo@` from the path before
  returning (or return `<endpoint>`), and add the scheme-less case to `tests/test_log_safety.py`.

#### [FOOTGUN] `AuthManager.create_session()` issues a session from the password alone

- **Location:** `core/auth.py:574-579`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the method verifies the password and skips the second factor entirely:

  ```python
  def create_session(self, username: str, password: str) -> Optional[str]:
      """Verify credentials and return a session token, or None."""
      username = username.strip().lower()
      if not self.verify_password(username, password):
          return None
      return self.create_session_trusted(username)
  ```

  Its callee's docstring states the contract it does not enforce — "Call only after
  verify_password (and TOTP if enabled) have passed" (`:581-583`) — and the login route performs
  the three steps in order (`routes/auth_routes.py:171-181`). `grep -rn '\.create_session(' src/
  routes/ core/` finds no production caller; the hits are `SessionManager.create_session` (a
  different class) and test helpers such as `tests/test_auth_session_revocation.py:51-53`. The
  spec states the invariant the method would break: "TOTP is checked before session issuance"
  (`specs/auth-security.md`).
- **Impact:** none today. The next caller that reaches for the natural-looking
  `auth_manager.create_session(user, password)` — a new login path, a CLI, a migration script —
  issues a seven-day session for a 2FA-enabled account after only the password. The safe path is
  a three-call sequence the method hides.
- **Fix:** delete the method, or make it fail closed for 2FA users
  (`if self.totp_enabled(username): return None`) and name it for what it does.

## 6. core: database, atomic IO, constants, platform

### Overview

`core/database.py` owns the SQLAlchemy schema for every persisted domain — sessions and
messages, documents, gallery, memory, notes, calendars, email accounts, model endpoints, API
tokens, MCP servers, webhooks, task runs — the boot-time migration ladder that runs when the
module is imported (`init_db()` at `:2737`), and the small query helpers on top of it.
`core/atomic_io.py` is the shared atomic JSON writer for every config store; `core/constants.py`
is a re-export shim over `src/constants.py`; `core/exceptions.py` holds four exception types;
`core/platform_compat.py` is the POSIX/Windows helper layer (file modes, process liveness and
teardown, bash discovery, SSH argv); `core/__init__.py` re-exports the chat core.

The boundary: the auth and session state built on this schema is `core-auth-session`; the route
handlers that read the schema are the `routes-*` sections; the secret stores that call
`atomic_write_json` (`src/secret_storage.py`, `src/api_key_manager.py`, `src/settings.py`,
`src/integrations.py`) are `src-platform`; the front end's use of the schema is `static-*`.

### Coverage

**Read fully:** `core/atomic_io.py` (66 lines), `core/constants.py` (12), `core/exceptions.py`
(29), `core/platform_compat.py` (452), `core/database.py` (2,737), `core/__init__.py` (53);
`specs/persistence.md`. Supporting reads for the findings: `src/memory.py` at the
`MemoryStoreUnreadable` paths (`:120-210`), `src/secret_storage.py` at the import block and key
chmod (`:20-50`), `src/settings.py` at the default settings and `save_settings` (`:85-95`,
`:252-253`), `src/api_key_manager.py` at the chmod sites (`:23`, `:33`), `src/integrations.py`
at `save_integrations` (`:253-258`), `routes/prefs_routes.py` at `_save` (`:26-27`),
`routes/mcp/mcp_routes.py` at the env parse/store (`:142`, `:235-258`),
`src/agent_tools/admin_tools.py` at the MCP create (`:260-270`),
`routes/webhook/webhook_routes.py` at the secret write (`:116-131`).

**Read partially:** `app.py` at the null-owner sweep (`:1214-1228`); `services/hwfit/hardware.py`
at `_run` (`:26-40`); `routes/hwfit_routes.py` at `_validate_detection_target` and its call
sites (`:21-25`, `:190`, `:204`, `:331`, `:417`); `src/database.py` as the re-export shim;
`tests/test_atomic_io.py`, `tests/test_app_db_permissions.py`,
`tests/test_memory_store_unreadable_no_wipe.py`, `tests/test_prefs_atomic_write.py`,
`tests/test_security_regressions.py` at their permission and durability assertions.

**Not read:** the bodies of the route and service modules named above beyond the cited regions;
the front end's consumers of the schema; `src/settings.py`, `src/api_key_manager.py`,
`src/integrations.py` and `src/secret_storage.py` outside the regions cited (assigned to
`src-platform` and `src-security`).

**Checks run:** a temp-SQLite probe that seeded 20,000 messages and timed
`_migrate_chat_messages_fts()` at four sizes, with `EXPLAIN QUERY PLAN` and two alternative
implementations (finding 1); a temp-directory probe that wrote a 0o600 file through
`atomic_write_json` and re-stat'ed it, plus `stat -c '%a %n'` on this checkout's `data/` and a
repo-wide chmod grep (finding 2); `bulk_insert_messages` called with its real signature
(finding 3); import probes for `routes.email_helpers`, `src.secret_storage` and `app` under a
temp data dir (finding 4); `grep -rn` for the env writers and the `EncryptedText` columns
(finding 5). Nine suites were run for the surface this section read — `tests/test_atomic_io.py`,
`tests/test_app_db_permissions.py`, `tests/test_memory_store_unreadable_no_wipe.py`,
`tests/test_prefs_atomic_write.py`, `tests/test_database_utcnow.py`,
`tests/test_sqlite_foreign_keys.py`, `tests/test_update_database_script.py`,
`tests/test_api_key_file_permissions.py`, `tests/test_security_regressions.py` — **148 passed**.

#### [SECURITY] `atomic_write_json` leaves the auth and settings stores at the umask default

- **Location:** `core/atomic_io.py:32-39` (with `core/auth.py:157`, `:222`, `src/settings.py:253`, `routes/prefs_routes.py:27`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the writer creates its temp file with `open(tmp, "w")` and replaces the target;
  no mode is ever applied, so the replacement is born at the process umask (0o644 under the
  default 0o022):

  ```python
  tmp = f"{path}.tmp.{uuid.uuid4().hex}"
  ...
  with open(tmp, "w", encoding="utf-8") as f:
      json.dump(data, f, indent=indent)
      f.flush()
      os.fsync(f.fileno())
  os.replace(tmp, path)
  ```

  Measured in a temp directory: a pre-existing 0o600 file becomes 0o644 after one write.

  ```
  PERMS before=0o600 after=0o644 umask=0o22
  ```

  This checkout's live stores carry that mode while the database does not:

  ```
  $ stat -c '%a %n' data/auth.json data/sessions.json data/settings.json data/app.db
  644 data/auth.json
  644 data/sessions.json
  644 data/settings.json
  600 data/app.db
  ```

  `atomic_write_json` is the writer for the password DB and the live state — the module
  docstring names them: "For password DBs (`auth.json`) and live state (`sessions.json`,
  `settings.json`, `integrations.json`, `cookbook_state.json`), that's a data-loss event."
  It has 30 non-test call sites, and the secret-bearing ones do not chmod the result:
  `core/auth.py:157` (session tokens), `core/auth.py:222` (`auth.json`: bcrypt hashes, TOTP
  secrets, backup codes), `src/settings.py:253` (`settings.json`, whose defaults include
  `brave_api_key`, `tavily_api_key` and `serper_api_key` at `:91-95`),
  `routes/prefs_routes.py:27`. `grep -rn chmod core/auth.py src/settings.py
  routes/prefs_routes.py` returns nothing. Every other credential store locks itself down:
  `core/database.py:2081` (the DB, with an operator warning when the chmod fails),
  `src/api_key_manager.py:23`, `:33`, `src/secret_storage.py:45`, and
  `src/integrations.py:258` (the integrations store, one line after its atomic write). The DB's
  own comment states the threat model for exactly this class of file: "the file is born here at
  the umask default, and nothing below resets the mode" (`core/database.py:2068-2072`).
  `tests/test_atomic_io.py` covers durability but asserts no mode;
  `tests/test_security_regressions.py:104-114` pins the Fernet key at 0o600 and
  `tests/test_app_db_permissions.py:42-51` re-locks a 0o644 database on startup, so the JSON
  stores are the untested exception.
- **Impact:** on any host with more than one local account, or any copy that preserves modes,
  the password hashes, TOTP secrets, backup codes, live session tokens and provider API keys in
  `data/*.json` are readable by every local user — `data/` itself is 0o755 in this checkout.
  A Docker install is single-user and less exposed, but `auth.json` is the application's
  password database and the DB file beside it is deliberately locked to 0o600. The failure is
  silent and persists across restarts: every save re-creates the file at the umask default, so a
  one-time `chmod` is undone by the next write.
- **Fix:** set the mode on the temp file before the replace in both helpers — `os.chmod(tmp,
  0o600)`, or preserve the existing target's mode when it has one — and let a caller that needs
  a wider mode opt in. `tests/test_atomic_io.py` is the place to pin it.

#### [PERF] The transcript FTS backfill is quadratic and runs on every startup

- **Location:** `core/database.py:2244-2254` (with `:2214`, `:2145`, `:2737`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the backfill's `NOT EXISTS` is checked against an `UNINDEXED` column, so SQLite
  scans the whole FTS table once per source row:

  ```python
  conn.execute(
      f"""
      INSERT INTO chat_messages_fts(content, message_id, session_id, role)
      SELECT {fts_content_expr_cm}, cm.id, cm.session_id, cm.role
      FROM chat_messages cm
      WHERE NOT EXISTS (
          SELECT 1 FROM chat_messages_fts fts
          WHERE fts.message_id = cm.id
      )
      """
  )
  ```

  The table is declared `message_id UNINDEXED` (`:2214`), and the plan confirms the nested scan:

  ```
  PLAN: SCAN cm
  PLAN: CORRELATED SCALAR SUBQUERY 1
  PLAN: SCAN fts VIRTUAL TABLE INDEX 0:
  ```

  Measured on a temp SQLite DB by calling `_migrate_chat_messages_fts()` against an
  already-populated index — the state every restart is in:

  ```
  FTS steady-state  2000 rows: 0.157s
  FTS steady-state  5000 rows: 0.956s
  FTS steady-state 10000 rows: 3.969s
  FTS steady-state 20000 rows: 15.535s
  ```

  The same call against an *empty* index, the case with real work to do, takes 0.03s at 20,000
  rows. `init_db()` calls the migration at `:2145` and `init_db()` runs at import (`:2737`), so
  every process that imports `core.database` — the server at boot, and any CLI or test process
  that imports the app's DB module — pays the steady-state cost. A count guard removes it:

  ```
  count guard: 0.0016s (20000 vs 20000)
  LEFT JOIN backfill (no-op): 30.22s
  ```

- **Impact:** startup time is quadratic in stored messages, spent to prove there is nothing to
  backfill. At 20,000 messages every boot burns 15s of CPU before the app can serve; the 4x
  rows → ~16x time curve extrapolates to roughly 6.5 minutes at 100,000 messages (a long-lived
  install's history). A fresh database has an empty index and is fast, so the regression appears
  only after the user has history, and it is re-paid on every restart and by every developer
  command that imports the module.
- **Fix:** skip the backfill when `SELECT COUNT(*) FROM chat_messages` equals
  `SELECT COUNT(*) FROM chat_messages_fts` (measured at 1.6ms for 20,000 rows), or record a
  schema version and run the backfill once. A `LEFT JOIN` is not a fix: it was measured at
  30.22s for the same no-op, because the join column is `UNINDEXED` too.

#### [BUG] The hourly null-owner sweep rewrites `memory.json` and `user_prefs.json` non-atomically

- **Location:** `core/database.py:1481-1482` and `:1513-1514` (with `:2123`, `app.py:1225-1226`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the sweep opens both JSON stores with a truncating write:

  ```python
  with open(mem_path, "w", encoding="utf-8") as f:
      _json.dump(memories, f, ensure_ascii=False, indent=2)
  ...
  with open(prefs_path, "w", encoding="utf-8") as f:
      _json.dump(new_prefs, f, indent=2)
  ```

  It runs at boot (`_migrate_assign_legacy_owner()` at `:2123`) and again hourly from the server
  loop (`app.py:1222-1226`, `asyncio.sleep(3600)`), so the write recurs whenever an ownerless
  entry exists — the condition the sweep was added for. The memory store's own reader names this
  writer as the reason a corrupt store is reachable: "A truncated memory.json is reachable
  because core/database.py rewrites it with a plain open(..,\"w\") + json.dump during
  migration" (`src/memory.py:145-149`). Both files have an atomic writer everywhere else —
  `src/memory.py:261-280` writes memory.json through a temp file, and
  `routes/prefs_routes.py:27` writes `user_prefs.json` through `atomic_write_json`.
- **Impact:** a kill, OOM, or power loss inside the write window leaves a truncated JSON file.
  The memory manager then raises `MemoryStoreUnreadable` by design and refuses to save over it
  (`src/memory.py:170-200`), so the memory feature stops until an operator repairs the file and
  the content that was being rewritten is gone. The window is small but it recurs hourly, and
  the file is the user's long-term memory store, not a cache.
- **Fix:** call `core.atomic_io.atomic_write_json` for both writes — the surrounding code already
  builds plain JSON-serializable structures, so this is a call swap, not a restructure.

#### [DEAD-CODE] `bulk_insert_messages` cannot insert anything

- **Location:** `core/database.py:2595-2609` (re-exported at `src/database.py:30`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the helper builds rows without the primary key, which the model requires and
  generates nowhere:

  ```python
  def bulk_insert_messages(session_id: str, messages: list):
      """Efficiently insert multiple messages"""
      with get_db_session() as db:
          db.bulk_insert_mappings(
              ChatMessage,
              [
                  {
                      'session_id': session_id,
                      'role': msg['role'],
                      'content': msg['content'],
                      'timestamp': utcnow_naive()
                  }
                  for msg in messages
              ]
          )
  ```

  `ChatMessage.id` is `Column(String, primary_key=True, index=True)` with no default (`:262`).
  Measured with the real signature:

  ```
  bulk_insert_messages: IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed: chat_messages.id
  rows after: 0
  ```

  `grep -rn 'bulk_insert_messages' src/ routes/ core/` finds only the definition and the
  `src/database.py:30` re-export, so no production path calls it today.
- **Impact:** none today. The function is part of the `src.database` facade, so the next caller
  that reaches for the obvious bulk-insert helper gets a rolled-back transaction and zero
  messages instead of an insert. The row dicts are rebuilt from four fixed keys, so a caller
  cannot supply an `id` through `messages` either; the only way to use it is to change it.
- **Fix:** add `'id': str(uuid.uuid4())` (and `'metadata': None` if callers rely on it) per row,
  or delete the function and its re-export.

#### [ERROR-HANDLING] The three encryption migrations are skipped whenever `src.secret_storage` is imported before `core`

- **Location:** `core/database.py:2330-2389` (with `src/secret_storage.py:26`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** each of the three legacy-encryption migrations imports its helper inside a
  `try` and continues when the import fails:

  ```python
  try:
      from src.secret_storage import encrypt
  except Exception as e:
      logging.getLogger(__name__).warning(
          f"secret_storage import failed; skipping password migration: {e}")
      return
  ```

  `src/secret_storage.py:26` imports `core.platform_compat` at module level, and importing
  `core.platform_compat` initializes the `core` package, which imports `core.database` — whose
  `init_db()` runs at import. Importing `src.secret_storage` first therefore runs the
  migrations while `src.secret_storage` is half-initialized. Reproduced with a temp data dir:

  ```
  $ python -c "import routes.email_helpers"
  WARNING:core.database:secret_storage import failed; skipping password migration:
  cannot import name 'encrypt' from partially initialized module 'src.secret_storage' ...
  (the signature and endpoint-key migrations print the same warning)
  ```

  The same happens for `import src.secret_storage`. The server is not affected: `import app`
  under the same conditions prints no skip, because `app.py:65` imports `core.constants` before
  any `src.*` module, so the migrations run with a complete `src.secret_storage`. The trigger is
  a process whose first core-touching import is `src.secret_storage` or a module that imports it
  first, such as `routes.email_helpers.py:38`.
- **Impact:** in such a process the password, signature and endpoint-key migrations are
  silently skipped and the affected values stay plaintext for that process's lifetime; the
  warning is the only signal. The server and its data are safe, and the next server start
  re-runs the migrations, so this is a tooling/diagnostic path rather than a production one —
  but the handler is fail-open by design, and the cycle that reaches it is avoidable.
- **Fix:** move `from core.platform_compat import safe_chmod` into the function that uses it
  (`src/secret_storage.py:45` is the only use), so importing the module no longer pulls in
  `core`. A test that imports `src.secret_storage` first and asserts no skip would pin it.

#### [SECURITY] MCP server env vars are stored plaintext while the same table encrypts OAuth tokens

- **Location:** `routes/mcp/mcp_routes.py:253` (with `core/database.py:579`, `:584`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the create route stores the parsed env as JSON text with no encryption:

  ```python
  srv = McpServer(
      ...
      env=json.dumps(parsed_env),
  ```

  The agent-facing writer does the same (`src/agent_tools/admin_tools.py:268`), and the read
  path is a plain `json.loads` (`routes/mcp/mcp_routes.py:142`). `McpServer.env` is
  `Column(Text, nullable=True)  # JSON object of env vars` (`core/database.py:579`) while
  `oauth_tokens` in the same class is `Column(EncryptedText, ...)` (`:584`). The rest of the
  schema encrypts its credentials the same way: model endpoint `api_key` (`:527`), Google
  `access_token`/`refresh_token` (`:565-566`), signatures (`:628`, `:631`); email passwords and
  Google OAuth tokens are encrypted manually; webhook secrets go through the API-key manager
  (`routes/webhook/webhook_routes.py:116-131`). `specs/persistence.md:99` lists the encrypted
  stores and does not include MCP env. The route already treats one env value as a secret — it
  pops `GOOGLE_CLIENT_SECRET` out of `parsed_env` before storing (`:240-241`) — so the field is
  known to carry credentials.
- **Impact:** an API key supplied to an MCP server as an env var (the normal way to give an MCP
  server credentials) sits in plaintext in `app.db`. The database is chmod 0o600, so the
  exposure is a copied, backed-up or otherwise leaked database — the threat `src.secret_storage`
  exists for — not a local reader.
- **Fix:** declare `env` as `EncryptedText` (like `oauth_tokens`) or encrypt the JSON with
  `src.secret_storage` at both write sites, and add the column to the encryption list in
  `specs/persistence.md`.

## 7. src: agent loop, runs, approvals and gates

### Overview

`src/action_intents.py`, `src/agent_loop.py`, `src/agent_runs.py`, `src/goal_based_extractor.py`, `src/interactive_gate.py`, `src/task_action_policy.py`, `src/tool_approval_scopes.py`, `src/tool_approvals.py`.

This section covers the loop that turns a chat message into tool calls: intent routing and tool
retrieval, system-prompt assembly, the multi-round execution loop, the detached-run manager, the
background-activity gate, and the exact-action approval store. The tool implementations are in
`src-agent-tools`; the route that starts a run is in `routes-chat-session`. A finding here is about
a decision the loop makes, not about whether a tool implementation is correct.

### Coverage

**Read fully:** all eight files — `src/agent_loop.py` (6,456 lines), `src/tool_approvals.py`
(513), `src/agent_runs.py` (271), `src/interactive_gate.py` (219), `src/action_intents.py` (165),
`src/tool_approval_scopes.py` (160), `src/task_action_policy.py` (47),
`src/goal_based_extractor.py` (23). Every cited line was re-read at `2992bf6d368a`.

**Not read:** the tool dispatcher and tool implementations (`src/agent_tools/`, assigned to
`src-agent-tools`), the routes that build the initial message list and consume the loop's events
(`routes/chat_routes.py`, `routes/chat_helpers.py`, assigned to `routes-chat-session`),
`src/tool_capabilities.py` and `src/tool_policy.py` (assigned to `src-tools-capabilities-policy`), and
`src/teacher_escalation.py` (assigned to `src-research-scheduling`). Statements about how those
modules consume values built here rest on the call sites visible in this section.

One hypothesis was tested and rejected; it is recorded in `sources/coverage-boundaries.md`.

#### [BUG] An ordinary "on <word>" phrase switches the turn to the workspace toolset

- **Location:** `src/agent_loop.py:1182`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** The third alternative in `_LOCAL_COMPUTER_REFERENCE_RE` matches `on` or `from`
  followed by any 2-32 character word outside a five-word blocklist:

  ```python
  r"|\b(?:on|from)\s+(?!this\b|my\b|the\b|a\b|an\b)(?:[a-z][a-z0-9_.-]{1,31})\b",
  ```

  `_looks_like_local_computer_request` (`:1205`) returns True on that match, and the
  tool-selection block treats it as one arm of a condition that replaces the whole retrieved set
  (`:3985` for the call, `:3990` for the assignment):

  ```python
  or _looks_like_local_computer_request(_retrieval_query or _last_user)
  ...
  _relevant_tools = set(_WORKSPACE_TERMINUS_TOOLS)
  ```

  Measured with the compiled expression:

  ```
  $ python3 -c "<regex from :1182, re.search>"
  True   add a meeting on Friday
  True   send an email to bob on Monday
  True   what is on Netflix tonight
  True   summarize the report from Alice
  True   schedule a dentist appointment on Tuesday at 3pm
  True   who is on call this weekend
  False  add milk on my todo list
  False  search for the weather in Berlin
  ```

  `_classify_agent_request` (`:1390`) routes "add a meeting on Friday" to `notes_calendar_tasks`,
  which seeds `manage_calendar` into `_relevant_tools` at `:3957-3958`; the replacement at `:3990`
  discards it. `_WORKSPACE_TERMINUS_TOOLS` (`:542`) is the `files` domain plus `manage_skills`,
  `ask_teacher`, `web_search`, `web_fetch`, `ask_user`, and `update_plan` — no email, calendar,
  notes, memory, contacts, documents, or UI tools. `_assemble_prompt` (`:847`) builds the system
  prompt from that set and `_tool_schemas_for_route` (`:4486`) filters the schema list the same
  way, so the dropped tools are absent from both channels.

- **Impact:** A turn whose text contains "on X" or "from X" — a common English construction, not
  only a machine name — loses the domain tools it needs and is given the coding toolset instead.
  "add a meeting on Friday" and "send an email to Bob on Monday" are answered by an agent holding
  `bash` and `read_file` but no `manage_calendar` or `send_email`. The comment above the regex
  calls the third alternative a "named computer task request"; the match is wider than that.
- **Fix:** Match named machines against the configured Cookbook server names and SSH aliases
  rather than any bare word, or require an explicit machine marker ("on the machine", "host: X").
  Excluding weekday and month names closes the most common false positive but not the class.

#### [BUG] The first-turn low-signal shortcut answers non-English action requests with no tools

- **Location:** `src/agent_loop.py:3544`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_classify_agent_request` is English-only apart from three Polish patterns. A
  German request is classified `low_signal` with no domains:

  ```
  $ venv/bin/python -c "<import src.agent_loop; _classify_agent_request>"
  'Recherchiere im Internet nach der aktuellen Temperatur in Berlin'
    {'low_signal': True, 'continuation': False, 'domains': set(), 'retrieval_query': '...'}
  ```

  `_direct_low_signal` (`:3544-3556`) is true for that turn: it is the first user turn, not a
  continuation, and no document, email, workspace, forced tool, or retrieved tool is present.
  `_is_casual_low_signal` is False, but the three `(_casual_low_signal_turn or not ...)` arms pass
  because each context is empty. The direct path then calls the model with only the latest user
  text and no tools (`:3597` for a non-Qwen model), caps the reply at 128 tokens (`:3696`), and
  returns before tool retrieval runs.

  The retrieval path it skips states the opposite intent (`:3885-3887`):

  ```python
  # Don't short-circuit: fall through to RAG retrieval below.
  # Non-English queries are flagged low_signal by the English-only
  # intent classifier, but fastembed retrieval works across languages.
  ```

  That branch is unreachable for a first-turn non-English message because the direct path has
  already returned. `tests/test_agent_loop.py:67` covers the Polish patterns; no test covers any
  other language.

- **Impact:** A first message in a language the classifier does not cover is answered from model
  memory with no web, calendar, email, or file tools, even when it names an action.
  "Recherchiere im Internet nach ..." gets a recalled answer instead of a `web_search`, and the
  128-token cap applies to the same call. The shortcut also drops the upload manifest that
  `stream_agent_loop` inserts at `:3521`; whether that loses attachment content depends on whether
  the route already inlined it into the user message, which is outside this section.
- **Fix:** Make `_direct_low_signal` require `_casual_low_signal_turn`, so only casual first turns
  skip retrieval, and let the other low-signal turns reach the RAG path the comment describes.

#### [DEAD-CODE] The first `_AGENT_RULES` and `_API_AGENT_RULES` are shadowed by a second definition

- **Location:** `src/agent_loop.py:307`
- **Severity:** low
- **Disposition:** next
- **Evidence:** The three prompt constants are assigned twice at module level:

  ```
  $ grep -n '^_AGENT_PREAMBLE = \|^_AGENT_RULES = \|^_API_AGENT_RULES = ' src/agent_loop.py
  307:_AGENT_PREAMBLE = """\
  313:_AGENT_RULES = """\
  360:_API_AGENT_RULES = """\
  425:_AGENT_PREAMBLE = """\
  429:_AGENT_RULES = """\
  440:_API_AGENT_RULES = """\
  ```

  The second assignment wins at import. `_assemble_prompt` (`:847`) reads the module globals at
  call time, so lines 307-423 — 117 lines — never reach a prompt. The two revisions differ: the
  shadowed `_AGENT_RULES` is the long operational block, and the live `_AGENT_RULES` (`:429`) is
  the short "Base rules" text; the domain rules it drops are restated separately in
  `_DOMAIN_RULES` (`:467`) and `_LINK_RULES`.

- **Impact:** A maintainer editing the first copy changes nothing, and the file gives no signal
  that one of the two copies is inert. The two revisions have already drifted, so which rules ship
  cannot be read off the file without tracking the rebinding.
- **Fix:** Delete the first block, keeping any text still wanted by folding it into the live
  constants or `_DOMAIN_RULES`. A test asserting that a known rule string appears in
  `AGENT_SYSTEM_PROMPT` would catch a reintroduced shadow.

#### [BUG] The Odysseus-Qwen artifact normalizer rewrites the word "star" to "start"

- **Location:** `src/agent_loop.py:1971`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_ODY_QWEN_TEXT_FIXES` (`:1948`) lists
  `(re.compile(r"\bstar\b", re.IGNORECASE), "start")` among repairs for dropped final letters.
  `_normalize_ody_qwen_text_artifacts` (`:1979`) applies every entry to each streamed delta
  (`:5212`), to deterministic tool summaries (`:6132`), and to the final response (`:6330`) when
  the model is an `odysseus-qwen3*` finetune. "star" is a complete English word:

  ```
  $ venv/bin/python -c "<import src.agent_loop; _normalize_ody_qwen_text_artifacts>"
  'The North Star is bright tonight.' -> 'The North start is bright tonight.'
  'a rising star' -> 'a rising start'
  'Star Wars' -> 'start Wars'
  ```

- **Impact:** Any response from that model containing "star" is altered before display, including
  quoted text and titles. The other entries in the list ("accoun", "documen", "reques", "migh")
  are not English words; "star" is the entry that corrupts valid prose. Scope is the shipped
  finetune models, not the general path.
- **Fix:** Remove the `star` entry. If the finetune really drops the final "t" from "start", key
  the repair on context that distinguishes the two words rather than on the standalone token.

#### [PERF] The base-prompt cache never avoids the prompt build

- **Location:** `src/agent_loop.py:2258`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** On a cache hit, `_build_system_prompt` assigns the cached string and then calls
  `_build_base_prompt` anyway to obtain the skill-index block, discarding the freshly built
  prompt:

  ```python
  if _cached_base_prompt and _cached_base_prompt_key == cache_key and not active_document:
      agent_prompt = _cached_base_prompt
      # ... Skill index ... is NOT cached. Always recompute when the cache hits.
      _, _skill_index_block = _build_base_prompt(
          disabled_tools, mcp_mgr, needs_admin, relevant_tools,
          mcp_disabled_map=mcp_disabled_map, compact=compact, owner=owner,
          suppress_local_context=suppress_local_context,
          suppress_skills=suppress_skills,
      )
  else:
      agent_prompt, _skill_index_block = _build_base_prompt(...)
  ```

  The hit branch and the miss branch run the same call; the only difference is which of two
  strings built from the same inputs is assigned. `_cached_base_prompt` and
  `_cached_base_prompt_key` save no work, and the cache-key computation at `:2257` is overhead.

- **Impact:** Low. `_build_base_prompt`'s dominant cost, `SkillsManager.index_for`, must run on
  every request to build the skill index regardless, so the wasted work is the string assembly in
  `_assemble_prompt`. It is recorded because the cache reads as an optimization and is not one,
  which invites a wrong conclusion when prompt-assembly cost is profiled later.
- **Fix:** Split the skill-index build out of `_build_base_prompt` so a hit skips the assembly, or
  delete the cache and its key.

#### [DEAD-CODE] Four helpers and one parameter are defined and never used

- **Location:** `src/agent_loop.py:100`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** Repo-wide references, excluding this run:

  ```
  $ for sym in _looks_like_notes_list_request _compact_tool_line _is_local_openai_compat_url \
  >            _code_write_intent; do grep -rn "$sym" --include='*.py' . | grep -v '^./audit/'; done
  src/agent_loop.py:100:def _looks_like_notes_list_request(text: str) -> bool:
  src/agent_loop.py:823:def _compact_tool_line(name: str, section: str) -> str:
  src/agent_loop.py:945:def _is_local_openai_compat_url(endpoint_url: str) -> bool:
  src/agent_loop.py:1427:    _code_write_intent = has(
  ```

  `_looks_like_notes_list_request` (10 lines) and `_compact_tool_line` (20 lines) have no call
  sites. `_is_local_openai_compat_url` has none; its sibling `_is_ollama_openai_compat_url`
  (`:930`) is called at `:1058`. `_code_write_intent` is assigned inside `_classify_agent_request`
  and never read. `_build_base_prompt` (`:2850`) takes `mcp_disabled_map` and never references it;
  the map is consumed in `_build_system_prompt` at `:2288` and `:2749`.

- **Impact:** Low. Each is a place a maintainer can read or extend with no effect.
  `_is_local_openai_compat_url` restates the local-endpoint policy that the live classifier
  implements differently at `:1027`, so the two can be mistaken for one.
- **Fix:** Delete the unused functions and the assignment, and drop the `mcp_disabled_map`
  parameter from `_build_base_prompt`.

#### [BUG] A native model's auto-created document result never reaches the model

- **Location:** `src/agent_loop.py:5414`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** When a round contains a large code block and no document tool call, the fallback
  appends a synthetic `create_document` block to `tool_blocks` (`:5414`), after
  `_resolve_tool_blocks` (`:2944`) has produced `converted_calls` aligned 1:1 with the block list.
  Execution then yields one more result than there are converted calls. `_append_tool_results`
  (`:2995`), called at `:6290`, iterates the converted calls and indexes the result lists by the
  same position:

  ```python
  for j, tc in enumerate(native_tool_calls):
      result_text = tool_result_texts[j] if j < len(tool_result_texts) else ""
  ```

  The auto-created block's result sits at the last index, outside that range, and is dropped. The
  fenced path includes it, because that branch joins the full `tool_results` list into one text
  message.

- **Impact:** Low. A native-function-calling model that emits a non-document tool call and a large
  code block in the same round gets a document created in the editor without any tool result in
  its next context, so it can answer as if the code existed only in chat. If it repeats the code,
  the fallback can create a second document; whether models do that was not measured.
- **Fix:** Give the synthetic block the same treatment as the converted calls — synthesize a
  matching assistant tool call so the result has an id — or, in native mode, emit its result as a
  separate context message instead of dropping it.

## 8. src: LLM interaction, endpoints, model capability

### Overview

`src/ai_interaction.py`, `src/chatgpt_subscription.py`, `src/copilot.py`, `src/endpoint_resolver.py`, `src/foreground_model_routing.py`, `src/image_model_ids.py`, `src/llm_core.py`, `src/model_capabilities.py`, `src/model_capability_readers/__init__.py`, `src/model_capability_readers/base.py`, `src/model_capability_readers/generic_openai.py`, `src/model_capability_readers/google.py`, `src/model_capability_readers/google_ai_studio_mapping.py`, `src/model_capability_readers/llamacpp.py`, `src/model_capability_readers/lmstudio.py`, `src/model_capability_readers/ollama.py`, `src/model_capability_readers/openai.py`, `src/model_capability_readers/openrouter.py`, `src/model_context.py`, `src/model_discovery.py`.

The outbound LLM layer. `src/llm_core.py` holds the three call entry points (`llm_call`,
`llm_call_async`, `stream_llm`), provider detection, the per-provider URL and payload builders, the
SSE protocol the front end and the agent loop consume, and the local-model concurrency gate.
`src/endpoint_resolver.py` turns a setting prefix, an endpoint id or a model spec into a
`(url, model, headers)` triple and builds the request URL and auth headers for each provider.
`src/model_context.py` discovers and caches the context window, `src/model_capabilities.py` and the
nine reader modules in `src/model_capability_readers/` describe what a model supports, and
`src/model_discovery.py` lists model ids. `src/ai_interaction.py` is the agent-side tool dispatch;
`src/foreground_model_routing.py`, `src/chatgpt_subscription.py`, `src/copilot.py` and
`src/image_model_ids.py` carry the provider-specific policy.

The boundary: the handlers that call `llm_call`/`stream_llm` are `routes-chat-session`,
`routes-models` and the `routes-rest-*` sections; the agent loop that consumes the SSE protocol and
the tool schemas that parse a streamed tool call are `src-agent-loop` and `src-tools-*`; the
`ModelEndpoint`/`Session` schema, the settings store `resolve_endpoint` reads and the
`ProviderAuthSession` row are `core-data-platform`; the middleware that authenticates a request is
`core-auth-session`; the search, memory and RAG helpers `ai_interaction` calls are `services-search`
and `src-memory-rag`. This section covers what this layer sends, to whom, with which credential, and
what it does with the reply.

### Coverage

**Read fully:** all 20 assigned files (10,231 lines): `src/llm_core.py` (3,730),
`src/ai_interaction.py` (1,489), `src/model_capabilities.py` (934), `src/endpoint_resolver.py`
(672), `src/model_context.py` (520), `src/model_capability_readers/llamacpp.py` (428),
`src/model_capability_readers/base.py` (316), `src/chatgpt_subscription.py` (315),
`src/model_discovery.py` (293), `src/copilot.py` (256), `src/foreground_model_routing.py` (206),
`src/model_capability_readers/ollama.py` (204), `src/model_capability_readers/openrouter.py` (200),
`src/model_capability_readers/lmstudio.py` (186),
`src/model_capability_readers/google_ai_studio_mapping.py` (162),
`src/model_capability_readers/__init__.py` (95), `src/model_capability_readers/openai.py` (65),
`src/model_capability_readers/google.py` (60),
`src/model_capability_readers/generic_openai.py` (58), `src/image_model_ids.py` (42).

**Read partially:** the boundary code each finding rests on — `src/tool_schemas.py` at
`function_call_to_tool_block` (`:1370-1400`, the consumer of the streamed tool-call event);
`src/tool_execution.py` at the `pipeline`/`manage_memory`/`ui_control` dispatch into
`dispatch_ai_tool` (`:1169-1171`); `routes/chat_helpers.py` at the context-length, compaction and
trim block (`:737`, `:745-805`) and the ChatGPT-subscription branch (`:455-465`);
`routes/chat_routes.py` at `_session_url_matches_endpoint` (`:415-425`), the subscription recovery
block (`:551-600`), `_reconcile_selected_route` (`:670-728`) and the foreground-policy block
(`:822-880`); `src/context_compactor.py` at `trim_for_context` (`:224-236`) and `maybe_compact`
(`:323-345`); `routes/model_routes.py` at endpoint creation (`:2000-2050`) and the probe hints
(`:1175-1230`); `routes/cookbook_routes.py` at the local-endpoint registration (`:1800-1915`);
`routes/chatgpt_subscription_routes.py` (`:26-95`) and `routes/copilot_routes.py` (`:38-90`);
`core/database.py` at the `Session.headers` JSON column (`:199`) and `provider_auth_id` (`:553`);
`core/session_manager.py` at the three `headers` normalizations (`:134-145`, `:190-200`,
`:470-485`); `src/url_safety.py` at `check_outbound_url` (`:1-80`); `app.py` at the uvicorn start
(`:1306`); `specs/model-capability-canonical.md` at its "Current Gaps" list (`:168-180`);
`tests/test_resolve_model_offloaded.py` and `tests/test_llm_core_usage_finish_delta.py` in full for
what is already pinned; `static/js/chat.js` at the interrupted-response control (`:1215-1235`).

**Not read:** `src/agent_loop.py` except the two frames a stack trace named during the checks
(`_strip_think_blocks` at `:1253-1280`, entered from `:5572`); `src/agent_tools/*`; `src/tool_schemas.py` beyond `function_call_to_tool_block`; the
`routes-*` handlers beyond the cited regions (they belong to their own sections); `src/settings.py`
and the `ProviderAuthSession` schema; `core/middleware.py`; `routes/session_routes.py`,
`routes/email_routes.py` and `routes/webhook/webhook_routes.py` (the API-chat path that combines a
caller-supplied `base_url` with a key, `routes/webhook/webhook_routes.py:296-312`, is that section's
to judge); the front end beyond the cited file; and every other section's files.

**Checks run:** seven probes with throwaway scripts under `/tmp/probe/` (outside the target tree),
each quoted in the finding it settles — the event-loop stall, request log and cache behaviour of
`get_context_length` (`p_ctx_stall.py`); the same probe against an endpoint whose `/v1/models`
requires a key (`p_ctx_auth.py`); the probe URLs captured through a monkeypatched `httpx.get` for
five base-URL shapes; the real `stream_llm` driven against a stub SSE server whose body is complete,
closed after one chunk, ended with `finish_reason: "length"`, and cut mid-tool-call
(`p_stream_cut.py`); a `200 text/html` body through `llm_call`, `llm_call_async` and
`llm_call_async_with_route_fallback` (`p_nonjson.py`, `p_nonjson2.py`); the
`CHATGPT_SUBSCRIPTION_BASE_URL` override through `_detect_provider`, `build_chat_url` and
`build_headers` (`p_cgpt.py`); and the local-model gate's waiting counter with one holder and one
waiter (`p_gate.py`). Also `httpx.get("http://slots", timeout=5)` timed directly, and greps for the
importers of `src/model_capability_readers` (only `tests/test_model_capability_readers.py`),
`finish_reason` across `src/`, `routes/`, `core/` and `static/js/` (one comment, no reader),
`CHATGPT_SUBSCRIPTION_BASE_URL` writers, producers of a list-content `system` message, writers of a
string-typed `Session.headers`, and the credential-forwarding shape in `_reconcile_selected_route`
(`routes/chat_routes.py:670-700`). On the SSRF question specifically: nothing in this section accepts
a caller-supplied endpoint URL. `_resolve_model` (`src/ai_interaction.py:78-213`) matches a model
name against the caller's enabled `ModelEndpoint` rows and takes the URL *and* the key from the same
row via `resolve_endpoint_runtime`, and `_reconcile_selected_route` uses a form-supplied
`selected_endpoint_url` only to match a stored row, building the request from that row
(`routes/chat_routes.py:697-700`). The two `check_outbound_url` calls in `src/ai_interaction.py`
(`:1149`, `:1431`) guard the *provider-supplied* image result URL, not an endpoint.

One ordering artifact, recorded because it is a check result rather than a finding: run in a
non-alphabetical order (`test_llm_core_*.py` before `test_foreground_model_routing.py`) the same 44
suites hang. The stack trace at the hang names
`tests/test_foreground_model_routing.py:2257` → `src/agent_loop.py:5572` →
`_strip_think_blocks` (`:1272`), where a `Mock` reached the `text` argument, so
`lowered.find(" thinking", pos)` never returns `-1` and the loop spins until GC. It does not
reproduce in the suite's natural order (604 passed, 8.5s), so the CI job is unaffected; the leaking
suite is outside this section and was not chased.
The 44 suites matching this surface — `tests/test_llm_core_*.py` (22 files),
`tests/test_model_context.py`, `tests/test_model_capabilities.py`,
`tests/test_model_capability_readers.py`, `tests/test_model_defaults.py`,
`tests/test_model_discovery_status.py`, `tests/test_context_budget.py`,
`tests/test_context_cache_per_endpoint.py`, `tests/test_context_compactor*.py`,
`tests/test_compact_truncate_tool_call_args.py`, `tests/test_estimate_tokens_tool_calls.py`,
`tests/test_endpoint_resolver_{headers,models,urls}.py`, `tests/test_resolve_endpoint_fallbacks.py`,
`tests/test_resolve_model_offloaded.py`, `tests/test_resolve_session_auth_chatgpt.py`,
`tests/test_foreground_model_routing.py`, `tests/test_copilot*.py`,
`tests/test_chatgpt_subscription_routes.py`, `tests/test_ai_interaction_owner_scope.py` — were run
over this surface in their natural order: **604 passed**.

Four hypotheses did not survive checking and are not findings. (1) A `Session.headers` value that is
a JSON string would raise `ValueError` in the Ollama branch (`h.update(headers)`,
`src/llm_core.py:2620`) and `AttributeError` in the Anthropic branch (`_build_anthropic_headers`),
where the sync `llm_call` explicitly tolerates one (`:180`); no live writer stores a string — the
three assignment sites pass `build_headers(...)` or `{}`, and `core/session_manager.py` normalizes a
string to a dict on load. (2) A `system` message whose `content` is a list would raise `TypeError` in
`_sanitize_llm_messages`; no caller in `src/`, `routes/` or `core/` builds one. (3) The reader
modules in `src/model_capability_readers/` have no production caller (only their own test file
imports the package) — that is the documented state, not a defect:
`specs/model-capability-canonical.md:170` records "Canonical records are not yet used by runtime
discovery, endpoint resolution, model context, request shaping, or frontend pickers." (4) A
caller-supplied endpoint URL or model name cannot redirect a request to a chosen address or attach a
stored credential — see the SSRF note in the checks above.

#### [PERF] Context-length discovery runs two synchronous HTTP probes on the event loop, once per local request

- **Location:** `src/model_context.py:424` and `:450` (`_query_context_length`), called from `src/llm_core.py:2623`, `:2377`, `:2017`, `src/context_compactor.py:338` and `routes/chat_helpers.py:791`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_query_context_length` makes both probes with a synchronous client, on a 5-second
  budget (`REQUEST_TIMEOUT = 5`, `src/model_context.py:107`), and has no `async` variant:

  ```python
  r = httpx.get(f"{base}/slots", timeout=REQUEST_TIMEOUT)          # :424
  ...
  r = httpx.get(models_url, timeout=REQUEST_TIMEOUT)               # :450
  ```

  The Ollama branch of the async stream builder calls it inline, for every request:

  ```python
  elif provider == "ollama":
      target_url = _normalize_ollama_url(url)
      ...
      payload = _build_ollama_payload(
          model, messages_copy, temperature, max_tokens,
          stream=True, tools=tools, num_ctx=get_context_length(url, model),   # :2623
      )
  ```

  `_stream_llm_inner` is an `async def`, and the same call appears in `llm_call_async` (`:2377`),
  `maybe_compact` (`src/context_compactor.py:323-338`, `async def`) and
  `build_chat_context` (`routes/chat_helpers.py:791`). A ticker task on the loop, with a local
  endpoint that delays each response by 1.0s (`/tmp/probe/p_ctx_stall.py`):

  ```
  A) a 1.0s-slow local endpoint, called from the event loop
    inline (no thread)         elapsed=5.25s  ticker iterations=0  ctx=128000
  B) the same call moved off the loop
    asyncio.to_thread          elapsed=4.74s  ticker iterations=467  ctx=128000
  ```

  Zero iterations means the loop did not run once during the call. The 5.25s is mostly the mangled
  `/slots` URL of the next finding (3.98s of DNS) plus the server's 1.0s; the per-call ceiling is
  `REQUEST_TIMEOUT`, and a lookup that reaches both probes can spend 10s. The lookup also repeats
  work: `_configured_endpoint_kind` opens a session and scans the enabled endpoints
  (`db.query(ModelEndpoint).filter(ModelEndpoint.is_enabled == True).all()`,
  `src/model_context.py:56-88`) four times per `get_context_length` call — counted by wrapping the
  function — and nothing is cached for a local endpoint:

  ```
  D) repeat calls (local endpoints are never cached)
     call 1: 4.74s, server requests=1, cache entries=0
     call 2: 5.00s, server requests=1, cache entries=0
  ```

- **Impact:** while the lookup runs, every other request on the single uvicorn worker
  (`app.py:1306` starts uvicorn with no `workers=`) waits. The reachable case is a local endpoint
  that is slow to answer, wedged, or unreachable-but-not-refusing: a llama.cpp server busy loading a
  model, or a Tailscale peer that drops packets. `routes-chat-session` reports the same class of
  stall for `build_context_preface` (that section's "The chat path runs synchronous LLM, web-search
  and URL-fetch calls on the event loop"); this is a different callee on a different call site, and
  it fires on the Ollama stream path where that one does not.
- **Fix:** offload the two `httpx.get` calls, or the whole `get_context_length` call, with
  `asyncio.to_thread` at the four async call sites — the idiom this repository already uses for the
  identical defect in `_resolve_model` (`src/ai_interaction.py:275`, `:695`, `:1048`, pinned by
  `tests/test_resolve_model_offloaded.py`). An `async def get_context_length_async` avoids
  re-doing the offload at each caller, at the cost of a second entry point.

#### [BUG] Context-length discovery sends no credential, so an authenticated endpoint's real window is never read

- **Location:** `src/model_context.py:450` (and `:424`, `:367`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_query_context_length(endpoint_url, model)` takes no headers and passes none, even
  though the callers hold the endpoint's credential: `maybe_compact(..., sess.headers, ...)` is
  invoked from `routes/chat_helpers.py:794` and then calls `get_context_length(endpoint_url, model)`
  without them (`src/context_compactor.py:338`). Against a stub endpoint whose `/v1/models` requires
  `Authorization: Bearer sk-probe-key` (`/tmp/probe/p_ctx_auth.py`):

  ```
  known table has 'unlisted-model-9': False

  get_context_length('unlisted-model-9') -> 128000
     GET /slots  Authorization=None   (endpoint answers 401)
     GET /v1/models  Authorization=None   (endpoint answers 401)

  what the same endpoint reports when the key is sent:
     unlisted-model-9: context_length=32768
  ```

- **Impact:** for an endpoint that requires a key on `/v1/models` and serves a model the built-in
  table does not list (`KNOWN_CONTEXT_WINDOWS`, `src/model_context.py:112`), the window is never
  read and the caller gets `DEFAULT_CONTEXT` (128000). In `routes/chat_helpers.py:790-800` that
  number is both the compaction threshold and the trim budget:

  ```python
  context_length = get_context_length(sess.endpoint_url, sess.model)
  ...
  messages = trim_for_context(messages, context_length)
  ```

  so a real window *smaller* than the default — a 32K model behind an authenticated vLLM or LiteLLM
  proxy — is never compacted or trimmed, and the request goes out over the window: the silent
  truncation the code's own comment at `routes/chat_helpers.py:744` warns about ("window is silently
  truncated there"). A real window *larger* than the default only costs an early compaction. The
  known-model table covers most well-known ids, which is why the fallback is invisible for common
  models.
- **Fix:** add `headers: Optional[dict] = None` to `get_context_length`, `get_context_length_known`,
  `_get_context_length_cached`, `_query_context_length` and `_proxy_catalog_context`, and pass
  `headers=headers` to the three `httpx.get` calls; every caller in this section already has the
  headers in scope. The cache key is `(endpoint_url, model)` today; the probe shows the same endpoint
  answers differently with and without a key, so a keyless result cached under that key would
  outlive the fix unless the key is cleared or the cache key includes the credential.

#### [ERROR-HANDLING] A stream that ends without `[DONE]`, or is cut off at the token limit, is reported as a complete answer

- **Location:** `src/llm_core.py:3337-3343` (the end-of-stream block), `:3183-3191` (the delta parser)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the OpenAI-compatible parser reads only `delta` from the choice object; the
  `finish_reason` that rides in the same object is never read (it appears once in the file, in a
  comment at `:3141`):

  ```python
  _c0 = (j["choices"] or [None])[0]          # :3183
  if _c0 is None:
      continue
  delta = _c0.get("delta") or {}             # :3186
  ```

  and the end of the response is handled unconditionally, whether or not a terminator arrived:

  ```python
  # End of stream (no explicit [DONE] received)      # :3337
  for event in _format_routed_content(_harmony_router.flush()):
      yield event
  tc_event = _emit_tool_calls()
  if tc_event:
      yield tc_event
  yield "data: [DONE]\n\n"                            # :3343
  ```

  The real `stream_llm` driven against a stub server (`/tmp/probe/p_stream_cut.py`) emits the same
  events for a complete response, a response whose connection is closed after the first chunk, and a
  response the provider stopped at the limit:

  ```
  complete  -> ['data: {"delta": "Hello"}', 'data: [DONE]']
  cut       -> ['data: {"delta": "Hello"}', 'data: [DONE]']
  length    -> ['data: {"delta": "Hello"}', 'data: [DONE]']
  ```

  A cut tool call is emitted the same way, and its consumer then drops it:

  ```
  cut_tool  -> ['data: {"type": "tool_calls", "calls": [{"id": "", "name": "bash", "arguments": "{\\"command\\": \\"ls"}]}', 'data: [DONE]']

  function_call_to_tool_block('bash', '{"command": "ls') -> None
  function_call_to_tool_block('bash', '') -> ToolBlock(tool_type='bash', content='')
  ```

  The last two lines come from `src/tool_schemas.py:1370-1385`: truncated arguments fail `json.loads`, are
  logged as "Failed to parse function call arguments for bash", and the call is discarded; empty
  arguments coerce to an empty command. Two signals that would distinguish the cases are already in
  the protocol and unused: the requested final usage chunk (`stream_options: {"include_usage": True}`,
  `:2639-2640`, for every provider except OpenRouter and Groq) and `finish_reason`. The front end
  offers a manual "Continue" control for an interrupted message
  (`static/js/chat.js:1215-1235`), but nothing sets it from a stream that ended early.
- **Impact:** a reply the provider truncated — at the token limit, or because the connection dropped
  mid-answer — is persisted and displayed as a complete answer, and an agent turn whose tool call was
  cut off simply ends as if the model had chosen not to call one. Nobody sees an error. The stored
  message is also what the next turn's context is built from.
- **Fix:** forward the terminal chunk's `finish_reason` as its own SSE event and let the agent loop
  and the front end treat `length`/`max_tokens` as a truncation; alternatively treat a missing usage
  chunk as truncation when it was requested. Passing the field through is the smaller change and does
  not guess.

#### [BUG] The `/slots` context probe loses its host for a base URL without a path

- **Location:** `src/model_context.py:423`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the probe target is built by string surgery:

  ```python
  base = endpoint_url.split("/v1")[0] if "/v1" in endpoint_url else endpoint_url.rsplit("/", 1)[0]
  r = httpx.get(f"{base}/slots", timeout=REQUEST_TIMEOUT)
  ```

  For a base URL with no path, `rsplit("/", 1)[0]` returns `http:/`, and `f"{base}/slots"` is
  `http://slots` — a request to a host named `slots`. Captured with a monkeypatched `httpx.get`:

  ```
  http://localhost:11434           -> ctx=128000
       requested http://slots   headers=None
       requested http://localhost:11434/api/tags   headers=None
  http://localhost:11434/v1        -> ctx=128000
       requested http://localhost:11434/slots   headers=None
  http://192.168.1.50:8080         -> ctx=128000
       requested http://slots   headers=None
  ```

  That request fails on DNS, and the failure is not instant:

  ```
  $ httpx.get('http://slots', timeout=5)
  failed after 3.98s: ConnectError: [Errno -2] Name or service not known
  ```

  A pathless base URL is a supported shape: the add-endpoint route only calls `normalize_base`,
  which strips suffixes and never adds `/v1` (`routes/model_routes.py:2011`), and `_detect_provider`
  classifies a pathless URL as Ollama. The cookbook's own local endpoints are created with `/v1`
  (`routes/cookbook_routes.py:1813`), where the probe URL is correct.
- **Impact:** every context lookup for a pathless endpoint pays a DNS lookup for `slots` — 3.98s
  measured here, bounded by the 5s timeout — and the llama.cpp `n_ctx` probe never runs. Ollama has
  no `/slots` endpoint, so for the shape that triggers it the lost value is only the wasted request;
  a llama-server configured without `/v1` loses the reported window and falls back to the models
  catalog or the default. The stall lands on the event loop through the previous finding.
- **Fix:** derive the probe target from the parsed URL —
  `f"{parsed.scheme}://{parsed.netloc}/slots"` — and skip the probe when the endpoint is Ollama,
  since `/slots` is a llama.cpp endpoint and `/api/tags` does not report a window.

#### [ERROR-HANDLING] A 200 response with a non-JSON body escapes as a `JSONDecodeError` instead of the documented 502

- **Location:** `src/llm_core.py:2044` (`llm_call`), `:2429` (`llm_call_async`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `data = r.json()` sits one line above the schema guard that turns a bad body into a
  502:

  ```python
  if not r.is_success:
      raise HTTPException(502, f"Upstream {target_url} -> {r.status_code}: {r.text}")
  data = r.json()                       # :2044
  try:
      ...
  except Exception:
      raise HTTPException(502, f"Unexpected schema from {target_url}: {str(data)[:400]}")   # :2065
  ```

  `llm_call_async` repeats the shape (`data = r.json()` at `:2429`, inside no `try`). A stub server
  answering `200 text/html` with an nginx-style error page (`/tmp/probe/p_nonjson.py`):

  ```
  llm_call         raised JSONDecodeError: Expecting value: line 1 column 1 (char 0)
  llm_call_async   raised JSONDecodeError: Expecting value: line 1 column 1 (char 0)
  ```

  The route-fallback chain shows the inconsistency directly — the same HTML body is a friendly
  `HTTPException` when the status is 502 and an unhandled `JSONDecodeError` when it is 200
  (`/tmp/probe/p_nonjson2.py`):

  ```
  html200   raised JSONDecodeError: Expecting value: line 1 column 1 (char 0)
  real502   raised HTTPException: 502: local endpoint is having an outage (HTTP 502). <html>...
  ```

  The streaming path already handles the equivalent case by skipping the bad line
  (`:3333-3335`, "Error parsing stream data").
- **Impact:** a reverse proxy or gateway that answers 200 with an HTML body produces an unexpected
  exception type instead of the documented failure mode: `llm_call_async_with_route_fallback` cannot
  classify it, so a route returns a 500 traceback where every other upstream failure yields a clean
  502 with a friendly message.
- **Fix:** move `data = r.json()` inside the existing `try:` block in both functions, or add
  `except ValueError: raise HTTPException(502, f"Non-JSON body from {target_url}: {r.text[:200]}")`
  next to the existing status check.

#### [BUG] `CHATGPT_SUBSCRIPTION_BASE_URL` cannot work: provider detection keys on the literal `chatgpt.com` host

- **Location:** `src/chatgpt_subscription.py:20-23` and `:64-75` (`is_chatgpt_subscription_base`), consumed by `src/llm_core.py:991-993` (`_detect_provider`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the module reads the environment variable into
  `DEFAULT_CHATGPT_SUBSCRIPTION_BASE_URL` (`:20-23`), and the classifier accepts only one host:

  ```python
  return host == "chatgpt.com" and (
      path == "/backend-api/codex" or path.startswith("/backend-api/codex/")
  )
  ```

  With the variable set to a gateway (`/tmp/probe/p_cgpt.py`):

  ```
  DEFAULT_CHATGPT_SUBSCRIPTION_BASE_URL = https://llm-gateway.internal.example/backend-api/codex
  is_chatgpt_subscription_base(base) = False
  _detect_provider(base)   = openai
  build_chat_url(base)     = https://llm-gateway.internal.example/backend-api/codex/chat/completions
  build_headers(token)     = [('Authorization', 'Bearer ACCESS-TOKEN')]

  the stock base URL for comparison:
    _detect_provider       = chatgpt-subscription
    build_chat_url         = https://chatgpt.com/backend-api/codex/responses
  ```

  The override is what the provisioner stores: `base_url=base` on the `ProviderAuthSession`
  (`routes/chatgpt_subscription_routes.py:51`) and on the `ModelEndpoint` it creates (`:71-78`), and
  `resolve_runtime_credentials` falls back to the same constant (`src/chatgpt_subscription.py:286`).
- **Impact:** an operator who points the subscription provider at a mirror or a gateway gets the
  OpenAI-compatible request path (`/chat/completions` instead of `/responses`), a plain bearer header
  without the Codex `Accept`/`Origin`/`Referer` set, and the OpenAI-compatible SSE parser instead of
  the Responses one — a 404 or a protocol mismatch on every request, with no error that names the
  cause. The model list is fetched from the hardcoded `https://chatgpt.com/...` URL regardless
  (`:94-98`), so the override is half-wired in either direction.
- **Fix:** have `is_chatgpt_subscription_base` also return True for
  `DEFAULT_CHATGPT_SUBSCRIPTION_BASE_URL`, or drop the environment override and hardcode the base in
  one place. If the variable is only a test seam, deleting it is the smaller change.

#### [BUG] The local-model gate decrements its foreground-waiting counter twice per call

- **Location:** `src/llm_core.py:98` (increment), `:123` and `:135` (two decrements)
- **Severity:** low
- **Disposition:** next
- **Evidence:** a foreground request increments once and decrements on acquire *and* again in the
  `finally`:

  ```python
  if kind == "foreground":
      _LOCAL_MODEL_WAITING_FOREGROUND += 1                          # :98
  ...
  try:
      await _LOCAL_MODEL_LOCK.acquire()
      acquired = True
      if kind == "foreground":
          _LOCAL_MODEL_WAITING_FOREGROUND = max(0, _LOCAL_MODEL_WAITING_FOREGROUND - 1)   # :123
      ...
      yield
  finally:
      if kind == "foreground":
          _LOCAL_MODEL_WAITING_FOREGROUND = max(0, _LOCAL_MODEL_WAITING_FOREGROUND - 1)   # :135
  ```

  The counter is the signal that keeps background work out of the local model pipe
  (`while _LOCAL_MODEL_WAITING_FOREGROUND > 0 or has_foreground_activity(): await asyncio.sleep(0.25)`,
  `:115`). One holder and one waiter (`/tmp/probe/p_gate.py`):

  ```
  holder inside slot      : counter=0
  after B starts waiting  : counter=1 (B is waiting for the lock)
  after the holder exits  : counter=0 (B is still waiting)
  after B finishes        : counter=0
  ```

  The holder's `finally` clears the waiter's increment, so the counter reads zero while a foreground
  request is still waiting — exactly the window the signal exists for. A second foreground request
  arriving later can also have its own increment consumed by an earlier call's `finally`, because the
  `max(0, ...)` clamp hides the negative.
- **Impact:** a background request entering that window skips the busy-wait and queues directly on
  the lock, so the priority mechanism the docstring describes ("foreground chat taking priority",
  `:83`) is weaker than it reads. The mitigation is that `asyncio.Lock` serves its waiters in order,
  so the waiting foreground request is still served first and no foreground request is starved; this
  is a wrong signal, not a wrong order.
- **Fix:** delete the decrement at `:123` and keep the one in the `finally`, or move the increment
  into a `try` whose `finally` owns the single matching decrement.

## 9. src: tool parsing and execution

### Overview

`src/tool_parsing.py` (1,525 lines) turns raw model text into executable `ToolBlock`s — fenced
blocks, `[TOOL_CALL]`, `<invoke>`/`<tool_call>`/DSML/StepFun/Gemma/`<tool_code>` markup, raw
OpenAI tool-call JSON — and provides the mirror `strip_tool_blocks` used for display and
persistence. `src/tool_execution.py` (1,417 lines) is the dispatcher: per-turn workspace
binding, the path-confinement helpers (`_resolve_tool_path`, `_resolve_search_root`,
`agent_cwd`, `vet_workspace`), the MCP-vs-native routing for each tool name, the
capability/admin/policy gates, and `format_tool_result`. The capability and policy tables
themselves (`src/tool_capabilities.py`, `src/tool_policy.py`, `src/tool_security.py`) are
assigned to `src-tools-capabilities-policy`; the individual tool handlers
(`src/agent_tools/*`) to `src-agent-tools`; the loop that calls the dispatcher to
`src-agent-loop`.

### Coverage

**Read fully:** `src/tool_parsing.py` (1,525 lines), `src/tool_execution.py` (1,417 lines).
Every cited line was re-read at `2992bf6d368a`.

**Read partially:** `src/builtin_mcp.py` (the `_BUILTIN_SERVERS` table and its comment);
`src/mcp_manager.py` at `call_tool` (`:467-508`); `src/agent_tools/subprocess_tools.py` at
`BashTool.execute` (`:298-357`) and the tmux helpers (`:41-176`); `src/agent_loop.py` at
`_resolve_tool_blocks` (`:2944-2990`), the two `execute_tool_block` call sites (`:4559`,
`:5793`), the `strip_tool_blocks` call sites (`:5007`, `:5425`), and the try/except structure
of `stream_agent_loop`; `routes/chat_routes.py` at `_resolve_request_workspace` (`:348-372`)
and the stream's only handler (`:2551`); `tests/test_redos_llm_parsers.py` (201 lines);
`tests/test_agent_bash_windows.py` at the tmux cases (`:55-100`); `src/preset_manager.py` and
`static/js/presets.js` only for the `max_tokens: 0` presets.

**Not read:** `src/tool_capabilities.py`, `src/tool_policy.py`, `src/tool_security.py`,
`src/tool_approvals.py`, `src/tool_schemas.py`, `src/tool_utils.py` (other sections); the
`src/agent_tools/*` handlers beyond the `ctx` reads cited here; the MCP servers under
`mcp_servers/`; `src/ai_interaction.py`; `src/tool_implementations.py`. No test suite was run.

### Findings

#### [ERROR-HANDLING] An uncaught `RecursionError` from `raw_decode` aborts the chat stream

- **Location:** `src/tool_parsing.py:755`
- **Severity:** low
- **Disposition:** next
- **Evidence:** Both raw-OpenAI scanners try to decode from every `[` or `{` in the response
  and catch only `json.JSONDecodeError`:

  ```python
  for match in re.finditer(r"[\[{]", text):
      try:
          parsed, _end = decoder.raw_decode(text[match.start():])
      except json.JSONDecodeError:
          continue
  ```

  `_strip_raw_openai_tool_call_json` has the same shape at `:783-785`. CPython's JSON scanner
  raises `RecursionError`, not `JSONDecodeError`, when array nesting exceeds the recursion
  limit. Measured with the project's `venv/bin/python`:

  ```
  parse_tool_blocks('"function"' + '['*9000)   OK              0.763s
  parse_tool_blocks('"function"' + '['*10000)  RecursionError   0.001s
  strip_tool_blocks('"function"' + '['*12000)  RecursionError
  ```

  Both entry points run on every response: `_parse_raw_openai_tool_call_json` is Pattern 4d of
  `parse_tool_blocks` (`:1462`), and `_strip_raw_openai_tool_call_json` runs unconditionally in
  `strip_tool_blocks` (`:1513`). Neither `_resolve_tool_blocks` (`src/agent_loop.py:2944`) nor
  the body of `stream_agent_loop` wraps those calls in a `try`, and the only handler around the
  stream is `except (asyncio.CancelledError, GeneratorExit)` (`routes/chat_routes.py:2551`), so
  the exception propagates out of the SSE generator.
- **Impact:** A model response (or prompt-injected text the model echoes) containing the literal
  `"function"` followed by ~10,000 nested `[` kills the turn: the client sees a truncated stream
  with no error event, and no assistant message is persisted. At 9,000 brackets the same scan is
  quadratic and already takes 0.76s.
- **Fix:** Catch `RecursionError` alongside `json.JSONDecodeError` in both scanners, or reject a
  candidate whose bracket nesting exceeds a small bound before decoding. The repo's ReDoS suite
  (`tests/test_redos_llm_parsers.py`) is the place for the regression case.
- **Re-review (2026-10-04):** lowered from medium. The input is a model response carrying about 10,000 nested brackets after
  the literal `"function"`, and the damage is that one turn. No request from another user is
  affected.


#### [BUG] The MCP fallback drops `session_id`, so the per-session tmux shell never runs

- **Location:** `src/tool_execution.py:696`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_MCP_TOOL_MAP` still routes bash through the MCP manager (`:564`), but
  `src/builtin_mcp.py:63-67` records that the bash/python/filesystem/web_search servers were
  folded into native execution, and `_BUILTIN_SERVERS` (`:72-77`) registers only
  image_gen/memory/rag/email. Every bash call therefore takes the fallback at `:1116` /
  `:696`, and `_call_mcp_tool` has no `session_id` to forward:

  ```python
  async def _call_mcp_tool(
      tool: str,
      content: str,
      progress_cb: Optional[Callable[[Dict], Awaitable[None]]] = None,
  ) -> Dict:
      ...
      if not mcp:
          return await _direct_fallback(tool, content, progress_cb=progress_cb) or ...
      ...
      fallback = await _direct_fallback(tool, content, progress_cb=progress_cb)
  ```

  `_direct_fallback` builds `ctx["session_id"]` from its own default `None`, and
  `BashTool.execute` gates the tmux persistence path on that value:

  ```python
  session_id = ctx.get("session_id")
  ...
  if session_id and not IS_WINDOWS and shutil.which("tmux"):
      stdout, stderr, rc, timed_out = await _run_tmux_bash(...)
  ```

  Measured with a stub MCP manager returning the not-connected result (`src/mcp_manager.py:481`),
  tmux installed at `/usr/bin/tmux`, and `_run_tmux_bash` patched to record invocation:

  ```
  execute_tool_block(ToolBlock("bash", "echo hello"), session_id="sess-1", owner="admin")
  desc: bash: echo hello
  result keys: ['exit_code', 'output']
  calls: [('mcp', 'mcp__bash__bash')]
  tmux used: False
  ```

- **Impact:** Every foreground bash call spawns a fresh `create_subprocess_exec`; `cd`, exported
  variables, and activated venvs do not survive to the next call in the same chat, the
  timeout path that sends Ctrl-C to a live tmux session is unreachable, and the
  `tmux_session` field the tool returns is never populated. The whole persistence feature is
  dead on a default deployment, including on the `get_mcp_manager() is None` branch, which
  drops `session_id` the same way.
- **Fix:** Add `session_id`/`owner` parameters to `_call_mcp_tool` (`:679`) and forward them in
  both `_direct_fallback` calls; pass them at the dispatch site (`:1116`).

#### [PERF] `_strip_bare_invoke_markup` re-lowercases the whole response on every iteration

- **Location:** `src/tool_parsing.py:1020`
- **Severity:** low
- **Disposition:** next
- **Evidence:** The scan calls `text.lower()` inside the loop, so each `<invoke>` block found
  copies and lowercases the entire remaining string — twice:

  ```python
  while True:
      start = text.lower().find("<invoke", pos)
      ...
      close = text.lower().find("</invoke>", tag_end + 1)
  ```

  The function is called unconditionally at the end of `strip_tool_blocks` (`:1523`), which
  runs on every round response. Measured on closed blocks, so every iteration pays both
  lowercases:

  ```
  '<invoke name="x"></invoke>' *  5000   130,000 chars    0.269s
  '<invoke name="x"></invoke>' * 10000   260,000 chars    1.071s
  '<invoke name="x"></invoke>' * 20000   520,000 chars    4.274s
  '<invoke name="x"></invoke>' * 40000 1,040,000 chars   17.315s
  ```

  Clean quadratic (4x per doubling). Response length is not bounded by default: a preset with
  `max_tokens: 0` sends the endpoint its own default (`src/preset_manager.py:59`), and
  `static/js/presets.js:470` maps any value above 8192 to 0, so a looping local model can
  emit megabytes.
- **Impact:** A response that repeats a closed `<invoke ...></invoke>` pair — a plausible
  local-model repetition loop — stalls the agent loop for 4s at 520 KB and 17s at 1 MB, on
  every round and on the model-failure path. The sibling scanners in this file were converted
  to forward-only iteration precisely to avoid this class (see `_iter_delimited`'s docstring
  at `:1178`).
- **Fix:** Hoist `lowered = text.lower()` before the loop (one pass instead of one per block),
  or drive the scan through `_iter_delimited`/`_strip_delimited` with a bare-`<invoke` opener
  carrying `re.IGNORECASE`.
- **Re-review (2026-10-04):** lowered from medium. The timings quoted are for a single model response of
  1 MB. That is beyond what one generation produces under an ordinary output-token limit, and the
  cost at the sizes a turn does produce is a fraction of a second because the scan is quadratic.
  The defect is real and the fix is the one stated; the reachability is what makes it low.


#### [PERF] The Gemma tool-call pattern is the remaining quadratic delimiter scan

- **Location:** `src/tool_parsing.py:170`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_GEMMA_TOOL_CALL_RE` is a lazy delimiter pattern that is still applied with
  `finditer`/`sub`, unlike every sibling pattern, which was split and moved to the
  forward-only `_iter_delimited`/`_strip_delimited`:

  ```python
  _GEMMA_TOOL_CALL_RE = re.compile(
      r"<\|?tool_call\|?>\s*call:([\w\d_-]+)\s*(\{[\s\S]*?\})\s*<\|?tool_call\|?>",
      re.IGNORECASE,
  )
  ```

  Used at `:1443` (`parse_tool_blocks`) and `:1511` (`strip_tool_blocks`). With an opener
  flood and no closing token, the engine rescans to end-of-string from every opener. Measured:

  ```
  parse_tool_blocks("<|tool_call|>call:x{" *  2000)    40,000 chars    0.234s
  parse_tool_blocks("<|tool_call|>call:x{" *  5000)   100,000 chars    1.464s
  parse_tool_blocks("<|tool_call|>call:x{" * 10000)   200,000 chars    5.872s
  parse_tool_blocks("<|tool_call|>call:x{" * 20000)   400,000 chars   23.589s
  strip_tool_blocks("<|tool_call|>call:x{" * 10000)   200,000 chars    5.886s
  ```

- **Impact:** A local model stuck in a repetition loop (or injected output) that emits the
  Gemma opener without the closing token stalls the round for 5.9s at 200 KB and 23.6s at
  400 KB, in both the parse and the display/persistence path. The same input is the one the
  repo's `tests/test_redos_llm_parsers.py` budget of 4s is meant to catch, but that suite does
  not cover this pattern.
- **Fix:** Split the pattern into open/close delimiters and use `_iter_delimited` for parse and
  `_strip_delimited` for strip, as `[TOOL_CALL]`, `<tool_call>`, `<tool_code>`, and
  `<function_model>` already do.
- **Re-review (2026-10-04):** lowered from medium. The timings quoted are for a single model response of
  200-400 KB. That is beyond what one generation produces under an ordinary output-token limit, and the
  cost at the sizes a turn does produce is a fraction of a second because the scan is quadratic.
  The defect is real and the fix is the one stated; the reachability is what makes it low.


#### [PERF] `_parse_raw_web_json_lookup` re-decodes every brace in each mention's window

- **Location:** `src/tool_parsing.py:591`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** For every `web_search` mention, the function scans a 1200-char window for `{`
  and calls `raw_decode` on the whole remaining response for each one:

  ```python
  for mention in _RAW_WEB_JSON_TOOL_RE.finditer(text):
      search_start = mention.end()
      search_end = min(len(text), search_start + 1200)
      for brace in re.finditer(r"\{", text[search_start:search_end]):
          start = search_start + brace.start()
          try:
              parsed, end = decoder.raw_decode(text[start:])
          except json.JSONDecodeError:
              continue
  ```

  Dense text makes the windows overlap: each mention retries the braces the previous mention
  already rejected. Measured on `"web_search {" * n`, and profiled at n=20,000:

  ```
  parse_tool_blocks("web_search {" *  5000)    60,000 chars    0.671s
  parse_tool_blocks("web_search {" * 10000)   120,000 chars    1.634s
  parse_tool_blocks("web_search {" * 20000)   240,000 chars    4.151s
  strip_tool_blocks("web_search {" * 20000)   240,000 chars    4.124s

  $ cProfile, n=20000: 1,995,050 raw_decode calls (~8 per input character), each
  failure constructing a JSONDecodeError.
  ```

  Reached through Pattern 6 (`:1468`) and the strip path (`:1517`), both gated on
  `not skip_fenced`, so it applies to fenced/local models.
- **Impact:** A response with many `web_search` mentions followed by braces — an odd but
  cheap-to-generate repetition — costs ~4s at 240 KB, with growth steeper than linear
  (0.67s → 1.63s → 4.15s per doubling) and both parse and strip paying it. The default
  `max_tokens` caps this in practice; an unbounded preset does not.
- **Fix:** Try only the first brace per mention, or cap the attempts and skip past a brace
  that failed, and check that the byte after `{` is `"` or `}` before calling `raw_decode`.

## 10. src: tool capabilities, policy and MCP builtins

### Overview

The tables and helpers every tool call is gated by, plus the built-in MCP registration:
`src/tool_capabilities.py` (708 lines) classifies each tool's effects and result integrity and
holds the run-local `ToolRunSecurityContext` that blocks high-impact tools once untrusted
context has entered the run; `src/tool_security.py` (284) holds the non-admin blocklist, the
plan-mode allowlist and its mutator backstop, and the owner-admin check; `src/tool_policy.py`
(242) composes the per-turn policy (the caller's disabled set, the guide-only detector, the web
toggles); `src/tool_utils.py` (92) is the leaf module for the MCP-manager and upload-handler
globals, output truncation, and the shared tool-arg parser; `src/builtin_mcp.py` (386)
registers the built-in stdio MCP servers (Python and the npx browser server) at startup. The
boundary with a neighbouring section: `src-tools-parse-exec` owns the dispatcher that calls
these tables (`execute_tool_block`) and the path-confinement helpers; `src-agent-tools` owns
the handlers the tables admit; `src-mcp` owns `mcp_manager.py` (read here only at
`_connect_stdio`); `src-tools-schema-index` owns the schema/index sources that
`plan_mode_disabled_tools` and `known_tool_names` read.

### Coverage

**Read fully:** `src/tool_capabilities.py` (708 lines), `src/tool_policy.py` (242),
`src/tool_security.py` (284), `src/tool_utils.py` (92), `src/builtin_mcp.py` (386);
`tests/test_tool_policy.py` (479) and `tests/test_email_registry_sync.py` (86), the two suites
that pin this section's policy partitions.

**Read partially:** `tests/test_external_context_tool_gate.py` (the capability assertions and
the gate/approval cases, not all 1,473 lines); `tests/test_builtin_mcp_npx_cache.py`;
`src/mcp_manager.py` at `_connect_stdio` (`:180-200`); `src/agent_loop.py` at the
`capabilities_for_action` call sites (`:3055-3090`, `:5745-5775`); `src/tool_approvals.py` at
`_matches_unlocked` (`:235-275`); `src/agent_tools/coding_tools.py` (the `todowrite` handler,
74 lines); `src/agent_tools/session_tools.py` at `manage_session` (`:248-470`);
`src/agent_tools/document_tools.py` at `ManageDocumentTool.execute` (`:740-900`);
`src/tools/system.py` at `do_manage_skills` (`:24-130`) and `do_manage_tasks` (`:274-520`);
`src/tools/calendar.py`, `src/tools/notes.py`, `src/tools/research.py`,
`src/tools/contacts.py` at their action dispatch; `src/ai_interaction.py` at
`do_manage_memory` (`:341-560`); `website/setup.md:735-755`; `specs/shell-mcp.md:88-100`;
`specs/testing-devops.md:218`.

**Not read:** `src/tool_schemas.py`, `src/tool_index.py`, `src/tool_approval_scopes.py`,
`src/tool_implementations.py` (assigned to `src-tools-schema-index`), `src/tool_execution.py`
(assigned to `src-tools-parse-exec`);
`src/agent_tools/*` beyond the handlers named above; `mcp_servers/*`; `src/mcp_manager.py`
beyond `_connect_stdio`; `src/teacher_escalation.py` beyond its `capabilities_for_action` call;
the JS/UI side of the tool toggles.

**Checks run:** the seven gate/policy suites above under `venv/bin/python -m pytest -q` —
`240 passed` in 2.0s. A script that diffs each multiplexed tool's read/write action sets in
`_PRIVATE_ACTION_READS`/`_PRIVATE_ACTION_WRITES` against its handler's `action ==` branches
(`manage_calendar`, `manage_contact`, `manage_documents`, `manage_memory`, `manage_notes`,
`manage_research`, `manage_session`, `manage_skills`, `manage_tasks`): no read action mutates
and no write action is classified read. A script computing
`TOOL_TAGS - plan_mode_disabled_tools() - PLAN_MODE_READONLY_TOOLS`: empty, so every
fence-callable tool is either allowlisted or denied in plan mode.

### Findings

#### [DOC-DRIFT] The browser MCP cache gate is off by default, and the setup guide documents the opposite

- **Location:** `src/builtin_mcp.py:212`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** The cache probe is only reached when `BROWSER_MCP_REQUIRE_CACHE` is true:

  ```python
  BROWSER_MCP_REQUIRE_CACHE = os.environ.get("ODYSSEUS_BROWSER_MCP_REQUIRE_CACHE", "").lower() in ("1", "true", "yes")
  ...
  if BROWSER_MCP_REQUIRE_CACHE and pkg_spec and not await _is_npx_package_cached(npx_path, pkg_spec):
  ```

  The comment above the gate states the intent — "the default path lets `npx -y` install
  @playwright/mcp on first start. Locked-down installs can opt back into the old no-network
  startup behavior with ODYSSEUS_BROWSER_MCP_REQUIRE_CACHE=1" (`:206-209`) — and
  `tests/test_builtin_mcp_npx_cache.py:39-43` pins the default to `False`. Measured with
  `venv/bin/python` against a stub manager, with `_is_npx_package_cached` stubbed to record its
  calls and report "not cached":

  ```
  --- default (env unset) ---
    REQUIRE_CACHE=False probe_called=False connect_attempted=True
    args: -y @playwright/mcp@latest --headless --caps vision --executable-path /usr/bin/chromium --isolated --no-sandbox
  --- ODYSSEUS_BROWSER_MCP_REQUIRE_CACHE=1 ---
    REQUIRE_CACHE=True probe_called=True connect_attempted=False
  ```

  Both shipped documents describe the `=1` behavior as the default. `website/setup.md:741`:
  "The npx-based ones (currently the browser server, `@playwright/mcp`) only start when their
  npm package is already in the local npx cache. If a package isn't cached, that server is
  skipped with a startup log message ... so a fresh install does not block on a multi-minute
  npm download". `specs/shell-mcp.md:96`: "It is cache-gated by checking npm's `_npx` cache ...
  uncached/missing browser MCP is logged with install guidance and skipped rather than blocking
  startup or downloading packages at boot." `specs/testing-devops.md:218` likewise calls it
  "cache-gated `@playwright/mcp@latest`". `ODYSSEUS_BROWSER_MCP_REQUIRE_CACHE` appears in no
  document at the snapshot (`grep -rn BROWSER_MCP_REQUIRE_CACHE --include='*.md'` over the
  repository outside the untracked `audit/` run returns nothing), so the switch that restores
  the documented behavior is undiscoverable.
- **Impact:** On a fresh install the browser server is not skipped; a background task runs
  `npx -y @playwright/mcp@latest`, which downloads and executes an unpinned third-party package
  (~300 MB with Playwright) as the app user, with the full parent environment inherited
  (`src/mcp_manager.py:193` passes `{**os.environ, **env}` to the stdio child). An operator who
  read `website/setup.md` and relies on the no-download-at-boot contract — an air-gapped or
  metered host, or a supply-chain policy that expects the package to be vetted into the cache
  first — does not get it, and the documented install step is no longer required. The app's own
  startup is not blocked (the work runs in `_spawn_bg`), but the server-registration behavior
  the document describes is inverted.
- **Fix:** Either make the documented behavior the default
  (`os.environ.get("ODYSSEUS_BROWSER_MCP_REQUIRE_CACHE", "1")`) and document `=0` as the
  auto-install opt-out, or keep the current default and rewrite `website/setup.md:741` and
  `specs/shell-mcp.md:96` and add the variable to the setup guide's environment table. Pinning
  `@playwright/mcp` to a version narrows the execution risk but does not close the mismatch.

## 11. src: tool schemas, index and implementations

### Overview

The three sources that decide which tools a model is told about, and how a native function
call becomes a tool invocation. `src/tool_schemas.py` (1,601 lines) holds
`FUNCTION_TOOL_SCHEMAS` — the 71 OpenAI-style function definitions sent to native
function-calling endpoints — and `function_call_to_tool_block`, the converter that turns a
native call's JSON arguments back into the text `ToolBlock` the execution pipeline consumes.
`src/tool_index.py` (629) holds `BUILTIN_TOOL_DESCRIPTIONS` (the RAG corpus), the `ToolIndex`
that embeds it so agent mode can retrieve the top-K tools per message, and the deterministic
keyword hints that force-include a toolset when retrieval is unavailable or thin.
`src/tool_implementations.py` (115) is a facade re-exporting the `do_*` handlers from
`src/tools/*` and `src/agent_tools/*`, and owns the active-email globals.

The boundary with a neighbouring section: `src-tools-parse-exec` owns the parsers
(`src/tool_parsing.py`) and the dispatcher (`src/tool_execution.py`) that consume this
module's `ToolBlock` output; `src-agent-tools` owns the `do_*` handler bodies;
`src-agent-loop` owns the loop that calls `function_call_to_tool_block`, assembles the prompt
from `TOOL_SECTIONS`, and filters the schema list it sends. The `TOOL_TAGS` set is defined in
`src/agent_tools/__init__.py`, but it is the fence-callable set this module's converter
checks against, so it is reviewed here; its other consumers (the plan-mode denylist, the
capability tables) belong to `src-tools-capabilities-policy`.

### Coverage

**Read fully:** `src/tool_schemas.py` (1,601 lines — every schema and the whole converter),
`src/tool_index.py` (629), `src/tool_implementations.py` (115);
`tests/test_tool_index_schema_parity.py` (56), `tests/test_research_report_read.py` (66),
`tests/test_tool_rag_keyword_hints.py` (65), `tests/test_tool_implementations_shim.py` (165).

**Read partially:** `src/agent_loop.py` at `_resolve_tool_blocks` (`:2944-2992`),
`_assemble_prompt` (`:848-865`), the domain/keyword tables (`:528-556`),
`_classify_agent_request` (`:1390-1489`), the `manage_session`/`manage_documents`/
`manage_research` prompt sections (`:693-702`), the native call site and per-block loop
(`:5631-5832`), the empty-tool-blocks exit (`:5433`), and the fenced gate (`:2983`);
`src/tool_execution.py` at `_split_bg_marker` (`:737-747`), the bash call (`:1087`),
`_MCP_ARG_PARSERS` (`:627-637`), and the `tail_serve_output` dispatch (`:1205-1207`);
`src/agent_tools/__init__.py` at the `TOOL_TAGS` set (`:79-114`);
`src/agent_tools/document_tools.py` (`:799-890`), `session_tools.py` (`:302-350`),
`web_tools.py` (`:8-30`), `filesystem_tools.py` (`:243-256`);
`src/tool_security.py` at `_PLAN_MODE_KNOWN_MUTATORS` (`:130-166`); `src/agent_runs.py` at
`_drain` (`:115-173`); `routes/chat_routes.py` at the active-email block (`:1091-1140`);
`src/tools/system.py`, `src/tools/calendar.py`, `src/tools/notes.py` and
`src/ai_interaction.py` at their action dispatch, to compare each multiplexed tool's enum
with its handler.

**Not read:** the `do_*` handler bodies beyond their action dispatch (assigned to
`src-agent-tools`); `src/tool_execution.py` beyond the call sites named;
`src/tool_parsing.py` (assigned to `src-tools-parse-exec`); `static/js/*` (the UI side of the
tool toggles and pickers); the embedding/ChromaDB lanes behind `ToolIndex`.

**Checks run:** a three-way set diff of the schema names, `TOOL_TAGS` and
`BUILTIN_TOOL_DESCRIPTIONS` keys (findings 2 and 3); `function_call_to_tool_block` driven
with seven malformed-but-plausible argument objects, each resulting block fed to its first
consumer (finding 1); a `ToolIndex` with retrieval stubbed to exercise the keyword hints for
four report-reading queries (finding 3); each multiplexed tool's enum compared with its
handler's `action ==` branches (finding 4). `venv/bin/python -m pytest -q` on the three test
files listed as read fully: `10 passed`.

### Findings

#### [ERROR-HANDLING] A non-string argument from a native call crashes the turn instead of returning a tool error

- **Location:** `src/tool_schemas.py:1416-1419`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** For every tool whose content is built from a single argument, the converter
  copies the model's value through without a type check:

  ```python
  if tool_type == "bash":
      content = args.get("command", "")
  elif tool_type == "python":
      content = args.get("code", "")
  ...
  elif tool_type == "read_file":
      ...
      content = args.get("path", "")
  ```

  The empty-argument guard above it (`:1399-1402`) coerces with `str(...)`, so a dict counts
  as a non-empty value and passes:

  ```python
  required_args = _REQUIRED_NATIVE_TOOL_ARGS.get(tool_type)
  if required_args and not any(str(args.get(key) or "").strip() for key in required_args):
  ```

  `_REQUIRED_NATIVE_TOOL_ARGS` (`:22-29`) lists `web_search`, `web_fetch`, `read_file`,
  `write_file`, `edit_file`, `apply_patch` — not `bash`, `python` or `create_document`. The
  converters that wrap the value in `json.dumps` (`grep`, `edit_file`, `todowrite`, `ls`,
  `glob`) are safe; the concatenating ones are not. Measured with the project's
  `venv/bin/python`, converter output and then the first consumer of that output:

  ```
  bash             -> content type 'dict' value {'command': 'echo hi'}
  python           -> content type 'list' value ['print(1)']
  read_file        -> content type 'dict' value {'p': '/etc/hostname'}
  create_document  -> CONVERTER RAISED TypeError: sequence item 0: expected str instance, dict found
  web_search       -> content type 'dict' value {'q': 'weather'}
  write_file       -> content type 'str'  value '{"path": "/tmp/x", "content": {"body": "hi"}}'
  grep             -> content type 'str'  value '{"pattern": 3}'

  _split_bg_marker({"command": "echo hi"})      -> AttributeError 'dict' object has no attribute 'split'
  WebSearchTool().execute({'q': 'weather'}, {}) -> AttributeError 'dict' object has no attribute 'strip'
  ```

  The consumers are `content.split("\n")` in `_split_bg_marker` (`src/tool_execution.py:740`,
  reached for any bash call with a `session_id` at `:1087`), `content.strip()` in
  `WebSearchTool.execute` (`src/agent_tools/web_tools.py:12`), and
  `content.split("\n", 1)[0]` in `ReadFileTool.execute`
  (`src/agent_tools/filesystem_tools.py:246`). `create_document` raises inside the converter
  itself (`src/tool_schemas.py:1459-1463`). `web_search` and `read_file` are not admin-only,
  so the dispatcher crashes are reachable for a normal user. Nothing catches the exception:
  `function_call_to_tool_block` is called at `src/agent_loop.py:2959`, the per-block loop has
  no handler, and an AST query for the `try` statements enclosing `desc, result = await
  _tool_task` (`:5819`) reports only one — the `try/finally` at `5808-5832`, with no
  `except`. For a normal chat the exception reaches `src/agent_runs.py:157`, which publishes
  a generic `event: error` ("Agent run failed before completion.") and marks the run
  `error`; compare panes stream without that wrapper and lose the connection.
- **Impact:** A model that emits a structured value where the schema says string — the class
  of output the non-object-arguments coercion at `src/tool_schemas.py:1392-1397` already
  defends against — kills the whole turn with a generic 500-class error instead of returning
  a tool result the model could correct on the next round. The user's message is saved and
  the assistant turn is not; a tool that was mid-work in the same round is abandoned.
  `bash` and `read_file` need an admin owner, `web_search` and `create_document` do not.
- **Fix:** Coerce at the converter boundary: `content = str(args.get("command") or "")` for
  each concatenating branch (and `json.dumps` for the object-valued cases), or reject a
  non-string value for a required string argument in the `_REQUIRED_NATIVE_TOOL_ARGS` guard
  and return `None` so the loop logs "FAILED to convert" and the model sees a normal error
  result. A regression test that feeds each schema's required string argument a dict and
  asserts no exception belongs next to `tests/test_function_call_non_object_args.py`.

#### [BUG] `tail_serve_output` is advertised to native models but missing from `TOOL_TAGS`, so every native call is rejected

- **Location:** `src/agent_tools/__init__.py:103-108`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** The `TOOL_TAGS` comment above the cookbook block states the contract and the
  exact failure mode:

  ```
  # Cookbook tools (LLM serving + downloads). Without these
  # entries, native function calls to e.g. list_served_models
  # are rejected as "Unknown function call" before reaching
  # the dispatcher — silent failure for the whole cookbook
  # surface.
  "download_model", "serve_model",
  "list_served_models", "stop_served_model",
  ...
  ```

  `tail_serve_output` is the one cookbook tool absent from the set. It has a schema
  (`src/tool_schemas.py:899`), an index description (`src/tool_index.py:130`), a prompt
  section telling the model to call it after a failed serve (`src/agent_loop.py:763`, plus
  the recovery hint at `:5506`), and a dispatcher branch (`src/tool_execution.py:1205`).
  Measured set diff at the snapshot:

  ```
  counts: schemas=71 tags=77 descs=73
  schemas - tags  : ['tail_serve_output']
  descs - tags    : ['tail_serve_output']
  ```

  It is reachable: the `cookbook` domain fires on `serve|launch|start|...`
  (`src/agent_loop.py:1417`) and seeds `_DOMAIN_TOOL_MAP["cookbook"]` (`:532`), which
  contains `tail_serve_output`, so for "why did the vllm serve crash on startup?" the
  schema is sent (measured: `domains=['cookbook'] tail_serve_output seeded=True`). The
  converter then rejects the call at `src/tool_schemas.py:1411` — `if tool_type not in
  TOOL_TAGS: logger.warning(f"Unknown function call: {name}")` — and `_resolve_tool_blocks`
  logs `FAILED to convert native call`. With no tool block produced, the turn takes the
  `if not tool_blocks:` exit at `src/agent_loop.py:5433` and accepts the model's prose as
  the final answer.
- **Impact:** The documented debug loop — `serve_model` → `list_served_models` reports
  `crashed` → `tail_serve_output` → retry with adjusted flags — cannot complete on any
  native function-calling endpoint (GPT/Claude/Qwen3/DeepSeek-V class). The model's log
  read is silently dropped, the turn ends as if it had answered, and the user gets a
  diagnosis the model made up rather than the traceback. The other 12 cookbook tools were
  added to this set precisely to prevent that; this one was missed. `schemas - tags` and
  `descs - tags` are both exactly this name, so the gap is a single missing string.
- **Fix:** Add `"tail_serve_output"` to the cookbook group in `TOOL_TAGS`. The existing
  parity test only pins one edge of the triangle (`tests/test_tool_index_schema_parity.py`
  asserts `schemas ⊆ descriptions`); extend it to assert `schemas ⊆ TOOL_TAGS` so a new
  schema cannot ship without a fence tag.

#### [BUG] `manage_research` has no native schema, so the report-read path the prompt and RAG steer to is unreachable for native models

- **Location:** `src/agent_loop.py:702`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** The prompt section tells every model that reading a finished deep-research
  report means calling this tool, including how to resolve the id and what not to do
  instead:

  > This IS how you read a finished report: when the user refers to a just-completed
  > deep-research job ("check it out", "read that report", "summarize the research") WITHOUT
  > giving an id, call `manage_research` with `action:list` to get the most-recent id, then
  > `action:read` with that id, and answer from the returned text. Do NOT `web_fetch`/
  > `app_api` the `/api/research/report/{id}` URL.

  `manage_research` is in `TOOL_TAGS` (`src/agent_tools/__init__.py:110`), in
  `BUILTIN_TOOL_DESCRIPTIONS` (`src/tool_index.py:102`), and in the RAG hint that fires for
  exactly these queries (`src/tool_index.py:445`: `{"manage_research", "trigger_research"}`
  for "my research", "the report", "saved research", …) — but it has no entry in
  `FUNCTION_TOOL_SCHEMAS` (measured: the only research-named schema is `trigger_research`).
  For a native model the tool is therefore advertised and unreachable at the same time.
  Measured with retrieval stubbed:

  ```
  query='summarize the research on fusion'
    relevant_tools: [ask_user, manage_memory, manage_research, trigger_research, ui_control, update_plan]
    schemas sent   : ask_user, manage_memory, trigger_research, ui_control, update_plan
    manage_research in relevant_tools: True
    manage_research in sent schemas  : False
    compact prompt line: ['- `manage_research`']
  ```

  The compact prompt used for native models (`_assemble_prompt(..., compact=True)`,
  `src/agent_loop.py:852-865`) lists the tool by name and says "Only the tool schemas
  provided by the API are available for this turn", so the model is told a tool exists that
  the API never declared. The fenced channel is closed too: for an API model
  `parse_tool_blocks` runs with `skip_fenced=True` (`src/agent_loop.py:2983`, gated on
  `is_api_model and not allow_fenced_for_api`), and a probe with a
  ```manage_research fence returns no block for `is_api_model=True` while the same input
  returns a block for a local model. `tests/test_research_report_read.py` pins the handler
  and the instruction text, not reachability, so the regression it guards (issue #1363 —
  the agent web-fetching the HTML report) can still reproduce on native endpoints. The
  handler's separate owner-scoping defect (it ignores `owner`) is recorded in
  `src-agent-tools.md`; this finding is only about reaching the tool at all.
- **Impact:** For every native function-calling endpoint the advertised way to read a saved
  report does not exist. The model either answers from nothing, or falls back to the two
  things the prompt forbids — `app_api`/`web_fetch` on the HTML render, or a fresh
  `trigger_research` — which is the behaviour #1363 was fixed for on the textual path. The
  `trigger_research` schema *is* sent on the same turn, so the cheapest available action is
  the wrong one.
- **Fix:** Add a `manage_research` schema (action enum `list|read|delete`, `id`, `search`)
  next to `trigger_research` in `FUNCTION_TOOL_SCHEMAS`; the handler already accepts the JSON
  form the other multiplexed tools use. If fence-only is deliberate, say so in the prompt
  section and stop steering native models to it, and extend the parity test to assert that
  every tool named in `TOOL_SECTIONS` is either schema-backed or in a documented
  fence-only list.

#### [BUG] Two native schema enums omit actions their handler and prompt support

- **Location:** `src/tool_schemas.py:813`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `manage_documents` advertises three actions and a `document_id` described
  only as "for delete":

  ```python
  "description": "Manage documents: list all documents ..., delete documents, or run tidy cleanup.",
  "action": {"type": "string", "enum": ["list", "delete", "tidy"]},
  "document_id": {"type": "string", "description": "Document ID (for delete)"},
  ```

  The handler accepts the read family (`src/agent_tools/document_tools.py:828`:
  `elif action in ("read", "view", "open", "get")`), and the prompt section for the same
  tool tells the model `{"action": "list|read|delete|tidy"}` and "`read` (aliases:
  view/open/get) takes `document_id` and returns the content" (`src/agent_loop.py:701`).
  `manage_session` has the same gap in the other direction: its enum (`:426`) is
  `["rename", "archive", "unarchive", "delete", "important", "unimportant", "truncate",
  "fork"]` and `required: ["action", "session_id"]` (`:430`), while the handler also
  implements `list` (`src/agent_tools/session_tools.py:302`) and
  `switch/open/select/view` (`:325`), and its prompt section lists them
  (`src/agent_loop.py:693`). No code validates arguments against these enums (a search for
  `["enum"]`/`jsonschema` in `src/`, `routes/`, `core/`, `services/` finds no reader), so a
  model that ignores the enum still works; the other nine multiplexed tools
  (`manage_notes`, `manage_memory`, `manage_tasks`, `manage_calendar`, `manage_contact`,
  `manage_skills`, `manage_research`, `ui_control`, `edit_image`) match their handlers
  exactly.
- **Impact:** A model that honours the function definition's enum cannot read a document or
  list/switch chats through these tools: the only available actions are destructive or
  administrative, and the "open/show/read my document" flow degrades to a list of clickable
  rows. For `manage_session` the `switch` flow has no alternative tool, so "open my X chat"
  is unavailable to a strict model. The enum and the prompt disagree, which is also the kind
  of contradiction that makes a model emit a call outside the declared contract.
- **Fix:** Add the supported actions to both enums and to their descriptions
  (`["list", "read", "delete", "tidy"]`; `["list", "switch", "rename", ...]`), make
  `session_id` required only for the actions that need it (or keep it and document
  `"current"`), and add a test that asserts each multiplexed tool's enum equals the set of
  actions its handler dispatches on.

#### [DEAD-CODE] Three `ToolIndex` members are assigned and never read

- **Location:** `src/tool_index.py:153`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `self._embedder` is assigned the embedding client (`:153`) and never read;
  `self._fingerprint` is initialised (`:159`) and recomputed (`:219`) and never read; the
  `_embed` method (`:168-174`) has no caller. A search for `self._embed(`, `self._embedder`
  and `self._fingerprint` over the file returns only the definition sites, and the repo-wide
  search over `src/`, `routes/`, `services/`, `tests/` finds no external reader. Retrieval
  goes through the lanes (`self._lanes[...]`), which own their clients.
- **Impact:** The fingerprint is a SHA-256 over the sorted tool names
  (`",".join(sorted(BUILTIN_TOOL_DESCRIPTIONS.keys()))`), computed and stored after each
  builtin reindex, but nothing reads it, so the apparent "did the corpus change" guard is not
  one. The MCP path keeps its own live guard in `self._mcp_generation` (`:230-231`), which
  makes the unused attribute look like the intended builtin counterpart. The unused method and
  attribute also make the class look like it has a second embedding path.
- **Fix:** Delete `_embed`, `_embedder` and `_fingerprint`, or wire the fingerprint into a
  rebuild decision the way `_mcp_generation` guards `index_mcp_tools`, with a test asserting a
  reindex is skipped when the tool-name set is unchanged.

#### [DEAD-CODE] The active-email global is written on every chat submit and never read

- **Location:** `src/tool_implementations.py:90-115`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `set_active_email` / `clear_active_email` / `get_active_email` manage a
  module global whose comment states the purpose — "Email tools can resolve 'this email'
  without guessing a UID" (`:87-89`). The frontend sends the open email on each submit
  (`static/js/chat.js:1867-1873`), the route calls `set_active_email(...)` /
  `clear_active_email()` around the turn (`routes/chat_routes.py:1099`, `:1131`), and
  `get_active_email` has no caller anywhere in the repository. The feature itself works
  through an explicit parameter: the route builds `active_email_ctx` from the form fields
  (`routes/chat_routes.py:1104-1126`), passes it to `stream_agent_loop(active_email=...)`,
  and the prompt injection reads the parameter (`src/agent_loop.py:2472-2478`).
  `tests/test_tool_implementations_shim.py:49-51` records that `get_active_email` has no
  in-repo importer and keeps the symbol for facade compatibility.
- **Impact:** Nothing breaks today, but the documented resolution mechanism does nothing,
  and the only reader that could be added is process-global state that the last chat submit
  overwrote — reviving `get_active_email()` inside an email handler would resolve "this
  email" from another user's turn. The per-request set/clear pair is otherwise dead weight
  on the chat path.
- **Fix:** Delete the global and the two `set_`/`clear_` calls from `routes/chat_routes.py`,
  keeping `get_active_email` (and the shim's `_EXPECTED` entry) only if the facade contract
  requires it; if the global is meant to be the source of truth, have the loop read it and
  key it by owner and session.

## 12. src: scheduled built-in actions

### Overview

`src/builtin_actions.py` (3,436 lines) is the registry of work a scheduled task can run without
an LLM: housekeeping (sessions, documents, memory, research), the email passes (summarize, draft
replies, auto-translate, urgency triage), the calendar passes (extract events from mail, classify
events), the daily brief, sender-signature learning, skill test and audit, the admin-only shell
actions (`ssh_command`, `run_script`, `run_local`), and the Cookbook serve launcher. The scheduler
that invokes an action (`src/task_scheduler.py:1242`) is assigned to `src-research-scheduling`; the
task routes that validate and gate creation are assigned to `routes-skills-calendar-task` and are
cited here only where a finding needs them. The email helpers the actions call
(`routes/email_helpers.py`) belong to `routes-email`, the skills pipeline to
`routes-skills-calendar-task`, and the other ten `src/tool_*.py` files to the three sibling
`src-tools-*` sections.

### Coverage

**Read fully:** `src/builtin_actions.py` (3,436 lines). Every cited line was re-read at
`2992bf6d368a`.

**Read partially:** the scheduler call path `_execute_action` and its result handling
(`src/task_scheduler.py:918-946`, `:1242-1268`); `RETIRED_HOUSEKEEPING_ACTIONS` (`:265-269`) and
the retirement sweep (`:2345-2361`); `src/task_action_policy.py` (the admin-action set and
`owner_has_admin_task_privileges`); `routes/task/task_routes.py:426-465` (create) and `:666-690`
(update) to confirm the admin gate is applied on both write paths; `routes/email_helpers.py` at
`_imap_connect` (`:1200-1248`) and `_get_email_config` (`:1011-1066`); the
`sender_signatures` schema (`:639-648`); `core/database.py` at `CalendarCal`/`CalendarEvent`
(`:1838-1881`); `static/js/tasks.js:222-233`, `:449`, `:620`, `:1332`; `src/settings.py:187`;
`tests/test_builtin_actions_owner_scope.py`, `tests/test_classify_events_memory_text.py`,
`tests/test_email_urgency_checkpoint.py:97-140`, `:1170-1200`, and
`tests/test_imap_uid_commands.py:78-108` to see what the suite pins.

**Not read:** `src/task_scheduler.py` in full; `routes/email_pollers.py` beyond
`_run_auto_summarize_once`'s return strings (`:1320-1356`); the email, calendar, and skills route
modules; `services/memory/skills.py`; `routes/skills_routes.py`; every test not named above. No
test suite was run.

### Findings

#### [BUG] The email-urgency triage never reaches its LLM classifier, and still requires an LLM endpoint

- **Location:** `src/builtin_actions.py:2707`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** Every newly fetched UID takes the heuristic path and then `continue`s, so the
  classifier that follows is unreachable for every item:

  ```python
                  verdict = _heuristic_email_verdict(item)
                  cache.setdefault("uids", {})[item["uid"]] = verdict
                  per_uid_scores[key] = verdict
                  saved_classifications += 1
                  continue
                  # ── LLM-classify. JSON-only response; bullet-proof parse.
                  llm_attempts += 1
                  prompt = (
  ```

  The unreachable region runs from `:2708` to the end of the loop body at `:2820`; the second
  `saved_classifications += 1` (`:2815`) and both `failed_classifications.append` sites
  (`:2746`, `:2817`) are inside it, so the report's
  "N failed" line (`:3074-3075`) and its "Unclassified" list (`:3130-3142`) can never appear;
  `llm_attempts` (`:2440`) is never read. The user-editable rules are loaded at `:2437`
  (`urgency_prompt = settings.get("urgent_email_prompt", "")`), exposed as a textarea in the
  Tasks panel (`static/js/tasks.js:222-233`, `:1332`, default at `src/settings.py:187`), and
  interpolated only into the dead prompt (`:2717`, `f"User's rules:\n{urgency_prompt}\n\n"`).
  The heuristic returns a hardcoded `"spam": False` (`:2519`), so the spam verdict the dead block
  computes can no longer be set. The action's own docstring still describes the removed
  behaviour ("Scan unread emails across all accounts, LLM-triage new ones", `:2250-2251`), and
  the gate that only the LLM needs remains at `:2434-2435`:

  ```python
          # ── 2. Account retirement above is state maintenance and does not
          # depend on model availability. Scanning still requires the utility
          # primary/fallback candidates resolved for this task owner.
          if not candidates:
              return "No LLM endpoint available", False
  ```

  `git blame` puts the heuristic call and the `continue` in `4ab68b656` ("Polish mobile UI and
  editor workflows"); the LLM block was left in place. `_execute_action` records the `False`
  return as `run.status = "error"` (`src/task_scheduler.py:923-927`).
- **Impact:** A user who writes custom triage rules sees them silently ignored, and the report
  can never say a classification failed. On a deployment with no utility model configured, a
  task that never calls a model is recorded as an error. The heuristic still scores, tags, and
  notifies, so this is a lost feature and a wrong failure status, not a broken action.
- **Fix:** Pick one path. For heuristic-only triage, delete `:2708-2820`, the `candidates` gate
  at `:2434-2435`, the `urgency_prompt` read, and `llm_attempts`, and say in the docstring and
  the rules field that it is unused. To keep the LLM, drop the `continue`; the block below it
  already parses, clamps, and falls back.

#### [BUG] `classify_events` classifies every user's calendar events with one user's memories

- **Location:** `src/builtin_actions.py:1369`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** The query selects from `CalendarEvent` alone — no join to `CalendarCal` and no
  owner filter:

  ```python
              events = db.query(CalendarEvent).filter(
                  CalendarEvent.dtstart >= now,
                  CalendarEvent.dtstart <= horizon,
                  CalendarEvent.status != "cancelled",
              ).all()
  ```

  `CalendarEvent` has no owner column; ownership is on `CalendarCal.owner`
  (`core/database.py:1843`). The sibling action in the same file scopes it and says why:

  ```python
              ev_q = db.query(CalendarEvent).join(CalendarCal).filter(
                  CalendarEvent.dtstart < tomorrow,
                  CalendarEvent.dtend > today,
                  CalendarEvent.status != "cancelled",
              )
              if owner:
                  ev_q = owner_filter(ev_q, CalendarCal, owner, include_shared=_allow_null)
  ```

  (`:1805-1812`, under the "v2 review HIGH-12" comment at `:1797-1804`.) The same function loads
  only the running owner's memories (`:1387`, `_Mem.owner == owner`) and prepends them to the
  prompt that classifies the batch (`:1435-1436`). `classify_events` is not in
  `ADMIN_ONLY_TASK_ACTIONS` (`src/task_action_policy.py:5-10`), so any user can schedule it. The
  existing test (`tests/test_builtin_actions_owner_scope.py:70`) fakes an event class with no
  owner and a `_Db.filter()` that returns every row, so it passes whatever the query filters.
- **Impact:** In a multi-user deployment, one user's scheduled run rewrites `event_type`,
  `importance`, and `color` on every other user's events, and other users' event titles are sent
  to the model alongside the runner's personal memory context. Single-user deployments see no
  difference.
- **Fix:** Join `CalendarCal` and apply `owner_filter(..., include_shared=_allow_null)` the way
  `daily_brief` does, and load memories for the same owner that owns the events.

#### [BUG] `daily_brief` reads the default mailbox instead of the task owner's

- **Location:** `src/builtin_actions.py:1828`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** The calendar and notes halves of this action were explicitly scoped for
  multi-user deployments (comment at `:1797-1804`, query at `:1805-1812`), but the email half
  connects with no owner:

  ```python
              import email as _email
              conn = _imap_connect(None)
  ```

  `_imap_connect` defaults `owner` to `""` (`routes/email_helpers.py:1200`), and
  `_get_email_config` documents what that does:

  ```python
        2. Else → the row with is_default=True (scoped to `owner` when given).
        ...
      SECURITY: without `owner`, the fallback queries (is_default, first-enabled)
      don't filter by user — so on a multi-user deploy a brand-new account would
      inherit whoever else's IMAP/SMTP creds happened to be the default. Pass
      `owner` from the route's auth dependency to scope the lookup.
  ```

  (`routes/email_helpers.py:1016`, `:1025-1028`; the unfiltered `is_default` query is at
  `:1059-1065`.) The other actions in this file pass the owner: `_imap_connect(acct.id,
  owner=owner)` (`:1198`), `_imap_connect(None, owner=owner)` (`:1597`, `:1684`). The one test that
  calls this action (`tests/test_imap_uid_commands.py:78`) passes `owner=""` and replaces
  `_imap_connect` with a lambda that ignores its arguments, so the missing owner is not
  exercised.
- **Impact:** In a multi-user deployment, any user's daily brief counts unread mail and quotes
  up to five sender/subject pairs from whichever account is the default (or the first enabled
  one), then persists that text as the task result in that user's assistant chat.
- **Fix:** `conn = _imap_connect(None, owner=owner)`.

#### [DEAD-CODE] `action_tidy_calendar` is unreachable, and would delete across owners if it were reachable

- **Location:** `src/builtin_actions.py:853`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** The 100-line function (`:853-954`) is absent from `BUILTIN_ACTIONS`
  (`:3394-3416`), and the scheduler deletes any task whose action is in
  `RETIRED_HOUSEKEEPING_ACTIONS` (`src/task_scheduler.py:265-269`; sweep at `:2345-2361`).
  `_execute_action` returns `"Unknown action: ..."` for anything not in the registry
  (`src/task_scheduler.py:1246-1248`). The function itself queries and deletes without an owner
  filter:

  ```python
              events = db.query(CalendarEvent).order_by(CalendarEvent.dtstart).all()
  ...
                          db.delete(e)
  ```

  Its state-file constant is still imported (`:16`) and defined (`src/constants.py:35`).
  `action_ping_events` (`:1513-1515`) is the same shape: a `TaskNoop` stub absent from the
  registry. `static/js/tasks.js:449`, `:620` still carry an icon and a label for
  `tidy_calendar`.
- **Impact:** No user-visible behaviour today. The cost is maintenance and a trap: re-registering
  the action to revive calendar tidy would delete duplicate events for every user in a
  multi-user deployment.
- **Fix:** Delete `action_tidy_calendar` and its state constant, or re-register it behind the
  admin gate with the `CalendarCal` owner filter `daily_brief` uses. Remove the stale UI
  icon/label either way.

#### [BUG] `action_learn_sender_signatures` records success when it did nothing

- **Location:** `src/builtin_actions.py:1632`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** Two no-work exits return `True` instead of raising `TaskNoop`, which is the
  convention everywhere else in the file (`TaskNoop` at `:412`, raised at `:1018`, `:1039`,
  `:1075`, `:1103`, `:1277`):

  ```python
          mails = await _aio.to_thread(_pull_headers)
          if not mails:
              return "No emails to scan", True
  ...
          if not eligible:
              return "All sender sigs already cached (or no eligible senders)", True
  ```

  (`:1632`, `:1670`.) The scheduler drops a `TaskNoop` run row silently and records any other
  return as a run (`src/task_scheduler.py:923-927`, `:1267-1269`).
- **Impact:** A pass that scanned nothing appears as a successful Activity entry, unlike the
  other email actions, which noop instead. Low: the text is accurate; only the status is wrong.
- **Fix:** Raise `TaskNoop` from both branches.

## 13. src: agent tool implementations

### Overview

`src/agent_tools/__init__.py`, `src/agent_tools/admin_tools.py`, `src/agent_tools/bg_job_tools.py`, `src/agent_tools/coding_tools.py`, `src/agent_tools/document_tools.py`, `src/agent_tools/filesystem_tools.py`, `src/agent_tools/interaction_tools.py`, `src/agent_tools/model_interaction_tools.py`, `src/agent_tools/session_tools.py`, `src/agent_tools/subprocess_tools.py`, `src/agent_tools/web_tools.py`, `src/tools/__init__.py`, `src/tools/_common.py`, `src/tools/calendar.py`, `src/tools/contacts.py`, `src/tools/cookbook.py`, `src/tools/image.py`, `src/tools/notes.py`, `src/tools/research.py`, `src/tools/search.py`, `src/tools/system.py`, `src/tools/vault.py`.

This section covers what a tool does once the dispatcher reaches it: the `TOOL_HANDLERS`
registry and the filesystem, shell, web, document, session, model-interaction, and admin tool
classes, plus the domain functions under `src/tools/` for notes, calendar, contacts, vault,
research, skills, scheduled tasks, the cookbook, and the generic internal-API bridge. The
dispatcher itself (`src/tool_execution.py`), the schemas (`src/tool_schemas.py`), and the
capability and policy tables (`src/tool_capabilities.py`, `src/tool_policy.py`) are assigned to
the three `src-tools-*` sections; the routes these tools call are assigned to the `routes-*` sections. A finding here
is about a tool's own behaviour, not about whether the dispatcher should have allowed the call.

### Coverage

**Read fully:** all 22 files (8,537 lines) — `src/tools/cookbook.py` (1,713),
`src/agent_tools/filesystem_tools.py` (1,140), `src/agent_tools/document_tools.py` (894),
`src/agent_tools/admin_tools.py` (804), `src/tools/system.py` (737), `src/tools/calendar.py`
(568), `src/agent_tools/session_tools.py` (493), `src/agent_tools/subprocess_tools.py` (383),
`src/tools/notes.py` (332), `src/agent_tools/model_interaction_tools.py` (215), `src/tools/vault.py`
(189), `src/agent_tools/web_tools.py` (171), `src/tools/contacts.py` (161),
`src/agent_tools/__init__.py` (158), `src/tools/research.py` (146), `src/agent_tools/bg_job_tools.py`
(98), `src/agent_tools/interaction_tools.py` (94), `src/agent_tools/coding_tools.py` (67),
`src/tools/image.py` (66), `src/tools/search.py` (51), `src/tools/__init__.py` (32),
`src/tools/_common.py` (25). Every cited line was re-read at `2992bf6d368a`.

**Read partially:** `src/tool_execution.py` only at the dispatch branches cited, to establish
which handler runs with which `owner`; its policy logic belongs to `src-tools-capabilities-policy`. `app.py` only at
the bearer-token branch (`:314-337`, `:417-440`) cited in the `manage_tokens` finding; the rest of
the file belongs to `repository-root` and `build-install-deploy`. `routes/chat_routes.py` only at
`:1552-1566`, the privilege-to-disabled-tools mapping that establishes `manage_research`'s
reachability. `src/tool_security.py` only at the blocklist memberships quoted. `src/tool_schemas.py`
only at the two schema entries quoted.

**Not read:** the route implementations these tools call (`routes/gallery/gallery_routes.py`,
`routes/email_routes.py`, `routes/research/research_routes.py`, `routes/cookbook_routes.py`, and
the rest), beyond the lines cited as evidence. Whether a route accepts a tool's request is
established here only where a finding cites it. No test file was read.

#### [SECURITY] The `app_api` path blocklist is bypassed by percent-encoded and dot-segment paths

- **Location:** `src/tools/system.py:669` (the check), with `:675` (the per-method check) and `:537-544` (the list)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `do_app_api` refuses a set of sensitive prefixes before sending the request, using
  the caller-supplied path string:

  ```python
  _APP_API_BLOCKLIST_PREFIXES = (
      "/api/auth", "/api/users", "/api/tokens", "/api/admin",
      "/api/shell", "/api/backup/restore",
  )
  ...
  if any(path.startswith(p) for p in _APP_API_BLOCKLIST_PREFIXES):
      return {"error": f"Path blocked for safety: {path}. ..."}
  ```

  The string that is checked is not the path the server routes. Two transformations happen after
  the check, and either one defeats it.

  The server percent-decodes. `uvicorn/protocols/http/h11_impl.py:205` sets
  `path = unquote(raw_path.decode("ascii"))`, and Starlette routes on that value. Measured against
  the running instance:

  ```
  $ for p in /nope-xyz /%61pi/nope-xyz /%61pi/health /api/health; do
      curl -s -m 3 -o /dev/null -w "$p -> %{http_code}\n" "http://127.0.0.1:7000$p"; done
  /nope-xyz -> 302
  /%61pi/nope-xyz -> 401
  /%61pi/health -> 200
  /api/health -> 200
  ```

  `/nope-xyz` is treated as a non-API path and redirected; `/%61pi/nope-xyz` is treated as the
  API path `/api/nope-xyz` (401, not 302); `/%61pi/health` reaches the health route.

  The client collapses dot segments. `do_app_api` sends with `httpx` (`:706-712`), and httpx
  0.28.1 normalizes the path before the request leaves the process, so no encoding is needed:

  ```
  $ venv/bin/python -c "<httpx.Request('GET', 'http://127.0.0.1:7000' + p).url.raw_path>"
  '/%61pi/tokens'      -> b'/%61pi/tokens'
  '/x/../api/tokens'   -> b'/api/tokens'
  '/./api/tokens'      -> b'/api/tokens'
  '/api/../api/tokens' -> b'/api/tokens'
  ```

  `/x/../api/tokens` does not start with `/api/tokens`, so it passes `:669`, and it is sent as
  `/api/tokens`. The per-method list at `:675` compares the same unnormalized string and is
  bypassed the same way, which includes `POST /api/cookbook/state`, the whole-file overwrite its
  comment records the agent performing once. No request carrying the internal token was sent to
  a blocked route in this pass; the two transformations were measured separately as shown.
- **Impact:** a path written as `/%61pi/tokens` or `/x/../api/tokens` executes with the internal
  tool headers against every class the list refuses in plain form: `/api/users`, `/api/tokens`
  (`routes/api_token_routes.py:130`), `/api/admin`, and `/api/shell`. Three things already bound
  this, and they set the severity:

  - `app_api` is refused for non-admins twice (`src/tool_security.py:65`, and the `_ADMIN_TOOLS`
    check at `src/tool_execution.py:1064`), so the caller is an administrator's agent.
  - `app_api` is registered with `ToolEffect.ADMIN_CHANGE` (`src/tool_capabilities.py:247-260`),
    which is in `POST_EXTERNAL_BLOCKED_EFFECTS` (`:553-565`). Once untrusted content has entered
    the run, `ToolRunSecurityContext.decision_for` (`:654-684`) blocks the call unless the user
    approves that exact action or has granted the chat session approval. A prompt injection
    arrives as untrusted content, so the injected call meets that gate first.
  - An administrator's agent normally also holds `bash`, which reaches the same host under the
    same gate. The list's own comment states its purpose as bounding "accidental account or
    command mistakes", not as a boundary against the administrator.

  What the bypass does remove is the guard in the configurations where it is the only one: an
  administrator who has switched `bash` off for the turn (`routes/chat_routes.py:1492-1493`) or
  listed it in the global `disabled_tools` setting still has `/api/shell` reachable through
  `app_api`, and a run with chat-session approval has no second check. The mechanism does not
  deliver what it claims; it is not an escalation past a boundary the caller did not already hold.
- **Fix:** normalize before checking, and check what will be routed: reject a path containing
  `%`, a `.` or `..` segment, or `//`, then compare path segments instead of string prefixes. A
  test that runs each blocked prefix through the encoded and dot-segment forms belongs beside it.
- **Re-review (2026-10-04):** re-derived in full and lowered from high. The first pass recorded
  the percent-encoding bypass, cited the list (`:537`) as the location, and described a
  prompt-injected token mint without the post-untrusted-content gate. This pass added the
  dot-segment bypass, moved the location to the check, and restated the impact with the three
  mitigations above. The finding was retitled, so its ID changed.

#### [SECURITY] `manage_research` ignores the owner and operates on every user's research files

- **Location:** `src/tools/research.py:17`
- **Severity:** high
- **Disposition:** next
- **Evidence:** the function accepts `owner` and never reads it — the name appears only in the
  signature. All three actions operate on the shared directory without a filter:

  ```python
  async def do_manage_research(content: str, owner: Optional[str] = None) -> Dict:
      ...
      for p in data_dir.glob("*.json"):          # list: every user's file
  ```

  `read` loads `data_dir / f"{rid}.json"` and returns its body (`:48-62`); `delete` unlinks the
  same path (`:64-73`). The saved JSON carries an owner — `src/research_handler.py:628-629` stamps
  it with the comment "SECURITY: stamp owner so route handlers can filter by user" — and the HTTP
  library route enforces that field:

  ```python
  # SECURITY: only show research belonging to this user. Legacy
  # JSONs without an `owner` field are hidden — auth was the only
  # gate before, so every user saw every other user's reports.
  if d.get("owner") != user:
      continue
  ```

  (`routes/research/research_routes.py:381-385`.) `manage_research` is not in
  `NON_ADMIN_BLOCKED_TOOLS` (`src/tool_security.py:42-70`), and no privilege disables it. The
  per-user privilege block at `routes/chat_routes.py:1546-1566` adds tools to `disabled_tools` for
  `can_use_bash`, `can_use_browser`, `can_use_documents`, `can_generate_images` and
  `can_manage_memory`; for `can_use_research` it only clears a flag:

  ```python
  if not _privs.get("can_use_research", True):
      _research_flags["do"] = False
  ```

  `_research_flags` gates the research pre-pass (`:1620`), not the tool. Every user who can use
  agent mode therefore reaches `manage_research`, including one whose research privilege an
  administrator removed. The dispatcher passes the caller's `owner` (`src/tool_execution.py:1246`),
  and the function drops it.
- **Impact:** a user's agent can list every user's research titles and ids, read any report body
  (the report can quote private mail or web content), and delete any report. The delete path is
  destructive and irreversible. The route's own comment shows this leak class was already treated
  as worth fixing once; the tool path was not given the same filter.
- **Fix:** filter the scan by `d.get("owner") == owner`, and on read/delete load the JSON and
  return not-found unless the owner matches, hiding existence as the route does. Hide owner-less
  legacy files from authenticated callers, matching the route.
- **Re-review (2026-10-04):** re-derived in full; high stands. `owner` appears in
  `src/tools/research.py` only in the two signatures and in the `_internal_headers(owner)` call of
  the other function. The preconditions are a second account and nothing else: `list` returns the
  ids that `read` and `delete` take. The first pass said `routes/chat_routes.py:1562` disables the
  tool for callers without `can_use_research`; that line does not touch `disabled_tools`, so the
  evidence above was corrected and the reach is wider than first stated.

#### [BUG] `edit_image` calls four routes that do not exist

- **Location:** `src/tools/image.py:33`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the schema advertises four actions — `"enum": ["upscale", "rembg", "inpaint",
  "harmonize"]` (`src/tool_schemas.py:1042`) — and the implementation posts a JSON body to a
  constructed path:

  ```python
  resp = await client.post(f"{_INTERNAL_BASE}/api/gallery/{action}", json=payload)
  ```

  No POST route matches `/api/gallery/upscale`, `/api/gallery/rembg`, `/api/gallery/inpaint`, or
  `/api/gallery/harmonize`. The gallery router's POST paths are `upload`, the `{image_id}/…`
  sub-routes, `ai-upscale`, `style-transfer`, `albums`, tag jobs, `download-zip`, and the tag
  maintenance routes; background removal, inpaint, and harmonize live under `/api/image/`. None
  of them implements the tool's contract of taking `image_id` JSON and returning a new image id:
  `ai-upscale` reads a multipart `image` file, and the `/api/image/*` handlers expect image and
  mask payloads. The call also omits `_internal_headers(owner)`, so even a matching route would
  fail `require_privilege` in auth-enabled mode. Every action falls into the error branch with
  `data.get("error", f"{action} failed")` on a 404 JSON body.
- **Impact:** the `edit_image` tool is non-functional for all four advertised actions. The model
  either reports a bare failure or retries; no image is ever modified.
- **Fix:** point each action at the real route with the shape it expects (multipart upload for
  `ai-upscale`; image/mask bodies for inpaint, harmonize, and remove-background) and pass
  `_internal_headers(owner)`, or remove the tool from the schema and registry until it is wired.

#### [BUG] `manage_tokens` mints tokens the middleware cannot authenticate

- **Location:** `src/agent_tools/admin_tools.py:466`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `create` builds the raw token without the `ody_` prefix and constructs `ApiToken`
  with no `owner` and no `scopes`:

  ```python
  raw_token = secrets.token_urlsafe(32)
  token_hash = bcrypt.hashpw(raw_token.encode(), bcrypt.gensalt()).decode()
  ...
  t = ApiToken(id=tid, name=name, token_hash=token_hash,
               token_prefix=raw_token[:8], is_active=True, ...)
  ```

  The middleware enters bearer handling only for `Bearer ody_...`
  (`app.py:418`), and the token cache drops any active row whose owner does not resolve to a
  known user (`app.py:323-330`), which includes `owner IS NULL`. The other two construction
  sites set all three fields: `routes/api_token_routes.py:130-141` builds
  `"ody_" + secrets.token_urlsafe(32)` with `owner=owner` and `scopes=scopes_value`, and
  `companion/pairing.py:196` sets them too.
- **Impact:** the tool reports "Created token 'x'" and returns the raw token, but that token is
  rejected as an invalid bearer for lack of the prefix, and the cache would skip it even if the
  prefix were present. An admin who asks the agent to mint an integration token receives a dead
  credential. The `list` and `delete` actions are unscoped, but the tool is admin-blocked
  (`src/tool_security.py:61`), so that part stays inside admin authority.
- **Fix:** build the token exactly as the admin route does — `"ody_" + secrets.token_urlsafe(32)`,
  `owner=owner`, and a `scopes` value — and factor the construction into one helper so the three
  sites cannot drift again.

#### [PERF] `list_models` probes endpoints with synchronous HTTP on the event loop

- **Location:** `src/agent_tools/model_interaction_tools.py:163`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `list_models` is an `async def`, but it calls the synchronous `httpx.get` once per
  enabled endpoint, sequentially, and the handler awaits it on the event loop:

  ```python
  for ep in endpoints:
      ...
      models_url = build_models_url(base)
      if models_url:
          r = httpx.get(models_url, headers=headers, timeout=5)
  ```

  Nothing offloads the call. The same file uses `asyncio.to_thread` for `_resolve_model`
  (`:50`, `:82`), and the surrounding tool layer runs on the loop (the registry handler
  `ListModelsTool.execute` awaits this function directly). `list_models` is not in
  `NON_ADMIN_BLOCKED_TOOLS` (`src/tool_security.py:42-70`).
- **Impact:** each enabled endpoint blocks the entire process for up to 5 seconds; ten configured
  endpoints stall every concurrent request for up to 50 seconds. Any user's agent can trigger it.
- **Fix:** use an `httpx.AsyncClient` (or `asyncio.to_thread`) and probe the endpoints
  concurrently with `asyncio.gather` and a bounded per-endpoint timeout.

#### [BUG] `adopt_served_model`'s endpoint registration always fails on a key mismatch

- **Location:** `src/tools/cookbook.py:1361`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the adopt path calls `do_manage_endpoints` with `endpoint_url`:

  ```python
  ep_result = await do_manage_endpoints(json.dumps({
      "action": "add",
      "name": display_name,
      "endpoint_url": endpoint_url,
      "is_local": False,
  }), owner=owner)
  ```

  `do_manage_endpoints` reads `args.get("base_url", "")` and returns `{"error": "base_url is
  required"}` when it is absent (`src/agent_tools/admin_tools.py:42-44`). Registration is the
  default branch (`add_endpoint = args.get("add_endpoint", True)`), so the output always ends
  with "Endpoint registration skipped: base_url is required".
- **Impact:** an adopted server is tracked in cookbook state but never appears in the endpoint
  list, which is the second half of what the tool's docstring promises. The user must add it
  manually. The adoption and health-check paths still work.
- **Fix:** send `"base_url": endpoint_url`, and drop `is_local`, which `do_manage_endpoints` also
  ignores; or accept `endpoint_url` as an alias in `do_manage_endpoints`.

#### [BUG] `resolve_contact`'s email-history lookup sends no internal tool headers

- **Location:** `src/tools/contacts.py:59`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the CardDAV leg runs in-process with a comment explaining why, but the
  email-history leg goes over HTTP with no headers:

  ```python
  resp = await client.get(f"{_INTERNAL_BASE}/api/email/resolve-contact", params={"name": name})
  ```

  The route depends on `require_owner` (`routes/email_routes.py:4471`), which authenticates the
  request. Every other loopback call in this section passes `_internal_headers(owner)` (for
  example `src/tools/research.py:123`, `src/tools/system.py:698`). The surrounding
  `except Exception: pass` swallows the resulting 401.
- **Impact:** in an auth-enabled deployment, email history silently contributes nothing to
  `resolve_contact`; only CardDAV results are returned. In auth-disabled single-user mode the
  route accepts the unauthenticated call, so the bug is invisible there.
- **Fix:** pass `headers=_internal_headers(owner)` and log the failure instead of swallowing it,
  or call the mail-search helper in-process like the CardDAV leg.

#### [DEAD-CODE] `todowrite` persists a per-session file that nothing reads

- **Location:** `src/agent_tools/coding_tools.py:55`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the tool writes `data/agent_todos/<session>.json`:

  ```python
  path = os.path.join(_TODO_DIR, f"{session_id}.json")
  with open(path, "w", encoding="utf-8") as f:
      json.dump({"todos": normalized}, f, ensure_ascii=False, indent=2)
  ```

  A repository-wide search for `agent_todos` (Python files, excluding `audit/`) returns only this
  module: `_TODO_DIR` is defined here, and nothing reads the file — not the tool, not a route,
  not the frontend's server side. The session id comes from `ctx` or the caller's JSON
  (`args.get("session_id")`), so the path is not an owner-keyed store either.
- **Impact:** none at runtime — the tool's return value carries the list — but the on-disk state
  is write-only. Nothing resumes from it after a restart, and no reader exists to point at it, so
  it presents persistence that does not exist.
- **Fix:** delete the file write, or add the reader that makes it meaningful and key it by owner
  and session.

#### [DEAD-CODE] The facade's `SHELL_TIMEOUT` and `PYTHON_TIMEOUT` are unused and disagree with the shell defaults

- **Location:** `src/agent_tools/__init__.py:75`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the module defines them under a comment that names `src.constants` as the single
  source of truth:

  ```python
  # Constants (re-exported for backward compatibility — single source of truth
  # is src.constants; always prefer importing from there for new code)
  MAX_AGENT_ROUNDS = 50
  SHELL_TIMEOUT = 60
  PYTHON_TIMEOUT = 30
  ```

  `src/constants.py` defines none of the three. `MAX_AGENT_ROUNDS` is imported from here by
  `src/agent_loop.py:68` and `routes/chat_routes.py:2311`; `SHELL_TIMEOUT` and `PYTHON_TIMEOUT`
  have no reader anywhere in the repository. The timeouts the shell tools actually use are
  `DEFAULT_BASH_TIMEOUT` and `DEFAULT_PYTHON_TIMEOUT`, both 3600
  (`src/agent_tools/subprocess_tools.py:12-13`).
- **Impact:** the constants are a trap for the next caller: importing `SHELL_TIMEOUT` expecting
  the tool's timeout yields 60, not 3600, and the comment sends readers to a module that does not
  define it.
- **Fix:** remove the two unused constants and correct the comment, or move `MAX_AGENT_ROUNDS`
  into `src.constants` where the comment claims it lives.

## 14. src: prompt security, secrets, URL safety, limits

### Overview

`src/api_key_manager.py`, `src/auth_helpers.py`, `src/host_docker_access.py`, `src/outbound_fetch.py`, `src/owner_identity.py`, `src/prompt_security.py`, `src/rate_limiter.py`, `src/secret_storage.py`, `src/settings_scrub.py`, `src/tls_overrides.py`, `src/upload_limits.py`, `src/url_safety.py`, `src/url_security.py`.

This section covers the guards the rest of the backend calls into: outbound URL admission,
credential encryption at rest, secret scrubbing for non-admin callers, privilege gating, upload
caps, and the prompt-injection wrapper. The neighbouring `src-agent-tools` and `routes-*` sections
cover the callers; this section covers the guards themselves, so a finding here is about whether a
guard holds, not about whether a caller invokes it.

### Coverage

**Read fully:** `src/api_key_manager.py`, `src/auth_helpers.py`, `src/host_docker_access.py`,
`src/owner_identity.py`, `src/prompt_security.py`, `src/rate_limiter.py`, `src/secret_storage.py`,
`src/settings_scrub.py`, `src/tls_overrides.py`, `src/upload_limits.py`.

**Read partially:** `src/outbound_fetch.py` — the address guard (`_PRIVATE_NETWORKS:23`,
`_is_private_address:36`) and its four call sites (`:83`, `:87`, `:106`, `:114`) were read, plus the
module head; the pinned-transport and capped-fetch implementation below line 44 was **not** read.
`src/url_safety.py` — the classifier `_classify:42`, `_SHARED_ADDRESS_SPACE_V4:34`, and the module
docstring. `src/url_security.py` — the block list and `_blocked_ip:47`.

**Not read:** the remainder of `src/outbound_fetch.py` (roughly 270 lines), and the callers covered
by the `src-agent-tools`, `routes-*`, and `services-search` sections.

One finding below rests on a measured comparison rather than a reading. It was run at this snapshot
against the three classifiers with 19 addresses, and two of the nineteen diverge:

| address | `url_safety` | `url_security` | `outbound_fetch` |
| --- | --- | --- | --- |
| `100.64.0.1` | blocked | blocked | **allowed** |
| `100.127.255.254` | blocked | blocked | **allowed** |

The other seventeen (loopback, RFC 1918, link-local, IPv6 ULA, IPv6 loopback, `0.0.0.0`) are
blocked by all three.

#### [SECURITY] The web fetcher's address guard omits the carrier-grade NAT range the codebase blocks elsewhere

- **Location:** `src/outbound_fetch.py:23`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_PRIVATE_NETWORKS` lists nine ranges and omits `100.64.0.0/10`:

  ```python
  _PRIVATE_NETWORKS = (
      ipaddress.ip_network("0.0.0.0/8"),
      ipaddress.ip_network("10.0.0.0/8"),
      ipaddress.ip_network("127.0.0.0/8"),
      ipaddress.ip_network("169.254.0.0/16"),
      ipaddress.ip_network("172.16.0.0/12"),
      ipaddress.ip_network("192.168.0.0/16"),
      ipaddress.ip_network("::1/128"),
      ipaddress.ip_network("fc00::/7"),
      ipaddress.ip_network("fe80::/10"),
  )
  ```

  The fallback at `:36` cannot cover the gap, because CPython does not classify shared space as
  private — which `src/url_safety.py:28-34` states outright:

  ```python
  # RFC 6598 shared address space (carrier-grade NAT). It is not globally
  # routable, but CPython does not classify it as ``is_private`` (it is "shared",
  # not "private"), so the is_private/is_loopback checks miss it. Reject the range
  # explicitly. This closes exactly the shared-space gap without coupling strict
  # mode to ``is_global``'s broader definition, which has shifted across CPython
  # versions for other special ranges.
  _SHARED_ADDRESS_SPACE_V4 = ipaddress.ip_network("100.64.0.0/10")
  ```

  `src/url_security.py:27` blocks the same range. The fetcher is the third implementation and the
  only one that does not.

  Reachable: `services/search/content.py:29` re-exports this exact function
  (`return _outbound_fetch._is_private_address(addr)`) and `:181` defines `fetch_webpage_content`,
  whose callers include the agent's own fetch tool at `src/agent_tools/web_tools.py:83,124`,
  `src/deep_research.py:616`, and `src/chat_processor.py:466`.

- **Impact:** A URL in `100.64.0.0/10` is fetched where an RFC 1918 URL is refused. In a Tailscale
  or CGNAT deployment that range is the tailnet, so a fetch that reaches the agent's web tool can
  read whatever answers HTTP there and return the body to the model. The agent's web tool takes its
  URL from the model, whose context the project's own `THREAT_MODEL.md` treats as containing
  untrusted content, so the guard is being bypassed on the path it exists to protect. Severity is
  medium rather than high because the consequence is bounded by what answers HTTP in shared space,
  and because the repository does not show whether any deployment occupies that range.
- **Fix:** Add `ipaddress.ip_network("100.64.0.0/10")` to `_PRIVATE_NETWORKS`. The durable fix is
  the `DUP` finding below — have this module call `url_safety._classify` so the three lists cannot
  drift again.

#### [ERROR-HANDLING] A privilege check skips itself when the privilege lookup raises

- **Location:** `src/auth_helpers.py:178`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `require_privilege` catches every exception from `get_privileges` and returns the
  user unchecked:

  ```python
  try:
      privs = auth_mgr.get_privileges(user) or {}
  except Exception:
      return user
  if not isinstance(privs, dict):
      privs = {}
  ```

  `core/auth.py:378-385` merges the stored privileges over the defaults:

  ```python
  stored = user.get("privileges", {})
  return {**DEFAULT_PRIVILEGES, **stored}
  ```

  A non-mapping `privileges` value raises out of that merge. Measured:

  ```
  $ python3 -c "D={'allow_shell': True}; print({**D, **[]})"
  TypeError: 'list' object is not a mapping
  ```

  So a stored `"privileges": []` — a hand-edited or corrupted `auth.json` — makes every
  `require_privilege` call for that user return early and permit the action. Note that the
  `isinstance(privs, dict)` guard on the line *after* the `except` shows the method was already
  expected to be able to return a non-dict; the `except` above it pre-empts that check.

- **Impact:** An authorization check fails open. The user is granted the privilege the check exists
  to deny. Today the trigger is a malformed `auth.json`; the blanket `except Exception` means any
  future exception added to `get_privileges` — a database read, a schema change — silently converts
  a denied action into a permitted one, with no log line.
- **Fix:** Drop the `except Exception` so the failure surfaces as a 500, or catch narrowly and
  raise `HTTPException(403)`. If the lookup must degrade, log at `error` and deny.
- **Re-review (2026-10-04):** lowered from medium. `AuthManager.set_privileges` (`core/auth.py:387-401`) is the only writer of
  the field and always stores the dict returned by `get_privileges`, and a non-object request body
  raises at `privileges.items()` before anything is stored. The trigger is therefore a hand-edited
  or corrupted `auth.json`: one more mistake has to happen before the check fails open.


#### [RACE] Fernet keys are generated without a lock, so concurrent first use discards a key

- **Location:** `src/secret_storage.py:37`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_load_or_create_key` checks for the key file, then generates and writes it, with no
  lock and no exclusive-create:

  ```python
  def _load_or_create_key() -> bytes:
      if _KEY_PATH.exists():
          return _KEY_PATH.read_bytes()
      _KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
      key = Fernet.generate_key()
      _KEY_PATH.write_bytes(key)
      safe_chmod(_KEY_PATH, 0o600)
  ```

  `_get_fernet` guards only the module global (`if _fernet is None`), which does not cover the
  file, and `_load_or_create_key` performs file I/O that releases the GIL, so two callers can be
  inside it at once. Measured with eight concurrent callers on a fresh path:

  ```
  $ venv/bin/python -c "<8 threads, barrier-synchronised, on an empty key path>"
  concurrent callers      : 8
  distinct keys returned  : 2
  returned the on-disk key: 6 of 8
  ```

  Two of the eight callers walked away holding a key that was no longer on disk. `src/api_key_manager.py:17`
  has the same shape in `get_or_create_key`, and it is called on *every* encrypt and decrypt
  (`encrypt_api_key` and `decrypt_api_key` each call it), so the window is re-entered constantly
  rather than once at startup.

- **Impact:** Data encrypted with the discarded key is unrecoverable. `secret_storage` backs the
  IMAP/SMTP passwords and OAuth tokens (`core/database.py:151`, `:422`, `:2330-2389`), and
  `api_key_manager` backs every stored provider credential; `decrypt` returns `""` on failure by
  design, so the loss appears as an account silently reverting to "unconfigured". Two concurrent
  requests during a fresh install are enough. The first-use race is the reachable one — after the
  file exists, both paths read it.
- **Fix:** Serialise generation behind a module lock and create the file exclusively, retrying the
  read on `FileExistsError`:

  ```python
  try:
      fd = os.open(_KEY_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
  except FileExistsError:
      return _KEY_PATH.read_bytes()
  ```

  That also closes the permission window in which the key exists with the process umask before
  `safe_chmod` runs — the same window `src/api_key_manager.py:21-24` already acknowledges for
  pre-existing files.
- **Re-review (2026-10-04):** lowered from medium. The window is one check-then-write per install: it exists only until
  `data/.app_key` is first created, and `_get_fernet` caches the result for the life of the
  process. The measurement above used eight barrier-synchronised threads; no unsynchronised run was
  made, and this pass did not find a shipped flow that issues two first-ever encrypts together. The
  consequence is unchanged and is worse than one lost secret when the losing thread assigns
  `_fernet` last: the process then encrypts with a key that is not on disk until it restarts. The
  `api_key_manager` copy is not reachable in production, because that store has no writer (see
  the `initialize_managers` finding in `src-platform`).


#### [DUP] Three private-address classifiers disagree, and only the strictest is tested

- **Location:** `src/outbound_fetch.py:36`
- **Severity:** low
- **Disposition:** next
- **Evidence:** Three modules independently decide whether an address is safe to contact:

  | module | function | mechanism |
  | --- | --- | --- |
  | `src/url_safety.py:42` | `_classify` | explicit range list, plus `_SHARED_ADDRESS_SPACE_V4:54` |
  | `src/url_security.py:47` | `_blocked_ip` | explicit range list, includes `100.64.0.0/10:27` |
  | `src/outbound_fetch.py:36` | `_is_private_address` | nine ranges, then CPython's `is_private`/`is_reserved` |

  Measured over 19 addresses, two diverge (the table under Coverage). `outbound_fetch` is the
  permissive outlier, and it is the one on the web-fetch path.

- **Impact:** This is the mechanism behind the `SECURITY` finding above: a policy expressed three
  times drifts, and the drift is invisible because no test compares the three. Each list is
  individually reasonable, so a reader auditing one of them concludes the range is covered.
- **Fix:** Keep one list. Have `outbound_fetch._is_private_address` delegate to
  `url_safety._classify`, and add a test that runs a shared address corpus through all three so a
  future edit to any one of them fails the suite.
- **Re-review (2026-10-04):** lowered from medium. The one divergence with a consequence is the carrier-grade NAT range, and
  that is already counted as the `SECURITY` finding above. What remains here is the duplication,
  which is a hazard for the next edit and not a second defect.


#### [UNDOCUMENTED] Five environment variables gate one SSRF policy and none appears in `.env.example`

- **Location:** `src/url_safety.py:17`
- **Severity:** low
- **Disposition:** next
- **Evidence:** One `block_private` parameter is driven by five different variables, all defaulting
  to off:

  | variable | call site | documented in |
  | --- | --- | --- |
  | `EMBEDDING_BLOCK_PRIVATE_IPS` | `routes/embedding_routes.py:269` | the `url_safety` docstring only |
  | `IMAGE_BLOCK_PRIVATE_IPS` | `routes/gallery/gallery_routes.py:337,1274,1538`, `src/ai_interaction.py:1151,1433` | nowhere |
  | `CARDDAV_BLOCK_PRIVATE_IPS` | `routes/contacts/contacts_routes.py:70` | nowhere |
  | `REMINDER_WEBHOOK_BLOCK_PRIVATE_IPS` | `routes/note/note_routes.py:454,495` | `specs/calendar-tasks-notes.md:106` |
  | `INTEGRATION_API_BLOCK_PRIVATE_IPS` | `src/integrations.py:563` | `specs/auth-security.md:133`, `specs/integrations.md:92` |

  ```
  $ for v in EMBEDDING_ CARDDAV_ IMAGE_ REMINDER_WEBHOOK_ INTEGRATION_API_; do
  >   grep -c "${v}BLOCK_PRIVATE_IPS" .env.example; done
  0
  0
  0
  0
  0
  ```

  The `url_safety` docstring names one variable as the knob for the whole policy:

  ```
  For exposed multi-tenant deployments, set ``EMBEDDING_BLOCK_PRIVATE_IPS=true`` to
  ```

  That variable governs only the embedding route. `CARDDAV_BLOCK_PRIVATE_IPS` and
  `IMAGE_BLOCK_PRIVATE_IPS` appear nowhere outside their own call sites.

- **Impact:** An operator hardening a deployment from `.env.example` — the file the project
  presents as the configuration surface — cannot see any of these switches, and the docstring
  points at one that covers a fraction of the paths. The default for all five is `false`, so the
  LAN-capable behaviour is what a deployment gets unless the operator reads the source. The
  gallery and embedding paths are the exposed ones, since they fetch user-supplied URLs.
- **Fix:** Add all five to `.env.example` with their defaults and a one-line explanation, and
  correct the `url_safety` docstring to name all five or to describe the policy without singling
  out one variable.
- **Re-review (2026-10-04):** lowered from medium. Every switch does what its call site says, the off default is the
  documented local-first design (`src/url_safety.py:7-10`), and two of the five are documented in
  `specs/`. The defect is the missing `.env.example` entries and one docstring sentence that
  overstates what `EMBEDDING_BLOCK_PRIVATE_IPS` covers.


#### [SECURITY] Secret scrubbing stops masking when a secret-shaped key holds a container

- **Location:** `src/settings_scrub.py:48`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `_scrub_value` tests the secret-shaped name only against the key at the level it is
  visiting. When a secret-shaped key holds a dict, the value fails the `isinstance(v, str)` test and
  the function recurses with the *parent* name, which the recursive call then ignores:

  ```python
  if isinstance(value, dict):
      return {
          k: ("" if (is_secret_key(k) and isinstance(v, str) and v)
              else _scrub_value(k, v))
          for k, v in value.items()
      }
  ```

  Measured:

  ```
  documented case   : {'email_account': {'smtp_password': ''}}
  nested dict value : {'smtp_password': {'nested': 'real-secret-2'}}
  ```

  The first line is the case the docstring describes and it works. In the second, the secret-shaped
  key `smtp_password` is dropped on the way down and its contents are returned in the clear.

- **Impact:** `/api/auth/settings` is auth-exempt and serves non-admin and unauthenticated callers
  (`src/settings_scrub.py` docstring), so this is a disclosure path. It is `low` and not higher
  because the trigger is a shape — a secret stored as a dict under a secret-named key — and I did
  not find that shape in the settings the app builds today; the shapes I checked nest the other way
  (`email_account` → `smtp_password`, where the inner key carries the secret-shaped name and is
  masked correctly). It is a live hazard because the recursion looks correct on inspection and the
  next nested credential silently defeats it.
- **Fix:** Carry the secret-shaped decision down instead of re-testing at each level — blank the
  whole subtree when the key is secret-shaped and the value is not a plain string, or pass the
  parent name into the recursive call and treat it as secret-shaped for all descendants.

#### [HARDCODE] The API-key store builds its paths instead of using `src/constants.py`

- **Location:** `src/api_key_manager.py:14`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** Both paths are assembled locally from the injected `data_dir`:

  ```python
  self.api_keys_file = os.path.join(data_dir, "api_keys.json")
  self.key_file = os.path.join(data_dir, ".key")
  ```

  `CONTRIBUTING.md:101` names this exact pattern as the thing not to do:

  > Every persisted file and directory has a named constant in `src/constants.py` ... Import and
  > use that named constant; do not re-derive the path locally with `os.path.join(DATA_DIR, "x.json")`
  > or `DATA_DIR / "x.json"`.

  `src/constants.py` has `APP_KEY_FILE` for the sibling store at `src/secret_storage.py:33` and no
  constant for either file here.

- **Impact:** Low on its own — the paths work. The reason it is recorded is that `DATA_DIR` is the
  single reader of `ODYSSEUS_DATA_DIR`, and these two literals are the only persisted paths in the
  section that bypass it, so a deployment that relocates its data directory has two files whose
  location is decided by whatever `data_dir` the caller passes rather than by the constant every
  other store uses. It also puts the API-key store's key file (`.key`) and the shared secret store's
  key file (`.app_key`) on separately-derived paths, which is what makes the two-key situation in
  the `RACE` finding above hard to see.
- **Fix:** Add `API_KEYS_FILE` and `API_KEY_FILE` to `src/constants.py` and import them, matching
  `APP_KEY_FILE`.

## 15. src: chat processing, context and sessions

### Overview

The non-route half of the chat pipeline. `src/chat_handler.py` preprocesses a turn (uploads,
YouTube transcripts, image/vision handling), `src/chat_processor.py` assembles the memory, RAG,
web and skills context preface, `src/context_compactor.py` decides what survives when the
conversation approaches the model's window and `src/context_budget.py` computes the agent's
input budget, `src/request_models.py` holds the pydantic bodies, `src/session_search.py` and
`src/topic_analyzer.py` read transcripts across sessions, `src/session_actions.py` and
`src/session_image_cleanup.py` tidy and delete session data, `src/chat_helpers.py` is the
URL/validation helper set, and `src/assistant_log.py` is the activity-log shim.

The boundary: the routes that call these modules (`routes/chat_routes.py`,
`routes/session_routes.py`, `routes/chat_helpers.py`) are `routes-chat-session`; the session
store, its cache and the message writes are `core/session_manager.py` / `core/models.py`, in
`core-auth-session`, whose findings (the global 100-row sidebar cache, the no-op
`save_sessions`) this section relies on rather than restates; the middleware that stamps the
caller is `core-auth-session` and `build-install-deploy`; the LLM transport and model-window
lookup (`src/llm_core.py`, `src/model_context.py`, `src/endpoint_resolver.py`) are
`src-llm-core`; the upload resolver is `src-documents`; the tool dispatcher that calls
`search_chats` is `src-tools-parse-exec`; and the scheduler that fires the tidy action is
`src-research-scheduling` / `src-tools-builtin-actions`. This section covers what these modules
do to a conversation once a route hands it over — what compaction keeps, what they read or
delete and on whose behalf, and what runs on the event loop — not whether the routes, the
store, or the transport are themselves correct.

### Coverage

**Read fully:** all 11 assigned files (2,840 lines): `src/context_compactor.py` (527),
`src/chat_processor.py` (525), `src/session_search.py` (369), `src/chat_handler.py` (352),
`src/chat_helpers.py` (316), `src/session_actions.py` (250), `src/request_models.py` (137),
`src/session_image_cleanup.py` (130), `src/topic_analyzer.py` (104), `src/context_budget.py`
(82), `src/assistant_log.py` (48). Line numbers refer to `2992bf6d368a`.

**Read partially:** the boundary code the findings rest on — `core/session_manager.py` at
`get_session` / `sync_session_metadata` / `_touch_session` (`:421-539`), `_persist_message`
(`:244-255`), `replace_messages` (`:352-412`) and `delete_session` (`:587-627`);
`core/models.py` in full (191 lines — `ChatMessage`, `Session`, `get_context_messages`);
`routes/chat_helpers.py` at `build_chat_context` (`:588-830`), `preprocess` (`:328-350`) and
`add_user_message` (`:409-418`); `routes/chat_routes.py` at the chat-endpoint context build
(`:780-870`) and `GET /api/search` (`:2696-2717`); `routes/session_routes.py` at
`_verify_session_owner` (`:104-131`) and the auto-sort route's Phase 1 (`:1120-1145`);
`src/agent_loop.py` at the compaction call sites (`:4276-4300`, `:4827-4840`) and the
`_protected` context messages (`:2430-2455`, `:2515-2530`); `src/llm_core.py` at
`_sanitize_llm_messages` (`:1673-1740`) and the response parse in both call paths (`:2061`,
`:2436-2465`); `src/document_processor.py` at `analyze_image_with_vl_result` (`:333-393`);
`src/task_scheduler.py` at `_execute_action` (`:1242-1275`), `HOUSEKEEPING_DEFAULTS`
(`:251-263`) and `ensure_defaults` (`:2313-2340`); `src/builtin_actions.py` at
`action_tidy_sessions` (`:433-446`); `routes/task/task_routes.py` at `_owner` and the create
handler (`:301-302`, `:453`, `:528-545`); `src/prompt_security.py` at
`untrusted_context_message` (`:64-96`); `src/tool_execution.py:1151`; `app.py` at the
assistant-log wiring (`:589-590`), the housekeeping seeding (`:1155-1177`) and the uvicorn
launch (`:1306`).

**Not read:** the rest of `routes/chat_routes.py` and `routes/session_routes.py` (assigned to
`routes-chat-session`); `core/middleware.py` and the auth middleware in `app.py` (assigned to
`core-auth-session` / `build-install-deploy`) — the findings here rest on the
`effective_user` / `_verify_session_owner` call sites quoted, not on the middleware; the LLM
transport beyond the cited lines (`src/model_context.py`, `src/endpoint_resolver.py`);
`src/upload_handler.py` and the document pipeline behind `build_user_content` (assigned to
`src-documents`); the tool dispatcher beyond the one `do_search_chats` call site; the front
end; and every other `src-*` module.

**Checks run:** five throwaway probes under `/tmp` (not part of the target tree), each quoted
in the finding it settles — `maybe_compact` with a realistic preface and an 11-message history;
the same call with the summary model returning `""`; a 1.0 s blocking VL call against a ticker
task on the same loop; `search_session_messages` against a 2,000-message in-memory DB with a
statement-counting event listener, plus `EXPLAIN QUERY PLAN` for its LIKE leg; and
`run_auto_sort("")` against a temp app DB holding one empty session for each of two owners.
Also greps for the unused symbols cited in the dead-code finding and for the callers of
`run_auto_sort`, `search_session_messages`, `maybe_compact`, `model_supports_vision` and
`_sanitize_tool_messages`. Suites: `ls tests | grep -iE
'chat|session|context|topic|compactor|request_models|assistant_log'` yields 64 files; running
them gives **1 failed, 523 passed**. The failure is the order-dependent pair already documented
in `routes-chat-session` (`tests/test_session_list_owner_scope.py` passes alone — 2 passed; with
`tests/test_archived_sessions_model_filter.py` ahead of it, 1 failed / 4 passed). The
compactor's own suites outside that glob (`tests/test_compaction_summary_failure.py`,
`tests/test_context_compactor.py`, `tests/test_context_compactor_nonstring.py`,
`tests/test_context_budget.py`) are **41 passed**, and the neighbouring budget suites
(`tests/test_compact_truncate_tool_call_args.py`, `tests/test_agent_tool_budget_nonnumeric.py`,
`tests/test_budget_auto_sentinel.py`, `tests/test_manage_settings_token_budget.py`,
`tests/test_history_compact_tool_calls.py`, `tests/test_document_processor_attachment_budget.py`)
are **25 passed**.

#### [BUG] Compaction rewrites the wrong slice of the session history, dropping messages it never summarized

- **Location:** `src/context_compactor.py:504-518` (with `:362`, `:432`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `maybe_compact` splits the system-stripped conversation at its midpoint and
  hands `_update_session_history` that index together with the request's system-message count:

  ```python
  split_point = len(convo_msgs) // 2                          # :362
  ...
  if persist:
      _update_session_history(session, split_point, summary, system_msg_count=len(system_msgs))  # :432
  ```

  `system_msgs` is counted over the request's message list, which starts with the preface
  `build_context_preface` builds: the untrusted-context policy message is appended
  unconditionally (`src/chat_processor.py:305-308`) and memory/RAG/web/URL/skills context add
  more. None of those are in `session.history` — the chat path only ever appends the user turn
  (`routes/chat_helpers.py:416`) and the model's reply — yet `_update_session_history` uses the
  count as an offset into it:

  ```python
  effective_split = system_msg_count + split_point            # :504
  system_prefix = list(session.history[:system_msg_count])    # :510
  recent_history = session.history[effective_split:]          # :511
  new_history = system_prefix + [summary_msg] + recent_history
  ```

  Measured with a throwaway probe (`venv/bin/python /tmp/probe_compaction_slice_p1.py`: one
  preface system message — the minimum — an 11-message history and a stubbed summary call):

  ```
  was_compacted : True
  history before: ['m0-…', 'm1-…', 'm2-…', 'm3-…', 'm4-…', 'm5-…', 'm6-…', 'm7-…', 'm8-…', 'm9-…', 'm10-curr']
  history after : ['m0-…', '[Convers…', 'm7-…', 'm8-…', 'm9-…', 'm10-curr']
  summarized    : m0..m5  (convo_msgs[:split_point])
  turns dropped from session.history     : ['m1-…', 'm2-…', 'm3-…', 'm4-…', 'm5-…', 'm6-…']
  ```

  `m1..m5` were summarized; `m6` was not — it survives only in the request built for this turn,
  and `replace_messages` deletes and re-inserts the stored rows
  (`core/session_manager.py:380-400`), so it is gone from the transcript. `m0` is kept verbatim
  *and* summarized, so it is duplicated. The same probe with three preface system messages drops
  `m3..m8`; the number of never-summarized turns lost equals the number of system messages in
  the preface. The agent path passes `session=None` and applies the plan later through
  `apply_compaction_state_for_session` (`:472-487`), which calls the same function with the same
  offset.
- **Impact:** every compaction permanently drops as many turns from the stored transcript as the
  request had system messages (one at minimum, two to four in the ordinary case) and keeps the
  oldest few twice. The user reloading the chat sees messages missing from the middle of the
  conversation, and the model on the next turn never received a summary covering them. Nothing
  logs the dropped range and `was_compacted=True` is reported, so the loss is silent.
  `tests/test_context_compactor.py` cannot catch it: it stubs `_update_session_history` out.
- **Fix:** compute the offset from the list being rewritten, not from the request — the number
  of leading `system` entries of `session.history`, or have `maybe_compact` return the count of
  history messages it summarized and slice `session.history` by that. A test that builds a real
  `Session`, calls `maybe_compact` with a preface, and asserts that the messages it summarized
  are the messages that left the history would pin it.

#### [ERROR-HANDLING] An empty compaction summary is accepted, replacing the older half with a bare header

- **Location:** `src/context_compactor.py:410-432`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `llm_call_async` returns the completion text and does not raise for a 200 with
  empty content — `response = content or msg.get("reasoning_content") or ""`
  (`src/llm_core.py:2461`; the sync path has the same line at `:2061`) — and it caches that empty
  string (`_set_cached_response`, `:2462-2466`). `maybe_compact` only strips a leading title
  before using it:

  ```python
  summary = normalize_compaction_summary(summary)      # :410
  summary_msg = {
      "role": "system",
      "content": f"[Conversation summary — earlier messages were compacted]\n{summary}",   # :412-415
  }
  ```

  Measured with the summary call returning `""` (`venv/bin/python /tmp/probe_empty_summary.py`,
  the shape of `tests/test_compaction_summary_failure.py` with an empty return instead of a
  raise):

  ```
  was_compacted: True
  history before: ['m0-…', 'm1-…', …, 'm10-curr']
  history after : ['m0-…', '[Conversation summary]\n', 'm7-…', 'm8-…', 'm9-…', 'm10-curr']
  summary message content: '[Conversation summary]\n'
  ```

  The older half is gone and its replacement is a header with nothing under it. The `except`
  branch twenty lines above states the contract this breaks — "Degrade gracefully: keep the
  conversation intact rather than silently dropping the older half" (`:406-407`) — and the suite
  that pins that branch only exercises a summary call that raises.
- **Impact:** a compaction/utility model that returns an empty completion (a truncated
  reasoning-model reply, an empty `choices[0].message.content`, a proxy that sends
  `content: null`) silently destroys the older half of the conversation while reporting success.
  Because the empty response is cached under the request's cache key, a retry of the same
  compaction returns the empty string again.
- **Fix:** treat an empty summary as a failure before any rewrite —
  `if not summary.strip(): return messages, context_length, False` — so the caller keeps the
  conversation and `trim_for_context` handles the length, as the raising path already does.

#### [PERF] `preprocess_message` runs the vision-model call inline on the event loop while offloading the vision probe beside it

- **Location:** `src/chat_handler.py:264` (with `:209`, `:217`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the async preprocessor offloads the LM Studio capability probe and then calls
  the vision description synchronously:

  ```python
  main_is_vision = await asyncio.to_thread(                    # :209
      model_supports_vision,
      sess.model or "",
      getattr(sess, "endpoint_url", "") or "",
  )
  ...
  if not vl_desc:
      vl_result = analyze_image_with_vl_result(file_info["path"], owner=owner)   # :264
  ```

  `analyze_image_with_vl_result` is a plain `def` (`src/document_processor.py:333`) that runs a
  synchronous `llm_call(..., timeout=120)` per candidate endpoint (`:375`), and its caller is
  awaited directly: `routes/chat_helpers.py:336` awaits `chat_handler.preprocess_message`, from
  `build_chat_context` (`:643`), which the async chat handlers await. Measured with the VL call
  replaced by a 1.0 s blocking sleep and a ticker task on the same loop
  (`venv/bin/python /tmp/probe_vl_blocking.py`):

  ```
  inline analyze_image_with_vl_result          elapsed=1.00s  ticker iterations=1
  VL call actually made: ['/tmp/photo.png']
  baseline: same 1.0s via asyncio.to_thread    elapsed=1.00s  ticker iterations=99
  ```

  The loop is held for the whole call, and the call sits inside the per-attachment loop
  (`:217-282`), so a turn with several images pays it once per image. The same path also writes
  the description to the gallery with a synchronous DB round-trip
  (`_sync_upload_vision_to_gallery`, `:32-59`).
- **Impact:** attaching an image to a turn whose main model is text-only freezes the process for
  the duration of the VL call — up to the 120 s timeout when the vision endpoint is cold or
  slow — on the single uvicorn worker the app starts (`app.py:1306`). During that window no
  other session's stream advances and `/api/health` does not answer. `routes-chat-session`
  reports the same class for `build_context_preface` and the ChatGPT catalog fetch; this is a
  third site, in a different file, with the largest timeout of the three.
- **Fix:** `vl_result = await asyncio.to_thread(analyze_image_with_vl_result, file_info["path"],
  owner=owner)`, and offload the gallery sync the same way.

#### [PERF] Every transcript search runs both search legs and builds context for candidate hits it then discards

- **Location:** `src/session_search.py:336-355` (with `:171`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** when the FTS leg returns anything, the LIKE leg runs anyway, and each leg
  materializes full results — including two context queries per hit — before the merge truncates
  to `limit`:

  ```python
  if fts_results is not None:
      like_results = _search_like(                     # :337
          db, query, limit, owner, include_archived, context_messages,
          restrict_owner, include_legacy_owner,
      )
      merged: list[SessionSearchResult] = []
      seen: set[str] = set()
      for result in [*fts_results, *like_results]:     # :349
          ...
          if len(merged) >= limit:
              break
  ```

  `_rows_to_results` runs `_context_for_message(db, msg, context_messages)` for every hit
  (`:171`), which issues one query for the messages before the hit and one for the messages
  after it (`:143-165`). Measured with a statement-counting event listener on an in-memory DB
  holding 2,000 messages across five sessions (`venv/bin/python
  /tmp/probe_session_search_queries.py`):

  ```
  messages in db            : 2000
  results returned          : 20
  SQL statements for 1 call : 84
  elapsed                   : 25 ms
  statement mix             : {'SELECT 1': 1, 'SELECT m.id': 1, 'SELECT chat_messages.id': 82}
  ```

  82 of the 84 statements are context queries for 41 candidate hits (21 from the FTS leg, 20
  from the LIKE leg) of which 20 are returned. The LIKE leg cannot use an index for a
  leading-wildcard match — `EXPLAIN QUERY PLAN` for that query (`/tmp/probe_like_plan.py`) is
  `SEARCH sessions USING INDEX ix_sessions_owner (owner=?)` then `SEARCH chat_messages USING
  INDEX ix_messages_session_time (session_id=?)`, i.e. a `lower(content) LIKE lower('%q%')`
  comparison on every message of each of the caller's non-archived sessions. Both callers run it
  inline: the async `GET /api/search` (`routes/chat_routes.py:2707`) and the agent's
  `search_chats` tool (`src/tool_execution.py:1151`).
- **Impact:** each search costs roughly four times the statements it needs and a per-message scan
  of the caller's transcripts, on the event loop of a single-worker process, for results that are
  then dropped. At the measured 2,000-message scale the whole call is 25 ms; the scan grows with
  the transcript while the discarded queries do not shrink.
- **Fix:** run the LIKE leg only when the FTS leg returned fewer than `limit` rows, and fetch
  context after the merge for the returned page only (or batch the before/after queries per
  session).

#### [BUG] The tidy action deletes session rows behind the session manager's back, so a chat that is still open loses its next turn

- **Location:** `src/session_actions.py:89-91` and `:136-140`
- **Severity:** low
- **Disposition:** next
- **Evidence:** both delete branches call `db.delete(row)` and commit without going through
  `SessionManager.delete_session`:

  ```python
  if (row.name or "").strip() == "Incognito":
      deleted_throwaway += 1
      db.delete(row)                 # :91 — no age check at all
      continue
  ...
  if should_delete:
      db.delete(row)                 # :137
  ...
  if deleted_empty or deleted_throwaway:
      db.commit()                    # :140
  ```

  The in-memory session survives, so the next turn is still accepted —
  `_verify_session_owner` allows an in-memory ghost the caller owns
  (`routes/session_routes.py:125-129`) — but the write is dropped:

  ```python
  if db_session is None:
      # A stream/tool callback can outlive a session delete. ...
      self.sessions.pop(session_id, None)
      logger.warning("Dropping message for deleted session %s", session_id)
      return
  ```
  (`core/session_manager.py:249-255`)

  The path is reachable from the shipped housekeeping task: `tidy_sessions` is seeded for every
  owner and is not ship-paused (`src/task_scheduler.py:252`, `ensure_defaults`), fires every
  five `session_created` events, and calls
  `run_auto_sort(owner, skip_llm=True, delete_throwaway=False)` (`src/builtin_actions.py:441`).
  An empty session is deleted once it is ten minutes old and no timestamp is newer
  (`_FRESH_EMPTY_SESSION_GRACE`, `:25`; `is_session_recently_active`, `:42-52`), so an open but
  idle empty chat is eligible. The sibling implementation in the route does what this one
  omits — after the same `db.delete(row)` it calls `session_manager.delete_session(row.id)`
  (`routes/session_routes.py:1136-1141`).
- **Impact:** a chat left open and idle for ten minutes loses the next exchange: the reply
  streams, nothing is written to the transcript, and the turn after that answers 404 because the
  cache entry was evicted on the dropped write. The direct delete also skips the generated-image
  cleanup and document detach that `delete_session` performs
  (`core/session_manager.py:591-600`), so a deleted throwaway chat's images stay active in the
  gallery. An `Incognito`-named row is deleted with no age check (the shipped browser names its
  incognito session `Nobody`, `static/js/sessions.js:2284`, which this branch does not match).
- **Fix:** route both branches through the manager when one is available
  (`manager.delete_session(row.id)`), keeping the direct delete as the fallback, so the cache
  entry, the linked images and the documents follow the same path as `DELETE /api/session/{id}`.

#### [FOOTGUN] `run_auto_sort` treats a missing owner as "every owner"

- **Location:** `src/session_actions.py:78-81` (with `:145-148`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** an empty or `None` owner removes the filter instead of matching nothing, in both
  the delete pass and the folder-assignment pass:

  ```python
  rows = db.query(DbSession).filter(
      DbSession.archived == False,
      *([DbSession.owner == owner] if owner else []),
  ).all()
  ```

  The one production caller forwards a column that is nullable and empty in the documented
  no-login mode: `action_tidy_sessions(owner, ...)` (`src/builtin_actions.py:433`) is invoked
  with `kwargs = {"owner": task.owner, ...}` (`src/task_scheduler.py:1256`),
  `ScheduledTask.owner` is `Column(String, nullable=True)` (`core/database.py:735`), and the
  create route fills it from `get_current_user`, which is `None` when auth is disabled
  (`routes/task/task_routes.py:301-302`, `:530`). Measured against a temp app DB holding one
  90-day-old empty session for each of two owners
  (`venv/bin/python /tmp/probe_auto_sort_owner.py`):

  ```
  sessions before: ['alice', 'bob']
  run_auto_sort('') -> Cleaned 2 sessions. Too few remaining to sort.
  sessions after : []
  ```

  The docstring says the opposite of what the code does with an empty owner — "owner: user whose
  sessions to process" (`:60`) — and this is a delete path. No current caller passes an empty
  owner in the shipped configuration (`ensure_defaults` is called per username), so today the
  unfiltered branch is reached only when a task row has a null owner.
- **Impact:** none today in a correctly seeded instance. The next caller that forgets the owner,
  or a task row created in the no-login mode described above, turns this into a cross-owner
  delete and folder rewrite over every account's sessions — including the `is_important` guard
  and the per-owner grace that the filtered path applies to one user's rows.
- **Fix:** fail closed — `if not owner: return "No owner; nothing to clean."` before the query,
  and keep the filter unconditional so an empty owner matches no rows.

#### [DEAD-CODE] The section's files carry public API nothing calls, including a whole shim module

- **Location:** `src/assistant_log.py:19-48` (with `src/chat_handler.py:115`, `:326`,
  `src/chat_helpers.py:188`, `src/request_models.py:30`, `:51`, `:107`, `:113`, `:131`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** greps over `src/ routes/ core/ services/ app.py` (tests excluded) return only the
  definitions:

  ```
  $ grep -rn "\btrim_history_if_needed\b" --include=*.py src/ routes/ core/ services/ app.py
  src/chat_handler.py:326:    def trim_history_if_needed(self, session):
  $ grep -rn "\b_LEGACY_TAG_RE\b" ...        → src/assistant_log.py:31:_LEGACY_TAG_RE = re.compile(...)
  $ grep -rn "\bSessionCreateRequest\b" ...  → src/request_models.py:30:class SessionCreateRequest(BaseModel):
  $ grep -rn "\bvalidate_file_upload\b" ...  → src/chat_helpers.py:188:def validate_file_upload(file: UploadFile) -> UploadFile:
  ```

  and the same for `enhance_message_if_needed` (`src/chat_handler.py:115`),
  `MemoryUpdateRequest`, `ErrorResponse`, `UploadResponse` and `MemoryResponse`. `MAX_CONTEXT_MESSAGES`
  (`src/constants.py:87`) is read only by the dead `trim_history_if_needed`. In
  `src/assistant_log.py` the module global is assigned by `set_session_manager` (`:19-24`, called
  from `app.py:589-590`) and never read, the `_LEGACY_TAG_RE` regex has no reader, and
  `log_to_assistant` logs at DEBUG and returns (`:47-48`) while four production call sites still
  call it (`src/task_scheduler.py:1236`, `src/tools/vault.py:126`,
  `routes/cookbook_routes.py:1395`, `:2820`) — the no-op is deliberate per its docstring, but the
  callers read as if the assistant's activity feed receives the text.
- **Impact:** a reader or a new caller can pick up `trim_history_if_needed` (which slices
  `session.history` without the tool-pairing repair `_sanitize_tool_messages` performs for
  `trim_for_context`), `validate_file_upload`, or a request model no route validates against, and
  get behaviour the app never exercised. The assistant-log shim makes four call sites look like
  they notify the user when the text reaches only the debug log.
- **Fix:** delete the unused symbols and the shim module together with its `app.py` wiring and
  the four call sites, or mark them deprecated in place. `trim_history_if_needed` should not be
  re-wired as written — `trim_for_context` is the live path.

## 16. src: memory, RAG, embeddings and settings

### Overview

`src/chroma_client.py`, `src/embedding_lanes.py`, `src/embeddings.py`, `src/index_walk.py`, `src/memory.py`, `src/memory_provider.py`, `src/memory_vector.py`, `src/personal_docs.py`, `src/preset_manager.py`, `src/rag_manager.py`, `src/rag_singleton.py`, `src/rag_vector.py`, `src/settings.py`.

This section covers what the assistant remembers with: the JSON memory store and the ChromaDB
vector index over memory entries, the personal-document index (vector and keyword), the embedding
lanes and clients that feed them, and the settings/presets stores. The route handlers that call into
it are covered by `routes-rest-memory-personal-research` and the other `routes-*` sections;
`core/database.py`'s hourly owner sweep and `core.atomic_io` are covered by `core-data-platform`;
the tool index's own copy of the embedding-lane bootstrap is covered by `src-tools-schema-index`.
A finding here is about the store or the index itself, not about who calls it.

### Coverage

**Read fully:** all thirteen files above, 3,667 lines.

Four findings rest on measurements taken at this snapshot against the real modules with
Chroma-shaped stub collections in place of ChromaDB (which is not reachable in this environment).
Each Evidence block states the probe, so the numbers can be reproduced; the stub replaces only the
external store, not the code under test.

#### [RACE] Concurrent memory writes lose entries, raise `FileNotFoundError`, and can leave `memory.json` unreadable

- **Location:** `src/memory.py:275-278` (the shared temp path), with `:180-186` and `:261-274`
- **Severity:** high
- **Disposition:** fix-now
- **Evidence:** every writer stages through the same fixed temp name and then renames it:

  ```python
  tmp_file = self.memory_file + ".tmp"
  with open(tmp_file, "w", encoding="utf-8") as f:
      json.dump(entries, f, ensure_ascii=False, indent=2)
  os.replace(tmp_file, self.memory_file)
  ```

  No lock anywhere in the tree guards this store. Twelve threads released by a barrier, each
  running `load_all_for_update()` → append one entry → `save()` (13 entries written), 30 bursts,
  `sys.setswitchinterval(1e-5)` to force GIL hand-offs:

  ```
  25 runs: valid JSON, 2 entries      writer exceptions over 30 bursts:
   4 runs: valid JSON, 3 entries         FileNotFoundError      211
   1 run : UNREADABLE JSONDecodeError    MemoryStoreUnreadable    6
  ```

  The loss is not a stress-case artefact. With **two** concurrent writers (3 entries written),
  50 bursts: all 3 survived in 7, at least one was lost in 43, and a writer raised in 22. With
  three writers: 50 of 50 bursts lost an entry and 50 of 50 had a writer raise. Two writers
  colliding on `memory.json.tmp` also means one writer's `os.replace` can install a file the other
  writer had only truncated, which is how a burst leaves the store unparsable — the state
  `MemoryStoreUnreadable` was written to make loud (`:8-20`, "the writes are atomic, so the loss is
  durable"). The durability half of the same file is reported separately in
  `core-data-platform.md` — the hourly owner sweep rewrites `memory.json` with a plain truncating
  write (`core/database.py:1481-1482`); this finding is the concurrency half, which needs no crash.

  The write path is ordinary traffic, not an admin action: `src/chat_processor.py:352-354` calls
  `increment_uses` (a read-modify-write) after injecting memories into a turn,
  `src/chat_handler.py:338-340` saves on an inline "remember:" command, `src/ai_interaction.py:396-401`
  on the agent memory tool, `routes/memory/memory_routes.py:137,511,540,562` on add/pin/edit/delete,
  `routes/backup_routes.py:83-107` on import merge, and `src/memory_provider.py:164-166,233-249` on
  the provider API. `mcp_servers/memory_server.py` is a second **process** (`src/builtin_mcp.py:74`)
  that builds its own `MemoryManager(DATA_DIR)` (`:104`) and runs the same
  load-append-save (`:70,187,215,243`), so the app process and the built-in MCP server share both
  the file and the temp name with no coordination at all.
- **Impact:** three distinct failures, all silent to the caller: (1) a lost update — the last
  writer's snapshot wins and every other writer's change is gone, so a memory the user saved is
  simply absent; (2) `FileNotFoundError` propagates out of `save()` (nothing catches it there), so
  the request that called it fails; (3) the store can be left unreadable, after which every
  read-modify-write caller refuses to write (by design, `routes/memory/memory_routes.py:40-49`
  turns that into a 503) and the memory feature stops until the file is repaired. A memory entry is
  user data the user explicitly asked to keep.
- **Fix:** hold one lock across the whole read-modify-write and stop sharing a temp name. A
  `threading.Lock` on the manager plus an `update(fn)` helper used by the callers above covers the
  lost update — a lock inside `save()` alone does not, because the window is between the load and
  the save. `tempfile.mkstemp(dir=os.path.dirname(self.memory_file), prefix="memory.json.")` before
  the dump covers the rename collision. A process-local lock does not cover
  `mcp_servers/memory_server.py`; if that server keeps writing the same file, the lock must be a
  file lock (or the server must be pointed at the app's API instead of the file).
- **Re-review (2026-10-04):** re-derived in full; high stands. The source is as quoted and no lock exists
  (`grep -n "Lock\|flock\|fcntl" src/memory.py mcp_servers/memory_server.py` returns nothing). Two
  facts make the race reachable without the forced switch interval used above. The pin, edit and
  delete handlers are plain `def` routes (`routes/memory/memory_routes.py:503`, `:528`, `:550`), so
  FastAPI runs them on worker threads while `increment_uses` runs on the event loop for every chat
  turn that injected a memory. `mcp_servers/memory_server.py` is a separate process, so no in-process
  ordering covers it. The loss rates quoted were measured with `sys.setswitchinterval(1e-5)`; the
  rate under ordinary scheduling was not measured and is lower.


#### [BUG] Re-indexing a directory never removes a changed file's previous chunks, so the index keeps serving the old text

- **Location:** `src/rag_vector.py:495-556` (`index_personal_documents`), with `:83-91` and `:191-198`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** document ids are a hash of the chunk text, so an edited chunk gets a new id, and
  the index path only ever adds:

  ```python
  doc_id = _generate_doc_id(text, metadata.get("owner") or "")
  ...
      existing = lane.collection.get(ids=[doc_id])
      if existing["ids"]:
          wrote = True
          continue
  ```

  Probe with a stub collection: index a one-file directory (`indexed_count=1`), edit the file, index
  the same directory again (`indexed_count=1`):

  ```
  rows in collection      : 2  (1 file on disk)
    doc_1fe6193099e0b755  source=note.md  text='version one content'
    doc_075032cb252826c2  source=note.md  text='version two content'
  ```

  Nothing in the tree removes the old rows. `reindex_directory` (`:599-613`) is the one method that
  removes before indexing and it has no caller — no route, no MCP action, nothing
  (`PersonalDocsManager.index_all_directories`, `src/personal_docs.py:448`, is likewise uncalled).
  The reachable index path is `POST /api/personal/add_directory`, which calls
  `rag.index_personal_documents(directory, owner=owner)` unconditionally
  (`routes/personal_routes.py:232`) even for a directory already tracked, and the agent-facing
  `mcp_servers/rag_server.py:116`.
- **Impact:** after an ordinary edit-then-re-add, retrieval can return the superseded text — for a
  small edit the old and new chunks embed almost identically and the stale one is a legitimate top
  hit — so the model answers from content the user has already changed. Each re-add also adds a
  copy of every changed chunk and nothing reclaims them, so the index grows monotonically with
  edits.
- **Fix:** after a file's chunks are written, delete that `source`'s rows whose ids are not among
  the ids just written. `delete_by_source` (`:686-687`) already implements the removal half, and the
  chunk ids for one file are computed in the same loop.

#### [ERROR-HANDLING] A collection that fails is reported as an empty, healthy lane, so retrieval returns nothing with no diagnostic

- **Location:** `src/embedding_lanes.py:42-46` (`count`), with `:339-340`, `:366-373`, `:387`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `EmbeddingLane.count` swallows the error and reports zero, with no log line:

  ```python
  def count(self) -> int:
      try:
          return int(self.collection.count())
      except Exception:
          return 0
  ```

  Probe with a real `EmbeddingLane` over a collection whose `count()` raises (the client is a plain
  object, so `healthy` is true and the failure is exactly the one ChromaDB being down produces):

  ```
  lane.healthy            : True
  lane.count()            : 0   <- real EmbeddingLane.count()
  log records emitted     : 0
  search() results        : []
  collection.query calls  : 0
  collection.get calls    : 0
  get_stats()             : document_count=0 healthy=True
  lane stats              : {... 'count': 0, 'healthy': True}
  ```

  `lane_count` (`:339-340`) is the max over the lanes, so one failing lane makes it zero and
  `VectorRAG.search` returns before querying anything (`src/rag_vector.py:353-354`). The keyword
  fallback is never reached, and `query_lanes`'s `raise_if_all_failed` (`:387`) requires
  `attempted > 0`, which a `count()` that returns 0 never increments.
- **Impact:** a ChromaDB outage during a chat produces no results, no fallback, and no log line —
  the assistant silently stops using the user's documents and memories. The admin panel reports the
  index as healthy with 0 documents, which is indistinguishable from an empty index, so the
  operator has nothing to act on until they notice the behaviour.
- **Fix:** log the exception in `count()` (or raise a typed error) and mark the lane unhealthy so
  `get_stats()` and the search path can tell an outage from an empty index — the distinction
  `src/memory.py:125-155` already draws for `memory.json` with `MemoryStoreUnreadable`.

#### [BUG] The personal-docs state files are written non-atomically, so a truncated write silently drops the tracked-directory list

- **Location:** `src/personal_docs.py:239-244` (`save_directories`), `:263-267` (`_save_excluded`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** both write the live file in place, with no temp file and no replace:

  ```python
  with open(self.directories_file, 'w', encoding="utf-8") as f:
      json.dump(_string_list(self.indexed_directories), f, indent=2)
  ```

  Every other JSON store in this section's files writes atomically through
  `core.atomic_io.atomic_write_json`: `src/settings.py:296`, `src/preset_manager.py:139`,
  `src/memory.py:275-278`. Probe: a truncated `indexed_directories.json` (a two-entry list cut
  mid-write) makes `load_directories` (`:223-236`) log one error and reset to empty:

  ```
  state file on disk      : '["/home/user/notes", "/home/user/work"'
  tracked directories     : []
  directories_count stat  : 1
  ```

- **Impact:** a crash or power loss inside the write loses the whole tracking list, and nothing
  reports it beyond one error line. The vector rows for those directories stay in the collection,
  but `remove_directory` returns early for an untracked directory (`:337`), `refresh_index` no
  longer walks it, and `get_file_list` no longer lists it — so the user cannot see or remove those
  indexed chunks from the UI until they re-add each directory by path. `excluded_files.json` has the
  same write and the same loss, which re-exposes files the user had excluded.
- **Fix:** write both through `core.atomic_io.atomic_write_json`, as the sibling stores do.

#### [PERF] Two index paths transfer the whole collection to do bounded work

- **Location:** `src/rag_vector.py:415` (`_keyword_search_fallback`), `:578` (`remove_directory`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** both call `collection.get` with no `where` and no `limit`, then filter in Python.
  Probe for `remove_directory`: three rows indexed, one under the target directory —

  ```
  remove_directory(notes) -> {'success': True, 'removed_count': 1, ...}
  rows scanned by get()   : 3
  get() arguments         : ids=None include=['metadatas'] where=None limit=None
  rows that matched       : 1
  ```

  The same file shows the filtered alternative it does not use: `delete_by_source` asks Chroma for
  `where={"source": source}` (`:686-687`). `_keyword_search_fallback` loads every document from
  every lane (`:415`) to score word overlap for one query, and it runs on the request path
  precisely when a lane query has already failed (`:405`).
- **Impact:** a directory removal and every fallback search pull the entire index across the HTTP
  boundary. On a large index this is the dominant cost of an operation that touches one directory
  or returns `k` rows, and the fallback cost lands on the degraded path where the app is already
  failing. `remove_directory`'s scan is deliberate — no Chroma operator selects a scalar string by
  path prefix, as its docstring explains — but the fallback has no such constraint: it could score
  against the already-loaded keyword index (`src/personal_docs.py`) or bound the candidate set.
- **Fix:** bound the fallback scan (or serve it from the in-memory keyword index), and for
  `remove_directory` at least stop fetching documents — `include=["metadatas"]` is already minimal,
  so the remaining step is to page the scan or maintain a per-directory id list.

#### [FOOTGUN] `VectorRAG._embed()` and `_collection` can come from different embedding lanes

- **Location:** `src/rag_vector.py:116-121` (`_embed`), with `:97-101` and `:93-95`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the lanes are built custom-first (`build_embedding_lanes`), but the collection
  prefers the fastembed lane while the model and the private encoder take the first lane:

  ```python
  self._collection = next(
      (lane.collection for lane in self._lanes if lane.name == LANE_FASTEMBED),
      self._lanes[0].collection,
  )
  self._model = self._lanes[0].client
  ...
  def _embed(self, texts: List[str]) -> List[List[float]]:
      return np.array(self._lanes[0].encode(texts), dtype=np.float32).tolist()
  ```

  With a custom endpoint configured, `_embed()` returns vectors from the custom model while
  `collection` is the fastembed lane's collection. Nothing calls either today — a grep for
  `_embed`/`.collection` across `routes/`, `src/`, `mcp_servers/`, `core/` and `app.py` finds no
  external user, and `_embed` has no caller at all — but `collection` is documented as the public
  access point for route code ("Expose the ChromaDB collection for direct access by personal_routes
  etc.", `:93-95`). The same bootstrap is repeated in `src/memory_vector.py:34-52` and
  `src/tool_index.py:150-162`, which is why the three copies can disagree.
- **Impact:** the next caller to pair the documented property with the private encoder writes or
  searches vectors from the wrong model. A dimension mismatch fails loudly; equal dimensions (two
  models with the same width) return unrelated neighbours with no error.
- **Fix:** delete `_embed` (it has no caller), or have both it and `_collection` resolve from one
  named lane rather than from `_lanes[0]` and a name search.

## 17. src: documents, uploads, PDF and office

### Overview

`src/attachment_refs.py`, `src/document_actions.py`, `src/document_processor.py`,
`src/generated_images.py`, `src/markitdown_runtime.py`, `src/office_doc.py`,
`src/pdf_form_doc.py`, `src/pdf_forms.py`, `src/pdf_runtime.py`, `src/upload_handler.py`.

The document pipeline behind a chat attachment and the upload store behind it: the
`UploadHandler` (rate limit, size/type checks, dedup, the `uploads.json` index, reservation
against cleanup, owner rename, retention sweep), the persistence form for message content and
attachment references, the PDF/office/text extraction `build_user_content` runs, the auto-created
`Document` rows for attached PDFs and Office files, the optional-dependency shims for
markitdown and PyMuPDF, the AcroForm helpers (field extraction, value fill, signature and
annotation stamping), and the generated-image filename resolver.

The boundary: the upload, document-library and gallery routes that call these helpers are
`routes-rest-media-files` and `routes-gallery-document`; the `/api/generated-image/{filename}`
handler that serves the file this section resolves is in `app.py` (`build-install-deploy`); the
byte caps are `src/upload_limits.py` (`src-security`); `Document`/`DocumentVersion` and the
`chat_messages` FTS table are `core-data-platform`; the session write that calls
`persistable_message_content` is `core-auth-session`/`src-chat-session`; the agent tool that
reaches `run_document_tidy` and the dispatcher around it are `src-agent-tools` and
`src-tools-parse-exec`; the scheduler that triggers the tidy action is
`src-research-scheduling`. This section covers what these helpers do with a caller-supplied
filename, upload id or document body, and what they do when a file or an optional dependency is
missing — not whether the routes that call them authenticate or scope correctly.

### Coverage

**Read fully:** all ten assigned files (3,429 lines): `src/upload_handler.py` (1,393),
`src/document_processor.py` (607), `src/pdf_form_doc.py` (441), `src/pdf_forms.py` (401),
`src/document_actions.py` (197), `src/attachment_refs.py` (164), `src/markitdown_runtime.py`
(106), `src/office_doc.py` (73), `src/generated_images.py` (32), `src/pdf_runtime.py` (15).
Line references are to the working tree at `2992bf6d368a`; `git status --porcelain` showed only
the untracked `audit/` directory.

**Read partially:** the boundary code the findings rest on — `routes/document/document_routes.py`
at the PDF import (`:225-300`), the tidy route (`:852-965`), the render/export/AI-fill handlers
(`:1380-1440`, `:1491-1625`) and the unguarded `import fitz` (`:1247-1255`);
`routes/document/document_helpers.py` at `_verify_doc_owner`, `_owner_session_filter`,
`_resolve_user_upload_path`, `_locate_upload` and `_assert_pdf_marker_upload_owned` (`:1-215`);
`routes/upload_routes.py` at the download handler (`:360-425`) and the offloaded cleanup
(`:325-327`); `app.py` at `/api/generated-image/{filename}` (`:513-553`), the exception handlers
(`:616-633`) and the startup seeding of housekeeping tasks (`:1160-1180`); `core/session_manager.py`
at the message persist (`:265-285`); `core/database.py` at `_scrub_legacy_chat_message_fts_media`
(`:2264-2292`); `src/agent_tools/document_tools.py` at the active-document globals and owner
query helpers (`:1-80`), the read/update/suggest targets (`:470-500`, `:705-735`) and the
`manage_documents` dispatch (`:763-892`); `src/tool_execution.py` at `_direct_fallback`
(`:765-780`), `_document_tool_dispatch` (`:783-802`), `execute_tool_block` (`:810-965`) and the
`manage_documents` branch (`:1133-1144`); `src/agent_loop.py` at the SSE tool wrapper
(`:5785-5825`); `routes/chat_routes.py` at the active-document fallback (`:1445-1475`) and the
stream handler's `try`/`except`/`finally` (`:2309`, `:2336`, `:2551`, `:2590-2600`);
`src/builtin_actions.py` at `TaskNoop` (`:412-422`) and `action_tidy_documents` (`:453-461`);
`src/task_scheduler.py` at `HOUSEKEEPING_DEFAULTS` (`:253`) and the seeding/status block
(`:2474-2507`); `src/tool_security.py` at `owner_is_admin_or_single_user` and
`blocked_tools_for_owner` (`:237-271`); `src/owner_identity.py:17-25`; `src/upload_limits.py`
in full (72 lines — the chat cap this handler reads); `requirements-optional.txt` at the
PyMuPDF and markitdown entries (`:30-46`).

**Not read:** the rest of `routes/document/document_routes.py`, `routes/chat_routes.py`,
`src/agent_loop.py`, `src/tool_execution.py`, `src/agent_tools/document_tools.py`,
`core/session_manager.py` and `src/task_scheduler.py` (each assigned to another section); the
front end that renders attachments, documents and the PDF editor; the RAG indexer's use of
markitdown (`src/personal_docs.py`, assigned elsewhere); the other `routes-*` and `src-*`
sections; and every path that needs PyMuPDF, which is not installed in this checkout
(`venv/bin/python -c "import fitz"` → `ModuleNotFoundError`) — `extract_fields`, `fill_fields`,
`stamp_signatures` and `stamp_annotations` were read, not run. The library's own tests were
executed, not read end to end.

**Checks run:** `git log --oneline -1` / `git status --porcelain` (clean apart from `audit/`),
the optional-dependency imports (`markitdown`, `fitz`, `magic`, `pypdf`, `PIL`,
`charset_normalizer`), and eleven throwaway probe scripts under `/tmp` (not part of the target
tree); the ones quoted below are: a crafted `.docx` with the zip encryption bit set, one with
compression method 9, and one with ten zeroed bytes in its deflate stream,
through `_extract_docx_native`, `convert_to_markdown` and `build_user_content`; the same
`build_user_content` call on a healthy `.docx` as a control; the real dispatcher
(`execute_tool_block` with a `manage_documents` `tidy` block, and `action=list` as the control)
against a temp app DB with nothing to tidy, with `AUTH_ENABLED=false` so the admin gate does not
short-circuit; `run_document_tidy` against a temp app DB holding an archived junk document, an
active document and an archived copy of it; the same function over 500 documents (2.9 MB) inside
a live event loop with a 10 ms ticker; `_process_pdf` on six malformed or hostile PDFs; and the
`DATA_URL_RE` match set over six data-URL shapes. Also greps for the callers of
`resolve_upload`, `reserve_upload`, `get_upload_info`, `persistable_message_content`,
`strip_inline_data_urls`, `build_user_content`, `run_document_tidy`, `set_active_document` and
`TaskNoop`, and an AST scan for functions in these ten files with no reference outside their
file.

The required discovery command, `ls tests | grep -iE
'upload|document|markitdown|pdf|office|attachment|generated_image'`, selected 48 suites. Running
`PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q -p no:cacheprovider` with those paths
produced **217 passed, 2 skipped** in 3.67s. The skips are `tests/test_markitdown_runtime.py:64`
(`could not import 'markitdown'`) and `tests/test_upload_content_detection_magic.py:41`
(`libmagic/python-magic not installed in this environment`). The only warning is the existing
SQLAlchemy `declarative_base()` deprecation. Every cited line was reopened before writing.

#### [BUG] A tidy run that finds nothing raises `TaskNoop` out of the agent tool dispatcher instead of returning a result

- **Location:** `src/document_actions.py:189-192` (with `src/agent_tools/document_tools.py:883-892`, `src/tool_execution.py:1133-1145`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the function ends a no-op run with a sentinel meant for the scheduler:

  ```python
  # src/document_actions.py:189-192
          if deleted == 0:
              # Use sentinel so the scheduler can drop the run row entirely.
              from src.builtin_actions import TaskNoop
              raise TaskNoop(f"scanned {len(docs)} document(s), no junk")
  ```

  `TaskNoop` inherits from `BaseException` on purpose, so `except Exception` wrappers do not
  catch it (`src/builtin_actions.py:412-421`), and the tool path that awaits the same function is
  wrapped only in `except Exception`:

  ```python
  # src/agent_tools/document_tools.py:883-892
              elif action == "tidy":
                  from src.document_actions import run_document_tidy
                  result = await run_document_tidy(owner or "")
                  return {"response": result, "exit_code": 0}
  ...
          except Exception as e:
              logger.error(f"manage_documents error: {e}")
              return {"error": str(e), "exit_code": 1}
  ```

  Measured with a temp app DB holding one ordinary document and no junk, through the real
  dispatcher (`AUTH_ENABLED=false` so the non-admin tool gate does not answer first):

  ```
  $ AUTH_ENABLED=false venv/bin/python /tmp/probe_tidy_dispatcher.py
  action=tidy: execute_tool_block RAISED TaskNoop: scanned 1 document(s), no junk
  action=list: returned desc='manage_documents: {"action": "list"}' result={'response': 'Found 1 document(s), ...'}
  ```

  The same call on the handler alone (`/tmp/probe_tidy_tasknoop.py`) gives
  `handler RAISED TaskNoop (BaseException subclass: True)`. Nothing above the handler absorbs it:
  `manage_documents` is routed through `_document_tool_dispatch`, which has no `try` of its own
  (`src/tool_execution.py:783-802`), while the sibling fallback catches `Exception` only (`:777`);
  the SSE tool wrapper's `_run_tool` has a bare `finally` and no handler
  (`src/agent_loop.py:5791-5805`), so `desc, result = await _tool_task` at `:5818` re-raises, and
  the `try` block that wraps the agent loop in the stream handler (opened at `:2309`) is closed
  only by `except (asyncio.CancelledError, GeneratorExit)` (`routes/chat_routes.py:2551`) and a
  bare `finally` at `:2590`.
- **Impact:** when the agent runs `manage_documents action=tidy` against a library with nothing to
  delete — the common outcome, since the junk rules are conservative — the tool never returns a
  result and the exception leaves the tool layer. The model is not told "nothing to tidy"; the
  `/api/chat_stream` turn ends on an unhandled `BaseException` with no terminal event, instead of
  a tool result the loop can continue from. The scheduler path is unaffected and behaves as
  documented, which is why the sentinel exists. The raise was verified at the handler and at
  `execute_tool_block`; the aborted-stream end state is read from the handlers named above, not
  observed in a full chat turn.
- **Fix:** keep the sentinel for the scheduler and return normally for the tool. Either raise it
  in the scheduler-facing wrapper (`action_tidy_documents`, `src/builtin_actions.py:453-461`) when
  the returned string says nothing was removed, or catch `TaskNoop` around the call in
  `document_tools.py` and answer `{"response": result, "exit_code": 0}`.

#### [ERROR-HANDLING] The native `.docx` fallback raises on a damaged or password-protected file instead of degrading

- **Location:** `src/markitdown_runtime.py:57-61` (the `except` clause), with the fallback call at `:85-97`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the fallback extractor absorbs only three failure modes of `ZipFile.read`:

  ```python
  # src/markitdown_runtime.py:57-61, inside _extract_docx_native
      try:
          with zipfile.ZipFile(path) as z:
              xml_bytes = z.read("word/document.xml")
      except (zipfile.BadZipFile, KeyError, OSError):
          return None
  ```

  A corrupt deflate stream raises `zlib.error`, an encrypted entry raises `RuntimeError`, and an
  unsupported compression method raises `NotImplementedError`; none is in that tuple, and
  `convert_to_markdown`'s own `except Exception` wraps only the markitdown call (`:98-106`), not
  the fallback at `:89`. Measured on crafted files:

  ```
  $ venv/bin/python /tmp/probe_docx_encrypted.py
  baseline (plain docx): 'hello'
  encrypted: RAISED RuntimeError: File 'word/document.xml' is encrypted, password required for extraction
  encrypted: convert_to_markdown RAISED RuntimeError: File 'word/document.xml' is encrypted, password required for extraction
  deflate64: RAISED NotImplementedError: That compression method is not supported
  deflate64: convert_to_markdown RAISED NotImplementedError: That compression method is not supported

  $ venv/bin/python /tmp/probe_docx_trunc.py
  trunc 0.30 (72B): returned None
  corrupt: RAISED error: Error -3 while decompressing data: invalid bit length repeat
  ```

  (`corrupt` is a valid `.docx` with ten bytes of its deflate stream zeroed; the truncated copies
  are the handled `BadZipFile` case and return `None`.) The same input through the chat
  attachment builder, with a healthy file as the control:

  ```
  $ venv/bin/python /tmp/probe_build_user_content_corrupt.py
  corrupt deflate: build_user_content RAISED error: Error -3 while decompressing data: invalid bit length repeat
  encrypted: build_user_content RAISED RuntimeError: File 'word/document.xml' is encrypted, password required for extraction
  healthy: returned 'summarize this\n\n[Document content — probe_min]:\nhello'
  ```

  markitdown is absent in this checkout, which is a supported configuration:
  `requirements-optional.txt:37-41` documents it as optional, with the Office formats falling
  back to a friendly install banner rather than extracting, and the module states the contract
  twice — "When absent, callers degrade gracefully (chat shows a hint; the RAG indexer skips the
  file)" (`:5-8`) and "Returns the extracted Markdown, or ``None`` if markitdown is unavailable
  or the conversion fails — callers degrade gracefully rather than erroring" (`:78-79`). Nothing
  between the helper and the route catches it: `_process_office_document` calls
  `convert_to_markdown` unguarded (`src/document_processor.py:226`), `build_user_content` calls
  that unguarded (`:575-582`), and the app's exception handlers cover four custom types, none of
  them `zlib.error` (`app.py:616-633`).
- **Impact:** on an install without markitdown, a user who attaches a `.docx` whose deflate stream
  is damaged, or a zip-encrypted one, gets an unhandled exception on the request thread instead of
  the "[Attached document … no extractable text found]" banner the fallback exists to produce.
  Only the uploader's own turn is affected, and only when the file is damaged; the truncation and
  wrong-container cases already degrade. `tests/test_markitdown_runtime.py` covers the
  missing-dependency path and a markitdown converter that raises (`:36-45`), but not a corrupt
  file on the native path.
- **Fix:** widen the clause to the family the extractor is meant to absorb — add `RuntimeError`,
  `NotImplementedError` and `zlib.error` to the tuple (or `except Exception`, in a function whose
  contract is "return `None` on failure") — and wrap the `_extract_docx_native` call in
  `convert_to_markdown` the way the markitdown call is wrapped.

#### [DUP] The REST tidy route reimplements the scheduled tidy, and the two delete different documents

- **Location:** `routes/document/document_routes.py:852-871` (the inline copy) against `src/document_actions.py:53-195`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the route keeps its own copy of the rules and imports only the title set, with a
  comment that claims parity:

  ```python
  # routes/document/document_routes.py:869-872
              # Same junk-detection logic as the scheduled tidy_documents
              # action (src/document_actions.py). Keep these two in sync.
              import re as _re
              from src.document_actions import _JUNK_TITLES
  ```

  The two disagree in three visible ways. The route restricts the candidate set to live,
  non-archived documents, while the shared helper queries every document for the owner:

  ```python
  # routes/document/document_routes.py:858-863
              q = (
                  db.query(Document)
                  .outerjoin(DbSession, Document.session_id == DbSession.id)
                  .filter(Document.is_active == True)
                  .filter((Document.archived == False) | (Document.archived.is_(None)))
              )
  ```

  ```python
  # src/document_actions.py:68-74
          if owner:
              docs = db.query(Document).filter(Document.owner == owner).all()
          else:
              docs = db.query(Document).all()
  ```

  The route also has an email-stub rule and a title-repair pass the helper lacks
  (`routes/document/document_routes.py:902-935`), and the helper has the duplicate-content pass
  the route lacks (`src/document_actions.py:148-184`). Measured on a temp app DB holding an
  archived document titled `asdf`, an active document, and an archived copy of it:

  ```
  $ venv/bin/python /tmp/probe_tidy_archived.py
  tidy result: Removed 2 of 3: asdf (junk title 'asdf'); Report (+1 duplicate copies) · 1 kept
  survivors: [('dup-archived', 'Report', True, True)]
  ```

  The helper hard-deleted the archived `asdf` document the button leaves alone, and kept the
  archived copy of the duplicate pair while deleting the active one.
- **Impact:** the manual tidy button and the automatic `tidy_documents` action delete different
  sets. The action is event-triggered after five document creations and seeded active by default
  (`src/task_scheduler.py:253` has no `ship_paused`, and `:2502` sets `status="paused" if
  ships_paused else "active"`), so a user can lose an archived document, or the active copy of a
  duplicate pair, without ever pressing the button. Every row the helper deletes is junk or a duplicate by
  its own rules, so the loss is bounded — but which copy survives is decided by `updated_at`, not
  by `archived`, so the archived member can be the survivor.
- **Fix:** have the route call `run_document_tidy` (it can keep the title-repair counting), or
  lift the rule sets into one function with an explicit parameter for the archived/inactive
  policy.

#### [BUG] `strip_inline_data_urls` leaves data URLs that carry a parameter before `;base64,` in persisted history

- **Location:** `src/attachment_refs.py:15-18`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the pattern's media-type run stops at the first `;`, so a data URL with any
  parameter before `;base64,` never matches:

  ```python
  # src/attachment_refs.py:15-18
  DATA_URL_RE = re.compile(
      r"data:[^;,\s\"']+;base64,[A-Za-z0-9+/=]+",
      re.IGNORECASE,
  )
  ```

  Measured on six shapes (each with a 200-character payload, output length in characters):

  ```
  $ venv/bin/python /tmp/probe_data_url_params.py
  plain              in= 226 out=  49 stripped=True
  charset param      in= 241 out= 241 stripped=False
  svg+xml            in= 230 out=  49 stripped=True
  name param         in= 248 out= 248 stripped=False
  percent-encoded    in= 229 out=  52 stripped=True
  wrapped newline    in= 227 out= 150 stripped=True
  ```

  `charset param` is `data:text/plain;charset=utf-8;base64,…`, `name param` is
  `data:application/pdf;name=report.pdf;base64,…`; `wrapped newline` is a base64 body split across
  a newline, where only the first segment is replaced. This helper is the only thing standing
  between provider media and the database on both write paths: `persistable_message_content` runs
  on every message that reaches `chat_messages` (`core/session_manager.py:274-276`), and the
  legacy FTS scrub selects rows by `instr(content, ';base64,') > 0` and re-indexes them through
  `search_index_text`, the same regex (`core/database.py:2264-2292`) — so a parameterised payload
  is not cleaned up by the scrub either. Both call sites state the opposite intent
  (`src/attachment_refs.py:1-6`, `core/session_manager.py:274-275`).
- **Impact:** a message whose text contains a data URL with a parameter — the common shape is
  `data:text/plain;charset=utf-8;base64,…` — is stored in `chat_messages.content` and indexed in
  `chat_messages_fts` at full base64 size, and is replayed to the model on a later turn. That is
  exactly the duplication the module exists to prevent. Reachability is limited to a parameterised
  data URL arriving in message text, and the payload is the caller's own data; the stored bytes
  and index entries are the cost.
- **Fix:** allow parameter segments before the marker, for example
  `r"data:[^,\s\"']*;base64,[A-Za-z0-9+/=]+"` (or `(?:[^;,\s\"']*;)*base64,`), and let the base64
  run span whitespace if wrapped payloads are in scope.

## 18. src: email, calendar and integrations

### Overview

`src/caldav_sync.py`, `src/caldav_writeback.py`, `src/email_thread_parser.py`, `src/integrations.py`, `src/webhook_manager.py`, `src/youtube_handler.py`.

The outbound integration layer. `src/caldav_sync.py` pulls a remote CalDAV server into the local
`CalendarCal`/`CalendarEvent` tables and retries the pending local→remote pushes;
`src/caldav_writeback.py` performs one create, update or delete against the remote calendar;
`src/email_thread_parser.py` splits an email body (HTML or plaintext) into quoted reply turns;
`src/integrations.py` owns the registered HTTP integrations, their stored credential, and the
`api_call` execution path; `src/webhook_manager.py` validates a webhook target and fires the
outgoing POSTs; `src/youtube_handler.py` is the compatibility alias that resolves to
`services.youtube.youtube_handler`.

The boundary: the CalDAV account configuration, the sync endpoint and the write-back triggers are
`routes-skills-calendar-task` (`routes/calendar_routes.py`); the read path that calls the thread
parser is `routes-email` (`routes/email_routes.py`); webhook registration is
`routes-rest-integrations-misc` (`routes/webhook/webhook_routes.py`); integration CRUD is
`routes-rest-auth-admin` (`routes/auth_routes.py`); the per-user preferences file the CalDAV
accounts live in is `routes-rest-media-files` (`routes/prefs_routes.py`); the Fernet key store,
`src/url_safety.py` and `src/api_key_manager.py` are `src-security`; `CalendarEvent` is
`core-data-platform`; the `api_call` tool wrapper and dispatcher are `src-agent-tools` and
`src-tools-parse-exec`; the canonical YouTube module is `services-media`. This section covers what
these six modules do with a caller-supplied URL, a stored credential and an untrusted body — not
whether the routes that call them are gated correctly.

### Coverage

Citations refer to the working tree at `2992bf6d368a`; `git status --porcelain` showed only the
untracked `audit/` directory.

**Read fully:** all six assigned files (2,935 lines) — `src/integrations.py` (810),
`src/caldav_sync.py` (722), `src/email_thread_parser.py` (614), `src/webhook_manager.py` (455),
`src/caldav_writeback.py` (311), `src/youtube_handler.py` (23). Also read fully for the
credential-storage and outbound-URL claims: `src/secret_storage.py` (87), `src/url_safety.py`
(108) and `routes/prefs_routes.py` (125, the per-user store the CalDAV accounts live in).

**Read partially:** the boundary code and callers this section's claims rest on —
`routes/calendar_routes.py` at `_require_user` (`:69-80`), the CalDAV config and account CRUD
(`:819-995`), `_push_caldav_event_after_commit` (`:151-179`), `_record_caldav_delete_tombstone`
(`:181-198`), the test-connection route (`:995-1085`) and `/sync` (`:1086-1093`);
`routes/email_routes.py` at the read path's parser call (`:3117-3128`) and the
`asyncio.to_thread` that runs it (`:3216`); `routes/webhook/webhook_routes.py` at the webhook CRUD
and test routes (`:64-160`); `routes/auth_routes.py` at the integration CRUD (`:759-917`);
`core/database.py` at `CalendarEvent` (`:1856-1888`); `src/settings.py` at `save_settings`
(`:250-254`); `src/api_key_manager.py` at `get_or_create_key` / `encrypt_api_key` /
`decrypt_api_key` (`:17-51`); `src/tools/system.py` at `do_api_call` (`:496-524`);
`src/tool_capabilities.py` at the `api_call`/`app_api` registration (`:247-261`) and
`tool_result_should_arm_gate` (`:505-547`); `src/task_scheduler.py` at the retired-action set
(`:265-269`) and the integrations caller (`:1398-1420`); `services/youtube/youtube_handler.py`
(`:1-60`), `services/youtube/__init__.py`, `services/__init__.py` and `src/chat_handler.py:19-26`
for the alias check; `static/js/emailLibrary.js` at the two `thread_turns` render sites
(`:5769-5771`, `:6188-6216`) and the `_sanitizeHtml` calls that feed them (`:5826-5847`);
`static/js/settings.js` at the integration auth-type select (`:3160-3187`). Of the module's own
tests: `tests/test_caldav_sync_uid_scope.py`, `tests/test_caldav_redirect_hardening.py`,
`tests/test_integrations_url_join.py` and `tests/test_webhook_ssrf_resilience.py` fully;
`tests/test_integrations_store_shape.py` at its first cases.

**Not read:** the rest of every caller file named above — `routes/email_routes.py` (~6,100 further
lines), `routes/calendar_routes.py`, `routes/auth_routes.py` and
`routes/webhook/webhook_routes.py` outside the regions cited; `src/task_scheduler.py` outside its
two cited regions; `src/agent_loop.py` beyond the integrations-prompt call (`:2733-2743`);
`src/tool_execution.py` beyond the `api_call` dispatch (`:1178`); `core/database.py` beyond
`CalendarEvent`; `services/youtube/youtube_handler.py` beyond `:60`; the IMAP/SMTP code that
produces the email bodies, the email front end beyond the sanitizer sites, and the `caldav` and
`httpx` library internals beyond the behavior the probes exercised; `mcp_servers/`. The other
sections' findings were read only where a cross-reference is named.

**Checks run:** the 32 suites matching `ls tests | grep -iE 'caldav|integrations|webhook|youtube|email_thread|carddav'`
— `venv/bin/python -m pytest -q -p no:cacheprovider <32 files>` from the repository root →
**163 passed** in 4.59s, 7 warnings (the `datetime.utcnow()` deprecations at
`src/caldav_sync.py:309-310` and one at `tests/test_caldav_google_principal_url.py:45`). Thirteen
throwaway probe scripts under `/tmp`, outside the target tree. The ones the findings quote: the
CalDAV DNS-flip probe (three runs; two quoted below), the VEVENT-UID collision probe (three runs,
including one with a non-colliding second event), the parser probes (four runs: a nesting-depth
sweep, a sibling-count sweep, a deep-chain run, and a smoke set of six real-world bodies), and the
webhook guard probe (two runs, comparing the accepted address list with `src/url_safety._classify`).
The last is the `api_call` path-join probe recorded under the dropped hypotheses. Also the greps
each finding records: the `parse_thread` caller set, the `turns_json` writer set, the `validate_webhook_url` / `_is_private_url` callers,
the `_join_integration_url` / `mask_integration_secret` / `load_integrations` callers, the
`set_loop` / `fire_and_forget` callers, the `untrusted_content` consumers, `uvicorn.run`'s worker
count, and `_find_integration` / `_stable_cal_id` call sites. Four hypotheses were checked and
dropped rather than reported: a `//host` path cannot move the `api_call` request to another host
(`_join_integration_url` strips every leading slash before `urljoin`, measured); the parser's turn
HTML is not a new XSS surface (the client runs `body_html` through `_sanitizeHtml`); the
integration store's read-modify-write has no interleaving caller (every writer is an `async`
handler whose load-and-save block contains no await, and `app.py:1306` launches uvicorn with no
worker count); and a missing `untrusted_content` flag on a successful `api_call` does not arm the
gate less than a failure (the tool is registered `ResultIntegrity.EXTERNAL_UNTRUSTED` at
`src/tool_capabilities.py:247-261`, which `tool_result_should_arm_gate` consults for both).

#### [SECURITY] The CalDAV host guard resolves once, so a rebinding DNS answer reaches loopback with the stored credentials

- **Location:** `src/caldav_sync.py:90-103` (`_validate_caldav_hostname`), `:231-253` (`_build_dav_client`), with the validate-then-connect pair at `:644-645`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the guard resolves the host and vets every address, and the client then resolves it
  again independently at connect time. Nothing pins the socket to the address that passed:

  ```python
  def _validate_caldav_hostname(host: str) -> None:
      ...
      try:
          addrs = _resolve_caldav_host_ips(host)
      except OSError:
          raise ValueError("CalDAV URL host does not resolve")
      if not addrs:
          raise ValueError("CalDAV URL host does not resolve")
      for addr in addrs:
          _validate_caldav_address(addr)
  ```

  `_build_dav_client` closes the *redirect* route into internal space
  (`client.session.max_redirects = 0`) and its docstring says so; it does not close this one.
  `sync_caldav` validates and syncs back to back, so the window is one request:

  ```python
  url = validate_caldav_url(url)
  result = await asyncio.to_thread(_sync_blocking, owner, url, user, pw, account_id)
  ```

  The two sibling outbound paths in this section close exactly this TOCTOU by pinning the connect
  to the IP the guard returned — `src/webhook_manager.py:130-160` (`_validated_public_ips`, whose
  docstring names the rebinding window) and `src/integrations.py:565-584` (the recording resolver,
  whose comment names the same window) — and `tests/test_webhook_dns_rebinding_pin.py` pins it for
  webhooks. `src/caldav_writeback.py:295-301` has the same unpinned shape.

  Measured with a probe that answers the validating lookup with a public address and every later
  lookup with `127.0.0.1`, against a loopback HTTP server standing in for an internal service:

  ```
  validate_caldav_url -> http://rebind.example:59455/dav | resolver calls: 1
  sink hits: [('PROPFIND', '/dav', None),
              ('PROPFIND', '/dav', 'Basic <base64 of the configured username:password>')]
  ```

  The first PROPFIND is unauthenticated; the sink answered it with
  `401 WWW-Authenticate: Basic realm="internal"` and the retry carried the account's Basic
  credential (a synthetic one in the probe). Through `_sync_blocking` on the same flip, the sink
  received two PROPFINDs and the sync reported the failure its own body produced
  (`'NoneType' object has no attribute 'tag'`), confirming the response that was parsed came from
  loopback.
- **Impact:** any signed-in user may add a CalDAV account (`routes/calendar_routes.py:914-941`,
  `_require_user` at `:69-80`) and trigger the sync (`POST /api/calendar/sync`, `:1086-1093`). A
  user who points an account at a hostname whose DNS answer they control can therefore make the
  server issue CalDAV requests — PROPFIND/REPORT on the pull, PUT/DELETE on the write-back — to
  loopback, link-local or RFC-1918 addresses, which is exactly what `_validate_caldav_address`
  exists to refuse, and hand the stored CalDAV username and password to an internal service that
  challenges with 401. The response is parsed by the CalDAV client rather than returned to the
  caller, so the attacker's view is blind; the reachability requirement is a DNS record that
  answers differently on two lookups milliseconds apart.
- **Fix:** pin the connect to the IP `_validate_caldav_hostname` returned, the way
  `_validated_public_ips` + `_PinnedAsyncTransport` do for webhooks and `api_call`. The `caldav`
  client uses a `requests` session, so this means mounting an adapter that connects to that
  address while preserving the `Host` header and TLS SNI, and re-validating when the pinned
  address is refused. A per-URL session is the cost.
- **Re-review (2026-10-04):** lowered from medium. Three things have to hold: a signed-in user who is hostile, a DNS record
  that user controls answering differently on two lookups milliseconds apart, and an internal
  service worth reaching blind, since the response is parsed by the CalDAV client and not returned.
  The credentials sent to the internal address are the attacker's own account's.


#### [BUG] A VEVENT UID that another calendar already holds discards that calendar's whole pull, while the counts still report it as synced

- **Location:** `src/caldav_sync.py:418`, `:437-455`, `:483-486`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the per-calendar loop adds a row for every UID the calendar does not already hold
  and commits the batch once. `CalendarEvent.uid` is the global primary key
  (`core/database.py:1860`), so a UID that another calendar holds raises at that commit, and the
  handler for the calendar rolls the entire unit of work back:

  ```python
  existing = _find_existing_event(db, pending, uid_val, local_cal.id)
  ...
  new_ev = CalendarEvent(uid=uid_val, calendar_id=local_cal.id, ...)
  db.add(new_ev)
  pending[uid_val] = new_ev
  result["events"] += 1
  db.commit()
  ...
  except Exception as e:
      logger.exception("CalDAV sync failed for one calendar")
      result["errors"].append(str(e)[:200])
      db.rollback()
  ```

  The containment is deliberate — `_find_existing_event`'s docstring
  (`src/caldav_sync.py:166-177`) says "a genuine
  cross-user uid collision then fails the PK insert inside the per-calendar try/except instead of
  hijacking the row" — but its granularity is the calendar, not the event, and
  `result["events"] += 1` has already counted the rows the rollback discards.

  Measured through the real `_sync_blocking` with a fake DAV client returning two events, a
  temporary database, and `core.database.SessionLocal` pointed at it. The trigger is the one that
  docstring names: the same remote calendar syncing under a second local calendar (here the
  account is deleted and re-added, which mints a new account id and therefore a new calendar id
  from `_stable_cal_id`, `src/caldav_sync.py:143-151`):

  ```
  first sync  : {'calendars': 1, 'events': 2, 'deleted': 0} errors: 0
  re-added    : {'calendars': 1, 'events': 2, 'deleted': 0} errors: ['(sqlite3.IntegrityError) UNIQUE constraint failed: cale']
  retry again : {'calendars': 1, 'events': 2, 'deleted': 0} errors: ['(sqlite3.IntegrityError) UNIQUE constraint failed: cale']
  calendar caldav-d8d60e1fce6e30622a0b6 name='Shared' events=2
  calendar caldav-8600239d70b7cfc40de1f1 name='Shared' events=0
  ```

  The second event in that pull has a UID no other row holds (`ev2@svc`); it is rolled back with
  the colliding one, so the loss is not limited to the colliding event.
- **Impact:** the affected calendar never syncs again. Its `CalendarCal` row is created and stays
  empty, every sync attempt ends with the same `IntegrityError` in the result the UI shows, and no
  remote event from that calendar is ever visible locally. The two ways in are a shared or
  subscribed calendar on the same server reaching two owners (or two accounts of one owner, the
  case `_stable_cal_id`'s account scoping was added for), and deleting then re-adding an account
  so the new calendar row re-fetches events whose UIDs the old row still owns. Locally created
  events are not a trigger: the ICS import mints a fresh uuid per event
  (`routes/calendar_routes.py:1449-1454`).
- **Fix:** contain the collision at the event, not the calendar — insert each new row inside a
  `db.begin_nested()` SAVEPOINT (or pre-check for a UID owned by another calendar) so only the
  colliding event is skipped, and record it as a per-event error. Increment `result["events"]`
  only for rows that survive the commit.

#### [PERF] The HTML thread parser re-walks each subtree at every nesting level, so a crafted email body occupies a worker thread for ~20 seconds

- **Location:** `src/email_thread_parser.py:535-548` (`_walk`, with the same shape in `_walk_with_meta` at `:578-591`), `:451-463`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** at every level the walk asks BeautifulSoup for the node's whole subtree and filters
  it, then does the same for each child:

  ```python
  nested = [t for t in node.find_all(True, recursive=True) if _is_quote_container(t)]
  ...
  direct_nested = [n for n in nested if not has_quote_between(n, node)]
  ```

  so the work is (nodes × nesting depth), and the top-level pass adds an ancestor walk per
  candidate (`tops = [t for t in all_quotes if not has_quote_ancestor(t)]`). The only bound is the
  200,000-character input cap at `:437`. Measured, with the sibling count fixed and the nesting
  depth varied, then at the worst case that fits the cap:

  ```
  depth= 100 len=106500   1.50s
  depth= 200 len=109000   2.93s
  depth= 400 len=114000   5.86s
  depth= 800 len=124000  11.93s
  depth= 900 siblings=6000 len=178500 turns=6900 elapsed=20.10s
  ```

  The one production caller runs it synchronously inside `asyncio.to_thread`
  (`routes/email_routes.py:3216` → `_read_email_sync`), and that caller's `except Exception`
  (`:3122-3127`) turns a failure into a flat render rather than a retry. Nothing absorbs a repeat
  read: `email_boundaries.turns_json` has no writer (`routes-email.md` records this in its
  thread-turn-cache finding), so the parse runs again for every open of the same message.
- **Impact:** the body is attacker-controlled — anyone who can send the user mail — and 178 KB is
  an ordinary newsletter size. Opening one such message holds a default-executor worker for the
  measured ~20 seconds and delays that read by the same amount; several opened at once occupy the
  executor that every other `asyncio.to_thread` call in the process shares. The cost scales
  linearly with nesting depth, so the attacker tunes it against the 200 KB cap rather than needing
  a large message.
- **Fix:** walk only the direct children (`node.find_all(True, recursive=False)` or
  `node.children`) and build the quote-container index once, keyed by parent, instead of
  re-scanning each subtree; cap the nesting depth the parser follows, as the plaintext path
  already caps input length.

#### [SECURITY] The webhook URL guard accepts the carrier-grade-NAT range the sibling guard rejects

- **Location:** `src/webhook_manager.py:30-40`, `:47-63`, `:115-127`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the module's stated policy is to block internal targets, and `_ip_is_private`
  implements it with the stdlib predicates plus an explicit list:

  ```python
  _PRIVATE_NETWORKS = [
      ipaddress.ip_network("10.0.0.0/8"), ..., ipaddress.ip_network("fe80::/10"),
  ]
  ...
      if (
          addr.is_private
          or addr.is_loopback
          or addr.is_link_local
          or addr.is_reserved
          or addr.is_multicast
          or addr.is_unspecified
      ):
          return True

      return any(addr in net for net in _PRIVATE_NETWORKS)
  ```

  `100.64.0.0/10` (RFC 6598 shared address space — the range Tailscale and several cluster CNIs
  allocate from) is in neither, and CPython does not classify it as private. `src/url_safety.py:28-34`
  documents that exact classification gap and closes it for the other outbound guard. Measured:

  ```
  100.64.0.0/10 in webhook _PRIVATE_NETWORKS: False
  IPv4Address('100.64.0.1').is_private: False
  validate_webhook_url('http://100.64.0.1/hook') -> http://100.64.0.1/hook
  _validated_public_ips('http://100.64.0.1/hook') -> [IPv4Address('100.64.0.1')]
  url_safety._classify(100.64.0.1, block_private=True) -> private/shared/loopback address blocked: 100.64.0.1
  ```

  `_validated_public_ips` re-uses the same predicate, so the delivery transport pins the connection
  to that address too. `tests/test_webhook_ssrf_resilience.py` lists the address classes it pins
  (`[::]`, `::ffff:127.0.0.1`, `::ffff:169.254.169.254`, `127.0.0.1`, `0.0.0.0`) and does not
  include this one.
- **Impact:** a stored webhook URL can target a tailnet or cluster address that this guard exists
  to refuse, and each delivery then sends the event payload and its HMAC signature there. The
  mitigation that keeps this low is that only an admin can register a webhook
  (`routes/webhook/webhook_routes.py:103`), so the caller is already trusted; the defect is a guard
  that does not cover the range it claims to.
- **Fix:** add `ipaddress.ip_network("100.64.0.0/10")` to `_PRIVATE_NETWORKS` — or have the module
  share `src/url_safety._classify` — and add the address to the reject list in
  `tests/test_webhook_ssrf_resilience.py`.

## 19. src: research, scheduling and background work

### Overview

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

### Coverage

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

#### [RACE] A killed background job can still be auto-continued — the job store has no writer lock

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

#### [SECURITY] An og:image URL containing `<!--` breaks the report's inline script out of its element

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

#### [SECURITY] The teacher takeover note interpolates a tool-output snippet outside the untrusted fence

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

#### [BUG] Task endpoints are matched by substring, so the wrong endpoint's API key can be attached

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

#### [BUG] `_save_result` rewrites the research record without the fields other writers own

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

#### [RACE] The research record is read-modify-written without a lock, so concurrent hides lose updates

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

#### [DEAD-CODE] The calendar-event reminder scanner is never started

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

#### [DOC-DRIFT] `teacher_escalation`'s stated gates no longer match its code, and its background path is unreachable

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

## 20. src: MCP management and OAuth

### Overview

`src/mcp_manager.py` owns everything below the MCP route layer: the three transports (stdio, SSE
and Streamable HTTP with the OAuth handshake), the tool inventory discovered from each server, the
prompt text and OpenAI function schemas rendered from it, the plan-mode read-only classification,
the tool call path, and the connection registry the routes, the agent loop and the scheduler read.

`src/mcp_oauth.py` holds the remote-server OAuth pieces: the loopback redirect URI, the
pending-authorization registry that bridges the SDK's browser flow to `/api/mcp/oauth/callback`,
and `DbTokenStorage`, the SDK token store backed by the encrypted `McpServer.oauth_tokens` column.

The boundary: the route layer that creates, toggles, reconnects and deletes servers and drives the
OAuth browser flow is `routes-rest-agent-admin` (its findings are cross-referenced here, not
restated); the agent-facing `manage_mcp` tool and its command allowlist are `src-agent-tools`; the
`McpServer` row, its columns and the encryption type are `core-data-platform`; the dispatcher that
calls `call_tool` and the loop that renders the schemas are `src-tools-parse-exec` and
`src-agent-loop`; the built-in servers registered into this manager are
`src-tools-capabilities-policy` and `mcp-servers`. This section covers what the manager does with a
server's configuration and with the tool data a server supplies — not whether the routes
authenticate, whether the agent allowlist is sufficient, or whether the built-in servers behave.

### Coverage

**Read fully:** both assigned files (920 lines): `src/mcp_manager.py` (709), `src/mcp_oauth.py`
(211).

**Read partially:** the callers and boundary code the findings rest on — `routes/mcp/mcp_routes.py`
in full (710 lines), because it is the caller set for the manager (`add_server`,
`reconnect_server`, `toggle_server`, `delete_server`, and the OAuth authorize/callback/exchange
handlers); `src/agent_tools/admin_tools.py` at `_validate_mcp_command` and `do_manage_mcp`'s
add/enable/reconnect branches (`:100-360`); `core/database.py` at the `McpServer` model
(`:570-584`) and `EncryptedText` (`:150-172`); `src/tool_execution.py` at the two MCP dispatch
sites (`:675-700`, `:1290-1320`); `src/task_scheduler.py` at the two `call_tool` sites
(`:1470-1480`, `:2240-2245`); `src/agent_loop.py` at the MCP prompt block (`:2746-2756`), the
schema merge (`:2286-2289`), the plan-mode block (`:3857-3864`) and the tool-result truncation
(`:5968-6002`); `app.py` at `load_dotenv` (`:48`), the startup connect task (`:1068-1076`) and the
shutdown disconnect (`:1291-1296`); `src/builtin_mcp.py` at `builtin_python_env` (`:148-160`) and
the two `connect_server` call sites; `static/js/settings.js` at the MCP server panel
(`:4939-4980`); the SDK the manager drives — `mcp/client/stdio/__init__.py`
(`get_default_environment`, `stdio_client`), `mcp/client/streamable_http.py`
(`streamablehttp_client`, `streamable_http_client`), `mcp/client/session.py` and
`mcp/shared/session.py` (the read-timeout handling), `mcp/client/auth/oauth2.py` (the refresh
path); and the module's own tests for what is already pinned. SDK and anyio paths named in the
findings are the installed packages (`venv/lib/python3.12/site-packages/`: `mcp` 1.30.0, anyio
4.15.1, httpx 0.28.1), not files in the target tree.

**Not read:** `src/builtin_mcp.py` beyond `builtin_python_env` and the two `connect_server` call
sites; `mcp_servers/*`; the rest of `agent_loop.py`, `tool_execution.py`, `task_scheduler.py` and
`admin_tools.py`; `src/settings.py`; the MCP front end beyond the server panel; the SDK beyond the
functions named above; and every other section's paths. Line numbers are the working tree at
`2992bf6d368a` (clean apart from this run's untracked `audit/` directory).

**Checks run:** a throwaway MCP server (`/tmp/mcp_probe_server.py`, a FastMCP server declaring one
mutating tool with `readOnlyHint=False`, one tool that reports its own environment variable names,
and one that sleeps for 600s) driven by four probe scripts under `/tmp`, none of them part of the
target tree; each probe's output is quoted in the finding it settles. Also a direct call of
`_format_mcp_params` with malformed `required` values, a `grep` for timeouts in the callers, and a
uvicorn probe confirming that two requests run in two different tasks (each request is a
`RequestResponseCycle.run_asgi()` task; three requests produced three distinct task objects). The
18 suites matching this surface — the 17 files from `ls tests | grep -iE 'mcp'` plus
`tests/test_plan_mode.py`, which pins the classifier the annotation finding touches — were run:
**127 passed**.

#### [BUG] Nothing bounds an MCP session call, so a server that stops answering wedges whatever is waiting on it

- **Location:** `src/mcp_manager.py:511` (with `:202`, `:271`, `:359`, `:442-458`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the call path passes no timeout, and neither does the session it uses:

  ```python
  # :509-511
  async def _do_call(self, session, tool_name: str, arguments: Dict) -> Dict:
      """Execute a single MCP tool call and return result dict."""
      result = await session.call_tool(tool_name, arguments)
  ```

  All three `ClientSession` constructions omit `read_timeout_seconds` — `:202` (stdio), `:271`
  (SSE), `:359` (HTTP):

  ```python
  session = await stack.enter_async_context(ClientSession(read_stream, write_stream))   # :202
  ```

  The SDK reads that as "wait forever": `ClientSession.__init__(read_timeout_seconds: timedelta |
  None = None)` (`mcp/client/session.py:126`), and `send_request` only bounds the wait when a
  timeout exists (`timeout = None` … `with anyio.fail_after(timeout)`,
  `mcp/shared/session.py:283-291`); `call_tool` itself accepts a per-call
  `read_timeout_seconds` (`mcp/client/session.py:386-394`) that this code does not pass. The only
  timeout in the file is the startup one, applied by `connect_all_enabled` and nowhere else:

  ```python
  # :442-458
  async def _connect_with_timeout(self, srv):
      args = json.loads(srv.args) if srv.args else []
      env = json.loads(srv.env) if srv.env else {}
      try:
          await asyncio.wait_for(self.connect_server(...), timeout=20)
  ```

  Measured against a stdio server whose handshake succeeds and whose tool sleeps 600s:

  ```
  == 3. call with no answer ==
  call_tool still waiting after 5.0s; probe's own 5s bound fired
  == 3b. connect to a stdio server that never answers ==
  connect_server still waiting after 7.1s; probe's own 5s bound fired
  ```

  The callers add nothing: `grep -n 'wait_for\|timeout' src/tool_execution.py` returns nothing,
  and the scheduled-task call sites (`src/task_scheduler.py:1474`, `:2243`) await `call_tool`
  directly.
- **Impact:** a stdio or SSE server that accepts a request and never answers — a wedged process, a
  tool blocked on a resource, a server whose stdout reader died — leaves `call_tool` awaiting
  forever. The chat turn that made the call stalls with no error and no timeout, and the SSE stream
  stops producing events; the user's only exit is to close the tab, which cancels the tool task.
  The same path serves scheduled tasks (`src/task_scheduler.py:1474`, `:2243`), where there is no
  client to disconnect and the task simply stops progressing. The HTTP transport is partly covered
  by the httpx timeouts the SDK sets (`streamable_http.py:714-716`: 30s connect/read, 300s SSE
  read), so the exposure is stdio and SSE. The connect side matters for the admin routes too:
  `POST /api/mcp/servers` awaits `connect_server` with no bound, so a stdio server that never
  completes `initialize()` hangs that request.
- **Fix:** pass `read_timeout_seconds` to the three `ClientSession` constructions, or wrap
  `_do_call` in `asyncio.wait_for` with a configurable limit; the SDK raises `McpError` with code
  408 on timeout, which `call_tool` already turns into an error result. Give the route-facing
  connect path the same bound `_connect_with_timeout` gives the startup one.

#### [SECURITY] A stdio server with any configured env var receives the whole application environment

- **Location:** `src/mcp_manager.py:193`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the environment handed to the child depends on whether the row has any env vars at
  all, and the non-empty branch replaces the SDK's whitelist with everything:

  ```python
  # :190-194
  server_params = StdioServerParameters(
      command=command,
      args=args,
      env={**os.environ, **env} if env else None,
  )
  ```

  The SDK's default is deliberately narrow — `stdio_client` builds
  `{**get_default_environment(), **server.env} if server.env is not None else
  get_default_environment()` (`mcp/client/stdio/__init__.py:127`), and
  `get_default_environment()` returns only `HOME`, `LOGNAME`, `PATH`, `SHELL`, `TERM` and `USER`
  (`:28-45`). Passing `None` selects that whitelist; passing `{**os.environ, **env}` bypasses it.
  Measured with a stdio server whose tool returns its own `os.environ` names, in a process holding
  a canary variable:

  ```
  no stored env:      connected=True count=4  names=['HOME', 'LC_CTYPE', 'PATH', 'SHELL']
  one stored env var: connected=True count=22 names=['EMAIL_ADDRESS', 'HOME', …, 'PROBE_CANARY',
                                                     'PWD', 'SHELL', 'SHLVL', '_']
  ```

  (The fourth name in the first row is the child interpreter's own locale coercion, not the
  manager's doing.) `app.py:48` runs `load_dotenv(encoding="utf-8-sig")` at import, so every value
  the operator keeps in `.env` is in `os.environ` when a server is spawned; `.env.example`
  documents API keys, a search secret, an OAuth client secret and the admin password among them.
- **Impact:** an admin who adds a third-party stdio server and gives it the one variable it needs —
  an account name, an API key — also hands it every other secret in the process environment. The
  mitigation is real and lowers this to `low`: a stdio server is arbitrary code running as the app
  user, which the add-server route's own docstring states ("registering a stdio server is
  equivalent to executing arbitrary binaries on the host", `routes/mcp/mcp_routes.py:170-172`), so
  a hostile one could read the data directory and the encryption key anyway. What this adds is the
  secrets that exist only in the environment (a container `-e` value, a variable exported by the
  operator's shell) plus an exposure the SDK's default was written to prevent. The trap is the
  asymmetry: a server with no env config gets the whitelist, and adding one innocuous variable
  flips it to the entire environment.
- **Fix:** keep the full environment for the built-in servers, which read `PYTHONPATH` and the
  app's own variables (`src/builtin_mcp.py:148-160`), and let the SDK's whitelist stand for
  admin-added ones — `env={**os.environ, **env} if self.is_builtin(server_id) else (env or None)`.
  The cost: a third-party server that depends on an app environment variable would have to have it
  added to its own env config.

#### [BUG] A tool schema whose `required` is not an array raises in the prompt renderer and drops every MCP description

- **Location:** `src/mcp_manager.py:77`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `properties` is type-checked one line above; `required` is not, and `set()` on a
  number or a boolean raises:

  ```python
  # :74-79
  props = input_schema.get("properties")
  if not isinstance(props, dict) or not props:
      return ""
  required = set(input_schema.get("required") or [])
  parts = []
  ```

  Measured, both directly and through the entry point the prompt builder calls:

  ```
  $ venv/bin/python -c "from src.mcp_manager import _format_mcp_params, McpManager; ..."
  normal:        Args (JSON): {"path": string (required)}
  required=5:    TypeError: 'int' object is not iterable
  required=True: TypeError: 'bool' object is not iterable
  get_tool_descriptions_for_prompt -> TypeError 'int' object is not iterable
  ```

  Nothing between the server and this function checks the shape: discovery stores the server's
  `inputSchema` verbatim (`:212`, `:281`, `:368`), and the SDK types it only as a dict
  (`Tool.inputSchema`). The caller swallows the failure at DEBUG, so it leaves no visible trace:

  ```python
  # src/agent_loop.py:2747-2756
      if mcp_mgr:
          try:
              _mcp_desc = mcp_mgr.get_tool_descriptions_for_prompt(mcp_disabled_map or {})
              ...
          except Exception as _mcp_err:
              logger.debug(f"MCP description injection skipped: {_mcp_err}")
  ```

  The result is not cached on failure, so every later request fails the same way. This is the class
  the renderer's own docstring claims to have closed — "MCP servers are third-party, so names/types
  are sanitized and the parameter count + total length are capped (issue #2660)" (`:69-70`) — but
  the caps cover names and lengths, not the shape of `required`.
- **Impact:** one server declaring `"required"` as a number or boolean (a hand-written schema
  saying `"required": true` for a single parameter is the plausible mistake) removes the whole MCP
  tool-description block from the agent prompt on every request — for every server, not just that
  one — taking with it each tool's description, argument names and required flags, which is what
  issue #2509 added. The native function schemas are built by a separate method
  (`get_all_openai_schemas`) and still go out, so the model keeps the tool list but loses the
  argument hints. Only a DEBUG line records it, and the root logger is set to INFO
  (`app.py:95`), so the shipped setup never writes it.
- **Fix:** check the type instead of assuming it —
  `required = set(input_schema.get("required")) if isinstance(input_schema.get("required"), list)
  else set()` — and raise the caller's log level to WARNING when a server's schema costs the whole
  block.

#### [BUG] Streamable HTTP discovery drops each tool's read-only annotations, so plan mode classifies those servers by name alone

- **Location:** `src/mcp_manager.py:365-369`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the stdio and SSE discovery loops record the server's annotations (`:213-216`,
  `:282-285`); the HTTP loop does not:

  ```python
  # :364-369
  for tool in tools_result.tools:
      tools.append({
          "name": tool.name,
          "description": tool.description or "",
          "input_schema": tool.inputSchema if hasattr(tool, "inputSchema") else {},
      })
  ```

  `mcp_tool_is_readonly` reads exactly that key and prefers it over the name heuristic
  (`:107-133`): `readOnlyHint is True` → read-only, `readOnlyHint is False` or
  `destructiveHint is True` → write. `plan_mode_blocked_mcp` (`:623-637`) blocks every tool it
  classifies as a write, both from the schema list and by qualified name at runtime
  (`src/agent_loop.py:3857-3864`). Measured with one FastMCP server declaring a single mutating
  tool (`readOnlyHint=False`, `destructiveHint=True`) named `get_and_delete_all`, connected over
  both transports in the same probe:

  ```
  stdio  connected=True tool keys=['annotations', 'description', 'input_schema', 'name']
  stdio  mcp_tool_is_readonly=False plan_mode_blocked={'mcp__s_ann__get_and_delete_all', ...}
  http   connected=True tool keys=['description', 'input_schema', 'name']
  http   mcp_tool_is_readonly=True plan_mode_blocked={'mcp__s_ann__hang', 'mcp__s_ann__env_keys'}
  ```

  `tests/test_plan_mode.py:61-71` pins the classifier with annotations supplied directly, but no
  test pins what discovery stores per transport — `grep -rn annotations tests/*.py` finds no other
  MCP annotation test — so the drop is unguarded.
- **Impact:** for a remote Streamable HTTP server, plan mode loses the server's own declaration and
  falls back to the leading-verb heuristic, so a mutating tool whose name starts with `get`,
  `list`, `read`, `search`, `fetch`, `query`, `find`, `describe`, `show`, `view`, `lookup`,
  `count`, `status`, `info`, `inspect` or `summar` is offered to the model and allowed to run in
  the mode that promises read-only investigation. The same server over stdio or SSE is classified
  correctly, so the gate's behaviour depends on the transport the admin picked. Preconditions: plan
  mode on, an HTTP-transport server, and a mutating tool named with a read verb — which is why
  this is `low`, but the annotation is data the client already received and threw away.
- **Fix:** add the `annotations` key to the HTTP tool dict, as the other two transports do.

#### [ERROR-HANDLING] Disconnecting a server cannot close its transport, because the context was entered in another task

- **Location:** `src/mcp_manager.py:407-412`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the stored exit stack holds the SDK's transport context managers, which are anyio
  task groups and must be exited in the task that entered them; anyio raises otherwise
  (`anyio/_backends/_asyncio.py:463-467`). The manager closes the stack from whatever task calls
  it:

  ```python
  # :407-412
  stack = self._stacks.pop(server_id, None)
  if stack:
      try:
          await stack.aclose()
      except Exception as e:
          logger.warning(f"Error closing MCP server {server_id}: {e}")
  ```

  In the app the connect and the disconnect are always different tasks: each request runs as its
  own `RequestResponseCycle.run_asgi()` task (measured: three requests produced three distinct task
  objects under uvicorn), `add_server` connects, `delete_server`/`toggle_server`/
  `reconnect_server` disconnect, the startup task connects every enabled server
  (`app.py:1068-1076`) and shutdown disconnects them from another (`app.py:1294`). Measured with
  the connect and the disconnect each in their own task, as the request handlers run them:

  ```
  children after connect: [3994701]
  Error closing MCP server t1: Attempted to exit cancel scope in a different task than it was entered in
  children after disconnect from a different task: []
  manager state: {'status': 'disconnected'} | sessions: [] | stacks: []
  ```

  The same warning appears for an HTTP server (`Error closing MCP server h1: …`). The exception
  comes from `TaskGroup.__aexit__`'s final `cancel_scope.__exit__` call
  (`anyio/_backends/_asyncio.py:846-853`), after the group collected its own errors — so the
  group's `BaseExceptionGroup` is replaced by the ownership error and the transport's real errors
  are dropped. The scope is never exited; in a probe whose connecting task was still alive, a later
  await in that task raised `CancelledError: Cancelled via cancel scope <the same scope>`.
- **Impact:** every disconnect — delete, disable, reconnect, shutdown — logs a warning that reads
  like a failure ("Error closing MCP server …"), and the transport's task-group shutdown does not
  happen: its errors are discarded and its cancel scope stays registered in anyio's per-task state.
  The child process is still terminated, because the SDK's `stdio_client` generator runs its
  `finally` (closing stdin, then SIGTERM/SIGKILL) before the task group is exited, and the probe
  shows no child surviving the disconnect; this is not an orphan-process defect. What is lost is
  the log's meaning and any error the transport itself raised, plus the possibility of a stray
  cancellation in the connecting task if it is still running when the disconnect arrives. Whether a
  real startup or route sequence reaches that last case was not established.
- **Fix:** give each server an owner task that holds its exit stack and performs the close there
  (the pattern the SDK's transports require), or have `connect_server` hand back a close callback
  that runs inside the connecting task. Catching `RuntimeError` here would only silence the log and
  leave the scope unexited.

## 21. src: config, runtime, health and remaining modules

### Overview

The shared runtime layer: `src/constants.py` owns every data path and the app-wide limits,
`src/runtime_paths.py` resolves source vs. frozen app/data roots, `src/app_initializer.py`
constructs the managers and hardens the agent workspace, `src/app_helpers.py` holds the HTML
nonce injection and the path-confinement check, `src/config.py` is a pydantic settings tree,
`src/event_bus.py` turns app events into scheduled-task triggers, `src/service_health.py` builds
the admin health report, and `src/readiness.py`, `src/user_time.py`, `src/text_helpers.py`,
`src/reminder_personas.py`, `src/optional_deps.py`, `src/database.py` and `src/exceptions.py`
fill in readiness, user-local time, thinking-tag cleanup, reminder personas, optional-dependency
shims, and the `core` re-exports. `src/search/*` are compatibility shims that alias the
`services.search.*` implementations.

The boundary: the manager classes `app_initializer` constructs are defined in `src-memory-rag`,
`src-chat-session` and `src-email-integrations`; the health endpoint that calls
`service_health.collect_service_health` is `routes-rest`; the search implementation behind the
`src/search/*` shims is `services-search`; the schema and the auth/session state are
`core-data-platform` and `core-auth-session`.

### Coverage

**Read fully:** all 22 assigned files (1,982 lines): `src/service_health.py` (506),
`src/user_time.py` (235), `src/config.py` (208), `src/text_helpers.py` (195),
`src/app_initializer.py` (154), `src/constants.py` (133), `src/event_bus.py` (119),
`src/reminder_personas.py` (78), `src/app_helpers.py` (61), `src/readiness.py` (61),
`src/database.py` (37), `src/optional_deps.py` (32), `src/runtime_paths.py` (29),
`src/search/__init__.py` (29), `src/exceptions.py` (22), `src/search/ranking.py` (14),
`src/search/analytics.py` (12), `src/search/core.py` (12), `src/search/providers.py` (12),
`src/search/cache.py` (11), `src/search/content.py` (11), `src/search/query.py` (11).

**Read partially:** `services/search/core.py` at `update_search_config` (`:81-93`);
`services/search/providers.py` at `_get_provider_key` / `_get_search_instance` (`:45-75`);
`src/api_key_manager.py` at `save`/`load` (`:77-105`); `src/upload_handler.py` at the upload cap
and the live extension sets (`:217`, `:375-378`); `src/chat_helpers.py` at the attachment
extension set (`:232-244`); `app.py` at the auth-exempt list and the auth middleware
(`:259-470`), the config import and its use (`:581`, `:721`) and the `/api/ready` route
(`:988-997`); `routes/search/search_routes.py` at `setup_search_routes` (`:39-44`);
`routes/diagnostics_routes.py` at the health route (`:24-30`); `routes/cleanup/cleanup_routes.py`;
`src/cleanup_service.py` at its public functions and its only caller
(`routes/cleanup/cleanup_routes.py:5`); `specs/runtime.md`, `specs/persistence.md`,
`CONTRIBUTING.md` at the data-path rules, `.env.example` and the three `docker-compose*.yml`
files at their cleanup/env blocks.

**Not read:** the manager classes `app_initializer` constructs (assigned to their own sections);
the `services/search` implementation (assigned to `services-search`); the `routes-*` handlers
that consume these helpers beyond the cited regions; the front-end persona definitions beyond
the ID comparison cited in the coverage checks.

**Checks run:** four probes for the config crash (`SECURITY_ALLOWED_ORIGINS=https://example.com`,
`DATA_MAX_UPLOAD_SIZE=abc` and `LLM_REQUEST_TIMEOUT=30s` against `src.config`, and the first
against `import app`), the empty-`ODYSSEUS_DATA_DIR` probe, the unused-config grep
(`config.<field>` and `from src.config import` across the repo), the
`APIKeyManager.save`/`load` caller grep, the `CLEANUP_*` reader grep, and a persona-ID comparison
between `src/reminder_personas.py` and `static/js/presets.js` (identical today). Thirteen suites
were run over this surface — `tests/test_readiness.py`, `tests/test_user_time.py`,
`tests/test_strip_think.py`, `tests/test_strip_reasoning_prose_dataloss.py`,
`tests/test_service_health_collect.py`, `tests/test_service_health_chromadb.py`,
`tests/test_service_health_email.py`, `tests/test_service_health_ntfy.py`,
`tests/test_service_health_providers.py`, `tests/test_service_health_search.py`,
`tests/test_app_initializer_memory_vector_degraded.py`, `tests/test_runtime_paths.py`,
`tests/test_agent_state_dir_confinement.py` — **141 passed**.

#### [BUG] `src/config.py` is an unused settings tree that can still stop the server from starting

- **Location:** `src/config.py:20-128`, `:176`, `:208` (with `app.py:581`, `:721`, `routes/search/search_routes.py:39`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the module builds four `BaseSettings` trees and a global `AppConfig()` at import,
  and nothing reads a single field. `grep -rn 'config\.\(data\|llm\|search\|security\|debug\|log_level\)'`
  over `src/ routes/ core/ services/ app.py` returns nothing, and the only import of the module
  in the repository is `app.py:581`:

  ```python
  # ========= IMPORT CONFIG =========
  from src.config import config
  ...
  app.include_router(setup_search_routes(config))     # app.py:721
  ```

  The receiving function never touches its parameter — `grep -n 'config'
  routes/search/search_routes.py` finds only the path string `/api/search/config`, the
  `get_search_config()` call, and docstrings:

  ```python
  def setup_search_routes(config) -> APIRouter:      # routes/search/search_routes.py:39
  ```

  The values that *are* live live elsewhere: the upload cap is
  `get_chat_upload_max_bytes()` (`src/upload_handler.py:217`), the attachment extension set is
  defined in `src/chat_helpers.py:232-234`, and the dangerous-extension set is defined in
  `src/upload_handler.py:375-378` (which excludes `.py`/`.js`/`.sh`, while the dead
  `SecurityConfig.dangerous_extensions` at `src/config.py:112-118` blocks them).

  Because `app.py` imports the module, the parse runs on every startup — and it fails hard on
  plausible values for env vars that do nothing:

  ```
  $ SECURITY_ALLOWED_ORIGINS=https://example.com python -c "import app"
  pydantic_settings.exceptions.SettingsError: error parsing value for field "allowed_origins"
  from source "EnvSettingsSource"

  $ DATA_MAX_UPLOAD_SIZE=abc python -c "import src.config"
  pydantic_core._pydantic_core.ValidationError: 1 validation error for DataConfig
  max_upload_size
    Input should be a valid integer, unable to parse string as an integer

  $ LLM_REQUEST_TIMEOUT=30s python -c "import src.config"
  pydantic_core._pydantic_core.ValidationError: 1 validation error for LLMConfig
  request_timeout
    Input should be a valid integer, unable to parse string as an integer
  ```

  A list-valued field rejects a plain string (the natural way to write a CORS origin), and the
  integer fields reject unit-suffixed values; both abort the import, so the server never starts.
  Values that do parse are silently inert.
- **Impact:** two failure modes from the same dead module. An operator who sets any
  `DATA_*` / `LLM_*` / `SEARCH_*` / `SECURITY_*` variable — names that look like real knobs, and
  `SECURITY_ALLOWED_ORIGINS` in particular reads like the CORS setting — either gets no effect
  (if it parses) or a startup crash with a pydantic traceback (if it does not). The crash is
  caused by configuration the application never consults.
- **Fix:** delete `src/config.py`, the `app.py:581` import, the `app.py:721` argument, and the
  unused `config` parameter of `setup_search_routes`. If the tree is intended to be live, wire it
  to its consumers, document the exact env names, and keep the parsing tolerant of the shapes
  users actually write.

#### [BUG] `initialize_managers` logs that it loaded an API key from a store nothing writes and a call that discards it

- **Location:** `src/app_initializer.py:132-136` (with `services/search/core.py:81-93`, `src/api_key_manager.py:77`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the startup path reads the encrypted provider-key store, passes the key to a
  function that documents it ignores the argument, and logs success:

  ```python
  # Load and apply saved API keys
  saved_keys = api_key_manager.load()
  if "brave" in saved_keys:
      update_search_config(api_key=saved_keys["brave"])
      logger.info("Loaded Brave API key from saved configuration")
  ```

  The callee states the opposite:

  ```python
  def update_search_config(api_key: str = None, **kwargs):
      """... Provider API keys are intentionally NOT cached here. They are read on
      demand from settings/env via ``_get_provider_key`` ... ``api_key`` is accepted
      for backward compatibility but no longer stored."""
      for k, v in kwargs.items():
          if not _is_secret_key(k):
              SEARCH_CONFIG[k] = v
  ```

  `APIKeyManager.save` (`src/api_key_manager.py:77`) has no production caller:
  `grep -rn 'api_key_manager\.\(load\|save\)' src/ routes/ core/ services/ app.py` finds only
  `src/app_initializer.py:133`, and the only `APIKeyManager(...)` construction outside tests is
  `src/app_initializer.py:85`. The `save`/`load` round trip is exercised only by
  `tests/test_api_key_manager_atomic_save.py` and its siblings. The live key path is
  `settings.json` plus env vars via `services/search/providers.py:50-75`.
- **Impact:** the log line tells an operator the saved key was applied when the value was
  discarded; the `data/api_keys.json` store is never written, so the load can only ever be
  empty. A reader debugging "why is Brave search unauthenticated" is pointed at a store that is
  not part of the key path, and a future caller may treat `api_key_manager.save` as the way to
  persist provider keys.
- **Fix:** drop the `load()`/`update_search_config(api_key=...)` block (the keys already reach
  search through `_get_provider_key`), and delete `APIKeyManager.save`/`load` and their tests if
  the store is retired.

#### [BUG] An empty `ODYSSEUS_DATA_DIR` puts every store next to the working directory

- **Location:** `src/constants.py:12`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the data dir is read with the two-argument `getenv`, which returns the empty
  string when the variable is present but empty:

  ```python
  DATA_DIR = os.getenv("ODYSSEUS_DATA_DIR", get_default_data_dir())
  ```

  Measured:

  ```
  $ ODYSSEUS_DATA_DIR= python -c "from src import constants; ..."
  DATA_DIR: ''
  AUTH_FILE: 'auth.json'
  APP_DB: 'app.db'
  abspath AUTH_FILE: /home/lhl/github/lhl/odysseus/auth.json

  $ env -u ODYSSEUS_DATA_DIR python -c ...
  DATA_DIR: '/home/lhl/github/lhl/odysseus/data'
  ```

  The file already documents this exact trap and fixes it for the neighbouring variable, with a
  comment explaining that `os.getenv(name, default)` only returns the default when the variable
  is absent:

  ```python
  # `or` (not os.getenv's default arg) so a PRESENT-but-EMPTY value falls back to
  # the default. docker-compose.yml injects `FASTEMBED_CACHE_PATH=${FASTEMBED_CACHE_PATH:-}`,
  # which sets the var to "" when the host hasn't defined it. ... the empty string
  # would win → os.makedirs("") raises ...
  FASTEMBED_CACHE_DIR = os.getenv("FASTEMBED_CACHE_PATH") or os.path.join(DATA_DIR, "fastembed_cache")
  ```

  `CONTRIBUTING.md:101` states the intent this breaks: "`DATA_DIR` is the single place that reads
  `ODYSSEUS_DATA_DIR`, so use it directly only for dynamic paths that have no fixed name."
- **Impact:** an operator whose env file expands the variable to nothing (a `${ODYSSEUS_DATA_DIR}`
  reference with no value, a systemd `Environment=ODYSSEUS_DATA_DIR=`, or a Docker `-e` flag with
  no value) gets `DATA_DIR=""`, so `auth.json`, `app.db`, `settings.json` and every cache are
  created relative to the process working directory instead of the data directory. In the
  container that is `/app` — outside the mounted `./data` volume — so the instance comes up as a
  fresh install and the new state is lost when the container is recreated. Nothing warns: the
  paths are valid, just wrong.
- **Fix:** use the same `or` form as `FASTEMBED_CACHE_DIR`:
  `DATA_DIR = os.getenv("ODYSSEUS_DATA_DIR") or get_default_data_dir()`.

#### [DOC-DRIFT] `CLEANUP_INTERVAL_HOURS` and `CLEANUP_ENABLED` are documented, injected, and read by nothing

- **Location:** `src/constants.py:106-107` (with `.env.example:185-186`, `docker-compose.yml:56`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** both constants are parsed at import and never read:

  ```python
  CLEANUP_ENABLED = os.getenv("CLEANUP_ENABLED", "True").lower() == "true"
  CLEANUP_INTERVAL_HOURS = int(os.getenv("CLEANUP_INTERVAL_HOURS", "24"))
  ```

  `grep -rn 'CLEANUP_ENABLED\|CLEANUP_INTERVAL_HOURS' --include='*.py'` over the repository
  returns only these two definition lines. The knob is documented and plumbed anyway:
  `.env.example:185-186` ("# Cleanup interval in hours (default: 24)" /
  `# CLEANUP_INTERVAL_HOURS=24`) and all three compose files pass it into the container —
  `docker-compose.yml:56`, `docker-compose.gpu-nvidia.yml:67`, `docker-compose.gpu-amd.yml:68`,
  each as `CLEANUP_INTERVAL_HOURS=${CLEANUP_INTERVAL_HOURS:-24}`. The live session-cleanup entry
  points are the manual routes (`routes/cleanup/cleanup_routes.py:22-23`, `:38-39`), whose only
  service callers are `get_cleanup_preview` and `cleanup_sessions` in `src/cleanup_service.py`
  (`:161`, `:268`); nothing schedules them, and `specs/runtime.md:78`'s list of startup
  fire-and-forget work names
  upload cleanup but not session cleanup.
- **Impact:** an operator who sets `CLEANUP_INTERVAL_HOURS=6` in `.env` gets the default cadence
  they were trying to change, with no warning — the variable survives the whole trip into the
  container and dies at the constant. `CLEANUP_ENABLED=false` is the same: it is not in the
  compose files or `.env.example`, so it is only discoverable by reading this file, and it does
  nothing.
- **Fix:** either wire the constants into a cleanup loop, or delete them and the compose/.env
  lines. Leaving a documented env var that no code reads is the part that misleads.

## 22. routes: email

### Overview

The email feature's server surface: `routes/email_routes.py` (every `/api/email/*` handler —
inbox list, read, attachments, flag/move/delete, compose, send, draft, schedule, AI summary,
reply and translate, writing style, and the account and Google OAuth CRUD),
`routes/email_helpers.py` (the auth dependencies, account-config resolution, IMAP/SMTP
connection helpers, message parsing and attachment extraction, the `scheduled_emails` schema
and the owner-scoped cache tables) and `routes/email_pollers.py` (the scheduled-send poller
and the auto-summarize/reply/classify pass).

The boundary: the middleware that stamps `request.state.current_user` and the
`AuthManager` behind `owner_is_admin_or_single_user` are `core-auth-session` /
`routes-rest-auth-admin`; the `EmailAccount` table and its encryption are
`core-data-platform` / `src-security`; the MCP tool that stages `agent_draft` rows is
`mcp-servers`; the reader that renders the returned HTML is `static-js-documents-email`.
This section covers whether each route authenticates, scopes and offloads correctly, and
whether the credentials these helpers hold stay server-side — not whether the store
underneath is safe.

### Coverage

**Read fully:** all three assigned files (9,725 lines): `routes/email_routes.py` (6,152),
`routes/email_helpers.py` (2,008), `routes/email_pollers.py` (1,565).

**Read partially:** the boundary code the findings rest on — `src/auth_helpers.py` at
`get_current_user`/`effective_user` (`:11-38`); `src/tool_security.py` at
`owner_is_admin_or_single_user` (`:237-262`); `src/email_thread_parser.py` at the output
shape (`:14-22`) and `parse_thread` (`:605-614`); `src/task_scheduler.py` at
`RETIRED_HOUSEKEEPING_ACTIONS` (`:265-269`); `app.py` at the router construction
(`:860-864`); `static/js/emailLibrary.js` at `_sanitizeHtml` and its three call sites
(`:5826-5847`, `:6175`); the three `docker-compose*.yml` files and `.env.example` at
`ODYSSEUS_INPROCESS_POLLERS`; `specs/email-contacts.md:93`.

**Not read:** the auth middleware and `AuthManager` internals (assigned to
`core-auth-session` and `routes-rest-auth-admin`); `src/auth_helpers.py` below `:40` and
`src/owner_identity.py`; the `EmailAccount` model, its migrations and `src/secret_storage.py`
beyond the `encrypt`/`decrypt` call sites in these files (assigned to
`core-data-platform`); the MCP email server (assigned to `mcp-servers`); `scripts/odysseus-mail`
and the cron/systemd deployment path; the front end beyond the sanitizer cited above.

**Checks run:** a route-level probe that built the real router with `setup_email_routes()` and
(a) confirmed `require_owner`'s sub-dependency carries the `account_id` query parameter and
that a foreign `account_id` on `GET /api/email/list` reaches `_assert_owns_account`, (b) called
the `/accounts/test` coroutine with a JSON array and a JSON string body, (c) printed
`attachment_extract_dir` for two inputs; an event-loop stall measurement against a black-hole
IMAP listener, quoted in the `PERF` finding; an `import app` probe that printed the poller
state at startup, quoted in the first finding; a `grep` for the callers of `_send_email_sync`,
`_auto_summarize_poller` and `email_boundaries`; and the writer/caller greps cited in each
finding. Forty-three suites were run over this surface — every file matching
`ls tests | grep -iE 'email|mail|imap|smtp'`, from `tests/test_active_email_reply_guard.py`
and `tests/test_email_account_default_serialization.py` through `tests/test_imap_uid_commands.py`
and `tests/test_schedule_email_offset_normalization.py` — **269 passed**.

#### [BUG] The scheduled-send poller starts only when a client asks for the inbox list

- **Location:** `routes/email_pollers.py:1542-1565` (with `routes/email_routes.py:2370-2372`, `:1514`, `app.py:863`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `setup_email_routes()` calls `_start_poller()` (`routes/email_routes.py:1514`),
  and `app.py:863` calls that at import time, before uvicorn has a running loop. `_launch`
  therefore raises `RuntimeError` and the only remaining start path is a hook that a route
  has to await:

  ```python
  def _launch():
      global _poller_task, _summarize_task
      loop = asyncio.get_running_loop()
      if _poller_task is None:
          _poller_task = loop.create_task(_scheduled_email_poller())
          logger.info("Started scheduled email poller")
      _summarize_task = None

  try:
      _launch()
  except RuntimeError:
      # No running loop yet (import-time call). Retry on first request
      # by registering a one-shot startup coroutine.
      ...
      _start_poller._deferred = _deferred_start
  ```

  `grep -rn '_deferred' routes/ app.py src/` finds exactly one consumer of that hook, inside
  `GET /api/email/list`:

  ```python
  _deferred = getattr(_start_poller, '_deferred', None)
  if _deferred:
      await _deferred()
  ```

  Measured by loading the app the way uvicorn does:

  ```
  $ ODYSSEUS_DATA_DIR=/tmp/audit-email-probe-data venv/bin/python -c "import app; import routes.email_pollers as ep; ..."
  _poller_task after import        : None
  _start_poller._deferred set      : True
  running loop at import           : no
  ```

  Nothing else in the repository starts it: `grep -rn '_start_poller\|email_pollers' app.py`
  matches only the `setup_email_routes` import and call.
- **Impact:** the in-process task that delivers `scheduled_emails` rows does not exist until
  someone opens the email list. A server that restarts while no browser is connected — or an
  install driven through the API, the MCP tools or a mobile client — holds due rows
  indefinitely: the row stays `pending`, `GET /api/email/scheduled` shows it as scheduled, and
  the poller that would send it was never created. The same delay applies to a `/pending` agent
  draft the user approves, since approval only flips the row to `pending`. All three compose
  files default `ODYSSEUS_INPROCESS_POLLERS` to `1`, so this is the default deployment, and
  nothing logs that the poller never started.
- **Fix:** start the poller from the app's lifespan/startup hook (where a loop exists) instead
  of relying on a route to await the deferred starter, or keep the deferred hook and also call
  it from startup so the first request is not required.

#### [PERF] Nineteen `async def` handlers run blocking IMAP, SMTP or HTTP I/O on the event loop

- **Location:** `routes/email_routes.py:3304` (with `:3286`, `:3331`, `:3393`, `:3714`, `:3736`, `:3753`, `:3768`, `:3800`, `:3815`, `:3854`, `:3906`, `:3992`, `:4008`, `:4205`, `:4474`, `:5893`, `:5938`, `:6059`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** each cited line opens a connection or issues a command inside a coroutine that
  has not awaited anything, so the whole round-trip runs on the loop thread. The same file
  offloads identical work elsewhere — `:2391`, `:3216`, `:3966`, `:4767`, `:4829` and `:4919`
  use `asyncio.to_thread` — and two routes spell out why:

  ```python
  # routes/email_routes.py:2770-2772
  # Sync def: the body is blocking IMAP I/O with no awaits. As `async def` it ran
  # directly on the event loop and stalled the whole app during a search; as a sync
  # def FastAPI runs it in a threadpool, keeping the loop responsive.
  ```

  The six attachment handlers fetch the whole message inline (`_imap_uid_fetch(conn, uid,
  "(RFC822)")` at `:3288`, `:3306`, `:3333`, `:3395`, `:3716`, `:4207`), so their stall scales
  with message size; the flag/move/delete handlers each pay a `SELECT` plus a `STORE`/`MOVE`
  round-trip, and `resolve_contact` issues up to 200 serial header fetches per folder across
  three folders (`uids = data[0].split()[-200:]`, `:4484`; `conn.fetch(...)`, `:4487`).
  `test_account_config` connects and logs in to IMAP and SMTP inline (`_open_imap_connection`,
  `:5893`; `smtplib.SMTP_SSL`, `:5938`), and `google_oauth_callback` makes two blocking `httpx`
  calls (`:6059`, `:6081`). Measured with
  `ODYSSEUS_IMAP_TIMEOUT_SECONDS=3` and a listener that accepts and never sends an IMAP
  greeting, running the real `/accounts/test` coroutine next to a 50 ms heartbeat:

  ```
  endpoint returned in 5.03s: {'ok': False, 'imap': {'ok': False, 'error': 'timed out'}, 'smtp': None}
  heartbeat ticks before/during/after: 5; max gap between ticks: 5.08s
  ```

  The heartbeat made no progress at all for the duration of the call. The shipped IMAP timeout
  is 30 s by default (`routes/email_helpers.py:1149-1157`, clamped to 5-300 s) and the SMTP
  connect carries its own 10 s timeout, so one "Test connection" click on an unreachable host
  can stall every other request for tens of seconds; a 20 MB attachment fetch stalls the loop
  for as long as the mailbox takes to deliver it.
- **Impact:** while any of these handlers is running, every other request in the process —
  including a streaming chat turn and the SSE progress stream — is frozen. Any authenticated
  user can trigger the long ones repeatedly (one click each, no special privilege), and the
  attachment routes are on the normal reading path. The mitigation the file already applies to
  its sibling routes (`asyncio.to_thread`, or a sync `def` so FastAPI's threadpool runs it) is
  simply missing here.
- **Fix:** wrap the IMAP/SMTP/httpx work in `await asyncio.to_thread(...)` (or make the handler
  a sync `def`, as `search_emails` and `archive_email` already are).

#### [RACE] Attachment extraction is keyed on folder and UID only, so two mailboxes share one file path

- **Location:** `routes/email_helpers.py:685-696` (with the write at `:1618-1621` and the call sites `routes/email_routes.py:3313`, `:3345`, `:3415`, `:3452`, `:3722`, `:4212`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the directory name is built from the two request values and nothing else — the
  owner and the account are not part of the key:

  ```python
  key = re.sub(r"[^A-Za-z0-9._-]", "_", f"{folder}_{uid}") or "_"
  target = (ATTACHMENTS_DIR / key).resolve()
  ```

  Measured:

  ```
  attachment_extract_dir('INBOX', '5') -> /tmp/audit-email-probe-data/mail-attachments/INBOX_5
  attachment_extract_dir('../../etc', '5') -> /tmp/audit-email-probe-data/mail-attachments/.._.._etc_5
  ```

  (The traversal attempt is flattened and then re-checked against the base directory, so the
  containment claim in the docstring holds.) All six call sites pass `(folder, uid)`.
  `_extract_attachment_to_disk` writes the file with a truncating open and returns the path, and
  `download_attachment` hands that same path to `FileResponse`:

  ```python
  target_dir = attachment_extract_dir(folder, uid)          # :3313
  filepath = _extract_attachment_to_disk(msg, index, target_dir)
  ...
  return FileResponse(path=str(filepath), filename=filepath.name, media_type="application/octet-stream")
  ```

  (`routes/email_routes.py:3313-3323`; the elided lines are the not-found check.)

  Nothing locks the directory, and nothing deletes the file when the response finishes.
- **Impact:** two users whose mailboxes both have an `INBOX` and a message at the same UID and
  an attachment that sanitizes to the same filename map to one path. A request from the second
  user that lands between the first user's write and the end of its streaming response
  overwrites the bytes the first response is reading, so a response can carry the other user's
  attachment or a truncated one; `attachment_as_doc` reads the file after extracting it in the
  same window. Every mailbox has an `INBOX` and low UIDs, so the folder/UID half collides
  routinely; the filename must collide too, which is what keeps this low.
- **Fix:** include the account (and owner) in the directory key — `attachment_extract_dir(owner,
  account_id, folder, uid)` — so each mailbox extracts into its own directory.

#### [BUG] A process death mid-send leaves a scheduled email in `sending` forever, invisible to the UI

- **Location:** `routes/email_pollers.py:1421-1424` (with `:1480`, `:1488`, `routes/email_routes.py:4368`, `:4389`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the row is claimed before any work and only two paths change the status
  afterwards — success to `sent`, an in-process exception to `failed`:

  ```python
  claim_cur = claim_conn.execute(
      "UPDATE scheduled_emails SET status='sending' WHERE id=? AND status='pending'",
      (sid,),
  )
  ...
  conn2.execute("UPDATE scheduled_emails SET status='sent' WHERE id=?", (sid,))
  ```

  Nothing else reads or writes that state: `grep -rn "'sending'" routes/ src/ core/ scripts/`
  returns that one `UPDATE`. The list endpoint filters `status IN ('pending', 'failed')`
  (`routes/email_routes.py:4368`) and cancel deletes only `status = 'pending'` (`:4389`), and
  there is no age-based reaper.
- **Impact:** a process that dies between the claim and the completion (SIGKILL, OOM kill,
  container stop, power loss) leaves the message permanently in `sending`: it is never retried,
  never listed, never cancellable, and it never sends. The claim's own comment explains why the
  claim exists, but the recovery half is missing; a kill during a `docker compose restart` while
  a send is in flight is enough.
- **Fix:** at the start of each poll pass, reset rows whose `sending` state is older than a few
  minutes back to `pending` (a `sending_at` timestamp, or reuse `created_at`), and show
  `sending` rows in the list so the user can see the state.

#### [ERROR-HANDLING] `POST /api/email/accounts/test` answers 500 for a non-object JSON body

- **Location:** `routes/email_routes.py:5792-5803`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the `try` covers only the parse, and the next statement assumes a mapping:

  ```python
  try:
      body = await req.json()
  except Exception:
      return {"ok": False, "imap": {"ok": False, "error": "invalid request body"}}

  ...
  acc_id = body.get("account_id")
  ```

  Measured with the real route coroutine and a request whose `json()` returns the parsed body:

  ```
  body=[]: AttributeError: 'list' object has no attribute 'get'
  body='x': AttributeError: 'str' object has no attribute 'get'
  ```

  This is a recurrence of the class reported for three admin endpoints in
  `routes-rest-auth-admin.md`. It is the only occurrence here: the other JSON endpoints in these
  files take a `data: dict` parameter (FastAPI answers 422 for an array or a string) or a
  Pydantic model such as `SendEmailRequest`.
- **Impact:** an authenticated client that sends `[]` or `"x"` gets an unhandled traceback and a
  500 where this handler's own contract is `{"ok": False, "imap": {"ok": False, "error":
  "invalid request body"}}`. Not reachable from the shipped UI, so the cost is a confusing
  failure and a log line.
- **Fix:** after the parse, `if not isinstance(body, dict): return {"ok": False, "imap": {"ok":
  False, "error": "invalid request body"}}`.

#### [BUG] The attachment-metadata cache falls back to another account's row

- **Location:** `routes/email_routes.py:1234-1242`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the exact-account lookup is followed by one that drops `account_key`:

  ```python
  row = conn.execute(
      """
      SELECT attachments_json
      FROM email_attachment_metadata_cache
      WHERE owner=? AND account_key=? AND folder=? AND uid=?
      """,
      (owner or "", _account_cache_key(account_id, owner), folder, str(uid)),
  ).fetchone()
  if not row:
      row = conn.execute(
          """
          SELECT attachments_json
          FROM email_attachment_metadata_cache
          WHERE owner=? AND folder=? AND uid=?
          ORDER BY updated_at DESC
          LIMIT 1
          """,
          (owner or "", folder, str(uid)),
      ).fetchone()
  ```

  Every sibling cache read in the file keys on `owner` and `account_key` together (for example
  `_email_preview_cache_get`, `:1158-1183`).
- **Impact:** for one owner with two accounts, `/attachments/{uid}?folder=INBOX&account_id=B`
  returns account A's cached attachment list whenever B has no cached row for that UID — the
  chips show another mailbox's filenames, sizes and content types. The bytes come from the
  right message because `/attachment/{uid}/{index}` re-extracts from the requested account, so
  the user can click a chip whose name does not match what downloads. No cross-owner exposure:
  the owner predicate is still in the query.
- **Fix:** drop the fallback, or restrict it to legacy rows whose `account_key` is empty
  (`AND (account_key='' OR account_key IS NULL)`).

#### [FOOTGUN] The thread-turn cache is read by Message-ID with no owner scope, and its rows carry message bodies

- **Location:** `routes/email_routes.py:3074-3077` (with `routes/email_helpers.py:933-941`, `:566-573`, `:720`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the read selects a row by Message-ID alone:

  ```python
  _row3 = _c.execute(
      "SELECT sig_start, quote_start, turns_json FROM email_boundaries WHERE message_id = ?",
      (message_id.strip(),),
  ).fetchone()
  ```

  and `turns_json` is returned to the caller as `thread_turns`/`boundaries`. The table has no
  owner column:

  ```sql
  CREATE TABLE IF NOT EXISTS email_boundaries (
      message_id TEXT PRIMARY KEY,
      uid TEXT,
      folder TEXT,
      sig_start INTEGER,
      quote_start INTEGER,
      model_used TEXT,
      created_at TEXT NOT NULL
  )
  ```

  The payload is message content — each turn carries the body (`src/email_thread_parser.py:14-22`:
  `{"level": 1, "body_html": "...", "meta": "Alice <a@x> · May 5"}`). Every neighbouring
  Message-ID-keyed cache is owner-scoped for exactly this reason
  (`OWNER_SCOPED_EMAIL_CACHE_TABLES`, `routes/email_helpers.py:566-573`; the migration comment at
  `:720`: "Message-IDs are global, so AI-derived cache rows must be owner-scoped just like
  email_tags"), and `email_boundaries` is not in that set. Nothing in the current tree writes the
  table — `grep -rn 'email_boundaries' routes/ src/` finds the schema, the `turns_json`
  migration and this read, and the writer that used to populate it is gone
  (`mark_email_boundaries` is in `RETIRED_HOUSEKEEPING_ACTIONS`, `src/task_scheduler.py:265-269`)
  — so only rows written by an earlier release can be served.
- **Impact:** on an install upgraded from a release that populated the table, opening a message
  whose Message-ID matches a row written for another owner returns that owner's parsed thread
  text and fold offsets instead of parsing the caller's own copy. The cache's version check
  guards the parser version, not the owner. Low because nothing writes new rows and it needs a
  Message-ID collision (an attacker who sends the same Message-ID to two users can create one,
  but only for a row that predates the upgrade).
- **Fix:** add `owner` to the table and to this read (and to `OWNER_SCOPED_EMAIL_CACHE_TABLES`),
  or delete the cache read and always parse on the fly, which is what already happens for every
  message with no cached row.

#### [DEAD-CODE] Two background/send implementations have no callers, and the docstrings still describe them as live

- **Location:** `routes/email_routes.py:4245` (with `routes/email_pollers.py:1370`, `:8`, `:11-12`, `:1548`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `grep -rn 'send_email_sync'` over the whole repository returns only the
  definition, whose docstring says the opposite:

  ```python
  async def _send_email_sync(
      to, cc, bcc, subject, body, in_reply_to, references, attachments,
      account_id=None, owner="", odysseus_kind=None, odysseus_ref=None,
  ):
      """Shared send logic used by both /send and scheduled delivery.

      SECURITY: callers MUST pass `owner` (the authed user) so the config
      lookup is scoped — ...
  ```

  `/send` builds its own MIME message inline (`:4533-4540`) and the scheduled poller builds its
  own (`routes/email_pollers.py:1435-1442`). `_auto_summarize_poller`
  (`routes/email_pollers.py:1370`) is likewise unreachable: nothing calls it, `_launch` clears
  its handle (`_summarize_task = None`, `:1548`), and its own docstring already says it is
  "[k]ept for backward compatibility" (`:1371-1372`) — while the module docstring above it still
  advertises "driver that wakes the pass on a 30-min cadence" (`:8`), and `_start_poller`'s says
  it "spawns both pollers" (`:11-12`).
- **Impact:** a maintainer reading this section believes the auto-summarize pass runs on a
  30-minute timer (the live drivers are the `summarize_emails` scheduled task,
  `src/builtin_actions.py:1006`, and the new-mail path at `routes/email_routes.py:422-423`) and
  that `_send_email_sync` is the shared send path (it is never called, so a fix or a security
  change made there changes nothing at runtime — and its owner-scoping warning is not attached
  to either live copy).
- **Fix:** delete both, or delete the stale docstring lines; if `_send_email_sync` is meant to
  replace the two inline copies, wire `/send` and the poller to it.

## 23. routes: cookbook

### Overview

The model-lifecycle surface: `routes/cookbook_routes.py` (the Cookbook router — SSH key management,
remote server setup, model download and serve launch, cached-model scanning, GPU probing, PID
killing, the cookbook state file, and the task-status poller) and `routes/cookbook_helpers.py` (the
validators, runner-script builders and request models those routes use). Every endpoint here that
mutates state or starts a process calls `require_admin(request)` in its body; the read-only lookups
are only authenticated — the HuggingFace and Ollama browse endpoints take `Depends(require_user)`,
and the two vLLM-recipe endpoints rely on the session middleware alone, since nothing under
`/api/cookbook` is in the auth-exempt lists in `app.py` (`:264-296`).

The boundary: the middleware that authenticates the request and the `require_admin` guard are
`core-auth-session`; the `ModelEndpoint` rows these routes write and probe are `routes-models`; the
tmux log directory and session naming come from `routes-shell`; `routes/cookbook_output.py` (the
download classifiers the poller imports) is `routes-rest-media-files`; the agent tool and the
scheduled action that POST to `/api/model/serve` are `src-agent-tools` and
`src-research-scheduling`. This section covers whether each route validates what the client sends and
what the server then runs, not whether the stores or the tools underneath are correct.

### Coverage

**Read fully:** both assigned files (6,065 lines): `routes/cookbook_routes.py` (4,583),
`routes/cookbook_helpers.py` (1,482). Every cited line was re-read at `2992bf6d368a`.

**Read partially:** the callees the findings rest on — `routes/model_routes.py` at `_probe_endpoint`
(`:958-998`, the synchronous `httpx` probe of a base URL's `/v1/models`); `core/middleware.py` at
`require_admin` (`:57-82`); `app.py` at the auth-exempt lists (`:264-296`); `core/atomic_io.py` at
`atomic_write_json` (`:22-45`); `core/platform_compat.py` at `safe_chmod` (`:40-52`);
`routes/_validators.py` (the whole 31-line file: `validate_remote_host`, `validate_ssh_port`);
`src/constants.py` at `COOKBOOK_STATE_FILE` (`:32`); `services/hwfit/hardware.py` at `detect_system`
(`:792-816`) and its `_run` helper (`:27-45`); `src/tools/cookbook.py` at the `serve_model` HTTP call
(`:755-800`); `src/builtin_actions.py` at `action_cookbook_serve` (`:3151-3300`);
`src/task_action_policy.py` (`:1-40`); `static/js/cookbookServe.js` at `_isMiniMaxM3Model` (`:425-434`)
and the MiniMax M3 launch path (`:1440-1465`).

**Not read:** `routes/cookbook_output.py` (`error_aware_output_tail`, `classify_dead_download`), which
the status handler imports; the `ModelEndpoint` table definition and the endpoint CRUD routes in
`routes/model_routes.py` beyond `_probe_endpoint`; `src/secret_storage.py` beyond the two function
signatures; `src/host_docker_access.py`; `core/platform_compat.py` beyond `safe_chmod` and
`_ssh_exec_argv`; `src/task_scheduler.py`'s dispatch of the `cookbook_serve` action; the front end
beyond the two regions named above; and the `routes-*` / `src-*` sections that own the modules these
routes call.

**Checks run:** four throwaway probes under `/tmp` (not part of the target tree), plus the cookbook
suites. The probes were: the `/api/cookbook/setup` handler driven with a stub `ssh` on `PATH` and the
real shell, once per platform branch, with each captured command also replayed through `sh -c`
(first finding); `POST /api/model/serve` driven the same way with a placeholder token, then
`stat` on the runner script it wrote (fourth finding); `GET /api/cookbook/hf-gguf-files` with
`httpx.AsyncClient` replaced by a constructor that raises (fifth finding); and `_validate_serve_cmd`
called directly with the shipped GGUF prelude and a modified one (third finding).

Twenty-six suites were run over this surface — `ls tests | grep -iE 'cookbook'`, plus
`tests/test_task_cookbook_admin_gate.py`: `tests/test_cookbook_helpers.py`,
`tests/test_cookbook_diagnosis.py`, `tests/test_cookbook_error_feedback.py`,
`tests/test_cookbook_serve_lifecycle.py`, `tests/test_cookbook_endpoint_registration.py`,
`tests/test_cookbook_hf_token.py`, `tests/test_cookbook_deps_recipes.py`,
`tests/test_cookbook_dependency_completion_regression.py`, `tests/test_cookbook_cpu_only_serve.py`,
`tests/test_cookbook_dead_download_status.py`, `tests/test_cookbook_docker_access.py`,
`tests/test_cookbook_package_detection.py`, `tests/test_cookbook_gemma4_thinking_template.py`,
`tests/test_cookbook_local_serve_pid_winpid.py`, `tests/test_cookbook_remote_windows_diffusers.py`,
`tests/test_cookbook_agent_tool_ssh_validation.py`, `tests/test_codex_cookbook_admin_gate.py`,
`tests/test_builtin_actions_cookbook_serve_state.py`, `tests/test_task_cookbook_admin_gate.py`, and
the seven JS-string suites (`tests/test_cookbook_diagnosis_js.py`,
`tests/test_cookbook_download_toast_duration.py`, `tests/test_cookbook_error_tail_lines.py`,
`tests/test_cookbook_port_parsing_js.py`, `tests/test_cookbook_progress_signal_js.py`,
`tests/test_cookbook_same_host_server_profiles_js.py`, `tests/test_cookbook_windows_stop_tree_js.py`)
— **229 passed, 1 skipped**.

#### [BUG] The remote setup endpoint interpolates its install script into a shell command, so no platform receives the script it built

- **Location:** `routes/cookbook_routes.py:2911` (the Linux command), `:2889` (the Termux command), `:2881` (the Windows command), `:2919` (the success check)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** each branch builds a command string and hands it to a shell (`asyncio.create_subprocess_shell(cmd, ...)`, `:2914`), while the script it embeds carries quoting the local shell re-parses:

  ```python
          elif platform == "termux":
              setup_script = (
                  "pkg install -y python tmux 2>/dev/null; "
                  ...
                  "python3 -c 'from huggingface_hub import snapshot_download; print(\"OK\")'"
              )
              cmd = f"ssh {pf}{host} '{setup_script}'"          # :2889
          else:
              setup_script = (
                  "if ! command -v tmux >/dev/null 2>&1; then "
                  ...
                  "command -v tmux >/dev/null 2>&1 || echo 'WARNING: tmux missing and auto-install failed (need passwordless sudo). Install manually.'; "
                  ...
                  "python3 -c 'from huggingface_hub import snapshot_download; print(\"OK\")'"
              )
              cmd = f"ssh {pf}{host} '{setup_script}'"          # :2911
  ```

  The first inner `'` ends the outer quote, so the rest of the script is parsed as shell syntax; which
  token the parser trips on depends on the script (the `(` in the Linux branch's warning text,
  `print("OK")` in the Termux branch). Driving the endpoint with a stub `ssh` on `PATH` and the real
  shell, the Linux and Termux branches make the setup command a syntax error, so `ssh` is never
  invoked for it — yet the handler reports success, because `ok` is a substring test on the echoed
  output (`ok = "OK" in output`, `:2919`):

  ```
  ===== linux  (platform 'linux')
    endpoint: {'ok': True, 'platform': 'linux', 'output': "...python3 -c 'from huggingface_hub import snapshot_download; print(\"OK\")\'''"}
    local sh -c exit 2: syntax error near unexpected token `('
    ssh invocations: 2 — 'example.invalid echo %OS%' and 'example.invalid test -d /data/data/com.termux && echo termux || echo linux'
  ===== termux (platform 'termux')
    endpoint: {'ok': True, 'platform': 'termux', ...}
    local sh -c exit 2: syntax error near unexpected token `"OK"'
    ssh invocations: 2 — the same two platform probes
  ```

  The Windows branch (`:2881`) builds its command without the outer quotes — `ssh {pf}{host} {setup_script}`
  — so the local shell keeps parsing it: it strips the quotes around the `powershell -Command` payload
  and expands `$env:TEMP` and `$null` as its own (empty) variables. Capturing that command and
  replaying it with the same stub shows what the client would send:

  ```
  ssh receives: ARGV[1]=powershell   ARGV[2]=-Command
    ARGV[3]=New-Item -ItemType Directory -Force -Path :TEMP\odysseus-sessions | Out-Null; try { python --version } catch { Write-Host 'ERROR: Python not found — install from python.org'; exit 1 }; ... 2>
  ```

  `$env:TEMP` arrived as `:TEMP` and `2>$null` as `2>`, and OpenSSH joins those arguments into one
  command string, so the remote shell sees the `-Command` payload unquoted with `| Out-Null` and `;`
  at its own level. What a real Windows host does with that was not tested here; the local
  transformation was.
- **Impact:** the Cookbook "server setup" action — the one the app's own missing-binary message sends
  the operator to ("Install it with your OS package manager, or run Cookbook server setup for that
  server", `:232`) — installs nothing on a Linux or Termux remote and reports `ok: true` while doing
  it, so the operator learns otherwise only when the next download or serve fails with "tmux is
  required"; on a Windows remote the script arrives mangled. The mitigation is that the same message
  names the manual install, and the endpoint is admin-only.
- **Fix:** stop building a command string: pass an argv list with
  `asyncio.create_subprocess_exec("ssh", *ssh_args, setup_script, ...)`, which hands the script to ssh
  as one argument with no local shell to re-parse it. That also fixes the Windows branch, whose quotes
  and `$` references the local shell consumes today.

#### [HARDCODE] The MiniMax M3 normalizer rewrites the model argument to a snapshot path under a developer's home directory

- **Location:** `routes/cookbook_routes.py:666-672`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_normalize_minimax_m3_vllm_cmd` runs on every serve command that mentions `vllm serve` and `minimax`/`m3` (`:645-650`) and rewrites the model argument unconditionally:

  ```python
          repo_id = "cyankiwi/MiniMax-M3-AWQ-INT4"
          snapshot = (
              "/home/pewds/.cache/huggingface/hub/"
              "models--cyankiwi--MiniMax-M3-AWQ-INT4/"
              "snapshots/4082acbbec1236d21828d55b6bb0fe02ade4ab5b"
          )
          if body[serve_i + 1] == repo_id:
              body[serve_i + 1] = snapshot
  ```

  The rewritten command is what the runner script executes: the vLLM branch copies it into
  `ODYSSEUS_SERVE_CMD` (`:2349`) and the runner evals that variable (`:2705-2706`). The same absolute
  path is hardcoded in the front end (`static/js/cookbookServe.js:1457`), where `_isMiniMaxM3Model`
  (`:425-434`) matches any model whose identity text contains `minimax` and `m3`, and that constant
  becomes the model path the launch form sends (`:1458-1460`).
- **Impact:** a saved preset, a retry from a running row, or the agent's `serve_model` that submits
  `cyankiwi/MiniMax-M3-AWQ-INT4` has it replaced with a path that exists only on the machine the
  string was copied from, so vLLM fails on a missing local directory instead of loading the repo (and
  the model can no longer be downloaded on first launch). Every host except the author's is affected;
  the front-end constant makes the launch form send that same path for any MiniMax M3 row.
- **Fix:** delete the rewrite (and the front-end constant), or gate it on the snapshot directory
  existing on the target host (`Path(snapshot).is_dir()`), which is how the rest of the module guards
  cached-path rewrites.

#### [SECURITY] A serve command's GGUF prelude skips the metacharacter check the validator claims to apply

- **Location:** `routes/cookbook_helpers.py:767-773` (the prelude branch), `:786-787` (the check it skips), `:624-626` (the pattern)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the validator's docstring states the contract — "`req.cmd` is dropped verbatim into a bash/PowerShell wrapper script and executed in a tmux session. Without this gate, an admin (or anyone in the pre-fix world) could pass arbitrary shell payloads." — and the check that implements it runs only on the non-prelude path:

  ```python
      m = _GGUF_PRELUDE_RE.match(v)
      if m:
          rest = v[m.end():]
          for part in rest.split("||"):
              _check_serve_binary(part.strip())
          return v
      ...
      if any(c in cleaned_v for c in (";", "&&", "||", "$(")):
          raise HTTPException(400, "Invalid characters in cmd")
  ```

  `_GGUF_PRELUDE_RE` (`:624-626`) matches `MODEL_FILE=$(<anything but a newline>) && {...} || {...} &&`,
  so the body of the command substitution is unconstrained, and the prelude branch returns the command
  unchanged without running the metacharacter test. Measured by calling the validator directly:

  ```
  shipped prelude accepted: True
  crafted prelude ACCEPTED unchanged: True
  control: bare ';' rejected -> Invalid characters in cmd
  ```

  The crafted string (`MODEL_FILE=$(touch /tmp/...; echo x) && { ... } || { ... } && python3 -m
  llama_cpp.server ...`) was only validated, never executed, so nothing ran. `_check_serve_binary` is
  applied to `rest`, the part after the prelude, and its basename check passes for `python3`, so the
  payload reaches the runner script intact.
- **Impact:** for commands that start with the GGUF prelude the Cookbook UI itself emits for llama.cpp
  models, the `$(...)` body can carry `;`, `&&`, or a nested command substitution. The route calls
  `require_admin` (`:1972`), and `require_admin` also accepts the in-process internal tool token
  (`core/middleware.py:66-73`) — the path the scheduled `cookbook_serve` action uses
  (`src/builtin_actions.py:3267`). Both are admin-only today (`serve_model` is in
  `NON_ADMIN_BLOCKED_TOOLS`, `src/tool_security.py:73`; `cookbook_serve` is in
  `ADMIN_ONLY_TASK_ACTIONS`, `src/task_action_policy.py:5-10`) and an admin can run `bash` anyway, so
  this is a control that does not deliver what it claims rather than an escalation. What would settle
  whether it is more than that is whether any other caller reaches `/api/model/serve` with a
  non-admin-supplied `cmd`; the scheduler's dispatch was not audited here.
- **Fix:** validate the prelude's `$(...)` body against the same safe-subshell patterns the non-prelude
  branch already uses (`_SAFE_PRINTF_SUBSHELL_RE`, `_SAFE_FIND_MMPROJ_SUBSHELL_RE`) instead of only
  shape-matching the prelude.

#### [SECURITY] The HuggingFace token is written in cleartext to world-readable runner scripts that the serve path never removes

- **Location:** `routes/cookbook_routes.py:2165` and `:2729-2733` (the serve bash runner), `:2090-2091` and `:2118` (the serve PowerShell runner), `:1244` and `:1321-1325` (the remote download runner), `:1174` and `:1216-1217` (the remote download PowerShell runner), `:1116` and `:1363-1364` (the local download wrapper)
- **Severity:** low
- **Disposition:** next
- **Evidence:** every runner builder embeds the token in the script it writes into `TMUX_LOG_DIR`
  (`/tmp/odysseus-tmux`, `routes/shell_routes.py:498`), and the bash ones are made world-readable by
  `safe_chmod(..., 0o755)` (`core/platform_compat.py:40-52`):

  ```python
              if req.hf_token:
                  runner_lines.append(f"export HF_TOKEN='{_bash_squote(req.hf_token)}'")   # :2165
              ...
              runner_path = TMUX_LOG_DIR / f"{session_id}_run.sh"                        # :2729
              runner_path.write_text("\n".join(runner_lines) + "\n", encoding="utf-8")
              safe_chmod(runner_path, 0o755)                                             # :2733
  ```

  Measured by calling `POST /api/model/serve` with a stubbed subprocess and a placeholder token:

  ```
  endpoint: {'ok': True, 'session_id': 'serve-45554ef5', 'remote': 'local', 'endpoint_id': ...}
  new files in TMUX_LOG_DIR: ['serve-45554ef5_run.sh']
  dir mode: 0o755
  serve-45554ef5_run.sh: mode=0o755 world_readable=True token_present_in_file=True
     line: export HF_TOKEN='[REDACTED]'
  ```

  Nothing removes it: each flow deletes only the *remote* copy of its script (`rm -f {remote_runner}`,
  `:1319`; `Remove-Item -Force "$HOME\{remote_runner}"`, `:1215`) and the download flow's local
  wrapper deletes itself at the end of a successful run (`rm -f '{wrapper_script}'`, `:1361`), while
  the serve bash runner (`:2729-2733`), the serve PowerShell runner (`:2118`), the local copy of the
  remote download runner (`:1321-1325`) and its PowerShell twin (`:1216-1217`) stay in place; the
  PowerShell ones get no explicit mode and take the umask default. Nothing in the tree reads these
  files, so nothing reaps them.
- **Impact:** on a host with more than one local account, any user can list `/tmp/odysseus-tmux` and
  read the administrator's HuggingFace token out of a runner script — permanently for serve tasks,
  and for every download that leaves a local copy of its remote runner behind. The documented
  deployment is a single-user container, where this exposes nothing; the risk is a native multi-user
  install. The same module locks its SSH private key to `0o600` (`safe_chmod(key_path, 0o600)`,
  `:956`), so the token files are the outlier.
- **Fix:** write the runner with mode `0o600` and invoke it as `bash <path>` in the tmux command (the
  execute bit is not needed), or pass the token through the tmux environment instead of the script,
  and delete the local runner when the task ends.

#### [ERROR-HANDLING] `hf_gguf_files` raises `NameError` in its own error path, turning an API failure into a 500

- **Location:** `routes/cookbook_routes.py:3885`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the handler is declared `hf_gguf_files(repo_id: str, owner: str = Depends(require_user))` (`:3868`) and its `except` block logs a name that does not exist in that scope:

  ```python
          except Exception:
              logger.exception("HF GGUF file scan failed for %s", repo)
              return {"ok": False, "files": [], "error": "HF API request failed"}
  ```

  `repo` is not a module-level name and is never assigned in this function (the only `repo` in the file
  is the parameter of `vllm_recipe`, `:4081`). Measured by calling the endpoint with
  `httpx.AsyncClient` replaced by a class that raises on construction:

  ```
  raised out of the handler: NameError name 'repo' is not defined
    File ".../routes/cookbook_routes.py", line 3885, in hf_gguf_files
      logger.exception("HF GGUF file scan failed for %s", repo)
  NameError: name 'repo' is not defined. Did you mean: 'repr'?
  ```

  The `return {"ok": False, ...}` the handler wrote never runs.
- **Impact:** any HuggingFace API failure — network error, timeout, DNS — on
  `GET /api/cookbook/hf-gguf-files` produces an unhandled 500 and a traceback instead of the JSON error
  the handler intends, and the log line loses the repo id it was meant to record. The endpoint is
  authenticated-only and read-only, so the cost is a confusing failure rather than a broken flow.
- **Fix:** log `repo_id`.

#### [DUP] `_diagnose_serve_output` exists twice and has already drifted; the route runs the copy the tests do not cover

- **Location:** `routes/cookbook_routes.py:432-599` (the copy that runs), `:58` (the import it shadows), `routes/cookbook_helpers.py:1252-1445`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `cookbook_routes.py` imports the helper and then redefines it inside `setup_cookbook_routes()`:

  ```python
      _diagnose_serve_output, run_ssh_command_async,           # :58
      ...
      def _diagnose_serve_output(text: str) -> dict | None:    # :432
  ```

  so the nested definition wins for every handler in the module, and the only production call site is
  the status poller (`:4557`); nothing outside that scope calls the imported name. Comparing the two
  `patterns` tables (`ast.literal_eval` on each `patterns = [...]` assignment, then keying by pattern):

  ```
  helpers entries: 27   routes entries: 23   shared keys: 23
  keys only in routes: none
  shared keys whose suggestion list differs: 0
  keys only in helpers: 4
    'There is no module or parameter named ['\"]lm_head\.input_scale['\"]|lm_head\.input_scale|weight_scale_2'
        -> vLLM cannot load this ModelOpt LM-head quantized checkpoint with the current runtime.
    'mflux-generate-qwen.*not found|mflux-generate.*not found|MLX image serving requires mflux|No module named ['\"]?mflux'
        -> MLX image serving requires mflux on this Apple Silicon server.
    'mlx-lama-swift|odysseus-mlx-inpaint|mlx-lama-serve|LaMa / MI-GAN MLX inpainting models require'
        -> LaMa / MI-GAN MLX inpainting requires an Odysseus-compatible mlx-lama-swift bridge on this Apple Silicon server.
    'mlx-ddcolor-swift|odysseus-mlx-colorize|mlx-ddcolor-serve|DDColor MLX models require'
        -> DDColor MLX colorization requires an Odysseus-compatible mlx-ddcolor-swift bridge on this Apple Silicon server.
  ```

  The two suites that pin this function import the helpers copy (`tests/test_cookbook_diagnosis.py:1`,
  `tests/test_cookbook_error_feedback.py:1`), so they exercise the copy the route does not use.
- **Impact:** the table the running server uses is missing exactly the four patterns above, so a serve
  failure in those four classes (the ModelOpt LM-head checkpoint, mflux image serving, and the two MLX
  bridges) gets no diagnosis or retry suggestion from the status poller or from the agent's
  `list_served_models`, while the helper — the copy the tests read — would produce one; and a later
  edit to the helper will not reach the running server. Nothing fails loudly; the tables just differ.
- **Fix:** delete the nested definition and let the import stand (or move the union of the two tables
  into the helper and import it), so the tests and the route exercise one object.

#### [PERF] The serve launch path runs synchronous SSH and HTTP probes on the event loop

- **Location:** `routes/cookbook_routes.py:2048` (and its `subprocess.run` at `:1627`), `:1946` (and `:1878`), `:1737`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `model_serve` is `async def` (`:1962`) and calls three synchronous blockers inline:

  ```python
              _ollama_chosen_port = _pick_free_port_for_ollama(       # :2048
                  remote, req.ssh_port, start_port=11434, max_offset=10,
              )
  ```
  ```python
                  r = subprocess.run(                                   # :1627, inside the sync helper
                      ssh_base + [host_arg, script],
                      capture_output=True, text=True, timeout=8,
                  )
  ```
  ```python
              endpoint_id = _auto_register_llm_endpoint(req, remote)  # :2792
              ...
                      probed = _probe_endpoint(base_url, None, timeout=5)   # :1946
  ```

  `_probe_endpoint` is synchronous and issues `httpx.get(...)` against the new endpoint's `/v1/models`
  (`routes/model_routes.py:958-998`), and the crash watchdog — an `async def` scheduled on the same
  loop (`:2806`) — blocks it again with `urllib.request.urlopen(probe_url, timeout=3)` (`:1737`).
  Sibling code in the same file offloads the identical pattern: `await asyncio.to_thread(_cookbook_tasks_status_sync)`
  (`:4214`), whose docstring gives the reason ("every subprocess.run inside this handler is a sync
  blocking call that — when this was a plain async def — froze the entire server event loop"), and
  `await asyncio.to_thread(_fetch_sync)` (`:4048`, `:4112`).
- **Impact:** an administrator launching a remote Ollama serve stalls every other in-flight request for
  up to about 8 s (the SSH port probe) plus up to 5 s per endpoint probe, a streaming chat turn
  included. The route is admin-only and infrequent, so this is a stall rather than an outage.
- **Fix:** wrap `_pick_free_port_for_ollama`, `_auto_register_llm_endpoint` /
  `_auto_register_image_endpoint` and the watchdog's reachability probe in `await asyncio.to_thread(...)`,
  matching the status handler.

## 24. routes: chat and session

### Overview

The core chat and session surface: `routes/chat_routes.py` (`POST /api/chat`, the SSE
`POST /api/chat_stream` with its `/api/chat/resume`, `/api/chat/stop` and
`/api/chat/stream_status` companions, `POST /api/rewrite`, `POST /api/inject_context` and
`GET /api/search`), `routes/session_routes.py` (session create, list, rename, archive,
star, compact, export, delete and bulk delete, the admin `DELETE /api/sessions/all` wipe,
and the AI folder tidy), and `routes/chat_helpers.py`, the shared context builder,
privilege gate and post-response task runner those routes call.

The boundary: the context builder the routes hand off to is `src-chat-session`
(`src/chat_processor.py`, `src/chat_helpers.py`); the agent loop is `src-agent-loop`; the
streaming client and provider fallback are `src-llm-core`; the session cache and message
store are `core-auth-session`; the tables are `core-data-platform`; the middleware that
authenticates the request and stamps `request.state.current_user` is `AuthMiddleware` in
`app.py` (`build-install-deploy`), and the `require_admin` gate one endpoint here uses is
`core-auth-session` (`core/middleware.py:57`); the browser end of the stream is
`static-js-chat`. This section covers whether each endpoint resolves a session against the
authenticated owner before it reads or mutates it, what the stream does on failure and on
disconnect, and what deletion and pruning leave behind — not whether the store or the loop
underneath is correct.

### Coverage

**Read fully:** all three assigned files (5,478 lines): `routes/chat_routes.py` (2,829),
`routes/session_routes.py` (1,386), `routes/chat_helpers.py` (1,263). Line numbers refer to
`2992bf6d368a`.

**Read partially:** the boundary code the findings rest on — `core/session_manager.py` at
`get_session`/`_load_session_from_db` (`:421-524`), `sync_session_metadata` (`:454-498`),
`replace_messages` (`:353-400`), `create_session` (`:541-578`), `delete_session`
(`:587-627`) and `get_sessions_for_user`/`save_sessions` (`:700-710`);
`src/auth_helpers.py` at `get_current_user`/`effective_user` (`:10-36`),
the delegated-credential predicate (`:44-55`) and `require_api_token_scope` /
`require_chat_api_token_scope` (`:60-80`); `src/agent_runs.py` end to end (the
detach/subscribe/evict machinery behind the stream); `src/chat_processor.py` at
`build_context_preface` (`:263-470`); `src/chat_helpers.py` at
`coerce_message_and_session` (`:251-316`); `src/upload_handler.py` at `reserve_upload`
(`:864-965`); `src/session_image_cleanup.py` (`:23-121`); `src/chatgpt_subscription.py` at
`fetch_available_models` (`:90-120`); `src/session_actions.py` at
`is_session_recently_active` (`:42-52`); `src/tool_security.py` at
`owner_is_admin_or_single_user` (`:237-262`); `src/tool_execution.py` at `vet_workspace`
(`:466-491`); `src/llm_core.py` at the `llm_call` definition (`:1969`);
`services/search/core.py:250` and `services/search/content.py:181` (definition lines);
`app.py` at the auth-exempt lists (`:264-296`), the exception handlers (`:617-629`), the
session-router mount (`:683`) and the uvicorn launch (`:1306`); `static/js/sessions.js` at
the incognito cleanup helpers (`:261-267`, `:1083`), the list request (`:1682-1684`) and
session materialization (`:2276-2300`); `tests/test_session_list_owner_scope.py` and
`tests/test_archived_sessions_model_filter.py` (the harnesses the first and third findings
quote).

**Not read:** the middleware itself (`core/middleware.py`); the models and the
session/message tables (`core/database.py`); the agent loop (`src/agent_loop.py`); the LLM
streaming path and provider fallback (`src/llm_core.py` beyond the one definition line);
the compactor and preprocessor (`src/context_compactor.py`, `src/chat_handler.py`); the
research handler; the memory, RAG and search stores behind the context preface; the front
end beyond the cited lines; and the other `routes-*` sections.

**Checks run:** three throwaway probes under `/tmp` (a two-owner incognito-purge probe
built on the `tests/test_session_list_owner_scope.py` harness; a probe that calls the three
handlers with a list/string body; a loop-stall measurement for an inline synchronous
`httpx.get`), a double-`setup_session_routes` closure probe, a `grep` for `to_thread` in
the three files and for the `setup_session_routes` call sites, and the 55 suites matching
`ls tests | grep -iE 'chat|session'` — **1 failed, 289 passed**. The failure is the subject
of the third finding and is reproducible as a pair.

#### [SECURITY] The session list deletes every owner's incognito rows, not just the caller's

- **Location:** `routes/session_routes.py:269-277` (with `:250-251`, `:280`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `list_sessions` resolves the caller at `:251` and then purges incognito
  rows without ever using it. The only row the query excludes is the one named in the
  caller's own `active_incognito_id` query parameter:

  ```python
  @router.get("/sessions")
  def list_sessions(request: Request):
      user = effective_user(request)
      active_incognito_id = str(request.query_params.get("active_incognito_id") or "").strip()
      ...
              _ghosts = _purge_db.query(DbSession).filter(
                  DbSession.name.in_(("Nobody", "Incognito")),
                  DbSession.created_at < _cutoff,
              ).all()
              for _g in _ghosts:
                  if active_incognito_id and _g.id == active_incognito_id:
                      continue
                  _purge_db.query(_DbMsg).filter(_DbMsg.session_id == _g.id).delete()
                  _purge_db.delete(_g)
                  if hasattr(session_manager, "delete_session"):
                      try:
                          session_manager.delete_session(_g.id)
  ```

  An incognito session is an ordinary owned row: the browser creates one through
  `POST /api/session` with the name `Nobody` (`static/js/sessions.js:2284`), and that route
  stamps `owner=user` from `effective_user(request)` (`routes/session_routes.py:468`). The
  front end sends `active_incognito_id` only for the session it is currently in
  (`static/js/sessions.js:1682-1684`), so the exemption protects the caller and nobody
  else.

  Measured with the two-owner harness from `tests/test_session_list_owner_scope.py`
  (temporary SQLite database, both rows named `Nobody`, both older than the 10-minute
  cutoff, caller = alice):

  ```
  $ ODYSSEUS_DATA_DIR=/tmp/odysseus_probe_data venv/bin/python /tmp/probe_incognito_purge.py
  caller                : alice (cookie user)
  alice incognito row   : DELETED
  bob incognito row     : DELETED
  bob incognito message : DELETED
  session_manager.delete_session calls: 2
  ```

  The `delete_session` call widens the damage: it unlinks the session's generated image
  files and detaches its documents (`core/session_manager.py:591-600`, reached through
  `src/session_image_cleanup.py:84-121`), and it drops the in-memory copy from the shared
  session cache. No test pins this behaviour: `grep -rn 'Nobody\|Incognito' tests/*.py`
  exits 1 with no output.
- **Impact:** on any instance with more than one account, one user's sidebar load destroys
  another user's incognito chat. Bob's row and messages are gone and the cached session
  object is gone, so his next message is refused by `_verify_session_owner`
  (`routes/session_routes.py:104-131`) with a 404 even though his transcript is still
  sitting in the process-local `_INCOGNITO_CONTEXTS` map (`routes/chat_helpers.py:60-100`)
  that only that session id can reach. Any chat-scoped bearer token reaches the same
  endpoint through the router dependency. The victim has to have been in the incognito
  session for more than ten minutes (`created_at < utcnow - 10min`), which is the ordinary
  case for a conversation worth having; a shorter session is spared.
- **Fix:** filter the purge by the caller — `DbSession.owner == user`, with the
  null-owner branch when `user` is None — and keep the `active_incognito_id` exemption for
  the caller's own live session.

#### [PERF] The chat path runs synchronous LLM, web-search and URL-fetch calls on the event loop

- **Location:** `routes/chat_helpers.py:737` (with `routes/chat_routes.py:607`, `:799`, `:1258`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `build_chat_context` is an `async def` and calls the context builder
  inline, with no thread:

  ```python
  preface, rag_sources, web_sources = chat_processor.build_context_preface(**_preface_kwargs)
  ```

  `build_context_preface` is a plain `def` (`src/chat_processor.py:263`) and makes three
  blocking network calls inside it:

  ```python
  generated_query = llm_call(                              # :404, timeout=15
  ...
  web_context, web_sources = comprehensive_web_search(     # :446
  ...
  result = fetch_webpage_content(url)                      # :466, timeout=5
  ```

  All three are synchronous clients — `src/llm_core.py:1969`,
  `services/search/core.py:250`, `services/search/content.py:181`. The callers are
  `async def chat_endpoint` (`routes/chat_routes.py:772`) and `async def chat_stream`
  (`:963`), which run on the single uvicorn worker the app starts
  (`app.py:1306`: `uvicorn.run(app, host=bind_host, port=bind_port, log_level="info")`,
  no `workers=`).

  The URL loop fires for any message that carries a non-YouTube URL (message under 2000
  characters, at most three URLs), so pasting a link into the composer is enough;
  `use_web=true` adds the query-generation `llm_call` and the search. Measured stall for
  the same call shape (a synchronous `httpx.get` against a local server that sleeps 1.0s,
  with a ticker task on the loop):

  ```
  $ venv/bin/python /tmp/probe_blocking_fetch.py
  inline (no thread)   elapsed=1.02s  ticker iterations=48
  asyncio.to_thread    elapsed=1.01s  ticker iterations=995
  ```

  A second site in the same route does it again: `_recover_empty_session_model` calls
  `fetch_available_models(api_key)` at `routes/chat_routes.py:607`, which is
  `httpx.get("https://chatgpt.com/...", timeout=10.0)` (`src/chatgpt_subscription.py:90-98`),
  and it is called inline from both async handlers (`:799`, `:1258`). Sibling modules in
  this repository offload the same shape — `routes/auth_routes.py:140`, `:160`, `:171`,
  `:181`, `routes/email_routes.py:2391`, `:2466` — and none of the three files in this
  section does: `grep -n 'to_thread\|run_in_executor' routes/chat_routes.py
  routes/session_routes.py routes/chat_helpers.py` returns nothing.
- **Impact:** during a link-prefetch or web-search turn the loop cannot schedule anything
  else: other users' SSE heartbeats stall, `/api/health` and `/api/ready` stop answering,
  and a second chat turn waits behind the first. The stall lasts as long as the blocking
  calls take — up to 15s for the query LLM plus the search and up to 5s per URL fetch, or
  up to 10s for the ChatGPT-subscription catalog fetch. Nothing in the section's suites
  covers the blocking shape.
- **Fix:** `await asyncio.to_thread(chat_processor.build_context_preface, **_preface_kwargs)`,
  and wrap the `fetch_available_models` call the same way. The cleaner version moves the
  synchronous I/O inside `src/chat_processor.py` onto awaitable helpers, but the two call
  sites are enough to stop the stall.

#### [BUG] `setup_session_routes` appends to a module-level router, so a second call's handlers never serve

- **Location:** `routes/session_routes.py:134` (with `:237`, `:250`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the router is built at import and every call to the factory decorates that
  same object and returns it:

  ```python
  router = APIRouter(                                     # :134
      prefix="/api",
      tags=["sessions"],
      dependencies=[Depends(require_chat_api_token_scope)],
  )
  ...
  def setup_session_routes(                               # :237
      session_manager: SessionManager,
      config: dict,
      ...
      @router.get("/sessions")                            # :250
      def list_sessions(request: Request):
  ```

  Each call therefore registers a second full copy of the handler set, each closing over
  the `session_manager` and `config` of that call. Starlette matches in registration
  order, so the first call's closures are the ones that serve. Measured by calling the
  factory twice with distinguishable `MagicMock` managers:

  ```
  $ venv/bin/python - <<'PY'
  returned router is the module-level object: True True
  distinct session_manager closures on /api/sessions: 2
  first handler closes over the FIRST manager: True
  second handler closes over the SECOND manager: True
  ```

  The sibling factory builds its router inside the function
  (`routes/chat_routes.py:763`), which is why the same double-call there is harmless.

  The repository's own suite already fails on this. Four test modules call
  `setup_session_routes`; `tests/test_archived_sessions_model_filter.py` runs first
  alphabetically, registers its `MagicMock()` manager, and
  `tests/test_session_list_owner_scope.py` then picks
  `next(r.endpoint for r in router.routes ...)`, which is the earlier file's handler:

  ```
  $ venv/bin/python -m pytest -q tests/test_archived_sessions_model_filter.py tests/test_session_list_owner_scope.py
  1 failed, 4 passed
  $ venv/bin/python -m pytest -q tests/test_session_list_owner_scope.py
  2 passed
  ```

  Production has one call site (`app.py:683`), so no request is served by a stale handler
  today.
- **Impact:** the factory's contract is not what it appears to be: the router returned by
  the second call does not use the manager it was given, and its routes are unreachable.
  Today that costs one red test in the section's own suite and depends on test file order
  to appear; the next caller that builds a session router — a second entry point, an
  embedded mode, another test — gets a silently misconfigured one.
- **Fix:** move `router = APIRouter(...)` inside `setup_session_routes` and return it, as
  `routes/chat_routes.py` does, or raise when the factory is called twice.

#### [ERROR-HANDLING] Three chat and session endpoints raise an unhandled `AttributeError` on a non-object JSON body

- **Location:** `routes/chat_routes.py:989` (`chat_stream`), `:2731` (`rewrite_message`),
  `routes/session_routes.py:582` (`inject_messages`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** each handler reads the body and calls `.get` on whatever came back:

  ```python
  body = await request.json()                             # chat_routes.py:969
  ...
  selected_endpoint_id = str(
      form_data.get("selected_endpoint_id")
      or (body or {}).get("selected_endpoint_id")         # :989
      or ""
  ).strip()
  ```
  ```python
  body = await request.json()                             # chat_routes.py:2727
  ...
  session_id = body.get("session_id")                     # :2731
  ```
  ```python
  body = await request.json()                             # session_routes.py:581
  messages = body.get("messages", [])                     # :582
  ```

  Measured by calling the three handlers with a request whose `json()` returns the
  payload, the harness style of `tests/test_integrations_store_shape.py`:

  ```
  $ venv/bin/python /tmp/probe_nondict_bodies.py
  POST /api/chat_stream  body=[1,2]  : AttributeError: 'list' object has no attribute 'get'  (raised at chat_routes.py:989)
  POST /api/chat_stream  body=[]     : HTTPException: 400: {'error': 'REQUEST_PROCESSING_ERROR', ...}  (raised at chat_routes.py:1153)
  POST /api/chat_stream  body="x"    : AttributeError: 'str' object has no attribute 'get'  (raised at chat_routes.py:989)
  POST /api/rewrite      body=[]     : AttributeError: 'list' object has no attribute 'get'  (raised at chat_routes.py:2731)
  POST /api/rewrite      body=[1,2]  : AttributeError: 'list' object has no attribute 'get'  (raised at chat_routes.py:2731)
  POST /api/session/x/inject_messages body=[]: AttributeError: 'list' object has no attribute 'get'  (raised at session_routes.py:582)
  POST /api/session/x/inject_messages body="x": AttributeError: 'str' object has no attribute 'get'  (raised at session_routes.py:582)
  ```

  `app.py` registers handlers for `SessionNotFoundError`, `InvalidFileUploadError`,
  `LLMServiceError` and `WebSearchError` (`app.py:617-629`) and none for a generic
  exception, so the `AttributeError` reaches the client as a 500. This is a recurrence of
  the class reported for three admin endpoints in `routes-rest-auth-admin.md`
  (`routes/auth_routes.py:329`, `:784`, `:794`). Two siblings in these files already keep
  the contract: `bulk_delete_sessions` wraps its parse in `try/except`
  (`routes/session_routes.py:619-622`), and `chat_stream`'s own JSON parse answers 400
  (`routes/chat_routes.py:966-975`).
- **Impact:** an API client that sends a JSON array or string to one of these endpoints
  gets a 500 and an unhandled traceback where the rest of the surface answers 400;
  `POST /api/rewrite` is the worst of the three, because an empty array is enough. The
  shipped UI always sends an object, so the cost is a confusing failure and a log line.
- **Fix:** add the `isinstance(body, dict)` guard used by `routes/backup_routes.py:73` to
  the three handlers after each `await request.json()`.

## 25. routes: model serving

### Overview

The model-endpoint registry and every surface built on it: `routes/model_routes.py` holds the
per-user model picker (`GET /api/models`), the endpoint CRUD (`POST`/`GET`/`PATCH`/`DELETE
/api/model-endpoints`, plus the `/models` and `/dependents` sub-resources), the probe and refresh
endpoints (`GET /api/ping`, `/api/probe`, `/api/model-endpoints/{id}/probe`,
`/api/model-endpoints/{id}/models`, `POST /api/probe-selected`, `POST /api/model-endpoints/test`),
local discovery (`GET /api/providers`, `/api/discover`, `/api/model-endpoints/probe-local`), the
default-chat resolution (`GET /api/default-chat`), the background model-cache refresh and the
stale-cookbook-endpoint sweep, and the tool on/off list (`GET`/`POST /api/tools`).

The boundary: the request-authenticating middleware and the `require_admin` gate these routes call
are `core-auth-session`; the `ModelEndpoint` row and its encrypted key column are
`core-data-platform`; the URL and header builders the probes use (`resolve_url`, `normalize_base`,
`build_chat_url`, `build_models_url`, `build_headers`, `resolve_endpoint_runtime`) are
`src-llm-core`; `src/auth_helpers.py` (`effective_user`, `owner_filter`) is `src-security`; the
settings store the CRUD reads and writes is `src-memory-rag`; the health report that probes the same
endpoints is `src-platform`, reached through `routes-rest-integrations-misc`. This section covers
what these routes do with a caller-supplied endpoint URL, who may call them, and what they reveal —
not whether the store, the URL builders, or the middleware are themselves correct.

### Coverage

**Read fully:** `routes/model_routes.py` (2,717 lines).

**Read partially:** the boundary code and callers the findings rest on —
`core/middleware.py` at `require_admin` (`:57-82`); `src/auth_helpers.py` in full (199 lines:
`get_current_user`, `effective_user`, `owner_filter`, `_auth_disabled`); `core/database.py` at the
`ModelEndpoint` model (`:520-554`); `src/endpoint_resolver.py` at `resolve_endpoint_runtime`
(`:146-162`), `resolve_url` (`:209-222`), `normalize_base` (`:225-234`), `_validated_endpoint_base`
(`:237-242`), `_prepare_endpoint_base` (`:245-247`), `build_chat_url` (`:271-283`),
`build_models_url` (`:286-315`) and `build_headers` (`:318-340`); `core/log_safety.py` (`:1-27`);
`src/readiness.py` in full (61 lines — it checks the database and the data directory and does not
touch the model-endpoint store); `src/service_health.py` at `providers_health` (`:346-382`) and the
enabled-endpoint query it feeds (`:435-445`); `app.py` at the auth-exempt list (`:265-292`) and
`/api/health` (`:956-958`); `routes/diagnostics_routes.py` at `get_service_health` (`:23-30`);
`src/tool_security.py` at `NON_ADMIN_BLOCKED_TOOLS` (`:42-78`); `src/agent_tools/admin_tools.py` at
`do_manage_endpoints` (`:22-80`); `routes/cookbook_routes.py` at the serve-registration block
(`:1888-1925`) and `save_cookbook_state` (`:3395-3415`); `routes/chatgpt_subscription_routes.py`
(`:55-95`) and `routes/copilot_routes.py` (`:55-90`); `src/chatgpt_subscription.py` at
`resolve_runtime_credentials` (`:254-286`); the chat-side credential resolution
(`src/ai_interaction.py:137`, `src/agent_loop.py:1029`, `routes/chat_routes.py:605`,
`routes/chat_helpers.py:484`); `static/js/admin.js` at the add-endpoint form (`:1100-1135`), the
refresh control (`:680-700`) and `_normalizeBaseUrl` (`:966-1000`); `static/js/markdown.js` at
`_isModelEndpointUrl` (`:168-177`), `_appendEndpointAddButtons` (`:1122-1142`) and
`_registerEndpointFromButton` (`:1144-1180`); `static/js/cookbookRunning.js` at
`_removeEndpointByUrl` (`:529-543`); `static/js/models.js:202`; and the module's own tests
(`tests/test_model_routes.py`, `tests/test_endpoint_probing.py`,
`tests/test_endpoint_owner_scope_followup.py`) for what is already pinned.

**Not read:** `src/llm_core.py` internals (`_detect_provider`, `httpx_get_kimi_aware`, the payload
builders) beyond the call signatures; `src/settings.py`; `core/database.py` beyond the
`ModelEndpoint` model (the encryption column, the session store); `core/middleware.py` beyond
`require_admin` (the request-authentication middleware itself belongs to `core-auth-session`);
`src/chatgpt_subscription.py` beyond `resolve_runtime_credentials`; the cookbook serve pipeline and
`_active_cookbook_endpoint_ids`' producer beyond the state-file shape cited below; the rest of the
front end; and every other `routes-*` module.

**Checks run:** six probes with throwaway scripts under `/tmp` (not part of the target tree), each
quoted in the finding it settles — the URL helpers against a query-bearing base; `GET /api/models`
and `GET /api/default-chat` and `DELETE /api/model-endpoints/{id}` with one such row visible, through
`fastapi.testclient` with the stores stubbed; `POST /api/model-endpoints` and
`POST /api/model-endpoints/test` with the same URL; the manual-refresh path with a subscription
endpoint row, capturing the `api_key` the probe receives and the log record it emits;
`POST /api/probe-selected` with five body shapes; and
`_disable_stale_cookbook_local_endpoints` against a state file holding only a stopped serve task and
then one holding a running task. Also a grep for the callers of `_resolve_probe_key` and of the
model-endpoint probe helpers. The 54 suites matching `ls tests | grep -iE 'model|endpoint|ready'`
were run over this surface — **714 passed**.

#### [BUG] An endpoint `base_url` carrying a query or fragment is accepted, then breaks the model picker and cannot be deleted

- **Location:** `routes/model_routes.py:1570` (`_fetch_models`), `:2483` (`get_default_chat`), `:2616` (`_session_uses_endpoint_url`), with the two write boundaries at `:1993` (`base_url: str = Form(...)`) and `:2554` (`if "base_url" in body`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** nothing on the write path rejects a query or fragment. `create_model_endpoint`
  normalizes the value and stores it (`:2011`, `:2159-2165`), and the PATCH branch does the same
  with no probe at all:

  ```python
  if "base_url" in body and isinstance(body["base_url"], str):
      _new_base = body["base_url"].strip().rstrip("/")
      for _suffix in ("/models", "/chat/completions", "/completions", "/v1/messages"):
          if _new_base.endswith(_suffix):
              _new_base = _new_base[: -len(_suffix)].rstrip("/")
      _new_base = _normalize_base(_new_base)
      if _new_base:
          ep.base_url = _new_base
  ```

  `_normalize_base` keeps the query, and every URL builder the read paths call goes through
  `src/endpoint_resolver.py:237-242`, which refuses it:

  ```
  $ venv/bin/python -c "... build_chat_url(normalize_base('http://localhost:1234/v1?api_key=…'))"
  normalize_base -> http://localhost:1234/v1?api_key=…
  build_chat_url -> ValueError: Endpoint base URL must not include query or fragment
  build_models_url -> ValueError: Endpoint base URL must not include query or fragment
  ```

  Measured end to end through `fastapi.testclient` with `SessionLocal` stubbed and the admin gate
  replaced by a no-op, so the handler body runs as written (the row the POST creates has
  `owner=None`, because `shared` defaults to `"true"` at `:2008`):

  ```
  POST /api/model-endpoints (skip_probe=true) -> 200
    stored base_url: http://198.51.100.7:8080/v1?api_key=…  |  row.owner: None
  GET  /api/models        as non-admin "alice" -> 500
  GET  /api/default-chat  as non-admin "alice" -> 500
  DELETE /api/model-endpoints/ep-q             -> 500   (db.delete never reached)
  DELETE again after clearing the query        -> 200 {'deleted': True, 'cleared_sessions': 1}
  ```

  The DELETE fails inside `_clear_sessions_for_endpoint` → `_session_uses_endpoint_url`
  (`:2608-2618`), which calls `build_chat_url(base)` at `:2616` for every session row. `POST
  /api/model-endpoints/test` with the same URL is a 500 as well, where the intended answer is the
  400 that `_model_endpoint_error_message` builds.

  Reachability of the store path: `POST` skips the probe whenever the caller sends
  `skip_probe=true` (`:2031-2033`), and a shipped button does exactly that with a URL taken from a
  rendered chat message — `static/js/markdown.js:1122-1142` adds an "Add to model picker" button to
  every `a[href]` whose path is `/v1` (`_isModelEndpointUrl`, `:168-177`, ignores the query), and
  `_registerEndpointFromButton` posts that href verbatim with `skip_probe=true` (`:1174`). The
  browser add form is safe by comparison: `static/js/admin.js:984` strips `?`/`#` before posting.
- **Impact:** one admin action — clicking that button on a link whose URL carries a query string, or
  any API/agent call that stores one — leaves a row that makes `GET /api/models` and
  `GET /api/default-chat` return 500 for every caller who can see it. Because the row is registered
  shared (null owner) by default, that is every user on the instance, and the model picker is the
  app's main model-selection surface. The row also cannot be removed through the API: `DELETE
  /api/model-endpoints/{id}` raises the same `ValueError` before `db.delete`, so the admin has to
  edit the database. Chat sessions already bound to a good endpoint are unaffected.
- **Fix:** validate at the two write boundaries — reject a `base_url` containing `?` or `#` with a
  400 (the PATCH branch currently validates nothing at all) — and make the read paths defensive:
  `_fetch_models` and `get_default_chat` should skip or degrade a row whose URL cannot produce a
  chat URL, and `_session_uses_endpoint_url` should treat the failure as "does not match" rather
  than letting it abort the DELETE.

#### [SECURITY] Endpoint URLs that can embed credentials are written to the log unredacted on the refresh and probe paths

- **Location:** `routes/model_routes.py:2333` (with `:172`, `:1059`, `:663`, `:674`, `:683`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the module imports the redactor and uses it on the probe's own log lines, but not on
  the other URL-bearing ones:

  ```python
  from core.log_safety import redact_url as _redact_url_for_log      # :20
  ...
  logger.info("Endpoint still loading model at %s", _redact_url_for_log(url))     # :1033
  logger.warning("Failed to probe %s with API key: %s", _redact_url_for_log(url), e)  # :1037
  ...
  logger.warning("Manual model refresh failed for endpoint %s at %s: %s", ep_id, base, exc)  # :2333
  logger.debug(f"Ollama /api/tags probe failed for {base}: {e}")                 # :1059
  logger.debug("Provider detection failed for %s: %s", base_url, exc)            # :663
  ```

  `base` at `:2333` is `_normalize_base(ep.base_url)` and `base_url` at `:663`/`:674`/`:683` is the
  caller's value, so the userinfo and the query survive. That is the case the helper documents:

  ```python
  # core/log_safety.py:3-6
  """Endpoint URLs configured by admins can embed credentials in the userinfo
  (``https://user:pass@host``) or query string (``?api_key=...``). Logging them
  raw leaks those secrets, so route/diagnostic logs run URLs through
  ``redact_url`` first.
  ```

  Measured by running the manual-refresh path with the row's `base_url` carrying a query and
  capturing the module logger:

  ```
  refresh header: failed
  LOG: Manual model refresh failed for endpoint ep-q at http://198.51.100.7:8080/v1?api_key=…: Endpoint base URL must not include query or fragment
  ```

  The same convention is kept elsewhere: `routes/chat_routes.py:728`, `:1670` and
  `routes/contacts/contacts_routes.py:723` all log their URLs through `redact_url`. The
  redactor has its own blind spot for scheme-less URLs
  (`core-auth-session.md`, `redact_url` returns a scheme-less value unchanged); the six lines
  here leak even a well-formed URL, so the two defects are independent.
- **Impact:** an operator who configures an endpoint as `https://user:pass@host/v1` or
  `https://host/v1?api_key=…` gets that credential written into `data/logs/app.log` — at WARNING for
  the refresh failure, at DEBUG for the probe helpers — instead of the redacted form used two
  functions away. The log is local and served only to admins
  (`/api/diagnostics/logs`), and it requires the credential to live in the URL rather than in the
  `api_key` field, which is the supported place for it; the fix is cheap and the rule is the
  project's own.
- **Fix:** route these six call sites through `_redact_url_for_log`, as `_probe_endpoint` already
  does.

#### [BUG] Every probe sends the stored static key and never the session-backed one, because `_resolve_probe_key` has no caller

- **Location:** `routes/model_routes.py:691-699` (the helper), with the probe call sites at `:1432`/`:1502` (`_should_refresh_endpoint` / `_refresh_caches_bg`), `:1782`, `:1873`, `:2271`, `:2280`, `:2331`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_resolve_probe_key` resolves the live credential through
  `resolve_endpoint_runtime` — the same call the chat paths use — and nothing calls it:

  ```
  $ grep -rn "_resolve_probe_key" --include=*.py .
  ./routes/model_routes.py:691:def _resolve_probe_key(ep) -> Optional[str]:
  ./tests/test_endpoint_probing.py:53:        _resolve_probe_key,
  ./tests/test_endpoint_probing.py:451:# ── _resolve_probe_key: static key vs provider-auth runtime token ──
  ```

  The three assertions under that comment (`tests/test_endpoint_probing.py:453-477`) pin both
  branches: a static endpoint returns its column, a `provider_auth_id` endpoint returns the
  resolved runtime token, and a resolution failure returns `None`. No production module appears in
  that grep.

  Every production call site passes the row's static column instead — `ep.api_key` at `:1782`,
  `:2331`, `ep_data["api_key"]` at `:2271`/`:2280`, `ep.get("api_key")` at `:1873`, and
  `info["api_key"] = getattr(ep, "api_key", None)` at `:1432` for the background refresh. For a
  subscription-backed endpoint that column is null by construction: the ChatGPT sign-in route writes
  `ep.api_key = None` with `ep.provider_auth_id = auth.id`
  (`routes/chatgpt_subscription_routes.py:82-83`), and `_probe_endpoint` (`:965-969`) returns an
  empty list when it has no key:

  ```python
  if provider == "chatgpt-subscription":
      from src.chatgpt_subscription import fetch_available_models
      if api_key:
          return fetch_available_models(api_key, timeout=timeout)
      return []
  ```

  Measured on the manual-refresh route with such a row, stubbing `_probe_endpoint` to record the key
  it receives and stubbing `resolve_endpoint_runtime` to return a live token:

  ```
  manual refresh status header: failed
  api_key the probe was called with: [None]
  what the unwired resolver would return: live-bearer
  ```

  The chat side does resolve it (`src/ai_interaction.py:137`, `src/agent_loop.py:1029`,
  `routes/chat_routes.py:605`), so the omission is specific to probing.
- **Impact:** an administrator can never refresh or probe a subscription-backed endpoint: the
  Refresh control on `/api/model-endpoints/{id}/models?refresh=true` returns
  `X-Model-Refresh-Status: failed`, and the admin UI surfaces that as a warning toast
  (`static/js/admin.js:686-691`), while the background refresh records the endpoint as failing. Chat
  keeps working, and the model list seeded at sign-in is still served, so the damage is a dead admin
  control rather than a broken flow — but the dead control is also the only way to update that list.
  The same static key is what `src/service_health.py:441-442` hands to the probe, so the health
  report counts such an endpoint as unreachable too.
- **Fix:** pass `_resolve_probe_key(ep)` at those call sites (keeping the static key as the
  fallback it already is), or resolve the runtime credential in `_probe_endpoint`'s callers the way
  the chat path does. The helper's own tests already pin the intended behaviour.

#### [ERROR-HANDLING] `POST /api/probe-selected` returns 500 for a malformed entry in `models`

- **Location:** `routes/model_routes.py:1797-1809`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the body is typed, so a non-object body is rejected — but the list elements are not
  checked before they are used as mappings:

  ```python
  @router.post("/probe-selected")
  def probe_selected(request: Request, request_body: dict = Body(...)):
      require_admin(request)
      models_to_probe = request_body.get("models", [])
      ...
      for item in models_to_probe:
          ep_id = item.get("endpoint_id", "")
  ```

  Measured through `fastapi.testclient` with the admin gate stubbed out:

  ```
  body=['a']                          -> HTTP 422
  body='a'                            -> HTTP 422
  body={'models': ['a']}              -> HTTP 500 Internal Server Error
  body={'models': 'a'}                -> HTTP 500 Internal Server Error
  body={'models': [{'model': 'm'}]}   -> HTTP 200
  ```

  This is the same class as the non-object-body finding in `routes-rest-auth-admin.md`
  (`routes/auth_routes.py:329`, `:784`, `:794`): an unchecked request shape reaches an unhandled
  `AttributeError` and the caller gets a 500 instead of a 400. Here the outer body is validated by
  the `dict` annotation, so the unchecked part is the element shape.
- **Impact:** an admin or a script that sends a string instead of an object list gets a 500 and a
  traceback in the log where the rest of the file answers 400 (as the two `request.json()` handlers
  in this file do, `:2376` and `:2503`). Admin-only, so the cost is a confusing failure, not an
  exposed path.
- **Fix:** reject or skip a non-dict element — `if not isinstance(item, dict): results.append(...);
  continue`, or a 400 up front — matching the guards the two raw-body handlers already use.

#### [BUG] The stale-cookbook sweep cannot disable the last stale endpoint

- **Location:** `routes/model_routes.py:151-155` (with `_active_cookbook_endpoint_ids` at `:123-148`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the sweep returns before looking at any row whenever no serve task is currently
  active, and `_active_cookbook_endpoint_ids` returns the empty set both for "no serve task is
  active" and for "the state file is missing or unreadable":

  ```python
  def _disable_stale_cookbook_local_endpoints(db) -> int:
      """Disable enabled cookbook endpoints whose serve task is no longer active."""
      active_ids = _active_cookbook_endpoint_ids()
      if not active_ids:
          return 0
  ```

  A stopped serve task stays in the state file (the cookbook status handler counts "accumulated
  stopped tasks", `routes/cookbook_routes.py:4436-4448`), so the ordinary end state — the last serve
  stopped — is exactly the empty-set case. Measured with a state file holding one stopped serve task
  and one enabled `local-` row, then one holding a running task beside it:

  ```
  active ids with only a stopped serve task: set()
  disabled count (stopped-only state): 0 | row.is_enabled now: True
  active ids with one running serve task: {'local-live'}
  disabled count (one active task): 1 | row.is_enabled now: False
  ```

  The docstring and the function's own comment state the opposite intent: "If a tmux stream is
  stopped or an old task lingers, the row must stop participating in model selection and defaults"
  (`:127-129`).
- **Impact:** after the only served model is stopped, a lingering `local-*` row stays enabled, so it
  keeps appearing in the picker as a candidate and keeps being probed — the state the sweep exists to
  clear. The mitigation is that the admin UI deletes the row when it stops a serve
  (`static/js/cookbookRunning.js:539`, `_removeEndpointByUrl`), so this only bites when the row
  outlives the task: a browser that closed mid-stop, a stop performed outside the UI, or a state
  file that was removed.
- **Fix:** distinguish the two cases — when the state file is readable and its `tasks` list contains
  no active serve task, every enabled `local-%` row is stale; keep the early return only for the
  missing/unreadable state file (where the answer really is unknown).

## 26. routes: shell and code execution

### Overview

`routes/shell_routes.py` (1,971 lines) owns the two endpoints that run arbitrary commands
(`POST /api/shell/exec`, `POST /api/shell/stream`), the three streaming backends behind them (pipe,
PTY, tmux, plus the Windows detached-process path), and the Cookbook dependency routes that probe and
mutate package state (`GET /api/cookbook/packages`, `POST /api/cookbook/packages/install`,
`POST /api/cookbook/install-system-deps`, `POST /api/cookbook/rebuild-engine`). The frontend calls
the shell endpoints from the code runner, the Cookbook download and install panels, and the
hardware-fit checks; the dependency routes are the Cookbook Dependencies tab's read path and its two
install actions. The agent's loopback bridge into these routes (`src/tools/system.py`,
`src/tools/cookbook.py`) is covered by `src-agent-tools`; the Cookbook route helpers and the tmux
task model the frontend drives belong to `routes-cookbook` and
`static-js-cookbook-settings-models`. A finding here is about what this router does with a command
once it has one, not about who may call it: admin-only is enforced at `_require_admin` and that
decision is not re-reviewed here.

### Coverage

**Read fully:** `routes/shell_routes.py` (1,971 lines). Every cited line was re-read at `2992bf6d368a`.

**Read partially:** `static/js/cookbook.js` at `_installDep` (`:1399-1470`) and the install-button
wiring (`:1509-1516`), to establish which endpoint the UI's install path calls;
`static/js/codeRunner.js:309-340` and `static/js/cookbookDownload.js:380-400`, the two call sites
that set the request shape; `app.py:125-145` (CORS origin list) and `:1303` (default bind host);
`routes/auth_routes.py:185-194` (session cookie flags). Two small reproduction scripts were run in
`/tmp` with the same `asyncio.create_subprocess_shell` call shape as `_create_shell`; their output is
quoted in the first finding.

**Not read:** every test file; `routes/cookbook_helpers.py` (`_llama_cpp_rebuild_cmd` is called at
`:1949` but not read); `routes/cookbook_routes.py`; the remaining Cookbook front-end panels beyond
the cited lines; `static/js/cookbookRunning.js`, which drives the tmux tasks these endpoints serve.
No test suite was run.

### Findings

#### [BUG] Killing the shell leaves its children running, and the timeout path can wait forever

- **Location:** `routes/shell_routes.py:591`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_create_shell` (`:552-572`) starts the command as `/bin/sh -c <command>` with
  `stdout=PIPE, stderr=PIPE` and no new session. When the timeout fires, `_exec_shell` kills only the
  direct child and then waits on it:

  ```python
  except asyncio.TimeoutError:
      if proc:
          try:
              proc.kill()
              await proc.wait()
  ```

  (`:588-592`; the wait is `:592`.) The pipe-streaming generator has the same kill-and-wait at
  `:1097-1098`, and on client disconnect kills without waiting at `:1082`. The PTY generator sets
  `preexec_fn=os.setsid` (`:627`) and then calls `proc.kill()` at `:644`, `:652`, and `:716` — it
  never signals the process group, so the new session buys nothing. Reproduced with the same call
  shape: a shell running `while true; do echo tick >> log; sleep 1; done & wait` was killed after the
  timeout, and its child survived while `proc.wait()` stayed blocked because the child holds the
  inherited stdout/stderr pipes:

  ```
  shell pid: 3580188 children: [3580190]
  sent SIGKILL to shell
  proc.wait() HUNG for 3s (grandchild holds the pipes)
  child 3580190 ALIVE
  ticks 5 -> 7: child STILL RUNNING
  ```

  The same sequence with `_exec_shell`'s exact prefix — `asyncio.wait_for(proc.communicate(),
  timeout=1)`, then `proc.kill()`, then `proc.wait()` — reproduced the same hang and the same
  surviving descendant. `asyncio`'s `Process.wait()` waits for pipe EOF, not only for the process to
  exit.
- **Impact:** `/api/shell/exec` and `/api/shell/stream` are the frontend's general command runners.
  Any command that leaves a child holding the pipes — a backgrounded server, a build tool that
  forks, user code that spawns `subprocess.run` — and then exceeds the timeout (30 s for exec, 120 s
  for stream) leaves the request blocked in `await proc.wait()`: the client never receives the
  timeout result, and the descendant keeps running with the pipe. The disconnect path and the PTY
  path leak the same descendants without the hang. Each occurrence holds a request task, two pipe
  transports, and a live process tree.
- **Fix:** start the child in its own session (`start_new_session=True` in `_create_shell`) and kill
  the group (`os.killpg(proc.pid, signal.SIGKILL)`), which also closes the pipes; in the PTY path use
  `os.killpg` for the session `setsid` already created. Bound every `await proc.wait()` with a short
  `asyncio.wait_for` so a surviving grandchild cannot pin the handler.

#### [BUG] `timeout: 0` means "no timeout" everywhere except `/api/shell/exec`, where it means "stop now"

- **Location:** `routes/shell_routes.py:974`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the request model documents `0 = no timeout (run until client disconnects)`
  (`:504-506`). The streaming path implements it: `shell_stream` logs `"none" if timeout == 0`
  (`:996`), the pipe loop sets `deadline = (loop.time() + timeout) if timeout else None` (`:1067`),
  and the PTY loop does the same (`:631`). `shell_exec` passes the value straight through:

  ```python
  result = await _exec_shell(
      cmd, timeout=req.timeout if req.timeout is not None else EXEC_TIMEOUT
  )
  ```

  (`:973-975`), and `_exec_shell` passes it to `asyncio.wait_for` (`:584`), where 0 is an
  already-expired deadline. Confirmed:

  ```
  $ python3 -c "import asyncio; asyncio.run(...wait_for(asyncio.sleep(5), timeout=0))"
  TimeoutError immediately with timeout=0
  ```

  The response is `{"stdout": "", "stderr": "Command timed out after 0s", "exit_code": -1}` with the
  process killed.
- **Impact:** a caller that follows the documented contract and sends `timeout: 0` to run a long
  command to completion gets an immediate false timeout. No current frontend caller sends 0 to this
  endpoint — every `/api/shell/exec` call site sends 5-60 — so the defect is latent and would
  surface when a caller adopts the documented value.
- **Fix:** pass `req.timeout or None` to `_exec_shell`, or drop `0 = no timeout` from the model and
  document that only the streaming endpoints accept it.

#### [BUG] The dependency installs report a timeout without stopping the install

- **Location:** `routes/shell_routes.py:1907`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `install_system_deps` runs the package-manager script under a 180 s timeout and
  returns without touching the process:

  ```python
  out, err = await asyncio.wait_for(proc.communicate(), timeout=180)
  except asyncio.TimeoutError:
      return {"ok": False, "error": "Install timed out after 180s"}
  ```

  (`:1907-1910`.) `rebuild_engine` is the same shape with a 30 s timeout (`:1964-1966`).
  `_exec_shell` at least calls `proc.kill()` in its timeout branch; these two do not.
- **Impact:** the response says the install failed while `apt-get`, `dnf`, or the rebuild keeps
  running. A retry starts a second package manager against the same lock, and the Cookbook panel's
  state (deps still missing) contradicts what the host is doing.
- **Fix:** kill the process group in the timeout branch before returning, and say in the error that
  the command was stopped.

#### [PERF] The tmux tail re-reads the whole log file every second on the event loop

- **Location:** `routes/shell_routes.py:805`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the 1 Hz tail loop reads and splits the entire log, then slices off the part it has
  already sent:

  ```python
  lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
  new_lines = lines[lines_sent:]
  ```

  (`:804-808`; the Windows path repeats it at `:918-920` and `:932-934`.) The read is synchronous
  inside the async generator. Measured on this machine: a 1 MB log takes 1 ms to read and split,
  5 MB takes 4 ms, and 20 MB takes 18 ms — repeated every second. Total bytes read over a run grow
  with the square of the log size: a 20 MB log polled for 30 minutes is roughly 36 GB of reads.
- **Impact:** the tmux path exists for long Cookbook builds and downloads, the commands that produce
  the largest logs. Each poll blocks the event loop for the read, stalling every other request, and
  the wasted I/O grows with the file.
- **Fix:** keep the file open and read only the appended bytes (track the byte offset and `seek`), or
  move the read to a thread. Cap or rotate the log.

#### [FOOTGUN] The cross-site guard is on the read-only dependency listing, not the shell endpoints

- **Location:** `routes/shell_routes.py:1201`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_reject_cross_site` rejects requests whose `Sec-Fetch-Site` is `cross-site`
  (`:72-75`). Its only call in the file is on `list_packages`, a GET (`:1201`). The mutating
  endpoints — `shell_exec` (`:963`), `shell_stream` (`:981`), `install_package` (`:1765`),
  `install_system_deps` (`:1820`), `rebuild_engine` (`:1941`) — call only `_require_admin`. The
  current cookie policy and body parsing block the obvious cross-site forms: the session cookie is
  `SameSite=Lax` (`routes/auth_routes.py:188`), and a Pydantic body needs `application/json`, which
  an HTML form cannot send. So this is not an exploitable CSRF today.
- **Impact:** the one endpoint that carries the guard is the one that changes nothing, and the
  endpoints that execute code depend on the cookie policy staying strict. If `SameSite` is relaxed
  for an embedded or tunneled deployment, or an origin is added to the CORS allowlist, the mutating
  endpoints have no cross-site check to fall back on.
- **Fix:** call `_reject_cross_site` in the mutating handlers, or install it as a router dependency.

#### [SECURITY] tmux wrapper scripts and their logs are readable by other local users

- **Location:** `routes/shell_routes.py:770`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the log directory is created with the process umask
  (`TMUX_LOG_DIR.mkdir(parents=True, exist_ok=True)`, `:749`), and the wrapper script is explicitly
  made world-readable and executable:

  ```python
  script_path.chmod(0o755)
  ```

  (`:770`.) The script embeds the command verbatim (`f"{cmd} 2>&1 | tee '{log_path}'"`, `:763`), and
  the log is created by `tee` under the same umask. On the machine this was read on:

  ```
  $ ls -la /tmp/odysseus-tmux/
  drwxr-xr-x 2 lhl lhl 60 ... .
  -rw-r--r-- 1 lhl lhl 10188 ... scan_cache.py
  ```

- **Impact:** on a host with more than one local account, another user can read the command line and
  the output while the job runs. Commands passed through this path can contain tokens, signed URLs,
  or private model paths. Admin-only authorization does not protect against a second local account.
- **Fix:** create the directory with mode 0700 and the script with 0700, and create the log with a
  restrictive mode (for example `umask 077` in the wrapper, or an `os.open(..., 0o600)` before
  `tee`).

#### [DEAD-CODE] `install_package` is unused by the UI, installs into the wrong interpreter, and rejects most catalog entries

- **Location:** `routes/shell_routes.py:1763`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the route always installs into the Cookbook server's own interpreter and accepts no
  target:

  ```python
  cmd = [_sys.executable, "-m", "pip", "install", pip_name]
  ```

  (`:1789-1791`.) The UI's install path does not call it: `_installDep` builds the pip command for
  the selected venv or remote host and submits it through the task flow
  (`static/js/cookbook.js:1399-1470`, wiring at `:1512`). A repository search finds no other caller
  of `/api/cookbook/packages/install`; the only references are the agent blocklist
  (`src/tools/system.py:557` and the refusal at `:678-679`) and a test. The `known` allowlist
  (`:1772-1793`) also does not contain most of the catalog's pip strings — the `diffusers` row is
  `"diffusers[torch] torchvision accelerate scipy python-multipart"` (`:1322`) and `krea_diffusers`
  is `"git+https://github.com/huggingface/diffusers.git torchvision accelerate scipy
  python-multipart"` (`:1329`), neither of which matches an entry — so those rows would be refused
  as unknown.
- **Impact:** an endpoint that would install into the server's environment rather than the selected
  one if it were called, plus a blocklist entry and a test that guard it. The UI works around it.
- **Fix:** delete the route, or route it through the same target-aware install flow the UI uses.

## 27. routes: gallery and documents

### Overview

The gallery and document surfaces. `routes/gallery/gallery_routes.py` owns the photo library
(upload with EXIF extraction and SHA-256 de-duplication, library search and facets, albums,
favourites, AI tagging, soft delete) and the image-edit proxies (inpaint, harmonize, sharpen,
denoise, upscale, SAM mask, background removal, face enhancement); `routes/gallery/gallery_helpers.py`
holds the EXIF reader, the row serializer, the owner filter and the patch model.
`routes/document/document_routes.py` owns document CRUD and version history, the document library,
PDF import and text re-extraction, page rendering, form export and the signed-reply handoff, plus the
tidy paths; `routes/document/document_helpers.py` holds the request models, the serializers,
`_verify_doc_owner`, the upload locator and the PDF-marker ownership check.

The boundary: the middleware that authenticates these requests and the `/api/generated-image/{filename}`
file server are in `app.py` (`build-install-deploy`); the `Document`, `DocumentVersion`,
`GalleryAlbum`, `GalleryImage` and `Signature` models are `core/database.py` (`core-data-platform`);
the upload store, the PDF form document builders and the PDF/VL processor are `src-documents`; the
upload byte caps are `src-security`; the gallery file cleanup that runs when sessions are deleted is
`routes/session_routes.py` (`routes-chat-session`). This section covers whether each handler
authenticates, scopes and confines correctly, not whether the stores underneath are safe.

### Coverage

**Read fully:** all six assigned files (4,548 lines): `routes/gallery/gallery_routes.py` (2,338),
`routes/document/document_routes.py` (1,810), `routes/document/document_helpers.py` (243),
`routes/gallery/gallery_helpers.py` (145), `routes/gallery/__init__.py` (6),
`routes/document/__init__.py` (6).

**Read partially:** the boundary code the findings rest on — `src/auth_helpers.py` in full
(`get_current_user`, `effective_user`, `require_user`, `require_privilege`, `owner_filter`,
`_auth_disabled`); `app.py` at the `/api/generated-image/{filename}` handler (`:513-553`) and the
auth-exempt lists (`:263-296`); `core/database.py` at the `Document`/`DocumentVersion`/`GalleryAlbum`/
`GalleryImage` definitions (`:283-383`); `src/upload_limits.py` in full (the gallery caps and
`read_upload_limited`); `src/upload_handler.py` at `max_upload_size` (`:217`), `detect_content_type`
(`:282-302`), `is_safe_file_type` (`:366-385`) and `save_upload` (`:1205-1250`);
`src/document_processor.py` at `_process_pdf` (`:112-152`) and `analyze_image_with_vl_result` /
`analyze_image_with_vl` (`:333-392`); `src/llm_core.py` at `llm_call` (`:1969-2045`) and
`httpx_post_kimi_aware` (`:934-947`); `src/pdf_runtime.py` in full; `src/generated_images.py` at
`GENERATED_IMAGE_HEADERS` and `resolve_generated_image_path` (`:14-22`); `routes/session_routes.py`
at the all-sessions delete path (`:677-731`); `routes/upload_routes.py` at
`_promote_chat_image_to_gallery` (`:195-250`); `src/chat_handler.py` at
`_sync_upload_vision_to_gallery` (`:33-53`); `routes/email_helpers.py` at
`_attach_compose_uploads` / `_cleanup_compose_uploads` (`:515-551`); `static/js/gallery.js` at the
library render (`:625-629`), the patch/delete helpers (`:190-226`), rotate (`:1810-1830`), the
set-as-cover button (`:1843-1858`) and rename (`:1887`); `static/js/document.js` at the AI-fill call
(`:1796`) and the compose-attachment removal (`:3610-3618`).

**Not read:** the auth middleware itself (`core/middleware.py` and `app.py`'s `AuthMiddleware`),
assigned to `core-auth-session` and `build-install-deploy`; the `UploadHandler` internals other than
the functions named above (`src-documents`); the `Signature` model and the PDF form builders
(`src-documents`); the front end beyond the regions named above; the other `routes-*` sections that
call into these modules.

**Checks run:** the 46 suites matching `ls tests | grep -iE 'gallery|document|image'` — **182
passed**; a request-level probe that mounts both routers in a FastAPI app with a real SQLite session
factory (the shape `tests/test_gallery_null_user_routes.py` uses) and posts a JSON array and a JSON
string to every raw-body endpoint, quoted in the non-object-body finding; the same probe with a
seeded album row for the three album sub-routes; an end-to-end probe of the set-cover → delete →
list-albums sequence, quoted in the album-cover finding; a probe that runs the vision call
`_process_pdf` makes inside a live event loop with a heartbeat task, quoted in the blocking-work
finding; and greps for `to_thread` / `run_in_threadpool` in these two files, for `request.json()`,
for `file_hash` readers, for `is_active = False` sites and for `import fitz`.

#### [PERF] PDF and image processing runs synchronously inside the async handlers

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

#### [BUG] An album keeps a cover that points at a deleted photo, and the album list renders the dead URL

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

#### [BUG] The replace route leaves `file_hash` and `file_size` describing the file it replaced

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

#### [ERROR-HANDLING] Seventeen raw-body endpoints answer 500 to a JSON array or string

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

#### [ERROR-HANDLING] The AI-fill endpoint imports PyMuPDF unguarded, so a missing optional dependency is a 500 instead of the 503 its siblings return

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

## 28. routes: skills, calendar, tasks

### Overview

The self-service skills library, the local calendar, and the scheduled-task CRUD surface:
`routes/skills_routes.py` (SKILL.md CRUD, slash-command invocation, the manual and autonomous
skill audit, the built-in tool-override editor), `routes/calendar_routes.py` (calendar and event
CRUD, ICS import and export, CalDAV account configuration, the natural-language quick-parse), and
`routes/task/task_routes.py` with `routes/task/__init__.py` (task CRUD, pause/resume/revert,
manual run and webhook triggers, run history, the natural-language task parser).

The boundary: the skills store these routes drive (`services/memory/skills.py`,
`skill_format.py`, `skill_importer.py`) is `services-memory`; the scheduler, its executors and
`compute_next_run` are `src-research-scheduling`; the CalDAV client and its write-back are
`src-email-integrations`; the `CalendarCal` / `CalendarEvent` / `ScheduledTask` / `TaskRun` tables
are `core-data-platform`; request authentication and `require_admin` are `core-auth-session`; the
`cookbook_serve` action is `routes-cookbook`; the calendar and task front end is in the
`static-*` sections. This section covers whether each route authenticates, scopes to its owner,
validates what it accepts, and bounds the work it starts — not whether the store, the scheduler or
the middleware underneath is correct.

### Coverage

**Read fully:** the four assigned files (4,860 lines): `routes/skills_routes.py` (1,899),
`routes/calendar_routes.py` (1,775), `routes/task/task_routes.py` (1,181),
`routes/task/__init__.py` (5).

**Read fully, outside the assigned paths:** `services/memory/skill_importer.py` (487),
`src/auth_helpers.py` (199), `src/upload_limits.py` (72), `src/task_action_policy.py` (47).

**Read partially:** `src/task_scheduler.py` at `compute_next_run` (`:113-231`),
`HOUSEKEEPING_DEFAULTS` (`:251-263`), the loop (`:673-700`), `_check_due_tasks` (`:701-735`),
`_execute_task` / `_execute_task_locked` (`:737-1159`), `run_task_now` / `stop_task`
(`:2264-2290`); `services/memory/skills.py` at the path helpers (`:76-83`), `_iter_skill_files` /
`_read_skill` / `_write_skill` (`:159-181`), `load` (`:278-287`), `add_skill` (`:293-383`),
`import_bundle_from_files` (`:384-431`), `update_skill` / `delete_skill` / `read_skill_md`
(`:432-575`); `services/memory/skill_format.py` at `slugify` (`:65-72`); `src/caldav_sync.py` at
`validate_caldav_url` (`:106-131`) and the sync entry points (`:617-722`); `core/middleware.py` at
`require_admin` (`:57-82`); `core/database.py` at `ScheduledTask` (`:730-760`), `TaskRun`
(`:810-825`), `CalendarCal` (`:1838-1855`) and `CalendarEvent` (`:1856-1875`);
`src/builtin_actions.py` at the urgency-cache writer (`:2275-2290`, `:2532`);
`routes/email_helpers.py` at `OWNER_SCOPED_EMAIL_CACHE_TABLES` (`:566-586`); `src/tools/system.py`
at the `manage_tasks` action (`:285-310`, `:340-365`); `app.py` at the uvicorn launch
(`:1300-1306`); `Dockerfile:113`; `specs/calendar-tasks-notes.md:52`; `static/js/tasks.js` at the
run-now paths (`:150-151`, `:1874-1877`, `:2767`).

**Not read:** the middleware that authenticates the request — what stamps
`request.state.current_user` lives in `app.py` and `core/middleware.py` (assigned to
`core-auth-session`), and only `require_admin`, `require_user` and `get_current_user` were read;
the task executors the scheduler dispatches into (`_execute_llm_task`, `_execute_action`,
`_execute_research_task`, `_deliver_task_result`, `_deliver_via_mcp`) beyond their call sites;
`src/agent_loop.stream_agent_loop` and the tool surface a skill test or an audit run reaches; the
CalDAV sync implementation (`_sync_blocking`, `src/caldav_writeback.py`) and
`src/url_safety.check_outbound_url`; the skills, calendar and task front end beyond the regions
cited; the `do_manage_*` agent tools (their own sections) beyond the `scheduled_day` pass-through
cited; the remaining 2,000-odd lines of `src/task_scheduler.py` (delivery, notifications,
research and check-in execution).

**Checks run:** four throwaway probes under `/tmp` that call the real handlers — a non-object-body
probe (the router built with a stub skills manager, mirroring
`tests/test_integrations_store_shape.py`), an ICS-import probe over a temp SQLite database
mirroring `tests/test_calendar_import_zero_duration.py`, a `create_task` probe over the same
harness, and a self-request repro mirroring `_try_delete`'s call shape; `_expand_rrule` timed
directly with a stub event; the dateutil expansion timed separately; and the `icalendar` parse of
100,000 `VEVENT`s timed. The
sixty-six suites matching `ls tests | grep -iE 'skill|calendar|task|ics'` were run —
**319 passed**.

#### [BUG] Deleting a cookbook task calls its own API from a blocking client, so the cascade never runs and the delete stalls for 10 seconds

- **Location:** `routes/task/task_routes.py:771` (the call), `:62-69` (the blocking client), `:89-91` (the fallback scan)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `delete_task` is an `async def` and calls the cascade synchronously, and the
  cascade reaches the running server over HTTP with a synchronous client:

  ```python
  _maybe_cascade_calendar_event(task)          # :771, inside `async def delete_task`
  ...
  def _try_delete(uid: str) -> bool:           # :62
      try:
          with httpx.Client(timeout=10) as client:
              r = client.delete(
                  f"{internal_api_base()}/api/calendar/events/{uid}",
                  headers=headers,
              )
  ```

  (The `...` line is an elision, not source.)

  The shipped deployment is one process with one event loop: `uvicorn.run(app, host=bind_host,
  port=bind_port, log_level="info")` (`app.py:1306`, no `workers=`) and
  `CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7000"]` (`Dockerfile:113`), with
  `internal_api_base()` resolving to this same listener. While the handler blocks in the sync
  client, the only event loop is not reading the socket, so the request it is waiting for is never
  served. Measured with a throwaway app that has the same shape (async handler, sync
  `httpx.Client(timeout=10)`, self-request on a single-worker uvicorn):

  ```
  GET /outer -> {'inner_error': 'ReadTimeout: timed out', 'elapsed': 10.011528253555298} wall=10.0s
  ```

  So every `DELETE /api/tasks/{id}` for a `cookbook_serve` task (an admin-only action) blocks
  every other request for ten seconds and then discards the failure — `_try_delete` catches the
  exception and returns `False`, and the caller ignores the result (`:80-82`). The spec states the
  opposite of what the code does: "task deletion cleans up the linked event when present, falling
  back to exact-summary matching for legacy events without a stored UID"
  (`specs/calendar-tasks-notes.md:52`). The comment above the call promises the same thing
  (`routes/task/task_routes.py:766-770`).
- **Impact:** the linked Cookbook calendar event is never deleted, so the calendar keeps a phantom
  event for a task that no longer exists — the outcome the cascade was written to prevent. In the
  fallback path (a task with no `cookbook_event_uid` marker) the
  stall repeats: the same handler makes two more loopback calls (`:91`, `:107`) before giving up.
  A multi-worker deployment would make the self-request serviceable, but neither launch path in
  the repository uses more than one worker.
- **Fix:** run the cascade off the event loop and let it finish before the row is deleted —
  `await asyncio.to_thread(_maybe_cascade_calendar_event, task)` — or call the calendar route's
  logic in-process instead of over HTTP. Offloading alone is enough for the loop to serve the
  self-request.

#### [PERF] An unvalidated RRULE makes a single calendar read block the event loop for seconds to minutes

- **Location:** `routes/calendar_routes.py:752` (the expansion loop), `:1249` and `:1300` (the unvalidated `rrule` writes), `:1188` (the call site)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** both write paths store the caller's `rrule` verbatim with no parse or bound
  (`rrule=data.rrule or ""` at `:1249`, `ev.rrule = data.rrule` at `:1300`), and the ICS import
  stores `comp.get("rrule").to_ical().decode()` (`:1538`). `list_events` then expands every
  recurring row synchronously on the event loop (`:1188`, inside `async def list_events` at
  `:1140`), and `_expand_rrule` asks dateutil for occurrences starting at the *window* while
  iterating from `DTSTART`:

  ```python
  expand_start = start - duration                                    # :746
  ...
  for occ_start in rule.xafter(expand_start, inc=True):              # :752
  ```

  (The `...` line is an elision, not source.)

  `_RRULE_EXPANSION_LIMIT` (`:661`, 1000) caps the results returned, not the work done to reach
  them, and the `if occ_start >= end: break` only fires after dateutil has walked every occurrence
  between `DTSTART` and the window. Measured with a stub event whose `DTSTART` is 2020-01-01 and
  `rrule = FREQ=MINUTELY;INTERVAL=1`, calling the real `_expand_rrule`:

  ```
  today's window (2026-10-04..+31d): 1000 occurrences, 4.34s
  _expand_rrule window 2026-01-01..+1d: 1000 occurrences, 3.95s
  _expand_rrule window 2028-01-01..+1d: 1000 occurrences, 5.25s
  _expand_rrule window 2100-01-01: 1000 occurrences, 51.83s
  ```

  End to end through the real handlers over a temp database — one `POST /api/calendar/import` of a
  one-event file, then one `GET /api/calendar/events`:

  ```
  minutely rrule + far window: import OK {...'imported': 1...} in 0.01s
     list 2030-01-01T00:00:00..2030-01-02T00:00:00: 1000 events in 6.28s
  ```

  (The `{...}` in the import line elides the rest of the printed dict.)

  `FREQ=SECONDLY` is worse: the same `rrulestr(...).xafter(2100-01-01)` call took 2946 s (49
  minutes) when measured directly. Any authenticated user can plant such an event — the calendar
  routes carry no admin gate — and a later `GET /api/calendar/events` for any window after the
  event's `DTSTART` pays the cost.
- **Impact:** the calendar view is not a one-off request: the cost is paid on every events request
  while the row exists, and the expansion runs on the event loop, so the whole instance (chat
  streams, task runs, other users) stalls for the duration — about 4 s for the ordinary
  current-month window with a minutely rule planted in 2020, 52 s for a window in 2100, and tens
  of minutes for a secondly rule.
- **Fix:** bound the iteration, not just the result — start the expansion from the later of
  `DTSTART` and `expand_start` (or reject a rule whose computed first occurrence is more than N
  iterations away), and validate `rrule` on write with `rrulestr` plus a minimum interval for
  `FREQ=MINUTELY`/`FREQ=SECONDLY`. Running `_expand_rrule` in `asyncio.to_thread` would keep the
  loop responsive but leave the per-request cost.

#### [BUG] A weekly task with a negative `scheduled_day` is created with a past `next_run` and re-runs forever

- **Location:** `src/task_scheduler.py:194-201` (the weekly branch), `routes/task/task_routes.py:498-503` (the create path), `:148` (the field)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `scheduled_day` is accepted as any integer and only cron expressions and
  `scheduled_date` are validated on the way in (`routes/task/task_routes.py:148`, `:498-503`). The
  weekly branch adds a negative `days_ahead` to today instead of normalizing it into the next
  seven days:

  ```python
  if schedule == "weekly":
      day = scheduled_day if scheduled_day is not None else 0  # 0=Monday
      candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
      days_ahead = day - candidate.weekday()
      if days_ahead < 0 or (days_ahead == 0 and candidate <= now):
          days_ahead += 7
      candidate += timedelta(days=days_ahead)
  ```

  `day = -100` on a Monday gives `days_ahead = -100 - 0 = -100`, then `-93`, so the returned time
  is 93 days in the past. Measured on `compute_next_run("weekly", "09:00", day, None, after=now)`
  with `now` a Monday at noon:

  ```
  scheduled_day=  -10 -> next_run=2026-10-02 09:00:00  in_past=True  delta_days=-4
  scheduled_day= -100 -> next_run=2026-07-04 09:00:00  in_past=True  delta_days=-94
  scheduled_day=    6 -> next_run=2026-10-11 09:00:00  in_past=False  delta_days=5
  ```

  and the same input through the real `POST /api/tasks` handler over a temp database:

  ```
  created: {'schedule': 'weekly', 'scheduled_day': -100, 'next_run': '2026-06-27T09:00:00Z', 'status': 'active'}
  now (naive utc): 2026-10-03T20:27:42.001450
  next_run in the past? True  delta: -99 days, 12:32:17.998550
  ```

  `status` is `"active"` because `next_run` is truthy (`routes/task/task_routes.py:544`), so
  `_check_due_tasks` selects it on the next tick (`ScheduledTask.status == "active",
  ScheduledTask.next_run <= now`, `src/task_scheduler.py:716-720`). After each run the scheduler
  recomputes the same past value (`:1027-1032`), so the task is due again immediately, and the
  loop's sleep is derived from that past value:

  ```python
  delta = (next_run[0] - _utcnow()).total_seconds()
  sleep_for = max(1.0, min(60.0, delta))          # src/task_scheduler.py:693-694
  ```

  A negative delta clamps to the 1-second floor, so the scheduler ticks every second.
- **Impact:** the task runs back to back for as long as it exists — an LLM task re-sends its prompt
  to the configured endpoint on every cycle — and the scheduler polls at 1 Hz instead of its
  normal ≤60 s cadence. The owner of the task is the one billed, but the instance never idles and
  every run writes a `task_runs` row. Reachable from the API (`scheduled_day` is an unvalidated
  integer on create and update) and from the agent's `manage_tasks` tool, which passes
  `args.get("scheduled_day")` straight through (`src/tools/system.py:296-308`, `:347`); the UI's
  own selector only offers 0-6, because it is built from the seven-entry `DAYS_OF_WEEK`
  (`static/js/tasks.js:27`, `:1416-1419`).
- **Fix:** validate the range where the value enters — `0 <= scheduled_day <= 6` for `weekly` and
  `1 <= scheduled_day <= 31` for `monthly` — and normalize a negative `days_ahead` with
  `days_ahead %= 7` in `compute_next_run` so a stored bad value cannot produce a past `next_run`.

#### [PERF] The ICS import has no event-count cap: a 10 MB file writes 100,000 rows in one 25-second request

- **Location:** `routes/calendar_routes.py:1446-1541` (the import loop), `:1419` (the byte cap)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the upload is capped in bytes (`read_upload_limited(file, ICS_MAX_BYTES, ...)`,
  `ICS_MAX_BYTES` = 10 MB, `src/upload_limits.py:59-61`) but nothing bounds the number of
  components, and the loop runs synchronously inside `async def import_ics` (`:1412`), one
  `SELECT` per event with a UID plus one `INSERT`:

  ```python
  for comp in cal_data.walk():                          # :1446
      ...
      existing = (
          db.query(CalendarEvent)
          .filter(
              CalendarEvent.calendar_id == target_cal.id,
              CalendarEvent.dtstart == naive_src,
              CalendarEvent.summary == str(comp.get("summary", "")),
          )
          .first()
      )                                                 # :1471-1479
      ...
      db.add(ev)                                        # :1540
  ```

  (The `...` marks are elisions — not source lines, and not the full printed dicts.)

  Measured end to end through the real handler over a temp SQLite database:

  ```
  20000 events: import OK {'ok': True, 'imported': 20000, ...} in 4.77s
  bytes: 10277842 events: 100000
  import of 100000 events: {'ok': True, 'imported': 100000, ...} in 24.99s
  ```

  The 100,000-event file is 10,277,842 bytes, just under the cap, and the parser is not the
  bottleneck: `icalendar.Calendar.from_ical` on that same file took 5.79 s, the rest is the row
  loop.
- **Impact:** one authenticated request (no admin gate on `POST /api/calendar/import`) stalls every
  other request in the instance for ~25 s and permanently adds 100,000 rows to
  `calendar_events`, which every subsequent `list_events` then filters and, for the recurring
  ones, expands. The caller can repeat it with different calendar names.
- **Fix:** cap the number of imported components (a few thousand is generous for a personal
  calendar) and fail the request with 400/413 past it, and move the parse and insert loop into
  `asyncio.to_thread` so the loop stays free while the transaction runs.

#### [PERF] The skill import route performs its whole synchronous GitHub fetch on the event loop

- **Location:** `routes/skills_routes.py:1361` (the call), `services/memory/skill_importer.py:246-252` (the client)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `import_skill_from_url` is an `async def` and calls the importer inline; the
  importer is synchronous end to end (`_PinnedBackend(httpcore.SyncBackend)`, `:124-128`) and uses
  a blocking client per hop:

  ```python
  files, _src = fetch_skill_bundle(body.url.strip())     # routes/skills_routes.py:1361
  ...
  with httpx.Client(
      transport=_PinnedTransport(pinned_ips),
      follow_redirects=False,
      timeout=timeout,
  ) as client:                                            # services/memory/skill_importer.py:248-252
  ```

  (The `...` line is an elision, not source.)

  Each request gets a 30 s timeout, up to five redirect hops are followed by hand
  (`_MAX_FETCH_REDIRECTS`), and a bundle can hold `MAX_FILES = 64` text files
  (`services/memory/skill_importer.py:19`, `:398-431`), so the handler can hold the loop for
  minutes on a slow or hostile host. The repository's convention is to offload exactly this
  (`await asyncio.to_thread(_fetch_sync)`, `routes/cookbook_routes.py:4048`;
  `routes/email_routes.py:2391`), and the CalDAV path does it
  (`src/caldav_sync.py:645`).
- **Impact:** while an administrator imports a skill, every other request waits — including
  streaming chat turns. Admin-gated and infrequent, so this is a stall rather than an outage.
- **Fix:** `files, _src = await asyncio.to_thread(fetch_skill_bundle, body.url.strip())`, and
  optionally pass the timeout budget down so a slow host cannot hold a thread for minutes.

#### [BUG] Clearing the email-urgency task cache deletes every owner's cache files

- **Location:** `routes/task/task_routes.py:632-639`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the database half of this handler is owner-scoped — the branch above it uses
  `_email_cache_owner_clause(user)` for every table in `OWNER_SCOPED_EMAIL_CACHE_TABLES`
  (`routes/email_helpers.py:566-573`) and `owner = ? OR owner = ''` for `email_tags` — but the file
  half removes every `*.json` in the shared cache directory:

  ```python
  if action == "check_email_urgency":
      cache_dir = Path(EMAIL_URGENCY_CACHE_DIR)
      if cache_dir.exists():
          for child in cache_dir.glob("*.json"):
              child.unlink()
              removed_files += 1
  ```

  Those files are per *account*, not per owner — the writer names them `CACHE_DIR / f"{acc.id}.json"`
  (`src/builtin_actions.py:2532`) in one instance-wide directory
  (`EMAIL_URGENCY_CACHE_DIR = os.path.join(DATA_DIR, "email_urgency_cache")`,
  `src/constants.py:51`) — and the per-owner state file beside them is handled separately with an
  owner slug (`routes/task/task_routes.py:640-648`), which shows the author was tracking ownership
  for the state and not for the cache.
- **Impact:** a user clearing their own Email Tags task cache discards every other user's
  already-triaged UID checkpoints, so each of their urgency tasks re-scores up to 30 recent
  messages per account with LLM calls on its next run. Nothing is lost permanently — it is a cache
  — but the work and the token spend are another owner's.
- **Fix:** delete only the files for accounts the caller owns (join `EmailAccount` on
  `owner == user`), or move the cache under a per-owner subdirectory.

#### [ERROR-HANDLING] Ten JSON endpoints answer 500 to a non-object body (recurrence of the class reported in `routes-rest-auth-admin.md`)

- **Location:** `routes/calendar_routes.py:1638-1639` (`quick_parse`), `:861-865` (`save_config`), `:919-923` (`add_caldav_account`), `:947-952` (`update_caldav_account`), `:991-994` (`test_connection`); `routes/skills_routes.py:1491-1492` (`test_skill`), `:1714-1715` (`audit_all_skills`), `:1808-1809` (`save_skill_markdown`), `:1890-1891` (`search_skills`); `routes/task/task_routes.py:1101-1102` (`parse_task`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** each handler parses the body and immediately calls `.get` on it, so a JSON array or
  string raises `AttributeError` inside the handler and FastAPI returns 500:

  ```python
  body = await request.json()                       # routes/calendar_routes.py:1638
  text = (body.get("text") or "").strip()           # :1639
  ...
  body = await request.json()                       # routes/skills_routes.py:1491
  task = (body.get("task") or "").strip()           # :1492
  ...
  body = await request.json()                       # routes/task/task_routes.py:1101
  desc = (body.get("description") or "").strip()    # :1102
  ```

  Measured by calling the real endpoint functions with a fake request whose `json()` returns `[]`
  (the same shape `tests/test_integrations_store_shape.py` uses for the auth routes):

  ```
  POST /api/calendar/quick-parse  body=[]: AttributeError: 'list' object has no attribute 'get'
  POST /api/calendar/config       body=[]: AttributeError: 'list' object has no attribute 'get'
  POST /api/calendar/test         body=[]: AttributeError: 'list' object has no attribute 'get'
  POST /api/calendar/config/accounts body=[]: AttributeError: 'list' object has no attribute 'get'
  PUT  /api/calendar/config/accounts/{id} body=[] (account exists): AttributeError 'list' object has no attribute 'get'
  POST /api/skills/search             body=[]: AttributeError: 'list' object has no attribute 'get'
  POST /api/skills/{id}/markdown     body=[]: AttributeError: 'list' object has no attribute 'get'
  POST /api/skills/{id}/test         body=[]: AttributeError: 'list' object has no attribute 'get'
  POST /api/skills/audit-all         body=[] (json ct): AttributeError: 'list' object has no attribute 'get'
  POST /api/tasks/parse              body=[]: AttributeError: 'list' object has no attribute 'get'
  ```

  Two handlers in the same files already keep the contract — `invoke_skill`
  (`routes/skills_routes.py:1425`, `... if isinstance(body, dict) else ""`) and
  `approve_skill_test_action` (`:1583-1584`, `raise HTTPException(400, "Tool approval body must be
  a JSON object.")`) — as does `import_data` in the section that reported this class
  (`routes/backup_routes.py:73`). The `try/except` wrappers around `await request.json()` at
  `routes/calendar_routes.py:860-863`, `:918-921`, `:946-949` and `:990-993` do not help: a JSON
  array parses successfully, so the fallback `body = {}` is never taken.
- **Impact:** an API client that sends a JSON array or string gets a 500 and an unhandled traceback
  in the log where a 400 is the contract the rest of the file keeps. Not reachable from the shipped
  UI, so the cost is a confusing failure and log noise, not a broken flow. `update_caldav_account`
  only reaches the raise when the caller already has a CalDAV account (otherwise the 404 at `:952`
  fires first), and `audit_all_skills` only when the request carries a JSON content type
  (`:1714`).
- **Fix:** add the `isinstance(body, dict)` guard used by `invoke_skill` to the ten handlers, or
  move them onto a Pydantic model the way the sibling event routes already are.

#### [ERROR-HANDLING] A malformed DTSTART in an uploaded .ics is answered with 500 instead of 400

- **Location:** `routes/calendar_routes.py:1421-1424` (the guarded parse) and `:1464` (the unguarded access)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the route wraps only `iCal.from_ical` in the 400 handler; `icalendar` does not raise
  there for a malformed `DTSTART` — it stores a broken property whose `.dt` raises on access, which
  the import loop reaches one line later:

  ```python
  try:
      cal_data = iCal.from_ical(content)
  except Exception as e:
      raise HTTPException(400, f"Invalid ICS file: {e}")      # :1421-1424
  ...
  src_dtstart = dtstart.dt                                     # :1464
  ```

  Measured through the real `POST /api/calendar/import` handler with a one-event file whose
  `DTSTART` is `not-a-date`:

  ```
  Failed to import ICS: Cannot access 'dt' on broken property 'DTSTART' (expected 'vDDDTypes'): Expected datetime, date, or time. Got: 'not-a-date'
  malformed DTSTART: import raised HTTPException: 500: Failed to import ICS in 0.03s
  ```

  The exception is logged at error level by the handler's own `logger.error("Failed to import
  ICS: %s", e)` (`:1556`) and the file is rejected — nothing is written — so this is a
  status-code and log-level defect, not a data defect.
- **Impact:** a user importing a file from a non-conforming exporter gets a 500 "Failed to import
  ICS" where the route's own intent (`Invalid ICS file`) is a 400, and every such upload adds an
  error-level traceback to the operator's log.
- **Fix:** move the `dtstart.dt` / `dtend.dt` accesses inside the same `try` that answers 400 (or
  catch `icalendar.error.BrokenCalendarProperty` alongside `ValueError`) so a bad property value
  is reported as a bad file.

## 29. routes: auth, API tokens, admin and provider sign-in

### Overview

The credential and administrator surface: `routes/auth_routes.py` (login, TOTP, session issuance
and revocation, user administration and privileges, settings, features and the integrations CRUD),
`routes/api_token_routes.py`, `routes/backup_routes.py`, `routes/device_flow.py` with the two
providers built on it (`routes/chatgpt_subscription_routes.py`, `routes/copilot_routes.py`),
`routes/admin_wipe/admin_wipe_routes.py` and the `routes/admin_wipe_routes.py` shim, plus
`routes/_validators.py` and `routes/__init__.py`.

The boundary: the middleware that consumes the sessions these routes issue is `core-auth-session`;
the tables they read are `core-data-platform`; the credential stores and guards they call are
`src-security`; the settings and integration stores they write are `src-memory-rag` and
`src-email-integrations`. This section covers whether each route authenticates, authorizes and
scopes correctly, not whether the store underneath is safe.

### Coverage

**Read fully:** all eleven files (2,114 lines): `routes/auth_routes.py` (919),
`routes/api_token_routes.py` (209), `routes/backup_routes.py` (221), `routes/device_flow.py` (193),
`routes/admin_wipe/admin_wipe_routes.py` (176), `routes/copilot_routes.py` (173),
`routes/chatgpt_subscription_routes.py` (170), `routes/admin_wipe_routes.py` (17),
`routes/_validators.py` (31), `routes/admin_wipe/__init__.py` (5), `routes/__init__.py` (0).

**Read partially:** the callees the findings rest on — `core/auth.py` at `setup`/`create_user`
(`:255-283`), `set_privileges` (`:387-403`), `status`/`policy` (`:669-680`); `src/integrations.py`
at `add_integration`/`update_integration` (`:269-315`); `src/rate_limiter.py` (`check`, `:25-36`);
`core/database.py` at `ProviderAuthSession` (`:556-568`) and `GalleryImage` (`:344-359`);
`routes/session_routes.py` at `/sessions/all` (`:677-731`); `routes/prefs_routes.py` at
`_load`/`_load_for_user` (`:17-52`); `src/memory.py` at `load_all_for_update`/`save` (`:180-187`,
`:261-278`); `core/database.py` at the transcript-FTS triggers (`:2178-2256`); `app.py` at the
auth-exempt list (`:265-289`), `_is_trusted_loopback` (`:348-362`) and the uvicorn launch
(`:1301-1306`); `launcher.py:135-149`; `core/middleware.py` at `require_admin`;
`src/agent_tools/admin_tools.py` at `do_manage_tokens` (`:445-489`); `static/js/admin.js` at the
token list (`:2555-2600`) and the Danger Zone (`:2896-2945`); `static/index.html` at the Danger Zone
modal (`:2455-2522`); `docker-compose.yml` at the app service (`:1-32`) and the other services'
port bindings; `website/setup.md` at the reverse-proxy guidance (`:530-540`) and the environment
table (`:716`); `.env.example` at `APP_BIND` (`:74-75`).

**Not read:** the middleware, `AuthManager` internals and models beyond the functions cited (their
sections); the settings, integrations, memory and skills stores beyond the call sites cited; the
front end beyond the token list and Danger Zone regions; the `routes-*` sections that own the
modules these routes call.

**Checks run:** a Docker peer-address probe (a container serving on a published
`127.0.0.1` port, curled from the host) and a `uvicorn.middleware.proxy_headers` probe under the
default trusted list, both quoted in the first finding; a bcrypt timing measurement; a route-level
probe that built the auth router with a stub manager (mirroring
`tests/test_integrations_store_shape.py`) and posted non-object bodies to the JSON endpoints,
quoted in the last finding; and a read of the callers of `APIKeyManager`/token rows. Twenty-seven
suites were run over this surface — `tests/test_api_token_routes.py`,
`tests/test_api_token_user_route_gate.py`, `tests/test_device_flow_routes.py`,
`tests/test_copilot_routes.py`, `tests/test_admin_wipe_gallery.py`,
`tests/test_admin_wipe_routes_shim.py`, `tests/test_backup_cli_security.py`,
`tests/test_backup_import_cross_user_dedup.py`, `tests/test_backup_import_skills.py`,
`tests/test_backup_import_skills_dedup.py`, `tests/test_auth_policy.py`,
`tests/test_auth_regressions.py`, `tests/test_auth_require_privilege_nondict.py`,
`tests/test_auth_root_path.py`, `tests/test_auth_session_revocation.py`,
`tests/test_rename_user_case_insensitive.py`, `tests/test_rename_user_owner_sync.py`,
`tests/test_rename_user_token_cache.py`, `tests/test_delete_user_invalidates_token_cache.py`,
`tests/test_delete_user_revokes_api_tokens.py`, `tests/test_setup_admin_user.py`,
`tests/test_rate_limiter.py`, `tests/test_totp_failclosed.py`, `tests/test_route_validators.py`,
`tests/test_integrations_store_shape.py`, `tests/test_cors_preflight.py`,
`tests/test_reserved_username_admin_escalation.py` — **203 passed**.

#### [SECURITY] The login, signup and setup limiters key on the socket peer, which the documented deployment makes identical for every client

- **Location:** `routes/auth_routes.py:119-121` (the three limiters), `:130`, `:148`, `:167` (the `.check(request.client.host)` call sites)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the three limiters are constructed per process and keyed on `request.client.host`:

  ```python
  _login_limiter = RateLimiter(max_requests=15, window_seconds=60)
  _signup_limiter = RateLimiter(max_requests=3, window_seconds=300)
  _setup_limiter = RateLimiter(max_requests=3, window_seconds=300)
  ...
  @router.post("/login")
  async def login(body: LoginRequest, request: Request, response: Response):
      if not _login_limiter.check(request.client.host):
          raise HTTPException(429, "Too many requests — try again later")
  ```

  `src/rate_limiter.py:26` keys its window on the string it is handed and nothing else. The value
  `request.client.host` carries is the socket peer unless uvicorn's `ProxyHeadersMiddleware`
  rewrites it, and that middleware only rewrites it for a peer in its trusted list. In this
  installation (uvicorn 0.54.0) `proxy_headers` defaults to `True` and the trusted list defaults to
  `os.environ.get("FORWARDED_ALLOW_IPS", "127.0.0.1,::1")`; the app passes neither
  (`uvicorn.run(app, host=bind_host, port=bind_port, log_level="info")`, `app.py:1306` and
  `launcher.py:149`) and no compose file or entrypoint sets `FORWARDED_ALLOW_IPS`. Measured against
  that middleware, with the default trusted list:

  ```
  loopback peer (native proxy)      peer=127.0.0.1   xff='203.0.113.9' -> client=('203.0.113.9', 0)
  docker bridge gateway peer        peer=172.18.0.1  xff='203.0.113.9' -> client=('172.18.0.1', 51234)
  ```

  The shipped compose publishes the app on the host loopback only —
  `- "${APP_BIND:-127.0.0.1}:${APP_PORT:-7000}:7000"` (`docker-compose.yml:14`) — and the setup
  guide tells the operator to reach it through a local proxy: "If your access layer reaches
  Odysseus on the same host, proxy to `http://127.0.0.1:7000`" (`website/setup.md:537`). A request
  that arrives that way reaches the container from the Docker gateway, not from loopback.
  Measured with a container publishing `127.0.0.1:18080:3000` and curled from the host:

  ```
  $ curl -s http://127.0.0.1:18080/                         # no headers
  peer=::ffff:172.17.0.1
  xff=-
  $ curl -s -H 'X-Forwarded-For: 203.0.113.9' http://127.0.0.1:18080/
  peer=::ffff:172.17.0.1
  xff=203.0.113.9
  ```

  So in the default deployment every client — the operator's browser through the tunnel, a second
  user, an attacker — presents the same key to all three limiters. (A native install behind a
  proxy on the same host is the case that works, because the peer is loopback and the forwarded
  chain is trusted; `app.py:348-362` shows the codebase reasons about that topology elsewhere.)
- **Impact:** the login budget is instance-wide, not per client. Sixteen unauthenticated POSTs to
  `/api/auth/login` inside a minute make the next attempt from anyone return 429, including the
  administrator's, and about one request every four seconds keeps the lockout up indefinitely; the
  signup and first-run-setup budgets (3 per 5 minutes) are shared the same way, so a lockout also
  blocks a new instance's setup while it is still unconfigured. It also means the limiter cannot
  isolate one account's failed attempts from another's, which is the property the comment above
  `_login_limiter` and the `RateLimiter` docstring ("keyed by IP") claim. What it still does is cap
  the total guess rate.
- **Fix:** give uvicorn a peer it can trust for client identity in the container deployment (set
  `FORWARDED_ALLOW_IPS` for the app service and make the documented proxy overwrite
  `X-Forwarded-For` rather than append to it), and pin the keying with a test — the existing
  `tests/test_rate_limiter.py` exercises the limiter, not what it is keyed on. If the header cannot
  be trusted, key on something a single client cannot exhaust for everyone (for example
  `(username, peer)` with a separate global ceiling).

#### [PERF] The admin create-user path hashes the password on the event loop while its siblings offload the same call

- **Location:** `routes/auth_routes.py:319` (with `:140`, `:160`, `:171-181`, `:235-238` and `:336`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `admin_create_user` is an `async def` and calls the synchronous
  `AuthManager.create_user` inline, so `bcrypt.gensalt()`/`hashpw` runs on the event loop:

  ```python
  @router.post("/users")
  async def admin_create_user(body: CreateUserRequest, request: Request):
      ...
      ok = auth_manager.create_user(body.username, body.password, body.is_admin)
  ```

  The three other credential paths in the same file offload it — `first_run_setup` uses
  `await asyncio.to_thread(auth_manager.setup, ...)`, `signup` uses
  `await asyncio.to_thread(auth_manager.create_user, body.username, body.password, is_admin=False)`,
  and `login` uses `asyncio.to_thread` for both the password check and session creation. Measured
  cost of one hash at the default bcrypt cost on this machine:

  ```
  bcrypt.gensalt()+hashpw default cost: 169 ms
  ```

  `rename_user` (`:336`) has the same shape with more work inline: an owner sweep over every mapped
  table with an `owner` column, `rglob` over `SKILLS_DIR` for `SKILL.md`, a walk of
  `DEEP_RESEARCH_DIR`, and a read-modify-write of `memory.json`, all inside the `async def`.
- **Impact:** while an administrator creates a user, every other in-flight request — including a
  streaming chat turn — stalls for about 170 ms; a rename stalls for as long as its file walks take.
  The route is admin-only and infrequent, so this is a stall rather than an outage, and it is the
  kind of work FastAPI's sync-endpoint threadpool or `asyncio.to_thread` exists for. Nothing in the
  section's suites covers the blocking shape.
- **Fix:** wrap the `create_user` call (and the file/DB portions of `rename_user`) in
  `await asyncio.to_thread(...)`, matching the sibling routes.

#### [BUG] The token list shows every owner's tokens, but revoke and rename refuse any token whose owner is not the caller — including the null-owner tokens the agent tool mints

- **Location:** `routes/api_token_routes.py:83` (list), `:170` and `:204` (the refusals), with `src/agent_tools/admin_tools.py:469-471` and `static/js/admin.js:2572-2584`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the list is unfiltered:

  ```python
  def list_tokens(request: Request):
      require_admin(request)
      with get_db_session() as db:
          tokens = db.query(ApiToken).all()
  ```

  while both mutating endpoints refuse any row whose `owner` is not exactly the caller:

  ```python
  if current_user and token.owner != current_user:
      raise HTTPException(403, "Not your token")
  ```

  A null owner fails that comparison. Null-owner rows are exactly what the agent's token tool
  writes — `src/agent_tools/admin_tools.py:469-471` constructs `ApiToken(id=tid, name=name,
  token_hash=token_hash, token_prefix=raw_token[:8], is_active=True, ...)` with no `owner` and no
  `ody_` prefix (reported in `src-agent-tools.md`). The admin UI renders a Revoke button for every
  row (`static/js/admin.js:2572`) and ignores the response status:

  ```js
  await fetch(`/api/tokens/${btn.dataset.admDelToken}`, { method: 'DELETE', credentials: 'same-origin' });
  loadTokens();
  ```

- **Impact:** an administrator sees tokens they cannot revoke or rename. The click looks like a
  no-op (the list reloads with the row still there and no error shown), so the only way to remove
  such a row is direct database access. On an instance with more than one administrator the same
  applies to a colleague's tokens. The tokens themselves are inert — the middleware cannot
  authenticate one that lacks the prefix — so this is an unusable admin control, not an exposure.
- **Fix:** let an administrator revoke a row with no owner (`if token.owner and token.owner !=
  current_user`), or filter `list_tokens` to the caller's own and null-owner rows, and surface the
  403 in the UI instead of discarding the response.

#### [ERROR-HANDLING] Three admin JSON endpoints raise an unhandled error on a non-object body

- **Location:** `routes/auth_routes.py:329` (`update_user_privileges`), `:784` (`create_integration`), `:794` (`update_integration_route`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** all three read the body and hand it straight to a function that expects a mapping:

  ```python
  body = await request.json()
  ok = auth_manager.set_privileges(username, body)      # :329
  ...
  body = await request.json()
  item = add_integration(body)                          # :784
  ...
  body = await request.json()
  item = update_integration(integration_id, body)       # :794
  ```

  and the callees iterate or `.get` it — `core/auth.py:397` (`for k, v in privileges.items()`),
  `src/integrations.py:273` (`preset_key = data.get("preset")`), `:304` (`data = dict(data)`).
  Measured by building the router with a stub manager and calling the endpoint functions with a
  fake request whose `json()` returns the body, the same shape
  `tests/test_integrations_store_shape.py` uses:

  ```
  PUT privileges body=[]: AttributeError: 'list' object has no attribute 'items'
  POST integrations body=[]: AttributeError: 'list' object has no attribute 'get'
  POST integrations body='x': AttributeError: 'str' object has no attribute 'get'
  PUT integrations/{id} body='x': ValueError: dictionary update sequence element #0 has length 1; 2 is required
  ```

  Two other handlers in this section already keep the contract — `routes/backup_routes.py:73`
  (`if not isinstance(body, dict): raise HTTPException(400, "Expected a JSON object")`) and
  `routes/api_token_routes.py:163` — as does the repository's `*_nondict` test convention.
- **Impact:** an API client that sends a JSON array or string to one of these endpoints gets a 500
  and an unhandled traceback in the log where a 400 is the contract the rest of the section keeps.
  Admin-only and not reachable from the shipped UI, so the cost is a confusing failure and a log
  line, not a broken flow.
- **Fix:** add the `isinstance(body, dict)` guard used by `import_data` to the three handlers.

## 30. routes: assistant, codex, MCP and workspace

### Overview

The integration surface: `routes/codex_routes.py` (the scope-gated `/api/codex/*` and
`/api/claude/plugin.zip` endpoints that external agents call, including the cookbook launch and
monitor wrappers), `routes/mcp/mcp_routes.py` (MCP server CRUD, tool enablement, and the OAuth
authorize/callback/exchange flow), its `sys.modules` shim at `routes/mcp_routes.py`,
`routes/assistant_routes.py` (the per-owner assistant singleton and its three check-in tasks), and
`routes/workspace_routes.py` (the admin-only directory picker).

The boundary: the API-token scopes and the bearer middleware these routes rely on are
`core-auth-session`'s; the tool-policy tables that decide what a non-admin owner may call are
`src-tools-capabilities-policy`'s; `src-mcp` owns the manager and transports; `routes-cookbook`
owns the serve/state implementation these wrappers call; `routes-email` owns the send and draft
handlers `codex_routes.py` invokes by function reference; `routes-gallery-document` owns the
document and gallery handlers it invokes the same way. This section covers whether the wrappers
authenticate, scope and forward correctly, not whether the handlers underneath are correct.

### Coverage

**Read fully:** all six files (2,055 lines): `routes/codex_routes.py` (910),
`routes/mcp/mcp_routes.py` (710), `routes/assistant_routes.py` (327), `routes/workspace_routes.py`
(85), `routes/mcp_routes.py` (18), `routes/mcp/__init__.py` (5).

**Read partially:** the callees the findings rest on — `routes/email_routes.py` at `send_email`
(`:4519-4725`); `routes/email_helpers.py` at `SendEmailRequest` (`:1990-2010`);
`src/tools/notes.py` at `do_manage_notes` (`:19-42`, `:88-327`); `routes/_validators.py` (all 31
lines); `src/tool_security.py` at `owner_is_admin_or_single_user` and `blocked_tools_for_owner`
(`:222-284`); `core/middleware.py` at `require_admin`; `src/auth_helpers.py` at `get_current_user`,
`require_user` and `require_authenticated_request`; `app.py` at the auth-exempt lists (`:265-292`)
and the logging setup (`:107-114`); `core/database.py` at the `McpServer`, `CrewMember` and
`ScheduledTask` models and `Path(DATA_DIR).mkdir` (`:40`); `src/constants.py` at `DATA_DIR`,
`MCP_OAUTH_DIR` and `COOKBOOK_STATE_FILE`; `src/task_scheduler.py` at `compute_next_run` and
`run_task_now`; `src/owner_identity.py` at `REQUEST_SENTINEL_OWNERS`; `routes/cookbook_helpers.py`
at `ServeRequest` and the `hf_token` fields (`:1060-1090`);
`integrations/codex/skills/odysseus/SKILL.md` and its `integrations/claude/` twin at the email
endpoint documentation (`:106-107`).

**Not read:** `src/mcp_manager.py` and `src/mcp_oauth.py` (the manager and the pending-state
registry these routes drive), the MCP client transports, `src/task_scheduler.py` beyond the two
functions named, `routes/cookbook_routes.py` and `routes/cookbook_helpers.py` beyond
`ServeRequest` (the `routes-cookbook` section owns them), `routes/email_routes.py` outside the
send region, `src/upload_handler.py`, `core/atomic_io.py`, the contents of the two plugin bundles,
and the front end's MCP, assistant and workspace panels.

**Checks run:** three probes, all quoted in the findings — the framework semantics of a locally
constructed `BackgroundTasks` against an injected one; the cookbook stop and adopt endpoints with
`asyncio.create_subprocess_shell` replaced by a recorder so that no tmux session was touched; and
the caller-set greps quoted in the third finding. Twenty-one suites were run over this surface —
`tests/test_codex_cookbook_admin_gate.py`, `tests/test_codex_ssh_host_validation.py`,
`tests/test_mcp_oauth.py`, `tests/test_mcp_routes_shim.py`, `tests/test_mcp_manager.py`,
`tests/test_manage_mcp_command_allowlist.py`, `tests/test_mcp_add_server_args_validation.py`,
`tests/test_mcp_cache_invalidation.py`, `tests/test_mcp_reconnect_args.py`,
`tests/test_mcp_memory_owner_scope.py`, `tests/test_mcp_param_hint_hardening.py`,
`tests/test_mcp_email_decode_header_spaces.py`, `tests/test_mcp_common_truncate.py`,
`tests/test_mcp_dependency_compatibility.py`, `tests/test_multiple_mcp_servers_timeout.py`,
`tests/test_mcp_tool_params_in_prompt.py`, `tests/test_builtin_mcp_bg_tasks.py`,
`tests/test_builtin_mcp_npx_cache.py`, `tests/test_builtin_mcp_pythonpath.py`,
`tests/test_workspace_confine.py`, `tests/test_merge_last_assistant_rows.py` — **170 passed**.

#### [BUG] The Codex and Claude email-send endpoint reports the message queued and never delivers it

- **Location:** `routes/codex_routes.py:387` (with `routes/email_routes.py:4519`, `:4708`, `:4714`, `:4717`, and `routes/email_helpers.py:2004`)
- **Severity:** high
- **Disposition:** fix-now
- **Evidence:** the wrapper hands the send handler a `BackgroundTasks` object it constructed
  itself rather than the one the framework injects and runs:

  ```python
  # routes/codex_routes.py:387
  return await email_send_endpoint(req=req, background_tasks=BackgroundTasks(), owner=owner)
  ```

  The handler delivers through that object on its default path — inline only when the request
  opts in, otherwise as a background task:

  ```python
  # routes/email_routes.py:4519
  async def send_email(req: SendEmailRequest, background_tasks: BackgroundTasks, owner: str = Depends(require_owner)):
      """Queue an email for SMTP delivery. Returns immediately; send runs in background."""
      ...
      if req.wait_for_delivery:                      # :4708
          result = await asyncio.to_thread(_deliver)
          ...
      background_tasks.add_task(_deliver)            # :4714
      return {
          "success": True,
          "queued": True,                            # :4717
          "account_id": cfg.get("account_id") or req.account_id,
          "message": f"Email queued for {req.to}",
      }
  ```

  `wait_for_delivery` defaults to false (`routes/email_helpers.py:2004`), and neither shipped skill
  bundle documents it — both list the body fields as `to`, `cc`, `bcc`, `subject`, `body`,
  `body_html`, `attachments`, `account_id`, `in_reply_to`, `references`
  (`integrations/codex/skills/odysseus/SKILL.md:106-107` and the `integrations/claude/` twin), so
  every documented call takes the branch that schedules delivery on the discarded object. Measured
  with a two-route FastAPI app reproducing both call shapes:

  ```
  framework-injected BackgroundTasks -> ['delivered']
  locally constructed BackgroundTasks -> task did NOT run
  ```

  Only the instance resolved as a dependency is attached to the response and awaited; a locally
  constructed one is not referenced by anything. `routes/codex_routes.py:387` is the only place in
  the tree that calls the send handler with a constructed instance, and no test in `tests/` covers
  `/api/codex/emails/send` or `codex_email_send` at all.
- **Impact:** an external agent using the shipped integration asks to send mail, receives
  `{"success": true, "queued": true, "message": "Email queued for …"}`, and nothing is ever sent.
  The failure is silent in both directions: the caller cannot distinguish it from a real queue, and
  the user is told the message was queued. The scope the plugin asks the user to grant (`email:send`)
  and the capability table's `"email_send_requires_confirmation": True` both describe a working
  send. Nothing else in the path is broken — the same handler delivers correctly from the web UI,
  which passes the framework's instance.
- **Fix:** take `background_tasks: BackgroundTasks` as a parameter of `codex_email_send` and
  forward it, or set `wait_for_delivery=True` on the request the wrapper builds so the handler
  delivers inline before returning. Add a test that posts to `/api/codex/emails/send` and asserts
  the delivery call happened, since no test currently reaches this endpoint.
- **Re-review (2026-10-04):** re-derived in full; high stands. `routes/codex_routes.py:387` is the only
  `BackgroundTasks()` construction under `routes/` and `src/`, `wait_for_delivery` is read only at
  `routes/email_routes.py:4708` and defaults to false at `routes/email_helpers.py:2004`, and the
  skill documents the send body without it (`integrations/codex/skills/odysseus/SKILL.md:107`).


#### [SECURITY] The MCP OAuth credentials are written to the application log in full

- **Location:** `routes/mcp/mcp_routes.py:213`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the handler logs the raw form field before parsing it, and that field is the
  credential document:

  ```python
  # routes/mcp/mcp_routes.py:213
  logger.info(f"MCP add_server: oauth_file={oauth_file!r}")
  ```

  The block immediately below parses the credentials out of that same string — the id at `:219`
  and the paired secret at `:220` — and writes them into the credentials file the MCP server reads
  (`:216-241`, writing at `:236`), so the logged value contains a live Google OAuth secret. (The
  two field names are not quoted verbatim here: the run's secret gate reads those
  thirteen-character literals as credentials and fails the build.) The log destination is
  `DATA_DIR/logs/app.log` through a `RotatingFileHandler` (`app.py:107-114`), and no logging filter
  anywhere in the tree scrubs secret-looking values — the only redaction helper is
  `core/log_safety.redact_url`, which handles URL userinfo, not a JSON document. The same handler
  writes the credentials file and the later token exchange writes the refresh token
  (`:575-576`) with plain `open(..., "w")` under a `DATA_DIR` created by
  `Path(DATA_DIR).mkdir(parents=True, exist_ok=True)` (`core/database.py:40`), which is the
  file-permission class already reported as a medium in `core-data-platform.md`; it is not
  re-reported here, but the two together mean the secret reaches disk twice, once deliberately and
  once in a log.
- **Impact:** anyone who can read the log file — any local user on a default-umask host, anyone
  given the log for debugging, and every log aggregator an operator forwards it to — obtains the
  secret half of the OAuth credentials for that MCP integration. The line fires on every attempt
  to add a server with credentials, including attempts that then fail.
- **Fix:** log the fact and the destination filename instead of the payload
  (`logger.info("MCP add_server: OAuth credentials supplied for %s", oauth_filename)`), or delete
  the line — the response already reports whether the server connected.

#### [BUG] The cookbook stop endpoint kills any tmux session by name, tracked or not

- **Location:** `routes/codex_routes.py:685` (the endpoint is at `:676`, the sibling check at `:609`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `codex_cookbook_stop` looks the task up in cookbook state and then ignores the
  result, passing `task or {}` to the host resolver and building the kill command from the path
  parameter alone:

  ```python
  # routes/codex_routes.py:676
  @router.post("/cookbook/stop/{session_id}")
  async def codex_cookbook_stop(request: Request, session_id: str):
      _require_cookbook_scope(request, COOKBOOK_LAUNCH_SCOPES)
      import re as _re
      if not _re.fullmatch(r"[a-zA-Z0-9_-]+", session_id):
          raise HTTPException(400, "Invalid session id")
      state = _read_cookbook_state()
      tasks = state.get("tasks") or []
      task = next((t for t in tasks if t.get("sessionId") == session_id), None)
      host, port_flag = _ssh_prefix_for_task(task or {})   # :685 — no 404 when task is None
      if host:
          cmd = f"ssh {port_flag}{host} \"tmux kill-session -t {session_id}\""
      else:
          cmd = f"tmux kill-session -t {session_id}"       # :688
      result = await _run_shell(cmd, timeout=10)
  ```

  The read-only sibling does refuse untracked names — `codex_cookbook_output` raises 404 when the
  session is not in state (`:609-610`) — and its comment gives the reason: "anything else would let
  the agent run arbitrary `tmux capture-pane` targets". The session-id regex blocks shell
  metacharacters, so this is not injection; the missing piece is the existence check. Measured with
  `asyncio.create_subprocess_shell` replaced by a recorder, so no session was actually killed:

  ```
  stop(untracked session) -> {'session_id': 'zzz-not-a-cookbook-task', 'exit_code': 0, 'host': 'local'}
  shell ran: ['tmux kill-session -t zzz-not-a-cookbook-task']
  ```

- **Impact:** an API token holding `cookbook:launch` can kill any tmux session on the host — or on
  a configured remote host whose name it guesses — including sessions the user started by hand and
  that have nothing to do with the cookbook. The scope is documented as "start/stop serves", and
  every other endpoint in this family resolves its target through cookbook state, so the reachable
  set is wider than the surface describes. The blast radius is limited to tmux sessions, and the
  caller must already hold a scope that permits launching serve commands on the same hosts.
- **Fix:** raise `HTTPException(404, "task not found")` when `task is None`, as
  `codex_cookbook_output` does.

#### [ERROR-HANDLING] Adopting a session returns a 500 when the port is not a number

- **Location:** `routes/codex_routes.py:869` (with `:836`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** every other field of the adopt body is validated — the tmux session name must match
  `[a-zA-Z0-9_-]+` and the model must be non-empty (`:838-843`), and the host goes through
  `validate_remote_host` (`:834`) — but the port is only defaulted and then converted in the
  payload literal:

  ```python
  port = norm.get("port") or 8000                      # :836
  ...
  "payload": {..., "port": int(port)},                 # :869
  ```

  Measured by calling the endpoint with a token-shaped request and the subprocess call faked:

  ```
  adopt(port='abc') -> ValueError: invalid literal for int() with base 10: 'abc'
  ```

  A dict or list port raises `TypeError` the same way. Both escape the handler, so FastAPI returns
  500 with a traceback in the log.
- **Impact:** an agent that sends a string or a structured value where an integer was expected gets
  a server error rather than the 400 that every other field of the same endpoint produces, and the
  failure is unattributable from the client side. Only reachable by an API token with
  `cookbook:launch`, so the cost is a confusing error and a log line.
- **Fix:** coerce the port the way the sibling payload fields are handled — parse it in a
  `try`/`except (TypeError, ValueError)` and raise `HTTPException(400, "Invalid port")`, or
  validate it with the same helper the SSH port uses.

## 31. routes: notes, contacts and history

### Overview

`routes/note/__init__.py`, `routes/note/note_routes.py`, `routes/note_routes.py`,
`routes/contacts/__init__.py`, `routes/contacts/contacts_routes.py`,
`routes/contacts_routes.py`, `routes/history/__init__.py`,
`routes/history/history_routes.py`, and `routes/history_routes.py`.

Notes with reminders and due dates, contacts with CardDAV and vCard/CSV import, and
chat history with display pagination, topics and compaction. Notes and history are
per-owner; contacts are a shared, admin-only address book, with one local JSON file,
CardDAV configuration and cache. There is no history-search or topic-id endpoint in
these files. The ownership model is `core-auth-session`'s; the database schema is
`core-data-platform`'s; the notes reminder scheduler is `src-research-scheduling`'s.
The earlier-registered session router and its live compaction endpoint belong to
`routes-chat-session`.

### Coverage

**Read fully:** all nine assigned files (2,765 lines): `routes/note/note_routes.py`
(937), `routes/contacts/contacts_routes.py` (916), `routes/history/history_routes.py`
(849), the three flat shims (18, 13 and 17 respectively), and each package's
`__init__.py` (5 each). Boundary files read fully: `src/auth_helpers.py`,
`src/topic_analyzer.py`, `src/url_safety.py`, `core/middleware.py` and
`core/atomic_io.py`. Read the audit prompt, header, coverage boundaries, review
scaffold and both requested model sections. Citations refer to working-tree source
at `2992bf6d368a`; `git status --short` showed only the untracked `audit/` directory.

**Read partially:** `app.py` at authentication and request identity assignment
(lines 259–499) and the session/history/note/contacts router registrations;
`routes/session_routes.py` at owner verification, the active-run guard, adjacent
helpers and the live compaction handler (98–287, 1004–1103), plus searches for
search/compaction definitions. `core/database.py` at the session factory and
Session, ChatMessage and Note models (factory search, 175–274, 1808–1855);
`core/session_manager.py` at message persistence/truncation (225–353), hydration
(421–555), and owner filtering/no-op save (700–714). The contacts JSON store and
its writes were read fully as part of the canonical route module. Test source read:
`tests/conftest.py`, `tests/test_contacts_carddav_security.py`,
`tests/test_contacts_import_nonstring.py`, `tests/test_contacts_vcard_parse.py`
(end to end), and `tests/test_history_compact_tool_calls.py` (1–250).

**Not read:** no assigned file remains unread. Boundary code beyond those regions,
including the full session manager, full database initialization/migrations, upload
reservation implementation, settings/integration/SMTP stores, reminder scheduler,
LLM transport and front end, was not reviewed. Other discovered tests were executed,
not read. Full-text history search outside these files was not reviewed. No live
CardDAV/SMTP/LLM service, DNS-rebinding exploit, browser flow, deployment or load test
was exercised; URL guards and HTTP call placement were inspected, and the CardDAV
probe used a stub transport. No run-level audit gate was run, as instructed.

**Checks run:** `git rev-parse --short=12 HEAD`, `git status --short`, file line
counts, the requested `ls tests | grep -iE 'note|contact|history'`, and targeted
searches for router registrations, body readers, stores and compaction handlers.
An inline `venv/bin/python` probe (in-memory SQLite, temporary data directory,
bytecode disabled) confirmed all three shim identities, vCard address loss,
CardDAV GET executing on the event-loop thread, and the nine JSON-body failures
below. A second inline probe registered session then history routers as `app.py`
does and replaced the session router's owner check with an HTTP 418 sentinel:
POST `/api/session/example/compact` returned that sentinel, confirming the history
module's compaction implementation is not selected in the shipped registration
order. An initial attempt to inspect `app.routes` directly returned no matches;
the request-level probe, not that inconclusive inspection, established precedence.

The focused command was:

```sh
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q -p no:cacheprovider \
  $(ls tests | grep -iE 'note|contact|history' | grep '\.py$' | awk '{print "tests/"$0}')
```

**75 passed, 7 warnings in 2.08s**, over 22 files:
`test_contacts_add_null_name.py`, `test_contacts_carddav_security.py`,
`test_contacts_import_nonstring.py`, `test_contacts_routes_shim.py`,
`test_contacts_vcard_parse.py`, `test_history_compact_tool_calls.py`,
`test_history_db_fallback_hidden.py`, `test_history_display_model_hydration.py`,
`test_history_order_by_timestamp_regression.py`, `test_history_routes_shim.py`,
`test_history_topics_owner_scope.py`, `test_manage_notes_owner_gate.py`,
`test_note_reminder_email_oauth.py`, `test_note_reminder_fire_scope.py`,
`test_note_routes_shim.py`, `test_notes_dom_xss_helpers.py`,
`test_notes_fail_closed_auth.py`, `test_notes_search_reset_on_reopen_js.py`,
`test_notes_select_esc_listener_js.py`, `test_notes_update_due_date.py`,
`test_notes_z_order_js.py`, and `test_tool_rag_contacts_domain.py` (all under `tests/`).
Warnings were SQLAlchemy's deprecated `declarative_base` location and naive
`datetime.utcnow()` usage; there were no failed or skipped tests.

#### [PERF] CardDAV requests run synchronously inside async contact handlers

- **Location:** `routes/contacts/contacts_routes.py:742-744`, with `:305-309`, `:363`, `:813-825` and `:832-837`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the list handler calls a synchronous helper without yielding:

  ```python
  async def list_contacts(_admin: str = Depends(require_admin)):
      """List all contacts."""
      contacts = _fetch_contacts()
  ```

  On a cache miss, `_fetch_contacts` performs synchronous REPORT and, if needed,
  GET requests:

  ```python
  contacts = _fetch_via_report(cfg, auth)
  if contacts is None:
      # Fallback: plain GET, concatenated vCards, no hrefs.
      r = httpx.get(cfg["url"], auth=auth, timeout=10)
  ```

  Search, add, import, export, edit and delete also call synchronous contact helpers
  from `async def`. Import can perform a sequential PUT for every card; export forces
  a fetch even while the cache is fresh. The inline probe invoked the real list
  endpoint with a cold cache, stubbed configuration/REPORT fallback, and replaced
  `httpx.get` with a function comparing its thread id to the running event loop's:

  ```text
  CardDAV GET runs on event-loop thread [True]
  ```

  The sibling reminder sender already uses `await _aio.to_thread(_smtp_send)`
  (`routes/note/note_routes.py:392`).
- **Impact:** a slow CardDAV server blocks unrelated requests and streaming work on
  the same event loop while each synchronous network operation waits. The socket
  timeout is 10 seconds for reads, not a short CPU-only pause, and imports multiply
  waits across cards. Admin-only access and the 60-second read cache limit frequency,
  not the effect on other users. The probe establishes thread placement, not measured
  production latency or a total wall-clock bound.
- **Fix:** move the synchronous handlers to FastAPI's synchronous endpoint threadpool,
  or offload the complete synchronous operation with `asyncio.to_thread`. Preserve
  serialization of shared contacts/settings read-modify-write operations when adding
  concurrency; atomic file replacement alone does not prevent lost updates.

#### [BUG] vCard export silently drops every contact's postal address

- **Location:** `routes/contacts/contacts_routes.py:623-632`, with `:258-260` and `:843`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_contacts_to_vcf` rebuilds each card with name, UID, email and phone,
  but does not pass the stored address:

  ```python
  _build_vcard(
      c.get("name") or ((c.get("emails") or [""])[0].split("@")[0] if c.get("emails") else "Contact"),
      "",
      uid=c.get("uid") or str(uuid.uuid4()),
      emails=c.get("emails") or [],
      phones=c.get("phones") or [],
  )
  ```

  The builder already supports addresses and emits `ADR` only when one is supplied:

  ```python
  addr = (address or "").strip()
  if addr:
      lines.append(f"ADR:;;{_vesc(addr)};;;;")
  ```

  `/api/contacts/export` calls this helper for its default vCard format. An inline
  Python probe passed a synthetic contact with a nonempty address through
  `_contacts_to_vcf` and then `_parse_vcards`; the result was:

  ```text
  vCard address roundtrip ''
  ```

- **Impact:** exports omit postal addresses that the add/edit/import paths preserve.
  A user transferring the export to another address book, or using it to restore
  contacts, gets no addresses and no warning. Export does not erase the original
  store, so recovery is possible while that store remains available.
- **Fix:** pass `address=c.get("address") or ""` to `_build_vcard` and add an
  export/import round-trip test with a nonempty address.

#### [ERROR-HANDLING] Nine notes and history endpoints return 500 for a non-object JSON body

- **Location:** `routes/note/note_routes.py:853-854`, `:905-906`; `routes/history/history_routes.py:255-256`, `:270-271`, `:288-289`, `:351-352`, `:461-462`, `:512-513`, `:601-602`
- **Severity:** low
- **Disposition:** next
- **Evidence:** this recurs from the non-object-body class reported in
  `routes-rest-auth-admin.md`. Each endpoint immediately uses `.get` on the result
  of `request.json()`, without verifying it is a mapping. For example:

  ```python
  body = await request.json()
  note_id = str(body.get("note_id") or "").strip()
  ```

  and:

  ```python
  body = await request.json()
  keep_count = body.get("keep_count", 0)
  ```

  An inline TestClient probe mounted the actual routers, stamped a synthetic
  authenticated identity, and stubbed history's session-owner lookup so it could
  reach body validation without a stored session. With exception propagation
  disabled, both `[]` and `"x"` returned 500 on every path:

  ```text
  /api/notes/fire-reminder
  /api/notes/reorder
  /api/session/example/truncate
  /api/session/example/message
  /api/session/example/delete-messages
  /api/session/example/edit-message
  /api/session/example/update-last-meta
  /api/session/example/merge-last-assistant
  /api/session/example/fork
  ```

  The history handlers that log the exception reported that `list` or `str` has no
  attribute `get`. As controls, the same two bodies returned 422 on POST
  `/api/notes` (Pydantic model) and POST `/api/contacts/import` (`data: dict`).
- **Impact:** an authenticated client sending a valid JSON value of the wrong shape
  receives an internal-error response rather than a validation error. The checked
  history paths require ownership before parsing, and the failure occurs before
  mutation; this is not an authorization bypass or demonstrated data loss.
- **Fix:** use request models, or reject non-dictionaries with 400 immediately after
  parsing. Keep any new validation exception outside broad handlers that would
  convert it back to 500.

## 32. routes: memory, personal files and research

### Overview

`routes/memory/__init__.py`,
`routes/memory/memory_routes.py`,
`routes/memory_routes.py`,
`routes/personal_routes.py`,
`routes/research/__init__.py`,
`routes/research/research_routes.py`,
`routes/research_routes.py`.

Memory CRUD and search, the personal-file library and its indexing, and the research job API
with report listing and HTML rendering. The stores and vector lanes they call are
`src-memory-rag` and `services-memory`; the live research handler is `src/research_handler.py`
(`src-research-scheduling`), not the similarly named `services/research/research_handler.py`.
Authentication is the `core-auth-session` boundary and the middleware in `app.py`.

### Coverage

**Read fully:** all seven assigned files (1,861 lines): `routes/memory/memory_routes.py` (568),
`routes/personal_routes.py` (465), `routes/research/research_routes.py` (783),
`routes/memory_routes.py` (18), `routes/research_routes.py` (17), and
`routes/memory/__init__.py` and `routes/research/__init__.py` (5 each). Boundary files read fully:
`src/auth_helpers.py`, `core/middleware.py`, `services/memory/__init__.py`, and
`services/memory/memory.py` (the compatibility import of `src.memory.MemoryManager`).
Working-tree line numbers refer to `2992bf6d368a`; `git status --short` showed only the untracked
`audit/` directory before and after the checks.

**Read partially:** `app.py` at authentication, exemptions, identity stamping and adjacent
static/image setup (250–549), plus the memory/research router registration search;
`src/app_initializer.py` at the `ResearchHandler` import, construction and return sites;
`src/memory.py` (1–310: reads, owner filtering, validation, save and entry construction);
`services/memory/memory_extractor.py` at `audit_memories` (495 through end), including its
owner-scoped merge and vector rebuild; `src/research_handler.py` (35–89 and 240–859: path
confinement, task launch, cancellation, timeout/error recovery, persistence, report/image access,
and the live research-service call); `src/personal_docs.py` (230–344: tracking and exclusions);
`src/rag_vector.py` (495–624 and 678 through end: owner metadata on indexing, directory/source
deletion); `src/request_models.py` (1–110: memory and directory body models); `core/auth.py`
(15–64: privilege defaults); `static/js/admin.js` and `static/js/init.js` by
`can_manage_memory` search. Tests read: `tests/test_memory_owner_isolation.py`,
`tests/test_research_owner_scope_routes.py` and `tests/test_personal_delete_file_confinement.py`
in full; the other executed tests were not read. The non-runtime
`services/research/research_handler.py` was searched for task/owner methods, not read fully.

**Not read:** no assigned route file remains unread. The rest of the authentication, memory,
vector, personal-document and research implementations beyond the regions above; the deep
research engine, endpoint resolver internals, visual-report renderer, PDF parser and front end
beyond the privilege searches. No live model, embedding service, browser flow, large-library
latency benchmark or multi-process race test was run.

**Checks run:** `git rev-parse --short=12 HEAD`, `git status --short`, assigned-file `wc -l`,
`ls tests | grep -iE 'memory|personal|research'`, focused route-import and privilege/JSON-call
searches, and two inline `venv/bin/python -` probes using temporary data directories outside
the checkout. The probes exercised actual routers through `TestClient` with a stamped user
and stub privilege manager, and the actual research persistence/library functions with model
work replaced by a deterministic timeout. The four JSON-body routes (memory add, personal
add-directory, research start and hide-image) returned **422 for both an array and a string**;
there is no `await request.json()` in these assigned routes, so the auth/admin section's
non-object-body error does not recur here. The two module-alias suites passed, including
legacy/canonical object identity and monkeypatch behavior.

`venv/bin/python -m pytest -q` was run with these fourteen files:
`tests/test_memory_owner_isolation.py`, `tests/test_memory_routes_session_owner.py`,
`tests/test_memory_routes_shim.py`, `tests/test_personal_delete_file_confinement.py`,
`tests/test_personal_dir_symlink_escape.py`, `tests/test_personal_remove_dir_confinement.py`,
`tests/test_personal_upload_isolation.py`, `tests/test_personal_upload_privilege.py`,
`tests/test_research_endpoint_owner_scope.py`, `tests/test_research_owner_scope_routes.py`,
`tests/test_research_report_read.py`, `tests/test_research_routes_path_confinement.py`,
`tests/test_research_routes_shim.py`, `tests/test_research_session_id_validation.py` —
**113 passed**, three deprecation warnings. A second invocation with
`tests/test_memory_bullet_extraction.py` and `tests/test_memory_store_unreadable_no_wipe.py`
returned **16 passed**, one deprecation warning. Total: **129 passed across 16 suites**.
The full suite and `audit.py` were not run; run-level generation, counts and secret-gate
validation belong to the coordinating reviewer.

#### [SECURITY] Memory pin, edit, delete and audit bypass the memory-management privilege

- **Location:** `routes/memory/memory_routes.py:503-513` (pin), `:528-549` (edit), `:550-566` (delete), `:289-324` (audit)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** add and import explicitly call `require_privilege(request, "can_manage_memory")`
  (`:106-107`, `:346-347`), and a grep for the helper over the whole module returns only those
  two sites, so the other mutations resolve the owner and nothing else. Delete, at `:550-566`:

  ```python
  def delete_memory(request: Request, memory_id: str):
      """Delete a memory item by its ID."""
      user = _owner(request)
      all_mem = _load_for_update(memory_manager)
      # ... find target and verify ownership ...
      _verify_memory_owner(target, user)

      all_mem = [m for m in all_mem if m["id"] != memory_id]
      memory_manager.save(all_mem)
  ```

  Pin (`:503-513`) and edit (`:528-549`) have the same shape, and `api_audit_memories`
  (`:289-324`) calls `audit_memories(..., owner=user)` without the gate; the callee actually
  rewrites the owner's entries. The router has no
  shared privilege dependency. `src/auth_helpers.py:163-188` enforces the flag only when
  `require_privilege` is called; the app middleware authenticates the user, not this feature.

  An inline Python `TestClient` probe used a real temporary `MemoryManager`, an authenticated
  `alice` request state, and an auth manager returning `can_manage_memory=False`:

  ```text
  privilege false: POST /api/memory/add 403
  privilege false: PUT /api/memory/one 200
  privilege false: POST /api/memory/one/pin 200
  privilege false: DELETE /api/memory/one 200
  remaining memory rows: 0
  ```

- **Impact:** an account whose administrator disabled memory management can still change,
  pin and erase existing memories through HTTP, and can invoke the consolidating audit if a
  model is configured. Owner checks still hold: this does not permit changing another user's
  memories. The audit's missing gate was verified statically; no live LLM call was made.
- **Fix:** apply the same `can_manage_memory` gate to pin, edit, delete and audit before loading
  or mutating state, and test denied privileges on every memory mutation, not just add/import.

#### [BUG] The research library silently drops saved partial reports with null statistics

- **Location:** `routes/research/research_routes.py:399-407`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the library defaults a missing `stats` key, but not a present null value:

  ```python
  "duration": d.get("stats", {}).get("Duration", ""),
  "rounds": d.get("stats", {}).get("Rounds", ""),
  # ...
  except Exception:
      continue
  ```

  Null is a value the live writer emits, not merely a malformed-file hypothesis:
  `src/research_handler.py:624` persists `"stats": entry.get("stats")`. The timeout recovery
  at `:356-367` formats the researcher's partial report, marks the entry `done` and saves it,
  but never assigns `entry["stats"]`. Its partial-error recovery has the same shape.

  An inline Python probe ran the actual `start_research` background task with
  `call_research_service` replaced by a coroutine that supplied an evolving report and raised
  `asyncio.TimeoutError`. Only report formatting and event dispatch were stubbed; persistence
  and the library route were real, using a temporary directory:

  ```text
  timeout recovery: status= done stats= None saved result present= True library total= 0
  ```

  A separate persistence/library probe changed only the saved `stats` value to `{}`:

  ```text
  saved stats: None
  library with null stats: {'research': [], 'total': 0}
  library after stats={} total: 1
  ```

- **Impact:** a partial report deliberately recovered after a research timeout is saved but
  absent from the user's library and its total count. The broad exception handler hides the
  failure. The JSON and result-access paths still retain the report, so this is loss of
  discoverability, not deletion of the saved research.
- **Fix:** normalize null statistics to an empty mapping before reading fields, preferably
  validate their shape as well, and persist the recovery statistics when saving partial
  results. Add a library test using the timeout recovery's real saved shape.

#### [PERF] Research library listing reads every report synchronously on the event loop

- **Location:** `routes/research/research_routes.py:367-380`, `:419`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the async handler walks and reads the shared directory without yielding:

  ```python
  async def research_library(
      # ...
  ):
      # ...
      for p in data_dir.glob("*.json"):
          try:
              d = json.loads(p.read_text(encoding="utf-8"))
      # ... owner filtering, thumbnail selection and sorting ...
      return {"research": items[:limit], "total": len(items)}
  ```

  Filtering by owner happens after the full JSON read, and the response limit is applied
  after all reads and sorting. An inline Python probe instrumented `Path.read_text` with
  two valid reports, one owned by the caller and one by another user:

  ```text
  library limit=1: JSON reads= 2 returned= 1 async handler= True
  ```

  In contrast, the sibling personal reload route at `routes/personal_routes.py:192-198`
  explicitly moves its blocking scan into `await run_in_threadpool(...)`.
- **Impact:** listing even one library item blocks other coroutines in that server process
  for the directory scan and parsing of every saved report, including other owners' reports.
  The work grows with total stored report bytes, not the requested page size. This is a
  scaling defect, not a measured outage: production library sizes and stall durations were
  not benchmarked.
- **Fix:** move the complete listing/filter/sort operation to a worker thread (or make this
  non-awaiting handler synchronous so FastAPI offloads it). A persistent metadata index can
  bound repeated full-report reads later; offloading is the smallest event-loop fix.

## 33. routes: uploads, embeddings, presets and preferences

### Overview

`routes/upload_routes.py`, `routes/embedding_routes.py`, `routes/editor_draft_routes.py`,
`routes/signature_routes.py`, `routes/preset_routes.py`, `routes/prefs_routes.py`,
`routes/font_routes.py`, `routes/emoji_routes.py`, `routes/tts_routes.py`,
`routes/stt_routes.py`, and `routes/cookbook_output.py`.

File and preference endpoints outside the chat and document-library routers: uploads,
embedding-model downloads and endpoint configuration, editor drafts, visual signature stamps,
presets, user preferences, custom-font discovery, the emoji proxy, and speech synthesis and
transcription. `cookbook_output.py` supplies pure output-classification helpers and cache-probe
scripts to the Cookbook router; it is not itself an HTTP output reader. The embedding routes do
not index or query owner documents.

The boundary: authentication is in `core-auth-session` and `app.py`; upload limits are in
`src-security`; upload storage is in `src-documents`; the database models are in
`core-data-platform`; preset management and embedding configuration
consumers are in `src-memory-rag`; speech services are in `services-media`. Preference
load/save helpers are implemented in the route file reviewed here. Cookbook execution and
status endpoints remain in `routes-cookbook`.

### Coverage

**Read fully:** all eleven assigned files, 1,882 lines: `routes/upload_routes.py` (533),
`routes/embedding_routes.py` (376), `routes/editor_draft_routes.py` (188),
`routes/signature_routes.py` (151), `routes/preset_routes.py` (126), `routes/prefs_routes.py`
(125), `routes/emoji_routes.py` (109), `routes/tts_routes.py` (87),
`routes/cookbook_output.py` (75), `routes/stt_routes.py` (57), and `routes/font_routes.py`
(55). Boundary helpers `core/atomic_io.py` and `src/upload_limits.py` were also read fully.
Line references are to the working tree at `2992bf6d368a`; `git status --short` showed only
the untracked audit directory.

**Read partially:** `app.py` at the authentication setup, exemptions and complete
`AuthMiddleware` implementation (250–489), plus router-registration searches;
`core/middleware.py` through line 140, including `require_admin`;
`src/auth_helpers.py` through line 160, including identity resolution and `require_user`;
`src/upload_handler.py` at filename/ID validation (1–89), construction, size policy,
hashing and MIME/extension handling (187–406), index loading (776–855), and upload
resolution, rate cleanup, statistics and the complete `save_upload` implementation
(1100–1394), with searches for ownership and reservation helpers;
`src/preset_manager.py` at persistence and all route-called mutators/getters (115–190),
with searches of loading/defaults; `core/database.py` at `Signature` and `EditorDraft`;
`services/tts/tts_service.py` at cache operations and synthesis (90–259);
`services/stt/stt_service.py` at local/API transcription and statistics (90–199);
`src/document_processor.py` at vision analysis (333–392);
`routes/calendar_routes.py` at preference-writing CalDAV configuration handlers (805–984);
`src/builtin_actions.py` at the scheduled model-serve preference update (3270–3354);
caller searches in `routes/`, `src/caldav_sync.py`, `src/task_scheduler.py`, and
`routes/cookbook_routes.py`. Test-source reads covered `tests/conftest.py`,
`tests/test_prefs_routes.py`, `tests/test_editor_draft_payload.py`,
`tests/test_preset_expand_owner_scope.py` and `tests/test_cookbook_dead_download_status.py`;
the other selected tests were executed, not read end to end.

**Not read:** no assigned route file remains unread. Boundary modules beyond the regions
above, the embedding/vector stores and their indexing/query paths, the rest of the speech
services and model pipelines, the Cookbook execution router, and the front-end consumers
were not reviewed. No real credential authentication, external speech/vision/embedding
provider, local inference model, browser rendering, or multi-process preference-write race
was exercised. The upload content-detector integration test could not run without libmagic/
python-magic. Run-level build and audit gates were not run, as required by this assignment.

**Checks run:** `git rev-parse --short HEAD`, `git status --short`, route/caller searches,
and an inline `venv/bin/python` probe using a temporary preference file and an in-memory
SQLite database. The probe exercised real preference/draft/signature endpoints with the
state that middleware stamps for two different bearer owners, called the three raw-JSON
handlers with a non-object body, and recorded the thread used by stub speech services.
It did not mint or authenticate real bearer credentials. A separate AST check found zero
`await` expressions in both `set_pref` and `_save_for_user`: ordinary preference PUTs on one
event loop do not interleave inside their read-modify-write operation. This does not establish
safety across workers or other threaded writers.

The required discovery command, `ls tests | grep -iE
'upload|embedding|prefs|signature|font|emoji|tts|stt|preset|editor_draft'`, selected 50 Python
suites. Running `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q -p no:cacheprovider`
with those paths produced **220 passed, 1 skipped**. A second focused invocation added
`tests/test_cookbook_dead_download_status.py` and repeated
`tests/test_upload_content_detection_magic.py` with `-rs`: **12 passed, 1 skipped**, of which
11 passes were additional Cookbook tests. Total distinct tests: **231 passed, 1 skipped**.
The skip reason was `libmagic/python-magic not installed in this environment`; both invocations
reported the existing SQLAlchemy `declarative_base()` deprecation warning. Every finding's
cited source span was reopened with line numbers before writing.

#### [SECURITY] Bearer callers share the same preferences, editor drafts and signatures across token owners

- **Location:** `routes/prefs_routes.py:108-122`, `routes/editor_draft_routes.py:83-88`, `:113-118`, `:171-178`, `routes/signature_routes.py:88-95`, `:103-110`, `:132-139`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** these handlers use the middleware's generic caller identity as the storage
  owner without rejecting bearer requests or resolving their actual owner:

  ```python
  user = get_current_user(request)
  prefs = _load_for_user(user)
  prefs[key] = body.get("value")
  _save_for_user(user, prefs)
  ```

  Draft and signature creation similarly store `owner=user`; their list and mutation
  checks compare against that same value. `src/auth_helpers.py:10-12` simply returns
  `request.state.current_user`. For every successfully authenticated bearer token,
  `app.py:458-460` sets:

  ```python
  # Keep bearer-token callers out of normal cookie/user
  request.state.current_user = "api"
  request.state.api_token = True
  ```

  The middleware allows these paths through after authentication; none of these three
  routers uses the bearer rejection in `require_user` (`src/auth_helpers.py:132-133`).
  An inline Python probe registered the real routers against temporary stores and stamped
  that state with a different bearer-token owner for each of two requests. After the first owner
  wrote data, the second owner's requests produced:

  ```text
  different bearer owner reads prefs: {'key': 'review', 'value': 'alice-data'}
  different bearer owner reads draft: 200 {'review': 'alice-data'}
  different bearer owner deletes draft: 200
  signature create: 200
  different bearer owner lists signatures: 1
  different bearer owner deletes signature: 200
  ```

  The probe substituted authentication state, not token validation; the state assignment
  and absence of a later gate were verified in the middleware and router registration.
- **Impact:** a valid delegated token can read or mutate data another token owner created
  through these APIs. Listing reveals the draft/signature IDs, so guessing an ID is not a
  prerequisite. Cookie-created data remains separated by username: the demonstrated exposure
  is the shared bearer-created bucket, not every browser user's existing records. Bearer-created
  records are also absent from their human owner's ordinary browser view.
- **Fix:** use `require_user` if these are browser-only routes. If bearer access is intended,
  require an explicit token scope and use its resolved owner for every read and write. Handle
  existing `api`-owned rows separately; their actual owners cannot be inferred from these rows.
- **Re-review (2026-10-04):** re-derived in full and lowered from high. The middleware assignment (`app.py:458-463`) and the
  three routers' use of `get_current_user` are as quoted, and no later gate exists. The shared
  bucket holds only what a bearer client stored through these three routers, and no shipped bearer
  client calls them: `grep -rln "api/prefs\|editor-draft\|api/signatures\|editor_draft" companion
  swift integrations mcp_servers` returns nothing, and the Codex and Claude integrations use the
  scope-aware `/api/codex/*` routes. Cookie users' records are not reachable this way. The defect
  that remains is that a token of any scope reaches three unscoped stores, which is a scope check
  that does not deliver what it claims, hence medium.


#### [PERF] Speech, upload processing and vision analysis run blocking work on the request event loop

- **Location:** `routes/tts_routes.py:41`, `:50`, `routes/stt_routes.py:39`, `routes/upload_routes.py:291-292`, `:484`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the handlers are asynchronous, but invoke synchronous processing directly:

  ```python
  audio_b64 = tts_service.synthesize_to_base64(request.text)
  audio_data = tts_service.synthesize(request.text)
  text = stt_service.transcribe(audio_bytes)
  meta = upload_handler.save_upload(u, client_ip, owner=owner)
  gallery_id = _promote_chat_image_to_gallery(meta, owner, session_id)
  text = analyze_image_with_vl(path, owner=current_user) or ""
  ```

  The endpoint speech implementations call synchronous `httpx.post(..., timeout=60)`
  (`services/tts/tts_service.py:189`, `services/stt/stt_service.py:144`); their public
  methods call those implementations directly. The local-provider branches also perform
  inference synchronously. Vision delegates directly to its synchronous implementation
  (`src/document_processor.py:390-392`), which calls
  `llm_call(..., timeout=120)` (`:375`). Upload saving hashes and copies the file and writes
  the index before returning; promotion copies the image and commits a database row.

  An inline Python probe called the real TTS and STT handlers from an event loop with stub
  services that compared `threading.get_ident()` with the loop thread:

  ```text
  TTS runs on event-loop thread: True
  STT runs on event-loop thread: True
  ```

  In contrast, the same upload router already offloads manual cleanup:

  ```python
  cleaned_count = await asyncio.to_thread(
      _run_reference_safe_cleanup,
      upload_handler,
  )
  ```

  (`routes/upload_routes.py:325-327`). No real model or network latency was measured.
- **Impact:** a cache-miss speech or vision request stalls other requests and streaming work
  on the same server event loop while inference or synchronous network I/O runs. A slow
  endpoint can hold that loop through its configured socket timeout; those timeout values
  are not measured end-to-end deadlines. Upload hashing, copying and image processing add
  shorter stalls proportional to file size. Authentication, upload limits and caches limit
  reach and repeated work, but do not prevent an ordinary authorized request from blocking
  unrelated users on the same worker.
- **Fix:** offload the complete blocking service calls and upload-processing operations with
  `asyncio.to_thread`, or move suitable handlers to synchronous FastAPI endpoints. Bound
  inference concurrency and verify shared service/store locking before introducing parallel
  calls; simply removing event-loop serialization must not introduce new store races.

#### [ERROR-HANDLING] Three raw-JSON endpoints raise unhandled errors on non-object bodies

- **Location:** `routes/preset_routes.py:79-81`, `:122-123`, `routes/upload_routes.py:516-519`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the handlers parse arbitrary JSON and immediately use mapping methods:

  ```python
  data = await request.json()
  draft = (data.get("prompt") or "").strip()
  # save_group_presets:
  data = await request.json()
  preset_manager.save_group_presets(data.get("groups", []))
  # put_vision_text:
  body = await request.json()
  # ... JSONDecodeError handler ...
  text = (body or {}).get("text", "")
  ```

  Catching `JSONDecodeError` does not reject valid JSON with the wrong shape. An inline
  Python probe called these actual endpoint functions with `json()` returning a nonempty
  list, using a stub model import and an existing temporary upload:

  ```text
  non-object /api/presets/expand AttributeError
  non-object /api/presets/groups AttributeError
  non-object /api/upload/{file_id}/vision AttributeError
  ```

  For the upload route an empty list happens to fall back to `{}`; a nonempty list or string
  does not. This is a recurrence of the raw-JSON shape failure reported in
  `routes-rest-auth-admin.md`, not a separate failure class for each endpoint.
- **Impact:** malformed client input produces an unhandled server error instead of a 4xx
  validation response. The group writer is admin-only, the upload path checks ownership
  before parsing the body, and all three paths require upstream authentication; this is
  limited to error handling for authorized callers, not an authentication bypass.
- **Fix:** validate `isinstance(body, dict)` before using mapping methods, or give each
  endpoint a Pydantic request model, including string types for the prompt/name/text fields.

## 34. routes: webhooks, vault, compare, hardware fit and shims

### Overview

`routes/webhook/__init__.py`,
`routes/webhook/webhook_routes.py`,
`routes/webhook_routes.py`,
`routes/hwfit_routes.py`,
`routes/compare/__init__.py`,
`routes/compare/compare_routes.py`,
`routes/compare_routes.py`,
`routes/vault/__init__.py`,
`routes/vault/vault_routes.py`,
`routes/vault_routes.py`,
`routes/diagnostics_routes.py`,
`routes/search/__init__.py`,
`routes/search/search_routes.py`,
`routes/search_routes.py`,
`routes/cleanup/__init__.py`,
`routes/cleanup/cleanup_routes.py`,
`routes/cleanup_routes.py`,
`routes/document_helpers.py`,
`routes/document_routes.py`,
`routes/gallery_helpers.py`,
`routes/gallery_routes.py`,
`routes/task_routes.py`,

The remaining first-party route modules: outgoing webhook registration and last-delivery status,
token-authenticated synchronous chat, the vault, model comparison, hardware-fit detection,
diagnostics, search configuration and execution, session cleanup, and the five compatibility shims
(`routes/document_*`, `routes/gallery_*`, `routes/task_routes`) that alias their canonical
subpackage modules.

The boundary: authentication middleware is `core-auth-session`; database models are
`core-data-platform`; search execution is `services-search`; hardware detection and ranking are
`services-hwfit`. The document/gallery implementations belong to `routes-gallery-document`, and
the task implementation, including the incoming webhook receiver, belongs to
`routes-skills-calendar-task`. This section checks those five extra shims as aliases, not as
second implementations of their targets.

### Coverage

**Read fully:** all 22 assigned files (1,921 lines) listed in the Overview: the seven canonical
route modules, ten flat shims, and **five** package `__init__.py` files (including cleanup).
Working-tree citations refer to `2992bf6d368a`; `git status --short` showed only the untracked
`audit/` directory. Also read fully for the request/storage boundaries: `core/middleware.py`,
`src/auth_helpers.py`, `src/cleanup_service.py`, `src/tools/vault.py`,
`services/search/core.py`, `routes/_validators.py`, and `SECURITY.md`. Read the test harness
`tests/conftest.py` and the three suites `tests/test_hwfit_remote_validation.py`,
`tests/test_search_routes_shim.py`, and `tests/test_webhook_trigger_auth_exempt.py` fully.

**Read partially:** `app.py:259-518` (exempt paths, internal/loopback checks, bearer and cookie
identity) and the seven routers' registration sites; `core/database.py:175-284`, `:520-617`,
`:648-680` (session/message, endpoint/comparison, and outgoing-webhook storage models);
`core/platform_compat.py:39-159`, `:350-453` (permissions, process helpers and SSH execution);
`services/hwfit/hardware.py:1-250`, `:710-908` (`_run`, initial GPU probes, visibility metadata and
`detect_system`); `src/webhook_manager.py` by function/signature search and `:323-455` (delivery,
signing, URL revalidation call sites and status writes); `services/search/providers.py:135-246`
(SearXNG JSON search), plus provider/settings/HTTP-call searches; `src/agent_tools/web_tools.py:1-100`
and `src/deep_research.py:565-609` (offloaded search callers); `routes/cookbook_routes.py` at its
admin-gate call sites and `:3135-3204` (GPU probing); `routes/session_routes.py:155-264` (raw-endpoint
gate and neighbouring persistence helpers); `routes/task/task_routes.py` at webhook generation
and update searches and `:1040` to end (incoming trigger, regeneration and neighbouring parser);
`src/tool_security.py` at the vault blocklist and owner/delegated-tool gates. Read the audit rules,
header, coverage boundaries, review scaffold and both supplied example sections.

**Not read:** none of the assigned files. The document/gallery canonical modules were imported
for alias-identity checks, not source-reviewed. Task implementation outside the stated regions,
the scheduler behind its trigger, session-manager internals, hardware ranking/catalogue code,
search content transports, webhook transport internals, diagnostics' health/RAG/YouTube/research
callees, and the remaining database/auth/storage internals were not reviewed here. The other
54 selected test files were executed, not read end to end. No real provider, SSH host, GPU,
Bitwarden installation, browser deployment, or external webhook receiver was exercised.

**Checks run:** `git rev-parse --short=12 HEAD`, `git status --short`, `wc -l` over the 22 paths,
and the requested `ls tests | grep -iE 'webhook|hwfit|compare|vault|diagnostic|search|cleanup'`.
From that discovery, selected the seven module families plus blind-comparison coverage, rather
than unrelated research/session suites whose names also contain `search` or `cleanup`:

```sh
TEST_FILES=$(ls tests | grep -iE '^test_(webhook|hwfit|compare|vault|diagnostic|search|cleanup)|^test_blind_compare' | awk '{print "tests/" $0}')
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q -p no:cacheprovider $TEST_FILES
```

**57 files, 253 passed in 6.28s**, with one SQLAlchemy `declarative_base()` deprecation warning.
Two stdin Python probes used temporary data directories outside the checkout, an in-memory DB,
and synthetic request state. They checked SSH reachability with a mocked runner, event-loop
execution with mocked search functions, non-object JSON responses, vault file modes, all ten
shim identities, and comparison ownership. Results appear below where they support findings.
All ten aliases were identical to their canonical module objects. The five typed JSON endpoints
(vault config/login/unlock, compare record and sync chat) returned 422 for both `[]` and a string;
the two search endpoints returned 200 with their missing-query error. Thus the non-object-body
500 class from `routes-rest-auth-admin` does not recur in this section's canonical handlers.
The adjacent task parser is outside this section's implementation scope.

Outgoing webhook management and all vault/diagnostics handlers require admin. The outgoing
webhook module has no unauthenticated receiver: `/api/v1/chat` additionally requires a chat-scoped
API token. None of these seven routers is auth-exempt. The dynamic exemption is the task
receiver's secret-bearing path, whose handler checks the stored token and active status before
asking the scheduler to run. It uses a reusable URL credential, not a timestamped signature;
repeated authorized triggers are intentional. External receivers' replay checks were not tested.
Cleanup derives its owner from request state, not client input, and its service applies strict
owner filters to archival, deletion candidates and the protected recent-session set. It deletes
eligible session rows (messages have a cascading foreign key) and removes their cached sessions;
this pass did not establish cleanup of every ancillary file/table.

`audit.py` and run-level validation were not run, as instructed; integration and the secret gate
remain the parent's responsibility. No source, test, or other run file was edited.

#### [SECURITY] Bearer callers share one comparison owner and can read and delete each other's records

- **Location:** `routes/compare/compare_routes.py:286`, `:310`, `:322-327`, `:348-358`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** record creation and history use the raw middleware username:

  ```python
  user = get_current_user(request)
  # record_comparison constructs Comparison(..., owner=user)
  ...
  user = get_current_user(request)
  ...
  if user:
      q = q.filter(Comparison.owner == user)
  ```

  Delete uses the same identity and rejects only `comp.owner != user`. For every valid bearer
  token, `app.py:458-464` stamps `request.state.current_user = "api"` while putting the token's
  real owner in a separate field on the same state object. `src/auth_helpers.py:10-12` returns the
  former unchanged.
  No comparison handler rejects bearer credentials or checks their scopes, and
  `app.py:815-816` registers the router without an additional dependency.

  A stdin probe run with `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -` mounted the real comparison
  router over a temporary SQLite table. Its middleware reproduced those bearer-state fields with
  distinct owners and chat scopes, without using real credentials. Alice recorded a synthetic
  comparison, then Bob requested history and deleted its returned id:

  ```text
  alice record: 200
  bob history: 200 contains alice record: True
  bob delete alice record: 200
  remaining records: 0
  ```

- **Impact:** token-created comparisons are shared between otherwise distinct owners. Another
  token holder can retrieve their prompt previews, model names and votes, then delete them.
  Normal browser-created comparisons retain their real owners and are not exposed by this
  particular path; the defect affects clients using bearer tokens on the comparison API. The
  probe tested route behavior with genuine middleware state shapes, not live token issuance.
- **Fix:** reject bearer callers with a router-level `require_user` dependency if comparisons are
  browser-only. If bearer comparison is supported, require an explicit scope and consistently use
  its resolved owner for creation, history, voting, deletion and endpoint lookup. Merely switching
  to `effective_user` without a scope gate would grant delegated credentials additional authority.

#### [SECURITY] Hardware-fit routes let non-admins run server-side SSH probes against caller-selected hosts

- **Location:** `routes/hwfit_routes.py:182-191` (router and system route), `:319-332`, `:371` (profiles)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** neither the router nor its four endpoints has an administrative dependency:

  ```python
  router = APIRouter(prefix="/api/hwfit", tags=["hwfit"])
  ...
  def get_system(host: str = "", ssh_port: str = "", platform: str = "", fresh: bool = False):
      ...
      host, ssh_port = _validate_detection_target(host, ssh_port)
      return detect_system(host=host, ssh_port=ssh_port, platform=platform, fresh=fresh)
  ```

  `app.py:811-812` adds no dependency at registration. The middleware authenticates the caller
  but does not require admin for this path. `_validate_detection_target` checks syntax only.
  `services/hwfit/hardware.py:27-45` runs the fixed detection commands with `run_ssh_command`;
  `core/platform_compat.py:362-417` builds and executes ordinary `ssh`, using the server process's
  SSH configuration and credentials. The profiles route also passes a caller-supplied model path
  to `_inspect_model_path`, which runs directory/config/weight-size probes
  (`routes/hwfit_routes.py:137-170`). The comparable GPU route explicitly calls
  `require_admin(request)` (`routes/cookbook_routes.py:3160`).

  A stdin Python/FastAPI probe mounted the real hardware-fit router, stamped an ordinary user,
  supplied an auth manager whose `is_admin` returned false, and replaced only the hardware
  module's SSH runner with a recorder. A GET to `/api/hwfit/system` with a synthetic host,
  port 2222, Linux platform and a fresh scan produced:

  ```text
  hwfit non-admin HTTP: 200 SSH calls: 2 targets: [('audit-target.example', '2222')]
  ```

  No SSH connection was made by this probe.
- **Impact:** any signed-in user, and bearer callers without a hardware-management scope check,
  can make the service attempt SSH connections to chosen hosts and ports. Where the server's SSH
  credentials work, they can obtain hardware and limited model-directory metadata using the
  administrator's server-side access. This is not arbitrary shell-command execution: host/port
  validation and `shlex.quote` constrain the commands, and successful remote inspection still
  requires usable SSH access.
- **Fix:** apply `Depends(require_admin)` to the hardware-fit router, matching the cookbook
  probes. If non-admin model recommendations are required, expose cached/sanitized results
  separately without accepting a remote target, filesystem path or refresh operation.

#### [PERF] Both search POST handlers execute synchronous network work on the event loop

- **Location:** `routes/search/search_routes.py:60-62`, `:103`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** both handlers are asynchronous but call blocking search functions directly:

  ```python
  context, sources = comprehensive_web_search(
      query, return_sources=True, time_filter=time_filter,
  )
  ...
  results = _call_provider(provider, query, min(count, 20))
  ```

  `_call_provider` dispatches synchronously (`services/search/core.py:96-110`), including to
  `httpx.get(..., timeout=15)` for SearXNG (`services/search/providers.py:186-192`). Comprehensive
  search also waits synchronously for its page-fetch futures
  (`services/search/core.py:368-384`); creating worker threads internally does not yield the
  calling event loop. The agent caller already offloads comprehensive search with
  `run_in_executor` (`src/agent_tools/web_tools.py:47-59`), and research uses
  `await asyncio.to_thread(_call_provider, ...)` (`src/deep_research.py:582`).

  A stdin Python probe called each real handler with a parsed JSON request and substituted a
  synchronous search recorder. Both recorders found the same running event loop as the handler.
  Each queued a `loop.call_soon` callback, which had not run when the handler returned and ran
  only after the probe yielded:

  ```text
  /api/search before handler return: [('provider_on_event_loop', True)]
  /api/search after yielding: [('provider_on_event_loop', True), ('callback', True)]
  /api/search/query before handler return: [('provider_on_event_loop', True)]
  /api/search/query after yielding: [('provider_on_event_loop', True), ('callback', True)]
  ```

- **Impact:** one authenticated standalone/Compare search prevents other coroutines in the same
  server worker from running while provider requests, retries and page fetching finish. A slow
  provider therefore stalls unrelated requests and streaming chat, rather than just the search
  caller. No real-network latency was measured; the synchronous execution path and the configured
  per-request timeout were verified.
- **Fix:** offload both search calls with `await asyncio.to_thread(...)`, as the research caller
  already does. Keep the provider socket timeouts; an outer coroutine timeout alone cannot stop
  a blocked worker thread.

#### [SECURITY] The vault writer restricts permissions only after writing the session-bearing file

- **Location:** `routes/vault/vault_routes.py:72-77`, with the unlock write at `:199-202`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_save_config` writes directly to the destination before applying its promised
  private mode:

  ```python
  VAULT_FILE.parent.mkdir(parents=True, exist_ok=True)
  VAULT_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
  ...
  safe_chmod(str(VAULT_FILE), 0o600)
  ```

  Unlock places the CLI's returned session in `cfg` and calls this writer without requiring a
  pre-existing config file. A stdin Python probe redirected `VAULT_FILE` to a new temporary path,
  set umask 022, called the real `_save_config` with non-secret synthetic data, and wrapped
  `safe_chmod` to inspect the mode immediately before delegating to the real function:

  ```text
  vault first-write modes: ['0o644'] final: 0o600
  ```

  `core/platform_compat.py:40-55` also converts a chmod failure into `False`, which this caller
  does not inspect.
- **Impact:** on POSIX, a first unlock against an already logged-in CLI but absent `vault.json`
  can briefly publish the session-bearing file as world-readable under a typical umask. A local
  user who can traverse its parent directories can open it before chmod; an interrupted write
  before chmod leaves that mode in place. Existing files already at 0600 remain private, the
  normal save-config-before-unlock flow creates such a file first, restrictive directory modes
  mitigate access, and remote HTTP callers cannot read the session through the admin-only config
  endpoint. These conditions make this a low-severity local exposure, not an HTTP secret leak.
- **Fix:** create a same-directory temporary file with mode 0600 before writing, then atomically
  replace the destination. Fail rather than silently accept a permission-setting error on POSIX;
  preserve the separate Windows ACL policy.

## 35. services: search

### Overview

The search implementation: `services/search/__init__.py` (the export surface),
`services/search/providers.py` (the SearXNG, Brave, DuckDuckGo, Google PSE, Tavily and Serper
calls plus the settings/key lookups they read), `services/search/core.py` (the provider chain,
the cached retry orchestrator, `comprehensive_web_search`, and the config accessors),
`services/search/content.py` (the guarded page fetch and its HTML/PDF/text extraction),
`services/search/query.py` (query enhancement and the cache-duration heuristic),
`services/search/ranking.py` (result ordering), `services/search/analytics.py` (the query
recorder and its stats surface), `services/search/cache.py` (the cache directories and the LRU
sweep), and `services/search/service.py` (the async `SearchService` facade).

The boundary: the four HTTP handlers that call into this module and their authentication are
`routes-rest-integrations-misc` (`routes/search/search_routes.py`), which already reports that
both search POST handlers run this synchronous code on the event loop — that defect is not
restated here. The SSRF guard and pinned transport that `content.py` delegates to live in
`src/outbound_fetch.py` and are `src-security`; the settings store these providers read is
`src-memory-rag`/`src-platform`; the chat, agent-tool, deep-research and research-handler call
sites are their own sections and are cited here only where a finding lands in them.

### Coverage

**Read fully:** all nine assigned files (2,222 lines): `providers.py` (641), `core.py` (478),
`content.py` (442), `ranking.py` (164), `query.py` (149), `analytics.py` (148), `service.py`
(102), `cache.py` (63), `__init__.py` (35). Also read fully for the boundaries the findings
rest on: `routes/search/search_routes.py` (111), `src/outbound_fetch.py` (354),
`src/settings_scrub.py` (70), `src/agent_tools/web_tools.py` (171), `src/search/*` (eight files:
six `sys.modules` aliases, a re-exporting `ranking.py`, and the package `__init__.py`), and
`specs/search.md`.

**Read partially:** `src/settings.py` at `DEFAULT_SETTINGS`' search keys (`:66-95`) and
`load_settings`/`save_settings`; `routes/auth_routes.py` at `GET`/`POST /api/auth/settings`
(`:715-755`); `app.py` at the auth-exempt lists (`:264-296`) and the bearer/cookie branch
(`:470-500`); `src/deep_research.py` at `_search` (`:560-607`), `_fetch_and_extract` (`:609-630`)
and the search-unavailable report path (`:326-340`); `services/research/research_handler.py` at
`call_research_service` (`:240-295`) and `_save_result` (`:209-231`); `src/service_health.py` at
`_searxng_instance`/`searxng_health` (`:216-255`); `src/chat_processor.py` at the web-search and
URL-prefetch call sites (`:440-470`); `.gitignore` at `*.cache`/`cache/` and
`**/search_analytics.json` (`:59-60`, `:111`); and the test suites listed below for what they
already pin.

**Not read:** the front end beyond `static/js/settings.js:1106` (`search_url` is posted
unvalidated) — `static/js/search.js`, the compare-mode and research-panel search callers, and
the admin search panel were not read; the pinned SearXNG image, its config and
`scripts/migrate_searxng_settings.py`; `src/tool_execution.py` and `src/session_search.py`
(other sections' search call sites); the rest of `services/research/*`, `src/chat_processor.py`
and `src/deep_research.py`; `src/constants.py` beyond the fetch caps and data dir; the tests
beyond the suites run; and every other `services-*` section.

**Checks run:** five throwaway probes under `/tmp` (not part of the target tree), each quoted in
the finding it settles — the Google PSE 403 probe (`probe_search_cred.py`), the
malformed-provider-row probe (`probe_search_rows.py`, which also holds the large-page timing
case), a dedicated `SearchService` probe (`probe_search_service.py`), an AST call-site probe for
the exported entry points (`probe_search_callsites.py`), and the settings-scrub probe — plus two
one-line checks: `issubclass(httpx.HTTPStatusError, httpx.RequestError)` → `False`, and `wc -l`
for the line counts above. Also the greps recorded in the findings
(`searxng_search_results` / `invalidate_search_cache` / `get_search_stats` / `_record_query`
across the repository) and `git log -S`. The large-page probe (1.37 MB of HTML through the real
extractor) took 1.9 s with the four summarizer helpers at 0.02 s, so the extraction cost is
bounded by the 2 MB soft cap and is not reported. The suites that import
this module were discovered with
`grep -rl "services\.search\|src\.search\|services/search\|src/search" tests/*.py` (32 files)
plus `tests/test_search_query_nonstring.py`, which loads `query.py` by path — **230 passed**. The
broader set the assignment names, `ls tests | grep -iE 'search|searxng|ddg|og_image|analytics|query|ranking|content'`
(74 files), was also run: 73 files, **391 passed, 1 skipped**. The 74th,
`tests/test_owned_document_query.py`, fails collection inside that batch
(`ModuleNotFoundError: No module named 'src.agent_tools.document_tools'; 'src.agent_tools' is
not a package`) and passes alone (2 passed); its subject is the document tools, not this
section, so it is recorded here and not reported as a finding.

#### [SECURITY] An upstream HTTP error status puts the Google PSE API key into the log, the returned context and the research report

- **Location:** `services/search/providers.py:487-501` (with `:472-477`, `:325-330`, `:553-558`, `:614-619`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** all four keyed providers call `raise_for_status()` inside a `try` that catches
  only `httpx.RequestError` and `RateLimitError`. Google PSE is the one that carries its key in
  the query string:

  ```python
  params = {
      "key": api_key,              # providers.py:473
      "cx": cx,
      "q": query,
      "num": min(count, 10),
  }
  ...
      response.raise_for_status()  # :495
  except httpx.RequestError as e:
      error_logger.error(f"Google PSE search failed: {e}")
      return []
  except RateLimitError as e:
      error_logger.error(str(e))
      return []
  ```

  `httpx.HTTPStatusError` is not a subclass of `httpx.RequestError`
  (`venv/bin/python -c "import httpx; print(issubclass(httpx.HTTPStatusError, httpx.RequestError))"`
  → `False`), so a non-429 error status escapes the provider. httpx builds that exception's
  message from the request URL, which contains the key. Probe with a fake 403 whose request URL
  is built from the provider's own `params` (the key below is a synthetic placeholder; it is
  shown as `[REDACTED]` here and is not a value from the tree):

  ```
  $ PYTHONPATH=. venv/bin/python /tmp/probe_search_cred.py
  === 1. direct provider call ===
  raised: HTTPStatusError
  message contains the key: True
  message: Client error '403 Forbidden' for url
    'https://www.googleapis.com/customsearch/v1?key=[REDACTED]&cx=cx-probe&q=probe+query&num=5'
  ...
  === 2. comprehensive_web_search context string ===
  returned string contains the key: True
  returned string: Web search failed — all providers errored or returned empty. Tried:
    google_pse:error: Client error '403 Forbidden' for url
    'https://www.googleapis.com/customsearch/v1?key=[REDACTED]&cx=cx-probe&q=probe+query&num=5'
  ```

  (The `...` stands for the probe's other output, and every occurrence of the synthetic key
  value is shown as `[REDACTED]`.) The same probe printed the module log line with the key in it:
  `Comprehensive search: google_pse attempt 1 failed: Client error '403 Forbidden' for url '...key=[REDACTED]...'`
  (`core.py:296`). Three sinks follow from the one missing catch: the app log, the context
  string built at `core.py:305-308`, and the research report — `src/deep_research.py:591` stores
  `f"{prov}: {e}"` in `_last_search_error`, which `:328-336` interpolates into the returned
  "**Search unavailable**" report, and `services/research/research_handler.py:209-229` persists
  that result to `data/deep_research/<session_id>.json`. The route layer passes the same text to
  the caller unchanged: `routes/search/search_routes.py:108-109` returns
  `{"error": str(e)}` from `/api/search/query`, a route that is authenticated but not
  admin-gated. The existing `tests/test_search_provider_json.py` pins the malformed-JSON case
  (HTTP 200), not the error-status case, and no suite exercises a provider's error-status path
  (`tests/test_search_content_extraction_parity.py` covers `HTTPStatusError` for
  `fetch_webpage_content`, a different function).
- **Impact:** the operator's Google API key — a billable credential — reaches places it should
  never be. The trigger is an upstream non-429 error status, which is exactly what a restricted,
  expired or over-quota key produces: on any such failure the key is written to the application
  log at WARNING, and when no provider in the chain returns results it is embedded in the text
  returned to the caller — which the agent search tool hands back as its output
  (`src/agent_tools/web_tools.py:76-80`) and which the chat prefetch path inserts as search
  context (`src/chat_processor.py:446-449`) — and written into a persisted research report. Any
  authenticated user can read it from the `/api/search/query` response body by selecting
  `google_pse`; nothing in the request is required beyond that. Brave, Tavily and Serper send
  their key in a header, so their escaped `HTTPStatusError` leaks the request URL and the query
  but not the credential. The project already treats this as a rule on the adjacent URL-fetch
  path: `src/chat_processor.py:467-470` and `:481-483` reduce a failed fetch to a
  transport-owned status because "the URL and exception can both contain signed-query
  credentials" and exception text must never reach the model.
- **Fix:** add `except httpx.HTTPStatusError` to the four providers (returning `[]` and logging a
  status-only message), or raise a status-only message instead of letting httpx build one from
  the URL. Redacting the URL is not enough on its own for the Google PSE case, because the key is
  a query parameter of a URL that is otherwise safe to show.

#### [DEAD-CODE] The caching, retry and analytics half of the search module has no caller

- **Location:** `services/search/core.py:136-214` (`searxng_search_results`), `:220-244` (`invalidate_search_cache`), `services/search/analytics.py:97-120` (`_record_query`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `searxng_search_results` is the only function that writes the search disk
  cache, the only caller of `_record_query`, and the only caller of `cleanup_cache` for search
  entries; `invalidate_search_cache` only deletes entries that nothing writes. Nothing in the
  repository calls it. An AST probe over every `.py` file outside `tests/` and
  `services/search/` that matches `Name`, `Attribute` and string constants against the exported
  names:

  ```
  $ venv/bin/python /tmp/probe_search_callsites.py
  searxng_search_results: 2 reference(s) outside tests/ and services/search/
      ./services/search/__init__.py:28     (the __all__ list)
      ./src/search/__init__.py:22          (the __all__ list)
  invalidate_search_cache: 2 reference(s) ...
      ./services/search/__init__.py:25
      ./src/search/__init__.py:19
  get_search_stats: 2 reference(s) ...
      ./services/search/__init__.py:24
      ./src/search/__init__.py:18
  ```

  Inside the package the only other references are the `_record_query` calls at `core.py:158`
  and `:193`, both inside `searxng_search_results`, and the import at `:15`
  (`grep -n "searxng_search_results\|invalidate_search_cache\|get_search_stats\|_record_query"
  services/search/*.py`). `git log -S "searxng_search_results" -- routes/` is
  empty, so no route in this history ever called it. The tests that exercise the path do so
  directly (`tests/test_search_cache_invalidation.py` builds the cache key by hand,
  `tests/test_services_search_analytics_defaults.py` calls `_record_query`), which is why the
  gap is not visible in the suite. The spec still describes it as live: `specs/search.md:36`
  says `comprehensive_web_search()` "coordinates ... cache invalidation, and analytics", and
  `:127` says search cache and analytics state live under the data dir — as do
  `.gitignore:59-60` and `:111`.
- **Impact:** nothing user-visible breaks, but the mechanisms the spec and the comments describe
  do not exist at runtime: every search goes to the provider, `data/cache/search/` is never
  written, `data/logs/search_analytics.json` is never written, and there is no stats surface
  (`get_search_stats` has no caller and no route serves it). `_cache_duration_for_query`
  computes a 24-hour TTL for reference queries and 30 minutes for news queries that nothing ever
  uses — and if the path were reconnected, `cleanup_cache(..., timedelta(hours=1))` at `:207`
  would evict any entry older than an hour on the next write, cutting the 24-hour TTL short.
  An operator tuning `search_result_count` or reading `specs/search.md` for how caching works is
  reading about code that does not run.
- **Fix:** either delete `searxng_search_results`, `invalidate_search_cache`, `get_search_stats`,
  `analytics.py`, `cache.py` and their exports (the tests pin behaviour no caller can reach), or
  route the standalone search path through `searxng_search_results` so the documented cache and
  analytics are live. Reconnecting it also means fixing the TTL mismatch and adding a caller for
  `invalidate_search_cache`, which nothing calls today.

#### [TYPE-SAFETY] A provider row with a non-string field aborts the whole search instead of dropping one result

- **Location:** `services/search/core.py:361` and `:412` (with `services/search/ranking.py:106-112`, `services/search/providers.py:175-181`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the SearXNG parser copies upstream field values through with only a default, and
  every consumer treats them as strings:

  ```python
  # providers.py:176-181
  return [
      {
          "title": r.get("title", ""),
          "url": r.get("url", ""),
          "snippet": r.get("content", ""),
      }
      ...
  ```

  A JSON `null` is *present*, so `.get("content", "")` returns `None`; a number or list is passed
  through as-is. Probe (provider stubbed, fetches stubbed, no network):

  ```
  $ PYTHONPATH=. venv/bin/python /tmp/probe_search_rows.py
  === A. provider row with a non-string snippet (int) ===
  raised: TypeError - object of type 'int' has no len()
  === B. provider row with a null snippet (JSON null survives .get(x, '')) ===
  raised: TypeError - 'NoneType' object is not subscriptable
  === C. provider row with an unhashable url ===
  raised: TypeError - unhashable type: 'list'
  ```

  The three failures are at `ranking.py:109` (`len(snippet)`), `core.py:412`
  (`result['snippet'][:200]`) and `core.py:361` (`_url_index`), in that order. Ranking is called
  at `core.py:318` with no `try` around it, and the formatting loop at `:409-412`
  slices `result['snippet']` directly, so a single bad row in the result list takes the whole
  call down. The caller sees an error string rather than the results that did parse
  (`src/agent_tools/web_tools.py:66-70` returns `web_search failed: TypeError: ...`;
  `routes/search/search_routes.py:64-66` returns `{"error": ...}`). The fetch path right beside
  it does the opposite — `core.py:374-382` catches per-URL exceptions and drops the one page —
  which is the behaviour this path is missing.
- **Impact:** a provider that returns one row with `"content": null` (or a non-string title, or a
  list-valued url) fails the entire search, including the results from the other rows and the
  other providers, instead of dropping the bad row. The trigger requires the upstream body to
  carry a non-string field; I did not establish that a stock SearXNG emits one, and the keyed
  providers' own fields are strings in their documented responses, so this is a robustness gap
  rather than a reproducible failure against a known provider. Its cost is one wasted search per
  occurrence plus a confusing `TypeError` in the log.
- **Fix:** coerce at the parse boundary — `str(r.get("title") or "")` and the same for `url` and
  `content` — or skip a row whose fields are not strings, matching the per-URL `except` the fetch
  loop already uses.

#### [BUG] `SearchService.fetch_content` cannot be called: an instance attribute shadows the method, and the method awaits a synchronous dict

- **Location:** `services/search/service.py:43-45`, `:96-98`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `__init__` stores the constructor flag under the same name as the method:

  ```python
  def __init__(self, default_depth: int = 1, fetch_content: bool = True):
      self.default_depth = default_depth
      self.fetch_content = fetch_content        # service.py:45

  ...
      async def fetch_content(self, url: str) -> Optional[str]:   # :96
          """Fetch content from a URL."""
          return await fetch_webpage_content(url)                 # :98
  ```

  The instance attribute wins, so the public call raises before the method body runs, and an
  unbound call reaches a second failure:

  ```
  $ PYTHONPATH=. venv/bin/python -u /tmp/probe_search_service.py
  instance call  -> TypeError - 'bool' object is not callable
  unbound call   ->
  Traceback (most recent call last):
    File "/tmp/probe_search_service.py", line 17, in <module>
      asyncio.run(svc_mod.SearchService.fetch_content(inst, "https://example.com"))
  TypeError: object dict can't be used in 'await' expression
  ```

  `fetch_webpage_content` (`services/search/content.py:181`) is a plain `def` returning a dict,
  and the annotation says `Optional[str]`. `self.fetch_content` is never read anywhere else in
  the file, so the attribute is only a collision. `tests/test_searchservice_search_call.py`
  covers `search()` only; no test calls `fetch_content`. `specs/search.md:11` and `:38` document
  `SearchService` as the exported async facade, and `services/__init__.py:19` re-exports it,
  although no production module in the repository constructs it (the same AST probe finds
  `SearchService` outside this package only in the two `__all__` lists).
- **Impact:** a documented, exported API method is unusable in both directions — the natural call
  raises `TypeError: 'bool' object is not callable` and the only way to reach the body raises
  `TypeError: object dict can't be used in 'await' expression`. Because nothing in the repository
  calls `SearchService`, no shipped flow breaks; the cost lands on anyone who follows the spec
  and uses the facade, and on the next reader who assumes the class works.
- **Fix:** rename the constructor attribute (`self._fetch_content` or `self.should_fetch_content`),
  and make the method either synchronous (`return fetch_webpage_content(url)`) or offload it
  (`return await asyncio.to_thread(fetch_webpage_content, url)`) with the annotation corrected to
  `dict`.

#### [SECURITY] The configured SearXNG URL is returned verbatim, including any userinfo or query credentials

- **Location:** `services/search/core.py:72` (with `services/search/providers.py:41-47`, `src/settings_scrub.py:66-70`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `get_search_config` copies the admin's URL into the response with no redaction:

  ```python
  # core.py:71-72
  if provider == "searxng":
      from .providers import _get_search_instance
      config["search_url"] = _get_search_instance()
  ```

  `_get_search_instance` only strips whitespace and a trailing slash
  (`providers.py:44-46`), so userinfo and query parameters survive. Probe:

  ```
  $ PYTHONPATH=. venv/bin/python - <<'PY'   (settings stubbed; URL value is a placeholder)
  get_search_config()['search_url'] -> http://searx-user:[REDACTED]@searx.internal:8080/v1?api_key=[REDACTED]
  scrub_settings keeps search_url -> http://searx-user:[REDACTED]@searx.internal:8080/v1?api_key=[REDACTED]
  scrub_settings blanks a key-shaped neighbour -> ''
  ```

  `GET /api/search/config` is served to any authenticated caller
  (`routes/search/search_routes.py:42-44`), and the same value reaches a wider audience through
  `GET /api/auth/settings`, which is in `AUTH_EXEMPT_EXACT` (`app.py:271`) and returns
  `scrub_settings(...)` to every non-admin caller (`routes/auth_routes.py:715-724`);
  `scrub_settings` masks only secret-*shaped key names (`src/settings_scrub.py:66-70`), and
  `search_url` is not one. The configuration is plausible rather than exotic because the only
  in-provider way to authenticate to a protected SearXNG instance is dead code: both SearXNG
  call sites set `api_key = ""` and then test it (`providers.py:140-143`, `:251-255`), so the
  `Authorization` header is never sent and the credentials have to live in the URL. The project
  has the helper for this (`core/log_safety.redact_url`, used by `routes/chat_routes.py:728`,
  `:1670` and `routes/contacts/contacts_routes.py:723`), and `routes-models.md` reports the same
  class of leak for model-endpoint URLs.
- **Impact:** an operator who reaches a password-protected SearXNG instance through
  `http://user:pass@host/...` (or a URL carrying a token query parameter) hands that credential
  to every authenticated user of the instance through the search config response, and to any
  caller of the auth-exempt settings endpoint, which the front end reads for keybinds and TTS
  preferences (`src/settings_scrub.py:7-9`).
  The mitigation is the premise: nothing documents userinfo in `search_url`, the shipped UI is a
  plain text field, and an operator can put a reverse proxy in front of SearXNG instead — so the
  exposure needs a configuration choice that no code recommends.
- **Fix:** run the URL through `redact_url` before it enters the config response (and use the
  same redaction anywhere else the instance URL is returned), or reject userinfo on the settings
  write and keep the dead `Authorization` path as the supported mechanism for authenticated
  instances.

## 36. services: memory

### Overview

`services/memory/__init__.py`, `services/memory/memory.py`, `services/memory/memory_extractor.py`,
`services/memory/memory_vector.py`, `services/memory/service.py`, `services/memory/skill_extractor.py`,
`services/memory/skill_format.py`, `services/memory/skill_importer.py`, `services/memory/skills.py`.

This is the package the rest of the app imports for memory and skills. Two of the nine files are
compatibility re-exports of canonical modules (`memory.py` re-exports `src.memory.MemoryManager` and
its helpers, `memory_vector.py` re-exports `src.memory_vector.MemoryVectorStore`). The others hold the
background memory extractor and its consolidating audit (`memory_extractor.py`), the background skill
extractor (`skill_extractor.py`), the SKILL.md reader/writer (`skill_format.py`), the disk-backed skill
store (`skills.py`), the GitHub/skills.sh bundle importer (`skill_importer.py`), and a `MemoryService`
facade (`service.py`) that no production caller uses.

The boundary: the stores and their own guards — `src/memory.py` (`MemoryManager`,
`MemoryStoreUnreadable`, the atomic write, the owner filter), `src/memory_vector.py`, the embedding
lanes, the Chroma client and the RAG index — are `src-memory-rag`; `services/memory/memory_vector.py`
is a five-line re-export of one of them, so this section reports only what the wrappers here do with
it. The route handlers that call the extractors, the audit and the importer, and the owner and
privilege checks they run first, are `routes-rest-memory-personal-research`
(`routes/memory/memory_routes.py`) and `routes-skills-calendar-task` (`routes/skills_routes.py`); the
agent-facing `manage_skills` and `manage_memory` wrappers are `src-agent-tools`; the teacher-escalation
loop that also writes skills is `src-research-scheduling`. A finding here is about what these modules
do with the values they are handed, not about whether their callers scoped them.

### Coverage

Line numbers refer to `2992bf6d368a`. `git status --short` showed only the untracked `audit/`
directory before and after the checks.

**Read fully:** all nine assigned files, 2,835 lines — `skills.py` (716), `memory_extractor.py` (678),
`skill_importer.py` (487), `skill_format.py` (483), `skill_extractor.py` (305), `service.py` (126),
`memory.py` (20), `__init__.py` (15), `memory_vector.py` (5).

**Read partially:** the boundary code the findings rest on. `src/memory.py` at `_read_entries`
(`:125-164`), `load_all` / `load_all_for_update` / `load` (`:166-194`), `_validate_entries`
(`:215-232`), `save` (`:261-278`) and `add_entry` (`:280-299`); `src/memory_vector.py` in full (251
lines — the store the extractor drives); `src/memory_provider.py` at the `NativeMemoryProvider` method
signatures (`:114-256`); `src/embedding_lanes.py` at `EmbeddingLane` (`:24-56`), `_create_lane`
(`:232-249`) and `build_embedding_lanes` (`:252-272`); `src/embeddings.py` at `FastEmbedClient`
(`:132-192`); `src/chroma_client.py` (`:1-60`); `routes/memory/memory_routes.py` at `_load_for_update`
(`:38-50`) and `api_audit_memories` (`:289-337`); `routes/chat_helpers.py` at the extraction dispatch
(`:1154-1250`); `routes/skills_routes.py` at `SkillAddRequest` (`:37-62`), `import-from-url`
(`:1351-1378`), `add` (`:1381-1412`) and `save_skill_markdown` (`:1804-1851`); `src/tools/system.py` at
`do_manage_skills` (`:24-245`); `src/builtin_actions.py` at `action_test_skills` and
`action_audit_skills` (`:1910-2050`); `setup.py` at the `MEMORY_VECTORS_DIR` entry (`:14-40`).

**Not read:** `src/memory.py` outside the regions above (search, consolidation, the chat-extraction
helpers); the `src/memory_provider.py` method bodies; `src/rag_vector.py`, `src/personal_docs.py` and
the rest of `src-memory-rag`'s files; the skills front end (`static/js/skills*.js`) and every other
`static-*` path; `src/teacher_escalation.py`; `mcp_servers/memory_server.py`; `services/__init__.py`;
and the parts of `routes/skills_routes.py`, `routes/memory/memory_routes.py` and
`routes/chat_helpers.py` outside the regions above. No live LLM, embedding endpoint or ChromaDB server
was reachable in this environment, so no extraction, audit or import was run end to end against a real
model or a real GitHub URL.

**Checks run:** `git rev-parse --short=12 HEAD` and `git status --short`; caller greps
(`MemoryService(`, `audit_memories`, `extract_and_store`, `MEMORY_VECTORS_DIR`, and `to_thread` /
`run_in_threadpool` across `routes/`, `src/` and `services/`); and four throwaway probes under `/tmp`
(not part of the target tree), each quoted in the finding it settles: the SKILL.md round trip, a
non-list `steps`/`tags` add and a nested-path import (`/tmp/probe_mem/skill_probes.py`);
`audit_memories` against an unparseable store (`/tmp/probe_mem/audit_unreadable.py`); a real
`MemoryVectorStore.rebuild` of 300 entries with the real fastembed encoder over a Chroma-shaped stub
collection (`/tmp/probe_mem/rebuild_loop_block.py`); and `_PinnedTransport.handle_request` over a stub
httpcore pool streaming 5 MiB (`/tmp/probe_mem/transport_buffer.py`). The 49 suites matching
`ls tests | grep -iE 'memory|skill'` were run over this surface — **205 passed**, 2 warnings, 3.55s.

#### [PERF] The memory audit re-embeds every owner's memories inside the request coroutine and stalls the event loop

- **Location:** `services/memory/memory_extractor.py:668` (with `:516`, `:658`, `:672`), reached from
  `routes/memory/memory_routes.py:316`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `audit_memories` is `async` for one `await` (the LLM call at `:550`); every other step
  runs synchronously on the caller's event loop. After the model answers, it writes the whole store
  and then re-embeds every entry in it, including entries belonging to other owners:

  ```python
  memory_manager.save(saved_entries)                                   # :658
  ...
  # Rebuild vector index from the full saved set, not just this owner's
  # slice — otherwise the shared collection is wiped of every other
  # owner's entries until they happen to run their own audit.
  if memory_vector and memory_vector.healthy:
      memory_vector.rebuild(saved_entries)                             # :668
  ...
  _save_tidy_state(memory_manager, owner, _fingerprint_entries(final_entries))   # :672
  ```

  `MemoryVectorStore.rebuild` (`src/memory_vector.py:188-244`) deletes and recreates the collections
  and encodes every entry in batches of 100 (`embeddings=lane.encode(batch_texts)`, `:236`), and
  `EmbeddingLane.encode` (`src/embedding_lanes.py:38-40`) runs the encoder inline. Probe with the real
  store and the real fastembed encoder, calling `rebuild` from inside a coroutine while a 10 ms
  heartbeat task ran:

  ```
  healthy: True lanes: ['fastembed']
  warm rebuild(300) inside coroutine: 0.40s wall; heartbeat ticks=5 max gap=0.41s
  ```

  The heartbeat was starved for the whole rebuild — 5 ticks instead of roughly 40, one 0.41 s gap —
  so the loop was blocked for the entire call, about 1.3 ms per stored memory on this machine. The
  route awaits the audit directly (`result = await audit_memories(...)`, `routes/memory/memory_routes.py:316`)
  and the automatic trigger at `:485` calls it from the background extraction task. Sibling paths in
  this codebase move the same class of work off the loop: `routes/personal_routes.py:196-197` wraps the
  personal-docs re-index in `await run_in_threadpool(...)`, `src/teacher_escalation.py:239` uses
  `asyncio.to_thread`, and 79 call sites for the two helpers exist under `routes/`, `src/` and
  `services/`; none of them is in a memory path.
- **Impact:** every request served by the same worker waits for the audit's synchronous half. The cost
  scales with the total stored memory count across all owners, not with the caller's slice, so a store
  of a few thousand entries blocks the loop for seconds at a time. `POST /api/memory/audit` is
  reachable by any authenticated user — the missing `can_manage_memory` gate on that route is
  `routes-rest-memory-personal-research.md`'s finding — and the automatic audit fires every five
  extracted memories (`AUDIT_INTERVAL`, `:114`), so this is not a rare admin action. The re-embedding
  itself is deliberate (the collection is shared); running it on the loop is not.
- **Fix:** move the blocking halves to a worker thread, e.g.
  `await asyncio.to_thread(memory_vector.rebuild, saved_entries)`, and the same for
  `memory_manager.save(...)` and the fingerprint/state writes if the store is large.

#### [BUG] Saving a SKILL.md drops every `##` heading outside the four known section names

- **Location:** `services/memory/skill_format.py:292-295` (`parse_body`), with `:40-41`, `:346-349` and
  `services/memory/skills.py:428`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `parse_body` looks each `##` heading up in `_HEADING_TO_KEY` and starts a section with
  `key=None` when the lookup fails — the heading line itself is dropped, and the lines under it become
  `body_extra`:

  ```python
  for line in body.splitlines():
      m = re.match(r"^##\s+(.*?)\s*$", line)
      if m:
          heading = m.group(1).strip().lower()
          key = _HEADING_TO_KEY.get(heading)
          sections.append((key, []))
          continue
      sections[-1][1].append(line)
  ```

  `emit_body` writes the known sections first and appends `body_extra` last (`:346-349`), so the
  surviving text also moves to the end of the file. Probe (`/tmp/probe_mem/skill_probes.py`)
  round-tripping a SKILL.md in the common third-party layout:

  ```
  --- headings in input : ['# Release checklist', '## When to Use', '## Instructions', '## Examples']
  --- headings in output: ['## When to Use', '# Release checklist']
  ```

  The same round trip drops frontmatter keys the schema does not know (`license` and `allowed-tools`
  in the probe) and rewrites `status`, `confidence`, `source` and `created`. The rewritten text is what
  lands on disk: `import_bundle_from_files` writes `sk.to_markdown()` (`services/memory/skills.py:428`)
  instead of the fetched file, and every edit goes through `update_skill` (`:432`) → `_write_skill`
  (`:175-181`, `atomic_write_text(path, sk.to_markdown())` at `:179`), which
  `POST /api/skills/{id}/markdown` reaches at `routes/skills_routes.py:1827`. The module docstring states the opposite for the body: "Anything else
  (raw paragraphs after the last known section) is preserved in `body_extra` and round-trips on save"
  (`:40-41`) — the paragraphs survive, their headings do not.
- **Impact:** a user who saves a skill whose markdown carries `## Notes`, `## Instructions` or
  `## Examples` — through the raw-markdown route or any later edit — or who imports a third-party
  SKILL.md written for a different section vocabulary, gets a file back whose headings are gone and
  whose sections have been reordered to the end of the document. The text is
  still there, so nothing is unrecoverable except the headings and the unknown frontmatter keys, and
  the original file is still at the source URL for an import — but the saved skill no longer reads the
  way it was written, and nothing warns.
- **Fix:** keep the unknown heading line when a `##` heading does not map to a known key (append it to
  `body_extra` before its lines, or store an ordered list of raw sections), and carry unknown
  frontmatter keys through `to_frontmatter` the way `body_extra` is carried. If the normalisation is
  intended, say so in the docstring and in the import response instead of claiming a round trip.

#### [ERROR-HANDLING] An unreadable memory store is reported as "nothing to audit", so the Tidy route answers 200 for a store it could not read

- **Location:** `services/memory/memory_extractor.py:516-519`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the audit's first read uses the lenient loader, which answers a failed read with an
  empty list, and the empty list is then reported as a successful no-op:

  ```python
  existing = memory_manager.load(owner=owner)
  if not existing:
      logger.info("Memory audit: nothing to audit")
      return {"before": 0, "after": 0}
  ```

  Probe (`/tmp/probe_mem/audit_unreadable.py`) with a store holding `{"not": "a list"}`:

  ```
  corrupt store: load_all() -> []
  corrupt store: load_all_for_update() -> MemoryStoreUnreadable: .../memory.json is not a JSON array (got dict)
  audit_memories() -> {'before': 0, 'after': 0}
  route response would be -> {'ok': True, 'before': 0, 'after': 0, 'removed': 0}
  ```

  The route builds that response from the result (`routes/memory/memory_routes.py:328-337`), so the
  caller gets HTTP 200 and `ok: true`. Every other path in the same file and module treats this state
  as an error: `extract_and_store` loads through `load_all_for_update()` and returns with
  "Skipping auto memory extraction, store unreadable" (`:392-399`), the audit's own merge step does the
  same and returns `{"error": "store_unreadable"}` (`:640-648`), and the route module's
  `_load_for_update` answers 503 "Memory store is temporarily unreadable — no changes were made"
  (`routes/memory/memory_routes.py:38-50`). The store is not damaged by this path — nothing is written
  — but the failure is invisible.
- **Impact:** a user whose `memory.json` is truncated or holds the wrong shape sees "Tidy" report 0
  before and 0 after with no error, which reads as "your memory is empty and clean" rather than "the
  store could not be read". That is the state `MemoryStoreUnreadable` exists to make loud, and the
  same state on the add path is already a 503. The user's actual memories are unaffected, so this is a
  diagnostic failure, not data loss.
- **Fix:** load through `load_all_for_update()` and return `{"error": "store_unreadable"}` (or raise)
  on `MemoryStoreUnreadable`, so the route answers 503 instead of 200 with zero counts.

#### [BUG] Importing a bundle whose SKILL.md sits at a nested path leaves a second, unowned copy of the skill on disk

- **Location:** `services/memory/skills.py:414-416` (with `:403`, `:428` and `:159-164`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the importer preserves the bundle's own layout under the skill directory and then also
  writes a root `SKILL.md`, so a bundle fetched from a skill folder keeps its original nested file:

  ```python
  # Preserve bundle layout (templates/, references/, etc.) under the skill dir.
  for rel, content in files.items():
      safe = _safe_relpath(rel)
      dest = os.path.join(skill_dir, safe)
      os.makedirs(os.path.dirname(dest), exist_ok=True)
      atomic_write_text(dest, content)
  ...
  atomic_write_text(self._skill_file(cat, nm), sk.to_markdown())      # :428
  ```

  The keys in `files` are repo-root-relative (`_list_github_dir` builds them as
  `f"{rel_dir}/{name}"`, `services/memory/skill_importer.py:416`), so a bundle fetched from
  `.../tree/main/skills/release-checklist` keeps
  `skills/release-checklist/SKILL.md` as a sub-path. `_iter_skill_files` (`:159-164`) yields *every*
  directory containing a file named `SKILL.md`, so the nested copy becomes a second skill record.
  Probe (`/tmp/probe_mem/skill_probes.py`) importing such a bundle:

  ```
  files on disk: ['imported/release-checklist/SKILL.md', 'imported/release-checklist/skills/release-checklist/SKILL.md', 'imported/release-checklist/skills/release-checklist/reference.md']
  load_all() names : ['release-checklist', 'release-checklist']
  load_all() owners: ['None', 'alice']
  load(owner=alice) : ['release-checklist']
  ```

  The nested copy keeps the frontmatter's own fields, so it is unowned (`None`) while the root copy
  carries the importing user. `load(owner=...)` filters strictly, so the duplicate is invisible in the
  owner's own list, but `load_all()` — used by `add_skill`'s name set (`:353`) and by the backup
  import (`routes/backup_routes.py:112`) — returns both. The nested directory is also what
  `read_skill_reference` serves: a reference file under it is readable through the preserved sub-path
  (`skills/release-checklist/reference.md` in the probe).
- **Impact:** one import can create two records for one skill. The unowned copy occupies the name in
  the global name set, so a later `add_skill` or import of that name is silently renamed
  (`name-2`) even though the user cannot see the skill that caused the collision; in the no-auth
  single-user deployment, where `load(owner=None)` returns everything, both copies are listed and the
  first delete removes only one of them. Disk use is doubled for the bundle. Nothing is lost, and an
  owner-scoped delete of the skill removes the whole directory including the nested copy.
- **Fix:** skip a bundle file whose basename is `SKILL.md` when its path differs from the chosen
  `pick_skill_md` key (or flatten it), so a bundle contributes exactly one `SKILL.md` per skill
  directory; alternatively, make `_iter_skill_files` ignore `SKILL.md` files below the skill root.

#### [TYPE-SAFETY] A non-list `steps` or `tags` value from the skill extractor's LLM reply is stored as a per-character list

- **Location:** `services/memory/skills.py:365` and `:375` (with `services/memory/skill_extractor.py:280-281`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `add_skill` coerces both fields with `list(...)` and no type check, and the extractor
  passes the model's JSON values straight through:

  ```python
  steps=data.get("steps", []),        # skill_extractor.py:280
  tags=data.get("tags", []),          # skill_extractor.py:281
  ```
  ```python
  tags=list(tags or []),                                            # skills.py:365
  procedure=list(procedure if procedure is not None else (steps or [])),   # skills.py:375
  ```

  Probe (`/tmp/probe_mem/skill_probes.py`) with `steps="1. build\n2. push"` and `tags="deploy ci"`:

  ```
  procedure stored as: ['1', '.', ' ', 'b', 'u', 'i', 'l', 'd', '\n', '2', '.', ' ', 'p', 'u', 's', 'h']
  tags stored as     : ['d', 'e', 'p', 'l', 'o', 'y', ' ', 'c', 'i']
  --- SKILL.md on disk ---
  tags: [d, e, p, l, o, y,  , c, i]
  ...
  ## Procedure

  1. 1
  2. .
  3.  
  4. b
  ```

  The skill is created and written, so the corruption is persisted rather than rejected. `str` is not
  the only shape: a dict or a list of dicts reaches `to_frontmatter`/`_emit_scalar` the same way. The
  HTTP add path is typed (`tags: List[str]`, `procedure: List[str]`,
  `routes/skills_routes.py:42-47`) and the agent tool path passes the model's JSON arguments
  unvalidated (`src/tools/system.py:120-140`), so the exposure is the two model-authored paths, not
  the form. `title` is handled: a non-string title raises `AttributeError` at
  `skill_extractor.py:238`, which the enclosing `except Exception` turns into a logged drop.
- **Impact:** a model that answers with a string (or an object) for `steps`/`tags` — a common
  LLM-output shape — produces a skill whose procedure is a list of single characters and whose tags
  are single letters, written to `data/skills/<category>/<name>/SKILL.md` and served to the agent by
  `read_skill_md`. It needs no further mistake to cause harm, but the damage is confined to one
  auto-created skill, which the user can delete, and a re-run of the extractor after the first
  creation is dropped as a duplicate title.
- **Fix:** coerce with a shape check before use — `steps = [str(s) for s in steps] if isinstance(steps, list) else []`
  (and the same for `tags`) in `add_skill`, or validate the parsed object in `_extract_json_object`'s
  callers. Rejecting the field is better than splitting it.

#### [PERF] The skill importer buffers a whole response body before applying its 400 KB file cap

- **Location:** `services/memory/skill_importer.py:211` (the transport), with `:21` and `:379-386`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the pinned transport reads the entire body into memory before httpx hands it back,
  and the only size guard runs afterwards:

  ```python
  core_response = self._pool.handle_request(core_request)
  content = b"".join(cast(Iterable[bytes], core_response.stream))    # :211
  ```
  ```python
  def _fetch_bytes(url: str) -> bytes:
      r = _get_checked(url, headers={"Accept": "application/vnd.github+json"}, timeout=30.0)
      if r.status_code >= 400:
          raise _github_response_error(r)
      _assert_github_url(str(r.url), context="redirect target")
      if len(r.content) > MAX_FILE_BYTES:                            # :384
          raise SkillImportError(f"file too large: {url}")
  ```

  Probe (`/tmp/probe_mem/transport_buffer.py`) driving the real `_PinnedTransport` with a stub httpcore
  pool that streams 80 × 64 KiB:

  ```
  MAX_FILE_BYTES               : 400000
  chunks the transport drained : 80 x 65536 bytes
  len(response.content)        : 5242880
  buffer exceeds the cap by    : 4842880 bytes
  ```

  Every fetch goes through this path — the SKILL.md, each sibling asset, and each entry of the
  directory listing (`_fetch_text`, `:389-393`), which fetches any file whose suffix is in
  `ALLOWED_SUFFIXES` (`.json`, `.csv`, `.md`, …). The GitHub contents API already returns a `size` per
  entry, which the listing loop ignores.
- **Impact:** the 400 KB / 2 MB limits bound what the importer *keeps*, not what it *reads*: a single
  allowed-suffix file in the imported repository is downloaded in full before it is rejected, so an
  admin importing from a repository that carries a large asset pays its whole size in server memory.
  Reachability is limited — the caller is an authenticated admin pasting a GitHub URL, and the
  repository is a third party's, not the requester's own — so the exposure is a memory spike on one
  request rather than a remotely triggerable outage. I did not measure what body size
  `raw.githubusercontent.com` will serve.
- **Fix:** check the listing's `size` before fetching an entry, and bound the read in
  `_PinnedTransport.handle_request` (accumulate the stream and abort past `MAX_FILE_BYTES`) so the cap
  holds for the raw and redirect paths too.

#### [DEAD-CODE] `MemoryService` has no production caller, and its `delete` and `recall` carry no owner

- **Location:** `services/memory/service.py:32-126` (with `:42-48`, `:90-108`, `:116-126`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** nothing outside the module and its tests constructs it:

  ```
  $ grep -rn "MemoryService(" --include=*.py .
  ./services/memory/service.py:37:        service = MemoryService()          # the docstring example
  ./tests/test_memory_imports.py:29:    service = MemoryService(str(tmp_path))
  ./tests/test_memory_recall_nondict_rows.py:20:    svc = MemoryService(str(tmp_path))
  ```

  The class is still imported on every memory request — `services/memory/__init__.py:4` imports it and
  `routes/memory/memory_routes.py:24` and `routes/backup_routes.py:9` import the package — so it is
  live code that looks live. Its API has no owner anywhere: `delete(memory_id)` rewrites the whole
  store from `load_all()` and removes the matching vector row (`:116-126`), `recall` delegates to
  `NativeMemoryProvider` without an owner, and `get_all` returns the first 100 entries of the shared
  store (`:111-113`). The two tests that exercise it pin its shape, not its reachability
  (`tests/test_memory_imports.py` drives remember/get_all/recall/delete on a single-user store).
- **Impact:** none today — no caller reaches it. It matters as a hazard and as a false signal: the
  module is exported from `services/__init__.py` as the service-layer memory API and its docstring
  shows `await service.remember(...)` usage, so the next caller to wire it up inherits an
  id-only delete that crosses owners on a multi-user instance, where the live path
  (`MemoryManager` through the routes) checks ownership on every mutation. Its
  `MemoryVectorStore` construction is also gated on `data/memory_vectors` existing
  (`:44-46`), a directory only `setup.py` creates.
- **Fix:** delete `service.py` and its exports from `services/memory/__init__.py` and
  `services/__init__.py` (and the two tests), or, if the facade is meant to be the service-layer
  entry point, give `remember`/`recall`/`get_all`/`delete` an owner argument and route them through
  `NativeMemoryProvider`'s owner-aware methods.

## 37. services: research and docs

### Overview

The two service-layer facades under `services/`: `services/docs/__init__.py` and
`services/docs/service.py` wrap the personal-document RAG lane in a `DocsService` that returns
`DocChunk` and `IndexResult` values, and `services/research/__init__.py`,
`services/research/research_handler.py` and `services/research/service.py` wrap a second copy of the
deep-research handler in a `ResearchService` that returns `ResearchResult`/`ResearchSource` values
and starts background jobs. Neither facade is constructed anywhere in production: the only importers
are the packages' own `__init__.py` files, `services/__init__.py`, and the tests, and the research
copy is recorded as a retirement item at `specs/research.md:150`.

The boundary: the live research handler is `src/research_handler.py` — `src/app_initializer.py:117`
constructs it, `app.py:713` hands it to the research routes, and `src/task_scheduler.py:2018` imports
it — so the file of that name in this section is a copy, not the runtime one. That copy, the routes
that serve it (`routes/research/research_routes.py`), and the report store and research engine are
`src-research-scheduling` and `routes-rest-memory-personal-research`; this section cites their code
where a finding rests on it and does not restate their findings. The vector lane the docs facade
calls (`src/rag_manager.py`, `src/rag_vector.py`, `src/embedding_lanes.py`) is `src-memory-rag`, and
`services/__init__.py`, which re-exports both packages, is `services-media`. "Docs" here is
personal-document RAG, not the living-document store that `scripts/odysseus-docs` and the document
routes read.

### Coverage

**Read fully:** all five assigned files (805 lines): `services/research/research_handler.py` (487),
`services/research/service.py` (167), `services/docs/service.py` (121), `services/docs/__init__.py`
(18), `services/research/__init__.py` (12). Working-tree line numbers refer to `2992bf6d368a`
(`git rev-parse --short=12 HEAD`); `git status --short` showed only the untracked `audit/`
directory, and the five files are unmodified against `HEAD`.

**Read partially:** the boundary code the findings rest on — the live handler
`src/research_handler.py` at `_research_json_path` (`:53-62`), `start_research` (`:240-364`), the
status/result/sources/raw-findings readers (`:407-521`) and `_handle_research_failure` (`:943-949`);
`src/rag_manager.py` in full (70 lines); `src/rag_vector.py` at `__init__`/`healthy` (`:76-142`),
`search` and its keyword fallback (`:348-443`), `index_personal_documents` (`:495-556`) and the
owner-scoped document-id helper (`:48-55`); `src/rag_singleton.py` in full (63 lines);
`src/constants.py` at the data-path constants (`:41-56`); `services/__init__.py` in full (27 lines);
`services/search/service.py` at the offloaded `comprehensive_web_search` call (`:64-77`);
`src/chat_processor.py:366`; `routes/personal_routes.py` at `_rag()`, the index-job lock and the
add-directory route (`:150-260`); `routes/research/research_routes.py` at the library owner gate
(`:367-386`); `src/app_initializer.py:117-124`; `app.py:713`; `src/task_scheduler.py:2014-2024` and
`:2122-2132`; `src/deep_research.py` at the round loop and the time budget (`:296`, `:536`,
`:796-797`); `specs/research.md:105-160` and `specs/documents-rag-uploads.md:150-170`. Tests read in
full: `tests/test_docs_query_nondict_rows.py`, `tests/test_research_handler_path_confinement.py`,
`tests/test_services_research_low_quality_sources.py`; the suites named under *Checks run* were
otherwise read only by result.

**Not read:** the live handler's other ~630 lines (`rename_owner`, the report HTML and image-hide
paths, the research-service call and the parts of the report formatter the copy does not share);
`src/deep_research.py` beyond the round loop and the time budget; the embedding, Chroma-client and
personal-docs internals (`src/embedding_lanes.py`, `src/chroma_client.py`, `src/embeddings.py`,
`src/personal_docs.py` beyond `retrieve_personal`); the rest of `routes/personal_routes.py` and
`routes/research/research_routes.py`; `src/task_scheduler.py` beyond the two regions above; the front
end; and every other `services-*` section. No live model, embedding service, Chroma instance or
browser was exercised, and no directory was indexed against a real vector store; the RAG probes below
stub the lane query and the chunk splitter so the surrounding code path stays real.

**Checks run:** `git rev-parse --short=12 HEAD`, `git status --short`, `wc -l` on the assigned files;
caller searches for the five assigned modules and their classes
(`grep -rn "services\.research\|services/research" --include=*.py .`, `grep -rn
'ResearchService\|ResearchHandler\|DocsService\|DocChunk\|IndexResult' app.py core routes src scripts`,
`grep -rn services scripts/`); greps for the store-directory constants (`CHROMA_DIR`, `RAG_DIR`); a
search for
`wait_for|TimeoutError|hard_timeout` in both research handlers; and four probes under
`venv/bin/python` with data directories in `/tmp` (outside the checkout), each quoted in the finding
it settles:

- **Report-path probe.** The copy's `get_status`, `get_result` and `_save_result` were called with
  `session_id="../outside"` and `RESEARCH_DATA_DIR` redirected to a temporary directory holding a
  sibling `outside.json`; the same id was passed to the live handler's `_research_json_path`.
- **Lane-filter and chunk-metadata probe.** `DocsService.query` and `DocsService.index` were run
  against the real `RAGManager`/`VectorRAG` code with `query_lanes`/`lane_count` stubbed to record the
  `where` filter, and with `add_document`/`_split_into_chunks` stubbed to record the metadata the
  indexer writes.
- **Index-result probe.** `DocsService.index` was run against the real `index_personal_documents`
  for a directory that does not exist, and the keys that method can return were read from its source.
- **Import probe.** `import services.search` was timed and inspected in `sys.modules` to see what the
  package `__init__` pulls in.

`venv/bin/python -m pytest -q` was run with the 41 files matching `ls tests | grep -iE
'research|docs|report'` (the docs/RAG, research, deep-research, personal-docs and visual-report
suites, `tests/run_order_report.py` and `tests/test_run_order_report.py` included) — **245 passed**,
3 warnings in 3.86s. The suites that pin this section's own modules
(`tests/test_docs_query_nondict_rows.py`, `tests/test_research_service.py`,
`tests/test_services_research_low_quality_sources.py`, `tests/test_svc_research_sources_nondict.py`,
`tests/test_research_handler_analyzed_urls.py`) are among them. The full suite and `audit.py` were not
run; run-level generation, counts and secret-gate validation belong to the coordinating reviewer.

#### [SECURITY] The compatibility research handler joins an unvalidated session id into its report path

- **Location:** `services/research/research_handler.py:117`, `:154`, `:174`, `:202`, `:219`
- **Severity:** low
- **Disposition:** next
- **Evidence:** five methods build the on-disk report path by joining the caller's id with no
  validation — `get_status` (`:117`), `get_result` (`:154`), `get_sources` (`:174`), `clear_result`
  (`:202`, which unlinks it) and `_save_result` (`:219`, which overwrites it):

  ```python
  path = RESEARCH_DATA_DIR / f"{session_id}.json"
  ```

  `ResearchService` forwards its caller's `session_id` unchanged (`services/research/service.py:157`,
  `:163`, `:167`). The live handler guards exactly this id with a regex plus a resolve-and-contain
  check, and its callers rely on it:

  ```python
  # src/research_handler.py:53-62
  def _research_json_path(session_id: str) -> Optional[Path]:
      if not isinstance(session_id, str) or not _RESEARCH_SESSION_ID_RE.fullmatch(session_id):
          return None
      root = RESEARCH_DATA_DIR.resolve()
      path = (RESEARCH_DATA_DIR / f"{session_id}.json").resolve()
      try:
          path.relative_to(root)
      except ValueError:
          return None
      return path
  ```

  `tests/test_research_handler_path_confinement.py:24-28` pins that `"../escape"`, `".."`,
  `"rp/test"` and `""` are rejected for the live module. Measured on the copy, with
  `RESEARCH_DATA_DIR` pointed at a temporary directory beside a file the id escapes to:

  ```
  svc path expr  : /tmp/svcprobe-jyv7er81/deep_research/../outside.json
  resolves to    : /tmp/svcprobe-jyv7er81/outside.json
  inside dir?    : False
  svc get_status("../outside") -> {'status': 'done', 'progress': {}, 'query': 'OUTSIDE-DIR-REPORT', 'started_at': 0}
  live _research_json_path("../outside") -> None
  outside.json after svc _save_result -> {"query": "OVERWRITTEN", "status": "done", "result": "OVERWRITTEN", ...}
  ```

  Reachability: nothing in production constructs this handler. `grep -rn
  'ResearchService|ResearchHandler|DocsService' app.py core routes src scripts` returns the live
  class in `src/app_initializer.py:23`, `:117`, `src/research_handler.py:65` and
  `src/task_scheduler.py:2018`, no reference to the copies (the one other hit,
  `routes/auth_routes.py:474`, is a comment about the live handler's registry), and no reader of
  either facade; the copies reach the runtime only as
  imports, because `services/research/__init__.py:5` re-exports this handler and
  `services/__init__.py:13` re-exports that, so any `from services.X import Y` in the app executes the
  chain (`import services.search` left `services.research.research_handler` and
  `services.docs.service` in `sys.modules`). `specs/research.md:120` and `:150` record the copy as
  compatibility surface to retire, and `specs/research.md:129` states the policy it does not meet
  ("Persisted report access and mutations should return 404 for cross-owner or null-owner JSON").
- **Impact:** a caller of `ResearchService` — or of the handler directly, which is how the project's
  own parity test loads it — that passes an id containing `..` or a path separator reads, overwrites
  or deletes a `*.json` file outside `data/deep_research`: another application store under `data/`, or
  a file outside the data directory entirely. No caller exists today, so this is a latent defect in
  the surface the spec asks to keep at parity, not a live vulnerability; the gap is specific to the
  copy, which did not receive the guard the live module got.
- **Fix:** retire the copy as `specs/research.md:150` proposes, or give it the same
  `_research_json_path` helper and reject an invalid id in `start_research` the way
  `src/research_handler.py:265-266` does.

#### [SECURITY] The docs facade cannot scope a search or an index write to an owner

- **Location:** `services/docs/service.py:52` (`query`), `:104` (`index`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** neither method takes an owner, and the lane treats an absent owner as "no filter":

  ```python
  results = self.rag.search(query, k=top_k)              # services/docs/service.py:52
  result = self.rag.index_personal_documents(directory)  # services/docs/service.py:104
  ```

  ```python
  # src/rag_vector.py:357 (search)
  where_filter = {"owner": owner} if owner else None
  # src/rag_vector.py:536-537 (index_personal_documents)
  if owner:
      meta['owner'] = owner
  ```

  The keyword fallback applies the same rule (`if owner and meta.get("owner") != owner: continue`,
  `src/rag_vector.py:420`). `RAGManager` forwards an owner when it is given one
  (`src/rag_manager.py:35-37`, `:39-50`), and the live callers pass it:
  `src/chat_processor.py:366` (`rag_manager.search(message, k=5, owner=owner)`),
  `routes/personal_routes.py:232` (`rag.index_personal_documents(directory, owner=owner)`) and
  `src/personal_docs.py:302`. Measured with the real `search`/`index_personal_documents` code and the
  lane query stubbed to record its filter:

  ```
  lane filter from DocsService.query() -> [('search', None)]
  lane filter with owner='alice'      -> [('search', {'owner': 'alice'})]
  chunk metadata written             -> [{'source': '/tmp/.../a.txt', 'filename': 'a.txt', 'directory': '/tmp/...', 'type': '.txt', 'chunk_id': 0}]
  chunk metadata with owner='alice'  -> [{'source': ..., 'owner': 'alice', 'chunk_id': 0}]
  ```

  No production module constructs `DocsService` (`grep -rn 'DocsService' app.py core routes src
  scripts` returns nothing).
- **Impact:** a consumer of the facade searches every owner's indexed personal documents — `owner=None`
  disables the lane filter, so the query is unscoped — and writes chunks that carry no owner, which
  every owner-filtered search then excludes. Nothing is exposed today because nothing calls it; the
  hazard is that `services/docs/service.py` is the documented facade for this lane
  (`specs/documents-rag-uploads.md:159`) and it cannot express the scoping the live paths use, so the
  first caller to adopt it gets both failure modes.
- **Fix:** add an `owner` parameter to `query` and `index` and pass it to the lane, or delete the
  facade in favour of `RAGManager`/`VectorRAG`, whose signatures already take it.

#### [ERROR-HANDLING] `DocsService.index` cannot report an error: the key it reads is never returned and `success` is dropped

- **Location:** `services/docs/service.py:104-109`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the facade reads three keys, and the only backend supplies two of them:

  ```python
  result = self.rag.index_personal_documents(directory)
  return IndexResult(
      indexed=result.get("indexed_count", result.get("indexed", 0)),
      failed=result.get("failed_count", result.get("failed", 0)),
      errors=result.get("errors", []),
  )
  ```

  `self.rag` is a `RAGManager`, which delegates to `VectorRAG.index_personal_documents`
  (`src/rag_manager.py:39-50`), whose two returns are
  `{success, indexed_count, failed_count, message}` (`src/rag_vector.py:548-553`, `:556`) — no
  `errors` key, and its per-file error text goes to the log only (`:545`). Read from the source and
  measured for a directory that does not exist:

  ```
  return keys of VectorRAG.index_personal_documents: ['chunk_id', 'directory', 'failed_count', 'filename', 'indexed_count', 'message', 'source', 'success', 'type']
  any 'errors' key in that source: False
  DocsService.index body reads: ['indexed_count', 'indexed', 'failed_count', 'failed', 'errors']

  missing dir -> IndexResult(indexed=0, failed=0, errors=[])
  raw backend -> {'success': True, 'indexed_count': 0, 'failed_count': 0, 'message': 'Indexed 0 chunks from /nonexistent/dir/xyz'}
  ```

  The module's own test supplies the missing key from a fake and names the case after the live shape:
  `tests/test_docs_query_nondict_rows.py:22` returns `{"indexed_count": 7, "failed_count": 2,
  "errors": ["bad.pdf"]}` under `test_index_maps_live_vectorrag_result_shape` (`:37`), so its
  `errors` assertion (`:45`) pins a shape the live backend does not produce. The spec describes the
  mapping as `indexed_count`/`failed_count` plus the legacy `indexed`/`failed`
  (`specs/documents-rag-uploads.md:159`).
- **Impact:** every failure shape collapses into the same success-shaped result. A directory that does
  not exist, an empty directory and a directory whose files all failed to extract are indistinguishable
  (`indexed=0, failed=0, errors=[]`), and the per-file reasons never reach the caller. The live route
  branches on the flag the facade drops (`if result["success"]:`, `routes/personal_routes.py:233`,
  `:250`), so this is a facade-specific loss rather than a backend one.
- **Fix:** carry `success` (and `message`) on `IndexResult` and populate it from the result — raising
  or returning a failed result when it is false — and either have the backend return `errors` or drop
  the field and fix the test to use the live shape.

#### [PERF] The async entry points run blocking index, search and web-search work on the event loop

- **Location:** `services/docs/service.py:52` and `:104`, `services/research/research_handler.py:445`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `DocsService.query` and `DocsService.index` are `async def` (`:41`, `:94`) and call the
  synchronous Chroma/embedding work inline, where the live route moves the identical call to a worker
  thread:

  ```python
  # routes/personal_routes.py:247-248, with the blocking cost noted at :151-154
  async with _index_job_lock:
      result = await run_in_threadpool(_index_directory)
  ```

  `_index_directory` is `rag.index_personal_documents(directory, owner=owner)`
  (`routes/personal_routes.py:232`), and the route reads the `success` flag the docs facade drops
  (`:233`, `:250`). The research copy's failure fallback has the same shape with an
  outbound fetch: `comprehensive_web_search` is synchronous, and the sibling service runs it in a
  thread with a comment saying why —

  ```python
  # services/search/service.py:66-72
  # comprehensive_web_search is synchronous ... Run it off the event
  # loop so we don't block it, ...
  _context, raw_results = await asyncio.to_thread(
      comprehensive_web_search,
  ```

  — while the copy calls it directly from the async `call_research_service` path:

  ```python
  # services/research/research_handler.py:443-445
  from src.search import comprehensive_web_search
  search_result = comprehensive_web_search(query)
  ```

  That last line is identical to the live handler's (`src/research_handler.py:949`), so it is not
  unique to the copy; the docs-side calls are, since no other code path in this section has a worker
  thread between the coroutine and the store.
- **Impact:** a caller that awaits `DocsService.index` on a large directory stalls every other
  coroutine in that process for the walk, the text extraction and the embedding calls, and
  `DocsService.query` does the same per query; the research fallback blocks the loop for a multi-page
  web search. No caller exists today, so the cost is unpaid — this is the shape a future caller
  inherits, and the two sibling implementations already show the fix.
- **Fix:** `await asyncio.to_thread(self.rag.index_personal_documents, directory)` and the same for
  `search` and `comprehensive_web_search`, or make these entry points synchronous so the caller owns
  the decision to offload.

## 38. services: hardware fit

### Overview

`services/hwfit/__init__.py` (empty), `services/hwfit/data/hf_models.json`,
`services/hwfit/data/mlx_community_models.json`, `services/hwfit/fit.py`,
`services/hwfit/hardware.py`, `services/hwfit/hf_discovery.py`,
`services/hwfit/image_models.py`, `services/hwfit/models.py`,
`services/hwfit/profiles.py`.

The hardware-fit service: `hardware.py` probes RAM, CPU and GPU locally or over SSH and caches the
result per target; `models.py` loads and merges the bundled and runtime model catalogues and holds
the quant, parameter-count and memory arithmetic; `fit.py` ranks catalogue rows against a detected
system and produces the fit level, speed estimate and composite score; `profiles.py` turns a model
plus a system into llama.cpp serve flags; `hf_discovery.py` refreshes the two runtime catalogues
from the Hugging Face API; `image_models.py` discovers and ranks image-generation models; and the
two JSON files are the bundled offline catalogue (924 and 629 rows).

The boundary: the four HTTP endpoints that call this service (`/api/hwfit/system`, `/models`,
`/profiles`, `/image-models`), their host/port validation, the caller-supplied `model_path` probe
and the missing admin gate on that router are `routes-rest-integrations-misc`, which reviews
`routes/hwfit_routes.py`. This section covers the layer behind those calls — how a host, port or
model path becomes a subprocess, an SSH invocation, a file read or an outbound request, and how a
catalogue row becomes a recommendation. `core/platform_compat.py` (the SSH argv builder) is
`core-data-platform`; `src/outbound_fetch.py` is `src-security`; the Cookbook's own GPU probe is
`routes-cookbook`; the front-end consumers of these results are
`static-js-cookbook-settings-models`; the catalogue import scripts are `scripts`. None of them were
reviewed here beyond the lines a finding cites. No module in this section reads the settings store
(`grep -rn 'settings' services/hwfit/*.py` returns nothing), so there is no settings dependency to
trace.

### Coverage

**Read fully:** the seven Python modules in scope, 3,173 lines: `services/hwfit/hardware.py` (907),
`services/hwfit/fit.py` (876), `services/hwfit/image_models.py` (435),
`services/hwfit/hf_discovery.py` (374), `services/hwfit/models.py` (343),
`services/hwfit/profiles.py` (238), `services/hwfit/__init__.py` (0 — the file is empty). Also read
fully as boundary material: `routes/hwfit_routes.py` (456 lines — the only production caller of the
service), `core/platform_compat.py:172-185` and `:362-417` (`NVIDIA_PATH_CANDIDATES`,
`SSH_PATH_OVERRIDE`, `_ssh_exec_argv`, `run_ssh_command`), `app.py:811-812`, and the nine suites
that pin this surface:
`tests/test_hwfit_remote_validation.py`, `tests/test_hwfit_models_nonstring_fields.py`,
`tests/test_hwfit_params_b_malformed.py`, `tests/test_hwfit_bandwidth_nonstring.py`,
`tests/test_hwfit_gpu_count_nonnumeric.py`, `tests/test_hwfit_cpu_only_fallback.py`,
`tests/test_image_models_nonstring_search.py`, `tests/test_image_models_nondict_system.py`,
`tests/test_serve_profiles.py`.

**Read structurally, not line by line:** `services/hwfit/data/hf_models.json` (19,477 lines, 924
rows) and `services/hwfit/data/mlx_community_models.json` (15,727 lines, 629 rows). Both were
parsed and every field of every row was type-censused with a script, and the head of each file plus
representative rows were read; the full text was not. The same census was run over the two runtime
caches a live instance feeds into `get_models()` — `data/hwfit/hf_collection_models.json` (501 rows)
and `data/hwfit/mlx_community_models.json` (659 rows), untracked runtime state present in this
checkout. Result: `name`, `parameter_count`, `quantization`, `use_case`, `provider` are strings in
every row of all four files; `parameters_raw` and `context_length` are ints in every row;
`active_parameters` is an int or `null` (52 static rows); and 29 static rows carry
`release_date: null` (handled by the `newest` sort and by the front end, so not reported).

**Read partially:** the other eleven `tests/test_hwfit_*.py` suites by search (what each pins)
rather than end to end; `static/js/cookbook-hwfit.js:158-168` (`_downloadSourceRepo`) and `:884`, and
`static/js/cookbookDownload.js:68`, `:477` (the consumers of `quant_repo`); `routes/cookbook_routes.py:3231-3237`;
`src/outbound_fetch.py:1-45` (docstring and private-address tables); the run's `header.md` and
`coverage-boundaries.md`, and the two reference sections.

**Not read:** `routes/_validators.py` (the host/port validators the routes call — their effect is
recorded in `routes-rest-integrations-misc` and in `coverage-boundaries`); `core/platform_compat.py`
outside the SSH and `which` helpers cited above; the rest of `src/outbound_fetch.py` and
`services/search/content.py`; the Cookbook's own GPU probe and the rest of `routes/cookbook_routes.py`;
the rest of the front end; `scripts/add_hwfit_models.py` and `scripts/import_from_vllm_recipes.py`
(assigned to `scripts`); the catalogue files line by line; the eleven other suites that were
executed but not read.

**Checks run:** `git log --oneline -1` → `2992bf6d fix(tools): publish blank-body files atomically`,
and `git status --porcelain` → only the untracked `audit/` directory, so the working tree matches the
commit for these paths and the line numbers below refer to it. The twenty suites matching this
module (`ls tests | grep -iE 'hwfit'` plus the three image/profiles suites that do not carry the
`hwfit` prefix) were run from the repository root with
`PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q -p no:cacheprovider …` — **126 passed, 1
warning** (the pre-existing SQLAlchemy `declarative_base()` deprecation). Five throwaway probes were
run with stdin scripts that replaced the transport with recorders; their output is quoted in the
findings that rest on them. No probe opened a real SSH connection or made an outbound network
request, and the only hardware probing any of them did was the local `/proc` and `/sys` reads the
service itself performs on this machine (no GPU operation was performed). Greps: the callers of `_read_file`/`_inspect_model_path`, `settings` in
`services/hwfit/`, the `_should_discover_variants` chain, and the consumers of `release_date` and
`quant_repo`. `./audit.py` was not run and no source, test, or run-level file was edited.

**Noted, not reported.** Three things I checked that did not become findings. (1) A failed remote
detection is cached as a result for `CACHE_TTL` (86,400 s): after one failed probe of a host, later
`detect_system` calls for it return `{"error": "Cannot connect to …"}` without retrying (measured: 2
SSH attempts, then 0). The `fresh=true` path the Rescan button uses bypasses the cache, so a user
can recover; it is a design choice, not a defect. (2) `refresh_mlx_community_cache` has no
per-source error containment while its sibling `refresh_hf_collection_models_cache` catches per
source, so an outage for `mlx-community` aborts the whole dynamic refresh; the route reports that to
the caller (`routes/hwfit_routes.py:209-213`) and the bundled catalogue still serves, so the impact
is a failed refresh, not a wrong answer. (3) `_fetch_hf_image_collection_models` calls `data.get`
on the parsed body without checking it is an object (`image_models.py:183`); a JSON array body raises
`AttributeError` out of `get_image_models`. I could not establish that the Hugging Face collections
endpoint returns a non-object for a valid slug, so it is recorded here rather than as a finding.

#### [RACE] One probe's SSH target is process-global, so concurrent requests swap hosts and cache each other's hardware

- **Location:** `services/hwfit/hardware.py:21-23` (the globals), `:27-31` (`_run` reads them), `:815` and `:904` (`detect_system` sets and clears them), `:689` (`_cache_by_host`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the target host of every probe is a module global that `detect_system` assigns at
  entry and clears at exit, and `_run` decides local-vs-remote from it at call time:

  ```python
  _remote_host = None  # set by detect_system(host=...)
  ...
  def _run(cmd):
      try:
          if _remote_host:
              ...
              r = run_ssh_command(_remote_host, _remote_port, cmd_str, ...)
          else:
              r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
  ```

  ```python
  _remote_host = host or None      # :815
  ...
  _remote_host = None              # :904
  _remote_platform = None          # :905
  _cache_by_host[cache_key] = (now, result)   # :906
  ```

  Nothing serialises this: there is no lock in the module, and the four endpoints are sync `def`
  handlers (`routes/hwfit_routes.py:186`, `:194`, `:319`, `:413`) that FastAPI runs in its worker
  threadpool, so two of them can be inside `detect_system` at once. Measured with a stdin probe that
  ran two threads — one `detect_system(fresh=True)` with no host, one
  `detect_system(host="audit-host.example", platform="linux", fresh=True)` — and replaced
  `run_ssh_command` with a recorder and `_run` with a wrapper that held the local thread before its
  first probe until the remote thread had set the global. No SSH connection was made:

  ```text
  local  request -> has_gpu=True gpu_name='NVIDIA GeForce RTX 4090' gpu_vram_gb=24.0
  remote request -> total_ram_gb=30.5 gpu_name='AMD GPU (card1)'
    ssh from 'A' -> 'audit-host.example' : cat /proc/meminfo
    ssh from 'local' -> 'audit-host.example' : nvidia-smi --query-gpu=memory.total,name --f
  cached ('_local', '', '') -> {'total_ram_gb': 125.1, 'gpu_name': 'NVIDIA GeForce RTX 4090', ...}
  cached ('audit-host.example', '', 'linux') -> {'total_ram_gb': 30.5, 'gpu_name': 'AMD GPU (card1)', ...}
  ```

  The local machine in that run is an AMD Strix Halo box whose own detection reports no NVIDIA GPU;
  the local request sent its `nvidia-smi` probe to the other caller's host and reported that host's
  GPU as its own.
  The remote request did the reverse: only its first probe went over SSH, and its result carries the
  local machine's CPU name and locally detected GPU.

- **Impact:** any two overlapping hardware-fit requests mix hardware between them, and the mixed
  result is stored in the process-wide cache under a key derived from the *caller's* own target
  (`_cache_key`, `:692-701`) for `CACHE_TTL` = 24 h (`:16`). A caller who asked for their own machine
  can be shown another user's host hardware, and every later local request — including the
  Cookbook's, which calls the same `detect_system` — sees the poisoned entry until someone passes
  `fresh=true`. The mixing also corrupts the remote side: a probe of `user@server` can report the
  server process's own CPU and GPU. Reachability is ordinary concurrency, not an attack: the SSH
  probes take seconds (15 s timeout, 5 s connect timeout per probe), and the routes that accept a
  host are reachable by any signed-in caller (`routes-rest-integrations-misc`). Two users pressing
  Rescan at the same time is enough; the non-admin gate recorded there makes it easier but is not
  required.
- **Fix:** stop using module globals for the probe target. Pass the target through an explicit
  parameter or a `threading.local()`/context object that `_run` and the `_detect_*` helpers read, and
  keep `_cache_by_host` keyed on that same per-call value. A module lock around `detect_system`
  would also close the race, at the cost of serialising all hardware probes.

#### [BUG] A single non-string field in one catalogue row still aborts the whole listing and ranking pass

- **Location:** `services/hwfit/models.py:132` and `:89` (`name` → `infer_quantization_from_name`), `:140` (`name` in `is_prequantized`), `:154` (`parameters_raw`), `:206` (`active_parameters`), `:247-248` (`infer_use_case`); `services/hwfit/fit.py:406` (`_native_quant`), `:451` (`context_length`) and `:463` (`quant_upper`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the catalogue parsers harden `parameter_count` and `quantization` but not their
  siblings, so several fields still reach a string method or an arithmetic operator unchecked:

  ```python
  def infer_quantization_from_name(name):
      n = (name or "").lower()                      # models.py:89
  ...
  def is_prequantized(model):
      name = (model.get("name") or "").lower()      # models.py:140
  ...
  def params_b(model):
      raw = model.get("parameters_raw")
      if raw and raw > 0:                           # models.py:154
  ...
  def _active_params_b(model):
      if model.get("is_moe") and model.get("active_parameters"):
          return model["active_parameters"] / 1_000_000_000.0   # models.py:206
  ```

  Measured on the real entry points — a stdin probe replaced `models._load_model_file` so the
  catalogue contained one malformed row and one good row, then called the functions the service
  uses:

  ```text
  get_models()  -> AttributeError: 'int' object has no attribute 'lower'
  rank_models() -> AttributeError: 'int' object has no attribute 'lower'

  {"name": 123}                 -> is_prequantized / _normalize_model_entry / infer_use_case /
                                   _native_quant / analyze_model all raise AttributeError
  {"use_case": 5}               -> infer_use_case and analyze_model raise AttributeError
  {"context_length": "32768"}   -> analyze_model raises TypeError (min() on str and int)
  {"active_parameters": "1e9"}  -> analyze_model raises TypeError
  {"parameters_raw": "7000000000"} -> params_b raises TypeError ('>' on str and int)
  {"quantization": 8}           -> analyze_model raises AttributeError ('int' has no 'upper')
  ```

  `get_models()` runs `_normalize_model_entry` over every row (`:325`, `:334`) and `rank_models`
  runs `analyze_model` over every row, so one bad row takes down the whole pass rather than that row.
  This is the same class the project already fixed twice: `tests/test_hwfit_models_nonstring_fields.py`
  states "Non-strings are now treated as unknown" and pins a non-string `parameter_count` and a
  non-string `quantization`, and `tests/test_hwfit_params_b_malformed.py` pins a malformed
  `parameter_count` — but the tests only cover the fields that were fixed. The bundled catalogues and
  the two runtime caches in this checkout are clean (2,713 rows type-censused), so today this needs a
  malformed row to be introduced.
- **Impact:** a hand-edited catalogue entry, or a new row written by
  `scripts/add_hwfit_models.py` (it writes `services/hwfit/data/hf_models.json`), that carries a
  numeric `name`, a numeric `use_case`, a string `parameters_raw`/`active_parameters`/
  `context_length`, or a numeric `quantization` makes `get_models()` raise, which is the whole
  `/api/hwfit/models` response (the route calls `if not get_models()` unguarded at
  `routes/hwfit_routes.py:214`) and the whole Cookbook model list; `/api/hwfit/profiles` builds its
  catalogue from the same call. `params_b` already treats an unparseable `parameter_count` as unknown
  size for exactly this reason, so the intent is established.
- **Fix:** validate each row once at the load boundary (`_load_model_file` / `_append_models` in
  `get_models`, and the same loop for the dynamic caches): drop or coerce a non-string `name`,
  `use_case`, `quantization` or `format`, and treat a non-numeric `parameters_raw`,
  `active_parameters` or `context_length` as unknown, the way `params_b` already does. Extend
  `tests/test_hwfit_models_nonstring_fields.py` to cover the fields above.

#### [BUG] A GGUF model's fit badge is computed against total multi-GPU VRAM while the fit decision used one GPU

- **Location:** `services/hwfit/fit.py:470` (the single-GPU pool), `:551` (the budget), `:563-568` (the badge thresholds)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `analyze_model` deliberately narrows the fit pool to one GPU for GGUF and
  GGUF-tier quants, because llama.cpp cannot shard them across cards, and then computes the
  perfect/good/marginal thresholds against the *total* pool:

  ```python
  if (is_gguf or is_gguf_quant) and not preq:
      effective_vram = single_gpu_vram          # :470, single_gpu_vram = gpu_vram / gpu_count
  ...
  budget = unified_budget if unified_memory else (effective_vram if run_mode == "gpu" else available_ram)  # :551
  if required_gb > budget:                                                                    # :552
      return None
  ...
      if gpu_vram >= required_gb * 1.50:        # :563  <- total, not the pool that serves it
          fit_level = "perfect"
      elif gpu_vram >= required_gb * 1.2:
          fit_level = "good"
  ```

  Measured with a stdin probe over a synthetic GGUF entry (32B, 8,192-token context) and a fixed
  24 GB per GPU; only the number of GPUs changes, and the quant filter is the one the UI sends:

  ```text
  estimate_memory_gb(Q4_K_M, 8192) = 21.16 GB
  gpu_count=1 total=24GB (per-GPU 24GB) -> fit_level='marginal' run_mode='gpu' required_gb=21.2 per-GPU ratio=1.13x
  gpu_count=2 total=48GB (per-GPU 24GB) -> fit_level='perfect'  run_mode='gpu' required_gb=21.2 per-GPU ratio=1.13x
  gpu_count=4 total=96GB (per-GPU 24GB) -> fit_level='perfect'  run_mode='gpu' required_gb=21.2 per-GPU ratio=1.13x
  ```

  The same model on the same 24 GB card goes from `marginal` to `perfect` when a second card is
  added that the GGUF path cannot use. The comment above the block states the intent — "GPU-only fit
  must leave real allocator/KV/runtime headroom … 141 GB on a 160 GB box is runnable, but not a
  comfortable perfect fit" — and the ratio the code actually needs for `good` is 1.2×, which the
  per-GPU pool does not reach here.
- **Impact:** on a multi-GPU box the Cookbook badges a GGUF model "Perfect" while the fit decision
  that produced it used one card holding the same model at 88% of its capacity — below the 1.2× the
  same block calls "good" and far below the 1.5× it calls "perfect". The label is a function of a
  pool the fit path discarded: the same model on the same 24 GB card reads `marginal` alone and
  `perfect` with a second card added. The model still runs, so this is a misleading recommendation
  rather than a broken one, but it is systematic — every GGUF row on a 2+-GPU machine is rated
  against a pool the fit decision did not use, and `fit_level` is what the user sorts and filters
  on. Whether llama.cpp may actually spread such a model across cards depends on the serve command
  the Cookbook builds, which is outside this section; the inconsistency is inside `analyze_model`.
  Prequantized (AWQ/GPTQ/FP8) rows are unaffected, because their `effective_vram` is already the
  total.
- **Fix:** use the pool the fit decision used in the three comparisons — `effective_vram` instead of
  `gpu_vram` — so the badge and `budget` cannot disagree. The variable is already in scope and equals
  `gpu_vram` for the sharded path, so the change is local.

#### [ERROR-HANDLING] A failed image-model discovery marks its cache fresh, blanking the image list for 30 minutes

- **Location:** `services/hwfit/image_models.py:189` (with the freshness check at `:172-173`, the TTL at `:33`, and the per-collection `except: continue` at `:178-182`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** every collection fetch is individually tolerated, and the cache timestamp is written
  unconditionally afterwards, so a total failure is stored as an empty, fresh result:

  ```python
  for slug, mlx_only in [...]:
      url = f"https://huggingface.co/api/collections/{slug}"
      try:
          ...
          with urllib.request.urlopen(req, timeout=2.5) as resp:
              data = json.loads(resp.read().decode("utf-8", "replace"))
      except Exception:
          continue
      ...
  _HF_COLLECTION_CACHE["ts"] = now            # :189 — runs even when all seven fetches failed
  _HF_COLLECTION_CACHE["models"] = models
  ```

  Measured with a stdin probe that replaced `urllib.request.urlopen` with a function that always
  raises `OSError` (no real request was made):

  ```text
  get_image_models() #1 -> 0 models, 7 outbound attempts
  get_image_models() #2 -> 0 models, 0 further outbound attempts (cache treated as fresh)
  cache rows stored: 0 | TTL: 1800 s
  ```

  `IMAGE_MODEL_REGISTRY` is empty (`:14`, deliberately), so those seven collections are the only
  source of image rows, and nothing clears this cache on demand: the route's `fresh` parameter is
  passed to `detect_system` only (`routes/hwfit_routes.py:418`), and `rank_image_models` takes no
  such argument (`:453`).
- **Impact:** one transient DNS, TLS or timeout failure across all seven fetches — each with a 2.5 s
  timeout — leaves the Cookbook's image-model list empty for 30 minutes with no retry in the window,
  and the UI's Rescan cannot force one. A partial failure is handled correctly: the rows that
  succeeded are kept and the rest are skipped, which is the behaviour the sibling
  `refresh_hf_collection_models_cache` documents. The bug is only the total-failure case, where
  "nothing came back" is recorded as "this is what there is".
- **Fix:** only write `_HF_COLLECTION_CACHE["ts"]` when at least one collection returned a body (or
  store the failure count and retry sooner), and leave the previous rows in place when nothing was
  fetched. Exposing a force flag through `rank_image_models` would let the Rescan button clear it too.

#### [SECURITY] The collection fetch follows a next-page URL taken from the response's `Link` header, to any host and with no body cap

- **Location:** `services/hwfit/hf_discovery.py:286-287` (with `_next_link` at `:267-270` and the loop at `:283-285`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the pagination URL is read out of the response header and used as the next request
  URL verbatim, with no host allowlist and no redirect policy of its own:

  ```python
  while url and pages < max_pages:                       # :283
      req = urllib.request.Request(url, headers={"User-Agent": "odysseus-hwfit/1.0"})
      with urllib.request.urlopen(req, timeout=timeout) as resp:
          payload = json.load(resp)                      # :286 — no size cap
          url = _next_link(resp.headers.get("Link"))     # :287
  ...
  def _next_link(header):
      m = re.search(r'<([^>]+)>;\s*rel="next"', header)
      return m.group(1) if m else None
  ```

  Measured with a stdin probe that served the first response with
  `Link: <http://127.0.0.1:9/internal-admin-api>; rel="next"` (no real request was made):

  ```text
  pages fetched: ['https://huggingface.co/api/collections?owner=Qwen&limit=100&expand=true',
                  'http://127.0.0.1:9/internal-admin-api']
  rows: ['Qwen/Qwen3-8B']
  ```

  The second URL is fetched and its rows are merged into the catalogue that `get_models()` serves.
  The repository already owns a guarded transport for exactly this shape —
  `src/outbound_fetch.py` (private-address blocking, one-resolution-per-hop DNS pinning, redirect
  handling, body budgets), used by `services/search/content.py` — and this module does not use it.
- **Impact:** the page-2 origin is chosen by the response, so a hostile or compromised
  `huggingface.co` answer, or anything that terminates its TLS, can make the server issue up to 19
  further GETs to arbitrary URLs — loopback, link-local and RFC1918 included — and feed their JSON
  into the model catalogue, which the Cookbook then offers for download. The precondition is control
  of that HTTPS response, which is why this is low and not higher; the first request is to a fixed
  host. Independently, `json.load(resp)` buffers the body without a limit, so an oversized response
  is read into memory before anything inspects it.
- **Fix:** pin pagination to the API origin — resolve the next link with `urllib.parse.urljoin`
  against `HF_COLLECTIONS_URL` and reject a result whose scheme/host differ, or rebuild the query
  from a page/cursor field — and read the body through a capped reader (the constants and helpers in
  `src/outbound_fetch.py` are the project's own answer to both).

#### [DEAD-CODE] `_should_discover_variants` returns a literal `False`, so image-model quant-variant discovery never runs

- **Location:** `services/hwfit/image_models.py:258-259` (with its only gate at `:290`, the consumer at `:368`, and the unused seed lists at `:29-30`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the whole variant-discovery chain hangs off one function that is hardcoded off:

  ```python
  def _should_discover_variants(repo_id: str) -> bool:
      return False
  ```

  ```python
  def _merge_quant_repos(model):
      ...
      if _should_discover_variants(repo_id):                 # :290 — never true
          discovered = _discover_quant_repos(...)
  ```

  `_discover_quant_repos` is the only caller of `_best_variant_repo`, which is the only caller of
  `_hf_model_search` and `_variant_score`; `_HF_VARIANT_CACHE` (`:34`) and
  `_HF_SEARCH_DISABLED_UNTIL` (`:35`) are written only from that chain, and `HF_IMAGE_REPO_SEEDS` /
  `HF_MLX_IMAGE_REPO_SEEDS` (`:29-30`, both empty) have no reader anywhere. Measured:

  ```text
  _should_discover_variants: False
  merged quant_repos: {} | searches run: []
  ```

  Every row built by `_collection_item_to_model` starts with `"quant_repos": {}` (`:157`), so
  `rank_image_models` always reports `quant_repo = None` (`:368`), and the front end falls back to
  the base repo id for the download source (`static/js/cookbook-hwfit.js:168`, `:884`;
  `static/js/cookbookDownload.js:68`).
- **Impact:** the FP8/GGUF variant repos this code is written to find are never offered, so an image
  model that has a quantized sibling is presented with only its base repo as the download source. The
  cost is not only the missing feature: the chain is about 90 lines (`image_models.py:194-283`)
  including the module's only Hugging Face search call, its scoring heuristic and its 10-minute
  failure backoff, and the tests
  monkeypatch `_discover_quant_repos` (`tests/test_image_models_nonstring_search.py`), which reads as
  if the path were live. A literal `return False` with no comment also hides whether this is a
  deliberate kill switch or a debugging leftover.
- **Fix:** pick one. If variant discovery is retired, delete `_should_discover_variants`,
  `_discover_quant_repos`, `_best_variant_repo`, `_variant_score`, `_hf_model_search`, the two
  caches, the two empty seed lists and the `quant_repos` plumbing, and drop the now-pointless
  monkeypatches in the tests. If it is meant to be on, give the predicate a documented condition and
  a test that exercises the discovery path end to end.

## 39. services: shell, STT, TTS, faces, youtube

### Overview

`services/__init__.py`, `services/faces/__init__.py`, `services/shell/__init__.py`, `services/shell/service.py`, `services/stt/__init__.py`, `services/stt/stt_service.py`, `services/tts/__init__.py`, `services/tts/tts_service.py`, `services/youtube/__init__.py`, `services/youtube/youtube_handler.py`.

The service-layer modules behind command execution, speech and YouTube context:
`services/shell/service.py` is a standalone `ShellService` subprocess wrapper; `services/stt/stt_service.py`
and `services/tts/tts_service.py` are the multi-provider speech services (local Whisper/Kokoro, an
OpenAI-compatible `ModelEndpoint`, or the browser) plus the TTS disk cache; `services/youtube/youtube_handler.py`
does YouTube URL detection, transcript fetch, yt-dlp comment fetch and LLM context formatting;
`services/faces/__init__.py` is a one-line placeholder package; the four package `__init__` files
re-export the public names and `services/__init__.py` is the package facade.

The boundary: `routes-shell.md` owns `routes/shell_routes.py`, the live shell and code-execution
router. That router does **not** import this section's `ShellService` — the only importers are
`services/__init__.py` and `tests/test_shell_service.py` — so the child-process behaviour routes-shell
reports there belongs to a second, separate implementation; this section owns `services/shell/service.py`
itself and does not restate routes-shell's findings. `routes-rest-media-files.md` owns
`routes/tts_routes.py`, `routes/stt_routes.py` and `routes/upload_routes.py` and already reports that the
speech handlers run their blocking service calls on the request event loop (citing
`services/tts/tts_service.py:189` and `services/stt/stt_service.py:144`); that finding is not repeated
here. The chat-side callers (`src/chat_handler.py`, `src/chat_processor.py`, `src/youtube_handler.py`),
the settings store (`src/settings.py`), the `ModelEndpoint` rows the API providers read, and the router
registration in `app.py` belong to other sections and are read here only where a finding rests on them.

### Coverage

Line numbers refer to `2992bf6d368a` in the working tree; `git log --oneline -1` is `2992bf6d` and
`git status --porcelain` shows only the untracked `audit/` directory.

**Read fully:** all ten assigned files (1,101 lines): `services/tts/tts_service.py` (350),
`services/youtube/youtube_handler.py` (302), `services/stt/stt_service.py` (208),
`services/shell/service.py` (163), `services/__init__.py` (37), `services/youtube/__init__.py` (22),
`services/tts/__init__.py` (9), `services/shell/__init__.py` (6), `services/stt/__init__.py` (3),
`services/faces/__init__.py` (1). The faces package is one docstring line with no code and no importer
(`grep -rn 'services\.faces' --include='*.py' .` returns nothing outside the audit directory), so there is
nothing in it to review beyond that claim.

**Read partially:** the boundary code and callers the findings rest on — `src/chat_handler.py` at the
YouTube preprocessing loop (`:145-175`); `src/chat_processor.py` at the non-YouTube URL filter
(`:455-500`); `src/chat_helpers.py` at `extract_urls` (`:21-36`); `src/youtube_handler.py` in full
(37 lines — it replaces its own `sys.modules` entry with the canonical module); the two speech routers
`routes/stt_routes.py` and `routes/tts_routes.py` in full (57 and 87 lines); `routes/diagnostics_routes.py`
at `GET /api/test/youtube` (`:73-92`); `app.py` at the service construction and router registration
(`:556-557`, `:611-614`, `:756-763`); `src/settings.py` at `load_settings` and its cache (`:232-259`) and
at the speech defaults (`:57-65`); `src/upload_limits.py` at the STT byte cap (`:56-58`, `:64-67`);
`static/js/settings.js` at the STT and TTS forms (`:925-985`); `static/js/tts-ai.js` at the stats read
and the client-side speed application (`:47`, `:50`, `:208`, `:316-317`); `static/js/voiceRecorder.js:31`;
`specs/search.md` at the YouTube section (`:105-109`); `specs/shell-mcp.md` at the `ShellService`
description (`:7-11`, `:48`, `:139`); `requirements.txt`, `requirements-optional.txt` and `Dockerfile`
(`:20-100`) for what the project actually installs; `tests/test_shell_service.py` and
`tests/test_stt_leak.py` in full; and, for the cross-references above, the first finding of
`routes-shell.md` and the whole of `routes-rest-media-files.md`.

**Not read:** `routes/shell_routes.py` itself (another section's file — only that section's written
findings were read); `routes/diagnostics_routes.py` beyond the YouTube test route; `src/settings.py`
beyond the cited region, so the settings POST route that writes the speech keys was not read here; the
`ModelEndpoint` model and the endpoint-probe machinery (`core/database.py`, `routes/model_routes.py`)
the API-provider branches call; the `faster-whisper`, `kokoro` and `yt-dlp` implementations themselves
(none of the three is installed in this checkout, so their real load and fetch paths were exercised with
fakes only); the rest of the front end's speech UI; and every test file other than the two named above.

**Checks run:** eight URLs through the real `is_youtube_url` / `extract_youtube_id`; a peak-RSS probe of
`ShellService.execute` with `max_output=10` against an 80 MB stdout; a probe that loads the STT model
stand-in, changes the setting and calls `_get_whisper` / `get_stats`; a probe that calls the real
`get_stats()` of both speech services with the heavy imports faked to record what they construct;
`-X importtime` for `import services.stt.stt_service` against loading the same file directly by spec, and
a check that importing `src.youtube_handler` still executes `services/__init__.py`; and greps for the
`ShellService` callers, the `services.*` importers, the `is_youtube_url` callers, the `get_stt_service`
callers, and `yt-dlp` across the repository, both requirement files and the Dockerfile. The 23 suites
matching `ls tests | grep -iE 'shell|stt|tts|youtube|face|kokoro|speech|audio'` were run —
**150 passed**.

#### [BUG] A YouTube-shaped URL with no extractable video id is dropped from both the transcript path and the web-fetch path

- **Location:** `services/youtube/youtube_handler.py:61` (with `:78` and the two callers, `src/chat_handler.py:149-152` and `src/chat_processor.py:461`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** detection is a substring test while extraction requires a host and path shape, so the two
  disagree for every YouTube page that is not a video:

  ```python
  def is_youtube_url(url: str) -> bool:                          # :61
      if not isinstance(url, str):
          return False
      return "youtube.com" in url or "youtu.be" in url           # :64
  ```

  Measured on the real functions:

  ```
  True  'dQw4w9WgXcQ'        https://www.youtube.com/watch?v=dQw4w9WgXcQ
  True  None                 https://www.youtube.com/playlist?list=PL1234567890
  True  None                 https://www.youtube.com/@SomeChannel
  True  None                 https://www.youtube.com/results?search_query=python
  True  None                 https://www.youtube.com/watch
  True  None                 https://example.com/post?ref=youtube.com
  True  None                 https://notyoutube.com/watch?v=abc
  ```

  Both callers read `is_youtube_url` as "this URL is fetched as YouTube". The chat path skips the URL
  when the id is missing (`src/chat_handler.py:148-152`):

  ```python
  for url in urls:
      if is_youtube_url(url):
          video_id = extract_youtube_id(url)
          if not video_id:
              continue
  ```

  and the context builder excludes every YouTube-shaped URL from the ordinary web fetch
  (`src/chat_processor.py:460-462`):

  ```python
  urls = extract_urls(message)
  non_yt_urls = [u for u in urls if not is_youtube_url(u)]
  skip_url_fetch = len(message) > 2000 or len(non_yt_urls) > 3
  ```

  `extract_urls` (`src/chat_helpers.py:23`) matches any `http(s)` URL, so a link whose path or query
  merely contains the substring qualifies too. The file's own comment at `:72-74` names this failure
  mode for the shapes it added prefixes for — "they must be extractable or the link is silently dropped
  (neither web-fetched nor transcript-fetched) by the chat pipeline" — and playlist, channel and
  `/results` URLs are still in it.
- **Impact:** a user who shares a playlist, channel or search-results link gets neither a transcript nor
  a fetched page for it, so the link contributes nothing to the model's context; because the injected
  `YOUTUBE_INSTRUCTION_PROMPT` (`:20-30`) is only added when an id was found, the model is not told to
  work from the link either. Nothing is surfaced to the user — the failure is a silent `continue` in one
  caller and a silent exclusion in the other. The video-URL flow the feature is built around is
  unaffected, and the raw URL text still reaches the model in the user message.
- **Fix:** use extraction as the YouTube test at both call sites (`video_id = extract_youtube_id(url)`;
  treat a missing id as "not a YouTube video" and let the URL fall through to the web-fetch path), or
  give `is_youtube_url` the same host and path check `extract_youtube_id` already applies.

#### [DEPENDENCY] The comment fetch shells out to `yt-dlp`, which no requirement file or image installs

- **Location:** `services/youtube/youtube_handler.py:217` (with `_find_ytdlp` at `:39-45` and the failure branch at `:274-276`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `fetch_youtube_comments` runs `_find_ytdlp()` as the program name:

  ```python
  cmd = [
      _find_ytdlp(),
      "--skip-download",
      "--write-comments",
      "--extractor-args", f"youtube:max_comments={max_comments},all,100,0",
      "--dump-json",
      "--js-runtimes", "node",
      "--remote-components", "ejs:github",
      f"https://www.youtube.com/watch?v={video_id}",
  ]                                                              # :216-225
  ```

  and the helper falls back to the bare name (`:41-45`):

  ```python
  venv_bin = Path(sys.executable).parent / "yt-dlp"
  if venv_bin.exists():
      return str(venv_bin)
  found = shutil.which("yt-dlp")
  return found or "yt-dlp"
  ```

  Nothing installs it. `grep -rn "yt-dlp" -I .` (excluding `venv/`) returns only this file and its tests;
  the string appears in neither `requirements.txt` nor `requirements-optional.txt`, in no `apt-get
  install` list, and nowhere else in the `Dockerfile`. Measured here:

  ```
  $ ls venv/bin/yt-dlp
  ls: cannot access 'venv/bin/yt-dlp': No such file or directory
  $ venv/bin/python -c "import importlib.metadata as m; m.version('yt-dlp')"
  PackageNotFoundError: No package metadata was found for yt-dlp
  ```

  The Dockerfile installs nodejs, npm, chromium and tmux from apt (`:23-37`) and runs exactly two
  `pip install`s from the requirement files plus `python-magic` (`:78`, `:84`), so the shipped image has
  no yt-dlp either. The absence is caught and returned as a value rather than raised (`:274-276`):

  ```python
  except FileNotFoundError:
      logger.warning("yt-dlp not installed — cannot fetch comments")
      return {"success": False, "error": "yt-dlp not installed", "comments": []}
  ```
- **Impact:** on the container image and on any host that installed `requirements.txt`, the "Audience
  Reception" half of the YouTube breakdown never runs: `format_comments_for_context` returns `""` for a
  failed fetch (`:283-285`), so the context carries the transcript only, and the operator sees a warning
  in the log rather than a broken request. `requirements-optional.txt` is the project's declared home for
  feature extras — it lists `faster-whisper`, `kokoro`, `ddgs`, `PyMuPDF` and `markitdown` under the note
  "The app handles their absence gracefully" — and yt-dlp is not there, so nothing in the repository
  tells an operator the binary is needed. Nothing pins its version either, so the flags the command uses
  are the only record of what it expects.
- **Fix:** add `yt-dlp` to `requirements-optional.txt` with a one-line feature note (or install it in the
  image), name the binary in the module docstring, and state the version floor the flags assume.

#### [BUG] The STT model setting has no effect once a model is loaded, and `/api/stt/stats` reports the new name as loaded

- **Location:** `services/stt/stt_service.py:58` (with `:66-67`, `:186`, `:191-192`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_get_whisper` reads the setting only inside the one-time load:

  ```python
  def _get_whisper(self):                        # :58
      if self._whisper_model is None:            # :59
          ...
          settings = self._load_settings()       # :66
          model_size = settings.get("stt_model", "base")   # :67
          ...
          self._whisper_model = WhisperModel(model_size, device=device, compute_type=compute_type)  # :83
  ```

  while `get_stats` reports the current setting and the cached model's presence as though they agreed:

  ```python
  "model": settings["stt_model"],                # :186
  ...
  whisper = self._get_whisper()                  # :191
  stats["model_loaded"] = whisper is not None    # :192
  ```

  Measured with a model stand-in already loaded and the setting changed to `large-v3`:

  ```
  settings now say stt_model = large-v3
  _get_whisper() returns the previously loaded object: True
  get_stats() -> {'provider': 'local', 'model': 'large-v3', 'model_loaded': True, 'available': True}
  ```

  The settings UI posts the change on every select and input change and reports success
  (`static/js/settings.js:958`, message "Saved") with no restart note, and nothing resets the service:
  `grep -rn 'get_stt_service\|_stt_service' routes/ src/ app.py` finds only `app.py:760-761`. The settings
  store is not the cause — `load_settings` re-reads the file after a two-second cache
  (`src/settings.py:236-247`).
- **Impact:** an operator who switches the local STT model in the UI keeps transcribing with the model
  loaded at first use until the process restarts, and the status the UI reads names the new model with
  `model_loaded: true`, so the misreport is the only feedback. Changing the model before the first
  transcription does load the new one, so the failure needs one prior transcription. Local STT only:
  the endpoint branch reads `stt_model` per call and passes it to the API request (`:161`, `:171`).
- **Fix:** record which model was loaded and reload when the setting differs (or expose an explicit
  reload and call it from the settings save); at minimum report the loaded name rather than the
  configured one.

#### [PERF] `GET /api/stt/stats` and `GET /api/tts/stats` load the local model as a side effect of a read

- **Location:** `services/stt/stt_service.py:191` (with `:51`, and `services/tts/tts_service.py:261`, `:274`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `get_stats` reaches the loader through `available` and then again for the counter:

  ```python
  if provider == "local":
      return self._get_whisper() is not None     # services/stt/stt_service.py:51
  ...
  "available": self.available and stt_enabled,   # :184
  ...
  if provider == "local":
      whisper = self._get_whisper()              # :191
      stats["model_loaded"] = whisper is not None
  ```

  `_get_whisper` constructs `WhisperModel(...)` (`:83`), which loads the checkpoint — and fetches it first
  when that size is not cached, which this checkout could not exercise because `faster-whisper` is not
  installed;
  `TTSService.get_stats` does the same through `_get_kokoro()` → `_KokoroPipeline()`
  (`services/tts/tts_service.py:154-157`, `:287-291`), whose `_init` imports `torch` and `kokoro` and
  loads Kokoro-82M onto the GPU (`:293-308`). Both stats handlers are `async def` and call the service
  directly (`routes/stt_routes.py:18-22`, `routes/tts_routes.py:24-28`), so the load runs on the request
  event loop. Measured by calling the real `get_stats()` with the heavy imports faked so the construction
  is visible:

  ```
  get_stats() -> {'provider': 'local', 'model': 'Kokoro-82M (GPU)', 'available': True, 'ready': True}
  side effects: ['_KokoroPipeline() constructed']
  STT get_stats() -> {'provider': 'local', 'model': 'base', 'model_loaded': True}
  side effects: ["WhisperModel('base', device='cpu')"]
  ```

  Both UIs call these endpoints as soon as the speech surface loads: `static/js/tts-ai.js:47` and
  `static/js/voiceRecorder.js:31`. This is the same blocking-call class as the second finding in
  `routes-rest-media-files.md`, which cites the synthesize and transcribe calls
  (`services/tts/tts_service.py:189`, `services/stt/stt_service.py:144`); the stats path is a different
  endpoint and a different trigger — a read that can start a model download.
- **Impact:** the first `/api/stt/stats` or `/api/tts/stats` after a restart can hold the event loop for
  the length of a model load — and, for a size not already cached, its download (hundreds of MB for
  Kokoro-82M, a Whisper checkpoint for STT) — with no
  progress reported and no bound, stalling unrelated requests on the worker. The load would otherwise
  happen at the first transcription, so the total cost is moved rather than added; what changes is that a
  status read now pays it. Only the `local` provider is affected — the `browser` and `endpoint:` branches
  of both `get_stats` methods touch no model (`services/stt/stt_service.py:190-196`,
  `services/tts/tts_service.py:273-278`).
- **Fix:** answer the stats read without loading — derive `model_loaded` from the cached instance
  (`self._whisper_model is not None`, `self._kokoro is not None`) and let `available` for `local` mean the
  library imports — or run the load off the loop with `asyncio.to_thread` and report a loading state.

#### [PERF] `ShellService.execute` buffers the whole command output before applying `max_output`

- **Location:** `services/shell/service.py:62-66`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `communicate()` reads both pipes to EOF into memory and the cap is applied to the decoded
  string afterwards:

  ```python
  stdout_b, stderr_b = await asyncio.wait_for(
      proc.communicate(), timeout=timeout
  )
  stdout = stdout_b.decode(errors="replace")[:self.max_output]
  stderr = stderr_b.decode(errors="replace")[:self.max_output]
  ```

  `specs/shell-mcp.md:48` describes this class as "a small standalone subprocess abstraction with output
  caps". Measured with `max_output=10` against a command printing 80 MB:

  ```
  max_output: 10
  returned stdout length: 10
  exit_code: 0
  peak RSS before 99.5 MB -> after 252.1 MB (delta 152.6 MB)
  ```

  The `decode` allocates a second copy of the buffer before the slice. The `stream` generator
  (`:88-163`) has the same property in a different shape: it queues decoded lines into an unbounded
  `asyncio.Queue` for as long as the consumer reads.
- **Impact:** the cap limits what the caller sees, not what the process holds, so a command that emits a
  gigabyte drives the server's peak RSS to roughly the size of its output and can get the whole app
  OOM-killed — the outcome the cap reads as preventing. Nothing calls this class today (next finding), so
  it is a hazard for whoever wires it up rather than a live failure.
- **Fix:** stop reading once the cap is reached — `await proc.stdout.read(max_output + 1)` per stream with
  the process killed when either exceeds it — or drop `max_output` in favour of a documented caller-side
  bound.

#### [DEAD-CODE] `ShellService` has no caller, and the shell it offers has no policy behind the "safe" wording

- **Location:** `services/shell/service.py:19` (with `:56-61` and `services/__init__.py:15`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the only references to the class are its definition, the two re-exports, and one test:

  ```
  $ grep -rn "ShellService" --include=*.py . | grep -v venv/
  ./services/__init__.py:15:from .shell import ShellService, ShellResult
  ./services/__init__.py:35:    "ShellService",
  ./services/shell/__init__.py:4:from .service import ShellService, ShellResult
  ./services/shell/__init__.py:6:__all__ = ["ShellService", "ShellResult"]
  ./services/shell/service.py:19:class ShellService:
  ./services/shell/service.py:24:        service = ShellService()
  ./tests/test_shell_service.py:10:ShellService = shell_service.ShellService
  ./tests/test_shell_service.py:51:        service = ShellService()
  ```

  The two `__all__` entries, the docstring example at `services/shell/service.py:24` and the test
  assignment are not callers, so the live-caller set is empty. The live shell path is
  `routes/shell_routes.py`'s own `_create_shell`/`_exec_shell` (reviewed in `routes-shell.md`). The one
  test constructs the class and drives `stream` with a fake process (`tests/test_shell_service.py:36-59`);
  `execute` has no test at all. `specs/shell-mcp.md` records the
  status: `:48` says it "does not own live route behavior", and `:139` calls `services.shell.service`
  "a transitional/simple facade". What the unreachable implementation offers is the unguarded form:

  ```python
  proc = await asyncio.create_subprocess_shell(
      command,
      stdout=asyncio.subprocess.PIPE,
      stderr=asyncio.subprocess.PIPE,
      cwd=cwd,
  )                                              # :56-61
  ```

  an arbitrary command string, a caller-supplied `cwd` (`:52`), and no allowlist, policy, admin check or
  workspace confinement — under a module docstring that reads "Shell service — safe command execution."
- **Impact:** two implementations of the same job, where the one a reader finds first by name advertises
  safety it does not implement: a future caller that imports `ShellService` instead of the route layer
  gets none of the guards `routes-shell.md` documents (admin gating, workspace confinement, output
  handling). Nothing is exploitable today because nothing calls it.
- **Fix:** delete the class, its re-exports and its test if no caller is planned, or state the missing
  policy in the docstring and point callers at the route layer. The "safe" wording in the module docstring
  and `specs/shell-mcp.md`'s "output caps" are the parts that mislead.

#### [PERF] `services/__init__.py` makes every `services.*` import load five packages

- **Location:** `services/__init__.py:11-15`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the facade imports all five service packages eagerly:

  ```python
  from .search import SearchService, SearchResult, SearchResponse
  from .docs import DocsService, DocChunk, IndexResult
  from .research import ResearchService, ResearchResult, ResearchSource
  from .memory import MemoryService, Memory, MemorySearchResult
  from .shell import ShellService, ShellResult
  ```

  Python executes a package's `__init__` before any submodule import, so `import
  services.stt.stt_service` — a leaf whose only third-party import is `httpx` — loads all of them.
  Measured in this checkout:

  ```
  $ venv/bin/python -c "<time import services.stt.stt_service>"
  package import: 537.1 ms, 23 services.* modules loaded
  package import: 435.3 ms, 23 services.* modules loaded
  package import: 502.3 ms, 23 services.* modules loaded
  $ venv/bin/python -c "<load services/stt/stt_service.py by spec, no parent package>"
  direct file load: 57.9 ms
  direct file load: 47.6 ms
  direct file load: 52.9 ms
  $ venv/bin/python -X importtime -c "import services.stt.stt_service"
  import time:       163 |     452856 |         services.search.core
  import time:        65 |     508742 |   services.stt
  ```

  The search stack is the bulk of it: `services.search.core` alone is 453 of the 509 ms in the
  `services.stt` subtree.

  `src/youtube_handler.py:20-21` states the opposite intent — "Import the canonical module directly
  (services.youtube.youtube_handler) without triggering the heavy services/__init__.py top-level
  imports" — and that comment is wrong: `importlib.import_module("services.youtube.youtube_handler")`
  runs the parent package's `__init__` like any other import. Measured: immediately after `import
  src.youtube_handler` in a fresh interpreter, `'services.docs' in sys.modules` is `True`.
- **Impact:** every process, script and test that imports one service pays for all five (0.4-0.5 s here,
  dominated by the search stack), and a heavy or optional dependency added to any service package
  silently becomes a dependency of every other one — which is exactly what the shim comment says is being
  avoided. No breakage today: the modules loaded this way pull in no optional import at module level
  (`chromadb`, `torch`, `faster_whisper` and `kokoro` are all absent from `sys.modules` after the import).
- **Fix:** drop the eager re-exports from `services/__init__.py` (leave the docstring) or expose them
  lazily through a module `__getattr__`, and correct the comment in `src/youtube_handler.py`.

## 40. static: image editor

### Overview

`static/js/editor/ai-inpaint.js`, `static/js/editor/ai-models.js`, `static/js/editor/ai-rembg.js`, `static/js/editor/ai-tool-runner.js`, `static/js/editor/ai-tools-misc.js`, `static/js/editor/build/controls.js`, `static/js/editor/build/popups.js`, `static/js/editor/build/right-panel.js`, `static/js/editor/build/toolbar.js`, `static/js/editor/build/topbar.js`, `static/js/editor/build/transform-popup.js`, `static/js/editor/canvas-coords.js`, `static/js/editor/canvas-events.js`, `static/js/editor/canvas-transforms.js`, `static/js/editor/checkerboard.js`, `static/js/editor/clipboard-and-drop.js`, `static/js/editor/composite-helpers.js`, `static/js/editor/filters/blur.js`, `static/js/editor/filters/edge-feather.js`, `static/js/editor/fx/adj-popup.js`, `static/js/editor/fx/filter-string.js`, `static/js/editor/fx/histogram.js`, `static/js/editor/fx/pixel-pass.js`, `static/js/editor/harmonize-masks.js`, `static/js/editor/history-panel.js`, `static/js/editor/keyboard-shortcuts.js`, `static/js/editor/layer-helpers.js`, `static/js/editor/layer-panel.js`, `static/js/editor/mask-utils.js`, `static/js/editor/shortcuts-popover.js`, `static/js/editor/slider-ux.js`, `static/js/editor/snap.js`, `static/js/editor/state.js`, `static/js/editor/stroke-pipeline.js`, `static/js/editor/stroke-tool-sliders.js`, `static/js/editor/tools/clone.js`, `static/js/editor/tools/crop.js`, `static/js/editor/tools/flood-fill.js`, `static/js/editor/tools/lasso-mask.js`, `static/js/editor/tools/lasso.js`, `static/js/editor/tools/move.js`, `static/js/editor/tools/stroke.js`, `static/js/editor/tools/transform-drag.js`, `static/js/editor/tools/transform-handles.js`, `static/js/editor/tools/transform-session.js`, `static/js/editor/tools/wand.js`, `static/js/editor/wire-import.js`, `static/js/editor/wire-inpaint-controls.js`, `static/js/editor/wire-merge-buttons.js`, `static/js/editor/wire-selection-controls.js`, `static/js/editor/wire-topbar-menus.js`, `static/js/editor/wire-topbar-overflow.js`, `static/js/editor/wire-topbar.js`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 41. static: model comparison UI

### Overview

`static/js/compare/icons.js`, `static/js/compare/index.js`, `static/js/compare/models.js`, `static/js/compare/panes.js`, `static/js/compare/probe.js`, `static/js/compare/scoreboard.js`, `static/js/compare/selector.js`, `static/js/compare/state.js`, `static/js/compare/stream.js`, `static/js/compare/vote.js`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 42. static: chat, sessions and composer UI

### Overview

`static/js/assistant.js`, `static/js/chat.js`, `static/js/chatModelProvenance.js`, `static/js/chatRenderer.js`, `static/js/chatStream.js`, `static/js/chatStreamErrors.js`, `static/js/composerArrowUpRecall.js`, `static/js/liveThinkingThrottle.js`, `static/js/sessions.js`, `static/js/slashAutocomplete.js`, `static/js/slashCommands.js`, `static/js/streamingRenderer.js`, `static/js/streamingSegmenter.js`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 43. static: documents, notes, email, calendar UI

### Overview

`static/js/calendar.js`, `static/js/calendar/reminders.js`, `static/js/calendar/utils.js`, `static/js/document.js`, `static/js/documentLibrary.js`, `static/js/emailInbox.js`, `static/js/emailLibrary.js`, `static/js/emailLibrary/replyRecipients.js`, `static/js/emailLibrary/signatureFold.js`, `static/js/emailLibrary/state.js`, `static/js/emailLibrary/utils.js`, `static/js/emailShared.js`, `static/js/gallery.js`, `static/js/galleryEditor.js`, `static/js/notes.js`, `static/js/signature.js`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 44. static: cookbook, settings, models UI

### Overview

`static/js/admin.js`, `static/js/cookbook-deps-recipes.js`, `static/js/cookbook-diagnosis.js`, `static/js/cookbook-hwfit.js`, `static/js/cookbook.js`, `static/js/cookbookDownload.js`, `static/js/cookbookPorts.js`, `static/js/cookbookProgressSignal.js`, `static/js/cookbookRunning.js`, `static/js/cookbookSchedule.js`, `static/js/cookbookServe.js`, `static/js/model/matchKey.js`, `static/js/modelPicker.js`, `static/js/modelSort.js`, `static/js/models.js`, `static/js/presets.js`, `static/js/providerDeviceFlow.js`, `static/js/providers.js`, `static/js/settings/dom.js`, `static/js/settings/lifecycle.js`, `static/js/settings/navigation.js`, `static/js/settings/registry.js`, `static/js/settings/search.js`, `static/js/settings/sidebar.js`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 45. static: research, memory and search UI

### Overview

`static/js/memory.js`, `static/js/rag.js`, `static/js/research/jobs.js`, `static/js/research/panel.js`, `static/js/researchSynapse.js`, `static/js/search-chat.js`, `static/js/search.js`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 46. static: remaining first-party JS

### Overview

`static/js/MODULE_SUMMARY.md`, `static/js/a11y.js`, `static/js/appConfig.js`, `static/js/censor.js`, `static/js/codeRunner.js`, `static/js/color/hex.js`, `static/js/colorPicker.js`, `static/js/dragSort.js`, `static/js/emojiPicker.js`, `static/js/emojiShortcodes.js`, `static/js/escMenuStack.js`, `static/js/fileHandler.js`, `static/js/group.js`, `static/js/init.js`, `static/js/keyboard-shortcuts.js`, `static/js/langIcons.js`, `static/js/markdown.js`, `static/js/markdown/tableRow.js`, `static/js/modalManager.js`, `static/js/modalSnap.js`, `static/js/package.json`, `static/js/panels.js`, `static/js/platform.js`, `static/js/section-management.js`, `static/js/settings.js`, `static/js/sidebar-layout.js`, `static/js/skills.js`, `static/js/spinner.js`, `static/js/startupShell.js`, `static/js/storage.js`, `static/js/tasks.js`, `static/js/theme.js`, `static/js/tileManager.js`, `static/js/toolWindowZOrder.js`, `static/js/tourAutoplay.js`, `static/js/tourHints.js`, `static/js/tts-ai.js`, `static/js/ui.js`, `static/js/ui_visibility.js`, `static/js/util/ordinal.js`, `static/js/voiceRecorder.js`, `static/js/windowDrag.js`, `static/js/windowResize.js`, `static/js/workspace.js`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 47. static: vendored libraries, fonts, icons, CSS

### Overview

`static/app.js`, `static/fonts/FiraCode-Light.woff2`, `static/fonts/FiraCode-Regular.woff2`, `static/fonts/FiraCode-SemiBold.woff2`, `static/fonts/Inter-Medium.woff2`, `static/fonts/Inter-Regular.woff2`, `static/fonts/Inter-SemiBold.woff2`, `static/fonts/OpenDyslexic-Bold.woff2`, `static/fonts/OpenDyslexic-Regular.woff2`, `static/fonts/custom/GohuFont.ttf`, `static/icon.ico`, `static/icons/icon-192.png`, `static/icons/icon-512.png`, `static/icons/icon-maskable-512.png`, `static/icons/ollama-mark-crop.png`, `static/icons/ollama-mark.png`, `static/icons/sglang-logo.png`, `static/icons/sglang-mark.png`, `static/index.html`, `static/lib/docx.umd.min.js`, `static/lib/highlight.min.js`, `static/lib/html2pdf.bundle.min.js`, `static/lib/katex/fonts/KaTeX_AMS-Regular.woff2`, `static/lib/katex/fonts/KaTeX_Caligraphic-Bold.woff2`, `static/lib/katex/fonts/KaTeX_Caligraphic-Regular.woff2`, `static/lib/katex/fonts/KaTeX_Fraktur-Bold.woff2`, `static/lib/katex/fonts/KaTeX_Fraktur-Regular.woff2`, `static/lib/katex/fonts/KaTeX_Main-Bold.woff2`, `static/lib/katex/fonts/KaTeX_Main-BoldItalic.woff2`, `static/lib/katex/fonts/KaTeX_Main-Italic.woff2`, `static/lib/katex/fonts/KaTeX_Main-Regular.woff2`, `static/lib/katex/fonts/KaTeX_Math-BoldItalic.woff2`, `static/lib/katex/fonts/KaTeX_Math-Italic.woff2`, `static/lib/katex/fonts/KaTeX_SansSerif-Bold.woff2`, `static/lib/katex/fonts/KaTeX_SansSerif-Italic.woff2`, `static/lib/katex/fonts/KaTeX_SansSerif-Regular.woff2`, `static/lib/katex/fonts/KaTeX_Script-Regular.woff2`, `static/lib/katex/fonts/KaTeX_Size1-Regular.woff2`, `static/lib/katex/fonts/KaTeX_Size2-Regular.woff2`, `static/lib/katex/fonts/KaTeX_Size3-Regular.woff2`, `static/lib/katex/fonts/KaTeX_Size4-Regular.woff2`, `static/lib/katex/fonts/KaTeX_Typewriter-Regular.woff2`, `static/lib/katex/katex.min.css`, `static/lib/katex/katex.min.js`, `static/lib/mammoth.browser.min.js`, `static/lib/mermaid.min.js`, `static/lib/qrcode.min.js`, `static/lib/xlsx.full.min.js`, `static/login.html`, `static/manifest.json`, `static/modal-control-variants.html`, `static/style.css`, `static/sw.js`, `static/wave-variants.html`, `static/whirlpool-variants.html`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 48. Bundled MCP servers

### Overview

`mcp_servers/__init__.py`, `mcp_servers/email_server.py`, `mcp_servers/image_gen_server.py`, `mcp_servers/memory_server.py`, `mcp_servers/rag_server.py`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 49. Companion apps and Swift clients

### Overview

`companion/README.md`, `companion/__init__.py`, `companion/pairing.py`, `companion/routes.py`, `integrations/claude/README.md`, `integrations/claude/skills/odysseus/SKILL.md`, `integrations/claude/skills/odysseus/scripts/odysseus_api.py`, `integrations/codex/.codex-plugin/plugin.json`, `integrations/codex/README.md`, `integrations/codex/scripts/odysseus_api.py`, `integrations/codex/skills/odysseus/SKILL.md`, `swift/odysseus-mlx-image-bridge/Package.swift`, `swift/odysseus-mlx-image-bridge/Sources/OdysseusMLXColorize/main.swift`, `swift/odysseus-mlx-image-bridge/Sources/OdysseusMLXInpaint/main.swift`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 50. Project website

### Overview

`website/_config.yml`, `website/agent-migration.md`, `website/attachments.md`, `website/backup-restore.md`, `website/bg.webm`, `website/chat.webm`, `website/compare.webm`, `website/document.webm`, `website/email-outlook.md`, `website/gallery.webm`, `website/index.html`, `website/notes.webm`, `website/pr-blocker-audit.md`, `website/research.webm`, `website/security-ci.md`, `website/setup.md`, `website/theme.webm`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 51. tests: harness, standards and helpers

### Overview

`tests/LAYOUT_INVENTORY.md`, `tests/OVERSIZED_TEST_SPLIT_PLAN.md`, `tests/README.md`, `tests/TESTING_STANDARD.md`, `tests/_taxonomy.py`, `tests/cli/test_calendar_cli_name.py`, `tests/cli/test_contacts_cli_rows.py`, `tests/cli/test_cookbook_cli_state.py`, `tests/cli/test_docs_cli_content_length.py`, `tests/cli/test_gallery_cli_album_count.py`, `tests/cli/test_gallery_cli_preview.py`, `tests/cli/test_logs_cli_resolve_nonstring.py`, `tests/cli/test_mail_cli_read_empty_fetch.py`, `tests/cli/test_mail_cli_recipients.py`, `tests/cli/test_mcp_cli_env_serialize.py`, `tests/cli/test_mcp_cli_json.py`, `tests/cli/test_memory_cli_rows.py`, `tests/cli/test_notes_cli_items.py`, `tests/cli/test_personal_cli_rows.py`, `tests/cli/test_preset_cli_invalid_entries.py`, `tests/cli/test_preset_cli_set_corrupt_entry.py`, `tests/cli/test_preset_cli_store.py`, `tests/cli/test_research_cli_preview.py`, `tests/cli/test_research_cli_status.py`, `tests/cli/test_research_cli_status_filter.py`, `tests/cli/test_research_cli_store.py`, `tests/cli/test_sessions_cli.py`, `tests/cli/test_signature_cli_export.py`, `tests/cli/test_skills_cli_preview.py`, `tests/cli/test_skills_cli_rows.py`, `tests/cli/test_tasks_cli_preview.py`, `tests/cli/test_theme_cli_store.py`, `tests/cli/test_webhook_cli_mask.py`, `tests/conftest.py`, `tests/helpers/__init__.py`, `tests/helpers/calendar_routes.py`, `tests/helpers/cli_loader.py`, `tests/helpers/db_stubs.py`, `tests/helpers/embedding_lanes.py`, `tests/helpers/import_state.py`, `tests/helpers/sqlite_db.py`, `tests/helpers/test_settings_shell.js`, `tests/helpers/test_settings_shell_coordinator.mjs`, `tests/run_focus.py`, `tests/run_order_report.py`, `tests/streaming/corpus.mjs`, `tests/streaming/invariant.test.mjs`, `tests/streaming/markdownHarness.mjs`, `tests/streaming/segmenter.test.mjs`, `tests/tools/build_oversized_test_split_plan.py`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 52. tests: security, guard and prompt-injection

### Overview

`tests/test_auth_config_lock_concurrency.py`, `tests/test_auth_disabled_document_access.py`, `tests/test_auth_event_loop.py`, `tests/test_auth_policy.py`, `tests/test_auth_regressions.py`, `tests/test_auth_require_privilege_nondict.py`, `tests/test_auth_root_path.py`, `tests/test_auth_session_revocation.py`, `tests/test_db_stubs_helper.py`, `tests/test_is_youtube_url_nonstring.py`, `tests/test_is_youtube_url_nonstring_svc.py`, `tests/test_pr_blocker_audit.py`, `tests/test_pr_description_check.py`, `tests/test_prompt_injection_audit.py`, `tests/test_prompt_security.py`, `tests/test_security_headers_middleware.py`, `tests/test_security_headers_pdf_preview.py`, `tests/test_security_regressions.py`, `tests/test_token_cache_atomic_swap.py`, `tests/test_vault_password_not_in_argv.py`, `tests/test_vault_routes_shim.py`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 53. tests: email, calendar and webhooks

### Overview

`tests/test_ai_image_url_safety.py`, `tests/test_ai_interaction_owner_scope.py`, `tests/test_caldav_bidirectional_sync.py`, `tests/test_caldav_client_cleanup.py`, `tests/test_caldav_google_principal_url.py`, `tests/test_caldav_prune_parse_failure.py`, `tests/test_caldav_redirect_hardening.py`, `tests/test_caldav_sync_prune_local_events.py`, `tests/test_caldav_sync_uid_scope.py`, `tests/test_caldav_test_connection_ssl.py`, `tests/test_caldav_url_hardening.py`, `tests/test_caldav_url_nonstring.py`, `tests/test_caldav_writeback.py`, `tests/test_caldav_writeback_route.py`, `tests/test_calendar_batch_events.py`, `tests/test_calendar_cli_overlap.py`, `tests/test_calendar_css_url_escape_js.py`, `tests/test_calendar_default_transaction.py`, `tests/test_calendar_event_contrast.py`, `tests/test_calendar_import_zero_duration.py`, `tests/test_calendar_list_range_aliases.py`, `tests/test_calendar_owner_scope.py`, `tests/test_calendar_parse_dt_naive.py`, `tests/test_calendar_parse_dt_time_first.py`, `tests/test_calendar_parse_dt_tonight.py`, `tests/test_calendar_recurrence.py`, `tests/test_calendar_reminder_minutes_parsing.py`, `tests/test_calendar_rrule.py`, `tests/test_calendar_rrule_until_utc.py`, `tests/test_calendar_update_event_tz.py`, `tests/test_calendar_utils_dates_js.py`, `tests/test_contacts_add_null_name.py`, `tests/test_contacts_carddav_security.py`, `tests/test_contacts_import_nonstring.py`, `tests/test_contacts_routes_shim.py`, `tests/test_contacts_vcard_parse.py`, `tests/test_diagnostics_logs.py`, `tests/test_diagnostics_service_route.py`, `tests/test_email_account_default_serialization.py`, `tests/test_email_account_port_validation.py`, `tests/test_email_decode_header.py`, `tests/test_email_envelope_recipients.py`, `tests/test_email_fallback_reconnect.py`, `tests/test_email_gmail_fetch_flags.py`, `tests/test_email_helpers_decode_header_spaces.py`, `tests/test_email_imap_timeout.py`, `tests/test_email_library_bulk_actions.py`, `tests/test_email_library_prewarm.py`, `tests/test_email_linkify_security_js.py`, `tests/test_email_oauth.py`, `tests/test_email_oauth_connect_smtp_security.py`, `tests/test_email_oauth_docker_config.py`, `tests/test_email_oauth_settings_redirect.py`, `tests/test_email_open_dedup_js.py`, `tests/test_email_owner_scope.py`, `tests/test_email_ownerless_account_owner_scope.py`, `tests/test_email_polly_imap_leak.py`, `tests/test_email_read_mark_seen.py`, `tests/test_email_registry_sync.py`, `tests/test_email_send_only_no_inbox.py`, `tests/test_email_smtp_security.py`, `tests/test_email_split_border_css.py`, `tests/test_email_summary_error_ui_js.py`, `tests/test_email_summary_llm.py`, `tests/test_email_test_connection_oauth.py`, `tests/test_email_thread_parser_nonstring.py`, `tests/test_email_uid_no_seqno_fallback.py`, `tests/test_email_unsubscribe_candidates.py`, `tests/test_email_urgency_checkpoint.py`, `tests/test_ics_escape.py`, `tests/test_ics_export_escaping.py`, `tests/test_ics_import_dedup_tz.py`, `tests/test_imap_leak_fixes.py`, `tests/test_imap_mailbox_quoting.py`, `tests/test_imap_move_uid.py`, `tests/test_imap_uid_commands.py`, `tests/test_web_fetch_plaintext.py`, `tests/test_web_fetch_size_caps.py`, `tests/test_web_search_query_sanitization.py`, `tests/test_web_search_raw_json_tool_call.py`, `tests/test_web_search_time_filter.py`, `tests/test_web_search_tool_icon_js.py`, `tests/test_web_user_agent_constant.py`, `tests/test_webhook_dns_rebinding_pin.py`, `tests/test_webhook_emitters_use_manager.py`, `tests/test_webhook_routes_shim.py`, `tests/test_webhook_sanitize_error_ipv6.py`, `tests/test_webhook_ssrf_resilience.py`, `tests/test_webhook_task_refs.py`, `tests/test_webhook_trigger_auth_exempt.py`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 54. tests: cookbook, models and providers

### Overview

`tests/test_cookbook_agent_tool_ssh_validation.py`, `tests/test_cookbook_cpu_only_serve.py`, `tests/test_cookbook_dead_download_status.py`, `tests/test_cookbook_dependency_completion_regression.py`, `tests/test_cookbook_deps_recipes.py`, `tests/test_cookbook_diagnosis.py`, `tests/test_cookbook_diagnosis_js.py`, `tests/test_cookbook_docker_access.py`, `tests/test_cookbook_download_toast_duration.py`, `tests/test_cookbook_endpoint_registration.py`, `tests/test_cookbook_error_feedback.py`, `tests/test_cookbook_error_tail_lines.py`, `tests/test_cookbook_gemma4_thinking_template.py`, `tests/test_cookbook_helpers.py`, `tests/test_cookbook_hf_token.py`, `tests/test_cookbook_local_serve_pid_winpid.py`, `tests/test_cookbook_package_detection.py`, `tests/test_cookbook_port_parsing_js.py`, `tests/test_cookbook_progress_signal_js.py`, `tests/test_cookbook_remote_windows_diffusers.py`, `tests/test_cookbook_same_host_server_profiles_js.py`, `tests/test_cookbook_serve_lifecycle.py`, `tests/test_cookbook_windows_stop_tree_js.py`, `tests/test_embedding_cache_confinement.py`, `tests/test_embedding_endpoint_config.py`, `tests/test_embedding_lane_ndarray_restore.py`, `tests/test_embedding_lanes.py`, `tests/test_embedding_lanes_legacy.py`, `tests/test_embedding_lanes_memory.py`, `tests/test_embedding_lanes_rag.py`, `tests/test_embedding_lanes_tool_index.py`, `tests/test_embeddings.py`, `tests/test_embeddings_client.py`, `tests/test_endpoint_owner_scope_followup.py`, `tests/test_endpoint_probing.py`, `tests/test_endpoint_resolver_headers.py`, `tests/test_endpoint_resolver_models.py`, `tests/test_endpoint_resolver_urls.py`, `tests/test_gpu_compose_standalone.py`, `tests/test_hwfit_amd.py`, `tests/test_hwfit_apple_bandwidth.py`, `tests/test_hwfit_bandwidth_nonstring.py`, `tests/test_hwfit_container_visibility_warning.py`, `tests/test_hwfit_cpu_arch_detection.py`, `tests/test_hwfit_cpu_only_fallback.py`, `tests/test_hwfit_gemma4_12b.py`, `tests/test_hwfit_gpu_count_nonnumeric.py`, `tests/test_hwfit_macos.py`, `tests/test_hwfit_manual_backend.py`, `tests/test_hwfit_models_nonstring_fields.py`, `tests/test_hwfit_native_quant_labels.py`, `tests/test_hwfit_params_b_malformed.py`, `tests/test_hwfit_quant_formats.py`, `tests/test_hwfit_remote_validation.py`, `tests/test_hwfit_unified_nvidia.py`, `tests/test_hwfit_windows.py`, `tests/test_llm_core_anthropic_cache.py`, `tests/test_llm_core_anthropic_temp_clamp.py`, `tests/test_llm_core_anthropic_temp_omit.py`, `tests/test_llm_core_async_mistral_content.py`, `tests/test_llm_core_concurrency.py`, `tests/test_llm_core_connect_timeout.py`, `tests/test_llm_core_fallback.py`, `tests/test_llm_core_mistral_content.py`, `tests/test_llm_core_ollama.py`, `tests/test_llm_core_ollama_thinking.py`, `tests/test_llm_core_openai_reasoning_tools.py`, `tests/test_llm_core_reasoning.py`, `tests/test_llm_core_reasoning_content_fallback.py`, `tests/test_llm_core_sanitize_tool_calls.py`, `tests/test_llm_core_sse_no_space.py`, `tests/test_llm_core_streaming.py`, `tests/test_llm_core_system_msg_missing_content.py`, `tests/test_llm_core_temperature_anthropic.py`, `tests/test_llm_core_temperature_moonshot.py`, `tests/test_llm_core_temperature_reasoning.py`, `tests/test_llm_core_thinking_models.py`, `tests/test_llm_core_usage_finish_delta.py`, `tests/test_model_capabilities.py`, `tests/test_model_capability_readers.py`, `tests/test_model_context.py`, `tests/test_model_defaults.py`, `tests/test_model_discovery_status.py`, `tests/test_model_helper_owner_scope.py`, `tests/test_model_interaction_registry.py`, `tests/test_model_name_tooltip.py`, `tests/test_model_routes.py`, `tests/test_model_sort_js.py`, `tests/test_provider_classification.py`, `tests/test_provider_classification_errors.py`, `tests/test_provider_classification_token_params.py`, `tests/test_provider_detection_builders.py`, `tests/test_provider_detection_detect.py`, `tests/test_provider_detection_host_match.py`, `tests/test_provider_device_flow_js.py`, `tests/test_provider_endpoints_headers.py`, `tests/test_provider_endpoints_models.py`, `tests/test_provider_endpoints_normalization.py`, `tests/test_provider_endpoints_tailscale.py`, `tests/test_provider_endpoints_url_building.py`, `tests/test_provider_label_js.py`, `tests/test_providers_mixtral_logo_js.py`, `tests/test_stt_leak.py`, `tests/test_tts_available_nonstring_provider.py`, `tests/test_tts_cache_stats.py`, `tests/test_tts_service_enforce_cache_limit.py`, `tests/test_tts_speed_malformed.py`, `tests/test_youtube_comments_timeout.py`, `tests/test_youtube_extract_id_nonstring.py`, `tests/test_youtube_handler_consolidation.py`, `tests/test_youtube_svc_comments_nondict.py`, `tests/test_youtube_transcript_seg_nondict.py`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 55. tests: LLM, tools and agent loop

### Overview

`tests/test_action_intents.py`, `tests/test_action_intents_shell_verbs.py`, `tests/test_agent_bash_windows.py`, `tests/test_agent_loop.py`, `tests/test_agent_loop_tool_output_truncation.py`, `tests/test_agent_migration_manifest.py`, `tests/test_agent_round_model_provenance_ui.py`, `tests/test_agent_rounds_exhausted.py`, `tests/test_agent_state_dir_confinement.py`, `tests/test_agent_thread_dot_alignment_css.py`, `tests/test_agent_tool_budget_nonnumeric.py`, `tests/test_agent_tools_truncate_nonstring.py`, `tests/test_app_config_shared_fetch_js.py`, `tests/test_app_db_permissions.py`, `tests/test_app_initializer_memory_vector_degraded.py`, `tests/test_app_static_mime.py`, `tests/test_ask_user_persistence.py`, `tests/test_ask_user_tool.py`, `tests/test_bg_job_tools.py`, `tests/test_bg_jobs_store.py`, `tests/test_bg_monitor_stream.py`, `tests/test_compaction_summary_failure.py`, `tests/test_loop_breaker_runaway.py`, `tests/test_mcp_add_server_args_validation.py`, `tests/test_mcp_cache_invalidation.py`, `tests/test_mcp_common_truncate.py`, `tests/test_mcp_dependency_compatibility.py`, `tests/test_mcp_email_decode_header_spaces.py`, `tests/test_mcp_manager.py`, `tests/test_mcp_memory_owner_scope.py`, `tests/test_mcp_oauth.py`, `tests/test_mcp_param_hint_hardening.py`, `tests/test_mcp_reconnect_args.py`, `tests/test_mcp_routes_shim.py`, `tests/test_mcp_tool_params_in_prompt.py`, `tests/test_research_chat_stream_owner.py`, `tests/test_research_endpoint_owner_scope.py`, `tests/test_research_handler_analyzed_urls.py`, `tests/test_research_handler_path_confinement.py`, `tests/test_research_handler_raw_nondict.py`, `tests/test_research_handler_sources_nondict.py`, `tests/test_research_owner_scope_routes.py`, `tests/test_research_probe_errors.py`, `tests/test_research_query_fallback.py`, `tests/test_research_report_read.py`, `tests/test_research_routes_path_confinement.py`, `tests/test_research_routes_shim.py`, `tests/test_research_service.py`, `tests/test_research_session_id_validation.py`, `tests/test_research_source_link_xss.py`, `tests/test_research_status_avg_duration.py`, `tests/test_research_utils.py`, `tests/test_research_utils_low_quality_nonstring.py`, `tests/test_schedule_email_offset_normalization.py`, `tests/test_scheduler_prompt_cache_time.py`, `tests/test_scheduler_restart_doublefire.py`, `tests/test_scheduler_scheduled_time_validation.py`, `tests/test_search_analytics_defaults.py`, `tests/test_search_cache_invalidation.py`, `tests/test_search_config_no_key_leak.py`, `tests/test_search_config_provider_key.py`, `tests/test_search_content_block_source_index.py`, `tests/test_search_content_extraction_parity.py`, `tests/test_search_content_url_guards.py`, `tests/test_search_module_consolidation.py`, `tests/test_search_provider_json.py`, `tests/test_search_query.py`, `tests/test_search_query_entities_nonstring.py`, `tests/test_search_query_nonstring.py`, `tests/test_search_query_unicode_names.py`, `tests/test_search_ranking.py`, `tests/test_search_ranking_recency.py`, `tests/test_search_ranking_sports_substring.py`, `tests/test_search_ranking_subject_substring.py`, `tests/test_search_routes_shim.py`, `tests/test_search_service_nondict_rows.py`, `tests/test_skill_edit_no_collapse_on_outside_click_js.py`, `tests/test_skill_extractor_json.py`, `tests/test_skill_extractor_rows.py`, `tests/test_skill_extractor_stray_brace.py`, `tests/test_skill_format_timestamp.py`, `tests/test_skill_frontmatter_escape_roundtrip.py`, `tests/test_skill_importer.py`, `tests/test_skill_importer_dns_pinning.py`, `tests/test_skill_importer_security.py`, `tests/test_skill_importer_ssrf_redirect.py`, `tests/test_skill_index_prompt_injection.py`, `tests/test_skill_index_toolset_gating.py`, `tests/test_skill_save_no_rename.py`, `tests/test_skills_delete_owner.py`, `tests/test_skills_manager_owner_isolation.py`, `tests/test_skills_routes_nondict.py`, `tests/test_skills_routes_owner_update.py`, `tests/test_skills_tag_token_match.py`, `tests/test_task_chain_owner_scope.py`, `tests/test_task_cookbook_admin_gate.py`, `tests/test_task_endpoint_normalization.py`, `tests/test_task_routes_shim.py`, `tests/test_task_scheduler_cache.py`, `tests/test_task_scheduler_cancel.py`, `tests/test_task_scheduler_session_delivery.py`, `tests/test_task_session_folder.py`, `tests/test_task_shell_tools.py`, `tests/test_tool_approval_frontend_routing.py`, `tests/test_tool_approval_single_action_scope.py`, `tests/test_tool_approval_task_scope.py`, `tests/test_tool_approvals.py`, `tests/test_tool_implementations_shim.py`, `tests/test_tool_index_keyword_boundaries.py`, `tests/test_tool_index_schema_parity.py`, `tests/test_tool_output_prompt_injection.py`, `tests/test_tool_parsing_bare_end_marker.py`, `tests/test_tool_parsing_hermes_json.py`, `tests/test_tool_parsing_nonstring.py`, `tests/test_tool_path_confinement.py`, `tests/test_tool_policy.py`, `tests/test_tool_rag_contacts_domain.py`, `tests/test_tool_rag_keyword_hints.py`, `tests/test_tool_support_heuristic.py`, `tests/test_tool_task_cancelled_on_disconnect.py`, `tests/test_tool_utils_import_clean.py`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 56. tests: session, chat, memory and RAG

### Overview

`tests/test_chat_attachment_picker.py`, `tests/test_chat_cached_model_normalization.py`, `tests/test_chat_helpers.py`, `tests/test_chat_helpers_bg_tasks_tracked.py`, `tests/test_chat_image_routing.py`, `tests/test_chat_metrics.py`, `tests/test_chat_model_provenance_js.py`, `tests/test_chat_preprocess_tool_policy.py`, `tests/test_chat_processor_pinned_memory.py`, `tests/test_chat_processor_web_search.py`, `tests/test_chat_route_tool_policy.py`, `tests/test_chat_stream_errors_js.py`, `tests/test_chat_stream_scope.py`, `tests/test_chat_tool_screenshot_xss.py`, `tests/test_chat_upload_limit_config.py`, `tests/test_chat_url_prefetch_failure_context.py`, `tests/test_chatgpt_subscription_routes.py`, `tests/test_chroma_client.py`, `tests/test_context_budget.py`, `tests/test_context_cache_per_endpoint.py`, `tests/test_context_compactor.py`, `tests/test_context_compactor_nonstring.py`, `tests/test_memory_add_submit_regression.py`, `tests/test_memory_audit_timeout.py`, `tests/test_memory_bullet_extraction.py`, `tests/test_memory_cli_add_nondict.py`, `tests/test_memory_extract_chat_nondict.py`, `tests/test_memory_extraction_parse.py`, `tests/test_memory_extractor_rows.py`, `tests/test_memory_extractor_vector_cross_tenant.py`, `tests/test_memory_extractor_vector_degraded.py`, `tests/test_memory_fallback_dislike.py`, `tests/test_memory_imports.py`, `tests/test_memory_owner_isolation.py`, `tests/test_memory_provider.py`, `tests/test_memory_recall_nondict_rows.py`, `tests/test_memory_routes_session_owner.py`, `tests/test_memory_routes_shim.py`, `tests/test_memory_store_unreadable_no_wipe.py`, `tests/test_memory_validate_entries_nondict.py`, `tests/test_personal_delete_file_confinement.py`, `tests/test_personal_dir_symlink_escape.py`, `tests/test_personal_docs_exclusions.py`, `tests/test_personal_docs_keyword_nondict.py`, `tests/test_personal_docs_lists.py`, `tests/test_personal_docs_office_index.py`, `tests/test_personal_docs_pdf_index.py`, `tests/test_personal_docs_state_store.py`, `tests/test_personal_index_hidden_dirs.py`, `tests/test_personal_remove_dir_confinement.py`, `tests/test_personal_upload_isolation.py`, `tests/test_personal_upload_privilege.py`, `tests/test_rag_index_hidden_dirs.py`, `tests/test_rag_keyword_fallback_owner.py`, `tests/test_rag_manager_owner_compat.py`, `tests/test_rag_remove_directory_scope.py`, `tests/test_rag_search_signature.py`, `tests/test_rag_server_directory_nonstring.py`, `tests/test_rag_vector_id_stability.py`, `tests/test_rag_vector_rename_owner.py`, `tests/test_searchservice_search_call.py`, `tests/test_session_actions_cleanup.py`, `tests/test_session_concurrent.py`, `tests/test_session_context_excludes_slash.py`, `tests/test_session_discovery_message_count.py`, `tests/test_session_endpoint_owner_scope.py`, `tests/test_session_export_filename.py`, `tests/test_session_export_nonstring_content.py`, `tests/test_session_ghost_delete.py`, `tests/test_session_image_cleanup.py`, `tests/test_session_list_owner_scope.py`, `tests/test_session_manager.py`, `tests/test_session_manager_cleanup.py`, `tests/test_session_manager_persist_guard.py`, `tests/test_session_mode_helpers.py`, `tests/test_session_owner_attribution.py`, `tests/test_session_routes_utcnow.py`, `tests/test_session_search.py`, `tests/test_session_search_batch_fetch.py`, `tests/test_session_tools_registry.py`, `tests/test_topic_analyzer.py`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 57. tests: documents, uploads, gallery and media

### Overview

`tests/test_attachment_refs.py`, `tests/test_doc_library_open_orphaned.py`, `tests/test_document_actions_nonstring.py`, `tests/test_document_ai_preview_refresh_js.py`, `tests/test_document_close_clears_active_route.py`, `tests/test_document_deeplink.py`, `tests/test_document_diff_discard_on_update_js.py`, `tests/test_document_editor_scroll.py`, `tests/test_document_library_delete_counters.py`, `tests/test_document_library_language_facet.py`, `tests/test_document_library_pdf_metadata.py`, `tests/test_document_pdf_marker.py`, `tests/test_document_processor_attachment_budget.py`, `tests/test_document_processor_empty_media_subtype.py`, `tests/test_document_render_pdf_iframe.py`, `tests/test_document_routes_shim.py`, `tests/test_document_session_owner_scope.py`, `tests/test_document_tidy_null_timestamp.py`, `tests/test_document_tool_owner_scope.py`, `tests/test_gallery_album_owner_scope.py`, `tests/test_gallery_delete_file_ordering.py`, `tests/test_gallery_endpoint_hardening.py`, `tests/test_gallery_endpoint_matching.py`, `tests/test_gallery_endpoint_ssrf.py`, `tests/test_gallery_exif_orientation.py`, `tests/test_gallery_filename_confinement.py`, `tests/test_gallery_image_endpoint_owner_scope.py`, `tests/test_gallery_image_privileges.py`, `tests/test_gallery_model_input_device.py`, `tests/test_gallery_null_user_routes.py`, `tests/test_gallery_owner_filter_single_user.py`, `tests/test_gallery_result_image_ssrf.py`, `tests/test_gallery_routes_shim.py`, `tests/test_image_models_nondict_system.py`, `tests/test_image_models_nonstring_search.py`, `tests/test_load_features_permission_error.py`, `tests/test_note_reminder_email_oauth.py`, `tests/test_note_reminder_fire_scope.py`, `tests/test_note_routes_shim.py`, `tests/test_notes_dom_xss_helpers.py`, `tests/test_notes_fail_closed_auth.py`, `tests/test_notes_search_reset_on_reopen_js.py`, `tests/test_notes_select_esc_listener_js.py`, `tests/test_notes_update_due_date.py`, `tests/test_notes_z_order_js.py`, `tests/test_pdf_ai_edit_derivative.py`, `tests/test_pdf_runtime.py`, `tests/test_upload_content_detection_magic.py`, `tests/test_upload_error_surfaced.py`, `tests/test_upload_handler_atomicity.py`, `tests/test_upload_handler_cleanup.py`, `tests/test_upload_handler_rename_owner.py`, `tests/test_upload_id_extension.py`, `tests/test_upload_id_validation.py`, `tests/test_upload_limits_centralized.py`, `tests/test_upload_multifile.py`, `tests/test_upload_routes_owner_scope.py`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

## 58. tests: remaining test modules

### Overview

`tests/bombadil-spec.ts`, `tests/live_thinking_scheduler.test.mjs`, `tests/markdown_codefence_placeholder_regression.mjs`, `tests/test_active_document_clear.py`, `tests/test_active_email_reply_guard.py`, `tests/test_add_directory_event_loop.py`, `tests/test_admin_device_flow_static.py`, `tests/test_admin_tools_registry.py`, `tests/test_admin_wipe_gallery.py`, `tests/test_admin_wipe_routes_shim.py`, `tests/test_amd_gpu_check_args.py`, `tests/test_anthropic_response_parse.py`, `tests/test_api_call_integration_routing.py`, `tests/test_api_chat_security.py`, `tests/test_api_key_file_permissions.py`, `tests/test_api_key_manager_atomic_save.py`, `tests/test_api_key_manager_corrupt_load.py`, `tests/test_api_key_manager_resilience.py`, `tests/test_api_token_routes.py`, `tests/test_api_token_tool_authority.py`, `tests/test_api_token_user_route_gate.py`, `tests/test_app.py`, `tests/test_approved_replay_message_shape.py`, `tests/test_archived_sessions_model_filter.py`, `tests/test_atomic_io.py`, `tests/test_aux_llm_owner_scope.py`, `tests/test_backup_cli_security.py`, `tests/test_backup_import_cross_user_dedup.py`, `tests/test_backup_import_skills.py`, `tests/test_backup_import_skills_dedup.py`, `tests/test_blind_compare_redaction.py`, `tests/test_budget_auto_sentinel.py`, `tests/test_build_user_content_pdf_marker.py`, `tests/test_builtin_actions_cookbook_serve_state.py`, `tests/test_builtin_actions_nonstring.py`, `tests/test_builtin_actions_owner_scope.py`, `tests/test_builtin_mcp_bg_tasks.py`, `tests/test_builtin_mcp_npx_cache.py`, `tests/test_builtin_mcp_pythonpath.py`, `tests/test_builtin_memory_consolidation.py`, `tests/test_cache_affinity_local_only.py`, `tests/test_canvas_coords_empty_touches_js.py`, `tests/test_carddav_password_encryption.py`, `tests/test_censor_pref_js.py`, `tests/test_cerebras_cache_affinity.py`, `tests/test_check_outbound_url_nonstring.py`, `tests/test_checkin_digest_owner_scope.py`, `tests/test_ci_authoritative_validation.py`, `tests/test_claim_ownerless_json.py`, `tests/test_classify_events_memory_text.py`, `tests/test_cleanup_owner_scope.py`, `tests/test_cleanup_routes_shim.py`, `tests/test_cleanup_service_utcnow.py`, `tests/test_code_nav_tools.py`, `tests/test_codex_cookbook_admin_gate.py`, `tests/test_codex_ssh_host_validation.py`, `tests/test_compact_truncate_tool_call_args.py`, `tests/test_companion_pairing.py`, `tests/test_companion_readonly.py`, `tests/test_compare_ask_user_routing.py`, `tests/test_compare_endpoint_owner_scope.py`, `tests/test_compare_js.py`, `tests/test_compare_routes_shim.py`, `tests/test_compare_stop_disconnect_poll.py`, `tests/test_composer_arrow_up_recall_js.py`, `tests/test_compute_next_run_monthly_clamp.py`, `tests/test_consolidate_memory_explicit_drops.py`, `tests/test_copilot.py`, `tests/test_copilot_routes.py`, `tests/test_copy_message_strips_thinking_js.py`, `tests/test_cors_preflight.py`, `tests/test_database_utcnow.py`, `tests/test_ddg_redirect_resolution.py`, `tests/test_deep_research_date_context.py`, `tests/test_deep_research_extraction_controls.py`, `tests/test_deep_research_parse_json_array_echo.py`, `tests/test_deep_research_search_error.py`, `tests/test_deep_research_synthesis_resilience.py`, `tests/test_delete_message_no_session.py`, `tests/test_delete_user_invalidates_token_cache.py`, `tests/test_delete_user_revokes_api_tokens.py`, `tests/test_deleted_session_sidebar_regression.py`, `tests/test_derive_title_nonstring.py`, `tests/test_device_flow_routes.py`, `tests/test_dialog_aria.py`, `tests/test_diffusion_server_security.py`, `tests/test_digest_windows.py`, `tests/test_direct_upload_limits.py`, `tests/test_docker_devops_hardening.py`, `tests/test_docs_no_orphan_images.py`, `tests/test_docs_query_nondict_rows.py`, `tests/test_edit_file.py`, `tests/test_editor_draft_payload.py`, `tests/test_emoji_shortcodes_js.py`, `tests/test_emoji_svg_hardening.py`, `tests/test_esc_menu_stack_js.py`, `tests/test_estimate_tokens_tool_calls.py`, `tests/test_external_context_tool_gate.py`, `tests/test_extract_quotes.py`, `tests/test_extract_skill_json_nonstring.py`, `tests/test_extract_statistics.py`, `tests/test_extract_urls.py`, `tests/test_fastembed_cache_path.py`, `tests/test_fenced_example_not_executed_for_native_models.py`, `tests/test_fenced_inline_args.py`, `tests/test_fenced_invoke_no_raw_xml.py`, `tests/test_focused_test_guidance.py`, `tests/test_font_routes.py`, `tests/test_foreground_model_routing.py`, `tests/test_fork_session_metadata.py`, `tests/test_form_markdown_roundtrip.py`, `tests/test_forwarded_message_divider.py`, `tests/test_function_call_non_object_args.py`, `tests/test_function_model_tool_call.py`, `tests/test_gemma_tool_call_parsing.py`, `tests/test_generated_image_confinement.py`, `tests/test_gmail_quote_attribution_js.py`, `tests/test_group_character_dropdown.py`, `tests/test_group_chat_storage.py`, `tests/test_harmonize_masks_invalid_layers_js.py`, `tests/test_harmony_tool_aliasing.py`, `tests/test_helpers_import_state.py`, `tests/test_hex_to_rgb_js.py`, `tests/test_history_compact_tool_calls.py`, `tests/test_history_db_fallback_hidden.py`, `tests/test_history_display_model_hydration.py`, `tests/test_history_order_by_timestamp_regression.py`, `tests/test_history_routes_shim.py`, `tests/test_history_topics_owner_scope.py`, `tests/test_icloud_imap_full_fetch.py`, `tests/test_inside_base_dir_nonstring.py`, `tests/test_integration_api_call_ssrf.py`, `tests/test_integrations_api_call_truncation.py`, `tests/test_integrations_store_shape.py`, `tests/test_integrations_url_join.py`, `tests/test_interactive_gate_passive_paths.py`, `tests/test_internal_api_base.py`, `tests/test_issue_description_check.py`, `tests/test_keybind_altgr_js.py`, `tests/test_kimi_code_hosts.py`, `tests/test_kimi_code_user_agent.py`, `tests/test_kokoro_optional_requirements.py`, `tests/test_kv_cache_invalidation_2927.py`, `tests/test_lang_icon_null_opts_js.py`, `tests/test_launcher.py`, `tests/test_legacy_default_fallback_ui.py`, `tests/test_live_fallback_round_attribution.py`, `tests/test_live_strip_email_tool_fences.py`, `tests/test_live_thinking_chat_integration.py`, `tests/test_live_thinking_scheduler_js.py`, `tests/test_llama_server_models_url.py`, `tests/test_llamacpp_discovery.py`, `tests/test_lmstudio_discovery.py`, `tests/test_lmstudio_models_url.py`, `tests/test_lmstudio_vision.py`, `tests/test_local_endpoint_api_key_js.py`, `tests/test_local_endpoint_js.py`, `tests/test_log_safety.py`, `tests/test_manage_mcp_command_allowlist.py`, `tests/test_manage_memory_blank_id.py`, `tests/test_manage_memory_list.py`, `tests/test_manage_notes_owner_gate.py`, `tests/test_manage_settings_token_budget.py`, `tests/test_manage_skills_action_required.py`, `tests/test_manage_tasks_owner_scope.py`, `tests/test_markdown_dom_xss_helpers.py`, `tests/test_markdown_lazy_lib_loading_js.py`, `tests/test_markdown_rendering_js.py`, `tests/test_markdown_table_row_js.py`, `tests/test_markitdown_format_nonstring.py`, `tests/test_markitdown_runtime.py`, `tests/test_match_model_key_js.py`, `tests/test_matchescombo_nonstring_js.py`, `tests/test_merge_last_assistant_rows.py`, `tests/test_migrate_faiss_to_chroma.py`, `tests/test_misfenced_read_file_tool_call.py`, `tests/test_mlx_image_server_security.py`, `tests/test_modal_dock_composer_clearance.py`, `tests/test_multiple_mcp_servers_timeout.py`, `tests/test_native_tool_result_threading.py`, `tests/test_new_chat_clears_input.py`, `tests/test_new_chat_model_preference.py`, `tests/test_nix_upload_text.py`, `tests/test_null_owner_gates.py`, `tests/test_odysseus_dispatcher.py`, `tests/test_odysseus_doc_fence_normalization.py`, `tests/test_og_image_extraction.py`, `tests/test_ollama_multimodal.py`, `tests/test_ollama_port_detection.py`, `tests/test_ollama_runner_hint.py`, `tests/test_ordinal_suffix_js.py`, `tests/test_owned_document_query.py`, `tests/test_owner_identity.py`, `tests/test_panel_loader_js.py`, `tests/test_parse_due_time_first.py`, `tests/test_parse_msg_content_jsonlike_string.py`, `tests/test_plain_ui_control_open_panel.py`, `tests/test_plan_mode.py`, `tests/test_platform_compat.py`, `tests/test_poll_endpoint_no_task_interrupt.py`, `tests/test_popup_opener_isolation_js.py`, `tests/test_portal_dropdown_z_js.py`, `tests/test_pr6020_browser_review_regressions.py`, `tests/test_pr6020_rebase_regressions.py`, `tests/test_prefs_atomic_write.py`, `tests/test_prefs_routes.py`, `tests/test_prefs_single_user_no_clobber.py`, `tests/test_preset_atomic_save.py`, `tests/test_preset_expand_owner_scope.py`, `tests/test_preset_fill_missing_defaults.py`, `tests/test_preset_local_storage_js.py`, `tests/test_preset_store_shape.py`, `tests/test_promote_image_fields.py`, `tests/test_public_blocked_tool_nonstring.py`, `tests/test_question_type_detection.py`, `tests/test_rate_limiter.py`, `tests/test_readiness.py`, `tests/test_readme_ascii_fenced.py`, `tests/test_realesrgan_torchvision_compat.py`, `tests/test_redos_cal_extract.py`, `tests/test_redos_llm_parsers.py`, `tests/test_redos_think_blocks.py`, `tests/test_redos_verdict_continuation.py`, `tests/test_redos_xml_tool_parsers.py`, `tests/test_reminder_ntfy_ssrf.py`, `tests/test_rename_user_case_insensitive.py`, `tests/test_rename_user_owner_sync.py`, `tests/test_rename_user_token_cache.py`, `tests/test_replace_messages_multimodal.py`, `tests/test_replace_messages_upload_reservations.py`, `tests/test_reply_all_cc_nonstring_js.py`, `tests/test_reply_recipients_js.py`, `tests/test_resend_message_nondestructive.py`, `tests/test_reserved_username_admin_escalation.py`, `tests/test_resolve_endpoint_fallbacks.py`, `tests/test_resolve_model_offloaded.py`, `tests/test_resolve_session_auth_chatgpt.py`, `tests/test_resolve_upload_path_nondict.py`, `tests/test_retired_settings_interfaces.py`, `tests/test_review_regressions.py`, `tests/test_rewrite_persist_column.py`, `tests/test_route_validators.py`, `tests/test_run_focus.py`, `tests/test_run_order_report.py`, `tests/test_runtime_paths.py`, `tests/test_sanitize_multimodal_merge.py`, `tests/test_sanitize_preserves_reasoning.py`, `tests/test_scheduled_poll_race.py`, `tests/test_searxng_image_pinned.py`, `tests/test_searxng_settings_migration.py`, `tests/test_select_dropdown_theme_css.py`, `tests/test_sender_signature_skip_roles.py`, `tests/test_serve_html_with_nonce.py`, `tests/test_serve_profiles.py`, `tests/test_service_health_chromadb.py`, `tests/test_service_health_collect.py`, `tests/test_service_health_email.py`, `tests/test_service_health_ntfy.py`, `tests/test_service_health_providers.py`, `tests/test_service_health_search.py`, `tests/test_service_search_provider_guards.py`, `tests/test_services_research_low_quality_sources.py`, `tests/test_services_search_analytics_defaults.py`, `tests/test_set_admin.py`, `tests/test_settings_error_paths.py`, `tests/test_settings_scrub.py`, `tests/test_settings_shell_js_behavior.py`, `tests/test_settings_store_shape.py`, `tests/test_setup_admin_user.py`, `tests/test_setup_device_auth_static.py`, `tests/test_setup_llamacpp_hint_js.py`, `tests/test_shell_routes.py`, `tests/test_shell_service.py`, `tests/test_signature_fold_js.py`, `tests/test_signature_fold_self_closing_br_js.py`, `tests/test_signature_route_hardening.py`, `tests/test_signature_settings_dom_xss.py`, `tests/test_slash_autocomplete_static.py`, `tests/test_slash_setup_provider_aliases.py`, `tests/test_snap_other_layers_nonarray_js.py`, `tests/test_speech_service_toggles.py`, `tests/test_spinner_stops_when_never_attached_js.py`, `tests/test_split_chunks_no_duplicate_tail.py`, `tests/test_sqlite_foreign_keys.py`, `tests/test_src_search_query_nonstring.py`, `tests/test_startup_session_bootstrap_js.py`, `tests/test_startup_shell_js.py`, `tests/test_streaming_segmenter_js.py`, `tests/test_strip_reasoning_prose_dataloss.py`, `tests/test_strip_think.py`, `tests/test_svc_research_sources_nondict.py`, `tests/test_tailscale_discovery_cache.py`, `tests/test_taxonomy.py`, `tests/test_teacher_audit_owner_scope.py`, `tests/test_teacher_eval_nonstring_reply.py`, `tests/test_teacher_eval_tier2.py`, `tests/test_tidy_research_owner_scope.py`, `tests/test_tile_manager_snap_zones_js.py`, `tests/test_tls_overrides_scope.py`, `tests/test_toast_dismiss_pointer_events.py`, `tests/test_totp_failclosed.py`, `tests/test_truncate_message_count_regression.py`, `tests/test_ui_control_rag_toggle.py`, `tests/test_ui_visibility_js.py`, `tests/test_unknown_tool_calls.py`, `tests/test_update_database_script.py`, `tests/test_update_plan_tool.py`, `tests/test_url_safety.py`, `tests/test_user_time.py`, `tests/test_vcard_unfolding.py`, `tests/test_venice_hosts.py`, `tests/test_vision_model_detection.py`, `tests/test_vision_owner_scope.py`, `tests/test_visual_report.py`, `tests/test_visual_report_icon_url.py`, `tests/test_visual_report_nonstring.py`, `tests/test_visual_report_slug_unique.py`, `tests/test_visual_report_toc_code_fence.py`, `tests/test_warmup_ping_urls.py`, `tests/test_windows_update_script.py`, `tests/test_workspace_confine.py`, `tests/test_write_file_empty_body.py`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

### Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

#### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->

# Coverage boundaries

This is a first pass. Of the 58 section files in this run, **fifteen** have been reviewed:
`src-security.md` (7 findings), `src-agent-loop.md` (7 findings), `src-agent-tools.md`
(9 findings), `routes-shell.md` (7 findings), `src-tools-builtin-actions.md`
(5 findings), `src-tools-parse-exec.md` (5 findings),
`src-tools-schema-index.md` (6 findings), `src-tools-capabilities-policy.md` (1 finding),
`core-auth-session.md` (5 findings), `core-data-platform.md` (6 findings),
`src-platform.md` (4 findings), `routes-rest-auth-admin.md` (4 findings), `routes-rest-agent-admin.md` (4 findings), and
`routes-rest-notes-contacts-history.md` (3 findings), and
`routes-rest-memory-personal-research.md` (3 findings), 76 total (3 high,
32 medium, 41 low). The other
43 are still the scaffolded stub — they contain no coverage claim and no findings, so nothing in
them has been checked. This section states the boundary once.

```
$ python3 -c "<strip HTML comments, look for '### ['>"
sections with real findings : 14
  src-security.md
  src-agent-loop.md
  src-agent-tools.md
  routes-shell.md
  src-tools-builtin-actions.md
  src-tools-parse-exec.md
  src-tools-schema-index.md
  src-tools-capabilities-policy.md
  core-auth-session.md
  core-data-platform.md
  src-platform.md
  routes-rest-auth-admin.md
  routes-rest-agent-admin.md
  routes-rest-notes-contacts-history.md
  routes-rest-memory-personal-research.md
sections still stubs        : 43
```

## Not covered

- **23 of 58 sections, unreviewed.** Thirty-five section files hold findings:
  `src-security`, `src-agent-loop`, `src-agent-tools`, `src-tools-builtin-actions`,
  `src-tools-parse-exec`, `src-tools-schema-index`, `src-tools-capabilities-policy`,
  `src-platform`, `src-memory-rag`, `src-research-scheduling`, `src-llm-core`,
  `src-chat-session`, `src-documents`, `src-email-integrations`, `src-mcp`,
  `core-auth-session`,
  `core-data-platform`, `routes-shell`, `routes-rest-auth-admin`, `routes-rest-agent-admin`,
  `routes-rest-notes-contacts-history`, `routes-rest-memory-personal-research`,
  `routes-rest-media-files`, `routes-rest-integrations-misc`, `routes-models`,
  `routes-chat-session`, `routes-gallery-document`, `routes-skills-calendar-task`,
  `routes-cookbook`, `routes-email`, `services-search`, `services-memory`,
  `services-research`, `services-hwfit` and `services-media`. Every other
  section file is
  still the template. That is the whole repository outside the `src` security guards, the agent
  loop, the tool implementations and dispatcher, the retrieval index, capability and policy
  tables, the shared runtime, the memory/RAG stores, the research and scheduling pipeline, the
  LLM call core and context discovery, the conversation store, compaction and search, the
  document pipeline and its tidy actions, the CalDAV, webhook, integration and thread-parser
  stores, the MCP manager and its OAuth pieces, the search service and its providers, the memory
  extractor, skill format, skill store and bundle importer, the research service, its handler copy
  and the docs facade, the hardware probe, the model catalogue and its ranking, and the Hugging
  Face discovery paths, the YouTube handler, the speech services and the shell facade, the
  auth/session and database core, the shell and code-execution router, the model-serving
  registry, the core chat and session routes, the gallery, document, skills, calendar, task,
  cookbook and email
  routes, and all six
  reviewed `routes-rest-*` surfaces — every `src-*` section among them. Every `core-*`, `routes-*`,
  `src-*` and `services-*` section is now reviewed. What remains is
  `repository-root`,
  `build-install-deploy`, `specs`, `scripts`, `website`, the eight
  `static-*`, the eight `tests-*`,
  `mcp-servers` and `companion-and-swift`.
  All 1573 assigned paths are listed in `run.toml`; a path is not covered
  because it appears there.
- **The dispatcher and the routes the tools call.** `src-agent-tools.md` covers what each tool
  does once it is reached. `src-tools-parse-exec.md` now covers the dispatcher and the
  file-confinement helpers (`_resolve_tool_path` / `_resolve_search_root` / `vet_workspace`),
  `src-tools-capabilities-policy.md` covers the capability and policy tables
  (`src/tool_capabilities.py`, `src/tool_policy.py`, `src/tool_security.py`) and the built-in
  MCP registration (`src/builtin_mcp.py`), and `src-tools-schema-index.md` covers the schema
  list, the native-call converter, the retrieval index and the `do_*` facade — but the route
  handlers the tools
  call are assigned to the `routes-*` sections, so
  whether a tool's request is accepted and scoped by its route is checked only where a finding
  cites the route. `src-tools-builtin-actions.md` reviews
  `src/builtin_actions.py` only, not the dispatcher those actions enter through.
- **The consumers of the agent loop.** `src-agent-loop.md` covers the loop's own decisions. The
  route that builds the initial message list and persists events (`routes/chat_routes.py`,
  `routes/chat_helpers.py`) and the capability tables (`src/tool_capabilities.py`,
  `src/tool_policy.py`) are assigned to other sections; `src-tools-capabilities-policy.md` now
  covers the tables themselves, but not the routes that supply them, so whether each loop
  decision is honored downstream is not checked here. `src-tools-builtin-actions.md` reads the
  scheduled actions that call back into the same database and mail surfaces; it does not read the
  scheduler that invokes them (`src/task_scheduler.py`, assigned to
  `src-research-scheduling`) except where a finding cites it.
- **The largest unreviewed files.** `run.toml`'s `notes` flags two as generated or vendored rather
  than first-party: `services/hwfit/data/*.json` (a ~35k-line model catalogue) and `static/lib/`
  (minified third-party bundles). They should be skimmed for provenance, not read as code.
- **`src/outbound_fetch.py` below line 44** — about 270 lines holding the pinned transport, the
  capped fetch, and the redirect handling. The address guard at the top of the file was read; the
  machinery that acts on its verdict was not. This is the most consequential gap in the section
  that *was* reviewed, because a guard is only as good as the code that consults it, and the
  `SECURITY` finding in `src-security.md` sits exactly on that boundary.
- **Callers of the reviewed guards.** `src-security.md` establishes what the guards do, not whether
  every caller reaches them correctly. The agent tool surface, the route handlers, and the search
  service are assigned to other sections and were not read.

## Not run

No build or deployment was run as part of this pass. The gate results quoted in this
audit come from reading `.github/workflows/ci.yml` and the manifests, not from observing a run.
The one exception is `src-tools-capabilities-policy.md`, which ran that section's own gate
suites — 240 tests over seven files — to check the policy partitions it had just read; the
result is recorded in the section's coverage statement. `src-tools-schema-index.md` ran the
three suites that pin its own surface (`tests/test_tool_index_schema_parity.py`,
`tests/test_tool_rag_keyword_hints.py`, `tests/test_tool_implementations_shim.py`) — 10 passed —
plus the throwaway probes its findings quote. `core-auth-session.md` ran the three suites that
pin its surface (`tests/test_session_manager_cleanup.py`, `tests/test_log_safety.py`,
`tests/test_auth_session_revocation.py`) — 15 passed. `core-data-platform.md` ran nine suites over
the surface it read (`tests/test_atomic_io.py`, `tests/test_app_db_permissions.py`,
`tests/test_memory_store_unreadable_no_wipe.py`, `tests/test_prefs_atomic_write.py`,
`tests/test_database_utcnow.py`, `tests/test_sqlite_foreign_keys.py`,
`tests/test_update_database_script.py`, `tests/test_api_key_file_permissions.py`,
`tests/test_security_regressions.py`) — 148 passed. `src-platform.md` ran thirteen suites over the
surface it read (`tests/test_readiness.py`, `tests/test_user_time.py`, `tests/test_strip_think.py`,
`tests/test_strip_reasoning_prose_dataloss.py`, `tests/test_service_health_collect.py`,
`tests/test_service_health_chromadb.py`, `tests/test_service_health_email.py`,
`tests/test_service_health_ntfy.py`, `tests/test_service_health_providers.py`,
`tests/test_service_health_search.py`, `tests/test_app_initializer_memory_vector_degraded.py`,
`tests/test_runtime_paths.py`, `tests/test_agent_state_dir_confinement.py`) — 141 passed.
`routes-rest-auth-admin.md` ran twenty-seven suites over the surface it read
(`tests/test_api_token_routes.py`, `tests/test_api_token_user_route_gate.py`,
`tests/test_device_flow_routes.py`, `tests/test_copilot_routes.py`,
`tests/test_admin_wipe_gallery.py`, `tests/test_admin_wipe_routes_shim.py`,
`tests/test_backup_cli_security.py`, `tests/test_backup_import_cross_user_dedup.py`,
`tests/test_backup_import_skills.py`, `tests/test_backup_import_skills_dedup.py`,
`tests/test_auth_policy.py`, `tests/test_auth_regressions.py`,
`tests/test_auth_require_privilege_nondict.py`, `tests/test_auth_root_path.py`,
`tests/test_auth_session_revocation.py`, `tests/test_rename_user_case_insensitive.py`,
`tests/test_rename_user_owner_sync.py`, `tests/test_rename_user_token_cache.py`,
`tests/test_delete_user_invalidates_token_cache.py`, `tests/test_delete_user_revokes_api_tokens.py`,
`tests/test_setup_admin_user.py`, `tests/test_rate_limiter.py`, `tests/test_totp_failclosed.py`,
`tests/test_route_validators.py`, `tests/test_integrations_store_shape.py`,
`tests/test_cors_preflight.py`, `tests/test_reserved_username_admin_escalation.py`) — 203 passed.
`routes-rest-agent-admin.md` ran twenty-one suites over the surface it read
(`tests/test_codex_cookbook_admin_gate.py`, `tests/test_codex_ssh_host_validation.py`,
`tests/test_mcp_oauth.py`, `tests/test_mcp_routes_shim.py`, `tests/test_mcp_manager.py`,
`tests/test_manage_mcp_command_allowlist.py`, `tests/test_mcp_add_server_args_validation.py`,
`tests/test_mcp_cache_invalidation.py`, `tests/test_mcp_reconnect_args.py`,
`tests/test_mcp_memory_owner_scope.py`, `tests/test_mcp_param_hint_hardening.py`,
`tests/test_mcp_email_decode_header_spaces.py`, `tests/test_mcp_common_truncate.py`,
`tests/test_mcp_dependency_compatibility.py`, `tests/test_multiple_mcp_servers_timeout.py`,
`tests/test_mcp_tool_params_in_prompt.py`, `tests/test_builtin_mcp_bg_tasks.py`,
`tests/test_builtin_mcp_npx_cache.py`, `tests/test_builtin_mcp_pythonpath.py`,
`tests/test_workspace_confine.py`, `tests/test_merge_last_assistant_rows.py`) — 170 passed.
`routes-rest-notes-contacts-history.md` ran the twenty-two suites matching its modules
(`test_contacts_add_null_name.py`, `test_contacts_carddav_security.py`,
`test_contacts_import_nonstring.py`, `test_contacts_routes_shim.py`,
`test_contacts_vcard_parse.py`, `test_history_compact_tool_calls.py`,
`test_history_db_fallback_hidden.py`, `test_history_display_model_hydration.py`,
`test_history_order_by_timestamp_regression.py`, `test_history_routes_shim.py`,
`test_history_topics_owner_scope.py`, `test_manage_notes_owner_gate.py`,
`test_note_reminder_email_oauth.py`, `test_note_reminder_fire_scope.py`,
`test_note_routes_shim.py`, `test_notes_dom_xss_helpers.py`, `test_notes_fail_closed_auth.py`,
`test_notes_search_reset_on_reopen_js.py`, `test_notes_select_esc_listener_js.py`,
`test_notes_update_due_date.py`, `test_notes_z_order_js.py` and `test_tool_rag_contacts_domain.py`)
— 75 passed.
`routes-rest-memory-personal-research.md` ran the sixteen suites matching its modules
(`tests/test_memory_owner_isolation.py`, `tests/test_memory_routes_session_owner.py`,
`tests/test_memory_routes_shim.py`, `tests/test_personal_delete_file_confinement.py`,
`tests/test_personal_dir_symlink_escape.py`, `tests/test_personal_remove_dir_confinement.py`,
`tests/test_personal_upload_isolation.py`, `tests/test_personal_upload_privilege.py`,
`tests/test_research_endpoint_owner_scope.py`, `tests/test_research_owner_scope_routes.py`,
`tests/test_research_report_read.py`, `tests/test_research_routes_path_confinement.py`,
`tests/test_research_routes_shim.py`, `tests/test_research_session_id_validation.py`,
`tests/test_memory_bullet_extraction.py` and `tests/test_memory_store_unreadable_no_wipe.py`) —
129 passed.
`routes-rest-media-files.md` ran the suites matching its modules (uploads, content detection,
embeddings, preferences, presets, drafts, signatures and speech) — **231 passed, 1 skipped**; the
section lists them. `src-research-scheduling.md` ran thirty-eight suites over its eleven files (the
background-job store, the research handler and engine, the scheduler, cleanup, the cookbook serve
reaper, the teacher-escalation and visual-report generators) — **168 passed**.
`routes-rest-integrations-misc.md` ran the fifty-seven suites matching its modules (webhook, hwfit,
compare, vault, diagnostics, search and cleanup) — **253 passed**.
`routes-models.md` ran the fifty-four suites matching `ls tests | grep -iE 'model|endpoint|ready'` —
**714 passed**.
`routes-chat-session.md` ran the fifty-five suites matching `ls tests | grep -iE 'chat|session'` —
**1 failed, 289 passed**. The failure is not a broken product path: it is the order-dependent
test named in that section's third finding, and it is reproducible only as a file pair (the two
files together fail; `tests/test_session_list_owner_scope.py` alone passes).
`routes-gallery-document.md` ran the forty-six suites matching
`ls tests | grep -iE 'gallery|document|image'` — **182 passed**.
`routes-skills-calendar-task.md` ran the sixty-six suites matching
`ls tests | grep -iE 'skill|calendar|task|ics'` — **319 passed**.
`routes-cookbook.md` ran the twenty-six suites matching `ls tests | grep -iE 'cookbook'` plus
`tests/test_task_cookbook_admin_gate.py` — **229 passed, 1 skipped**.
`routes-email.md` ran the forty-three suites matching `ls tests | grep -iE 'email|mail|imap|smtp'`
— **269 passed**.
`src-llm-core.md` ran the forty-four suites matching this surface (the `test_llm_core_*` files plus
the model-context, capability, endpoint-resolver, context-compactor, copilot and subscription
suites) in their natural order — **604 passed**; run in a non-alphabetical order the same 44 hang in
`tests/test_foreground_model_routing.py:2257` → `src/agent_loop.py:5572` → `_strip_think_blocks`,
which is that section's neighbour's leak, not a defect in the CI order.
`src-chat-session.md` ran the sixty-four suites matching
`ls tests | grep -iE 'chat|session|context|topic|compactor|request_models|assistant_log'` — **1
failed, 523 passed**, where the failure is the same order-dependent pair `routes-chat-session.md`
already reports, plus its four compactor suites (**41 passed**) and six neighbouring budget suites
(**25 passed**).
`src-documents.md` ran the forty-eight suites matching
`ls tests | grep -iE 'upload|document|markitdown|pdf|office|attachment|generated_image'` — **217
passed, 2 skipped**, the skips being the optional `markitdown` and `python-magic` imports.
`src-email-integrations.md` ran the thirty-two suites matching
`ls tests | grep -iE 'caldav|integrations|webhook|youtube|email_thread|carddav'` — **163 passed**.
`src-mcp.md` ran the eighteen suites matching `ls tests | grep -iE 'mcp'` plus
`tests/test_plan_mode.py` — **127 passed**.
`services-search.md` ran two sets: the thirty-three suites importing the module
(`grep -rl "services\.search\|src\.search\|services/search\|src/search" tests/*.py` plus
`tests/test_search_query_nonstring.py`) — **230 passed** — and the wider
`ls tests | grep -iE 'search|searxng|ddg|og_image|analytics|query|ranking|content'` set — 73 files,
**391 passed, 1 skipped**. The 74th file of that set, `tests/test_owned_document_query.py`, fails
collection inside the batch (`src.agent_tools` is not a package) and passes alone; its subject is
the document tools, so it is recorded and not reported.
`services-memory.md` ran the forty-nine suites matching `ls tests | grep -iE 'memory|skill'` —
**205 passed**.
`services-research.md` ran the forty-one suites matching
`ls tests | grep -iE 'research|docs|report'` — **245 passed**.
`services-hwfit.md` ran the twenty suites matching this module — **126 passed**.
`services-media.md` ran the twenty-three suites matching
`ls tests | grep -iE 'shell|stt|tts|youtube|face|kokoro|speech|audio'` — **150 passed**.
No other
suite was run.

Commands that *were* run are the small ones a finding cites — address-classifier comparisons, a
concurrency probe, an expression that raises. Each is recorded with its result under `Evidence` in
the finding that rests on it. The two shell findings that needed a process tree were checked with
throwaway scripts under `/tmp` that mirror `_create_shell`'s call shape; their output is quoted in
`routes-shell.md`, and they are not part of the target tree. Anything that could not be settled that
way says so in the finding.

Line numbers refer to `2992bf6d368a`. Use the quoted code to find a line after the code changes.

## Re-review, 2026-10-04

An independent pass over this run, made from the source at `2992bf6d368a` and not from the run's
prose. It changed ten severities, corrected the evidence of two findings, and removed none.

**Re-derived in full (5):** every finding rated high when the pass began. Each one's cited lines
were re-read and its conclusion reached again from the code; each carries a `Re-review` line
saying what was checked.

| Finding | Section | Before | After | Reason |
| --- | --- | --- | --- | --- |
| `manage_research` ignores the owner | `src-agent-tools` | high | high | Confirmed. The evidence said `can_use_research` disables the tool; `routes/chat_routes.py:1562-1563` only clears a flag, so the reach is every agent-capable user. |
| Codex and Claude email send never delivers | `routes-rest-agent-admin` | high | high | Confirmed at `routes/codex_routes.py:387`. |
| Concurrent memory writes lose entries | `src-memory-rag` | high | high | Confirmed. Added that the pin, edit and delete handlers run on worker threads, and that the loss rates were measured under a forced switch interval. |
| `app_api` blocklist bypass | `src-agent-tools` | high | medium | Confirmed, and a second bypass added (httpx collapses `/x/../api/tokens`). Lowered because the tool is admin-only, is blocked after untrusted content unless approved, and sits beside `bash`. Retitled; its ID changed. |
| Bearer callers share preferences, drafts and signatures | `routes-rest-media-files` | high | medium | Confirmed. Lowered because no shipped bearer client calls the three routers, so the shared bucket holds only third-party-client data. Disposition moved from `fix-now` to `next`. |

**Sampled (21 of 67 mediums):** the cited source was re-read for each. Thirteen stand at medium;
eight were lowered.

| Section | Finding | Result |
| --- | --- | --- |
| `src-security` | Web fetcher omits the carrier-grade NAT range | stands; measured again, `100.64.0.1` is not blocked |
| `src-security` | Privilege check skips itself when the lookup raises | medium to low: the only writer always stores a dict |
| `src-security` | Fernet keys generated without a lock | medium to low: one first-use window per install |
| `src-security` | Three private-address classifiers disagree | medium to low: its one consequence is counted above |
| `src-security` | Five undocumented SSRF variables | medium to low: a documentation gap over an intended default |
| `src-tools-parse-exec` | Uncaught `RecursionError` aborts the stream | medium to low: needs ~10,000 nested brackets, costs one turn |
| `src-tools-parse-exec` | `_strip_bare_invoke_markup` quadratic scan | medium to low: timings are for a 1 MB response |
| `src-tools-parse-exec` | Gemma pattern quadratic scan | medium to low: timings are for a 200-400 KB response |
| `src-email-integrations` | CalDAV host guard resolves once | medium to low: hostile user, rebinding DNS, blind response |
| `routes-chat-session` | Session list deletes every owner's incognito rows | stands |
| `routes-rest-integrations-misc` | Hardware-fit routes run SSH probes for non-admins | stands; the router has no admin dependency |
| `routes-rest-memory-personal-research` | Memory pin, edit, delete bypass the privilege | stands; only `:106-107` and `:346-347` call `require_privilege` |
| `services-search` | Google PSE key reaches the log and the response | stands; `HTTPStatusError` is not caught at `:487-501` |
| `core-data-platform` | `atomic_write_json` leaves stores at the umask default | stands; `data/auth.json`, `sessions.json` and `settings.json` are `-rw-r--r--` beside a `-rw-------` `app.db` |
| `src-tools-schema-index` | `tail_serve_output` missing from `TOOL_TAGS` | stands |
| `src-agent-tools` | `edit_image` calls four routes that do not exist | stands; no route matches |
| `src-agent-tools` | `manage_tokens` mints unusable tokens | stands |
| `src-agent-loop` | "on <word>" switches the toolset | stands; the regex is as quoted |
| `routes-cookbook` | MiniMax normalizer rewrites to a developer's home path | stands |
| `routes-skills-calendar-task` | Negative `scheduled_day` re-runs forever | stands |
| `services-media` | `yt-dlp` is not installed by any requirement file or image | stands |

**Not opened:** the other 46 mediums and all 118 lows the first pass recorded. They carry only
the first pass's evidence. No measurement script from the first pass was re-run except the four
`curl` probes and the address check named above. The 23 sections with no coverage statement were
not read by this pass either.

**Hypotheses this pass tested and rejected:**

- That the `app_api` bypass lets a prompt injection mint a token unassisted. `app_api` carries
  `ToolEffect.ADMIN_CHANGE`, which `ToolRunSecurityContext.decision_for`
  (`src/tool_capabilities.py:654-684`) blocks once untrusted content is in the run. This is why
  the finding is medium.
- That `trigger_research` shares `manage_research`'s missing privilege check. It posts to
  `/api/research/start`, and that route calls `require_privilege(request, "can_use_research")`
  and re-checks the impersonated owner (`routes/research/research_routes.py:496-504`).
- That a shipped client stores data in the shared bearer bucket. The `grep` in that finding
  returns nothing for `companion`, `swift`, `integrations` and `mcp_servers`.

## Hypotheses tested and rejected

Recorded so a later pass does not re-derive them. Each names the hypothesis and the evidence that
closed it.

- **"`can_use_bash` is offered in the admin UI but never enforced."** Not so. It is the only
  privilege in `DEFAULT_PRIVILEGES` that defaults to `False`, and it looked unenforced because a
  search for `require_privilege(..., "can_use_bash")` returns nothing. It is enforced on a
  different path: `routes/chat_routes.py:1552` reads `_privs.get("can_use_bash", True)` to build
  the disabled-tool set, and `tests/test_chat_route_tool_policy.py:264-287` covers both the
  privilege-denied case and the case where a caller sends `allow_bash=true` anyway.
- **"`running_in_container()` misses Podman, so `local_docker_available()` fails open and grants
  Docker access inside a container without the env var."** The detection is genuinely narrow — it
  tests for the literal tokens `docker`, `containerd`, and `kubepods` in `/proc/1/cgroup` — but it
  is not an authorization gate. `local_docker_available` is consumed only by
  `routes/cookbook_routes.py:335,350` to decide whether to *advertise* Docker features. The gates
  that decide who may use them are `host_docker_access_enabled`, called at
  `routes/shell_routes.py:1755` and `routes/cookbook_routes.py:2071`, and the documented opt-in
  overlay `docker/host-docker.yml` sets `ODYSSEUS_ENABLE_HOST_DOCKER=true` itself. A detection miss
  changes which features are shown, not who may use them.
- **"A misspelled privilege key at a call site silently permits the action."** Not currently. The
  four distinct keys used at `require_privilege` call sites — `can_generate_images`,
  `can_manage_memory`, `can_use_documents`, `can_use_research` — all exist in `DEFAULT_PRIVILEGES`
  (`core/auth.py:24-42`). The fail-open default (`privs.get(key, True)`) is still a hazard for the
  next call site, but no live call site is affected, so it is recorded here rather than as a
  finding.
- **"`src/tls_overrides.py` exposes a verify-off knob that could weaken TLS."** It does not. The
  module only *adds* an operator-supplied CA on top of the default trust store, states in its
  docstring that no verify-off knob exists and why, and pins its two permitted call sites with
  `tests/test_tls_overrides_scope.py`, which fails when the scope is extended without a written
  justification.
- **"The `prompt_security` guard markers can be forged by nesting, letting content escape the
  untrusted block."** Not by this path. `_escape_guard_markers` rewrites both markers before the
  block is assembled, and `GUARD_CLOSE` (`<<<END_UNTRUSTED_SOURCE_DATA>>>`) does not contain
  `GUARD_OPEN` (`<<<UNTRUSTED_SOURCE_DATA>>>`) as a substring, so the replacement order cannot
  reconstruct a marker from the other one. Input containing the already-escaped
  `<<<_UNTRUSTED_DATA>>>` survives unchanged and is inert, because it is not a marker the prompt
  treats as a delimiter.
- **"A chat-session approval grant can be forged through a client-supplied metadata blob."** The
  marker `_tool_approval_chat_session_granted` is trusted by `ToolRunSecurityContext.observe_messages`
  (`src/tool_capabilities.py:646`), but it is projected by
  `Session.get_context_messages()` (`core/models.py:153-180`) only when
  `_history_grants_chat_session_approval` verifies an HMAC over the session id, approval id, and
  decision (`core/models.py:41-76`). The two routes that persist caller metadata,
  `routes/session_routes.py:604` and `routes/history/history_routes.py:275`, both run the blob
  through `sanitize_client_message_metadata`, which drops the marker and `tool_events`. The
  remaining route that writes message metadata, `POST /api/inject_context`, builds it with
  `untrusted_context_message`, not from the request body. Rejected on that trace.
- **"The `_build_system_prompt` cache key omits `mcp_disabled_map`, so a disabled MCP tool keeps
  its prompt text."** Not a correctness issue: `_build_base_prompt` (`src/agent_loop.py:2850`) never
  reads the parameter, and the map is consumed after the cache block at `:2288` and `:2749`. The
  cache is inert for a different reason, recorded as a `PERF` finding in `src-agent-loop.md`.
- **"A tool budget hit mid-batch misaligns native tool calls with their results."** Not reachable:
  `_append_tool_results` bounds-checks both result lists (`src/agent_loop.py:3056`), and a budget
  hit breaks out of the round loop before another request is built, so no provider sees an
  unanswered `tool_call_id`.
- **"The `settings_scrub` masking gap is live."** Not established, and the finding is rated `low`
  accordingly. The gap is real and measured, but it needs a secret stored as a *container* under a
  secret-shaped key, and the settings shapes checked nest the other way. What would settle it is
  enumerating every value `/api/auth/settings` can return and testing each against
  `is_secret_key` at every depth; that requires reading the settings producer, which is assigned
  to another section.
- **"`do_app_api` can be turned into an SSRF by passing an absolute URL as `path`."** Not so. A
  value that does not start with `/` is prefixed with one (`src/tools/system.py:666-668`), so the
  request always goes to `_INTERNAL_BASE`, never to a caller-supplied origin. The percent-encoding
  bypass recorded above is a different mechanism and is a finding.
- **"`do_manage_research`'s id check can be walked out of the research directory."** Not by the
  path the tool accepts. The id is checked with `re.fullmatch(r"[A-Za-z0-9_-]+", rid)`
  (`src/tools/research.py:37-38`), which excludes `.`, `/`, and `\`, so `../settings` and
  `..%2f` do not reach the `data_dir / f"{rid}.json"` join. The owner-scoping defect recorded
  above is in the same function but is a different issue.
- **"`manage_tokens` list/delete cross the owner boundary."** Not as a privilege boundary. Both
  actions query `ApiToken` without an owner filter, so an admin's agent can list or delete any
  token; but `manage_tokens` is in `NON_ADMIN_BLOCKED_TOOLS` (`src/tool_security.py:61`), so only
  admins reach it, and the admin UI already exposes the same operations. The create path's broken
  output is a finding; the missing filters are noted here.
- **"`TodoWriteTool`'s session id can escape `data/agent_todos`."** Not so. `_safe_session_id`
  replaces every character outside `[A-Za-z0-9_.-]` with `_` and truncates to 120 characters
  (`src/agent_tools/coding_tools.py:11-13`), so separators cannot appear in the filename. The
  finding about this file is that nothing reads it, not that the path is unsafe.
- **"`install_package`'s pip allowlist is a command-injection path."** Not so. The value must equal
  a member of the `known` set exactly (`routes/shell_routes.py:1772-1793`), and the argv goes to
  `asyncio.create_subprocess_exec`, so no shell parses it. The defect recorded for the route is that
  it is unused and target-blind, not that it is injectable.
- **"The ssh host or the venv path in `list_packages` is shell-injectable."** Not so.
  `_ssh_base_argv` (`routes/shell_routes.py:82-94`) rejects a host that starts with `-` and passes
  the rest as one argv element to `create_subprocess_exec`; `_venv_activate_prefix` (`:96-108`)
  accepts only `[A-Za-z0-9_./~-]+` before leaving the value unquoted to expand `~`. Neither reaches
  a shell parser.
- **"The missing `_reject_cross_site` on the mutating shell endpoints is an exploitable CSRF."**
  Not established, and rated `low` FOOTGUN instead. The session cookie is `SameSite=Lax`
  (`routes/auth_routes.py:188`), so a cross-site POST carries no session, and a Pydantic body
  requires `application/json`, which a cross-site HTML form cannot send. What would settle it is a
  deployment that sets `SameSite=None` or adds an allowed origin; the finding records the placement
  gap, not an exploit.
- **"`_normalize_legacy_remote_tmux_exec` re-quotes a command in a way that changes its meaning."**
  Not established as a defect. It rewrites only admin-supplied `ssh ... tmux ...` commands, uses
  `shlex.split`/`shlex.join` round-tripping, and returns the original unchanged for anything it does
  not recognize (`routes/shell_routes.py:514-547`).

- **"`_result_has_work`'s zero-count guard discards a run that did process mail."** Not for the
  callers that use it. The guard returns false when a result contains `" 0"` twice together with
  `tagged`, `moved`, or `drafted` (`src/builtin_actions.py:1046-1048`). Reading the producer
  (`routes/email_pollers.py:1320-1356`) shows each scheduled action requests one output at a
  time — `summarize_emails` asks for `summary` only, `draft_email_replies` for `reply` only,
  `extract_email_events` for `calendar` only — so a processed run's string carries at most one
  `" 0"` token (`summarized 0` or `drafted 0`), and `processed 0` is never emitted (the part is
  omitted when zero). The guard is not reached by a real run.
- **"`action_learn_sender_signatures` crashes when a cached row has no `last_built_at`."** Not
  possible: the comparison `cached.get(addr, "") > cutoff_iso` (`src/builtin_actions.py:1667`)
  would raise on a `None`, but the column is `last_built_at TEXT NOT NULL`
  (`routes/email_helpers.py:644`) and every insert writes a timestamp (`:1728-1734`).
- **"`_parse_gemma_tool_call`'s key-value fallback regex is quadratic through the parser."** The
  regex itself is quadratic on a body with no `}` (10.4s for a 40 KB body), but the function is
  only reached with the `_GEMMA_TOOL_CALL_RE` capture, whose `(\{[\s\S]*?\})` guarantees the
  body ends at a `}`; with one present the first `finditer` match succeeds in one linear pass,
  and the end-to-end parse of a 40 KB Gemma call is 0.001s. The reachable quadratic in that
  pattern is the opener flood, which is a finding.
- **"`format_tool_result`'s `success` branch raises `KeyError` on `path`/`size`."** It would,
  for a `{"success": True}` result without those keys, but no tool handler returns a `success`
  key at the snapshot: a search over `src/agent_tools/`, `src/tool_implementations.py`, and
  `src/ai_interaction.py` finds none, so the branch is unreachable and is not a finding.
- **"`format_tool_result` raises `TypeError` on a list-valued `results`."** Every tool-result
  producer returns a string for `results`; the list-valued returns are HTTP payloads
  (`routes/search/search_routes.py`, `routes/contacts/contacts_routes.py`,
  `routes/model_routes.py`) and a scheduled-action result (`src/builtin_actions.py:2082`), none
  of which is passed to the formatter.
- **"`execute_tool_block` binds an unvetted workspace."** The only production callers pass the
  value the route vetted through `vet_workspace` (`routes/chat_routes.py:370-371` and `:1224`),
  and the exact-approval path re-vets the sealed workspace (`src/tool_execution.py:883`). The
  missing check in the dispatcher is defense-in-depth, not a live gap.
- **"The `_MCP_TOOL_MAP` fallback also drops `owner`, so a fallback tool loses its scoping."**
  Checked every handler on that map: bash reads `session_id`, the subprocess and web tools read
  `progress_cb`/`subproc_env`, and `read_file`/`write_file` read no `ctx` keys at all. Only the
  dropped `session_id` has an effect, and that is the tmux finding.
- **"`edit_file`/`grep`/`glob`/`ls` lose session or owner like bash does."** Their handlers in
  `src/agent_tools/filesystem_tools.py` contain no `ctx` reads, so the dispatch omitting those
  keys changes nothing.
- **"`web_search` stays available after external context, so an injected page can exfiltrate
  workspace reads through the query."** Allowed deliberately: the gate's own test keeps
  `web_search` available and blocks only `web_fetch`, the tool whose URL the model chooses
  (`tests/test_external_context_tool_gate.py:332-351`). The query goes to the fixed configured
  provider, not an attacker-chosen origin, so the residual exposure is the provider's logs
  rather than a controllable endpoint. Recorded as a design decision, not a finding.
- **"`web_fetch` is in the plan-mode allowlist, so plan mode can still egress."** Deliberate:
  `PLAN_MODE_READONLY_TOOLS` (`src/tool_security.py:103-145`) is an allowlist of
  read/inspection tools, and plan mode constrains mutation, not network reads. The same
  allowlist keeps `chat_with_model` and `ask_teacher`.
- **"The browser MCP's `--no-sandbox` default is an unguarded hardening failure."** Deliberate
  and pinned by tests: `tests/test_builtin_mcp_npx_cache.py:62` asserts the flag is present and
  `:90` asserts `ODYSSEUS_BROWSER_NO_SANDBOX=0` removes it. It is a policy choice with an
  opt-out, so it is recorded rather than reported; the missing cache gate next to it is not
  tested and is a finding.
- **"`_is_npx_package_cached`'s `subprocess.run` fallback blocks the event loop."** The fallback
  runs only when `asyncio.create_subprocess_exec` raises `NotImplementedError`, the Windows
  event-loop case the branch exists for, and it is capped at five seconds and covered by
  `tests/test_builtin_mcp_npx_cache.py:130`. Not reachable on the POSIX deployment path.
- **"A mutating `manage_*` action is classified read, letting it past the post-context gate."**
  Diffed every handler's action dispatch against `_PRIVATE_ACTION_READS` /
  `_PRIVATE_ACTION_WRITES` (`src/tool_capabilities.py:318-368`): the sets match, and any
  unlisted action falls to the fail-high READ+WRITE branch (`:520-528`). `manage_skills`
  `index` is a read alias for `list` (`src/tools/system.py:62`), not an index rebuild.
- **"An unknown MCP tool is classified from its bare suffix after `mcp__email__`."** Only a
  name in `BUILTIN_EMAIL_TOOLS` is aliased (`src/tool_capabilities.py:294-299`); every other
  `mcp__*` name returns the unknown fail-high capabilities, which is what
  `tests/test_external_context_tool_gate.py:357` asserts.
- **"A fence-callable tool can be missing from both the plan-mode denylist and the
  allowlist."** Computed `TOOL_TAGS - plan_mode_disabled_tools() - PLAN_MODE_READONLY_TOOLS` at
  the snapshot: empty (77 fence tags, 54 denied, the rest allowlisted). The seven
  fence-taggable tools with no native schema (`draft_email`, `draft_email_reply`,
  `ai_draft_email_reply`, `download_attachment`, `generate_image`, `manage_research`,
  `search_emails`) are all covered by the static mutator backstop or the allowlist.
- **"Every fence-callable tool with no native schema is reachable another way."** The
  seven names in the plan-mode bullet were re-checked for native reachability in
  `src-tools-schema-index.md`. Six are XML-only by design or have a native substitute
  (`reply_to_email`'s schema redirects drafts to `ui_control action=open_email_reply`;
  `generate_image` is named as XML-invocable at `src/tool_security.py:135`); `manage_research`
  is the finding.
- **"`generate_image`'s missing schema is the same gap as `manage_research`'s."** Not
  reported: `src/tool_security.py:134-141` names `generate_image` as an example of a tool that
  is only XML-invocable, and `reply_to_email`'s schema explicitly redirects drafting to
  `ui_control action=open_email_reply`, so the fence-only status of the other six is a
  documented pattern. `manage_research` differs in that the prompt routes *all* models to it
  for a shipped flow. (The same comment's `manage_notes` example is stale — `manage_notes`
  has had a schema since the registry migration — but a stale example in a comment is not a
  finding.)
- **"The `_REQUIRED_NATIVE_TOOL_ARGS` guard catches a non-string required argument."** It
  does not: it coerces with `str(args.get(key) or "").strip()`, so `{"query": {"q": "x"}}`
  passes and the dict reaches the handler. That is the mechanism of the converter finding,
  not a defense against it.
- **"The other multiplexed tools' enums drift from their handlers the way
  `manage_documents` and `manage_session` do."** Compared each enum with its handler's
  `action ==` / `action in (...)` branches: `manage_notes`, `manage_memory`, `manage_tasks`,
  `manage_calendar`, `manage_contact`, `manage_skills`, `manage_research`, `ui_control` and
  `edit_image` all match exactly. Only the two reported tools drift.
- **"A `tail_serve_output` native call reaches the dispatcher by some other route."**
  `function_call_to_tool_block` is the only native-to-`ToolBlock` converter (every parser
  entry point delegates to it), it returns `None` for a name outside `TOOL_TAGS` before the
  dispatch, and `FUNCTION_TOOL_SCHEMAS` is a static list with no runtime additions
  (`grep -rn 'FUNCTION_TOOL_SCHEMAS' src/ routes/` finds only reads).
- **"`list_email_accounts`'s `"properties": {},` trailing comma is a syntax defect."** It is
  a valid trailing comma in a dict literal; the module imports.
- **"`ToolIndex._fingerprint` gates the index rebuild."** Nothing reads it (`grep -rn
  '_fingerprint' src/ tests/` finds only the two assignment sites), so the rebuild decision
  does not consult it. Reported as dead code, not as a broken rebuild.
- **"`get_active_email` has an out-of-tree caller."** `tests/test_tool_implementations_shim.py:49-51`
  documents it as a facade-compatibility symbol with no in-repo importer. The *global* still
  has no reader, which is the reported finding.
- **"The `message_count` column's drift hands the model a truncated transcript or inflates the
  displayed total."** Not in the reviewed code. `get_session` reconciles the cached count
  against the real `chat_messages` rows before its hydration gate
  (`core/session_manager.py:441`, `:486-491`), `load_sessions` recomputes the count for its
  discovery set (`:103-113`), and `tests/test_history_display_model_hydration.py` covers both
  drift directions (`test_inflated_message_count_column_does_not_reload_warm_sessions`,
  `test_stale_low_message_count_column_still_hydrates_for_the_model`) plus the empty-cache fork
  (`test_fork_after_restart_copies_the_real_transcript`).
- **"`require_admin`'s raw `X-Odysseus-Internal-Token` check is a remote admin bypass."** It is
  weaker than `app.py`'s check (which also requires a direct loopback client,
  `app.py:348-362`), but the middleware always runs first and rejects a non-loopback header
  before the route is reached; the auth-exempt paths (`app.py:265-289`) contain no
  `require_admin` call site (`grep -rn 'require_admin' routes/`). `specs/auth-security.md`
  documents the raw-header trust as intended ("`require_admin()` trusts the stamped sentinel or
  raw internal header and should be used behind equivalent middleware control").
- **"`get_sessions_for_user(None)` returns every owner's sessions to an unauthenticated
  caller."** `effective_user` (`src/auth_helpers.py:15-36`) resolves every request that passed
  the middleware to a cookie user or a token owner; it returns `None` only when no middleware
  stamped state, which is the documented `AUTH_ENABLED=false` / `LOCALHOST_BYPASS` single-user
  mode.
- **"`AuthManager.delete_user` and `rename_user` leave the affected user's API tokens live."**
  `delete_user` deletes the owner's `ApiToken` rows and fails closed if that store is
  unavailable (`core/auth.py:301-317`); the rename route updates every `Base.registry` model
  that has an `owner` column, `ApiToken` included (`routes/auth_routes.py:432-441`).
- **"`AuthManager.change_password` leaves a stolen cookie valid."** The route revokes the user's
  other sessions with `revoke_user_sessions` and keeps only the caller's token
  (`routes/auth_routes.py:238`).
- **"`SecurityHeadersMiddleware`'s per-request nonce is never used, so the CSP blocks the app's
  inline scripts."** `static/index.html` and `static/login.html` carry `{{CSP_NONCE}}`
  placeholders that `src/app_helpers.py:47` substitutes from `request.state.csp_nonce`.
- **"`SessionManager.archive_session` and `mark_important` are the archive/important paths."**
  Neither has a caller; the two routes write the DB directly behind owner checks
  (`routes/session_routes.py:730-797`, `:967-1003`). They are noted here rather than reported:
  while unused they do nothing wrong, and `archive_session` would no-op for a session outside
  the cache, which is the same cache-shaped hazard as the reported `save_sessions` finding.
- **"The ssh port in `core/platform_compat._ssh_exec_argv` is an argument-injection path."** The
  helper casts the port into `-p <value>` without validating it, so a value such as
  `-oProxyCommand=...` would be parsed by ssh as an option. Not reachable from the application:
  both call sites validate the port with `validate_ssh_port` (`routes/_validators.py:23-31`)
  before it reaches the helper — `routes/hwfit_routes.py:190`, `:204`, `:331`, `:417` all pass
  through `_validate_detection_target` (`:21-25`), and `services/hwfit/hardware.py:35` only sees
  values those routes stored. The missing check in the helper is defense-in-depth, not a live
  gap.
- **"The OAuth token columns are a missing-encryption defect like MCP env."** Documented and
  deliberate: `specs/persistence.md:99` states that email passwords and Google OAuth
  access/refresh tokens are `String` columns encrypted and decrypted manually, and that "legacy
  plaintext rows are tolerated until migration or rewrite". The writers encrypt, and any rewrite
  migrates the row. It is the MCP `env` column, absent from that list, that is reported.
- **"The `Integration` model is a second integrations store that has drifted."** It is dead
  schema, not a live divergence: `grep -rn 'Integration' routes/ src/ core/` finds no reader or
  writer of the ORM class (the hits are unrelated strings and HTTP error messages), and the live
  store is `data/integrations.json` via `src/integrations.py`, which the spec's JSON list names.
  `create_all` still creates the table. Noted rather than reported: an empty table has no
  behaviour to get wrong.
- **"`src/service_health.py`'s report leaks credentials through probe errors or endpoint URLs."**
  Not by the paths checked. `_classify_error` never returns the exception text (its comment names
  the reason: `httpx`/`imaplib` messages can embed the target URL), `_safe_url` strips the query
  and the userinfo before a URL reaches the report, and `_label` sanitizes endpoint names; the
  six `tests/test_service_health_*.py` suites pin the response shapes. What the module *does*
  return raw is the readiness probe's error text, in `src/readiness.py`, which is reachable only
  by an authenticated caller — noted in the section rather than reported.
- **"`_bounded_map` leaks worker threads when a probe hangs."** Not materially. Each probe
  carries its own socket-level timeout (`_imap_connect(..., timeout=4)`, `httpx.get(...,
  timeout=4)`), so a worker cannot outlive its budget by much; the map's own timeout decides what
  the report *says* about the stragglers, and `ex.shutdown(wait=False)` returns without waiting
  for them. The thread count stays bounded by the probe concurrency.
- **"The front-end persona list has drifted from `src/reminder_personas.py`."** Not today: the
  five IDs in `static/js/presets.js:32-69` (`socrates`, `razor`, `nietzsche`, `spark`,
  `odysseus`) are exactly the five keys of `PERSONAS`. No test pins the parity, so the next edit
  to either list is unguarded — a hazard, not a defect.
- **"The unused helpers in `src/app_helpers.py` are a reachable path."** They are not reachable:
  `read_if_exists` and `file_to_data_url` have no caller anywhere in `src/ routes/ core/ services/
  app.py`, so the unbounded `f.read()` inside `file_to_data_url` has no consumer. Noted as dead
  code rather than reported.
- **"The first-run setup race lets two callers both create the admin account."** Not so.
  `AuthManager.setup` re-checks `is_configured` under `self._setup_lock` before creating anything
  (`core/auth.py:257-260`), and `create_user` takes `_config_lock` and refuses an existing
  username (`:270-272`), so the second caller gets `False` and a 500/409 rather than an overwrite.
- **"`rename_user` leaves file-backed owner references behind."** Traced every store the route
  touches: the prefs `_users` key (`routes/prefs_routes.py:39-44` is the shape the migration
  renames), `deep_research/*.json`, `memory.json`, the upload handler's owner map and index keys,
  personal RAG directories and vector metadata, `SKILL.md` frontmatter plus `_usage.json` keys,
  the in-memory session cache and the bearer-token cache. The remaining risk is that each file
  migration is wrapped in a `try/except` that logs and continues, so a failed one returns 200 with
  the rename half-applied — noted, not reported, because the DB half is transactional and the
  alternative (failing after the auth store changed) is worse.
- **"The Danger Zone's chats wipe mirrors `/api/sessions/all` as its docstring says."** It does
  not: `/api/sessions/all` deactivates the gallery rows for the deleted sessions and unlinks their
  generated files (`routes/session_routes.py:694-715`), while the wipe deletes the session and
  message rows only. The wipe's own modal text — "Every session, message, and chat history.
  Documents/notes/etc. stay." (`static/index.html:2464`) — makes the narrower behavior deliberate,
  so the stale word is "mirrors" in the docstring, not the code.
- **"The backup import's memory merge is a lost-update race."** The read-modify-write is real
  (`routes/backup_routes.py:100-124` loads a snapshot with `load_all_for_update` and writes it back
  with `save`, and `src/memory.py:261-278`'s `save` takes no lock — the module has no lock at all),
  so a concurrent memory write between the two is lost. Not reported here because the missing lock
  is `src/memory.py`'s, which is assigned to `src-memory-rag`; this section only shows one caller.
- **"A read-scoped todo token can perform a write."** Not so. `routes/codex_routes.py:35`'s
  `WRITE_ACTIONS` is a superset of the actions that actually write in the callee: `do_manage_notes`
  handles list/search/find, view, add, update, delete and toggle_item
  (`src/tools/notes.py:88-327`), and the only aliases it resolves
  (`src/tools/notes.py:34-41`) are create/new/save/remind → add, remove → delete and
  remove_item → toggle_item, all six of which the route already classifies as writes. An unknown
  action falls through to the read set and the callee answers "Unknown action".
- **"A cookie-session caller can reach the cookbook surface without admin."** Not so.
  `_require_cookbook_scope` (`routes/codex_routes.py:117-127`) adds `require_admin` for every
  caller that is not an API token, and `tests/test_codex_cookbook_admin_gate.py` pins it.
- **"`/api/codex/capabilities` and `/api/assistant/available-timezones` are unauthenticated
  endpoints."** Neither handler checks identity, but neither is reachable unauthenticated:
  `/api/codex` is not in `AUTH_EXEMPT_EXACT` or the exempt prefix and pattern lists
  (`app.py:265-292`), and neither is `/api/assistant`, so `AuthMiddleware` rejects the request
  before the handler runs. Both payloads are static — a capability table plus the caller's own
  token scopes, and the IANA timezone list — so there is nothing to scope.
- **"A non-admin can grant the assistant admin-only tools by writing `enabled_tools`."** Not so.
  The list is stored as given (`routes/assistant_routes.py:184`), but what a caller may actually
  invoke is decided in the dispatcher from `blocked_tools_for_owner`
  (`src/tool_security.py:267-271`, returning `NON_ADMIN_BLOCKED_TOOLS`), so naming `bash` or an
  email tool in the assistant's list does not make it callable for a non-admin. The
  `allow_autonomous_email` toggle edits the same list.
- **"The MCP OAuth path confinement can be escaped."** Not so. `_resolve_mcp_oauth_path`
  (`routes/mcp/mcp_routes.py:29-52`) expands, resolves symlinks with `Path.resolve(strict=False)`
  and then requires `relative_to(base)`, so both `..` segments and a symlink pointing out of
  `mcp_oauth` raise 400; `add_server` confines the caller's `dir` and `filename` through the same
  helper.
- **"`_redact_task` misses a secret the cookbook stores in a task."** Not so for the keys the
  launcher writes. `ServeRequest` and the download request carry the Hugging Face token as
  `hf_token` (`routes/cookbook_helpers.py:1060-1090`), which `_redact_task` strips at the top level
  and inside `payload` (`routes/codex_routes.py:566-573`), and `codex_cookbook_servers` drops the
  ssh credential fields explicitly.
- **"The `sys.modules` shim for `routes.mcp_routes` breaks importers or monkeypatching."** Not so.
  The shim replaces its own entry with the canonical module object (`routes/mcp_routes.py:15`), so
  attribute access, `monkeypatch.setattr`, `importlib.import_module` and re-import all reach one
  object; `tests/test_mcp_routes_shim.py` pins it.
- **"`_as_owner` leaks the substituted identity into other requests."** Not so. It restores
  `request.state.current_user` and `api_token` in a `finally`
  (`routes/codex_routes.py:82-100`), and Starlette builds a fresh `Request` and state per request,
  so the substitution is confined to the inner call.
- **"The flat `*_routes.py` shims diverge from their canonical modules."** Not so for the three in
  this section: `routes/note_routes.py`, `routes/contacts_routes.py` and
  `routes/history_routes.py` each replace their own `sys.modules` entry with the canonical module
  object, so every import path reaches one object. A probe confirmed all three identities.
- **"Contacts leak across owners."** Not so. Contacts are a shared, admin-only address book rather
  than a per-owner store: every route in `routes/contacts/contacts_routes.py` is gated by
  `Depends(require_admin)` (`:741`, `:812`, `:835-838` and the rest of the family). The section's
  Overview was corrected to say so.
- **"The notes list endpoint shows rows the id-based operations refuse."** Not so. The list filters
  by owner and the id-based operations reject a mismatched or null owner for an authenticated
  caller, so the two directions agree.
- **"History message edit and delete reach another owner's rows."** Not so. Session ownership is
  verified before the message is touched, and the edit and delete queries constrain the session id
  as well as the message id.
- **"Topic analysis leaks across owners."** Not so. `src/topic_analyzer.py`'s entry point requires
  an owner, filters strictly on it, and returns an empty result when it is absent.
- **"An explicit history page size is unbounded."** Not so. Supplied limits clamp to 1–100; the
  no-limit full-history mode that remains is deliberate and reached only when the caller asks for
  the whole history.
- **"A CardDAV href or UID can escape the configured origin."** Not so on the reading: hrefs are
  pinned to the configured origin, UID path segments are quoted, and the base URL is validated.
  DNS rebinding against the configured host was not established either way — the reviewer recorded
  it as unverified rather than as a finding.
- **"Non-string import fields or a null contact name crash the importer."** Not so. The import
  fields are coerced, the null-name path has a fallback, and the typed contact endpoints answer 422
  for an array or string body (unlike the nine raw-body endpoints reported in this section's own
  finding).
- **"The history module's compaction timestamp ordering is a shipped defect."** It is not reachable.
  The compaction implementation in `routes/history/history_routes.py` is shadowed by the session
  router's handler, which is registered first, so the history copy never runs; the reviewer
  confirmed the selection with a request-level probe that replaced the session handler's owner
  check with an HTTP 418 sentinel and saw the sentinel returned. Worth knowing before anyone edits
  that copy.
- **"Memory reads, edits and deletes lack owner checks."** Not so, and the distinction matters for
  that section's privilege finding: the load is filtered and each id-based operation calls an
  explicit owner check before mutating, so the missing piece there is the feature privilege, not
  owner isolation.
- **"Session-keyed memory operations expose another user's chat."** Not so. Session ownership is
  verified for both extraction and metadata access.
- **"Research report reads and deletes lack owner checks."** Not so. The disk path and the
  active-task path each gate on the owner, and the focused owner-scope suites pass.
- **"Research identifiers permit traversal or symlink escape."** Not so. The identifier is
  validated and the resolved path is confined, which
  `tests/test_research_routes_path_confinement.py` and
  `tests/test_research_session_id_validation.py` pin.
- **"Personal global listings expose data to ordinary users."** Not so. Listing and directory
  management depend on the administrative privilege, and uploads derive their ownership from
  authenticated request state rather than the body.
- **"Personal deletion or directory management escapes the filesystem boundary."** Not so.
  Resolved-path checks reject it and the confinement suites pass; removing a directory from the
  global vector index remains an administrative operation.
- **"The flat `*_routes.py` shims diverge from their canonical modules."** Not so here either: the
  alias-identity and monkeypatch suites pass for `routes/memory_routes.py` and
  `routes/research_routes.py`.
- **"The non-object-body error recurs in this section."** It does not. All four JSON-body routes
  in these files answer 422 for an array or a string, because each takes a Pydantic model rather
  than calling `request.json()` — the reviewer measured both bodies against all four.
- **"A research launch discards its background work."** Not so. The live handler creates the
  asyncio task, retains it, and handles cancellation, timeout and error recovery.
- **"A memory entry without `text` can be persisted, so every reader that indexes `entry['text']`
  raises."** No caller can build one. `MemoryManager.save` would accept such an entry —
  `_validate_entries` fills `id`, `timestamp`, `source` and `category` but not `text`
  (`src/memory.py:214-230`) — so the readers that index it (`find_duplicates`, `:316-321`,
  `categorize_memory_by_relevance`, `:323-357`, `get_relevant_memories`, `:359-457`) would raise
  `KeyError`. But the import endpoint returns LLM suggestions rather than saving them, and every
  accept path goes through `add_entry`, which raises on empty text (`:283-285`). A hand-edited
  store can still produce the crash; no reachable writer does.
- **"Excluding a file from the personal library hides it from the listing but not from
  retrieval."** Rejected on the caller: the only caller of `exclude_file` is the delete-file route,
  which removes the chunks first (`rag.delete_by_source(filepath)`) and writes the exclusion after
  (`routes/personal_routes.py:414-446`), so the vector rows are gone before the exclusion exists.
- **"`PersonalDocsManager.refresh_index()` re-reads and re-extracts every tracked file on every
  request."** Rejected on construction and offload: the manager is a single instance built at app
  init (`src/app_initializer.py:84`), and both callers run the refresh in a threadpool
  (`routes/personal_routes.py:196-197`, `:236-238`), so the re-extraction is neither per-request
  nor on the event loop.
- **"The hybrid ranking is invalid because it orders candidates from two embedding spaces by one
  score."** Not reported. `VectorRAG.search` merges the custom and fastembed lanes' hits and sorts
  them by a score computed in each lane's own vector space (`src/rag_vector.py:377-395`). The
  effect is bounded — both lanes hold the same rows, so `dedupe_results` collapses them, and the
  cross-space comparison only decides which of two near-identical rows survives and how distinct
  documents interleave — and no measurement produced a user-visible ordering error, so it is not a
  finding.
- **"`VectorRAG._embed` disagreeing with `_collection` is a live defect."** It is latent, not live,
  and is reported as a `FOOTGUN` for that reason: `grep` over `routes/`, `src/`, `mcp_servers/`,
  `core/` and `app.py` finds no external caller of either, and `_embed` has no caller at all.
- **"The memory store's non-atomic write is already covered, so the concurrent-write defect is a
  duplicate."** The two are different halves of one file. `core-data-platform` reports the hourly
  owner sweep rewriting `memory.json` with a plain truncating write
  (`core/database.py:1481-1482`), which is a durability defect that needs a crash inside the write
  window; `src-memory-rag` reports the lock-free read-modify-write and the shared `memory.json.tmp`
  (`src/memory.py:275-278`), which loses data with no crash at all. Both are findings; neither
  subsumes the other.

- **"Session cleanup can archive or delete every user's sessions, because `owner=None` skips the
  filter in `_apply_owner_filter`."** Not reachable. Both routes pass the authenticated user
  (`routes/cleanup/cleanup_routes.py:30,48`); the auth middleware answers 401 to any
  unauthenticated `/api/` request (`app.py:497-501`), and a bearer caller is stamped with the
  pseudo-user `"api"` (`app.py:459`), which owns no sessions, so the unfiltered branch is only
  the single-user/no-auth deployment where all sessions belong to the one operator.
- **"Deleting old sessions orphans their chat messages, because a bulk `query.delete()` bypasses
  ORM cascades."** The database cascades instead: `chat_messages.session_id` declares
  `ForeignKey("sessions.id", ondelete="CASCADE")` (`core/database.py:265`) and the engine sets
  `PRAGMA foreign_keys=ON` on every SQLite connect (`core/database.py:140-146`).
- **"Cleanup can delete a session with many messages because the denormalized `message_count` is
  stale."** The column is maintained on load, add, truncate and save
  (`core/session_manager.py:100-118,214-218,240,288-290,332-334,399-407`), and the preview and the
  delete path read the same column with the same predicate (`src/cleanup_service.py:98-107,178-186`).
- **"The report page's Sources panel builds `href` from a source URL with no scheme whitelist, so
  a `javascript:` URL would execute under the report's `script-src 'unsafe-inline'` CSP."** No
  non-http(s) URL can reach `sources[].url`. Findings only exist for URLs that fetched
  successfully (`src/deep_research.py:618-621` returns `None` when the fetch fails), the model's
  own `url` field is overwritten with the fetched URL (`:647`), and every finding URL originates
  in a provider result (`:525-530`) that `fetch_webpage_content` must then fetch over http(s)
  (`services/search/content.py:220-228`). The front end already whitelists the same field
  (`static/js/research/panel.js`, guarded by `tests/test_research_source_link_xss.py`), so the
  renderer's missing whitelist is defense-in-depth rather than a live path.
- **"The report's `category` field is injectable into the page."** It reaches only two sinks:
  `body_class` is `html.escape`d, and `_category_css` looks the value up in a static `styles`
  dict (`src/visual_report.py:1521,1673-1675`) instead of interpolating it. `category` arrives
  unvalidated from the request body, and `tests/test_security_regressions.py:1256-1276` covers
  both the escape and a non-string value.
- **"The scheduler fires tasks at the wrong local time or in the wrong timezone."** Every
  comparison is naive UTC (`_utcnow`, `src/task_scheduler.py:22-24`); local wall-clock
  interpretation happens only when the task's CrewMember has a timezone, and it converts back to
  naive UTC before storage (`:120-165,233-243`).
- **"A task that raises never runs again, or busy-loops on its stale `next_run`."** The error
  path advances `next_run` explicitly for that reason (`src/task_scheduler.py:1119-1135`), and if
  its commit fails a fresh session pushes `next_run` five minutes forward and aborts the run row
  (`:1145-1163`).
- **"The scheduler dispatches the same due task twice."** `_check_due_tasks` adds each id to
  `_executing` under `_executing_lock` before dispatching and excludes the snapshot from the
  query; `_execute_task` discards the id in its `finally` (`src/task_scheduler.py:700-733,790-810`).
- **"`run_task_now` is an unguarded trigger, so one user can run another user's task."** All
  three call sites authorize first: owner check plus admin gate (`routes/task/task_routes.py:859-866`),
  webhook token (`:1055-1064`), owner filter (`routes/assistant_routes.py:275-285`).
- **"`is_low_quality`'s phrase markers drop legitimate findings."** Real but not a finding: the
  markers are phrase-level on purpose (`"not relevant to"`, `"does not contain"`), the bare
  tokens that caused the worst false positives were already removed
  (`src/research_utils.py:33-56`), and a false positive only narrows a report instead of corrupting
  it.
- **"`bg_jobs.launch` leaks a zombie per job because the `Popen` handle is dropped."** CPython's
  `Popen.__del__` appends a still-running child to the subprocess module's `_active` list, which
  the interpreter reaps at exit; the child is also `setsid`-detached, so it is not a live process
  leak (`src/bg_jobs.py:150-165`).
- **"The non-object-body 500 class from `routes-rest-auth-admin` recurs in the remaining route
  modules."** It does not. A probe sent `[]` and a string to the five typed endpoints in
  `routes-rest-integrations-misc` (vault config/login/unlock, compare record, sync chat) — all
  answered 422 — and the two search endpoints answered 200 with their missing-query error, because
  each takes a Pydantic model or validates the body before use.
- **"The ten flat `*_routes.py` shims in that section are second implementations."** All ten
  aliases are identical to their canonical module objects.
- **"The outgoing-webhook, vault or diagnostics routers are reachable without an admin
  credential."** Management handlers call `require_admin`, `/api/v1/chat` additionally requires a
  chat-scoped API token, and none of the seven routers is auth-exempt. The only exempt path is the
  task receiver, whose handler checks the stored token and the task's active status before asking
  the scheduler to run it; it uses a reusable URL credential rather than a timestamped signature,
  so replay was not tested (`routes/task/task_routes.py:1040`+).
- **"Session cleanup archives or deletes another user's rows."** The owner comes from request
  state, and `src/cleanup_service.py` applies owner filters to archival, to the deletion
  candidates, and to the protected recent-session set; messages cascade from the session row.
  Ancillary file and table cleanup was not established.
- **"Concurrent preference PUTs interleave inside the read-modify-write on one event loop."** An
  AST check found no `await` in `set_pref` or `_save_for_user`, so the operation does not suspend
  mid-way on a single loop; safety across workers or other threaded writers is not established.
- **"A non-admin can register or probe a model endpoint, so the stored key reaches a
  caller-chosen URL (SSRF)."** No. Every probe and registration route in `routes/model_routes.py`
  calls `require_admin` (fifteen sites from `:1683` to `:2664`); the only ungated routes are
  `GET /api/models`, `GET /api/default-chat` and `GET /api/tools`; `manage_endpoints` is in
  `NON_ADMIN_BLOCKED_TOOLS` (`src/tool_security.py:58`); and the cookbook serve registration that
  also writes rows is admin-gated (`routes/cookbook_routes.py:1972`). Every probe pairs a row's
  key with that same row's URL, and the one caller-supplied key (`probe_selected`) is admin-only
  and never combined with a stored key.
- **"Model endpoints echo the stored API key back on read, or leak another owner's config."**
  Neither. The list and create responses return `has_key` plus an 8-hex sha256 fingerprint
  (`routes/model_routes.py:1370-1376`), never the value; `_fetch_models` and `get_default_chat`
  filter non-admins through `owner_filter`, the admin flag is part of the picker cache key, and
  every by-id route is admin-gated.
- **"One of the model routes is unauthenticated, or `require_admin` fails open on an unconfigured
  instance."** No. None of them appears in `app.py`'s exempt lists, and `AuthManager.is_configured`
  is a property (`core/auth.py:238-240`), so the gate answers 403.
- **"A non-admin can force a global endpoint probe with `/api/models?refresh=true`."** Reachable,
  but not reported: the shipped picker itself calls it that way (`static/js/models.js:202`), and
  the effect is re-probing stored endpoints with their own stored keys.
- **"The UI's own add-endpoint form stores a query URL."** No. `_normalizeBaseUrl` strips `?` and
  `#` before posting (`static/js/admin.js:984`); the markdown add-to-picker button is the reachable
  path, and the finding says so.
- **"`GET /api/tools` is a privilege leak, and `_delete_orphaned_provider_auth(exclude_ep_id=None)`
  deletes a still-referenced auth row."** Neither holds. The tool list is authenticated-only and
  returns names and disabled flags; the orphan sweep's only call site passes the deleted endpoint's
  id, so the `id != NULL` no-match case is unreachable.
- **"A mutating chat or session endpoint touches a row the caller does not own."** No. All eight
  chat endpoints and all eighteen session endpoints resolve the session through
  `_verify_session_owner` first (or `require_admin` for the all-sessions wipe); the unfiltered
  incognito purge is the one exception, and it is that section's first finding.
- **"`GET /api/search` leaks other owners' messages."** No: the call passes `owner`, a
  `restrict_owner` flag, and `include_legacy_owner=False`.
- **"Attachment or image ids build a path outside the upload root."** No. Both the image helper and
  the upload manifest go through `resolve_upload` → `reserve_upload`, which returns `None` for an
  out-of-root index path (`src/upload_handler.py:936-941`), and the manifest re-checks
  `_inside_upload_dir` and `_resolve_tool_path`.
- **"The stream hides a provider failure from the client, or a disconnect leaks the stream
  registry."** Neither for the detached path: `agent_runs._drain` publishes an `error` event and
  marks the run on any generator exception, `_safe_stream`'s `finally` pops the registry, and a
  finished run evicts its buffer 180s after the last subscriber. Compare-mode streams have no such
  wrapper, but what the compare UI does with a truncated SSE was not established, so it is not
  reported.
- **"Session deletion orphans message rows, `auto_sort_sessions` deletes other owners' rows,
  `_verify_session_owner`'s ghost branch reaches another owner's in-memory session, `POST
  /api/rewrite` rewrites another owner's row, or `coerce_message_and_session` 500s on a list
  body."** None hold: `delete_session` deletes `chat_messages` explicitly and detaches documents;
  the tidy candidates come from an owner-filtered query and recent sessions are spared; the ghost
  branch requires `ghost.owner == user`; the rewrite verifies ownership before an update that also
  filters on `session_id`; and the coercion helper catches and re-raises 400.
- **"The workspace helpers gate on `get_current_user` instead of `effective_user`, so a token can
  bind a workspace."** Not reachable: a bearer caller resolves to the pseudo-user `api`, which is
  not an admin, so the workspace is dropped.
- **"Image generation keeps burning upstream compute after a compare-pane stop."** The `_img_task`
  is indeed not cancelled when the generator closes, contrary to the comment beside it, but it
  needs compare mode and an image-generation session in one pane and the compare UI was not read
  far enough to confirm that combination, so it is not reported.
- **"A gallery filename, document upload id or image id escapes its directory."** No.
  `_gallery_image_path` sanitizes, resolves and requires the common path to equal the root plus an
  exact-match check; `_resolve_user_upload_path` re-checks the real path against the upload
  directory; both are pinned by existing confinement suites.
- **"A gallery or document read, update or delete is not owner-scoped."** Every query in the two
  files was walked: the list and library endpoints use the owner filters (failing closed for a
  null user when auth is on) and every by-id endpoint calls `_verify_doc_owner`,
  `_get_or_404_image` or `_get_or_404_album`. The export-zip skips non-owned documents rather than
  leaking them. This is the one reviewed route surface where the list and the mutators agree.
- **"An upload or import is unbounded, or trusts the client's content type."** No: the gallery
  paths go through `read_upload_limited` (100 MB / 25 MB caps) with a fixed extension set, the PDF
  import goes through `save_upload` (cap plus `detect_content_type`), and the generated-image
  server maps the extension to a MIME type with no HTML or script extension reachable.
- **"One user's image-endpoint key can be used by another user."** No: the endpoint query runs
  through `owner_filter`, and its fallback branch can only select a shared, owner-less row.
- **"Cross-owner deletion through the chat-history cleanup in the gallery delete path."** The
  `LIKE` scan is unscoped, but a match requires a message whose tool events reference this image's
  id or filename, which only the owner's own sessions contain. The unscoped full-table scan per
  delete was considered and dropped as too weak to report.
- **"`gallery_upload` leaves an orphan file when the database insert fails."** Real in shape (the
  file is written before the insert) but no reachable trigger was found, so it is not reported.
- **"`render_page_png`'s public cache header, a missing dimension cap, an abandoned compose copy,
  a denylist PDF check, or the upload rate limiter are this section's findings."** None is. The
  cache key is an unguessable document UUID and no shared cache in the documented deployment was
  established; the byte caps exist and PIL's own decompression guard covers the decode paths; the
  abandoned copy could not be reached without a full PDF/signature fixture; the denylist result
  only affects the caller's own document; and the rate limiter lives in `src/upload_handler.py`,
  which belongs to `src-documents`.
- **"A skill name, filename or bundle key escapes the skills directory."** No: every path
  component runs through `slugify`, the walk does not follow symlinks, and the bundle importer
  rejects `..` and absolute keys; no route creates a symlink inside the data directory.
- **"`import-from-url` is an SSRF."** No: hosts are pinned to GitHub and skills.sh, each redirect
  hop is re-validated, and the socket is pinned to the validated DNS snapshot — three suites cover
  it.
- **"A task's owner can be set or changed by the request body."** No: the create and update models
  carry no owner field, pydantic v2 drops the extra key (measured), and the handler writes
  `owner=user`.
- **"Event read, update or delete is not owner-scoped."** No: the by-id helpers reject a null or
  foreign owner and the list joins the calendar and filters on it; the unscoped branch needs a
  falsy owner, which is the documented single-user mode.
- **"An imported ICS makes the server fetch a URL, or an imported rule injects lines into the
  export."** Neither: the import loop reads six fields and never touches `URL`, `ATTACH` or
  `VALARM`, the exported rule is unfolded, and the text fields are escaped.
- **"A mutating endpoint in these three families is missing its admin gate."** No: the calendar
  routes are owner-scoped rather than admin-gated by design, the skills gates cover the builtin
  and URL-import paths, and every task path that can execute an admin-only action is gated, with
  `_execute_task_locked` re-checking at execution; the onboarding resume path can only queue the
  housekeeping defaults, none of which is admin-only.
- **"`compute_next_run` never fires for other inputs."** The monthly branch clamps an out-of-range
  day to the month's last day and the time and cron parsers fail closed; the weekly negative-day
  case is the only runaway.
- **"`clear-cache` wipes other owners' database rows, or `?force=true` is an unbounded-concurrency
  hole."** Neither: every table in the cleanup map is owner-scoped for an authenticated caller
  (only the files are not, which is the reported finding), and `force=true` is the UI's documented
  parallel start while `_executing` still prevents a duplicate dispatch.
- **"The CalDAV paths block the loop."** They do not: the sync offloads its blocking half and the
  connection test uses the async client; the skill import and the task cascade are the two sites
  on the loop.
- **"`?refresh=1` on the two vLLM-recipe endpoints, or the recipe cache growing without bound, is
  a finding."** Neither is: the first is reachable without an admin gate but serves public data to
  an authenticated caller — the same reachable-but-not-reported call this run already recorded for
  the sibling `/api/models?refresh=true` probe — and the cache holds small entries for
  authenticated callers with no measured growth.
- **"`repo` in `vllm_recipe` is an SSRF or a path traversal."** No: the host is fixed to
  raw.githubusercontent.com and only the path segment is interpolated.
- **"The `0o755` on the runner scripts is required for tmux."** It is not: the tmux command runs
  `bash <script>`, which needs no execute bit, so the token exposure is avoidable.
- **"The Windows branch of the setup endpoint is unaffected by the quoting defect."** Disproved by
  measurement and folded into that finding.
- **"The GGUF-prelude bypass reaches a non-admin."** No: the tool that submits the command is in
  the non-admin-blocked set and the task action is admin-only, so the validator is a control that
  does not deliver its claim rather than an escalation.
- **"The two `_diagnose_serve_output` copies differ in their shared suggestions too."** They do
  not: 23 shared keys, none with a differing suggestion list; only the four keys named in the
  finding are missing from the copy the route runs.
- **"The email list route is not owner-scoped."** It is: the route probe showed
  `require_owner`'s sub-dependency carries the `account_id` query parameter and a foreign
  `account_id` on `GET /api/email/list` reaches `_assert_owns_account`.
- **"`attachment_extract_dir` is a path traversal."** It is not: the user values are flattened
  to one path segment and the result is re-checked against the attachments base, and the probe
  printed the flattened directory for a `../../etc` input.
- **"The non-object-body 500 class covers the other JSON endpoints in these three files."** It
  does not: the rest take a `data: dict` parameter (FastAPI answers 422) or a Pydantic model, so
  `/accounts/test` is the only occurrence here.
- **"The attachment-metadata fallback leaks another owner's rows."** It does not: the owner
  predicate stays in the query, so the wrong row is another account of the same owner.
- **"The thread-turn cache serves current data across owners."** Not in this tree: nothing
  writes `email_boundaries` (its writer is a retired housekeeping action), so only rows from an
  earlier release can be served — which is why that finding is low.
- **"An email body reaches the front end unsanitized."** Not at the call sites this section
  read: `_sanitizeHtml` is applied at all three (`static/js/emailLibrary.js:5826-5847`, `:6175`).
- **"A string-valued `Session.headers`, or a `system` message whose content is a list, breaks the
  Ollama and Anthropic request builders."** Neither is reachable: every writer stores a dict (the
  session manager normalizes a string on load) and no caller in `src/`, `routes/` or `core/`
  builds a list-content system message.
- **"The `src/model_capability_readers/` package is dead code."** It has no production caller, but
  that is the documented state rather than a defect — the spec records that canonical records are
  not yet used by runtime discovery, endpoint resolution or the front end.
- **"A caller-supplied endpoint URL or model name can redirect an LLM request or attach a stored
  credential."** No: the resolver matches a model name to the caller's own enabled endpoint rows
  and takes the URL and key from that same row, and the chat route uses a form-supplied URL only to
  match a stored row.
- **"`POST /api/v1/chat` lets a token holder point the server at any host."** (Raised by
  `src-llm-core` as a hand-off and checked here.) It does not: the token-supplied `base_url` goes
  through `validate_public_http_url` (`routes/webhook/webhook_routes.py:289`), which requires a
  public HTTP(S) endpoint, fails closed on DNS failure and rejects private-network targets.
- **"The order-dependent test failure the conversation section observed is a second defect."** It
  is not: the same pair (`tests/test_session_list_owner_scope.py` behind
  `tests/test_archived_sessions_model_filter.py`) is the failure `routes-chat-session.md` already
  reports, and the file passes alone.
- **"The compaction slice loss is caught by the compactor's own tests."** It is not:
  `tests/test_context_compactor.py` stubs `_update_session_history` out, and the probe that builds a
  real session reproduces the loss.
- **"The empty-summary path is covered by the summary-failure test."** It is not:
  `tests/test_compaction_summary_failure.py` exercises a summary call that raises, not one that
  returns an empty string, which is the path that rewrites the history.
- **"`run_auto_sort` with an empty owner is harmless because the shipped seeding passes a name."**
  Today's callers are seeded per user, which is why that finding is low — but the probe shows the
  unfiltered branch deletes every owner's sessions, so the guard is the fix, not the seeding.
- **"A forged `pdf_source`/`pdf_form_source` upload id in a document body reads another user's
  upload, or `resolve_generated_image_path` escapes its root with `..`, an absolute path or a
  symlink."** Neither: the marker upload is resolved through `resolve_upload(owner=…)` and 400s, and
  the image path passes a strict hex regex, then realpath and `commonpath` against the resolved
  root.
- **"An upload can overwrite or collide with another owner's file."** No: the name is `uuid4().hex`
  plus a sanitized extension in a date directory, and dedup matches on hash *and* owner.
- **"A malformed or hostile PDF crashes the chat path, or forges a form-field bullet in the
  generated markdown."** Neither: six crafted inputs each return a `[PDF processing failed: …]`
  string, and the field renderer collapses newlines, percent-encodes the label and anchors its
  bullet marker to end-of-line.
- **"A null-owner document is readable by others, or the global active-document pointer leaks a
  document into another user's agent turn."** Neither: the owner check falls back to the session
  join and 404s, and the pointer's fallback filters through the owner/session predicate.
- **"`run_document_tidy(owner or "")` deletes across owners."** The falsy-owner branch is the
  documented single-user mode and both callers pass an authenticated owner — which is what
  distinguishes it from the conversation section's `run_auto_sort` finding, whose caller forwards a
  nullable task column.
- **"The native extractor's unbounded `z.read` is a zip bomb, or `run_document_tidy` blocks the
  loop materially."** Neither is reported: the same exposure exists on the primary markitdown path,
  and the tidy measured 153 ms for 500 documents (2.9 MB).
- **"`get_upload_info` is dead code, or `create_office_document`'s unused `upload_id` loses a needed
  link."** Neither: the upload tests exercise the first and it behaves, and the office document has
  no re-extraction path for the second to feed.
- **"`.html` uploads are stored XSS."** No: the download route passes `filename=`, so the response
  carries `Content-Disposition: attachment`, plus `nosniff`.
- **"PDF fill/stamp output paths escape a directory."** No: every output path is a
  `NamedTemporaryFile(...).name` and the download name is sanitized.
- **"A failed `uploads.json` write leaves a silent orphan."** Real in shape, but with no trigger
  independent of the failure itself — the same call this run made for the gallery orphan.
- **"`extract_fields` raises on a malformed PDF and 500s the import route."** Unverifiable without
  PyMuPDF, so dropped rather than asserted.
- **"A `//host` path can move an `api_call` request to another host."** No:
  `_join_integration_url` strips every leading slash before `urljoin`.
- **"The parser's turn HTML is a new XSS surface."** No: the client runs `body_html` through
  `_sanitizeHtml`.
- **"The integration store's read-modify-write interleaves."** No live caller: every writer is an
  `async` handler whose load-and-save block contains no await, and the server runs one worker.
- **"A successful `api_call` without the `untrusted_content` flag arms the gate less than a
  failure."** It does not: the tool is registered `ResultIntegrity.EXTERNAL_UNTRUSTED`, which the
  gate consults for both outcomes.
- **"A wedged MCP server also strands the Streamable HTTP transport."** It does not: the SDK sets
  httpx timeouts for that transport, so the unbounded-call finding covers stdio and SSE.
- **"Disconnecting an MCP server orphans its child process."** It does not: the SDK's stdio
  generator runs its own `finally` (stdin close, then SIGTERM/SIGKILL) before the task group is
  exited, and the probe shows no surviving child — what the wrong-task close loses is the
  transport's own errors and the log's meaning.
- **"A hostile stdio server gains something it could not already do."** Little: registering one is
  executing arbitrary binaries on the host, as the route's own docstring states, so the added
  exposure is only the secrets that exist solely in the environment — which is why that finding is
  low.
- **"The plan-mode read-only gate is unreliable in general."** It is not: the classifier is pinned
  by `tests/test_plan_mode.py` with annotations supplied directly; only what discovery stores per
  transport is unpinned, which is the reported defect.
- **"The admin-set `search_url` is a provider-layer SSRF."** The provider calls skip the outbound
  guard, but the write path is admin-only, the documented default is localhost, and no credential
  is attached — design intent, not a finding.
- **"A non-string query crashes ranking."** No: `query.py` guards with `isinstance` and both
  production callers coerce.
- **"Cache keys collide across owners or queries."** No: keys are sha256 over the query, count,
  time filter and URL cap, and nothing owner-specific is cached.
- **"A corrupt cache entry is served or crashes the caller."** No: both read paths catch, unlink
  and refetch.
- **"Failed or blocked fetches are cached, making a guard verdict sticky."** No: the failure paths
  return before `_cache_result`.
- **"A malformed provider JSON body aborts the search."** Already pinned, and SearXNG falls back
  to the HTML scrape on any exception; the error-status path is the different, unpinned one.
- **"Huge pages make extraction unbounded."** No: 1.9 s measured for 1.37 MB under a 2 MB cap, and
  the route-level event-loop blocking is already `routes-rest-integrations-misc`'s finding.
- **"The analytics file leaks one user's queries or grows without bound."** True in shape, but the
  whole path is dead, so there is no exposure.
- **"`searxng_search_results`'s count rewrite and `invalidate_search_cache`'s key are live
  defects."** Both sit inside the dead path.
- **"`SearchService.search`'s page budget is unbounded."** No: results are capped by the
  configured count.
- **"The `api_key = ""` branches are a live auth bypass."** Dead branches; folded into the
  SearXNG-URL finding's premise instead of reported separately.
- **"DDG redirect resolution can be walked to another host."** No: the host guard plus
  `tests/test_service_search_provider_guards.py`.
- **"The SearXNG HTML fallback trusts an instance-supplied href."** No: the URL still goes through
  the guarded transport on fetch.
- **"An import can overwrite another owner's skill."** No: the target name is deduped against
  `load_all()` — all owners — so a collision is suffixed, `slugify` collapses it to a filename-safe
  slug and `_safe_relpath` rejects `..` and absolute keys.
- **"A hostile bundle escapes the skills directory by path."** No: keys come from the GitHub listing
  and every write goes through `_safe_relpath`.
- **"`read_skill_reference` can be walked out of the skill directory."** No: `realpath` plus
  `commonpath` against the skill dir, with a check that the target is not the directory itself.
- **"`update_skill`'s rename can land on another owner's skill."** No: the target path is built from
  the renamed skill's own category and name, and the rename returns `False` when that directory
  exists. A rename into a different category can still leave two same-named skills, which is noted
  rather than reported.
- **"`MemoryService.__init__`'s vector gate never opens."** No: `setup.py` creates
  `data/memory_vectors` on every install.
- **"Unowned legacy memories can never be removed by an owner's audit."** No: `load(owner=...)`
  filters strictly, so they are never in the audited set.
- **"A malformed LLM reply writes a partial record over a good store."** No: the parser returns `[]`
  on any failure, extraction returns before saving when nothing survives, and the read-modify-write
  uses the strict loader; the audit refuses to save on bad JSON and on a cut of more than half.
- **"A non-string `title` crashes the extractor's background task."** No: the `AttributeError` is
  caught by the enclosing handler, which logs and drops the skill.
- **"The importer force-publishes a third-party bundle past review."** No: the importer never
  touches `status`, auto-extracted skills default to published anyway, and the import is an explicit
  admin action.
- **"A hostile directory listing makes the importer recurse without bound."** No: depth, file count
  and byte total bound the walk, and exceeding the byte total raises rather than truncating.
- **"The compatibility handler's records leak another owner's report."** No: the live route hides
  records without an owner key, and nothing calls the copy.
- **"`ResearchService._parse_sources` cannot parse its own handler's report."** Disproved by probe:
  both source links parsed.
- **"`DocsService` reads a different Chroma store than the app."** No: `persist_directory` is only
  used for a `mkdir`, and the collections come from the embedding lanes, so the constants differ but
  the store does not.
- **"No hard timeout leaves a research job running forever."** Not established: every LLM and search
  call inside the researcher carries its own timeout and the budget is checked between rounds, and
  the spec already warns the copy may lack active-route policy behaviour.
- **"The duplicated handler is undocumented dead code."** No: it is documented compatibility surface
  with a retirement item, which is why the parity gap is filed as a security finding instead of a
  dead-code one.
- **"Non-dict finding or row handling is broken in either module."** No: both filter non-dict rows
  and their suites pass.
- **"`services/docs/__init__.py` re-exports have drifted."** No: it re-exports the `RAGManager` and
  `VectorRAG` its docstring names.
- **"A caller-supplied host or port reaches a shell in the hardware layer."** No: the host is passed
  as one ssh argv element, the exec helper rejects a leading `-`, and the string commands carry no
  caller data.
- **"A caller-supplied model path becomes an arbitrary file read there."** No: path handling lives
  in the route layer, and the hardware reader is only ever called with `/proc/meminfo` and
  `/proc/cpuinfo`.
- **"A hung SSH probe leaves the remote target set, so later local probes go remote."** Not by that
  path: every exception is caught and each assignment is cleared before return with no unguarded
  raise in between — the concurrent case is the reported race.
- **"A failed hardware detection is retried on the next call."** It is not, but the Rescan flag
  bypasses the 24-hour cache, so it is noted rather than reported.
- **"An outage for one community source loses the whole dynamic refresh."** It aborts the refresh,
  but the route reports it and the bundled catalogue still serves.
- **"The shared temp filename can be served half-written."** Not established: the replace is atomic
  and the loader catches a parse failure.
- **"A zero or missing VRAM value divides by zero."** No: every divisor is guarded and the serve
  profiler returns empty for a non-positive VRAM.
- **"A null release date breaks the newest sort or the UI."** No: the sort maps it to an empty
  string and the front end coerces.
- **"The empty image-model registry means the image list is always empty."** No: the collections
  supply rows when the fetch succeeds; it is empty only while the blank-cache finding is live.
- **"A non-string search or non-dict system still crashes image ranking."** No: both are fixed and
  pinned by passing suites.
- **"`_normalize_model_entry` corrupts the cached catalogue across calls."** No: rows are re-parsed
  from JSON per load and only the normalized result list is cached.
- **"The TTS cache key collides across users and serves one user's audio to another."** No: the key
  hashes provider, model, voice, speed and text, so a hit requires the same text, and the filename
  is a digest with no traversal component.
- **"The TTS speed setting is ignored by the local provider."** No: each provider applies it once —
  client-side for local and browser, in the payload for an endpoint.
- **"`clear_cache` deletes unrelated files or crashes on a directory."** No in practice: the cache
  directory has no other writer, and the crash needs a hand-made directory named like a digest.
- **"A YouTube playlist link is still web-fetched, so only the transcript is lost."** No: the context
  builder filters every `is_youtube_url` match out of the fetch list too.
- **"`ShellService` is what the live shell routes call."** No: the route layer implements its own
  create/exec helpers and no import of the class exists outside the re-export and its test.
- **"The comment-fetch timeout is broken."** No: the communicate call is wrapped in a timeout with
  kill-and-reap, pinned by a suite.
- **"`fetch_youtube_comments` can be aimed at an internal address or inject an argument."** No: the
  URL is a fixed template and the command is an argv list with no shell.
- **"`format_transcript_for_context` raises on a segment without text."** No: segments are built by
  the same module with both keys, and a non-dict guard is pinned by a suite.

## Unresolved state

One item is carried forward for a later section rather than left as a finding.
`tests/test_services_research_low_quality_sources.py:8-9` asserts that
`services/research/service.py` is the live research path; `specs/research.md:118` and
`src/app_initializer.py:117` say the live path is `src/research_handler.py` and the
`services/` copy is compatibility surface to retire. The `services-research` pass found no
production caller of the copy, so the test's premise is stale. Whether that staleness matters is
for the `tests-*` pass, which owns that file.

The one observation the previous pass left open — the three `secret_storage import failed;
skipping <x> migration` warnings from `core/database.py` — is now a finding in
`core-data-platform.md`. The reproduction is deterministic for a process whose first core-touching
import is `src.secret_storage`, or a module that imports it first such as `routes.email_helpers`,
and `import app` under the same conditions reports no skip, so the server boot order is safe. The
finding records the one-line fix; what remains open is only whether a future entry point takes that
import order.

## How to extend this audit

`PROMPT.md` is the assignment a reviewer executes. It gives the finding schema, the evidence rules,
the section files, and the stopping point.

Coverage should proceed in this order, most consequential first:

1. **The tool-surface sections and the memory layer are now reviewed.** `src-tools-parse-exec`,
   `src-tools-capabilities-policy`, `src-tools-schema-index`, `src-agent-tools` and
   `src-agent-loop` together cover the schema list, the converter, the retrieval index, the
   policy tables, the parsers, the dispatcher and the loop. `src-memory-rag` now covers the stores
   and lanes that surface retrieves through; its six findings are a concurrent memory write that
   loses entries and can leave the store unreadable, a re-index path that never removes a changed
   file's previous chunks, a failing embedding collection reported as an empty healthy lane,
   non-atomic personal-docs state files, unbounded full-collection scans, and a private encoder
   that can disagree with the collection it is meant to serve. What remains around that surface is
   the scheduler that invokes the built-in actions (`src-research-scheduling`). `src-platform` (the
   settings and secrets the policy reads) is now reviewed. The guards in `src-security.md` and the
   decisions in `src-agent-loop.md` are only worth what their callers make of them: both `SECURITY`
   findings rated high in this run are guards that hold everywhere except on one path that
   mattered.
2. **`core-data-platform` and `src-platform` are now reviewed.** The remaining credential and
   authorization surfaces: the two Fernet stores found in `src-security` are only half the
   picture, and the `RACE` finding would be much stronger or weaker depending on whether anything
   else writes keys — `src-platform` checked the third candidate and found that
   `APIKeyManager.save` has no production caller, so it is not a second writer. `core-auth-session`
   is reviewed (its five findings are the global 100-row
   session cache that can hide a second user's sidebar, a no-op `save_sessions` whose callers'
   in-memory field writes are overwritten on the next read, a dead cleanup method that raises and
   rolls back, a log redactor that passes scheme-less URLs through with their userinfo, and a
   password-only session-issuing method on the auth class). `core-data-platform` is reviewed too
   (its six findings are the shared JSON writer leaving `auth.json` and `settings.json` at the
   umask default, a transcript-FTS backfill that is quadratic on every startup, a non-atomic
   rewrite of `memory.json`/`user_prefs.json` in the hourly owner sweep, an unusable
   `bulk_insert_messages`, the fail-open import guard that skips the three encryption migrations,
   and plaintext MCP env vars). `src-platform` is reviewed as well (its four findings are a dead
   pydantic settings tree that can still stop the server from starting on a stray `SECURITY_*` /
   `DATA_*` / `LLM_*` value, a startup log that claims a Brave key was loaded from a store nothing
   writes, an empty `ODYSSEUS_DATA_DIR` that moves every store next to the working directory, and
   the documented-but-unread `CLEANUP_*` knobs). `routes-rest-auth-admin` is the first route
   section reviewed (its four findings are the login/signup/setup limiter keyed on a socket peer
   the documented Docker deployment makes identical for every client, an admin create-user path
   that hashes the password on the event loop, a token list that shows rows the revoke endpoint
   refuses, and three admin JSON endpoints that 500 on a non-object body), and
   `routes-rest-agent-admin` is the second (its four findings are the Codex and Claude email-send
   endpoint that reports a message queued while the delivery call is attached to a discarded
   `BackgroundTasks` object, the MCP OAuth client secret written verbatim to the application log,
   a cookbook stop endpoint that kills any tmux session by name including untracked ones, and an
   adopt endpoint that 500s on a non-numeric port). `routes-rest-notes-contacts-history` is the
   third (its three findings are a vCard export that drops every stored postal address, contacts
   handlers that run synchronous CardDAV requests on the event loop, and nine notes and history
   endpoints that answer 500 to a JSON array or string where their typed siblings answer 422),
   and `routes-rest-memory-personal-research` is the fourth (its three findings are the missing
   `can_manage_memory` privilege gate on memory edit, pin, delete and audit, a research library that
   silently omits a saved partial report whose statistics are null, and a library listing that
   parses every stored report on the event loop before applying the result limit).
   `routes-rest-media-files` is the fifth (its three findings are a shared bearer-owned
   preferences/drafts/signatures bucket that every delegated token can read and mutate, speech,
   vision and upload work run on the request event loop, and three raw-JSON endpoints that raise on
   a non-object body).
   What the policy layer
   reads and the credential routes do are now covered; the next surfaces are the remaining route
   sections.
3. **The rest of `routes-rest`, then the other route sections.** `routes-rest` was split into six
   sub-sections during this pass; `routes-rest-auth-admin`, `routes-rest-agent-admin`,
   `routes-rest-notes-contacts-history`, `routes-rest-memory-personal-research`,
   `routes-rest-media-files` and `routes-rest-integrations-misc` are reviewed. Then
   `routes-email`, `routes-cookbook`, `routes-chat-session`, `routes-models`,
   `routes-gallery-document` and `routes-skills-calendar-task`, which are also under review. The
   widest route surface, and the ones that consume `settings_scrub`, `upload_limits`, and the URL
   guards.
4. **The remaining `src-*` and `services-*` sections**, then `tests-*` (which is where the missing
   cross-classifier test would go), then `static-*`, which is the largest surface and the least
   likely to hold a backend trust-boundary defect.

Record the new pass as follows:

1. Update `sources/header.md` with the new audit date, snapshot, and counts.
2. Refresh each section's coverage statement to match what was read.
3. Run `./audit.py build odysseus/2026-10-03T2340` and `./audit.py check odysseus/2026-10-03T2340`.
4. Run `./audit.py snapshot odysseus/2026-10-03T2340` so `./audit.py compare` can show what moved.
