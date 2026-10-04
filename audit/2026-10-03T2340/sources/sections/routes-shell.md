# routes: shell and code execution

## Overview

`routes/shell_routes.py` (1,971 lines) owns the two endpoints that run arbitrary commands
(`POST /api/shell/exec`, `POST /api/shell/stream`), the three streaming backends behind them (pipe,
PTY, tmux, plus the Windows detached-process path), and the Cookbook dependency routes that probe and
mutate package state (`GET /api/cookbook/packages`, `POST /api/cookbook/packages/install`,
`POST /api/cookbook/install-system-deps`, `POST /api/cookbook/rebuild-engine`). The frontend calls
the shell endpoints from the code runner, the Cookbook download and install panels, and the
hardware-fit checks; the dependency routes are the Cookbook Dependencies tab's read path and its two
install actions. The agent's loopback bridge into these routes (`src/tools/system.py`,
`src/tools/cookbook.py`) is covered by `src-agent-tools`; the Cookbook route helpers and the tmux
task model the frontend drives belong to `routes-cookbook` and
`static-js-cookbook-settings-models`. A finding here is about what this router does with a command
once it has one, not about who may call it: admin-only is enforced at `_require_admin` and that
decision is not re-reviewed here.

## Coverage

**Read fully:** `routes/shell_routes.py` (1,971 lines). Every cited line was re-read at `2992bf6d368a`.

**Read partially:**

- `static/js/cookbook.js` at `_installDep` (`:1399-1470`) and the install-button wiring
  (`:1509-1516`), to establish which endpoint the UI's install path calls
- `static/js/codeRunner.js:309-340` and `static/js/cookbookDownload.js:380-400`, the two call sites
  that set the request shape
- `app.py:125-145` (CORS origin list) and `:1303` (default bind host)
- `routes/auth_routes.py:185-194` (session cookie flags). Two small reproduction scripts were run in
  `/tmp` with the same `asyncio.create_subprocess_shell` call shape as `_create_shell`
- their output is quoted in the first finding

**Not read:**

- every test file
- `routes/cookbook_helpers.py` (`_llama_cpp_rebuild_cmd` is called at `:1949` but not read)
- `routes/cookbook_routes.py`
- the remaining Cookbook front-end panels beyond the cited lines
- `static/js/cookbookRunning.js`, which drives the tmux tasks these endpoints serve

No test suite was run.

## Findings

### [BUG] Killing the shell leaves its children running, and the timeout path can wait forever

- **Location:** `routes/shell_routes.py:591`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_create_shell` (`:552-572`) starts the command as `/bin/sh -c <command>` with
  `stdout=PIPE, stderr=PIPE` and no new session. When the timeout fires, `_exec_shell` kills only the
  direct child and then waits on it:

  ```python
  except asyncio.TimeoutError:
      if proc:
          try:
              proc.kill()
              await proc.wait()
  ```

  (`:588-592`; the wait is `:592`.) The pipe-streaming generator has the same kill-and-wait at
  `:1097-1098`, and on client disconnect kills without waiting at `:1082`. The PTY generator sets
  `preexec_fn=os.setsid` (`:627`) and then calls `proc.kill()` at `:644`, `:652`, and `:716` — it
  never signals the process group, so the new session buys nothing. Reproduced with the same call
  shape: a shell running `while true; do echo tick >> log; sleep 1; done & wait` was killed after the
  timeout, and its child survived while `proc.wait()` stayed blocked because the child holds the
  inherited stdout/stderr pipes:

  ```
  shell pid: 3580188 children: [3580190]
  sent SIGKILL to shell
  proc.wait() HUNG for 3s (grandchild holds the pipes)
  child 3580190 ALIVE
  ticks 5 -> 7: child STILL RUNNING
  ```

  The same sequence with `_exec_shell`'s exact prefix — `asyncio.wait_for(proc.communicate(),
  timeout=1)`, then `proc.kill()`, then `proc.wait()` — reproduced the same hang and the same
  surviving descendant. `asyncio`'s `Process.wait()` waits for pipe EOF, not only for the process to
  exit.
- **Impact:** `/api/shell/exec` and `/api/shell/stream` are the frontend's general command runners.
  Any command that leaves a child holding the pipes — a backgrounded server, a build tool that
  forks, user code that spawns `subprocess.run` — and then exceeds the timeout (30 s for exec, 120 s
  for stream) leaves the request blocked in `await proc.wait()`: the client never receives the
  timeout result, and the descendant keeps running with the pipe. The disconnect path and the PTY
  path leak the same descendants without the hang. Each occurrence holds a request task, two pipe
  transports, and a live process tree.
- **Fix:** start the child in its own session (`start_new_session=True` in `_create_shell`) and kill
  the group (`os.killpg(proc.pid, signal.SIGKILL)`), which also closes the pipes; in the PTY path use
  `os.killpg` for the session `setsid` already created. Bound every `await proc.wait()` with a short
  `asyncio.wait_for` so a surviving grandchild cannot pin the handler.

### [BUG] `timeout: 0` means "no timeout" everywhere except `/api/shell/exec`, where it means "stop now"

- **Location:** `routes/shell_routes.py:974`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the request model documents `0 = no timeout (run until client disconnects)`
  (`:504-506`). The streaming path implements it: `shell_stream` logs `"none" if timeout == 0`
  (`:996`), the pipe loop sets `deadline = (loop.time() + timeout) if timeout else None` (`:1067`),
  and the PTY loop does the same (`:631`). `shell_exec` passes the value straight through:

  ```python
  result = await _exec_shell(
      cmd, timeout=req.timeout if req.timeout is not None else EXEC_TIMEOUT
  )
  ```

  (`:973-975`), and `_exec_shell` passes it to `asyncio.wait_for` (`:584`), where 0 is an
  already-expired deadline. Confirmed:

  ```
  $ python3 -c "import asyncio; asyncio.run(...wait_for(asyncio.sleep(5), timeout=0))"
  TimeoutError immediately with timeout=0
  ```

  The response is `{"stdout": "", "stderr": "Command timed out after 0s", "exit_code": -1}` with the
  process killed.
- **Impact:** a caller that follows the documented contract and sends `timeout: 0` to run a long
  command to completion gets an immediate false timeout. No current frontend caller sends 0 to this
  endpoint — every `/api/shell/exec` call site sends 5-60 — so the defect is latent and would
  surface when a caller adopts the documented value.
- **Fix:** pass `req.timeout or None` to `_exec_shell`, or drop `0 = no timeout` from the model and
  document that only the streaming endpoints accept it.

### [BUG] The dependency installs report a timeout without stopping the install

- **Location:** `routes/shell_routes.py:1907`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `install_system_deps` runs the package-manager script under a 180 s timeout and
  returns without touching the process:

  ```python
  out, err = await asyncio.wait_for(proc.communicate(), timeout=180)
  except asyncio.TimeoutError:
      return {"ok": False, "error": "Install timed out after 180s"}
  ```

  (`:1907-1910`.) `rebuild_engine` is the same shape with a 30 s timeout (`:1964-1966`).
  `_exec_shell` at least calls `proc.kill()` in its timeout branch; these two do not.
- **Impact:** the response says the install failed while `apt-get`, `dnf`, or the rebuild keeps
  running. A retry starts a second package manager against the same lock, and the Cookbook panel's
  state (deps still missing) contradicts what the host is doing.
- **Fix:** kill the process group in the timeout branch before returning, and say in the error that
  the command was stopped.

### [PERF] The tmux tail re-reads the whole log file every second on the event loop

- **Location:** `routes/shell_routes.py:805`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the 1 Hz tail loop reads and splits the entire log, then slices off the part it has
  already sent:

  ```python
  lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
  new_lines = lines[lines_sent:]
  ```

  (`:804-808`; the Windows path repeats it at `:918-920` and `:932-934`.) The read is synchronous
  inside the async generator. Measured on this machine: a 1 MB log takes 1 ms to read and split,
  5 MB takes 4 ms, and 20 MB takes 18 ms — repeated every second. Total bytes read over a run grow
  with the square of the log size: a 20 MB log polled for 30 minutes is roughly 36 GB of reads.
- **Impact:** the tmux path exists for long Cookbook builds and downloads, the commands that produce
  the largest logs. Each poll blocks the event loop for the read, stalling every other request, and
  the wasted I/O grows with the file.
- **Fix:** keep the file open and read only the appended bytes (track the byte offset and `seek`), or
  move the read to a thread. Cap or rotate the log.

### [FOOTGUN] The cross-site guard is on the read-only dependency listing, not the shell endpoints

- **Location:** `routes/shell_routes.py:1201`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_reject_cross_site` rejects requests whose `Sec-Fetch-Site` is `cross-site`
  (`:72-75`). Its only call in the file is on `list_packages`, a GET (`:1201`). The mutating
  endpoints — `shell_exec` (`:963`), `shell_stream` (`:981`), `install_package` (`:1765`),
  `install_system_deps` (`:1820`), `rebuild_engine` (`:1941`) — call only `_require_admin`. The
  current cookie policy and body parsing block the obvious cross-site forms: the session cookie is
  `SameSite=Lax` (`routes/auth_routes.py:188`), and a Pydantic body needs `application/json`, which
  an HTML form cannot send. So this is not an exploitable CSRF today.
- **Impact:** the one endpoint that carries the guard is the one that changes nothing, and the
  endpoints that execute code depend on the cookie policy staying strict. If `SameSite` is relaxed
  for an embedded or tunneled deployment, or an origin is added to the CORS allowlist, the mutating
  endpoints have no cross-site check to fall back on.
- **Fix:** call `_reject_cross_site` in the mutating handlers, or install it as a router dependency.

### [SECURITY] tmux wrapper scripts and their logs are readable by other local users

- **Location:** `routes/shell_routes.py:770`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the log directory is created with the process umask
  (`TMUX_LOG_DIR.mkdir(parents=True, exist_ok=True)`, `:749`), and the wrapper script is explicitly
  made world-readable and executable:

  ```python
  script_path.chmod(0o755)
  ```

  (`:770`.) The script embeds the command verbatim (`f"{cmd} 2>&1 | tee '{log_path}'"`, `:763`), and
  the log is created by `tee` under the same umask. On the machine this was read on:

  ```
  $ ls -la /tmp/odysseus-tmux/
  drwxr-xr-x 2 lhl lhl 60 ... .
  -rw-r--r-- 1 lhl lhl 10188 ... scan_cache.py
  ```

- **Impact:** on a host with more than one local account, another user can read the command line and
  the output while the job runs. Commands passed through this path can contain tokens, signed URLs,
  or private model paths. Admin-only authorization does not protect against a second local account.
- **Fix:** create the directory with mode 0700 and the script with 0700, and create the log with a
  restrictive mode (for example `umask 077` in the wrapper, or an `os.open(..., 0o600)` before
  `tee`).

### [DEAD-CODE] `install_package` is unused by the UI, installs into the wrong interpreter, and rejects most catalog entries

- **Location:** `routes/shell_routes.py:1763`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the route always installs into the Cookbook server's own interpreter and accepts no
  target:

  ```python
  cmd = [_sys.executable, "-m", "pip", "install", pip_name]
  ```

  (`:1789-1791`.) The UI's install path does not call it: `_installDep` builds the pip command for
  the selected venv or remote host and submits it through the task flow
  (`static/js/cookbook.js:1399-1470`, wiring at `:1512`). A repository search finds no other caller
  of `/api/cookbook/packages/install`; the only references are the agent blocklist
  (`src/tools/system.py:557` and the refusal at `:678-679`) and a test. The `known` allowlist
  (`:1772-1793`) also does not contain most of the catalog's pip strings — the `diffusers` row is
  `"diffusers[torch] torchvision accelerate scipy python-multipart"` (`:1322`) and `krea_diffusers`
  is `"git+https://github.com/huggingface/diffusers.git torchvision accelerate scipy
  python-multipart"` (`:1329`), neither of which matches an entry — so those rows would be refused
  as unknown.
- **Impact:** an endpoint that would install into the server's environment rather than the selected
  one if it were called, plus a blocklist entry and a test that guard it. The UI works around it.
- **Fix:** delete the route, or route it through the same target-aware install flow the UI uses.
