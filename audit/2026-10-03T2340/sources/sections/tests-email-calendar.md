# tests: email, calendar and webhooks

## Overview

`tests/test_ai_image_url_safety.py`, `tests/test_ai_interaction_owner_scope.py`, `tests/test_caldav_bidirectional_sync.py`, `tests/test_caldav_client_cleanup.py`, `tests/test_caldav_google_principal_url.py`, `tests/test_caldav_prune_parse_failure.py`, `tests/test_caldav_redirect_hardening.py`, `tests/test_caldav_sync_prune_local_events.py`, `tests/test_caldav_sync_uid_scope.py`, `tests/test_caldav_test_connection_ssl.py`, `tests/test_caldav_url_hardening.py`, `tests/test_caldav_url_nonstring.py`, `tests/test_caldav_writeback.py`, `tests/test_caldav_writeback_route.py`, `tests/test_calendar_batch_events.py`, `tests/test_calendar_cli_overlap.py`, `tests/test_calendar_css_url_escape_js.py`, `tests/test_calendar_default_transaction.py`, `tests/test_calendar_event_contrast.py`, `tests/test_calendar_import_zero_duration.py`, `tests/test_calendar_list_range_aliases.py`, `tests/test_calendar_owner_scope.py`, `tests/test_calendar_parse_dt_naive.py`, `tests/test_calendar_parse_dt_time_first.py`, `tests/test_calendar_parse_dt_tonight.py`, `tests/test_calendar_recurrence.py`, `tests/test_calendar_reminder_minutes_parsing.py`, `tests/test_calendar_rrule.py`, `tests/test_calendar_rrule_until_utc.py`, `tests/test_calendar_update_event_tz.py`, `tests/test_calendar_utils_dates_js.py`, `tests/test_contacts_add_null_name.py`, `tests/test_contacts_carddav_security.py`, `tests/test_contacts_import_nonstring.py`, `tests/test_contacts_routes_shim.py`, `tests/test_contacts_vcard_parse.py`, `tests/test_diagnostics_logs.py`, `tests/test_diagnostics_service_route.py`, `tests/test_email_account_default_serialization.py`, `tests/test_email_account_port_validation.py`, `tests/test_email_decode_header.py`, `tests/test_email_envelope_recipients.py`, `tests/test_email_fallback_reconnect.py`, `tests/test_email_gmail_fetch_flags.py`, `tests/test_email_helpers_decode_header_spaces.py`, `tests/test_email_imap_timeout.py`, `tests/test_email_library_bulk_actions.py`, `tests/test_email_library_prewarm.py`, `tests/test_email_linkify_security_js.py`, `tests/test_email_oauth.py`, `tests/test_email_oauth_connect_smtp_security.py`, `tests/test_email_oauth_docker_config.py`, `tests/test_email_oauth_settings_redirect.py`, `tests/test_email_open_dedup_js.py`, `tests/test_email_owner_scope.py`, `tests/test_email_ownerless_account_owner_scope.py`, `tests/test_email_polly_imap_leak.py`, `tests/test_email_read_mark_seen.py`, `tests/test_email_registry_sync.py`, `tests/test_email_send_only_no_inbox.py`, `tests/test_email_smtp_security.py`, `tests/test_email_split_border_css.py`, `tests/test_email_summary_error_ui_js.py`, `tests/test_email_summary_llm.py`, `tests/test_email_test_connection_oauth.py`, `tests/test_email_thread_parser_nonstring.py`, `tests/test_email_uid_no_seqno_fallback.py`, `tests/test_email_unsubscribe_candidates.py`, `tests/test_email_urgency_checkpoint.py`, `tests/test_ics_escape.py`, `tests/test_ics_export_escaping.py`, `tests/test_ics_import_dedup_tz.py`, `tests/test_imap_leak_fixes.py`, `tests/test_imap_mailbox_quoting.py`, `tests/test_imap_move_uid.py`, `tests/test_imap_uid_commands.py`, `tests/test_web_fetch_plaintext.py`, `tests/test_web_fetch_size_caps.py`, `tests/test_web_search_query_sanitization.py`, `tests/test_web_search_raw_json_tool_call.py`, `tests/test_web_search_time_filter.py`, `tests/test_web_search_tool_icon_js.py`, `tests/test_web_user_agent_constant.py`, `tests/test_webhook_dns_rebinding_pin.py`, `tests/test_webhook_emitters_use_manager.py`, `tests/test_webhook_routes_shim.py`, `tests/test_webhook_sanitize_error_ipv6.py`, `tests/test_webhook_ssrf_resilience.py`, `tests/test_webhook_task_refs.py`, `tests/test_webhook_trigger_auth_exempt.py`.

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
