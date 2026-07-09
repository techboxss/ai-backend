import httpx
from shared.schemas.gmail_schema import GmailThreadMessage
from utils.gmail_utils import get_header, extract_message_body

GMAIL_BASE_URL = "https://gmail.googleapis.com/gmail/v1/users/me"

PROPERTY_GMAIL_QUERY = (
    'is:inbox newer_than:30d '
    '(closing OR escrow OR title OR property OR buyer OR seller OR earnest OR EMD OR settlement OR contract OR deed)'
)

async def fetch_gmail_threads(access_token: str, query: str | None = None, max_results: int = 20) -> list[GmailThreadMessage]:
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(timeout=60) as client:
        list_response = await client.get(
            f"{GMAIL_BASE_URL}/threads",
            headers=headers,
            params={"maxResults": max_results, "q": query or PROPERTY_GMAIL_QUERY},
        )
        if list_response.status_code >= 400:
            raise RuntimeError(f"Failed to list Gmail threads: {list_response.text}")
        thread_refs = list_response.json().get("threads", [])
        emails: list[GmailThreadMessage] = []
        for thread_ref in thread_refs:
            detail_response = await client.get(f"{GMAIL_BASE_URL}/threads/{thread_ref['id']}", headers=headers)
            if detail_response.status_code >= 400:
                continue
            thread = detail_response.json()
            messages = thread.get("messages", [])
            if not messages:
                continue
            latest_msg = messages[-1]
            payload = latest_msg.get("payload", {})
            headers_list = payload.get("headers", [])
            body = extract_message_body(payload) or latest_msg.get("snippet", "")
            emails.append(GmailThreadMessage(
                id=latest_msg.get("id"),
                thread_id=thread_ref["id"],
                subject=get_header(headers_list, "subject") or "(No Subject)",
                sender=get_header(headers_list, "from") or "Unknown Sender",
                date=get_header(headers_list, "date") or "",
                snippet=latest_msg.get("snippet", ""),
                body=body,
                labels=latest_msg.get("labelIds", []),
                message_id_header=get_header(headers_list, "message-id"),
                references_header=get_header(headers_list, "references"),
            ))
    return emails
