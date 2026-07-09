from fastapi import APIRouter, HTTPException, Request
from modules.auth_service import get_access_token_from_request
from modules.triage_engine import triage_email
from shared.schemas.triage_schema import TriageRequest

router = APIRouter(prefix="/api/triage", tags=["triage"])

@router.post("/email")
async def triage_email_route(request: Request, payload: TriageRequest):
    await get_access_token_from_request(request)
    try:
        result = await triage_email(payload.email)
        return result.model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to triage email: {str(exc)}")
