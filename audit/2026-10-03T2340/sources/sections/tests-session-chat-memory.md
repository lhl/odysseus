# tests: session, chat, memory and RAG

## Overview

`tests/test_chat_attachment_picker.py`, `tests/test_chat_cached_model_normalization.py`, `tests/test_chat_helpers.py`, `tests/test_chat_helpers_bg_tasks_tracked.py`, `tests/test_chat_image_routing.py`, `tests/test_chat_metrics.py`, `tests/test_chat_model_provenance_js.py`, `tests/test_chat_preprocess_tool_policy.py`, `tests/test_chat_processor_pinned_memory.py`, `tests/test_chat_processor_web_search.py`, `tests/test_chat_route_tool_policy.py`, `tests/test_chat_stream_errors_js.py`, `tests/test_chat_stream_scope.py`, `tests/test_chat_tool_screenshot_xss.py`, `tests/test_chat_upload_limit_config.py`, `tests/test_chat_url_prefetch_failure_context.py`, `tests/test_chatgpt_subscription_routes.py`, `tests/test_chroma_client.py`, `tests/test_context_budget.py`, `tests/test_context_cache_per_endpoint.py`, `tests/test_context_compactor.py`, `tests/test_context_compactor_nonstring.py`, `tests/test_memory_add_submit_regression.py`, `tests/test_memory_audit_timeout.py`, `tests/test_memory_bullet_extraction.py`, `tests/test_memory_cli_add_nondict.py`, `tests/test_memory_extract_chat_nondict.py`, `tests/test_memory_extraction_parse.py`, `tests/test_memory_extractor_rows.py`, `tests/test_memory_extractor_vector_cross_tenant.py`, `tests/test_memory_extractor_vector_degraded.py`, `tests/test_memory_fallback_dislike.py`, `tests/test_memory_imports.py`, `tests/test_memory_owner_isolation.py`, `tests/test_memory_provider.py`, `tests/test_memory_recall_nondict_rows.py`, `tests/test_memory_routes_session_owner.py`, `tests/test_memory_routes_shim.py`, `tests/test_memory_store_unreadable_no_wipe.py`, `tests/test_memory_validate_entries_nondict.py`, `tests/test_personal_delete_file_confinement.py`, `tests/test_personal_dir_symlink_escape.py`, `tests/test_personal_docs_exclusions.py`, `tests/test_personal_docs_keyword_nondict.py`, `tests/test_personal_docs_lists.py`, `tests/test_personal_docs_office_index.py`, `tests/test_personal_docs_pdf_index.py`, `tests/test_personal_docs_state_store.py`, `tests/test_personal_index_hidden_dirs.py`, `tests/test_personal_remove_dir_confinement.py`, `tests/test_personal_upload_isolation.py`, `tests/test_personal_upload_privilege.py`, `tests/test_rag_index_hidden_dirs.py`, `tests/test_rag_keyword_fallback_owner.py`, `tests/test_rag_manager_owner_compat.py`, `tests/test_rag_remove_directory_scope.py`, `tests/test_rag_search_signature.py`, `tests/test_rag_server_directory_nonstring.py`, `tests/test_rag_vector_id_stability.py`, `tests/test_rag_vector_rename_owner.py`, `tests/test_searchservice_search_call.py`, `tests/test_session_actions_cleanup.py`, `tests/test_session_concurrent.py`, `tests/test_session_context_excludes_slash.py`, `tests/test_session_discovery_message_count.py`, `tests/test_session_endpoint_owner_scope.py`, `tests/test_session_export_filename.py`, `tests/test_session_export_nonstring_content.py`, `tests/test_session_ghost_delete.py`, `tests/test_session_image_cleanup.py`, `tests/test_session_list_owner_scope.py`, `tests/test_session_manager.py`, `tests/test_session_manager_cleanup.py`, `tests/test_session_manager_persist_guard.py`, `tests/test_session_mode_helpers.py`, `tests/test_session_owner_attribution.py`, `tests/test_session_routes_utcnow.py`, `tests/test_session_search.py`, `tests/test_session_search_batch_fetch.py`, `tests/test_session_tools_registry.py`, `tests/test_topic_analyzer.py`.

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
