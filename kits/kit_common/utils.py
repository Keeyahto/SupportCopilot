import re


def normalize_text(text: str) -> str:
    if not text:
        return ""
    # Normalize newlines and spaces
    s = text.replace('\r\n', '\n').replace('\r', '\n')
    s = re.sub(r"\u00A0", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

