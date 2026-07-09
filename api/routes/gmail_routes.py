from fastapi import APIRouter, HTTPException, Request
from modules.auth_service import get_access_token_from_request
from modules.gmail_fetcher import fetch_gmail_threads
from modules.gmail_actions import create_gmail_draft_reply, send_gmail_reply, archive_gmail_thread
from modules.property_extractor import extract_property_transaction_from_email
from shared.schemas.gmail_schema import EmailDraftRequest, SendReplyRequest, ArchiveThreadRequest
from shared.schemas.property_schema import PropertyTransactionsResponse

router = APIRouter(prefix="/api/gmail", tags=["gmail"])

@router.get("/threads")
async def get_threads(request: Request):
    access_token = await get_access_token_from_request(request)
    try:
        threads = await fetch_gmail_threads(access_token)
        return {"threads": [thread.model_dump() for thread in threads]}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Gmail threads: {str(exc)}")

@router.get("/property-transactions", response_model=PropertyTransactionsResponse)
async def get_property_transactions(request: Request):
    access_token = await get_access_token_from_request(request)
    try:
        emails = await fetch_gmail_threads(access_token)
        transactions = []
        for email in emails:
            transaction = await extract_property_transaction_from_email(email)
            if transaction:
                transactions.append(transaction)
        return PropertyTransactionsResponse(transactions=transactions)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch property transactions: {str(exc)}")

@router.post("/draft-reply")
async def draft_reply(request: Request, payload: EmailDraftRequest):
    access_token = await get_access_token_from_request(request)
    try:
        result = await create_gmail_draft_reply(
            access_token=access_token,
            thread_id=payload.thread_id,
            to=payload.to,
            subject=payload.subject,
            body=payload.body,
            message_id_header=payload.message_id_header,
            references_header=payload.references_header,
        )
        return {"ok": True, "draft": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create draft reply: {str(exc)}")

@router.post("/send-reply")
async def send_reply(request: Request, payload: SendReplyRequest):
    access_token = await get_access_token_from_request(request)
    try:
        result = await send_gmail_reply(
            access_token=access_token,
            thread_id=payload.thread_id,
            to=payload.to,
            subject=payload.subject,
            body=payload.body,
            message_id_header=payload.message_id_header,
            references_header=payload.references_header,
        )
        return {"ok": True, "message": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to send reply: {str(exc)}")

@router.post("/archive-thread")
async def archive_thread(request: Request, payload: ArchiveThreadRequest):
    access_token = await get_access_token_from_request(request)
    try:
        result = await archive_gmail_thread(access_token, payload.thread_id)
        return {"ok": True, "thread": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to archive thread: {str(exc)}")
