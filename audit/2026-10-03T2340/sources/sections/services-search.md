# services: search

## Overview

The search implementation: `services/search/__init__.py` (the export surface),
`services/search/providers.py` (the SearXNG, Brave, DuckDuckGo, Google PSE, Tavily and Serper
calls plus the settings/key lookups they read), `services/search/core.py` (the provider chain,
the cached retry orchestrator, `comprehensive_web_search`, and the config accessors),
`services/search/content.py` (the guarded page fetch and its HTML/PDF/text extraction),
`services/search/query.py` (query enhancement and the cache-duration heuristic),
`services/search/ranking.py` (result ordering), `services/search/analytics.py` (the query
recorder and its stats surface), `services/search/cache.py` (the cache directories and the LRU
sweep), and `services/search/service.py` (the async `SearchService` facade).

The boundary: the four HTTP handlers that call into this module and their authentication are
`routes-rest-integrations-misc` (`routes/search/search_routes.py`), which already reports that
both search POST handlers run this synchronous code on the event loop — that defect is not
restated here. The SSRF guard and pinned transport that `content.py` delegates to live in
`src/outbound_fetch.py` and are `src-security`; the settings store these providers read is
`src-memory-rag`/`src-platform`; the chat, agent-tool, deep-research and research-handler call
sites are their own sections and are cited here only where a finding lands in them.

## Coverage

**Read fully:** all nine assigned files (2,222 lines): `providers.py` (641), `core.py` (478),
`content.py` (442), `ranking.py` (164), `query.py` (149), `analytics.py` (148), `service.py`
(102), `cache.py` (63), `__init__.py` (35). Also read fully for the boundaries the findings
rest on: `routes/search/search_routes.py` (111), `src/outbound_fetch.py` (354),
`src/settings_scrub.py` (70), `src/agent_tools/web_tools.py` (171), `src/search/*` (eight files:
six `sys.modules` aliases, a re-exporting `ranking.py`, and the package `__init__.py`), and
`specs/search.md`.

**Read partially:** `src/settings.py` at `DEFAULT_SETTINGS`' search keys (`:66-95`) and
`load_settings`/`save_settings`; `routes/auth_routes.py` at `GET`/`POST /api/auth/settings`
(`:715-755`); `app.py` at the auth-exempt lists (`:264-296`) and the bearer/cookie branch
(`:470-500`); `src/deep_research.py` at `_search` (`:560-607`), `_fetch_and_extract` (`:609-630`)
and the search-unavailable report path (`:326-340`); `services/research/research_handler.py` at
`call_research_service` (`:240-295`) and `_save_result` (`:209-231`); `src/service_health.py` at
`_searxng_instance`/`searxng_health` (`:216-255`); `src/chat_processor.py` at the web-search and
URL-prefetch call sites (`:440-470`); `.gitignore` at `*.cache`/`cache/` and
`**/search_analytics.json` (`:59-60`, `:111`); and the test suites listed below for what they
already pin.

**Not read:** the front end beyond `static/js/settings.js:1106` (`search_url` is posted
unvalidated) — `static/js/search.js`, the compare-mode and research-panel search callers, and
the admin search panel were not read; the pinned SearXNG image, its config and
`scripts/migrate_searxng_settings.py`; `src/tool_execution.py` and `src/session_search.py`
(other sections' search call sites); the rest of `services/research/*`, `src/chat_processor.py`
and `src/deep_research.py`; `src/constants.py` beyond the fetch caps and data dir; the tests
beyond the suites run; and every other `services-*` section.

**Checks run:** five throwaway probes under `/tmp` (not part of the target tree), each quoted in
the finding it settles — the Google PSE 403 probe (`probe_search_cred.py`), the
malformed-provider-row probe (`probe_search_rows.py`, which also holds the large-page timing
case), a dedicated `SearchService` probe (`probe_search_service.py`), an AST call-site probe for
the exported entry points (`probe_search_callsites.py`), and the settings-scrub probe — plus two
one-line checks: `issubclass(httpx.HTTPStatusError, httpx.RequestError)` → `False`, and `wc -l`
for the line counts above. Also the greps recorded in the findings
(`searxng_search_results` / `invalidate_search_cache` / `get_search_stats` / `_record_query`
across the repository) and `git log -S`. The large-page probe (1.37 MB of HTML through the real
extractor) took 1.9 s with the four summarizer helpers at 0.02 s, so the extraction cost is
bounded by the 2 MB soft cap and is not reported. The suites that import
this module were discovered with
`grep -rl "services\.search\|src\.search\|services/search\|src/search" tests/*.py` (32 files)
plus `tests/test_search_query_nonstring.py`, which loads `query.py` by path — **230 passed**. The
broader set the assignment names, `ls tests | grep -iE 'search|searxng|ddg|og_image|analytics|query|ranking|content'`
(74 files), was also run: 73 files, **391 passed, 1 skipped**. The 74th,
`tests/test_owned_document_query.py`, fails collection inside that batch
(`ModuleNotFoundError: No module named 'src.agent_tools.document_tools'; 'src.agent_tools' is
not a package`) and passes alone (2 passed); its subject is the document tools, not this
section, so it is recorded here and not reported as a finding.

### [SECURITY] An upstream HTTP error status puts the Google PSE API key into the log, the returned context and the research report

- **Location:** `services/search/providers.py:487-501` (with `:472-477`, `:325-330`, `:553-558`, `:614-619`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** all four keyed providers call `raise_for_status()` inside a `try` that catches
  only `httpx.RequestError` and `RateLimitError`. Google PSE is the one that carries its key in
  the query string:

  ```python
  params = {
      "key": api_key,              # providers.py:473
      "cx": cx,
      "q": query,
      "num": min(count, 10),
  }
  ...
      response.raise_for_status()  # :495
  except httpx.RequestError as e:
      error_logger.error(f"Google PSE search failed: {e}")
      return []
  except RateLimitError as e:
      error_logger.error(str(e))
      return []
  ```

  `httpx.HTTPStatusError` is not a subclass of `httpx.RequestError`
  (`venv/bin/python -c "import httpx; print(issubclass(httpx.HTTPStatusError, httpx.RequestError))"`
  → `False`), so a non-429 error status escapes the provider. httpx builds that exception's
  message from the request URL, which contains the key. Probe with a fake 403 whose request URL
  is built from the provider's own `params` (the key below is a synthetic placeholder; it is
  shown as `[REDACTED]` here and is not a value from the tree):

  ```
  $ PYTHONPATH=. venv/bin/python /tmp/probe_search_cred.py
  === 1. direct provider call ===
  raised: HTTPStatusError
  message contains the key: True
  message: Client error '403 Forbidden' for url
    'https://www.googleapis.com/customsearch/v1?key=[REDACTED]&cx=cx-probe&q=probe+query&num=5'
  ...
  === 2. comprehensive_web_search context string ===
  returned string contains the key: True
  returned string: Web search failed — all providers errored or returned empty. Tried:
    google_pse:error: Client error '403 Forbidden' for url
    'https://www.googleapis.com/customsearch/v1?key=[REDACTED]&cx=cx-probe&q=probe+query&num=5'
  ```

  (The `...` stands for the probe's other output, and every occurrence of the synthetic key
  value is shown as `[REDACTED]`.) The same probe printed the module log line with the key in it:
  `Comprehensive search: google_pse attempt 1 failed: Client error '403 Forbidden' for url '...key=[REDACTED]...'`
  (`core.py:296`). Three sinks follow from the one missing catch: the app log, the context
  string built at `core.py:305-308`, and the research report — `src/deep_research.py:591` stores
  `f"{prov}: {e}"` in `_last_search_error`, which `:328-336` interpolates into the returned
  "**Search unavailable**" report, and `services/research/research_handler.py:209-229` persists
  that result to `data/deep_research/<session_id>.json`. The route layer passes the same text to
  the caller unchanged: `routes/search/search_routes.py:108-109` returns
  `{"error": str(e)}` from `/api/search/query`, a route that is authenticated but not
  admin-gated. The existing `tests/test_search_provider_json.py` pins the malformed-JSON case
  (HTTP 200), not the error-status case, and no suite exercises a provider's error-status path
  (`tests/test_search_content_extraction_parity.py` covers `HTTPStatusError` for
  `fetch_webpage_content`, a different function).
- **Impact:** the operator's Google API key — a billable credential — reaches places it should
  never be. The trigger is an upstream non-429 error status, which is exactly what a restricted,
  expired or over-quota key produces: on any such failure the key is written to the application
  log at WARNING, and when no provider in the chain returns results it is embedded in the text
  returned to the caller — which the agent search tool hands back as its output
  (`src/agent_tools/web_tools.py:76-80`) and which the chat prefetch path inserts as search
  context (`src/chat_processor.py:446-449`) — and written into a persisted research report. Any
  authenticated user can read it from the `/api/search/query` response body by selecting
  `google_pse`; nothing in the request is required beyond that. Brave, Tavily and Serper send
  their key in a header, so their escaped `HTTPStatusError` leaks the request URL and the query
  but not the credential. The project already treats this as a rule on the adjacent URL-fetch
  path: `src/chat_processor.py:467-470` and `:481-483` reduce a failed fetch to a
  transport-owned status because "the URL and exception can both contain signed-query
  credentials" and exception text must never reach the model.
- **Fix:** add `except httpx.HTTPStatusError` to the four providers (returning `[]` and logging a
  status-only message), or raise a status-only message instead of letting httpx build one from
  the URL. Redacting the URL is not enough on its own for the Google PSE case, because the key is
  a query parameter of a URL that is otherwise safe to show.

### [DEAD-CODE] The caching, retry and analytics half of the search module has no caller

- **Location:** `services/search/core.py:136-214` (`searxng_search_results`), `:220-244` (`invalidate_search_cache`), `services/search/analytics.py:97-120` (`_record_query`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `searxng_search_results` is the only function that writes the search disk
  cache, the only caller of `_record_query`, and the only caller of `cleanup_cache` for search
  entries; `invalidate_search_cache` only deletes entries that nothing writes. Nothing in the
  repository calls it. An AST probe over every `.py` file outside `tests/` and
  `services/search/` that matches `Name`, `Attribute` and string constants against the exported
  names:

  ```
  $ venv/bin/python /tmp/probe_search_callsites.py
  searxng_search_results: 2 reference(s) outside tests/ and services/search/
      ./services/search/__init__.py:28     (the __all__ list)
      ./src/search/__init__.py:22          (the __all__ list)
  invalidate_search_cache: 2 reference(s) ...
      ./services/search/__init__.py:25
      ./src/search/__init__.py:19
  get_search_stats: 2 reference(s) ...
      ./services/search/__init__.py:24
      ./src/search/__init__.py:18
  ```

  Inside the package the only other references are the `_record_query` calls at `core.py:158`
  and `:193`, both inside `searxng_search_results`, and the import at `:15`
  (`grep -n "searxng_search_results\|invalidate_search_cache\|get_search_stats\|_record_query"
  services/search/*.py`). `git log -S "searxng_search_results" -- routes/` is
  empty, so no route in this history ever called it. The tests that exercise the path do so
  directly (`tests/test_search_cache_invalidation.py` builds the cache key by hand,
  `tests/test_services_search_analytics_defaults.py` calls `_record_query`), which is why the
  gap is not visible in the suite. The spec still describes it as live: `specs/search.md:36`
  says `comprehensive_web_search()` "coordinates ... cache invalidation, and analytics", and
  `:127` says search cache and analytics state live under the data dir — as do
  `.gitignore:59-60` and `:111`.
- **Impact:** nothing user-visible breaks, but the mechanisms the spec and the comments describe
  do not exist at runtime: every search goes to the provider, `data/cache/search/` is never
  written, `data/logs/search_analytics.json` is never written, and there is no stats surface
  (`get_search_stats` has no caller and no route serves it). `_cache_duration_for_query`
  computes a 24-hour TTL for reference queries and 30 minutes for news queries that nothing ever
  uses — and if the path were reconnected, `cleanup_cache(..., timedelta(hours=1))` at `:207`
  would evict any entry older than an hour on the next write, cutting the 24-hour TTL short.
  An operator tuning `search_result_count` or reading `specs/search.md` for how caching works is
  reading about code that does not run.
- **Fix:** either delete `searxng_search_results`, `invalidate_search_cache`, `get_search_stats`,
  `analytics.py`, `cache.py` and their exports (the tests pin behaviour no caller can reach), or
  route the standalone search path through `searxng_search_results` so the documented cache and
  analytics are live. Reconnecting it also means fixing the TTL mismatch and adding a caller for
  `invalidate_search_cache`, which nothing calls today.

### [TYPE-SAFETY] A provider row with a non-string field aborts the whole search instead of dropping one result

- **Location:** `services/search/core.py:361` and `:412` (with `services/search/ranking.py:106-112`, `services/search/providers.py:175-181`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the SearXNG parser copies upstream field values through with only a default, and
  every consumer treats them as strings:

  ```python
  # providers.py:176-181
  return [
      {
          "title": r.get("title", ""),
          "url": r.get("url", ""),
          "snippet": r.get("content", ""),
      }
      ...
  ```

  A JSON `null` is *present*, so `.get("content", "")` returns `None`; a number or list is passed
  through as-is. Probe (provider stubbed, fetches stubbed, no network):

  ```
  $ PYTHONPATH=. venv/bin/python /tmp/probe_search_rows.py
  === A. provider row with a non-string snippet (int) ===
  raised: TypeError - object of type 'int' has no len()
  === B. provider row with a null snippet (JSON null survives .get(x, '')) ===
  raised: TypeError - 'NoneType' object is not subscriptable
  === C. provider row with an unhashable url ===
  raised: TypeError - unhashable type: 'list'
  ```

  The three failures are at `ranking.py:109` (`len(snippet)`), `core.py:412`
  (`result['snippet'][:200]`) and `core.py:361` (`_url_index`), in that order. Ranking is called
  at `core.py:318` with no `try` around it, and the formatting loop at `:409-412`
  slices `result['snippet']` directly, so a single bad row in the result list takes the whole
  call down. The caller sees an error string rather than the results that did parse
  (`src/agent_tools/web_tools.py:66-70` returns `web_search failed: TypeError: ...`;
  `routes/search/search_routes.py:64-66` returns `{"error": ...}`). The fetch path right beside
  it does the opposite — `core.py:374-382` catches per-URL exceptions and drops the one page —
  which is the behaviour this path is missing.
- **Impact:** a provider that returns one row with `"content": null` (or a non-string title, or a
  list-valued url) fails the entire search, including the results from the other rows and the
  other providers, instead of dropping the bad row. The trigger requires the upstream body to
  carry a non-string field; I did not establish that a stock SearXNG emits one, and the keyed
  providers' own fields are strings in their documented responses, so this is a robustness gap
  rather than a reproducible failure against a known provider. Its cost is one wasted search per
  occurrence plus a confusing `TypeError` in the log.
- **Fix:** coerce at the parse boundary — `str(r.get("title") or "")` and the same for `url` and
  `content` — or skip a row whose fields are not strings, matching the per-URL `except` the fetch
  loop already uses.

### [BUG] `SearchService.fetch_content` cannot be called: an instance attribute shadows the method, and the method awaits a synchronous dict

- **Location:** `services/search/service.py:43-45`, `:96-98`
- **Severity:** low
- **Disposition:** next
- **Evidence:** `__init__` stores the constructor flag under the same name as the method:

  ```python
  def __init__(self, default_depth: int = 1, fetch_content: bool = True):
      self.default_depth = default_depth
      self.fetch_content = fetch_content        # service.py:45

  ...
      async def fetch_content(self, url: str) -> Optional[str]:   # :96
          """Fetch content from a URL."""
          return await fetch_webpage_content(url)                 # :98
  ```

  The instance attribute wins, so the public call raises before the method body runs, and an
  unbound call reaches a second failure:

  ```
  $ PYTHONPATH=. venv/bin/python -u /tmp/probe_search_service.py
  instance call  -> TypeError - 'bool' object is not callable
  unbound call   ->
  Traceback (most recent call last):
    File "/tmp/probe_search_service.py", line 17, in <module>
      asyncio.run(svc_mod.SearchService.fetch_content(inst, "https://example.com"))
  TypeError: object dict can't be used in 'await' expression
  ```

  `fetch_webpage_content` (`services/search/content.py:181`) is a plain `def` returning a dict,
  and the annotation says `Optional[str]`. `self.fetch_content` is never read anywhere else in
  the file, so the attribute is only a collision. `tests/test_searchservice_search_call.py`
  covers `search()` only; no test calls `fetch_content`. `specs/search.md:11` and `:38` document
  `SearchService` as the exported async facade, and `services/__init__.py:19` re-exports it,
  although no production module in the repository constructs it (the same AST probe finds
  `SearchService` outside this package only in the two `__all__` lists).
- **Impact:** a documented, exported API method is unusable in both directions — the natural call
  raises `TypeError: 'bool' object is not callable` and the only way to reach the body raises
  `TypeError: object dict can't be used in 'await' expression`. Because nothing in the repository
  calls `SearchService`, no shipped flow breaks; the cost lands on anyone who follows the spec
  and uses the facade, and on the next reader who assumes the class works.
- **Fix:** rename the constructor attribute (`self._fetch_content` or `self.should_fetch_content`),
  and make the method either synchronous (`return fetch_webpage_content(url)`) or offload it
  (`return await asyncio.to_thread(fetch_webpage_content, url)`) with the annotation corrected to
  `dict`.

### [SECURITY] The configured SearXNG URL is returned verbatim, including any userinfo or query credentials

- **Location:** `services/search/core.py:72` (with `services/search/providers.py:41-47`, `src/settings_scrub.py:66-70`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `get_search_config` copies the admin's URL into the response with no redaction:

  ```python
  # core.py:71-72
  if provider == "searxng":
      from .providers import _get_search_instance
      config["search_url"] = _get_search_instance()
  ```

  `_get_search_instance` only strips whitespace and a trailing slash
  (`providers.py:44-46`), so userinfo and query parameters survive. Probe:

  ```
  $ PYTHONPATH=. venv/bin/python - <<'PY'   (settings stubbed; URL value is a placeholder)
  get_search_config()['search_url'] -> http://searx-user:[REDACTED]@searx.internal:8080/v1?api_key=[REDACTED]
  scrub_settings keeps search_url -> http://searx-user:[REDACTED]@searx.internal:8080/v1?api_key=[REDACTED]
  scrub_settings blanks a key-shaped neighbour -> ''
  ```

  `GET /api/search/config` is served to any authenticated caller
  (`routes/search/search_routes.py:42-44`), and the same value reaches a wider audience through
  `GET /api/auth/settings`, which is in `AUTH_EXEMPT_EXACT` (`app.py:271`) and returns
  `scrub_settings(...)` to every non-admin caller (`routes/auth_routes.py:715-724`);
  `scrub_settings` masks only secret-*shaped key names (`src/settings_scrub.py:66-70`), and
  `search_url` is not one. The configuration is plausible rather than exotic because the only
  in-provider way to authenticate to a protected SearXNG instance is dead code: both SearXNG
  call sites set `api_key = ""` and then test it (`providers.py:140-143`, `:251-255`), so the
  `Authorization` header is never sent and the credentials have to live in the URL. The project
  has the helper for this (`core/log_safety.redact_url`, used by `routes/chat_routes.py:728`,
  `:1670` and `routes/contacts/contacts_routes.py:723`), and `routes-models.md` reports the same
  class of leak for model-endpoint URLs.
- **Impact:** an operator who reaches a password-protected SearXNG instance through
  `http://user:pass@host/...` (or a URL carrying a token query parameter) hands that credential
  to every authenticated user of the instance through the search config response, and to any
  caller of the auth-exempt settings endpoint, which the front end reads for keybinds and TTS
  preferences (`src/settings_scrub.py:7-9`).
  The mitigation is the premise: nothing documents userinfo in `search_url`, the shipped UI is a
  plain text field, and an operator can put a reverse proxy in front of SearXNG instead — so the
  exposure needs a configuration choice that no code recommends.
- **Fix:** run the URL through `redact_url` before it enters the config response (and use the
  same redaction anywhere else the instance URL is returned), or reject userinfo on the settings
  write and keep the dead `Authorization` path as the supported mechanism for authenticated
  instances.
