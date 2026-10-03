"""Content-guard sink: severity mapping, bounding, filtering, and escaping."""

import threading

from src.content_guard_sink import ContentGuardSink


def _finding(kind="invisible_char", severity="warn"):
    return {"kind": kind, "severity": severity, "detail": "", "codepoint": "", "offset": None}


# ── recording and ordering ───────────────────────────────────────


def test_recent_returns_newest_first():
    sink = ContentGuardSink()
    sink.record(source="first", findings=[_finding()])
    sink.record(source="second", findings=[_finding()])

    assert [r["source"] for r in sink.recent()] == ["second", "first"]


def test_record_carries_metadata():
    sink = ContentGuardSink()
    record = sink.record(
        source="email: invoice",
        findings=[_finding("bidi_control", "error")],
        owner="admin",
        session_id="sess-1",
        scanned_chars=42,
        truncated=True,
    )

    assert record["source"] == "email: invoice"
    assert record["owner"] == "admin"
    assert record["session_id"] == "sess-1"
    assert record["scanned_chars"] == 42
    assert record["truncated"] is True
    assert record["kinds"] == ["bidi_control"]
    assert record["finding_count"] == 1
    assert record["timestamp"]


# ── severity mapping ─────────────────────────────────────────────


def test_severity_is_the_max_across_findings():
    sink = ContentGuardSink()
    record = sink.record(
        source="web",
        findings=[_finding(severity="info"), _finding(severity="error"), _finding(severity="warn")],
    )

    assert record["severity"] == "error"


def test_semantic_tier_raises_severity_above_findings():
    sink = ContentGuardSink()
    record = sink.record(
        source="web",
        findings=[_finding(severity="warn")],
        semantic_score=0.95,
        semantic_tier="critical",
    )

    assert record["severity"] == "critical"


def test_semantic_tier_none_does_not_lower_severity():
    """A clean semantic verdict must not mask a structural error."""
    sink = ContentGuardSink()
    record = sink.record(
        source="web",
        findings=[_finding(severity="error")],
        semantic_score=0.01,
        semantic_tier="none",
    )

    assert record["severity"] == "error"


def test_semantic_only_hit_is_recorded():
    sink = ContentGuardSink()
    record = sink.record(
        source="web", findings=[], semantic_score=0.9, semantic_tier="high"
    )

    assert record["severity"] == "error"
    assert record["kinds"] == []
    assert record["semantic_tier"] == "high"


def test_semantic_score_is_rounded():
    sink = ContentGuardSink()
    record = sink.record(
        source="web", findings=[], semantic_score=0.123456789, semantic_tier="medium"
    )

    assert record["semantic_score"] == 0.1235


# ── bounding ─────────────────────────────────────────────────────


def test_capacity_is_bounded_and_drops_oldest():
    sink = ContentGuardSink(max_records=3)
    for index in range(5):
        sink.record(source=f"src-{index}", findings=[_finding()])

    sources = [r["source"] for r in sink.recent(limit=10)]
    assert sources == ["src-4", "src-3", "src-2"]
    assert sink.stats()["retained"] == 3
    # Totals keep counting past the cap so operators see real volume.
    assert sink.stats()["total_recorded"] == 5


def test_capacity_of_zero_still_retains_one():
    """A misconfigured zero must not silently discard every finding."""
    sink = ContentGuardSink(max_records=0)
    sink.record(source="only", findings=[_finding()])

    assert sink.stats()["retained"] == 1


# ── filtering ────────────────────────────────────────────────────


def test_min_severity_filters_lower_severities():
    sink = ContentGuardSink()
    sink.record(source="low", findings=[_finding(severity="info")])
    sink.record(source="mid", findings=[_finding(severity="warn")])
    sink.record(source="high", findings=[_finding(severity="error")])

    assert [r["source"] for r in sink.recent(min_severity="error")] == ["high"]
    assert [r["source"] for r in sink.recent(min_severity="warn")] == ["high", "mid"]


def test_owner_filter():
    sink = ContentGuardSink()
    sink.record(source="a", findings=[_finding()], owner="alice")
    sink.record(source="b", findings=[_finding()], owner="bob")

    assert [r["source"] for r in sink.recent(owner="alice")] == ["a"]
    assert len(sink.recent(owner=None)) == 2


def test_limit_is_applied():
    sink = ContentGuardSink()
    for index in range(5):
        sink.record(source=f"s{index}", findings=[_finding()])

    assert len(sink.recent(limit=2)) == 2


# ── excerpt escaping ─────────────────────────────────────────────


def test_invisible_characters_are_escaped_in_source_label():
    """A finding about a zero-width char must not render invisibly in the UI."""
    sink = ContentGuardSink()
    record = sink.record(source="web\u200bpage\u202eevil", findings=[_finding()])

    assert "\u200b" not in record["source"]
    assert "\u202e" not in record["source"]
    assert "\\u200b" in record["source"]
    assert "\\u202e" in record["source"]


def test_source_label_is_length_capped():
    from src.constants import CONTENT_GUARD_EXCERPT_MAX_CHARS

    sink = ContentGuardSink()
    record = sink.record(source="x" * 5000, findings=[_finding()])

    assert len(record["source"]) == CONTENT_GUARD_EXCERPT_MAX_CHARS + 1  # + ellipsis
    assert record["source"].endswith("…")


# ── clear and stats ──────────────────────────────────────────────


def test_clear_empties_the_buffer():
    sink = ContentGuardSink()
    sink.record(source="a", findings=[_finding()])

    assert sink.clear() == 1
    assert sink.recent() == []


def test_stats_counts_by_severity():
    sink = ContentGuardSink()
    sink.record(source="a", findings=[_finding(severity="error")])
    sink.record(source="b", findings=[_finding(severity="error")])
    sink.record(source="c", findings=[_finding(severity="info")])

    stats = sink.stats()
    assert stats["by_severity"] == {"error": 2, "info": 1}
    assert stats["total_recorded"] == 3


# ── concurrency ──────────────────────────────────────────────────


def test_concurrent_records_are_not_lost():
    """Scans run from FastAPI's threadpool, so writes must be lock-guarded."""
    sink = ContentGuardSink(max_records=500)
    threads = [
        threading.Thread(
            target=lambda n=n: [sink.record(source=f"t{n}-{i}", findings=[_finding()]) for i in range(50)]
        )
        for n in range(8)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sink.stats()["total_recorded"] == 400
    assert sink.stats()["retained"] == 400
