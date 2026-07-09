import re
from html import unescape


def strip_html(html: str) -> str:
    text = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</p>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def remove_quoted_history(text: str) -> str:
    cleaned = text
    for pattern in [r"\nOn .+ wrote:\n", r"\nFrom:\s.+\nSent:\s.+\n", r"\n-{2,}\s*Original Message\s*-{2,}"]:
        cleaned = re.split(pattern, cleaned, maxsplit=1, flags=re.I)[0]
    return cleaned.strip()


def read_labeled_value(text: str, labels: list[str]) -> str | None:
    for line in [line.strip() for line in text.splitlines() if line.strip()]:
        for label in labels:
            match = re.match(rf"^{re.escape(label)}\s*[:=-]\s*(.+)$", line, flags=re.I)
            if match:
                return match.group(1).strip()
    return None
