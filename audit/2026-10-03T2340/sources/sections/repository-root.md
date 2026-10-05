# Repository root and project policy

## Overview

The seven root documents that state what the project promises its users and contributors:

- `ACKNOWLEDGMENTS.md` (third-party attribution and the license-compatibility note)
- `CONTRIBUTING.md` (branch model, setup, checks, style and code conventions)
- `LICENSE` (the license text)
- `README.md` (quick start, image tags, feature list, security pointers)
- `ROADMAP.md`
- `SECURITY.md` (supported versions, deployment guidance, the fork-publishing scan, reporting)
- `THREAT_MODEL.md` (trust boundary, roles, loopback, prompt-injection policy, headers, known gaps)

The boundary: every finding below is about a document's claim, not about the code the claim
describes. The files these documents point at belong to other sections and are cited by name, never
restated. `.env.example`, `docker-compose*.yml`, the `Dockerfile`, `.github/workflows/*` and
`website/setup.md` are `build-install-deploy` and `website`; `core/middleware.py` and `core/auth.py`
are `core-auth-session`; the tool gates are `src-tools-capabilities-policy` and
`src-tools-parse-exec`; `src/pdf_runtime.py` and the document routes are `src-documents` and
`routes-gallery-document`; `services/search/` is `services-search`; `static/lib/` is
`static-assets-vendored`. This section does not cover whether those components are correct — only
whether the root documents describe them correctly.

## Coverage

**Read fully:** all seven assigned files, 846 lines.

| File | Lines |
| --- | ---: |
| `LICENSE` | 235, the unmodified GNU AGPL-3.0 text |
| `ACKNOWLEDGMENTS.md` | 181 |
| `CONTRIBUTING.md` | 133 |
| `README.md` | 89 |
| `ROADMAP.md` | 87 |
| `THREAT_MODEL.md` | 81 |
| `SECURITY.md` | 40 |

**Read partially:** the code and documents each claim points at, as far as the claim required.

- `core/middleware.py` in full (152 lines)
- `core/auth.py` at `DEFAULT_PRIVILEGES` (`:24-48`), `TOKEN_TTL` (`:53`), `RESERVED_USERNAMES`
  (`:55-62`), the 2FA backup codes (`:519-543`), `validate_token` (`:598-621`) and the atomic
  session writes (`:22`, `:152-157`)
- `src/owner_identity.py` (`:1-19`)
- `src/auth_helpers.py` at the `LOCALHOST_BYPASS` branch (`:150-153`)
- `src/tool_security.py` at `NON_ADMIN_BLOCKED_TOOLS` (`:42-78`), `is_public_blocked_tool` (`:234`)
  and `owner_is_admin_or_single_user` (`:237-271`)
- `src/tool_execution.py` at the admin and public-blocked gate (`:1064-1070`)
- `routes/auth_routes.py` at `_secure_cookie` (`:89-110`)
- `routes/webhook/webhook_routes.py` at the `/v1/chat` direct-`base_url` branch (`:270-300`)
- `src/url_security.py` at `is_public_http_url`/`validate_public_http_url` (`:74-93`)
- `src/search/{core,providers,analytics,cache,content,query,ranking}.py`
- `src/pdf_runtime.py` (15 lines)
- `src/pdf_forms.py` at the `fitz` import (`:12-19`)
- `routes/document/document_routes.py` at the `fitz` sites (`:1151`, `:1220`, `:1249`, `:1296`,
  `:1425`)
- `src/app_helpers.py` at `serve_html_with_nonce` (`:30-50`)
- `docker/entrypoint.sh` (the `setup.py` invocation) and `setup.py` (`:100-141`)
- `docker-compose.yml` at the image/build block (`:1-14`) and the four published ports (`:14`,
  `:102`, `:134`, `:168`)
- `.github/workflows/ci.yml`, `docker-publish.yml` and `secret-scan.yml`
- `.github/ISSUE_TEMPLATE/config.yml`
- `requirements.txt` and `requirements-optional.txt`
- `website/setup.md` at `:31`, `:469` and the security notes
- `static/index.html` and `static/login.html` at their `nonce` placeholders
- the headers of the bundles under `static/lib/` and the lines of `static/js/tasks.js`,
  `static/js/admin.js` and `static/style.css` that `SECURITY.md`'s scan matches
- the tests named in the findings

**Not read:**

- the other sections' paths outside the regions above
- `static/` beyond the lines named
- the minified bundles beyond their first bytes and version strings
- these trees, outside the section's scope:
  - `specs/`, `swift/` and `companion/`
  - `integrations/`, `mcp_servers/` and `data/`
  - the rest of `website/`

**Checks run** (all from the repository root; `venv/bin/python` is Python 3.12.13):

```
$ venv/bin/python -m py_compile app.py routes/*.py src/*.py          # CONTRIBUTING's check
exit=0
$ node --check static/js/tasks.js                                    # CONTRIBUTING's check
node ok
$ docker compose config -q                                           # CONTRIBUTING's Docker check
level=warning msg="The \"ODYSSEUS_TTS_CACHE_MAX_BYTES\" variable is not set. Defaulting to a blank string."
exit=0
$ docker compose up --dry-run -d                                     # README's pull-then-build claim
 Image ghcr.io/odysseus-dev/odysseus:latest Pulling
 Image ghcr.io/odysseus-dev/odysseus:latest Pulled
$ venv/bin/python -m pytest -q                                       # CONTRIBUTING's test check
5952 passed, 4 skipped, 127 warnings in 140.85s (0:02:20)
$ venv/bin/python -m pytest -q tests/test_readme_ascii_fenced.py tests/test_docs_no_orphan_images.py \
      tests/test_setup_admin_user.py tests/test_security_regressions.py tests/test_docker_devops_hardening.py
127 passed, 1 skipped, 1 warning in 1.23s
$ git check-ignore -v .env data/auth.json data/app.db logs/compound.log odysseus.db
.gitignore:14:.env	.env
.gitignore:28:data/	data/auth.json
.gitignore:28:data/	data/app.db
.gitignore:31:logs/	logs/compound.log
.gitignore:33:*.db	odysseus.db
$ git symbolic-ref refs/remotes/origin/HEAD
refs/remotes/origin/dev
```

**Claims checked and found accurate** (the positive half of this pass; each was tested against the
tree, not assumed):

- `CONTRIBUTING.md`'s branch model and gates. `refs/remotes/origin/HEAD` is `origin/dev`; CI runs on
  pushes to `main` and `dev` and on pull requests (`.github/workflows/ci.yml:3-6`); docker publish
  does the same (`docker-publish.yml:14-16`). All four documented check commands exist and pass, and
  `pytest`/`pytest-asyncio` are in `requirements.txt:48-49`, so the documented setup installs the
  documented test runner.
- `README.md`'s quick start. `docker compose up --dry-run -d` plans a pull of
  `ghcr.io/odysseus-dev/odysseus:latest` with no build step, matching "pull the official multi-arch
  image … and only build locally if the pull fails"; the tag scheme it describes matches
  `docker-publish.yml:4-7` (`:latest`, `:X.Y.Z`, `:X.Y.Z-<sha>` on `main`; `:dev`,
  `:X.Y.Z-dev.<sha>` on `dev`); and the first admin password really is printed to the container log,
  because `docker/entrypoint.sh` runs `/app/setup.py` on every start and `setup.py:139` prints
  `Temporary password: …` when the process is non-interactive and `ODYSSEUS_ADMIN_PASSWORD` is unset.
- `SECURITY.md`'s deployment guidance. `AUTH_ENABLED` is read by `src/owner_identity.py:19`,
  `LOCALHOST_BYPASS` only applies to a loopback caller (`src/auth_helpers.py:150-153`), and the
  `SECURE_COOKIES` behaviour described is the implemented one — an explicit `true`/`false` is
  authoritative, anything else derives `Secure` from the request scheme or the first
  `X-Forwarded-Proto` hop (`routes/auth_routes.py:89-110`, pinned by `tests/test_auth_policy.py:307-361`).
  The internal-only port list matches the compose file (Odysseus 7000 at `docker-compose.yml:14`,
  ChromaDB 8100 at `:102`, SearXNG 8080 at `:134`, ntfy 8091 at `:168`; Ollama 11434 is its own
  default and is named at `:30`), and the reporting guidance matches
  `.github/ISSUE_TEMPLATE/config.yml`, which links the private advisory form and says to read
  `SECURITY.md`.
- `THREAT_MODEL.md`'s role table and authentication section. `core/auth.py:24-40` `DEFAULT_PRIVILEGES`
  grants non-admins exactly the six ✓ rows (chat, browser, documents, research, images, memory) and
  none of the ✗ ones; `src/tool_security.py:42-78` blocks the tools behind the ✗ rows (email, shell,
  Python, file read/write, MCP, calendar, tokens, webhooks, model serving, vault, settings) and
  `:234` blocks every `mcp__` name for non-admins, as the document states.

  `TOKEN_TTL` is 7 days (`:53`), sessions are written with `core.atomic_io.atomic_write_json` (`:22`,
  `:152-157`), 2FA issues exactly 8 backup codes (`:520`), `validate_token` re-checks that the user
  record still exists (`:611-617`), and `internal-tool` is in `RESERVED_AUTH_USERNAMES`
  (`src/owner_identity.py:11-14`). The loopback description matches `core/middleware.py:20`,
  `:57-72` and `app.py:383-397`, and the claim that tool dispatch checks the owner before admin
  tooling runs is real (`src/tool_execution.py:1064-1070`). The CSP claim is accurate too: the
  middleware sets `script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net` (`:143`) and the HTML
  is templated through `serve_html_with_nonce`, which substitutes `{{CSP_NONCE}}` in
  `static/index.html` and `static/login.html`.
- `ACKNOWLEDGMENTS.md`'s vendored-asset and dependency lists. `static/lib/` holds exactly the
  libraries the table names and nothing else — docx, highlight.js, html2pdf (with the jsPDF and
  html2canvas it bundles), KaTeX, mammoth, Mermaid, node-qrcode and SheetJS xlsx — and `static/fonts/`
  holds exactly the four families listed. The pinned versions that
  can be checked from the bundles match: highlight.js v11.9.0 in its banner, KaTeX `0.16.22` and
  Mermaid `11.16.1` in their bundles, and `ls static/lib/katex/fonts/` shows only `.woff2` (20 files),
  as the note claims. chardet is gone (`grep -rn chardet` over the tree returns nothing) and
  `requirements-optional.txt` really does list PyMuPDF and markitdown.
- `ROADMAP.md` makes no completion claims to falsify: it is a to-do list, and the one refactor target
  that could be checked against the tree is still open (`tour-core.js` does not exist; `static/js/`
  has only `tourAutoplay.js` and `tourHints.js`).
- `LICENSE` and `licenses/`. `LICENSE` is the AGPL-3.0 text and `README.md:89` says
  `AGPL-3.0-or-later`; the six files under `licenses/` cover all three adapted projects (opencode,
  llmfit, Tongyi DeepResearch) and the three asset rows that link a file (KaTeX, Mermaid,
  OpenDyslexic). The contradiction is inside
  `ACKNOWLEDGMENTS.md` itself (finding 1), not between `LICENSE` and `licenses/`.

### [DOC-DRIFT] `ACKNOWLEDGMENTS.md` still describes the shipped core as permissive, four months after the project relicensed to AGPL-3.0

- **Location:** `ACKNOWLEDGMENTS.md:149` (with `:151`, `:160`, `:166`)
- **Severity:** medium
- **Disposition:** fix-now
- **Evidence:** the section headed "License-compatibility notes (for the repo's own LICENSE choice)"
  opens with:

  ```
  The **core ships fully permissive** (MIT-compatible), so the two copyleft
  concerns from earlier are resolved:                                       # ACKNOWLEDGMENTS.md:151
  ```

  and repeats it in two of its four bullets — "The MIT core runs without it" (`:160`), "the MIT core
  runs without it" (`:166`). The repository's own license is the opposite: `LICENSE` is the GNU
  Affero General Public License version 3, and `README.md:89` reads
  `AGPL-3.0-or-later -- see [LICENSE](LICENSE) and [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md)`. The
  relicense left this file untouched — `git show --stat 23f0d64e` ("Change project license to
  AGPL-3.0-or-later", 2026-06-09) lists only `LICENSE` and `README.md`, and
  `git log -1 -S'used *only* by the PDF form-filling feature' -- ACKNOWLEDGMENTS.md` returns the
  initial commit `e5c99a5e` (2026-05-31), so no later commit revised those lines. The same stale
  phrase is repeated in three files outside this section's paths, cited only as corroboration:
  `Dockerfile:75` ("the default image stays MIT-core"), `requirements-optional.txt:33` and `:41`
  ("The MIT core …", "the core stays pure-MIT"), and `src/pdf_forms.py:13`.
- **Impact:** a downstream integrator, packager or contributor who reads this note instead of
  `LICENSE` can reasonably conclude they may redistribute the code on permissive terms, or
  contribute under the assumption that their patch is taken under MIT. README's License line is the
  only pointer to `ACKNOWLEDGMENTS.md` for licensing, so this is the note they are most likely to
  meet first, and it is the only root document that contradicts the LICENSE file.
- **Fix:** replace the "License-compatibility notes" paragraph with a statement of the actual license
  (AGPL-3.0-or-later, matching README) and reframe the four bullets as compatibility notes for
  optional and vendored dependencies rather than for the core; then correct the same phrase in
  `Dockerfile`, `requirements-optional.txt` and `src/pdf_forms.py`.

### [UNDOCUMENTED] The admin-bypass loopback token can be pinned from an undocumented environment variable, and the threat model says it is never persisted

- **Location:** `THREAT_MODEL.md:48` (code: `core/middleware.py:20`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** step 1 of the loopback description reads:

  ```
  1. At app startup, `core/middleware.py` generates a random `INTERNAL_TOOL_TOKEN` via
     `secrets.token_hex(32)`. It is never persisted and never sent to clients.
  ```

  The code prefers an environment value when one is set:

  ```python
  # core/middleware.py:20
  INTERNAL_TOOL_TOKEN = os.environ.get("ODYSSEUS_INTERNAL_TOKEN") or secrets.token_hex(32)
  ```

  That token is the entire credential for the bypass: `require_admin` returns before any user check
  when the header matches (`core/middleware.py:65-72`), and the auth middleware in `app.py:383-397`
  authenticates a request carrying it from a trusted-loopback peer, stamping `current_user` from
  `X-Odysseus-Owner` or as `internal-tool`. Nothing documents the override: a tree-wide
  `grep -rn "ODYSSEUS_INTERNAL_TOKEN"` (excluding `venv/` and this run's `audit/`) returns only
  `core/middleware.py:20`, `grep -n -i internal .env.example` returns no match, and
  `specs/auth-security.md:101` describes the token as "the random per-process secret" without
  mentioning the environment path.
- **Impact:** an operator who sets the variable — or a compose file, image or service unit that sets
  it for them — turns a per-process random secret into a durable, operator-chosen one that satisfies
  every `require_admin` gate, and the threat model's assurance that the secret is never persisted
  becomes false for that deployment. Because the variable appears in no document, an operator cannot
  discover it, rotate it deliberately, or know that the bypass credential is now stable; a security
  reviewer working from `THREAT_MODEL.md:48` will not look for it. Reach is limited to someone who
  can already set the process environment, which is why this is `low`.
- **Fix:** either drop the environment fallback so the token is process-random as documented, or
  document `ODYSSEUS_INTERNAL_TOKEN` in `.env.example` and in the loopback section of
  `THREAT_MODEL.md`, stating that setting it makes the admin bypass credential durable and must be
  treated and rotated as a secret.

### [DOC-DRIFT] The threat model's Known Gaps register is stale in two entries and overstates a third

- **Location:** `THREAT_MODEL.md:77` (and `:79`, `:75`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** gap 2 says a chat-scoped API token "can supply an arbitrary `base_url`; the server
  forwards the LLM request to that host without validating the scheme or address. PR #1039 fixes
  this." The route validates it today — the token-supplied direct `base_url` goes through the public
  URL guard, and a failure is a 400:

  ```python
  # routes/webhook/webhook_routes.py:286-291
  direct_base_url = body.base_url.strip().rstrip("/") if body.base_url else None
  if direct_base_url:
      try:
          base_url = validate_public_http_url(direct_base_url)
      except ValueError as e:
          detail = str(e).replace("URL", "base_url", 1)
          raise HTTPException(400, detail)
  ```

  `validate_public_http_url` (`src/url_security.py:81-93`) rejects anything `is_public_http_url`
  (`:74`) does not accept, and its own docstring states the residual limit: "DNS checks reduce
  obvious private-network targets but do not eliminate every DNS rebinding race by themselves"
  (`:86-87`).

  Gap 3 says five modules under `src/search/` (analytics, cache, content, query and ranking)
  "are still independent copies that can drift". All five are compatibility modules of 11-14 lines
  that alias the `services.search` implementation (`wc -l` → 12, 11, 11, 11, 14), for example
  `src/search/cache.py`: "the implementation now lives in `services.search.cache` so the two
  cannot drift".

  Gap 1's headline still holds, because `bash` is unconfined, but its detail does not. It says the
  `read_file` and `write_file` tools have "no … filesystem confinement", while those handlers
  resolve every model-supplied path through `_resolve_tool_path`. That function denies sensitive and
  app-state paths and requires containment in an allowlist (data subdirectories and temp roots) or
  in the active workspace (`src/tool_execution.py:357-405`; callers at
  `src/agent_tools/filesystem_tools.py` lines 197, 257, 369 and 467). Gap 4, the coarse token
  scopes, is not challenged here.
- **Impact:** the register is what a security reviewer, packager or contributor reads to judge where
  the project is exposed and where help is wanted. A stale entry overstates exposure and misdirects
  work — someone could re-implement the `base_url` guard or redo the search consolidation — and an
  entry that contradicts the code costs the register its credibility for the gaps that are real.
- **Fix:** rewrite gap 2 to say what the guard now does and what it does not (the rebinding limit in
  its own docstring, and the three disagreeing private-address classifiers reported in
  `src-security.md`); reduce gap 3 to the aliasing note it now is or delete it; and correct gap 1 to
  say that the path-based confinement of the file and code-nav tools is not an OS sandbox, with
  `bash` the unconfined path that keeps the gap open.

### [DOC-DRIFT] The threat model does not state multi-user data isolation as a goal, while the code enforces owner scoping and this audit found that enforcement failing

- **Location:** `THREAT_MODEL.md:7-12`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the four things the document says it tries to prevent are unauthenticated access,
  non-admins reaching admin-only capabilities, the agent acting on injected instructions, and
  internal services being externally reachable (`:9-12`). Isolation between users is not among them,
  and the word "owner" appears in the file only in the reserved-username and loopback paragraphs
  (`:40`, `:52`). The code treats owner scoping as a control: `owner_is_admin_or_single_user` and
  `blocked_tools_for_owner` gate the tool surface (`src/tool_security.py:237-271`), the dispatcher
  re-checks it before executing (`src/tool_execution.py:1064-1070`), and the suite carries dedicated
  owner-scope guards (`tests/test_session_list_owner_scope.py`, `tests/test_notes_fail_closed_auth.py`).
  Other sections of this audit found the control failing in places: `src-agent-tools.md` reports
  `[SECURITY] manage_research ignores the owner and operates on every user's research files`
  (rated high there), `core-auth-session.md` reports `[BUG] The sidebar list is served from a global
  100-row cache, so one user's sessions can hide another's`, and `src-chat-session.md:366-380` shows a
  cleanup path that deletes across accounts when the owner is empty. `SECURITY.md`'s own guidance
  assumes multi-account installs ("Disable open signup unless you intentionally want new accounts",
  "Keep demo/test users non-admin").
- **Impact:** with no stated requirement, "one user cannot read or change another user's data" is not
  a documented property of the product, so the owner-scoping defects the audit found sit outside the
  project's own threat model and can be closed as ordinary bugs rather than security bugs. A reader
  deciding whether to host several users — or a reviewer assessing that deployment — has no statement
  to test against, and the many owner checks in the code answer to no stated policy.
- **Fix:** add one line to the prevented list ("one authenticated user reading or changing another
  user's data") and say that per-owner scoping is a security control enforced by the tool gates and
  the owner-scoped stores; either record the known failures as gaps or fix them.

### [DOC-DRIFT] The Python dependency table omits an LGPL package that ships in the core requirements, and seven other installed packages

- **Location:** `ACKNOWLEDGMENTS.md:99` (intro at `:101`, rows `:105-131`, the stale row at `:129`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the section is headed "Python dependencies — Core (`requirements.txt`) and optional
  (`requirements-optional.txt`)", so the table reads as the inventory of those two files. It has 27
  rows; the two files install 31 and 6 package lines. The omissions are:

  | List | Missing packages | Where declared |
  | --- | --- | --- |
  | Core | `nh3`, `httpcore`, `httpx2`, `python-dateutil`, `psycopg2-binary` | `requirements.txt:28,6,53,34,58` |
  | Optional | `faster-whisper`, `soundfile`, `kokoro` | `requirements-optional.txt:13,22,23` |

  One omission matters beyond completeness: `psycopg2-binary` is LGPL, which the document's own
  compatibility note treats as the category it has cleared: "chardet (LGPL-2.1) has been removed
  entirely" (`:153-155`). The installed distribution's metadata says so:

  ```
  $ venv/bin/python -c "import importlib.metadata as m; md=m.metadata('psycopg2-binary'); ..."
  psycopg2-binary      version=2.9.13     License='LGPL with exceptions' classifiers=['License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)']
  ```

  The table also names a package no requirement file installs: `duckduckgo-search (optional)` at
  `:129`, while `requirements-optional.txt:28` installs `ddgs` (the setup guide's optional-dependency
  table already uses `ddgs`, `website/setup.md:468`).
- **Impact:** anyone using this file as the dependency inventory — a packager assembling notices, a
  reviewer checking what copyleft reaches the process, or a contributor looking for the optional
  extras — gets a list that is both short and, in one row, wrong. The LGPL entry is the one that
  matters: the same document argues that the core's copyleft dependencies were resolved, and this
  table does not show the LGPL dependency that remains in the default install. The packages are pip
  dependencies rather than code distributed in the tree, which is why this is `low`.
- **Fix:** add the eight missing rows with their licenses and change the `duckduckgo-search` row to
  `ddgs`, or state at the top of the table that it lists the compatibility-relevant subset rather
  than every requirement.

### [DOC-DRIFT] `ACKNOWLEDGMENTS.md` says PyMuPDF is used only for PDF form-filling, but the PDF viewer requires it

- **Location:** `ACKNOWLEDGMENTS.md:157-160` (table row at `:131`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the note reads:

  ```
  - **PyMuPDF (AGPL-3.0)** is no longer a core dependency. It is **optional** and
    used *only* by the PDF form-filling feature (`src/pdf_forms.py` and the form
    endpoints in `routes/document_routes.py`), lazy-imported and listed in
    `requirements-optional.txt`. The MIT core runs without it.               # ACKNOWLEDGMENTS.md:157-160
  ```

  `src/pdf_runtime.py` exists only to load PyMuPDF for the viewer, and its first constant is the
  user-facing message for a missing dependency:

  ```python
  # src/pdf_runtime.py:3-6
  PDF_VIEWER_PYMUPDF_MISSING = (
      "PDF viewer requires PyMuPDF. Install optional PDF dependencies with "
      "`pip install -r requirements-optional.txt` (PyMuPDF is AGPL-3.0)."
  )
  ```

  The document routes call that loader at `:1151` (`render_pages`), `:1220` (`render_page_png`) and
  `:1425`, with a further `import fitz` at `:1249` and `fitz.open` at `:1296`, and the front end
  frames the result (`static/js/documentLibrary.js:941`). The project's own setup guide already
  states the scope correctly: "`PyMuPDF` | PDF page rendering in the side viewer panel and
  form-filling. (Note: AGPL-3.0)" (`website/setup.md:469`; see also `:31`, "To include optional
  extras in the image (PDF viewer, Office extraction; includes AGPL PyMuPDF)"). The line predates
  the feature: `git log -1 -S'used *only* by the PDF form-filling feature' -- ACKNOWLEDGMENTS.md`
  returns the initial commit `e5c99a5e` (2026-05-31), while `src/pdf_runtime.py` was added in
  `d538882c` (2026-06-01). The separate defect in the form-fill endpoint when PyMuPDF is absent is
  reported in `routes-gallery-document.md`; this finding is about the attribution claim.
- **Impact:** the note is what an operator reads when deciding whether to install the optional
  extras, and it tells them PyMuPDF "only unlocks form-filling" and that the viewer is unaffected. In
  fact the viewer's page-render endpoints cannot work without it, so anyone weighing the optional
  set's AGPL obligations or its footprint gets the wrong scope, and the note's premise — that the
  dependency is narrowly scoped enough to be optional — is weaker than stated.
- **Fix:** name both features and both modules in the bullet — `src/pdf_forms.py` for form filling,
  `src/pdf_runtime.py` for the viewer's page rendering — matching `website/setup.md:469`.

### [DOC-DRIFT] The threat model's framing-header bullet names an exemption no route serves and omits the one that does

- **Location:** `THREAT_MODEL.md:67`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the bullet reads "`X-Frame-Options: DENY` + `frame-ancestors 'none'` on all routes
  except tool-render iframes (which are sandboxed at the HTML level)". The middleware has three
  framing branches, not one:

  ```python
  # core/middleware.py
   97   is_tool_render = path.startswith("/api/tools/") and path.endswith("/render")
   99   is_document_pdf_preview = path.startswith("/api/document/") and path.endswith("/render-pdf")
  101   is_report = path.startswith("/api/research/report/")
  128       response.headers["X-Frame-Options"] = "SAMEORIGIN"          # pdf preview
  131           "frame-ancestors 'self'"
  134       response.headers["X-Frame-Options"] = "DENY"                # everything else
  ```

  The tool-render branch skips every framing header, the document-preview branch sets `SAMEORIGIN`
  with `frame-ancestors 'self'`, and the research-report branch sets no `X-Frame-Options` at all
  (only a CSP that still ends `frame-ancestors 'none'`). No route serves the tool-render path:
  `grep -rn '"/api/tools' --include=*.py` over the tree (excluding `venv/` and this run's `audit/`)
  returns only `core/middleware.py:97` and two tests, no router declares a `/tools` prefix, and the
  only exemption test dispatches a synthetic path (`tests/test_document_render_pdf_iframe.py:92-98`,
  `"/api/tools/foo/bar/render"`). The reachable exemption — the PDF preview — is pinned by
  `tests/test_security_headers_pdf_preview.py:33-35` and
  `tests/test_document_render_pdf_iframe.py:56-62`, neither of which the threat model mentions.
- **Impact:** a reviewer auditing clickjacking protection from this document checks the tool-render
  path, which cannot occur, and misses the framing exemption the app actually grants to
  `/api/document/{id}/render-pdf`; the bullet also implies every route carries `X-Frame-Options`,
  which the research-report pages do not. The exemption itself is deliberate and same-origin, so
  nothing is exposed by the code here — what is wrong is the security document's description of the
  policy a reviewer is meant to trust. Whether the unreachable middleware branch should also be
  deleted is a code question for `core-auth-session`, which owns `core/middleware.py`.
- **Fix:** rewrite the bullet to say that framing is denied everywhere except the document PDF
  preview, which is same-origin frameable so the viewer can embed it, and the tool-render paths,
  which omit framing headers; note that report pages set `frame-ancestors 'none'` without
  `X-Frame-Options`.

### [DOC-DRIFT] `SECURITY.md`'s fork-publishing scan returns two dozen false positives on the repository it ships with

- **Location:** `SECURITY.md:33`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the block tells a fork publisher to run three commands before pushing. The third one,
  run at the reviewed commit over the repository's own files (excluding this run's `audit/`
  artifacts, which a fork does not have), matches 24 lines:

  ```
  $ git grep -n -I -E "(sk-[A-Za-z0-9_-]{20,}|xox[baprs]-|AIza[0-9A-Za-z_-]{20,}|Bearer [A-Za-z0-9._~+/-]{20,})" \
        -- . ':!static/lib/**' ':!package-lock.json' ':!audit/**' | cut -d: -f1 | sort | uniq -c
        1 static/js/admin.js
       15 static/js/tasks.js
        8 static/style.css
  ```

  Twenty-three of them are the `sk-…` alternative matching inside `task-*` CSS class names and
  element ids — `class="task-…"` (`static/js/tasks.js:130`, `:2458`), `id="task-…"` (`:1326`),
  `getElementById('task-…')` (`:1330`, `:1523`, `:1670`), `.task-… {` (`static/style.css:24104`,
  `:24663`) — where the class name itself contains `sk-` followed by a state word. The twenty-fourth
  is the five-character Slack bot-token prefix inside the help text that tells the user where to
  paste their own token (`static/js/admin.js:1843`, a Slack MCP server template). The `check-ignore`
  command in the same block behaves as advertised:
  `git check-ignore -v .env data/auth.json data/app.db logs/compound.log odysseus.db` exits 0 with all
  five paths matched by `.gitignore` (`:14`, `:28`, `:31`, `:33`). The repository's maintained
  scanner is the gitleaks job in `.github/workflows/secret-scan.yml` (pinned to 8.30.1 with a
  checksum, full history), which does not share these patterns.
- **Impact:** the scan is presented as the gate that keeps credentials out of a public fork, and it
  fires 24 times on the tree it ships with. A publisher must inspect each hit by hand to tell a CSS
  class name from a key, which is either wasted triage or — worse — a habit of ignoring the one check
  that would catch a real committed credential, since a genuine key would be buried in the same list.
- **Fix:** anchor the alternatives so class names cannot match
  (`(^|[^A-Za-z0-9_-])sk-[A-Za-z0-9_-]{20,}`) and require more than the bare Slack prefix
  (`xox[baprs]-[A-Za-z0-9-]{10,}`), or replace the command with a pointer to the gitleaks invocation
  CI already uses.
