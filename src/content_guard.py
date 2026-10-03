"""TextGuard-backed inspection of untrusted content.

Odysseus already routes every external source through
``src.prompt_security.untrusted_context_message`` — web results, fetched pages,
emails, transcripts, memories, skills, MCP descriptions and raw tool output.
This module adds a TextGuard inspection pass at that same boundary so hostile
text is characterised before the model ever sees it.

Two independent detectors run:

* **Structural** (``textguard.scan``) — invisible characters, bidi controls,
  homoglyph/confusable substitution, Unicode tag characters, encoded payloads.
  Cheap (~1 ms for a typical page) and always available.
* **Semantic** (PromptGuard v2 via ONNX) — a classifier score for
  instruction-injection intent. Costs ~250 ms per item and needs the optional
  ``textguard[promptguard]`` extra plus a downloaded model pack, so it degrades
  away independently of the structural pass.

Findings are handed to :mod:`src.content_guard_sink`; they are deliberately not
written into the prompt (see that module's docstring for why).

Everything here fails soft. A guard that raises inside
``untrusted_context_message`` would take down chat, email and research at once,
so an unavailable dependency, a missing model pack or a scan error disables the
guard and logs, rather than propagating.
"""

from __future__ import annotations

import hashlib
import logging
import os
import threading
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.constants import (
    CONTENT_GUARD_CACHE_SIZE,
    CONTENT_GUARD_ENABLED,
    CONTENT_GUARD_MAX_SCAN_CHARS,
    CONTENT_GUARD_PRESET,
    CONTENT_GUARD_PROMPTGUARD_MODEL_PATH,
    CONTENT_GUARD_SEMANTIC_ENABLED,
)

logger = logging.getLogger(__name__)

# PromptGuard v2 pack name in textguard's own model registry.
_PROMPTGUARD_MODEL_NAME = "promptguard2"

_load_lock = threading.Lock()
_scanner: Any = None
_scanner_ready = False
_semantic_ready = False
_degraded_reason: Optional[str] = None

# Content digest -> verdict. Bounded LRU; see CONTENT_GUARD_CACHE_SIZE.
_cache_lock = threading.Lock()
_verdict_cache: "OrderedDict[str, GuardVerdict]" = OrderedDict()

@dataclass
class GuardVerdict:
    """One inspection result. Serialisable; carries no raw source text."""

    findings: List[Dict[str, Any]] = field(default_factory=list)
    semantic_score: Optional[float] = None
    semantic_tier: Optional[str] = None
    scanned_chars: int = 0
    truncated: bool = False

    @property
    def has_findings(self) -> bool:
        return bool(self.findings)

    @property
    def is_flagged(self) -> bool:
        """True when anything was detected, structural or semantic."""
        return bool(self.findings) or self.semantic_tier not in (None, "none")


def _resolve_model_path() -> Optional[str]:
    """Return the PromptGuard pack directory, or None when it is not installed.

    An explicit ``ODYSSEUS_CONTENT_GUARD_MODEL_PATH`` wins; otherwise try
    textguard's own resolver, then its documented XDG location. The second
    candidate matters because ``default_model_dir`` is not re-exported from
    ``textguard.backends`` — it lives in ``textguard.backends.promptguard`` — so
    relying on the import alone would silently disable semantic detection if
    textguard reorganises its internals.
    """
    configured = (CONTENT_GUARD_PROMPTGUARD_MODEL_PATH or "").strip()
    if configured:
        return configured

    candidates: List[Path] = []
    try:
        from textguard.backends.promptguard import default_model_dir

        candidates.append(Path(default_model_dir(_PROMPTGUARD_MODEL_NAME)))
    except Exception:
        pass

    xdg = (os.environ.get("XDG_DATA_HOME") or "").strip()
    base = Path(xdg).expanduser() if xdg else Path.home() / ".local" / "share"
    candidates.append(base / "textguard" / "models" / _PROMPTGUARD_MODEL_NAME)

    for candidate in candidates:
        try:
            if candidate.is_dir():
                return str(candidate)
        except OSError:
            continue
    return None


def _prepare_transformers_env() -> None:
    """Silence transformers' "PyTorch was not found" advisory.

    textguard's PromptGuard backend uses only the tokenizer plus ONNX Runtime —
    never the torch model runtime — so the advisory is expected rather than a
    fault, but it prints on every load and reads like a broken install.

    ``TRANSFORMERS_NO_ADVISORY_WARNINGS`` is transformers' own documented opt-out
    and is consulted only by ``Logger.warning_advice``, so genuine warnings and
    errors still surface. ``setdefault`` leaves an operator free to override it.

    Must run before transformers is first imported: the check happens at import
    time in ``transformers/__init__.py``. textguard imports transformers lazily
    inside its backend loader, so setting it here is early enough.
    """
    os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")


def _semantic_deps_available() -> bool:
    """Whether the optional [promptguard] dependencies are installed.

    Checked before arming the semantic backend because textguard loads it lazily
    inside ``scan()``: on a host that installed base ``textguard`` but not the
    ``[promptguard]`` extra, the model path resolves fine and the failure only
    surfaces at scan time — where it would take the structural pass down with it.

    Uses ``find_spec`` rather than importing, so this stays cheap enough for
    ``status()`` to call and does not pull transformers into the process. A
    dependency that is present but broken at import is caught by the scan-time
    demotion path instead.
    """
    import importlib.util

    for name in ("onnxruntime", "transformers"):
        try:
            if importlib.util.find_spec(name) is None:
                return False
        except (ImportError, ValueError):
            return False
    return True


def _build_scanner(model_path: Optional[str]) -> Any:
    """Construct the TextGuard instance, or raise with a readable reason."""
    _prepare_transformers_env()
    from textguard import TextGuard

    kwargs: Dict[str, Any] = {"preset": CONTENT_GUARD_PRESET}
    if model_path is not None:
        kwargs["promptguard_model_path"] = model_path
    return TextGuard(**kwargs)


def _resolve_semantic_model_path(*, log: bool = True) -> Optional[str]:
    """Model path to arm the semantic pass with, or None to stay structural.

    Returns None when the pass is disabled, when no pack is installed, or when
    the [promptguard] dependencies are missing — the last case being the normal
    state for an install that took only the base ``textguard`` requirement.

    ``log=False`` for status probes, which run on every poll and would otherwise
    repeat the explanation on each one.
    """
    if not CONTENT_GUARD_SEMANTIC_ENABLED:
        return None
    model_path = _resolve_model_path()
    if model_path is None:
        if log:
            logger.info(
                "content-guard: PromptGuard model pack not found; semantic detection "
                "disabled (set ODYSSEUS_CONTENT_GUARD_MODEL_PATH, or run "
                "`textguard models fetch %s`)",
                _PROMPTGUARD_MODEL_NAME,
            )
        return None
    if not _semantic_deps_available():
        if log:
            logger.info(
                "content-guard: semantic detection disabled — the optional "
                "[promptguard] dependencies are not installed "
                "(`pip install -r requirements-optional.txt`); structural "
                "detection is unaffected"
            )
        return None
    return model_path


def _get_scanner() -> Any:
    """Lazily build and memoise the scanner. Returns None when unavailable."""
    global _scanner, _scanner_ready, _semantic_ready, _degraded_reason

    if _scanner_ready:
        return _scanner

    with _load_lock:
        if _scanner_ready:
            return _scanner
        try:
            model_path = _resolve_semantic_model_path()
            _scanner = _build_scanner(model_path)
            _semantic_ready = model_path is not None
            _degraded_reason = None
        except ImportError:
            _scanner = None
            _degraded_reason = "textguard is not installed"
            logger.info(
                "content-guard: disabled — %s (install `textguard` to enable)", _degraded_reason
            )
        except Exception as exc:
            _scanner = None
            _degraded_reason = str(exc)
            logger.error("content-guard: disabled — scanner init failed: %s", exc)
        _scanner_ready = True
        return _scanner


def _demote_to_structural(reason: str) -> None:
    """Rebuild the scanner without the semantic backend after a scan failure.

    The semantic backend is the only optional part that can fail mid-scan (a
    corrupt or half-downloaded model pack, for instance). Dropping it keeps the
    structural pass working instead of losing both, and stops every later scan
    from re-paying the failed attempt.
    """
    global _scanner, _scanner_ready, _semantic_ready
    with _load_lock:
        logger.warning(
            "content-guard: semantic detection disabled after a scan failure "
            "(%s); continuing with structural detection only",
            reason,
        )
        try:
            _scanner = _build_scanner(None)
        except Exception as exc:
            _scanner = None
            logger.error("content-guard: structural scanner rebuild failed: %s", exc)
        _semantic_ready = False
        _scanner_ready = True


def is_enabled() -> bool:
    """Whether inspection should run at all."""
    return bool(CONTENT_GUARD_ENABLED)


def status() -> Dict[str, Any]:
    """Report guard configuration and health, without forcing a load.

    ``semantic_available`` reflects what the next scan would actually do: once
    the scanner is loaded it reports the armed state, and before that it probes
    the three things the semantic pass needs (the setting, a model pack, and the
    optional dependencies) so an operator sees an accurate picture immediately
    rather than a false ``false`` until first use.
    """
    if _scanner_ready:
        semantic_available = _semantic_ready
        loaded = _scanner is not None
    else:
        semantic_available = _resolve_semantic_model_path(log=False) is not None
        loaded = False
    return {
        "enabled": is_enabled(),
        "loaded": loaded,
        "semantic_enabled": bool(CONTENT_GUARD_SEMANTIC_ENABLED),
        "semantic_available": semantic_available,
        "preset": CONTENT_GUARD_PRESET,
        "max_scan_chars": CONTENT_GUARD_MAX_SCAN_CHARS,
        "model_path": _resolve_model_path() if CONTENT_GUARD_SEMANTIC_ENABLED else None,
        "degraded_reason": _degraded_reason,
    }


def _cache_get(digest: str) -> Optional[GuardVerdict]:
    with _cache_lock:
        verdict = _verdict_cache.get(digest)
        if verdict is not None:
            _verdict_cache.move_to_end(digest)
        return verdict


def _cache_put(digest: str, verdict: GuardVerdict) -> None:
    with _cache_lock:
        _verdict_cache[digest] = verdict
        _verdict_cache.move_to_end(digest)
        while len(_verdict_cache) > max(1, int(CONTENT_GUARD_CACHE_SIZE)):
            _verdict_cache.popitem(last=False)


def inspect_untrusted(
    label: str,
    text: str,
    *,
    owner: Optional[str] = None,
    session_id: Optional[str] = None,
    record: bool = True,
) -> Optional[GuardVerdict]:
    """Inspect untrusted ``text`` and optionally record findings.

    Returns None when the guard is disabled or unavailable, so callers can treat
    "no verdict" and "clean verdict" identically. Never raises.

    Verdicts are cached by content digest. The agent loop rebuilds its message
    list every round, so the same tool result is re-wrapped — and would
    otherwise be re-scanned at ~250 ms with the semantic pass — on every round.
    A cache hit also skips recording, which keeps the sink to one entry per
    distinct blob instead of one per round.
    """
    if not is_enabled():
        return None

    body = "" if text is None else str(text)
    if not body.strip():
        return None

    budget = max(1, int(CONTENT_GUARD_MAX_SCAN_CHARS))
    truncated = len(body) > budget
    sample = body[:budget]

    digest = hashlib.sha256(sample.encode("utf-8", "replace")).hexdigest()
    cached = _cache_get(digest)
    if cached is not None:
        return cached

    scanner = _get_scanner()
    if scanner is None:
        return None

    try:
        result = scanner.scan(sample)
    except Exception as exc:
        # A scan failure must never break the content path it is protecting.
        logger.warning("content-guard: scan failed for source=%r: %s", label, exc)
        if not _semantic_ready:
            return None
        # The semantic backend is the only optional part that fails this way, and
        # it takes the structural pass down with it. Demote and retry rather than
        # discarding a result the structural pass could still produce.
        _demote_to_structural(str(exc))
        scanner = _get_scanner()
        if scanner is None:
            return None
        try:
            result = scanner.scan(sample)
        except Exception as retry_exc:
            logger.warning(
                "content-guard: structural scan failed for source=%r: %s", label, retry_exc
            )
            return None

    findings = [
        {
            "kind": getattr(item, "kind", "") or "unknown",
            "severity": getattr(item, "severity", "") or "info",
            "detail": getattr(item, "detail", "") or "",
            "codepoint": getattr(item, "codepoint", "") or "",
            "offset": getattr(item, "offset", None),
            "excerpt": getattr(getattr(item, "context", None), "excerpt", "") or "",
        }
        for item in (getattr(result, "findings", None) or [])
    ]

    semantic = getattr(result, "semantic", None)
    verdict = GuardVerdict(
        findings=findings,
        semantic_score=getattr(semantic, "score", None),
        semantic_tier=getattr(semantic, "tier", None),
        scanned_chars=len(sample),
        truncated=truncated,
    )

    _cache_put(digest, verdict)

    if record and verdict.is_flagged:
        try:
            from src.content_guard_sink import record_findings

            record_findings(
                source=label,
                findings=findings,
                semantic_score=verdict.semantic_score,
                semantic_tier=verdict.semantic_tier,
                owner=owner,
                session_id=session_id,
                scanned_chars=verdict.scanned_chars,
                truncated=verdict.truncated,
            )
        except Exception as exc:  # pragma: no cover - sink is defensive by design
            logger.warning("content-guard: sink write failed: %s", exc)

    return verdict


def reset_for_tests() -> None:
    """Drop the memoised scanner and verdict cache so tests can start clean."""
    global _scanner, _scanner_ready, _semantic_ready, _degraded_reason
    with _load_lock:
        _scanner = None
        _scanner_ready = False
        _semantic_ready = False
        _degraded_reason = None
    with _cache_lock:
        _verdict_cache.clear()