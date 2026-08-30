from __future__ import annotations

from app.i18n.messages import MESSAGES

DEFAULT_LANG = "ru"


def t(key: str, lang: str = DEFAULT_LANG, /, **kwargs) -> str:
    """Translate a message key for the given language, with .format() kwargs."""
    lang = lang if lang in MESSAGES else DEFAULT_LANG
    template = MESSAGES[lang].get(key) or MESSAGES[DEFAULT_LANG].get(key) or key
    try:
        return template.format(**kwargs)
    except (KeyError, IndexError):
        return template
