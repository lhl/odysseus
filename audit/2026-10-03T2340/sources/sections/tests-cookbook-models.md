# tests: cookbook, models and providers

## Overview

`tests/test_cookbook_agent_tool_ssh_validation.py`, `tests/test_cookbook_cpu_only_serve.py`, `tests/test_cookbook_dead_download_status.py`, `tests/test_cookbook_dependency_completion_regression.py`, `tests/test_cookbook_deps_recipes.py`, `tests/test_cookbook_diagnosis.py`, `tests/test_cookbook_diagnosis_js.py`, `tests/test_cookbook_docker_access.py`, `tests/test_cookbook_download_toast_duration.py`, `tests/test_cookbook_endpoint_registration.py`, `tests/test_cookbook_error_feedback.py`, `tests/test_cookbook_error_tail_lines.py`, `tests/test_cookbook_gemma4_thinking_template.py`, `tests/test_cookbook_helpers.py`, `tests/test_cookbook_hf_token.py`, `tests/test_cookbook_local_serve_pid_winpid.py`, `tests/test_cookbook_package_detection.py`, `tests/test_cookbook_port_parsing_js.py`, `tests/test_cookbook_progress_signal_js.py`, `tests/test_cookbook_remote_windows_diffusers.py`, `tests/test_cookbook_same_host_server_profiles_js.py`, `tests/test_cookbook_serve_lifecycle.py`, `tests/test_cookbook_windows_stop_tree_js.py`, `tests/test_embedding_cache_confinement.py`, `tests/test_embedding_endpoint_config.py`, `tests/test_embedding_lane_ndarray_restore.py`, `tests/test_embedding_lanes.py`, `tests/test_embedding_lanes_legacy.py`, `tests/test_embedding_lanes_memory.py`, `tests/test_embedding_lanes_rag.py`, `tests/test_embedding_lanes_tool_index.py`, `tests/test_embeddings.py`, `tests/test_embeddings_client.py`, `tests/test_endpoint_owner_scope_followup.py`, `tests/test_endpoint_probing.py`, `tests/test_endpoint_resolver_headers.py`, `tests/test_endpoint_resolver_models.py`, `tests/test_endpoint_resolver_urls.py`, `tests/test_gpu_compose_standalone.py`, `tests/test_hwfit_amd.py`, `tests/test_hwfit_apple_bandwidth.py`, `tests/test_hwfit_bandwidth_nonstring.py`, `tests/test_hwfit_container_visibility_warning.py`, `tests/test_hwfit_cpu_arch_detection.py`, `tests/test_hwfit_cpu_only_fallback.py`, `tests/test_hwfit_gemma4_12b.py`, `tests/test_hwfit_gpu_count_nonnumeric.py`, `tests/test_hwfit_macos.py`, `tests/test_hwfit_manual_backend.py`, `tests/test_hwfit_models_nonstring_fields.py`, `tests/test_hwfit_native_quant_labels.py`, `tests/test_hwfit_params_b_malformed.py`, `tests/test_hwfit_quant_formats.py`, `tests/test_hwfit_remote_validation.py`, `tests/test_hwfit_unified_nvidia.py`, `tests/test_hwfit_windows.py`, `tests/test_llm_core_anthropic_cache.py`, `tests/test_llm_core_anthropic_temp_clamp.py`, `tests/test_llm_core_anthropic_temp_omit.py`, `tests/test_llm_core_async_mistral_content.py`, `tests/test_llm_core_concurrency.py`, `tests/test_llm_core_connect_timeout.py`, `tests/test_llm_core_fallback.py`, `tests/test_llm_core_mistral_content.py`, `tests/test_llm_core_ollama.py`, `tests/test_llm_core_ollama_thinking.py`, `tests/test_llm_core_openai_reasoning_tools.py`, `tests/test_llm_core_reasoning.py`, `tests/test_llm_core_reasoning_content_fallback.py`, `tests/test_llm_core_sanitize_tool_calls.py`, `tests/test_llm_core_sse_no_space.py`, `tests/test_llm_core_streaming.py`, `tests/test_llm_core_system_msg_missing_content.py`, `tests/test_llm_core_temperature_anthropic.py`, `tests/test_llm_core_temperature_moonshot.py`, `tests/test_llm_core_temperature_reasoning.py`, `tests/test_llm_core_thinking_models.py`, `tests/test_llm_core_usage_finish_delta.py`, `tests/test_model_capabilities.py`, `tests/test_model_capability_readers.py`, `tests/test_model_context.py`, `tests/test_model_defaults.py`, `tests/test_model_discovery_status.py`, `tests/test_model_helper_owner_scope.py`, `tests/test_model_interaction_registry.py`, `tests/test_model_name_tooltip.py`, `tests/test_model_routes.py`, `tests/test_model_sort_js.py`, `tests/test_provider_classification.py`, `tests/test_provider_classification_errors.py`, `tests/test_provider_classification_token_params.py`, `tests/test_provider_detection_builders.py`, `tests/test_provider_detection_detect.py`, `tests/test_provider_detection_host_match.py`, `tests/test_provider_device_flow_js.py`, `tests/test_provider_endpoints_headers.py`, `tests/test_provider_endpoints_models.py`, `tests/test_provider_endpoints_normalization.py`, `tests/test_provider_endpoints_tailscale.py`, `tests/test_provider_endpoints_url_building.py`, `tests/test_provider_label_js.py`, `tests/test_providers_mixtral_logo_js.py`, `tests/test_stt_leak.py`, `tests/test_tts_available_nonstring_provider.py`, `tests/test_tts_cache_stats.py`, `tests/test_tts_service_enforce_cache_limit.py`, `tests/test_tts_speed_malformed.py`, `tests/test_youtube_comments_timeout.py`, `tests/test_youtube_extract_id_nonstring.py`, `tests/test_youtube_handler_consolidation.py`, `tests/test_youtube_svc_comments_nondict.py`, `tests/test_youtube_transcript_seg_nondict.py`.

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
