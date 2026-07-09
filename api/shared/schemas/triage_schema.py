from pydantic import BaseModel
from typing import Literal, Optional
from shared.schemas.property_schema import PropertyTransactionStatus

class EmailForTriage(BaseModel):
    id: Optional[str] = None
    thread_id: Optional[str] = None
    subject: str
    sender: str
    date: str
    body: str
    snippet: Optional[str] = ""
    message_id_header: Optional[str] = None
    references_header: Optional[str] = None

class TriageRequest(BaseModel):
    email: EmailForTriage

class SuggestedTask(BaseModel):
    title: str
    due_date: Optional[str] = None

class SuggestedEvent(BaseModel):
    summary: str
    description: str
    date_time: Optional[str] = None

class PropertyTransactionExtract(BaseModel):
    property_address: Optional[str] = None
    buyer_client: Optional[str] = None
    escrow_officer: Optional[str] = None
    earnest_money: Optional[str] = None
    closing_scheduled: Optional[str] = None
    status: PropertyTransactionStatus = "UNKNOWN"

class TriageResponse(BaseModel):
    classification: str
    confidence: Literal["High", "Medium", "Low"]
    detected_critical_signals: list[str]
    priority: Literal["High", "Medium", "Low"]
    urgency: str
    deadline_date: Optional[str] = None
    deadline_reason: Optional[str] = None
    privilege_assessment: str
    brief_summary: str
    suggested_draft_response: str
    suggested_tasks: list[SuggestedTask]
    suggested_events: list[SuggestedEvent]
    should_delegate: bool = False
    suggested_assignee: Optional[str] = None
    delegation_reason: Optional[str] = None
    property_transaction: Optional[PropertyTransactionExtract] = None
