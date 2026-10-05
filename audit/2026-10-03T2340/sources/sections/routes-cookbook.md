# routes: cookbook

## Overview

The model-lifecycle surface: `routes/cookbook_routes.py` (the Cookbook router — SSH key management,
remote server setup, model download and serve launch, cached-model scanning, GPU probing, PID
killing, the cookbook state file, and the task-status poller) and `routes/cookbook_helpers.py` (the
validators, runner-script builders and request models those routes use). Every endpoint here that
mutates state or starts a process calls `require_admin(request)` in its body; the read-only lookups
are only authenticated — the HuggingFace and Ollama browse endpoints take `Depends(require_user)`,
and the two vLLM-recipe endpoints rely on the session middleware alone, since nothing under
`/api/cookbook` is in the auth-exempt lists in `app.py` (`:264-296`).

The boundary: the middleware that authenticates the request and the `require_admin` guard are
`core-auth-session`; the `ModelEndpoint` rows these routes write and probe are `routes-models`; the
tmux log directory and session naming come from `routes-shell`; `routes/cookbook_output.py` (the
download classifiers the poller imports) is `routes-rest-media-files`; the agent tool and the
scheduled action that POST to `/api/model/serve` are `src-agent-tools` and
`src-research-scheduling`. This section covers whether each route validates what the client sends and
what the server then runs, not whether the stores or the tools underneath are correct.

## Coverage

**Read fully:** both assigned files (6,065 lines): `routes/cookbook_routes.py` (4,583),
`routes/cookbook_helpers.py` (1,482). Every cited line was re-read at `2992bf6d368a`.

**Read partially:** the callees the findings rest on:

- `routes/model_routes.py` at `_probe_endpoint` (`:958-998`, the synchronous `httpx` probe of a base
  URL's `/v1/models`)
- `core/middleware.py` at `require_admin` (`:57-82`)
- `app.py` at the auth-exempt lists (`:264-296`)
- `core/atomic_io.py` at `atomic_write_json` (`:22-45`)
- `core/platform_compat.py` at `safe_chmod` (`:40-52`)
- `routes/_validators.py` (the whole 31-line file: `validate_remote_host`, `validate_ssh_port`)
- `src/constants.py` at `COOKBOOK_STATE_FILE` (`:32`)
- `services/hwfit/hardware.py` at `detect_system` (`:792-816`) and its `_run` helper (`:27-45`)
- `src/tools/cookbook.py` at the `serve_model` HTTP call (`:755-800`)
- `src/builtin_actions.py` at `action_cookbook_serve` (`:3151-3300`)
- `src/task_action_policy.py` (`:1-40`)
- `static/js/cookbookServe.js` at `_isMiniMaxM3Model` (`:425-434`) and the MiniMax M3 launch path
  (`:1440-1465`)

**Not read:**

- `routes/cookbook_output.py` (`error_aware_output_tail`, `classify_dead_download`), which the
  status handler imports
- the `ModelEndpoint` table definition and the endpoint CRUD routes in `routes/model_routes.py`
  beyond `_probe_endpoint`
- `src/secret_storage.py` beyond the two function signatures
- `src/host_docker_access.py`
- `core/platform_compat.py` beyond `safe_chmod` and `_ssh_exec_argv`
- `src/task_scheduler.py`'s dispatch of the `cookbook_serve` action
- the front end beyond the two regions named above
- the `routes-*` / `src-*` sections that own the modules these routes call

**Checks run:**

- four throwaway probes under `/tmp` (not part of the target tree), plus the cookbook suites. The
  probes were: the `/api/cookbook/setup` handler driven with a stub `ssh` on `PATH` and the real
  shell, once per platform branch, with each captured command also replayed through `sh -c` (first
  finding)
- `POST /api/model/serve` driven the same way with a placeholder token, then `stat` on the runner
  script it wrote (fourth finding)
- `GET /api/cookbook/hf-gguf-files` with `httpx.AsyncClient` replaced by a constructor that raises
  (fifth finding)
- `_validate_serve_cmd` called directly with the shipped GGUF prelude and a modified one (third
  finding)

Twenty-six suites were run over this surface: **229 passed, 1 skipped**. They are the files from
`ls tests | grep -iE 'cookbook'`, plus `tests/test_task_cookbook_admin_gate.py`:

- `tests/test_cookbook_helpers.py`
- `tests/test_cookbook_diagnosis.py`
- `tests/test_cookbook_error_feedback.py`
- `tests/test_cookbook_serve_lifecycle.py`
- `tests/test_cookbook_endpoint_registration.py`
- `tests/test_cookbook_hf_token.py`
- `tests/test_cookbook_deps_recipes.py`
- `tests/test_cookbook_dependency_completion_regression.py`
- `tests/test_cookbook_cpu_only_serve.py`
- `tests/test_cookbook_dead_download_status.py`
- `tests/test_cookbook_docker_access.py`
- `tests/test_cookbook_package_detection.py`
- `tests/test_cookbook_gemma4_thinking_template.py`
- `tests/test_cookbook_local_serve_pid_winpid.py`
- `tests/test_cookbook_remote_windows_diffusers.py`
- `tests/test_cookbook_agent_tool_ssh_validation.py`
- `tests/test_codex_cookbook_admin_gate.py`
- `tests/test_builtin_actions_cookbook_serve_state.py`
- `tests/test_task_cookbook_admin_gate.py`
- the seven JS-string suites:
  - `tests/test_cookbook_diagnosis_js.py`
  - `tests/test_cookbook_download_toast_duration.py`
  - `tests/test_cookbook_error_tail_lines.py`
  - `tests/test_cookbook_port_parsing_js.py`
  - `tests/test_cookbook_progress_signal_js.py`
  - `tests/test_cookbook_same_host_server_profiles_js.py`
  - `tests/test_cookbook_windows_stop_tree_js.py`

### [BUG] The remote setup endpoint interpolates its install script into a shell command, so no platform receives the script it built

- **Location:** `routes/cookbook_routes.py:2911` (the Linux command), `:2889` (the Termux command), `:2881` (the Windows command), `:2919` (the success check)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** each branch builds a command string and hands it to a shell (`asyncio.create_subprocess_shell(cmd, ...)`, `:2914`), while the script it embeds carries quoting the local shell re-parses:

  ```python
          elif platform == "termux":
              setup_script = (
                  "pkg install -y python tmux 2>/dev/null; "
                  ...
                  "python3 -c 'from huggingface_hub import snapshot_download; print(\"OK\")'"
              )
              cmd = f"ssh {pf}{host} '{setup_script}'"          # :2889
          else:
              setup_script = (
                  "if ! command -v tmux >/dev/null 2>&1; then "
                  ...
                  "command -v tmux >/dev/null 2>&1 || echo 'WARNING: tmux missing and auto-install failed (need passwordless sudo). Install manually.'; "
                  ...
                  "python3 -c 'from huggingface_hub import snapshot_download; print(\"OK\")'"
              )
              cmd = f"ssh {pf}{host} '{setup_script}'"          # :2911
  ```

  The first inner `'` ends the outer quote, so the rest of the script is parsed as shell syntax; which
  token the parser trips on depends on the script (the `(` in the Linux branch's warning text,
  `print("OK")` in the Termux branch). Driving the endpoint with a stub `ssh` on `PATH` and the real
  shell, the Linux and Termux branches make the setup command a syntax error, so `ssh` is never
  invoked for it — yet the handler reports success, because `ok` is a substring test on the echoed
  output (`ok = "OK" in output`, `:2919`):

  ```
  ===== linux  (platform 'linux')
    endpoint: {'ok': True, 'platform': 'linux', 'output': "...python3 -c 'from huggingface_hub import snapshot_download; print(\"OK\")\'''"}
    local sh -c exit 2: syntax error near unexpected token `('
    ssh invocations: 2 — 'example.invalid echo %OS%' and 'example.invalid test -d /data/data/com.termux && echo termux || echo linux'
  ===== termux (platform 'termux')
    endpoint: {'ok': True, 'platform': 'termux', ...}
    local sh -c exit 2: syntax error near unexpected token `"OK"'
    ssh invocations: 2 — the same two platform probes
  ```

  The Windows branch (`:2881`) builds its command without the outer quotes — `ssh {pf}{host} {setup_script}`
  — so the local shell keeps parsing it: it strips the quotes around the `powershell -Command` payload
  and expands `$env:TEMP` and `$null` as its own (empty) variables. Capturing that command and
  replaying it with the same stub shows what the client would send:

  ```
  ssh receives: ARGV[1]=powershell   ARGV[2]=-Command
    ARGV[3]=New-Item -ItemType Directory -Force -Path :TEMP\odysseus-sessions | Out-Null; try { python --version } catch { Write-Host 'ERROR: Python not found — install from python.org'; exit 1 }; ... 2>
  ```

  `$env:TEMP` arrived as `:TEMP` and `2>$null` as `2>`, and OpenSSH joins those arguments into one
  command string, so the remote shell sees the `-Command` payload unquoted with `| Out-Null` and `;`
  at its own level. What a real Windows host does with that was not tested here; the local
  transformation was.
- **Impact:** the Cookbook "server setup" action — the one the app's own missing-binary message sends
  the operator to ("Install it with your OS package manager, or run Cookbook server setup for that
  server", `:232`) — installs nothing on a Linux or Termux remote and reports `ok: true` while doing
  it, so the operator learns otherwise only when the next download or serve fails with "tmux is
  required"; on a Windows remote the script arrives mangled. The mitigation is that the same message
  names the manual install, and the endpoint is admin-only.
- **Fix:** stop building a command string: pass an argv list with
  `asyncio.create_subprocess_exec("ssh", *ssh_args, setup_script, ...)`, which hands the script to ssh
  as one argument with no local shell to re-parse it. That also fixes the Windows branch, whose quotes
  and `$` references the local shell consumes today.

### [HARDCODE] The MiniMax M3 normalizer rewrites the model argument to a snapshot path under a developer's home directory

- **Location:** `routes/cookbook_routes.py:666-672`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_normalize_minimax_m3_vllm_cmd` runs on every serve command that mentions `vllm serve` and `minimax`/`m3` (`:645-650`) and rewrites the model argument unconditionally:

  ```python
          repo_id = "cyankiwi/MiniMax-M3-AWQ-INT4"
          snapshot = (
              "/home/pewds/.cache/huggingface/hub/"
              "models--cyankiwi--MiniMax-M3-AWQ-INT4/"
              "snapshots/4082acbbec1236d21828d55b6bb0fe02ade4ab5b"
          )
          if body[serve_i + 1] == repo_id:
              body[serve_i + 1] = snapshot
  ```

  The rewritten command is what the runner script executes: the vLLM branch copies it into
  `ODYSSEUS_SERVE_CMD` (`:2349`) and the runner evals that variable (`:2705-2706`). The same absolute
  path is hardcoded in the front end (`static/js/cookbookServe.js:1457`), where `_isMiniMaxM3Model`
  (`:425-434`) matches any model whose identity text contains `minimax` and `m3`, and that constant
  becomes the model path the launch form sends (`:1458-1460`).
- **Impact:** a saved preset, a retry from a running row, or the agent's `serve_model` that submits
  `cyankiwi/MiniMax-M3-AWQ-INT4` has it replaced with a path that exists only on the machine the
  string was copied from, so vLLM fails on a missing local directory instead of loading the repo (and
  the model can no longer be downloaded on first launch). Every host except the author's is affected;
  the front-end constant makes the launch form send that same path for any MiniMax M3 row.
- **Fix:** delete the rewrite (and the front-end constant), or gate it on the snapshot directory
  existing on the target host (`Path(snapshot).is_dir()`), which is how the rest of the module guards
  cached-path rewrites.

### [SECURITY] A serve command's GGUF prelude skips the metacharacter check the validator claims to apply

- **Location:** `routes/cookbook_helpers.py:767-773` (the prelude branch), `:786-787` (the check it skips), `:624-626` (the pattern)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the validator's docstring states the contract — "`req.cmd` is dropped verbatim into a bash/PowerShell wrapper script and executed in a tmux session. Without this gate, an admin (or anyone in the pre-fix world) could pass arbitrary shell payloads." — and the check that implements it runs only on the non-prelude path:

  ```python
      m = _GGUF_PRELUDE_RE.match(v)
      if m:
          rest = v[m.end():]
          for part in rest.split("||"):
              _check_serve_binary(part.strip())
          return v
      ...
      if any(c in cleaned_v for c in (";", "&&", "||", "$(")):
          raise HTTPException(400, "Invalid characters in cmd")
  ```

  `_GGUF_PRELUDE_RE` (`:624-626`) matches `MODEL_FILE=$(<anything but a newline>) && {...} || {...} &&`,
  so the body of the command substitution is unconstrained, and the prelude branch returns the command
  unchanged without running the metacharacter test. Measured by calling the validator directly:

  ```
  shipped prelude accepted: True
  crafted prelude ACCEPTED unchanged: True
  control: bare ';' rejected -> Invalid characters in cmd
  ```

  The crafted string (`MODEL_FILE=$(touch /tmp/...; echo x) && { ... } || { ... } && python3 -m
  llama_cpp.server ...`) was only validated, never executed, so nothing ran. `_check_serve_binary` is
  applied to `rest`, the part after the prelude, and its basename check passes for `python3`, so the
  payload reaches the runner script intact.
- **Impact:** for commands that start with the GGUF prelude the Cookbook UI itself emits for llama.cpp
  models, the `$(...)` body can carry `;`, `&&`, or a nested command substitution. The route calls
  `require_admin` (`:1972`), and `require_admin` also accepts the in-process internal tool token
  (`core/middleware.py:66-73`) — the path the scheduled `cookbook_serve` action uses
  (`src/builtin_actions.py:3267`). Both are admin-only today (`serve_model` is in
  `NON_ADMIN_BLOCKED_TOOLS`, `src/tool_security.py:73`; `cookbook_serve` is in
  `ADMIN_ONLY_TASK_ACTIONS`, `src/task_action_policy.py:5-10`) and an admin can run `bash` anyway, so
  this is a control that does not deliver what it claims rather than an escalation. What would settle
  whether it is more than that is whether any other caller reaches `/api/model/serve` with a
  non-admin-supplied `cmd`; the scheduler's dispatch was not audited here.
- **Fix:** validate the prelude's `$(...)` body against the same safe-subshell patterns the non-prelude
  branch already uses (`_SAFE_PRINTF_SUBSHELL_RE`, `_SAFE_FIND_MMPROJ_SUBSHELL_RE`) instead of only
  shape-matching the prelude.

### [SECURITY] The HuggingFace token is written in cleartext to world-readable runner scripts that the serve path never removes

- **Location:** `routes/cookbook_routes.py:2165` and `:2729-2733` (the serve bash runner), `:2090-2091` and `:2118` (the serve PowerShell runner), `:1244` and `:1321-1325` (the remote download runner), `:1174` and `:1216-1217` (the remote download PowerShell runner), `:1116` and `:1363-1364` (the local download wrapper)
- **Severity:** low
- **Disposition:** next
- **Evidence:** every runner builder embeds the token in the script it writes into `TMUX_LOG_DIR`
  (`/tmp/odysseus-tmux`, `routes/shell_routes.py:498`), and the bash ones are made world-readable by
  `safe_chmod(..., 0o755)` (`core/platform_compat.py:40-52`):

  ```python
              if req.hf_token:
                  runner_lines.append(f"export HF_TOKEN='{_bash_squote(req.hf_token)}'")   # :2165
              ...
              runner_path = TMUX_LOG_DIR / f"{session_id}_run.sh"                        # :2729
              runner_path.write_text("\n".join(runner_lines) + "\n", encoding="utf-8")
              safe_chmod(runner_path, 0o755)                                             # :2733
  ```

  Measured by calling `POST /api/model/serve` with a stubbed subprocess and a placeholder token:

  ```
  endpoint: {'ok': True, 'session_id': 'serve-45554ef5', 'remote': 'local', 'endpoint_id': ...}
  new files in TMUX_LOG_DIR: ['serve-45554ef5_run.sh']
  dir mode: 0o755
  serve-45554ef5_run.sh: mode=0o755 world_readable=True token_present_in_file=True
     line: export HF_TOKEN='[REDACTED]'
  ```

  Nothing removes it: each flow deletes only the *remote* copy of its script (`rm -f {remote_runner}`,
  `:1319`; `Remove-Item -Force "$HOME\{remote_runner}"`, `:1215`) and the download flow's local
  wrapper deletes itself at the end of a successful run (`rm -f '{wrapper_script}'`, `:1361`), while
  the serve bash runner (`:2729-2733`), the serve PowerShell runner (`:2118`), the local copy of the
  remote download runner (`:1321-1325`) and its PowerShell twin (`:1216-1217`) stay in place; the
  PowerShell ones get no explicit mode and take the umask default. Nothing in the tree reads these
  files, so nothing reaps them.
- **Impact:** on a host with more than one local account, any user can list `/tmp/odysseus-tmux` and
  read the administrator's HuggingFace token out of a runner script — permanently for serve tasks,
  and for every download that leaves a local copy of its remote runner behind. The documented
  deployment is a single-user container, where this exposes nothing; the risk is a native multi-user
  install. The same module locks its SSH private key to `0o600` (`safe_chmod(key_path, 0o600)`,
  `:956`), so the token files are the outlier.
- **Fix:** write the runner with mode `0o600` and invoke it as `bash <path>` in the tmux command (the
  execute bit is not needed), or pass the token through the tmux environment instead of the script,
  and delete the local runner when the task ends.

### [ERROR-HANDLING] `hf_gguf_files` raises `NameError` in its own error path, turning an API failure into a 500

- **Location:** `routes/cookbook_routes.py:3885`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the handler is declared `hf_gguf_files(repo_id: str, owner: str = Depends(require_user))` (`:3868`) and its `except` block logs a name that does not exist in that scope:

  ```python
          except Exception:
              logger.exception("HF GGUF file scan failed for %s", repo)
              return {"ok": False, "files": [], "error": "HF API request failed"}
  ```

  `repo` is not a module-level name and is never assigned in this function (the only `repo` in the file
  is the parameter of `vllm_recipe`, `:4081`). Measured by calling the endpoint with
  `httpx.AsyncClient` replaced by a class that raises on construction:

  ```
  raised out of the handler: NameError name 'repo' is not defined
    File ".../routes/cookbook_routes.py", line 3885, in hf_gguf_files
      logger.exception("HF GGUF file scan failed for %s", repo)
  NameError: name 'repo' is not defined. Did you mean: 'repr'?
  ```

  The `return {"ok": False, ...}` the handler wrote never runs.
- **Impact:** any HuggingFace API failure — network error, timeout, DNS — on
  `GET /api/cookbook/hf-gguf-files` produces an unhandled 500 and a traceback instead of the JSON error
  the handler intends, and the log line loses the repo id it was meant to record. The endpoint is
  authenticated-only and read-only, so the cost is a confusing failure rather than a broken flow.
- **Fix:** log `repo_id`.

### [DUP] `_diagnose_serve_output` exists twice and has already drifted; the route runs the copy the tests do not cover

- **Location:** `routes/cookbook_routes.py:432-599` (the copy that runs), `:58` (the import it shadows), `routes/cookbook_helpers.py:1252-1445`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `cookbook_routes.py` imports the helper and then redefines it inside `setup_cookbook_routes()`:

  ```python
      _diagnose_serve_output, run_ssh_command_async,           # :58
      ...
      def _diagnose_serve_output(text: str) -> dict | None:    # :432
  ```

  so the nested definition wins for every handler in the module, and the only production call site is
  the status poller (`:4557`); nothing outside that scope calls the imported name. Comparing the two
  `patterns` tables (`ast.literal_eval` on each `patterns = [...]` assignment, then keying by pattern):

  ```
  helpers entries: 27   routes entries: 23   shared keys: 23
  keys only in routes: none
  shared keys whose suggestion list differs: 0
  keys only in helpers: 4
    'There is no module or parameter named ['\"]lm_head\.input_scale['\"]|lm_head\.input_scale|weight_scale_2'
        -> vLLM cannot load this ModelOpt LM-head quantized checkpoint with the current runtime.
    'mflux-generate-qwen.*not found|mflux-generate.*not found|MLX image serving requires mflux|No module named ['\"]?mflux'
        -> MLX image serving requires mflux on this Apple Silicon server.
    'mlx-lama-swift|odysseus-mlx-inpaint|mlx-lama-serve|LaMa / MI-GAN MLX inpainting models require'
        -> LaMa / MI-GAN MLX inpainting requires an Odysseus-compatible mlx-lama-swift bridge on this Apple Silicon server.
    'mlx-ddcolor-swift|odysseus-mlx-colorize|mlx-ddcolor-serve|DDColor MLX models require'
        -> DDColor MLX colorization requires an Odysseus-compatible mlx-ddcolor-swift bridge on this Apple Silicon server.
  ```

  The two suites that pin this function import the helpers copy (`tests/test_cookbook_diagnosis.py:1`,
  `tests/test_cookbook_error_feedback.py:1`), so they exercise the copy the route does not use.
- **Impact:** the table the running server uses is missing exactly the four patterns above, so a serve
  failure in those four classes (the ModelOpt LM-head checkpoint, mflux image serving, and the two MLX
  bridges) gets no diagnosis or retry suggestion from the status poller or from the agent's
  `list_served_models`, while the helper — the copy the tests read — would produce one; and a later
  edit to the helper will not reach the running server. Nothing fails loudly; the tables just differ.
- **Fix:** delete the nested definition and let the import stand (or move the union of the two tables
  into the helper and import it), so the tests and the route exercise one object.

### [PERF] The serve launch path runs synchronous SSH and HTTP probes on the event loop

- **Location:** `routes/cookbook_routes.py:2048` (and its `subprocess.run` at `:1627`), `:1946` (and `:1878`), `:1737`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `model_serve` is `async def` (`:1962`) and calls three synchronous blockers inline:

  ```python
              _ollama_chosen_port = _pick_free_port_for_ollama(       # :2048
                  remote, req.ssh_port, start_port=11434, max_offset=10,
              )
  ```
  ```python
                  r = subprocess.run(                                   # :1627, inside the sync helper
                      ssh_base + [host_arg, script],
                      capture_output=True, text=True, timeout=8,
                  )
  ```
  ```python
              endpoint_id = _auto_register_llm_endpoint(req, remote)  # :2792
              ...
                      probed = _probe_endpoint(base_url, None, timeout=5)   # :1946
  ```

  `_probe_endpoint` is synchronous and issues `httpx.get(...)` against the new endpoint's `/v1/models`
  (`routes/model_routes.py:958-998`), and the crash watchdog — an `async def` scheduled on the same
  loop (`:2806`) — blocks it again with `urllib.request.urlopen(probe_url, timeout=3)` (`:1737`).
  Sibling code in the same file offloads the identical pattern: `await asyncio.to_thread(_cookbook_tasks_status_sync)`
  (`:4214`), whose docstring gives the reason ("every subprocess.run inside this handler is a sync
  blocking call that — when this was a plain async def — froze the entire server event loop"), and
  `await asyncio.to_thread(_fetch_sync)` (`:4048`, `:4112`).
- **Impact:** an administrator launching a remote Ollama serve stalls every other in-flight request for
  up to about 8 s (the SSH port probe) plus up to 5 s per endpoint probe, a streaming chat turn
  included. The route is admin-only and infrequent, so this is a stall rather than an outage.
- **Fix:** wrap `_pick_free_port_for_ollama`, `_auto_register_llm_endpoint` /
  `_auto_register_image_endpoint` and the watchdog's reachability probe in `await asyncio.to_thread(...)`,
  matching the status handler.
