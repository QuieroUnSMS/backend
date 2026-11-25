import hashlib
import secrets


def generate_session_token() -> str:
    """Opaque URL-safe token with at least 256 bits of randomness."""
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    """SHA-256 hex digest stored at rest; the raw token is never persisted."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
