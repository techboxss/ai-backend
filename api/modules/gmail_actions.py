import httpx
from modules.gmail_fetcher import GMAIL_BASE_URL
from utils.gmail_utils import build_reply_raw

async def create_gmail_draft_reply(access_token: str, thread_id: str, to: str, subject: str, body: str, message_id_header: str | None = None, references_header: str | None = None) -> dict:
    raw = build_reply_raw(to, subject, body, message_id_header, references_header)
    payload = {"message": {"raw": raw, "threadId": thread_id}}
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{GMAIL_BASE_URL}/drafts",
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
            json=payload,
        )
    if response.status_code >= 400:
        raise RuntimeError(f"Failed to create Gmail draft: {response.text}")
    return response.json()

async def send_gmail_reply(access_token: str, thread_id: str, to: str, subject: str, body: str, message_id_header: str | None = None, references_header: str | None = None) -> dict:
    raw = build_reply_raw(to, subject, body, message_id_header, references_header)
    payload = {"raw": raw, "threadId": thread_id}
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{GMAIL_BASE_URL}/messages/send",
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
            json=payload,
        )
    if response.status_code >= 400:
        raise RuntimeError(f"Failed to send Gmail reply: {response.text}")
    return response.json()

async def archive_gmail_thread(access_token: str, thread_id: str) -> dict:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{GMAIL_BASE_URL}/threads/{thread_id}/modify",
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
            json={"removeLabelIds": ["INBOX"]},
        )
    if response.status_code >= 400:
        raise RuntimeError(f"Failed to archive Gmail thread: {response.text}")
    return response.json()
