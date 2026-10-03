"""Content-guard routes — inspection status and recorded findings.

Findings are produced by :mod:`src.content_guard` at the untrusted-content
boundary and stored by :mod:`src.content_guard_sink`. They are surfaced here
rather than in the prompt, so an operator can see what hostile content arrived
without the model being told about (or asked to repeat) it.

Admin-only: findings describe untrusted content arriving on the instance, which
is operational telemetry rather than per-user data.
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request

from core.middleware import require_admin

logger = logging.getLogger(__name__)


def setup_content_guard_routes() -> APIRouter:
    router = APIRouter(tags=["content-guard"])

    @router.get("/api/content-guard/status")
    async def get_content_guard_status(request: Request) -> Dict[str, Any]:
        """Report whether inspection is enabled, loaded, and semantically armed.

        Deliberately does not force a scanner load, so this stays cheap to poll.
        """
        require_admin(request)
        from src.content_guard import status

        return status()

    @router.get("/api/content-guard/findings")
    async def get_content_guard_findings(
        request: Request,
        limit: int = 50,
        min_severity: str = "info",
        owner: str = "",
    ) -> Dict[str, Any]:
        """Return the newest findings first, optionally filtered by severity."""
        require_admin(request)
        from src.content_guard_sink import SEVERITY_ORDER, get_sink

        if min_severity and min_severity not in SEVERITY_ORDER:
            raise HTTPException(
                400, f"min_severity must be one of: {', '.join(SEVERITY_ORDER)}"
            )

        sink = get_sink()
        return {
            "findings": sink.recent(
                limit=max(1, min(limit, 500)),
                min_severity=min_severity or None,
                owner=(owner or "").strip() or None,
            ),
            "stats": sink.stats(),
        }

    @router.post("/api/content-guard/findings/clear")
    async def clear_content_guard_findings(request: Request) -> Dict[str, Any]:
        require_admin(request)
        from src.content_guard_sink import get_sink

        return {"cleared": get_sink().clear()}

    return router
