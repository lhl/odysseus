# Bundled MCP servers

## Overview

The four stdio servers the application registers for itself: `mcp_servers/email_server.py`
(IMAP/SMTP tools over the user's mailboxes), `mcp_servers/image_gen_server.py` (image generation
plus the gallery row), `mcp_servers/memory_server.py` (the JSON memory store) and
`mcp_servers/rag_server.py` (the personal-document index). `mcp_servers/__init__.py` is empty. These
are the only part of the MCP surface whose code the project owns: the manager that spawns them, the
three transports, the tool inventory and the call path are `src-mcp`; the registration that hands
each one a command, an argument list and an environment at startup is `src/builtin_mcp.py`, read here
as context. The same data is reachable through the route layer, and that is where the comparisons
below come from: `routes-email` and `routes-rest-memory-personal-research` own the handlers whose
guards these servers either copy or drop, `src-memory-rag` owns the stores, and `core-data-platform`
owns the `EmailAccount` and `GalleryImage` rows. Findings in those files are cross-referenced, not
restated.

The question this section answers is who a server thinks is asking. The transport carries no
identity — the parent process is the only client and the stdio protocol says nothing about which
application user made the call — so each server has to be told, and the four do not agree.
`email_server` takes an owner from a hidden `_odysseus_owner` argument that the caller injects
(`src/tool_execution.py:1316-1319`, overwriting anything the model sent), `memory_server` takes one
from an environment variable nothing in the tree sets, and `image_gen_server` and `rag_server` take
none at all: they read and write ownerless rows in stores whose readers are owner-filtered.

## Coverage

**Read fully:** all five assigned files (3,541 lines): `mcp_servers/email_server.py` (2,912),
`mcp_servers/memory_server.py` (285), `mcp_servers/image_gen_server.py` (184),
`mcp_servers/rag_server.py` (160) and `mcp_servers/__init__.py` (empty, 0 bytes).

**Read partially:** the boundary code the findings rest on — `src/builtin_mcp.py` in full (the
`_BUILTIN_SERVERS` table, `builtin_python_env` and both `connect_server` call sites);
`src/tool_execution.py` at the dispatch (`:1112-1122`), the legacy MCP map (`:562-572`), the owner
injection (`:1301-1304`, `:1316-1319`), the `generate_image` promotion (`:699-728`), the dead-map
comment (`:644-651`) and the agent's readable data roots (`:175-215`); `src/mcp_manager.py` at
`is_builtin` (`:641-648`), `get_all_openai_schemas` (`:570-600`) and
`get_tool_descriptions_for_prompt` (`:661-706`); `src/tool_index.py` at `ALWAYS_AVAILABLE` (`:35-45`),
`BUILTIN_TOOL_DESCRIPTIONS` (`:69-143`) and `index_mcp_tools` (`:224-252`); `src/agent_loop.py` at
`_DOMAIN_TOOL_MAP` (`:528-540`), `_load_mcp_disabled_map` (`:287-301`), the email prompt text
(`:1917-1918`) and the tool-selection block (`:3880-3950`); `src/tool_parsing.py` at the fence regex
(`:33-38`) and the `mcp__` branch (`:639-642`); `routes/personal_routes.py` at
`_resolve_allowed_personal_dir` (`:165-182`) and both directory handlers (`:200-297`);
`routes/email_helpers.py` at `attachment_extract_dir` (`:685-696`) and the owner dependencies
(`:440-486`); `routes/gallery/gallery_helpers.py` at `_owner_filter` (`:125-136`) and
`_image_to_dict` (`:96-121`); `app.py` at the generated-image handler (`:513-553`); the native
counterparts `src/ai_interaction.py` (`do_manage_memory`, `do_manage_rag`, `do_generate_image` and
its gallery writers), `src/memory.py` (`load_all`, `load_all_for_update`, `add_entry`, `save`) and
`src/personal_docs.py` (`add_directory`, `remove_directory`); `src/session_image_cleanup.py` at
`session_image_refs` (`:46-52`); the MCP SDK's `Server.call_tool` decorator
(`venv/lib/python3.12/site-packages/mcp/server/lowlevel/server.py:498-600`) and the stdlib's
`imaplib.IMAP4._command`, neither of which is part of the target tree.

**Not read:** the rest of `routes/email_routes.py` (4,600+ lines), `routes/gallery/gallery_routes.py`
and the other `routes-*` paths; `src/ai_interaction.py`, `src/agent_loop.py` and
`src/tool_execution.py` outside the regions named above; the other sections' paths.

**Checks run:** throwaway probe programs under `/tmp/mcpsrv/` (eight distinct programs —
`probe_gallery.py` was rewritten as `probe_gallery2.py`, and the attachment probe is three files, one
per input shape): a stubbed RAG manager recording what `manage_rag` passes down; a fake IMAP
connection serving one attachment, run three times with different `folder`/`uid`; the real
`routes.gallery_helpers._owner_filter` over a real `GalleryImage` table in an in-memory SQLite
database; the email server's `_load_config` twice around a database update; `builtin_python_env` plus
the memory server's `_scope_entries`; and `parse_tool_blocks` on three shapes of an MCP call. Each
probe's output is quoted in the finding it settles. The 26 suites
matching this surface — the 17 files from `ls tests | grep -iE 'mcp'` plus the 9 further files that
reference `mcp_servers/` — were run: **233 passed** in 5.47s.

Malformed arguments are worth one line because the brief asks: a bad shape does **not** kill the
server. The SDK validates the arguments against the tool's declared `inputSchema` before the function
runs and returns `Input validation error: …` as a tool error, and it wraps the call itself in
`except Exception as e: return self._make_error_result(str(e))`
(`mcp/server/lowlevel/server.py:534-538`, `:590-591`), so a raise inside a server body becomes an
`isError` result rather than a dead session. Nothing below therefore reports an argument shape as a
crash; the type guards the servers do carry are for callers that reach `call_tool` directly, as
`tests/test_rag_server_directory_nonstring.py` does.

What the suites already pin, and what they leave open: `tests/test_mcp_memory_owner_scope.py` pins
the memory server's three owner modes (configured owner, owner-scoped store with no owner, ownerless
store); `tests/test_imap_leak_fixes.py` pins the logout-on-failure paths of `_list_emails`,
`_read_email`, `_reply_to_email` and `_download_attachment`; `tests/test_mcp_email_decode_header_spaces.py`
pins owner-scoped draft staging for `send_email`; and `tests/test_agent_state_dir_confinement.py`
pins the **read**-side confinement roots the agent's file tools use, `MAIL_ATTACHMENTS_DIR` among
them — which is the guard the write side in the first finding below does not have. No suite pins
where `download_attachment` writes, what owner an image row gets, whether `_ACCOUNT_CACHE` is ever
invalidated, or what `manage_rag` is allowed to index.

### [SECURITY] `download_attachment` builds its target directory from unvalidated tool arguments, so the write escapes the attachment root

- **Location:** `mcp_servers/email_server.py:2077` (with `:2061-2080`, `:1188-1215`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the directory name is the two tool arguments concatenated, and nothing flattens or
  re-checks the result:

  ```python
  # mcp_servers/email_server.py:2077-2078
  target_dir = Path(MAIL_ATTACHMENTS_DIR) / f"{folder}_{uid}"
  filepath = _extract_attachment_to_disk(msg, index, target_dir)
  ```

  `folder` and `uid` come straight from the tool call (`call_tool` reads
  `arguments.get("folder", "INBOX")` and passes it through). `_extract_attachment_to_disk` then does
  `os.makedirs(target_dir, exist_ok=True)` and writes the decoded part to
  `os.path.join(target_dir, safe_name)` (`:1206-1214`); `safe_name` strips `/` from the *filename*
  but the directory is untouched. Measured with a stubbed `_imap_connect` returning one message with
  one attachment:

  ```
  $ venv/bin/python /tmp/mcpsrv/probe_attach.py     # folder="../../../../tmp/mcpsrv/escape", uid="1"
  returned: {'path': '/tmp/mcpsrv/mail-attachments/../../../../tmp/mcpsrv/escape_1/dropped.txt', ...}
  file exists at escape path: True
  wrote /tmp/mcpsrv/escape_1/dropped.txt b'PAYLOAD-BYTES'
  nothing written under MAIL_ATTACHMENTS_DIR: True

  $ venv/bin/python /tmp/mcpsrv/probe_attach2.py    # folder="INBOX", uid="../../uid-escape"
  returned: /tmp/mcpsrv/mail2/INBOX_../../uid-escape/note.txt
  resolves to: /tmp/mcpsrv/mail2/uid-escape/note.txt

  $ venv/bin/python /tmp/mcpsrv/probe_attach3.py    # folder="/tmp/mcpsrv/home/.ssh", uid="/../.ssh"
  returned  : /tmp/mcpsrv/home/.ssh_/../.ssh/authorized_keys
  realpath  : /tmp/mcpsrv/home/.ssh/authorized_keys
  wrote into the exact .ssh directory: True
  content   : b'ssh-rsa AAAA attacker key\n'
  ```

  The third run is the interesting one: an absolute `folder` discards the base (`pathlib` drops the
  left operand), and a `uid` of `/../<last segment>` cancels the `_<uid>` suffix, so the directory
  resolves to an exact path rather than a suffixed one — and the file *name* is the attachment's
  `Content-Disposition` filename, sanitized only by `re.sub(r"[^\w\s\-.]", "_", filename)`
  (`:1206`), which keeps `authorized_keys`, `.bashrc` and any other word-character name. The HTTP
  route extracts attachments through a helper that has both guards this copy lacks:

  ```python
  # routes/email_helpers.py:685-696
  key = re.sub(r"[^A-Za-z0-9._-]", "_", f"{folder}_{uid}") or "_"
  target = (ATTACHMENTS_DIR / key).resolve()
  base = ATTACHMENTS_DIR.resolve()
  if target != base and base not in target.parents:
      raise HTTPException(400, "Invalid attachment location")
  ```

  (The collision problem in that route-side helper is `routes-email.md`'s finding; the containment
  guard itself works, as its docstring's measured example shows.) `MAIL_ATTACHMENTS_DIR` is one of
  the roots the agent's own file tools are confined to (`src/tool_execution.py:175-215`), so the
  confinement the file tools enforce is not enforced here.
- **Impact:** an arbitrary-file-write primitive as the application user. Both inputs are
  model-supplied: `folder` and `uid` are ordinary strings in the tool schema, and the model is
  routinely handed untrusted text (an email body, a document) that can name them — the
  `download_attachment` description even instructs the model to fetch the attachment it is about to
  read. The bytes and the file name come from the attachment itself, so a sender who can email the
  user chooses both; only the model's compliance with an injected `folder`/`uid` stands between that
  and a file written anywhere the process can write, such as `~/.ssh/authorized_keys` when the app
  runs as that user. Without injection the tool is safe, which is what keeps this at medium rather
  than high.
- **Re-review (2026-10-05):** stands at medium. The impact says only the model's compliance stands
  between an injected `folder` or `uid` and the write. A second control exists:
  `download_attachment` carries `READ_PRIVATE` and `WRITE_WORKSPACE`
  (`src/tool_capabilities.py:194-199`), which `decision_for` blocks once untrusted content is in
  the run unless the user approves the call. Reading the email that carries the injection arms
  that gate. Whether the gate covers the MCP-qualified name of this tool was not traced.
- **Fix:** call the existing `routes.email_helpers.attachment_extract_dir` (or inline its two lines:
  flatten `f"{folder}_{uid}"` to `[A-Za-z0-9._-]`, then assert the resolved path is inside
  `MAIL_ATTACHMENTS_DIR` and return an error text otherwise). Also validate `uid` as digits where it
  is used as a UID, as the finding below asks.

### [SECURITY] `manage_rag` indexes or removes any path on the filesystem, with no confinement and no owner, unlike the admin-only route it duplicates

- **Location:** `mcp_servers/rag_server.py:110-124` (add), `:138-145` (remove)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the route that does the same thing resolves the path under `PERSONAL_DIR`, requires
  an admin, and stamps the caller as the chunk owner:

  ```python
  # routes/personal_routes.py:200-204, :217, :232
  async def add_directory_to_rag(
      request: Request,
      directory_request: DirectoryRequest,
      owner: str = Depends(require_user), _admin: None = Depends(require_admin),
  ):
      directory = _resolve_allowed_personal_dir(directory)
      ...
      result = rag.index_personal_documents(directory, owner=owner)
  ```

  `_resolve_allowed_personal_dir` realpaths the candidate, requires it to be under
  `os.path.realpath(PERSONAL_DIR)` and raises 403 otherwise (`:165-182`). The MCP copy has none of
  the three:

  ```python
  # mcp_servers/rag_server.py:110-116
  directory = os.path.abspath(os.path.expanduser(directory))
  if not os.path.isdir(directory):
      return [TextContent(type="text", text=f"Error: Directory not found: {directory}")]
  if not _rag_manager:
      return [TextContent(type="text", text="Error: RAG manager not available")]
  try:
      result = _rag_manager.index_personal_documents(directory)
  ```

  Measured with the managers replaced by recorders:

  ```
  args={'action': 'add_directory', 'directory': '/etc'}
    -> "Directory '/etc' added to RAG index (3 chunks indexed)"
    call: ('index_personal_documents', '/etc', (), {})          # no owner kwarg
    call: ('docs.add_directory', '/etc', (), {'index': False})  # no owner kwarg
  args={'action': 'add_directory', 'directory': '~/.ssh'}
    -> "Directory '/home/lhl/.ssh' added to RAG index (3 chunks indexed)"
  args={'action': 'remove_directory', 'directory': '/home/someone-else/docs'}
    -> "Directory '/home/someone-else/docs' removed from RAG index"
    call: ('docs.remove_directory', '/home/someone-else/docs', (), {})
    call: ('rag.remove_directory', '/home/someone-else/docs', (), {})
  ```

  `owner=None` is not a no-op: `VectorRAG.index_personal_documents` only writes `meta['owner']` when
  it is given one (`src/rag_vector.py:536-537`), and search filters on it
  (`where_filter = {"owner": owner} if owner else None`, `:357`), so an ownerless chunk is visible to
  every user's retrieval and the directory is recorded in the shared
  `PersonalDocsManager` tracking list (`mcp_servers/rag_server.py:124`,
  `src/personal_docs.py:276-310`). The ownerless-write failure mode is the one `services-research.md`
  reports for `services/docs/service.py:104`; the difference here is that this copy is registered at
  every startup (`src/builtin_mcp.py:72-77`, `:170-181`) and its tool is the only live
  RAG-management path — the native `do_manage_rag` has no dispatcher (`grep -rn "manage_rag"
  src/ --include=*.py` returns only `src/ai_interaction.py:529`, its definition, and a comment).

  Reachability, measured rather than assumed: `mcp__rag__manage_rag` is not advertised to the model.
  Built-in servers are skipped both in the function schemas (`src/mcp_manager.py:580-582`) and in the
  prompt block and tool index (`:679-680`, `src/tool_index.py:245`), `manage_rag` has no entry in
  `BUILTIN_TOOL_DESCRIPTIONS` and no keyword hint, and it is in neither `ALWAYS_AVAILABLE`
  (`src/tool_index.py:35-45`) nor `_DOMAIN_TOOL_MAP` (`src/agent_loop.py:528-540`). A fenced block
  tagged with the name does not parse at all, because the fence regex is built from `TOOL_TAGS`
  (`src/tool_parsing.py:33-38`); the XML form does:

  ```
  $ venv/bin/python /tmp/mcpsrv/probe_parse.py
  xml invoke  -> [ToolBlock(tool_type='mcp__rag__manage_rag', content='{"action": "add_directory", "directory": "/etc"}')]
  fenced      -> []
  tool_call   -> []
  ```
- **Impact:** whoever can get this tool called — an ordinary authenticated user whose agent emits the
  qualified name, or any untrusted text that names it to a model that already supports the XML call
  shape — gets two things the route refuses: indexing a directory outside `PERSONAL_DIR`
  (`/etc`, another user's home, a checkout) into the shared collection that every user's chat
  retrieves from, and removing another owner's indexed directory. The route's admin requirement is
  the control that says this is an operator action; the server has no equivalent. Today the model has
  to be told the name, which is what keeps this at medium; the defect is that the guard is missing,
  not that it is hard to reach.
- **Fix:** have `rag_server` reuse the route's helper — resolve through
  `_resolve_allowed_personal_dir`'s realpath-plus-commonpath check and return its 403 as a tool
  error — and pass an owner the way `email_server` does. If the server is meant to stay ownerless,
  the honest alternative is to stop registering it, since the native path already covers the feature.

### [BUG] An agent-generated image is written to the gallery with no owner and no session, so it never appears in any user's gallery

- **Location:** `mcp_servers/image_gen_server.py:143-153`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the row omits both attribution columns:

  ```python
  # mcp_servers/image_gen_server.py:143-152
  db.add(GalleryImage(
      id=str(uuid.uuid4()),
      filename=filename,
      prompt=prompt,
      model=model_id,
      size=size,
      quality=payload.get("quality", "medium"),
  ))
  db.commit()
  db.close()
  ```

  The native writer sets them, and it is the path this server replaced: `generate_image` is in
  `_MCP_TOOL_MAP` (`src/tool_execution.py:570`) and every call takes the MCP branch
  (`:1112-1116`) — the direct fallback runs only when the server is not connected — so
  `src/ai_interaction.py`'s `_save_to_gallery` (`:1113-1134`, with `session_id=session_id`,
  `owner=owner` at `:1126-1127`) is not reached for agent calls. The gallery's own filter is strict:
  a named user sees only `owner == user`, so an ownerless row is visible to nobody, and the
  ownerless row is listed for every caller only when no user resolves at all. Measured against the
  real filter and a real table:

  ```
  $ venv/bin/python /tmp/mcpsrv/probe_gallery2.py
  AUTH_ENABLED=false user=None   -> [('mcp', None), ('native', 'alice')]
  AUTH_ENABLED=false user=alice  -> [('native', 'alice')]
  AUTH_ENABLED=true  user=None   -> []
  AUTH_ENABLED=true  user=alice  -> [('native', 'alice')]
  ```

  (`('mcp', None)` is the row shape above; `('native', 'alice')` is the shape `ai_interaction.py`
  writes.) The row is also unreachable by session: `session_image_refs` selects
  `GalleryImage.session_id == session_id` (`src/session_image_cleanup.py:52`), which is NULL here,
  while the serving endpoint treats a falsy owner as "no owner recorded → allow"
  (`app.py:530`).
- **Impact:** in a multi-user install, an image the agent generated renders in the chat but is absent
  from the gallery of the user who asked for it and from everyone else's, so it cannot be
  favourited, albumed, tagged or deleted through the UI; the file stays on disk and the row stays in
  the table. The prompt, model, size and quality it records are the user's own, so this is
  attribution rather than disclosure. In a single-user install (auth disabled) every row is listed
  and the defect is invisible, which is why it has gone unnoticed.
- **Fix:** thread the caller's owner and session into the tool arguments the way
  `email_server`'s `_odysseus_owner` is threaded — `src/tool_execution.py:1301-1304` already
  overwrites a model-supplied value, so the injection point exists — and pass both to `GalleryImage`.
  A cheaper interim step is to read the owner from the environment as `email_server` does, which
  covers single-owner installs only.

### [BUG] The email account cache is never invalidated, so a disabled or edited account keeps being used

- **Location:** `mcp_servers/email_server.py:283-285` (read), `:369` (write)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_load_config` memoizes the fully resolved config — passwords included — in a
  module-level dict keyed by owner and selector, and returns the memo before touching the database:

  ```python
  # mcp_servers/email_server.py:283-285
  cache_key = (_current_owner(), (account or "").strip().lower() or "__default__")
  if cache_key in _ACCOUNT_CACHE:
      return _ACCOUNT_CACHE[cache_key]
  ...
  _ACCOUNT_CACHE[cache_key] = cfg          # :369
  ```

  Nothing clears it: `grep -rn "_ACCOUNT_CACHE" --include=*.py .` finds the four lines above plus
  `.clear()` calls in `tests/test_mcp_email_decode_header_spaces.py` only. The cache lives in the
  server subprocess, which is connected once at startup (`src/builtin_mcp.py:170-181`,
  `app.py:1071-1072`) and reconnected only by the admin route (`routes/mcp/mcp_routes.py:295`) or a
  restart; no email-account route touches the MCP manager. Measured with a temp database holding one
  owner-scoped account, then disabled and re-passworded underneath the running process:

  ```
  first  _load_config: name='Work' imap_password='pw-one' smtp_password='smtp-one' account_id='acct1'
  rows the DB now returns : []
  _list_accounts_raw()    : []
  second _load_config: name='Work' imap_password='pw-one' smtp_password='smtp-one' account_id='acct1'
  cache keys: [('alice', '__default__')]
  ```

  (Synthetic passwords; the values are the probe's own.)
- **Impact:** `enabled = 0` and the delete route are the two controls that are supposed to stop an
  account being used, and both are filtered out by `_read_accounts_from_db` (`WHERE enabled = 1`) —
  but only on a cache miss. After an edit, the agent keeps sending from the mailbox with the old
  credentials: a rotated password means failing IMAP/SMTP logins that look like a server problem,
  and a deleted account remains usable through the MCP tools until the process restarts. The same
  dict also grows by one entry per distinct selector string the model passes, since the selector is
  matched as a substring.
- **Fix:** keep the cache but key it on the row's `updated_at` (or re-read `email_accounts` before
  the cache hit and compare), or drop the cache — `_load_config` is called once per tool call, and
  the query it replaces is a single indexed `SELECT`.

### [BUG] The built-in memory server can never be owner-scoped, and the app no longer dispatches it

- **Location:** `mcp_servers/memory_server.py:29-46` (with `:60-87`), `src/builtin_mcp.py:148-160`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the server's only owner source is an environment variable, and the registration hands
  it an environment containing exactly one key:

  ```python
  # src/builtin_mcp.py:148-160
  def builtin_python_env(base_dir: str) -> dict[str, str]:
      existing = os.environ.get("PYTHONPATH", "")
      parts = [base_dir]
      for item in existing.split(os.pathsep):
          if item and item not in parts:
              parts.append(item)
      return {"PYTHONPATH": os.pathsep.join(parts)}
  ```

  ```
  $ venv/bin/python /tmp/mcpsrv/probe_memory_env.py
  builtin_python_env(base_dir) -> {'PYTHONPATH': '/app/root'}
  owner env keys in it        -> []
  _configured_owner() in that env -> None
  {'action': 'list'} -> Error: Memory MCP owner is not configured for an owner-scoped memory store. …
  {'action': 'add', 'text': 'new'} -> Error: Memory MCP owner is not configured for an owner-scoped memory store. …
  ```

  `grep -rn "ODYSSEUS_MCP_MEMORY_OWNER\|ODYSSEUS_MEMORY_OWNER"` over the tree returns the server's
  own read (`:29`), `specs/memory-skills.md:60` and `tests/test_mcp_memory_owner_scope.py:58` —
  nothing sets either name in production. So the fail-closed branch at `:76-77` is the only
  reachable one once any entry in `memory.json` carries an owner, which is exactly the multi-user
  state `src/memory.py:196-204` creates. The tool is also no longer on the app's dispatch path:
  `manage_memory` routes to the native `do_manage_memory` (`src/tool_execution.py:1169-1171`) and
  the module comment records why ("an entry outside that map is dead, as manage_memory was",
  `:647-649`), while `mcp__memory__manage_memory` is skipped in the schemas and the prompt because
  `memory` is a built-in (`src/mcp_manager.py:641-648`, `:580-582`, `:679-680`). The store this
  second process writes is the same `memory.json` the app writes, which `src-memory-rag.md` reports
  as an unsynchronized race; that finding is not restated here.
- **Impact:** every install spawns a Python subprocess whose only tool either refuses the request
  (owner-scoped store) or duplicates the native tool's job with a weaker owner model (ownerless
  store), and whose writes can lose entries to the app's own writes. A user whose agent happens to
  emit `mcp__memory__manage_memory` gets an error message naming an environment variable they have
  no way to set, from a server the app registers at every startup but does not advertise.
- **Fix:** delete the server from `_BUILTIN_SERVERS` — the native handler covers every action — or
  give it the per-call owner argument `email_server` uses, and delete the env-var path. Leaving both
  copies in place is what makes the next memory fix land in one of them.

### [SECURITY] No IMAP argument is checked for CR/LF, and the uid parameters are not checked at all

- **Location:** `mcp_servers/email_server.py:45-47` (`_q`), `:1929`, `:1950`, `:1958`, `:1977`,
  `:1231`, `:1099-1102`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `folder`, `uid` and `uids` are plain strings in the tool schemas and are interpolated
  into IMAP commands. `_q` escapes only a backslash and a double quote, so a CR/LF passes through:

  ```python
  # mcp_servers/email_server.py:45-47
  def _q(name: str) -> str:
      """Quote an IMAP mailbox name for commands that take mailbox args."""
      return '"' + (name or "").replace("\\", "\\\\").replace('"', '\\"') + '"'
  ```

  The uid paths do not even quote: `conn.uid("STORE", _b(uid), op, flag)` (`:1929`),
  `msg_set = ",".join(str(u) for u in uids)` (`:1950`, `:1977`) and
  `f'(HEADER Message-ID "{message_id}")'` (`:1231`, where the quotes are literal and unescaped). The
  stdlib does not sanitize them either — `imaplib.IMAP4._command` concatenates every argument and
  appends CRLF with no control-character check:

  ```
  $ python3 -c "import imaplib, inspect; print(inspect.getsource(imaplib.IMAP4._command))"
      data = tag + b' ' + name
      for arg in args:
          if arg is None: continue
          if isinstance(arg, str):
              arg = bytes(arg, self._encoding)
          data = data + b' ' + arg
      ...
      self.send(data + CRLF)
  ```

  (`uid` is documented in the tool descriptions as "Exact Email UID from list_emails/read_email;
  never invent UID 1" — a constraint on the model, not on the value.) The counter-example in the
  same file is `_search_emails`, which does escape quotes and backslashes in the query (`:1099`) but
  still not CR/LF.
- **Impact:** a `folder`, `uid`, `uids` or `message_id` value carrying CRLF appends IMAP commands to
  the authenticated connection — `SELECT` another mailbox, `STORE`/`EXPUNGE` a message set the tools
  do not expose, `CREATE`/`DELETE`/`RENAME` a mailbox — and the trailing quote or message-set token
  is consumed by a second command line the caller writes. The mailbox and the account are still the
  user's own, and the model already has delete and move tools, so the escalation is small; what is
  missing is the validation, which is also what makes an ordinary bug (a `folder` copied from a
  header, a `uid` with a stray newline) produce a corrupted command instead of an error.
- **Fix:** validate at the boundary — `uid`/`uids` must match `^\d+$` (they are UIDs), `folder` and
  `message_id` must not contain CR or LF — and return a tool error otherwise. `imaplib` has no
  literal-length handling here, so validation is the only place this can be closed.

### [ERROR-HANDLING] A failed gallery write is swallowed with no log line and leaks the session

- **Location:** `mcp_servers/image_gen_server.py:139-154`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the whole block is inside `try/except Exception: pass` and closes the session only on
  the success path:

  ```python
  # mcp_servers/image_gen_server.py:139-154
  try:
      from src.database import SessionLocal, GalleryImage
      db = SessionLocal()
      db.add(GalleryImage(...))
      db.commit()
      db.close()
  except Exception:
      pass
  ```

  The native copy of the same insert logs the failure and returns an empty id
  (`logger.warning(f"Failed to save gallery record: {_ge}")`, `src/ai_interaction.py:1133`). Here the
  image file has already been written and the URL is already in the tool result the model receives,
  so the caller sees success.
- **Impact:** when the insert fails — a locked database, a schema missing a column, a duplicate
  filename — the user gets an image in the chat that is not in the gallery, the cause is recorded
  nowhere, and the session is left open for the life of the subprocess. This is also why the finding
  above has no symptom to point at.
- **Fix:** log the exception and close the session in a `finally`, as the sibling implementation
  does.
