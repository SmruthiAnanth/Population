from __future__ import annotations

import re
import unicodedata


COUNTRY_ALIAS_MAP = {
    "gr": "el",
    "greece": "el",
    "sp": "es",
    "sw": "se",
    "uk": "gb",
    "great britain": "gb",
    "united kingdom": "gb",
    "united kingdom of great britain and northern ireland": "gb",
}


def normalize_text(value: str) -> str:
    value = "" if value is None else str(value)
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def clean_country_code(value: str) -> str:
    key = normalize_text(value)
    return COUNTRY_ALIAS_MAP.get(key, key)
