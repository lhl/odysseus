# tests: remaining test modules

## Overview

`tests/bombadil-spec.ts`, `tests/live_thinking_scheduler.test.mjs`, `tests/markdown_codefence_placeholder_regression.mjs`, `tests/test_active_document_clear.py`, `tests/test_active_email_reply_guard.py`, `tests/test_add_directory_event_loop.py`, `tests/test_admin_device_flow_static.py`, `tests/test_admin_tools_registry.py`, `tests/test_admin_wipe_gallery.py`, `tests/test_admin_wipe_routes_shim.py`, `tests/test_amd_gpu_check_args.py`, `tests/test_anthropic_response_parse.py`, `tests/test_api_call_integration_routing.py`, `tests/test_api_chat_security.py`, `tests/test_api_key_file_permissions.py`, `tests/test_api_key_manager_atomic_save.py`, `tests/test_api_key_manager_corrupt_load.py`, `tests/test_api_key_manager_resilience.py`, `tests/test_api_token_routes.py`, `tests/test_api_token_tool_authority.py`, `tests/test_api_token_user_route_gate.py`, `tests/test_app.py`, `tests/test_approved_replay_message_shape.py`, `tests/test_archived_sessions_model_filter.py`, `tests/test_atomic_io.py`, `tests/test_aux_llm_owner_scope.py`, `tests/test_backup_cli_security.py`, `tests/test_backup_import_cross_user_dedup.py`, `tests/test_backup_import_skills.py`, `tests/test_backup_import_skills_dedup.py`, `tests/test_blind_compare_redaction.py`, `tests/test_budget_auto_sentinel.py`, `tests/test_build_user_content_pdf_marker.py`, `tests/test_builtin_actions_cookbook_serve_state.py`, `tests/test_builtin_actions_nonstring.py`, `tests/test_builtin_actions_owner_scope.py`, `tests/test_builtin_mcp_bg_tasks.py`, `tests/test_builtin_mcp_npx_cache.py`, `tests/test_builtin_mcp_pythonpath.py`, `tests/test_builtin_memory_consolidation.py`, `tests/test_cache_affinity_local_only.py`, `tests/test_canvas_coords_empty_touches_js.py`, `tests/test_carddav_password_encryption.py`, `tests/test_censor_pref_js.py`, `tests/test_cerebras_cache_affinity.py`, `tests/test_check_outbound_url_nonstring.py`, `tests/test_checkin_digest_owner_scope.py`, `tests/test_ci_authoritative_validation.py`, `tests/test_claim_ownerless_json.py`, `tests/test_classify_events_memory_text.py`, `tests/test_cleanup_owner_scope.py`, `tests/test_cleanup_routes_shim.py`, `tests/test_cleanup_service_utcnow.py`, `tests/test_code_nav_tools.py`, `tests/test_codex_cookbook_admin_gate.py`, `tests/test_codex_ssh_host_validation.py`, `tests/test_compact_truncate_tool_call_args.py`, `tests/test_companion_pairing.py`, `tests/test_companion_readonly.py`, `tests/test_compare_ask_user_routing.py`, `tests/test_compare_endpoint_owner_scope.py`, `tests/test_compare_js.py`, `tests/test_compare_routes_shim.py`, `tests/test_compare_stop_disconnect_poll.py`, `tests/test_composer_arrow_up_recall_js.py`, `tests/test_compute_next_run_monthly_clamp.py`, `tests/test_consolidate_memory_explicit_drops.py`, `tests/test_copilot.py`, `tests/test_copilot_routes.py`, `tests/test_copy_message_strips_thinking_js.py`, `tests/test_cors_preflight.py`, `tests/test_database_utcnow.py`, `tests/test_ddg_redirect_resolution.py`, `tests/test_deep_research_date_context.py`, `tests/test_deep_research_extraction_controls.py`, `tests/test_deep_research_parse_json_array_echo.py`, `tests/test_deep_research_search_error.py`, `tests/test_deep_research_synthesis_resilience.py`, `tests/test_delete_message_no_session.py`, `tests/test_delete_user_invalidates_token_cache.py`, `tests/test_delete_user_revokes_api_tokens.py`, `tests/test_deleted_session_sidebar_regression.py`, `tests/test_derive_title_nonstring.py`, `tests/test_device_flow_routes.py`, `tests/test_dialog_aria.py`, `tests/test_diffusion_server_security.py`, `tests/test_digest_windows.py`, `tests/test_direct_upload_limits.py`, `tests/test_docker_devops_hardening.py`, `tests/test_docs_no_orphan_images.py`, `tests/test_docs_query_nondict_rows.py`, `tests/test_edit_file.py`, `tests/test_editor_draft_payload.py`, `tests/test_emoji_shortcodes_js.py`, `tests/test_emoji_svg_hardening.py`, `tests/test_esc_menu_stack_js.py`, `tests/test_estimate_tokens_tool_calls.py`, `tests/test_external_context_tool_gate.py`, `tests/test_extract_quotes.py`, `tests/test_extract_skill_json_nonstring.py`, `tests/test_extract_statistics.py`, `tests/test_extract_urls.py`, `tests/test_fastembed_cache_path.py`, `tests/test_fenced_example_not_executed_for_native_models.py`, `tests/test_fenced_inline_args.py`, `tests/test_fenced_invoke_no_raw_xml.py`, `tests/test_focused_test_guidance.py`, `tests/test_font_routes.py`, `tests/test_foreground_model_routing.py`, `tests/test_fork_session_metadata.py`, `tests/test_form_markdown_roundtrip.py`, `tests/test_forwarded_message_divider.py`, `tests/test_function_call_non_object_args.py`, `tests/test_function_model_tool_call.py`, `tests/test_gemma_tool_call_parsing.py`, `tests/test_generated_image_confinement.py`, `tests/test_gmail_quote_attribution_js.py`, `tests/test_group_character_dropdown.py`, `tests/test_group_chat_storage.py`, `tests/test_harmonize_masks_invalid_layers_js.py`, `tests/test_harmony_tool_aliasing.py`, `tests/test_helpers_import_state.py`, `tests/test_hex_to_rgb_js.py`, `tests/test_history_compact_tool_calls.py`, `tests/test_history_db_fallback_hidden.py`, `tests/test_history_display_model_hydration.py`, `tests/test_history_order_by_timestamp_regression.py`, `tests/test_history_routes_shim.py`, `tests/test_history_topics_owner_scope.py`, `tests/test_icloud_imap_full_fetch.py`, `tests/test_inside_base_dir_nonstring.py`, `tests/test_integration_api_call_ssrf.py`, `tests/test_integrations_api_call_truncation.py`, `tests/test_integrations_store_shape.py`, `tests/test_integrations_url_join.py`, `tests/test_interactive_gate_passive_paths.py`, `tests/test_internal_api_base.py`, `tests/test_issue_description_check.py`, `tests/test_keybind_altgr_js.py`, `tests/test_kimi_code_hosts.py`, `tests/test_kimi_code_user_agent.py`, `tests/test_kokoro_optional_requirements.py`, `tests/test_kv_cache_invalidation_2927.py`, `tests/test_lang_icon_null_opts_js.py`, `tests/test_launcher.py`, `tests/test_legacy_default_fallback_ui.py`, `tests/test_live_fallback_round_attribution.py`, `tests/test_live_strip_email_tool_fences.py`, `tests/test_live_thinking_chat_integration.py`, `tests/test_live_thinking_scheduler_js.py`, `tests/test_llama_server_models_url.py`, `tests/test_llamacpp_discovery.py`, `tests/test_lmstudio_discovery.py`, `tests/test_lmstudio_models_url.py`, `tests/test_lmstudio_vision.py`, `tests/test_local_endpoint_api_key_js.py`, `tests/test_local_endpoint_js.py`, `tests/test_log_safety.py`, `tests/test_manage_mcp_command_allowlist.py`, `tests/test_manage_memory_blank_id.py`, `tests/test_manage_memory_list.py`, `tests/test_manage_notes_owner_gate.py`, `tests/test_manage_settings_token_budget.py`, `tests/test_manage_skills_action_required.py`, `tests/test_manage_tasks_owner_scope.py`, `tests/test_markdown_dom_xss_helpers.py`, `tests/test_markdown_lazy_lib_loading_js.py`, `tests/test_markdown_rendering_js.py`, `tests/test_markdown_table_row_js.py`, `tests/test_markitdown_format_nonstring.py`, `tests/test_markitdown_runtime.py`, `tests/test_match_model_key_js.py`, `tests/test_matchescombo_nonstring_js.py`, `tests/test_merge_last_assistant_rows.py`, `tests/test_migrate_faiss_to_chroma.py`, `tests/test_misfenced_read_file_tool_call.py`, `tests/test_mlx_image_server_security.py`, `tests/test_modal_dock_composer_clearance.py`, `tests/test_multiple_mcp_servers_timeout.py`, `tests/test_native_tool_result_threading.py`, `tests/test_new_chat_clears_input.py`, `tests/test_new_chat_model_preference.py`, `tests/test_nix_upload_text.py`, `tests/test_null_owner_gates.py`, `tests/test_odysseus_dispatcher.py`, `tests/test_odysseus_doc_fence_normalization.py`, `tests/test_og_image_extraction.py`, `tests/test_ollama_multimodal.py`, `tests/test_ollama_port_detection.py`, `tests/test_ollama_runner_hint.py`, `tests/test_ordinal_suffix_js.py`, `tests/test_owned_document_query.py`, `tests/test_owner_identity.py`, `tests/test_panel_loader_js.py`, `tests/test_parse_due_time_first.py`, `tests/test_parse_msg_content_jsonlike_string.py`, `tests/test_plain_ui_control_open_panel.py`, `tests/test_plan_mode.py`, `tests/test_platform_compat.py`, `tests/test_poll_endpoint_no_task_interrupt.py`, `tests/test_popup_opener_isolation_js.py`, `tests/test_portal_dropdown_z_js.py`, `tests/test_pr6020_browser_review_regressions.py`, `tests/test_pr6020_rebase_regressions.py`, `tests/test_prefs_atomic_write.py`, `tests/test_prefs_routes.py`, `tests/test_prefs_single_user_no_clobber.py`, `tests/test_preset_atomic_save.py`, `tests/test_preset_expand_owner_scope.py`, `tests/test_preset_fill_missing_defaults.py`, `tests/test_preset_local_storage_js.py`, `tests/test_preset_store_shape.py`, `tests/test_promote_image_fields.py`, `tests/test_public_blocked_tool_nonstring.py`, `tests/test_question_type_detection.py`, `tests/test_rate_limiter.py`, `tests/test_readiness.py`, `tests/test_readme_ascii_fenced.py`, `tests/test_realesrgan_torchvision_compat.py`, `tests/test_redos_cal_extract.py`, `tests/test_redos_llm_parsers.py`, `tests/test_redos_think_blocks.py`, `tests/test_redos_verdict_continuation.py`, `tests/test_redos_xml_tool_parsers.py`, `tests/test_reminder_ntfy_ssrf.py`, `tests/test_rename_user_case_insensitive.py`, `tests/test_rename_user_owner_sync.py`, `tests/test_rename_user_token_cache.py`, `tests/test_replace_messages_multimodal.py`, `tests/test_replace_messages_upload_reservations.py`, `tests/test_reply_all_cc_nonstring_js.py`, `tests/test_reply_recipients_js.py`, `tests/test_resend_message_nondestructive.py`, `tests/test_reserved_username_admin_escalation.py`, `tests/test_resolve_endpoint_fallbacks.py`, `tests/test_resolve_model_offloaded.py`, `tests/test_resolve_session_auth_chatgpt.py`, `tests/test_resolve_upload_path_nondict.py`, `tests/test_retired_settings_interfaces.py`, `tests/test_review_regressions.py`, `tests/test_rewrite_persist_column.py`, `tests/test_route_validators.py`, `tests/test_run_focus.py`, `tests/test_run_order_report.py`, `tests/test_runtime_paths.py`, `tests/test_sanitize_multimodal_merge.py`, `tests/test_sanitize_preserves_reasoning.py`, `tests/test_scheduled_poll_race.py`, `tests/test_searxng_image_pinned.py`, `tests/test_searxng_settings_migration.py`, `tests/test_select_dropdown_theme_css.py`, `tests/test_sender_signature_skip_roles.py`, `tests/test_serve_html_with_nonce.py`, `tests/test_serve_profiles.py`, `tests/test_service_health_chromadb.py`, `tests/test_service_health_collect.py`, `tests/test_service_health_email.py`, `tests/test_service_health_ntfy.py`, `tests/test_service_health_providers.py`, `tests/test_service_health_search.py`, `tests/test_service_search_provider_guards.py`, `tests/test_services_research_low_quality_sources.py`, `tests/test_services_search_analytics_defaults.py`, `tests/test_set_admin.py`, `tests/test_settings_error_paths.py`, `tests/test_settings_scrub.py`, `tests/test_settings_shell_js_behavior.py`, `tests/test_settings_store_shape.py`, `tests/test_setup_admin_user.py`, `tests/test_setup_device_auth_static.py`, `tests/test_setup_llamacpp_hint_js.py`, `tests/test_shell_routes.py`, `tests/test_shell_service.py`, `tests/test_signature_fold_js.py`, `tests/test_signature_fold_self_closing_br_js.py`, `tests/test_signature_route_hardening.py`, `tests/test_signature_settings_dom_xss.py`, `tests/test_slash_autocomplete_static.py`, `tests/test_slash_setup_provider_aliases.py`, `tests/test_snap_other_layers_nonarray_js.py`, `tests/test_speech_service_toggles.py`, `tests/test_spinner_stops_when_never_attached_js.py`, `tests/test_split_chunks_no_duplicate_tail.py`, `tests/test_sqlite_foreign_keys.py`, `tests/test_src_search_query_nonstring.py`, `tests/test_startup_session_bootstrap_js.py`, `tests/test_startup_shell_js.py`, `tests/test_streaming_segmenter_js.py`, `tests/test_strip_reasoning_prose_dataloss.py`, `tests/test_strip_think.py`, `tests/test_svc_research_sources_nondict.py`, `tests/test_tailscale_discovery_cache.py`, `tests/test_taxonomy.py`, `tests/test_teacher_audit_owner_scope.py`, `tests/test_teacher_eval_nonstring_reply.py`, `tests/test_teacher_eval_tier2.py`, `tests/test_tidy_research_owner_scope.py`, `tests/test_tile_manager_snap_zones_js.py`, `tests/test_tls_overrides_scope.py`, `tests/test_toast_dismiss_pointer_events.py`, `tests/test_totp_failclosed.py`, `tests/test_truncate_message_count_regression.py`, `tests/test_ui_control_rag_toggle.py`, `tests/test_ui_visibility_js.py`, `tests/test_unknown_tool_calls.py`, `tests/test_update_database_script.py`, `tests/test_update_plan_tool.py`, `tests/test_url_safety.py`, `tests/test_user_time.py`, `tests/test_vcard_unfolding.py`, `tests/test_venice_hosts.py`, `tests/test_vision_model_detection.py`, `tests/test_vision_owner_scope.py`, `tests/test_visual_report.py`, `tests/test_visual_report_icon_url.py`, `tests/test_visual_report_nonstring.py`, `tests/test_visual_report_slug_unique.py`, `tests/test_visual_report_toc_code_fence.py`, `tests/test_warmup_ping_urls.py`, `tests/test_windows_update_script.py`, `tests/test_workspace_confine.py`, `tests/test_write_file_empty_body.py`.

This is the catch-all test section: the 322 paths that belong to no other `tests-*` section,
three of which are not Python at all. It asks of each one what the
sibling test sections ask of theirs — not whether it passes, but which edit to the production
code would make it fail. Two answers carry almost every finding below: the assertion is a
substring of a production source file rather than an observation of behaviour, and the fixture
replaces the code under test with something that cannot disagree with it.

The boundary: the harness itself (`tests/conftest.py`, `tests/helpers/*`, `tests/run_focus.py`,
`tests/run_order_report.py`, `tests/_taxonomy.py`, `tests/streaming/*`, `tests/cli/*`,
`tests/TESTING_STANDARD.md` and the other `tests/*.md` artifacts) belongs to `tests-harness`; it
is cited here only as the repository's own rulebook. The security, prompt-injection and
auth-guard group belongs to `tests-security`; the email/calendar, cookbook/models, LLM/tools,
session/chat/memory and documents/media groups belong to their own sections. The production code
these files pin belongs to the matching `src-*`, `routes-*`, `core-*`, `services-*` and
`static-js-*` sections, so where a weak test sits on top of a defect another section already
reports, this section names the test and cross-references the defect instead of restating it.

## Coverage

322 paths were assigned. Nothing here is a claim about the whole set: **47 files (4,108 lines)
were read end to end, 8 more were read in the regions a finding or a cross-check rests on, and
267 were not opened.** The sample was chosen by risk, in this order:

1. **Files whose name promises a security property** (`*_security`, `*_auth*`, `*_xss*`,
   `*_owner*`, `*_scope*`, `*_confinement*`, `*_ssrf*`, `*_allowlist*`, `*_gate*`, `*_hardening*`,
   `*_permissions*`, `*_redaction*`, `*_totp*`, `*_cors*`) — 42 files, rising to 68 once
   `*_token*`, `*_admin*`, `*_inject*`, `*_sanitiz*`, `*_path*` and `*_revoke*` are added. These
   are where a test that passes without exercising its guard costs the most, so most of them were
   at least scanned for the anti-patterns below.
2. **Files that pin a route this run already reported a defect in.** `tests/test_focused_test_guidance.py`
   (a `build-install-deploy` finding), `tests/test_blind_compare_redaction.py` (the `[CMP]` blind-mode
   contract that `static-js-compare` deliberately left to another section),
   `tests/test_url_safety.py` and `tests/test_generated_image_confinement.py` (both re-examined
   after the sections that own their production code had run them).
3. **The three non-pytest files** — `tests/bombadil-spec.ts`, `tests/live_thinking_scheduler.test.mjs`
   and `tests/markdown_codefence_placeholder_regression.mjs`.
4. **Mechanical sweeps over all 319 `.py` files** for the shapes that produce a passing test with
   no behaviour under it: `read_text()` plus substring assertions (78 files),
   `inspect.getsource` (1), `sys.modules[...] =` assignments (104 hits across 20 files, some at
   module scope and some inside fixtures), raw
   `os.environ[...] =` (2 files), assertions of the form `assert X is not None` (59 hits), and
   test files that import no project module at all (96 files, most of them Node wrappers that
   legitimately import nothing).

**Read fully (47):** `tests/bombadil-spec.ts` (107), `tests/markdown_codefence_placeholder_regression.mjs`
(69), `tests/test_active_email_reply_guard.py` (13), `tests/test_add_directory_event_loop.py` (394),
`tests/test_admin_wipe_routes_shim.py` (25), `tests/test_amd_gpu_check_args.py` (21),
`tests/test_api_chat_security.py` (404), `tests/test_api_key_file_permissions.py` (51),
`tests/test_api_token_tool_authority.py` (327), `tests/test_app.py` (98),
`tests/test_aux_llm_owner_scope.py` (72), `tests/test_blind_compare_redaction.py` (92),
`tests/test_builtin_mcp_pythonpath.py` (22), `tests/test_cerebras_cache_affinity.py` (27),
`tests/test_checkin_digest_owner_scope.py` (70), `tests/test_ci_authoritative_validation.py` (35),
`tests/test_claim_ownerless_json.py` (24), `tests/test_cleanup_owner_scope.py` (191),
`tests/test_cors_preflight.py` (30), `tests/test_direct_upload_limits.py` (61),
`tests/test_emoji_svg_hardening.py` (54), `tests/test_focused_test_guidance.py` (148),
`tests/test_generated_image_confinement.py` (72), `tests/test_group_chat_storage.py` (13),
`tests/test_live_thinking_scheduler_js.py` (29), `tests/test_manage_mcp_command_allowlist.py` (168),
`tests/test_manage_memory_list.py` (7), `tests/test_manage_notes_owner_gate.py` (120),
`tests/test_markdown_dom_xss_helpers.py` (38), `tests/test_migrate_faiss_to_chroma.py` (36),
`tests/test_odysseus_dispatcher.py` (13), `tests/test_owner_identity.py` (102),
`tests/test_retired_settings_interfaces.py` (119), `tests/test_searxng_image_pinned.py` (26),
`tests/test_setup_admin_user.py` (72), `tests/test_setup_device_auth_static.py` (42),
`tests/test_settings_error_paths.py` (94), `tests/test_signature_settings_dom_xss.py` (26),
`tests/test_taxonomy.py` (151), `tests/test_teacher_audit_owner_scope.py` (72),
`tests/test_tidy_research_owner_scope.py` (159), `tests/test_tls_overrides_scope.py` (149),
`tests/test_totp_failclosed.py` (21), `tests/test_update_database_script.py` (8),
`tests/test_url_safety.py` (117), `tests/test_vision_owner_scope.py` (101),
`tests/test_windows_update_script.py` (18).

**Read partially (8):** `tests/test_truncate_message_count_regression.py` (`:1-40` of 78, the
fixture the finding rests on), `tests/live_thinking_scheduler.test.mjs` (`:1-60` of 277, enough to
see that it drives the real module), `tests/test_history_topics_owner_scope.py` (`:140-280` of 280;
the first half was skimmed for its fixtures), `tests/test_compare_endpoint_owner_scope.py`
(`:1-50` of 104, the query stub), `tests/test_rename_user_owner_sync.py` (the 22 `read_text()`
call sites and their assertions, of 752), `tests/test_api_token_user_route_gate.py` (`:1-27` of 62),
`tests/test_builtin_mcp_npx_cache.py` (`:1-76` of 185),
`tests/test_docker_devops_hardening.py` (`:240-255` of 255, the `TEST_DOCS` venv guard).

**Not read (267).** The shape of what was skipped. **Sixteen of them are over 400 lines** and
were grepped for the anti-patterns above and otherwise left alone, because evaluating them
properly needs fixture work this section's budget did not cover:
`tests/test_foreground_model_routing.py` (3,649), `tests/test_external_context_tool_gate.py`
(1,473), `tests/test_review_regressions.py` (1,449),
`tests/test_pr6020_browser_review_regressions.py` (933), `tests/test_api_token_routes.py` (578),
`tests/test_history_display_model_hydration.py` (549), `tests/test_shell_routes.py` (538),
`tests/test_workspace_confine.py` (533), `tests/test_markdown_lazy_lib_loading_js.py` (510),
`tests/test_run_focus.py` (492), `tests/test_companion_readonly.py` (484),
`tests/test_kv_cache_invalidation_2927.py` (463), `tests/test_compare_stop_disconnect_poll.py`
(463), `tests/test_companion_pairing.py` (448), `tests/test_helpers_import_state.py` (426) and
`tests/test_teacher_eval_tier2.py` (406). A few of those are named in the section's own boundary
as another section's subject (`test_run_focus.py`, `test_helpers_import_state.py` to
`tests-harness`; `test_compare_stop_disconnect_poll.py` to `static-js-compare`) and are listed
here only because the mechanical sweeps still ran over them.

**The other 251 unread files are all under 400 lines**, and most are under 100. 50 of them match
`*_nonstring.py`, `*_js.py` or `*_shim.py` — the small pins that assert one helper's behaviour —
and the rest are provider-discovery, migration and CLI-wrapper modules. They were not opened at
all; the sweeps above are the only evidence about them. Nothing in this section claims to have
found every weak test in its slice; it claims the nine findings below are real, each verified
against `2992bf6d368a`.

**Checks run.** The whole slice in one process, then the per-file probes quoted in the findings:

```
$ venv/bin/python -m pytest -q $(python3 - <<'EOF'
import re; t=open('audit/2026-10-03T2340/run.toml').read()
m=re.search(r'stem = "tests-rest".*?paths = \[(.*?)\]\n', t, re.S)
print(' '.join(p for p in re.findall(r'"([^"]+)"', m.group(1)) if p.endswith('.py')))
EOF
)                                            # the 319 .py paths of this section
2412 passed, 2 skipped, 27 warnings in 57.47s
```

The two skips are environmental, not coverage the section chose to drop:
`tests/test_docker_devops_hardening.py:149` (`Docker test image is unavailable:
odysseus-odysseus:latest`) and `tests/test_markitdown_runtime.py:64` (`could not import
'markitdown': No module named 'markitdown'`). **Zero failures, zero xfail** — every finding below
is about a test that passes.

`node v24.16.0` is on PATH here, so no JS wrapper skipped. The probes live under `/tmp/audit-probe/`
and are not part of the target tree. Three of them matter enough to name: `block_modules.py` (a
pytest plugin whose `find_spec` raises `ModuleNotFoundError` for a `BLOCK_MODULES` list, plus
`control_blocked.py`, which fails unless the block actually took effect), `mutate_read_text.py`
(a plugin that serves mutated production text to `pathlib.Path.read_text`, so a source-grep test
can be run against a behaviourally-changed tree), and `probe_db_state.py` (reports the process's
`DATABASE_URL` and engine URL). Running the suite left the tracked tree untouched: `git status
--porcelain` shows only `audit/`, and `sha256sum` of `data/auth.json` and `data/features.json` is
unchanged. `data/app.db` is not a counterexample to that — `data/` is gitignored
(`.gitignore:28`), and that file's hash did change, at 20:57 JST, after this section's last
measured run and while the sibling sections' suites were running in the same working tree. Any
pytest process here can rewrite it, which is the point of the finding below about
`tests/test_truncate_message_count_regression.py`.

### [BUG] The blind-mode naming scan passes with the blind guard inverted

- **Location:** `tests/test_blind_compare_redaction.py:76` (the scan is `:83-92`; the guarded lines are `static/js/compare/index.js:250`, `static/js/compare/panes.js:386`, `static/js/compare/panes.js:589`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the test's docstring says it pins that "a blind comparison is never named after
  its real model", and it decides that by scanning each line for two substrings:

  ```python
  # tests/test_blind_compare_redaction.py:83-88
  for path in sorted(compare_dir.glob("*.js")):
      for lineno, line in enumerate(
          path.read_text(encoding="utf-8").splitlines(), 1
      ):
          if "'[CMP] '" in line and "_blindMode" not in line:
              offenders.append(f"{path.name}:{lineno}: {line.strip()}")
  ```

  The real lines read `'[CMP] ' + (state._blindMode ? 'Model ' + _slotChar(i) : modelShorts[i])`.
  Swapping the two branches of that ternary keeps both substrings on the line, so the guard can
  point at the model name in blind mode and the scan still reports no offenders. Measured with
  `/tmp/audit-probe/mutate_read_text.py` serving the inverted text to the *real* test:

  ```
  $ venv/bin/python -m pytest -q tests/test_blind_compare_redaction.py
  5 passed, 1 warning in 0.08s

  $ PYTHONPATH=/tmp/audit-probe MUTATIONS=/tmp/audit-probe/mut_blind.json \
      venv/bin/python -m pytest -q -p mutate_read_text tests/test_blind_compare_redaction.py
  5 passed, 1 warning in 0.08s
  ```

  The mutation was confirmed to be what the test read, not a no-op:

  ```
  static/js/compare/index.js:250: fd.append('name', '[CMP] ' + (state._blindMode ? modelShorts[i] : 'Model ' + _slotChar(i)));
  static/js/compare/panes.js:386: fd.append('name', '[CMP] ' + (state._blindMode ? m.name : 'Model ' + _slotChar(i)));
  static/js/compare/panes.js:589: fd.append('name', '[CMP] ' + (state._blindMode ? 'Model ' + _slotChar(paneIdx) : m.name));
  ```

  (Two of the three naming lines were inverted; the third was left alone to show that the scan is
  line-local and per-line.) `tests/TESTING_STANDARD.md:118-123` names this exact pattern — a
  source-text assertion "can pass even when behavior regresses, because the asserted string still
  appears somewhere" — and permits it only where the invariant cannot be driven at runtime
  (`:128-132`). Here it can be: the helper session's name is built in a click handler that can be
  reached through the existing Node harness, or the three call sites can be extracted into one
  naming function that a test calls with `_blindMode` true and false.
- **Impact:** the de-anonymization the test exists to prevent — a blind comparison whose helper
  session is named after the real model, which is what `GET /api/sessions` and the sidebar then
  show — can be reintroduced by any edit that keeps the two strings on the same line. The four
  backend tests (`:46-71`) call `SR._public_model` and compare a real constant, and they do hold;
  only the frontend half is a text scan. `static-js-compare.md:23` explicitly leaves the `[CMP]` naming
  contract to the session section, and no section reports this.
- **Fix:** assert the produced name, not the source. Extract the three `'[CMP] ' + (...)` expressions
  into one function in `static/js/compare/` and drive it twice from a Node test (or the existing
  `test_compare_js.py` harness) with `_blindMode` true and false, asserting the slot label and the
  model name respectively. If the scan stays, also assert that no line contains a model-name
  variable inside the `_blindMode` branch.

### [BUG] `test_aux_llm_owner_scope.py` never imports the code it names, and one assertion is satisfied by an unrelated line

- **Location:** `tests/test_aux_llm_owner_scope.py:28` (with `:11`, `:18`, `:37`, `:43`, `:56`)
- **Severity:** medium
- **Disposition:** next
- **Evidence:** the whole file is `from pathlib import Path` plus six `read_text()` scans of
  production sources; it imports no project module at all. Making every module it names
  unimportable changes nothing:

  ```
  $ PYTHONPATH=/tmp/audit-probe \
      BLOCK_MODULES=routes.session_routes,routes.task.task_routes,routes.chat_helpers,\
  src.context_compactor,src.session_actions,src.task_scheduler,routes.research.research_routes \
      venv/bin/python -m pytest -q -s -p block_modules \
      tests/test_aux_llm_owner_scope.py /tmp/audit-probe/control_blocked.py
  ......CONTROL blocked routes.session_routes: blocked by audit probe: routes.session_routes
  CONTROL blocked routes.task.task_routes: blocked by audit probe: routes.task.task_routes
  CONTROL blocked routes.chat_helpers: blocked by audit probe: routes.chat_helpers
  CONTROL blocked src.context_compactor: blocked by audit probe: src.context_compactor
  CONTROL blocked src.session_actions: blocked by audit probe: src.session_actions
  CONTROL blocked src.task_scheduler: blocked by audit probe: src.task_scheduler
  CONTROL blocked routes.research.research_routes: blocked by audit probe: routes.research.research_routes
  7 passed, 2 warnings in 0.33s
  ```

  The control is not decorative — the same plugin does stop a file that really imports its
  subject (`PYTHONPATH=/tmp/audit-probe BLOCK_MODULES=src.url_safety pytest -q -p block_modules
  tests/test_url_safety.py` → `Interrupted: 1 error during collection !!!`, `ModuleNotFoundError:
  blocked by audit probe: src.url_safety`). The scan is not even a faithful stand-in for the
  behaviour: `test_auto_compaction_utility_endpoint_keeps_chat_owner` asserts
  `assert "owner=user" in helper_src` (`:32`), and `routes/chat_helpers.py` contains that
  substring twice — at `:729`, a `_preface_kwargs` dict entry for the message preface, and at
  `:795`, the `maybe_compact(...)` call the test is named for. Changing the `:795` argument to
  `owner=None` leaves the file green:

  ```
  $ PYTHONPATH=/tmp/audit-probe MUTATIONS=/tmp/audit-probe/mut1.json \
      venv/bin/python -m pytest -q -p mutate_read_text tests/test_aux_llm_owner_scope.py
  6 passed, 1 warning in 0.07s
  ```

  The same file shows the cost of a duplicated needle: `:47` and `:49` both assert
  `"owner=task.owner or None" in src`, and `src/task_scheduler.py` has three such call sites, so
  dropping the owner from one of them is invisible —

  ```
  $ PYTHONPATH=/tmp/audit-probe MUTATIONS=/tmp/audit-probe/mut3.json \
      venv/bin/python -m pytest -q -p mutate_read_text \
      "tests/test_aux_llm_owner_scope.py::test_scheduler_fallbacks_and_research_headers_are_owner_scoped"
  1 passed, 1 warning in 0.07s
  ```

  (mutation: `src/task_scheduler.py:1914` only, of the three occurrences at `:1914`, `:2003`,
  `:2036`). `tests/TESTING_STANDARD.md:128-132` allows a source assertion only where the invariant
  cannot be driven at runtime, and asks the docstring to say why; no test in this file says why.
- **Impact:** six tests that read as coverage for owner-scoped endpoint resolution — the mechanism
  that keeps one tenant's utility/teacher/research call from spending another tenant's endpoint
  and API key — pin only that certain strings exist somewhere in four large files. The
  auto-compaction path is the one that matters most, because `resolve_endpoint("utility",
  owner=owner)` at `src/context_compactor.py:379` is the last owner-carrying hop: break the
  argument at `routes/chat_helpers.py:795` and the compaction runs against a null-owner endpoint
  with no test failing. The owner-scope behaviour these files describe is exercised properly
  elsewhere in this section — `tests/test_vision_owner_scope.py:10-84`,
  `tests/test_tidy_research_owner_scope.py:62-158` and `tests/test_teacher_audit_owner_scope.py:15-71`
  all observe the owner that reaches the resolver — so the fix is to bring this file up to their
  standard rather than to invent a new harness.
- **Fix:** delete the `read_text()` scans and drive the real call. For the compaction case, the
  cheapest honest pin is a test that calls `maybe_compact(...)` with `owner="alice"` and a
  monkeypatched `resolve_endpoint` that records the `owner` keyword — the same shape
  `tests/test_vision_owner_scope.py:47-84` already uses for the vision path.

### [BUG] `test_focused_test_guidance.py` freezes the wrong interpreter as the expected output, contradicting the repository's own rule and its own guard

- **Location:** `tests/test_focused_test_guidance.py:58` (with `:83`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** two tests assert that the CI helper's suggested command contains `python3`:

  ```python
  # tests/test_focused_test_guidance.py:54-58
  def test_format_report_builds_command_for_changed_python_test():
      report = guidance.format_report(["tests/test_beta.py"])
      assert "- `tests/test_beta.py`" in report
      assert "python3 -m pytest -q tests/test_beta.py" in report
  ```

  and again at `:83` for a path with spaces. That string is produced by
  `.github/scripts/focused_test_guidance.py:71` (`command = ["python3", "-m", "pytest", "-q", *paths]`),
  which `build-install-deploy.md:629-660` already reports as the wrong interpreter.
  `tests/TESTING_STANDARD.md:27` says "Run tests with the project virtualenv interpreter
  (`./venv/bin/python -m pytest`)", and the repository's own guard forbids exactly the string this
  test requires:

  ```
  $ sed -n '244,251p' tests/test_docker_devops_hardening.py
  def test_testing_docs_use_project_venv_for_python_validation():
      stale_patterns = [
          "python3 -m pytest",
          ...
  ```

  So the two guards point in opposite directions: `tests/test_docker_devops_hardening.py:255`
  fails if `python3 -m pytest` appears in `tests/README.md`, `tests/TESTING_STANDARD.md` or
  `tests/LAYOUT_INVENTORY.md`, while `tests/test_focused_test_guidance.py:58` fails if it stops
  appearing in the generated report.
- **Impact:** the guidance CI prints to contributors is the one command in the repository that is
  generated for a human to copy, and this test makes the fix to it a red build. A maintainer who
  follows the `build-install-deploy` recommendation and changes
  `.github/scripts/focused_test_guidance.py:71` to `./venv/bin/python` must edit this test in the
  same change or watch it fail — the same shape as the fail-open pin in `tests-security.md`'s
  `test_require_privilege_still_blocks_disallowed`, where a test encodes the defect as the
  contract.
- **Fix:** change `:58` and `:83` to assert `"./venv/bin/python -m pytest -q ..."` and fix
  `.github/scripts/focused_test_guidance.py:71` in the same change, so the test and the rule agree.

### [BUG] Four source-text "pins" pass with the code they name made unimportable

- **Location:** `tests/test_manage_memory_list.py:4` (with `tests/test_active_email_reply_guard.py:4`, `tests/test_direct_upload_limits.py:38`, `tests/test_generated_image_confinement.py:67`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** each of these tests reads a production file and asserts a substring, and each
  survives having the module it names made unimportable. Measured with the same
  `find_spec`-raising plugin and the same control as the finding above:

  ```
  $ PYTHONPATH=/tmp/audit-probe BLOCK_MODULES=src.ai_interaction,mcp_servers.memory_server \
      venv/bin/python -m pytest -q -s -p block_modules \
      tests/test_manage_memory_list.py /tmp/audit-probe/control_blocked.py
  .CONTROL blocked src.ai_interaction: blocked by audit probe: src.ai_interaction
  CONTROL blocked mcp_servers.memory_server: blocked by audit probe: mcp_servers.memory_server
  2 passed, 2 warnings in 0.33s

  $ PYTHONPATH=/tmp/audit-probe BLOCK_MODULES=routes.chat_routes \
      venv/bin/python -m pytest -q -s -p block_modules \
      tests/test_active_email_reply_guard.py /tmp/audit-probe/control_blocked.py
  .CONTROL blocked routes.chat_routes: blocked by audit probe: routes.chat_routes
  2 passed, 2 warnings in 0.33s

  $ PYTHONPATH=/tmp/audit-probe BLOCK_MODULES=routes.stt_routes,routes.gallery.gallery_routes,\
  routes.memory.memory_routes,routes.calendar_routes,routes.email_routes \
      venv/bin/python -m pytest -q -s -p block_modules \
      tests/test_direct_upload_limits.py /tmp/audit-probe/control_blocked.py
  ....CONTROL blocked routes.stt_routes: blocked by audit probe: routes.stt_routes
  CONTROL blocked routes.gallery.gallery_routes: blocked by audit probe: routes.gallery.gallery_routes
  CONTROL blocked routes.memory.memory_routes: blocked by audit probe: routes.memory.memory_routes
  CONTROL blocked routes.calendar_routes: blocked by audit probe: routes.calendar_routes
  CONTROL blocked routes.email_routes: blocked by audit probe: routes.email_routes
  5 passed, 2 warnings in 0.34s

  $ PYTHONPATH=/tmp/audit-probe BLOCK_MODULES=src.generated_images \
      venv/bin/python -m pytest -q -p block_modules tests/test_generated_image_confinement.py
  8 failed, 1 passed, 1 warning in 0.11s
  ```

  In the last case the single survivor is `test_generated_image_route_uses_confining_resolver`
  (`:67-72`), which is exactly the file's one `read_text()` test; the eight behavioural tests in
  the same file fail, which is the proof that the block reached the module they exercise. Each of
  the four tests is weaker than its name:

  - `tests/test_manage_memory_list.py:4` asserts `assert "memories[:100]" not in source` against
    `Path("mcp_servers/memory_server.py")` and `Path("src/ai_interaction.py")`. The name says
    "implementations do not truncate results"; the assertion forbids one spelling of one truncation
    (`memories[:100]`) and passes for `memories[:200]`, `memories[:limit]`, `islice`, or a
    `LIMIT 100` in the query. It is also cwd-relative, so it errors rather than fails when pytest
    is invoked from another directory.
  - `tests/test_active_email_reply_guard.py:4-13` slices `routes/chat_routes.py` between two marker
    strings and asserts five tool-name literals appear inside. Nothing calls the guard, so a change
    that keeps the list but stops consulting it — or consults it after the tool has run — passes.
    The behaviour is reachable: `routes/chat_routes.py` is importable and the guard runs on the
    chat request path.
  - `tests/test_direct_upload_limits.py:38-61` asserts six call-site strings exist across five
    route files. The three behavioural tests above it (`:20-35`) do cover `read_upload_limited` itself, so
    the gap is only the wiring: nothing proves a route passes the result of the bounded read to the
    parser rather than reading the upload a second time.
  - `tests/test_generated_image_confinement.py:67-72` reads `Path("app.py")` — also cwd-relative —
    and asserts three substrings, one of them negative. Its siblings at `:13-54` already prove the
    resolver confines traversal and symlink escapes, so this test adds no behaviour, only a text
    check that would also pass if the route called the resolver and then ignored its result.

  `tests/TESTING_STANDARD.md:128-132` permits a source-text assertion only when the invariant
  cannot be exercised at runtime and the docstring says so; none of these four docstrings does.
- **Impact:** four claimed regression pins cannot detect the regression they describe, and each is
  counted as coverage in the pytest job. The `manage_memory` one is the sharpest: the truncation it
  guards against is a silent data-loss shape (a user's memory list cut to 100 entries), and the
  assertion cannot see a re-introduction at any other limit.
- **Fix:** for `manage_memory`, call the memory-list implementation against a store with 150 entries
  and assert 150 come back. For the reply guard, import the guard and assert it refuses
  `reply_to_email` while an active-email context is set. For the upload limits, drive one route with
  an oversized body and assert 413. For the image route, delete the test — the resolver tests above
  it are the real pin — or drive the route with a traversal token.

### [FOOTGUN] `test_truncate_message_count_regression.py` leaves the process's database pointed at a temp file

- **Location:** `tests/test_truncate_message_count_regression.py:16` (with `:19`, `:24`, `:28`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the helper rebinds two core modules and the environment, and nothing undoes it:

  ```python
  # tests/test_truncate_message_count_regression.py:16-29
  def _make_manager():
      db_fd, db_path = tempfile.mkstemp(suffix=".db")
      os.close(db_fd)
      os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

      # Import after DATABASE_URL is set so the engine binds to the temp DB.
      import importlib
      import core.database as database
      importlib.reload(database)
      database.Base.metadata.create_all(bind=database.engine)

      import core.session_manager as sm_mod
      importlib.reload(sm_mod)
      return sm_mod.SessionManager(), database, sm_mod
  ```

  `_make_manager()` runs once per test, so the last run's temp file is what the process keeps.
  Measured with `/tmp/audit-probe/probe_db_state.py`:

  ```
  $ venv/bin/python -m pytest -q -s /tmp/audit-probe/probe_db_state.py
  PROBE env DATABASE_URL      : None
  PROBE core.database engine  : sqlite:////home/lhl/github/lhl/odysseus/data/app.db
  PROBE session_manager bind  : Engine(sqlite:////home/lhl/github/lhl/odysseus/data/app.db)

  $ venv/bin/python -m pytest -q -s tests/test_truncate_message_count_regression.py \
      /tmp/audit-probe/probe_db_state.py
  ..PROBE env DATABASE_URL      : sqlite:////tmp/tmp8gul2c31.db
  PROBE core.database engine  : sqlite:////tmp/tmp8gul2c31.db
  PROBE session_manager bind  : Engine(sqlite:////tmp/tmp8gul2c31.db)
  ```

  `tests/TESTING_STANDARD.md:102-106` says to use `monkeypatch.setenv`/`delenv` "never raw
  `os.environ[...] = ...` that outlives the test", and the same bullet says a test that needs a
  file-backed DB must opt in through `tests.helpers.sqlite_db.make_temp_sqlite` and bind
  `SessionLocal` on the module under test. This file does neither, and `importlib.reload` is a
  harder version of the same leak: it changes the module object in place, so every later
  `from core.session_manager import SessionManager` sees the temp bind. The files in this slice
  that read `DATABASE_URL` after it (`tests/test_webhook_dns_rebinding_pin.py:24`,
  `tests/test_webhook_sanitize_error_ipv6.py:20`, `tests/test_webhook_ssrf_resilience.py:23`)
  each re-pin it with `patch.dict`, so `pytest -q tests/test_truncate_message_count_regression.py
  tests/test_webhook_*.py` gives `18 passed` — and their `patch.dict` restore puts the leaked
  value back rather than `None`. The four other readers in this slice use
  `os.environ.setdefault` at module scope (`tests/test_add_directory_event_loop.py:18`,
  `tests/test_code_nav_tools.py:8`, `tests/test_history_order_by_timestamp_regression.py:20`,
  `tests/test_settings_error_paths.py:17`), which cannot take effect once the key exists. That is
  measurable with a two-test file that does the same `setdefault`:

  ```
  $ venv/bin/python -m pytest -q -s /tmp/audit-probe/probe_setdefault.py
  PROBE before      : None
  PROBE after setdefault: sqlite:////tmp/test_code_nav.db

  $ venv/bin/python -m pytest -q -s tests/test_truncate_message_count_regression.py \
      /tmp/audit-probe/probe_setdefault.py
  3 passed, 10 warnings in 0.56s
  PROBE before      : sqlite:////tmp/tmpzue2aqlw.db
  PROBE after setdefault: sqlite:////tmp/tmpzue2aqlw.db
  ```

  Nothing fails today because the four `setdefault` files sort before this one alphabetically, so
  a full-suite run never reaches them with the leak in place; only a focused run in the other
  order does. The `mkstemp` files are never unlinked either, so each run leaves two files in
  `/tmp`.
- **Impact:** any test added after this file that opens a session without re-pinning the URL
  silently writes to a stale temp database instead of the one it thinks it uses, and the failure
  mode is a pass, not an error. A focused run that puts this file first also silently disarms the
  `setdefault` isolation of four other files in this section, which is how a targeted run and a
  full-suite run can disagree.
- **Fix:** build the manager the way `tests/helpers/sqlite_db.py` already does — `make_temp_sqlite`
  for the engine and `monkeypatch.setattr(core.session_manager, "SessionLocal", sessionmaker)` for
  the bind — and drop the `importlib.reload` and the raw `os.environ` write. If a reload is
  genuinely needed, wrap it in `tests.helpers.import_state.preserve_import_state`.

### [DEAD-CODE] `tests/markdown_codefence_placeholder_regression.mjs` is run by nothing, and its assertions rest on three hand-written copies of real modules

- **Location:** `tests/markdown_codefence_placeholder_regression.mjs:11` (with `:15`, `:19`, `:53-69`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the file is a bare Node script — no test framework, one `console.log('ok')` at the
  end — and no file in the repository references it:

  ```
  $ grep -rn "codefence_placeholder" . --exclude-dir=node_modules --exclude-dir=audit
  (no output)
  $ grep -c "scripts" package.json
  0
  ```

  `package.json` declares `@antithesishq/bombadil` and nothing else — no `scripts` block — and the
  only CI job that touches JavaScript is `node-syntax` (`.github/workflows/ci.yml:96-101`), which
  runs `node --check` over `static/app.js` and `static/js/**/*.js` only. `pytest` does not collect
  it: `python -m pytest -q --collect-only tests/` lists no match for the filename. The single
  execution on record is a manual `node tests/markdown_codefence_placeholder_regression.mjs` →
  `ok` in `static-js-rest.md:97`. To run at all, the script rewrites `static/js/markdown.js` on the
  way into a `vm` context, replacing three sibling imports with inline copies:

  ```javascript
  // tests/markdown_codefence_placeholder_regression.mjs:11-22
  src = src.replace(
    /import uiModule from '\.\/ui\.js';/,
    'const uiModule = { esc: (s) => String(s).replace(...) };'
  );
  src = src.replace(
    /import \{ splitTableRow \} from '\.\/markdown\/tableRow\.js';/,
    'const splitTableRow = (row) => row.split("|").filter((cell) => cell.trim() !== "");'
  );
  ```

  The `splitTableRow` stand-in is not the real one: `static/js/markdown/tableRow.js:13` guards its
  input (`const text = typeof row === 'string' ? row : '';`), and the replacement would throw on a
  non-string. This is the same shape `tests-harness.md:318-357` reports for
  `tests/streaming/markdownHarness.mjs`, in a different file that no runner reaches.
- **Impact:** a regression pin with no runner cannot fail. If the code-fence placeholder contract
  it checks (no `___ALLOWED_HTML_` sentinel leaking into the rendered HTML for a fenced `html`
  block) breaks, nothing reports it, and a reader who finds the filename in `ls tests` will assume
  CI covers it. The three inlined copies also mean the two assertions at `:66-67` are made against
  a renderer assembled from stubs, so even when run by hand the result is not evidence about the
  browser's renderer.
- **Fix:** either delete it and rely on `tests/test_markdown_rendering_js.py`, or convert it to a
  `node:test` file driven by a pytest wrapper the way `tests/test_live_thinking_scheduler_js.py:20`
  drives its `.mjs`, and load the real sibling modules instead of the inline copies.

### [HARDCODE] `tests/bombadil-spec.ts` carries a plaintext login password, in a spec no runner executes and the repository's own secret scan does not flag

- **Location:** `tests/bombadil-spec.ts:69` (the login action is `:62-72`; the username literal is `:67`)
- **Severity:** low
- **Disposition:** next
- **Evidence:** the Bombadil action list types a fixed username and a fixed password into the login
  form, and the password is a literal in the committed source. **The value is deliberately not
  reproduced here** — the run's secret gate extracts secret-shaped values from the tree at HEAD,
  so quoting it would put it in an audit artifact. What was measured is that the repository's own
  scanner does not consider it one:

  ```
  $ gitleaks version
  8.30.1
  $ gitleaks dir --no-banner --redact tests/bombadil-spec.ts
  8:52PM INF scanned ~3846 bytes (3.85 KB) in 2.92ms
  8:52PM INF no leaks found
  ```

  8.30.1 is the exact version `.github/workflows/secret-scan.yml:50` pins, and the repository ships
  no `.gitleaks.toml`, so the default rule set is what the `gitleaks` job runs. (For completeness:
  `gitleaks dir tests/` does report two `generic-api-key` hits, both in
  `tests/__pycache__/*.pyc` bytecode rather than in any tracked source file.) Nothing runs the
  spec: `package.json` has no `scripts` block, no CI job installs `@antithesishq/bombadil` or runs
  `npm ci`, and the only references to the file in the tree are prose —
  `specs/frontend.md:19`, `specs/testing-devops.md:9` and `:54`, where it is described as
  requiring "npm-installed Bombadil dev dependencies and a running/browser-capable UI workflow
  when used". `static-js-compare.md:109` already records that it is "not run".
- **Impact:** two distinct costs, both small. First, a password-shaped string now lives in the
  repository's history and its own scanner will not catch it, so the credential-shaped-material
  policy in `.github/workflows/secret-scan.yml:1-7` is not actually enforced for it — if the value
  is one a maintainer also uses elsewhere, it is disclosed. Second, if anyone does run the spec
  against a live instance, the login action attempts `tester` with that password, which will fail
  against a real deployment and looks like a product bug rather than a stale fixture.
- **Fix:** replace the literal with a value read from the environment (for example
  `process.env.BOMBADIL_TEST_PASSWORD`), or delete the file together with the `devDependencies`
  entry it is the only consumer of. Either way, rotate the string if it is anything other than a
  throwaway.

### [FOOTGUN] `test_settings_error_paths.py` sets an environment variable no code reads

- **Location:** `tests/test_settings_error_paths.py:16` (with `:15`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** the module's isolation block sets two variables at import time:

  ```python
  # tests/test_settings_error_paths.py:15-17
  _TMP = Path(tempfile.mkdtemp(prefix="odysseus-settings-test-"))
  os.environ.setdefault("DATA_DIR", str(_TMP))
  os.environ.setdefault("DATABASE_URL", f"sqlite:///{_TMP / 'app.db'}")
  ```

  `DATA_DIR` is not the name the application reads. The canonical variable is `ODYSSEUS_DATA_DIR`,
  read in exactly one place:

  ```
  $ sed -n '12p;16p' src/constants.py
  DATA_DIR = os.getenv("ODYSSEUS_DATA_DIR", get_default_data_dir())
  # Single source of truth: every persisted file/dir lives under DATA_DIR, which
  # is the ONLY place ODYSSEUS_DATA_DIR is read.
  $ grep -rn "os.environ.get(\"DATA_DIR\"\|os.getenv(\"DATA_DIR\"" src/ core/ routes/ app.py
  routes/cookbook_helpers.py:97:    path = Path(state_path) if state_path else Path(os.environ.get("DATA_DIR", "data")) / "cookbook_state.json"
  ```

  So the `setdefault` at `:16` isolates nothing for `src/settings.py`, and its only effect in the
  process is to redirect `routes/cookbook_helpers.py:97`'s state path into a temp directory for
  every later test in the same pytest process. The `setdefault` at `:17` is a no-op under the test
  suite, because `tests/conftest.py:18` has already set `DATABASE_URL` to `sqlite:///:memory:`.
- **Impact:** the file reads as though it isolates the data directory, and a maintainer extending
  it — or copying the block into a new test — will believe the isolation exists. It also leaks a
  path change for the cookbook state store to unrelated later tests. The file's own tests are
  unaffected, because they pass `tmp_path` and patch `src.settings.SETTINGS_FILE` explicitly
  (`:24-40`), so nothing here is currently failing.
- **Fix:** drop the `DATA_DIR` line, or change it to `ODYSSEUS_DATA_DIR` if the intent is to
  isolate a real data directory; and drop the `DATABASE_URL` line since `tests/conftest.py`
  already provides an in-memory default. A test that needs a file-backed DB should use
  `tests.helpers.sqlite_db.make_temp_sqlite` as `tests/TESTING_STANDARD.md:102-106` requires.

### [BUG] `test_app.py`'s "structure" tests assert that files exist, not that anything works

- **Location:** `tests/test_app.py:18` (with `:23`, `:28`, `:33`, `:46`, `:82`, `:88`, `:94`)
- **Severity:** low
- **Disposition:** backlog
- **Evidence:** eight of the file's twelve tests are `os.path.exists` checks on tracked files:

  ```python
  # tests/test_app.py:15-18
  def test_app_file_exists(self):
      """Test that app.py exists"""
      app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.py")
      assert os.path.exists(app_path), "app.py should exist"
  ```

  The same shape covers `static/`, `routes/`, `src/`, `.env.example` and three route modules
  (`:82`, `:88`, `:94` — including `routes/memory_routes.py`, an 803-byte compatibility shim). The
  other four are one `.gitignore` check (`:35-41`) and three import smoke tests whose assertions
  are `BASE_DIR is not None` (`:55`), `STATIC_DIR is not None` (`:56`), `callable(abs_join)`
  (`:61`) and `issubclass(SessionNotFoundError, Exception)` (`:72`). Nothing in the file exercises
  a route, a handler or a helper's behaviour, and the file predates the repository's own standard:
  the only real invariant it states is `:41`, that `.env` is in `.gitignore`.
- **Impact:** the file contributes twelve passing tests to the pytest job and a name
  (`test_app.py`) that reads like application coverage. Its existence checks cannot fail for any
  change that keeps the paths — which every change does — and the import smoke tests fail only on
  an `ImportError`, which collection of any other test in the suite already catches. A reader
  grepping for `app.py` coverage finds this and stops.
- **Fix:** replace the existence checks with the cheapest behavioural assertion that would catch a
  real break — for example importing `app` and asserting the route table contains a known path, and
  calling `abs_join` with a traversal-shaped argument and asserting the result stays under
  `BASE_DIR`. `tests/test_auth_root_path.py:119-283` and `tests/test_cors_preflight.py:18-30` show
  both shapes already in use in this suite.
