import time
import urllib.parse
import httpx
from fastapi import HTTPException, Request
from configs.config import settings
from shared.constants import GOOGLE_AUTH_URL, GOOGLE_TOKEN_URL, GOOGLE_USERINFO_URL, GOOGLE_SCOPES
from modules.session_store import create_session, get_session, update_tokens


def build_google_login_url() -> str:
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=500, detail="Google OAuth env vars are not configured.")
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": " ".join(GOOGLE_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
    }
    return f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"


async def exchange_code_for_session(code: str) -> tuple[str, dict]:
    async with httpx.AsyncClient(timeout=60) as client:
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_response.status_code >= 400:
            raise HTTPException(status_code=400, detail=f"Google token exchange failed: {token_response.text}")
        tokens = token_response.json()
        user_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        if user_response.status_code >= 400:
            raise HTTPException(status_code=400, detail="Could not fetch Google user profile.")
        user = user_response.json()
    session_id = create_session(tokens, user)
    return session_id, user


async def refresh_access_token(session_id: str, refresh_token: str) -> str:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
    if response.status_code >= 400:
        raise HTTPException(status_code=401, detail="Google session expired. Please sign in again.")
    tokens = response.json()
    update_tokens(session_id, tokens)
    return tokens["access_token"]


async def get_access_token_from_request(request: Request) -> str:
    session_id = request.cookies.get("legalease_session")
    session = get_session(session_id)
    if not session or not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated with Gmail.")
    if time.time() >= session.get("expires_at", 0):
        refresh_token = session["tokens"].get("refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Google session expired. Please sign in again.")
        return await refresh_access_token(session_id, refresh_token)
    return session["tokens"]["access_token"]


def get_user_from_request(request: Request) -> dict | None:
    session = get_session(request.cookies.get("legalease_session"))
    return session.get("user") if session else None
