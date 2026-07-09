from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("")
async def health_check():
    return {"ok": True, "service": "legalease-fastapi-backend", "timestamp": datetime.now(timezone.utc).isoformat()}
