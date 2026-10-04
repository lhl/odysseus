# What is under audit

This audit reviews https://github.com/odysseus-dev/odysseus at `2992bf6d368a`.

Odysseus is a self-hosted, multi-user AI workspace: a FastAPI backend and a first-party
JavaScript front end covering chat, an agent loop with a tool surface, email, calendar, documents
and RAG, memory, research, model serving, and MCP. An operator runs it from the Docker compose
files or a native install, and accounts on one instance share that process.

Four surfaces carry the most consequence if they are wrong:

- **Authentication and per-user isolation.** Sessions, API tokens, privileges, and the owner
  filter on every stored record.
- **The agent tool surface.** A model can run shell commands, read and write files, fetch URLs
  and call the app's own API.
- **Credential storage.** Password hashes, TOTP secrets, session tokens and provider API keys
  live in JSON files and one SQLite database under the data directory.
- **Outbound requests.** Web fetch, search, webhooks, CalDAV and MCP reach hosts a user or a
  model names.

## Sections

The run is divided into 58 sections. Each is one file under `sources/sections/`, named by
its stem, and each states its own coverage. `run.toml` lists the paths assigned to each section.

| # | Section | Stem |
| ---: | --- | --- |
| 1 | Repository root and project policy | `repository-root` |
| 2 | Build, install, launcher, CI and containers | `build-install-deploy` |
| 3 | Specifications | `specs` |
| 4 | Operational scripts | `scripts` |
| 5 | core: auth, sessions, middleware, models | `core-auth-session` |
| 6 | core: database, atomic IO, constants, platform | `core-data-platform` |
| 7 | src: agent loop, runs, approvals and gates | `src-agent-loop` |
| 8 | src: LLM interaction, endpoints, model capability | `src-llm-core` |
| 9 | src: tool parsing and execution | `src-tools-parse-exec` |
| 10 | src: tool capabilities, policy and MCP builtins | `src-tools-capabilities-policy` |
| 11 | src: tool schemas, index and implementations | `src-tools-schema-index` |
| 12 | src: scheduled built-in actions | `src-tools-builtin-actions` |
| 13 | src: agent tool implementations | `src-agent-tools` |
| 14 | src: prompt security, secrets, URL safety, limits | `src-security` |
| 15 | src: chat processing, context and sessions | `src-chat-session` |
| 16 | src: memory, RAG, embeddings and settings | `src-memory-rag` |
| 17 | src: documents, uploads, PDF and office | `src-documents` |
| 18 | src: email, calendar and integrations | `src-email-integrations` |
| 19 | src: research, scheduling and background work | `src-research-scheduling` |
| 20 | src: MCP management and OAuth | `src-mcp` |
| 21 | src: config, runtime, health and remaining modules | `src-platform` |
| 22 | routes: email | `routes-email` |
| 23 | routes: cookbook | `routes-cookbook` |
| 24 | routes: chat and session | `routes-chat-session` |
| 25 | routes: model serving | `routes-models` |
| 26 | routes: shell and code execution | `routes-shell` |
| 27 | routes: gallery and documents | `routes-gallery-document` |
| 28 | routes: skills, calendar, tasks | `routes-skills-calendar-task` |
| 29 | routes: auth, API tokens, admin and provider sign-in | `routes-rest-auth-admin` |
| 30 | routes: assistant, codex, MCP and workspace | `routes-rest-agent-admin` |
| 31 | routes: notes, contacts and history | `routes-rest-notes-contacts-history` |
| 32 | routes: memory, personal files and research | `routes-rest-memory-personal-research` |
| 33 | routes: uploads, embeddings, presets and preferences | `routes-rest-media-files` |
| 34 | routes: webhooks, vault, compare, hardware fit and shims | `routes-rest-integrations-misc` |
| 35 | services: search | `services-search` |
| 36 | services: memory | `services-memory` |
| 37 | services: research and docs | `services-research` |
| 38 | services: hardware fit | `services-hwfit` |
| 39 | services: shell, STT, TTS, faces, youtube | `services-media` |
| 40 | static: image editor | `static-js-editor` |
| 41 | static: model comparison UI | `static-js-compare` |
| 42 | static: chat, sessions and composer UI | `static-js-chat` |
| 43 | static: documents, notes, email, calendar UI | `static-js-documents-email` |
| 44 | static: cookbook, settings, models UI | `static-js-cookbook-settings-models` |
| 45 | static: research, memory and search UI | `static-js-research-memory-rag` |
| 46 | static: remaining first-party JS | `static-js-rest` |
| 47 | static: vendored libraries, fonts, icons, CSS | `static-assets-vendored` |
| 48 | Bundled MCP servers | `mcp-servers` |
| 49 | Companion apps and Swift clients | `companion-and-swift` |
| 50 | Project website | `website` |
| 51 | tests: harness, standards and helpers | `tests-harness` |
| 52 | tests: security, guard and prompt-injection | `tests-security` |
| 53 | tests: email, calendar and webhooks | `tests-email-calendar` |
| 54 | tests: cookbook, models and providers | `tests-cookbook-models` |
| 55 | tests: LLM, tools and agent loop | `tests-llm-tools` |
| 56 | tests: session, chat, memory and RAG | `tests-session-chat-memory` |
| 57 | tests: documents, uploads, gallery and media | `tests-documents-media` |
| 58 | tests: remaining test modules | `tests-rest` |

## How this run was scoped

`./audit.py discover` proposed the sections from the directory structure, and the list was then
edited. A path belongs to exactly one section.

- **Two sections were split during the review.** `src-tools` (10,435 lines) became the four
  `src-tools-*` sections and `routes-rest` became the six `routes-rest-*` sections, because one
  pass over either could not hold the evidence standard.
- **Two trees are listed for coverage and are not first-party code.**
  `services/hwfit/data/*.json` is a generated model catalogue of about 35,000 lines, and
  `static/lib/` holds minified third-party bundles. A finding there is about the pin or the
  provenance, not about the upstream project.
- **A boundary between two sections is stated in each section's Overview**, which names the
  neighbouring section that owns the code on the other side.

## The release boundary

The repository has no Makefile or package script, so its gates are the GitHub Actions jobs.

| Gate | What it runs | Run by this audit |
| --- | --- | --- |
| `ci.yml`, job `check` | `compileall` over every source root, `node --check` over the first-party JavaScript, then the full `pytest` suite. Runs on push and pull request. | Subsets only; each section's Coverage records them. |
| Other CI jobs | CodeQL, a secret scan, container scanning, a dependency review and a workflow-security audit. | No. They need network access or credentials. |
| `docker-publish.yml` | Publishes the image on push to `dev` and `main`. It does not depend on the `check` job. | No. No image was built. |
