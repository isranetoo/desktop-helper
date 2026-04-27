"""Utilitários simples de internacionalização (i18n)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).parent
LOCALE_DIR = APP_DIR / "locale"
DEFAULT_LANG = "pt"


class I18n:
    def __init__(self, language: str = DEFAULT_LANG):
        self.language = language or DEFAULT_LANG
        self._translations = self._load_translations(self.language)
        self._fallback = self._load_translations(DEFAULT_LANG) if self.language != DEFAULT_LANG else self._translations

    def _load_translations(self, language: str) -> dict[str, Any]:
        path = LOCALE_DIR / f"{language}.json"
        if not path.exists():
            path = LOCALE_DIR / f"{DEFAULT_LANG}.json"
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def get(self, key: str, default: str | None = None, **kwargs) -> str:
        value = self._translations.get(key)
        if value is None:
            value = self._fallback.get(key, default if default is not None else key)
        if not isinstance(value, str):
            return default if default is not None else key
        if kwargs:
            try:
                return value.format(**kwargs)
            except Exception:
                return value
        return value

    def month_name(self, month: int) -> str:
        key = f"month_{int(month):02d}"
        return self.get(key, f"{int(month):02d}")


def get_translator(language: str = DEFAULT_LANG) -> I18n:
    return I18n(language)
