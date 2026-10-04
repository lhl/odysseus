# services: hardware fit

## Overview

`services/hwfit/__init__.py` (empty), `services/hwfit/data/hf_models.json`,
`services/hwfit/data/mlx_community_models.json`, `services/hwfit/fit.py`,
`services/hwfit/hardware.py`, `services/hwfit/hf_discovery.py`,
`services/hwfit/image_models.py`, `services/hwfit/models.py`,
`services/hwfit/profiles.py`.

The hardware-fit service: `hardware.py` probes RAM, CPU and GPU locally or over SSH and caches the
result per target; `models.py` loads and merges the bundled and runtime model catalogues and holds
the quant, parameter-count and memory arithmetic; `fit.py` ranks catalogue rows against a detected
system and produces the fit level, speed estimate and composite score; `profiles.py` turns a model
plus a system into llama.cpp serve flags; `hf_discovery.py` refreshes the two runtime catalogues
from the Hugging Face API; `image_models.py` discovers and ranks image-generation models; and the
two JSON files are the bundled offline catalogue (924 and 629 rows).

The boundary: the four HTTP endpoints that call this service (`/api/hwfit/system`, `/models`,
`/profiles`, `/image-models`), their host/port validation, the caller-supplied `model_path` probe
and the missing admin gate on that router are `routes-rest-integrations-misc`, which reviews
`routes/hwfit_routes.py`. This section covers the layer behind those calls — how a host, port or
model path becomes a subprocess, an SSH invocation, a file read or an outbound request, and how a
catalogue row becomes a recommendation. `core/platform_compat.py` (the SSH argv builder) is
`core-data-platform`; `src/outbound_fetch.py` is `src-security`; the Cookbook's own GPU probe is
`routes-cookbook`; the front-end consumers of these results are
`static-js-cookbook-settings-models`; the catalogue import scripts are `scripts`. None of them were
reviewed here beyond the lines a finding cites. No module in this section reads the settings store
(`grep -rn 'settings' services/hwfit/*.py` returns nothing), so there is no settings dependency to
trace.

## Coverage

**Read fully:** the seven Python modules in scope, 3,173 lines.

| File | Lines |
| --- | ---: |
| `services/hwfit/hardware.py` | 907 |
| `services/hwfit/fit.py` | 876 |
| `services/hwfit/image_models.py` | 435 |
| `services/hwfit/hf_discovery.py` | 374 |
| `services/hwfit/models.py` | 343 |
| `services/hwfit/profiles.py` | 238 |

`services/hwfit/__init__.py` (0 — the file is empty). Also read fully as boundary material:
`routes/hwfit_routes.py` (456 lines — the only production caller of the service),
`core/platform_compat.py:172-185` and `:362-417` (`NVIDIA_PATH_CANDIDATES`, `SSH_PATH_OVERRIDE`,
`_ssh_exec_argv`, `run_ssh_command`), `app.py:811-812`, and the nine suites that pin this surface:
the 9 test files listed below.

- `tests/test_hwfit_remote_validation.py`
- `tests/test_hwfit_models_nonstring_fields.py`
- `tests/test_hwfit_params_b_malformed.py`
- `tests/test_hwfit_bandwidth_nonstring.py`
- `tests/test_hwfit_gpu_count_nonnumeric.py`
- `tests/test_hwfit_cpu_only_fallback.py`
- `tests/test_image_models_nonstring_search.py`
- `tests/test_image_models_nondict_system.py`
- `tests/test_serve_profiles.py`

**Read structurally, not line by line:**

- `services/hwfit/data/hf_models.json` (19,477 lines, 924 rows) and
  `services/hwfit/data/mlx_community_models.json` (15,727 lines, 629 rows). Both were parsed and
  every field of every row was type-censused with a script, and the head of each file plus
  representative rows were read
- the full text was not. The same census was run over the two runtime caches a live instance feeds
  into `get_models()` — `data/hwfit/hf_collection_models.json` (501 rows) and
  `data/hwfit/mlx_community_models.json` (659 rows), untracked runtime state present in this
  checkout. Result: `name`, `parameter_count`, `quantization`, `use_case`, `provider` are strings in
  every row of all four files
- `parameters_raw` and `context_length` are ints in every row
- `active_parameters` is an int or `null` (52 static rows)
- 29 static rows carry `release_date: null` (handled by the `newest` sort and by the front end, so
  not reported)

**Read partially:**

- the other eleven `tests/test_hwfit_*.py` suites by search (what each pins) rather than end to end
- `static/js/cookbook-hwfit.js:158-168` (`_downloadSourceRepo`) and `:884`, and
  `static/js/cookbookDownload.js:68`, `:477` (the consumers of `quant_repo`)
- `routes/cookbook_routes.py:3231-3237`
- `src/outbound_fetch.py:1-45` (docstring and private-address tables)
- the run's `header.md` and `coverage-boundaries.md`, and the two reference sections

**Not read:**

- `routes/_validators.py` (the host/port validators the routes call — their effect is recorded in
  `routes-rest-integrations-misc` and in `coverage-boundaries`)
- `core/platform_compat.py` outside the SSH and `which` helpers cited above
- the rest of `src/outbound_fetch.py` and `services/search/content.py`
- the Cookbook's own GPU probe and the rest of `routes/cookbook_routes.py`
- the rest of the front end
- `scripts/add_hwfit_models.py` and `scripts/import_from_vllm_recipes.py` (assigned to `scripts`)
- the catalogue files line by line
- the eleven other suites that were executed but not read

**Checks run:** `git log --oneline -1` → `2992bf6d fix(tools): publish blank-body files atomically`,
and `git status --porcelain` → only the untracked `audit/` directory, so the working tree matches the
commit for these paths and the line numbers below refer to it. The twenty suites matching this
module (`ls tests | grep -iE 'hwfit'` plus the three image/profiles suites that do not carry the
`hwfit` prefix) were run from the repository root with
`PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q -p no:cacheprovider …` — **126 passed, 1
warning** (the pre-existing SQLAlchemy `declarative_base()` deprecation). Five throwaway probes were
run with stdin scripts that replaced the transport with recorders; their output is quoted in the
findings that rest on them. No probe opened a real SSH connection or made an outbound network
request, and the only hardware probing any of them did was the local `/proc` and `/sys` reads the
service itself performs on this machine (no GPU operation was performed). Greps: the callers of `_read_file`/`_inspect_model_path`, `settings` in
`services/hwfit/`, the `_should_discover_variants` chain, and the consumers of `release_date` and
`quant_repo`. `./audit.py` was not run and no source, test, or run-level file was edited.

**Noted, not reported.:**

- Three things I checked that did not become findings. (1) A failed remote detection is cached as a
  result for `CACHE_TTL` (86,400 s): after one failed probe of a host, later `detect_system` calls
  for it return `{"error": "Cannot connect to …"}` without retrying (measured: 2 SSH attempts, then
  0). The `fresh=true` path the Rescan button uses bypasses the cache, so a user can recover
- it is a design choice, not a defect. (2) `refresh_mlx_community_cache` has no per-source error
  containment while its sibling `refresh_hf_collection_models_cache` catches per source, so an
  outage for `mlx-community` aborts the whole dynamic refresh
- the route reports that to the caller (`routes/hwfit_routes.py:209-213`) and the bundled catalogue
  still serves, so the impact is a failed refresh, not a wrong answer. (3)
  `_fetch_hf_image_collection_models` calls `data.get` on the parsed body without checking it is an
  object (`image_models.py:183`)
- a JSON array body raises `AttributeError` out of `get_image_models`

I could not establish that the Hugging Face collections endpoint returns a non-object for a valid
slug, so it is recorded here rather than as a finding.

### [RACE] One probe's SSH target is process-global, so concurrent requests swap hosts and cache each other's hardware

- **Location:** `services/hwfit/hardware.py:21-23` (the globals), `:27-31` (`_run` reads them), `:815` and `:904` (`detect_system` sets and clears them), `:689` (`_cache_by_host`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the target host of every probe is a module global that `detect_system` assigns at
  entry and clears at exit, and `_run` decides local-vs-remote from it at call time:

  ```python
  _remote_host = None  # set by detect_system(host=...)
  ...
  def _run(cmd):
      try:
          if _remote_host:
              ...
              r = run_ssh_command(_remote_host, _remote_port, cmd_str, ...)
          else:
              r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
  ```

  ```python
  _remote_host = host or None      # :815
  ...
  _remote_host = None              # :904
  _remote_platform = None          # :905
  _cache_by_host[cache_key] = (now, result)   # :906
  ```

  Nothing serialises this: there is no lock in the module, and the four endpoints are sync `def`
  handlers (`routes/hwfit_routes.py:186`, `:194`, `:319`, `:413`) that FastAPI runs in its worker
  threadpool, so two of them can be inside `detect_system` at once. Measured with a stdin probe that
  ran two threads — one `detect_system(fresh=True)` with no host, one
  `detect_system(host="audit-host.example", platform="linux", fresh=True)` — and replaced
  `run_ssh_command` with a recorder and `_run` with a wrapper that held the local thread before its
  first probe until the remote thread had set the global. No SSH connection was made:

  ```text
  local  request -> has_gpu=True gpu_name='NVIDIA GeForce RTX 4090' gpu_vram_gb=24.0
  remote request -> total_ram_gb=30.5 gpu_name='AMD GPU (card1)'
    ssh from 'A' -> 'audit-host.example' : cat /proc/meminfo
    ssh from 'local' -> 'audit-host.example' : nvidia-smi --query-gpu=memory.total,name --f
  cached ('_local', '', '') -> {'total_ram_gb': 125.1, 'gpu_name': 'NVIDIA GeForce RTX 4090', ...}
  cached ('audit-host.example', '', 'linux') -> {'total_ram_gb': 30.5, 'gpu_name': 'AMD GPU (card1)', ...}
  ```

  The local machine in that run is an AMD Strix Halo box whose own detection reports no NVIDIA GPU;
  the local request sent its `nvidia-smi` probe to the other caller's host and reported that host's
  GPU as its own.
  The remote request did the reverse: only its first probe went over SSH, and its result carries the
  local machine's CPU name and locally detected GPU.

- **Impact:** any two overlapping hardware-fit requests mix hardware between them, and the mixed
  result is stored in the process-wide cache under a key derived from the *caller's* own target
  (`_cache_key`, `:692-701`) for `CACHE_TTL` = 24 h (`:16`). A caller who asked for their own machine
  can be shown another user's host hardware, and every later local request — including the
  Cookbook's, which calls the same `detect_system` — sees the poisoned entry until someone passes
  `fresh=true`. The mixing also corrupts the remote side: a probe of `user@server` can report the
  server process's own CPU and GPU. Reachability is ordinary concurrency, not an attack: the SSH
  probes take seconds (15 s timeout, 5 s connect timeout per probe), and the routes that accept a
  host are reachable by any signed-in caller (`routes-rest-integrations-misc`). Two users pressing
  Rescan at the same time is enough; the non-admin gate recorded there makes it easier but is not
  required.
- **Fix:** stop using module globals for the probe target. Pass the target through an explicit
  parameter or a `threading.local()`/context object that `_run` and the `_detect_*` helpers read, and
  keep `_cache_by_host` keyed on that same per-call value. A module lock around `detect_system`
  would also close the race, at the cost of serialising all hardware probes.

### [BUG] A single non-string field in one catalogue row still aborts the whole listing and ranking pass

- **Location:** `services/hwfit/models.py:132` and `:89` (`name` → `infer_quantization_from_name`), `:140` (`name` in `is_prequantized`), `:154` (`parameters_raw`), `:206` (`active_parameters`), `:247-248` (`infer_use_case`); `services/hwfit/fit.py:406` (`_native_quant`), `:451` (`context_length`) and `:463` (`quant_upper`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the catalogue parsers harden `parameter_count` and `quantization` but not their
  siblings, so several fields still reach a string method or an arithmetic operator unchecked:

  ```python
  def infer_quantization_from_name(name):
      n = (name or "").lower()                      # models.py:89
  ...
  def is_prequantized(model):
      name = (model.get("name") or "").lower()      # models.py:140
  ...
  def params_b(model):
      raw = model.get("parameters_raw")
      if raw and raw > 0:                           # models.py:154
  ...
  def _active_params_b(model):
      if model.get("is_moe") and model.get("active_parameters"):
          return model["active_parameters"] / 1_000_000_000.0   # models.py:206
  ```

  Measured on the real entry points — a stdin probe replaced `models._load_model_file` so the
  catalogue contained one malformed row and one good row, then called the functions the service
  uses:

  ```text
  get_models()  -> AttributeError: 'int' object has no attribute 'lower'
  rank_models() -> AttributeError: 'int' object has no attribute 'lower'

  {"name": 123}                 -> is_prequantized / _normalize_model_entry / infer_use_case /
                                   _native_quant / analyze_model all raise AttributeError
  {"use_case": 5}               -> infer_use_case and analyze_model raise AttributeError
  {"context_length": "32768"}   -> analyze_model raises TypeError (min() on str and int)
  {"active_parameters": "1e9"}  -> analyze_model raises TypeError
  {"parameters_raw": "7000000000"} -> params_b raises TypeError ('>' on str and int)
  {"quantization": 8}           -> analyze_model raises AttributeError ('int' has no 'upper')
  ```

  `get_models()` runs `_normalize_model_entry` over every row (`:325`, `:334`) and `rank_models`
  runs `analyze_model` over every row, so one bad row takes down the whole pass rather than that row.
  This is the same class the project already fixed twice: `tests/test_hwfit_models_nonstring_fields.py`
  states "Non-strings are now treated as unknown" and pins a non-string `parameter_count` and a
  non-string `quantization`, and `tests/test_hwfit_params_b_malformed.py` pins a malformed
  `parameter_count` — but the tests only cover the fields that were fixed. The bundled catalogues and
  the two runtime caches in this checkout are clean (2,713 rows type-censused), so today this needs a
  malformed row to be introduced.
- **Impact:** a hand-edited catalogue entry, or a new row written by
  `scripts/add_hwfit_models.py` (it writes `services/hwfit/data/hf_models.json`), that carries a
  numeric `name`, a numeric `use_case`, a string `parameters_raw`/`active_parameters`/
  `context_length`, or a numeric `quantization` makes `get_models()` raise, which is the whole
  `/api/hwfit/models` response (the route calls `if not get_models()` unguarded at
  `routes/hwfit_routes.py:214`) and the whole Cookbook model list; `/api/hwfit/profiles` builds its
  catalogue from the same call. `params_b` already treats an unparseable `parameter_count` as unknown
  size for exactly this reason, so the intent is established.
- **Fix:** validate each row once at the load boundary (`_load_model_file` / `_append_models` in
  `get_models`, and the same loop for the dynamic caches): drop or coerce a non-string `name`,
  `use_case`, `quantization` or `format`, and treat a non-numeric `parameters_raw`,
  `active_parameters` or `context_length` as unknown, the way `params_b` already does. Extend
  `tests/test_hwfit_models_nonstring_fields.py` to cover the fields above.

### [BUG] A GGUF model's fit badge is computed against total multi-GPU VRAM while the fit decision used one GPU

- **Location:** `services/hwfit/fit.py:470` (the single-GPU pool), `:551` (the budget), `:563-568` (the badge thresholds)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `analyze_model` deliberately narrows the fit pool to one GPU for GGUF and
  GGUF-tier quants, because llama.cpp cannot shard them across cards, and then computes the
  perfect/good/marginal thresholds against the *total* pool:

  ```python
  if (is_gguf or is_gguf_quant) and not preq:
      effective_vram = single_gpu_vram          # :470, single_gpu_vram = gpu_vram / gpu_count
  ...
  budget = unified_budget if unified_memory else (effective_vram if run_mode == "gpu" else available_ram)  # :551
  if required_gb > budget:                                                                    # :552
      return None
  ...
      if gpu_vram >= required_gb * 1.50:        # :563  <- total, not the pool that serves it
          fit_level = "perfect"
      elif gpu_vram >= required_gb * 1.2:
          fit_level = "good"
  ```

  Measured with a stdin probe over a synthetic GGUF entry (32B, 8,192-token context) and a fixed
  24 GB per GPU; only the number of GPUs changes, and the quant filter is the one the UI sends:

  ```text
  estimate_memory_gb(Q4_K_M, 8192) = 21.16 GB
  gpu_count=1 total=24GB (per-GPU 24GB) -> fit_level='marginal' run_mode='gpu' required_gb=21.2 per-GPU ratio=1.13x
  gpu_count=2 total=48GB (per-GPU 24GB) -> fit_level='perfect'  run_mode='gpu' required_gb=21.2 per-GPU ratio=1.13x
  gpu_count=4 total=96GB (per-GPU 24GB) -> fit_level='perfect'  run_mode='gpu' required_gb=21.2 per-GPU ratio=1.13x
  ```

  The same model on the same 24 GB card goes from `marginal` to `perfect` when a second card is
  added that the GGUF path cannot use. The comment above the block states the intent — "GPU-only fit
  must leave real allocator/KV/runtime headroom … 141 GB on a 160 GB box is runnable, but not a
  comfortable perfect fit" — and the ratio the code actually needs for `good` is 1.2×, which the
  per-GPU pool does not reach here.
- **Impact:** on a multi-GPU box the Cookbook badges a GGUF model "Perfect" while the fit decision
  that produced it used one card holding the same model at 88% of its capacity — below the 1.2× the
  same block calls "good" and far below the 1.5× it calls "perfect". The label is a function of a
  pool the fit path discarded: the same model on the same 24 GB card reads `marginal` alone and
  `perfect` with a second card added. The model still runs, so this is a misleading recommendation
  rather than a broken one, but it is systematic — every GGUF row on a 2+-GPU machine is rated
  against a pool the fit decision did not use, and `fit_level` is what the user sorts and filters
  on. Whether llama.cpp may actually spread such a model across cards depends on the serve command
  the Cookbook builds, which is outside this section; the inconsistency is inside `analyze_model`.
  Prequantized (AWQ/GPTQ/FP8) rows are unaffected, because their `effective_vram` is already the
  total.
- **Fix:** use the pool the fit decision used in the three comparisons — `effective_vram` instead of
  `gpu_vram` — so the badge and `budget` cannot disagree. The variable is already in scope and equals
  `gpu_vram` for the sharded path, so the change is local.

### [ERROR-HANDLING] A failed image-model discovery marks its cache fresh, blanking the image list for 30 minutes

- **Location:** `services/hwfit/image_models.py:189` (with the freshness check at `:172-173`, the TTL at `:33`, and the per-collection `except: continue` at `:178-182`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** every collection fetch is individually tolerated, and the cache timestamp is written
  unconditionally afterwards, so a total failure is stored as an empty, fresh result:

  ```python
  for slug, mlx_only in [...]:
      url = f"https://huggingface.co/api/collections/{slug}"
      try:
          ...
          with urllib.request.urlopen(req, timeout=2.5) as resp:
              data = json.loads(resp.read().decode("utf-8", "replace"))
      except Exception:
          continue
      ...
  _HF_COLLECTION_CACHE["ts"] = now            # :189 — runs even when all seven fetches failed
  _HF_COLLECTION_CACHE["models"] = models
  ```

  Measured with a stdin probe that replaced `urllib.request.urlopen` with a function that always
  raises `OSError` (no real request was made):

  ```text
  get_image_models() #1 -> 0 models, 7 outbound attempts
  get_image_models() #2 -> 0 models, 0 further outbound attempts (cache treated as fresh)
  cache rows stored: 0 | TTL: 1800 s
  ```

  `IMAGE_MODEL_REGISTRY` is empty (`:14`, deliberately), so those seven collections are the only
  source of image rows, and nothing clears this cache on demand: the route's `fresh` parameter is
  passed to `detect_system` only (`routes/hwfit_routes.py:418`), and `rank_image_models` takes no
  such argument (`:453`).
- **Impact:** one transient DNS, TLS or timeout failure across all seven fetches — each with a 2.5 s
  timeout — leaves the Cookbook's image-model list empty for 30 minutes with no retry in the window,
  and the UI's Rescan cannot force one. A partial failure is handled correctly: the rows that
  succeeded are kept and the rest are skipped, which is the behaviour the sibling
  `refresh_hf_collection_models_cache` documents. The bug is only the total-failure case, where
  "nothing came back" is recorded as "this is what there is".
- **Fix:** only write `_HF_COLLECTION_CACHE["ts"]` when at least one collection returned a body (or
  store the failure count and retry sooner), and leave the previous rows in place when nothing was
  fetched. Exposing a force flag through `rank_image_models` would let the Rescan button clear it too.

### [SECURITY] The collection fetch follows a next-page URL taken from the response's `Link` header, to any host and with no body cap

- **Location:** `services/hwfit/hf_discovery.py:286-287` (with `_next_link` at `:267-270` and the loop at `:283-285`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the pagination URL is read out of the response header and used as the next request
  URL verbatim, with no host allowlist and no redirect policy of its own:

  ```python
  while url and pages < max_pages:                       # :283
      req = urllib.request.Request(url, headers={"User-Agent": "odysseus-hwfit/1.0"})
      with urllib.request.urlopen(req, timeout=timeout) as resp:
          payload = json.load(resp)                      # :286 — no size cap
          url = _next_link(resp.headers.get("Link"))     # :287
  ...
  def _next_link(header):
      m = re.search(r'<([^>]+)>;\s*rel="next"', header)
      return m.group(1) if m else None
  ```

  Measured with a stdin probe that served the first response with
  `Link: <http://127.0.0.1:9/internal-admin-api>; rel="next"` (no real request was made):

  ```text
  pages fetched: ['https://huggingface.co/api/collections?owner=Qwen&limit=100&expand=true',
                  'http://127.0.0.1:9/internal-admin-api']
  rows: ['Qwen/Qwen3-8B']
  ```

  The second URL is fetched and its rows are merged into the catalogue that `get_models()` serves.
  The repository already owns a guarded transport for exactly this shape —
  `src/outbound_fetch.py` (private-address blocking, one-resolution-per-hop DNS pinning, redirect
  handling, body budgets), used by `services/search/content.py` — and this module does not use it.
- **Impact:** the page-2 origin is chosen by the response, so a hostile or compromised
  `huggingface.co` answer, or anything that terminates its TLS, can make the server issue up to 19
  further GETs to arbitrary URLs — loopback, link-local and RFC1918 included — and feed their JSON
  into the model catalogue, which the Cookbook then offers for download. The precondition is control
  of that HTTPS response, which is why this is low and not higher; the first request is to a fixed
  host. Independently, `json.load(resp)` buffers the body without a limit, so an oversized response
  is read into memory before anything inspects it.
- **Fix:** pin pagination to the API origin — resolve the next link with `urllib.parse.urljoin`
  against `HF_COLLECTIONS_URL` and reject a result whose scheme/host differ, or rebuild the query
  from a page/cursor field — and read the body through a capped reader (the constants and helpers in
  `src/outbound_fetch.py` are the project's own answer to both).

### [DEAD-CODE] `_should_discover_variants` returns a literal `False`, so image-model quant-variant discovery never runs

- **Location:** `services/hwfit/image_models.py:258-259` (with its only gate at `:290`, the consumer at `:368`, and the unused seed lists at `:29-30`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the whole variant-discovery chain hangs off one function that is hardcoded off:

  ```python
  def _should_discover_variants(repo_id: str) -> bool:
      return False
  ```

  ```python
  def _merge_quant_repos(model):
      ...
      if _should_discover_variants(repo_id):                 # :290 — never true
          discovered = _discover_quant_repos(...)
  ```

  `_discover_quant_repos` is the only caller of `_best_variant_repo`, which is the only caller of
  `_hf_model_search` and `_variant_score`; `_HF_VARIANT_CACHE` (`:34`) and
  `_HF_SEARCH_DISABLED_UNTIL` (`:35`) are written only from that chain, and `HF_IMAGE_REPO_SEEDS` /
  `HF_MLX_IMAGE_REPO_SEEDS` (`:29-30`, both empty) have no reader anywhere. Measured:

  ```text
  _should_discover_variants: False
  merged quant_repos: {} | searches run: []
  ```

  Every row built by `_collection_item_to_model` starts with `"quant_repos": {}` (`:157`), so
  `rank_image_models` always reports `quant_repo = None` (`:368`), and the front end falls back to
  the base repo id for the download source (`static/js/cookbook-hwfit.js:168`, `:884`;
  `static/js/cookbookDownload.js:68`).
- **Impact:** the FP8/GGUF variant repos this code is written to find are never offered, so an image
  model that has a quantized sibling is presented with only its base repo as the download source. The
  cost is not only the missing feature: the chain is about 90 lines (`image_models.py:194-283`)
  including the module's only Hugging Face search call, its scoring heuristic and its 10-minute
  failure backoff, and the tests
  monkeypatch `_discover_quant_repos` (`tests/test_image_models_nonstring_search.py`), which reads as
  if the path were live. A literal `return False` with no comment also hides whether this is a
  deliberate kill switch or a debugging leftover.
- **Fix:** pick one. If variant discovery is retired, delete `_should_discover_variants`,
  `_discover_quant_repos`, `_best_variant_repo`, `_variant_score`, `_hf_model_search`, the two
  caches, the two empty seed lists and the `quant_repos` plumbing, and drop the now-pointless
  monkeypatches in the tests. If it is meant to be on, give the predicate a documented condition and
  a test that exercises the discovery path end to end.
