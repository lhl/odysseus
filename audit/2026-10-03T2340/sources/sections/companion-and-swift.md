# Companion apps and Swift clients

## Overview

`companion/` is the LAN bridge a mobile client uses to discover and pair with a running instance:
three read endpoints (`/api/companion/ping`, `/info`, `/models`) plus the admin pairing page and
mint (`GET`/`POST /api/companion/pair`). `integrations/claude/` and `integrations/codex/` are the
two agent bundles shipped as downloadable zips — a `SKILL.md` that tells the agent what it may
call, a README with the setup flow, and a byte-identical `odysseus_api.py` helper that runs those
calls from a terminal.

`swift/odysseus-mlx-image-bridge/` builds two one-shot CLI executables
(`odysseus-mlx-colorize`, `odysseus-mlx-inpaint`) that `scripts/mlx_image_server.py` invokes with
argv for the MLX colorize and inpaint endpoints; neither executable opens a socket, binds an
interface, or authenticates a caller — they read `--image`/`--mask`, load weights from `--model`,
write `--output`, and exit, and the shipped caller passes fixed paths inside a temp dir
(`scripts/mlx_image_server.py:205-260`).

The boundary: the request-authenticating middleware, `require_admin` and the API-token cache are
`core-auth-session`; the `ApiToken` row is `core-data-platform`; the `/api/codex/*` server surface
the integration clients call, and the email-send defect they inherit, are `routes-rest-agent-admin`;
the Python image server that drives the Swift binaries is `scripts`; the pairing spec is `specs`.

The pairing facts this pass established. Minting requires an admin **cookie session**
(`companion/routes.py:202`; a bearer caller is the `api` pseudo-user, and `is_admin("api")` is
False — `api` is a reserved username, `src/owner_identity.py:13-14`). The mint is a POST, so the
`SameSite=Lax` session cookie (`routes/auth_routes.py:188`) is not sent cross-site; `GET /pair`
only renders the form. The credential is a normal `chat`-scoped `ApiToken`
(`companion/pairing.py:191-204`): bcrypt hash at rest, raw value shown once, cache invalidated so it
works on the next request. It is **not** single-use, not bound to the requesting device, and has no
expiry — it stays valid until an admin deletes it in Settings.

A paired client reaches the chat/session surfaces as a delegated credential: agent tools are capped
at the non-admin policy (`src/tool_security.py:274-284`), tool approvals are refused
(`routes/chat_routes.py:100-114`), and the scope-aware `/api/codex/*` routes reject a chat-only
token. The companion's own read endpoints
hold the line the second test suite names: `/models` scopes to the token's real owner plus legacy
null-owner rows in SQL and again in Python (`companion/routes.py:120-160`) and omits
`api_key`/`headers`/`base_url`. That is stricter than the sibling `/api/models`, whose admin-token
path returns the global endpoint pool (`routes/model_routes.py:1645-1660`, owned by `routes-models`).

## Coverage

**Read fully:** all 14 assigned files (1,570 lines).

| File | Lines |
| --- | ---: |
| `companion/routes.py` | 265 |
| `companion/pairing.py` | 227 |
| `integrations/claude/skills/odysseus/scripts/odysseus_api.py` | 218 |
| `integrations/codex/scripts/odysseus_api.py` | 218 |
| `integrations/claude/skills/odysseus/SKILL.md` | 154 |
| `integrations/codex/skills/odysseus/SKILL.md` | 142 |
| `Sources/OdysseusMLXInpaint/main.swift` | 88 |
| `Sources/OdysseusMLXColorize/main.swift` | 80 |
| `integrations/codex/README.md` | 51 |
| `integrations/claude/README.md` | 36 |
| `swift/odysseus-mlx-image-bridge/Package.swift` | 30 |
| `companion/README.md` | 28 |
| `integrations/codex/.codex-plugin/plugin.json` | 22 |
| `companion/__init__.py` | 11 |

Both companion test suites were read in full.

**Read partially:** the boundary code the findings rest on.

- `core/middleware.py` at `require_admin` (`:57-82`)
- `app.py` at the auth-exempt lists (`:263-296`), the bearer branch and token cache (`:300-335`,
  `:418-466`), the setup-required 401 (`:407-414`), middleware installation (`:485-488`) and
  companion router registration (`:887-888`)
- `core/database.py` at `ApiToken` (`:634-645`)
- `core/auth.py` at `normalize_known_username` (`:65-70`) and `is_admin` (`:369-370`)
- `routes/api_token_routes.py` in full (209 lines, for the "mirrors" claim and the scope vocabulary)
- `routes/auth_routes.py` at the session cookie (`:183-194`)
- `routes/codex_routes.py` at the scope constants and `_scope_owner` (`:27-110`), `plugin.zip`
  (`:218-233`, `:891-908`) and the email send/draft handlers (`:340-387`)
- `routes/email_routes.py` at `send_email` (`:4519-4720`)
- `src/auth_helpers.py` in full (199 lines)
- `src/tool_security.py` at `delegated_credential_blocked_tools` (`:274-284`)
- `routes/chat_routes.py` at the delegated-credential gates (`:100-114`, `:1479-1486`) and
  `routes/session_routes.py` (`:141`, `:180`, `:947`)
- `scripts/mlx_image_server.py` at the bridge invocations (`:205-260`, `:320-450`)
- `specs/integrations.md` at the companion and token sections (`:127-140`)
- the two companion suites' assertions

**Not read:**

- the rest of these files:
  - `app.py`, `core/middleware.py` and `core/database.py`
  - `routes/codex_routes.py` and `routes/email_routes.py`
  - `scripts/mlx_image_server.py`
- the mobile client itself (not in this repository)
- `integrations/*` beyond the 11 assigned files
- the vendored Swift dependencies `mlx-lama-swift` and `mlx-ddcolor-swift`
- every other section's paths

Line numbers are the working tree at `2992bf6d368a` (clean apart from this run's untracked `audit/`
directory).

**Checks run:** the two suites covering this surface —
`venv/bin/python -m pytest -q tests/test_companion_pairing.py tests/test_companion_readonly.py` →
**104 passed**; the companion's `COMPANION_BASE_URL` plumbing is pinned by
`tests/test_docker_devops_hardening.py::test_compose_files_forward_companion_base_url` (**1 passed**;
105 with the two suites run together). Four probes under `/tmp`, each quoted where it is used: the
integration helper run
against a throwaway HTTP server (exit status on a 200 `success:false` body, and the `..` path
guard), a minimal uvicorn/FastAPI app to establish what Starlette routes for a dot-segment path,
`md5sum`/`diff` on the two client scripts, and a `grep` for `find_admin_user` callers. The Swift
executables were not built or run (no macOS/Swift toolchain here); their interface was established
by reading and by the Python caller.

### [DOC-DRIFT] The pairing credential is described as one-time but is a permanent, replayable bearer token

- **Location:** `companion/routes.py:187` (also `:259`), `companion/README.md:12`,
  `companion/__init__.py:5`
- **Severity:** low
- **Disposition:** next
- **Evidence:** all three user-facing descriptions call the pairing code single-use:

  ```
  companion/routes.py:187  <p>Generate a one-time pairing code (a chat-scoped API token) for a LAN client.</p>
  companion/README.md:12   | POST | `/api/companion/pair` | **admin cookie** | mint a one-time pairing token ...
  companion/__init__.py:5  ... (/api/companion/pair) that mints a one-time chat-scoped token on POST.
  ```

  The mint produces an ordinary long-lived token, and nothing consumes it on use:

  ```python
  # companion/pairing.py:191-204
  raw_token = "ody_" + secrets.token_urlsafe(32)
  token_hash = bcrypt.hashpw(raw_token.encode(), bcrypt.gensalt()).decode()
  ...
  db.add(ApiToken(id=token_id, owner=owner, name=name, token_hash=token_hash,
                  token_prefix=raw_token[:8], scopes=COMPANION_SCOPE, is_active=True))
  ```

  `ApiToken` has no expiry column and no consumption flag. Its columns are id, owner, name,
  token_hash, token_prefix, scopes, is_active and last_used_at (`core/database.py:638-645`).
  The auth cache loads every active row (`app.py:321`), and the middleware's only write on a
  successful bearer request is `last_used_at` (`app.py:441-456`). The spec is accurate and the code
  matches it: `specs/integrations.md:136` says the POST "mints a normal chat-scoped API token".
  Nothing binds the credential to the requesting device either: `pairing_payload` carries only
  `{"v", "host", "port", "token"}` (`companion/pairing.py:208-210`), so any client holding the
  payload can use it concurrently.
- **Impact:** an admin who pairs a phone reads "one-time" and may assume the code is spent after
  the first device uses it, or that a screenshot/QR leak has a bounded window. It does not: the
  value is a bearer credential valid until an admin revokes it under Settings → API tokens, as the
  same page's warning at `:259` does say. The misdescription is what could lead an admin to leave a
  leaked credential live.
- **Fix:** reword the three descriptions to "shown once; valid until revoked" (or "one-time
  display"), or give the mint an expiry / consume-on-first-use if single use is the intent — the
  latter needs a new `ApiToken` column and a check in the middleware.

### [BUG] In auth-disabled mode the pairing route mints a token that can never authenticate

- **Location:** `companion/routes.py:202-209` (with `companion/pairing.py:196-204`,
  `app.py:321-330`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `require_admin` returns early when auth is explicitly off (`core/middleware.py:76`),
  and with `AUTH_ENABLED=false` no middleware is installed at all (`app.py:485-488`), so nothing
  sets `request.state.current_user`:

  ```python
  # companion/routes.py:202-209
  require_admin(request)
  ...
  owner = get_current_user(request)
  invalidate = getattr(request.app.state, "invalidate_token_cache", None)
  token_id, raw_token = mint_pairing_token(owner, invalidate)
  ```

  `get_current_user` is `getattr(request.state, 'current_user', None)` (`src/auth_helpers.py:10-12`),
  so `owner` is `None` and the row is written with `owner=None` (`companion/pairing.py:196-204`).
  The auth cache drops every active row whose owner does not resolve to a known user:

  ```python
  # app.py:323-330
  owner_key = normalize_known_username(auth_manager.users, getattr(r, "owner", None))
  if not owner_key:
      logger.warning("Ignoring active API token '%s' for unknown auth user '%s'", ...)
      continue
  ```

  `normalize_known_username` returns `None` for a `None` username (`core/auth.py:65-70`), so the
  token is never admitted to `_token_cache`, and `_token_cache` is the only place the middleware
  looks. `src-agent-tools` already established this mechanism for the agent's token tool
  (`src-agent-tools.md`, the ownerless-token finding); this is the second construction site it
  reaches. The pairing page still promises "This grants chat access to your Odysseus"
  (`companion/routes.py:259`), and the spec treats auth-disabled mode as supported for this feature
  (`specs/integrations.md:140`).
- **Impact:** on an instance running with `AUTH_ENABLED=false`, any LAN caller can open the pairing
  page and is handed a credential that cannot authenticate — while auth stays off it is simply
  unused, and after the operator turns auth on the cache ignores it. The user-visible result is a
  pairing flow that reports success and produces a dead token.
- **Fix:** refuse the mint (or return an explicit warning instead of a token) when `auth_disabled()`
  is true and no user identity can be resolved, since there is no per-device credential to issue in
  that mode.

### [ERROR-HANDLING] The integration helper exits 0 for API responses that report failure

- **Location:** `integrations/codex/scripts/odysseus_api.py:203-207` and the identical
  `integrations/claude/skills/odysseus/scripts/odysseus_api.py:203-207`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the helper treats any HTTP 2xx as success and never inspects the body:

  ```python
  # :203-207
  req = urllib.request.Request(base_url + path, data=data, headers=headers, method=method)
  try:
      with urllib.request.urlopen(req, timeout=20) as resp:
          print(resp.read().decode("utf-8"))
          return 0
  ```

  The send endpoint it documents can return HTTP 200 with `success: false`:
  `routes/email_routes.py:4527-4531` returns
  `{"success": False, "error": "No SMTP-capable email account configured"}` when no sendable
  account resolves, and `routes/codex_routes.py:387` passes that dict straight through. Measured
  with the helper against a server returning that body:

  ```
  --- A documented send call, endpoint returns 200 with success:false
  server saw: [('POST', '/api/codex/emails/send')]
  stdout: {"success": false, "error": "No SMTP-capable email account configured"}
  exit: 0
  ```

  The queued path is worse in the same way: `routes/email_routes.py:4714-4720` returns
  `{"success": true, "queued": true, ...}` for the documented call, and the helper prints it and
  exits 0. The non-delivery behind that response is `routes-rest-agent-admin`'s finding (the
  discarded `BackgroundTasks` at `routes/codex_routes.py:387`); the residual defect here is that
  the client's own success signal is the HTTP status alone, so an agent that checks the exit code —
  the normal way a CLI is consumed — reports a failed action as done. The skills document the send
  body without `wait_for_delivery` (`integrations/codex/skills/odysseus/SKILL.md:107` and its
  Claude twin), so the documented call always takes the queued branch.
- **Impact:** an agent or script that chains on the exit status treats a rejected send (and any
  other 200-with-`success:false` response) as successful; only a human reading stdout sees the
  error. Combined with the `routes-rest-agent-admin` non-delivery bug, "email sent" reaches the
  user with no mail on the wire.
- **Fix:** parse the response body and return non-zero when it is a JSON object with
  `success is False` (falling back to 0 for non-JSON bodies); and document
  `wait_for_delivery: true` in the two skills' send section so the helper surfaces the real result.

### [FOOTGUN] The helper's `/api/codex/` path guard is bypassable with `..` segments

- **Location:** `integrations/codex/scripts/odysseus_api.py:178-182` and the identical
  `integrations/claude/skills/odysseus/scripts/odysseus_api.py:178-182`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the guard is a string prefix test on the caller-supplied path:

  ```python
  # :178-182
  if not path.startswith("/"):
      path = "/" + path
  if not path.startswith("/api/codex/"):
      print("refusing non-/api/codex path; use scoped Odysseus integration endpoints only", file=sys.stderr)
      return 2
  ```

  A dot-segment path passes it and is sent verbatim; the probe server saw the raw path and the
  helper exited 0:

  ```
  --- B dot-segment guard bypass
  argv: ['GET', '/api/codex/../api/prefs']
  server saw: [('GET', '/api/codex/../api/prefs')]
  exit: 0
  ```

  What the server does with that path was measured separately, with a minimal uvicorn/FastAPI app
  whose only exact route is `/api/prefs` plus a catch-all:

  ```
  /api/prefs -> {"route":"prefs"}
  /api/codex/../api/prefs -> {"route":"catchall","rest":"api/codex/../api/prefs"}
  /api/codex/%2e%2e/api/prefs -> {"route":"catchall","rest":"api/codex/../api/prefs"}
  ```

  So against a stock uvicorn/Starlette deployment the raw path matches no route and 404s; the guard
  is defeated at the client layer, but only a fronting proxy that normalizes dot segments before
  forwarding would resolve it to the non-codex route. The bypass matters because the skills present
  the `/api/codex/*` rule as the data-access boundary ("All Odysseus data access MUST go through
  the scoped HTTP API under `/api/codex/*`", `integrations/codex/skills/odysseus/SKILL.md:30`), and
  `routes-rest-media-files` found that several non-codex stores accept a bearer token of any scope.
- **Impact:** an agent steered toward a non-codex path can walk past the helper's refusal (and the
  scope boundary the skill describes) on deployments whose proxy normalizes the URI. The server's
  own scope checks still apply to `/api/codex/*`, and the unscoped routes are reported separately
  by `routes-rest-media-files`.
- **Fix:** normalize before the check (`path = posixpath.normpath(path)`) and reject any path whose
  normalized form is not under `/api/codex/`, or reject segments equal to `..`.

### [DEPENDENCY] The Swift bridge pins both upstream packages to a moving branch

- **Location:** `swift/odysseus-mlx-image-bridge/Package.swift:12-13`
- **Severity:** low
- **Disposition:** next
- **Evidence:** both dependencies track `main`, and no lockfile is committed:

  ```swift
  dependencies: [
      .package(url: "https://github.com/xocialize/mlx-lama-swift", branch: "main"),
      .package(url: "https://github.com/xocialize/mlx-ddcolor-swift", branch: "main"),
  ],
  ```

  `find swift -name Package.resolved` returns nothing, so each `swift build` resolves whatever
  `main` is at build time. The binaries are then put on PATH and invoked by
  `scripts/mlx_image_server.py:205-260`, which the operator runs on an Apple Silicon host
  (`routes/shell_routes.py:1354` tells them to "build ... and put odysseus-mlx-inpaint or
  mlx-lama-serve on PATH").
- **Impact:** the image bridge an operator builds is not reproducible; an upstream commit, force
  push, or compromised maintainer account silently changes the code compiled into a binary that
  runs with the operator's privileges and loads model weights. A regression cannot be attributed to
  a known revision.
- **Fix:** pin each dependency to a release tag or commit, or commit a `Package.resolved` and build
  with automatic resolution disabled.

### [DUP] The Claude and Codex bundles ship the same client script twice

- **Location:** `integrations/claude/skills/odysseus/scripts/odysseus_api.py:1` and
  `integrations/codex/scripts/odysseus_api.py:1`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the two files are byte-identical, including the docstring:

  ```
  $ md5sum integrations/codex/scripts/odysseus_api.py integrations/claude/skills/odysseus/scripts/odysseus_api.py
  b2c80e216f9fbc7bab935df7cf0dc006  integrations/codex/scripts/odysseus_api.py
  b2c80e216f9fbc7bab935df7cf0dc006  integrations/claude/skills/odysseus/scripts/odysseus_api.py
  $ diff -u integrations/codex/scripts/odysseus_api.py integrations/claude/skills/odysseus/scripts/odysseus_api.py && echo IDENTICAL
  IDENTICAL
  ```

  The Claude copy's first line still reads `"""Small Odysseus scoped API helper for Codex terminal
  sessions."""` (`:2`). The two skills were maintained separately (their wording differs: "Claude
  Agent" vs "Codex Agent", different install paths), but the scripts were copied verbatim. The
  bundles are delivered by two independent routes (`routes/codex_routes.py:218-233` zips
  `integrations/codex`, `:891-908` zips `integrations/claude/skills`), so nothing keeps the copies
  in sync.
- **Impact:** every script fix — including the two findings above — has to be applied twice, and
  the Claude bundle's helper misidentifies itself. A fix landed in one copy silently leaves the
  other broken.
- **Fix:** keep one script as the source (for example under `integrations/common/`) and have the
  packaging step place it in both zips, or generate the Claude copy from the Codex one in the
  `plugin.zip` handler.

### [DEAD-CODE] `find_admin_user` has no caller outside its own test

- **Location:** `companion/pairing.py:162-179`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** a tree-wide grep finds the definition and one test, and nothing that calls it in
  production:

  ```
  $ grep -rn "find_admin_user" . --include=*.py --exclude-dir=audit --exclude-dir=.git
  ./companion/pairing.py:162:def find_admin_user() -> str | None:
  ./tests/test_companion_pairing.py:211:def test_find_admin_user_ignores_invalid_auth_shape(tmp_path, monkeypatch, payload):
  ./tests/test_companion_pairing.py:214:    # find_admin_user reads the import-time AUTH_FILE constant, so redirect that
  ./tests/test_companion_pairing.py:218:    assert P.find_admin_user() is None
  ```

  The pairing POST resolves its owner through `get_current_user(request)`
  (`companion/routes.py:207`), not this helper, so the function is unreachable. It reads
  `data/auth.json` directly (`companion/pairing.py:165-168`) rather than consulting
  `AuthManager.users`, the map the middleware and the token cache actually use.
- **Impact:** dead code that duplicates the auth store's schema assumption; if it is ever wired
  into a route it can disagree with the live in-memory user map (for example after a rename or a
  reserved-username migration, `core/auth.py:165-170`). It also keeps a direct file read of the
  credential store in the companion package.
- **Fix:** delete the function and its test, or route it through `AuthManager` if a caller is
  actually planned.

### [DUP] The two Swift executables duplicate their argument and image I/O helpers

- **Location:** `swift/odysseus-mlx-image-bridge/Sources/OdysseusMLXColorize/main.swift:15-18`,
  `:33-40`, `:42-49`, `:51-63` and the same helpers at
  `swift/odysseus-mlx-image-bridge/Sources/OdysseusMLXInpaint/main.swift:17-20`, `:36-43`,
  `:45-52`, `:54-66`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `diff -u` between the two files shows only imports, the `Args` fields,
  `parseArgs` and the main body differ; the `value(after:)`, `decodeCGImage`, `encodePNG` and
  `BridgeError` definitions are byte-identical (no diff hunk touches them). The two targets are in
  one package with no shared target:

  ```swift
  // Package.swift:15-29 — two executableTargets, no library target
  .executableTarget(name: "OdysseusMLXInpaint", dependencies: [...]),
  .executableTarget(name: "OdysseusMLXColorize", dependencies: [...]),
  ```
- **Impact:** an I/O fix (for example handling a `CGImageDestination` failure differently, or
  bounds-checking arguments) must be made in two files that have already drifted once; the next
  executable added to the package copies the pattern a third time.
- **Fix:** move `value`, `decodeCGImage`, `encodePNG` and `BridgeError` into a shared library target
  that both executables import.
