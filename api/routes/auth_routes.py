from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse
from configs.config import settings
from modules.auth_service import build_google_login_url, exchange_code_for_session, get_user_from_request
from modules.session_store import delete_session

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.get("/google/login")
async def google_login():
    return RedirectResponse(build_google_login_url())

@router.get("/google/callback")
async def google_callback(code: str):
    session_id, _user = await exchange_code_for_session(code)
    response = RedirectResponse(f"{settings.frontend_origin}/?auth=success")
    response.set_cookie(
        key="legalease_session",
        value=session_id,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    return response

@router.get("/me")
async def me(request: Request):
    user = get_user_from_request(request)
    return {"authenticated": bool(user), "user": user}

@router.post("/logout")
async def logout(request: Request):
    session_id = request.cookies.get("legalease_session")
    delete_session(session_id)
    response = Response(content='{"ok": true}', media_type="application/json")
    response.delete_cookie("legalease_session")
    return response
