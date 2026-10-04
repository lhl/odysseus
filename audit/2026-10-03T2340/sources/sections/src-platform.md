# src: config, runtime, health and remaining modules

## Overview

The shared runtime layer: `src/constants.py` owns every data path and the app-wide limits,
`src/runtime_paths.py` resolves source vs. frozen app/data roots, `src/app_initializer.py`
constructs the managers and hardens the agent workspace, `src/app_helpers.py` holds the HTML
nonce injection and the path-confinement check, `src/config.py` is a pydantic settings tree,
`src/event_bus.py` turns app events into scheduled-task triggers, `src/service_health.py` builds
the admin health report, and `src/readiness.py`, `src/user_time.py`, `src/text_helpers.py`,
`src/reminder_personas.py`, `src/optional_deps.py`, `src/database.py` and `src/exceptions.py`
fill in readiness, user-local time, thinking-tag cleanup, reminder personas, optional-dependency
shims, and the `core` re-exports. `src/search/*` are compatibility shims that alias the
`services.search.*` implementations.

The boundary: the manager classes `app_initializer` constructs are defined in `src-memory-rag`,
`src-chat-session` and `src-email-integrations`; the health endpoint that calls
`service_health.collect_service_health` is `routes-rest`; the search implementation behind the
`src/search/*` shims is `services-search`; the schema and the auth/session state are
`core-data-platform` and `core-auth-session`.

## Coverage

**Read fully:** all 22 assigned files (1,982 lines): `src/service_health.py` (506),
`src/user_time.py` (235), `src/config.py` (208), `src/text_helpers.py` (195),
`src/app_initializer.py` (154), `src/constants.py` (133), `src/event_bus.py` (119),
`src/reminder_personas.py` (78), `src/app_helpers.py` (61), `src/readiness.py` (61),
`src/database.py` (37), `src/optional_deps.py` (32), `src/runtime_paths.py` (29),
`src/search/__init__.py` (29), `src/exceptions.py` (22), `src/search/ranking.py` (14),
`src/search/analytics.py` (12), `src/search/core.py` (12), `src/search/providers.py` (12),
`src/search/cache.py` (11), `src/search/content.py` (11), `src/search/query.py` (11).

**Read partially:** `services/search/core.py` at `update_search_config` (`:81-93`);
`services/search/providers.py` at `_get_provider_key` / `_get_search_instance` (`:45-75`);
`src/api_key_manager.py` at `save`/`load` (`:77-105`); `src/upload_handler.py` at the upload cap
and the live extension sets (`:217`, `:375-378`); `src/chat_helpers.py` at the attachment
extension set (`:232-244`); `app.py` at the auth-exempt list and the auth middleware
(`:259-470`), the config import and its use (`:581`, `:721`) and the `/api/ready` route
(`:988-997`); `routes/search/search_routes.py` at `setup_search_routes` (`:39-44`);
`routes/diagnostics_routes.py` at the health route (`:24-30`); `routes/cleanup/cleanup_routes.py`;
`src/cleanup_service.py` at its public functions and its only caller
(`routes/cleanup/cleanup_routes.py:5`); `specs/runtime.md`, `specs/persistence.md`,
`CONTRIBUTING.md` at the data-path rules, `.env.example` and the three `docker-compose*.yml`
files at their cleanup/env blocks.

**Not read:** the manager classes `app_initializer` constructs (assigned to their own sections);
the `services/search` implementation (assigned to `services-search`); the `routes-*` handlers
that consume these helpers beyond the cited regions; the front-end persona definitions beyond
the ID comparison cited in the coverage checks.

**Checks run:** four probes for the config crash (`SECURITY_ALLOWED_ORIGINS=https://example.com`,
`DATA_MAX_UPLOAD_SIZE=abc` and `LLM_REQUEST_TIMEOUT=30s` against `src.config`, and the first
against `import app`), the empty-`ODYSSEUS_DATA_DIR` probe, the unused-config grep
(`config.<field>` and `from src.config import` across the repo), the
`APIKeyManager.save`/`load` caller grep, the `CLEANUP_*` reader grep, and a persona-ID comparison
between `src/reminder_personas.py` and `static/js/presets.js` (identical today). Thirteen suites
were run over this surface — `tests/test_readiness.py`, `tests/test_user_time.py`,
`tests/test_strip_think.py`, `tests/test_strip_reasoning_prose_dataloss.py`,
`tests/test_service_health_collect.py`, `tests/test_service_health_chromadb.py`,
`tests/test_service_health_email.py`, `tests/test_service_health_ntfy.py`,
`tests/test_service_health_providers.py`, `tests/test_service_health_search.py`,
`tests/test_app_initializer_memory_vector_degraded.py`, `tests/test_runtime_paths.py`,
`tests/test_agent_state_dir_confinement.py` — **141 passed**.

### [BUG] `src/config.py` is an unused settings tree that can still stop the server from starting

- **Location:** `src/config.py:20-128`, `:176`, `:208` (with `app.py:581`, `:721`, `routes/search/search_routes.py:39`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the module builds four `BaseSettings` trees and a global `AppConfig()` at import,
  and nothing reads a single field. `grep -rn 'config\.\(data\|llm\|search\|security\|debug\|log_level\)'`
  over `src/ routes/ core/ services/ app.py` returns nothing, and the only import of the module
  in the repository is `app.py:581`:

  ```python
  # ========= IMPORT CONFIG =========
  from src.config import config
  ...
  app.include_router(setup_search_routes(config))     # app.py:721
  ```

  The receiving function never touches its parameter — `grep -n 'config'
  routes/search/search_routes.py` finds only the path string `/api/search/config`, the
  `get_search_config()` call, and docstrings:

  ```python
  def setup_search_routes(config) -> APIRouter:      # routes/search/search_routes.py:39
  ```

  The values that *are* live live elsewhere: the upload cap is
  `get_chat_upload_max_bytes()` (`src/upload_handler.py:217`), the attachment extension set is
  defined in `src/chat_helpers.py:232-234`, and the dangerous-extension set is defined in
  `src/upload_handler.py:375-378` (which excludes `.py`/`.js`/`.sh`, while the dead
  `SecurityConfig.dangerous_extensions` at `src/config.py:112-118` blocks them).

  Because `app.py` imports the module, the parse runs on every startup — and it fails hard on
  plausible values for env vars that do nothing:

  ```
  $ SECURITY_ALLOWED_ORIGINS=https://example.com python -c "import app"
  pydantic_settings.exceptions.SettingsError: error parsing value for field "allowed_origins"
  from source "EnvSettingsSource"

  $ DATA_MAX_UPLOAD_SIZE=abc python -c "import src.config"
  pydantic_core._pydantic_core.ValidationError: 1 validation error for DataConfig
  max_upload_size
    Input should be a valid integer, unable to parse string as an integer

  $ LLM_REQUEST_TIMEOUT=30s python -c "import src.config"
  pydantic_core._pydantic_core.ValidationError: 1 validation error for LLMConfig
  request_timeout
    Input should be a valid integer, unable to parse string as an integer
  ```

  A list-valued field rejects a plain string (the natural way to write a CORS origin), and the
  integer fields reject unit-suffixed values; both abort the import, so the server never starts.
  Values that do parse are silently inert.
- **Impact:** two failure modes from the same dead module. An operator who sets any
  `DATA_*` / `LLM_*` / `SEARCH_*` / `SECURITY_*` variable — names that look like real knobs, and
  `SECURITY_ALLOWED_ORIGINS` in particular reads like the CORS setting — either gets no effect
  (if it parses) or a startup crash with a pydantic traceback (if it does not). The crash is
  caused by configuration the application never consults.
- **Fix:** delete `src/config.py`, the `app.py:581` import, the `app.py:721` argument, and the
  unused `config` parameter of `setup_search_routes`. If the tree is intended to be live, wire it
  to its consumers, document the exact env names, and keep the parsing tolerant of the shapes
  users actually write.

### [BUG] `initialize_managers` logs that it loaded an API key from a store nothing writes and a call that discards it

- **Location:** `src/app_initializer.py:132-136` (with `services/search/core.py:81-93`, `src/api_key_manager.py:77`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the startup path reads the encrypted provider-key store, passes the key to a
  function that documents it ignores the argument, and logs success:

  ```python
  # Load and apply saved API keys
  saved_keys = api_key_manager.load()
  if "brave" in saved_keys:
      update_search_config(api_key=saved_keys["brave"])
      logger.info("Loaded Brave API key from saved configuration")
  ```

  The callee states the opposite:

  ```python
  def update_search_config(api_key: str = None, **kwargs):
      """... Provider API keys are intentionally NOT cached here. They are read on
      demand from settings/env via ``_get_provider_key`` ... ``api_key`` is accepted
      for backward compatibility but no longer stored."""
      for k, v in kwargs.items():
          if not _is_secret_key(k):
              SEARCH_CONFIG[k] = v
  ```

  `APIKeyManager.save` (`src/api_key_manager.py:77`) has no production caller:
  `grep -rn 'api_key_manager\.\(load\|save\)' src/ routes/ core/ services/ app.py` finds only
  `src/app_initializer.py:133`, and the only `APIKeyManager(...)` construction outside tests is
  `src/app_initializer.py:85`. The `save`/`load` round trip is exercised only by
  `tests/test_api_key_manager_atomic_save.py` and its siblings. The live key path is
  `settings.json` plus env vars via `services/search/providers.py:50-75`.
- **Impact:** the log line tells an operator the saved key was applied when the value was
  discarded; the `data/api_keys.json` store is never written, so the load can only ever be
  empty. A reader debugging "why is Brave search unauthenticated" is pointed at a store that is
  not part of the key path, and a future caller may treat `api_key_manager.save` as the way to
  persist provider keys.
- **Fix:** drop the `load()`/`update_search_config(api_key=...)` block (the keys already reach
  search through `_get_provider_key`), and delete `APIKeyManager.save`/`load` and their tests if
  the store is retired.

### [BUG] An empty `ODYSSEUS_DATA_DIR` puts every store next to the working directory

- **Location:** `src/constants.py:12`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the data dir is read with the two-argument `getenv`, which returns the empty
  string when the variable is present but empty:

  ```python
  DATA_DIR = os.getenv("ODYSSEUS_DATA_DIR", get_default_data_dir())
  ```

  Measured:

  ```
  $ ODYSSEUS_DATA_DIR= python -c "from src import constants; ..."
  DATA_DIR: ''
  AUTH_FILE: 'auth.json'
  APP_DB: 'app.db'
  abspath AUTH_FILE: /home/lhl/github/lhl/odysseus/auth.json

  $ env -u ODYSSEUS_DATA_DIR python -c ...
  DATA_DIR: '/home/lhl/github/lhl/odysseus/data'
  ```

  The file already documents this exact trap and fixes it for the neighbouring variable, with a
  comment explaining that `os.getenv(name, default)` only returns the default when the variable
  is absent:

  ```python
  # `or` (not os.getenv's default arg) so a PRESENT-but-EMPTY value falls back to
  # the default. docker-compose.yml injects `FASTEMBED_CACHE_PATH=${FASTEMBED_CACHE_PATH:-}`,
  # which sets the var to "" when the host hasn't defined it. ... the empty string
  # would win → os.makedirs("") raises ...
  FASTEMBED_CACHE_DIR = os.getenv("FASTEMBED_CACHE_PATH") or os.path.join(DATA_DIR, "fastembed_cache")
  ```

  `CONTRIBUTING.md:101` states the intent this breaks: "`DATA_DIR` is the single place that reads
  `ODYSSEUS_DATA_DIR`, so use it directly only for dynamic paths that have no fixed name."
- **Impact:** an operator whose env file expands the variable to nothing (a `${ODYSSEUS_DATA_DIR}`
  reference with no value, a systemd `Environment=ODYSSEUS_DATA_DIR=`, or a Docker `-e` flag with
  no value) gets `DATA_DIR=""`, so `auth.json`, `app.db`, `settings.json` and every cache are
  created relative to the process working directory instead of the data directory. In the
  container that is `/app` — outside the mounted `./data` volume — so the instance comes up as a
  fresh install and the new state is lost when the container is recreated. Nothing warns: the
  paths are valid, just wrong.
- **Fix:** use the same `or` form as `FASTEMBED_CACHE_DIR`:
  `DATA_DIR = os.getenv("ODYSSEUS_DATA_DIR") or get_default_data_dir()`.

### [DOC-DRIFT] `CLEANUP_INTERVAL_HOURS` and `CLEANUP_ENABLED` are documented, injected, and read by nothing

- **Location:** `src/constants.py:106-107` (with `.env.example:185-186`, `docker-compose.yml:56`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** both constants are parsed at import and never read:

  ```python
  CLEANUP_ENABLED = os.getenv("CLEANUP_ENABLED", "True").lower() == "true"
  CLEANUP_INTERVAL_HOURS = int(os.getenv("CLEANUP_INTERVAL_HOURS", "24"))
  ```

  `grep -rn 'CLEANUP_ENABLED\|CLEANUP_INTERVAL_HOURS' --include='*.py'` over the repository
  returns only these two definition lines. The knob is documented and plumbed anyway:
  `.env.example:185-186` ("# Cleanup interval in hours (default: 24)" /
  `# CLEANUP_INTERVAL_HOURS=24`) and all three compose files pass it into the container —
  `docker-compose.yml:56`, `docker-compose.gpu-nvidia.yml:67`, `docker-compose.gpu-amd.yml:68`,
  each as `CLEANUP_INTERVAL_HOURS=${CLEANUP_INTERVAL_HOURS:-24}`. The live session-cleanup entry
  points are the manual routes (`routes/cleanup/cleanup_routes.py:22-23`, `:38-39`), whose only
  service callers are `get_cleanup_preview` and `cleanup_sessions` in `src/cleanup_service.py`
  (`:161`, `:268`); nothing schedules them, and `specs/runtime.md:78`'s list of startup
  fire-and-forget work names
  upload cleanup but not session cleanup.
- **Impact:** an operator who sets `CLEANUP_INTERVAL_HOURS=6` in `.env` gets the default cadence
  they were trying to change, with no warning — the variable survives the whole trip into the
  container and dies at the constant. `CLEANUP_ENABLED=false` is the same: it is not in the
  compose files or `.env.example`, so it is only discoverable by reading this file, and it does
  nothing.
- **Fix:** either wire the constants into a cleanup loop, or delete them and the compose/.env
  lines. Leaving a documented env var that no code reads is the part that misleads.
