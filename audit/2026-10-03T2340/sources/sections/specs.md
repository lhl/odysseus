# Specifications

## Overview

`specs/` is the repository's implementation-truth map: 61 files, 5,165 lines, each opening with a
`Last updated: dev@<short-sha> | YYYY-MM-DD` stamp and each describing one subsystem's current
shape, ownership, contracts, security policy and known gaps. `specs/_readme.md` is the control
document: it sets the quality contract, the subsystem map, and the working rule that "if code and
specs disagree, treat code as ground truth".

This section checks the specs' claims against the code at `2992bf6d368a`. A spec sentence that
asserts a mechanism, a default, a file, an owner, or a detection rule that the tree does not have
is a finding here. The boundary runs the other way for code defects: when a spec correctly
describes a broken mechanism, the defect belongs to the section that owns the code, and this
section cross-references it instead of restating it (`services-search.md`, `services-media.md`,
`services-research.md`, `src-tools-capabilities-policy.md`). What is owned here is the sentence,
because the spec is what the next maintainer reads before touching the code, and a wrong sentence
costs them the work of re-deriving the truth.

The specs are, on the whole, accurate. Every `path:line` citation in `specs/*.md` resolves to an
existing file and an in-range line, and of the symbol-anchored citations only one paragraph
(`auth-security.md:89`) points more than three lines away from the symbol it names.

The mechanism-level claims I spot-checked held: `chat_messages_fts` is probed before use and message
rows are fetched with one `IN (...)` query (`src/session_search.py:121`, `:230`, `:267-269`), the
reserved-username set matches `src/owner_identity.py:14`, login still issues an `HttpOnly`
`SameSite=Lax` cookie with the seven-day `TOKEN_TTL` (`routes/auth_routes.py:187-193`,
`core/auth.py:53`), all eight `/api/image/*` routes carry `require_privilege(request,
"can_generate_images")`, the OpenAI reader keeps capabilities unknown and never reads `owned_by`
for identity (`src/model_capability_readers/openai.py`), and content fetching really does pin
`Accept-Encoding: identity` (`services/search/content.py:221`).

The findings below are the exceptions: each is a sentence whose claim the tree does not support, and
none of them is reported by another section. Three of the eleven — the CodeQL instruction, the
unresolvable stamps, and `/backgrounds` — are the ones a maintainer would otherwise have to
discover the hard way.

## Coverage

**Read fully:** 30 of the 61 assigned files.

Top level:

- `specs/_readme.md`
- `specs/agent-tools.md`
- `specs/auth-security.md`
- `specs/calendar-tasks-notes.md`
- `specs/chat.md`
- `specs/compare.md`
- `specs/context-building.md`
- `specs/cookbook-hwfit.md`
- `specs/documents-rag-uploads.md`
- `specs/email-contacts.md`
- `specs/frontend.md`
- `specs/gallery-editor-media.md`
- `specs/integrations.md`
- `specs/llm-models.md`
- `specs/memory-skills.md`
- `specs/model-capability-canonical.md`
- `specs/model-quirks.md`
- `specs/persistence.md`
- `specs/research.md`
- `specs/runtime.md`
- `specs/search.md`
- `specs/settings-admin.md`
- `specs/speech.md`
- `specs/testing-devops.md`

Provider specs:

- `specs/model-providers/_readme.md`
- `anthropic.md`
- `mistral.md`
- `moonshot-kimi.md`
- `ollama.md`
- `openai.md`

These are 19-218 line files read end-to-end.

**Read partially:**

- `specs/shell-mcp.md` (lines 40-100 and the `ShellService` claim at `:48`)
- `specs/model-providers/minimax.md` (lines 10-48, the catalog-shape and fallback sections)

**Not read:** `specs/model-providers/` minus the seven files named above — the 29 remaining
provider specs:

- `atlas-cloud.md`
- `azure-openai.md`
- `bedrock.md`
- `cerebras.md`
- `chatgpt-subscription.md`
- `cloudflare-workers-ai.md`
- `cohere.md`
- `deepseek.md`
- `fireworks.md`
- `github-copilot.md`
- `github-models.md`
- `google.md`
- `groq.md`
- `hugging-face.md`
- `llama-cpp.md`
- `lm-studio.md`
- `local-compatible-engines.md`
- `nvidia-nim.md`
- `openai-compatible.md`
- `opencode.md`
- `openrouter.md`
- `perplexity.md`
- `sglang.md`
- `siliconflow.md`
- `together.md`
- `venice.md`
- `vllm.md`
- `xai.md`
- `zai.md`

They are not claimed as reviewed; the citation check in `Checks run` covers them mechanically, which
is not the same as reading them.

**Checks run.** (1) A throwaway script (`/tmp/check_refs.py`, `/tmp/check_refs2.py`) that extracts
every `` `path:line` `` citation from `specs/*.md`, resolves the path, compares the line against the
file length, and — where the prose names a backticked symbol — measures the distance from the cited
line to the nearest occurrence of that symbol. Result: 0 missing files, 0 out-of-range lines, 2
symbol anchors more than three lines off, both on `specs/auth-security.md:89`. (2) `git cat-file -t`
and a scan of every commit object for the four distinct stamps in the set. (3) `ls`, `grep` and
`git log --all` over the files the findings name (`docs/`, `website/`, `.github/workflows/`,
`package.json`, `static/backgrounds.html`, `src/tool_index.py`, `src/model_capability_readers/`,
`services/search/core.py`, `services/shell/service.py`). (4) A probe script
(`/tmp/probe_backgrounds.py`) that calls `serve_html_with_nonce` with the path the `/backgrounds`
route builds. Line numbers are the working tree at `2992bf6d368a`.

### [DOC-DRIFT] `testing-devops.md` tells maintainers not to add the CodeQL workflow the repo added a month before the spec's own baseline

- **Location:** `specs/testing-devops.md:172`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the sentence in full: "Security metadata includes container Trivy SARIF upload,
  Dockerfile lint, dependency review, secret scan, workflow security linting, GitHub default-setup
  CodeQL, Dependabot metadata, and hardened PR/issue description checks that avoid unsafe
  head-branch execution. `docs/security-ci.md` documents CodeQL as a dynamic GitHub default-setup
  workflow; the repo should not add a checked-in CodeQL workflow while that default setup is
  active." The checked-in workflow exists and is not a default-setup helper — it is an advanced
  setup whose own header says so:

  ```
  # .github/workflows/codeql.yml:3-4
  # Advanced setup so CodeQL also runs on pull requests (including from forks),
  # surfacing findings before merge instead of only after a change lands on dev.
  ```

  It landed before the spec was written: `git log -1 --format="%h %cs %s" b07c1e3b` →
  `b07c1e3b 2026-07-21 ci: add CodeQL advanced setup to scan pull requests before merge (#5250)`,
  and `git merge-base --is-ancestor b07c1e3b e71f8ce` succeeds, so the file is present at the
  spec's own baseline `dev@e71f8ce` (2026-08-25). The current contributor documentation records the
  opposite arrangement from the spec: `website/security-ci.md:14-15` ("CodeQL uses the checked-in
  advanced configuration in `.github/workflows/codeql.yml`") and `:96-97` ("Under **Code
  scanning**, keep **Default setup** disabled. CodeQL is configured by
  `.github/workflows/codeql.yml`").
- **Impact:** A maintainer reconciling CI with the spec — the instruction is imperative, and the
  spec is the document the readme tells them to read before changing an area — would remove
  `.github/workflows/codeql.yml` or leave the contradiction standing. Removing it drops PR-time
  scanning for `actions`, `javascript-typescript` and `python` back to whatever the GitHub default
  setup does, which is not PR-gating, and the spec's own reference for the claim
  (`docs/security-ci.md`) no longer exists.
- **Fix:** Replace the clause with the current arrangement: CodeQL runs from the checked-in
  advanced configuration in `.github/workflows/codeql.yml` (three languages, `build-mode: none`,
  push to `dev`/`main`, PRs to `dev`, weekly), GitHub's Default setup stays disabled, and
  `website/security-ci.md` documents it.

### [DOC-DRIFT] 26 of the 61 specs are stamped with a baseline commit that does not exist in this repository

- **Location:** `specs/model-providers/minimax.md:3` (17 files stamped `dev@28d27ee | 2026-07-17`)
  and `specs/model-providers/chatgpt-subscription.md:3` (9 files stamped `dev@e57f60b | 2026-07-20`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `specs/_readme.md:15-16` requires the stamp to be "the upstream `dev` commit the
  spec text was inspected against", so a reader is expected to be able to look that commit up.
  Two of the four distinct stamps in the set do not resolve:

  ```
  $ for h in e71f8ce 2e2bb52 28d27ee e57f60b; do printf "%-10s " "$h"; git cat-file -t "$h"; done
  e71f8ce    commit
  2e2bb52    commit
  28d27ee    fatal: Not a valid object name 28d27ee
  e57f60b    fatal: Not a valid object name e57f60b
  $ git cat-file --batch-all-objects --batch-check | awk '$2=="commit"' | grep -c "^28d2\|^e57f"
  0
  $ git rev-parse --is-shallow-repository; git rev-list --count HEAD
  false
  2098
  ```

  The clone is not shallow and the July dates themselves are represented in history, so this is not
  a missing-fetch artifact: no object with either prefix exists. The 26 affected files are the 17
  `specs/model-providers/*.md` at `dev@28d27ee` (`atlas-cloud`, `azure-openai`, `bedrock`,
  `cerebras`, `cloudflare-workers-ai`, `fireworks`, `github-models`, `groq`,
  `local-compatible-engines`, `minimax`, `moonshot-kimi`, `nvidia-nim`, `perplexity`,
  `siliconflow`, `venice`, `xai`, `zai`) and the 9 at `dev@e57f60b` (`chatgpt-subscription`,
  `cohere`, `github-copilot`, `hugging-face`, `llama-cpp`, `lm-studio`, `sglang`, `together`,
  `vllm`); the 35 files at `dev@e71f8ce` (27) and `dev@2e2bb52` (8) resolve. The repository carries
  both a history-rewrite marker (`origin/backup/main-before-history-cleanup-20260910`) and a
  mid-July repository transfer (`cc4c7f42 chore: update repository URLs after organization transfer
  (#5622)`, 2026-07-20), either of which could explain stamps taken from a tree this clone does not
  contain — the backup branch does not contain them either, so the two stamps cannot be recovered
  from this clone at all.
- **Impact:** For 26 of 61 specs — the ones covering every provider except Anthropic, Mistral,
  Moonshot/Kimi, Ollama and OpenAI — the documented workflow of reading a spec against its baseline
  fails: `git show <stamp>:specs/...`, `git log <stamp>..HEAD -- specs/...` and "how much has moved
  since this was written" are all unavailable. A maintainer cannot tell whether one of those specs
  is two weeks stale or three months stale, which is exactly the judgement the stamp exists to
  support.
- **Fix:** Re-stamp those 26 files against a commit that exists in the published history the next
  time they are touched (the file is being edited anyway, so the merge-base at edit time is the
  right value), and add one line to `specs/_readme.md`'s quality contract saying the stamp must
  resolve in the published repository.

### [DOC-DRIFT] `/backgrounds` is documented as a live app-owned endpoint, but the page it serves has never existed

- **Location:** `specs/runtime.md:49`, `specs/frontend.md:21` (with `app.py:940-943`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `specs/runtime.md:49` lists the endpoint among the "Direct app-owned endpoints" and
  hedges: "`/backgrounds` points at `static/backgrounds.html`; if that file is absent or the route
  remains auth-gated, that is route/static drift rather than an intentional public contract."
  `specs/frontend.md:21` repeats it: "`/backgrounds` currently targets `static/backgrounds.html`;
  if that route remains, the file must exist or the route should be removed." Both halves of the
  hedge are true. The file is absent, and it has never been tracked in any commit:

  ```
  $ ls static/backgrounds.html
  ls: cannot access 'static/backgrounds.html': No such file or directory
  $ git log --oneline --all -- static/backgrounds.html
  (no output)
  ```

  The route reads it through a helper that maps a read failure to a logged 500
  (`src/app_helpers.py:44-46`), so the endpoint is a hard error:

  ```
  $ venv/bin/python /tmp/probe_backgrounds.py     # calls serve_html_with_nonce with the route's path
  Failed to read page /home/lhl/github/lhl/odysseus/static/backgrounds.html
  HTTPException 500 'Internal server error'
  ```

  The route's own docstring claims the opposite of the other half of the hedge
  (`app.py:942`: "Sandbox page for prototyping background effects. No auth required."), but
  `/backgrounds` is not in `AUTH_EXEMPT_EXACT` (`app.py:264-277`, which holds `/login`, the
  `/api/auth/*` endpoints, `/api/health` and `/api/version`), so under `AUTH_ENABLED` the
  middleware gates it. Nothing in the frontend links to it (`grep -rn backgrounds static/js/*.js
  static/index.html` matches only unrelated comments), and the helper and its test name it as a
  real caller (`src/app_helpers.py:33`, `tests/test_serve_html_with_nonce.py:4`).
- **Impact:** An authenticated user who visits `/backgrounds` gets a 500 and an
  `ERROR ... Failed to read page` traceback in the log for a page that has never shipped, and two
  specs plus two docstrings describe it as a working surface. A reader who trusts
  `specs/runtime.md`'s endpoint list will assume the route is intentional and hunt for a deployment
  fault instead of a missing file.
- **Fix:** Delete the route (`app.py:940-943`) and the two docstring mentions, or commit a
  `static/backgrounds.html` and decide whether the route is public — if it is meant to be, add
  `/backgrounds` to `AUTH_EXEMPT_EXACT`; if not, drop the "No auth required" line.

### [DOC-DRIFT] `agent-tools.md` describes `ALWAYS_AVAILABLE` as the catalog for a dozen tools; it holds three

- **Location:** `specs/agent-tools.md:67`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the spec sentence: "`src.tool_index.ALWAYS_AVAILABLE` is the retrieval catalog for
  high-frequency tools such as shell/python, web search/fetch, read/write/edit-file, code-nav,
  `manage_memory`, `ask_user`, `update_plan`, selected Cookbook serve controls, and `app_api`."
  The constant is a three-element set and was already one at the spec's own baseline:

  ```python
  # src/tool_index.py:35-45 (identical at e71f8ce)
  ALWAYS_AVAILABLE = frozenset({
      "manage_memory",
      "ask_user",
      "update_plan",
  })
  ```

  The list the spec describes resembles a different constant with a different job — the Personal
  Assistant's scheduled-task set at `src/tool_index.py:49-62` (`list_emails`, `send_email`,
  `manage_calendar`, `web_search`, `read_file`, `api_call`, `ui_control`, ...) — and neither
  constant contains `shell`, `python`, `app_api`, or a Cookbook serve control. The comment above the
  real set states the intent the spec contradicts: "Keep this deliberately tiny. Domain tools (web,
  documents, email, cookbook/model serving, files, settings, etc.) are injected by retrieval or
  keyword intent". `grep -rn ALWAYS_AVAILABLE audit/2026-10-03T2340/sources/sections/` finds no
  other section reporting this.
- **Impact:** A maintainer reading the spec to decide what is unconditionally in the prompt gets
  the wrong answer for `web_search`, `read_file`, `write_file`, `edit_file`, `bash`, `python`,
  `app_api` and the Cookbook controls, and may add a tool to `ALWAYS_AVAILABLE` believing it is
  already there (or assume a small-context model already carries those schemas). The next sentence
  in the spec — "Current prompt/schema assembly preserves only selected base tools
  unconditionally" — is the accurate one, which makes the pair self-contradictory.
- **Fix:** Rewrite the sentence to say what `ALWAYS_AVAILABLE` is (the three ambient tools:
  memory, `ask_user`, `update_plan`) and name `ASSISTANT_ALWAYS_AVAILABLE` separately for the
  scheduled-check-in set.

### [DOC-DRIFT] `minimax.md` bases provider identity on an `owned_by` discriminator and host matching that no reader implements

- **Location:** `specs/model-providers/minimax.md:16`, `:44`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the spec states the discriminator as fact — ":16 `created`, and `owned_by:
  minimax`. The `owned_by` discriminator identifies the provider shape" — and then uses it as the
  selection rule: ":44 Exact MiniMax hosts or the discriminating `owned_by: minimax` model-list
  shape select provider identity." Nothing reads it. There is no MiniMax capability reader:

  ```
  $ grep -rn "^VENDOR_" src/model_capability_readers/base.py
  20:VENDOR_GENERIC_OPENAI = "generic_openai"
  21:VENDOR_OPENAI = "openai"
  22:VENDOR_OPENROUTER = "openrouter"
  23:VENDOR_GOOGLE = "google"
  24:VENDOR_ANTHROPIC = "anthropic"
  25:VENDOR_OLLAMA = "ollama"
  26:VENDOR_LMSTUDIO = "lmstudio"
  27:VENDOR_LLAMACPP = "llamacpp"
  28:VENDOR_VLLM = "vllm"
  29:VENDOR_SGLANG = "sglang"
  30:VENDOR_HUGGINGFACE = "huggingface"
  31:VENDOR_UNKNOWN = "unknown"        # no VENDOR_MINIMAX
  $ ls src/model_capability_readers/
  base.py generic_openai.py google.py google_ai_studio_mapping.py __init__.py llamacpp.py
  lmstudio.py ollama.py openai.py openrouter.py       # no minimax.py
  ```

  `detect_vendor()` (`src/model_capability_readers/base.py:271-316`) maps an endpoint kind or a
  base-URL host to those vendors and has no MiniMax rule, so a MiniMax base URL falls through to
  `VENDOR_GENERIC_OPENAI`. The OpenAI-compatible reader that would receive such a payload keeps
  capabilities `unknown` on purpose (`src/model_capability_readers/openai.py:4-6`: "Those fields
  prove availability, not model capabilities"), and `owned_by` appears only in
  `OFFICIAL_MODEL_FIELDS` as a field to preserve, never as a discriminator. The only MiniMax-aware
  code in the tree keys off the *model name*, not the provider: `src/llm_core.py:1051`
  `_is_local_minimax_mlx_request` (name substring plus a local endpoint, to choose conservative
  sampling defaults) and `src/llm_core.py:1441`, where `"minimax"` sits in
  `_THINKING_MODEL_PATTERNS`. The spec file itself is one of the 26 with an unresolvable baseline
  (`dev@28d27ee`, 2026-07-17), so it cannot be diffed against the code it was written for.
- **Impact:** A maintainer implementing MiniMax support, or debugging why a MiniMax endpoint is
  classified as a generic OpenAI-compatible one, is told by the spec that a discriminator already
  selects the provider shape. It does not, so the spec sends them looking for a matcher that was
  never written — and the section that does own MiniMax behavior
  (`audit/.../sections/routes-cookbook.md:161`) is about the Cookbook serve path, not this rule.
- **Fix:** Mark the rule as not implemented in the runtime (the spec's own "Fallback And Current
  Gaps" section is the right home: state that identity today comes from whatever the endpoint's
  configured vendor is, that `owned_by` is preserved as raw metadata only, and that host matching
  does not exist), or implement the matcher the spec describes.

### [DOC-DRIFT] `search.md` presents cache invalidation and analytics as part of `comprehensive_web_search()`

- **Location:** `specs/search.md:36` (with `:11`, `:38`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** "`services/search/core.py` owns `comprehensive_web_search()`. It coordinates
  provider selection, fallback chains, ranking, optional fetch/content extraction, formatted prompt
  context, cache invalidation, and analytics." The last two items are not reachable from that
  function: `invalidate_search_cache`, `searxng_search_results` and `get_search_stats` have no
  caller outside the package and its `src/search` shim:

  ```
  $ grep -rn "invalidate_search_cache\|get_search_stats\|searxng_search_results" --include=*.py . \
      | grep -v venv/ | grep -v /audit/ | grep -v "^./tests/"
  ./services/search/__init__.py:6,7,12,24,25,28      (re-exports)
  ./services/search/analytics.py:123                 (definition)
  ./services/search/core.py:1,136,220,231            (definitions)
  ./src/search/__init__.py:6,7,12,18,19,22           (re-exports)
  ```

  The code-level finding is `services-search.md` (the search path never populates the cache it
  reads, and the analytics counters are never written); this finding is the spec's half of it —
  `specs/search.md:36` asserts the coordination as current behavior, so a reader tuning
  `search_result_count` or looking for where cache invalidation happens is pointed at a function
  that never calls either helper.
- **Impact:** A maintainer tuning `search_result_count`, or looking for the place where a search
  cache is invalidated, is pointed at a function that calls neither helper, and the spec sentence
  is the reason they would not look for the missing caller. The same sentence makes the search
  surface look instrumented, so an operator debugging search quality expects `get_search_stats`
  counters that nothing writes.
- **Fix:** Move "cache invalidation, and analytics" out of the ownership sentence and into
  `specs/search.md`'s gaps, or make `comprehensive_web_search()` call them as the sentence claims.

### [DOC-DRIFT] `shell-mcp.md` describes `ShellService` as "safe command execution" with "output caps"

- **Location:** `specs/shell-mcp.md:48`
- **Severity:** low
- **Disposition:** next
- **Evidence:** the spec sentence: "`services.shell.service.ShellService` is a small standalone
  subprocess abstraction with output caps. It does not own live route behavior, PTY/tmux paths,
  Windows shell selection, admin checks, or Cookbook package probes." Both descriptors overstate
  what the class does: the module docstring says "Shell service — safe command execution"
  (`services/shell/service.py:2`) but the class applies no command policy, and the `max_output`
  constructor argument is applied to the captured bytes only after `proc.communicate()` has returned
  (`services/shell/service.py:29`, `:63-66`), so the cap bounds the returned string rather than the
  memory a command can consume. The measurements and the code path are in `services-media.md` (its
  `ShellService` finding); this finding is the spec's half — `specs/shell-mcp.md:48` is one of the
  two documents that make the class sound governed. The spec file is stamped
  `dev@2e2bb52 | 2026-08-16`, an older baseline than the rest of the set.
- **Impact:** A maintainer looking for where shell output is bounded, or deciding whether the
  service is safe to expose to a new caller, is told by the spec that caps and safety already exist
  and stops looking. The class is described as an abstraction while its one behavioral guarantee
  (the cap) is applied at the wrong end of the pipe.
- **Fix:** Reword to "a thin subprocess wrapper that applies its output cap to the captured result
  after completion and enforces no command policy", or enforce the cap while streaming.

### [DOC-DRIFT] `research.md` states the owner-scoping rule without recording that its own compatibility surface does not meet it

- **Location:** `specs/research.md:129` (with `:120`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** `specs/research.md:129` states the rule unconditionally: "Research routes require an
  authenticated user, and start routes require research privilege. Persisted report access and
  mutations should return 404 for cross-owner or null-owner JSON." The spec's own compatibility
  section at `:120` records the duplicate handler as "compatibility/cleanup surface rather than
  canonical runtime truth; check parity before assuming it has every active-route field or policy
  behavior", and `:150` lists consolidating or retiring it as a gap — but neither sentence says
  that the parity check has been done and failed. It has: the duplicate's report-id handling has no
  path confinement, so an id containing `..` reaches outside `data/deep_research`, which is both a
  path-confinement defect and a failure of the owner-scoping rule stated at `:129`. The code
  evidence, the probe output and the reachability analysis are in `services-research.md`; this
  finding is that the spec's Security Policy section does not scope its rule to the live handler,
  and its compatibility note is phrased as a caution rather than as a known violation.
- **Impact:** A maintainer who treats the Security Policy section as the subsystem's contract
  (which is what it is for) will assume the rule holds everywhere "research" appears, and the one
  place where it does not is the surface the spec tells them to check parity on. The warning
  ("check parity") is correct but easy to read as boilerplate, since the same paragraph reads as
  though the copy is merely incomplete in fields.
- **Fix:** Add one clause to `specs/research.md:120`: the duplicate handler does not implement the
  `:129` owner/path rule, so callers must not use it for report access until it does.

### [DOC-DRIFT] Four spec references point at `docs/` paths that now live under `website/`

- **Location:** `specs/documents-rag-uploads.md:14`; `specs/testing-devops.md:18`, `:172`, `:174`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the citations name files in a `docs/` directory that does not exist in this tree:

  ```
  $ ls docs
  ls: cannot access 'docs': No such file or directory
  specs/documents-rag-uploads.md:14:  `docs/attachments.md`;
  specs/testing-devops.md:18:- contributor workflow docs in `CONTRIBUTING.md` and `docs/pr-blocker-audit.md`;
  specs/testing-devops.md:172:... `docs/security-ci.md` documents CodeQL ...
  specs/testing-devops.md:174:`scripts/pr_blocker_audit.py` ... documented in `docs/pr-blocker-audit.md`.
  ```

  All three targets exist one directory over, as the `website` section's own path list shows:
  `website/attachments.md`, `website/pr-blocker-audit.md`, `website/security-ci.md` (also
  `website/setup.md`, `website/agent-migration.md`, `website/backup-restore.md`). The same rename
  is why the CodeQL sentence above cites a path a reader cannot open. The citations were correct
  when the specs were written: the move is `c9dd68d8 refactor(docs): separate Pages site source
  (#6176)`, dated 2026-08-27 — two days *after* the `dev@e71f8ce` baseline and not an ancestor of
  it — so this is a mechanical follow-up to that refactor rather than an error in the specs.
- **Impact:** Four "see also" pointers in two specs are dead, including the one that carries the
  attachment contract (`docs/attachments.md`, named in `documents-rag-uploads.md:14` as "the public
  reference contract" for the upload surface). A maintainer following the citation finds nothing
  and cannot tell whether the document was deleted or moved.
- **Fix:** Rewrite the four citations to `website/...`.

### [DOC-DRIFT] `testing-devops.md` says `package.json` owns the Anthropic SDK

- **Location:** `specs/testing-devops.md:48`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** "`package.json` owns Node dependencies for Bombadil and the Anthropic SDK, and
  `package-lock.json` owns npm integrity/version state." The SDK was removed two months before the
  spec's baseline:

  ```
  $ grep -c anthropic package.json package-lock.json
  package.json:0
  package-lock.json:0
  $ git log -1 --format="%h %cs %s" 955544ae
  955544ae 2026-06-19 chore(deps): remove unused @anthropic-ai/sdk dependency (#4566)
  ```

  `package.json` declares one dev dependency, `@antithesishq/bombadil`. The same paragraph's test
  count ("roughly 728 `test_*.py` files") is also behind the tree it was written against — 793 at
  `e71f8ce` and 801 at `2992bf6d` — but the spec pre-empts that one by calling the count "a moving
  source metric, not a target", so only the dependency claim is wrong in a way that matters.
- **Impact:** Small: a maintainer auditing the Node dependency surface (for supply-chain or
  licensing work) is told there is an Anthropic SDK dependency to review, and the file that would
  document such a removal — this paragraph — does not record it. `DEPENDENCY`-category work that
  trusts the spec will look for a package that is gone.
- **Fix:** Change the sentence to name Bombadil as the only declared Node dependency.

### [DOC-DRIFT] `auth-security.md`'s trigger-attribution paragraph anchors two symbols about eleven lines away from the code they name

- **Location:** `specs/auth-security.md:89`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the paragraph is the spec's account of how scheduled-task actions attribute
  ownership, and it cites four locations. Two of them do not land on the symbol they name:

  ```
  $ sed -n '89p' specs/auth-security.md
  ... `_execute_action` (`src/task_scheduler.py:1231`) invokes the action with `owner=task.owner` ...
  ... the `manage_tasks` agent tool (`src/tools/system.py:469`) ...
  ... and success-chained tasks (`src/task_scheduler.py:1063-1074`), which additionally require ...
  ```

  `src/task_scheduler.py:1231` is inside `_log_result_to_assistant`'s body; `async def
  _execute_action` is at `:1242`, and the `owner=task.owner` it is cited for is at `:1256`. The
  chaining block the range is cited for starts at `:1074` ("# Task chaining — trigger the next task
  on success", owner check at `:1078`, cycle check at `:1083`), so `:1063-1074` ends where the code
  begins. `src/tools/system.py:469` is the `if owner and task.owner != owner:` check inside
  `do_manage_tasks` (defined at `:274`) — six lines above the `run_task_now` call at `:475` — so it
  is defensible as a trigger anchor but does not match the "the `manage_tasks` agent tool"
  phrasing. The paragraph's substantive claims all hold
  (`kwargs = {"owner": task.owner, ...}` at `:1256`; the chain owner and cycle checks at
  `:1078`/`:1083`), and a sibling section already cites the correct line for the same function
  (`src-chat-session.md:48` uses `_execute_action` (`:1242-1275`)). A mechanical pass over every
  symbol-anchored citation in `specs/*.md` (`/tmp/check_refs2.py`) found these two as the only
  anchors more than three lines from their symbol.
- **Impact:** Small and mechanical: a reader auditing the most security-sensitive attribution
  paragraph in the spec set lands on the logging helper or on the end of the previous block and has
  to search for the real symbol. The claims are right, so nothing is misled about behavior — only
  the navigation is wrong.
- **Fix:** Update the two anchors (`src/task_scheduler.py:1242`, `:1074-1086`) and consider
  `src/tools/system.py:274` for the tool.
