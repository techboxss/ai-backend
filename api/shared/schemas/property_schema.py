from pydantic import BaseModel
from typing import Literal, Optional

PropertyTransactionStatus = Literal["UNDERWAY", "AT RISK", "DELAYED", "CLOSED", "UNKNOWN"]

class SourceEmail(BaseModel):
    subject: str
    sender: str
    date: str
    thread_id: str
    message_id: str

class PropertyTransaction(BaseModel):
    id: str
    property_address: Optional[str] = None
    buyer_client: Optional[str] = None
    escrow_officer: Optional[str] = None
    earnest_money: Optional[str] = None
    closing_scheduled: Optional[str] = None
    status: PropertyTransactionStatus = "UNKNOWN"
    source_email: SourceEmail

class PropertyTransactionsResponse(BaseModel):
    transactions: list[PropertyTransaction]
