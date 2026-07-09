import re
from shared.schemas.gmail_schema import GmailThreadMessage
from shared.schemas.property_schema import PropertyTransaction, SourceEmail
from shared.prompts.property_prompt import build_property_extraction_prompt
from modules.ollama_client import generate_json_from_ollama
from utils.text_utils import read_labeled_value, remove_quoted_history
from utils.date_utils import normalize_date, find_closing_date_messy
from utils.money_utils import normalize_money, find_earnest_money_messy

VALID_STATUSES = {"UNDERWAY", "AT RISK", "DELAYED", "CLOSED", "UNKNOWN"}


def find_address_messy(text: str) -> str | None:
    labeled = read_labeled_value(text, ["Property Address", "Property", "Address", "Premises", "Subject Property"])
    if labeled:
        return labeled
    match = re.search(r"\b\d{2,6}\s+[A-Za-z0-9 .'-]+(?:Dr|Drive|St|Street|Ave|Avenue|Rd|Road|Ln|Lane|Blvd|Boulevard|Ct|Court|Way|Pkwy|Parkway|Pl|Place|Ter|Terrace|Cir|Circle|Trl|Trail)\b(?:,\s*[A-Za-z .'-]+,\s*[A-Z]{2}\s*\d{5})?", text, flags=re.I)
    return match.group(0) if match else None


def find_buyer_client_messy(text: str) -> str | None:
    labeled = read_labeled_value(text, ["Buyer/Client", "Buyer", "Client", "Purchaser", "Purchasers", "Borrower", "Borrowers", "Represented Party"])
    if labeled:
        return labeled
    patterns = [
        r"\b(?:buyer|purchaser|client|borrower)\s+(?:is|are|will be|appears as|listed as)\s+([A-Z][A-Za-z.'-]+(?:\s+(?:&|and)\s+[A-Z][A-Za-z.'-]+)?(?:\s+[A-Z][A-Za-z.'-]+){0,3})",
        r"\bfor\s+(?:our\s+)?(?:client|buyer|purchaser|borrower)\s+([A-Z][A-Za-z.'-]+(?:\s+(?:&|and)\s+[A-Z][A-Za-z.'-]+)?(?:\s+[A-Z][A-Za-z.'-]+){0,3})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            return match.group(1).strip()
    return None


def find_escrow_officer_messy(text: str) -> str | None:
    labeled = read_labeled_value(text, ["Escrow Officer", "Escrow", "Title Officer", "Settlement Agent", "Closing Contact", "Title Contact", "Closer"])
    if labeled:
        return labeled
    patterns = [
        r"\b([A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+){0,2})\s+(?:at|with|from)\s+[A-Z][A-Za-z& .'/-]*(?:Title|Escrow|Settlement|Closing)\b",
        r"\b(?:escrow officer|title officer|settlement agent|closer|closing contact)\s+(?:is|will be|assigned is)?\s*([A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+){0,2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            return match.group(1).strip()
    return None


def infer_status(text: str) -> str:
    lower = text.lower()
    if re.search(r"\b(closed|funded|recorded|disbursed|settlement completed)\b", lower):
        return "CLOSED"
    if re.search(r"\b(delayed|postponed|extended|extension required|rescheduled|cannot close)\b", lower):
        return "DELAYED"
    if re.search(r"\b(at risk|default|urgent|missing|title issue|financing issue|wire fraud|objection|lien)\b", lower):
        return "AT RISK"
    if re.search(r"\b(closing|escrow|title|settlement|earnest money|emd|property|buyer|seller|contract|purchase agreement)\b", lower):
        return "UNDERWAY"
    return "UNKNOWN"


def fallback_extract(email: GmailThreadMessage) -> dict | None:
    text = remove_quoted_history(f"{email.subject}\n{email.snippet}\n{email.body}\n{email.sender}")
    if not re.search(r"property|closing|escrow|title|earnest money|\bemd\b|buyer|seller|settlement|contract|deed|purchase agreement|lender|mortgage", text, flags=re.I):
        return None
    earnest = read_labeled_value(text, ["Earnest Money", "Earnest Money Deposit", "EMD", "Deposit", "Contract Deposit"]) or find_earnest_money_messy(text)
    closing = read_labeled_value(text, ["Closing Scheduled", "Closing Date", "Settlement Date", "Scheduled Closing", "Close Date"]) or find_closing_date_messy(text)
    return {
        "property_address": find_address_messy(text),
        "buyer_client": find_buyer_client_messy(text),
        "escrow_officer": find_escrow_officer_messy(text),
        "earnest_money": normalize_money(earnest),
        "closing_scheduled": normalize_date(closing),
        "status": infer_status(text),
    }


def normalize_status(value: object) -> str:
    status = str(value or "UNKNOWN").upper()
    return status if status in VALID_STATUSES else "UNKNOWN"


def has_useful_fields(tx: dict) -> bool:
    return bool(tx.get("property_address") or tx.get("buyer_client") or tx.get("escrow_officer") or tx.get("earnest_money") or tx.get("closing_scheduled"))


async def extract_property_transaction_from_email(email: GmailThreadMessage) -> PropertyTransaction | None:
    fallback = fallback_extract(email) or {}
    llm_result: dict = {}
    try:
        llm_result = await generate_json_from_ollama(build_property_extraction_prompt(email))
    except Exception as exc:
        print(f"Ollama property extraction failed. Using fallback only. {exc}")
    merged = {
        "property_address": llm_result.get("property_address") or fallback.get("property_address"),
        "buyer_client": llm_result.get("buyer_client") or fallback.get("buyer_client"),
        "escrow_officer": llm_result.get("escrow_officer") or fallback.get("escrow_officer"),
        "earnest_money": normalize_money(llm_result.get("earnest_money") or fallback.get("earnest_money")),
        "closing_scheduled": normalize_date(llm_result.get("closing_scheduled") or fallback.get("closing_scheduled")),
        "status": normalize_status(llm_result.get("status") or fallback.get("status")),
    }
    if not has_useful_fields(merged):
        return None
    return PropertyTransaction(
        id=email.thread_id,
        property_address=merged["property_address"],
        buyer_client=merged["buyer_client"],
        escrow_officer=merged["escrow_officer"],
        earnest_money=merged["earnest_money"],
        closing_scheduled=merged["closing_scheduled"],
        status=merged["status"],
        source_email=SourceEmail(subject=email.subject, sender=email.sender, date=email.date, thread_id=email.thread_id, message_id=email.id),
    )
