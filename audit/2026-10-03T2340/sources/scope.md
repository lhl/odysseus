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
