# Build, install, launcher, CI and containers

## Overview

The packaging and deployment surface:

- the `Dockerfile` and its two build stages
- the entrypoint that drops privileges
- the three standalone Compose files (`docker-compose.yml` plus the GPU mirrors
  `docker-compose.gpu-amd.yml` and `docker-compose.gpu-nvidia.yml`)
- the host-docker compose file and the two overlays under `docker/` (`host-docker.yml`,
  `gpu.amd.yml`, `gpu.nvidia.yml`)
- the SearXNG settings template the compose file mounts
- the dependency declarations (`requirements.txt`, `requirements-optional.txt`, `pyproject.toml`,
  `package.json`/`package-lock.json`)
- the first-run installer (`setup.py`) and its `.env` template
- the native launchers:
  - `start-macos.sh`
  - `build-macos-app.sh`
  - `launch-windows.ps1`
  - `build-windows-portable.ps1`
  - `update_windows.bat`
  - `launcher.py`
  - `Odysseus.spec`
- the systemd unit and its installer
- the CI and security workflows under `.github/`
- the issue/PR templates and the three check scripts they drive
- the ignore files
- `app.py` as the process entry point every launcher starts
- the six vendored licence texts

The boundary: this section owns what an operator receives and what a container, a CI job or a
launcher is allowed to do with it — the dependency declarations, the build inputs, the permissions of
the files first-run setup writes, and the workflows' triggers and tokens. It does not own the
application code those entry points start.

Where a finding here rests on code another section owns,
the owning section is named and its finding is cross-referenced rather than restated: the runtime
state paths come from `src/constants.py` (`core-data-platform`), the `atomic_write_json` mode
behaviour from `core-data-platform.md`, "[SECURITY] `atomic_write_json` leaves the auth and settings
stores at the umask default", the `yt-dlp` dependency from `services-media.md`, "[DEPENDENCY] The
comment fetch shells out to `yt-dlp`, which no requirement file or image installs", and the missing
SSRF switches in this same `.env.example` from `src-security.md`, "[UNDOCUMENTED] Five environment
variables gate one SSRF policy and none appears in `.env.example`". Findings in other sections are
cited by title rather than line number because those files are still being written.

`app.py` is
assigned here and read in full, but its route wiring, auth middleware and lifespan work are the
subject of the `core-*`, `routes-*` and `src-*` sections; only the parts a deployment depends on (the
`.env` load, the bind address, the static mount, the CORS origins) are treated here.

## Coverage

Line numbers refer to the working tree, which is `4ceb65d4` ("in-progress code-audit") on top of
`2992bf6d`. No source file changed between the two: `git diff --name-only 2992bf6d..4ceb65d4 | grep -v
'^audit/'` is empty, so every line number below is identical at both commits.
`git status --porcelain | grep -v '^.. audit/'` is also empty, i.e. the only uncommitted changes are
under `audit/`.

**Read fully:** all 57 text files in the assigned list (6,567 lines).

| File | Lines |
| --- | ---: |
| `app.py` | 1306 |
| `setup.py` | 304 |
| `start-macos.sh` | 270 |
| `.env.example` | 268 |
| `.github/scripts/check-pr-description.js` | 240 |
| `.github/scripts/check-issue-description.js` | 211 |
| `licenses/DeepResearch-Apache-2.0.txt` | 201 |
| `docker-compose.gpu-nvidia.yml` | 200 |
| `docker-compose.gpu-amd.yml` | 197 |
| `docker-compose.yml` | 178 |
| `build-macos-app.sh` | 177 |
| `launch-windows.ps1` | 173 |
| `docker/entrypoint.sh` | 155 |
| `.github/workflows/docker-publish.yml` | 153 |
| `.gitignore` | 122 |
| `Dockerfile` | 113 |
| `.dockerignore` | 54 |
| `requirements-optional.txt` | 46 |

Also read fully:

- all eleven workflow files (921 lines together)
- the three compose files under `docker/` (plus `docker/entrypoint.sh` and
  `docker/build-realesrgan-wheels.sh`)
- `config/searxng/settings.yml`
- `Odysseus.spec`
- `package.json`
- `package-lock.json`
- the three `.github/scripts/` files
- the three issue templates
- both PR templates
- `.gitattributes`
- `.github/CODEOWNERS`
- `.github/dependabot.yml`
- `pyproject.toml`
- `requirements.txt`
- `install-service.sh`
- `odysseus-ui.service`
- `update_windows.bat`
- `build-windows-portable.ps1`
- `launcher.py`
- the five remaining licence texts:
  - `licenses/KaTeX-MIT-LICENSE.txt`
  - `Mermaid-MIT-LICENSE.txt`
  - `OpenDyslexic-OFL.txt`
  - `llmfit-MIT-LICENSE.txt`
  - `opencode-MIT-LICENSE.txt`

**Read partially:** nothing in the assigned list. Outside it, the code the findings rest on:

- `services/search/content.py` at the PDF branch (`:62-66`, `:253-291`)
- `src/constants.py` at the `DATA_DIR` tree and `PASSWORD_MIN_LENGTH` (`:12-63`, `:110`)
- `core/atomic_io.py` in full (66 lines)
- `core/auth.py` at the load and save paths (`:117`, `:152-157`, `:221-222`)
- `routes/vault/vault_routes.py` at `_find_bw` and the missing-binary message (`:27-60`, `:102`)
- `routes/cookbook_helpers.py:109`
- `src/builtin_mcp.py` at the browser-executable and `npx` lookup (`:36-129`)
- `tests/TESTING_STANDARD.md` and `tests/README.md` at the venv rule
- `specs/testing-devops.md` in full (it is the spec for this surface)
- for the cross-references above, `services-media.md`, `core-data-platform.md`, `src-platform.md`
  and `src-security.md`

**Not read:**

- the three branding images under `assets/branding/` are binary; they were identified with `file(1)`
  and their three references (`README.md:2`, `README.md:21`, `build-macos-app.sh:31`) were checked,
  and nothing else about them is claimed
- the six licence texts were read as headers plus a scan of the body; no attempt was made to verify
  them against upstream
- `package-lock.json` is a two-package lockfile and was read as JSON, not line by line
- nothing was built: no `docker build`, no `pip install`, no PyInstaller run and no macOS/Windows
  launcher execution, so every claim about what the image contains is derived from the Dockerfile
  and the requirement files, not from an image

**Checks run:** the two suites named in the brief, then the wider set that touches this surface:

```
$ venv/bin/python -m pytest -q tests/test_docker_devops_hardening.py tests/test_ci_authoritative_validation.py
14 passed, 1 skipped, 1 warning

$ venv/bin/python -m pytest -q tests/test_docker_devops_hardening.py tests/test_ci_authoritative_validation.py \
    tests/test_gpu_compose_standalone.py tests/test_searxng_image_pinned.py \
    tests/test_searxng_settings_migration.py tests/test_launcher.py \
    tests/test_kokoro_optional_requirements.py tests/test_setup_admin_user.py \
    tests/test_email_oauth_docker_config.py tests/test_pr_description_check.py \
    tests/test_builtin_mcp_npx_cache.py tests/test_fastembed_cache_path.py \
    tests/test_mcp_dependency_compatibility.py
106 passed, 1 skipped, 1 warning

$ venv/bin/python -m pytest -q tests/test_app.py tests/test_pdf_runtime.py \
    tests/test_markitdown_runtime.py tests/test_web_fetch_plaintext.py \
    tests/test_search_content_block_source_index.py
28 passed, 1 skipped, 1 warning
```

(Timings omitted; the counts are what is stable across runs.)

The one skip in each run is `tests/test_docker_devops_hardening.py:149`, which needs a built image:
`SKIPPED [1] tests/test_docker_devops_hardening.py:149: Docker test image is unavailable:
odysseus-odysseus:latest`. The Docker CLI is present (`docker version` → server 29.8.0) but the image
is not, so the real-entrypoint ownership probe did not run here.

Beyond the suites: `git check-ignore -q` over the runtime-state and secret paths; a `.env` parser
probe that replays `start-macos.sh:23-29` against a synthetic fixture and compares the result with
`python-dotenv`; a mode probe that replays `setup.py`'s two writes under `umask 022`; an AST walk
over `core/`, `routes/`, `src/`, `services/`, `mcp_servers/`, `integrations/`, `companion/`,
`scripts/` and `app.py` collecting module-level third-party imports (22 distinct modules; guarded
imports inside `try` blocks are not in that set, so `pdfminer` was checked with a repository-wide
`grep` instead) for comparison against both requirement files; `pip`-level checks that the imports
resolve in the project venv; a PyPI metadata query for the binary dependencies the Dockerfile
installs on Python 3.14; and `docker pull python:3.14-slim` followed by
`apt-get install -s --no-install-recommends` for the Dockerfile's exact apt list, to check that every
package name resolves on the base image's Debian release. Those last two came back clean and are
recorded as rejected hypotheses in the report, not as
findings.

### [DEPENDENCY] `pdfminer.six` is imported at module level but declared in no requirement file, so every fetched PDF yields no text

- **Location:** `services/search/content.py:64` (with `:265-267`; declaration belongs in `requirements-optional.txt:46`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the import is guarded but module-level, so the guard is what decides whether the
  feature exists at all:

  ```python
  # PDF extraction (optional dependency)
  try:
      from pdfminer.high_level import extract_text as pdf_extract_text
  except ImportError:
      pdf_extract_text = None  # type: ignore
  ```

  Nothing installs it. `pdfminer` occurs in exactly two places in the repository, both in this file
  (`:64`, and the error string at `:266`), and the specification treats the absence as normal —
  `specs/search.md:127`: "PDF extraction uses `pdfminer.six` only when installed." It is in neither
  requirement file, and it is not present in this checkout's venv, which was built from
  `requirements.txt`:

  ```
  $ grep -rn "pdfminer" requirements.txt requirements-optional.txt
  (no output)
  $ venv/bin/python -c "import pdfminer"
  ModuleNotFoundError: No module named 'pdfminer'
  $ venv/bin/python -c "import importlib.metadata as m; m.version('pdfminer.six')"
  PackageNotFoundError: No package metadata was found for pdfminer.six
  ```

  The image does not add it either. `Dockerfile:76-79` installs `requirements-optional.txt` only when
  `INSTALL_OPTIONAL=true`, and that file's one Office/PDF extra deliberately excludes the markitdown
  extras that would have supplied it — `markitdown[docx,pptx,xlsx,xls]==0.1.6`
  (`requirements-optional.txt:46`), whose comment says "We avoid the [all]/Azure/audio extras".
  Queried from PyPI, the extras that pull `pdfminer-six` are `pdf` and `all`, and the pinned extras
  list selects neither:

  ```
  $ curl -s https://pypi.org/pypi/markitdown/0.1.6/json   # requires_dist, filtered to the extras
  pdfminer-six>=20251230; extra == "all"
  pdfminer-six>=20251230; extra == "pdf"
  pdfplumber>=0.11.9; extra == "pdf"
  mammoth~=1.11.0; extra == "docx"
  ```

  (Four of the lines that query prints, chosen to show the two extras that carry `pdfminer-six`.)

  So on the shipped image and on any host that installed `requirements.txt`, `pdf_extract_text` is
  `None`, and the PDF branch reports a failure the caller cannot distinguish from a bad PDF:

  ```python
  if pdf_extract_text is None:
      logger.error("pdfminer.six is not installed; cannot extract PDF text.")
      pdf_text = ""
  ...
  "success": bool(pdf_text),
  "error": "" if pdf_text else "Failed to extract PDF text",     # :286-287
  ```

  No test covers the path: `grep -rn "pdfminer\|pdf_extract_text" tests/` returns nothing, so the
  degradation is not even pinned as intended behaviour.
- **Impact:** any URL that returns `application/pdf` — the ordinary case for a research source or a
  linked paper — contributes an empty page to the model's context. The result is cached by
  `_cache_result` (`:290`) with `success: false`, so retrying the same URL re-serves the empty page
  from disk. The operator sees one `ERROR` log line per first fetch and nothing in the UI. The
  declared core already ships a PDF text extractor (`pypdf`, `requirements.txt:10`, used for uploads
  at `src/document_processor.py:115`) so the same file type works through one path and silently
  fails through the other.
- **Fix:** add `pdfminer.six` to `requirements-optional.txt` next to the markitdown block with a
  one-line note that it is the web-fetch PDF extractor, or move the import behind
  `src/markitdown_runtime.py`-style lazy loading and report the missing extra the way
  `src/pdf_forms.py:29-32` reports missing PyMuPDF. A test that asserts the missing-extra message
  would stop the next silent removal.

### [FOOTGUN] `start-macos.sh` parses `.env` itself, so quoted values keep their quotes and any `#` truncates the value

- **Location:** `start-macos.sh:23-29` (with `:36`, `:168`, `:270`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the script loads `.env` with a hand-rolled loop and then exports every key into the
  environment of `setup.py` and `uvicorn`:

  ```bash
  while IFS='=' read -r key value; do
      [[ "$key" =~ ^[[:space:]]*# ]] && continue
      [[ -z "${key// }" ]] && continue
      value="${value%%#*}"                                        # :26
      value="${value#"${value%%[![:space:]]*}"}"
      value="${value%"${value##*[![:space:]]}"}"
      [ -n "$key" ] && [ -z "${!key+x}" ] && export "$key=$value"  # :29
  done < .env
  ```

  Replaying those five lines against synthetic fixtures and comparing with `python-dotenv`, which is
  what `app.py:48` and `setup.py:250` use:

  ```
  $ /tmp/envprobe.sh /tmp/fixture.env   # the loader above, verbatim
  fixture line: ODYSSEUS_ADMIN_PASSWORD=Correct#Horse#Battery9
  shell parse:   |Correct|                 len=7
  python-dotenv: |Correct#Horse#Battery9|  len=22

  fixture line: ODYSSEUS_ADMIN_PASSWORD=HorseBattery#9
  shell parse:   |HorseBattery|            len=12
  python-dotenv: |HorseBattery#9|          len=14

  fixture line: ODYSSEUS_ADMIN_PASSWORD="quoted-secret"
  shell parse:   |"quoted-secret"|         len=15
  python-dotenv: |quoted-secret|           len=13
  ```

  (Every value above is a synthetic placeholder written for this probe.) The loop neither strips
  quotes nor understands `#` inside a value, and it exports the result — so the shell value shadows
  the file for every child process, because `load_dotenv` does not override an already-set variable.
  `ODYSSEUS_ADMIN_PASSWORD` is read by `setup.py:103`, validated at `:106-113`, and reported at
  `:291-298`.
- **Impact:** on the macOS quick-start path only, and it reaches every key in `.env`, not just the
  password. Two outcomes, both bad. When the part before the first `#` is a valid password
  (`HorseBattery#9` above), the admin account is created with the prefix and setup prints its normal
  success lines — `[ok] Initial admin user created (admin)` (`setup.py:137`) and `Login with your
  admin credentials.` (`:292`): the operator is locked out of the instance they just installed and
  has to delete `data/auth.json` and re-run. When the prefix is shorter than `PASSWORD_MIN_LENGTH`
  (`src/constants.py:110`), the run fails with `[error] ODYSSEUS_ADMIN_PASSWORD must be at least 8
  characters` (`setup.py:111`) followed by `Admin creation did not happen: a system or file error
  occurred. / Check write permissions for the 'data' directory and rerun setup.` (`setup.py:297-298`)
  — a message that sends the operator to the data directory instead of the launcher that truncated
  the value. The quoted-value case is quieter still: the server runs with a password containing
  literal quote characters, which is not the password the operator wrote, and the same `.env` would
  work under Docker, Windows or `uvicorn app:app` directly because those paths use `python-dotenv`.
- **Fix:** replace the loop with `set -a; . ./.env; set +a`, or read the values through
  `./venv/bin/python -c "from dotenv import dotenv_values; ..."` so the launcher and the app agree on
  the format. If the loop stays, strip surrounding quotes and stop treating `#` as a comment marker
  inside a value.

### [SECURITY] The systemd unit binds the agent server to every interface and applies no sandboxing

- **Location:** `odysseus-ui.service:12` (whole file, 18 lines; installed by `install-service.sh:16`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the unit is 18 lines and its only hardening-relevant directives are `User` and
  `Restart`:

  ```
  [Service]
  Type=simple
  # CHANGE THESE to match your user and install path:
  User=YOURUSER
  WorkingDirectory=/home/YOURUSER/odysseus-ui
  ExecStart=/home/YOURUSER/odysseus-ui/venv/bin/uvicorn app:app --port 7000 --host 0.0.0.0
  Restart=always
  RestartSec=3
  EnvironmentFile=-/home/YOURUSER/odysseus-ui/.env
  ```

  ```
  $ grep -rn "ProtectSystem\|NoNewPrivileges\|PrivateTmp\|ReadWritePaths" --include="*" . | grep -v venv/ | grep -v audit/
  (no output)
  ```

  Nothing in the repository pins the unit's behaviour either: `grep -rln "odysseus-ui.service" tests/
  website/ scripts/` returns nothing, and the only reference outside the file itself is
  `specs/testing-devops.md:20`, which lists it as part of this surface. The bind address contradicts
  every other launcher in the same directory: `app.py:1303` (`APP_BIND`, default `127.0.0.1`),
  `start-macos.sh:36` (`127.0.0.1`), `launch-windows.ps1:18` (`127.0.0.1`), the Compose port map
  (`${APP_BIND:-127.0.0.1}`, guarded by `tests/test_security_regressions.py:119-122`) and
  `.env.example:73-75`, which says to keep the bind on loopback unless LAN access is intended.
- **Impact:** an operator who follows `install-service.sh` gets a network-reachable agent on a host
  with no service-level confinement, while the same operator following the README's Docker or native
  path gets a loopback bind. The app is designed to run shell commands, spawn MCP servers and write
  files (`routes/shell_routes.py`, `src/builtin_mcp.py`), so the process boundary is the only thing
  limiting what a compromised or misbehaving tool call can reach; `NoNewPrivileges` in particular
  costs nothing here and blocks setuid escalation from a spawned command. Authentication is on by
  default, so this is exposure of a login page and an API surface, not of an unauthenticated app.
- **Fix:** add `NoNewPrivileges=true`, `ProtectSystem=full` and `PrivateTmp=true` to `[Service]`, and
  change `ExecStart` to `--host 127.0.0.1` with a comment pointing at `APP_BIND=0.0.0.0` for
  operators who want LAN access. `ProtectHome` and a read-only `ProtectSystem=strict` are not
  options: the Cookbook runners put `$HOME/.local/bin` on PATH and pip-install there
  (`routes/cookbook_routes.py:2341-2344`), and the HuggingFace cache defaults to
  `~/.cache/huggingface` (`routes/cookbook_output.py:21`).

### [SECURITY] A plaintext file named `secrets.env` is excluded from the image but not from git

- **Location:** `.gitignore:20-25` (with `.dockerignore:13-22`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** both ignore files carry a block describing a SOPS workflow, and they disagree about
  the bare name. `.dockerignore` protects it:

  ```
  # Secrets: keep plaintext and every transient secrets.env variant out of
  # the build context. If an encrypted secrets.env is used, it is mounted
  # at runtime — never baked into the image. Mirrored in .gitignore.
  secrets.env
  secrets.env.*
  ...
  !secrets.env.example
  ```

  `.gitignore` does not — its patterns are `secrets.env.*` and `!secrets.env.example`, so the bare
  name falls through:

  ```
  $ git check-ignore -q secrets.env;            echo $?
  1
  $ git check-ignore -q secrets.env.bak;        echo $?
  0
  $ git check-ignore -q .env;                   echo $?
  0
  ```

  The `.dockerignore` comment calls itself "Mirrored in .gitignore", and `.gitignore:20-22` says
  "every variant (plaintext, manual decrypt copy, editor backup) must stay out of git" — but the one
  variant both comments call plaintext is the one git will accept. Nothing else in the repository
  defines the convention: `grep -rn "secrets.env" --include="*.md" --include="*.sh" --include="*.yml"`
  finds no mention in any Markdown, shell or YAML file, `git ls-files | grep -i secrets` is empty,
  there is no `.sops.yaml`, and the file both negations un-ignore (`!secrets.env.example`) does not
  exist.
- **Impact:** the block reads as protection that is only half-wired. A contributor or operator who
  follows the naming the comments imply — a plaintext secrets file at the repository root named
  `secrets.env` — gets a `git add -A` that stages it. The secret scan is the only thing left in the
  way, and it runs on pull requests and pushes to `main`, so a secret committed on a branch and
  pushed without a PR is not covered. The failure mode requires a user to adopt a workflow the
  repository never documents, which is why this is low rather than higher.
- **Fix:** pick one convention and state it in the same place both files point at. Either ship a
  `secrets.env.example` and document the SOPS flow (encrypted `secrets.env.enc` committable,
  plaintext `secrets.env` never committed), which means adding `secrets.env` to `.gitignore` beside
  `secrets.env.*` and keeping `.dockerignore` as it is, or delete the block from both files until the
  workflow exists.

### [FOOTGUN] First-run setup writes the password database and the `.env` file world-readable

- **Location:** `setup.py:131-132` (with `:166`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `create_default_admin` writes `data/auth.json` with a plain `open()` and no mode:

  ```python
  with open(auth_path, "w", encoding="utf-8") as f:      # :131
      json.dump(auth_data, f, indent=2)                  # :132
  ```

  and `create_env` copies the template with `shutil.copy2`, which preserves the source's mode:

  ```python
  shutil.copy2(example_path, env_path)                   # :166
  ```

  Replaying both writes under `umask 022` in a scratch directory:

  ```
  $ (umask 022; python3 /tmp/modeprobe.py)   # setup.py:131-132 and :166, replayed verbatim
  0o644 data/auth.json
  0o644 .env
  ```

  and in this working tree, where setup has been run, `stat -c '%a %n'` gives `644 .env` and
  `644 data/auth.json`, while the database beside them is `600 data/app.db` — the mode
  `core/database.py:2068-2073` sets explicitly for the same reason (it holds bcrypt hashes and
  encrypted provider keys). `.env.example` is committed `100644`, so the copy inherits
  0644 on every install. This is the same class the `core-data-platform` section already reports for
  `core/atomic_io.py` (`atomic_write_json` leaves a pre-existing 0o600 file at 0o644 after a write);
  the difference here is the writer: `setup.py` bypasses the helper entirely, so its write is also
  the non-atomic `open("w") + json.dump` the helper's docstring says it exists to replace — a kill
  during first-run setup leaves a truncated `auth.json`.
- **Impact:** on a shared host, any local user can read the bcrypt hashes in `data/auth.json` and
  crack them offline, and can read every provider credential the operator later adds to `.env`.
  Inside Docker the same two files land 0644 on the bind-mounted host directory
  (`${APP_DATA_DIR:-./data}:/app/data:z`, `docker-compose.yml:16`; the two GPU mirrors mount the same
  path), so the mode travels out of the container. The truncation risk is
  narrow: `setup.py` runs once, and `|| true` in `docker/entrypoint.sh:150` means a failed setup does
  not stop the container — but a truncated `auth.json` fails `json.load`, so `AuthManager._load`
  logs `Failed to load auth config: ...` and starts from an empty config
  (`core/auth.py:132-134`): an instance with no users.
- **Fix:** `os.chmod(auth_path, 0o600)` after the write (or `os.open(..., 0o600)` before it), and
  `os.chmod(env_path, 0o600)` after the `copy2`; both go through
  `core.platform_compat.safe_chmod` for the Windows no-op. Route the `auth.json` write through
  `core.atomic_io.atomic_write_json` so it gets the same truncation protection as the later saves.

### [PERF] `start-macos.sh` force-reinstalls `chromadb` on every launch, because its guard can never be false

- **Location:** `start-macos.sh:158-162` (with `:143-152`, `requirements.txt:19`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the block is meant to clean up a package that an older requirement file used to
  install:

  ```bash
  # chromadb-client (HTTP-only) conflicts with the full chromadb package. If
  # it got installed (e.g., from an older requirements-optional.txt), remove
  # it to prevent ChromaDB from silently failing in HTTP-only mode.
  if "$VENV_PY" -m pip show chromadb-client >/dev/null 2>&1; then
      echo "▶ Cleaning up conflicting chromadb-client package…"
      "$VENV_PY" -m pip uninstall -y chromadb-client
      "$VENV_PY" -m pip install --force-reinstall chromadb
  fi
  ```

  `chromadb-client` is a core requirement now (`requirements.txt:19`), and
  `requirements-optional.txt:4` records the move: "chromadb-client + fastembed moved to
  requirements.txt". The step immediately above (`:143-152`) installs `requirements.txt` whenever its
  md5 changes, so on a fresh macOS install the guard is true before the block is reached. Measured in
  this checkout, whose venv was built from `requirements.txt`:

  ```
  $ venv/bin/python -c "import importlib.metadata as m; print(m.version('chromadb-client'))"
  1.5.9
  $ venv/bin/python -c "import importlib.metadata as m; m.version('chromadb')"
  PackageNotFoundError: No package metadata was found for chromadb
  $ ls venv/bin/chroma
  ls: cannot access 'venv/bin/chroma': No such file or directory
  ```

  The install is unconditional: `pip show chromadb-client` stays true after the full `chromadb`
  package is installed alongside it, and nothing records that the swap already happened, so the next
  `./start-macos.sh` repeats it. `--force-reinstall` applies to the whole resolution, not just the
  named package.
- **Impact:** every macOS launch after the first pays a full reinstall of `chromadb` and its
  dependency tree (onnxruntime, tokenizers, numpy and the rest) instead of the hash-gated fast path
  the step above deliberately added. `--force-reinstall` also re-resolves unpinned dependencies, so a
  launch can silently move a shared dependency away from the version `requirements.txt` resolved to.
  The block does serve a purpose — `start-macos.sh:213` starts `$VENV_PY`'s sibling `chroma` CLI for
  the local vector store, and only the full package provides it — so the fix is to make the guard
  match the intent, not to delete the block.
- **Fix:** gate on the package the script actually needs — `if ! "$VENV_PY" -m pip show chromadb
  >/dev/null 2>&1; then` — and drop `--force-reinstall` in favour of a plain install.

### [UNDOCUMENTED] `.env.example` omits two variables the code reads and the compose files forward

- **Location:** `.env.example:23` (the API-key block; missing `HF_TOKEN`/`HUGGING_FACE_HUB_TOKEN` and `ODYSSEUS_ADMIN_USER`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the file is 268 lines and documents 52 variables; an extraction of every
  `os.environ.get`/`os.getenv` name in `core/`, `routes/`, `src/`, `services/`, `scripts/`,
  `mcp_servers/`, `integrations/`, `app.py`, `launcher.py` and `setup.py` (129 names) minus the
  documented set leaves 98 names, most of them internal (`PATH`, `APPDATA`, `TMPDIR`) or
  feature-internal. Three of the remainder are operator-facing credentials or identities that all
  three compose files already forward into the container:

  ```
  $ grep -n "HF_TOKEN\|HUGGING_FACE_HUB_TOKEN\|ODYSSEUS_ADMIN_USER" docker-compose.yml
  38:      - HF_TOKEN=${HF_TOKEN:-}
  39:      - HUGGING_FACE_HUB_TOKEN=${HUGGING_FACE_HUB_TOKEN:-}
  47:      - ODYSSEUS_ADMIN_USER=${ODYSSEUS_ADMIN_USER:-admin}

  $ grep -c "HF_TOKEN" .env.example
  0
  ```

  The code reads them: `routes/cookbook_helpers.py:109`
  (`token = (os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN") or "").strip()`),
  `scripts/diffusion_server.py:359` (whose `:370` logs `No HF_TOKEN set — gated models will fail`),
  `scripts/backfill_model_release_dates.py:89`, `scripts/import_from_vllm_recipes.py:283`, and
  `setup.py:102` for the username. `.env.example:99-101` documents the password half of the same
  pair ("Optional: pre-seed the first admin password during setup") without the username, and
  `routes/cookbook_routes.py:66-67` carries a dedicated `_HF_TOKEN_STATUS_SNIPPET` that reports
  whether the token is present, so the project treats it as a real setting. The SSRF switches
  reported as missing from this same file by `src-security.md` ("[UNDOCUMENTED] Five environment
  variables gate one SSRF policy and none appears in `.env.example`") are a separate defect and are
  not restated here.
- **Impact:** an operator who configures a deployment from `.env.example` — the file the project
  presents as the configuration surface — cannot discover that a HuggingFace token is a supported
  setting, and cannot pre-seed the admin *username* the compose files already pass through. Both
  omissions produce a working install with a degraded feature (gated model downloads fall back to
  anonymous, which fails) rather than an error, so the gap is only visible in a log line.
- **Fix:** add `# HF_TOKEN=` (and the `HUGGING_FACE_HUB_TOKEN` alias) to the LLM/search block with a
  one-line note about gated repositories, and extend the admin-seeding comment at `:99-101` to name
  `ODYSSEUS_ADMIN_USER` and its `admin` default.

### [DOC-DRIFT] `RESEARCH_LLM_ENDPOINT` is documented and injected into the container, and no code reads it

- **Location:** `.env.example:28` (with `docker-compose.yml:37`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the variable appears in exactly five places in the repository, none of them a reader:

  ```
  $ grep -rn "RESEARCH_LLM_ENDPOINT" . | grep -v venv/ | grep -v audit/
  ./docker-compose.gpu-amd.yml:49:      - RESEARCH_LLM_ENDPOINT=${RESEARCH_LLM_ENDPOINT:-}
  ./docker-compose.gpu-nvidia.yml:48:      - RESEARCH_LLM_ENDPOINT=${RESEARCH_LLM_ENDPOINT:-}
  ./docker-compose.yml:37:      - RESEARCH_LLM_ENDPOINT=${RESEARCH_LLM_ENDPOINT:-}
  ./.env:28:# RESEARCH_LLM_ENDPOINT=http://localhost:8000/v1/chat/completions
  ./.env.example:28:# RESEARCH_LLM_ENDPOINT=http://localhost:8000/v1/chat/completions
  ```

  (`./.env` is this checkout's local file, copied from the template by `setup.py:166` and untracked;
  `./.env.example:28` is the tracked line. The other three are the compose files.) A search of
  `core/`, `routes/`, `src/`, `services/`, `app.py` and `setup.py` for `research_llm`,
  `research_endpoint` or `RESEARCH_` returns only `DEEP_RESEARCH_DIR` and unrelated identifiers. This
  is the same class as the `CLEANUP_INTERVAL_HOURS`/`CLEANUP_ENABLED` pair already reported in
  `src-platform.md` — a knob that survives the whole trip from `.env` into the container and dies at
  the far end — but it is a different variable, in this section's files, and that section's finding
  does not cover it.
- **Impact:** an operator who points `RESEARCH_LLM_ENDPOINT` at a dedicated research model gets the
  default routing with no warning and no error; the deep-research feature keeps using whatever the
  normal model path resolves to. The cost is an afternoon of debugging a setting that is documented,
  accepted by every compose variant and ignored.
- **Fix:** either wire it up as the endpoint the research handler prefers, or delete the line from
  `.env.example` and the three compose files. A documented environment variable that no code reads
  is worse than an undocumented one, because the documentation is the thing that misleads.

### [BUG] The docs-only CI bypass skips the tests whose subject is `README.md`

- **Location:** `.github/workflows/ci.yml:128` (with `:136-146`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the `python-tests` job classifies the diff and skips pytest when every changed path
  matches the prose pattern:

  ```
  non_docs=$(echo "$changed" | grep -Ev '^(docs/|[^/]+\.md$|\.github/[^/]+\.md$)' || true)
  if [ -z "$non_docs" ]; then
    echo "docs_only=true" >> "$GITHUB_OUTPUT"
    echo "Docs-only change detected — skipping pytest."
  ```

  `[^/]+\.md$` matches any root-level Markdown file, and `README.md` is one. The comment two lines
  above states the rule that was applied to `website/` and `assets/branding/` — "Keep website/ and
  assets/branding/ out of this bypass: pytest owns regression guards for their published-file and
  orphan-asset contracts" — and `README.md` has the same kind of guard:

  ```python
  # tests/test_security_regressions.py:134-138
  def test_readme_warns_auth_enabled_for_network_access():
      readme = Path("README.md").read_text(encoding="utf-8")
      assert "Keep `AUTH_ENABLED=true` for any network-accessible deployment." in readme
      assert "Keep `LOCALHOST_BYPASS=false` outside local development." in readme
  ```

  plus `tests/test_readme_ascii_fenced.py:12` (`README = ... / "README.md"`) and
  `tests/test_security_regressions.py:125-131`, which reads `README.md` and `website/setup.md` for the
  loopback quickstart. A PR that only edits `README.md` therefore reports green while the assertions
  that guard that file's security guidance never execute. The classifier's treatment of `README.md`
  is pinned as intended by `tests/test_docs_no_orphan_images.py:155`
  (`assert docs_only.match("README.md")`) and by `specs/testing-devops.md:148` ("pytest still skips
  documentation-only changes"), so this is a deliberate decision whose consequence was not
  carried over from the two carve-outs above it rather than an accident.
- **Impact:** the two README sentences that tell a self-hoster to keep authentication on and the
  loopback bypass off are the documented contract for the network-exposure decision the rest of this
  section is about; they can be deleted, weakened or moved without CI noticing. The same applies to
  the two assertions in `tests/test_readme_ascii_fenced.py:25-39`, whose docstring records why they
  exist: the README's original banner rendered misaligned on GitHub (#1390), so the file now pins
  the wordmark image and the fencing rule instead.
- **Fix:** exclude the files pytest reads from the bypass — add `README.md` (and any other root
  Markdown that a test reads) to the `grep -Ev` alternation as an explicit non-doc path, and update
  `tests/test_docs_no_orphan_images.py:155` to match. Narrower and simpler: drop the `[^/]+\.md$`
  arm entirely and let the docs-only fast path cover `docs/` and `.github/*.md`, where no test
  asserts on content.

### [DOC-DRIFT] The focused-test guidance CI prints tells contributors to run pytest with the wrong interpreter

- **Location:** `.github/scripts/focused_test_guidance.py:71`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the helper builds the command it suggests and the workflow writes it into the job
  summary:

  ```python
  def pytest_command(paths: Iterable[str]) -> str:
      """Build a copyable pytest command for changed runnable test files."""
      command = ["python3", "-m", "pytest", "-q", *paths]     # :71
      return shlex.join(command)
  ```

  The repository's testing standard requires the project venv, and a test enforces that the string
  `python3 -m pytest` does not appear in the docs that state the rule:

  ```
  $ grep -n "Run tests with the project" tests/TESTING_STANDARD.md
  27:Run tests with the project virtualenv interpreter (`./venv/bin/python -m pytest`).

  $ sed -n '245,248p' tests/test_docker_devops_hardening.py
      stale_patterns = [
          "python3 -m pytest",
          "python3 -m py_compile",
  ```

  That guard covers `tests/README.md`, `tests/TESTING_STANDARD.md` and `tests/LAYOUT_INVENTORY.md`
  only (`TEST_DOCS`, `tests/test_docker_devops_hardening.py:26-30`), so the script is outside it — but
  it is the one place in the repository that *generates* a command for a contributor to copy, and
  `.github/workflows/ci.yml:64-68` runs it with the runner's system `python3`, which has none of the
  project's dependencies installed. `specs/testing-devops.md:44` describes the helper as mapping
  changed files to "suggested focused tests", so the string is the product of the job, not an
  internal detail.
- **Impact:** a contributor who pastes the suggested command gets whatever `python3` is on their
  PATH — the same non-authoritative interpreter the testing standard and its regression test exist to
  rule out. The failure mode is a confusing collection error or, worse, a run against different
  dependency versions that passes locally and fails in CI.
- **Fix:** emit `./venv/bin/python -m pytest -q ...` in `pytest_command`, matching
  `tests/TESTING_STANDARD.md:27`, and add `python3 -m pytest` to the `stale_patterns` list's coverage
  by asserting the helper's output shape in `tests/test_focused_test_guidance.py`.

### [SECURITY] The Docker CLI tarball is installed as root with no integrity check

- **Location:** `Dockerfile:59-70`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the image downloads a release tarball and unpacks it into `/usr/local/bin` with
  nothing verifying what arrived:

  ```dockerfile
  ARG DOCKER_CLI_VERSION=29.6.2
  RUN ARCH="$(dpkg --print-architecture)" \
      && case "$ARCH" in \
           amd64) DARCH=x86_64 ;; \
           arm64) DARCH=aarch64 ;; \
           *) echo "unsupported arch $ARCH"; exit 1 ;; \
         esac \
      && curl -fsSL "https://download.docker.com/linux/static/stable/${DARCH}/docker-${DOCKER_CLI_VERSION}.tgz" \
         -o /tmp/docker.tgz \
      && tar -xzf /tmp/docker.tgz -C /tmp \
      && install -m 0755 /tmp/docker/docker /usr/local/bin/docker
  ```

  The same repository verifies checksums for the two binaries its CI downloads —
  `.github/workflows/secret-scan.yml:50-57` (gitleaks) and
  `.github/workflows/workflow-security.yml:45-53` (actionlint) both pin a version *and* a SHA-256 and
  run `sha256sum -c -` before executing the file — so the norm is established next to the exception.
  The version is pinned, so this is not a moving target; it is the missing second half of the pin.
  The two `pip install` layers below it (`:78`, `:84`) inherit PyPI's own integrity metadata, and the
  apt layer inherits Debian's signed indexes, so this download is the one artifact in the image whose
  bytes are trusted on the strength of TLS alone.
- **Impact:** whatever that tarball contains becomes a root-owned executable in `/usr/local/bin`, and
  the image's own comment (`Dockerfile:54-58`) says why the CLI is there: the host-docker mode mounts
  `/var/run/docker.sock` (`docker/host-docker.yml:9`) so the container drives the host daemon. A
  substituted binary is therefore a path from image build to host control, not just a broken
  container. The window is narrow — the URL is HTTPS and the version is pinned, so it takes an
  upstream compromise or a TLS-breaking interceptor — which is why this is `backlog` rather than
  `next`, and closing it costs one `ARG` and one `sha256sum -c` line.
- **Fix:** add the upstream SHA-256 for the pinned version as an `ARG` beside `DOCKER_CLI_VERSION`
  and check it with `echo "${DOCKER_CLI_SHA256}  /tmp/docker.tgz" | sha256sum -c -` before the
  `tar -xzf`, the way the two workflows already do. Bumping the version then means bumping both
  arguments together, which is the same discipline `dependabot.yml` already asks of the action pins.
