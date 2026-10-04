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
