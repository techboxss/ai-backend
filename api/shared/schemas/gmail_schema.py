from pydantic import BaseModel
from typing import Optional

class GmailThreadMessage(BaseModel):
    id: str
    thread_id: str
    subject: str
    sender: str
    date: str
    snippet: str
    body: str
    labels: list[str] = []
    message_id_header: Optional[str] = None
    references_header: Optional[str] = None

class EmailDraftRequest(BaseModel):
    message_id: str
    thread_id: str
    to: str
    subject: str
    body: str
    message_id_header: Optional[str] = None
    references_header: Optional[str] = None

class SendReplyRequest(BaseModel):
    message_id: str
    thread_id: str
    to: str
    subject: str
    body: str
    message_id_header: Optional[str] = None
    references_header: Optional[str] = None

class ArchiveThreadRequest(BaseModel):
    thread_id: str
