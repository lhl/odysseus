# odysseus Codebase Review

This file is edited by hand. Unlike [`README.md`](README.md), it is not generated.

The tables between `<!-- metrics: name -->` and `<!-- /metrics: name -->` markers are
computed by `./audit.py table`. Paste its output over a block to update it; `./audit.py
fill` does every block at once. Prose is never rewritten by a tool, so a sentence that
cites a number is yours to keep true.

| | |
| --- | --- |
| **Review date** | 2026-10-05 |
| **Subject** | [the code audit](README.md), audit date 2026-10-03, `2992bf6d368a` |
| **Counts as of** | that audit snapshot, after the re-review of 2026-10-05 |
| **Coverage** | All 58 sections reviewed. At least 220,914 of 468,155 lines (47.2%) were read end to end; see [Coverage by surface](#coverage-by-surface). |
| **Tooling** | `./audit.py build` (the generated audit), `./audit.py table` (these tables), `./audit.py check` (the gate) |

## Updating the tables

The tables are snapshots of one run. After the audit changes:

1. Run `./audit.py verify odysseus/2026-10-03T2340` to list stale blocks.
2. Run `./audit.py fill odysseus/2026-10-03T2340` to refresh them.
3. Update any prose that cites a number from a refreshed block. No tool checks prose.

## Verdict

**Grade: C (confidence: medium — at least 47.2% of the tree read end to end).**

The letter covers all 58 sections. The backend (`core`, `src`, `routes`, `services`) was read
whole. The front end was read whole for small modules and in regions for the largest files, and
three test sections sampled.

Correctness, Security and Testing drive the letter. The run records 400 defects, five of them
high. Two of the five are script execution in the browser, which the first pass rated medium and
the re-review of 2026-10-05 measured. The test suite is large and CI runs all of it, but 50 of the
72 findings in the test sections are tests that pass without exercising the code they name.
Enforcement is the weakest dimension: the release image is published by a workflow that runs no
test.

The count of 400 is a floor set by what was read. See
[Coverage boundaries](README.md#coverage-boundaries) for what each re-review covered.

### Report card

The six dimensions and the scale are fixed by
[`docs/GRADING-RUBRIC.md`](../../../docs/GRADING-RUBRIC.md). Densities divide by 220.9 KLOC, the
lines read end to end. That figure is a floor, so each density is an upper bound.

| Dimension | Grade | Basis |
| --- | --- | --- |
| Correctness | C | `(10 × 5 + 3 × 105 + 290) / 220.9` = at most 2.97 weighted defects per reviewed KLOC, on 5 high, 105 medium, 290 low. The record places 2.02 at C and 3.03 at D. C is kept because the denominator omits the large files read in regions, and because each of the five highs has a fix of a few lines. |
| Security | C | Worst `SECURITY` severity is high, carried by three findings: `manage_research` reads and deletes every user's research files, and a search-result title and a calendar location each run script in the app's origin. 24 more are medium and 29 are low. The script policy allowlists a public CDN, so it did not stop the two injections. The agent tool gate is ordered and fails closed (`ToolRunSecurityContext.decision_for`), which kept three injection findings at medium in the re-reviews. No committed credential was found: the secret gate matches none of the secret-shaped values in the tree against this run. D was considered and not used because the gates, the address guards and the at-rest encryption exist and mostly hold. |
| Testing | C | `ls tests/*.py` lists 805 modules, and `.github/workflows/ci.yml:145` runs `python -m pytest -q` on push and pull request. The third step fails: 50 of the 72 findings in the eight test sections are tests that assert on a copy of the code, a source substring or a stubbed guard. Three test sections sampled, so the 50 is a floor. |
| Enforcement | D | CI gates on `compileall`, `node --check` and the full test suite. No lint or type check is configured. `docker-publish.yml:13-15` publishes on push to `dev` and `main`, and its one `needs:` names its own build job, not the test job. The rubric grades a missing lint or type check F; D is used because CI exists and runs every test. |
| Documentation | C | 35 `DOC-DRIFT` findings, at most 0.16 per reviewed KLOC; the record places 0.13 at C. 32 of the 35 are in the specifications, the root documents, the website and the test standards. |
| Maintainability | C | 61 `DEAD-CODE` + `DUP` + `FOOTGUN` findings, at most 0.28 per reviewed KLOC, between the 0.07 the record places at B and the 0.35 it places at D. |
| **Overall** | **C** | Four dimensions at C, one at D, none above C. Correctness, Security and Testing drive it. |

### Coverage by surface

| Surface | Findings | What was read |
| --- | --- | --- |
| `core` | 12 — 0 high, 5 medium, 7 low | 2 sections, 11 files, 5,182 lines, all read. |
| `src` | 85 — 2 high, 30 medium, 53 low | 15 sections, 149 files, 62,737 lines, all read. |
| `routes` | 65 — 1 high, 23 medium, 41 low | 13 sections, 86 files, 47,962 lines, all read. |
| `services` | 29 — 0 high, 4 medium, 25 low | 5 sections, 40 files, 10,136 lines, all read. |
| `static` | 61 — 2 high, 11 medium, 48 low | 8 sections. Small modules read whole; the largest files read in regions that each section's Coverage lists. `static/lib/` checked for provenance only. |
| `tests` | 72 — 0 high, 19 medium, 53 low | 8 sections. Five read every assigned file. `tests-rest` read 47 of 322 files, `tests-llm-tools` 46 of 121, `tests-cookbook-models` 59 of 112. |
| Root, build, CI, `specs`, `scripts`, `mcp_servers`, `companion`, `swift`, `website` | 76 — 0 high, 13 medium, 63 low | 7 sections. All assigned files read except `specs`, which read 30 of 61. |

The 220,914 lines are the backend's 126,017 plus the 94,897 that 17 of the other 23 sections
state as read end to end. Six sections state their coverage in files, and their lines are not in
the figure.

<!-- metrics: counts -->
| Count | Value |
| ---: | ---: |
| Findings | 400 |
| High severity | 5 |
| Medium severity | 105 |
| Low severity | 290 |
| Disposition `fix-now` | 11 |
| Disposition `next` | 303 |
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
| Working tree | dirty |
<!-- /metrics: scale -->

### Findings

<!-- metrics: findings -->
| Section | Findings | High | Medium | Low |
| --- | ---: | ---: | ---: | ---: |
| Repository root and project policy | 8 | 0 | 1 | 7 |
| Build, install, launcher, CI and containers | 11 | 0 | 1 | 10 |
| Specifications | 11 | 0 | 0 | 11 |
| Operational scripts | 24 | 0 | 8 | 16 |
| core: auth, sessions, middleware, models | 6 | 0 | 2 | 4 |
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
| static: chat, sessions and composer UI | 8 | 1 | 1 | 6 |
| static: documents, notes, email, calendar UI | 8 | 1 | 2 | 5 |
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
| **Total** | **400** | **5** | **105** | **290** |
<!-- /metrics: findings -->

### Tags

<!-- metrics: tags -->
| Tag | Findings |
| --- | ---: |
| `BUG` | 155 |
| `SECURITY` | 56 |
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
| `fix-now` | 11 |
| `next` | 303 |
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

- **Test files outside the samples.** 403 files in the three sampled test sections were not read
  end to end.
- **The largest front-end files, line by line.** They were read in the regions each section lists.
- **Runtime behaviour.** No deployment was built and the full suite was not run. Measurements are
  the probes each finding records.
- **279 of the 290 lows** were not read by either re-review. A script checked their quoted code
  and locations against the source.
- **The Gates table reads "no invocable targets"** because the repository has no Makefile or
  package script. The gates are the CI jobs named in the report card.

## Recommendations

1. **Write the research spinner's message as text, and escape the calendar location before
   linkifying it** (`static-js-chat`, `static-js-documents-email`, both high). Each runs
   attacker-supplied script in the user's session.
2. **Remove `cdn.jsdelivr.net` from `script-src`** (`core-auth-session`, medium). It is the reason
   the two findings above execute. Decision: self-host Pyodide, or load it in a sandboxed frame.
3. **Filter `manage_research` by owner** (`src-agent-tools`, high). Decision: whether owner-less
   legacy files are hidden, as the HTTP route hides them.
4. **Pass the injected `BackgroundTasks` to the Codex and Claude email send**
   (`routes-rest-agent-admin`, high). Decision: forward the object, or set `wait_for_delivery`.
5. **Lock the memory store's read-modify-write and use a unique temp name** (`src-memory-rag`,
   high). Decision: a file lock, or pointing `mcp_servers/memory_server.py` at the app's API,
   because a process-local lock does not cover that second process.
6. **Make the release path depend on the tests, and add a lint and a type check** (Enforcement D).
   Decision: whether `docker-publish.yml` waits on `ci.yml` or runs the suite itself.
7. **Resolve owner identity in one place.** The executive summary lists the findings that share
   this cause. Decision: one helper that returns the storage owner, used by tools, routes and
   scheduled actions.
8. **Move blocking I/O off the event loop.** `PERF` holds 35 findings, and its mediums each
   describe an `async def` handler making a synchronous call. Decision: convert the handlers to
   `def`, or wrap the calls in `asyncio.to_thread`.
9. **Replace the tests that pin a copy of the code** with tests that drive the real call path,
   starting with the stubbed URL guards in the CalDAV and CardDAV suites.
10. **Re-derive the specifications from the code**, security claims first.

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
