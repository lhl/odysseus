# core: database, atomic IO, constants, platform

## Overview

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

## Coverage

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

### [SECURITY] `atomic_write_json` leaves the auth and settings stores at the umask default

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

### [PERF] The transcript FTS backfill is quadratic and runs on every startup

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

### [BUG] The hourly null-owner sweep rewrites `memory.json` and `user_prefs.json` non-atomically

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

### [DEAD-CODE] `bulk_insert_messages` cannot insert anything

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

### [ERROR-HANDLING] The three encryption migrations are skipped whenever `src.secret_storage` is imported before `core`

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

### [SECURITY] MCP server env vars are stored plaintext while the same table encrypts OAuth tokens

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
