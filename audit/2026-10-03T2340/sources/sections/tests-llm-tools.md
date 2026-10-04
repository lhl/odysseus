# tests: LLM, tools and agent loop

## Overview

`tests/test_action_intents.py`, `tests/test_action_intents_shell_verbs.py`, `tests/test_agent_bash_windows.py`, `tests/test_agent_loop.py`, `tests/test_agent_loop_tool_output_truncation.py`, `tests/test_agent_migration_manifest.py`, `tests/test_agent_round_model_provenance_ui.py`, `tests/test_agent_rounds_exhausted.py`, `tests/test_agent_state_dir_confinement.py`, `tests/test_agent_thread_dot_alignment_css.py`, `tests/test_agent_tool_budget_nonnumeric.py`, `tests/test_agent_tools_truncate_nonstring.py`, `tests/test_app_config_shared_fetch_js.py`, `tests/test_app_db_permissions.py`, `tests/test_app_initializer_memory_vector_degraded.py`, `tests/test_app_static_mime.py`, `tests/test_ask_user_persistence.py`, `tests/test_ask_user_tool.py`, `tests/test_bg_job_tools.py`, `tests/test_bg_jobs_store.py`, `tests/test_bg_monitor_stream.py`, `tests/test_compaction_summary_failure.py`, `tests/test_loop_breaker_runaway.py`, `tests/test_mcp_add_server_args_validation.py`, `tests/test_mcp_cache_invalidation.py`, `tests/test_mcp_common_truncate.py`, `tests/test_mcp_dependency_compatibility.py`, `tests/test_mcp_email_decode_header_spaces.py`, `tests/test_mcp_manager.py`, `tests/test_mcp_memory_owner_scope.py`, `tests/test_mcp_oauth.py`, `tests/test_mcp_param_hint_hardening.py`, `tests/test_mcp_reconnect_args.py`, `tests/test_mcp_routes_shim.py`, `tests/test_mcp_tool_params_in_prompt.py`, `tests/test_research_chat_stream_owner.py`, `tests/test_research_endpoint_owner_scope.py`, `tests/test_research_handler_analyzed_urls.py`, `tests/test_research_handler_path_confinement.py`, `tests/test_research_handler_raw_nondict.py`, `tests/test_research_handler_sources_nondict.py`, `tests/test_research_owner_scope_routes.py`, `tests/test_research_probe_errors.py`, `tests/test_research_query_fallback.py`, `tests/test_research_report_read.py`, `tests/test_research_routes_path_confinement.py`, `tests/test_research_routes_shim.py`, `tests/test_research_service.py`, `tests/test_research_session_id_validation.py`, `tests/test_research_source_link_xss.py`, `tests/test_research_status_avg_duration.py`, `tests/test_research_utils.py`, `tests/test_research_utils_low_quality_nonstring.py`, `tests/test_schedule_email_offset_normalization.py`, `tests/test_scheduler_prompt_cache_time.py`, `tests/test_scheduler_restart_doublefire.py`, `tests/test_scheduler_scheduled_time_validation.py`, `tests/test_search_analytics_defaults.py`, `tests/test_search_cache_invalidation.py`, `tests/test_search_config_no_key_leak.py`, `tests/test_search_config_provider_key.py`, `tests/test_search_content_block_source_index.py`, `tests/test_search_content_extraction_parity.py`, `tests/test_search_content_url_guards.py`, `tests/test_search_module_consolidation.py`, `tests/test_search_provider_json.py`, `tests/test_search_query.py`, `tests/test_search_query_entities_nonstring.py`, `tests/test_search_query_nonstring.py`, `tests/test_search_query_unicode_names.py`, `tests/test_search_ranking.py`, `tests/test_search_ranking_recency.py`, `tests/test_search_ranking_sports_substring.py`, `tests/test_search_ranking_subject_substring.py`, `tests/test_search_routes_shim.py`, `tests/test_search_service_nondict_rows.py`, `tests/test_skill_edit_no_collapse_on_outside_click_js.py`, `tests/test_skill_extractor_json.py`, `tests/test_skill_extractor_rows.py`, `tests/test_skill_extractor_stray_brace.py`, `tests/test_skill_format_timestamp.py`, `tests/test_skill_frontmatter_escape_roundtrip.py`, `tests/test_skill_importer.py`, `tests/test_skill_importer_dns_pinning.py`, `tests/test_skill_importer_security.py`, `tests/test_skill_importer_ssrf_redirect.py`, `tests/test_skill_index_prompt_injection.py`, `tests/test_skill_index_toolset_gating.py`, `tests/test_skill_save_no_rename.py`, `tests/test_skills_delete_owner.py`, `tests/test_skills_manager_owner_isolation.py`, `tests/test_skills_routes_nondict.py`, `tests/test_skills_routes_owner_update.py`, `tests/test_skills_tag_token_match.py`, `tests/test_task_chain_owner_scope.py`, `tests/test_task_cookbook_admin_gate.py`, `tests/test_task_endpoint_normalization.py`, `tests/test_task_routes_shim.py`, `tests/test_task_scheduler_cache.py`, `tests/test_task_scheduler_cancel.py`, `tests/test_task_scheduler_session_delivery.py`, `tests/test_task_session_folder.py`, `tests/test_task_shell_tools.py`, `tests/test_tool_approval_frontend_routing.py`, `tests/test_tool_approval_single_action_scope.py`, `tests/test_tool_approval_task_scope.py`, `tests/test_tool_approvals.py`, `tests/test_tool_implementations_shim.py`, `tests/test_tool_index_keyword_boundaries.py`, `tests/test_tool_index_schema_parity.py`, `tests/test_tool_output_prompt_injection.py`, `tests/test_tool_parsing_bare_end_marker.py`, `tests/test_tool_parsing_hermes_json.py`, `tests/test_tool_parsing_nonstring.py`, `tests/test_tool_path_confinement.py`, `tests/test_tool_policy.py`, `tests/test_tool_rag_contacts_domain.py`, `tests/test_tool_rag_keyword_hints.py`, `tests/test_tool_support_heuristic.py`, `tests/test_tool_task_cancelled_on_disconnect.py`, `tests/test_tool_utils_import_clean.py`.

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
