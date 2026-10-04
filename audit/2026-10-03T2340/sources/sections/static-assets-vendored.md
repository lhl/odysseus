# static: vendored libraries, fonts, icons, CSS

## Overview

The app-shell assets that no other section owns: `static/sw.js` (the PWA service worker),
`static/index.html` (the SPA shell, 2,591 lines with seven nonce-bearing inline scripts),
`static/login.html` (the pre-auth page, which is a separate document with its own inline
`<style>` and scripts), `static/style.css`, `static/manifest.json`, the three `*-variants.html`
prototype pages, and the binary/vendored payload the shells load — `static/lib/*` (docx,
highlight.js, html2pdf, KaTeX, mammoth, mermaid, qrcode, xlsx), `static/fonts/*`,
`static/fonts/custom/GohuFont.ttf`, `static/icons/*` and `static/icon.ico`.

Boundary: the `static/js/**` modules belong to the `static-js-*` sections and are read here only
where a finding rests on one of them; `static/app.js` (the module-graph entry point) is assigned
here and was read in full. The header layer is not this section's: `core/middleware.py` owns the
`Content-Security-Policy` that the shells live under and belongs to `core-auth-session`; the nonce
substitution helper `src/app_helpers.py:serve_html_with_nonce` belongs to `src-platform`; `app.py`
(the `/static` mount, the `/`, `/login` and `/backgrounds` routes) belongs to `build-install-deploy`.
This section reports what the shipped assets do under that policy, and cross-references rather than
restates those sections' findings.

The vendored bundles are third-party minified output and were not reviewed as first-party code.
Presence and stated versions only: `highlight.min.js` states `Highlight.js v11.9.0`,
`katex/katex.min.js` states `0.16.22` (matching `ACKNOWLEDGMENTS.md:68`),
`mermaid.min.js` states `11.16.1` (`ACKNOWLEDGMENTS.md:69`), `xlsx.full.min.js` states
`0.20.3` (SheetJS), and `docx.umd.min.js`, `mammoth.browser.min.js` and
`html2pdf.bundle.min.js` state no version of their own anywhere in the tree
(`ACKNOWLEDGMENTS.md:62-66` lists them without one). `static/lib/katex/fonts/` ships exactly the
20 `.woff2` files that `katex.min.css` references, and only `.woff2`; the `.woff`/`.ttf`
fallbacks that the stylesheet also lists are absent by design (`ACKNOWLEDGMENTS.md:71-73`).
`static/fonts/` (nine files), `static/icons/` (seven files) and `static/icon.ico` are binary and
were not read beyond their existence and their use in `style.css` and `manifest.json`.

## Coverage

Line numbers refer to `2992bf6d368a` in the working tree; `git log --oneline -1` is `2992bf6d` and
`git status --porcelain` shows only the untracked `audit/` directory.

**Read fully:** `static/sw.js` (239 lines), `static/login.html` (618), `static/app.js` (4,583),
`static/manifest.json` (16), `static/wave-variants.html` (226), `static/whirlpool-variants.html`
(281) and `static/modal-control-variants.html` (240).

**Read partially:** `static/index.html` — the head and the whole executable surface (the seven
inline `<script>` blocks at `:17`, `:118`, `:260`, `:998`, `:1065`, `:1301`, `:2589`, the
`<script src>`/`<link>` inventory at `:211-260` and `:2556-2588`); the remaining ~2,000 lines are
static modal markup and were grepped for inline event handlers, `javascript:` URLs and template
placeholders rather than read line by line. `static/style.css` — 41,401 lines, read structurally
only: every `url()` (24 occurrences), every `@font-face` and every `@import` were checked; the rule
bodies were not read. `static/lib/*` — file headers only, for the version strings above.

**Not read:** the internals of the eight minified bundles and the 20 KaTeX font files; the binary
fonts and icons; `static/js/**` (other sections) except the lines cited below; `static/index.html`
markup beyond the greps described above.

**Checks run:** a probe against the real ASGI app via `fastapi.testclient` (`GET /`, `/login`,
`/static/sw.js`, `/static/{index,login,wave-variants,whirlpool-variants,modal-control-variants}.html`,
`/static/manifest.json`, `/backgrounds`) recording status, `Location`, the
`Content-Security-Policy` header and the response header name set; a script that extracts the URLs
`index.html` actually requests and diffs them against `PRECACHE` in `sw.js`; a script that resolves
the KaTeX `@font-face` URLs against `static/lib/katex/fonts/`; greps for `Service-Worker-Allowed`,
`Content-Security-Policy`, `@import`, `url(http`, `qrcode`, `jsdelivr`, `createElement('script')`
and remote `src=`/`href=` across the tree. Test suites were discovered with
`ls tests | grep -iE 'static|sw|serve_html|nonce|security_header|font|markdown_lazy|panel_loader|app_config_shared'`
and run as one command — `venv/bin/python -m pytest -q tests/test_serve_html_with_nonce.py
tests/test_security_headers_middleware.py tests/test_security_headers_pdf_preview.py
tests/test_app_static_mime.py tests/test_markdown_lazy_lib_loading_js.py tests/test_panel_loader_js.py
tests/test_app_config_shared_fetch_js.py tests/test_font_routes.py tests/test_admin_device_flow_static.py
tests/test_setup_device_auth_static.py tests/test_slash_autocomplete_static.py
tests/test_document_render_pdf_iframe.py` — **64 passed, 1 warning**.

**Out-of-scope observation, not counted as a finding:** `app.py:943` serves `/backgrounds` from
`static/backgrounds.html`, which does not exist in the tree (`ls static/` has no such file), so an
authenticated `GET /backgrounds` reaches `serve_html_with_nonce` on a missing path and returns 500.
`specs/frontend.md:21` and `specs/runtime.md:49` already record the drift; `app.py` belongs to
`build-install-deploy`, so it is left to that section.

### [BUG] The service worker's scope is `/static/`, so it never controls the app shell

- **Location:** `static/index.html:2589` (registration), with `static/sw.js:196-208`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the registration passes no scope:

  ```html
  <script nonce="{{CSP_NONCE}}">if('serviceWorker' in navigator){navigator.serviceWorker.register('/static/sw.js').catch(()=>{});}</script>
  ```

  The default scope is the directory the worker script sits in, and widening it needs a header:
  MDN's `ServiceWorkerContainer.register` — "The default `scope` for a service worker registration
  is the directory where the service worker script is located (resolving `./` against `scriptURL`)"
  and "If you need a broader scope, this can be permitted via the HTTP `Service-Worker-Allowed`
  header." That header is set nowhere: `grep -rn "Service-Worker-Allowed" .` (excluding `venv/`,
  `audit/`, `.git/`) returns nothing, and the live response for the worker confirms it — a
  `TestClient` request to `/static/sw.js` against the real app returns header names
  `['accept-ranges', 'cache-control', 'content-encoding', 'content-length',
  'content-security-policy', 'content-type', 'etag', 'last-modified', 'permissions-policy',
  'referrer-policy', 'vary', 'x-content-type-options', 'x-frame-options']`. So the registration
  scope is `/static/`, and `self.clients.claim()` in `sw.js:182` can only claim clients under that
  path. The fetch handler's navigation branch is therefore unreachable for the app:

  ```js
  if (e.request.mode === 'navigate' && url.pathname === '/') {   // sw.js:196
  ```

  `/`, `/notes`, `/calendar`, `/email`, `/library` and `/login` are all outside `/static/`
  (`app.py:893-949`), and the only pages inside it are the unreferenced `*-variants.html`
  prototypes and `static/index.html` itself.
- **Impact:** the PWA installs and the worker activates, but it intercepts nothing the app
  actually loads — no offline app shell, no cached HTML, no cached module responses for the real
  pages. Every offline claim in the file header and in `specs/frontend.md:76` is inert, and the
  install-time precache of 100 files / 5.78 MB (`fetch(url, {cache: 'reload'})`, `sw.js:161-176`)
  is downloaded on every `CACHE_NAME` bump for a cache nothing reads. Users lose the offline mode
  the manifest and worker advertise; the failure is silent because registration succeeds and
  nothing logs a scope mismatch.
- **Fix:** register with an explicit scope and allow it server-side —
  `navigator.serviceWorker.register('/static/sw.js', { scope: '/' })` plus a
  `Service-Worker-Allowed: /` response header for the worker (a small route or a header added in
  `_RevalidatingStatic`), or move `sw.js` to the site root so the default scope is `/`.

### [BUG] `PRECACHE` does not match the URLs `index.html` requests, so the offline shell misses 16 first-paint URLs and re-downloads 12 of them

- **Location:** `static/sw.js:40-99` (PRECACHE), with `static/index.html:248-253` and `:2556-2588`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `sw.js:39` states the rule the list breaks — "Entries must match the exact URL the
  browser requests, query string included." Extracting the `src`/`href` URLs the shell loads and
  diffing them against `PRECACHE` shows 16 distinct URLs missing (`/static/app.js?v=…` appears
  twice in the shell, as a `modulepreload` and as the final script tag):

  ```
  === index.html shell requests (40) ===
  requested but NOT in PRECACHE: 17
      /static/js/memory.js?v=20260722memoryloading1
      /static/js/tourAutoplay.js
      /static/js/models.js?v=20260715startupcalm2
      /static/js/document.js?v=20260815approvalsave1
      /static/js/gallery.js?v=20260708match1
      /static/js/chatRenderer.js?v=20260819approvalcontrol1
      /static/js/chatStream.js?v=20260819approvalcontrol1
      /static/js/chat.js?v=20260819approvalcontrol1
      /static/js/cookbookSchedule.js
      /static/js/settings.js?v=20260815approvalsave1
      /static/js/assistant.js
      /static/app.js?v=20260815toolapproval4
      /static/js/init.js?v=20260715freshroot3
      /static/js/a11y.js
      /static/style.css?v=20260808startupshell1
      /static/app.js?v=20260815toolapproval4
      /static/js/chat.js?v=20260815toolapproval4
  ```

  Twelve of those are `?v=` variants of entries that *are* precached without the query
  (`'/static/style.css'` at `sw.js:42`, `'/static/app.js'` at `:43`, `'/static/js/chat.js'` at
  `:66`, and so on); four (`tourAutoplay.js`, `cookbookSchedule.js`, `assistant.js`, `a11y.js`) have
  no entry at all. `PANEL_PRECACHE` has the same shape but is verified: `tests/test_panel_loader_js.py`
  walks the lazy editor graph and asserts each file is listed "query string included"; nothing does
  that for the shell list. `specs/frontend.md:52` says the same thing the code does not do:
  "Versioned script tags, unversioned imports, and service-worker precache entries must stay aligned."
- **Impact:** offline the app shell loads and then dies on its own module graph: the JS/CSS branch
  (`sw.js:212-222`) falls back to `caches.match(e.request)`, which misses the versioned URL the page
  asked for, so the modules never resolve. Online, every install fetches the unversioned twins that
  the page never requests — `app.js`, `style.css` and the rest are downloaded twice per
  `CACHE_NAME` bump — and the cache is populated with entries that will never be read.
- **Fix:** make the precache list match the shell exactly (generate `PRECACHE` from `index.html`, or
  drop the `?v=` queries from the script tags and the imports together), and add a test mirroring
  `test_panel_loader_js.py`'s graph walk for the first-paint list so the next `?v=` bump cannot
  silently drift again.

### [FOOTGUN] The navigation branch keys its cache on the constant `/` and never checks the request origin

- **Location:** `static/sw.js:196-208` (the `cache.match('/')` at `:199` and `cache.put('/', …)` at `:201`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the branch decides on `url.pathname === '/'` alone; `cache.match('/')` resolves that
  string against the worker's own base URL, not against `e.request.url`:

  ```js
  if (e.request.mode === 'navigate' && url.pathname === '/') {
    e.respondWith(
      caches.open(CACHE_NAME).then(async cache => {
        const cached = await cache.match('/');
  ```

  A fetch event reaches the handler for requests from controlled pages, not only same-origin ones
  (web.dev, "Serving": "The fetch event lets us intercept every network request made by the PWA in
  the service worker's scope, for both same-origin and cross-origin requests"), and `respondWith`
  is free to answer a request with a response from any origin. Every other branch in the file has
  the same shape: `url.pathname.startsWith('/static/')` (`:212`, `:226`) with no `url.origin` test.
- **Impact:** today this is latent — with the scope bug above, no app page is controlled, and no
  page under `/static/` navigates off-origin. Fix the scope without fixing this and the branch goes
  live: a controlled page navigating to another origin's `/` (a link, `location.assign`, a form
  target) is answered with the cached Odysseus shell at that foreign URL, and the `cache.put('/')`
  on the same branch would store whatever that navigation returned under the app shell's key. The
  `/static/` branches have the same missing check, but there the `res.ok` guard keeps opaque
  cross-origin responses out of the cache.
- **Fix:** reject anything that is not the worker's own origin at the top of the fetch handler —
  `if (url.origin !== self.location.origin) return;` — and match the cached entry with
  `cache.match(e.request)` instead of the literal `'/'`.

### [SECURITY] A third-party script is injected from `cdn.jsdelivr.net` with no integrity attribute

- **Location:** `static/js/codeRunner.js:156` (allowed by `core/middleware.py:143`, owned by `core-auth-session`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the only remote asset load left in the front end is the Pyodide bootstrap:

  ```js
  script.src = 'https://cdn.jsdelivr.net/pyodide/v0.27.5/full/pyodide.js';   // :156
  script.onload = () => { window.loadPyodide({ indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.27.5/full/' })   // :158
  ```

  No `integrity` attribute is set, and the runtime's remaining files are fetched from the same CDN
  base at run time. The default `Content-Security-Policy` keeps a hole open for exactly this:
  `script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net` (`core/middleware.py:143`), with the
  same host allowed in `style-src` and `font-src`. Greps for remote `src=`/`href=`/`createElement('script')`
  across `static/` (excluding `static/lib/`) find no other remote script; the shell comment at
  `static/index.html:236` records that KaTeX and Mermaid were moved off this CDN on purpose
  ("cost ~985 KB on the wire, broke offline installs, and announced every session to a third party").
- **Impact:** the code runner executes a CDN-supplied script inside an authenticated session, so a
  compromise of that CDN path (or of the DNS/TLS chain in front of it) yields arbitrary script with
  the user's cookie — and therefore the user's API, including the agent's shell tools — on the one
  path the app deliberately left remote. Reach is limited to users who run Python in the code
  runner, and the URL is version-pinned, which is why this is `low` rather than higher.
- **Fix:** vendor the Pyodide runtime under `static/lib/` like every other bundle and drop
  `https://cdn.jsdelivr.net` from `script-src`; if the CDN has to stay, pin the script with an
  `integrity` hash and narrow the policy to that exact URL.

### [BUG] `/static/*.html` serves the raw template with an unsubstituted nonce, so its inline scripts are blocked

- **Location:** `static/login.html:10` (also `static/index.html:17`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the pages are templates: the nonce placeholder is replaced only by
  `serve_html_with_nonce`, which the `/` and `/login` routes call (`app.py:896`, `:949`). The
  `/static` mount (`app.py:510`, `_RevalidatingStatic`) serves the same files byte for byte, and
  `/static` is auth-exempt (`app.py:277`, `AUTH_EXEMPT_PREFIXES = ["/static"]`). A `TestClient`
  request to `/static/login.html` against the real app returns 200 with the placeholder intact
  while the response's own CSP carries a real nonce:

  ```
  /static/login.html status 200
  placeholder present in served body: True
  nonce occurrences: 3
  ```

  `script-src 'self' 'nonce-…'` (`core/middleware.py:143`) has no `'unsafe-inline'`, so a
  `<script nonce="{{CSP_NONCE}}">` whose nonce does not match the header is not executed.
- **Impact:** anyone who opens `/static/login.html` or `/static/index.html` gets a page that renders
  and does nothing: the login form's submit handler never runs, so `<form id="authForm">` — which
  has no `action` or `method` — falls back to a native GET submission and puts `username` and
  `password` in the URL (browser history, access logs). Nothing in the tree links to those URLs
  (`grep -rn "static/login.html\|static/index.html"` finds only docs and `specs/`), so the reach is
  low; the same applies to the `static/manifest.json` link, which resolves to
  `/static/static/manifest.json` from that path and 404s.
- **Fix:** stop serving the nonce-bearing templates through the static mount — move them out of
  `static/` and keep the three routes as the only entry points, or have `_RevalidatingStatic`
  substitute the nonce for `.html` instead of returning the file unchanged.

### [DEAD-CODE] Three prototype pages ship in the public static root; two carry inline scripts the CSP blocks

- **Location:** `static/wave-variants.html:180` and `static/whirlpool-variants.html:145` (with `static/modal-control-variants.html`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** nothing in the tree references them — `grep -rn "modal-control-variants\|wave-variants\|whirlpool-variants"` outside `static/` returns nothing, and `specs/frontend.md` does not list them. They are nevertheless public: `/static` is auth-exempt (`app.py:277`) and a `TestClient` request to each returns `200` with no session. Their `<script>` tags carry no nonce
  (`<script>` at `wave-variants.html:180`, `whirlpool-variants.html:145`) while the same CSP as above
  applies (the probe shows `csp_has_unsafe_inline=False` for all three), so their animations never
  start. `modal-control-variants.html` is pure HTML/CSS and has no script.
- **Impact:** three development artifacts (a modal-chrome study and two ASCII/whirlpool spinner
  studies) stay reachable without authentication in a deployed instance, and two of them are broken
  as shipped because the policy blocks their scripts. Nothing user-specific is exposed — the pages
  are static, load no data and make no requests — so this is surface-area and dead weight, not a
  disclosure.
- **Fix:** delete the three files (they are unreferenced), or move them under a docs/dev directory
  that is not mounted at `/static`; if they are meant to keep working, give their scripts a nonce.

### [DEAD-CODE] `static/lib/qrcode.min.js` is vendored but never loaded

- **Location:** `static/lib/qrcode.min.js:1`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** a case-insensitive search for `qrcode`/`QRCode` across `static/` finds no loader —
  the only hits are `settings.js:2062` and `:2066`, which render a QR image the *server* produced.
  `routes/auth_routes.py:258-263` generates the 2FA QR with the Python `qrcode` package and returns
  it as `data:image/png;base64,…`. The only other mention in the tree is the attribution entry
  `ACKNOWLEDGMENTS.md:67` ("node-qrcode (`qrcode.min.js`) | QR-code rendering (2FA setup)"), which
  describes a use that does not exist. The file is also absent from both `PRECACHE` and
  `PANEL_PRECACHE`, so it is not reachable offline either.
- **Impact:** 24 KB of a browser QR library ships to every install and is never executed; the
  acknowledgements file tells a reader that 2FA setup uses it, which sends anyone auditing the 2FA
  flow to the wrong implementation.
- **Fix:** delete the file and its acknowledgements row, or wire it up and drop the server-side PNG.

### [PERF] The login page imports the whole theme module graph for a decorative background

- **Location:** `static/login.html:610`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the login page's last script block dynamically imports the main app's theme module:

  ```js
  const tm = await import((window.__odysseusLoginAppUrl || ((path) => path))('/static/js/theme.js'));   // :610
  ```

  Resolving that module's static imports transitively gives 13 files / 342,740 bytes uncompressed:
  `theme.js` (92 KB), `modalManager.js` (71 KB), `ui.js` (51 KB), `modalSnap.js` (47 KB),
  `colorPicker.js`, `tileManager.js`, `windowDrag.js`, `windowResize.js`, `spinner.js`,
  `escMenuStack.js`, `toolWindowZOrder.js`, `storage.js`, `color/hex.js`. The page uses one function
  from it (`applyBgPattern`) to animate a canvas background; the login document has none of the
  modals, windows or pickers those other modules exist for.
- **Impact:** the pre-auth page — the first thing every user loads, on the path that gates the rest
  of the app — pulls 335 KB of application JavaScript for a background effect, on top of its own
  inline styles. The comment at `login.html:601-608` documents the dependency but the cost was not
  part of the trade.
- **Fix:** move the canvas background effects into a small module with no app imports (or inline
  the handful of patterns the login page offers) so the login page stops loading the modal/window
  machinery.
