"""Provide an ephemeral signing key for isolated tests only."""
import os
import secrets

os.environ.setdefault("AUDIT_SECRET_KEY", secrets.token_hex(32))
