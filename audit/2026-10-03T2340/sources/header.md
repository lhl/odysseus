# odysseus Code Audit

| | |
| --- | --- |
| **Audit date** | 2026-10-03 |
| **Snapshot** | `2992bf6d368a` of https://github.com/odysseus-dev/odysseus |
| **Run** | `odysseus/2026-10-03T2340` |
| **Findings** | 399 — 3 high, 106 medium, 290 low |
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

`TEST-GAP` is for a path with no test at all, or a test no gate runs. A test that exists and passes
without exercising the code it names is tagged `BUG`, so the 8 `tests-*` sections' findings of that
shape are found under `BUG`, not under `TEST-GAP`.

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
