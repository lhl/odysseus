# static: documents, notes, email, calendar UI

## Overview

The browser-side modules behind five Odysseus surfaces: the email library and inbox
(`static/js/emailLibrary.js`, `static/js/emailInbox.js`, `static/js/emailShared.js`,
`static/js/emailLibrary/*.js`), the document editor and its library
(`static/js/document.js`, `static/js/documentLibrary.js`), notes (`static/js/notes.js`),
the calendar (`static/js/calendar.js`, `static/js/calendar/*.js`) and the gallery
(`static/js/gallery.js`, `static/js/galleryEditor.js`), plus the signature pad
(`static/js/signature.js`). The section covers what these modules insert into the DOM, which
stored or remote value they insert, and where a value crosses a trust boundary on the way in.

The findings here are about the client-side sink. The backend facts they rest on are cited as
evidence rather than restated. Each neighbour owns one piece:

| Owner | What it owns |
| --- | --- |
| `routes-email.md`, `src-email-integrations.md` | The backend that produces the objects these modules render: the IMAP read path, the thread parser, the send path |
| `static-js-rest.md` | `static/js/markdown.js`. The `mdToHtml` and `sanitizeAllowedHtml` sanitizers the document editor calls are read here only where a finding rests on them |
| `static-assets-vendored.md` | The app's Content-Security-Policy (`core/middleware.py:141-152`). It reports that the policy has no `'unsafe-inline'` in `script-src`; this section depends on that for its severity judgements and cross-references it |
| `routes-gallery-document.md` | The gallery and document routes |
| `static-js-cookbook-settings-models.md` | `settings.js` |
| Another section | `ui.js`, the shared `esc`, `showToast`, `showError` and `styledConfirm` helpers the modules here call. It was read only to decide whether a sink escapes |

## Coverage

Line numbers refer to commit `2992bf6d368a`; `git log --oneline -1` in the working tree is
`4cff473d`, and `git diff --name-only 2992bf6d368a HEAD -- static/js/emailLibrary.js
static/js/emailInbox.js static/js/emailShared.js static/js/emailLibrary static/js/document.js
static/js/documentLibrary.js static/js/notes.js static/js/calendar.js static/js/calendar
static/js/gallery.js static/js/galleryEditor.js static/js/signature.js` prints nothing (0 paths),
so every citation resolves at both revisions.

**Read fully (8 files, 2,418 lines):**

| File | Lines |
| --- | ---: |
| `static/js/emailInbox.js` | 1,456 |
| `static/js/emailLibrary/utils.js` | 248 |
| `static/js/emailLibrary/signatureFold.js` | 339 |
| `static/js/calendar/reminders.js` | 114 |
| `static/js/calendar/utils.js` | 180 |
| `static/js/emailLibrary/state.js` | 35 |
| `static/js/emailLibrary/replyRecipients.js` | 27 |
| `static/js/emailShared.js` | 19 |

**Read partially (8 files, 40,403 lines):** the remaining assigned files are large and were read
by sink, not end to end. For each one I enumerated every `innerHTML` / `insertAdjacentHTML` /
`outerHTML` assignment and every `${…}` interpolation (two throwaway scanners in `/tmp/audit-probe`,
`scan.js` and `scan2.js`), then read each flagged region plus the regions the assignment named:

| File | Lines | Regions read |
| --- | ---: | --- |
| `static/js/emailLibrary.js` | 8,771 | imports (`:1-60`), settings form, `_decodeAttrValue` (`:613`), unsubscribe scan + candidate cards (`:1520-1700`), reader card meta (`:5200-5320`), reader header and body mount (`:5470-5700`), body render + sanitizer calls (`:5740-5900`), inline-image placeholder and loader (`:5852-6060`), thread bubbles (`:6160-6230`), summary panel (`:6526-6560`), attachment chips (`:6700-6840`), reader modals (`:7180-7400`), menus (`:7890-8170`, `:8590-8640`) |
| `static/js/document.js` | 11,207 | email document type in full (`:2225-3200`), send path (`:3853-3960`, `:4010-4030`), attachment picker (`:3380-3440`), PDF form pane (`:760-935`), version history (`:10910-11000`), export (`:9690-9740`), misc sinks flagged by the scanner |
| `static/js/calendar.js` | 3,722 | dropdown/confirm/settings (`:440-620`, `:2480-2760`), event reminder (`:568-610`), month grid and event rows (`:1040-1100`), agenda/day detail (`:1700-1920`), escaping helpers (`:3434-3450`) |
| `static/js/notes.js` | 5,365 | reminder poll/fire (`:600-1010`), card and list render (`:1440-2000`), note form (`:2930-3080`), reminder menu (`:3440-3500`), checklist/draw renderers (`:3900-4060`), menus (`:4390-4460`), `_linkify` and helpers (`:490-530`, `:4910-4920`, `:5150-5170`) |
| `static/js/gallery.js` | 3,006 | render/filter helpers (`:400-700`), grid and cards (`:940-1300`), detail pane (`:1390-1520`), albums, menus, `_esc` (`:2983-2988`) |
| `static/js/galleryEditor.js` | 4,386 | landing/templates (`:330-440`), AI-command suggestions (`:400-440`), layer panel (`:2120-2150`), filter modal (`:2600-2650`), loading overlay (`:4040-4050`) |
| `static/js/documentLibrary.js` | 3,422 | import/convert helpers (`:1390-1450`), grid and card render (`:430-1000`), previews incl. chat preview (`:1900-2100`), archive view (`:2320-2600`), research detail (`:2725-2760`) |
| `static/js/signature.js` | 524 | escaping and data-URL guard (`:14-30`), `_modal` (`:318-326`), capture (`:380-455`), picker (`:455-500`) |

**Not read:** the bodies of the eight partially-read files outside the regions above — most
substantially `document.js` outside the email-draft/export/version paths (the markdown editor,
AI diff, PDF form machinery), `notes.js` outside the reminder/card/form paths,
`galleryEditor.js` outside the template and panel renderers, and `documentLibrary.js` outside
its preview renderers. No finding here rests on an unread region.

**Checks run.** Three pytest runs over the suites that touch these files, all green:

```
venv/bin/python -m pytest -q tests/test_calendar_css_url_escape_js.py \
  tests/test_calendar_utils_dates_js.py tests/test_document_ai_preview_refresh_js.py \
  tests/test_document_diff_discard_on_update_js.py tests/test_email_linkify_security_js.py \
  tests/test_email_open_dedup_js.py tests/test_email_summary_error_ui_js.py \
  tests/test_gmail_quote_attribution_js.py tests/test_notes_search_reset_on_reopen_js.py \
  tests/test_notes_select_esc_listener_js.py tests/test_notes_z_order_js.py \
  tests/test_reply_all_cc_nonstring_js.py tests/test_reply_recipients_js.py \
  tests/test_signature_fold_js.py tests/test_signature_fold_self_closing_br_js.py \
  tests/test_notes_dom_xss_helpers.py
49 passed, 1 warning in 1.62s

venv/bin/python -m pytest -q tests/test_email_library_bulk_actions.py \
  tests/test_email_library_prewarm.py tests/test_external_context_tool_gate.py \
  tests/test_forwarded_message_divider.py tests/test_security_regressions.py
264 passed, 1 warning in 1.33s

venv/bin/python -m pytest -q tests/test_calendar_event_contrast.py \
  tests/test_doc_library_open_orphaned.py tests/test_document_editor_scroll.py \
  tests/test_document_library_delete_counters.py tests/test_markdown_lazy_lib_loading_js.py
24 passed, 1 warning in 0.80s
```

337 tests pass. Beyond pytest, the render claims below were settled in a real browser: a read-only
local HTTP server (`/tmp/audit-probe/serve.py`) serving the repo tree under `/repo/` and the probe
pages under `/`, driven by headless Chromium
(`/home/lhl/.cache/ms-playwright/chromium_headless_shell-1200/…`) through Playwright. The probes
import the real modules (`static/js/emailLibrary/utils.js`) or replicate the cited function
verbatim, and one probe page is served with the app's exact CSP header copied from
`core/middleware.py:141-152`. The drivers are in `/tmp/audit-probe/`:

- `rerun.py`, which runs all pages
- `beacon.py`, `battery.py`
- `csp_out.py`, `run_detached.py`

### [SECURITY] A calendar event's location is only partly escaped, so a synced or imported event injects HTML and CSS into the calendar UI

- **Location:** `static/js/calendar.js:3437-3449` (the URL branch at `:3439-3444`; sinks at
  `:1709`, `:1775`, `:1902`, `:1915`)
- **Severity:** high
- **Disposition:** fix-now
- **Evidence:** `_locHTML` escapes each matched URL and nothing else — the text between URLs is
  concatenated into the returned HTML unescaped:

  ```js
  function _locHTML(loc) {
    if (!loc) return '';
    const urlRe = /(https?:\/\/[^\s]+)/gi;
    if (urlRe.test(loc)) {
      return loc.replace(urlRe, (url) => {
        const safe = _e(url);
        return `<a href="${safe}" …>${safe}</a>`;
      }).replace(/\n/g, '<br>');
    }
  ```

  `_e` is `uiModule.esc` (`static/js/calendar.js:3434`), and every caller puts the result straight into
  `innerHTML` (`:1709`, `:1775`, `:1902`, `:1915`). Replaying the function verbatim in Chromium
  with the location
  `https://maps.example.test/room5 <style>#probe-target{color:rgb(1,2,3)}</style><img src="//127.0.0.1:8765/px?loc=1">`
  produced:

  ```
  { "generated": "<a href=\"https://maps.example.test/room5\" target=\"_blank\" rel=\"noopener\" onclick=\"event.stopPropagation();\">https://maps.example.test/room5</a> <style>#probe-target{color:rgb(1,2,3)}</style><img src=\"//127.0.0.1:8765/px?loc=1\">", "injectedElements": [ "A", "STYLE", "IMG" ], "styleApplied": "rgb(1, 2, 3)", "imgSrc": "//127.0.0.1:8765/px?loc=1", "noUrlBranch": "<a href=\"https://www.openstreetmap.org/search?query=Room%205%20%3Cstyle%3Ex%7B%7D%3C%2Fstyle%3E\" …>Room 5 &lt;style&gt;x{}&lt;/style&gt;</a>" }
  -- BEACONS: /px?loc=1
  ```

  The `<style>` element applies (the probe element's computed colour is `rgb(1, 2, 3)`, not the
  stylesheet's own value) and the browser fetched the `<img>`. The same input without a URL takes
  the other branch, whose anchor text is fully escaped (`Room 5 &lt;style&gt;x{}&lt;/style&gt;`),
  which is what makes this a one-branch bug rather than a design choice. The value is not
  necessarily user-authored: `src/caldav_sync.py:411` stores a
  remote server's `location` property verbatim (`location = str(comp.get("location", ""))`, then
  `existing.location = location` / `location=location` at `:426`/`:442`), and `.ics` import does
  the same for an uploaded file.
- **Impact:** anyone who can write an event into a calendar the user syncs (a shared or public
  CalDAV collection, or an `.ics` file the user imports) gets arbitrary HTML and CSS rendered inside
  the calendar modal: remote fetches that disclose the user's IP and confirm the calendar is open,
  CSS that can hide or overlay calendar chrome, markup that survives until the view re-renders, and, through an injected `<iframe srcdoc>`, script from `cdn.jsdelivr.net` running in the user's session.
  An inline handler does not run: `script-src` in the app's policy has no `'unsafe-inline'`, and
  a companion page served with that exact policy (`core/middleware.py:141-152`, `nonce-dummy`
  standing in for the per-response nonce) logged `Executing inline event handler violates the
  following Content Security Policy directive 'script-src 'self' 'nonce-dummy'
  https://cdn.jsdelivr.net' … The action has been blocked.` and never ran the handler. The `_locHTML`
  probe page itself was served without the header, so its console was empty; the `<style>` and
  `<img>` effects above are what the policy does not stop, since `style-src` allows `'unsafe-inline'`
  and `img-src` allows `https:` and same-origin fetches.
- **Re-review (2026-10-05):** raised from medium to high. The first pass tested an inline handler,
  which the policy refuses, and concluded that script execution is not reachable. With `_locHTML`
  copied by line range onto a page served with the app's policy, the location
  `https://maps.example.test/room5 <iframe srcdoc="<script
  src=https&colon;//cdn.jsdelivr.net/npm/lodash@4.17.21/lodash.min.js></script>">` ran the CDN
  script in a frame whose origin is the page's. The `&colon;` keeps the script URL out of the
  linkifier's `https?://` match. The same location without a leading URL takes the escaped branch
  and does not execute. The script acts with the session of whoever opens the event. See the
  policy finding in `core-auth-session`.
- **Fix:** escape the whole string first and linkify the escaped copy, the way
  `static/js/notes.js:517-529` already does (`const escaped = _esc(s); … escaped.replace(urlRe, …)`).

### [SECURITY] A sender's display name and attachment filename escape their attribute, because `_esc` is used where an attribute escaper is needed

- **Location:** `static/js/emailLibrary.js:699` (`_recipientChipHtml`; also `:6821`,
  `:1656`) and `static/js/emailInbox.js:626`; same pattern at `static/js/gallery.js:1282`, `:1464`,
  `:1495`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_esc` is `div.textContent = text; return div.innerHTML` (`static/js/emailLibrary/utils.js:27-31`),
  which escapes `&`, `<` and `>` but not `"` — the module that needs quotes carries a separate
  `_attrEsc` for exactly that reason (`utils.js:53-59`, used only inside `_escLinkify`). These
  templates nevertheless interpolate `_esc` into quoted attributes:

  ```js
  // emailLibrary.js:699
  return `<span class="${cls}" data-full="${_esc(fullText || labelText)}" data-email="${_esc(addr)}" title="Click for details">…`;
  ```

  Replaying that line verbatim in Chromium with the sender's display name
  `Eve" onmouseover="window.__pwned_chip=1` produced a chip whose attributes are
  `["class=recipient-chip from-chip", "data-full=Eve", "onmouseover=window.__pwned_chip=1",
  "data-email=eve@example.com", "title=Click for details"]` — the payload closed `data-full` and
  opened a real handler attribute, and dispatching `mouseover` ran it (`"chipHandlerRan": true`).
  The same probe served with the app's policy reported `"chipHandlerRan": false` and
  `"chip2HandlerRan": "undefined"` (against `true` and `"0x"` without the header), with
  `Executing inline event handler violates the following Content Security Policy directive
  'script-src 'self' 'nonce-dummy' https://cdn.jsdelivr.net'` in the console — so this is attribute
  injection rather than script execution. The inputs are entirely
  sender-controlled: `from_name`/`from_address` come from `parseaddr(msg["From"])`
  (`routes/email_routes.py:3010`) and are rendered by `_recipientChipHtml` at `:5559` (also `:7191`,
  `:7339`);
  `a.filename` comes from the MIME part's filename parameter with only header decoding applied
  (`routes/email_helpers.py:1537-1539`, `_decode_header`) and is interpolated into
  `data-att-name`/`data-open-name` at `:6821`; the unsubscribe link at `:1656` interpolates a
  sender's `List-Unsubscribe` URL, which the backend only scheme-checks (`http`/`https`/`mailto`,
  `routes/email_routes.py:588`), not character-checks. `gallery.js` has the same helper
  (`_esc` at `:2983-2988`) in attribute position for `img.prompt` (`:1282`, `:1464`) and for the
  AI-tag and user-tag chips (`:1495`, `:1497`).
- **Impact:** every received message can inject arbitrary attributes into the reader's markup —
  `style` is the useful one, since `style-src 'unsafe-inline'` allows it, so a sender can overlay or
  hide reader chrome (a spoofed banner or button over the real one) and force CSS-driven fetches
  from the reader. Injected duplicates cannot redirect the attachment fetch (`data-att-uid` and
  `data-open-uid` come first in the tag and first-wins applies) but can override later attributes
  such as `data-open-folder`. Markup after the break is corrupted, so the row/chip renders wrong.
  No script execution: `script-src` has no `'unsafe-inline'`, which I verified in Chromium.
- **Fix:** use an attribute escaper (`_attrEsc`, or move to `element.dataset.x = value` /
  `setAttribute`) for every `_esc(…)` that sits inside a quoted attribute in these files.

### [SECURITY] The email HTML sanitizer keeps remote URLs in inline styles and `poster`, so an HTML mail beacons without the user's consent

- **Location:** `static/js/emailLibrary/utils.js:184-188` (the attribute and CSS lists) with the
  render sink at `static/js/emailLibrary.js:5585` (`_safeRenderEmailBody`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** `_sanitizeHtmlOnce` strips the URL attributes (`src`, `href`, `srcset`, then `poster` and
  `background`) only when the URL uses `javascript:`, `vbscript:` or `data:` (`utils.js:184`, `:199-202`).
  `STRIP_CSS_PROPS` covers `color`, `background`, `background-color` and `font*`, and
  separately `position` and `z-index`, but not `background-image` or other URL-bearing properties (`utils.js:186-188`).
  Running the real `_sanitizeHtml` over a sender-style body and inserting the result into a live
  element (as the reader does at `:5585`) gave:

  ```
  { "sanitized": "<p>hello</p><div style=\"background-image:url(http://127.0.0.1:8765/px?css=1)\">css bg</div><img src=\"http://127.0.0.1:8765/px?img=1\"><video poster=\"http://127.0.0.1:8765/px?poster=1\"></video>" }
  BEACONS HIT:
  /px?poster=1
  /px?img=1
  /px?css=1
  ```

  All three URLs survive the sanitizer and all three were fetched once the result was inserted (the
  three loads complete in varying order between runs). The `<img>` beacon is the one the app does
  block: `_prepareEmailInlineImages` (`static/js/emailLibrary.js:5852-5889`) rewrites
  `root.querySelectorAll('img')` into a "Remote image blocked" placeholder, and it returns early when
  the body has no `<img>` at all (`if (!/<img[\s>]/i.test(raw)) return raw;`), so a CSS-only body
  never reaches even that pass. The CSS and `poster` beacons have no guard and fire as soon as the
  reader renders.

  A 24-payload battery through the same sanitizer set none of the 17 `window.__xss*` flags it checks
  and left no dangerous URL alive, so the sanitizer is sound on the scheme axis; this is the
  residual gap. The payload classes were:

  - inline handlers and `javascript:` hrefs
  - `<svg>` and `<math>`, `<template>` and `srcdoc`
  - `meta refresh` and `base`, `noscript` mutation-XSS
  - `srcset`, `data:` images, `expression()` and entity-split quotes
- **Impact:** any sender can tell when a message was opened, from which IP, and with a per-recipient
  token, defeating the "Remote image blocked" affordance the reader shows the user. It needs no
  click: opening the email is enough.
- **Fix:** extend the style filter to drop any declaration whose value contains `url(` unless the
  scheme is explicitly allowed, and either strip `poster` outright or route it through the same
  inline-image placeholder the `<img>` path uses.

### [BUG] `_escLinkify` linkifies the address inside the `href` it just built, mangling any URL that contains `@`

- **Location:** `static/js/emailLibrary/utils.js:75-86`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the URL pass inserts markup and the mail pass then runs over the whole string,
  including the `href` the URL pass just wrote:

  ```js
  return escaped
    .replace(urlRe, (m) => { … return `<a href="${_attrEsc(href)}" …>${m}</a>`; })
    .replace(mailRe, (m) => `<a href="${_attrEsc(`mailto:${m}`)}">${m}</a>`);
  ```

  `_escLinkify('https://user@example.test/x')` returns

  ```
  <a href="https://<a href="mailto:user@example.test">user@example.test</a>/x" target="_blank" rel="noopener noreferrer">https://<a href="mailto:user@example.test">user@example.test</a>/x</a>
  ```

  and parsing that HTML back gives an anchor whose `href` is `https://&lt;a href=` with a stray
  `mailto:user@example.test"=""` attribute and a nested mailto link. Any plain-text message
  containing a URL with an `@` (a userinfo URL, or a query string carrying an address) renders
  broken. The plain-text render path calls this for every text-only message
  (`static/js/emailLibrary.js:5805`, `:5833`, `:5846`).
- **Impact:** the visible link text and its target diverge — what reads as an `https://` URL is not
  a working link, and the reader shows the tail of the URL as loose text. Cosmetic, not a script
  sink: the injected quotes come from this function's own output, and attacker text cannot supply
  one (the URL and address character classes both exclude `"`).
- **Fix:** linkify e-mail addresses in the same pass as URLs, or run the mail pass over the escaped
  text before the URL pass inserts markup.

### [BUG] The reply draft parses the sender's plain-text body as HTML, firing remote fetches and rewriting the quoted text

- **Location:** `static/js/document.js:2460-2464` (`_emailHtmlToPlainText`, called from `:2504`) and
  `static/js/document.js:2348-2349` (`_sanitizeOutgoingEmailBody`'s probe)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the reply draft body that `emailInbox.js` builds quotes the sender's body verbatim
  after the separator (`static/js/emailInbox.js:29`, `:961-995`; a text/plain part is used as-is, and the
  HTML fallback strips tags at `:967` *before* decoding entities at `:970-971`, so `&lt;img …&gt;`
  becomes a live-looking tag). Rendering that draft calls `_emailBodyToHtml` (`document.js:3056`), which for a
  body containing the separator takes the `quotedPart` branch and passes it to

  ```js
  function _emailHtmlToPlainText(html) {
    const d = document.createElement('div');
    d.innerHTML = String(html || '');
    return d.innerText || d.textContent || '';
  }
  ```

  Replaying that function with a draft built exactly as `emailInbox.js` builds one, from a sender
  body containing `<img src="/px?detached=1">`, produced:

  ```
  { "quotedPart": "---------- Previous message ----------\nOn Mon, Apr 18, 2026 at 9:31 AM, Eve <eve@example.com> wrote:\n> hi there\n> <img src=\"/px?detached=1\">\n> bye", "plain": "---------- Previous message ----------\nOn Mon, Apr 18, 2026 at 9:31 AM, Eve wrote:\n> hi there\n> \n> bye", "detached": true }
  BEACONS: /px?detached=1
  ```

  The div is never inserted into the document, yet the browser fetched the image — the beacon needs
  no rendering of the draft, only the reply opening. The quoted text is also lossy: the
  `> <img src="/px?detached=1">` line the sender wrote comes back as an empty `> ` line. The same
  branch exists in `_sanitizeOutgoingEmailBody` (`:2349 probe.innerHTML = text`), which runs on the
  draft body when a local draft is restored (`:2930`).
- **Impact:** a sender can force a request to a URL of their choosing (an `https://` image is allowed
  by `img-src`) the moment the user hits Reply on a plain-text message — a read receipt that the
  reader's remote-image blocking does not cover, disclosing the user's IP and confirming the reply.
  The parse also drops or reflows text: tag-looking sequences vanish from the quoted history
  (`innerText` on a detached node returns text nodes only), so the quote the user sees can differ
  from the message they received. Inline handlers do not run under the app CSP, which the same probe
  confirmed separately.
- **Fix:** read the quote with `textContent` (`_emailPlainTextToHtml` already does the right thing at
  `:2454-2458`) instead of assigning to `innerHTML`, or run the sender's text through
  `_sanitizeHtml` before the entity/plain-text conversion.

### [BUG] Inline `onclick` attributes in generated markup never run, because the app CSP forbids inline handlers

- **Location:** `static/js/calendar.js:3443`, `static/js/calendar.js:3448`,
  `static/js/notes.js:527`
- **Severity:** low
- **Disposition:** next
- **Evidence:** these templates carry `onclick="event.stopPropagation();"` on links they build for
  locations and note text. The app's policy (`core/middleware.py:141-152`) is
  `script-src 'self' 'nonce-…' https://cdn.jsdelivr.net` with no `'unsafe-inline'`; a page served
  with that exact header, with an element carrying an inline handler, logged `Executing inline event
  handler violates the following Content Security Policy directive 'script-src 'self' 'nonce-dummy'
  https://cdn.jsdelivr.net'. Either the 'unsafe-inline' keyword, a hash ('sha256-...'), or a nonce
  ('nonce-...') is required to enable inline execution. … The action has been blocked.` and the
  handler never ran (`"chipHandlerRan": false`, `"detachedInnerHtmlRanHandler": false`). `static-assets-vendored.md` already reports the policy itself; this is the in-tree
  markup that assumes otherwise.
- **Impact:** clicking a URL inside a note or a location inside a calendar event does not stop
  propagation, so the link opens *and* the note editor / event modal opens behind it. The stated
  intent of the attribute is silently unmet in every deployment.
- **Fix:** drop the attributes and call `stopPropagation` from a delegated listener, or attach the
  listener directly to the generated anchor after insertion.

### [SECURITY] A note's custom-background URL goes into a CSS `url()` unescaped, unlike the calendar's equivalent helper

- **Location:** `static/js/notes.js:329-335` (sink `:332`) and `static/js/notes.js:343-347`
  (sink `:346`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** `_dotBg` and `_customColorStyle` interpolate the stored `bg:<url>` sentinel directly
  into a quoted CSS string — `` `center/cover no-repeat url('${url}')` `` (`:334`) and
  `` `… url('${url}'); background-size: cover; …` `` (`:346`) — with no escaping. The calendar's
  equivalent does escape, and says why: `_cssUrlEscape` (`static/js/calendar/utils.js:73-78`, comment at
  `:68-72`) backslash-escapes first so a trailing `\` cannot escape the closing quote, and carries a
  CodeQL `js/incomplete-sanitization` note. The value is written verbatim: `NoteRequest.color` is a free
  string (`routes/note/note_routes.py:31`, `:47`) stored as given (`:670`, `:735`), and the agent's
  `manage_notes` tool passes an arbitrary `color` through (`src/tools/notes.py:207`, `:222`).
- **Impact:** a value containing `')` closes the CSS string and lets the rest of the declaration run
  inside a `style` attribute — `style-src 'unsafe-inline'` permits it, so a caller can add
  declarations (an overlay, or a `url()` fetch) to the note card. The write path is the user's own
  notes API, so the reach is self-inflicted or agent-mediated (a prompt-injected agent call can set
  a colour); I found no cross-user path to a note's `color` field.
- **Fix:** move `_cssUrlEscape` into a shared helper and use it in both modules.

### [BUG] Reply ignores the `Reply-To` header, so a reply to a mailing list goes to the poster

- **Location:** `static/js/emailInbox.js:901-903` (`toAddress = … : data.from_address`) and
  `static/js/emailInbox.js:995`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the reply's `To:` is `data.from_address` (`static/js/emailInbox.js:901-903`; only a
  message that is itself the user's own falls back to the original `To`, then `Cc`, then `From`),
  and no `Reply-To` header is consulted anywhere in the path.
  `grep -rn "Reply-To\|reply_to\b\|replyTo" routes/ static/js/ --include=*.py --include=*.js`
  (filtering out `in_reply_to` and `In-Reply-To`) returns one line,
  `routes/email_pollers.py:709: # (e.g. someone forging a Reply-To with our address as the`, a
  comment about the `From` header, not an implementation. The read response dict built in
  `_read_email_sync` (`routes/email_routes.py:3127-3145`) carries the sender, recipient and threading fields
  (`from_name`, `from_address`, `to`, then `cc`, `in_reply_to`, `references`) but no `Reply-To`. The `Cc:` for reply-all comes from the raw
  `To` and `Cc` headers via `buildReplyAllCc` (`static/js/emailLibrary/replyRecipients.js:20-27`),
  which is the standard behaviour.
- **Impact:** on any list that sets `Reply-To:` (Mailman, Google Groups, most ticketing systems) the
  user's reply is addressed to the individual who posted rather than to the list — the message lands
  in one person's mailbox instead of the thread the user meant to join. The direction is the safe
  one (a sender cannot redirect a reply), which is why this is a correctness bug rather than a
  security one; the draft's `To:` field does show the address that will be used.
- **Fix:** parse `Reply-To` in the read path, surface it, and prefer it (when it parses to a single
  address) for the reply's `To:`, falling back to `From`.
