"""Bounded sink for content-guard findings.

`src/content_guard.py` inspects untrusted content but must not put its findings
into the model-visible prompt: ``UNTRUSTED_CONTEXT_POLICY`` explicitly tells the
model not to mention wrapper labels or prompt-injection warnings, so anything
smuggled in as prompt text is both self-defeating and a leak risk. Findings
therefore land here instead — a bounded in-process store plus a structured log
line — and the admin API in ``routes/content_guard_routes.py`` reads them back
for display.

The store is intentionally in-memory and bounded: findings are operational
telemetry for "what hostile content just arrived", not an audit trail. Nothing
here is written to disk, so a restart clears it.
"""

from __future__ import annotations

import logging
import threading
from collections import deque
from datetime import datetime, timezone
from typing import Any, Deque, Dict, List, Optional

from src.constants import CONTENT_GUARD_EXCERPT_MAX_CHARS, CONTENT_GUARD_SINK_MAX_RECORDS

logger = logging.getLogger(__name__)

# Ordered severity scale. Finding severities from textguard are
# info/warn/error; semantic tiers from PromptGuard are none/medium/high/critical.
# Both are projected onto this one scale so the API has a single sortable field.
SEVERITY_ORDER = {"info": 0, "warn": 1, "error": 2, "critical": 3}

# PromptGuard tier -> unified severity. "none" is deliberately absent: a clean
# semantic verdict must not raise the record's severity above its findings.
_TIER_SEVERITY = {
    "medium": "warn",
    "high": "error",
    "critical": "critical",
}

# Characters that are invisible or can reorder terminal/HTML display. Excerpts
# are quoted back to an admin UI, so they are escaped rather than rendered.


def _escape_invisible(text: str) -> str:
    """Escape invisible and display-reordering characters.

    Findings routinely point at zero-width or bidi characters, so a naive
    excerpt would render as invisible or reversed text in the UI — exactly the
    confusion the finding is reporting. Escaping keeps them visible and inert.
    """
    out: List[str] = []
    for char in text:
        if "\u007f" <= char <= "\u009f" or char in "\u00ad\ufeff" or (
            "\u200b" <= char <= "\u200f"
        ) or ("\u202a" <= char <= "\u202e") or ("\u2060" <= char <= "\u206f"):
            out.append(f"\\u{ord(char):04x}")
        else:
            out.append(char)
    return "".join(out)


def _clamp_excerpt(text: str) -> str:
    escaped = _escape_invisible(str(text or ""))
    if len(escaped) > CONTENT_GUARD_EXCERPT_MAX_CHARS:
        return escaped[: CONTENT_GUARD_EXCERPT_MAX_CHARS] + "…"
    return escaped


def _max_severity(values: List[str]) -> str:
    best = "info"
    for value in values:
        if SEVERITY_ORDER.get(value, 0) > SEVERITY_ORDER.get(best, 0):
            best = value
    return best


class ContentGuardSink:
    """Thread-safe, bounded ring buffer of content-guard findings.

    Scans run from FastAPI's threadpool (and from agent threads), so every
    mutation is lock-guarded.
    """

    def __init__(self, max_records: int = CONTENT_GUARD_SINK_MAX_RECORDS) -> None:
        self._lock = threading.Lock()
        self._records: Deque[Dict[str, Any]] = deque(maxlen=max(1, int(max_records)))
        self._total = 0
        self._by_severity: Dict[str, int] = {}

    def record(
        self,
        *,
        source: str,
        findings: List[Dict[str, Any]],
        semantic_score: Optional[float] = None,
        semantic_tier: Optional[str] = None,
        owner: Optional[str] = None,
        session_id: Optional[str] = None,
        scanned_chars: int = 0,
        truncated: bool = False,
    ) -> Dict[str, Any]:
        """Store one inspection result. Returns the stored record."""
        severities = [str(item.get("severity") or "info") for item in findings]
        if semantic_tier:
            mapped = _TIER_SEVERITY.get(str(semantic_tier))
            if mapped:
                severities.append(mapped)
        severity = _max_severity(severities) if severities else "info"

        kinds = sorted({str(item.get("kind") or "unknown") for item in findings})

        record: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": _clamp_excerpt(source),
            "owner": owner or None,
            "session_id": session_id or None,
            "severity": severity,
            "kinds": kinds,
            "finding_count": len(findings),
            "semantic_score": (
                round(float(semantic_score), 4) if semantic_score is not None else None
            ),
            "semantic_tier": semantic_tier or None,
            "scanned_chars": int(scanned_chars),
            "truncated": bool(truncated),
        }

        with self._lock:
            self._records.append(record)
            self._total += 1
            self._by_severity[severity] = self._by_severity.get(severity, 0) + 1

        # Log so the finding is visible even without an admin watching the API.
        log = logger.warning if SEVERITY_ORDER.get(severity, 0) >= SEVERITY_ORDER["error"] else logger.info
        log(
            "content-guard: severity=%s source=%s kinds=%s findings=%d semantic=%s",
            severity,
            record["source"],
            ",".join(kinds) or "-",
            len(findings),
            f"{record['semantic_tier']}({record['semantic_score']})"
            if record["semantic_tier"]
            else "-",
        )
        return record

    def recent(
        self,
        limit: int = 50,
        *,
        owner: Optional[str] = None,
        min_severity: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return the newest records first, optionally filtered."""
        threshold = SEVERITY_ORDER.get(str(min_severity or "info"), 0)
        with self._lock:
            records = list(self._records)
        selected = [
            item
            for item in reversed(records)
            if (owner is None or item.get("owner") == owner)
            and SEVERITY_ORDER.get(str(item.get("severity")), 0) >= threshold
        ]
        return selected[: max(1, int(limit))]

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "total_recorded": self._total,
                "retained": len(self._records),
                "capacity": self._records.maxlen,
                "by_severity": dict(self._by_severity),
            }

    def clear(self) -> int:
        with self._lock:
            count = len(self._records)
            self._records.clear()
        return count


_sink = ContentGuardSink()


def get_sink() -> ContentGuardSink:
    """Return the process-wide sink."""
    return _sink


def record_findings(**kwargs: Any) -> Dict[str, Any]:
    """Record via the process-wide sink."""
    return _sink.record(**kwargs)
