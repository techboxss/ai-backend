import re


def normalize_money(value: str | None) -> str | None:
    if not value:
        return None
    clean = re.sub(r"\s+", " ", value).strip()
    dollar = re.search(r"\$\s?\d[\d,]*(?:\.\d{2})?", clean)
    if dollar:
        return dollar.group(0).replace(" ", "")
    k_amount = re.search(r"\b(\d+(?:\.\d+)?)\s?k\b", clean, flags=re.I)
    if k_amount:
        return f"${float(k_amount.group(1)) * 1000:,.0f}"
    amount = re.search(r"\b\d[\d,]*(?:\.\d{2})?\b", clean)
    if amount:
        return f"${amount.group(0)}"
    return None


def find_earnest_money_messy(text: str) -> str | None:
    patterns = [
        r"\b(?:earnest money|emd|deposit|binder|escrow deposit|contract deposit)\b.{0,80}?(\$\s?\d[\d,]*(?:\.\d{2})?|\d+(?:\.\d+)?\s?k)\b",
        r"(\$\s?\d[\d,]*(?:\.\d{2})?|\d+(?:\.\d+)?\s?k)\b.{0,80}?\b(?:earnest money|emd|deposit|binder|escrow deposit|contract deposit)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            return normalize_money(match.group(1))
    return None
