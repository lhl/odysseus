# tests: documents, uploads, gallery and media

## Overview

`tests/test_attachment_refs.py`, `tests/test_doc_library_open_orphaned.py`, `tests/test_document_actions_nonstring.py`, `tests/test_document_ai_preview_refresh_js.py`, `tests/test_document_close_clears_active_route.py`, `tests/test_document_deeplink.py`, `tests/test_document_diff_discard_on_update_js.py`, `tests/test_document_editor_scroll.py`, `tests/test_document_library_delete_counters.py`, `tests/test_document_library_language_facet.py`, `tests/test_document_library_pdf_metadata.py`, `tests/test_document_pdf_marker.py`, `tests/test_document_processor_attachment_budget.py`, `tests/test_document_processor_empty_media_subtype.py`, `tests/test_document_render_pdf_iframe.py`, `tests/test_document_routes_shim.py`, `tests/test_document_session_owner_scope.py`, `tests/test_document_tidy_null_timestamp.py`, `tests/test_document_tool_owner_scope.py`, `tests/test_gallery_album_owner_scope.py`, `tests/test_gallery_delete_file_ordering.py`, `tests/test_gallery_endpoint_hardening.py`, `tests/test_gallery_endpoint_matching.py`, `tests/test_gallery_endpoint_ssrf.py`, `tests/test_gallery_exif_orientation.py`, `tests/test_gallery_filename_confinement.py`, `tests/test_gallery_image_endpoint_owner_scope.py`, `tests/test_gallery_image_privileges.py`, `tests/test_gallery_model_input_device.py`, `tests/test_gallery_null_user_routes.py`, `tests/test_gallery_owner_filter_single_user.py`, `tests/test_gallery_result_image_ssrf.py`, `tests/test_gallery_routes_shim.py`, `tests/test_image_models_nondict_system.py`, `tests/test_image_models_nonstring_search.py`, `tests/test_load_features_permission_error.py`, `tests/test_note_reminder_email_oauth.py`, `tests/test_note_reminder_fire_scope.py`, `tests/test_note_routes_shim.py`, `tests/test_notes_dom_xss_helpers.py`, `tests/test_notes_fail_closed_auth.py`, `tests/test_notes_search_reset_on_reopen_js.py`, `tests/test_notes_select_esc_listener_js.py`, `tests/test_notes_update_due_date.py`, `tests/test_notes_z_order_js.py`, `tests/test_pdf_ai_edit_derivative.py`, `tests/test_pdf_runtime.py`, `tests/test_upload_content_detection_magic.py`, `tests/test_upload_error_surfaced.py`, `tests/test_upload_handler_atomicity.py`, `tests/test_upload_handler_cleanup.py`, `tests/test_upload_handler_rename_owner.py`, `tests/test_upload_id_extension.py`, `tests/test_upload_id_validation.py`, `tests/test_upload_limits_centralized.py`, `tests/test_upload_multifile.py`, `tests/test_upload_routes_owner_scope.py`.

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
