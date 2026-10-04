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
