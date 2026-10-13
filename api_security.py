"""Shared access policy for the local FastAPI entry points."""
import hmac
import os

from fastapi import HTTPException, Request


def require_api_access(request: Request) -> None:
    """Only allow loopback requests when no API key has been configured."""
    expected = os.getenv("CYTOLOGY_API_KEY")
    if expected:
        provided = request.headers.get("x-api-key", "")
        if not hmac.compare_digest(provided, expected):
            raise HTTPException(status_code=401, detail="Invalid or missing API key")
    elif not request.client or request.client.host not in ("127.0.0.1", "::1"):
        raise HTTPException(
            status_code=503,
            detail="Remote API access disabled: configure CYTOLOGY_API_KEY",
        )
