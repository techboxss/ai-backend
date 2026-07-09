import base64
from email.mime.text import MIMEText
from email.utils import parseaddr
from utils.text_utils import strip_html


def decode_base64_url(value: str) -> str:
    try:
        padded = value.replace("-", "+").replace("_", "/")
        padded += "=" * (-len(padded) % 4)
        return base64.b64decode(padded).decode("utf-8", errors="replace")
    except Exception:
        return ""


def encode_base64_url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("utf-8").rstrip("=")


def get_header(headers: list[dict], name: str) -> str | None:
    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return header.get("value")
    return None


def find_mime_part(parts: list[dict], mime_type: str) -> dict | None:
    for part in parts:
        if part.get("mimeType") == mime_type:
            return part
        nested = part.get("parts", [])
        if nested:
            found = find_mime_part(nested, mime_type)
            if found:
                return found
    return None


def extract_message_body(payload: dict) -> str:
    if not payload:
        return ""
    mime_type = payload.get("mimeType")
    if mime_type == "text/plain" and payload.get("body", {}).get("data"):
        return decode_base64_url(payload["body"]["data"])
    parts = payload.get("parts", [])
    if parts:
        plain = find_mime_part(parts, "text/plain")
        if plain and plain.get("body", {}).get("data"):
            return decode_base64_url(plain["body"]["data"])
        html = find_mime_part(parts, "text/html")
        if html and html.get("body", {}).get("data"):
            return strip_html(decode_base64_url(html["body"]["data"]))
    if mime_type == "text/html" and payload.get("body", {}).get("data"):
        return strip_html(decode_base64_url(payload["body"]["data"]))
    return ""


def email_address_only(sender: str) -> str:
    return parseaddr(sender)[1] or sender


def build_reply_raw(to: str, subject: str, body: str, message_id_header: str | None = None, references_header: str | None = None) -> str:
    msg = MIMEText(body, "plain", "utf-8")
    msg["To"] = to
    msg["Subject"] = subject if subject.lower().startswith("re:") else f"Re: {subject}"
    if message_id_header:
        msg["In-Reply-To"] = message_id_header
        msg["References"] = f"{references_header or ''} {message_id_header}".strip()
    return encode_base64_url(msg.as_bytes())
