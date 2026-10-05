# services: shell, STT, TTS, faces, youtube

## Overview

The service-layer modules behind command execution, speech and YouTube context:
`services/shell/service.py` is a standalone `ShellService` subprocess wrapper; `services/stt/stt_service.py`
and `services/tts/tts_service.py` are the multi-provider speech services (local Whisper/Kokoro, an
OpenAI-compatible `ModelEndpoint`, or the browser) plus the TTS disk cache; `services/youtube/youtube_handler.py`
does YouTube URL detection, transcript fetch, yt-dlp comment fetch and LLM context formatting;
`services/faces/__init__.py` is a one-line placeholder package; the four package `__init__` files
re-export the public names and `services/__init__.py` is the package facade.

The boundary with the neighbouring sections:

- `routes-shell` owns `routes/shell_routes.py`, the live shell and code-execution router. That
  router does **not** import this section's `ShellService`: the only importers are
  `services/__init__.py` and `tests/test_shell_service.py`. So the child-process behaviour
  `routes-shell` reports belongs to a second, separate implementation. This section owns
  `services/shell/service.py` itself and does not restate `routes-shell`'s findings.
- `routes-rest-media-files` owns `routes/tts_routes.py`, `routes/stt_routes.py` and
  `routes/upload_routes.py`. It already reports that the speech handlers run their blocking service
  calls on the request event loop (citing `services/tts/tts_service.py:189` and
  `services/stt/stt_service.py:144`); that finding is not repeated here.
- Other sections own the chat-side callers (`src/chat_handler.py`, `src/chat_processor.py`,
  `src/youtube_handler.py`), the settings store (`src/settings.py`), the `ModelEndpoint` rows the
  API providers read, and the router registration in `app.py`. They are read here only where a
  finding rests on them.

## Coverage

Line numbers refer to `2992bf6d368a` in the working tree; `git log --oneline -1` is `2992bf6d` and
`git status --porcelain` shows only the untracked `audit/` directory.

**Read fully:** all ten assigned files (1,101 lines).

| File | Lines |
| --- | ---: |
| `services/tts/tts_service.py` | 350 |
| `services/youtube/youtube_handler.py` | 302 |
| `services/stt/stt_service.py` | 208 |
| `services/shell/service.py` | 163 |
| `services/__init__.py` | 37 |
| `services/youtube/__init__.py` | 22 |
| `services/tts/__init__.py` | 9 |
| `services/shell/__init__.py` | 6 |
| `services/stt/__init__.py` | 3 |
| `services/faces/__init__.py` | 1 |

The faces package is one docstring line with no code and no importer (`grep -rn 'services\.faces'
--include='*.py' .` returns nothing outside the audit directory), so there is nothing in it to
review beyond that claim.

**Read partially:** the boundary code and callers the findings rest on:

- `src/chat_handler.py` at the YouTube preprocessing loop (`:145-175`)
- `src/chat_processor.py` at the non-YouTube URL filter (`:455-500`)
- `src/chat_helpers.py` at `extract_urls` (`:21-36`)
- `src/youtube_handler.py` in full (37 lines — it replaces its own `sys.modules` entry with the
  canonical module)
- the two speech routers `routes/stt_routes.py` and `routes/tts_routes.py` in full (57 and 87 lines)
- `routes/diagnostics_routes.py` at `GET /api/test/youtube` (`:73-92`)
- `app.py` at the service construction and router registration (`:556-557`, `:611-614`, `:756-763`)
- `src/settings.py` at `load_settings` and its cache (`:232-259`) and at the speech defaults
  (`:57-65`)
- `src/upload_limits.py` at the STT byte cap (`:56-58`, `:64-67`)
- `static/js/settings.js` at the STT and TTS forms (`:925-985`)
- `static/js/tts-ai.js` at the stats read and the client-side speed application (`:47`, `:50`,
  `:208`, `:316-317`)
- `static/js/voiceRecorder.js:31`
- `specs/search.md` at the YouTube section (`:105-109`)
- `specs/shell-mcp.md` at the `ShellService` description (`:7-11`, `:48`, `:139`)
- `requirements.txt`, `requirements-optional.txt` and `Dockerfile` (`:20-100`) for what the project
  actually installs
- `tests/test_shell_service.py` and `tests/test_stt_leak.py` in full
- and, for the cross-references above, the first finding of `routes-shell.md` and the whole of
  `routes-rest-media-files.md`

**Not read:**

- `routes/shell_routes.py` itself (another section's file — only that section's written findings
  were read)
- `routes/diagnostics_routes.py` beyond the YouTube test route
- `src/settings.py` beyond the cited region, so the settings POST route that writes the speech keys
  was not read here
- the `ModelEndpoint` model and the endpoint-probe machinery (`core/database.py`,
  `routes/model_routes.py`) the API-provider branches call
- the `faster-whisper`, `kokoro` and `yt-dlp` implementations themselves (none of the three is
  installed in this checkout, so their real load and fetch paths were exercised with fakes only)
- the rest of the front end's speech UI
- every test file other than the two named above

**Checks run:**

- eight URLs through the real `is_youtube_url` / `extract_youtube_id`
- a peak-RSS probe of `ShellService.execute` with `max_output=10` against an 80 MB stdout
- a probe that loads the STT model stand-in, changes the setting and calls `_get_whisper` /
  `get_stats`
- a probe that calls the real `get_stats()` of both speech services with the heavy imports faked to
  record what they construct
- `-X importtime` for `import services.stt.stt_service` against loading the same file directly by
  spec, and a check that importing `src.youtube_handler` still executes `services/__init__.py`
- greps for the `ShellService` callers, the `services.*` importers, the `is_youtube_url` callers,
  the `get_stt_service` callers, and `yt-dlp` across the repository, both requirement files and the
  Dockerfile

The 23 suites matching `ls tests | grep -iE 'shell|stt|tts|youtube|face|kokoro|speech|audio'` were
run — **150 passed**.

### [BUG] A YouTube-shaped URL with no extractable video id is dropped from both the transcript path and the web-fetch path

- **Location:** `services/youtube/youtube_handler.py:61` (with `:78` and the two callers, `src/chat_handler.py:149-152` and `src/chat_processor.py:461`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** detection is a substring test while extraction requires a host and path shape, so the two
  disagree for every YouTube page that is not a video:

  ```python
  def is_youtube_url(url: str) -> bool:                          # :61
      if not isinstance(url, str):
          return False
      return "youtube.com" in url or "youtu.be" in url           # :64
  ```

  Measured on the real functions:

  ```
  True  'dQw4w9WgXcQ'        https://www.youtube.com/watch?v=dQw4w9WgXcQ
  True  None                 https://www.youtube.com/playlist?list=PL1234567890
  True  None                 https://www.youtube.com/@SomeChannel
  True  None                 https://www.youtube.com/results?search_query=python
  True  None                 https://www.youtube.com/watch
  True  None                 https://example.com/post?ref=youtube.com
  True  None                 https://notyoutube.com/watch?v=abc
  ```

  Both callers read `is_youtube_url` as "this URL is fetched as YouTube". The chat path skips the URL
  when the id is missing (`src/chat_handler.py:148-152`):

  ```python
  for url in urls:
      if is_youtube_url(url):
          video_id = extract_youtube_id(url)
          if not video_id:
              continue
  ```

  and the context builder excludes every YouTube-shaped URL from the ordinary web fetch
  (`src/chat_processor.py:460-462`):

  ```python
  urls = extract_urls(message)
  non_yt_urls = [u for u in urls if not is_youtube_url(u)]
  skip_url_fetch = len(message) > 2000 or len(non_yt_urls) > 3
  ```

  `extract_urls` (`src/chat_helpers.py:23`) matches any `http(s)` URL, so a link whose path or query
  merely contains the substring qualifies too. The file's own comment at `:72-74` names this failure
  mode for the shapes it added prefixes for — "they must be extractable or the link is silently dropped
  (neither web-fetched nor transcript-fetched) by the chat pipeline" — and playlist, channel and
  `/results` URLs are still in it.
- **Impact:** a user who shares a playlist, channel or search-results link gets neither a transcript nor
  a fetched page for it, so the link contributes nothing to the model's context; because the injected
  `YOUTUBE_INSTRUCTION_PROMPT` (`:20-30`) is only added when an id was found, the model is not told to
  work from the link either. Nothing is surfaced to the user — the failure is a silent `continue` in one
  caller and a silent exclusion in the other. The video-URL flow the feature is built around is
  unaffected, and the raw URL text still reaches the model in the user message.
- **Fix:** use extraction as the YouTube test at both call sites (`video_id = extract_youtube_id(url)`;
  treat a missing id as "not a YouTube video" and let the URL fall through to the web-fetch path), or
  give `is_youtube_url` the same host and path check `extract_youtube_id` already applies.

### [DEPENDENCY] The comment fetch shells out to `yt-dlp`, which no requirement file or image installs

- **Location:** `services/youtube/youtube_handler.py:217` (with `_find_ytdlp` at `:39-45` and the failure branch at `:274-276`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `fetch_youtube_comments` runs `_find_ytdlp()` as the program name:

  ```python
  cmd = [
      _find_ytdlp(),
      "--skip-download",
      "--write-comments",
      "--extractor-args", f"youtube:max_comments={max_comments},all,100,0",
      "--dump-json",
      "--js-runtimes", "node",
      "--remote-components", "ejs:github",
      f"https://www.youtube.com/watch?v={video_id}",
  ]                                                              # :216-225
  ```

  and the helper falls back to the bare name (`:41-45`):

  ```python
  venv_bin = Path(sys.executable).parent / "yt-dlp"
  if venv_bin.exists():
      return str(venv_bin)
  found = shutil.which("yt-dlp")
  return found or "yt-dlp"
  ```

  Nothing installs it. `grep -rn "yt-dlp" -I .` (excluding `venv/`) returns only this file and its tests;
  the string appears in neither `requirements.txt` nor `requirements-optional.txt`, in no `apt-get
  install` list, and nowhere else in the `Dockerfile`. Measured here:

  ```
  $ ls venv/bin/yt-dlp
  ls: cannot access 'venv/bin/yt-dlp': No such file or directory
  $ venv/bin/python -c "import importlib.metadata as m; m.version('yt-dlp')"
  PackageNotFoundError: No package metadata was found for yt-dlp
  ```

  The Dockerfile installs nodejs, npm, chromium and tmux from apt (`:23-37`) and runs exactly two
  `pip install`s from the requirement files plus `python-magic` (`:78`, `:84`), so the shipped image has
  no yt-dlp either. The absence is caught and returned as a value rather than raised (`:274-276`):

  ```python
  except FileNotFoundError:
      logger.warning("yt-dlp not installed — cannot fetch comments")
      return {"success": False, "error": "yt-dlp not installed", "comments": []}
  ```
- **Impact:** on the container image and on any host that installed `requirements.txt`, the
  "Audience Reception" half of the YouTube breakdown never runs. `format_comments_for_context`
  returns `""` for a failed fetch (`:283-285`), so the context carries the transcript only, and the
  operator sees a warning in the log rather than a broken request. `requirements-optional.txt` is
  the project's declared home for feature extras, under the note "The app handles their absence
  gracefully". It lists five extras (faster-whisper, kokoro, ddgs, PyMuPDF and markitdown), and
  yt-dlp is not there, so nothing in the repository tells an operator the binary is needed. Nothing pins
  its version either, so the flags the command uses are the only record of what it expects.
- **Fix:** add `yt-dlp` to `requirements-optional.txt` with a one-line feature note (or install it in the
  image), name the binary in the module docstring, and state the version floor the flags assume.

### [BUG] The STT model setting has no effect once a model is loaded, and `/api/stt/stats` reports the new name as loaded

- **Location:** `services/stt/stt_service.py:58` (with `:66-67`, `:186`, `:191-192`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `_get_whisper` reads the setting only inside the one-time load:

  ```python
  def _get_whisper(self):                        # :58
      if self._whisper_model is None:            # :59
          ...
          settings = self._load_settings()       # :66
          model_size = settings.get("stt_model", "base")   # :67
          ...
          self._whisper_model = WhisperModel(model_size, device=device, compute_type=compute_type)  # :83
  ```

  while `get_stats` reports the current setting and the cached model's presence as though they agreed:

  ```python
  "model": settings["stt_model"],                # :186
  ...
  whisper = self._get_whisper()                  # :191
  stats["model_loaded"] = whisper is not None    # :192
  ```

  Measured with a model stand-in already loaded and the setting changed to `large-v3`:

  ```
  settings now say stt_model = large-v3
  _get_whisper() returns the previously loaded object: True
  get_stats() -> {'provider': 'local', 'model': 'large-v3', 'model_loaded': True, 'available': True}
  ```

  The settings UI posts the change on every select and input change and reports success
  (`static/js/settings.js:958`, message "Saved") with no restart note, and nothing resets the service:
  `grep -rn 'get_stt_service\|_stt_service' routes/ src/ app.py` finds only `app.py:760-761`. The settings
  store is not the cause — `load_settings` re-reads the file after a two-second cache
  (`src/settings.py:236-247`).
- **Impact:** an operator who switches the local STT model in the UI keeps transcribing with the model
  loaded at first use until the process restarts, and the status the UI reads names the new model with
  `model_loaded: true`, so the misreport is the only feedback. Changing the model before the first
  transcription does load the new one, so the failure needs one prior transcription. Local STT only:
  the endpoint branch reads `stt_model` per call and passes it to the API request (`:161`, `:171`).
- **Fix:** record which model was loaded and reload when the setting differs (or expose an explicit
  reload and call it from the settings save); at minimum report the loaded name rather than the
  configured one.

### [PERF] `GET /api/stt/stats` and `GET /api/tts/stats` load the local model as a side effect of a read

- **Location:** `services/stt/stt_service.py:191` (with `:51`, and `services/tts/tts_service.py:261`, `:274`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `get_stats` reaches the loader through `available` and then again for the counter:

  ```python
  if provider == "local":
      return self._get_whisper() is not None     # services/stt/stt_service.py:51
  ...
  "available": self.available and stt_enabled,   # :184
  ...
  if provider == "local":
      whisper = self._get_whisper()              # :191
      stats["model_loaded"] = whisper is not None
  ```

  `_get_whisper` constructs `WhisperModel(...)` (`:83`), which loads the checkpoint — and fetches it first
  when that size is not cached, which this checkout could not exercise because `faster-whisper` is not
  installed;
  `TTSService.get_stats` does the same through `_get_kokoro()` → `_KokoroPipeline()`
  (`services/tts/tts_service.py:154-157`, `:287-291`), whose `_init` imports `torch` and `kokoro` and
  loads Kokoro-82M onto the GPU (`:293-308`). Both stats handlers are `async def` and call the service
  directly (`routes/stt_routes.py:18-22`, `routes/tts_routes.py:24-28`), so the load runs on the request
  event loop. Measured by calling the real `get_stats()` with the heavy imports faked so the construction
  is visible:

  ```
  get_stats() -> {'provider': 'local', 'model': 'Kokoro-82M (GPU)', 'available': True, 'ready': True}
  side effects: ['_KokoroPipeline() constructed']
  STT get_stats() -> {'provider': 'local', 'model': 'base', 'model_loaded': True}
  side effects: ["WhisperModel('base', device='cpu')"]
  ```

  Both UIs call these endpoints as soon as the speech surface loads: `static/js/tts-ai.js:47` and
  `static/js/voiceRecorder.js:31`. This is the same blocking-call class as the second finding in
  `routes-rest-media-files.md`, which cites the synthesize and transcribe calls
  (`services/tts/tts_service.py:189`, `services/stt/stt_service.py:144`); the stats path is a different
  endpoint and a different trigger — a read that can start a model download.
- **Impact:** the first `/api/stt/stats` or `/api/tts/stats` after a restart can hold the event loop for
  the length of a model load — and, for a size not already cached, its download (hundreds of MB for
  Kokoro-82M, a Whisper checkpoint for STT) — with no
  progress reported and no bound, stalling unrelated requests on the worker. The load would otherwise
  happen at the first transcription, so the total cost is moved rather than added; what changes is that a
  status read now pays it. Only the `local` provider is affected — the `browser` and `endpoint:` branches
  of both `get_stats` methods touch no model (`services/stt/stt_service.py:190-196`,
  `services/tts/tts_service.py:273-278`).
- **Fix:** answer the stats read without loading — derive `model_loaded` from the cached instance
  (`self._whisper_model is not None`, `self._kokoro is not None`) and let `available` for `local` mean the
  library imports — or run the load off the loop with `asyncio.to_thread` and report a loading state.

### [PERF] `ShellService.execute` buffers the whole command output before applying `max_output`

- **Location:** `services/shell/service.py:62-66`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `communicate()` reads both pipes to EOF into memory and the cap is applied to the decoded
  string afterwards:

  ```python
  stdout_b, stderr_b = await asyncio.wait_for(
      proc.communicate(), timeout=timeout
  )
  stdout = stdout_b.decode(errors="replace")[:self.max_output]
  stderr = stderr_b.decode(errors="replace")[:self.max_output]
  ```

  `specs/shell-mcp.md:48` describes this class as "a small standalone subprocess abstraction with output
  caps". Measured with `max_output=10` against a command printing 80 MB:

  ```
  max_output: 10
  returned stdout length: 10
  exit_code: 0
  peak RSS before 99.5 MB -> after 252.1 MB (delta 152.6 MB)
  ```

  The `decode` allocates a second copy of the buffer before the slice. The `stream` generator
  (`:88-163`) has the same property in a different shape: it queues decoded lines into an unbounded
  `asyncio.Queue` for as long as the consumer reads.
- **Impact:** the cap limits what the caller sees, not what the process holds, so a command that emits a
  gigabyte drives the server's peak RSS to roughly the size of its output and can get the whole app
  OOM-killed — the outcome the cap reads as preventing. Nothing calls this class today (next finding), so
  it is a hazard for whoever wires it up rather than a live failure.
- **Fix:** stop reading once the cap is reached — `await proc.stdout.read(max_output + 1)` per stream with
  the process killed when either exceeds it — or drop `max_output` in favour of a documented caller-side
  bound.

### [DEAD-CODE] `ShellService` has no caller, and the shell it offers has no policy behind the "safe" wording

- **Location:** `services/shell/service.py:19` (with `:56-61` and `services/__init__.py:15`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the only references to the class are its definition, the two re-exports, and one test:

  ```
  $ grep -rn "ShellService" --include=*.py . | grep -v venv/
  ./services/__init__.py:15:from .shell import ShellService, ShellResult
  ./services/__init__.py:35:    "ShellService",
  ./services/shell/__init__.py:4:from .service import ShellService, ShellResult
  ./services/shell/__init__.py:6:__all__ = ["ShellService", "ShellResult"]
  ./services/shell/service.py:19:class ShellService:
  ./services/shell/service.py:24:        service = ShellService()
  ./tests/test_shell_service.py:10:ShellService = shell_service.ShellService
  ./tests/test_shell_service.py:51:        service = ShellService()
  ```

  The two `__all__` entries, the docstring example at `services/shell/service.py:24` and the test
  assignment are not callers, so the live-caller set is empty. The live shell path is
  `routes/shell_routes.py`'s own `_create_shell`/`_exec_shell` (reviewed in `routes-shell.md`). The one
  test constructs the class and drives `stream` with a fake process (`tests/test_shell_service.py:36-59`);
  `execute` has no test at all. `specs/shell-mcp.md` records the
  status: `:48` says it "does not own live route behavior", and `:139` calls `services.shell.service`
  "a transitional/simple facade". What the unreachable implementation offers is the unguarded form:

  ```python
  proc = await asyncio.create_subprocess_shell(
      command,
      stdout=asyncio.subprocess.PIPE,
      stderr=asyncio.subprocess.PIPE,
      cwd=cwd,
  )                                              # :56-61
  ```

  an arbitrary command string, a caller-supplied `cwd` (`:52`), and no allowlist, policy, admin check or
  workspace confinement — under a module docstring that reads "Shell service — safe command execution."
- **Impact:** two implementations of the same job, where the one a reader finds first by name advertises
  safety it does not implement: a future caller that imports `ShellService` instead of the route layer
  gets none of the guards `routes-shell.md` documents (admin gating, workspace confinement, output
  handling). Nothing is exploitable today because nothing calls it.
- **Fix:** delete the class, its re-exports and its test if no caller is planned, or state the missing
  policy in the docstring and point callers at the route layer. The "safe" wording in the module docstring
  and `specs/shell-mcp.md`'s "output caps" are the parts that mislead.

### [PERF] `services/__init__.py` makes every `services.*` import load five packages

- **Location:** `services/__init__.py:11-15`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the facade imports all five service packages eagerly:

  ```python
  from .search import SearchService, SearchResult, SearchResponse
  from .docs import DocsService, DocChunk, IndexResult
  from .research import ResearchService, ResearchResult, ResearchSource
  from .memory import MemoryService, Memory, MemorySearchResult
  from .shell import ShellService, ShellResult
  ```

  Python executes a package's `__init__` before any submodule import, so `import
  services.stt.stt_service` — a leaf whose only third-party import is `httpx` — loads all of them.
  Measured in this checkout:

  ```
  $ venv/bin/python -c "<time import services.stt.stt_service>"
  package import: 537.1 ms, 23 services.* modules loaded
  package import: 435.3 ms, 23 services.* modules loaded
  package import: 502.3 ms, 23 services.* modules loaded
  $ venv/bin/python -c "<load services/stt/stt_service.py by spec, no parent package>"
  direct file load: 57.9 ms
  direct file load: 47.6 ms
  direct file load: 52.9 ms
  $ venv/bin/python -X importtime -c "import services.stt.stt_service"
  import time:       163 |     452856 |         services.search.core
  import time:        65 |     508742 |   services.stt
  ```

  The search stack is the bulk of it: `services.search.core` alone is 453 of the 509 ms in the
  `services.stt` subtree.

  `src/youtube_handler.py:20-21` states the opposite intent — "Import the canonical module directly
  (services.youtube.youtube_handler) without triggering the heavy services/__init__.py top-level
  imports" — and that comment is wrong: `importlib.import_module("services.youtube.youtube_handler")`
  runs the parent package's `__init__` like any other import. Measured: immediately after `import
  src.youtube_handler` in a fresh interpreter, `'services.docs' in sys.modules` is `True`.
- **Impact:** every process, script and test that imports one service pays for all five (0.4-0.5 s here,
  dominated by the search stack), and a heavy or optional dependency added to any service package
  silently becomes a dependency of every other one — which is exactly what the shim comment says is being
  avoided. No breakage today: the modules loaded this way pull in no optional import at module level
  (`chromadb`, `torch`, `faster_whisper` and `kokoro` are all absent from `sys.modules` after the import).
- **Fix:** drop the eager re-exports from `services/__init__.py` (leave the docstring) or expose them
  lazily through a module `__getattr__`, and correct the comment in `src/youtube_handler.py`.
