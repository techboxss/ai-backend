import re

MONTHS = {
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12",
}


def normalize_date(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    iso = re.search(r"\b20\d{2}-\d{2}-\d{2}\b", value)
    if iso:
        return iso.group(0)
    us = re.search(r"\b(\d{1,2})/(\d{1,2})/(20\d{2})\b", value)
    if us:
        month, day, year = us.groups()
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    long_date = re.search(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s*(20\d{2})\b", value, flags=re.I)
    if long_date:
        month_name, day, year = long_date.groups()
        return f"{year}-{MONTHS[month_name.lower()]}-{day.zfill(2)}"
    return None


def find_closing_date_messy(text: str) -> str | None:
    date_pattern = r"(20\d{2}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/20\d{2}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s*20\d{2})"
    patterns = [
        rf"\b(?:closing|settlement|close|signing|funding|recording)\b.{{0,100}}?{date_pattern}",
        rf"{date_pattern}.{{0,100}}?\b(?:closing|settlement|close|signing|funding|recording)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            for group in match.groups():
                normalized = normalize_date(group)
                if normalized:
                    return normalized
    return None
