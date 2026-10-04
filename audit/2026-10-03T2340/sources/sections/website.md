# Project website

## Overview

The published project website: the landing page, the operator and contributor guides, and the clips
the landing page plays. The section reads documentation against code — every concrete promise in a
guide (an environment variable and its default, a path, a script flag, a port, a printed password)
is checked against the tree that has to honour it, and each finding is stated against the page.

The files a guide describes belong to other sections: `scripts.md` owns the backup and audit
scripts, `build-install-deploy.md` the workflows, compose files and requirements, `src-documents.md`
the upload and attachment code, `src-memory-rag.md` the Chroma client,
`src-tools-capabilities-policy.md` the built-in MCP registration. They were read here only as
evidence for a mismatch.

## Coverage

Line numbers refer to the tree at commit `2992bf6d368a`; the only later commit,
`4ceb65d4 in-progress code-audit`, adds the audit run's own files under `audit/` and touches no
code.

**Read fully:** all nine assigned text files (2,476 lines).

| File | Lines |
| --- | ---: |
| `website/index.html` | 961 |
| `website/setup.md` | 767 |
| `website/agent-migration.md` | 198 |
| `website/pr-blocker-audit.md` | 192 |
| `website/backup-restore.md` | 133 |
| `website/security-ci.md` | 105 |
| `website/attachments.md` | 89 |
| `website/email-outlook.md` | 21 |
| `website/_config.yml` | 10 |

`website/setup.md` was read line by line against the code it instructs the operator to run.

**Not read:** the eight assigned `.webm` clips (6,390,879 bytes of binary media), confirmed to be
WebM containers with `file` and checked only through the `<source>` references in `index.html`.
Nothing inside the recordings was reviewed.

**Read partially:** the code each finding rests on.

- `src/chroma_client.py` in full (73 lines); `scripts/odysseus-backup` in full (272);
  `scripts/_lib/cli.py` in full (122); `launch-windows.ps1` in full; `src/upload_limits.py` in
  full (72)
- `setup.py` at `create_default_admin` (`:90-152`)
- `start-macos.sh` at the dependency install and the ChromaDB bootstrap (`:141-215`)
- `core/auth.py` at `DEFAULT_PRIVILEGES` (`:24-48`) and `get_privileges`
- `routes/auth_routes.py` at `_secure_cookie` (`:88-112`), `POST /api/auth/settings` (`:726-757`)
  and the signup toggle (`:635-660`)
- `routes/chat_routes.py` at the per-user privilege gate (`:1543-1570`)
- `routes/chat_helpers.py` at the attachment manifest (`:390-405`)
- `routes/model_routes.py` at `GET /api/model-endpoints` (`:1932-1935`) and
  `PATCH /model-endpoints/{ep_id}` (`:2495-2516`)
- `routes/email_helpers.py` at `_friendly_email_auth_error` (`:195-224`)
- `core/middleware.py` at the HSTS block (`:105-114`)
- `src/agent_loop.py` at `_is_ollama_openai_compat_url` and the tool-path choice (`:930-1070`)
- `src/mcp_oauth.py` at `_resolve_redirect_base` (`:20-42`)
- `core/database.py` at `_migrate_chat_messages_fts` (`:2178-2260`)
- `src/app_initializer.py` at the manager construction and the memory-vector warning (`:75-110`)
- `services/tts/tts_service.py` at `__init__` (`:33-49`)
- `static/js/ui.js` at `copyToClipboard` (`:218-235`), `static/js/chat.js:5310-5316`,
  `static/js/codeRunner.js:100-125` and the other `navigator.clipboard` call sites
- `requirements.txt` (`:1-30`), `requirements-optional.txt` in full, `Dockerfile` (`:6-79`)
- `docker-compose.yml` in full, `docker/host-docker.yml`, `docker/gpu.nvidia.yml`,
  `docker/gpu.amd.yml`, `docker/entrypoint.sh`
- the nine workflows this section cites, at their names, triggers and job/step identifiers: `ci`,
  `secret-scan`, `workflow-security`, `dependency-review`, `container-scan`, `container-trivy`,
  `codeql`, `deploy-pages`, `docker-publish`
- `.github/CODEOWNERS`, `.github/dependabot.yml`, `.gitignore`, `.dockerignore`
- `scripts/encode_previews.sh`, `scripts/check-docker-gpu.sh` at its flag parsing and `.env` writer
- `src/settings.py`, `src/auth_helpers.py` and `app.py` only at the call sites cited

**Not read:** the rest of the repository — in particular the implementations behind features the
guides mention in passing (Cookbook, email, calendar, the MCP manager internals, the front end's
settings UI), which other sections own.

**Checks run:**

```
$ venv/bin/python -m pytest -q tests/test_docs_no_orphan_images.py tests/test_setup_admin_user.py \
    tests/test_agent_migration_manifest.py tests/test_pr_blocker_audit.py \
    tests/test_backup_cli_security.py tests/test_readme_ascii_fenced.py tests/test_security_regressions.py
195 passed, 1 warning in 1.40s

$ venv/bin/python -m pytest -q tests/test_backup_import_cross_user_dedup.py \
    tests/test_backup_import_skills_dedup.py tests/test_backup_import_skills.py \
    tests/test_upload_handler_cleanup.py
18 passed, 1 warning in 0.57s
```

The first group is the set that reads these pages (`tests/test_docs_no_orphan_images.py` asserts the
guide front matter, the site's video references and that every relative guide link resolves inside
`website/`; `tests/test_security_regressions.py:126-129` reads `website/setup.md` as part of its
source). `docker compose config -q` was run for all five `COMPOSE_FILE` combinations the guide
documents and for both standalone GPU files — all seven parse (each only warns that
`ODYSSEUS_TTS_CACHE_MAX_BYTES` is unset). Also run: a probe of the installed ChromaDB distribution
and the thin-client mode (quoted in the first finding), `git ls-files website/` (17 files, no
`.mp4`), `find . -name '*.mp4'` (no result outside `venv/` and the audit run), and
`grep -o 'https\?://[^"'\'' )]*' website/index.html` for the page's absolute URLs.

**Drift reported elsewhere:** the npx cache-gating paragraph at `website/setup.md:741` is already a
finding in `src-tools-capabilities-policy.md` — the code defaults to letting `npx -y` install
`@playwright/mcp` on first start, and the switch that restores the documented no-download behaviour
is undocumented — so it is not restated here. The reverse-proxy guidance at `website/setup.md:537`
is cited as evidence by `routes-rest-auth-admin.md` for the client-IP derivation there; the page's
own claims about it (`SECURE_COOKIES`, HSTS, `OAUTH_REDIRECT_BASE_URL`, `GOOGLE_OAUTH_REDIRECT_URI`)
were checked against `_secure_cookie` (`routes/auth_routes.py:88-112`), the HSTS block
(`core/middleware.py:105-114`) and `_resolve_redirect_base` (`src/mcp_oauth.py:20-42`) and hold.

### [DOC-DRIFT] The native install path never gets a ChromaDB server, and the backup guide says the vectors live in `data/chroma/`

- **Location:** `website/setup.md:60-73` (with `website/setup.md:726` and `website/backup-restore.md:132`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the manual native steps create a venv, install `requirements.txt`, run `python
  setup.py` and start uvicorn; nothing in them starts ChromaDB. The app reaches ChromaDB only over
  HTTP and needs a server already listening (`src/chroma_client.py` itself is owned by
  `src-memory-rag.md`, which reports the store's internals; the defect here is the install path that
  never gives it one):

  ```python
  host = os.getenv("CHROMADB_HOST", "localhost")          # src/chroma_client.py:49
  port = int(os.getenv("CHROMADB_PORT", "8100"))          # :50
  if not _port_open(host, port):
      raise RuntimeError(
          f"ChromaDB is not reachable at {host}:{port}. Start the ChromaDB "
          f"service (e.g. `docker compose up chromadb`) or set CHROMADB_HOST / "
          f"CHROMADB_PORT to point at a running instance.")  # :52-57
  client = chromadb.HttpClient(host=host, port=port)      # :59
  ```

  `grep -rn "import chromadb\|from chromadb"` over the tree outside `venv/` returns exactly this one
  import, and `grep -rn PersistentClient` returns nothing, so there is no in-process store the app
  could fall back to. The shipped dependency is the thin HTTP client, which carries no server and no
  CLI:

  ```
  $ venv/bin/python -c "import importlib.metadata as m; d=m.distribution('chromadb-client'); print(m.version('chromadb-client'), list(d.entry_points))"
  1.5.9 []
  $ ls venv/bin | grep -i chroma
  (no output)
  $ venv/bin/python -c "import chromadb; print('is_thin_client:', chromadb.is_thin_client)"
  is_thin_client: True
  ```

  The only place in the tree that starts a server is the macOS script, and it first swaps the thin
  client for the full package so that a `chroma` CLI exists:

  ```bash
  if "$VENV_PY" -m pip show chromadb-client >/dev/null 2>&1; then   # start-macos.sh:158
      "$VENV_PY" -m pip uninstall -y chromadb-client                # :160
      "$VENV_PY" -m pip install --force-reinstall chromadb          # :161
  fi
  ...
  CHROMA_BIN="$(dirname "$VENV_PY")/chroma"                         # :199
  nohup "$CHROMA_BIN" run --host "$CHROMA_BIND" --port "$CHROMA_PORT" --path "$PWD/data/chroma" >"$CHROMA_LOG" 2>&1 &   # :213
  ```

  On the native path the guide mentions ChromaDB only in the configuration table, where
  `CHROMADB_PORT` defaults to `8100` "for manual host runs" (`website/setup.md:726`) without saying
  what to run there, and in the troubleshooting entry that treats installing the full package as a
  conflict fix (next finding). `website/backup-restore.md:132` then promises "On native installs
  ChromaDB lives at `data/chroma/` and is included in the snapshot normally" — true for the macOS
  script, which passes `--path "$PWD/data/chroma"` and whose bind mount makes `./data` the same tree
  for Docker, but not for the manual native install, where nothing creates `data/chroma/`.
- **Impact:** an operator who follows the manual native steps gets an app with no vector store:
  `get_rag_manager()` returns `None` (`app.py:561-570`) and RAG retrieval, semantic memory and the
  tool index fall back to keyword search, with `MemoryVectorStore DEGRADED: ChromaDB vector memory
  unavailable` in the log (`src/app_initializer.py:106`) and a DEGRADED row in service health. The
  guide's own "Useful checks" greps for `DEGRADED` (`website/setup.md:366`), so the symptom is
  discoverable, but nothing in the guide says how to fix it on Linux — the runtime error text
  suggests `docker compose up chromadb`, which a native user is not running. The backup guide
  compounds it: the operator is told the vectors live in `data/chroma/` and are inside the snapshot,
  so a restore is trusted to have recovered an index that was never built.
- **Fix:** add the prerequisite to the native section — start a ChromaDB server on
  `CHROMADB_HOST:CHROMADB_PORT` (`pip install chromadb && chroma run --path data/chroma`, or the
  compose service) before starting Odysseus — and qualify `website/backup-restore.md:132` so
  `data/chroma/` is only claimed when a server was started with that path.

### [DOC-DRIFT] The ChromaDB troubleshooting entry describes a mode the app does not have, and its fix removes the dependency `requirements.txt` installs

- **Location:** `website/setup.md:428-435`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the entry reads "If `chromadb-client` (the lightweight HTTP-only package) is
  installed alongside the full `chromadb` package, Odysseus starts but ChromaDB silently falls back
  to HTTP-only mode and fails", with this fix:

  ```bash
  ./venv/bin/pip uninstall chromadb-client -y
  ./venv/bin/pip install --force-reinstall chromadb
  ```

  HTTP-only is not a fallback in this codebase, it is the only mode: `src/chroma_client.py:59`
  constructs `chromadb.HttpClient` and nothing else, and the probe in the previous finding shows the
  installed module reporting `is_thin_client: True` with `chromadb.PersistentClient(...)` raising
  `RuntimeError: Chroma is running in http-only client mode ...`. The package the fix removes is the
  one the project declares:

  ```text
  # chromadb-client is the lightweight HTTP client (talks to a standalone
  # ChromaDB service); fastembed runs local ONNX embeddings.      requirements.txt:17-18
  chromadb-client                                                 requirements.txt:19
  ```

  The failure the app actually reports when the client is installed and no server is running is the
  opposite of "silently ... falls back": `ChromaDB is not reachable at localhost:8100. Start the
  ChromaDB service ...` (`src/chroma_client.py:53-56`). The word "embedded" in the heading appears
  nowhere else in the tree: `grep -rn -i embedded` over `*.py`, `*.md` and `*.txt` outside `venv/`
  matches ChromaDB only in this heading.

  The block carries the same wrong model in its own comment — "chromadb-client (HTTP-only) conflicts
  with the full chromadb package ... prevent ChromaDB from silently failing in HTTP-only mode"
  (`start-macos.sh:158-159`) — which is where the guide entry's wording comes from. The
  unconditional-reinstall side of that block is reported in `build-install-deploy.md` ([PERF]
  `start-macos.sh` force-reinstalls `chromadb` on every launch); the subject here is the page that
  repeats the claim.
- **Impact:** an operator who greps the guide for a ChromaDB error is sent after a conflict that
  cannot occur, and the recommended fix puts the environment out of sync with `requirements.txt` —
  the next `pip install -r requirements.txt` restores `chromadb-client`, so the state is not
  durable. The real prerequisite (a reachable server) is visible only in the runtime error text.
- **Fix:** retitle the entry to the failure that exists ("ChromaDB not reachable / DEGRADED") and
  make the body about starting a server on `CHROMADB_HOST:CHROMADB_PORT`; if the pip swap is kept
  for the macOS-style local server, say that is what it is for rather than calling it a conflict
  fix.

### [DOC-DRIFT] `security-ci.md` tells the operator to enable "Require review from Code Owners", but no path has an owner

- **Location:** `website/security-ci.md:82-84` (with `.github/CODEOWNERS:1-9`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the step reads "Also enable **Require a pull request before merging** and **Require
  review from Code Owners** (this uses the `.github/CODEOWNERS` file so every change needs your
  sign-off)." The file it points at carries no rules at all:

  ```text
  # Code owners.
  #
  # Intentionally empty for now. The catch-all rule that mapped every path to a
  # single owner froze all merges the moment "Require review from Code Owners"
  # was enabled, because no other maintainer's approval could satisfy the gate.
  # A per-area ownership map (security/auth, CI, frontend, agent internals, with
  # multiple named owners per line) is being worked out in issue #593; once
  # agreed it replaces this file.
  ```

  (`cat .github/CODEOWNERS` — nine lines, all comments, no `pattern @owner` entry.) GitHub requires
  approval from a code owner *of the changed files*; with no owner patterns there is no such
  approval to require, so the setting cannot deliver the sign-off the page promises. The rest of the
  page was verified against the workflows and is correct: the required-check names match
  `ci.yml:73` (`Python syntax (compileall)`), `ci.yml:86` (`JS syntax (node --check)`),
  `secret-scan.yml:32` (`gitleaks`), `workflow-security.yml:33` (`actionlint`) and `:58`
  (`zizmor (Actions SAST)`), `container-scan.yml:34` (`hadolint (Dockerfile lint)`) and
  `dependency-review.yml:31` (`dependency-review (PR gate)`); the advisory ones match
  `dependency-review.yml:50` (`pip-audit (advisory)`) and `container-trivy.yml:50`
  (`Trivy (image scan, advisory)`); every workflow runs on `pull_request`; and `.github/dependabot.yml`
  is weekly for pip, npm, github-actions and docker as the page says.
- **Impact:** a maintainer who follows the page believes every change needs their review before it
  can merge; in fact the branch rule adds nothing, and a pull request can be merged without an owner
  approval. The repository documents the ownerless state in the file itself (issue #593) and in the
  same file's closing line ("required reviews and the security CI gate ... remain in force via
  branch protection"), so the page and the file disagree about which gate is actually in force.
- **Fix:** drop "Require review from Code Owners" from the steps until `.github/CODEOWNERS` carries
  rules, or keep the step and add "(no effect until `.github/CODEOWNERS` lists owners — see #593)".

### [DEPENDENCY] The landing page loads two images from third-party origins with no local copy or pinning

- **Location:** `website/index.html:519` and `website/index.html:530`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the only non-GitHub absolute URLs on the page are two `<img>` sources:

  ```
  $ grep -o 'https\?://[^"'\'' )]*' website/index.html | sort | uniq -c | sort -rn
        3 https://github.com/odysseus-dev/odysseus
        2 https://github.com/odysseus-dev/odysseus.git
        1 http://www.w3.org/2000/svg
        1 https://images.pexels.com/photos/5876695/pexels-photo-5876695.jpeg?auto=compress&...
        1 https://cdn.prod.website-files.com/66708f90d7e407423093fa76/66708f91..._john-carter-testimonial-image-dentistry-x-webflow-template.png
  ```

  `website/index.html:519` is the Webflow template asset and `:530` the Pexels photo, both in the
  testimonial carousel (`loading="lazy"`, no `srcset`, no local copy). There is no remote script,
  stylesheet, font or `@import` on the page — the only `<script>` is the inline block at `:703` and
  the only `<link>` is a data-URI favicon (`:8`) — so these two images are the whole third-party
  surface. `git ls-files website/` shows no committed
  copy of either image, and the repository's asset guard only walks in the other direction
  (`tests/test_docs_no_orphan_images.py:97-103` asserts every tracked video is *referenced*, not
  that every reference is tracked).
- **Impact:** every visitor's browser fetches bytes from `cdn.prod.website-files.com` and
  `images.pexels.com`, disclosing their IP, user agent and the site as referrer to two third parties
  the project does not control — on a page whose copy says "Local-first, privacy-first, and no
  telemetry" (`:433`) and offers a "No telemetry" pill (`:690`). The page also breaks if the Webflow
  template asset (someone else's demo file) is moved or removed, and the image content can change
  under the project without a commit.
- **Fix:** self-host both images under `website/` (they are two small avatars) and reference them
  relatively, or replace them with the inline SVG avatars the other two cards already use.

### [DEAD-CODE] Eight `<source>` elements point at `.mp4` files that were never committed

- **Location:** `website/index.html:612` (and `:621`, `:626`, `:631`, `:636`, `:641`, `:646`, `:655`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** each preview panel and the section background offer an `.mp4` fallback after the
  `.webm` source:

  ```html
  <video muted loop playsinline preload="none"><source src="chat.webm" type="video/webm"><source src="chat.mp4" type="video/mp4"></video>
  ```

  `grep -c '\.mp4' website/index.html` is 8; the files are absent from the tree and from the index:

  ```
  $ find . -name '*.mp4' -not -path './venv/*' -not -path './audit/*'
  (no output)
  $ git ls-files website/
  website/_config.yml
  website/agent-migration.md
  ... (17 entries: the nine text files and eight .webm clips)
  ```

  `.mp4` is not gitignored (`.gitignore` has no `mp4` rule), so these are not ignored files — the
  fallbacks were simply never added. `scripts/encode_previews.sh:1-3` is the producer and emits both
  halves ("Encode a source screen-recording (.mkv) into web-optimized preview clips for the landing
  page: website/<name>.webm (VP9) + website/<name>.mp4 (H.264)"), so the intent is a matched pair.
  The repository guard does not catch this: `tests/test_docs_no_orphan_images.py:97-103` asserts
  tracked videos are referenced by the entry point, not that referenced videos are tracked.
- **Impact:** a browser that cannot play VP9/WebM requests `chat.mp4`, `bg.mp4` and the rest, gets a
  404 from GitHub Pages, and shows the empty labelled placeholder instead of the preview — the
  inline comment at `:795` ("files just leave the labeled placeholder") confirms this is the
  degradation path rather than a designed state. The background clip on the "How it started" section
  fails the same way, leaving the tint over an empty area. Modern Chrome, Firefox and Safari play the
  `.webm` source, so the loss is limited to clients without VP9 support — and nothing catches the
  missing half: the encoder's own test asserts only the `.webm` target
  (`tests/test_docs_no_orphan_images.py:142-146`, `assert "landing page: website/<name>.webm" in
  encoder`).
- **Fix:** either commit the eight `.mp4` files the encoder produces, or delete the eight
  `type="video/mp4"` `<source>` lines so the page stops advertising files the repository does not
  ship.

### [DOC-DRIFT] The first-run admin instructions describe a printed password that the native installs never print

- **Location:** `website/setup.md:17-20` (with `website/setup.md:423`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the guide says "On first setup, Odysseus creates an admin account (`admin` unless
  `ODYSSEUS_ADMIN_USER` is set) and prints a temporary password in the terminal. For Docker
  installs, the same line is in `docker compose logs odysseus`." That is the non-interactive branch
  only. `setup.py` prompts on a terminal and prints no password:

  ```python
  elif sys.stdin.isatty() and not os.getenv("ODYSSEUS_SKIP_ADMIN_PROMPT"):
      # Interactive terminal — ask the user
      username, password = _prompt_admin_credentials()          # setup.py:113-115
  else:
      # Non-interactive (Docker, CI) — fall back to generated password
      password = password or __import__("secrets").token_urlsafe(18)   # :119
  ...
  if sys.stdin.isatty() and not os.getenv("ODYSSEUS_ADMIN_PASSWORD"):
      print(f"  [ok] Admin account created ({username})")        # :134-135  — no password
  else:
      print(f"  [ok] Initial admin user created ({username})")   # :137
      if not os.getenv("ODYSSEUS_ADMIN_PASSWORD"):
          print(f"        Temporary password: {password}")       # :139
  ```

  Both native paths the guide documents run `setup.py` with a terminal attached: the manual
  Linux/macOS steps (`python setup.py`, `website/setup.md:67`), `start-macos.sh:168`
  (`ODYSSEUS_SKIP_RUN_HINT=1 ./venv/bin/python setup.py` — that variable suppresses the run hint, not
  the prompt) and `launch-windows.ps1:140` (`& $venvPy setup.py`). In those runs the operator chooses
  the username (default `admin`) and types the password, so neither the printed line nor
  `ODYSSEUS_ADMIN_USER` is what sets it. Line 423 repeats the assumption for Windows: "log in with
  the generated admin password".
- **Impact:** an operator following the native guide looks for a temporary password in the terminal
  that is never printed (or, in the SSH-without-a-TTY case, gets one without being told it exists),
  and the sentence about `ODYSSEUS_ADMIN_USER` reads as the only way to change the account name when
  the prompt also does. Nothing breaks — the account is created either way — but the first
  instruction in the guide does not describe what the reader will see.
- **Fix:** say the native installs prompt for a username and password (Enter accepts `admin`), and
  keep "prints a temporary password" for the non-interactive case (`docker compose logs odysseus`,
  or `ODYSSEUS_SKIP_ADMIN_PROMPT=1`).

### [DOC-DRIFT] The plain-HTTP clipboard trap is stale: the shared copy helper falls back to `execCommand`

- **Location:** `website/setup.md:456`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the trap says "**Copy buttons do nothing over a plain-HTTP Tailscale/LAN URL.**
  Browsers only expose the clipboard API (`navigator.clipboard`) on **secure origins** ... Over
  `http://100.x.y.z:7860` it is blocked." The shared helper used by the chat code blocks catches the
  rejection and copies through a textarea instead:

  ```javascript
  export async function copyToClipboard(text) {          // static/js/ui.js:220
    try {
      await navigator.clipboard.writeText(text);         // :222
      showToast('Copied');
    }
    catch {
      const ta = document.createElement('textarea');     // :226
      ta.select();
      document.execCommand('copy');                      // :231
      showToast('Copied');
    }
  }
  ```

  and the code-block button routes through it (`static/js/chat.js:5316`
  `uiModule.copyToClipboard(code)`), as does the session transcript export
  (`static/app.js:495`). `static/js/codeRunner.js:103-106` states the intent in a comment — "the
  single most reliable path across browsers / non-secure contexts / mobile Firefox" — and
  `static/js/cookbook-diagnosis.js:959-960` names "non-HTTPS origins (Tailscale IPs, LAN IPs, etc.)"
  explicitly. Other copy handlers still call `navigator.clipboard.writeText` with no fallback
  (`static/js/settings.js:4374`, `static/js/notes.js:2494`, `static/js/sessions.js:742`,
  `static/js/document.js:9146`, `static/js/documentLibrary.js:151`, `static/js/emailLibrary.js:656`,
  `static/js/tasks.js:1500`, `static/js/admin.js:2675`, `static/js/cookbook.js:1577`, `:1705`), so
  the page's blanket "copy buttons do nothing" is true for some surfaces and false for the ones
  users hit most.
- **Impact:** an operator on a plain-HTTP LAN URL who reads the trap may stand up TLS for a problem
  they do not have, or report a working copy button as broken; conversely the buttons that really do
  fail over HTTP are not the ones the paragraph points at. Low reach — the advice to prefer HTTPS is
  still correct for other reasons.
- **Fix:** narrow the claim to the handlers without a fallback, or say that copy works over plain
  HTTP wherever the shared helper is used and fails on the settings, notes, sessions and document
  surfaces.
