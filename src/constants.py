# src/constants.py
"""Application-wide constants and configuration values."""
import os

from src.runtime_paths import get_app_root, get_default_data_dir

APP_VERSION = "1.0.3"

# Base paths
BASE_DIR = os.path.join(get_app_root(), "")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_DIR = os.getenv("ODYSSEUS_DATA_DIR", get_default_data_dir())

# Data file paths
# Single source of truth: every persisted file/dir lives under DATA_DIR, which
# is the ONLY place ODYSSEUS_DATA_DIR is read. Import these constants instead of
# re-deriving paths from __file__ or a relative "data" literal.
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")
MEMORY_FILE = os.path.join(DATA_DIR, "memory.json")
PERSONAL_DIR = os.path.join(DATA_DIR, "personal_docs")
RUNBOOK_DIR = os.path.join(PERSONAL_DIR, "runbook")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
FEATURES_FILE = os.path.join(DATA_DIR, "features.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
AUTH_FILE = os.path.join(DATA_DIR, "auth.json")
USER_PREFS_FILE = os.path.join(DATA_DIR, "user_prefs.json")
PRESETS_FILE = os.path.join(DATA_DIR, "presets.json")
INTEGRATIONS_FILE = os.path.join(DATA_DIR, "integrations.json")
CONTACTS_FILE = os.path.join(DATA_DIR, "contacts.json")
APP_KEY_FILE = os.path.join(DATA_DIR, ".app_key")
EMBEDDING_ENDPOINT_FILE = os.path.join(DATA_DIR, "embedding_endpoint.json")
COOKBOOK_STATE_FILE = os.path.join(DATA_DIR, "cookbook_state.json")
BG_JOBS_FILE = os.path.join(DATA_DIR, "bg_jobs.json")
VAULT_FILE = os.path.join(DATA_DIR, "vault.json")
TIDY_CALENDAR_STATE_FILE = os.path.join(DATA_DIR, "tidy_calendar_state.json")
SKILLS_FILE = os.path.join(DATA_DIR, "skills.json")
APP_DB = os.path.join(DATA_DIR, "app.db")
SCHEDULED_EMAILS_DB = os.path.join(DATA_DIR, "scheduled_emails.db")
EMAIL_CACHE_DB = os.path.join(DATA_DIR, "email_cache.db")

# Data subdirectories
PERSONAL_UPLOADS_DIR = os.path.join(DATA_DIR, "personal_uploads")
EMOJI_CACHE_DIR = os.path.join(DATA_DIR, "emoji_cache")
RAG_DIR = os.path.join(DATA_DIR, "rag")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma")
BG_JOBS_DIR = os.path.join(DATA_DIR, "bg_jobs")
DEEP_RESEARCH_DIR = os.path.join(DATA_DIR, "deep_research")
MCP_OAUTH_DIR = os.path.join(DATA_DIR, "mcp_oauth")
GENERATED_IMAGES_DIR = os.path.join(DATA_DIR, "generated_images")
TTS_CACHE_DIR = os.path.join(DATA_DIR, "tts_cache")
EMAIL_URGENCY_CACHE_DIR = os.path.join(DATA_DIR, "email_urgency_cache")
SKILLS_DIR = os.path.join(DATA_DIR, "skills")
GALLERY_DIR = os.path.join(DATA_DIR, "gallery")
GALLERY_UPLOADS_DIR = os.path.join(DATA_DIR, "gallery_uploads")
MEMORY_VECTORS_DIR = os.path.join(DATA_DIR, "memory_vectors")

# The only part of DATA_DIR the agent's file tools and subprocesses may touch.
# Everything else under DATA_DIR is application state (session store, auth
# database, encryption key, settings), and the agent has no business reading it.
AGENT_WORKSPACE_DIR = os.path.join(DATA_DIR, "agent_workspace")

# Paths with an intentional dedicated env override, defaulting under DATA_DIR.
MAIL_ATTACHMENTS_DIR = os.getenv("ODYSSEUS_MAIL_ATTACHMENTS_DIR", os.path.join(DATA_DIR, "mail-attachments"))
# `or` (not os.getenv's default arg) so a PRESENT-but-EMPTY value falls back to
# the default. docker-compose.yml injects `FASTEMBED_CACHE_PATH=${FASTEMBED_CACHE_PATH:-}`,
# which sets the var to "" when the host hasn't defined it. os.getenv(name, default)
# only returns the default when the var is ABSENT, so the empty string would win →
# os.makedirs("") raises [Errno 2] No such file or directory: '' → FastEmbed fails to
# init and all vector features (RAG, semantic memory, tool index) silently degrade.
FASTEMBED_CACHE_DIR = os.getenv("FASTEMBED_CACHE_PATH") or os.path.join(DATA_DIR, "fastembed_cache")

# Agent tool output limits (single source of truth — imported by tool_execution.py,
# tool_implementations.py, agent_tools.py, and any other module that needs them)
MAX_OUTPUT_CHARS = 10_000       # cap for bash/python/web_search/web_fetch output
MAX_READ_CHARS = 20_000         # cap for read_file / document preview
MAX_DIFF_LINES = 400            # cap for edit_file unified-diff display

# web_fetch response-size policy (#3812). MAX_OUTPUT_CHARS above only trims
# what the agent SEES; these caps bound what the server downloads, parses,
# and writes to the content cache. The soft cap is the default download
# budget; the agent can raise it per call (full/max_bytes) but never past
# the hard cap, so a model can't decide to pull a multi-GB file.
WEB_FETCH_SOFT_MAX_BYTES = 2_000_000    # default download budget (2 MB)
WEB_FETCH_HARD_MAX_BYTES = 20_000_000   # absolute ceiling, even with override (20 MB)

# API Configuration
MAX_CONTEXT_MESSAGES = 90
REQUEST_TIMEOUT = 20
OPENAI_COMPAT_PATH = "/v1/chat/completions"

# Outbound UA for web_fetch / web_search scraping; common desktop UA so pages serve normal HTML.
WEB_FETCH_USER_AGENT = os.environ.get(
    "WEB_FETCH_USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
)

# Environment variables with defaults
DEFAULT_HOST = os.getenv("LLM_HOST", "localhost")
LLM_HOSTS = [h.strip() for h in os.getenv("LLM_HOSTS", "").split(",") if h.strip()]
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SEARXNG_INSTANCE = os.getenv("SEARXNG_INSTANCE", "http://localhost:8080")


# Cleanup configuration
CLEANUP_ENABLED = os.getenv("CLEANUP_ENABLED", "True").lower() == "true"
CLEANUP_INTERVAL_HOURS = int(os.getenv("CLEANUP_INTERVAL_HOURS", "24"))

# Content guard — TextGuard inspection of untrusted content.
#
# Every external source (web results, fetched pages, emails, transcripts,
# memories, skills, MCP descriptions, tool output) is inspected at the
# src.prompt_security.untrusted_context_message boundary. Findings go to
# src/content_guard_sink.py, never into the prompt. All of it is optional and
# fails soft: without textguard installed, or with the guard disabled, the
# content path is unchanged.


def _read_positive_int_env(name: str, default: int) -> int:
    """Read a positive-integer env var, failing fast on a bad value.

    Matches src/upload_limits.read_byte_limit_env: an invalid value is a
    configuration error and should surface at import rather than silently
    falling back to a default that hides the typo.
    """
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if value < 1:
        raise ValueError(f"{name} must be greater than 0")
    return value


def _read_choice_env(name: str, default: str, choices: tuple) -> str:
    """Read an env var constrained to a fixed set of values."""
    raw = (os.getenv(name) or "").strip().lower()
    if not raw:
        return default
    if raw not in choices:
        raise ValueError(f"{name} must be one of: {', '.join(choices)}")
    return raw


CONTENT_GUARD_ENABLED = os.getenv("ODYSSEUS_CONTENT_GUARD", "True").lower() == "true"
# The semantic (PromptGuard) pass costs ~250 ms per item versus ~1 ms for the
# structural pass, so it can be disabled independently on constrained hosts.
CONTENT_GUARD_SEMANTIC_ENABLED = (
    os.getenv("ODYSSEUS_CONTENT_GUARD_SEMANTIC", "True").lower() == "true"
)
# textguard rewrite preset. "default" scans and normalises lightly; "strict"
# additionally strips invisible/bidi/ANSI characters; "ascii" transliterates.
CONTENT_GUARD_PRESET = _read_choice_env(
    "ODYSSEUS_CONTENT_GUARD_PRESET", "default", ("default", "strict", "ascii")
)
# Cap on the prefix inspected per item. Structural scanning is ~0.75 ms/KB, so
# the default bounds one inspection at roughly 150 ms; the web fetch soft cap is
# 2 MB and the hard cap 20 MB, which would otherwise cost 1.5-15 s per page.
CONTENT_GUARD_MAX_SCAN_CHARS = _read_positive_int_env(
    "ODYSSEUS_CONTENT_GUARD_MAX_SCAN_CHARS", 200_000
)
# Explicit PromptGuard model-pack directory. Empty falls back to textguard's own
# XDG location (~/.local/share/textguard/models/promptguard2).
CONTENT_GUARD_PROMPTGUARD_MODEL_PATH = os.getenv("ODYSSEUS_CONTENT_GUARD_MODEL_PATH", "")
# Retained findings in the in-memory sink, and the excerpt cap for each finding.
CONTENT_GUARD_SINK_MAX_RECORDS = _read_positive_int_env(
    "ODYSSEUS_CONTENT_GUARD_SINK_MAX_RECORDS", 200
)
CONTENT_GUARD_EXCERPT_MAX_CHARS = 200
# Verdict cache size, keyed by content digest. The agent loop rebuilds its
# message list every round, so the same tool result is re-wrapped (and would be
# re-scanned) on each round; this makes repeats free and keeps the sink to one
# record per distinct blob.
CONTENT_GUARD_CACHE_SIZE = _read_positive_int_env("ODYSSEUS_CONTENT_GUARD_CACHE_SIZE", 256)

# Auth policy
PASSWORD_MIN_LENGTH = 8

# Default parameters
DEFAULT_TEMPERATURE = 1.0
DEFAULT_MAX_TOKENS = 0


def internal_api_base() -> str:
    """Base URL for in-process loopback calls to Odysseus's own API.

    Agent tools and background jobs reach admin-gated routes by calling the
    running server over HTTP. Resolution order:
      1. ODYSSEUS_INTERNAL_BASE  - explicit override (e.g. behind a TLS proxy).
      2. APP_PORT                - http://127.0.0.1:$APP_PORT (docker-compose).
      3. Fallback http://127.0.0.1:7000 - legacy default.

    127.0.0.1 (not "localhost") avoids IPv6/DNS ambiguity for a strictly-local
    call. Without this, loopback tools fail with "All connection attempts
    failed" whenever the server is not on port 7000.
    """
    override = os.environ.get("ODYSSEUS_INTERNAL_BASE")
    if override:
        return override.rstrip("/")
    return f"http://127.0.0.1:{os.environ.get('APP_PORT', '7000')}"
