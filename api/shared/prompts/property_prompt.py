from shared.schemas.gmail_schema import GmailThreadMessage


def build_property_extraction_prompt(email: GmailThreadMessage) -> str:
    return f"""
You are a legal real-estate transaction extraction assistant.
Return ONLY valid JSON. Do not include markdown or commentary.

Extract property transaction fields from this email. Real emails may be messy, informal, incomplete, forwarded, or quoted.
Infer fields only when the text reasonably supports the inference. Do not invent names, addresses, dates, or money amounts.
If a field is missing or uncertain, return null.

FIELD RULES:
- property_address: real property address, premises, parcel, subject property, or closing property.
- buyer_client: buyer, purchaser, borrower, client, or represented party.
- escrow_officer: escrow officer, title officer, settlement agent, closer, or title-company contact.
- earnest_money: EMD, earnest money deposit, binder, escrow deposit, or contract deposit.
- closing_scheduled: scheduled closing, signing, settlement, funding, or recording date in YYYY-MM-DD.
- status: UNDERWAY, AT RISK, DELAYED, CLOSED, or UNKNOWN.

EMAIL:
Subject: {email.subject}
Sender: {email.sender}
Date: {email.date}
Snippet: {email.snippet}
Body:
{email.body}

Return this exact JSON:
{{
  "property_address": "string or null",
  "buyer_client": "string or null",
  "escrow_officer": "string or null",
  "earnest_money": "string or null",
  "closing_scheduled": "YYYY-MM-DD or null",
  "status": "UNDERWAY | AT RISK | DELAYED | CLOSED | UNKNOWN"
}}
"""
