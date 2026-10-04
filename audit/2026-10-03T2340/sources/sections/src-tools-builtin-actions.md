# src: scheduled built-in actions

## Overview

`src/builtin_actions.py` (3,436 lines) is the registry of work a scheduled task can run without
an LLM: housekeeping (sessions, documents, memory, research), the email passes (summarize, draft
replies, auto-translate, urgency triage), the calendar passes (extract events from mail, classify
events), the daily brief, sender-signature learning, skill test and audit, the admin-only shell
actions (`ssh_command`, `run_script`, `run_local`), and the Cookbook serve launcher. The scheduler
that invokes an action (`src/task_scheduler.py:1242`) is assigned to `src-research-scheduling`; the
task routes that validate and gate creation are assigned to `routes-skills-calendar-task` and are
cited here only where a finding needs them. The email helpers the actions call
(`routes/email_helpers.py`) belong to `routes-email`, the skills pipeline to
`routes-skills-calendar-task`, and the other ten `src/tool_*.py` files to the three sibling
`src-tools-*` sections.

## Coverage

**Read fully:** `src/builtin_actions.py` (3,436 lines). Every cited line was re-read at
`2992bf6d368a`.

**Read partially:**

- the scheduler call path `_execute_action` and its result handling
  (`src/task_scheduler.py:918-946`, `:1242-1268`)
- `RETIRED_HOUSEKEEPING_ACTIONS` (`:265-269`) and the retirement sweep (`:2345-2361`)
- `src/task_action_policy.py` (the admin-action set and `owner_has_admin_task_privileges`)
- `routes/task/task_routes.py:426-465` (create) and `:666-690` (update) to confirm the admin gate is
  applied on both write paths
- `routes/email_helpers.py` at `_imap_connect` (`:1200-1248`) and `_get_email_config` (`:1011-1066`)
- the `sender_signatures` schema (`:639-648`)
- `core/database.py` at `CalendarCal`/`CalendarEvent` (`:1838-1881`)
- `static/js/tasks.js:222-233`, `:449`, `:620`, `:1332`
- `src/settings.py:187`
- `tests/test_builtin_actions_owner_scope.py`, `tests/test_classify_events_memory_text.py`,
  `tests/test_email_urgency_checkpoint.py:97-140`, `:1170-1200`, and
  `tests/test_imap_uid_commands.py:78-108` to see what the suite pins

**Not read:**

- `src/task_scheduler.py` in full
- `routes/email_pollers.py` beyond `_run_auto_summarize_once`'s return strings (`:1320-1356`)
- the email, calendar, and skills route modules
- `services/memory/skills.py`
- `routes/skills_routes.py`
- every test not named above

No test suite was run.

## Findings

### [BUG] The email-urgency triage never reaches its LLM classifier, and still requires an LLM endpoint

- **Location:** `src/builtin_actions.py:2707`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** Every newly fetched UID takes the heuristic path and then `continue`s, so the
  classifier that follows is unreachable for every item:

  ```python
                  verdict = _heuristic_email_verdict(item)
                  cache.setdefault("uids", {})[item["uid"]] = verdict
                  per_uid_scores[key] = verdict
                  saved_classifications += 1
                  continue
                  # ── LLM-classify. JSON-only response; bullet-proof parse.
                  llm_attempts += 1
                  prompt = (
  ```

  The unreachable region runs from `:2708` to the end of the loop body at `:2820`; the second
  `saved_classifications += 1` (`:2815`) and both `failed_classifications.append` sites
  (`:2746`, `:2817`) are inside it, so the report's
  "N failed" line (`:3074-3075`) and its "Unclassified" list (`:3130-3142`) can never appear;
  `llm_attempts` (`:2440`) is never read. The user-editable rules are loaded at `:2437`
  (`urgency_prompt = settings.get("urgent_email_prompt", "")`), exposed as a textarea in the
  Tasks panel (`static/js/tasks.js:222-233`, `:1332`, default at `src/settings.py:187`), and
  interpolated only into the dead prompt (`:2717`, `f"User's rules:\n{urgency_prompt}\n\n"`).
  The heuristic returns a hardcoded `"spam": False` (`:2519`), so the spam verdict the dead block
  computes can no longer be set. The action's own docstring still describes the removed
  behaviour ("Scan unread emails across all accounts, LLM-triage new ones", `:2250-2251`), and
  the gate that only the LLM needs remains at `:2434-2435`:

  ```python
          # ── 2. Account retirement above is state maintenance and does not
          # depend on model availability. Scanning still requires the utility
          # primary/fallback candidates resolved for this task owner.
          if not candidates:
              return "No LLM endpoint available", False
  ```

  `git blame` puts the heuristic call and the `continue` in `4ab68b656` ("Polish mobile UI and
  editor workflows"); the LLM block was left in place. `_execute_action` records the `False`
  return as `run.status = "error"` (`src/task_scheduler.py:923-927`).
- **Impact:** A user who writes custom triage rules sees them silently ignored, and the report
  can never say a classification failed. On a deployment with no utility model configured, a
  task that never calls a model is recorded as an error. The heuristic still scores, tags, and
  notifies, so this is a lost feature and a wrong failure status, not a broken action.
- **Fix:** Pick one path. For heuristic-only triage, delete `:2708-2820`, the `candidates` gate
  at `:2434-2435`, the `urgency_prompt` read, and `llm_attempts`, and say in the docstring and
  the rules field that it is unused. To keep the LLM, drop the `continue`; the block below it
  already parses, clamps, and falls back.

### [BUG] `classify_events` classifies every user's calendar events with one user's memories

- **Location:** `src/builtin_actions.py:1369`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** The query selects from `CalendarEvent` alone — no join to `CalendarCal` and no
  owner filter:

  ```python
              events = db.query(CalendarEvent).filter(
                  CalendarEvent.dtstart >= now,
                  CalendarEvent.dtstart <= horizon,
                  CalendarEvent.status != "cancelled",
              ).all()
  ```

  `CalendarEvent` has no owner column; ownership is on `CalendarCal.owner`
  (`core/database.py:1843`). The sibling action in the same file scopes it and says why:

  ```python
              ev_q = db.query(CalendarEvent).join(CalendarCal).filter(
                  CalendarEvent.dtstart < tomorrow,
                  CalendarEvent.dtend > today,
                  CalendarEvent.status != "cancelled",
              )
              if owner:
                  ev_q = owner_filter(ev_q, CalendarCal, owner, include_shared=_allow_null)
  ```

  (`:1805-1812`, under the "v2 review HIGH-12" comment at `:1797-1804`.) The same function loads
  only the running owner's memories (`:1387`, `_Mem.owner == owner`) and prepends them to the
  prompt that classifies the batch (`:1435-1436`). `classify_events` is not in
  `ADMIN_ONLY_TASK_ACTIONS` (`src/task_action_policy.py:5-10`), so any user can schedule it. The
  existing test (`tests/test_builtin_actions_owner_scope.py:70`) fakes an event class with no
  owner and a `_Db.filter()` that returns every row, so it passes whatever the query filters.
- **Impact:** In a multi-user deployment, one user's scheduled run rewrites `event_type`,
  `importance`, and `color` on every other user's events, and other users' event titles are sent
  to the model alongside the runner's personal memory context. Single-user deployments see no
  difference.
- **Fix:** Join `CalendarCal` and apply `owner_filter(..., include_shared=_allow_null)` the way
  `daily_brief` does, and load memories for the same owner that owns the events.

### [BUG] `daily_brief` reads the default mailbox instead of the task owner's

- **Location:** `src/builtin_actions.py:1828`
- **Severity:** medium
- **Disposition:** next
- **Evidence:** The calendar and notes halves of this action were explicitly scoped for
  multi-user deployments (comment at `:1797-1804`, query at `:1805-1812`), but the email half
  connects with no owner:

  ```python
              import email as _email
              conn = _imap_connect(None)
  ```

  `_imap_connect` defaults `owner` to `""` (`routes/email_helpers.py:1200`), and
  `_get_email_config` documents what that does:

  ```python
        2. Else → the row with is_default=True (scoped to `owner` when given).
        ...
      SECURITY: without `owner`, the fallback queries (is_default, first-enabled)
      don't filter by user — so on a multi-user deploy a brand-new account would
      inherit whoever else's IMAP/SMTP creds happened to be the default. Pass
      `owner` from the route's auth dependency to scope the lookup.
  ```

  (`routes/email_helpers.py:1016`, `:1025-1028`; the unfiltered `is_default` query is at
  `:1059-1065`.) The other actions in this file pass the owner: `_imap_connect(acct.id,
  owner=owner)` (`:1198`), `_imap_connect(None, owner=owner)` (`:1597`, `:1684`). The one test that
  calls this action (`tests/test_imap_uid_commands.py:78`) passes `owner=""` and replaces
  `_imap_connect` with a lambda that ignores its arguments, so the missing owner is not
  exercised.
- **Impact:** In a multi-user deployment, any user's daily brief counts unread mail and quotes
  up to five sender/subject pairs from whichever account is the default (or the first enabled
  one), then persists that text as the task result in that user's assistant chat.
- **Fix:** `conn = _imap_connect(None, owner=owner)`.

### [DEAD-CODE] `action_tidy_calendar` is unreachable, and would delete across owners if it were reachable

- **Location:** `src/builtin_actions.py:853`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** The 100-line function (`:853-954`) is absent from `BUILTIN_ACTIONS`
  (`:3394-3416`), and the scheduler deletes any task whose action is in
  `RETIRED_HOUSEKEEPING_ACTIONS` (`src/task_scheduler.py:265-269`; sweep at `:2345-2361`).
  `_execute_action` returns `"Unknown action: ..."` for anything not in the registry
  (`src/task_scheduler.py:1246-1248`). The function itself queries and deletes without an owner
  filter:

  ```python
              events = db.query(CalendarEvent).order_by(CalendarEvent.dtstart).all()
  ...
                          db.delete(e)
  ```

  Its state-file constant is still imported (`:16`) and defined (`src/constants.py:35`).
  `action_ping_events` (`:1513-1515`) is the same shape: a `TaskNoop` stub absent from the
  registry. `static/js/tasks.js:449`, `:620` still carry an icon and a label for
  `tidy_calendar`.
- **Impact:** No user-visible behaviour today. The cost is maintenance and a trap: re-registering
  the action to revive calendar tidy would delete duplicate events for every user in a
  multi-user deployment.
- **Fix:** Delete `action_tidy_calendar` and its state constant, or re-register it behind the
  admin gate with the `CalendarCal` owner filter `daily_brief` uses. Remove the stale UI
  icon/label either way.

### [BUG] `action_learn_sender_signatures` records success when it did nothing

- **Location:** `src/builtin_actions.py:1632`
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** Two no-work exits return `True` instead of raising `TaskNoop`, which is the
  convention everywhere else in the file (`TaskNoop` at `:412`, raised at `:1018`, `:1039`,
  `:1075`, `:1103`, `:1277`):

  ```python
          mails = await _aio.to_thread(_pull_headers)
          if not mails:
              return "No emails to scan", True
  ...
          if not eligible:
              return "All sender sigs already cached (or no eligible senders)", True
  ```

  (`:1632`, `:1670`.) The scheduler drops a `TaskNoop` run row silently and records any other
  return as a run (`src/task_scheduler.py:923-927`, `:1267-1269`).
- **Impact:** A pass that scanned nothing appears as a successful Activity entry, unlike the
  other email actions, which noop instead. Low: the text is accurate; only the status is wrong.
- **Fix:** Raise `TaskNoop` from both branches.
