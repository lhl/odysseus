# static: cookbook, settings, models UI

## Overview

First-party client-side JavaScript for the Cookbook (model download, dependency install, serve and
schedule flows), the admin panel, the model picker, the provider registry, and the Settings panel
framework — 24 files under `static/js/`, about 24,800 lines. This section covers what the browser
does with values it receives from the server and with what the user types into these panels. It does
not cover the Python routes, helpers or agent tools those modules call (`routes-cookbook`,
`routes-models`, `routes-shell`, `routes-rest-auth-admin` and `src-mcp` own those), nor
`static/js/settings.js`, `tasks.js`, `ui.js` and the other static modules outside the list above
(`static-js-rest` owns those), nor the memory/RAG panels (`static-js-research-memory-rag`).

## Coverage

**Read in full:** `cookbookPorts.js` (19), `cookbookProgressSignal.js` (29), `model/matchKey.js`
(19), `modelSort.js` (33), `settings/dom.js` (7), `settings/navigation.js` (57),
`settings/lifecycle.js` (176), `settings/search.js` (172), `settings/registry.js` (237),
`settings/sidebar.js` (238), `cookbook-deps-recipes.js` (189), `providerDeviceFlow.js` (128),
`cookbookSchedule.js` (386).

**Read in part:** `admin.js` (3197), `cookbook.js` (3677), `cookbookServe.js` (4305),
`cookbookRunning.js` (4435), `cookbook-hwfit.js` (2826), `cookbookDownload.js` (670),
`cookbook-diagnosis.js` (1079), `models.js` (642), `presets.js` (1151), `modelPicker.js` (958),
`providers.js` (186). These were reviewed by targeted search — every `innerHTML`/`insertAdjacentHTML`
sink, every serve/download command builder, every `fetch` URL and request body, and every place a
secret is persisted — plus line-by-line reading of each range cited below. They were not read line
by line, so a defect outside those areas could remain.

**Not read:** none of the 24 assigned paths was skipped entirely.

**Checks run:**

- Twenty-three suites covering this surface, all passing:

  ```
  $ venv/bin/python -m pytest -q tests/test_cookbook_port_parsing_js.py tests/test_cookbook_progress_signal_js.py \
      tests/test_cookbook_deps_recipes.py tests/test_cookbook_diagnosis_js.py tests/test_model_sort_js.py \
      tests/test_match_model_key_js.py tests/test_provider_device_flow_js.py tests/test_preset_local_storage_js.py \
      tests/test_provider_label_js.py tests/test_providers_mixtral_logo_js.py tests/test_local_endpoint_js.py \
      tests/test_local_endpoint_api_key_js.py tests/test_admin_device_flow_static.py tests/test_setup_llamacpp_hint_js.py \
      tests/test_cookbook_same_host_server_profiles_js.py tests/test_cookbook_windows_stop_tree_js.py \
      tests/test_cookbook_hf_token.py tests/test_cookbook_error_feedback.py tests/test_cookbook_download_toast_duration.py \
      tests/test_model_name_tooltip.py tests/test_chat_model_provenance_js.py tests/test_settings_shell_js_behavior.py \
      tests/test_agent_round_model_provenance_ui.py
  96 passed, 1 warning in 2.79s
  ```

- `/tmp/audit-probe/check_ids2.mjs` — extracts every id `admin.js` looks up via `el(...)` /
  `getElementById(...)` and checks it against every HTML file in the tree (fourth finding).
- `/tmp/audit-probe/*.py` — the real `_safe_env_prefix` and `_validate_serve_cmd` helpers called
  directly with the strings the UI emits (second finding). Nothing was executed.
- A repository-wide `grep -rn` for each symbol cited here, to deduplicate against the 46 sections
  already written.

### [SECURITY] The model picker writes endpoint names and model ids into `innerHTML` unescaped

- **Location:** `static/js/modelPicker.js:954` (current-model label), `:612` (provider group header), fed by `:948` and `:412-421`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the module imports no escaping helper at all (`grep -n "esc" static/js/modelPicker.js`
  matches nothing), and two of its `innerHTML` sinks interpolate strings that come from the endpoint
  registry and from the endpoint's own model list:

  ```js
  // static/js/modelPicker.js:948, 952-954
  const displayName = modelId ? modelId.split('/').pop() : 'Select model';
  ...
  if (logo) {
    label.innerHTML = '<span class="model-picker-logo">' + logo + '</span> ' + displayName;
  ```
  ```js
  // static/js/modelPicker.js:612 — reached for every group keyed `~endpoint:<name>`
  + `<span class="mp-provider-name">${_providerGroupName(provider)}</span>`
  ```

  `_providerGroupName` (`:418-421`) returns everything after `~endpoint:` verbatim, and
  `_providerGroupKey` (`:412-417`) builds that key from `m.epName`, which `static/js/models.js:238`
  takes from `item.endpoint_name`. The server sets that field to the endpoint's stored name
  (`routes/model_routes.py:1593`) and the sibling model ids are whatever the endpoint's own model
  listing returned (`:1588`). The `displayName` sink is reached whenever `providerLogo(modelId)`
  matched, and those patterns are loose — `/minimax/i`, `/glm/i`, `/gpt/i`, `/nous|hermes/i`
  (`static/js/providers.js:11-90`, matched at `:93-99`) — so a model id such as
  `minimax/<img src=x onerror=…>` returned by a configured endpoint takes the `innerHTML` branch
  while a non-matching one takes `textContent`.
  Every other renderer of the same data escapes it: the picker's own row builder uses
  `nameSpan.textContent = m.display` (`static/js/modelPicker.js:489`) and the sidebar uses
  `epLabel.textContent = epName` (`static/js/models.js:401`).
- **Impact:** markup that arrives from a configured model endpoint, or that an admin types into an
  endpoint name, is parsed as HTML in the app's origin. `script-src` carries a nonce and no
  `'unsafe-inline'` (`core/middleware.py:143`), so injected `<script>` blocks and inline event
  handlers do not run; what remains reachable is markup substitution inside the picker (spoofed rows,
  injected links) and, since `img-src` allows `https:`, an outbound image request to a host named by
  the injected markup. The same unescaped-interpolation pattern also exists in the unreachable MCP
  panel (`static/js/admin.js:2076` builds `${statusText}` from `s.error`, `:2082` interpolates it into
  `list.innerHTML`); escaping it there is a one-line change, but see the dead-code finding below
  before touching that code.
- **Re-review (2026-10-05):** stands at low. The impact says injected script does not run; an
  injected `<iframe srcdoc>` that loads script from `cdn.jsdelivr.net` does (the policy finding in
  `core-auth-session`). This sink was not probed. Low is kept because the input comes from an
  endpoint an admin configured or a name an admin typed.
- **Fix:** escape both interpolations (`esc(displayName)`, `esc(_providerGroupName(provider))`) or
  build them with `textContent` as the rest of the module does.

### [BUG] The serve launch builds the venv activation and the model path without quoting, so a path containing a space is rejected or mis-parsed

- **Location:** `static/js/cookbookRunning.js:1982` and `:1984` (activation prefix), `static/js/cookbook.js:708`, `:761`, `:953` (model path)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_launchServeTask` builds the same activation prefix `_buildEnvPrefix` does, but
  without `_shellQuote`:

  ```js
  // static/js/cookbookRunning.js:1980-1985
  if (_envState.env === 'venv' && _envState.envPath) {
    const p = _venvRootFromPath(_envState.envPath);
    envPrefix = 'source ' + (p.endsWith('/bin/activate') ? p : p + '/bin/activate');
  } else if (_envState.env === 'conda' && _envState.envPath) {
    envPrefix = 'eval "$(conda shell.bash hook)" && conda activate ' + _envState.envPath;
  }
  ```
  ```js
  // static/js/cookbook.js:618-620 — the quoted form used by the download path
  parts.push('source ' + _shellQuote(activate));
  parts.push('eval "$(conda shell.bash hook)" && conda activate ' + _shellQuote(_envState.envPath));
  ```

  `POST /api/model/serve` re-parses whatever arrives with `shlex.split` and rejects anything that is
  not exactly two tokens (`routes/cookbook_helpers.py:1164-1168`, `:1194`). Measured by calling the
  real helper with the two strings above (synthetic paths):

  ```
  'source /Users/me/My Env/bin/activate' -> HTTP 400 Invalid env_prefix
  "source '/Users/me/My Env/bin/activate'" -> '[ -f "/Users/me/My Env/bin/activate" ] && source "/Users/me/My Env/bin/activate" || true'
  'conda activate /Users/me/My Env' -> HTTP 400 Invalid env_prefix
  ```

  The model path has the same shape. It is the free-text `model_path` field when set and otherwise
  the scanned directory plus the repo (`static/js/cookbookServe.js:1863`), and it is interpolated raw
  into `vllm serve ${modelName} …` (`static/js/cookbook.js:708`), `… --model-path ${modelName} …`
  (`:761`) and the diffusers launcher (`:953`), while the llama.cpp branch quotes the same value
  (`:834`, `const modelArg = needsGgufPrelude ? '"$MODEL_FILE"' : \`"${ggufPath}"\``). Validation
  accepts the unquoted form, so nothing catches it before the backend does:

  ```
  'vllm serve /Users/me/My Models/Qwen --port 8000' -> ACCEPTED
  ```

- **Impact:** an admin whose venv or model directory sits under a path with a space — common on
  macOS and Windows — gets `Failed to start: Invalid env_prefix` from the serve path
  (`static/js/cookbookRunning.js:2017`, which surfaces the FastAPI `detail`), or a backend that
  receives `--model-path /Users/me/My` and dies on argument parsing. The download path and the
  llama.cpp serve path accept the same paths, so the failure looks arbitrary. No injection follows:
  the server rejects shell metacharacters in the env prefix and in the command, so this is a
  functional bug rather than an escalation.
- **Fix:** quote the activation path in `_launchServeTask` with the same helpers `_buildEnvPrefix`
  uses (`_shellQuote`, `_psQuote`), and wrap `modelName` in `_shellQuote` at the three `cookbook.js`
  sites.

### [BUG] The API-endpoint form can never send `model_type`, so an image endpoint added there is stored as an LLM

- **Location:** `static/js/admin.js:1120-1121`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the add-endpoint handler reads a select that exists nowhere:

  ```js
  // static/js/admin.js:1120-1121
  const epType = el('adm-epType');
  if (epType) fd.append('model_type', epType.value);
  ```

  The id probe (`/tmp/audit-probe/check_ids2.mjs`, 6 HTML files scanned) lists `adm-epType` among the
  45 of 88 ids `admin.js` looks up that no HTML file defines. The sibling local-endpoint form has the
  control and sends it (`static/index.html:2223-2226`, `static/js/admin.js:1628`), and the route
  defaults the field to `llm` (`routes/model_routes.py:1997`, `model_type: str = Form("llm")`). The
  distinction is used downstream: `admin.js:533` renders an "Image" badge from `ep.model_type`,
  `static/js/models.js:243` and `static/js/tasks.js:1593` branch on it. No other client path sends
  `model_type` for an existing endpoint — `grep -rn "model_type" static/js/*.js` finds only the two
  form fields above, the serve-time registrations in `cookbookRunning.js` and `markdown.js`, and the
  readers.
- **Impact:** a diffusion or TTS endpoint added through the cloud/proxy form is stored as an LLM, so
  the model picker offers it as a chat model, with no UI path to correct it afterwards. Endpoints
  added through the local form are unaffected.
- **Fix:** add the LLM/Image select to the API form (reusing the options at `static/index.html:2223-2226`),
  or drop the dead lookup and let the endpoint list own the field.

### [DEAD-CODE] A third of `admin.js` cannot run: 45 of the element ids it looks up exist in no HTML file

- **Location:** `static/js/admin.js:2066` (`loadMcpServers`) through `:2836` (`initCalDAV`), with the unused functions at `:2414`, `:2482`, `:2689`, `:2740`, `:2768`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the id probe reports every id `admin.js` resolves through `el(...)`/`getElementById(...)`
  against all HTML in the tree:

  ```
  $ node /tmp/audit-probe/check_ids2.mjs
  HTML files scanned: 6 (static/index.html static/login.html static/modal-control-variants.html
  static/wave-variants.html static/whirlpool-variants.html website/index.html)
  ids referenced by admin.js: 88
  absent from every HTML file: 45
  adm-epMsg adm-epType adm-featureToggles adm-mcpAddBtn adm-mcpArgs adm-mcpCommand adm-mcpEnv
  adm-mcpEnvFields adm-mcpEnvRow adm-mcpHelp adm-mcpList adm-mcpMsg adm-mcpName adm-mcpPreset
  adm-mcpSseRow adm-mcpTransport adm-mcpUrl adm-ragAddDirBtn adm-ragDirInput adm-ragDirList
  adm-ragDropZone adm-ragFileInput adm-ragFileList adm-ragReloadBtn adm-ragStatus adm-tokenAddBtn
  adm-tokenCopyBtn adm-tokenList adm-tokenMsg adm-tokenName adm-tokenReveal adm-tokenScopes
  adm-tokenValue adm-whAddBtn adm-whList adm-whMsg adm-whName adm-whSecret adm-whUrl caldav-pass
  caldav-save-btn caldav-status caldav-test-btn caldav-url caldav-user
  ```

  That is the whole MCP (16 ids), RAG (9), API-token (8), webhook (7), CalDAV (6) and feature-toggle
  (1) markup. The entry points are null-guarded and return immediately — `admin.js:2068`
  (`if (!list) return;`), `:2795` (`if (!urlIn || !saveBtn) return;`) — and five of the functions are
  never called at all: `loadRag` (`:2414`), `initRag` (`:2482`), `loadWebhooks` (`:2689`),
  `initWebhookForm` (`:2740`) and `loadFeatures` (`:2768`) appear only in their own definitions and in
  calls from inside the dead cluster; `refreshAll` (`:3169-3176`) calls `loadMcpServers` and
  `loadTokens`, which return on the guard, and `initAll` (`:3155-3164`) calls `initMcpForm`,
  `initCalDAV` and `initTokenForm`, which do the same. `loadRag`'s own error path dereferences the
  same missing elements, so it would throw again inside the `catch`:

  ```js
  // static/js/admin.js:2455-2458
  } catch (e) {
    el('adm-ragDirList').innerHTML = '<div class="admin-error">Failed to load</div>';
    el('adm-ragFileList').innerHTML = '';
  }
  ```

  The retirement is undocumented — `grep -rn "adm-mcp\|adm-rag\|adm-wh\|adm-token\|caldav-url\|adm-featureToggles" tests/ docs/`
  finds nothing — while the comparable retirement next door is commented
  (`static/js/cookbook.js:2772-2775`: "Browse Ollama library popup removed … the handler below is a
  no-op now because the elements no longer exist"). One already-written section asserts the opposite
  of what this probe shows: `static-js-research-memory-rag` calls `static/js/admin.js:2416-2507` "the
  live replacements" for the retired `rag.js` panel, but `loadRag` is never called and its container
  does not exist.

  The CalDAV panel is not only dead markup; its route contract has also drifted. It reads
  `d.caldav_url` / `d.caldav_username` / `d.caldav_password` (`:2800-2802`) and posts the same three
  names (`:2811`), while `GET /api/calendar/config` returns `url` / `username` / `password`
  (`routes/calendar_routes.py:848-854`) and `POST /api/calendar/config` reads `body["url"]`, treating
  an absent `url` as a request to clear the account (`:865-867`, `_save_caldav_accounts(owner, [])`,
  returning `{"ok": True, "cleared": True}`).
- **Impact:** about 700 lines of admin UI ship that no user can reach, and a reader looking for the
  MCP, token, webhook or RAG admin surfaces finds them in `admin.js` and assumes they work. The
  CalDAV detail is a trap: restoring that markup as it stands would have "Save" delete the user's
  CalDAV account and report `Saved`.
- **Fix:** delete the unreachable blocks, or restore the markup — and if restored, re-point the
  CalDAV form at `/api/calendar/config/accounts` with the `url` / `username` / `password` keys the
  route actually uses.

### [DUP] Two port-parsing call sites bypass the helper extracted for them

- **Location:** `static/js/cookbookRunning.js:1944` and `:1949`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `cookbookPorts.js` was extracted so the regexes could be unit-tested without the
  browser-bound rest of `cookbookRunning.js` (`static/js/cookbookPorts.js:1-2`) and is already
  imported and used by that file (`:11`, `:301`, `:525`), yet `_launchServeTask` still inlines both:

  ```js
  // static/js/cookbookRunning.js:1944 and :1949
  const _pm = cmd.match(/--port[=\s]+(\d+)/) || cmd.match(/(?:^|\s)-p[=\s]+(\d+)/);
  const _tm = _t.payload._cmd.match(/--port[=\s]+(\d+)/) || _t.payload._cmd.match(/(?:^|\s)-p[=\s]+(\d+)/);
  ```
  ```js
  // static/js/cookbookPorts.js:8
  const m = s.match(/--port[=\s]+(\d+)/) || s.match(/(?:^|\s)-p[=\s]+(\d+)/);
  ```

  `tests/test_cookbook_port_parsing_js.py` loads only the helper file (`:14`), so the copies inside
  `_launchServeTask` are outside the suite that exists to cover this parsing.
- **Impact:** the comparison that decides whether a launch kills an already-running server on the
  same port is untested in two of its three copies; adding a flag form to the helper would silently
  stop matching there, and two servers would be left on one port.
- **Fix:** call `portOf(cmd)` and `portOf(_t.payload._cmd)` at both sites.
