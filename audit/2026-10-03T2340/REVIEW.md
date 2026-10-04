# odysseus Codebase Review

This file is edited by hand. Unlike [`README.md`](README.md), it is not generated.

The tables between `<!-- metrics: name -->` and `<!-- /metrics: name -->` markers are
computed by `./audit.py table`. Paste its output over a block to update it; `./audit.py
fill` does every block at once. Prose is never rewritten by a tool, so a sentence that
cites a number is yours to keep true.

| | |
| --- | --- |
| **Review date** | 2026-10-03 |
| **Subject** | [the code audit](README.md), audit date 2026-10-03, `2992bf6d368a` |
| **Counts as of** | that audit snapshot |
| **Coverage** | 126,017 of 468,155 lines (26.9%): all of `core`, `src`, `routes` and `services`, in 35 of 58 sections. No front-end, test, build, spec or script file was read. |
| **Tooling** | `./audit.py build` (the generated audit), `./audit.py table` (these tables), `./audit.py check` (the gate) |

## Updating the tables

The tables are snapshots of one run. After the audit changes:

1. Run `./audit.py verify odysseus/2026-10-03T2340` to list stale blocks.
2. Run `./audit.py fill odysseus/2026-10-03T2340` to refresh them.
3. Update any prose that cites a number from a refreshed block. No tool checks prose.

## Verdict

**Grade: C (confidence: medium — 26.9% of the tree read).**

The letter covers the Python backend: `core`, `src`, `routes` and `services`, 126,017 lines in
35 sections. It does not cover the other 342,138 lines. `static` (205,901 lines) and `tests`
(113,318 lines) are the two largest trees in the repository and neither was read.

Correctness, Security and Enforcement drive the letter. The backend holds 190 recorded defects,
three of them high, and the release image is published by a workflow that runs no test. Testing
keeps the letter from going lower: 805 test modules exist and CI runs the whole suite on every
push and pull request.

The count of 190 is a floor set by what was read, not a measure of the repository. A re-review on
2026-10-04 re-derived 26 of the 190 from source; the other 164 carry the first pass's evidence
only. See [Re-review, 2026-10-04](README.md#re-review-2026-10-04).

### Report card

The six dimensions and the scale are fixed by
[`docs/GRADING-RUBRIC.md`](../../../docs/GRADING-RUBRIC.md). Densities divide by the 126.0
reviewed KLOC.

| Dimension | Grade | Basis |
| --- | --- | --- |
| Correctness | C | `(10 × 3 + 3 × 61 + 126) / 126.0` = 2.69 weighted defects per reviewed KLOC, on 3 high, 61 medium, 126 low. The record places 2.02 at C and 3.03 at D. C is kept because 126 of the 190 are low and the three highs each have a fix of a few lines. |
| Security | C | Worst `SECURITY` severity is high, carried by one finding: `manage_research` reads and deletes every user's research files. Ten more are medium and 18 are low. The agent tool gates are ordered and fail closed (`is_public_blocked_tool`, `ToolRunSecurityContext.decision_for`), which is why two findings first rated high were lowered. No committed credential was found: the secret gate matches none of the 189 secret-shaped values in the tree against this run. |
| Testing | B | `ls tests/*.py` lists 805 modules, and `.github/workflows/ci.yml:145` runs `python -m pytest -q` on push and pull request. This run executed subsets only, and read no test file, so whether the suite asserts negative cases is not established. |
| Enforcement | D | CI gates on `compileall`, `node --check` and the full test suite (`ci.yml:83`, `:100`, `:145`). No lint or type check is configured: `grep -rln "ruff\|mypy\|flake8\|pylint\|pyright\|eslint" .github pyproject.toml setup.py package.json` returns nothing. `docker-publish.yml:13-15` publishes on push to `dev` and `main` with no dependency on the test job. The rubric grades a missing lint or type check F; D is used because CI exists and runs every test, so the gap is the publish path and the two missing checks. |
| Documentation | B | 3 `DOC-DRIFT` findings, 0.02 per reviewed KLOC. Documentation exists (`README.md`, `THREAT_MODEL.md`, `SECURITY.md`, 61 files under `specs/`) and none of it was read as its own section, so drift was found only where a code finding led to a document. |
| Maintainability | C | 24 `DEAD-CODE` + `DUP` + `FOOTGUN` findings, 0.19 per reviewed KLOC, between the 0.07 the record places at B and the 0.35 it places at D. 16 of the 24 are dead code. |
| **Overall** | **C** | Three dimensions at C, one at D, two at B. Correctness, Security and Enforcement drive it. |

### Coverage by surface

| Surface | Findings | What was read |
| --- | --- | --- |
| `core` | 11 — 0 high, 4 medium, 7 low | 2 sections, 11 files, 5,182 lines. |
| `src` | 85 — 2 high, 30 medium, 53 low | 15 sections, 149 files, 62,737 lines. |
| `routes` | 65 — 1 high, 23 medium, 41 low | 13 sections, 86 files, 47,962 lines. |
| `services` | 29 — 0 high, 4 medium, 25 low | 5 sections, 40 files, 10,136 lines. |
| `static` | none recorded | Not read. 8 sections, 205,901 lines. |
| `tests` | none recorded | Not read. 8 sections, 113,318 lines. |
| Root, build, CI, `specs`, `scripts`, `mcp_servers`, `companion`, `swift`, `website` | none recorded | Not read as sections. 7 sections, 22,919 lines. Single files were opened where a backend finding cited them. |

Each section's own coverage statement lists the files it read in part.

<!-- metrics: counts -->
| Count | Value |
| ---: | ---: |
| Findings | 399 |
| High severity | 3 |
| Medium severity | 106 |
| Low severity | 290 |
| Disposition `fix-now` | 8 |
| Disposition `next` | 305 |
| Disposition `backlog` | 86 |
| Disposition `wontfix` | 0 |
| Findings with no disposition | 0 |
| Distinct tags | 13 |
| Sections with at least one finding | 58 of 58 |
| Findings carrying an issue number | 0 |
<!-- /metrics: counts -->

## The evidence

### Scale

<!-- metrics: scale -->
| Area | Files | Lines |
| ---: | ---: | ---: |
| Repository root and build surface | 19 | 3,818 |
| core | 11 | 5,182 |
| src | 149 | 62,737 |
| routes | 86 | 47,962 |
| services | 40 | 10,136 |
| static | 172 | 205,901 |
| tests | 854 | 113,318 |
| specs and scripts | 85 | 12,436 |
| Other tracked trees | 26 | 6,665 |
| **Total** | **1,442** | **468,155** |

| Repository history | Value |
| ---: | ---: |
| Snapshot | `2992bf6d368a11472323e47d3bfed91e79cefc6b` |
| First commit | 2026-05-31 |
| Latest commit | 2026-10-04 |
| Commits | 2,106 |
| Audit date | 2026-10-03 |
| Working tree | clean |
<!-- /metrics: scale -->

### Findings

<!-- metrics: findings -->
| Section | Findings | High | Medium | Low |
| --- | ---: | ---: | ---: | ---: |
| Repository root and project policy | 8 | 0 | 1 | 7 |
| Build, install, launcher, CI and containers | 11 | 0 | 1 | 10 |
| Specifications | 11 | 0 | 0 | 11 |
| Operational scripts | 24 | 0 | 8 | 16 |
| core: auth, sessions, middleware, models | 5 | 0 | 1 | 4 |
| core: database, atomic IO, constants, platform | 6 | 0 | 3 | 3 |
| src: agent loop, runs, approvals and gates | 7 | 0 | 2 | 5 |
| src: LLM interaction, endpoints, model capability | 7 | 0 | 3 | 4 |
| src: tool parsing and execution | 5 | 0 | 1 | 4 |
| src: tool capabilities, policy and MCP builtins | 1 | 0 | 1 | 0 |
| src: tool schemas, index and implementations | 6 | 0 | 3 | 3 |
| src: scheduled built-in actions | 5 | 0 | 3 | 2 |
| src: agent tool implementations | 9 | 1 | 4 | 4 |
| src: prompt security, secrets, URL safety, limits | 7 | 0 | 1 | 6 |
| src: chat processing, context and sessions | 7 | 0 | 3 | 4 |
| src: memory, RAG, embeddings and settings | 6 | 1 | 2 | 3 |
| src: documents, uploads, PDF and office | 4 | 0 | 2 | 2 |
| src: email, calendar and integrations | 4 | 0 | 2 | 2 |
| src: research, scheduling and background work | 8 | 0 | 1 | 7 |
| src: MCP management and OAuth | 5 | 0 | 1 | 4 |
| src: config, runtime, health and remaining modules | 4 | 0 | 1 | 3 |
| routes: email | 8 | 0 | 2 | 6 |
| routes: cookbook | 7 | 0 | 2 | 5 |
| routes: chat and session | 4 | 0 | 2 | 2 |
| routes: model serving | 5 | 0 | 1 | 4 |
| routes: shell and code execution | 7 | 0 | 1 | 6 |
| routes: gallery and documents | 5 | 0 | 1 | 4 |
| routes: skills, calendar, tasks | 8 | 0 | 4 | 4 |
| routes: auth, API tokens, admin and provider sign-in | 4 | 0 | 1 | 3 |
| routes: assistant, codex, MCP and workspace | 4 | 1 | 0 | 3 |
| routes: notes, contacts and history | 3 | 0 | 2 | 1 |
| routes: memory, personal files and research | 3 | 0 | 2 | 1 |
| routes: uploads, embeddings, presets and preferences | 3 | 0 | 2 | 1 |
| routes: webhooks, vault, compare, hardware fit and shims | 4 | 0 | 3 | 1 |
| services: search | 5 | 0 | 1 | 4 |
| services: memory | 7 | 0 | 0 | 7 |
| services: research and docs | 4 | 0 | 0 | 4 |
| services: hardware fit | 6 | 0 | 1 | 5 |
| services: shell, STT, TTS, faces, youtube | 7 | 0 | 2 | 5 |
| static: image editor | 9 | 0 | 3 | 6 |
| static: model comparison UI | 7 | 0 | 1 | 6 |
| static: chat, sessions and composer UI | 8 | 0 | 2 | 6 |
| static: documents, notes, email, calendar UI | 8 | 0 | 3 | 5 |
| static: cookbook, settings, models UI | 5 | 0 | 0 | 5 |
| static: research, memory and search UI | 11 | 0 | 1 | 10 |
| static: remaining first-party JS | 5 | 0 | 1 | 4 |
| static: vendored libraries, fonts, icons, CSS | 8 | 0 | 2 | 6 |
| Bundled MCP servers | 7 | 0 | 2 | 5 |
| Companion apps and Swift clients | 8 | 0 | 0 | 8 |
| Project website | 7 | 0 | 1 | 6 |
| tests: harness, standards and helpers | 10 | 0 | 1 | 9 |
| tests: security, guard and prompt-injection | 11 | 0 | 3 | 8 |
| tests: email, calendar and webhooks | 12 | 0 | 6 | 6 |
| tests: cookbook, models and providers | 7 | 0 | 1 | 6 |
| tests: LLM, tools and agent loop | 6 | 0 | 2 | 4 |
| tests: session, chat, memory and RAG | 10 | 0 | 3 | 7 |
| tests: documents, uploads, gallery and media | 7 | 0 | 1 | 6 |
| tests: remaining test modules | 9 | 0 | 2 | 7 |
| **Total** | **399** | **3** | **106** | **290** |
<!-- /metrics: findings -->

### Tags

<!-- metrics: tags -->
| Tag | Findings |
| --- | ---: |
| `BUG` | 155 |
| `SECURITY` | 55 |
| `DOC-DRIFT` | 35 |
| `ERROR-HANDLING` | 35 |
| `PERF` | 35 |
| `DEAD-CODE` | 31 |
| `FOOTGUN` | 19 |
| `DUP` | 11 |
| `RACE` | 8 |
| `HARDCODE` | 6 |
| `DEPENDENCY` | 4 |
| `UNDOCUMENTED` | 3 |
| `TYPE-SAFETY` | 2 |
<!-- /metrics: tags -->

### Dispositions

<!-- metrics: dispositions -->
| Disposition | Findings |
| --- | ---: |
| `fix-now` | 8 |
| `next` | 305 |
| `backlog` | 86 |
<!-- /metrics: dispositions -->

### Tests

<!-- metrics: tests -->
| Test location | Test files | Runner |
| --- | ---: | ---: |
| `tests` | 834 | — |
| **Total** | **834** |  |
<!-- /metrics: tests -->

### Gates

<!-- metrics: gates -->
_No invocable targets were detected for this project._
<!-- /metrics: gates -->

### What was not checked

- **The front end.** `static` is 44% of the repository's lines and no file in it was read. No
  claim is made about cross-site scripting, client-side authorization, or UI correctness.
- **The tests.** No test file was read. The Tests table counts files; it does not say what they
  assert, and the full suite was not run by this audit.
- **Build and release.** `Dockerfile`, the compose files, the installers and the workflows were
  not reviewed as a section. The Enforcement grade rests on the three commands cited in the
  report card.
- **The bundled MCP servers and companion apps.** `mcp_servers/memory_server.py` was opened only
  for the memory-store finding.
- **Runtime behaviour.** No deployment was built. Measurements are the small probes each finding
  records.
- **164 of the 190 findings** were not re-derived by the re-review.
- **The Gates table reads "no invocable targets"** because the repository has no Makefile or
  package script. The gates are the CI jobs named in the report card.

## Recommendations

1. **Filter `manage_research` by owner** (`src-agent-tools`, high). Any agent-capable user reads
   and deletes every user's research reports. Decision: whether owner-less legacy files are
   hidden, as the HTTP route hides them.
2. **Pass the injected `BackgroundTasks` to the Codex and Claude email send**
   (`routes-rest-agent-admin`, high). Every send through the documented integration is dropped
   while reporting success. Decision: forward the object, or set `wait_for_delivery`.
3. **Lock the memory store's read-modify-write and use a unique temp name** (`src-memory-rag`,
   high). Decision: a file lock, or pointing `mcp_servers/memory_server.py` at the app's API,
   because a process-local lock does not cover that second process.
4. **Make the release path depend on the tests, and add a lint and a type check** (Enforcement D).
   Decision: whether `docker-publish.yml` waits on `ci.yml` or runs the suite itself.
5. **Resolve owner identity in one place.** Six findings are the same defect in different files:
   a handler takes the caller's identity and does not apply it, or applies the shared `api`
   identity. They are `manage_research`, the bearer bucket on preferences, drafts and signatures,
   the bearer bucket on comparisons, the incognito purge, `classify_events`, and `daily_brief`.
   Decision: one helper that returns the storage owner, used by tools, routes and scheduled
   actions.
6. **Move blocking I/O off the event loop.** `PERF` is the second-largest tag at 30 findings, and
   its medium findings in `routes-email`, `routes-chat-session`, `routes-gallery-document` and
   `routes-rest-media-files` each describe an `async def` handler making a synchronous call.
   Decision: convert the handlers to `def`, or wrap the calls in `asyncio.to_thread`.
7. **Normalize the `app_api` path before the blocklist check** (`src-agent-tools`, medium), and
   add the percent-encoded and dot-segment forms to its tests.
8. **Read the front end and the tests next.** The grade cannot move above medium confidence, and
   the Testing letter cannot be confirmed, until they are read.

## Review rules

- A claim about the code cites a file and a line at `2992bf6d368a`, or a command and its
  output. Neither is optional.
- A number in prose is either computed by a tool or is not stated.
- A grade describes the surface that was read, and the reviewed surface is stated next to
  it.
- Every dimension letter cites this run's own evidence, and the rubric in
  [`docs/GRADING-RUBRIC.md`](../../../docs/GRADING-RUBRIC.md) states the scale, the rules,
  and where comparable evidence has landed. A letter that departs from that record says why
  in the basis column.
- Findings are counted with everything else, including findings that were corrected after
  the pass. The tables are a record, not an open-issue list.
