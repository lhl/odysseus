# tests: security, guard and prompt-injection

## Overview

`tests/test_auth_config_lock_concurrency.py`, `tests/test_auth_disabled_document_access.py`, `tests/test_auth_event_loop.py`, `tests/test_auth_policy.py`, `tests/test_auth_regressions.py`, `tests/test_auth_require_privilege_nondict.py`, `tests/test_auth_root_path.py`, `tests/test_auth_session_revocation.py`, `tests/test_db_stubs_helper.py`, `tests/test_is_youtube_url_nonstring.py`, `tests/test_is_youtube_url_nonstring_svc.py`, `tests/test_pr_blocker_audit.py`, `tests/test_pr_description_check.py`, `tests/test_prompt_injection_audit.py`, `tests/test_prompt_security.py`, `tests/test_security_headers_middleware.py`, `tests/test_security_headers_pdf_preview.py`, `tests/test_security_regressions.py`, `tests/test_token_cache_atomic_swap.py`, `tests/test_vault_password_not_in_argv.py`, `tests/test_vault_routes_shim.py`.

Say here what this section is responsible for, and where its boundary with a neighbouring
section falls. One or two sentences: a reader should be able to tell from this whether the
section covers the code they care about.

## Coverage

Not read. This section has no findings and no coverage claim. Everything it covers is
unreviewed.

<!--
Replace the coverage statement above before adding findings, and make it specific: which
files were read fully, which were read partially, and which were not read at all. Coverage
is a claim about this pass, so an unread file is named as unread.

Findings go below the coverage statement, one per heading, most severe first:

### [TAG] Short statement of what is wrong

- **Location:** `path/to/file.ts:120`
- **Severity:** high | medium | low
- **Disposition:** fix-now | next | backlog | wontfix
- **Issue:** #123          (optional; the issue tracking this)
- **Evidence:** what you read or ran, and what it showed.
- **Impact:** what goes wrong, and for whom.
- **Fix:** the smallest change that removes the problem.

A finding without Location, Severity, and Disposition fails `./audit.py check`. Quote the
code or the command output under Evidence; an assertion without evidence is not a finding.
Delete this comment once the section holds findings.
-->
