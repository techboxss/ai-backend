import time
import uuid
from typing import Any

SESSIONS: dict[str, dict[str, Any]] = {}


def create_session(tokens: dict, user: dict) -> str:
    session_id = uuid.uuid4().hex
    expires_at = time.time() + int(tokens.get("expires_in", 3600)) - 60
    SESSIONS[session_id] = {
        "tokens": tokens,
        "user": user,
        "expires_at": expires_at,
    }
    return session_id


def get_session(session_id: str | None) -> dict | None:
    if not session_id:
        return None
    return SESSIONS.get(session_id)


def delete_session(session_id: str | None) -> None:
    if session_id:
        SESSIONS.pop(session_id, None)


def update_tokens(session_id: str, tokens: dict) -> None:
    session = SESSIONS.get(session_id)
    if not session:
        return
    merged = {**session["tokens"], **tokens}
    session["tokens"] = merged
    session["expires_at"] = time.time() + int(tokens.get("expires_in", 3600)) - 60
