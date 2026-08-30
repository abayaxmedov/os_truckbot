from __future__ import annotations

import re

_CYRILLIC_MAP = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "e",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "h",
    "ц": "c",
    "ч": "ch",
    "ш": "sh",
    "щ": "sch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
}


def transliterate(text: str) -> str:
    return "".join(_CYRILLIC_MAP.get(ch, ch) for ch in text.lower())


def slugify(text: str) -> str:
    text = transliterate(text)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "item"


def normalize_part_number(number: str) -> str:
    """Normalize an OEM / article number for matching.

    Strips separators and uppercases so "MAN 51.10100-6126", "51 10100 6126"
    and "51.10100-6126" all compare equal on their alphanumeric core.
    """
    return re.sub(r"[^A-Za-z0-9]", "", number or "").upper()
