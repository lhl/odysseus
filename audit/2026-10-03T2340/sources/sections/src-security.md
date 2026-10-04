# src: prompt security, secrets, URL safety, limits

## Overview

`src/api_key_manager.py`, `src/auth_helpers.py`, `src/host_docker_access.py`, `src/outbound_fetch.py`, `src/owner_identity.py`, `src/prompt_security.py`, `src/rate_limiter.py`, `src/secret_storage.py`, `src/settings_scrub.py`, `src/tls_overrides.py`, `src/upload_limits.py`, `src/url_safety.py`, `src/url_security.py`.

This section covers the guards the rest of the backend calls into: outbound URL admission,
credential encryption at rest, secret scrubbing for non-admin callers, privilege gating, upload
caps, and the prompt-injection wrapper. The neighbouring `src-agent-tools` and `routes-*` sections
cover the callers; this section covers the guards themselves, so a finding here is about whether a
guard holds, not about whether a caller invokes it.

## Coverage

**Read fully:** `src/api_key_manager.py`, `src/auth_helpers.py`, `src/host_docker_access.py`,
`src/owner_identity.py`, `src/prompt_security.py`, `src/rate_limiter.py`, `src/secret_storage.py`,
`src/settings_scrub.py`, `src/tls_overrides.py`, `src/upload_limits.py`.

**Read partially:** `src/outbound_fetch.py` — the address guard (`_PRIVATE_NETWORKS:23`,
`_is_private_address:36`) and its four call sites (`:83`, `:87`, `:106`, `:114`) were read, plus the
module head; the pinned-transport and capped-fetch implementation below line 44 was **not** read.
`src/url_safety.py` — the classifier `_classify:42`, `_SHARED_ADDRESS_SPACE_V4:34`, and the module
docstring. `src/url_security.py` — the block list and `_blocked_ip:47`.

**Not read:** the remainder of `src/outbound_fetch.py` (roughly 270 lines), and the callers covered
by the `src-agent-tools`, `routes-*`, and `services-search` sections.

One finding below rests on a measured comparison rather than a reading. It was run at this snapshot
against the three classifiers with 19 addresses, and two of the nineteen diverge:

| address | `url_safety` | `url_security` | `outbound_fetch` |
| --- | --- | --- | --- |
| `100.64.0.1` | blocked | blocked | **allowed** |
| `100.127.255.254` | blocked | blocked | **allowed** |

The other seventeen (loopback, RFC 1918, link-local, IPv6 ULA, IPv6 loopback, `0.0.0.0`) are
blocked by all three.

### [SECURITY] The web fetcher's address guard omits the carrier-grade NAT range the codebase blocks elsewhere

- **Location:** `src/outbound_fetch.py:23`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_PRIVATE_NETWORKS` lists nine ranges and omits `100.64.0.0/10`:

  ```python
  _PRIVATE_NETWORKS = (
      ipaddress.ip_network("0.0.0.0/8"),
      ipaddress.ip_network("10.0.0.0/8"),
      ipaddress.ip_network("127.0.0.0/8"),
      ipaddress.ip_network("169.254.0.0/16"),
      ipaddress.ip_network("172.16.0.0/12"),
      ipaddress.ip_network("192.168.0.0/16"),
      ipaddress.ip_network("::1/128"),
      ipaddress.ip_network("fc00::/7"),
      ipaddress.ip_network("fe80::/10"),
  )
  ```

  The fallback at `:36` cannot cover the gap, because CPython does not classify shared space as
  private — which `src/url_safety.py:28-34` states outright:

  ```python
  # RFC 6598 shared address space (carrier-grade NAT). It is not globally
  # routable, but CPython does not classify it as ``is_private`` (it is "shared",
  # not "private"), so the is_private/is_loopback checks miss it. Reject the range
  # explicitly. This closes exactly the shared-space gap without coupling strict
  # mode to ``is_global``'s broader definition, which has shifted across CPython
  # versions for other special ranges.
  _SHARED_ADDRESS_SPACE_V4 = ipaddress.ip_network("100.64.0.0/10")
  ```

  `src/url_security.py:27` blocks the same range. The fetcher is the third implementation and the
  only one that does not.

  Reachable: `services/search/content.py:29` re-exports this exact function
  (`return _outbound_fetch._is_private_address(addr)`) and `:181` defines `fetch_webpage_content`,
  whose callers include the agent's own fetch tool at `src/agent_tools/web_tools.py:83,124`,
  `src/deep_research.py:616`, and `src/chat_processor.py:466`.

- **Impact:** A URL in `100.64.0.0/10` is fetched where an RFC 1918 URL is refused. In a Tailscale
  or CGNAT deployment that range is the tailnet, so a fetch that reaches the agent's web tool can
  read whatever answers HTTP there and return the body to the model. The agent's web tool takes its
  URL from the model, whose context the project's own `THREAT_MODEL.md` treats as containing
  untrusted content, so the guard is being bypassed on the path it exists to protect. Severity is
  medium rather than high because the consequence is bounded by what answers HTTP in shared space,
  and because the repository does not show whether any deployment occupies that range.
- **Fix:** Add `ipaddress.ip_network("100.64.0.0/10")` to `_PRIVATE_NETWORKS`. The durable fix is
  the `DUP` finding below — have this module call `url_safety._classify` so the three lists cannot
  drift again.

### [ERROR-HANDLING] A privilege check skips itself when the privilege lookup raises

- **Location:** `src/auth_helpers.py:178`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `require_privilege` catches every exception from `get_privileges` and returns the
  user unchecked:

  ```python
  try:
      privs = auth_mgr.get_privileges(user) or {}
  except Exception:
      return user
  if not isinstance(privs, dict):
      privs = {}
  ```

  `core/auth.py:378-385` merges the stored privileges over the defaults:

  ```python
  stored = user.get("privileges", {})
  return {**DEFAULT_PRIVILEGES, **stored}
  ```

  A non-mapping `privileges` value raises out of that merge. Measured:

  ```
  $ python3 -c "D={'allow_shell': True}; print({**D, **[]})"
  TypeError: 'list' object is not a mapping
  ```

  So a stored `"privileges": []` — a hand-edited or corrupted `auth.json` — makes every
  `require_privilege` call for that user return early and permit the action. Note that the
  `isinstance(privs, dict)` guard on the line *after* the `except` shows the method was already
  expected to be able to return a non-dict; the `except` above it pre-empts that check.

- **Impact:** An authorization check fails open. The user is granted the privilege the check exists
  to deny. Today the trigger is a malformed `auth.json`; the blanket `except Exception` means any
  future exception added to `get_privileges` — a database read, a schema change — silently converts
  a denied action into a permitted one, with no log line.
- **Fix:** Drop the `except Exception` so the failure surfaces as a 500, or catch narrowly and
  raise `HTTPException(403)`. If the lookup must degrade, log at `error` and deny.
- **Re-review (2026-10-04):** lowered from medium. `AuthManager.set_privileges` (`core/auth.py:387-401`) is the only writer of
  the field and always stores the dict returned by `get_privileges`, and a non-object request body
  raises at `privileges.items()` before anything is stored. The trigger is therefore a hand-edited
  or corrupted `auth.json`: one more mistake has to happen before the check fails open.


### [RACE] Fernet keys are generated without a lock, so concurrent first use discards a key

- **Location:** `src/secret_storage.py:37`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_load_or_create_key` checks for the key file, then generates and writes it, with no
  lock and no exclusive-create:

  ```python
  def _load_or_create_key() -> bytes:
      if _KEY_PATH.exists():
          return _KEY_PATH.read_bytes()
      _KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
      key = Fernet.generate_key()
      _KEY_PATH.write_bytes(key)
      safe_chmod(_KEY_PATH, 0o600)
  ```

  `_get_fernet` guards only the module global (`if _fernet is None`), which does not cover the
  file, and `_load_or_create_key` performs file I/O that releases the GIL, so two callers can be
  inside it at once. Measured with eight concurrent callers on a fresh path:

  ```
  $ venv/bin/python -c "<8 threads, barrier-synchronised, on an empty key path>"
  concurrent callers      : 8
  distinct keys returned  : 2
  returned the on-disk key: 6 of 8
  ```

  Two of the eight callers walked away holding a key that was no longer on disk. `src/api_key_manager.py:17`
  has the same shape in `get_or_create_key`, and it is called on *every* encrypt and decrypt
  (`encrypt_api_key` and `decrypt_api_key` each call it), so the window is re-entered constantly
  rather than once at startup.

- **Impact:** Data encrypted with the discarded key is unrecoverable. `secret_storage` backs the
  IMAP/SMTP passwords and OAuth tokens (`core/database.py:151`, `:422`, `:2330-2389`), and
  `api_key_manager` backs every stored provider credential; `decrypt` returns `""` on failure by
  design, so the loss appears as an account silently reverting to "unconfigured". Two concurrent
  requests during a fresh install are enough. The first-use race is the reachable one — after the
  file exists, both paths read it.
- **Fix:** Serialise generation behind a module lock and create the file exclusively, retrying the
  read on `FileExistsError`:

  ```python
  try:
      fd = os.open(_KEY_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
  except FileExistsError:
      return _KEY_PATH.read_bytes()
  ```

  That also closes the permission window in which the key exists with the process umask before
  `safe_chmod` runs — the same window `src/api_key_manager.py:21-24` already acknowledges for
  pre-existing files.
- **Re-review (2026-10-04):** lowered from medium. The window is one check-then-write per install: it exists only until
  `data/.app_key` is first created, and `_get_fernet` caches the result for the life of the
  process. The measurement above used eight barrier-synchronised threads; no unsynchronised run was
  made, and this pass did not find a shipped flow that issues two first-ever encrypts together. The
  consequence is unchanged and is worse than one lost secret when the losing thread assigns
  `_fernet` last: the process then encrypts with a key that is not on disk until it restarts. The
  `api_key_manager` copy is not reachable in production, because that store has no writer (see
  the `initialize_managers` finding in `src-platform`).


### [DUP] Three private-address classifiers disagree, and only the strictest is tested

- **Location:** `src/outbound_fetch.py:36`
- **Severity:** low
- **Disposition:** next
- **Evidence:** Three modules independently decide whether an address is safe to contact:

  | module | function | mechanism |
  | --- | --- | --- |
  | `src/url_safety.py:42` | `_classify` | explicit range list, plus `_SHARED_ADDRESS_SPACE_V4:54` |
  | `src/url_security.py:47` | `_blocked_ip` | explicit range list, includes `100.64.0.0/10:27` |
  | `src/outbound_fetch.py:36` | `_is_private_address` | nine ranges, then CPython's `is_private`/`is_reserved` |

  Measured over 19 addresses, two diverge (the table under Coverage). `outbound_fetch` is the
  permissive outlier, and it is the one on the web-fetch path.

- **Impact:** This is the mechanism behind the `SECURITY` finding above: a policy expressed three
  times drifts, and the drift is invisible because no test compares the three. Each list is
  individually reasonable, so a reader auditing one of them concludes the range is covered.
- **Fix:** Keep one list. Have `outbound_fetch._is_private_address` delegate to
  `url_safety._classify`, and add a test that runs a shared address corpus through all three so a
  future edit to any one of them fails the suite.
- **Re-review (2026-10-04):** lowered from medium. The one divergence with a consequence is the carrier-grade NAT range, and
  that is already counted as the `SECURITY` finding above. What remains here is the duplication,
  which is a hazard for the next edit and not a second defect.


### [UNDOCUMENTED] Five environment variables gate one SSRF policy and none appears in `.env.example`

- **Location:** `src/url_safety.py:17`
- **Severity:** low
- **Disposition:** next
- **Evidence:** One `block_private` parameter is driven by five different variables, all defaulting
  to off:

  | variable | call site | documented in |
  | --- | --- | --- |
  | `EMBEDDING_BLOCK_PRIVATE_IPS` | `routes/embedding_routes.py:269` | the `url_safety` docstring only |
  | `IMAGE_BLOCK_PRIVATE_IPS` | `routes/gallery/gallery_routes.py:337,1274,1538`, `src/ai_interaction.py:1151,1433` | nowhere |
  | `CARDDAV_BLOCK_PRIVATE_IPS` | `routes/contacts/contacts_routes.py:70` | nowhere |
  | `REMINDER_WEBHOOK_BLOCK_PRIVATE_IPS` | `routes/note/note_routes.py:454,495` | `specs/calendar-tasks-notes.md:106` |
  | `INTEGRATION_API_BLOCK_PRIVATE_IPS` | `src/integrations.py:563` | `specs/auth-security.md:133`, `specs/integrations.md:92` |

  ```
  $ for v in EMBEDDING_ CARDDAV_ IMAGE_ REMINDER_WEBHOOK_ INTEGRATION_API_; do
  >   grep -c "${v}BLOCK_PRIVATE_IPS" .env.example; done
  0
  0
  0
  0
  0
  ```

  The `url_safety` docstring names one variable as the knob for the whole policy:

  ```
  For exposed multi-tenant deployments, set ``EMBEDDING_BLOCK_PRIVATE_IPS=true`` to
  ```

  That variable governs only the embedding route. `CARDDAV_BLOCK_PRIVATE_IPS` and
  `IMAGE_BLOCK_PRIVATE_IPS` appear nowhere outside their own call sites.

- **Impact:** An operator hardening a deployment from `.env.example` — the file the project
  presents as the configuration surface — cannot see any of these switches, and the docstring
  points at one that covers a fraction of the paths. The default for all five is `false`, so the
  LAN-capable behaviour is what a deployment gets unless the operator reads the source. The
  gallery and embedding paths are the exposed ones, since they fetch user-supplied URLs.
- **Fix:** Add all five to `.env.example` with their defaults and a one-line explanation, and
  correct the `url_safety` docstring to name all five or to describe the policy without singling
  out one variable.
- **Re-review (2026-10-04):** lowered from medium. Every switch does what its call site says, the off default is the
  documented local-first design (`src/url_safety.py:7-10`), and two of the five are documented in
  `specs/`. The defect is the missing `.env.example` entries and one docstring sentence that
  overstates what `EMBEDDING_BLOCK_PRIVATE_IPS` covers.


### [SECURITY] Secret scrubbing stops masking when a secret-shaped key holds a container

- **Location:** `src/settings_scrub.py:48`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `_scrub_value` tests the secret-shaped name only against the key at the level it is
  visiting. When a secret-shaped key holds a dict, the value fails the `isinstance(v, str)` test and
  the function recurses with the *parent* name, which the recursive call then ignores:

  ```python
  if isinstance(value, dict):
      return {
          k: ("" if (is_secret_key(k) and isinstance(v, str) and v)
              else _scrub_value(k, v))
          for k, v in value.items()
      }
  ```

  Measured:

  ```
  documented case   : {'email_account': {'smtp_password': ''}}
  nested dict value : {'smtp_password': {'nested': 'real-secret-2'}}
  ```

  The first line is the case the docstring describes and it works. In the second, the secret-shaped
  key `smtp_password` is dropped on the way down and its contents are returned in the clear.

- **Impact:** `/api/auth/settings` is auth-exempt and serves non-admin and unauthenticated callers
  (`src/settings_scrub.py` docstring), so this is a disclosure path. It is `low` and not higher
  because the trigger is a shape — a secret stored as a dict under a secret-named key — and I did
  not find that shape in the settings the app builds today; the shapes I checked nest the other way
  (`email_account` → `smtp_password`, where the inner key carries the secret-shaped name and is
  masked correctly). It is a live hazard because the recursion looks correct on inspection and the
  next nested credential silently defeats it.
- **Fix:** Carry the secret-shaped decision down instead of re-testing at each level — blank the
  whole subtree when the key is secret-shaped and the value is not a plain string, or pass the
  parent name into the recursive call and treat it as secret-shaped for all descendants.

### [HARDCODE] The API-key store builds its paths instead of using `src/constants.py`

- **Location:** `src/api_key_manager.py:14`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** Both paths are assembled locally from the injected `data_dir`:

  ```python
  self.api_keys_file = os.path.join(data_dir, "api_keys.json")
  self.key_file = os.path.join(data_dir, ".key")
  ```

  `CONTRIBUTING.md:101` names this exact pattern as the thing not to do:

  > Every persisted file and directory has a named constant in `src/constants.py` ... Import and
  > use that named constant; do not re-derive the path locally with `os.path.join(DATA_DIR, "x.json")`
  > or `DATA_DIR / "x.json"`.

  `src/constants.py` has `APP_KEY_FILE` for the sibling store at `src/secret_storage.py:33` and no
  constant for either file here.

- **Impact:** Low on its own — the paths work. The reason it is recorded is that `DATA_DIR` is the
  single reader of `ODYSSEUS_DATA_DIR`, and these two literals are the only persisted paths in the
  section that bypass it, so a deployment that relocates its data directory has two files whose
  location is decided by whatever `data_dir` the caller passes rather than by the constant every
  other store uses. It also puts the API-key store's key file (`.key`) and the shared secret store's
  key file (`.app_key`) on separately-derived paths, which is what makes the two-key situation in
  the `RACE` finding above hard to see.
- **Fix:** Add `API_KEYS_FILE` and `API_KEY_FILE` to `src/constants.py` and import them, matching
  `APP_KEY_FILE`.
