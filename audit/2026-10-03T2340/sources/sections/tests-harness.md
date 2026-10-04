# tests: harness, standards and helpers

## Overview

The machinery the suite runs on, rather than the product behaviour it pins: `tests/conftest.py` and
`tests/_taxonomy.py` (the collection-time `area_*`/`sub_*` markers, the `DATABASE_URL` default and
the not-installed dependency stubs), the shared helpers under `tests/helpers/` (script loading, core
DB stubs, import-state save/restore, fake Chroma and embedding lanes, temp SQLite, and the two Node
harnesses for the Settings shell), the two runners `tests/run_focus.py` and
`tests/run_order_report.py`, the streaming-render JS harness and its corpus, the generator behind
`tests/OVERSIZED_TEST_SPLIT_PLAN.md`, the four standards documents, and the 28 `tests/cli/` tests
that consume `cli_loader`.

The boundary: the suites this harness serves belong to the other `tests-*` sections, which judge the
production behaviour each test pins. This section judges only what the harness can and cannot catch —
whether the tree follows the rules `tests/TESTING_STANDARD.md` and `tests/README.md` state, whether a
fixture lets a test pass without exercising the code it names, and whether a test's outcome depends on
the working directory, a real network, wall-clock time or machine state. A production defect that a
weak test fails to catch is named here only as the consequence of the gap, and cross-referenced where
another section already reports the defect itself (for example `build-install-deploy` for the
`python3 -m pytest` string in `.github/scripts/focused_test_guidance.py`).

## Coverage

Line numbers refer to `2992bf6d368a`; `git diff --stat 2992bf6d368a -- tests/` is empty, so the
working tree matches the reviewed commit for every path below.

**Read fully:** all 50 assigned paths, 5,728 lines.

| Group | Files | Lines |
| --- | ---: | ---: |
| `tests/cli/*.py` (the CLI directory; `area_cli` selects 30 files — see the LAYOUT_INVENTORY finding) | 28 | 884 |
| `tests/conftest.py`, `tests/_taxonomy.py`, `run_focus.py`, `run_order_report.py`, `tools/build_oversized_test_split_plan.py` | 5 | 1,312 |
| `tests/helpers/*.py`, `test_settings_shell.js`, `test_settings_shell_coordinator.mjs` | 9 | 2,262 |
| `tests/streaming/corpus.mjs`, `invariant.test.mjs`, `markdownHarness.mjs`, `segmenter.test.mjs` | 4 | 265 |
| `LAYOUT_INVENTORY.md`, `OVERSIZED_TEST_SPLIT_PLAN.md`, `README.md`, `TESTING_STANDARD.md` | 4 | 1,005 |

`tests/helpers/__init__.py` is empty (0 bytes) — it exists only to make `tests.helpers` a package.

**Read partially — the code each finding rests on:** the 21 `scripts/odysseus-*` entry points each CLI
test targets, at the function under test (`_text_len`, `_preview_text`, `_text_field`, `_mask_token`,
`_recipient_list`, `_split_recipients`, `_memory_entries`, `_file_rows`, `_skill_entries`,
`_contact_rows`, `_entry_or_fail`, `_json_list`, `_json_dict`, `_decode_png_data`, `_summarize`,
`cmd_read`, `cmd_list`, `_resolve`, `_album_image_count`, `_calendar_name`, `_serialize`) and the
imports they need; `static/js/markdown/tableRow.js` and `static/js/ui.js` (`esc`) for the streaming
harness; `pyproject.toml` (`[tool.pytest.ini_options]`), `.github/workflows/ci.yml:104-146` (the
pytest job) and `tests/test_docker_devops_hardening.py:26-30`, `:244-251` (the doc-interpreter guard);
`tests/test_settings_shell_js_behavior.py` and `tests/test_streaming_segmenter_js.py`, which are the
pytest entry points for two of this section's harness files.

**Not read:** the ~800 remaining test modules and everything they cover — the other `tests-*` sections
own those, and this section's claims are about the harness those modules run on, not about them.
`tests/test_run_focus.py`, `tests/test_taxonomy.py`, `tests/test_run_order_report.py`,
`tests/test_helpers_import_state.py`, `tests/test_db_stubs_helper.py` and the six
`tests/test_embedding_lanes*.py` files are other sections' paths; they were read only as the
consumers of this section's helpers.

**Checks run** (project venv, from the repository root):

```
$ venv/bin/python -m pytest -q tests/cli/ tests/test_streaming_segmenter_js.py \
    tests/test_settings_shell_js_behavior.py tests/test_run_focus.py \
    tests/test_run_order_report.py tests/test_taxonomy.py tests/test_helpers_import_state.py \
    tests/test_db_stubs_helper.py tests/test_embedding_lanes.py tests/test_embedding_lanes_memory.py \
    tests/test_embedding_lanes_rag.py tests/test_embedding_lanes_tool_index.py \
    tests/test_embedding_lanes_legacy.py tests/test_embedding_lane_ndarray_restore.py
214 passed, 1 warning in 3.32s

$ venv/bin/python -m pytest -q tests/cli/
48 passed, 1 warning in 0.11s

$ venv/bin/python -m pytest --collect-only -q          # collection cost, whole suite
5956 tests collected in 1.98s

$ node --test tests/streaming/segmenter.test.mjs tests/streaming/invariant.test.mjs
ℹ tests 120   ℹ pass 120   ℹ fail 0   ℹ duration_ms 198.918435

$ node --experimental-vm-modules tests/helpers/test_settings_shell_coordinator.mjs
{"realEsmGraph":true,"initialization":true,"finderBinding":true,"sidebarBinding":true,
 "navigationCallback":true,"directOpen":true,"directClose":true}
```

Nothing in this slice reaches the network or the wall clock: `grep -rn
"chdir\|urlopen\|requests\.\|time\.sleep\|datetime\.now\|time\.time()"` over the 15 pytest files
listed above returns one line, `tests/test_run_order_report.py:129: monkeypatch.chdir(tmp_path)`, which
restores on teardown. The 214 tests are the whole surface of the assigned files and they run in 3.3 s.
The two Node harnesses are wired into
pytest by `tests/test_streaming_segmenter_js.py:23` and `tests/test_settings_shell_js_behavior.py:94`,
both of which skip cleanly on a missing `node` (`shutil.which`), as `TESTING_STANDARD.md:109-111`
requires. Everything else in this section is probes under `/tmp/audit-probe/`, quoted in the findings
that use them; no probe touched the target tree.

### [BUG] The `odysseus-logs` non-string regression test cannot fail on a clean checkout

- **Location:** `tests/cli/test_logs_cli_resolve_nonstring.py:10`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the whole test is two assertions on `_resolve`:

  ```python
  def test_non_string_name_returns_none():
      cli = load_script("odysseus-logs")
      assert cli._resolve(None) is None
      assert cli._resolve(123) is None
  ```

  The guard it pins is `scripts/odysseus-logs:61-62` (`if not isinstance(name, str): return None`).
  Without that guard the function falls through to `for p in base.glob("*.log"): ... name in p.name`
  (`:64-68`), which only raises for a non-string `name` when at least one `*.log` file exists in
  `logs/` or `/tmp/odysseus-tmux` — and the test creates neither. A probe that loads the same script
  with the guard text deleted (`/tmp/audit-probe/logs_guard_probe.py`) shows both outcomes:

  ```
  app logs dir exists: True files: []
  tmux logs dir exists: True files: []
  UNFIXED _resolve(None) with the environment as-is -> None
  UNFIXED _resolve(None) with one *.log present -> TypeError: 'in <string>' requires string as left
  operand, not NoneType
  ```

  So the test passes on a clean machine with or without the fix. In CI it is provably vacuous:
  `logs/` is git-ignored (`.gitignore:31`) so a fresh clone has no `logs/` directory at all,
  `.github/workflows/ci.yml:143` creates only `data/`, and `/tmp/odysseus-tmux` does not exist on a
  GitHub runner — both `base.is_dir()` checks are False and `_resolve` returns `None` for every input.
  On a developer machine the same test silently changes meaning, because the app's own tmux sessions
  write `*.log` files into `/tmp/odysseus-tmux` (`scripts/odysseus-logs:5-6`), which makes the
  assertion depend on machine state rather than on the code.
- **Impact:** a user-visible crash path has a regression test that cannot detect its regression.
  `odysseus-logs tail <name>`/`cat <name>` raise `TypeError` for a non-string `name` again and CI
  stays green; meanwhile the suite's result on a developer machine depends on what is in `/tmp`.
  This violates `TESTING_STANDARD.md:35-46` (deterministic, no reliance on wall-clock/network/RNG
  and environment-independent) — the test is neither.
- **Fix:** point the module at a temp directory inside the test instead of relying on the machine,
  e.g. `monkeypatch.setattr(cli, "_APP_LOGS", tmp_path)` with a `tmp_path / "app.log"` file and
  `monkeypatch.setattr(cli, "_TMUX_LOGS", tmp_path / "tmux")`, the way
  `tests/cli/test_research_cli_store.py:13` and `tests/cli/test_preset_cli_store.py:8` already inject
  their data paths. One added assertion that the unfixed form would raise would pin the regression.

### [DOC-DRIFT] `conftest.py`'s pre-import block makes the module-scope stub guards for the modules it pre-imports dead in 23 files

- **Location:** `tests/conftest.py:20` (with `:25-31`, `:53-57`, `:59-62`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the root conftest documents that test-module stubs win or lose depending on what has
  already been imported, and resolves it by importing the real modules first:

  ```python
  # Pre-import real heavy modules BEFORE any test file's module-level stubs can
  # replace them with MagicMock. Some test files (e.g. test_llm_core_sanitize_*)
  # stub sqlalchemy/core.database at module scope with `if mod not in sys.modules`,
  # which fires during collection. If the real module hasn't been imported yet,
  # the stub wins and contaminates every subsequent test that needs the real ORM.
  ```

  `grep -rn "if .*not in sys.modules" tests/*.py | wc -l` returns 47 sites across 33 test files, and
  because `sqlalchemy`, `core.database`, `src.database` and `core.models` are already in `sys.modules`
  when collection starts, every one of those guards that names one of the four is dead. Those guards
  sit in 23 of the 33 files (one stub block each, in both the inline and the loop form); the other 24
  sites name modules the block never touches. A probe
  plugin (`/tmp/audit-probe/probe_plugin.py`) that reports the module objects at
  `pytest_collection_finish` confirms the real modules, not stubs, are what the guards see:

  ```
  [probe] core.database: type=module __file__='/home/lhl/github/lhl/odysseus/core/database.py'
  [probe] core.models:   type=module __file__='/home/lhl/github/lhl/odysseus/core/models.py'
  [probe] sqlalchemy:    type=module __file__='.../site-packages/sqlalchemy/__init__.py'
  [probe] src.database:  type=module __file__='/home/lhl/github/lhl/odysseus/src/database.py'
  ```

  `tests/test_compaction_summary_failure.py:11-22` is the pattern: a docstring that says "Uses mock
  imports to avoid loading the full app stack", followed by `if mod not in sys.modules: sys.modules[mod]
  = MagicMock()` for exactly those four names — none of which installs. The standard calls the
  underlying property a bug: "**Order independence** — a test must not depend on a sibling having
  imported, cached, or stubbed something first. Order-sensitivity is a bug to fix, not a constraint to
  encode" (`TESTING_STANDARD.md:112-114`), and the harness ships `tests/helpers/import_state.py` plus
  the report-only `tests/run_order_report.py` for precisely this.
- **Impact:** the harness's correctness rests on a documented collection-order dependency instead of
  the helper built to remove it, and the mitigation covers only the four pre-imported names — the other
  guard sites in those 33 files name modules the block never touches, so whether they install still
  depends on which file pytest imports first. A test
  that believes it is running against a stub gets the real module with `DATABASE_URL=sqlite:///:memory:`
  and no warning, so its hermeticity claim is unverified.
- **Fix:** move the module-scope installs in the 33 files onto
  `tests.helpers.import_state.preserve_import_state` (documented for exactly this in `tests/README.md:177`)
  and delete the pre-import block, so a stub is either explicitly in scope or absent. If the block
  stays, say in the comment that the guards naming those four modules are inert.

### [DOC-DRIFT] `LAYOUT_INVENTORY.md` documents a move that already happened and a boundary that no longer holds

- **Location:** `tests/LAYOUT_INVENTORY.md:50` (with `:22`, `:48-49`, `:62-93`, `:121-131`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the document plans the first low-risk split and claims its boundary is mechanical: "the
  set is exactly the files classified `area_cli` by `_taxonomy.py`, so before/after selection counts
  can be compared mechanically" (`:50-52`). The move is done — all 28 files are tracked at
  `tests/cli/` — but the inventory still lists them at their pre-move paths (`:66-93`), and its own
  verification snippet (`:126-127`, `Path("tests").glob("test_*.py")`) does not recurse. Run verbatim
  today it prints the opposite of the "Expected: 28 files" comment at `:121`:

  ```
  $ venv/bin/python - <<'PY'   # the snippet at LAYOUT_INVENTORY.md:122-132
  ...classify_test_path(p).area == "cli"...
  PY
  2
  tests/test_calendar_cli_overlap.py
  tests/test_memory_cli_add_nondict.py
  security
  ```

  `area_cli` is now 30 files, not 28, and two of them (`tests/test_calendar_cli_overlap.py`,
  `tests/test_memory_cli_add_nondict.py`) are flat under `tests/` because `_taxonomy.py` matches the
  filename token `cli` (`tests/_taxonomy.py:26`, in the `KEYWORD_AREAS` priority order at `:42-48`)
  and never looks at the directory — the same reason the inventory gives at `:94-98` for excluding
  `tests/test_backup_cli_security.py`. So `tests/cli/` and `area_cli` no
  longer agree, and the before/after count comparison the document prescribes (`:165-167`) cannot be
  reproduced. The coupling claim is also stale: "every file imports only the script under test (via
  `cli_loader`) plus `tests.helpers` stubs — no app, no routes, no real DB" (`:48-49`) is contradicted
  by eight of the 28 files, which install stubs for production modules —
  `tests/cli/test_mail_cli_recipients.py:9`, `:17` (`routes.email_helpers`, `routes.email_pollers`),
  `tests/cli/test_mail_cli_read_empty_fetch.py:31`, `:38`, `tests/cli/test_contacts_cli_rows.py:9`
  (`routes.contacts_routes`), `tests/cli/test_memory_cli_rows.py:9`, `tests/cli/test_skills_cli_rows.py:9`,
  `tests/cli/test_skills_cli_preview.py:15` (`services.memory.*`), `tests/cli/test_personal_cli_rows.py:9`
  (`src.personal_docs`), `tests/cli/test_signature_cli_export.py:8-11` (`sqlalchemy`, `core`,
  `core.database`). The inventory's own coupling grep (`:137-138`) searches only for
  `TestClient|FastAPI|create_app|SessionLocal|sqlite|dependency_overrides`, so it would not have
  surfaced any of them. `TESTING_STANDARD.md:55` was updated for the same move ("the current `area_cli`
  set has moved to `tests/cli/`"); the inventory was not.
- **Impact:** the next refactor slice that trusts this document starts from a false baseline: the file
  list is wrong, the prescribed check prints `2`, and the "crisp, machine-checkable boundary" it uses
  to justify moving CLI tests ahead of everything else has already stopped being crisp. An agent or
  contributor following the validation block records a bogus baseline and compares against it.
- **Fix:** either mark the document as the historical plan for a completed move, or regenerate it —
  replace the flat paths with `tests/cli/…`, restate the boundary as "the 28 files under `tests/cli/`"
  (not "the `area_cli` set"), note the two flat `area_cli` stragglers as the next reclassification
  candidate, and make the check recurse (`Path("tests").rglob("test_*.py")`) so it counts the files it
  claims to count.

### [DOC-DRIFT] The oversized-split plan's metrics are stale against its own freshness check

- **Location:** `tests/OVERSIZED_TEST_SPLIT_PLAN.md:29` (with `:30`, `:34-47`, `:319-326`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the document says its metrics "were generated from the current test tree" and ships a
  freshness check that must produce no diff (`:319-326`, `git diff --exit-code --
  tests/OVERSIZED_TEST_SPLIT_PLAN.md`). Regenerating with the committed builder — imported and run with
  `OUTPUT` redirected to `/tmp` so the tree is untouched (`/tmp/probe_regen_plan.py`) — does not
  reproduce it:

  ```
  $ diff tests/OVERSIZED_TEST_SPLIT_PLAN.md /tmp/plan-regen.md
  29,30c29,30
  < - test files scanned: 583
  < - collected pytest items counted: 3586
  ---
  > - test files scanned: 829
  > - collected pytest items counted: 5956
  38c38
  < | cli | 28 |
  ---
  > | cli | 30 |
  ```

  Every area row moves (security 77→97, services 144→216, uncategorized 234→338, js 39→62), and the
  regenerated tables list files the committed plan never mentions. `tests/tools/build_oversized_test_split_plan.py:82-90`
  re-runs `pytest --collect-only -q tests`, so the two numbers are deterministic counts of the same
  tree; 583/3586 is a snapshot of an older, much smaller `tests/`. The plan's closing section still
  reads "Use this plan to choose the first actual oversized-file split issue" (`:305-309`), so it is
  an open plan rather than a closed record, and the "Suggested first manual-review candidates" table
  is drawn from the stale candidate set.
- **Impact:** whoever picks the first split from this plan is choosing from a candidate list that
  leaves out roughly 30% of the current test files (583 scanned against 829 present), with thresholds
  applied to numbers that no longer describe the tree. The check meant to prevent exactly this
  (`:319-326`) therefore fails today.
- **Fix:** regenerate the document with `tests/tools/build_oversized_test_split_plan.py` and commit the
  result, or add the freshness check to CI (`.github/workflows/ci.yml`) so the drift is caught when it
  happens instead of by a reviewer who happens to regenerate it.

### [HARDCODE] The plan, its generator and `run_focus.py` name an interpreter path that does not exist

- **Location:** `tests/tools/build_oversized_test_split_plan.py:511` (with `:519`,
  `tests/OVERSIZED_TEST_SPLIT_PLAN.md:316`, `:324`, `tests/run_focus.py:185`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the builder writes the reproduction and freshness commands into the plan as literal
  strings, and both use `.venv/bin/python`:

  ```python
  # tests/tools/build_oversized_test_split_plan.py:509-521
  "```bash",
  ".venv/bin/python tests/tools/build_oversized_test_split_plan.py",
  "```",
  ...
  ".venv/bin/python tests/tools/build_oversized_test_split_plan.py",
  "git diff --exit-code -- tests/OVERSIZED_TEST_SPLIT_PLAN.md",
  ```

  This checkout has `venv/`, not `.venv` (`ls -d .venv` → `No such file or directory`), and the
  project's own rule is `./venv/bin/python -m pytest` (`TESTING_STANDARD.md:27`, restated in
  `tests/README.md:64-66`). The repository already treats `.venv/bin/python` as a stale pattern:
  `tests/test_docker_devops_hardening.py:244-251` fails if that string appears in
  `tests/README.md`, `tests/TESTING_STANDARD.md` or `tests/LAYOUT_INVENTORY.md` — the generated plan
  and the generator are simply outside that guard's file list (`:26-30`). `tests/run_focus.py:185`
  repeats it in the docstring that tells a contributor how to invoke the runner. The same class of
  wrong-interpreter instruction in `.github/scripts/focused_test_guidance.py` is already reported in
  `build-install-deploy`; this is a different file and a different wrong path. (`tests/run_order_report.py:14-15`
  has the third variant, `python3 tests/run_order_report.py`, which contradicts `tests/README.md:96`
  for the same command.)
- **Impact:** the two commands the plan tells a contributor to copy fail immediately with "no such
  file or directory", so the freshness check above is not just skipped but un-runnable as written. The
  wrong-path text is generated, so it comes back on every regeneration.
- **Fix:** use `./venv/bin/python` in `tests/tools/build_oversized_test_split_plan.py:511`, `:519` and
  `tests/run_focus.py:185`, regenerate the plan, and add `tests/OVERSIZED_TEST_SPLIT_PLAN.md` plus
  `tests/tools/` to the `TEST_DOCS`/`stale_patterns` coverage in
  `tests/test_docker_devops_hardening.py:26-30` so the string cannot return.

### [DUP] The streaming harness inlines copies of three real sibling modules, and one copy has already diverged

- **Location:** `tests/streaming/markdownHarness.mjs:30` (with `:29`, `:34-47`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the harness loads the real `static/js/markdown.js` but replaces its sibling imports
  with hand-written text spliced in by regex, and the file's header claims the result is the real
  thing: "This mirrors the loader in tests/test_markdown_rendering_js.py so the streaming tests
  exercise the exact same renderer the browser runs" (`:1-4`). `splitTableRow` is replaced by an
  inlined one-liner (`:32`):

  ```js
  function splitTableRow(row){return (row||'').replace(/^\s*\|/,'').replace(/\|\s*$/,'').split('|').map((c)=>c.trim());}
  ```

  while the module it stands in for guards its input: `static/js/markdown/tableRow.js:13` reads
  `const text = typeof row === 'string' ? row : '';`. A probe that runs both implementations over the
  same inputs (`/tmp/audit-probe/table_row_probe.mjs`) shows they agree on every string case but not on
  the non-string case the real module defends against:

  ```
  same  "| a | b |"  real=["a","b"]  stub=["a","b"]
  same  "| a |  | c |"  real=["a","","c"]  stub=["a","","c"]
  same  "| a \\| b | c |"  real=["a \\","b","c"]  stub=["a \\","b","c"]
  DIFF  {}   -> TypeError: (row || "").replace is not a function
  ```

  `escapeHtml` is replaced the same way (`:43-47`) with a re-implementation of `ui.js`'s `esc`
  (`static/js/ui.js:786-788`, `(s || '').replace(...)` versus the harness's `String(v ?? '')...`), and
  `emojiShortcodes.js` is inlined with `export` stripped by regex (`:34-42`). Nothing fails if these
  copies drift further: the harness only breaks if the import *statement* it matches disappears.
- **Impact:** the streaming invariant test — the one test that fuzzes the freeze/tail split at every
  prefix of every corpus sample — is comparing two renders that both come from the copied functions,
  so a change to the real `tableRow.js` or `ui.js` escaping is invisible to it. The corpus's
  `gfm table` sample and the code-fence samples pass through the copies, and the suite would keep
  passing while the browser renders something else. The divergence above is latent today because the
  corpus only feeds strings, but the copies are the reason the divergence cannot be noticed.
- **Fix:** import the real modules instead of inlining them — `markdownHarness.mjs` already runs under
  Node's ESM loader, so `splitTableRow` and `esc` can be imported and injected into the data-URL module
  (or `markdown.js` can be loaded through a small `vm`/loader shim as
  `test_settings_shell_coordinator.mjs:872-930` does for `settings.js`). If the inline copies stay, add
  a test that runs both implementations over the same inputs, so drift fails loudly.

### [FOOTGUN] `cli_loader.load_script` never registers the module, so a script using a string-annotated dataclass cannot be loaded

- **Location:** `tests/helpers/cli_loader.py:24`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `load_script` builds the module, executes it and returns it without ever putting it in
  `sys.modules` (`:20-25`):

  ```python
  loader = importlib.machinery.SourceFileLoader(module_name, str(path))
  spec = importlib.util.spec_from_loader(loader.name, loader)
  module = importlib.util.module_from_spec(spec)
  loader.exec_module(module)
  return module
  ```

  A module that is absent from `sys.modules` cannot be found by `cls.__module__` lookups. A probe that
  replicates those four lines byte for byte against a script using a string-annotated dataclass
  (`/tmp/audit-probe/loader_dataclass_probe.py`) fails:

  ```
  AttributeError: 'NoneType' object has no attribute '__dict__'
  registered first: loaded fine -> Row(name='a', tags=('b',))
  ```

  The same file loads normally as soon as it is inserted into `sys.modules` before `exec_module`.
  `scripts/pr_blocker_audit.py` and `scripts/agent_migration_manifest.py` are the two `scripts/` entry
  points that use `@dataclass`; neither is loaded through this helper today, so nothing fails now. The
  helper's docstring and `tests/README.md:158-165` state the one import-time requirement it has
  (inject `sys.modules` stubs first) but not this one.
- **Impact:** a contributor adding a `@dataclass` to any of the 21 scripts the CLI tests load gets a
  bare `AttributeError` from `dataclasses` with no mention of the loader, and the natural next step is
  to blame their script rather than the harness. The failure mode is also easy to misdiagnose as
  "works when run directly, fails only under test".
- **Fix:** register the module for the duration of the load and clean up afterwards, e.g.
  `sys.modules[module_name] = module` inside a `try/finally` that pops it when the helper installed it
  (the module is deliberately *not* cached across calls, so the cleanup must preserve that), and note
  the requirement in the docstring next to the existing stub warning.

### [FOOTGUN] `run_focus.py` builds a pytest command with no target path, so the selection follows the caller's working directory

- **Location:** `tests/run_focus.py:187`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `build_pytest_command` starts from `[python, "-m", "pytest"]` and appends only `-m`,
  `-k`, `--last-failed` and duration flags (`:187-201`). There is no path argument and no `cwd=`, so
  pytest resolves `rootdir`, `testpaths` and collection from wherever the caller happens to be.
  `--dry-run` from the repository root prints a command with no target:

  ```
  $ venv/bin/python tests/run_focus.py --dry-run --area cli
  /home/lhl/github/lhl/odysseus/venv/bin/python -m pytest -m area_cli
  ```

  Running that same command from another directory — the documented `--area` workflow, with a decoy
  test file present — collects the decoy and none of the 50 `area_cli` tests:

  ```
  $ cd /tmp/audit-probe/cwd && <venv>/python -m pytest -m area_cli -q
  1 deselected in 0.00s        (exit 5)
  $ cd /home/lhl/github/lhl/odysseus && venv/bin/python -m pytest -m area_cli --collect-only -q
  50/5956 tests collected (5906 deselected) in 1.88s
  ```

  The neighbouring runner gets this right by stating it: `tests/run_order_report.py:109-112` prints the
  working directory and tells the reader to reproduce "from this working directory".
- **Impact:** a contributor who runs the documented command from a subdirectory, a `--last-failed`
  workflow started elsewhere, or a script whose cwd is not the repository root gets pytest's exit 5
  with no hint that the selection silently changed target — and pytest exit 5 is easy to read as "the
  focused lane is empty" rather than "the runner did not point at `tests/`".
- **Fix:** append `str(TESTS_DIR)` to the command in `build_pytest_command` (it is already computed at
  `:31`), or pass `cwd=PROJECT_ROOT` to the executor in `run()` (`:289-316`). Either makes the
  selection independent of where the user stands.

### [DOC-DRIFT] `tests/README.md` says no test is marked `slow`, but the fast lane already excludes five

- **Location:** `tests/README.md:54`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the fast-lane section states:

  ```
  `and`. Because no tests may be marked `slow` yet, `--fast` can initially match
  the full focused selection; it becomes a real speed-up as `slow` marks are added
  from duration evidence.
  ```

  Five tests carry the marker (`tests/test_auth_config_lock_concurrency.py:66`, `:105`, `:133`,
  `:159`, `:206`), and the fast lane already deselects them:

  ```
  $ venv/bin/python -m pytest -m "not slow" --collect-only -q
  5951/5956 tests collected (5 deselected) in 1.98s
  ```

  The `--fast` behaviour itself is correct — `tests/run_focus.py:171-172` composes `not slow` with the
  area/sub-area expression using `and` — so only the sentence describing the current state is wrong.
  `TESTING_STANDARD.md:78-90` describes the fast lane without the "no tests may be marked slow yet"
  claim, so the two documents now disagree about the same fact.
- **Impact:** a reviewer reading `tests/README.md` concludes that `--fast` cannot hide anything yet and
  therefore treats it as equivalent to the full selection; in fact it silently skips the five
  concurrency tests, which are the ones most likely to be flaky and most likely to need the reviewer's
  attention. `tests/test_run_focus.py` pins the marker arithmetic but not this sentence.
- **Fix:** replace the clause with the current count, e.g. "five tests are marked `slow` today
  (`tests/test_auth_config_lock_concurrency.py`), so `--fast` excludes them; add marks only from
  `--durations` evidence", and keep the count out of the prose by pointing at `-m slow --collect-only`
  if it is expected to drift.

### [DUP] Two CLI tests re-implement `cli_loader.load_script` instead of using it

- **Location:** `tests/cli/test_research_cli_status.py:21` (with `tests/cli/test_research_cli_status_filter.py:27`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** both files open with their own copy of the helper:

  ```python
  # tests/cli/test_research_cli_status.py:21-27
  def _load_cli():
      path = ROOT / "scripts" / "odysseus-research"
      loader = importlib.machinery.SourceFileLoader("odysseus_research_cli_status", str(path))
      spec = importlib.util.spec_from_loader(loader.name, loader)
      module = importlib.util.module_from_spec(spec)
      loader.exec_module(module)
      return module
  ```

  `tests/cli/test_research_cli_status_filter.py:27-33` is the same five lines under a different module
  name (`odysseus_research_cli`). `tests/README.md:156-159` defines the helper for exactly this case —
  "Use when a test needs to import a script under `scripts/` without repeating `SourceFileLoader` /
  `importlib.util` boilerplate" — and `tests/LAYOUT_INVENTORY.md:22-23` describes the whole CLI group as
  the files that "load `scripts/` entry points via `tests.helpers.cli_loader.load_script`". The other 26
  files in the directory do use it. Because the two copies name the module differently, the same script
  is loaded under two identities inside one directory, which is the kind of drift the shared helper
  exists to prevent.
- **Fix:** replace both `_load_cli` bodies with `from tests.helpers.cli_loader import load_script` and
  `load_script("odysseus-research")`, as `tests/cli/test_research_cli_store.py:4` already does in the
  same directory, and delete the now-unused `importlib` imports.
