# Operational scripts

## Overview

Everything under `scripts/` that an operator runs by hand: the `odysseus` umbrella dispatcher, the
twenty `odysseus-<subcommand>` CLIs and the two shell-completion files that drive them, the
`scripts/_lib` helpers they import, and the standalone operational tools (backup/restore, the two
image servers, the database and vector-store migrations, the hardware-fit catalogue writers, the
demo-email seeder, the host GPU probes, and the PR-audit and migration-manifest helpers). The
section stops where these scripts call into the application: `src/*`, `core/*`, `routes/*` and
`services/*` belong to the `src-*`, `core-*`, `routes-*` and `services-*` sections, so a defect
that lives in one of those modules is cross-referenced here rather than re-reported.

The recurring question in this slice is what a script assumes about its environment. Nine scripts —
eight of the `odysseus-*` CLIs plus the demo-email seeder — resolve `data/` from the repository root
instead of the application's `DATA_DIR`, so on any install that sets `ODYSSEUS_DATA_DIR` they read
and write a different store than the server does. The two
image servers are started with `--host 0.0.0.0` by the Cookbook and accept unbounded generation
parameters. `odysseus-backup` writes the archive that contains the Fernet key, and its restore path
does not put the key's mode back. The rest are error-handling and diagnostic defects in scripts
that an operator runs by hand, once, at the moment they need it to be right.

## Coverage

**Read fully:** all 40 assigned files.

- `scripts/odysseus`
- all twenty `scripts/odysseus-*` CLIs:
  - `backup`
  - `calendar`
  - `contacts`
  - `cookbook`
  - `docs`
  - `gallery`
  - `logs`
  - `mail`
  - `mcp`
  - `memory`
  - `notes`
  - `personal`
  - `preset`
  - `research`
  - `sessions`
  - `signature`
  - `skills`
  - `tasks`
  - `theme`
  - `webhook`
- `scripts/_lib/cli.py`
- `scripts/_lib/__init__.py` (empty, 0 bytes)
- `scripts/_completion/odysseus.bash`
- `scripts/_completion/odysseus.zsh`
- `scripts/check-docker-gpu.sh`
- `scripts/check-docker-amd-gpu.sh`
- `scripts/encode_previews.sh`
- `scripts/demo_email/manage.sh`
- `scripts/demo_email/demo_account.py`
- `scripts/demo_email/seed_demo_emails.py`
- `scripts/claim_ownerless.py`
- `scripts/fix_paths.py`
- `scripts/update_database.py`
- `scripts/hf_download.py`
- `scripts/migrate_faiss_to_chroma.py`
- `scripts/index_documents.py`
- `scripts/migrate_searxng_settings.py`
- `scripts/mlx_image_server.py`
- `scripts/backfill_model_release_dates.py`

**Read partially:** five files.

- `scripts/diffusion_server.py`: the module head, the security middleware, both request models, the
  `/v1/models`, `/v1/images/generations` and `/v1/images/progress` bodies, the start of
  `/v1/images/edits`, the progress plumbing and `__main__`; the model-loading internals at `:342-689`
  and the `/v1/images/inpaint` and `/v1/images/harmonize` bodies at `:974-1460` were not read line by
  line — those two were grepped for authentication, request bounds and generation parameters, which
  is what the findings below depend on
- `scripts/pr_blocker_audit.py`: the `gh` wrapper, the output writer and `main`, plus whole-file
  greps for `shell=True`, `eval`/`exec`, `open(...,"w")`, `rmtree` and `os.remove`; the scoring and
  rendering helpers were not read line by line
- `scripts/import_from_vllm_recipes.py`: `main` and the catalogue write path; the recipe parsers at
  `:84-244` were skimmed
- `scripts/add_hwfit_models.py`: `main` and the entry builder; the parameter-estimation helpers at
  `:121-300` were skimmed
- `scripts/agent_migration_manifest.py`: the collectors, the archive walkers, the CLI and the output
  path; the conversation normalizers at `:191-350` were skimmed

**Not read:** none of the 45 assigned paths was left unread; the five partially-read files are named
above.

**Checks run:** `venv/bin/python -m pytest -q tests/cli tests/test_backup_cli_security.py
tests/test_claim_ownerless_json.py tests/test_diffusion_server_security.py
tests/test_mlx_image_server_security.py tests/test_migrate_faiss_to_chroma.py
tests/test_update_database_script.py tests/test_odysseus_dispatcher.py
tests/test_agent_migration_manifest.py tests/test_calendar_cli_overlap.py
tests/test_searxng_settings_migration.py tests/test_memory_cli_add_nondict.py
tests/test_amd_gpu_check_args.py tests/test_pr_blocker_audit.py tests/test_docs_no_orphan_images.py
tests/test_email_account_default_serialization.py` → **202 passed, 3 warnings in 2.72s**.

The suite reaches these scripts unevenly, which is worth stating before the findings: the twenty
`odysseus-*` CLIs, `scripts/odysseus`, `_lib/cli.py`, `claim_ownerless.py`,
`migrate_faiss_to_chroma.py`, `agent_migration_manifest.py`, `migrate_searxng_settings.py` and both
image servers have dedicated tests. `update_database.py` is covered only by an assertion that it
has one `__main__` guard (`tests/test_update_database_script.py`, eight lines whose only test
reads the script and counts the guard), `check-docker-gpu.sh`
has no test at all (`tests/test_amd_gpu_check_args.py:5` covers `check-docker-amd-gpu.sh`), and
`encode_previews.sh` is covered by two string assertions
(`tests/test_docs_no_orphan_images.py:142-146`). `demo_account.py` is exercised once, through its
`teardown()` (`tests/test_email_account_default_serialization.py:489-522`). No test executes
`hf_download.py` (the only mention is `tests/test_cookbook_helpers.py:264`, which tests the
Cookbook's repo-id validator), `fix_paths.py`, `index_documents.py`, `add_hwfit_models.py`,
`import_from_vllm_recipes.py`, `seed_demo_emails.py` or `manage.sh`.

Probes for the findings below ran from `/tmp/audit_probe/` against throwaway data directories;
nothing in the repository was written.

### [SECURITY] `snapshot` writes the archive world-readable, beside the key it contains

- **Location:** `scripts/odysseus-backup:99`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the archive is created with `with tarfile.open(out_path, "w:gz") as tar:`, so its
  mode is `0666 & ~umask` and nothing in the script changes it. Snapshotting a throwaway data dir
  that holds a `0600` key file under `umask 022` (`/tmp/audit_probe/backup_probe3.py`):

  ```
  live data/.app_key mode: 0o600
  archive mode: 0o644
    in-tar data/.app_key: mode 0o600
    in-tar data/app.db: mode 0o644
  ```

  The archive carries `data/.app_key`, the Fernet key, next to the database it decrypts.
  `src/secret_storage.py:7-9` states what that key is for ("protects against SQLite-file
  exfiltration (stolen backup, leaked container layer, sibling-tenant read)") and
  `src/secret_storage.py:45` locks the live copy to `0o600`; the copy inside the archive is
  protected by nothing but the archive's own mode. `_sqlite_safe_copy` stages each database through
  a temp file, so a database that is `0600` in `data/` also lands in the archive as `0644`.
- **Impact:** anyone who can read `backups/` — another local account, a sync client, a directory
  copied to a NAS — gets the key that decrypts every `enc:` value in the backed-up database. That
  is the "stolen backup" case the encryption exists for, and it is the case the encryption does not
  cover.
- **Fix:** create the archive `0o600` (`fd = os.open(out_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)`
  and pass `fileobj=os.fdopen(fd, "wb")` to `tarfile.open`), or chmod it immediately after opening.

### [SECURITY] `restore` does not restore file modes, so the app key comes back world-readable

- **Location:** `scripts/odysseus-backup:208`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_extract_restore_members` writes every member through `open(target, "wb")`, which
  creates the file `0666 & ~umask` and ignores the mode recorded in the tar. Round-tripping the
  archive from the finding above under `umask 022` (`/tmp/audit_probe/backup_probe3.py`):

  ```
    in-tar data/.app_key: mode 0o600
    restored .app_key: mode 0o644
    restored app.db: mode 0o644
  ```

  `src/secret_storage.py:41-45` chmods the key only when `_load_or_create_key` creates it, so a
  restored key keeps whatever the umask allowed and nothing ever tightens it again.
- **Impact:** after a restore — the documented recovery path — `data/.app_key` is readable by every
  local account while the application assumes `0o600`. The key then becomes the weakest link in the
  threat model the encryption was built for, and the weakened mode survives restarts because the
  file exists.
- **Fix:** apply the recorded mode while extracting (`os.chmod(target, m.mode & 0o777)` after the
  copy), or at minimum chmod the extracted `.app_key` to `0o600` before reporting success.

### [HARDCODE] Nine scripts resolve data paths from the repo root, ignoring `ODYSSEUS_DATA_DIR`

- **Location:** `scripts/odysseus-theme:30`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** each of these builds its own path from `_REPO_ROOT` instead of importing the
  application's constants: `odysseus-theme:30`
  (`_USER_PREFS_PATH = _REPO_ROOT / "data" / "user_prefs.json"`), `odysseus-preset:24` (`_PATH`),
  `odysseus-memory:39` (`_DATA_DIR`), `odysseus-personal:34` (`_DATA_DIR`), `odysseus-research:26`
  (`_DATA_DIR = _REPO_ROOT / "data" / "deep_research"`), `odysseus-skills:33`,
  `odysseus-cookbook:42`, `odysseus-backup:31`, and `scripts/demo_email/seed_demo_emails.py:53`
  (`CACHE_DB = _REPO_ROOT / "data" / "scheduled_emails.db"`). Loading each module with
  `ODYSSEUS_DATA_DIR=/tmp/env_data` set (`/tmp/audit_probe/datadir_probe.py`):

  ```
  ODYSSEUS_DATA_DIR: /tmp/env_data
  app src.constants.DATA_DIR: /tmp/env_data
  odysseus-theme         _USER_PREFS_PATH   /home/lhl/github/lhl/odysseus/data/user_prefs.json
  odysseus-preset        _PATH              /home/lhl/github/lhl/odysseus/data/presets.json
  odysseus-memory        _DATA_DIR          /home/lhl/github/lhl/odysseus/data
  odysseus-personal      _DATA_DIR          /home/lhl/github/lhl/odysseus/data
  odysseus-research      _DATA_DIR          /home/lhl/github/lhl/odysseus/data/deep_research
  odysseus-skills        _DATA_DIR          /home/lhl/github/lhl/odysseus/data
  odysseus-cookbook      _DATA_DIR          /home/lhl/github/lhl/odysseus/data
  odysseus-backup        _DATA_DIR          /home/lhl/github/lhl/odysseus/data
  ```

  `src/constants.py:12` is the definition the application uses
  (`DATA_DIR = os.getenv("ODYSSEUS_DATA_DIR", get_default_data_dir())`) and `src/constants.py:15-17`
  states the rule these scripts break: "every persisted file/dir lives under `DATA_DIR`, which is
  the ONLY place `ODYSSEUS_DATA_DIR` is read. Import these constants instead of re-deriving paths
  from `__file__`". `CONTRIBUTING.md:101` repeats it as a review rule. Three sibling scripts
  already comply: `scripts/claim_ownerless.py:16` (`from src.constants import MEMORY_FILE,
  SKILLS_FILE`), `scripts/index_documents.py:23` (`from src.constants import PERSONAL_DIR`), and
  `scripts/migrate_faiss_to_chroma.py:66` (`from src.constants import MEMORY_VECTORS_DIR,
  MEMORY_FILE`).
- **Impact:** on any deployment that sets `ODYSSEUS_DATA_DIR` (the documented way to move the data
  dir, and what the Docker image does), these CLIs silently operate on a different store than the
  server: `odysseus-memory list` shows a stale `memory.json`, `odysseus-theme set` edits a file the
  server never reads, `odysseus-backup snapshot` archives a tree that may not be the live one, and
  the seeder writes `scheduled_emails.db` next to the code. Every one of them reports success.
- **Fix:** import the named constants from `src.constants` in all nine scripts (adding constants
  where a file has none, as `CONTRIBUTING.md:101` instructs) instead of deriving paths from
  `_REPO_ROOT`.

### [BUG] `odysseus-cookbook` reads `DATA_DIR`, a variable the application never reads

- **Location:** `scripts/odysseus-cookbook:42`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_DATA_DIR = Path(os.environ.get("DATA_DIR", str(_REPO_ROOT / "data")))` — the
  variable is `DATA_DIR`, not `ODYSSEUS_DATA_DIR`. `src/constants.py:12` is the only place the
  application reads the environment for this, and it reads `ODYSSEUS_DATA_DIR`. Both settings
  diverge from the app in opposite directions (`/tmp/audit_probe/datadir_probe2.py`):

  ```
  ### ODYSSEUS_DATA_DIR=/tmp/env_data, DATA_DIR unset ###
  app COOKBOOK_STATE_FILE:  /tmp/env_data/cookbook_state.json
  odysseus-cookbook            /home/lhl/github/lhl/odysseus/data/cookbook_state.json

  ### ODYSSEUS_DATA_DIR unset, DATA_DIR=/tmp/other_var ###
  app COOKBOOK_STATE_FILE:  /home/lhl/github/lhl/odysseus/data/cookbook_state.json
  odysseus-cookbook            /tmp/other_var/cookbook_state.json
  ```

  It is the only CLI in this slice that follows `DATA_DIR`, and it is the only one whose write
  target can be moved by an unrelated environment variable.
- **Impact:** with `ODYSSEUS_DATA_DIR` set, `odysseus-cookbook state-set` writes app state to a
  directory the server never reads; with a stray `DATA_DIR` in the environment (a common name —
  several tools and test harnesses export it), the CLI writes `cookbook_state.json` into whatever
  directory that variable names.
- **Fix:** import the cookbook state constant from `src.constants` (or `DATA_DIR` itself) instead
  of re-deriving the path from `DATA_DIR`/`_REPO_ROOT`.

### [BUG] `odysseus-notes create` writes a note that no account can see

- **Location:** `scripts/odysseus-notes:104`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `cmd_create` builds `Note(...)` with no `owner` argument, so `owner` takes the
  column default. `core/database.py:1813` declares it `owner = Column(String, nullable=True,
  index=True)`, so the note is stored with `owner = NULL`. Creating one and reading the row back
  (`/tmp/audit_probe/notes_probe/app.db`, a throwaway database):

  ```
  ('695dc4d8-...', 'cli probe', None, 'user')   # (id, title, owner, source)
  ```

  The HTTP create path sets it (`routes/note/note_routes.py:665`, `owner=user`), and the list
  endpoint filters on it (`routes/note/note_routes.py:633-634`, `if user is not None: q =
  q.filter(Note.owner == user)`). With auth configured, every user is non-None, so a note created
  by the CLI matches no user's query. `claim_ownerless.py` is the only way to recover it.
- **Impact:** the CLI reports the created note (with its id) as success, and the note then exists
  in the database but in no user's list, search, or export. The operator's natural next step —
  "the note I just created isn't there, so let me create it again" — adds more invisible rows.
- **Fix:** accept an `--owner` argument and set `owner=...` (the other CLIs in this directory
  already take `--owner`); the umbrella `odysseus notes create --owner <name>` is the consistent
  shape.

### [FOOTGUN] `odysseus-skills delete` and `export` build the skill path from the stored category

- **Location:** `scripts/odysseus-skills:102`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `cmd_delete` resolves `path = skills_root / cat / s["name"]` and calls
  `shutil.rmtree(path)` (:102-104) using the category string from the loaded record; `cmd_export`
  does the same at `:116` (`Path(_DATA_DIR) / "skills" / cat / args.name / "SKILL.md"`). The record's
  category is the raw frontmatter value (`services/memory/skill_format.py:451`), while the
  directory on disk is built from a slug (`services/memory/skill_format.py:446`, used by
  `services/memory/skills.py:76-79`). Two probe runs against throwaway data dirs
  (`/tmp/audit_probe/skills_probe/probe.py`, `probe2.py`):

  ```
  ### SKILL.md with `category: ../../outside` ###
  record category as loaded: '../../outside'
  real SKILL.md on disk:       .../data/skills/general/note-taker/SKILL.md True
  {"ok": true, "deleted": "note-taker", "path": ".../data/skills/../../outside/note-taker"}
  outside dir still there: False
  real skill dir still there: True

  ### SKILL.md with `category: DevOps` ###
  record category: 'DevOps' | file really at: .../data/skills/devops/note-taker/SKILL.md
  error: skill record found but directory missing: .../data/skills/DevOps/note-taker
  exit code: 1
  skill dir survived: True
  ```

  The first run deleted `data/outside/note-taker` — outside the skills root — and reported it as a
  successful delete of the skill, which was still on disk. The second shows the benign version of
  the same mismatch. `SKILL.md` files are written by the model during skill capture, so the
  category is not operator-controlled input.
- **Impact:** `delete` can `rmtree` a directory outside `data/skills/` (its path is
  `skills_root / <raw category> / <name>`, with `..` and absolute components honored), and in the
  common case of a category that is not already a slug it deletes nothing while the record stays,
  or reports "directory missing" for a skill that exists.
- **Fix:** resolve the directory the same way the writer does — slugify the category (or take the
  path from the loaded record instead of recomputing it) and assert the resolved path is inside
  `skills_root` before `rmtree`.

### [BUG] `diffusion_server` accepts an unbounded image count and unbounded pixel size

- **Location:** `scripts/diffusion_server.py:707`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `ImageRequest` declares `n: int = 1` and `size: str = "1024x1024"` with no
  bounds (`:188-192`), `_parse_size` splits on `x` and returns `int(w), int(h)` with no clamp
  (`:198-203`), and `generate_image` loops `for image_index in range(req.n):` (`:707`), appending
  every image and then base64-encoding all of them into one JSON body (`_image_response`,
  `:249-255`). The same file caps the same parameter on the edit endpoint — `total_images =
  max(1, min(int(n or 1), 4))` (`:796`) — and `scripts/mlx_image_server.py:338` caps `n` the same
  way, so the missing cap is an oversight rather than a design choice. Nothing in the request path
  authenticates the caller: the middleware is `TrustedHostMiddleware` plus default-deny CORS
  (`:92-114`), a DNS-rebinding defense written for the loopback bind
  (`tests/test_diffusion_server_security.py:1-13`), and the application's own launcher starts the
  server with `--host 0.0.0.0` (`src/tools/cookbook.py:458`). There is no `--max-size`/`--max-n`
  flag either: `--width`/`--height` (`:1479-1480`) are only the fallback used when `size` fails to
  parse.
- **Impact:** one unauthenticated request (`{"n": 100000}`, or `"size": "100000x100000"`)
  occupies the GPU indefinitely and can exhaust RAM in the response body; the server has no queue,
  timeout, or per-request memory bound, so the instance stays unresponsive afterwards.
- **Fix:** clamp in the model (`n: int = Field(1, ge=1, le=4)`) and in `_parse_size` (reject or
  clamp to a maximum edge, e.g. 4096, and to a multiple of 8).

### [BUG] `mlx_image_server` clamps the floor of a requested size but not the ceiling

- **Location:** `scripts/mlx_image_server.py:58`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_size` returns `max(64, int(w)), max(64, int(h))` — a minimum only. Calling it
  directly (`/tmp/audit_probe/mlx_size_probe.py`):

  ```
  _size('1024x1024')      -> (1024, 1024)
  _size('100000x100000')  -> (100000, 100000)
  _size('1x1')            -> (64, 64)
  ```

  The result feeds the generator directly (`:336-346`, `width, height = _size(req.size)` then
  `_generate_hidream(model, req.prompt, out_path, width, height, ...)`), and `n` is capped at 4 on
  the same code path (`:338`), so the size is the only unbounded parameter. Like the diffusion
  server this process has no authentication and is started with `--host 0.0.0.0` by the
  application's launcher (`src/tools/cookbook.py:456`).
- **Impact:** an unauthenticated caller picks the allocation size for the GPU/ANE; a single
  request for an extreme size fails the generation (or thrashes memory) and takes the shared
  image server down for the users the Cookbook started it for.
- **Fix:** add an upper clamp next to the lower one (`min(4096, max(64, int(w)))`) or reject
  out-of-range sizes with a 400.

### [BUG] `claim_ownerless.py` assigns data to any name, including one that is not a user

- **Location:** `scripts/claim_ownerless.py:30`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `owner_arg` returns `argv[1].strip()` if it is non-empty and never checks it
  against the configured users (`core/auth.py:65`, `normalize_known_username`, is the helper that
  does that for the app). Running it with a plausible typo (`/tmp/audit_probe/claim_probe2.sh`):

  ```
  --- run A: writable DB, username that exists nowhere (typo) ---
  Claiming all ownerless data for: adminn
    memory.json: claimed 1 entries
    sessions: claimed 1
  Done! All ownerless data now belongs to adminn
  exit code: 0
  sessions after A: [('s1', 'adminn')]
  memory.json after A: [{'id': 'm1', ..., 'owner': 'adminn'}]
  usernames in data/auth.json: no auth.json
  ```

- **Impact:** the run succeeds, the data is written under a name no account matches, and the
  script cannot be re-run to fix it — the entries are no longer ownerless, so a corrected run
  skips every one of them. Recovery means editing `memory.json`, `skills.json` and the database by
  hand. The script does print the name it is about to use, which is the only warning the operator
  gets.
- **Fix:** load the configured users (`core/auth.py`) and refuse a name that is not among them
  (with `--force` for the deliberate case).

### [ERROR-HANDLING] `claim_ownerless.py` prints "Done!" and exits 0 after a failed write

- **Location:** `scripts/claim_ownerless.py:101`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the database block catches every exception, rolls back and prints it (`:95-97`),
  then falls through to the success message at `:101`. With the database made read-only
  mid-flight (`/tmp/audit_probe/claim_probe2.sh`):

  ```
  --- run B: DB made read-only mid-flight ---
  Claiming all ownerless data for: admin
    memory.json: claimed 0 entries
    skills.json: not found, skipping
    ERROR: (sqlite3.OperationalError) attempt to write a readonly database
  Done! All ownerless data now belongs to admin
  Restart the server: sudo systemctl restart odysseus-ui
  exit code: 0
  sessions after B: [('s1', 'adminn')]
  ```

  Nothing was claimed in the database, and the script still told the operator the migration was
  complete and to restart the server. (The JSON half of the same script writes in place rather
  than atomically — the same non-atomic rewrite pattern reported in `core-data-platform.md:208`.)
- **Impact:** an operator who runs this once, sees "Done!", and restarts has a half-migrated
  instance: the JSON stores are claimed, the database tables are not, and the only trace is an
  `ERROR:` line that scrolls past above the success banner.
- **Fix:** track failures and exit non-zero (`sys.exit(1)`) without printing the completion
  message when the rollback path was taken.

### [ERROR-HANDLING] A failed `restore` leaves `data/` half-extracted and never names the stash

- **Location:** `scripts/odysseus-backup:233`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `cmd_restore` renames the live tree to `data.before-restore-<ts>` (`:229`), then
  extracts member by member; the first failure is caught and reported as
  `fail(f"extract failed: {e}")` (`:233`). Restoring a tarball whose second member cannot be
  written (`/tmp/audit_probe/restore_fail_probe.py`):

  ```
  error: extract failed: [Errno 21] Is a directory: '/tmp/audit_probe/restore_fail/repo/data'
  exit code: 1
  data/ still exists: True
  data/ contents: ['a.txt']
  stash dirs: ['data.before-restore-20261004-200125']
  precious.json in the stash: True
  ```

  The error names the member that failed but not where the previous tree went; the operator is
  left with a `data/` that contains one file from the archive and the real data in a sibling
  directory they have to find. The command is not re-runnable in place either — a second attempt
  would stash the partial `data/` and extract again, so the first failure's leftovers stay on
  disk as an extra `data.before-restore-*` directory.
- **Impact:** the recovery path for a corrupt archive leaves the instance in a state that looks
  like data loss (empty-ish `data/`) until the operator notices the stash directory. Nothing is
  destroyed — the stash holds the real tree — but the message does not say so.
- **Fix:** on the failure path, print the stash path and the partial-extract state, and either
  remove the partial tree or say explicitly that it was kept.

### [BUG] `update_database.py` cannot start: it imports a module that does not exist

- **Location:** `scripts/update_database.py:21`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `from database import DATABASE_URL, SessionLocal, Base` — there is no `database`
  module on `sys.path` (the module is `core/database.py`, and the script does not add the repo
  root to `sys.path` the way its siblings do). Running it:

  ```
  Traceback (most recent call last):
    File ".../scripts/update_database.py", line 21, in <module>
      from database import DATABASE_URL, SessionLocal, Base
  ModuleNotFoundError: No module named 'database'
  exit code: 1
  ```

  The script is not referenced from the docs, the `odysseus` dispatcher, or any test beyond an
  assertion on its `__main__` guard (`tests/test_update_database_script.py`), so nothing fails
  loudly until an operator follows the docstring's "Usage: python update_database.py".
- **Impact:** the documented one-time schema updater has been unusable; an operator who needs it
  gets a traceback with no hint that the module moved.
- **Fix:** `from core.database import ...` (with the repo root inserted on `sys.path` as the other
  scripts do), or delete the script if the migration is no longer part of any upgrade path.

### [BUG] `update_database.add_column_sqlite` rebuilds a table without its keys, constraints, or indexes

- **Location:** `scripts/update_database.py:58`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the rebuild collects `PRAGMA table_info` and re-emits each column as
  `f"{col[1]} {col[2]}"` — name and type only. `col[3]` (NOT NULL), `col[4]` (default) and
  `col[5]` (primary key) are dropped, and the `DROP TABLE`/`RENAME` pair at `:67-68` discards every
  index and constraint attached to the old table. Running the real function against a realistic
  `sessions` table (`/tmp/audit_probe/upd_probe.py`):

  ```
  --- BEFORE ---
  CREATE TABLE sessions (
    id VARCHAR NOT NULL PRIMARY KEY, name VARCHAR NOT NULL, endpoint_url VARCHAR NOT NULL,
    model VARCHAR NOT NULL, owner VARCHAR, created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL)
  CREATE INDEX ix_sessions_owner ON sessions (owner)
  CREATE UNIQUE INDEX ix_sessions_name ON sessions (name)
  --- AFTER add_column_sqlite(..., 'last_accessed', 'DATETIME') ---
  CREATE TABLE "sessions" (id VARCHAR, name VARCHAR, endpoint_url VARCHAR, model VARCHAR,
    owner VARCHAR, created_at DATETIME, updated_at DATETIME, last_accessed DATETIME)
  --- rows survived: [('s1', 'alice', None)]
  ```

  The primary key, all five NOT NULL constraints and both indexes are gone; the rows survive. This
  is latent today because the script cannot run at all (the finding above) and because every
  current install already has the three columns, so `check_column_exists` short-circuits the
  rebuild.
- **Impact:** if the import is fixed — a one-word change — the first run against a database that
  predates one of the columns silently removes that table's primary key, uniqueness constraints
  and indexes. Nothing in the script verifies the rebuilt schema.
- **Fix:** do not rebuild the table. Modern SQLite supports `ALTER TABLE ... ADD COLUMN` with
  `DEFAULT`, which is all three of these migrations need; or copy the full `sql` column from
  `sqlite_master` and the index definitions, and verify the result before committing.

### [BUG] The RAG half of the FAISS→Chroma migration looks in the current working directory

- **Location:** `scripts/migrate_faiss_to_chroma.py:129`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `docs_path = os.path.join("data", "rag", "docs.json")` — a relative path, resolved
  against the CWD — while the memory half of the same script uses the application constants
  (`:66`, `from src.constants import MEMORY_VECTORS_DIR, MEMORY_FILE`). Running `migrate_rag()`
  with the data dir set to a directory that *does* contain `data/rag/docs.json` but from a CWD that
  does not (`/tmp/audit_probe/rag_probe.py`):

  ```
  ### cwd=/tmp/audit_probe, ODYSSEUS_DATA_DIR=/tmp/audit_probe/ragcwd ###
  constants: ... MEMORY_VECTORS_DIR=/tmp/audit_probe/ragcwd/memory_vectors ... RAG_DIR=/tmp/audit_probe/ragcwd/rag
  cwd = /tmp/audit_probe | data/rag/docs.json here: False
  No RAG DocStore found, skipping RAG migration

  ### cwd=/tmp/audit_probe/ragcwd, ODYSSEUS_DATA_DIR=/tmp/audit_probe/ragdata ###
  cwd = /tmp/audit_probe/ragcwd | data/rag/docs.json here: True
  (found the CWD file; proceeds to the embedding client)
  ```

- **Impact:** the migration's RAG half silently reports "No RAG DocStore found, skipping RAG
  migration" unless the operator happens to run it from a directory containing `data/rag/`, and it
  migrates whatever `data/rag/docs.json` is relative to the CWD rather than the live store. The
  migration then reports success for data it never touched.
- **Fix:** `os.path.join(RAG_DIR, "docs.json")` from `src.constants`.

### [ERROR-HANDLING] The FAISS→Chroma migration is not idempotent and reports success when it skips

- **Location:** `scripts/migrate_faiss_to_chroma.py:113`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** both halves call `collection.add(...)` with ids taken from the FAISS store
  (`:113` for memories, `:156` for RAG chunks) and neither checks whether those ids are already in
  the collection. The application code that writes the same collections guards against exactly
  that: `src/memory_vector.py:110-113` does `existing = lane.collection.get(ids=[memory_id])` and
  `continue`s if the id is present before calling `add`. The migration's add loops have no
  `try`/`except`, and `__main__` logs "Migration complete" (`:173`) after both halves regardless of
  whether they ran: each half returns early on a missing store, an empty store, or a missing
  embedding client, and every early return is followed by the same success line.
- **Impact:** a re-run after a partial failure re-sends the ids it already inserted, with no
  guard and no rollback, so the migration is effectively one-shot and the operator cannot tell a
  complete migration from a skipped one in the log output.
- **Fix:** use `upsert` (or the same existence check the app uses), and make the two halves return
  a status that `__main__` uses to decide between "Migration complete" and an error.

### [BUG] `hf_download.py` aborts before it downloads anything

- **Location:** `scripts/hf_download.py:131`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_patch_tqdm` does `import tqdm as tqdm_mod` (`:127`) and then assigns
  `tqdm_mod.auto.tqdm = PipeTqdm` (`:131`), but nothing imports the `tqdm.auto` submodule, and
  `tqdm` does not expose `auto` as an attribute on a bare import. Running the script:

  ```
  File ".../scripts/hf_download.py", line 161, in main
      _patch_tqdm()
  File ".../scripts/hf_download.py", line 131, in _patch_tqdm
      tqdm_mod.auto.tqdm = PipeTqdm
  AttributeError: module 'tqdm' has no attribute 'auto'

  $ venv/bin/python -c "import tqdm; print(hasattr(tqdm, 'auto'))"
  False
  ```

  The crash happens before `snapshot_download` is imported and before the `START` line is printed,
  so every invocation fails the same way regardless of the model or arguments.
- **Fix:** `import tqdm.auto as tqdm_auto` before assigning, or drop the line — the
  `tqdm_mod.tqdm = PipeTqdm` assignment on the line above already covers the plain import path.

### [BUG] `odysseus-logs` hardcodes `/tmp` while the process that writes those logs does not

- **Location:** `scripts/odysseus-logs:33`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `_TMUX_LOGS = Path("/tmp/odysseus-tmux")`, while the writer uses the platform temp
  dir: `routes/shell_routes.py:498`, `TMUX_LOG_DIR = Path(tempfile.gettempdir()) /
  "odysseus-tmux"`. On a host with `TMPDIR` set:

  ```
  $ TMPDIR=/tmp/alt_tmp venv/bin/python -c "import tempfile; print(tempfile.gettempdir())"
  /tmp/alt_tmp
  ```

  `_enumerate()` skips a base directory that does not exist (`if not base.is_dir(): continue`), so
  the mismatch produces no message — the tmux logs simply are not in the listing.
- **Impact:** on an install where the two sides resolve the temp dir differently (a `TMPDIR` set
  in the service environment, or the CLI run outside the container the app runs in), `odysseus
  logs list` silently shows only the application logs, and the operator concludes no tmux log
  exists.
- **Fix:** use `tempfile.gettempdir()` here too (and check both directories, so an existing
  `/tmp/odysseus-tmux` is still found).

### [ERROR-HANDLING] `index_documents.py` exits 0 after indexing nothing

- **Location:** `scripts/index_documents.py:56`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** when the documents directory is missing, the script logs an error and returns:

  ```
  $ ODYSSEUS_DATA_DIR=/tmp/audit_probe/nodocs venv/bin/python scripts/index_documents.py
  <ts> - ERROR - VectorRAG init failed: ChromaDB is not reachable at localhost:8100. ...
  <ts> - ERROR - Directory '/tmp/audit_probe/nodocs/personal_docs' not found!
  <ts> - INFO - Please create the directory and add your documents: mkdir /tmp/audit_probe/nodocs/personal_docs
  $ echo $?
  0
  ```

  (Timestamps elided as `<ts>`; the lines are otherwise verbatim.)

  The same run shows the second silent failure: the vector store is unreachable, which is logged
  as an error and does not stop the script.
- **Impact:** an operator wiring this into a cron job or a deploy step gets a zero exit status for
  a run that indexed nothing, including the case where the vector store was down.
- **Fix:** exit non-zero when the documents directory is missing or when the vector store could
  not be reached.

### [HARDCODE] The demo-email tooling ships a fixed account password in plaintext

- **Location:** `scripts/demo_email/manage.sh:17`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the password is a literal in three places: `manage.sh:17` (`DEMO_PASS="<8 chars>"`,
  written as `printf '%s:{PLAIN}%s\n' "$DEMO_USER" "$DEMO_PASS" >> "$USERS_FILE"` at `:31`),
  `demo_account.py:35` (the same literal, stored encrypted in the `EmailAccount` row via
  `encrypt(...)` at `:137`), and `seed_demo_emails.py:37` (the same literal as the default of
  `DEMO_IMAP_PASSWORD`). Only the seeder honors the environment override: `manage.sh` always
  writes the literal into Dovecot's passdb file, and `demo_account.py` always uses it for the
  account, so setting `DEMO_IMAP_PASSWORD` for a run makes the seeder authenticate with a password
  the Dovecot user does not have.
- **Impact:** the account is created enabled, with `owner = ""` (`demo_account.py:38`, `:128`,
  `:133`) — the shared pool that `routes/email_routes.py:213` defines as `or_(owner == None, owner
  == "")`, and the file's own comment says so (`:36-37`, "Owner empty-string => same list as the
  real Default account (switchable in the ...)") — so it is offered to every user of that
  instance, and `setup()` prints it as "switchable" (`:148`). Its password is a repository
  constant, so anyone who can reach that Dovecot (the account points at `localhost:31143`,
  `:134-135`) can read the demo mailbox. What keeps this low is the rest of the tooling's intent:
  it is documented as a throwaway local demo, the mail it seeds is synthetic (`seed_demo_emails.py:2-11`,
  "fake demo emails" against an account with "NO mbsync channel"), and SMTP is pointed
  at a dead local port (`:141-142`) so an accidental send fails locally.
- **Fix:** generate a random password per install (and write the same value to both places), or
  read it from an environment variable in all three scripts and refuse to run without it.

### [ERROR-HANDLING] `check-docker-gpu.sh` reports the apt repository as added when the download failed

- **Location:** `scripts/check-docker-gpu.sh:543`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the repo step is a pipeline with `||`:

  ```sh
  curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
      | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
      | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list > /dev/null \
      || { _fail "Failed to add NVIDIA apt repository."; exit 1; }
  ```

  Without `set -o pipefail` the exit status of the pipeline is `tee`'s, which succeeds on empty
  input. Reproducing the exact pipeline with a `curl` that fails (`/tmp/audit_probe/shims/curl`,
  exit 7, destination redirected to a temp file):

  ```
  [PASS] apt repository added.
  file written by tee: 0 bytes
  curl exit code was: 7
  ```

  The GPG-key step above it is a pipeline too, but there the guard fires: `gpg --dearmor` is the
  last command and exits 2 on empty input, so the failure surfaces (and leaves a zero-byte keyring
  file behind, which the next `apt-get update` would report as a missing public key):

  ```
  $ printf '' | gpg --batch --yes --dearmor -o /tmp/audit_probe/x.gpg
  gpg: no valid OpenPGP data found.
  gpg on empty input exit=2
  ```

  The repository step has no such backstop: `sed` and `tee` both succeed on empty input.
- **Impact:** a failed download is reported as `[PASS] apt repository added` and setup continues
  with a zero-byte sources file, so whichever of the next two steps fails — `apt-get update` on the
  empty source file (`:552`), or the install on a package that was never added — the log above it
  already says the repository step passed. (Whether `apt-get update` itself errors on a zero-byte
  `.list` file was not run: this host has no `apt`.)
- **Fix:** add `set -o pipefail` (the script sets no shell options at all today; the sibling
  `check-docker-amd-gpu.sh:9` sets `-u`, and `encode_previews.sh:11` and `demo_email/manage.sh:11`
  set `-euo pipefail`), or test the downloaded content before writing it
  (`[ -s /tmp/nvidia.list ]`).

### [BUG] The zsh completion does not register `odysseus-logs`

- **Location:** `scripts/_completion/odysseus.zsh:1`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the `#compdef` line lists 19 of the 20 sub-CLIs — every one except `odysseus-logs`:

  ```
  $ ls scripts/ | grep '^odysseus-' | wc -l          # 20
  $ sed -n 1p scripts/_completion/odysseus.zsh | tr ' ' '\n' | grep '^odysseus-' | wc -l   # 20 (incl. the umbrella name)
  missing from the zsh compdef: logs
  ```

  `zsh` only calls the completion function for the names on that line, so `odysseus-logs <tab>`
  completes nothing, while the docstring at `:8` promises that direct invocation works the same as
  the umbrella form. The umbrella form (`odysseus logs <tab>`) is unaffected, because the
  subcommand table is built by enumerating `odysseus-*` at `:20-41`. The bash completion has no
  such list — it discovers the scripts at `:37` — so only zsh drifts.
- **Impact:** a user who types `odysseus-logs <tab>` (or any future CLI added without editing
  line 1) gets no completion for that command, and the failure is invisible unless they compare
  the two files.
- **Fix:** add `odysseus-logs` to line 1, or register the function against the discovered names
  instead of a hand-maintained list.

### [DEAD-CODE] `fix_paths.py` rewrites a line that no longer exists

- **Location:** `scripts/fix_paths.py:5`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the whole script is a loop over `app.py` that replaces lines starting with
  `BASE_DIR = ` (`:5-6`). `app.py` has no such assignment — it imports the constant
  (`app.py:65-67`, `from core.constants import (BASE_DIR, STATIC_DIR, SESSIONS_FILE, ...)`) and only
  uses it (`:586`, `:894`, `:902`). The script is referenced nowhere in the repository (no docs,
  no dispatcher entry, no test, no CI step). It also rewrites `app.py` in the current working
  directory in place, with no backup.
- **Impact:** none today — running it writes `app.py` back unchanged. It is a trap for the next
  reader (it looks like part of the install flow) and a latent footgun: if `app.py` ever grows a
  `BASE_DIR = ` line, an unversioned one-off script rewrites it in place.
- **Fix:** delete it.

### [DUP] Six CLIs import the output helpers and then redefine them locally

- **Location:** `scripts/odysseus-mail:55`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `odysseus-mail` imports the helpers at `:35`
  (`from cli import quiet_logs, emit, fail, common_parser, run, REPO_ROOT as _REPO_ROOT`) and then
  defines all three again later in the same module (`quiet_logs` at `:55`, `emit` at `:91`,
  `fail` at `:100`), so the import is dead — the later `def` rebinds the name for the whole
  module. The same pattern is in `odysseus-calendar` (`:25` import, `:38`/`:59` locals),
  `odysseus-contacts` (`:24`, `:35`/`:58`), `odysseus-cookbook` (`:26`, `:54`), `odysseus-tasks`
  (`:15`) and `odysseus-notes` (`:17`). Comparing the AST-extracted bodies against
  `scripts/_lib/cli.py`, the copies are behaviorally identical today — the only differences are
  docstrings and code formatting.
- **Impact:** none at runtime. The copies are the ones that run, so a fix to `cli.emit` (for
  example the `default=str` handling of datetimes) does not reach these six commands, and no test
  compares the copies against `cli.py` — the AST comparison above was written for this review.
- **Fix:** delete the local copies and keep the import.

### [BUG] `add_hwfit_models.py` rewrites the shared catalogue with a different indent and without the atomic write its siblings use

- **Location:** `scripts/add_hwfit_models.py:411`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the file it maintains is `services/hwfit/data/hf_models.json` (`:31`) — a tracked
  924-entry, 494 KB catalogue (`git ls-files` confirms it; `.gitignore:30` force-includes it) laid
  out with `indent=1`. (The catalogue itself is generated data that belongs to the hwfit section;
  the defect is in how this writer rewrites it.) `add_hwfit_models.py` dumps with `indent=2`
  (`:406` for the `.bak`, `:411`
  for the catalogue), while both sibling writers use `indent=1, ensure_ascii=False` inside a
  tmp-file-plus-rename (`backfill_model_release_dates.py:120-126`,
  `import_from_vllm_recipes.py:330-334`). Re-serializing the current file with the two settings:

  ```
  size: 494829 bytes | 19477 lines | 924 entries
  json.dumps(indent=1, ensure_ascii=False) differs from the file on 8 lines (4 x \u2014 escaping)
  json.dumps(indent=2) differs from the file on 38951 diff lines
  ```

  `add_hwfit_models.py` is also the only one of the three that writes the catalogue in place
  (`open(DATA_PATH, "w")` at `:410`) rather than through a temp file and `replace`.
- **Impact:** one run rewrites all 19,477 lines, so the actual change (a handful of new models) is
  unreviewable in the diff, and a crash during the write leaves a truncated catalogue with only a
  manual `.bak` to recover from. The `.bak` itself is not gitignored, so it also appears as a new
  untracked 500 KB file.
- **Fix:** match the siblings (`indent=1`, atomic tmp+replace) and add `*.bak` for that path to
  `.gitignore`.

